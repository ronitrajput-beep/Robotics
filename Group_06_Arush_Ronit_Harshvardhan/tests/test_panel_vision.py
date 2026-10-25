import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from panel_vision import CameraCalibration,detect_dirt
from surface_debris import SurfaceDebris


class VisionChecks(unittest.TestCase):
    def camera(self):
        return CameraCalibration(np.array([0.,0.,5.02]),np.eye(3),60,np.zeros(3),np.eye(3))
    def test_projection(self):
        np.testing.assert_allclose(self.camera().project_pixel(160,120,320,240),[0,0],atol=1e-9)
    def test_rgb_detection_and_clean_scene(self):
        image=np.full((240,320,3),[25,45,80],np.uint8)
        self.assertEqual(detect_dirt(image,self.camera())[0],[])
        image[115:125,155:165]=[100,55,20]
        detections,_=detect_dirt(image,self.camera())
        self.assertEqual(len(detections),1)
        self.assertLess(abs(detections[0]['panel_x_m']),.02)
    def test_no_cleaning_without_contact_or_with_large_gap(self):
        field=SurfaceDebris();field.deposit([(0,0)])
        field.clean(np.array([0,0,.08]),np.array([0,1,0]),.06,.4,0,10,.5)
        self.assertEqual(field.patches[0].remaining,1)
        field.clean(np.array([0,0,.3]),np.array([0,1,0]),.06,.4,10,10,.5)
        self.assertEqual(field.patches[0].remaining,1)
        field.clean(np.array([0,0,.08]),np.array([0,1,0]),.06,.4,10,10,.5)
        self.assertLess(field.patches[0].remaining,.1)
