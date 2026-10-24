import sys,unittest
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(root/'src'),str(root/'analytics')]
from planning import raster,segment_reference,clearance
from photovoltaic_degradation_economics import economics

class Checks(unittest.TestCase):
    def test_cross_track(self):
        target,error=segment_reference(np.array([1.,.2]),np.array([0.,0]),np.array([2.,0]))
        self.assertAlmostEqual(error,.2);np.testing.assert_allclose(target,[1.3,0])
    def test_path_clearance(self):
        self.assertTrue(all(clearance(p)>.1 for p in raster()))
        self.assertLess(clearance([2.8,0]),0)
    def test_economics(self):
        self.assertAlmostEqual(economics()['payback_months'],12*.65/.72)
        self.assertIsNone(economics(robot_cost_ratio=1.1)['payback_months'])
        self.assertIsNone(economics(arrival_rate=.3)['queue_wait_hours'])
        with self.assertRaises(ValueError):economics(service_rate=0)

if __name__=='__main__':unittest.main()
