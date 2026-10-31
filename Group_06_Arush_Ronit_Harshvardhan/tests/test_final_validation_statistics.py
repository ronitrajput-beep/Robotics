"""Boundary and reference checks for completion uncertainty, not trial data."""
import sys,unittest
from pathlib import Path
from scipy import stats
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'analytics'))
from analyse_final_validation import wilson

class CompletionIntervalChecks(unittest.TestCase):
    def test_exact_zero_and_one_have_valid_plot_errors(self):
        for successes in (0,30):
            fraction=successes/30;lo,hi=wilson(successes,30)
            self.assertLessEqual(0.,lo);self.assertLessEqual(lo,fraction)
            self.assertLessEqual(fraction,hi);self.assertLessEqual(hi,1.)
            self.assertGreaterEqual(fraction-lo,0.);self.assertGreaterEqual(hi-fraction,0.)
    def test_matches_independent_scipy_wilson_reference(self):
        for successes in (0,1,15,29,30):
            reference=stats.binomtest(successes,30).proportion_ci(method='wilson')
            lo,hi=wilson(successes,30)
            self.assertAlmostEqual(lo,reference.low,places=14)
            self.assertAlmostEqual(hi,reference.high,places=14)
