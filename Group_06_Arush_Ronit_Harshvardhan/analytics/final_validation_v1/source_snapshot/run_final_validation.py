"""Frozen full-mission Monte Carlo runs; separate run-level common-window statistics."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','LP_NUM_THREADS'):os.environ.setdefault(key,'1')
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,contextlib,csv,hashlib,json,lzma,math,shutil,time,traceback,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
EXTRA_FIELDS=['tau_left_front_Nm','tau_left_rear_Nm','tau_right_front_Nm','tau_right_rear_Nm','tau_brush_Nm','vx_panel_mps','vy_panel_mps','vz_panel_mps']


class CompactTelemetry:
    """500 Hz measured samples; declared 9-digit numeric serialization, XZ lossless compression."""
    def __init__(self,path):
        self.path=Path(path);self.file=None;self.writer=None;self.rows=0;self.window_n=0;self.window_ss=0.;self.window_effort=0.;self.next_progress=0.
    def __call__(self,row,torques,velocity):
        from crawler_cleaning_controller import TELEMETRY_FIELDS
        if self.file is None:
            self.file=lzma.open(self.path,'xt',newline='',preset=1);self.writer=csv.writer(self.file);self.writer.writerow(TELEMETRY_FIELDS+EXTRA_FIELDS)
        self.writer.writerow([format(float(x),'.9g') if not isinstance(x,str) else x for x in [*row,*torques,*velocity]])
        self.rows+=1
        if row[0]<30.-1e-9:
            self.window_n+=1;self.window_ss+=float(row[7])**2;self.window_effort+=sum(float(x)**2 for x in torques)*.002
        if row[0]>=self.next_progress:
            self.next_progress=float(row[0])+10.
            self.path.with_name('progress.json').write_text(json.dumps({'time_s':float(row[0]),'state':row[1],'samples':self.rows}))
    def close(self):
        if self.file:self.file.close()


def run_one(job):
    from vision_mission import run
    directory=Path(job['directory']);sink=CompactTelemetry(directory/'telemetry.csv.xz');start=time.monotonic()
    with (directory.parent.parent/'logs'/f"{directory.parent.name}_{directory.name}.log").open('w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
        try:
            report=run(directory,scenario='combined',duration=job['horizon_s'],guarded_model_path=job['model_path'],seed=job['seed'],variant=job['variant'],debris_seed=job['debris_seed'],save_images=False,telemetry_sink=sink,compact_logs=True)
            physical=report['physical_mission'];solid=report['physical_solid'];inventory=report['collection']
            row={**{k:job[k] for k in ('variant','seed','debris_seed','tilt_deg')},'status':report['status'],'physics_status':physical['status'],'success':report['status']=='CLEAN_AND_HOME','duration_s':physical['time_s'],'primary_30s_rmse_m':math.sqrt(sink.window_ss/sink.window_n) if sink.window_n==15000 else None,'primary_window_samples':sink.window_n,'full_observed_rmse_m':physical['path_tracking_rmse_m'],'effort_first30_Nm2_s':sink.window_effort,'effort_Nm2_s':physical['effort_Nm2_s'],'work_J':physical['positive_mechanical_work_J'],'coverage_fraction':physical['coverage_metrics_v2']['qualified_contact_fraction'],'uncleared_patches':report['hidden_dirt_score']['uncleared_patches'],'mean_patch_residual':report['hidden_dirt_score']['mean_residual'],'solid_contact_s':solid['first_tool_contact_s'],'solid_retained':solid['retained_in_tray_at_end'],'peak_tool_force_N':solid['peak_tool_object_force_N'],'mass_balance_error_kg':inventory['mass_balance_error_kg'],'station_dust_kg':inventory['station_waste_kg'],'blower_J':inventory['blower_energy_J'],'charge_J':inventory['dock_charge_energy_J'],'max_height_m':physical['maximum_chassis_height_m'],'max_tilt_deg':physical['maximum_chassis_tilt_deg'],'model_sha256':physical['model_sha256'],'controller_sha256':physical['controller_sha256'],'wall_seconds':time.monotonic()-start,'telemetry_samples':sink.rows}
        except Exception as error:
            traceback.print_exc();row={**job,'status':'EXCEPTION','success':False,'error':repr(error),'wall_seconds':time.monotonic()-start,'telemetry_samples':sink.rows}
            directory.mkdir(parents=True,exist_ok=True)
        finally:sink.close()
    (directory/'trial_summary.json').write_text(json.dumps(row,indent=2,allow_nan=False)+'\n');return row


def run_batch(folder,angles=(10,20,30),runs=30,workers=3,pilot=False,horizon=1000.):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False);(folder/'models').mkdir();(folder/'logs').mkdir();(folder/'source_snapshot').mkdir()
    import numpy as np
    model_path=ROOT/'models/collection_cleaning_crawler.xml';jobs=[]
    for angle in angles:
        root=ET.fromstring(model_path.read_text());rotation=f'{np.deg2rad(angle):.17g} 0 0'
        for name in ('pv_array_rack','crawler_chassis'):root.find(f".//body[@name='{name}']").set('euler',rotation)
        model=folder/'models'/f'tilt_{angle:g}.xml';ET.indent(root,space='  ');model.write_text(ET.tostring(root,encoding='unicode'))
        condition=folder/f'tilt_{angle:g}';condition.mkdir()
        for variant in ('baseline','proposed'):
            for replicate in range(runs):
                seed=(400 if variant=='baseline' else 600)+int(angle)+replicate if pilot else (10000 if variant=='baseline' else 20000)+int(angle)*100+replicate
                jobs.append({'variant':variant,'seed':seed,'debris_seed':50000+seed,'tilt_deg':angle,'horizon_s':horizon,'model_path':str(model.resolve()),'directory':str((condition/f'{variant}_{seed}').resolve())})
    hashes={}
    for source in sorted((ROOT/'src').glob('*.py')):
        hashes[source.name]=hashlib.sha256(source.read_bytes()).hexdigest();shutil.copyfile(source,folder/'source_snapshot'/source.name)
    protocol={'phase':'excluded development pilot' if pilot else 'frozen full-mission evaluation','runs_per_controller_per_tilt':runs,'angles_deg':list(angles),'jobs':jobs,'horizon_s':horizon,'source_hashes':hashes,'randomisation':'Independent initial x/y U(-.01,.01) m from trial seed; independent scattered-patch shape/offset RNG from debris_seed; fixed deposit clusters and 120 g solid corridor. Dry nominal friction held fixed.','primary_continuous_metric':'Geometric tracking RMSE over common 0<=t<30 s window (15000 measured samples), not old model/data; every trial continues to docking/abort/horizon.','secondary_endpoints':['complete camera-clean AND safe AND solid retained AND settled external home','whole-panel contact footprint','observed full mission duration/effort/work; failures retained and differing exposure explicitly reported'],'statistics':'Run is unit of analysis; independent-seed baseline/proposed Welch t, two-sided .05, 95% Welch CI, pooled-SD Cohen d; Holm adjustment across tilt conditions. Early aborts under 30 s have unavailable primary metric, not favourable imputation. Completion Fisher exact and Wilson CI.','logging':'500 Hz CSV.xz with state, pose, reference, error, 5 actual actuator torques, panel velocity, contact/load/coverage, effort/work and safety fields. 9 significant digits, timestamp quantization <=0.5 us; numeric quantization disclosed, not synthetic data.','scope':'Controlled simulation repeatability over 10/20/30 degrees, initial pose and soil-layout variation; not field reliability, calibrated PV yield, coating/structural safety or unrestricted vision/localisation.'}
    (folder/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    summaries=[];started=time.monotonic()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(run_one,job):job for job in jobs}
        for future in as_completed(futures):
            row=future.result();summaries.append(row)
            with (folder/'completed_trials.jsonl').open('a') as stream:stream.write(json.dumps(row,allow_nan=False)+'\n')
            print(f"{len(summaries)}/{len(jobs)} tilt={row['tilt_deg']} {row['variant']} seed={row['seed']} {row['status']} wall={row['wall_seconds']:.1f}s",flush=True)
    keys=sorted(set().union(*(row.keys() for row in summaries)))
    with (folder/'summary.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader();writer.writerows(sorted(summaries,key=lambda row:(row['tilt_deg'],row['variant'],row['seed'])))
    (folder/'batch_complete.json').write_text(json.dumps({'attempted':len(jobs),'recorded':len(summaries),'exceptions':sum(row['status']=='EXCEPTION' for row in summaries),'wall_seconds':time.monotonic()-started},indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--runs',type=int,default=30);parser.add_argument('--workers',type=int,default=3);parser.add_argument('--angles',type=float,nargs='+',default=[10,20,30]);parser.add_argument('--pilot',action='store_true');parser.add_argument('--horizon',type=float,default=1000.);args=parser.parse_args()
    run_batch(args.output_dir,args.angles,args.runs,args.workers,args.pilot,args.horizon)
