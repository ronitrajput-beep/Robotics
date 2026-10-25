import sys,tempfile,unittest
from pathlib import Path
import numpy as np
import mujoco
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from build_collection_model import build
from collection_system import CollectionSystem
from surface_debris import SurfaceDebris
from guarded_geometry import edge_raster,sweep_goal_count,supported_position
from crawler_cleaning_controller import mission

class CollectionChecks(unittest.TestCase):
    def test_dust_is_conserved_through_capture_and_emptying(self):
        field=SurfaceDebris();field.deposit([(0,0)]);system=CollectionSystem()
        before=system.soil_mass(field)
        field.clean(np.array([0.,0.,.08]),np.array([0.,1.,0.]),.06,.4,10.,15.,.5)
        system.pickup(before,system.soil_mass(field),.5)
        self.assertGreater(system.bin_kg,0)
        system.sample(1.,'SWEEP',field,.002)
        self.assertEqual(system.station_kg,0.)
        for i in range(4000):system.sample(2+i*.002,'DOCK_SERVICE',field,.002)
        result=system.summary(field)
        self.assertLess(abs(result['mass_balance_error_kg']),1e-14)
        self.assertEqual(result['onboard_bin_kg'],0.)
        self.assertGreater(result['station_waste_kg'],0.)
        self.assertAlmostEqual(result['dock_charge_energy_J'],240.,places=8)
    def test_external_home_and_supported_opening(self):
        route=edge_raster('external_dock')
        np.testing.assert_array_equal(route[0],route[-1]);self.assertLess(route[0,0],-3.22)
        self.assertEqual(sweep_goal_count('external_dock'),25)
        np.testing.assert_allclose(route[-2],[-2.72,1.53])
        self.assertTrue(supported_position([-3.65,1.6,.12],True))
        self.assertFalse(supported_position([-3.65,0,.12],True))
        self.assertFalse(supported_position([0,0,-.1],True))
    def test_external_dock_physically_supports_stationary_robot(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'model.xml';build(path)
            m=mujoco.MjModel.from_xml_path(str(path))
            self.assertAlmostEqual(m.body_subtreemass[m.body('crawler_chassis').id],8.5)
            self.assertAlmostEqual(m.geom_pos[m.geom('dock_platform').id,2]+m.geom_size[m.geom('dock_platform').id,2],.02)
            contacts=[]
            def sample(m,d,state,coverage):
                names=[{m.geom(c.geom1).name,m.geom(c.geom2).name} for c in d.contact]
                contacts.extend(pair for pair in names if 'dock_platform' in pair and any(n.endswith('_roller') for n in pair))
            result=mission(duration=3,guarded=True,route_profile='external_dock',guarded_model_path=path,should_move=lambda:False,on_sample=sample)
        self.assertTrue(contacts)
        self.assertEqual(result['waypoints_reached'],0)
        self.assertLess(result['maximum_chassis_tilt_deg'],1.)
        self.assertLess(result['maximum_chassis_height_m'],.123)

    def test_service_does_not_report_complete_when_horizon_expires(self):
        from unittest.mock import patch
        route=np.array([[-3.65,1.53],[-3.50,1.53],[-3.65,1.53]])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'model.xml';build(path);states=[]
            with patch('crawler_cleaning_controller.edge_raster',return_value=route):
                result=mission(duration=10,guarded=True,route_profile='external_dock',guarded_model_path=path,dock_service_s=20,on_sample=lambda m,d,s,c:states.append(s))
        self.assertIn('DOCK_SERVICE',states)
        self.assertEqual(result['status'],'TIMEOUT')
        self.assertFalse(any(e['event']=='DOCK_SERVICE_COMPLETE' for e in result['events']))

    def test_collection_cutaway_and_service_preserve_sensor_rgb(self):
        from cinematic_scene import RooftopScene,make_renderer,render_studio,cinematic_camera
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'model.xml';build(path)
            m=mujoco.MjModel.from_xml_path(str(path));d=mujoco.MjData(m);mujoco.mj_forward(m,d)
            rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3).copy();origin=d.xpos[rack].copy()
            d.qpos[:3]=origin+R@[-3.65,1.53,.12];mujoco.mj_forward(m,d)
            qpos=d.qpos.copy();qvel=d.qvel.copy();rgba=m.geom_rgba.copy()
            scene=RooftopScene();scene.collection_status={'bin_g':5.,'station_g':2.,'charge_J':120.,'state':'DOCK_SERVICE'}
            with mujoco.Renderer(m,height=240,width=320) as sensor:
                sensor.update_scene(d,camera='edge_left');before=sensor.render().copy()
                studio=make_renderer(m,width=960,height=540)
                image=render_studio(studio,m,d,cinematic_camera(0,d,m),scene);studio.close()
                sensor.update_scene(d,camera='edge_left');after=sensor.render().copy()
            self.assertEqual(image.shape,(540,960,3))
            np.testing.assert_array_equal(before,after)
            np.testing.assert_array_equal(qpos,d.qpos);np.testing.assert_array_equal(qvel,d.qvel)
            np.testing.assert_array_equal(rgba,m.geom_rgba)
