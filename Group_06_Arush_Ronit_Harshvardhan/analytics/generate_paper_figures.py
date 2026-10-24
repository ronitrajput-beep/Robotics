"""Plot saved physics telemetry. Never generate observations or overwrite evidence."""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def generate_publication_assets(input_path, output_path):
    input_path, output_path = Path(input_path), Path(output_path)
    if output_path.exists():
        raise FileExistsError(output_path)
    d = pd.read_csv(input_path, low_memory=False)
    required = ['time_s', 'x_m', 'y_m', 'ref_x_m', 'ref_y_m', 'path_error_m',
                'brush_normal_N', 'brush_rad_s']
    if any(c not in d for c in required) or len(d) < 2:
        raise ValueError('Expected physics mission telemetry, not starter benchmark data')
    if not np.isfinite(d[required]).all().all() or not (np.diff(d.time_s) > 0).all():
        raise ValueError('Telemetry must be finite with increasing timestamps')
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    axes[0, 0].plot(d.ref_x_m, d.ref_y_m, '--', lw=.5, label='Controller reference')
    axes[0, 0].plot(d.x_m, d.y_m, lw=.7, label='Measured chassis')
    axes[0, 0].set(xlabel='Panel x (m)', ylabel='Panel y (m)'); axes[0, 0].axis('equal'); axes[0, 0].legend()
    for ax, column, label in [(axes[0, 1], 'path_error_m', 'Geometric segment error (m)'),
                               (axes[1, 0], 'brush_normal_N', 'Brush normal force (N)'),
                               (axes[1, 1], 'brush_rad_s', 'Brush angular speed (rad/s)')]:
        ax.plot(d.time_s, d[column], lw=.5)
        ax.set(xlabel='Simulation time (s)', ylabel=label)
    fig.suptitle('Recorded simulation telemetry; ground-truth feedback; rigid brush/panel')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    generate_publication_assets(args.input, args.output)
