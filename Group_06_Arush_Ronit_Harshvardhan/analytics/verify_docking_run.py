"""Independent checks and figures from the saved full-mission docking evidence."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
p=root/'analytics/docked_nominal_real_trials.csv.gz'
d=pd.read_csv(p,low_memory=False);r=json.loads(p.with_suffix('.json').read_text())
assert r['status']=='DOCKED'
assert r['waypoints_reached']==r['waypoints_total']
assert r['dock_error_m']<=.12
assert r['terminal_speed_mps']<.02
assert r['terminal_angular_speed_rad_s']<.05
assert r['terminal_brush_speed_rad_s']<1
assert np.allclose(np.diff(d.time_s),.002,atol=1e-9)
assert np.isfinite(d.select_dtypes('number')).all().all()
# Check the logged settling window independently of the supervisor state.
window=d[d.time_s>=r['time_s']-.5]
assert len(window)>=249
assert (window.speed_mps<.02).all()
assert (window.angular_speed_rad_s<.05).all()
assert (window.brush_rad_s.abs()<1).all()
assert (window.state=='DOCKING').all()
assert (d.clearance_m>0).all()
fig,axes=plt.subplots(1,2,figsize=(10,4))
axes[0].plot(d.x_m,d.y_m,lw=.7);axes[0].scatter([0],[-1],marker='x',color='red',label='Dock target');axes[0].set(xlabel='Panel x (m)',ylabel='Panel y (m)',title='Measured complete route');axes[0].axis('equal');axes[0].legend()
tail=d[d.time_s>d.time_s.max()-2]
axes[1].plot(tail.time_s,tail.speed_mps,label='Planar speed (m/s)');axes[1].plot(tail.time_s,tail.angular_speed_rad_s,label='Angular speed (rad/s)');axes[1].set(xlabel='Simulation time (s)',title='Measured endpoint settling');axes[1].legend();fig.tight_layout();fig.savefig(root/'docs/validation/docking_result.png',dpi=300)
print(f"Docking evidence verified: {len(d)} samples, 500 Hz, {r['dock_error_m']:.4f} m endpoint error")
