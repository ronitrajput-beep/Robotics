"""Independent run-level analysis of the frozen full-mission validation batch."""
from pathlib import Path
import argparse,json,math
import numpy as np,pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from analyse_tracking_benchmark import comparison


def wilson(successes,n):
    z=stats.norm.ppf(.975);p=successes/n;den=1+z*z/n
    centre=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(centre-half),float(centre+half)]


def audit_trace(directory,row):
    columns=['time_s','path_error_m','effort_Nm2_s','tau_left_front_Nm','tau_left_rear_Nm','tau_right_front_Nm','tau_right_rear_Nm','tau_brush_Nm']
    n=0;ss=0.;effort=0.;last=None;total=0;max_dt_error=0.;finite=True
    for chunk in pd.read_csv(directory/'telemetry.csv.xz',usecols=columns,chunksize=50000):
        numeric=chunk.to_numpy(float);finite=finite and bool(np.isfinite(numeric).all())
        t=chunk.time_s.to_numpy();deltas=np.diff(np.r_[last,t] if last is not None else t)
        if len(deltas):max_dt_error=max(max_dt_error,float(np.max(abs(deltas-.002))))
        last=float(t[-1]);total+=len(chunk)
        window=chunk[t<30.-1e-9];n+=len(window);ss+=float(np.sum(window.path_error_m.to_numpy()**2))
        effort+=float(np.sum(window.filter(like='tau_').to_numpy()**2))*.002
    rmse=math.sqrt(ss/n) if n==15000 else None
    primary_match=(rmse is None and pd.isna(row.primary_30s_rmse_m)) or (rmse is not None and abs(rmse-float(row.primary_30s_rmse_m))<1e-8)
    return {'finite':finite,'sample_count_matches':total==int(row.telemetry_samples),'sampling_500Hz':max_dt_error<1e-6,'max_dt_error_s':max_dt_error,'primary_rmse_matches':primary_match,'effort_30s_matches':abs(effort-float(row.effort_first30_Nm2_s))<max(1e-6,abs(effort)*1e-7),'common_window_samples':n}


def analyse(folder):
    folder=Path(folder);complete=json.loads((folder/'batch_complete.json').read_text());protocol=json.loads((folder/'protocol.json').read_text())
    if protocol['phase']!='frozen full-mission evaluation':raise ValueError('Pilot trials cannot be final results')
    data=pd.read_csv(folder/'summary.csv');expected={(j['tilt_deg'],j['variant'],j['seed']) for j in protocol['jobs']}
    observed=set(zip(data.tilt_deg,data.variant,data.seed));assert expected==observed and len(data)==len(expected)
    if complete['exceptions']:raise ValueError('Batch contains setup/runtime exceptions; inspect rather than silently exclude')
    audits={};conditions=[];figdir=folder/'figures';figdir.mkdir(exist_ok=False)
    for row in data.itertuples():
        directory=folder/f'tilt_{row.tilt_deg:g}'/f'{row.variant}_{row.seed}'
        audits[directory.name+'_'+str(row.tilt_deg)]=audit_trace(directory,row)
    if not all(all(v[k] for k in ('finite','sample_count_matches','sampling_500Hz','primary_rmse_matches','effort_30s_matches')) for v in audits.values()):raise AssertionError('Trace audit failed')
    for angle in protocol['angles_deg']:
        groups={v:data[(data.tilt_deg==angle)&(data.variant==v)] for v in ('baseline','proposed')}
        for v,group in groups.items():assert len(group)==protocol['runs_per_controller_per_tilt']
        a=groups['proposed'].primary_30s_rmse_m.dropna();b=groups['baseline'].primary_30s_rmse_m.dropna()
        stats_result=comparison(a,b) if min(len(a),len(b))>=2 and (a.var()+b.var())>0 else {'note':'Continuous comparison unavailable: insufficient common-window data/variance','p_value':None}
        result={'tilt_deg':angle,'primary_metric':'0–30 s common-window geometric tracking RMSE, metres','statistics':stats_result,'controllers':{}}
        for v,group in groups.items():
            success=group.success.astype(str).str.lower().eq('true');n=len(group);ns=int(success.sum());report={'attempted':n,'successes':ns,'success_fraction':ns/n,'wilson95':wilson(ns,n),'statuses':{str(k):int(x) for k,x in group.status.value_counts().items()},'metrics':{}}
            for col in ('primary_30s_rmse_m','effort_first30_Nm2_s','full_observed_rmse_m','duration_s','effort_Nm2_s','work_J','coverage_fraction','mean_patch_residual','max_height_m','max_tilt_deg','peak_tool_force_N'):
                vals=group[col].dropna();report['metrics'][col]={'n':len(vals),'mean':float(vals.mean()),'sd':float(vals.std(ddof=1)),'min':float(vals.min()),'max':float(vals.max())}
            vals=group.loc[success,'duration_s'];report['successful_cycle_duration_s']={'n':len(vals),'mean':float(vals.mean()) if len(vals) else None,'sd':float(vals.std(ddof=1)) if len(vals)>1 else None}
            result['controllers'][v]=report
        counts=[[result['controllers'][v]['successes'],result['controllers'][v]['attempted']-result['controllers'][v]['successes']] for v in ('proposed','baseline')]
        odds,p=stats.fisher_exact(counts);result['completion_fisher']={'p_two_sided':float(p),'odds_ratio':float(odds) if np.isfinite(odds) else None};conditions.append(result)
    valid=sorted([(i,c['statistics']['p_value']) for i,c in enumerate(conditions) if c['statistics'].get('p_value') is not None],key=lambda x:x[1]);previous=0.
    for rank,(i,pvalue) in enumerate(valid):
        previous=max(previous,min(1.,(len(valid)-rank)*pvalue));conditions[i]['statistics']['p_holm']=previous
    report={'scope':protocol['scope'],'protocol':'protocol.json','attempted_runs':len(data),'conditions':conditions,'sampling_audit_pass':True,'primary_interpretation':'Common 30-second exposure is comparable even when later missions terminate at different times. Full-run observed RMSE/effort/duration are secondary and are not interpreted as equal-exposure superiority.','randomisation':protocol['randomisation']}
    (folder/'statistics.json').write_text(json.dumps(report,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else x,allow_nan=False)+'\n');(folder/'trace_audit.json').write_text(json.dumps(audits,indent=2)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True);boxes=[];efforts=[];labels=[]
    for angle in protocol['angles_deg']:
        for v in ('baseline','proposed'):
            g=data[(data.tilt_deg==angle)&(data.variant==v)];boxes.append(g.primary_30s_rmse_m.dropna()*100);efforts.append(g.effort_first30_Nm2_s);labels.append(f'{angle:g}°\n{v.title()}')
    axes[0].boxplot(boxes,tick_labels=labels);axes[0].set(ylabel='Run-level first-30-s RMSE (cm)',title='Equal-exposure tracking; 30 trials per box')
    axes[1].boxplot(efforts,tick_labels=labels);axes[1].set(ylabel='First-30-s ∫Στ²dt (N² m² s)',title='Actual actuator control effort')
    for ax in axes:ax.grid(axis='y',alpha=.2)
    fig.savefig(figdir/'tracking_and_effort.png',dpi=260);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True)
    for offset,v,color in [(-.16,'baseline','#b27032'),(.16,'proposed','#168489')]:
        ys=[];lower=[];upper=[]
        for c in conditions:
            m=c['controllers'][v];ys.append(m['success_fraction']);lower.append(m['success_fraction']-m['wilson95'][0]);upper.append(m['wilson95'][1]-m['success_fraction'])
        axes[0].bar(np.arange(len(conditions))+offset,ys,width=.30,color=color,label=v.title(),yerr=[lower,upper],capsize=4)
    axes[0].set(xticks=np.arange(len(conditions)),xticklabels=[f'{x:g}°' for x in protocol['angles_deg']],ylim=(0,1.15),ylabel='Complete-cycle success fraction',title='All attempts retained; Wilson 95% interval');axes[0].legend()
    axes[1].boxplot([data[(data.tilt_deg==a)&(data.variant==v)].coverage_fraction*100 for a in protocol['angles_deg'] for v in ('baseline','proposed')],tick_labels=labels);axes[1].set(ylabel='Whole-panel qualifying footprint (%)',title='Observed progress at completion/abort/timeout')
    fig.savefig(figdir/'completion_and_coverage.png',dpi=260);plt.close(fig)
    figure,ax=plt.subplots(figsize=(7,4.8),constrained_layout=True);ax.add_patch(Rectangle((-3,-2),6,4,fc='#eff3f7',ec='#567'));ax.add_patch(Rectangle((-4.5,1),1.5,1,fc='#d9e5df',ec='#567'))
    for v,color in [('baseline','#b27032'),('proposed','#168489')]:
        g=data[(data.tilt_deg==20)&(data.variant==v)].sort_values('seed').iloc[0];path=folder/'tilt_20'/f'{v}_{int(g.seed)}'/'telemetry.csv.xz';trace=pd.read_csv(path,usecols=['x_m','y_m','ref_x_m','ref_y_m']).iloc[::50]
        ax.plot(trace.x_m,trace.y_m,color=color,lw=.8,label=f'{v.title()} seed {int(g.seed)} / {g.status}')
        if v=='proposed':ax.plot(trace.ref_x_m,trace.ref_y_m,color='#888',lw=.5,ls='--',label='Proposed local reference')
    ax.set(xlabel='Panel x (m)',ylabel='Panel y (m)',aspect='equal',title='Prespecified first seeds at 20°; plot decimated to 10 Hz');ax.legend(fontsize=7);figure.savefig(figdir/'representative_trajectories.png',dpi=260);plt.close(figure)
    print(json.dumps({'attempted':len(data),'sampling_audit':'PASS','conditions':[(c['tilt_deg'],c['statistics'].get('p_value')) for c in conditions]},indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);analyse(p.parse_args().directory)
