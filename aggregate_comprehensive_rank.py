#!/usr/bin/env python3
"""Robust consensus leaderboard across 68th, 73rd, 78th pressure percentiles.
Average within-cohort percentile ranks, requiring eligibility in all 3 cohorts.
No RR home-ground points. Demonstrates sensitivity rather than claiming exact rank.
"""
import json
from pathlib import Path
import pandas as pd
OUT=Path(__file__).resolve().parent/'outputs'
for role in ('bat','bowl'):
    tables={q:pd.read_csv(OUT/f'{role}_comprehensive_q{q}.csv') for q in (68,73,78)}
    common=set.intersection(*(set(a.player_id) for a in tables.values()))
    ranker=pd.DataFrame({'player_id':sorted(common)})
    for q,df in tables.items():
        df=df[['player_id','score','rank','pressure_balls','match_consistency_pct']].copy()
        df[f'percentile_q{q}']=100*(1-(df['rank']-1)/max(1,len(df)-1))
        df=df.rename(columns={'score':f'score_q{q}','rank':f'rank_q{q}','pressure_balls':f'pressure_balls_q{q}',
                              'match_consistency_pct':f'match_consistency_pct_q{q}'})
        ranker=ranker.merge(df,on='player_id',how='left')
    # q73 is central percentile but all three counted.
    ranker['consensus_index']=.25*ranker.percentile_q68+.5*ranker.percentile_q73+.25*ranker.percentile_q78
    primary=tables[73].drop(columns=['rank','score','pressure_balls','match_consistency_pct'])
    primary=primary.rename(columns={'player':'player'})
    ranker=ranker.merge(primary,on='player_id')
    ranker=ranker.sort_values('consensus_index',ascending=False).reset_index(drop=True)
    ranker.insert(0,'rank',range(1,len(ranker)+1))
    first=['rank','player','consensus_index','rank_q68','rank_q73','rank_q78','score_q73','pressure_balls_q73','match_consistency_pct_q73']
    ranker[first+[x for x in ranker.columns if x not in first]].to_csv(OUT/f'{role}_comprehensive_consensus.csv',index=False)
    print('\n'+role.upper()+' CONSENSUS')
    print(ranker[first].head(15).to_string(index=False,float_format=lambda x:f'{x:.2f}'))