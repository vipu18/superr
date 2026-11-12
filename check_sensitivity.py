#!/usr/bin/env python3
"""Sensitivity to pressure label percentile; rank again from same pre-ball events."""
import json
from pathlib import Path
from advanced_pressure_rank import data_load,match_context,pressure_rows,add_expected,rankings,OUT,read
mm,bb,links=data_load()
d,states=pressure_rows(mm,bb,match_context(mm,bb))
d,base_threshold=add_expected(d)
excluded=set(links.loc[links.team_name.astype(str).str.casefold().eq('pakistan'),'player_id'].astype(int))
comparisons={}
for q in [0.68,0.73,0.78]:
    for role in ['bat','bowl']:
        d['pressure_'+role]=d['p_'+role]>=d['p_'+role].quantile(q)
    rr=rankings(d,excluded)
    for role in ['bat','bowl']:
        rr[role].to_csv(OUT/f'{role}_pressure_q{int(q*100)}.csv',index=False)
    comparisons[str(q)]={'bat':rr['bat'].player.head(10).tolist(),'bowl':rr['bowl'].player.head(10).tolist()}
base=comparisons['0.73']
result={'thresholds':comparisons,'top10_overlap':{str(q):{role:len(set(comparisons[str(q)][role])&set(base[role])) for role in ('bat','bowl')} for q in (0.68,0.78)}}
(OUT/'pressure_sensitivity.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
