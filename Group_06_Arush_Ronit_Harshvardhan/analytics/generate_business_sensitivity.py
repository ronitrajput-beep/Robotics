"""Assumption sensitivity; no claim of measured economic savings."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photovoltaic_degradation_economics import economics
root=Path(__file__).resolve().parents[1]
rows=[economics(robot_cost_ratio=float(k)) for k in np.linspace(.05,1.2,116)]
d=pd.DataFrame(rows);d.to_csv(root/'analytics/business_sensitivity.csv',index=False)
f,axs=plt.subplots(1,2,figsize=(10,4));axs[0].plot(d.kappa,d.payback_months);axs[0].axvline(1,color='red',ls='--',label='No positive savings');axs[0].set(xlabel='Assumed robot/manual annual cost ratio',ylabel='Payback (months)',ylim=(0,100));axs[0].legend()
axs[1].plot(d.kappa,d.NCRI);axs[1].axhline(0,color='red',ls='--');axs[1].set(xlabel='Assumed robot/manual annual cost ratio',ylabel='Normalised cost reduction')
f.suptitle('Scenario assumptions: capital ratio 0.65; not observed financial results');f.tight_layout();f.savefig(root/'docs/validation/business_sensitivity.png',dpi=300)
(root/'analytics/business_assumptions.json').write_text(json.dumps({'input_status':'unverified scenario assumptions, not sourced deployment costs','capital_ratio':.65,'robot_cost_ratio_range':[.05,1.2],'life_years':5,'manual_hours_per_month':120,'supervision_hours_per_month':20,'maintenance_hours_per_month':10,'queue_arrivals_per_hour':.1,'queue_service_rate_per_hour':.25,'warning':'Queue and labour rates are illustrative and not calibrated to current partial-panel route.'},indent=2))
print('Wrote sensitivity CSV, assumptions and 300 DPI figure.')
