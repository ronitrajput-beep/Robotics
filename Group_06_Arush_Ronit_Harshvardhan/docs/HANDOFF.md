# Resume here — Group 06

Branch: feat/e052-waterless-rotary-bru. Repository: /workspace/NMIMS-MPSTME-MDRIIA-2026. Only edit Group_06_Arush_Ronit_Harshvardhan. All work is local, uncommitted and unpushed. Do not discard changes. Environment: /workspace/venvs/group06/bin/python; set MPLCONFIGDIR=/workspace/.cache/group06-matplotlib. Full original plan: /workspace/GROUP_06_PROJECT_PLAN.md. Read the latest user instructions and current code before continuing.

## User's goal

Own implementation through simulation, tests, genuine telemetry, analysis/economics, submission preparation. Stop only for a needed AI model change or concrete external blocker. The assistant cannot see account usage percentage. This handoff supports resuming on another account on the same PC, provided that account can access this SAME cloud workspace; that access is not guaranteed. Download/archive uncommitted files before changing accounts if workspace access differs. Never put credentials in the archive.

## Done

- Group 06 Word dossier and showcase guide extracted to /workspace/Group_06_Submission_Pack.
- Dependencies installed; pip check and independent engine check pass.
- Phase 1 XML repaired: world-child free chassis, four torque-driven rollers approximating tracks; total robot mass 8.5 kg; explicit torque and command limits.
- src/validate_physics.py passes stationary/forward/reverse/turning and brush checks; docs/PHASE_1_PHYSICS.md describes limitations.
- Replaced synthetic numerical mission controller with real MuJoCo stepping, panel-frame waypoint pursuit, bounded wheel-speed PI, actual contact-gated brush footprint map, explicitly uncalibrated soil proxy, bounded mission, viewer option, and 500 Hz CSV.
- Seed 0 nominal route reaches all 12 waypoints in 214.15 simulated seconds. Actual contact coverage 45.96%, removed-soil proxy 24.78%. Route completion is NOT full cleaning success. analytics/development_real_trials.csv and JSON contain development data, not a statistical experiment.
- tests/test_mission.py verifies repeatable seed results, timestep/log row count, timeout outcome and actual progress. One integration test passes.
- analytics/plot_development_run.py generates docs/validation/development_run.png from real CSV; no target data.

## Next: use strongest available reasoning model for physics/control review

The next gate needs careful path/contact/safety review before claiming cleaning completion or launching expensive final experiments. Current waypoint-distance RMS is NOT cross-track RMSE. Fix before rubric analysis. All sensing uses simulator ground truth; disclose this. Boundary guard checks centre only, not full body/brush envelope. At 20 degrees turns drift downhill. Brush speed is torque-limited. Contact coverage has large gaps/unreachable border. Raster begins at centre x and omits half of the first row. Finish at dock does not yet perform robust docking. No safe abort brake is modelled. No adaptive baseline/proposed comparison, fault injection, provenance-complete manifests or final statistical validation exists.

Review and implement feasible coverage trajectories including the full swept footprint and return route; improve control using measured path error; measure actual contact load and slip; validate edge bounds and fault behaviour. Do NOT force state or invent ideal traction. Distinguish domain model assumptions from measured state. Add meaningful unit and integration tests, verify headless and viewer paths separately. Then freeze independent evaluation seeds and run >=30 runs/controller/condition (aim 50), retain failures, and compute run-level statistics. Pilot runtime/storage first: development CSV alone is about 22 MB.

## Later mandatory deliverables

Implement real-data-only publication plots, sourced/assumption-labelled dimensionless business inputs, labour/payback/NCRI, queue with stability guard, sensitivity/break-even and >=4 FMEA modes. Verify sources rather than repeating template claims. Complete dossier evidence in Sections 1–6; preserve Word controls. Never invent student IDs, signatures, consent, AI-error cases or peer reviews. Team must record 3–4 minute video, appear/speak and perform individual Teams turn-in; those human acts cannot be fabricated. Deadline 26 Oct 2026 23:59 IST; showcase 31 Oct. Current IDs conflict across roster and dossier; user says checked all good but exact corrected values were not supplied.

## Commands

From group directory:
```
/workspace/venvs/group06/bin/python src/validate_physics.py
/workspace/venvs/group06/bin/python -m unittest discover -s tests
/workspace/venvs/group06/bin/python src/crawler_cleaning_controller.py --seed 0 --output analytics/development_real_trials.csv
MPLCONFIGDIR=/workspace/.cache/group06-matplotlib /workspace/venvs/group06/bin/python analytics/plot_development_run.py
```

Environment draft was saved earlier but publication is unverified; its old start notes still describe the now-repaired XML error and need updating when next touching environment configuration. Course repo membership wasn't added to that draft. Do not assume a different task/account restores this checkout.

## Latest checkpoint — stronger reasoning review needed

Read docs/IMPLEMENTATION_STATUS.md first. Current controller/planner supersede earlier 214-second route. Four tests pass. Conservative full-footprint guard exposed unsafe turns previously missed by centre-only check. Upper-left downhill raster reaches 12/16 waypoints then ABORT_EDGE at 222.618 s, coverage 47.86%, geometric path RMSE .275 m. Evidence: analytics/coverage_development_real_trials.csv and .json. Do NOT weaken footprint guard or label route safe. Next investigate measured turning trajectories and roller skid/brush contact, then derive safe turn manoeuvres or revise locomotion approximation with physical justification. Current medium-reasoning work has not resolved this coupling. Suggested next mode: strongest model with high reasoning. Fix telemetry sample alignment before final trial data. Economics implementation and geometry/economic tests have been added; defaults remain assumptions. No final batch, push, publication, or completed signed dossier exists.

## Newest checkpoint: turn blocker resolved

Read the final section of IMPLEMENTATION_STATUS.md. Forward/reverse raster with inward diagonal connectors completes all 16 waypoints for seeds 0/1/2. Approximately 244 seconds, 4.4 cm RMS geometric tracking error, 55% total-panel brush-contact coverage; no full-cleaning claim. Original rigid-brush model retained after spring experiment worsened contact. All four tests and physics validation pass. EGL rendering verified. Continue brush-contact/load diagnosis and clearly defined coverage goals, then fault tests, final experiments and submission work. Do not request another model switch just to continue routine development. Preserve old development datasets and distinguish their model/code revisions from current ones.

## Latest: portable checkpoint and completed tracking benchmark

The active sharing repository is https://github.com/ronitrajput-beep/Robotics on feat/e052-waterless-rotary-bru. The faculty repository remains the upstream source and final submission destination. In a new checkout, paths under /workspace are NOT portable: use a local virtual environment and this group's requirements.txt. Read docs/CONTINUE_HERE.md first; older chronological handoff sections are history.

The 30 baseline + 30 proposed runs finished. Each is exactly a 30-second initial-sweep tracking experiment, not a complete cleaning mission. Proposed mean path RMSE 0.02275 m; baseline 0.11685 m. Very small random initial-position perturbations produce tiny within-group variance and consequently extreme significance/effect-size values. Do not describe this as broad robustness or hardware performance. Raw 500 Hz CSV.gz, manifests, protocol, summary and statistics are in analytics/tracking_benchmark. All outcomes are TIMEOUT by design at the fixed horizon, not mission completion.
