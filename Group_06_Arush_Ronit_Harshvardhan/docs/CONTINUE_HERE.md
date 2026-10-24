# Start here — Ronit, Group 06

## Goal and ownership

Finish the autonomous inclined-solar-panel cleaning crawler capstone for Arush (E048), Ronit (E052), Harshvardhan (E058). User authorised autonomous implementation, tests, data analysis and frequent checkpoint pushes to this personal sharing repo. Work only inside this group folder for project changes. Use feat/e052-waterless-rotary-bru. Preserve existing files. Never fabricate teammate authorship, signatures, consent, peer reviews, sources or measurements.

## Current truth

- MuJoCo model compiles: 8.5 kg robot, four torque-driven rollers approximate tracks, rigid brush/panel.
- Bidirectional raster avoids unsafe pivot turns. Full route tested on 3 development seeds: about 244 s, 4.4 cm geometric tracking RMSE, about 55% whole-panel contact coverage. Full cleaning is NOT achieved.
- Normal brush contact force is logged. Cleaning proxy requires force >0.1 N and speed >1 rad/s. Proxy is uncalibrated; no glass-deflection/coating-safety claim.
- Lowered and compliant brush experiments were rejected. Current geometry is the validated rigid-brush design.
- 60 independent 30-second tracking runs completed. See analytics/tracking_benchmark/statistics.json. This narrow initial-position study is NOT 30 full missions or robust-environment validation.
- Six automated tests and physical model validation pass. EGL image rendering works; interactive viewer needs rehearsal.
- Economics and sensitivity are computed but default inputs remain explicitly unverified assumptions.
- Nothing has been submitted to faculty, Teams or LinkedIn.

## Resume without asking for already-known context

1. Read this document, PROJECT_PLAN.md, RUN_AND_DEMO.md, IMPLEMENTATION_STATUS.md, current model/controller/tests and experiment protocol.
2. Install with Python 3.12 and group-local requirements.txt in a virtual environment. Run tests and validate_physics.py. Do not assume old cloud paths exist.
3. Improve actual brush-contact coverage with measured load/speed and defined reachable-area limits; do not hide full-panel denominator.
4. Implement predictive edge braking, bounded recovery and reproducible fault injection; present physically unrecoverable conditions honestly. Current edge abort ends the experiment and is not a mechanical brake.
5. Complete provenance/logging robustness, validated baseline/proposed full-mission scenarios and statistical analysis. Preserve existing 60-run study as narrow evidence, not a substitute for full validation.
6. Verify primary sources; calibrate or clearly vary business assumptions; finish FMEA with demonstrated mitigation, queue and sensitivity.
7. Rewrite outdated starter claims and synthetic plots. Prepare dossier evidence, video script and live demo. Human signatures, actual video participation/posting, peer review and individual Teams turn-in remain human actions.
8. Commit and push meaningful checkpoints to the sharing repo so another chat can resume. Do not push to faculty main. Final faculty work should be reviewed through a feature branch/PR.

## Submission

Due 26 Oct 2026 23:59 IST: completed Word and signed 4-page PDF dossier, code/model/business scripts/real telemetry in Group 06; each member turns in identical PDF individually on Teams. 3–4 minute LinkedIn video, every member appears/speaks, URL in dossier. Live showcase 31 Oct, no PPT. Group 06 reviews Groups 07 and 12. Do not invent missing personal IDs: user said checked but did not supply corrected values.

## Data and portability

Development CSVs may be gzip-compressed in this sharing checkout. pandas reads .csv.gz directly. All statistical source logs are preserved in analytics/tracking_benchmark. Virtual environments and credentials are excluded. Old HANDOFF.md sections describe superseded experiments; this document takes precedence for current status.
