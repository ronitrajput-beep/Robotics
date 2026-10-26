# Run the current implementation

**MacBook:** follow [MACBOOK_SETUP.md](MACBOOK_SETUP.md) for the current combined simulation. Use the compact ZIP, native CGL graphics and `requirements-macos.txt`; the cloud `/workspace` paths and EGL setting are Linux-specific.

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

## Watch or record a headless simulation

`src/record_demo.py --output-dir <NEW_DIRECTORY>` records an actual fresh MuJoCo run via EGL and streams RGB frames to the system `ffmpeg` executable. Use the same Python environment as above. A full mission is shown at **8× playback**, with simulation time, controller state and whole-panel qualifying projected coverage overlaid. The renderer's framebuffer dimensions are set at runtime; physics parameters are unchanged. The output directory must be new and receives MP4, preview, video metadata, full telemetry and the mission manifest. Rendering records observation callbacks before integration; it does not replay or overwrite robot state. This is separate from desktop `--viewer` operation and the required team video.

Recorded example: `docs/validation/demo_v2/mujoco_demo.mp4` (32.08 s, 960×720 H.264, 25 FPS, 8× playback). It represents 256.628 s of simulation ending DOCKED, matching the earlier expanded-safe-return seed-0 physical metrics exactly. All 802 frames were decoded successfully with ffmpeg. Its telemetry, coverage map and manifests are alongside the video. This visualises movement and measured coverage statistics; the panel surface does not display a simulated dirt texture.

## New event-driven vision prototype

From the Group 06 folder in the pinned Python environment (EGL required for headless camera rendering; ffmpeg required for recording):

```
python src/vision_mission.py --scenario dirty --record-video --output-dir analytics/MY_NEW_VISION_RUN
python src/verify_vision_run.py analytics/MY_NEW_VISION_RUN
```

The output directory must not exist. The default dirty scene takes about 488 simulated seconds on the current code. It uses actual RGB images to trigger from home, a fixed 0.8 m brush, physical transparent guards, contact-qualified visible dirt attenuation, a camera-directed revisit if needed and return to the initial home region. Fixed cameras are elevated above the panel edges; camera dirt detection does not imply camera-based navigation. The saved clip is `docs/validation/vision_demo_v1/vision_cleaning_demo.mp4`.

Negative scenarios (use fresh directories):

```
python src/vision_mission.py --scenario clean --duration 12 --output-dir analytics/MY_CLEAN_TEST
python src/vision_mission.py --scenario subthreshold --duration 12 --output-dir analytics/MY_SMALL_DIRT_TEST
```

Both should remain in HOME_MONITOR; the subthreshold scene deposits one visible patch and leaves it uncleared. Do not interpret that deliberately idle scene as a cleaning failure. Run `python src/validate_camera_pipeline.py --output-dir analytics/MY_RGB_CHECK` for rendered clean/dirty camera checks. Run `python src/validate_crumb.py --output-dir analytics/MY_CRUMB_TEST` for the separate genuine rigid-crumb ejection/catch-tray test. None of these scripts overwrites existing output directories.

The old controller `--viewer` shows its physics model without the new sensor-rendered dirt overlays. The new event-driven prototype currently supports headless RGB rendering/MP4; a fully interactive integrated viewer remains unfinished.

## Rooftop cinematic and larger solid-object recording

Use fresh output directories. On a headless Linux machine set EGL before Python imports MuJoCo:

```
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python src/vision_mission.py --scenario dirty --cinematic --duration 650 --output-dir analytics/NEW_ROOFTOP_RUN
python src/verify_vision_run.py analytics/NEW_ROOFTOP_RUN
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python src/record_solid_object.py --output-dir analytics/NEW_SOLID_RUN
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python -m unittest discover -s tests
```

Latest videos: `docs/validation/cinematic_demo_v2/cinematic_cleaning.mp4` (2:24.68) and `docs/validation/solid_object_demo_v1/solid_object_demo.mp4` (0:31). Normal-speed inspections and accelerated traversals are labelled. The rooftop/city/material details are presentation-only; the tested sensor appearance is preserved. See POLISH_AND_EDGE_TESTS.md before interpreting perimeter cleaning or the solid-object force peaks.

## Current no-lift scenario with camera feeds

The latest replacement is `docs/validation/no_lift_scattered_demo/cinematic_cleaning.mp4` (3:13.12). It shows 32 varied spots, a camera-requested bottom-edge task, shallow return routing and actual left/right/onboard RGB feeds at 2 Hz with detection boxes. For a fresh run:

```
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python src/vision_mission.py --scenario scattered --cinematic --duration 1100 --output-dir analytics/NEW_NO_LIFT_RUN
python src/verify_scattered_run.py analytics/NEW_NO_LIFT_RUN
```

Use `verify_scattered_run.py` for this new route, rather than the historical verifier requiring all four body-edge contacts. It verifies global height/tilt bounds, all 32 dirt targets, camera causality for edge service, guard-contact policy and settled home return. Contact coverage is independently reported (89.03125% in this run); its exact-90 flag remains false. See LIFT_FIX_AND_CAMERA_FEEDS.md for design tradeoffs and rejected development variants. Raw full-size camera examples are in docs/validation/raw_camera_before_after.png.

## Latest combined external-dock simulation

Watch docs/validation/collection_demo_v6/cinematic_cleaning.mp4 (3:20.40, 720p/25 fps) and solid_contact_slow_motion.mp4 (15.96 s at labelled .25×). This fresh run passes independent combined-cycle checks and exactly reproduces pilot8 telemetry. It includes off-glass home, visible fixed brush supports, intake/bin, fixed solids guide, permanent tray, actual camera feeds, fine-dust cleaning, physical block collection and modelled dock service.

```sh
MUJOCO_GL=egl python src/vision_mission.py --scenario combined --cinematic --duration 1000 --output-dir analytics/NEW_COMBINED_RUN
python src/verify_collection_run.py analytics/NEW_COMBINED_RUN
```

Read COLLECTION_AND_EXTERNAL_DOCK.md for mass accounting, the declared lower-strip block corridor and model limitations. The current code preserves the 8.5 kg assumed mass budget; suction airflow, charging/emptying hardware and structural strength are not physically validated. Previous failed/partial collection recordings v1–v5 are retained and explicitly rejected. Forty-nine tests pass.
