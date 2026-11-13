# Optional Rajasthan Royals current-squad exclusion

**Date checked:** 13 November 2026.

This is an **optional eligibility filter**, not a change to the underlying pressure model or its score weights. Players from the 2026 Rajasthan Royals roster (including season replacements and the Sam Curran contract) are excluded **after** the overall rankings are calculated.

The upcoming IPL 2027 retention/release list was not final on this date. This filter does not mean that everybody remaining is available at auction; many remaining players are under contract with other franchises.

## Reproduce
```bash
python comprehensive_pressure_rank.py
python check_comprehensive_sensitivity.py
python hackathon_recommended_rank.py
python exclude_current_rr_squad.py
```
Full filtered data and excluded-player audits are written to `outputs/`. The committed top-10 snapshots list the same ranking rounded to two decimals.

**Result:** Donovan Ferreira drops from the batting top ten, Rovman Powell enters at rank ten. Bowling top ten is unchanged. Across the complete eligible pools, five batting candidates and five bowling candidates are removed.

**Sources:**
- https://www.rajasthanroyals.com/rr-players
- https://www.rajasthanroyals.com/latest-news/rajasthan-royals-vs-lucknow-super-giants-rr-lsg-ipl-2026-match-preview
- https://www.iplt20.com/news/article/tata-ipl-2026-player-retentions-announced
