# Current live demonstration

Use Python 3.12 and run from this Group 06folder. On Mac, use requirements-macos.txt in a local virtual environment; on Linux the tested pinned requirements.txt is available. System ffmpeg is needed only for recording, not the native live window.

```bash
source .venv/bin/activate
MUJOCO_GL=cgl mjpython src/run_live.py --speed 6
```

Linux desktop: `MUJOCO_GL=glfw python src/run_live.py --speed 6`. P pauses/resumes; mouse rotates/zooms. This is the actual controller/physics/camera pipeline, not a movie. Physics remains500 Hz; requested playback speed is limited by hardware throughput. A clean-scene idle check uses `--scenario clean --duration 12` . The combined mission starts only after actual persistent dirt detection.

The standalone XML viewer does not run the controller. `src/run_live.py` is the showcase entry point. Read JURY_PRESENTATION.md for the four-minute plan. Live model/logic is independently verified on Linux; Mac hardware is not available in this cloud environment and the team must rehearse locally.

## Reproduce statistical and business evidence

```bash
python analytics/reproduce_compact_validation.py --output-dir analytics/NEW_primary_check
python analytics/final_business_model.py --validation-dir analytics/final_validation_v1 --output-dir analytics/NEW_business_check
```

Both commands refuse to overwrite an existing analysis directory. The compact data contain actual500 Hz0–30 s samples for all 180 full attempts; complete per-run metadata and two full nominal traces are included. analytics/FULL_RAW_DATA_MANIFEST.json pins all 180original full traces in the sharing repository. `python analytics/fetch_full_validation.py --download` explicitly retrieves missing originals (approximately8 GB); this is optional for the already supplied complete primary windows.

## Verification

```bash
MUJOCO_GL=egl python -m unittest discover -s tests
python src/validate_physics.py
```

The release contains the focused current-system tests; historical starter economics/generated-target fixtures are not used as evidence. Required test-only snapshots are under analytics/collection_contact_trace. All source code and frozen evaluation snapshots are retained. Full physics/calibration, guard containment, contact proxy and market-assumption limitations are documented in the dossier and business report.
