"""Integration checks for genuine stepping, logging and deterministic initialization."""
import csv,sys,tempfile
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from crawler_cleaning_controller import mission

class MissionChecks(unittest.TestCase):
    def test_reproducible_and_500hz(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'trial.csv'
            a=mission(seed=7,output=path,duration=2)
            b=mission(seed=7,duration=2)
            self.assertEqual(a,b)
            self.assertEqual(a['status'],'TIMEOUT')
            with path.open() as f:rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),1000)
            self.assertAlmostEqual(float(rows[1]['time_s'])-float(rows[0]['time_s']),.002)
            self.assertGreater(a['positive_mechanical_work_J'],0)
            self.assertGreater(float(rows[-1]['x_m']),float(rows[500]['x_m']))

if __name__=='__main__':unittest.main()
