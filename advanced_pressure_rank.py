#!/usr/bin/env python3
"""SupeRR v2: scoreboard-observable multi-dimensional pressure benchmark.
Date scope: 2024-01-01 through 2026-11-12. No RR ranking bonus.

IMPORTANT: tactical labels are *proxies* inferred from match states. They are not
claims about a player's thoughts or real-time team instructions. Prospective
qualification NRR targets, sledging, fitness and selection threats are NOT scored.
"""
from __future__ import annotations
import csv, json, math, statistics
from collections import defaultdict, deque, Counter
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
DATE_BEGIN='2024-01-01';DATE_END='2026-11-12'
TIME_WEIGHT={2024:.78,2025:.89,2026:1.0}
WICKET_RUN_VALUE=6.0

def clamp(x,a=0.,b=1.):return max(a,min(b,float(x)))
def sigmoid(x):return 1/(1+math.exp(-max(-30,min(30,x))))
def smooth_rate(impact,balls,k=90,limit=75):
    return (balls/(balls+k))*clamp(100*impact/max(1e-8,balls),-limit,limit)
def read(name):return pd.read_csv(DATA/name,low_memory=False)

def data_load():
    cm=read('competitions.csv');mm=read('matches.csv');bb=read('ball_by_ball.csv')
    cm['fmt']=np.where(cm.comp_name.astype(str).str.startswith('IPL '),'IPL',np.where(cm.match_format=='T20I','T20I',''))
    mm=mm.merge(cm[['comp_id','fmt','comp_name']],on='comp_id',how='left')
    mm['match_date']=pd.to_datetime(mm.match_date,errors='coerce')
    mm['valid']=mm.fmt.isin(['IPL','T20I']) & mm.win_team_id.notna() & (mm.match_date>=DATE_BEGIN)&(mm.match_date<=DATE_END) & mm.first_inn_revised_overs.isna() & mm.second_inn_revised_overs.isna() & mm.revised_target.isna()
    bb=bb[bb.match_id.isin(mm.loc[mm.valid,'match_id'])&bb.innings.isin([1,2])].copy()
    bb['runs']=pd.to_numeric(bb.runs,errors='coerce').fillna(0).astype(float)
    bb['extra']=pd.to_numeric(bb.extras1_runs,errors='coerce').fillna(0)+pd.to_numeric(bb.extras_2_runs,errors='coerce').fillna(0)
    bb['runs_all']=bb.runs+bb.extra
    bb['legal']=~bb.extras_type.isin(['wide','Overstep'])
    bb['bat_ball']=(bb.extras_type!='wide')
    bb['runs_bowler']=bb.runs+np.where(bb.extras_type.isin(['byes','legbyes','Penalty']),0,bb.extra)
    bb['wicket_flag']=bb.is_wicket.astype(str).str.lower().eq('true')
    bb['wicket_bowler']=bb.wicket_flag&bb.dismissal_type.isin(['Caught','Bowled','LBW','Stump','Hit Wicket'])
    bb['striker_out']=(bb.wicket_flag & (bb.striker_id==bb.dismissed_player_id) & ~bb.dismissal_type.isin(['Retire Out','Retired Out']))
    bb=bb.sort_values(['match_id','innings','innings_ball_num','overid','over_ball_num'],kind='stable')
    eligible=[]
    for (mid,inn),g in bb.groupby(['match_id','innings'],sort=False):
        if len(g)>=19:eligible.append((mid,inn))
    inc=set(eligible)
    full={mid for mid,inn in eligible if inn==1}&{mid for mid,inn in eligible if inn==2}
    full={mid for mid in full if bb[(bb.match_id==mid)&(bb.innings==1)].legal.sum()>=36}
    mm=mm[mm.match_id.isin(full)].copy();bb=bb[bb.match_id.isin(full)].copy()
    return mm,bb,read('competition_team_player_mapping.csv')

def match_context(mm,bb):
    # Pre-match rolling team strength, venue scoring and toss history.
    results=defaultdict(lambda:deque(maxlen=10));venue_scores=defaultdict(lambda:deque(maxlen=25)); venue_chases=defaultdict(lambda:deque(maxlen=25))
    league=defaultdict(lambda:defaultdict(lambda:[0,0]))
    innings1=bb[bb.innings==1].groupby('match_id').agg(first_runs=('runs_all','sum'),first_legal=('legal','sum')).to_dict('index')
    meta={}
    for m in mm.sort_values(['match_date','match_id']).itertuples():
        fmt=m.fmt; venue=str(m.venue_id); key=(fmt,venue)
        home=int(m.home_team_id);away=int(m.away_team_id);w=int(m.win_team_id);toss=int(m.toss_win_team_id) if pd.notna(m.toss_win_team_id) else 0
        hs=(sum(results[(fmt,home)])+4)/(len(results[(fmt,home)])+8)
        as_=(sum(results[(fmt,away)])+4)/(len(results[(fmt,away)])+8)
        vs=venue_scores[key]; vc=venue_chases[key]
        par=(sum(vs)+8*8.7)/(len(vs)+8)
        chase_p=(sum(vc)+6)/(len(vc)+12)
        fav=('Fielding' if chase_p>.54 else 'Batting' if chase_p<.46 else None) if len(vc)>=6 else None
        ownstrength={home:hs,away:as_};
        k=m.comp_id; league_games=league[k]
        if fmt=='IPL' and str(m.stage).lower()=='league':
            all_teams=[u for u,cnt in league_games.items() if cnt[0]>0]
            ranked=sorted(all_teams,key=lambda x:(league_games[x][1]/league_games[x][0],league_games[x][1]),reverse=True)
            for t in (home,away):
                games=league_games[t][0]
                rk=ranked.index(t)+1 if t in ranked else 5
                ownstrength.setdefault('stake_'+str(t),clamp((games-8)/6)*(.65 if rk in range(3,8) else .38))
        def team_stake(t):return ownstrength.get('stake_'+str(t),0)
        meta[m.match_id]=dict(fmt=fmt,venue=venue,par=par,first_score=innings1[m.match_id]['first_runs'],
          winner=w,toss=toss,decision=m.toss_opted,opp_adv=bool(fav and toss and fav==m.toss_opted),
          playoff=str(m.stage).lower() in ('final','semi final','qualifier','eliminator') or bool(m.knock_out),
          strength=ownstrength,stake={home:team_stake(home),away:team_stake(away)},home=home,away=away,
          chase_prior=chase_p,toss_sample=len(vc))
        if w in (home,away):
            results[fmt,home].append(int(w==home));results[fmt,away].append(int(w==away))
            if fmt=='IPL':
                for t in (home,away):league[k][t][0]+=1;league[k][t][1]+=int(t==w)
        x=innings1[m.match_id]
        if x['first_legal']>=90:
            venue_scores[key].append(x['first_runs']*6/x['first_legal'])
        if toss and m.toss_opted in ['Fielding','Batting']:
            chase_team=toss if m.toss_opted=='Fielding' else (away if toss==home else home)
            venue_chases[key].append(int(w==chase_team))
    return meta

def pressure_rows(mm,bb,meta):
    rows=[]; tactical_counts=Counter(); feats=Counter()
    for (mid,inn),g in bb.groupby(['match_id','innings'],sort=False):
        m=meta[mid];runs=0;wk=0;legal=0;recent=deque(maxlen=12);last_wicket=-1000
        bats=Counter(); bowler_runs=Counter();bowler_legal=Counter();bowler_wks=Counter()
        bowler_recent=defaultdict(lambda:deque(maxlen=3));striker_dot=Counter()
        target=m['first_score']+1;par=m['par']; playoff=m['playoff']; team=m['home']
        for r in g.itertuples(index=False):
            bat=int(r.batting_team_id);bowl=int(r.bowling_team_id)
            striker=int(r.striker_id);bol=int(r.bowler_id)
            balls_left=max(1,120-legal);stage=legal/120
            wstress=clamp((wk-1)/6);recent_wks=sum(q[1] for q in recent)
            last6_runs=sum(q[0] for q in list(recent)[-6:]);last12_runs=sum(q[0] for q in recent)
            recent_run_rate=last6_runs*6/max(1,min(6,len(recent)))
            low_over=clamp((par-recent_run_rate)/5)
            wicket_shock=clamp(.65*recent_wks/2+.35*math.exp(-max(0,legal-last_wicket)/8))
            batting_carried=bats[striker]/max(40,runs)*clamp((runs-25)/45)
            top_other=max([v for p,v in bats.items() if p!=striker] or [0])
            carry=clamp((batting_carried-.34)/.40)*clamp((bats[striker]-top_other)/25)
            bowl_carry=clamp((bowler_wks[bol]-1)/3)*clamp((wk-1)/5)
            economy=6*bowler_runs[bol]/max(1,bowler_legal[bol]) if bowler_legal[bol]>=6 else par
            bowl_expensive=clamp((economy-par-1)/5)*clamp((bowler_legal[bol]-6)/18)
            boundary_streak=clamp(sum(1 for x in bowler_recent[bol] if x>=4)/2)
            dot_pressure=clamp(striker_dot[striker]/5)
            weak_opp=clamp((.49-m['strength'].get(bowl,.5))/.18)
            strong_opp=clamp((m['strength'].get(bowl,.5)-.51)/.18)
            own_weak=clamp((.49-m['strength'].get(bat,.5))/.18)
            own_strong=clamp((m['strength'].get(bat,.5)-.51)/.18)
            upset=clamp((m['strength'].get(bat,.5)-m['strength'].get(bowl,.5)-.12)/.30)
            bat_lost=(m['toss']==bowl and m['opp_adv'])
            bowl_lost=(m['toss']==bat and m['opp_adv'])
            stakes=(.8 if playoff else max(m['stake'].get(bat,0),m['stake'].get(bowl,0)))
            if inn==2:
                need=max(0,target-runs); rrr=need*6/balls_left
                chase_over=clamp((rrr-par+.3)/5)
                if wk>=7 and rrr>par+5: state='survival'
                elif recent_wks>=2 and rrr<par+2.2:state='consolidation'
                elif rrr>par+2.4 or target>=205 and rrr>par+.4:state='attack'
                elif rrr<par-2.0 and wk<=3:state='controlled'
                else:state='balanced'
                # Scoreboard leverage: close to a realistic scoring path with innings expiring.
                projected_gap=abs(need-balls_left*par/6)
                tight=clamp(1-projected_gap/(15+.40*balls_left))*clamp((stage-.22)/.65)
                match_s= .28*chase_over+.25*wstress+.24*stage+.23*tight
                bowldef=clamp((par-rrr+2)/5)*clamp((1-stage)/.7)
                bow_match=.27*stage+.25*clamp((need/balls_left*6-par)/5)+.25*bowldef+.23*clamp((wk-1)/6)
                # Once victory becomes vanishingly unlikely the context is not a live winning-pressure opportunity.
                near_lost=(wk>=7 and rrr>=par+9 and balls_left<=48)
                if near_lost:match_s*=.62;bow_match*=.60
                tactic_bat={'attack':.95,'consolidation':.70,'survival':.20,'controlled':.20,'balanced':.40}[state]
                tactic_bowl={'attack':.90,'consolidation':.55,'survival':.10,'controlled':.75,'balanced':.40}[state]
            else:
                rr_now=runs*6/max(6,legal)
                pace_lag=clamp((par-rr_now+.4)/5)
                state='first_innings'
                match_s=.35*clamp((stage-.35)/.65)+.32*wstress+.33*pace_lag
                bow_match=.35*clamp((stage-.35)/.65)+.32*clamp((rr_now-par+1)/6)+.33*wstress
                tactic_bat=clamp(.25+.45*pace_lag+.30*stage)
                tactic_bowl=clamp(.25+.45*clamp((rr_now-par)/5)+.30*stage)
            momentum_bat=clamp(.50*low_over+.29*wicket_shock+.21*dot_pressure)
            momentum_bowl=clamp(.42*boundary_streak+.38*bowl_expensive+.20*clamp((recent_run_rate-par)/5))
            # Do not assume a team's mental state. Tactical state is a SCOREBOARD proxy.
            strong_batting_opp=clamp((m['strength'].get(bat,.5)-.51)/.18)
            opp_bat=.50*strong_opp+.25*upset+.25*own_weak
            opp_bowl=.65*strong_batting_opp+.35*clamp((m['strength'].get(bowl,.5)-m['strength'].get(bat,.5)-.12)/.3)
            bat_conds=.60*float(bat_lost)+.40*clamp((par-9.0)/2)
            bowl_conds=.60*float(bowl_lost)+.40*clamp((par-8.0)/2)
            bat_resp=.64*carry+.36*clamp(recent_wks/2)
            bowl_resp=.55*bowl_carry+.45*clamp((1.2*bowler_wks[bol]-wk/5)/3)
            p_bat=clamp(.42*match_s+.14*momentum_bat+.13*bat_resp+.12*(.48*stakes+.52*opp_bat)+.10*bat_conds+.09*tactic_bat)
            p_bowl=clamp(.42*bow_match+.14*momentum_bowl+.13*bowl_resp+.12*(.48*stakes+.52*opp_bowl)+.10*bowl_conds+.09*tactic_bowl)
            if inn==2 and state=='survival':p_bat*=.74;p_bowl*=.62
            d={'match_id':mid,'date':str(r.match_id) if False else None,'innings':inn,'fmt':m['fmt'],'venue_id':m['venue'],'phase':'PP' if legal<36 else 'MID' if legal<90 else 'DEATH',
               'pace_spin':r.pace_or_spin if r.pace_or_spin in ('Pace','Spin') else 'Other',
               'batting_team_id':bat,'bowling_team_id':bowl,'striker_id':striker,'striker_name':r.striker_name,'bowler_id':bol,'bowler_name':r.bowler_name,
               'bat_runs':float(r.runs),'bowl_runs':float(r.runs_bowler),'striker_out':int(r.striker_out),'bowler_wicket':int(r.wicket_bowler),
               'legal':bool(r.legal),'bat_ball':bool(r.bat_ball),'p_bat':p_bat,'p_bowl':p_bowl,'tactical':state,
               'playoff':int(playoff),'stake_proxy':stakes,'opp_strength_bat':m['strength'].get(bowl,.5),'opp_strength_bowl':m['strength'].get(bat,.5),
               'bat_toss_disadv':int(bat_lost),'bowl_toss_disadv':int(bowl_lost),'carry_pressure':carry,'recent_wicket_pressure':wicket_shock,
               'bat_momentum':momentum_bat,'bowl_momentum':momentum_bowl,'required_rate':rrr if inn==2 else np.nan,
               'target':target if inn==2 else np.nan,'runs_before':runs,'wickets_before':wk,'balls_before':legal,'venue_expected_runrate':par}
            rows.append(d);tactical_counts[state]+=1
            if r.legal:
                recent.append((r.runs_all,int(r.wicket_flag)));legal+=1
                bowler_legal[bol]+=1
            runs+=float(r.runs_all)
            if r.wicket_flag:
                wk+=1; last_wicket=legal
            bats[striker]+=float(r.runs)
            bowler_runs[bol]+=float(r.runs_bowler)
            if r.wicket_bowler:bowler_wks[bol]+=1
            if r.bat_ball:
                striker_dot[striker]=striker_dot[striker]+1 if r.runs==0 else 0
            bowler_recent[bol].append(float(r.runs_bowler))
    d=pd.DataFrame(rows)
    d['date']=d.match_id.map(mm.set_index('match_id').match_date).dt.strftime('%Y-%m-%d')
    return d,tactical_counts

def add_expected(d):
    # Peer actuals from whole research period, but focal match excluded: avoids training on that match.
    # Pool format/inning/phase/pace/pressure band; smooth venue and tactical subgroup to global.
    for role in ['bat','bowl']:
        p='p_'+role
        threshold=float(d[p].quantile(.73))
        d['pressure_'+role]=d[p]>=threshold
        d['band_'+role]=pd.cut(d[p],bins=[-1,.18,.31,.42,.52,.65,2],labels=False).fillna(0).astype(int)
        base=['fmt','innings','phase','pace_spin','band_'+role]
        if role=='bat':
            stats=['bat_runs','striker_out'];event=d.bat_ball
        else:stats=['bowl_runs','bowler_wicket'];event=np.ones(len(d),dtype=bool)
        d['exp_runs_'+role]=0.;d['exp_wk_'+role]=0.
        relevant=d[event].copy()
        overall=relevant[stats].mean().to_numpy()
        base_stats=relevant.groupby(base,dropna=False).agg(n=(stats[0],'size'),runs=(stats[0],'sum'),wks=(stats[1],'sum'))
        base_stats.columns=['base_n','base_runs','base_wks']
        venue_stats=relevant.groupby(base+['venue_id'],dropna=False).agg(n=(stats[0],'size'),runs=(stats[0],'sum'),wks=(stats[1],'sum'))
        venue_stats.columns=['v_n','v_runs','v_wks']
        combo=venue_stats.join(base_stats,on=base)
        joined=d.join(combo,on=base+['venue_id'])
        nbr=joined['base_n'].fillna(0)-event.astype(int)
        bb=joined['base_runs'].fillna(0)-np.where(event,d[stats[0]],0.)
        bw=joined['base_wks'].fillna(0)-np.where(event,d[stats[1]],0.)
        mu_run=(bb+160*overall[0])/(nbr+160)
        mu_wk=(bw+160*overall[1])/(nbr+160)
        vn=joined['v_n'].fillna(0)-event.astype(int)
        vr=joined['v_runs'].fillna(0)-np.where(event,d[stats[0]],0.)
        vw=joined['v_wks'].fillna(0)-np.where(event,d[stats[1]],0.)
        d['exp_runs_'+role]=(vr+130*mu_run)/(vn+130)
        d['exp_wk_'+role]=(vw+130*mu_wk)/(vn+130)
        if role=='bat':
            d['impact_bat']=d['bat_runs']-d['exp_runs_bat']-WICKET_RUN_VALUE*(d['striker_out']-d['exp_wk_bat'])
        else:
            d['impact_bowl']=d['exp_runs_bowl']-d['bowl_runs']+WICKET_RUN_VALUE*(d['bowler_wicket']-d['exp_wk_bowl'])
    return d,{'bat':float(d.p_bat.quantile(.73)),'bowl':float(d.p_bowl.quantile(.73))}

def rankings(d,exclude_pak):
    result={}
    for role in ('bat','bowl'):
        p='p_'+role;pressure='pressure_'+role; pid=role=='bat' and 'striker_id' or 'bowler_id';nme='striker_name' if role=='bat' else 'bowler_name';impact='impact_'+role
        work=d[d.bat_ball].copy() if role=='bat' else d.copy()
        work['pid']=work[pid].astype(int)
        work=work[~work.pid.isin(exclude_pak)]
        work['recy']=work.date.str[:4].astype(int).map(TIME_WEIGHT)
        work['weighted_impact']=work[impact]*work.recy
        work['weighted_n']=work.recy
        result_rows=[]
        for player,g in work.groupby('pid',sort=False):
            pg=g[g[pressure]];ng=g[~g[pressure]];ipl=g[g.fmt=='IPL']; intl=g[g.fmt=='T20I']
            nip=ipl[ipl[pressure]]
            pm=pg.groupby('match_id').agg(n=('pid','size'),impact=('weighted_impact','sum'),weighted_n=('weighted_n','sum'))
            pm=pm[pm.n>=3]
            if len(pg)<46 or len(ng)<75 or g.match_id.nunique()<8 or ipl.match_id.nunique()<4 or len(ipl)<(100 if role=='bat' else 120) or len(nip)<(22 if role=='bat' else 28) or len(pm)<5:continue
            def rrate(q):
                n=q.weighted_n.sum();return 100*q.weighted_impact.sum()/max(.00001,n)
            p_rate=rrate(pg);n_rate=rrate(ng)
            press=clamp(p_rate,-65,65)*pg.weighted_n.sum()/(pg.weighted_n.sum()+75)
            resilience=clamp(p_rate-n_rate,-55,55)*pg.weighted_n.sum()/(pg.weighted_n.sum()+100)
            cons=float((pm.impact>0).mean())
            match_stability=15*(cons-.50)
            m_rates=pm.impact/pm.weighted_n*100
            uncertainty=min(6,(m_rates.std(ddof=1)/math.sqrt(len(m_rates)))*.09) if len(pm)>1 else 6
            ph=[]
            for phase,weight in [('PP',.33),('MID',.34),('DEATH',.33)]:
                group=g[g.phase==phase]
                ph.append(weight*smooth_rate(group.weighted_impact.sum(),group.weighted_n.sum(),85))
            phase_index=sum(ph)
            hard=g[(g[pressure])&((g['opp_strength_'+role]>=.57)|(g.playoff==1)|(g.stake_proxy>=.42))]
            adversity=g[(g[pressure]) & ((g[role+'_toss_disadv']==1)|(g['tactical'].isin(['attack','consolidation'])))]
            hard_index=smooth_rate(hard.weighted_impact.sum(),hard.weighted_n.sum(),70)
            adverse_index=smooth_rate(adversity.weighted_impact.sum(),adversity.weighted_n.sum(),70)
            form_index=.66*smooth_rate(ipl.weighted_impact.sum(),ipl.weighted_n.sum(),130)+.34*smooth_rate(intl.weighted_impact.sum(),intl.weighted_n.sum(),130)
            score=.49*press+.13*resilience+.10*match_stability+.10*phase_index+.08*hard_index+.06*adverse_index+.04*form_index-uncertainty
            res={'player':g[nme].mode().iloc[0].replace('Namboori Tilak Varma','Tilak Varma'), 'player_id':player,
                 'score':round(score,3),'pressure_index':round(press,3),'resilience_index':round(resilience,3),
                 'match_consistency_pct':round(100*cons,1),'reliability_index':round(match_stability,3),
                 'phase_index':round(phase_index,3),'strong_opposition_stakes_index':round(hard_index,3),
                 'adversity_toss_tactics_index':round(adverse_index,3),'all_form_index':round(form_index,3),
                 'uncertainty_penalty':round(uncertainty,3),'pressure_rate_per100':round(p_rate,2),
                 'normal_rate_per100':round(n_rate,2),'pressure_balls':len(pg),'normal_balls':len(ng),
                 'pressure_matches':len(pm),'ipl_matches':ipl.match_id.nunique(),'t20i_matches':intl.match_id.nunique(),
                 'ipl_balls':len(ipl),'t20i_balls':len(intl),
                 'hard_pressure_balls':len(hard),'adverse_pressure_balls':len(adversity),
                 'opp_favored_toss_pressure_balls':int(((g[role+'_toss_disadv']==1)&g[pressure]).sum()),
                 'attack_pressure_balls':int(((g.tactical=='attack')&g[pressure]).sum()),
                 'consolidation_pressure_balls':int(((g.tactical=='consolidation')&g[pressure]).sum()),
                 'survival_pressure_balls':int(((g.tactical=='survival')&g[pressure]).sum()),
                 'last_appearance_in_supplied_data':g.date.max(),
                 'fitness_status':'unverified','future_ipl_availability':'unverified','external_domestic_form':'not uniformly available'}
            for phase in ['PP','MID','DEATH']:
                phg=g[g.phase==phase];res[phase+'_balls']=len(phg);res[phase+'_excess_per100']=round(rrate(phg),2) if len(phg) else np.nan
            result_rows.append(res)
        rr=pd.DataFrame(result_rows).sort_values(['score','pressure_matches'],ascending=False).reset_index(drop=True)
        rr.insert(0,'rank',range(1,len(rr)+1));rr.to_csv(OUT/f'{role}_advanced_rankings.csv',index=False)
        result[role]=rr
    return result

def main():
    mm,bb,links=data_load(); meta=match_context(mm,bb);d,tactics=pressure_rows(mm,bb,meta)
    d,thresholds=add_expected(d)
    exclusions=set(links.loc[links.team_name.astype(str).str.casefold().eq('pakistan'),'player_id'].astype(int))
    ranks=rankings(d,exclusions)
    key_cols=['match_id','date','innings','fmt','venue_id','phase','tactical','p_bat','p_bowl','pressure_bat','pressure_bowl','runs_before','wickets_before','balls_before','required_rate','target','venue_expected_runrate','recent_wicket_pressure','carry_pressure','bat_momentum','bowl_momentum','stake_proxy','bat_toss_disadv','bowl_toss_disadv']
    d[key_cols].groupby(['match_id','date','innings','fmt','venue_id','phase','tactical']).agg(
      n=('p_bat','size'),bat_pressure_balls=('pressure_bat','sum'),bowl_pressure_balls=('pressure_bowl','sum'),
      mean_bat_pressure=('p_bat','mean'),mean_bowl_pressure=('p_bowl','mean')).reset_index().to_csv(OUT/'pressure_conditions_by_match.csv',index=False)
    summary={'analysis_window':[DATE_BEGIN,DATE_END],'eligible_matches':int(mm.match_id.nunique()),'deliveries':len(d),
      'bat_pressure_deliveries':int(d.pressure_bat.sum()),'bowl_pressure_deliveries':int(d.pressure_bowl.sum()),
      'pressure_thresholds':thresholds,'tactical_state_distribution':dict(tactics),
      'eligible_batters':len(ranks['bat']),'eligible_bowlers':len(ranks['bowl']),
      'score_weights':{'pressure_excess':.49,'pressure_vs_normal':.13,'match_consistency':.10,'phase_versatility':.10,'tough_opponents_and_stakes':.08,'toss_tactical_adversity':.06,'overall_form':.04},
      'pressure_context_weights':{'match_state':.42,'momentum':.14,'carry_responsibility':.13,'opposition_tournament':.12,'conditions_toss':.10,'tactical_response_proxy':.09},
      'unscored':['verified sledging','true mental state','medical fitness','selection job security','exact NRR win-by-over requirements without complete tournament standings'],
      'note':'Pre-ball tactical labels are inferred behaviours, not observed mentality; group comparison uses peer averages from whole analysis period, excluding the evaluated delivery, not a forward-looking holdout.'}
    (OUT/'advanced_benchmark_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    for role in ('bat','bowl'):
        print('\n'+role.upper()+' TOP 15')
        print(ranks[role][['rank','player','score','pressure_balls','match_consistency_pct','hard_pressure_balls','adverse_pressure_balls']].head(15).to_string(index=False))
if __name__=='__main__':main()
