"""Guarded camera-triggered development mission; perception never reads dirt truth."""
import os
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import argparse,json,hashlib,csv,gzip
import mujoco
import numpy as np
from PIL import Image
from crawler_cleaning_controller import mission,ROOT
from panel_vision import CameraCalibration,detect_dirt
from surface_debris import SurfaceDebris
from debris_events import FallingDebris


class Trigger:
    def __init__(self):self.streak=0;self.active=False;self.events=[]
    def observe(self,time,points):
        self.streak=self.streak+1 if len(points)>=3 else 0
        if self.streak>=2 and not self.active:
            self.active=True;self.events.append({'event':'VISION_TRIGGER','time_s':time,'targets':points})


def run(directory,scenario='dirty',duration=520,record_video=False,cinematic=False,guarded_model_path=None):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    combined=scenario=='combined'
    if combined and guarded_model_path is None:guarded_model_path=ROOT/'models/collection_cleaning_crawler.xml'
    from collection_system import CollectionSystem,PhysicalSolid
    collection=CollectionSystem() if combined else None;solid=PhysicalSolid() if combined else None
    field=SurfaceDebris();fall=FallingDebris(scenario);trigger=Trigger()
    from mission_video import MissionVideo
    if cinematic:
        from cinematic_video import CinematicVideo
        video=CinematicVideo(directory)
    else:video=MissionVideo(directory) if record_video else None
    renderer=None;next_camera=0.;observations=[];last_targets=[]
    stream=(directory/'observations.jsonl').open('w')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'src/panel_vision.py',ROOT/'src/surface_debris.py',ROOT/'src/debris_events.py',ROOT/'src/mission_video.py',ROOT/'src/cinematic_video.py',ROOT/'src/cinematic_scene.py',ROOT/'src/collection_system.py',ROOT/'src/build_collection_model.py']}

    def sample(m,d,state,coverage):
        nonlocal renderer,next_camera,last_targets
        rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3);origin=d.xpos[rack]
        fall.update(m,d,origin,R,field)
        if solid is not None:solid.update(m,d,origin,R)
        brush=m.geom('brush_cylinder').id;glass=m.geom('pv_glass_surface').id
        force=0.
        for i,c in enumerate(d.contact):
            if {int(c.geom1),int(c.geom2)}=={brush,glass}:
                wrench=np.zeros(6);mujoco.mj_contactForce(m,d,i,wrench);force+=max(0.,wrench[0])
        if state in ('SWEEP','EDGE_CLEAN_BOTTOM'):
            before=collection.soil_mass(field) if collection is not None else 0.
            field.clean(R.T@(d.geom_xpos[brush]-origin),R.T@d.geom_xmat[brush].reshape(3,3)[:,2],
                        *m.geom_size[brush,:2],force,d.qvel[m.joint('brush_hinge').dofadr[0]],m.opt.timestep)
            if collection is not None:collection.pickup(before,collection.soil_mass(field),m.opt.timestep)
        if collection is not None:collection.sample(d.time,state,field,m.opt.timestep)
        if d.time+1e-9>=next_camera:
            next_camera=float(d.time)+.5
            if renderer is None:renderer=mujoco.Renderer(m,height=480,width=640,max_geom=10000)
            targets=[];sensor_views={}
            for name in ('edge_left','edge_right','robot_camera'):
                camera=m.camera(name).id;renderer.update_scene(d,camera=camera);field.append_visuals(renderer.scene,origin,R)
                rgb=renderer.render()
                calibration=CameraCalibration(d.cam_xpos[camera].copy(),d.cam_xmat[camera].reshape(3,3).copy(),m.cam_fovy[camera],origin.copy(),R.copy())
                detections,_=detect_dirt(rgb,calibration)
                sensor_views[name]={'rgb':rgb.copy(),'detections':detections}
                for detection in detections:
                    point=np.array([detection['panel_x_m'],detection['panel_y_m']])
                    if detection['confidence']>=.8 and all(np.linalg.norm(point-np.array(t))>.12 for t in targets):targets.append(point.tolist())
                if (not trigger.active and d.time<5) or int(d.time)%30==0:
                    Image.fromarray(rgb).save(directory/f'{name}_{d.time:.1f}.png')
            if video is not None and hasattr(video,'update_sensor_views'):video.update_sensor_views(float(d.time),sensor_views)
            trigger.observe(float(d.time),targets)
            last_targets=targets
            observation={'time_s':float(d.time),'state':state,'targets':targets,'triggered':trigger.active}
            observations.append(observation);stream.write(json.dumps(observation)+'\n');stream.flush()
        if video is not None and collection is not None:
            video.collection_status={'bin_g':collection.bin_kg*1000,'station_g':collection.station_kg*1000,'charge_J':collection.charge_J,'solid':solid.summary(),'state':state}
        if video is not None:video.capture(m,d,field,origin,R,state,coverage.summary(),len(last_targets))
    try:
        result=mission(seed=0,duration=duration,guarded=True,output=directory/'telemetry.csv.gz',on_sample=sample,should_move=lambda:trigger.active,revisit_targets=lambda:last_targets,edge_service_targets=lambda:last_targets,
                       route_profile="external_dock" if combined else "inward_turns",guarded_model_path=guarded_model_path,dock_service_s=8. if combined else 0.)
    finally:
        stream.close()
        if renderer is not None:renderer.close()
    status='CLEAN_AND_HOME' if result['status']=='DOCKED' and not last_targets else ('IDLE_COMPLETE' if not trigger.active and result['status']=='TIMEOUT' and result['time_s']>=duration-.003 else 'INCOMPLETE')
    estimated_status=status
    if status=='CLEAN_AND_HOME' and field.summary()['uncleared_patches']>0:status='VERIFICATION_MISS'
    no_lift=result['maximum_chassis_tilt_deg']<1. and result['maximum_chassis_height_m']<.123
    if status=='CLEAN_AND_HOME' and not no_lift:status='UNSAFE_MOTION'
    if status=='CLEAN_AND_HOME' and solid is not None and not solid.final_retained:status='SOLID_NOT_COLLECTED'
    report={'independent_no_lift_pass':no_lift,'camera_estimated_status':estimated_status,'status':status,'independent_cleaning_pass':status=='CLEAN_AND_HOME' and field.summary()['uncleared_patches']==0,'independent_coverage_pass':result['coverage_metrics_v2']['qualified_contact_fraction']>=.9,'scenario':scenario,'physical_mission':result,'trigger_events':trigger.events,'deposition_events':fall.events,
            'hidden_dirt_score':field.summary(),'last_camera_targets':last_targets,'source_hashes':hashes,
            'limitations':['Controlled-colour RGB detector, not general debris recognition','Ground-truth navigation retained; camera-based dirt trigger only','Aggregate load plus local gap is a soil proxy','Fine-particle conversion is explicit hybrid deposition; larger crumbs not yet implemented','At most two camera-driven revisit cycles; persistent targets end INCOMPLETE']}
    if collection is not None:
        report['collection']=collection.summary(field);report['physical_solid']=solid.summary()
        report['limitations']=[x for x in report['limitations'] if 'larger crumbs not yet' not in x]+['Dust capture, service power and mass flow are reduced-order assumptions; no resolved airflow or battery model','Solid starts in a declared first-row handling corridor; arbitrary solid routing and scratch safety unvalidated']
        for name,headers,rows in [('collection.csv',['time_s','surface_kg','bin_kg','station_kg','deposited_kg','balance_error_kg','blower_J','charge_J'],collection.rows),('solid.csv',['time_s','x_m','y_m','z_m','brush_force_N','off_glass','caught','retained'],solid.rows)]:
            with gzip.open(directory/(name+'.gz'),'wt',newline='') as f:
                writer=csv.writer(f);writer.writerow(headers);writer.writerows(rows)
    if video is not None:video.close(report)
    (directory/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    (directory/'camera_observations.json').write_text(json.dumps(observations,indent=2)+'\n')
    print(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--scenario',choices=['clean','subthreshold','dirty','edges','scattered','combined'],default='dirty');p.add_argument('--model',type=Path);p.add_argument('--cinematic',action='store_true');p.add_argument('--record-video',action='store_true');p.add_argument('--duration',type=float,default=520);a=p.parse_args()
    run(a.output_dir,a.scenario,a.duration,a.record_video,a.cinematic,a.model)
