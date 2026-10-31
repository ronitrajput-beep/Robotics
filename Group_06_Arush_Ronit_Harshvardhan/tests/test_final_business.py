"""Algebra/edge-case fixtures, not measured commercial data."""
import sys,json,copy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analytics'))
from final_business_model import calculate

class FinalBusinessChecks(unittest.TestCase):
    def setUp(self):
        self.inputs=json.loads((ROOT/'analytics/final_business_inputs.json').read_text())
        self.measured={'success_fraction':1.,'mean_attempt_s':600.,'mean_positive_mechanical_work_J':3600.,'mean_modelled_blower_J':7000.}
    def test_failed_service_has_no_finite_payback(self):
        self.measured['success_fraction']=0.;r=calculate(self.inputs,self.measured)
        self.assertFalse(r['viable_service']);self.assertIsNone(r['payback_months']);self.assertEqual(r['service_rate_sections_h'],0)
    def test_overloaded_queue_and_cost_increase_are_explicit(self):
        self.inputs['sections_per_day']=500;r=calculate(self.inputs,self.measured)
        self.assertFalse(r['queue_stable']);self.assertIsNone(r['queue_wait_h']);self.assertLess(r['NCRI'],0);self.assertIsNone(r['payback_months'])
    def test_manual_transfers_are_not_free_when_supervision_is_zero(self):
        self.inputs['supervision_fraction']=0.;r=calculate(self.inputs,self.measured)
        self.assertAlmostEqual(r['total_robot_related_person_h_month'],41.5)
        self.assertAlmostEqual(r['labour_reclaimed_person_h_month'],78.5)
    def test_capacity_has_consistent_seconds_to_hours_units(self):
        r=calculate(self.inputs,self.measured);mu=3600/780;arrival=21/8
        self.assertAlmostEqual(r['service_rate_sections_h'],mu);self.assertAlmostEqual(r['queue_wait_h'],arrival/(mu*(mu-arrival)))
        self.assertAlmostEqual(r['NCRI']+r['kappa'],1)
        self.assertAlmostEqual(r['payback_months'],12*.65/r['NCRI'])
