"""Fresh complete mission with explicit camera-hardware shots and frame provenance."""
import os,sys
os.environ.setdefault('MUJOCO_GL','cgl' if sys.platform=='darwin' else 'glfw' if sys.platform=='win32' else 'egl')
from pathlib import Path
import argparse,csv,hashlib,json
import mujoco,numpy as np
from cinematic_video import CinematicVideo
from vision_mission import run,ROOT


def inspection_shot(m,d):
    """Only presentation pose changes; calibrated RGB cameras remain untouched."""
    t=float(d.time)
    if not 8<=t<25:return None
    camera=mujoco.MjvCamera();mujoco.mjv_defaultCamera(camera)
    if t<11.5 or t>=22:
        points=np.array([d.cam_xpos[m.camera(name).id] for name in ('edge_left','edge_right')])
        origin=d.xpos[m.body('pv_array_rack').id]
        camera.lookat[:]=.5*(points.mean(axis=0)+origin)
        camera.distance=11.7;camera.elevation=-35;camera.azimuth=100
        return camera,'TWO PANEL CAMERAS + ONBOARD CAMERA / ACTUAL RGB AT RIGHT'
    name='edge_left' if t<15 else 'edge_right' if t<18.5 else 'robot_camera'
    cid=m.camera(name).id;C=d.cam_xmat[cid].reshape(3,3);cp=d.cam_xpos[cid]
    camera.lookat[:]=cp+C[:,2]*.05
    offset=-C[:,2]+.35*C[:,0]+.3*C[:,1];offset/=np.linalg.norm(offset)
    camera.azimuth=float(np.rad2deg(np.arctan2(offset[1],offset[0])))+180.
    camera.elevation=float(-np.rad2deg(np.arcsin(offset[2])))
    camera.distance=.65 if name=='robot_camera' else 1.05
    label={'edge_left':'LEFT PANEL CAMERA / CALIBRATED INSPECTION RIG','edge_right':'RIGHT PANEL CAMERA / CALIBRATED INSPECTION RIG','robot_camera':'ONBOARD CAMERA / MOVES WITH THE ROBOT'}[name]
    return camera,label


class CompleteCameraVideo(CinematicVideo):
    def __init__(self,directory):
        super().__init__(directory,presentation_shot=inspection_shot,cruise_speed=12)
        self.frame_stream=(self.directory/'frame_map.csv').open('w',newline='')
        self.frame_writer=csv.writer(self.frame_stream)
        self.frame_writer.writerow(['frame','video_time_s','simulation_time_s','state','shot'])
        self.last_state='';self.last_simulation_time=0.;self.camera_poses=None
    def capture(self,m,d,*args):
        if self.camera_poses is None:
            self.camera_poses={}
            for name in ('edge_left','edge_right','robot_camera'):
                c=m.camera(name).id
                self.camera_poses[name]={'position_world_m':d.cam_xpos[c].tolist(),'optical_axis_world':(-d.cam_xmat[c].reshape(3,3)[:,2]).tolist(),'fovy_deg':float(m.cam_fovy[c])}
        self.realtime=8<=d.time<25
        before=self.frames;super().capture(m,d,*args)
        if self.frames==before:return
        state=args[3];shot=inspection_shot(m,d);label=shot[1] if shot else 'mission'
        self.frame_writer.writerow([before,before/25,float(d.time),state,label])
        self.last_state=state;self.last_simulation_time=float(d.time)
        if self.frames%25==0:self.frame_stream.flush()
        for time,name in [(10.,'camera_rigs_overview'),(13.,'left_panel_camera'),(16.5,'right_panel_camera'),(20.,'onboard_camera'),(24.,'camera_rigs_and_panel')]:
            target=self.directory/(name+'.png')
            if d.time>=time and not target.exists():self.last_picture.save(target)
    def close(self,report=None):
        before=self.frames
        try:
            super().close(report)
            for frame in range(before,self.frames):
                self.frame_writer.writerow([frame,frame/25,self.last_simulation_time,self.last_state,'held final result; no new physical time'])
            path=self.directory/'cinematic_metadata.json';metadata=json.loads(path.read_text())
            metadata.update({'scope':'Complete fresh combined cleaning mission with visible calibrated inspection hardware','playback':'1x during initial deposition, camera-hardware inspection at simulation t=8..25 s, brush inspections, solid contact/tray landing and dock service; other transits 12x; final result held 3 s','frame_provenance':'frame_map.csv maps every encoded frame to actual integrated simulation time; final hold is explicitly labelled','camera_hardware':'Two elevated panel units and one onboard camera, rendered at the actual sensor poses; presentation-only housings','initial_sensor_poses':self.camera_poses})
            path.write_text(json.dumps(metadata,indent=2)+'\n')
        finally:self.frame_stream.close()


def record(directory,duration=1000.):
    directory=Path(directory)
    if directory.exists():raise FileExistsError(directory)
    sources={p.name:p.read_bytes() for p in sorted((ROOT/'src').glob('*.py'))}
    model=(ROOT/'models/collection_cleaning_crawler.xml').read_bytes()
    report=run(directory,scenario='combined',duration=duration,video_factory=CompleteCameraVideo)
    snapshot=directory/'source_snapshot';snapshot.mkdir()
    for name,content in sources.items():(snapshot/name).write_bytes(content)
    (directory/'executed_model.xml').write_bytes(model)
    (directory/'launch_manifest.json').write_text(json.dumps({'source_hashes':{name:hashlib.sha256(data).hexdigest() for name,data in sources.items()},'model_sha256':hashlib.sha256(model).hexdigest(),'duration_limit_s':duration,'purpose':'Fresh complete camera-hardware + cleaning recording; short --duration previews are not full mission evidence'},indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--duration',type=float,default=1000.)
    args=parser.parse_args();record(args.output_dir,args.duration)
