#!/usr/bin/env python3
"""Exclude players on any current IPL squad; audited 2026 rosters, 2026-11-13.

This filter applies AFTER the overall pressure ranking. It does not estimate
2027 auction eligibility. Refuses to assume unverified candidate names are free.
Reference: https://www.ipl.com/series/indian-premier-league-2026-129908/squad
2027 trades: https://www.moneycontrol.com/sports/cricket/ipl/ipl-2027-complete-list-of-players-traded-so-far-when-is-the-retention-deadline-article-14077857.html
"""
import csv, json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
# Candidate-level audited roster subset: all names appearing in current
# recommended batting/bowling full-ranking datasets.
SQUAD_PLAYERS = {
    "CSK": "Shivam Dube;Jamie Overton;Noor Ahmad;Anshul Kamboj;Khaleel Ahmed",
    "DC": "Tristan Stubbs;David Miller;Lokesh Rahul;Axar Patel;Mitchell Starc;Lungi Ngidi;Rishabh Pant;Dushmantha Chameera;Mukesh Kumar",
    "GT": "Jos Buttler;Washington Sundar;Rahul Tewatia;Jason Holder;Mohammed Siraj;Prasidh Krishna;Kagiso Rabada;Rashid Khan",
    "KKR": "Rovman Powell;Rinku Singh;Cameron Green;Sunil Narine;Varun Chakravarthy;Vaibhav Arora;Matheesha Pathirana;Harshit Rana",
    "LSG": "Ayush Badoni;Aiden Markram;Nicholas Pooran;Kuldeep Yadav;Wanindu Hasaranga;Avesh Khan;Mayank Yadav;Prince Yadav;Anrich Nortje;Digvesh Rathi",
    "MI": "Naman Dhir;Tilak Varma;Suryakumar Yadav;Sherfane Rutherford;Hardik Pandya;Jasprit Bumrah;Trent Boult;Shardul Thakur;Mitchell Santner",
    "PBKS": "Shreyas Iyer;Shashank Singh;Marcus Stoinis;Azmatullah Omarzai;Marco Jansen;Arshdeep Singh;Yuzvendra Chahal;Lockie Ferguson",
    "RR": "Donovan Ferreira;Riyan Parag;Ravindra Jadeja;Dhruv Jurel;Shimron Hetmyer;Jofra Archer;Tushar Deshpande;Ravi Bishnoi;Sandeep Sharma;Sam Curran",
    "RCB": "Jitesh Sharma;Tim David;Rasikh Salam;Josh Hazlewood;Yash Dayal;Suyash Sharma;Jacob Duffy;Nuwan Thushara;Krunal Pandya;Romario Shepherd;Bhuvneshwar Kumar",
    "SRH": "Heinrich Klaasen;Liam Livingstone;Ishan Kishan;Nitish Reddy;Eshan Malinga;Harshal Patel;Gerald Coetzee;Patrick Cummins;T Natarajan",
}
UNCONTRACTED = {
    "Mustafizur Rahman": "KKR contract terminated; 2027 auction registration reported",
    "Mohit Sharma": "Released by DC before IPL 2026",
    "Naveen ul Haq": "Not auctioned in IPL 2026",
    "Maheesh Theekshana": "Unsold in IPL 2026",
}
RETIRED = {"Andre Russell": "Retired from IPL in November 2025"}

def key(name):
    return "".join(c for c in name.lower() if c.isalnum())

def csv_save(path, records, columns):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(records)

def main():
    roster = {}
    for team, names in SQUAD_PLAYERS.items():
        for name in names.split(";"):
            ident=key(name)
            if ident in roster: raise ValueError("Duplicate roster entry " + name)
            roster[ident]=team
    free={key(name):note for name,note in UNCONTRACTED.items()}
    retired={key(name):note for name,note in RETIRED.items()}
    audit=[]
    summary={"snapshot":"2026-11-13", "retention_deadline":"2026-11-17",
             "scope":"all 10 IPL team squads","roles":{}}
    for role in ("bat","bowl"):
        with (OUT/f"{role}_hackathon_recommended_full.csv").open(
                encoding="utf-8", newline="") as f:
            reader=csv.DictReader(f)
            columns=reader.fieldnames
            candidates=list(reader)
        keep=[]; excluded=[]; unavailable=[]
        for r in candidates:
            p=key(r["player"])
            if p in roster:
                status="current_ipl_squad"; team=roster[p]; note="Roster listing"
                excluded.append(r)
            elif p in retired:
                status="retired"; team=""; note=retired[p]; unavailable.append(r)
            elif p in free:
                status="uncontracted"; team=""; note=free[p]; keep.append(r.copy())
            else:
                raise ValueError("Unverified candidate; review squad status first: " + r["player"])
            audit.append({"role":role,"overall_rank":r["rank"],"player":r["player"],
                          "score":r["score"],"team":team,"status":status,"reason":note})
        for idx,r in enumerate(keep,1):r["rank"]=str(idx)
        for suffix,rows in [("no_current_ipl_team_full",keep),
                             ("no_current_ipl_team_top10",keep[:10]),
                             ("excluded_all_ipl_squads",excluded),
                             ("ipl_retired_or_unavailable",unavailable)]:
            csv_save(OUT/f"{role}_{suffix}.csv",rows,columns)
        summary["roles"][role]={"initial":len(candidates),"excluded_in_team":len(excluded),
                                "retired":len(unavailable),"remaining":len(keep)}
        for r in keep:print(role,r["rank"],r["player"],r["score"])
    csv_save(OUT/"all_ipl_squads_candidate_audit.csv",audit,
             ["role","overall_rank","player","score","team","status","reason"])
    (OUT/"all_ipl_squads_filter_summary.json").write_text(
         json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
