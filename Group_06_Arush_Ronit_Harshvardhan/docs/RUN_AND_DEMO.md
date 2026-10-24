# Run the current implementation

From the Group 06 directory, with Python 3.12:

```
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/test_env.py
python src/validate_physics.py
python -m unittest discover -s tests
python src/crawler_cleaning_controller.py --seed 0 --output analytics/my_run_real_trials.csv
```

Use a new output filename to preserve previous evidence. The controller refuses an existing output or companion manifest. For a desktop viewer add `--viewer`; desktop GUI operation remains to be rehearsed. Cloud headless EGL rendering has been tested separately. The viewer currently runs at simulation throughput rather than enforcing real-time pacing; do not imply a recording is real-time unless paced or labelled.

The retained model approximates tracks using four driven rollers, has a rigid panel and rigid brush, and uses ground-truth pose feedback. It has no validated particulate/coating model. Its soil field is an uncalibrated numerical proxy. Route completion does not mean whole-panel cleaning; inspect contact coverage separately.

## Benchmark

`python src/run_tracking_benchmark.py` creates a fresh analytics/tracking_benchmark directory and refuses to overwrite it. The frozen comparison has 30 independent seeds per controller, a 30-second horizon and actual 500 Hz compressed CSV. This is an initial-sweep tracking study, not 30 complete cleaning missions. Plot with `python analytics/analyse_tracking_benchmark.py` after all runs finish.

`python analytics/generate_business_sensitivity.py` generates labelled assumption-based scenarios. Default financial and queue inputs have not been sourced or calibrated to hardware. No real cost-savings claim is supported by these inputs.

## 3–4 minute video outline

- 0:00–0:20: All members introduce the authorised question. Explain the simulated crawler and its incline.
- 0:20–1:20: Show actual forward/reverse raster, explain torque-driven rollers and state feedback. State the track approximation and ground-truth sensing.
- 1:20–1:50: Show the failed old pivot trajectory and edge abort as recorded evidence, clearly identified as a replay. A live repeatable fault/recovery demo is still required; do not claim the experiment abort is a mechanical brake.
- 1:50–2:30: Show generated tracking comparison with N, horizon, RMSE, CI and test. Explain that whole-panel contact coverage is a different outcome.
- 2:30–3:10: Show economic sensitivity and the no-payback boundary. Identify assumed inputs and missing sourcing.
- 3:10–3:45: Each member explains their actual contribution, one verified issue they understand, and the major remaining sim-to-real limitation.

Every member must actually appear and speak. Record only after final evidence is reviewed. Never invent a post URL, consent, signature or completed peer review. Use the final assignment's 3–4 minute requirement, not the older 60–90 second example.

## Current coverage candidate and read-only figures

Optional wider development candidate (the default route remains standard):

```
python src/crawler_cleaning_controller.py --layout expanded_safe_return --seed 0 --duration 420 --output analytics/new_expanded.csv.gz
python analytics/audit_contact_coverage.py analytics/new_expanded.csv.gz --report analytics/new_expanded_audit.json --figure docs/validation/new_expanded.png
python analytics/generate_paper_figures.py --input analytics/new_expanded.csv.gz --output docs/validation/new_telemetry.png
```

Both figure tools refuse existing output paths. Read CONTACT_COVERAGE.md before interpreting coverage. Do not present the `expanded` variant's stopped lower-return pilots as mission completions. To reproduce the small development fault matrix use `python src/run_fault_checks.py` in a fresh checkout/output directory; it refuses the retained `analytics/fault_matrix_v1` directory to protect existing evidence.
