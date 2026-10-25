import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from transit_planning import cross_slope_transit
from guarded_geometry import edge_raster,sweep_goal_count


class TransitPlanningChecks(unittest.TestCase):
    def test_transits_bound_uphill_heading_and_reach_requested_endpoint(self):
        cases=[([0,-1.1],[0,1.0]),([1.8,-1.4],[-2.72,1.53]),([-2.72,1.53],[-1.7,-.06]),([1.2,0],[1.2,1.5])]
        for start,end in cases:
            points=np.vstack([start,cross_slope_transit(start,end)])
            np.testing.assert_allclose(points[-1],end)
            for dx,dy in np.diff(points,axis=0):
                self.assertTrue(abs(dy)<.020001 or abs(dy)<=.300001*abs(dx),(dx,dy))
            self.assertLessEqual(abs(points[:,0]).max(),2.72)
    def test_return_route_is_separate_from_coverage(self):
        route=edge_raster('inward_turns');count=sweep_goal_count('inward_turns')
        self.assertAlmostEqual(route[count,1],-1.6)
        self.assertGreater(len(route)-count,3)
        np.testing.assert_array_equal(route[0],route[-1])
        for dx,dy in np.diff(route[count:],axis=0):
            self.assertTrue(abs(dy)<.020001 or abs(dy)<=.300001*abs(dx))
