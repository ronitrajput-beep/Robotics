import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analytics'))
from analyse_tracking_benchmark import comparison

class StatisticsCheck(unittest.TestCase):
    def test_direction_and_interval(self):
        r=comparison([1,2,3,4],[11,12,13,14])
        self.assertAlmostEqual(r['mean_difference_m'],-10)
        self.assertLess(r['ci95_m'][1],0)
        self.assertLess(r['p_value'],.001)
    def test_insufficient(self):
        with self.assertRaises(ValueError):comparison([1],[2])

if __name__=='__main__':unittest.main()
