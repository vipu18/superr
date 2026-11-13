#!/usr/bin/env python3
"""Optionally exclude players in Rajasthan Royals' IPL 2026 roster from final pressure rankings.

Snapshot checked 2026-11-13. This is NOT the eventual 2027 retention list.
Sources:
- https://www.rajasthanroyals.com/rr-players
- https://www.rajasthanroyals.com/latest-news/rajasthan-royals-vs-lucknow-super-giants-rr-lsg-ipl-2026-match-preview
- https://www.iplt20.com/news/article/tata-ipl-2026-player-retentions-announced
"""
from pathlib import Path
import csv

OUT = Path(__file__).resolve().parent / "outputs"
RR_2026 = {
    "Adam Milne", "Aman Rao", "Aman Perala", "Brijesh Sharma",
    "Dasun Shanaka", "Emanjot Chahal", "Dhruv Jurel", "Donovan Ferreira",
    "Jofra Archer", "Kuldeep Sen", "Kwena Maphaka", "Lhuan-dre Pretorius",
    "Nandre Burger", "Ravi Bishnoi", "Ravi Singh", "Ravindra Jadeja",
    "Riyan Parag", "Sandeep Sharma", "Shimron Hetmyer", "Shubham Dubey",
    "Sushant Mishra", "Tushar Deshpande", "Vaibhav Sooryavanshi",
    "Vignesh Puthur", "Yash Raj Punja", "Yash Punja", "Yashasvi Jaiswal",
    "Yudhvir Singh", "Yudhvir Singh Charak", "Sam Curran"
}

def normalize(value):
    return "".join(c for c in value.casefold() if c.isalnum())

EXCLUDE = {normalize(p) for p in RR_2026}

def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    for kind in ("bat", "bowl"):
        src = OUT / f"{kind}_hackathon_recommended_full.csv"
        with src.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames)
            rows = list(reader)
        available = [r for r in rows if normalize(r["player"]) not in EXCLUDE]
        excluded = [r for r in rows if normalize(r["player"]) in EXCLUDE]
        for new_rank, row in enumerate(available, 1):
            row["rank"] = new_rank
        write_csv(OUT / f"{kind}_excluding_current_rr_full.csv", available, fields)
        write_csv(OUT / f"{kind}_excluding_current_rr_top10.csv", available[:10], fields)
        write_csv(OUT / f"{kind}_excluded_rr_players.csv", excluded, fields)
        print(f"{kind}: {len(excluded)} squad players excluded; {len(available)} eligible")
        for row in available[:10]:
            print(row["rank"], row["player"], round(float(row["score"]), 2))

if __name__ == "__main__":
    main()
