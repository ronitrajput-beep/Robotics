# Group 06 reproduction

Run from `Group_06_Arush_Ronit_Harshvardhan` using Python 3.12 and `requirements.txt` in a virtual environment. Set `MUJOCO_GL=egl` before importing MuJoCo in a headless machine; an interactive desktop can use the existing viewer commands in `docs/RUN_AND_DEMO.md`.

## Verification and frozen experiments

```bash
MUJOCO_GL=egl python -m unittest discover -s tests
MUJOCO_GL=egl LP_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python src/run_final_validation.py --output-dir analytics/final_validation_new --runs 30 --workers 4 --angles 10 20 30
python analytics/analyse_final_validation.py analytics/final_validation_new
python analytics/final_business_model.py --validation-dir analytics/final_validation_new --output-dir analytics/final_business_new
```

Use a new output directory; never overwrite raw runs. Every attempt runs the actual combined camera/physics mission to dock, abort or the 1000 s horizon. Source snapshots, independent seeds, distributions, control comparison, numerical serialization and statistical endpoints are fixed in `protocol.json`. Development pilots and runtime profiling runs are excluded. The primary tracking comparison uses the same first 30 seconds in each full attempt; full mission completion is separately reported. Failed/partial attempts are retained. The historical `tracking_benchmark` is a distinct earlier-model initial-sweep study, not final collection-system evidence.

Raw telemetry is real measured simulation CSV, compressed as `.csv.xz` with nine significant digits. The compression itself is lossless; decimal serialization is disclosed separately. pandas reads it directly. Log columns include every 0.002 s sample, actual torques for all five actuators and panel-frame chassis velocity. `statistics.json` is derived from these logs and run summaries; `trace_audit.json` checks sample counts, intervals, finiteness and independently recomputed primary metrics. No `SIMULATED_*` starter targets are used.

## Nominal demonstration

The completed demonstration and independent checks are under `docs/validation/collection_demo_v6`. Its executed code/model snapshots are preserved alongside it. `analytics/collection_pilot8` is the separately validated matching headless run. The camera hardware preview is `docs/validation/panel_camera_rig_v4` and intentionally stops at 20 s; it is not a failed full mission. Reproduction details are in `docs/COLLECTION_AND_EXTERNAL_DOCK.md` and `docs/PANEL_CAMERA_RIGS.md`.

The reduced-order vacuum/soil accounting is not calibrated airflow. The block is actual rigid-body contact dynamics in a prescribed corridor. Guards supply physical containment. Ground-truth navigation is separate from RGB contamination detection. Mechanical work is not electrical power and dust clearance is not PV energy recovery.

## Business model

All commercial inputs are labelled assumptions in `analytics/final_business_inputs.json`. One section is the modelled 24 m² bay; transfer to another bay is assumed manual labour, not an autonomous capability. The final analysis uses all 30 nominal proposed attempts, including failures. A file explicitly named `business_nominal_draft_v1` uses one development run while the final experiment runs; it must not be called a measured commercial or final statistical result.

The script reports labour, normalized annual costs, NCRI, simple payback, lifetime-normalized payback, queue stability/delay, eight ±30% sensitivities and a success-lower-confidence scenario. Poisson arrivals, exponential service, efficiency, electronics/auxiliary wattage and retries are assumptions. No electrical PV uplift is monetized. Unsupported inherited Mumbai/soiling/recovery/payback constants are not inputs.

## Original Word form and PDF

The original is preserved at `submission/templates/MDRIIA_Group_06_Technical_Dossier_original.docx`. Use a separate document environment with `submission/requirements-document.txt` and LibreOffice or desktop Microsoft Word. The template is the faculty's six-section form; the optional four-page IEEE paper is a different deliverable, not a four-page limit on this form.

```bash
python submission/build_dossier.py --preliminary  # only while final study is pending
python submission/build_dossier.py              # requires final_validation_v1 + final_business_v1
soffice --headless --convert-to pdf --outdir docs docs/MDRIIA_Group_06_Technical_Dossier.docx
python submission/check_deliverables.py
python submission/package_submission.py
```

The builder preserves all 212 content-control tags and original dropdown choices. `dossier_field_audit.json` lists the genuinely personal fields left for members. Signatures/consent, hours, authorship, learning and actual peer reviews are never fabricated. The build audit checks PDF text/layout and document hash correspondence. Original exact-height image placeholders are expanded to prevent clipping the worked example.

AI assistance: Codex/ChatGPT generated and edited code, tests, analysis and the technical report during development. Repository commit metadata is not proof of which student authored a script. Each member must personally review and explain their actual contribution before completing the authorship/individual/sign-off fields.

## Raw data and file sharing

The compact submission ZIP includes the technical dossier, code/models, assumptions, derived evidence, selected screenshots and demonstration videos. It excludes bulk raw trial streams to keep the download practical. Full raw files remain in the personal Robotics repository under `analytics/final_validation_v1/tilt_*`; completed trials are pushed in checkpoints. The ZIP's manifest includes hashes, sizes and the exact status at packaging. Never treat a running-status archive as a completed final study. The faculty repository and individual Teams turn-in require the team's final human review and signatures.
