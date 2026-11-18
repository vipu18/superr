# SupeRR Selector Pressure Performance Analysis

A Python-based analysis of **which batters and bowlers perform most reliably under pressure** in IPL and men's T20 International cricket.

The project was developed for **SupeRR Selector Season 2 Round 1**. Instead of choosing players based on reputation, total runs, or wickets alone, it evaluates **how difficult each match situation was** and **how well the player performed compared with expectations**.

> **Analysis period:** 1 January 2024 to 12 November 2026  
> **Data:** Provided IPL and men's T20I ball-by-ball, match, competition, and player-mapping CSVs  
> **Goal:** Two overall top-10 rankings batters and bowlers

## IPL 2027 Rajasthan Royals scouting shortlist

Updated 18 November 2026. The scouting model uses **114,946 deliveries from 484 eligible IPL and men's T20I matches**, spanning 11 January 2024 to 1 November 2026. The final selection uses the supplied releases from the other nine franchises. It excludes all nine Rajasthan releases, retained and traded-in players, Pakistan representatives, retirees and known withdrawals. Release alone leaves full-season availability provisional.

| Rank | Batter | Score | Bowler | Score |
|---:|---|---:|---|---:|
| 1 | Shahrukh Khan | 1.06 | Matheesha Pathirana | 13.47 |
| 2 | Abishek Porel | -4.29 | Jaydev Unadkat | 8.66 |
| 3 | Kamindu Mendis | -7.34 | Wanindu Hasaranga | 6.33 |
| 4 | Nehal Wadhera | -9.07 | Trent Boult | 5.52 |
| 5 | Pathum Nissanka | 3.33 | Spencer Johnson | 5.39 |
| 6 | Rachin Ravindra | -3.90 | Mustafizur Rahman | 4.82 |
| 7 | Matt Short | -5.25 | Blessing Muzarabani | 1.91 |
| 8 | Nitish Rana | -11.77 | Zak Foulkes | 0.49 |
| 9 | Rahul Tripathi | -14.50 | Lockie Ferguson | 0.46 |
| 10 | Wanindu Hasaranga | -22.83 | Avesh Khan | -0.84 |

Players rank by evidence tier first and score second within each role. Four batters met the stronger sample requirements. The remaining six qualified in the smaller-sample tier, which is why Pathum Nissanka ranks fifth despite his higher score. All ten selected bowlers met the stronger requirements.

The rating combines historical pressure performance (55%), IPL pressure performance (15%), recent IPL form (15%), pressure performance in India (10%) and recent T20I form (5%). Positive pressure impact at Jaipur and Guwahati can earn up to three additional points, with smaller bonuses for sparse evidence. Trent Boult moves from fifth to fourth after the venue adjustment.

**How stable are the picks?** Matheesha Pathirana led at all three pressure cutoffs, and nine or ten of the selected bowlers stayed in the top ten at each cutoff across 24 qualifying candidates. Shahrukh Khan also led at all three cutoffs, but exactly 10 batters qualified. His adjusted impact was similar under pressure and in ordinary situations. These checks measure historical stability within the dataset.

To reproduce the shortlist, place the four input CSVs listed below in `data/` and run `python rank_scouting.py`. Run `python -m unittest discover -s tests` to check model behaviour. The batting and bowling CSVs include evidence tiers, rank before the venue bonus, pressure sample sizes at each RR ground and availability status.

[Scouting methodology](SCOUTING_2027.md) · [Batting rankings](outputs/bat_scouting_2027.csv) · [Bowling rankings](outputs/bowl_scouting_2027.csv) · [Dated player pool](scouting_pool_2027.csv)

## Overall Round 1 benchmark rankings

These are the results from `hackathon_recommended_rank.py`, using pressure-adjusted performance, improvement over normal form, match-by-match reliability, and sample-size safeguards.

| Rank | Batter | Score | Bowler | Score |
| ---: | --- | ---: | --- | ---: |
| 1 | **Naman Dhir** | 28.09 | **Sunil Narine** | 22.60 |
| 2 | Shreyas Iyer | 27.54 | Jasprit Bumrah | 21.57 |
| 3 | Tilak Varma | 26.60 | Rasikh Salam | 19.84 |
| 4 | Shashank Singh | 24.65 | Mitchell Starc | 18.54 |
| 5 | Jitesh Sharma | 18.64 | Matheesha Pathirana | 13.66 |
| 6 | Jos Buttler | 13.88 | Wanindu Hasaranga | 12.27 |
| 7 | Donovan Ferreira | 13.46 | Jason Holder | 11.98 |
| 8 | Tim David | 13.44 | Lungi Ngidi | 11.30 |
| 9 | Tristan Stubbs | 12.42 | Jamie Overton | 8.98 |
| 10 | Marcus Stoinis | 12.27 | Varun Chakravarthy | 8.91 |

**Scores are relative statistical indices, not winning probabilities.** Batting and bowling scores are calculated separately and should not be compared directly.

## What counts as pressure?

The system calculates pressure **before each delivery**, using only the match state and previously observed information available for the pressure features. Batters and bowlers receive separate pressure assessments.

| Pressure category | Weight | Examples |
| --- | ---: | --- |
| **Match situation** | 42% | Required run rate, runs needed, balls left, wickets down, close finishes, innings stage |
| **Recent momentum** | 14% | Recent scoring, dot-ball streaks, wickets falling, bowler economy, recovering after an expensive delivery |
| **Individual responsibility** | 13% | Carrying the team, teammates struggling, captaincy, coming in during a collapse, recent form dip |
| **Opposition and tournament** | 12% | Opponent strength, batter–bowler difficulty, knockout matches, estimated league-table pressure |
| **Pitch, innings and toss** | 10% | Venue scoring history, batting or bowling first, opponent receiving a historically favourable toss choice |
| **Likely opposition strategy** | 9% | Scoreboard-inferred attacking chase, consolidation after wickets, controlled chase, or defensive survival |

The last category represents **inferred tactics from the scoreboard**, not a claim that we know what a player was thinking.

## How the ranking works

### Step 1 Prepare the data

Python and Pandas join the provided CSVs, filter the analysis dates and eligible IPL/T20I matches, clean delivery records, and separate batting from bowling events. Incomplete and revised-target matches that the model cannot evaluate consistently are excluded.

### Step 2 Measure pressure before the ball

For each delivery, the script estimates the difficulty of the situation using the six categories above. It distinguishes pressure on the **batter** from pressure on the **bowler**.

Pressure thresholds at the **68th, 73rd and 78th percentiles** are tested so the rankings do not depend on one definition of a high-pressure delivery.

### Step 3 Measure what the player actually did

A player's result is compared with expected performance in similar situations, taking into account format, innings, over phase, bowling style, pressure level and venue.

Simplified per-ball calculations:

- **Batting impact:** actual runs − expected runs − 6 × (actual striker dismissal − expected dismissal risk)
- **Bowling impact:** expected runs conceded − actual runs conceded + 6 × (credited wicket − expected wicket expectation)

The **6-run wicket value is a model assumption**, not an official cricket statistic. Expected outcomes are estimated retrospectively from the dataset.

### Step 4 Reward reliable performance

The final **recommended** score uses:

| Rating component | Weight |
| --- | ---: |
| Better-than-expected performance under pressure | **60%** |
| Improvement over the player's ordinary performance | **25%** |
| Consistency across pressure matches | **15%** |

Small samples are shrunk toward neutral estimates. Match consistency uses a conservative lower confidence bound. Scores from the three pressure thresholds are averaged with weights **25% / 50% / 25%**, with a penalty for instability across thresholds.

The underlying comprehensive benchmark also produces a richer seven-component diagnostic score; see [Factor Audit](FACTOR_AUDIT.md) and [Detailed Methodology](HACKATHON_RECOMMENDATION.md). The table above shows the **recommended final selection method**, not that separate diagnostic formula.

### Step 5 Check eligibility and robustness

For the final recommended shortlist, players must appear at all three pressure cutoffs, have at least **12 qualifying pressure matches**, and at the central cutoff have at least **135 high-pressure batting balls** or **150 high-pressure bowling balls**. The upstream model also applies IPL participation minimums.

These are **research thresholds, not official challenge eligibility rules**. Alternative rating weights are tested to see how many players stay in the top 10.

## Tools used

- **Python:** data processing, pressure calculations, ranking logic and reproducibility
- **Pandas:** joining, filtering, grouping and aggregating match records
- **NumPy:** numeric operations and pressure-related calculations
- **CSV and JSON:** saving player rankings, match summaries and sensitivity results
- **unittest:** basic automated tests of model behaviour

This is a **rules-based statistical benchmark**, not a trained machine-learning model.

## Run it yourself

**Requirements:** Python 3 and the supplied CSV files (not included in this repository).

```bash
git clone https://github.com/vipu18/superr.git
cd superr
python -m pip install -r requirements.txt
mkdir -p data
```

Place these four files in the `data/` directory:

```text
data/
├── ball_by_ball.csv
├── matches.csv
├── competitions.csv
└── competition_team_player_mapping.csv
```

Run the full benchmark and generate the final recommended rankings:

```bash
python comprehensive_pressure_rank.py
python check_comprehensive_sensitivity.py
python hackathon_recommended_rank.py
python -m unittest discover -s tests
```

**Output files:**

- `outputs/bat_hackathon_recommended_top10.csv` final top 10 batters
- `outputs/bowl_hackathon_recommended_top10.csv` final top 10 bowlers
- `outputs/bat_hackathon_recommended_full.csv` all qualifying batters
- `outputs/bowl_hackathon_recommended_full.csv`all qualifying bowlers
- `outputs/hackathon_recommendation_validation.json`alternative-weight stability checks
- `outputs/comprehensive_sensitivity.json` three pressure thresholds

The complete analysis can take longer than running the final ranking script alone. **Run the scripts in the listed order:** the final script needs the intermediate `q68`, `q73`, and `q78` ranking files produced by the sensitivity script.

## Project files

| File | Purpose |
| --- | --- |
| [`comprehensive_pressure_rank.py`](comprehensive_pressure_rank.py) | Builds pre-ball pressure features and initial player scores |
| [`check_comprehensive_sensitivity.py`](check_comprehensive_sensitivity.py) | Recalculates scores under three pressure definitions |
| [`hackathon_recommended_rank.py`](hackathon_recommended_rank.py) | Produces the conservative final rankings |
| [`HACKATHON_RECOMMENDATION.md`](HACKATHON_RECOMMENDATION.md) | Detailed explanation of final ratings and results |
| [`FACTOR_AUDIT.md`](FACTOR_AUDIT.md) | Which pressure factors are measurable and which are not |
| [`tests/`](tests/) | Basic automated tests |

## Limitations and assumptions

The model has important boundaries:

- **Not scored:** sledging, actual thoughts or instructions, medical fitness, confirmed risk of being dropped, future team contracts, and comprehensive domestic-league form.
- **Estimated, not exact:** playoff/qualification stakes and net-run-rate pressure, because a complete official standings ledger is not supplied. An exact requirement such as *win within 14 overs* is not reconstructed.
- **Tactics are inferred:** attacking or defensive labels reflect scorecard conditions, not verified player mentality.
- **Venue and toss features are observational:** historical outcomes do not prove the toss itself caused an advantage.
- **Current code excludes players representing Pakistan** based on an additional user-selected filter. This is **not an official Round 1 rule**. The upstream model also requires a minimum IPL sample.
- **No independent future-season validation:** peer expectations and scoring choices are retrospective; sensitivity checks do not establish predictive accuracy.

Do not interpret small differences in ranking scores as conclusive proof that one player is better than another.

## Data and usage

The supplied ball-by-ball and supporting datasets are **not redistributed** here. Add them locally only if your rights to the data permit it.

This repository is intended as a transparent, reproducible approach to the **overall question: who performs most consistently under pressure?**
