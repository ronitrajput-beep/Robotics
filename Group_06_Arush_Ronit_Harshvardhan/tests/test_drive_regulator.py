import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from drive_regulator import DriveRegulator


class DriveRegulatorChecks(unittest.TestCase):
    def test_acceleration_torque_slew_and_limit(self):
        regulator=DriveRegulator(.002);last=np.zeros(4);last_target=np.zeros(4)
        for i in range(1000):
            out=regulator.update(np.ones(4)*100,np.zeros(4),('DRIVE',1))
            self.assertTrue((abs(out-last)<=.008000001).all())
            self.assertTrue((abs(regulator.targets-last_target)<=.008000001).all())
            self.assertTrue((abs(out)<=1.0).all())
            last=out;last_target=regulator.targets.copy()
        self.assertLess(abs(regulator.integral).max(),.8)
    def test_mode_reset_and_braking(self):
        regulator=DriveRegulator(.002)
        for i in range(300):regulator.update(np.ones(4),np.zeros(4),('DRIVE',1))
        regulator.update(np.zeros(4),np.ones(4),('BRAKING',))
        self.assertLess(abs(regulator.integral).max(),.01)
        for i in range(500):regulator.update(np.zeros(4),np.zeros(4),('BRAKING',))
        np.testing.assert_allclose(regulator.targets,0,atol=1e-10)
