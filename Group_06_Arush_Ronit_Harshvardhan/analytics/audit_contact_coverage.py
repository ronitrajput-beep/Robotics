"""Read-only analysis of measured CSV and saved coverage-grid evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def audit(path):
    path = Path(path)
    manifest = path.with_suffix('.json')
    grid_path = path.with_suffix('.coverage.npz')
    result = json.loads(manifest.read_text())
    d = pd.read_csv(path, low_memory=False)
    with np.load(grid_path) as g:
        x, y = g['x_m'], g['y_m']
        geometric, qualified, soil = g['geometric'], g['qualified'], g['soil']
        interior = g['interior']
    assert len(d) > 1 and np.allclose(np.diff(d.time_s), .002, atol=1e-9)
    assert np.isfinite(d.select_dtypes('number')).all().all()
    assert np.all(~qualified | geometric)
    assert np.all((soil >= 0) & (soil <= 1))
    assert np.isclose(qualified.mean(), result['coverage_metrics_v2']['qualified_contact_fraction'])
    sweep = d.state.eq('SWEEP')
    active = sweep & (d.brush_normal_N > .1) & (d.brush_rad_s.abs() > 1)
    report = {
        'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (path, manifest, grid_path)},
        'status': result['status'], 'seed': result['seed'],
        'samples': len(d), 'dt_s': .002,
        'coverage_metrics_v2': result['coverage_metrics_v2'],
        'sweep_samples': int(sweep.sum()),
        'qualifying_duty_during_sweep': float(active.sum() / sweep.sum()) if sweep.any() else None,
        'sweep_force_N_quantiles_0_50_95_100': d.loc[sweep, 'brush_normal_N'].quantile([0, .5, .95, 1]).tolist(),
        'sweep_absolute_brush_speed_rad_s_quantiles_0_50_95_100': d.loc[sweep, 'brush_rad_s'].abs().quantile([0, .5, .95, 1]).tolist(),
        'whole_panel_never_projected_fraction': float((~geometric).mean()),
        'whole_panel_projected_but_never_qualified_fraction': float((geometric & ~qualified).mean()),
        'minimum_clearance_m': float(d.clearance_m.min()),
        'interpretation': 'Projected rectangular footprint activated by aggregate measured brush force and speed; not resolved bristle contact or calibrated soil removal. Interior is a declared reporting region, not guaranteed reachability.',
    }
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    fields = [(geometric, 'Projected footprint (all states)'),
              (qualified, 'Qualified brush footprint'), (1-soil, 'Uncalibrated soil-removal proxy')]
    for ax, (field, title) in zip(axes, fields):
        im = ax.imshow(field, origin='lower', extent=(-3, 3, -2, 2), vmin=0, vmax=1)
        ax.plot([-2.55, 2.55, 2.55, -2.55, -2.55], [-1.55, -1.55, 1.55, 1.55, -1.55], 'r--', lw=.8)
        ax.set(title=title, xlabel='Panel x (m)', ylabel='Panel y (m)')
        fig.colorbar(im, ax=ax, shrink=.6)
    return report, fig


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--figure', type=Path, required=True)
    args = parser.parse_args()
    for target in (args.report, args.figure):
        if target.exists():
            raise FileExistsError(target)
        target.parent.mkdir(parents=True, exist_ok=True)
    report, fig = audit(args.input)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    fig.savefig(args.figure, dpi=300)
    print(json.dumps(report, indent=2))
