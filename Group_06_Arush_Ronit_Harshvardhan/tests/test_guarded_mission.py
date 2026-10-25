import sys,unittest
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from guarded_geometry import edge_raster,body_edge_gaps
from crawler_cleaning_controller import mission
from vision_mission import Trigger


class GuardedChecks(unittest.TestCase):
    def test_closed_home_route(self):
        route=edge_raster();np.testing.assert_array_equal(route[0],route[-1])
        self.assertGreater(route[:,0].max(),2.7)
        self.assertLess(route[:,1].min(),-1.7)
    def test_actual_box_not_brush_radius(self):
        gaps=body_edge_gaps(np.array([2.78,0,0]),np.eye(3))
        self.assertAlmostEqual(gaps[1],0)
    def test_guarded_model_collision_masks_and_fixed_width(self):
        root=Path(__file__).resolve().parents[1]
        m=mujoco.MjModel.from_xml_path(str(root/'models/guarded_cleaning_crawler.xml'))
        self.assertEqual(m.geom_contype[m.geom('guard_left').id],2)
        self.assertEqual(m.geom_conaffinity[m.geom('chassis_geom').id],3)
        self.assertEqual(m.geom_conaffinity[m.geom('brush_cylinder').id],1)
        self.assertAlmostEqual(m.geom_size[m.geom('brush_cylinder').id,1],.4)
    def test_idle_holds_and_brush_off(self):
        states=[]
        def record(m,d,state,coverage):
            states.append((state,float(d.ctrl[4])))
        r=mission(duration=2,guarded=True,should_move=lambda:False,on_sample=record)
        self.assertEqual(r['waypoints_reached'],0)
        self.assertEqual(r['coverage_metrics_v2']['qualified_contact_fraction'],0)
        self.assertTrue(all(state=='HOME_MONITOR' and brush==0 for state,brush in states))
    def test_trigger_requires_persistence_and_significant_targets(self):
        t=Trigger();t.observe(0,[[0,0]]);self.assertFalse(t.active)
        points=[[0,0],[1,0],[2,0]]
        t.observe(.5,points);self.assertFalse(t.active)
        t.observe(1,[]);t.observe(1.5,points);self.assertFalse(t.active)
        t.observe(2,points);self.assertTrue(t.active)
        t.observe(2.5,[]);self.assertTrue(t.active)

class CrumbPhysicsChecks(unittest.TestCase):
    def test_brush_physically_ejects_crumb_into_tray(self):
        import tempfile
        from validate_crumb import run
        with tempfile.TemporaryDirectory() as directory:
            result=run(Path(directory)/'crumb')
        self.assertTrue(result['fully_left_glass'])
        self.assertTrue(result['contacted_catch_tray'])
        self.assertGreater(result['peak_crumb_contact_force_N'],0)
