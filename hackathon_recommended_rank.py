#!/usr/bin/env python3
"""Hackathon recommended leaderboard: robust pressure excess/uplift/consistency."""
import csv, math, json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
QUANTILES = (68, 73, 78)
WQ = (.25, .50, .25)
BASE = (.60, .25, .15)
MIN = {"bat":(135,12), "bowl":(150,12)}

def clamp(x,lo,hi): return max(lo,min(hi,float(x)))

def wilson(p,n,z=1.28155):
    if n <= 0: return 0.
    z2=z*z
    return (p+z2/(2*n)-z*math.sqrt(p*(1-p)/n+z2/(4*n*n)))/(1+z2/n)

def cutoff_score(r,weights=BASE):
    n=float(r["pressure_balls"])
    matches=float(r["pressure_matches"])
    rate=float(r["pressure_rate_per100"])
    ordinary=float(r["normal_rate_per100"])
    positive=float(r["match_consistency_pct"])/100
    excess=clamp(rate,-60,60)*n/(n+110)
    uplift=clamp(rate-ordinary,-45,45)*n/(n+130)
    reliability=50*(wilson(positive,matches)-.40)
    return weights[0]*excess+weights[1]*uplift+weights[2]*reliability

def rank(role,weights=BASE):
    data={}
    for q in QUANTILES:
        with (OUT/f"{role}_comprehensive_q{q}.csv").open(newline="",encoding="utf-8") as f:
            for row in csv.DictReader(f):
                data.setdefault(row["player_id"],{})[q]=row
    results=[]
    for pid,rec in data.items():
        if set(rec) != set(QUANTILES): continue
        r=rec[73]
        if int(r["pressure_balls"]) < MIN[role][0] or int(r["pressure_matches"]) < MIN[role][1]: continue
        qs=[cutoff_score(rec[q],weights) for q in QUANTILES]
        mean=sum(a*b for a,b in zip(WQ,qs))
        penalty=.15*(max(qs)-min(qs))
        results.append(dict(player=r["player"], player_id=pid,
          score=round(mean-penalty,4),pressure_balls=int(r["pressure_balls"]),
          pressure_matches=int(r["pressure_matches"]),
          positive_match_pct=float(r["match_consistency_pct"]),
          pressure_rate_per100=float(r["pressure_rate_per100"]),
          normal_rate_per100=float(r["normal_rate_per100"]),
          score_q68=round(qs[0],4),score_q73=round(qs[1],4),score_q78=round(qs[2],4),
          instability_penalty=round(penalty,4),
          ipl_matches=int(r["ipl_matches"]),t20i_matches=int(r["t20i_matches"])))
    results.sort(key=lambda x:(-x["score"],-x["pressure_balls"],x["player"]))
    for i,r in enumerate(results,1): r["rank"]=i
    return results

def save(path,rows):
    fields=["rank"]+[k for k in rows[0] if k!="rank"]
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

if __name__=="__main__":
    checks={}
    for role in ("bat","bowl"):
        base=rank(role)
        if not base: raise RuntimeError("No eligible players: generate q68/q73/q78 first")
        save(OUT/f"{role}_hackathon_recommended_full.csv",base)
        save(OUT/f"{role}_hackathon_recommended_top10.csv",base[:10])
        selected={r["player"] for r in base[:10]}
        scenarios={"pressure_first":(.75,.15,.10),
                   "uplift_first":(.48,.42,.10),
                   "consistency_first":(.50,.20,.30)}
        checks[role]={label:len(selected & {r["player"] for r in rank(role,weights)[:10]})
                      for label,weights in scenarios.items()}
        for row in base[:10]:
            print(role,row["rank"],row["player"],row["score"])
    (OUT/"hackathon_recommendation_validation.json").write_text(
        json.dumps({"weight_sensitivity_top10_overlap":checks,
                    "warning":"Retrospective research model, not out-of-time validated."},indent=2))
