"""Plot measured development telemetry; no synthetic target data."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
root=Path(__file__).resolve().parents[1]
source=root/'analytics/development_real_trials.csv'
if not source.exists(): source=source.with_suffix('.csv.gz')
d=pd.read_csv(source)
f,ax=plt.subplots(1,2,figsize=(11,4))
ax[0].plot(d.x_m,d.y_m,lw=.8,label='MuJoCo chassis position')
ax[0].set(xlim=(-3,3),ylim=(-2,2),xlabel='Panel x (m)',ylabel='Panel y (m)',title='Development trajectory')
ax[0].legend();ax[0].set_aspect('equal')
ax[1].plot(d.time_s,d.coverage_fraction*100,label='Brush-contact coverage')
ax[1].plot(d.time_s,d.soil_removed_fraction*100,label='Uncalibrated soil proxy')
ax[1].set(xlabel='Simulation time (s)',ylabel='Panel fraction (%)',title='Development run: not final evaluation');ax[1].legend()
f.tight_layout();f.savefig(root/'docs/validation/development_run.png',dpi=300)
