# Rajasthan Royals scouting shortlist, 18 November 2026

The 2024–November 2026 rerun used 484 completed, eligible IPL and men's T20I matches and 114,946 deliveries from the supplied CSVs. Actual match dates range from 11 January 2024 to 1 November 2026. Run `python rank_scouting.py` and `python -m unittest discover -s tests` from the project root.

## Performance

The script estimates pre-delivery pressure with the existing comprehensive model, including required rate, wickets, balls left, recent momentum, phase, opposition, toss and venue scoring history. The same benchmark estimates expected runs and wickets from format, innings, phase, bowling type, pressure band and venue. Expectations are retrospective and exclude the evaluated delivery from the local sums. A wicket carries six runs of impact. Bowling observations include illegal deliveries. Batting observations exclude wides.

Rates are weighted by season, with a factor of 0.84 for each year before 2026. At each role-specific 68th, 73rd and 78th pressure percentile, 55% of the rating comes from the existing shrinkage-adjusted pressure excess, uplift over ordinary performance and match consistency formula. The other components are IPL pressure performance (15%), 2025–26 IPL form (15%), pressure performance in India (10%) and 2026 T20I form (5%). Each uses expected-adjusted impact per 100 observations with a 100-observation neutral prior. No observations contribute zero. Components intentionally overlap to emphasize the target competition. The three cutoff scores receive weights of 25%, 50% and 25%, followed by a penalty of 15% of their range.

## Rajasthan venues

The Jaipur and Guwahati IDs in the supplied matches file are 6 and 1241. Cross-check the [Jaipur fixture](https://www.iplt20.com/matches/fae1b499-16f4-4271-a2fc-04dae75424b2/rajasthan-royals-vs-lucknow-super-giants/match-details) and [Guwahati fixture](https://www.iplt20.com/matches/ecdc5958-43b9-418b-87b2-f8181cc6c9dc/rajasthan-royals-vs-punjab-kings/match-details). Count all central-cutoff pressure observations at either ground, regardless of opponent or competition. Add 10% of their shrunk positive impact per 100 observations, capped at three index points. A player with zero local evidence receives zero bonus. Counts at each ground are printed separately so readers can distinguish no exposure from a non-positive result. The bonus measures observed local performance. It cannot measure future pitch preparation or dew.

## Evidence and availability

All players are evaluated before roster filtering, with no minimum IPL appearances. Tier 1 requires 46 pressure observations, 75 ordinary observations and five qualifying pressure matches at each cutoff. Tier 2 requires 20, 40 and three respectively. A qualifying match contains at least three pressure observations. These scouting thresholds broaden the original recommendation pool. Tier 1 precedes Tier 2, then scores sort descending. Tier 2 fills open places with explicitly lower-confidence candidates. Scores can be negative.

The final shortlist admits only known releases in the supplied ten-team snapshot, keyed by player ID. Players outside the snapshot need a separate availability check before admission. Pakistan representatives, retired players and known withdrawals are excluded. Other releases are provisional. Mustafizur Rahman's registration was reported. Full-season commitments, medical clearance and domestic form outside the supplied IPL/T20I data are unverified. Update the roster CSV and rerun if an availability decision changes.

Sources for availability include the [retention lists](https://www.wisden.com/series/ipl-2027/cricket-news/ipl-2027-retention-list-full-list-retained-released), [Head, Starc and Bethell report](https://www.reuters.com/sports/cricket/head-starc-among-players-released-before-ipl-2027-auction-2026-11-17/) and [Mustafizur registration reporting](https://www.indiatoday.in/sports/cricket/story/ipl-2027-mini-auction-bangladesh-mustafizur-rahman-exclusive-kkr-release-3036897-2026-11-11).

The two output CSVs contain the full scored release lists, including before/after ranks, cutoff sensitivity, recent-form samples and evidence tiers. These are custom RR scouting lists. Round 1 itself asks for overall pressure rankings.
