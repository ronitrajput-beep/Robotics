"""Recompute primary statistics from genuine, compact 500 Hz trial windows.

These are explicitly 0<=t<30 s samples from 180 complete attempts. Full mission
outcomes remain separate, and full original streams can be fetched by hash.
"""
from pathlib import Path
import argparse, json, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyse_tracking_benchmark import comparison

ROOT = Path(__file__).resolve().parents[1]


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    summary = pd.read_csv(ROOT/'analytics/final_validation_v1/summary.csv')
    totals = {}
    paths = sorted((ROOT/'analytics/primary_windows').glob('*_real_trials.csv.*'))
    if len(paths) != 6:
        raise ValueError('Requires the six genuine primary-window files from the faculty release')
    for path in paths:
        for chunk in pd.read_csv(path, chunksize=30000):
            for key, group in chunk.groupby('run_id', sort=False):
                values = totals.setdefault(key, {'n':0,'ss':0.,'effort':0.,'variant':group.variant.iloc[0],
                    'tilt_deg':float(group.tilt_deg.iloc[0]),'seed':int(group.seed.iloc[0])})
                values['n'] += len(group)
                values['ss'] += float(np.sum(group.path_error_m.to_numpy()**2))
                values['effort'] += float(np.sum(group.filter(like='tau_').to_numpy()**2))*.002
    assert len(totals) == len(summary) == 180
    results = []
    for key, value in totals.items():
        assert value['n'] == 15000, key
        measured = math.sqrt(value['ss']/value['n'])
        original = summary[(summary.variant==value['variant']) & (summary.tilt_deg==value['tilt_deg']) & (summary.seed==value['seed'])].iloc[0]
        assert abs(measured-original.primary_30s_rmse_m) < 1e-8, key
        assert abs(value['effort']-original.effort_first30_Nm2_s) < 1e-6, key
        results.append({'run_id':key,**value,'primary_30s_rmse_m':measured,'effort_first30_Nm2_s':value['effort']})
    data = pd.DataFrame(results)
    data.to_csv(output/'recomputed_primary_real_trials.csv',index=False)
    conditions = []
    frozen = json.loads((ROOT/'analytics/final_validation_v1/statistics.json').read_text())
    for angle in [10,20,30]:
        proposed = data[(data.tilt_deg==angle)&(data.variant=='proposed')].primary_30s_rmse_m
        baseline = data[(data.tilt_deg==angle)&(data.variant=='baseline')].primary_30s_rmse_m
        result = comparison(proposed,baseline)
        reference = next(c for c in frozen['conditions'] if c['tilt_deg']==angle)['statistics']
        assert abs(result['mean_difference_m']-reference['mean_difference_m']) < 1e-8
        assert np.allclose(result['ci95_m'],reference['ci95_m'],atol=1e-8,rtol=1e-7)
        conditions.append({'tilt_deg':angle,'statistics_recomputed_from_serialised_samples':result})
    previous = 0.
    for rank, condition in enumerate(sorted(conditions,key=lambda c:c['statistics_recomputed_from_serialised_samples']['p_value'])):
        result = condition['statistics_recomputed_from_serialised_samples']
        previous = max(previous,min(1.,(len(conditions)-rank)*result['p_value']))
        result['p_holm'] = previous
    fig, axes = plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True)
    labels, errors, efforts = [], [], []
    for angle in [10,20,30]:
        for variant in ['baseline','proposed']:
            group = data[(data.tilt_deg==angle)&(data.variant==variant)]
            labels.append(f'{angle}°\n{variant}')
            errors.append(group.primary_30s_rmse_m*100)
            efforts.append(group.effort_first30_Nm2_s)
    axes[0].boxplot(errors,tick_labels=labels);axes[1].boxplot(efforts,tick_labels=labels)
    axes[0].set(ylabel='First-30-second RMSE (cm)',title='Actual 500 Hz windows; 30 trials/group')
    axes[1].set(ylabel='First-30-second ∫Στ²dt (N² m² s)',title='Actual actuator torques; equal exposure')
    fig.savefig(output/'recomputed_tracking_and_effort.png',dpi=250);plt.close(fig)
    report = {'pass':True,'trials':len(data),'measured_samples':int(data.n.sum()),'all_primary_metrics_match':True,
              'quantisation':'Original log serialisation is nine significant digits; small numerical differences from full-precision run summaries are explicitly tolerated.',
              'scope':'Only the declared 0<=t<30s primary windows are recomputed here. Full mission metadata/trace audits remain in final_validation_v1; full original data is pinned in FULL_RAW_DATA_MANIFEST.json.',
              'conditions':conditions}
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':True,'trials':len(data),'samples':int(data.n.sum()),'output':str(output)},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True)
    main(parser.parse_args().output_dir)
