"""Plots from a completed combined run only; refuses overwriting figures."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot(directory):
    directory=Path(directory)
    if (directory/'collection_evidence.png').exists():raise FileExistsError('Evidence plot already exists')
    result=json.loads((directory/'result.json').read_text())
    motion=pd.read_csv(directory/'telemetry.csv.gz',low_memory=False)
    mass=pd.read_csv(directory/'collection.csv.gz');solid=pd.read_csv(directory/'solid.csv.gz')
    fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
    ax=axes[0,0];ax.add_patch(Rectangle((-3,-2),6,4,fc='#e5edf5',ec='#476176'))
    ax.add_patch(Rectangle((-4.5,1),1.5,1,fc='#d9e2df',ec='#476176'))
    ax.add_patch(Rectangle((-3.25,-2.66),6.5,.66,fc='#c5cdd0',ec='#476176'))
    ax.plot(motion.x_m[::100],motion.y_m[::100],lw=.7,color='#168489',label='Actual chassis path')
    ax.plot(solid.x_m[::10],solid.y_m[::10],lw=1.5,color='#b16f24',label='Persistent block path')
    ax.scatter([motion.x_m.iloc[0]],[motion.y_m.iloc[0]],marker='s',color='#168489',label='External home')
    ax.scatter([solid.x_m.iloc[-1]],[solid.y_m.iloc[-1]],marker='o',color='#b16f24')
    ax.set(xlabel='Panel x (m)',ylabel='Panel y (m)',title='Physical paths, dock and permanent tray',aspect='equal');ax.legend(fontsize=8)
    ax=axes[0,1]
    for col,label in [('surface_kg','Surface residual'),('bin_kg','Onboard bin'),('station_kg','Station waste')]:ax.plot(mass.time_s[::100],mass[col][::100]*1000,label=label)
    ax.plot(mass.time_s[::100],mass.deposited_kg[::100]*1000,ls='--',color='#555',label='Deposited total')
    ax.set(xlabel='Simulation time (s)',ylabel='Modelled fine-dust mass (g)',title='Explicit dust inventory (assumed loading)');ax.legend(fontsize=8)
    ax=axes[1,0]
    touch=result['physical_solid']['first_tool_contact_s'];window=solid[(solid.time_s>=touch-1)&(solid.time_s<=touch+5)]
    ax.plot(window.time_s,window.brush_force_N,color='#b16f24')
    for event in result['physical_solid']['events']:
        if 'OFF_GLASS' in event['event'] or 'TRAY_CONTACT' in event['event']:
            ax.axvline(event['time_s'],ls='--',lw=.8,label=event['event'].replace('SOLID_',''))
    ax.set(xlabel='Simulation time (s)',ylabel='Tool–block normal force (N)',title='Measured contact; glass damage is not modelled');ax.legend(fontsize=8)
    ax=axes[1,1];ax.plot(motion.time_s[::25],motion.chassis_tilt_deg[::25],color='#168489')
    ax.set(xlabel='Simulation time (s)',ylabel='Chassis tilt from panel normal (degrees)',title=f"Actual motion: peak {motion.chassis_tilt_deg.max():.3f}°")
    for a in axes.flat:a.grid(alpha=.15)
    fig.suptitle(f"Combined nominal development run: {result['status']} — not hardware validation")
    fig.savefig(directory/'collection_evidence.png',dpi=250);fig.savefig(directory/'collection_evidence.pdf');plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);plot(p.parse_args().directory)
