"""Rebuild 2027 scouting rankings from the supplied delivery files."""
from pathlib import Path

import pandas as pd

import comprehensive_pressure_rank as benchmark
from hackathon_recommended_rank import cutoff_score

ROOT = Path(__file__).resolve().parent
CUTOFFS = (68, 73, 78)
JAIPUR, GUWAHATI = '6', '1241'


def rate(group):
    return 100 * group.weighted.sum() / group.weight.sum() if len(group) else 0


def form(group):
    return 100 * group.weighted.sum() / (100 + group.weight.sum())


def rr_bonus(pressure):
    local = pressure[pressure.venue_id.isin([JAIPUR, GUWAHATI])]
    # Prior of 100 neutral deliveries limits single-match effects.
    return min(3.0, .10 * max(0.0, form(local)))


def score_role(deliveries, role, india_matches):
    batting = role == 'bat'
    work = deliveries[deliveries.bat_ball].copy() if batting else deliveries.copy()
    player_id = 'striker_id' if batting else 'bowler_id'
    pressure = 'p_' + role
    work['weight'] = 0.84 ** (2026 - work.date.str[:4].astype(int))
    work['weighted'] = work.weight * work['impact_' + role]
    work['india'] = work.match_id.isin(india_matches)
    thresholds = {q: work[pressure].quantile(q / 100) for q in CUTOFFS}
    rows = []
    for pid, group in work.groupby(player_id):
        cut_scores = []
        meets_standard = True
        for q, threshold in thresholds.items():
            high = group[group[pressure] >= threshold]
            ordinary = group[group[pressure] < threshold]
            match = high.groupby('match_id').weighted.agg(['sum', 'size'])
            match = match[match['size'] >= 3]
            if len(high) < 20 or len(ordinary) < 40 or len(match) < 3:
                break
            meets_standard &= len(high) >= 46 and len(ordinary) >= 75 and len(match) >= 5
            evidence = dict(pressure_balls=len(high), pressure_matches=len(match),
                            pressure_rate_per100=rate(high), normal_rate_per100=rate(ordinary),
                            match_consistency_pct=100 * (match['sum'] > 0).mean())
            core = cutoff_score(evidence)
            ipl = group[group.fmt == 'IPL']
            recent_ipl = ipl[ipl.date >= '2025-01-01']
            international = group[(group.fmt == 'T20I') & (group.date >= '2026-01-01')]
            indian = high[high.india]
            score = (.55 * core + .15 * form(high[high.fmt == 'IPL'])
                     + .15 * form(recent_ipl) + .10 * form(indian) + .05 * form(international))
            cut_scores.append(score)
            if q == 73:
                central = dict(**evidence, rr_bonus=rr_bonus(high),
                               jaipur_pressure_balls=(high.venue_id == JAIPUR).sum(),
                               guwahati_pressure_balls=(high.venue_id == GUWAHATI).sum(), india_pressure_balls=len(indian),
                               recent_ipl_balls=len(recent_ipl), recent_t20i_balls=len(international))
        if len(cut_scores) == 3:
            low, mid, high_score = cut_scores
            score = (low + 2 * mid + high_score) / 4 - .15 * (max(cut_scores) - min(cut_scores))
            rows.append(dict(player_id=pid, base_score=score, score=score + central['rr_bonus'], evidence_tier=1 if meets_standard else 2, **central,
                             **dict(zip(('score_q68', 'score_q73', 'score_q78'), cut_scores))))
    return pd.DataFrame(rows)


def shortlist(scores, pool, excluded):
    scored = pool.merge(scores, on='player_id', how='left', validate='one_to_one')
    eligible = scored[scored.score.notna() & scored.released_by.ne('RR') & ~scored.player_id.isin(excluded)
                      & scored.availability.isin(['release only', 'registration reported', 'confirmed'])]
    return eligible.sort_values(['evidence_tier', 'score', 'pressure_balls', 'player_id'],
                                ascending=[True, False, False, True])


def main():
    mm, bb, links = benchmark.data_load()
    context = benchmark.match_context(mm, bb)
    history = benchmark.pre_match_player_evidence(mm, bb)
    frame, _ = benchmark.pressure_rows(mm, bb, context, history)
    frame, _ = benchmark.add_expected(frame)
    pool = pd.read_csv(ROOT / 'scouting_pool_2027.csv')
    excluded = set(links.loc[links.team_name.str.casefold() == 'pakistan', 'player_id'])
    india = mm.loc[mm.venue_country == 'India', 'match_id']
    print(f'{len(mm)} matches, {len(frame)} deliveries, {mm.match_date.min()} to {mm.match_date.max()}')
    for role in ('bat', 'bowl'):
        scores = score_role(frame, role, india)
        ranked = shortlist(scores, pool, excluded).copy()
        base_order = ranked.sort_values(['evidence_tier', 'base_score', 'pressure_balls', 'player_id'],
                                        ascending=[True, False, False, True])
        ranked['rank_without_bonus'] = pd.Series(range(1, len(ranked) + 1), index=base_order.index)
        ranked.insert(0, 'rank', range(1, len(ranked) + 1))
        ranked.to_csv(ROOT / 'outputs' / f'{role}_scouting_2027.csv', index=False, float_format='%.4f')
        print(role, ranked.head(10)[['player', 'score', 'pressure_balls', 'pressure_matches']].to_string(index=False))


if __name__ == '__main__':
    main()
