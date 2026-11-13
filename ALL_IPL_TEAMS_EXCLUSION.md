# Exclude all current IPL teams — optional post-ranking filter

Snapshot checked **13 November 2026**. The complete 2027 retention/release decisions are not due until **17 November 2026**, so these are provisional `2026 IPL squad` exclusions, updated for the reported 2027 trades. An excluded current squad player could be released later, and an uncontracted player is not automatically auction-eligible.

The pressure model and its scoring weights are **unchanged**. This post-filter applies to the conservative recommendation output at `outputs/{bat,bowl}_hackathon_recommended_full.csv`. It audits every candidate and fails on an unknown player's roster status instead of assuming that player is available.

| Role | Previously ranked | Current IPL squad | IPL-retired | Remaining |
|---|---:|---:|---:|---:|
| Batters | 37 | 36 | 1 | **0** |
| Bowlers | 61 | 56 | 1 | **4** |

Remaining bowlers, in pressure-score order:

1. Mustafizur Rahman **+2.46** — KKR contract terminated; reported registration for 2027 auction.
2. Mohit Sharma **−1.80** — DC released before IPL 2026.
3. Naveen-ul-Haq **−6.08** — no IPL 2026 franchise.
4. Maheesh Theekshana **−9.45** — unsold in IPL 2026.

**Andre Russell** has no current player contract but is explicitly excluded because he retired from the IPL. There is **no legitimate top 10** from the current conservative eligibility pool: the ranking engine requires prior IPL participation, so expanding to 10 unattached batters/bowlers requires a separately validated broader T20I/domestic-player model. Negative scores are not probabilities.

Run after `python hackathon_recommended_rank.py`:

```bash
python exclude_all_ipl_squads.py
```

Outputs are separate and do **not overwrite** overall rankings. Candidate audit: `outputs/all_ipl_squads_candidate_audit.csv`.

Sources:
- [All 10 IPL 2026 rosters](https://www.ipl.com/series/indian-premier-league-2026-129908/squad)
- [Reported 2027 trades and retention deadline](https://www.moneycontrol.com/sports/cricket/ipl/ipl-2027-complete-list-of-players-traded-so-far-when-is-the-retention-deadline-article-14077857.html)
- [Mustafizur registration and termination](https://www.indiatoday.in/sports/cricket/story/ipl-2027-mini-auction-bangladesh-mustafizur-rahman-exclusive-kkr-release-3036897-2026-11-11)
- [Andre Russell IPL retirement](https://www.reuters.com/sports/cricket/russell-retires-ipl-joins-kkrs-coaching-department-2025-11-30/)
- [Theekshana 2026 unsold](https://www.cricbuzz.com/cricket-series/ipl-2026/auction/players/18504)
- [Naveen 2026 unauctioned](https://www.cricbuzz.com/cricket-series/ipl-2026/auction/players/11289)
- [Mohit 2026 release](https://www.indiatoday.in/sports/cricket/story/ipl-2026-retentions-full-list-players-mini-auction-purse-remaining-2820429-2025-11-15)
