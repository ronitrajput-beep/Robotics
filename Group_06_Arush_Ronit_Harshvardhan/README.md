# Group 06 — inclined solar-panel cleaning crawler

Development project for Arush, Ronit and Harshvardhan, based on the faculty MDRIIA scaffold. **Read [CONTINUE_HERE](docs/CONTINUE_HERE.md) for current state and remaining work.**

The MuJoCo model uses four torque-driven rollers as a track approximation, an 8.5 kg chassis assembly, a rotary brush and a 20-degree rigid panel. The controller follows alternating forward/reverse sweeps with diagonal row shifts using simulated ground-truth feedback.

## Latest collection prototype

The combined external-dock development run is independently verified: camera-triggered departure, 32 scattered dust spots including upper-left glass, physical guide-to-tray handling of a persistent 120 g block, settled off-glass return, modelled bin emptying and charging. Headless evidence is in `analytics/collection_pilot8`; the fresh presentation recording in `docs/validation/collection_demo_v6` is still rendering and is not yet a completed video.

The fixed brush now uses robust rounded contact geometry and has visible support arms; a fixed diagonal guide handles larger solids separately from the vacuum-intake/bin representation. Fine-dust capture/service are reduced-order models. Actual whole-panel qualifying contact footprint is 89.97917%, with all selected dirt patches below threshold; exact-90 remains false. This is a nominal development result, not hardware validation. See [collection design and evidence](docs/COLLECTION_AND_EXTERNAL_DOCK.md).

## Historical tracking evidence

- Physical-model compilation and stationary/forward/reverse/turning checks pass.
- Three developmental seeds completed the route in approximately 244 seconds, with approximately 4.4 cm geometric path-tracking RMSE and 55% whole-panel contact coverage. This is NOT complete cleaning.
- A separate 30-second initial-sweep study ran 30 baseline and 30 proposed trials, recording 500 Hz data. Mean tracking RMSE: 11.68 cm baseline, 2.27 cm proposed. Narrow initial-position randomisation gives very small within-group variance; results do not establish broad robustness or real-world performance.
- Pose-dropout and brush-jam injections demonstrate active braking. Severe traction loss remains unsafe. See [safety validation](docs/SAFETY_VALIDATION.md).
- Settled endpoint docking is verified in a complete seed-0 mission, including a 0.5-second low-speed hold and independently checked 500 Hz logs. See docs/DOCKING.md.
- Headless EGL rendering works. Interactive viewer rehearsal is still pending.

## Run

See [RUN_AND_DEMO](docs/RUN_AND_DEMO.md). Use Python 3.12, install this folder's requirements.txt into a virtual environment, then:

```
python src/test_env.py
python src/validate_physics.py
python -m unittest discover -s tests
python src/crawler_cleaning_controller.py --seed 0 --output analytics/new_run.csv
```

Add `--viewer` on a desktop with a display. Output files must be new. Runtime has no AI-service dependency.

## Data and limitations

Actual experiment logs, manifests and statistics: analytics/tracking_benchmark/. Development runs are separately named. Files prefixed SIMULATED and the original generate_paper_figures.py remain faculty target examples and must not be used as measurements. Current measured figure generation is analytics/analyse_tracking_benchmark.py.

The brush-dose/soil field is uncalibrated, panel deformation is not modelled, and no coating-safety claim is supported. Economics defaults are explicitly assumption-based sensitivity scenarios, not sourced deployment costs. Older research guide/manuscript documents retain scaffold claims pending verification; this README describes the current implementation.

The final Word/PDF dossier, team submission video, peer review and faculty submission remain separate unfinished actions. See [submission readiness](docs/SUBMISSION_READINESS.md). All team sign-offs and personal turn-ins must be performed by the actual students.
