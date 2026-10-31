import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from cleaning_coverage import CoverageMap


class CoverageChecks(unittest.TestCase):
    def test_no_qualified_cleaning_without_contact_rotation_and_sweep(self):
        for force, speed, sweep in [(0, 15, True), (2, 0, True), (2, 15, False)]:
            c = CoverageMap()
            c.update([0, 0], [0, 1], .06, .275, force, speed, sweep, .002)
            self.assertGreater(c.geometric.sum(), 0)
            self.assertFalse(c.qualified.any())
            np.testing.assert_array_equal(c.soil, 1)

    def test_union_and_dose_are_distinct(self):
        c = CoverageMap()
        c.update([0, 0], [0, 1], .06, .275, 2, 15, True, .5)
        first = c.qualified.copy()
        c.update([0, 0], [0, 1], .06, .275, 2, 15, True, .5)
        np.testing.assert_array_equal(c.qualified, first)
        np.testing.assert_allclose(c.soil[first], np.exp(-2))
        self.assertAlmostEqual(c.summary()['interior_area_m2'], 15.81)
        self.assertAlmostEqual(c.summary()['panel_area_m2'], c.X.size*c.dx*c.dy)

    def test_orientation_and_outside_panel(self):
        a, b = CoverageMap(), CoverageMap()
        a.update([0, 0], [0, 1], .06, .275, 2, 15, True, .002)
        b.update([0, 0], [1, 0], .06, .275, 2, 15, True, .002)
        self.assertFalse(np.array_equal(a.qualified, b.qualified))
        c = CoverageMap()
        c.update([4, 0], [0, 1], .06, .275, 2, 15, True, .002)
        self.assertFalse(c.geometric.any())

class ExpandedRasterChecks(unittest.TestCase):
    def test_layout_retains_full_footprint_margin(self):
        from planning import raster, clearance
        route = raster('expanded')
        self.assertEqual(len(route), 17)
        self.assertGreaterEqual(min(clearance(p) for p in route), .14)
        self.assertAlmostEqual(route[:, 1].max(), 1.35)
        self.assertAlmostEqual(route[:, 1].min(), -1.35)
        with self.assertRaises(ValueError):
            raster('invalid')

    def test_safe_return_retains_original_lower_row(self):
        from planning import raster
        route = raster('expanded_safe_return')
        self.assertAlmostEqual(route[:, 1].min(), -1.20)
        self.assertAlmostEqual(route[:, 1].max(), 1.35)
