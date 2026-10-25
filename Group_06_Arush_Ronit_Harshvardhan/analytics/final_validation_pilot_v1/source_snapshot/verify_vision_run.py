"""Independent consistency checks of saved RGB-triggered mission evidence."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd


def verify(directory):
    directory=Path(directory);report=json.loads((directory/'result.json').read_text())
    physical=report['physical_mission'];d=pd.read_csv(directory/'telemetry.csv.gz',low_memory=False)
    assert report['status']=='CLEAN_AND_HOME'
    assert report['independent_cleaning_pass'] and report['independent_coverage_pass']
    assert physical['status']=='DOCKED' and physical['dock_error_m']<=.12
    assert np.allclose(np.diff(d.time_s),.002,atol=1e-9)
    assert np.isfinite(d.select_dtypes('number')).all().all()
    trigger=report['trigger_events'][0]
    deposition=[e for e in report['deposition_events'] if e['event']=='HYBRID_DEPOSITION']
    assert len(deposition)==6 and max(e['time_s'] for e in deposition)<trigger['time_s']
    before=d[d.time_s<trigger['time_s']]
    assert before.state.eq('HOME_MONITOR').all()
    assert report['hidden_dirt_score']['uncleared_patches']==0 and not report['last_camera_targets']
    assert physical['coverage_metrics_v2']['qualified_contact_fraction']>=.9
    gaps=np.array(physical['minimum_chassis_edge_gaps_m'])
    assert np.all(gaps<.005) and np.all(gaps>-.005),gaps
    window=d[d.time_s>=physical['time_s']-.5]
    assert len(window)>=249 and window.state.eq('DOCKING').all()
    assert (window.speed_mps<.02).all() and (window.angular_speed_rad_s<.05).all() and (window.brush_rad_s.abs()<1).all()
    observations=[json.loads(line) for line in (directory/'observations.jsonl').read_text().splitlines()]
    first=next(i for i,o in enumerate(observations) if o['triggered'])
    assert first>0 and len(observations[first-1]['targets'])>=3 and len(observations[first]['targets'])>=3
    home=d[['x_m','y_m']].iloc[0].to_numpy();end=d[['x_m','y_m']].iloc[-1].to_numpy()
    assert np.linalg.norm(home-end)<.12
    return {'samples':len(d),'trigger_time_s':trigger['time_s'],'all_six_deposited_before_trigger':True,
            'initial_idle_verified':True,'measured_qualified_coverage':physical['coverage_metrics_v2']['qualified_contact_fraction'],
            'body_reached_all_four_boundaries':True,'minimum_chassis_gaps_m':gaps.tolist(),
            'revisit_cycles':physical['vision_revisit_cycles'],'home_error_from_initial_pose_m':float(np.linalg.norm(home-end)),
            'final_settling_window_verified':True,'hidden_dirt_score':report['hidden_dirt_score'],
            'scope':'One controlled-colour development scenario with physical containment; not held-out robustness evidence'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args()
    target=a.directory/'independent_checks.json'
    if target.exists():raise FileExistsError(target)
    result=verify(a.directory);target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
