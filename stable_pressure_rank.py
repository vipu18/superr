#!/usr/bin/env python3
"""Stable pressure rankings from comprehensive q68, q73 and q78 outputs."""
from pathlib import Path
import pandas as pd

OUT = Path(__file__).resolve().parent / "outputs"
THRESHOLDS = (68, 73, 78)
MIN_PRESSURE_BALLS_Q73 = 120
MIN_PRESSURE_MATCHES_Q73 = 12

for role in ("bat", "bowl"):
    d = pd.read_csv(OUT / f"{role}_comprehensive_consensus.csv")
    ranks = [f"rank_q{q}" for q in THRESHOLDS]
    consistency = [f"match_consistency_pct_q{q}" for q in THRESHOLDS]
    d = d.loc[(d.pressure_balls_q73 >= MIN_PRESSURE_BALLS_Q73)
              & (d.pressure_matches >= MIN_PRESSURE_MATCHES_Q73)].copy()
    d["worst_case_rank"] = d[ranks].max(axis=1)
    d["mean_rank"] = d[ranks].mean(axis=1)
    d["top10_cutoffs"] = (d[ranks] <= 10).sum(axis=1)
    d["positive_pressure_matches_pct"] = d[consistency].mean(axis=1)
    # Conservative worst-case rank, positive-match consistency tiebreaker.
    d = d.sort_values(
        ["worst_case_rank", "positive_pressure_matches_pct", "consensus_index", "pressure_balls_q73"],
        ascending=[True, False, False, False]
    ).head(10).copy()
    d.insert(0, "stable_rank", range(1, len(d) + 1))
    columns = ["stable_rank","player","rank_q68","rank_q73","rank_q78",
               "worst_case_rank","top10_cutoffs","positive_pressure_matches_pct",
               "pressure_balls_q73","pressure_matches","consensus_index",
               "score_q73","pressure_index","resilience_index",
               "fitness_status","future_ipl_availability"]
    d[columns].round(2).to_csv(OUT / f"{role}_most_stable_pressure_top10.csv", index=False)
    print(f"{role}:")
    print(d[columns[:10]].round(1).to_string(index=False))
