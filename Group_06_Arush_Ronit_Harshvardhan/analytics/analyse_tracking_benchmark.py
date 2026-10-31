"""Run-level Welch inference from actual tracking runs; strict protocol checks."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]

def comparison(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if min(len(a),len(b))<2 or not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('Insufficient/invalid samples')
    va=a.var(ddof=1);vb=b.var(ddof=1);na=len(a);nb=len(b)
    se=np.sqrt(va/na+vb/nb);df=(va/na+vb/nb)**2/((va/na)**2/(na-1)+(vb/nb)**2/(nb-1))
    difference=a.mean()-b.mean();half=stats.t.ppf(.975,df)*se
    pooled=np.sqrt(((na-1)*va+(nb-1)*vb)/(na+nb-2))
    t,p=stats.ttest_ind(a,b,equal_var=False)
    return {'difference_definition':'proposed minus baseline','mean_difference_m':difference,'ci95_m':[difference-half,difference+half],'welch_t':float(t),'df':float(df),'p_value':float(p),'cohens_d_pooled':float(difference/pooled),'proposed_mean_m':a.mean(),'baseline_mean_m':b.mean(),'proposed_sd_m':np.sqrt(va),'baseline_sd_m':np.sqrt(vb),'n_proposed':na,'n_baseline':nb}

if __name__=='__main__':
    folder=ROOT/'analytics/tracking_benchmark';d=pd.read_csv(folder/'summary.csv')
    protocol=json.loads((folder/'protocol.json').read_text())
    for v,seeds in protocol['seeds'].items():
        rows=d[d.variant==v]
        assert set(rows.seed)==set(seeds) and len(rows)==len(seeds)
    assert (d.status=='TIMEOUT').all() and np.allclose(d.time_s,30), 'Unexpected early termination'
    for column in ['model_sha256','controller_sha256','planner_sha256']:assert d[column].nunique()==1
    a=d.loc[d.variant=='proposed','path_tracking_rmse_m'];b=d.loc[d.variant=='baseline','path_tracking_rmse_m']
    result=comparison(a,b);result['scope']=protocol['scope'];(folder/'statistics.json').write_text(json.dumps(result,indent=2))
    fig,ax=plt.subplots(figsize=(7,4));ax.boxplot([b*100,a*100],tick_labels=['Baseline','Proposed']);ax.set(ylabel='Run-level tracking RMSE (cm)',title='30-second tracking comparison: 30 runs per controller');ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(ROOT/'docs/validation/tracking_comparison.png',dpi=300)
    print(json.dumps(result,indent=2))
