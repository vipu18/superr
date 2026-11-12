# SupeRR Selector — Overall Multi-Pressure Cricket Benchmark

Research period: **1 January 2024–12 November 2026**. Analyses supplied IPL/T20I delivery data. The official challenge requests the most reliable players under pressure; therefore the overall rankings do **not** add a Rajasthan Royals ground bonus.

## Consensus rankings (2024–2026)
**Batters:** Shreyas Iyer, Shashank Singh, Naman Dhir, Tilak Varma, Tim David, Abhishek Sharma, Jos Buttler, Virat Kohli, Tristan Stubbs, Riyan Parag.

**Bowlers:** Sunil Narine, Jasprit Bumrah, Rasikh Salam, Matheesha Pathirana, Cameron Green, Mitchell Starc, Jason Holder, Lungi Ngidi, Varun Chakravarthy, Ravindra Jadeja.

## Method
Match state before each ball is used to estimate pressure from run rate, wickets, balls remaining, recent dots/wickets, individual responsibility, pre-match opponent strength, tournament stakes, past venue scoring, and plausible tactical choices during chases (attack/consolidation/survival).

**Tactical response is inferred from scoreboards; this does not measure real mental state.** Sledging, medical fitness, selection insecurity, future IPL availability, and exact net-run-rate qualification deadlines are not reliably available in these CSVs and are not given invented scores.

Scores use context-adjusted actual minus expected runs/wickets, smoothing for small samples and match-to-match stability. The final index averages normalized rank percentiles at pressure quantiles **0.68 (25%)**, **0.73 (50%)**, and **0.78 (25%)**. 484 eligible matches and 114,946 deliveries were analysed. These are retrospective statistical rankings, not validated success probabilities.

## Inputs and reproducibility
Do not commit the supplied licensed CSV dataset. Keep the four provided files in `data/`:
- `ball_by_ball.csv`
- `matches.csv`
- `competitions.csv`
- `competition_team_player_mapping.csv`

The complete reproducible script package and CSV diagnostics are supplied as a companion download in the user's ChatGPT session. GitHub files are being populated independently of the licensed data.

## Limitations
Pressure weights are research choices rather than trained parameters. Threshold changes can materially change some mid-table ranks, and retrospective peer baselines are not prospective cross-validation. There is no bonus for RR home games in this official-challenge version.
