import sys,tempfile,unittest
from pathlib import Path
import numpy as np
import mujoco
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from panel_vision import CameraCalibration,detect_dirt
from solid_object_demo import run


class EdgeVisionChecks(unittest.TestCase):
    def test_bright_edge_patches_are_not_missed(self):
        root=Path(__file__).resolve().parents[1]
        m=mujoco.MjModel.from_xml_path(str(root/'models/guarded_cleaning_crawler.xml'))
        d=mujoco.MjData(m);mujoco.mj_forward(m,d)
        rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3);origin=d.xpos[rack]
        points=[]
        for name in ('edge_left','edge_right'):
            rgb=np.array(Image.open(Path(__file__).parent/'fixtures'/f'{name}_bright.png'))
            c=m.camera(name).id
            cal=CameraCalibration(d.cam_xpos[c],d.cam_xmat[c].reshape(3,3),m.cam_fovy[c],origin,R)
            detections,_=detect_dirt(rgb,cal)
            for detection in detections:
                p=np.array([detection['panel_x_m'],detection['panel_y_m']])
                if detection['confidence']>=.8 and all(np.linalg.norm(p-q)>.12 for q in points):points.append(p)
        self.assertEqual(len(points),6)
        self.assertTrue(any(p[0]<-2.8 for p in points))
        self.assertTrue(any(p[0]>2.8 for p in points))


class LargerSolidChecks(unittest.TestCase):
    def test_object_persists_and_is_physically_caught(self):
        alpha=[];positions=[]
        def observe(m,d,info):
            g=m.geom('solid_object_geom').id
            alpha.append(float(m.geom_rgba[g,3]));positions.append(info['position'])
        with tempfile.TemporaryDirectory() as directory:
            result=run(Path(directory)/'solid',observe)
        self.assertTrue(result['fully_left_glass']);self.assertTrue(result['contacted_catch_tray'])
        self.assertEqual(result['mass_kg'],.12)
        self.assertTrue(all(a==1 for a in alpha))
        self.assertLess(np.linalg.norm(np.diff(positions,axis=0),axis=1).max(),.1)
        times=[e['time_s'] for e in result['events']]
        self.assertEqual(times,sorted(times))
        self.assertGreater(result['peak_brush_object_force_N'],0)
