import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from safety import StopSupervisor
from crawler_cleaning_controller import mission

class SafetyChecks(unittest.TestCase):
    def test_latched_stop(self):
        s=StopSupervisor()
        self.assertEqual(s.update(0,.2,1,False),'BRAKING')
        self.assertEqual(s.update(.1,0,1,True),'BRAKING')
        self.assertEqual(s.update(.7,0,1,True),'STOPPED')
        self.assertEqual(s.reason,'POSE_DROPOUT')
    def test_cannot_stop(self):
        s=StopSupervisor()
        self.assertEqual(s.update(0,.3,.01),'BRAKING')
        self.assertEqual(s.update(3.1,.3,.01),'ABORT_UNSTOPPED')
    def test_pose_dropout(self):
        r=mission(duration=8,fault='pose_dropout')
        self.assertEqual(r['status'],'STOPPED')
        self.assertEqual(r['stop_reason'],'POSE_DROPOUT')
        self.assertLess(r['terminal_speed_mps'],.02)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'run.csv';p.write_text('preserve')
            with self.assertRaises(FileExistsError):mission(duration=1,output=p)
            self.assertEqual(p.read_text(),'preserve')

if __name__=='__main__':unittest.main()
