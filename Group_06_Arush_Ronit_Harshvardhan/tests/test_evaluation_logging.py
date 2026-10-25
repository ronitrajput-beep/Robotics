import sys,tempfile,unittest,json,lzma,csv
from pathlib import Path
import numpy as np,mujoco
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cleaning_coverage import CoverageMap
from crawler_cleaning_controller import mission
from run_final_validation import CompactTelemetry
from panel_vision import CameraCalibration,detect_dirt

class EvaluationChecks(unittest.TestCase):
    def test_roi_coverage_equals_full_grid_reference(self):
        fast=CoverageMap();geometric=fast.geometric.copy();qualified=fast.qualified.copy();soil=fast.soil.copy();rng=np.random.default_rng(723)
        for i in range(600):
            centre=rng.uniform([-4.5,-3],[4.5,3]);axle=rng.normal(size=2)*rng.uniform(.5,1.2);norm=np.linalg.norm(axle);lateral=axle/norm;forward=np.array([lateral[1],-lateral[0]])
            radius=rng.uniform(.02,.1);width=rng.uniform(.2,.5);force=float(i%3);speed=3.;sweeping=i%2==0
            dx,dy=fast.X-centre[0],fast.Y-centre[1];mask=(abs(dx*forward[0]+dy*forward[1])<radius)&(abs(dx*lateral[0]+dy*lateral[1])<width*norm)
            geometric|=mask
            if sweeping and force>.1:qualified|=mask;soil[mask]*=np.exp(-.004)
            fast.update(centre,axle,radius,width,force,speed,sweeping,.002)
        np.testing.assert_array_equal(fast.geometric,geometric);np.testing.assert_array_equal(fast.qualified,qualified);np.testing.assert_array_equal(fast.soil,soil)
    def test_component_optimisation_preserves_real_camera_detections(self):
        m=mujoco.MjModel.from_xml_path(str(ROOT/'models/collection_cleaning_crawler.xml'));d=mujoco.MjData(m);mujoco.mj_forward(m,d);rack=m.body('pv_array_rack').id;R=d.xmat[rack].reshape(3,3);o=d.xpos[rack]
        for fixture in json.loads((ROOT/'tests/fixtures/rgb_components_before_optimisation.json').read_text()):
            c=m.camera(fixture['camera']).id;cal=CameraCalibration(d.cam_xpos[c],d.cam_xmat[c].reshape(3,3),m.cam_fovy[c],o,R)
            detected,_=detect_dirt(np.array(Image.open(ROOT/fixture['image'])),cal)
            self.assertEqual(detected,fixture['detections'])
    def test_compact_logger_does_not_change_physics_and_retains_torques(self):
        options=dict(duration=2.,guarded=True,route_profile='external_dock',guarded_model_path=ROOT/'models/collection_cleaning_crawler.xml',should_move=lambda:False)
        reference=mission(**options)
        with tempfile.TemporaryDirectory() as tmp:
            sink=CompactTelemetry(Path(tmp)/'samples.csv.xz');observed=mission(**options,telemetry_sink=sink);sink.close()
            with lzma.open(sink.path,'rt') as f:rows=list(csv.DictReader(f))
        for key in ('status','time_s','path_tracking_rmse_m','effort_Nm2_s','positive_mechanical_work_J','maximum_chassis_height_m','maximum_chassis_tilt_deg'):self.assertEqual(reference[key],observed[key])
        self.assertEqual(len(rows),1000);self.assertIn('tau_brush_Nm',rows[0]);self.assertIn('vx_panel_mps',rows[0]);self.assertEqual(sink.window_n,1000)
