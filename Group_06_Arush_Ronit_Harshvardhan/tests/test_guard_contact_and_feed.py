import os
import sys,tempfile,unittest,json
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from guarded_geometry import edge_raster
from surface_debris import SurfaceDebris
from cinematic_video import CinematicVideo


class GuardContactChecks(unittest.TestCase):
    def test_wall_contacts_cannot_transmit_climbing_friction(self):
        root=Path(__file__).resolve().parents[1]
        m=mujoco.MjModel.from_xml_path(str(root/'models/guarded_cleaning_crawler.xml'));d=mujoco.MjData(m)
        mujoco.mj_forward(m,d);rack=m.body('pv_array_rack').id
        R=d.xmat[rack].reshape(3,3).copy();o=d.xpos[rack].copy()
        d.qpos[:3]=o+R@np.array([2.79,0,.12]);mujoco.mj_forward(m,d)
        wall_contacts=[]
        for i,c in enumerate(d.contact):
            if any(m.geom(int(g)).name.startswith('guard_') for g in (c.geom1,c.geom2)):
                wall_contacts.append(c);self.assertEqual(c.dim,1)
                wrench=np.zeros(6);mujoco.mj_contactForce(m,d,i,wrench)
                np.testing.assert_allclose(wrench[1:],0,atol=1e-12)
        self.assertTrue(wall_contacts)
    def test_row_reversal_retreats_before_diagonal_turn(self):
        route=edge_raster('inward_turns')
        # First row end -> straight retreat -> inward diagonal -> next row end.
        self.assertAlmostEqual(route[1,1],route[2,1])
        self.assertGreater(abs(route[1,0])-abs(route[2,0]),.69)
        self.assertLess(abs(route[3,0]),1.1)
        np.testing.assert_array_equal(route[0],route[-1])
    def test_scattered_deposits_vary_shape_size_and_position(self):
        field=SurfaceDebris();field.deposit_scattered([0,0],np.random.default_rng(603))
        self.assertEqual(len(field.patches),3)
        self.assertGreater(np.ptp([p.radius for p in field.patches]),.001)
        self.assertGreater(np.ptp([p.angle for p in field.patches]),.1)
        json.dumps(field.summary())


class ActualFeedLayoutChecks(unittest.TestCase):
    def test_rgb_feed_is_displayed_without_modifying_detector_input(self):
        root=Path(__file__).resolve().parents[1]
        m=mujoco.MjModel.from_xml_path(str(root/'models/guarded_cleaning_crawler.xml'));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
        source=np.full((480,640,3),[20,40,80],np.uint8);original=source.copy()
        views={name:{'rgb':source,'detections':[{'confidence':1.,'bbox_xyxy':[100,100,140,140]}]} for name in ('edge_left','edge_right','robot_camera')}
        with tempfile.TemporaryDirectory() as directory:
            video=CinematicVideo(directory);video.update_sensor_views(0,views)
            rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3)
            video.capture(m,d,SurfaceDebris(),d.xpos[rack],R,'HOME_MONITOR',{'qualified_contact_fraction':0},0)
            image=np.array(video.last_picture)
            region=image[120:150,1020:1060]
            self.assertTrue(((region[:,:,1]>240)&(region[:,:,0]<100)).any())
            video.close()
        np.testing.assert_array_equal(source,original)
