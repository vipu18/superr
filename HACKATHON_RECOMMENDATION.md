# SupeRR Selector Season 2 — Recommended pressure ranking (2024–2026)

**Period:** 2024-01-01 through 2026-11-12. **Data:** supplied IPL and T20I delivery records. **Scope:** overall pressure reliability, not an RR acquisition list. No Jaipur/Guwahati ranking bonus.

## Why this ranking is recommended
The challenge asks which players repeatedly outperform both other players in comparable situations **and their own normal performance**. We score **context first, outcome second**, rather than giving rewards merely for encountering pressure. The upstream `comprehensive_pressure_rank.py` computes separate pre-ball pressure levels for batting and bowling using:
- chase target, required rate, balls remaining, wickets and closeness;
- recent dots, runs and wickets, bowling economy and post-error recovery;
- share of team performance, captaincy and historical personal form;
- opponent/team strength, knockout games and approximate playoff standings;
- venue, innings, toss advantage and likely chase tactics inferred from the scoreboard.
These are pre-ball numerical proxies. They do **not** claim to read a player's mind.

## Ball impact and comparison
Batting impact: `runs − peer expected runs − 6 × (dismissal − expected dismissal)`.
Bowling impact: `peer expected runs conceded − runs conceded + 6 × (credited wicket − expected wicket)`.
Peers are matched by format, innings, phase, bowling type, pressure band and smoothed venue evidence. **Six runs per wicket is a modelling assumption.**

The prior scoring engine provides results at pressure cutoffs q68, q73 and q78. We derive three *different* measures from those results:
1. **60%** sample-adjusted positive performance **above similar peers** under pressure. Shrink by `n/(n+110)`.
2. **25%** improvement relative to the same player's usual performance, shrink by `n/(n+130)`.
3. **15%** match-by-match reliability, based on the one-sided **80% Wilson lower bound** of the percentage of qualifying pressure matches with positive impact.

We combine threshold scores `0.25 × q68 + 0.50 × q73 + 0.25 × q78` and subtract `0.15 × (maximum − minimum cutoff score)` as an instability penalty.

Eligibility in this conservative version: present in all three q lists, at least 135 high-pressure batting deliveries or 150 high-pressure bowling deliveries at q73, and at least 12 qualifying pressure matches.

## Final top 10
| Rank | Batter | Score | Bowler | Score |
|---:|---|---:|---|---:|
| 1 | Naman Dhir | 28.09 | Sunil Narine | 22.60 |
| 2 | Shreyas Iyer | 27.54 | Jasprit Bumrah | 21.57 |
| 3 | Tilak Varma | 26.60 | Rasikh Salam | 19.84 |
| 4 | Shashank Singh | 24.65 | Mitchell Starc | 18.54 |
| 5 | Jitesh Sharma | 18.64 | Matheesha Pathirana | 13.66 |
| 6 | Jos Buttler | 13.88 | Wanindu Hasaranga | 12.27 |
| 7 | Donovan Ferreira | 13.46 | Jason Holder | 11.98 |
| 8 | Tim David | 13.44 | Lungi Ngidi | 11.30 |
| 9 | Tristan Stubbs | 12.42 | Jamie Overton | 8.98 |
| 10 | Marcus Stoinis | 12.27 | Varun Chakravarthy | 8.91 |

*Scores are relative model indices, not probabilities. The batting and bowling index scales are not directly comparable.*

## Sensitivity tests
Alternative weights were `(.75,.15,.10)` pressure-first, `(.48,.42,.10)` improvement-first and `(.50,.20,.30)` consistency-first. Top-10 overlap with the main selections was **10, 9, 10** among batters and **10, 8, 10** among bowlers. These are **weight sensitivity checks, not independent future-season validation**.

## Limitations
- The upstream results require minimum IPL participation and exclude Pakistan players based on a user-specified IPL relevance constraint. The official challenge itself does not explicitly exclude T20I-only players or Pakistani national-team players.
- Qualifying match and pressure minimums are research choices, not Unstop rules.
- Pitch and tactical response are inferred from scorecards, not direct pitch reports, dew readings or interviews.
- Exact must-win-before-14th-over qualification calculations require complete contemporaneous points tables and are not fully reproduced.
- Sledging, true selection threats, fitness, future contracts, and all domestic T20 matches are **unscored**, not zero.
- Expected outcomes were estimated retrospectively from the study period; a prospectively held-out predictive test has **not** been completed. Small scoring differences should not be treated as decisive.
- The raw copyrighted ball-by-ball data are deliberately **not** uploaded.

## Reproduce the rankings
Copy the supplied data CSVs to `data/` and run:
```bash
python comprehensive_pressure_rank.py
python check_comprehensive_sensitivity.py
python hackathon_recommended_rank.py
```
The third command generates full and top-10 CSVs plus a weight-sensitivity JSON in `outputs/`. Scripts require the packages listed in `requirements.txt` for the upstream model. The final aggregation itself uses Python's standard library.

Detailed offline archive and full results were also supplied in the conversation.
