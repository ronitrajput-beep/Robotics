"""Independent full-run checks for the declared combined collection development case."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd


def verify(directory,require_hybrid_mass=True):
    directory=Path(directory);report=json.loads((directory/'result.json').read_text())
    motion=pd.read_csv(directory/'telemetry.csv.gz',low_memory=False);mass=pd.read_csv(directory/'collection.csv.gz');solid=pd.read_csv(directory/'solid.csv.gz')
    observations=[json.loads(line) for line in (directory/'observations.jsonl').read_text().splitlines()]
    checks={}
    checks['completed']=report['status']=='CLEAN_AND_HOME' and report['physical_mission']['status']=='DOCKED'
    checks['all_dust_below_threshold']=report['hidden_dirt_score']['patches']==32 and report['hidden_dirt_score']['uncleared_patches']==0
    checks['finite_500Hz_motion']=bool(np.isfinite(motion.select_dtypes('number').drop(columns=['stop_reason'],errors='ignore')).all().all() and np.max(abs(np.diff(motion.time_s)-.002))<1e-8)
    checks['no_lift']=bool(motion.chassis_tilt_deg.max()<1. and motion.chassis_height_m.max()<.123)
    checks['external_home']=bool(motion.x_m.iloc[0]+.22<-3 and motion.x_m.iloc[-1]+.22<-3 and 1.<motion.y_m.iloc[-1]<1.85)
    checks['settled_at_home']=bool((motion.tail(250).speed_mps<.02).all() and (motion.tail(250).angular_speed_rad_s<.05).all() and (abs(motion.tail(250).brush_rad_s)<1).all())
    deposition_mass=sum(e.get('transferred_mass_kg',0.) for e in report['deposition_events'] if e['event']=='HYBRID_DEPOSITION')
    if require_hybrid_mass:checks['hybrid_mass_conserved']=abs(deposition_mass-mass.deposited_kg.iloc[-1])<1e-12
    checks['mass_conserved_every_step']=bool(mass.balance_error_kg.abs().max()<1e-12 and np.max(abs(mass.surface_kg+mass.bin_kg+mass.station_kg-mass.deposited_kg))<1e-12)
    checks['bin_then_station']=bool(mass.bin_kg.max()>0 and mass.station_kg.iloc[-1]>0 and mass.bin_kg.iloc[-1]<1e-12)
    service=motion[motion.state=='DOCK_SERVICE'];checks['eight_second_station_service']=bool(len(service)>=3999 and (service.x_m+.22<-3).all())
    # Station inventory and charge can change only during a logged stationary service.
    merged=mass.merge(motion[['time_s','state']],on='time_s',validate='one_to_one')
    transfer=merged.station_kg.diff().fillna(0)>1e-14
    charging=merged.charge_J.diff().fillna(0)>1e-8
    checks['service_only_transfer']=bool((merged.loc[transfer|charging,'state']=='DOCK_SERVICE').all())
    info=report['physical_solid'];events={e['event']:e['time_s'] for e in info['events']}
    checks['physical_push_and_retention']=bool(info['first_tool_contact_s'] is not None and info['fully_left_glass'] and info['contacted_catch_tray'] and info['retained_in_tray_at_end'] and solid.brush_force_N.max()>0)
    checks['solid_sequence']=all(k in events for k in ('SOLID_RELEASED','SOLID_TOOL_CONTACT','SOLID_OFF_GLASS','SOLID_TRAY_CONTACT')) and events.get('SOLID_RELEASED',np.inf)<events.get('SOLID_TOOL_CONTACT',-np.inf)<events.get('SOLID_OFF_GLASS',-np.inf)<=events.get('SOLID_TRAY_CONTACT',-np.inf)
    checks['solid_continuous_after_release']=bool(np.linalg.norm(np.diff(solid[['x_m','y_m','z_m']],axis=0),axis=1).max()<.1)
    trigger=report['trigger_events'][0]['time_s']
    checks['image_trigger_precedes_motion']=bool((motion[motion.time_s<trigger-1e-6].state=='HOME_MONITOR').all() and max(len(o['targets']) for o in observations if o['time_s']<=trigger)>=3)
    checks['camera_verifies_clean']=not report['last_camera_targets']
    checks={key:bool(value) for key,value in checks.items()}
    result={'pass':all(checks.values()),'mass_balance_scope':'grain-to-soil plus surface/bin/station' if require_hybrid_mass else 'legacy surface/bin/station only; grain transfer not verified','checks':checks,'metrics':{'max_tilt_deg':float(motion.chassis_tilt_deg.max()),'max_height_m':float(motion.chassis_height_m.max()),'contact_coverage':report['physical_mission']['coverage_metrics_v2']['qualified_contact_fraction'],'mass_balance_max_abs_kg':float(mass.balance_error_kg.abs().max()),'peak_solid_force_N':float(solid.brush_force_N.max()),'terminal_dust_bin_kg':float(mass.bin_kg.iloc[-1]),'terminal_station_waste_kg':float(mass.station_kg.iloc[-1])}}
    (directory/'independent_collection_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if not result['pass']:raise AssertionError('Combined mission did not satisfy every acceptance check')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--legacy-inventory',action='store_true');a=p.parse_args();verify(a.directory,not a.legacy_inventory)
