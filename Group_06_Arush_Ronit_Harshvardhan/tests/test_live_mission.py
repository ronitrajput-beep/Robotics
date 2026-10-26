"""Actual RGB/physics integration with a non-GUI native-handle test double."""
import contextlib,gzip,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import mujoco,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from vision_mission import run


class NativeHandleDouble:
    def __init__(self,model,data,key_callback=None,**kwargs):
        self.cam=mujoco.MjvCamera();mujoco.mjv_defaultCamera(self.cam)
        self.user_scn=mujoco.MjvScene(model,maxgeom=10000)
        self.closed=False;self.sync_count=0;self.max_geoms=0
    def lock(self):return contextlib.nullcontext()
    def is_running(self):return not self.closed
    def sync(self):self.sync_count+=1;self.max_geoms=max(self.max_geoms,self.user_scn.ngeom)
    def close(self):self.closed=True


class LiveMissionChecks(unittest.TestCase):
    def test_live_overlay_keeps_actual_camera_decisions_and_physics_identical(self):
        handles=[]
        def launch(m,d,**kw):
            h=NativeHandleDouble(m,d,**kw);handles.append(h);return h
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'headless';b=Path(tmp)/'live'
            plain=run(a,scenario='combined',duration=8,save_images=False)
            with patch('mujoco.viewer.launch_passive',side_effect=launch):
                live=run(b,scenario='combined',duration=8,save_images=False,live_viewer=True,viewer_speed=1e9)
            self.assertEqual(gzip.open(a/'telemetry.csv.gz','rb').read(),gzip.open(b/'telemetry.csv.gz','rb').read())
            self.assertEqual((a/'observations.jsonl').read_bytes(),(b/'observations.jsonl').read_bytes())
            self.assertEqual(plain['trigger_events'],live['trigger_events']);self.assertTrue(live['trigger_events'])
            self.assertEqual(plain['physical_mission'],live['physical_mission'])
            self.assertTrue(handles[0].closed);self.assertGreater(handles[0].sync_count,100);self.assertGreater(handles[0].max_geoms,500)
            import csv
            with gzip.open(b/'telemetry.csv.gz','rt') as f:rows=list(csv.DictReader(f))
            start=np.array([float(rows[0]['x_m']),float(rows[0]['y_m'])]);end=np.array([float(rows[-1]['x_m']),float(rows[-1]['y_m'])])
            self.assertGreater(np.linalg.norm(end-start),.05)

    def test_clean_live_scene_remains_home_without_a_fake_start(self):
        with tempfile.TemporaryDirectory() as tmp,patch('mujoco.viewer.launch_passive',side_effect=NativeHandleDouble):
            report=run(Path(tmp)/'clean',scenario='clean',duration=5,save_images=False,live_viewer=True,viewer_speed=1e9)
        self.assertEqual(report['status'],'IDLE_COMPLETE');self.assertEqual(report['trigger_events'],[])

    def test_closing_window_stops_mission_and_closes_handle(self):
        handles=[]
        def launch(m,d,**kw):
            h=NativeHandleDouble(m,d,**kw);h.closed=True;handles.append(h);return h
        with tempfile.TemporaryDirectory() as tmp,patch('mujoco.viewer.launch_passive',side_effect=launch):
            report=run(Path(tmp)/'closed',scenario='combined',duration=5,save_images=False,live_viewer=True,viewer_speed=1e9)
        self.assertEqual(report['physical_mission']['status'],'USER_STOP');self.assertTrue(handles[0].closed)
