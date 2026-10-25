"""Guarded camera-triggered development mission; perception never reads dirt truth."""
import os
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import argparse,json,hashlib
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


def run(directory,scenario='dirty',duration=520):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    field=SurfaceDebris();fall=FallingDebris(scenario);trigger=Trigger()
    renderer=None;next_camera=0.;observations=[];last_targets=[]
    stream=(directory/'observations.jsonl').open('w')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'src/panel_vision.py',ROOT/'src/surface_debris.py',ROOT/'src/debris_events.py']}

    def sample(m,d,state,coverage):
        nonlocal renderer,next_camera,last_targets
        rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3);origin=d.xpos[rack]
        fall.update(m,d,origin,R,field)
        brush=m.geom('brush_cylinder').id;glass=m.geom('pv_glass_surface').id
        force=0.
        for i,c in enumerate(d.contact):
            if {int(c.geom1),int(c.geom2)}=={brush,glass}:
                wrench=np.zeros(6);mujoco.mj_contactForce(m,d,i,wrench);force+=max(0.,wrench[0])
        if state=='SWEEP':
            field.clean(R.T@(d.geom_xpos[brush]-origin),R.T@d.geom_xmat[brush].reshape(3,3)[:,2],
                        *m.geom_size[brush,:2],force,d.qvel[m.joint('brush_hinge').dofadr[0]],m.opt.timestep)
        if d.time+1e-9<next_camera:return
        next_camera=float(d.time)+.5
        if renderer is None:renderer=mujoco.Renderer(m,height=480,width=640,max_geom=10000)
        targets=[]
        for name in ('edge_left','edge_right','robot_camera'):
            camera=m.camera(name).id;renderer.update_scene(d,camera=camera);field.append_visuals(renderer.scene,origin,R)
            rgb=renderer.render()
            calibration=CameraCalibration(d.cam_xpos[camera].copy(),d.cam_xmat[camera].reshape(3,3).copy(),m.cam_fovy[camera],origin.copy(),R.copy())
            detections,_=detect_dirt(rgb,calibration)
            for detection in detections:
                point=np.array([detection['panel_x_m'],detection['panel_y_m']])
                if detection['confidence']>=.8 and all(np.linalg.norm(point-np.array(t))>.12 for t in targets):targets.append(point.tolist())
            if (not trigger.active and d.time<5) or int(d.time)%30==0:
                Image.fromarray(rgb).save(directory/f'{name}_{d.time:.1f}.png')
        trigger.observe(float(d.time),targets)
        last_targets=targets
        observation={'time_s':float(d.time),'state':state,'targets':targets,'triggered':trigger.active}
        observations.append(observation);stream.write(json.dumps(observation)+'\n');stream.flush()
    try:
        result=mission(seed=0,duration=duration,guarded=True,output=directory/'telemetry.csv.gz',on_sample=sample,should_move=lambda:trigger.active,revisit_targets=lambda:last_targets)
    finally:
        stream.close()
        if renderer is not None:renderer.close()
    status='CLEAN_AND_HOME' if result['status']=='DOCKED' and not last_targets else ('IDLE_COMPLETE' if not trigger.active and result['status']=='TIMEOUT' and result['time_s']>=duration-.003 else 'INCOMPLETE')
    report={'status':status,'independent_cleaning_pass':status=='CLEAN_AND_HOME' and field.summary()['uncleared_patches']==0,'independent_coverage_pass':result['coverage_metrics_v2']['qualified_contact_fraction']>=.9,'scenario':scenario,'physical_mission':result,'trigger_events':trigger.events,'deposition_events':fall.events,
            'hidden_dirt_score':field.summary(),'last_camera_targets':last_targets,'source_hashes':hashes,
            'limitations':['Controlled-colour RGB detector, not general debris recognition','Ground-truth navigation retained; camera-based dirt trigger only','Aggregate load plus local gap is a soil proxy','Fine-particle conversion is explicit hybrid deposition; larger crumbs not yet implemented','At most two camera-driven revisit cycles; persistent targets end INCOMPLETE']}
    (directory/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    (directory/'camera_observations.json').write_text(json.dumps(observations,indent=2)+'\n')
    print(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--scenario',choices=['clean','subthreshold','dirty'],default='dirty');p.add_argument('--duration',type=float,default=520);a=p.parse_args()
    run(a.output_dir,a.scenario,a.duration)
