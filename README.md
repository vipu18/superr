# SupeRR Selector — Comprehensive Pressure Benchmark

**Research window:** 1 January 2024 – 12 November 2026. IPL and men's T20I matches from the supplied datasets. Main rankings measure **overall pressure reliability**, not special RR home-ground fit. Indian venue and toss conditions are still included in the context score.

## Reproduce

```bash
python -m pip install -r requirements.txt
mkdir -p data
# Copy the supplied ball_by_ball.csv, matches.csv, competitions.csv,
# and competition_team_player_mapping.csv into the data/ folder.
python comprehensive_pressure_rank.py
python check_comprehensive_sensitivity.py
python aggregate_comprehensive_rank.py
python -m unittest discover -s tests
```

The final overall top 10 are found in `outputs/bat_comprehensive_consensus.csv` and `outputs/bowl_comprehensive_consensus.csv`. Three alternative definitions of high pressure (68th, 73rd and 78th percentiles) are combined as rank percentiles with weights 25% / 50% / 25%. The **0–100 consensus index is not a prediction of winning probability**.

## Pressure included

- **Match context:** target/required rate, wickets remaining, balls left, low-score defence, closeness, innings progress.
- **Momentum:** recent run rate, dot-ball streaks, recent wickets, bowler economy, previous boundaries and no-ball/expensive-delivery recovery.
- **Responsibility:** carrying the innings, weak supporting batting, wicket share, captaincy, lower-order entry during a collapse, and individual prior-form dips.
- **Opposition and stakes:** pre-match rolling team strength, historical batter–bowler difficulty, knockout games, approximate IPL standings and net run rate before the match.
- **Ground and toss:** venue scoring, innings and opponent-favoured toss decisions.
- **Opponent approach:** scoreboard-inferred attack, consolidation, controlled chase and survival states. These are proxies, **not observations of psychological mentality**.

Impact per ball is adjusted against peer expectations for format, innings, phase, bowling style, pressure band and venue. Batting impact: actual runs minus expected runs minus six times excess striker dismissals. Bowling impact: expected runs minus conceded runs plus six times excess bowler-credit wickets.

Within each threshold the ranking score weighs: **49% high-pressure impact, 13% pressure-vs-normal improvement, 10% match-to-match reliability, 10% phase versatility, 8% opposition/stakes, 6% toss/tactical adversity, 4% general form**, minus a sample-uncertainty penalty. Historical year weights are 0.78 (2024), 0.89 (2025), and 1 (2026). These are research choices, not fitted weights.

## Limitations

Exact qualification targets (e.g. needing a chase in 14 overs), sledging incidents, true mental state, confirmed risk of being removed from the playing XI, medical fitness, contract availability, and complete domestic/franchise T20 results cannot be reliably calculated from these CSVs and **are not fabricated**. League standings/NRR are approximations from data-quality-filtered matches. Personal form dips are proxies, **not actual selection decisions**. Expected peer outcomes use retrospective data and rankings have not been prospectively validated. These limitations are important before final submission.

The user requested exclusion of players representing Pakistan for IPL context; this is **not stated as an official Round 1 rule**. IPL sample minimums are also model choices. There is no RR-specific venue ranking bonus; team fit is a separate question.

**Input data are not distributed in this repository.** Reuse the supplied files only where permitted by their licence.

For a factor-by-factor audit see [FACTOR_AUDIT.md](FACTOR_AUDIT.md).
