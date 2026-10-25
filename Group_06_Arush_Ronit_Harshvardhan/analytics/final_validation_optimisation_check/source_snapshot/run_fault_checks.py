"""Development fault matrix; retains unsafe outcomes, never a certification study."""
from pathlib import Path
import contextlib
import json
from crawler_cleaning_controller import mission

ROOT = Path(__file__).resolve().parents[1]


def run():
    directory = ROOT / 'analytics/fault_matrix_v1'
    directory.mkdir(exist_ok=False)
    protocol = {'seeds': [0, 1, 2], 'faults': ['pose_dropout', 'brush_jam', 'traction_loss'],
                'fault_time_s': 3., 'duration_s': 10., 'variant': 'proposed',
                'scope': 'Development matrix at fixed 20 degree nominal model; no failure-rate inference. Severe traction loss is expected to remain unsafe.'}
    (directory / 'protocol.json').write_text(json.dumps(protocol, indent=2))
    results = []
    for fault in protocol['faults']:
        for seed in protocol['seeds']:
            stem = f'{fault}_{seed}'
            with (directory / (stem + '.log')).open('w') as log, contextlib.redirect_stdout(log):
                result = mission(seed=seed, output=directory / (stem + '.csv.gz'),
                                 duration=10, fault=fault, fault_time=3)
            results.append(result)
            (directory / 'results.json').write_text(json.dumps(results, indent=2))
            print(f"{stem}: {result['status']} ({result['stop_reason']})", flush=True)


if __name__ == '__main__':
    run()
