"""Dimensionless scenario economics. Defaults are assumptions, not sourced results."""
import argparse,json

def economics(manual_hours=120, supervision_hours=20, maintenance_hours=10,
              robot_cost_ratio=.28, capital_ratio=.65, life_years=5,
              arrival_rate=.1, service_rate=.25):
    if min(manual_hours,supervision_hours,maintenance_hours,robot_cost_ratio,capital_ratio,arrival_rate)<0 or life_years<=0 or service_rate<=0:
        raise ValueError('Invalid economic input')
    savings=1-robot_cost_ratio
    return {'input_status':'assumptions; replace with sourced inputs and measured throughput',
            'labour_reclaimed_hours_per_month':manual_hours-supervision_hours-maintenance_hours,
            'kappa':robot_cost_ratio,'NCRI':savings,
            'payback_months':12*capital_ratio/savings if savings>0 else None,
            'lifetime_normalised_payback':capital_ratio/(life_years*savings) if savings>0 else None,
            'utilisation':arrival_rate/service_rate,
            'queue_stable':arrival_rate<service_rate,
            'queue_wait_hours':arrival_rate/(service_rate*(service_rate-arrival_rate)) if arrival_rate<service_rate else None,
            'queue_assumption':'M/M/1; Poisson arrivals, independent exponential service times'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',help='JSON object with function parameter names');a=p.parse_args()
    inputs=json.load(open(a.inputs)) if a.inputs else {}
    print(json.dumps(economics(**inputs),indent=2,allow_nan=False))
