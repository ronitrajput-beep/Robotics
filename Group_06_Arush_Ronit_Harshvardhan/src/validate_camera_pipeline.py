"""Functional RGB checks using actual MuJoCo camera images, not label buffers."""
import os
os.environ.setdefault('MUJOCO_GL','egl')
from pathlib import Path
import argparse,json
import mujoco,numpy as np
from PIL import Image
from panel_vision import CameraCalibration,detect_dirt
from surface_debris import SurfaceDebris


def run(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    m=mujoco.MjModel.from_xml_path(str(Path(__file__).resolve().parents[1]/'models/guarded_cleaning_crawler.xml'))
    d=mujoco.MjData(m);mujoco.mj_forward(m,d)
    rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3).copy();origin=d.xpos[rack].copy()
    truth=[[-1.2,.6],[.2,.5],[1.1,-.4]];field=SurfaceDebris();report={}
    with mujoco.Renderer(m,height=480,width=640) as renderer:
        for dirty in (False,True):
            if dirty:field.deposit(truth)
            fused=[]
            for name in ('edge_left','edge_right','robot_camera'):
                camera=m.camera(name).id;renderer.update_scene(d,camera=camera);field.append_visuals(renderer.scene,origin,R)
                rgb=renderer.render();Image.fromarray(rgb).save(directory/f'{name}_{dirty}.png')
                calibration=CameraCalibration(d.cam_xpos[camera].copy(),d.cam_xmat[camera].reshape(3,3).copy(),m.cam_fovy[camera],origin,R)
                detections,_=detect_dirt(rgb,calibration)
                for detection in detections:
                    point=np.array([detection['panel_x_m'],detection['panel_y_m']])
                    if detection['confidence']>=.8 and all(np.linalg.norm(point-other)>.12 for other in fused):fused.append(point)
            report[str(dirty)]=[p.tolist() for p in fused]
            if not dirty:assert not fused, 'Clean image produced dirt detections'
            else:
                assert len(fused)==len(truth),f'Expected three patches, got {len(fused)}'
                errors=[min(np.linalg.norm(np.array(t)-p) for p in fused) for t in truth]
                assert max(errors)<.06,errors
                report['localisation_errors_m']=errors
    (directory/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();run(a.output_dir)
