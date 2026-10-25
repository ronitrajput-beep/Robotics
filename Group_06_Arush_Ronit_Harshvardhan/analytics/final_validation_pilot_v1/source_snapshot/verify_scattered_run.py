"""Verify no-lift motion, actual camera causality and all scattered dirt targets."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd


def verify(directory):
    directory=Path(directory);r=json.loads((directory/'result.json').read_text());p=r['physical_mission']
    d=pd.read_csv(directory/'telemetry.csv.gz',low_memory=False)
    observations=[json.loads(line) for line in (directory/'observations.jsonl').read_text().splitlines()]
    assert r['status']=='CLEAN_AND_HOME' and r['independent_no_lift_pass']
    assert r['hidden_dirt_score']['patches']==32 and r['hidden_dirt_score']['uncleared_patches']==0
    assert p['status']=='DOCKED' and p['dock_error_m']<=.12
    assert np.allclose(np.diff(d.time_s),.002,atol=1e-9)
    assert np.isfinite(d.select_dtypes('number')).all().all()
    assert d.chassis_tilt_deg.max()<1 and d.chassis_height_m.max()<.123
    trigger=r['trigger_events'][0]['time_s']
    deposit=[e for e in r['deposition_events'] if e['event']=='HYBRID_DEPOSITION']
    assert len(deposit)==8 and max(e['time_s'] for e in deposit)<trigger
    assert d[d.time_s<trigger].state.eq('HOME_MONITOR').all()
    requests=[e for e in p['events'] if e['event']=='VISION_EDGE_SERVICE']
    for event in requests:
        earlier=[o for o in observations if o['time_s']<=event['time_s']]
        sensor=earlier[-1]
        assert event['edge']=='bottom' and event['targets']
        assert event['time_s']-sensor['time_s']<=.501
        assert any(y<-1.65 for x,y in sensor['targets'])
    assert not d.state.eq('EDGE_CLEAN_BOTTOM').any() or requests
    permitted=np.zeros(len(d),dtype=bool)
    ends=[e for e in p['events'] if e['event']=='EDGE_SERVICE_COMPLETE']
    for event in requests:
        end=next(e['time_s'] for e in ends if e['time_s']>=event['time_s'])
        permitted|=(d.time_s.to_numpy()>=event['time_s'])&(d.time_s.to_numpy()<=end)
    assert not ((d.guard_normal_N.to_numpy()>.01)&~permitted).any(), 'Guard contact outside a camera-requested edge task'
    assert d.state.eq('RETURN_HOME').any()
    window=d[d.time_s>=p['time_s']-.5]
    assert len(window)>=249 and window.state.eq('DOCKING').all()
    assert (window.speed_mps<.02).all() and (window.angular_speed_rad_s<.05).all() and (window.brush_rad_s.abs()<1).all()
    return {'outcome':r['status'],'samples':len(d),'all_32_dirt_patches_below_threshold':True,
            'maximum_chassis_tilt_deg':float(d.chassis_tilt_deg.max()),
            'maximum_normal_height_m':float(d.chassis_height_m.max()),
            'maximum_height_above_initial_mm':float((d.chassis_height_m.max()-d.chassis_height_m.iloc[0])*1000),
            'guard_contacts_only_within_camera_requested_edge_task':True,'vision_requested_bottom_passes':len(requests),'edge_request_sensor_causality_verified':True,
            'actual_contact_coverage':p['coverage_metrics_v2']['qualified_contact_fraction'],
            'exact_90_percent_coverage_target_met':bool(p['coverage_metrics_v2']['qualified_contact_fraction']>=.90),
            'coverage_note':'Coverage is reported separately; safer turns may trade a little coverage for stability. No old exact-90 criterion is silently changed.',
            'home_settling_verified':True,'scope':'One development scenario, no hardware or broad robustness claim'}


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('directory',type=Path);p=a.parse_args();out=p.directory/'independent_scattered_checks.json'
    if out.exists():raise FileExistsError(out)
    result=verify(p.directory);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
