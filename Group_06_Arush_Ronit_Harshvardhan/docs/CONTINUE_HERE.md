# Start here — Ronit, Group 06

## Goal and ownership

Finish the autonomous inclined-solar-panel cleaning crawler capstone for Arush (E048), Ronit (E052), Harshvardhan (E058). User authorised autonomous implementation, tests, data analysis and frequent checkpoint pushes to this personal sharing repo. Work only inside this group folder for project changes. Use feat/e052-waterless-rotary-bru. Preserve existing files. Never fabricate teammate authorship, signatures, consent, peer reviews, sources or measurements.

## Current truth

- MuJoCo model compiles: 8.5 kg robot, four torque-driven rollers approximate tracks, rigid brush/panel.
- Bidirectional raster avoids unsafe pivot turns. Full route tested on 3 development seeds: about 244 s, 4.4 cm geometric tracking RMSE, about 55% whole-panel contact coverage. Full cleaning is NOT achieved.
- Normal brush contact force is logged. Cleaning proxy requires force >0.1 N and speed >1 rad/s. Proxy is uncalibrated; no glass-deflection/coating-safety claim.
- Lowered and compliant brush experiments were rejected. Current geometry is the validated rigid-brush design.
- 60 independent 30-second tracking runs completed. See analytics/tracking_benchmark/statistics.json. This narrow initial-position study is NOT 30 full missions or robust-environment validation.
- Eleven automated tests and physical model validation pass. EGL image rendering works; interactive viewer needs rehearsal.
- Economics and sensitivity are computed but default inputs remain explicitly unverified assumptions.
- Nothing has been submitted to faculty, Teams or LinkedIn.

## Resume without asking for already-known context

1. Read this document, PROJECT_PLAN.md, RUN_AND_DEMO.md, IMPLEMENTATION_STATUS.md, current model/controller/tests and experiment protocol.
2. Install with Python 3.12 and group-local requirements.txt in a virtual environment. Run tests and validate_physics.py. Do not assume old cloud paths exist.
3. Improve actual brush-contact coverage with measured load/speed and defined reachable-area limits; do not hide full-panel denominator.
4. Extend the implemented latched active-braking supervisor and fault injections. Pose-dropout and brush-jam seed-0 tests settle; severe traction loss still fails. See SAFETY_VALIDATION.md. Validate wider conditions, angular settling and bounded recovery before safety claims.
5. Complete provenance/logging robustness, validated baseline/proposed full-mission scenarios and statistical analysis. Preserve existing 60-run study as narrow evidence, not a substitute for full validation.
6. Verify primary sources; calibrate or clearly vary business assumptions; finish FMEA with demonstrated mitigation, queue and sensitivity.
7. Rewrite outdated starter claims and synthetic plots. Prepare dossier evidence, video script and live demo. Human signatures, actual video participation/posting, peer review and individual Teams turn-in remain human actions.
8. Commit and push meaningful checkpoints to the sharing repo so another chat can resume. Do not push to faculty main. Final faculty work should be reviewed through a feature branch/PR.

## Submission

Due 26 Oct 2026 23:59 IST: completed Word and signed 4-page PDF dossier, code/model/business scripts/real telemetry in Group 06; each member turns in identical PDF individually on Teams. 3–4 minute LinkedIn video, every member appears/speaks, URL in dossier. Live showcase 31 Oct, no PPT. Group 06 reviews Groups 07 and 12. Do not invent missing personal IDs: user said checked but did not supply corrected values.

## Data and portability

Development CSVs may be gzip-compressed in this sharing checkout. pandas reads .csv.gz directly. All statistical source logs are preserved in analytics/tracking_benchmark. Virtual environments and credentials are excluded. Old HANDOFF.md sections describe superseded experiments; this document takes precedence for current status.

## Latest pushed development checkpoint

Active-braking supervisor is in src/safety.py. Fault CLI supports pose_dropout, brush_jam and traction_loss. Stop reasons/events and terminal planar speed are logged. Existing output paths are protected. Nominal full-route regression with supervisor completed all 16 waypoints at 244.002 s, no false stops; data in analytics/supervised_nominal_real_trials.csv.gz. It ends at the route endpoint while still moving ~0.095 m/s; that historical run predates the settled docking implementation below. Fault evidence and 10 tests are included. Group README now supersedes stale starter claims; AI_AUDIT.md records actual AI error cases for student verification. Remaining work is still listed above; never mark full-panel cleaning or final submission complete.

## Settled docking checkpoint

The current controller enters DOCKING at the endpoint and physically brakes until planar speed <0.02 m/s, chassis angular speed <0.05 rad/s and brush speed <1 rad/s all hold for 0.5 s. Final endpoint error must be <=0.12 m. Full seed-0 run reached DOCKED at 244.526 s, error 0.10096 m, speed 0.00463 m/s. Independent CSV verification is analytics/verify_docking_run.py; measured data and 300 DPI figure are included. Eleven tests pass. Remaining priorities: contact/coverage, wider full-mission and fault validation, source verification/business calibration, viewer/video and dossier. Docking is endpoint settling, not a charging connector or passive mechanical latch.

## Recovered workspace checkpoint — 25 October 2026

The pushed files were recovered into `/workspace/Robotics`. Python 3.12 pinned requirements, pip check, physics checks and **18 tests** pass on the new instance; EGL 640×480 rendering was independently checked again. Interactive desktop viewer is still unverified. Cloud install/start instructions were saved as a draft, not published.

Read `CONTACT_COVERAGE.md` next. New cell-centre coverage maps preserve the 24 m² denominator, separately report a declared 15.81 m² interior and distinguish projected footprint, qualifying contact and soil proxy. New NPZ snapshots and brush-pose CSV fields support diagnosis. The original legacy coverage fields remain intact. Standard seed 0 reproduced identical motion/docking. Its v2 contact union is 55.885%, while 44.094% of the panel is never under the projected brush footprint.

Three expanded-layout pilots reached ~64% contact but stopped before docking on EDGE_MARGIN; preserve these failures. The optional `--layout expanded_safe_return` restored the original lower row while widening the upper/side sweep. Seeds 0/1/2 all DOCKED, 255.4–257.2 s, 61.3–61.7% whole-panel contact union, >0.145 m minimum logged clearance. Independent CSV checks are in `analytics/expanded_safe_return_checks.json`. The standard route remains default. Contact union is not calibrated cleaning; the soil-proxy threshold metric did not improve, so report that tradeoff honestly.

The nine-case fault matrix retained 3/3 settled dropout stops, 3/3 settled jam stops and 3/3 severe traction-loss edge failures. No broad robustness or hardware safety claim is supported. Code/model were unchanged within each batch; earlier coverage-audit and expanded-pilot datasets intentionally have different controller/planner hashes, recorded at launch.

The old `generate_paper_figures.py` no longer synthesises observations; it requires genuine mission telemetry and refuses overwriting outputs. Historical starter datasets/images remain excluded from evidence. The manuscript blueprint now reports actual narrow tracking results and limitations instead of invented full-mission/manual-baseline significance.

Next: investigate measured force spikes/intermittent dose and unreachable border geometry, freeze an explicit full-mission protocol for baseline/proposed with suitable conditions and sufficient held-out runs, improve logging/provenance failure handling, verify sources/business assumptions, rehearse viewer/video and complete the dossier with team review. Never substitute these three development seeds or the old 30-second study for final full-mission evaluation. Human signatures, video appearances/posting, peer reviews and Teams turn-in remain outstanding.

## Simulation recording and status checklist

The latest `SUBMISSION_READINESS.md` distinguishes working features from unfinished engineering and human submission actions. `src/record_demo.py` records actual EGL-rendered physics at 8× playback, using a tested observation callback that preserves deterministic mission results. It requires system ffmpeg and a fresh output directory. The 19-test suite passes; desktop interactive viewing remains unverified. A first recording attempt exceeded the default 640 px framebuffer; the recorder now explicitly sets display framebuffer dimensions at runtime, without XML or physics changes.

Recording finished: `docs/validation/demo_v2/mujoco_demo.mp4` shows the full fresh seed-0 route at labelled 8× playback (32.08 s video, 256.628 s simulation, DOCKED). Full decode verified; motion and coverage match the prior nonrecorded run exactly. Telemetry and metadata are retained beside it. The display is a physics overview with state/coverage overlays, not a calibrated visual cleaning model or the required team presentation.

## New user requirement — plan before implementation

Read `VISION_FULL_CLEANING_PLAN.md` before further engineering. The user now requires full-panel edge/corner cleaning, visible falling dirt, real RGB detection from robot/edge cameras, thresholded departure from home, targeted revisits plus complete coverage, visual verification and return home. Aesthetics are deferred. The latest checkpoint adds the plan only; vision, debris rendering, edge-tool redesign and event-driven control are NOT implemented. The old ~61% route is insufficient. Do not begin implementation as part of the planning request.

## Latest scope revision — fixed brush, ~90% target, disclosed containment

The user cancelled telescoping/deploying edge brushes and accepts roughly 90% whole-panel coverage for simplicity. Permanently extended/fixed brush geometry is acceptable. The revised `VISION_FULL_CLEANING_PLAN.md` supersedes the prior 100%-coverage and articulated-tool plan. It prioritises footprint/support-aware routing, a documented physical collision guard (allowed to be invisible in presentation), traction tests and a fixed brush. Do not use hidden pose clamps or present guard-assisted containment as demonstrated wheel grip. Larger crumbs require actual physical pushing/removal. Camera-triggered home/clean/verify/return behaviour remains required; unreachable dirt is reported rather than silently ignored. This is a plan-only revision; current demonstrated coverage remains ~61–62%.

## Current demonstration scope — visible body-to-edge pass, central dirt scenario

The demonstration requires visible chassis-to-edge passes, with approximately 90% actual cleaning coverage as the engineering target. Read the latest presentation section in VISION_FULL_CLEANING_PLAN.md. Use deliberate chassis-to-edge/perimeter routing, a fixed brush, the authorised concealed collision guard and centrally deposited dirt for the main demo. Camera-triggered start, actual central debris removal and home return remain required. Arbitrary edge-dirt removal is not required in this selected demonstration. Keep actual physical coverage separate from chassis proximity; existing ~61–62% coverage has not yet improved. This update changes the plan only.

## Implementation started — guarded reach, RGB sensing and debris prototypes

Read `GUARDED_IMPLEMENTATION.md`. Initial guarded fixed-brush pilot (`analytics/guarded_pilot0.*`) DOCKED at 344.264 s with 90.292% contact-gated projected coverage. It relies on physical transparent collision guards and has not demonstrated camera-guided cleaning. Later guarded model/controller revisions add compiled-active falling fine particles, image-only dirt detection, a home monitoring gate, closed-home route and bounded camera-target revisit logic. Current source is under integrated development; do not describe an in-progress run as completed.

29 tests pass, including physical crumb ejection. Actual rendered RGB checks detect all three controlled dirt patches with ~1 cm localisation error and zero clean-scene detections. Valid 12 s clean/subthreshold tests remain home; the single subthreshold deposited patch persists. Corrections for early failed pilots are stored explicitly. Separate physical crumb pilot genuinely pushes a rigid crumb off glass into a catch tray; arbitrary central-crumb collection remains unintegrated. All perception assumptions and current ground-truth navigation are disclosed in implementation notes. Preserve source snapshots and failed datasets.

## Latest implementation checkpoint — working recorded vision-triggered cycle

`docs/validation/vision_demo_v1/vision_cleaning_demo.mp4` is a fresh actual-physics recording. `result.json` reports CLEAN_AND_HOME: six physical grain depositions, RGB-only persistent detection triggers at 4 s, a guarded sweep, one camera-targeted revisit, all six dirt patches below the declared residual threshold, home return and settling at 487.602 s. New-grid whole-panel qualifying contact footprint is 92.083%. Actual chassis reaches all four boundaries within normal soft-contact penetration (<0.2 mm). Guards are physical and relied upon; they do not establish real-world traction. No telescoping tool exists: the brush is permanently 0.8 m wide.

Independent CSV/event checks passed via `src/verify_vision_run.py`; all 1749 H.264 frames decode. The clip is 69.96 s (first 8 simulation seconds at 1×, rest at 8×, final 2 s held summary). 29 automated tests pass; clean/subthreshold 12 s cases stay home. Physical rigid-crumb ejection is independently demonstrated in a separate pilot. Full instructions and limitations are in RUN_AND_DEMO.md and GUARDED_IMPLEMENTATION.md.

The prior `analytics/vision_dirty_pilot3` physically completed the same trajectory but failed saving the final orchestration report on a NumPy scalar. The corrected recorded run saved successfully and independently confirms the final dirt score. Earlier invalid/failed runs and source snapshots remain labelled; never count them as passing evidence.

Next: extend sensing beyond controlled dirt colours, integrate general central-crumb collection, implement estimated localisation/uncertainty, finish interactive viewer and fault handling for the new pipeline, validate wider conditions/held-out runs, then scenery and submission work. Ground-truth navigation and the soil-removal proxy remain explicit assumptions. The new successful development clip does not complete final statistical validation, hardware safety or any human submission actions.

## Visual polish and explicit edge/solid diagnostics

Read POLISH_AND_EDGE_TESTS.md. Corrected bright-edge RGB detection now sees patches previously missed; the explicit edge run clears four of six and reports the two unreachable left-strip patches as INCOMPLETE. Hidden scoring also overrides false camera-clean success with VERIFICATION_MISS. Do not claim every edge is cleaned just because the body touches it.

A new 31-second 720p physical solid-object clip is in docs/validation/solid_object_demo_v1/solid_object_demo.mp4: a persistent 70×70×50 mm, 120 g block is moved by real brush contact and gravity into a lower catch tray. It is a scripted interaction test, not integrated camera-selected object collection. The measured ~283.8 N peak normal load is explicitly unvalidated for glass safety.

Presentation-only rooftop scenery and cinematic cameras are implemented without changing sensor RGB or physical state. 32 tests pass with MUJOCO_GL=egl set before import in the headless environment. The full cinematic_demo_v2 run is still being recorded at this checkpoint; do not claim its result before independent checks. The interrupted cinematic_demo_v1 draft is retained and labelled incomplete. No external assets or credentials were required.
