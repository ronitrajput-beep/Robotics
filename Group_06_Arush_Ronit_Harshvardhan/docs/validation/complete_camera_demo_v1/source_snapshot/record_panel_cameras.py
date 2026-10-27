"""Short actual-physics equipment tour of visible, calibrated camera housings."""
import os,sys
os.environ.setdefault('MUJOCO_GL','cgl' if sys.platform=='darwin' else 'glfw' if sys.platform=='win32' else 'egl')
from pathlib import Path
import argparse,hashlib,json
import mujoco,numpy as np
from cinematic_video import CinematicVideo
from vision_mission import run


def tour_shot(m,d):
    cam=mujoco.MjvCamera();mujoco.mjv_defaultCamera(cam)
    t=float(d.time)
    if t<5 or t>=18:
        points=np.array([d.cam_xpos[m.camera(name).id] for name in ('edge_left','edge_right')])
        origin=d.xpos[m.body('pv_array_rack').id]
        cam.lookat[:]=.5*(points.mean(axis=0)+origin)
        cam.distance=11.7;cam.elevation=-35;cam.azimuth=100+5*np.sin(t/5)
        return cam,'PANEL INSPECTION CAMERAS - FRAME-SUPPORTED RIGS'
    name='edge_left' if t<10 else 'edge_right' if t<15 else 'robot_camera'
    cid=m.camera(name).id;C=d.cam_xmat[cid].reshape(3,3);cp=d.cam_xpos[cid]
    cam.lookat[:]=cp+C[:,2]*.05
    # Inspect the lens from its actual front side, slightly off the optical axis.
    offset=-C[:,2]+.35*C[:,0]+.3*C[:,1];offset/=np.linalg.norm(offset)
    cam.azimuth=float(np.rad2deg(np.arctan2(offset[1],offset[0])))+180.
    cam.elevation=float(-np.rad2deg(np.arcsin(offset[2])))
    cam.distance=1.05 if name!='robot_camera' else .65
    label={'edge_left':'LEFT PANEL CAMERA / edge_left','edge_right':'RIGHT PANEL CAMERA / edge_right','robot_camera':'ONBOARD CAMERA / robot_camera'}[name]
    return cam,label


class CameraTourVideo(CinematicVideo):
    def __init__(self,directory):
        super().__init__(directory,presentation_shot=tour_shot,realtime=True)
        self.camera_poses=None
    def capture(self,m,d,*args):
        if self.camera_poses is None:
            rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3);origin=d.xpos[rack]
            self.camera_poses={}
            for name in ('edge_left','edge_right','robot_camera'):
                cid=m.camera(name).id;C=d.cam_xmat[cid].reshape(3,3)
                self.camera_poses[name]={'position_world_m':d.cam_xpos[cid].tolist(),'position_panel_m':(R.T@(d.cam_xpos[cid]-origin)).tolist(),'optical_direction_world':(-C[:,2]).tolist(),'fovy_deg':float(m.cam_fovy[cid])}
        before=self.frames;super().capture(m,d,*args)
        if self.frames==before:return
        for time,name in [(3.,'rig_overview'),(7.,'left_camera'),(12.,'right_camera'),(17.,'robot_camera'),(19.5,'rig_overview_end')]:
            path=self.directory/(name+'.png')
            if d.time>=time and not path.exists():self.last_picture.save(path)
    def close(self,report=None):
        # This deliberately short tour is not a complete cleaning-cycle result.
        if report is not None:report['recording_scope']='20-second actual-physics camera hardware tour; horizon intentionally precedes mission completion'
        super().close(None)
        (self.directory/'cinematic_cleaning.mp4').rename(self.directory/'panel_camera_tour.mp4')
        path=self.directory/'cinematic_metadata.json';meta=json.loads(path.read_text())
        meta.update({'scope':'Camera equipment tour; actual RGB inputs and actual stepping, not a full cleaning cycle','playback':'1x throughout; no held mission-result card','camera_poses_at_start':self.camera_poses,'sensor_calibration':'Unchanged existing sensors: two elevated edge views, one onboard view','hardware':'Presentation-only housings, lenses, LEDs, posts, frame braces, brackets and cables; no added collision bodies','tour_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
        path.unlink();(self.directory/'panel_camera_tour_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();run(args.output_dir,scenario='combined',duration=20.,video_factory=CameraTourVideo)
