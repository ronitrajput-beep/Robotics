# Group 06: Solar-panel cleaning crawler — implementation and evidence plan

Prepared 24 October 2026. Planning only: no dependencies installed, simulation executed, branch created, or course repository files modified for this review.

## 1. The project to build

Build a physically driven MuJoCo crawler that cleans an inclined photovoltaic array, measures its own progress, detects unsafe operation, and either recovers or aborts with an explicit reason. Present a live comparison between a simple controller and an improved controller, with reproducible measurements and an economics model driven by those measurements.

The strongest demonstration: the crawler starts a raster sweep, encounters a seeded low-friction patch, visibly detects slip, reduces brush load/speed and attempts a bounded recovery. If traction is physically insufficient, it enters a clearly labelled unsafe/sliding state rather than pretending that zero motor command holds it still. Show a comparison against the baseline under the same disturbance. Show the result even when the proposed controller fails.

No system is fault-proof. Our target is bounded, observable failure with reproducible diagnosis, plus a thoroughly tested nominal operating envelope.

## 2. Repository audit and authority

Primary implementation directory: `/workspace/NMIMS-MPSTME-MDRIIA-2026/Group_06_Arush_Ronit_Harshvardhan`. Future changes belong exclusively inside this directory. Shared root documentation is reference material; do not modify it or other groups.

Reviewed the repository structure, shared course instructions and governance, Group 06 source/model/analytics/documentation, the Word dossier's extracted text, and the showcase PDF. Other groups' model/controller structures were surveyed as context; their project logic is not a dependency of Group 06. Citations and standards have not been independently verified against primary publications in this planning pass. No runtime findings are claimed.

Use the newer capstone rubric, Group 06 dossier, and showcase PDF to interpret obsolete examples. Preserve the authorised research question. Record unresolved contradictions rather than silently inventing an answer.

| Conflict | Decision for planning |
|---|---|
| Older 60–90 second video versus current 3–4 minute video | Plan a 3:00–4:00 video; optional short teaser later. |
| Older paper-centric milestones versus current 20-mark capstone | Dossier + runnable software + evidence first; conference paper is optional. |
| 30 versus 50 trials | At least 30 per controller per condition; aim for 50 to satisfy the stricter older manual if runtime permits. |
| Manual says ISO 3691-4 applies; project dossier hints it does not | Investigate actual scope. Use PV-specific IEC 61215/61730 as candidates, verify editions/clauses, and explain applicability. Never claim certification. |
| Dossier and roster disagree on SAP IDs | Team verifies its own IDs before submission; do not select a value automatically. |
| Dossier says four actuators; XML declares three | Report compiled model counts after repair, not template counts. |
| Starter examples imply results already exist | Replace result claims only after actual runs. |

Current rubric: robotics 10 marks; business 5; showcase/viva 5. Required outputs include completed original Word dossier and PDF, model, controller, business script, real-run CSVs, a 3–4 minute LinkedIn video, and individual Teams turn-in by every member. Dossier Word controls must be preserved; team completes/signs it in Microsoft Word. Group 06 reviews Groups 07 and 12.

## 3. What the starter actually provides

| Finding from static inspection | Consequence / planned correction |
|---|---|
| Controller does not import MuJoCo or call `mj_step` | Replace the numerical position animation with a real physics loop. |
| Slip and vibration are generated using random target values | Remove these from measured outputs; compute only from model state/sensors. Randomness belongs in seeded scenario inputs and sensor models. |
| Drift error is always passed as zero | Measure error against a planned path; implement feedback and test disturbance rejection. |
| Row shifts directly increment position | Generate physically feasible turns and row changes; no pose teleportation. |
| Track geoms are rigid boxes attached to chassis | There are no moving tread joints; choose and validate a real propulsion mechanism. |
| Purported left/right motors have orthogonal force gears | They do not describe a left/right traction pair; audit actuator transmission against installed MuJoCo documentation. |
| Free joint is nested under rack body | Treat as a likely compilation blocker: move free robot under world and initialise its panel-relative world pose correctly. Confirm through compilation. |
| Rack is rigid and fixed | Its position cannot establish glass bending or micro-crack safety. Add a labelled compliant proxy or omit that claim. |
| Four bumper sites but only two touch sensors | Implement and test all required sensing. A site alone is not a physical bumper. |
| Named robot masses sum to 9.2 kg, not 8.5 kg | Derive total mass, inertia and CoM from compiled model; set a consistent mass budget. |
| Brush cylinder full width is 0.52 m, while guide says 0.55 m | Use actual contact geometry and account for end effects in coverage. |
| Frame half-height is 0.035 m | Full box height is 0.07 m; reconcile actual protrusion above panel and intended specification. |
| `friction="1.8 0.08 0.005"` is treated as track anisotropy | Those are sliding/torsional/rolling coefficients, not longitudinal/lateral coefficients. Verify pair friction/contact-frame support before asserting anisotropy. |
| Controller stops at 60 seconds | Full-panel cleaning at its assumed speed/width requires much longer. Use task completion and justified timeout. |
| Area accumulates regardless of overlap/contact | Track the union of the actual brush footprint, and separately track cleaning efficacy. |
| Smoke test falls back when XML is missing and takes one step | Require the exact model and sustained dynamics tests. Missing model must fail. |
| Figure generator creates target CSVs and synthetic plots | Replace result-plot path with strict read-only analysis of real-run telemetry. |
| Manuscript asserts significance before experimental evidence | Treat prose as placeholder, remove unsupported claims during implementation. |
| Business inputs are fixed assumptions | Source or label and vary them; calculate outputs from inputs and real throughput. |

Other scientific corrections: the condition `mu >= tan(theta)` is a static idealised sliding bound, not unconditional safety. Differential drive cannot command sideways velocity directly. Chassis vibration is not glass deformation. MuJoCo soft-contact penetration is not structural glass deflection. An opaque rigid brush does not establish scratch prevention or particulate removal. A valid DOI does not prove the adjacent claim is supported.

At 0.25 m/s and nominal 0.55 m width, an ideal 24 m² pass needs at least about 175 seconds before overlap and turns. This is a lower-bound sanity check, not a simulated result.

## 4. Recommended physical and mathematical models

### 4.1 Robot and locomotion

Retain the group's own crawler model as the starting identity. Do not import an unrelated humanoid/manipulator from a model zoo. Use simple collision geometry with separate decorative meshes/materials.

Recommended deadline implementation: a clearly documented skid-steer crawler approximation with multiple driven rollers per side, joint torque actuation, passive support where necessary, and collision-free visual tread covers. This produces torque-mediated contact propulsion and allows testing traction and slip. It remains a roller approximation, not a mechanically faithful continuous belt; name that limitation explicitly in dossier and video. If the instructor requires continuous belts, that requirement must be resolved before using this approximation as the final model.

Higher-fidelity extension: articulated tread segments, sprockets and validated belt constraints, or a documented contact-traction implementation with explicit force limits. Prototype separately and retain only after stable long-run tests and runtime benchmarks. Avoid making a large constrained belt the critical path two days before submission. A contact-traction approximation must not be described as a resolved mechanical belt.

Robot world pose is derived from panel transform, track radius and clearance. Use a free body, explicit mass budget, credible inertias, named drive joints, actuator torque/speed limits, and a brush whose collision/contact load actually exists. Check centre of mass in the compiled model.

### 4.2 Array, contacts and sensors

Use the supplied 6 m × 4 m rack as the nominal environment, initially at 20 degrees. Parameterise tilt, friction, mass, initial pose, dust and disturbances. Validate on 10, 20 and 30 degrees; 35 degrees is an optional stress condition.

Compute planning and telemetry in the panel frame, with a separately defined robot forward/left/up frame. Use transformed gravity, not a manual downhill acceleration added on top of MuJoCo gravity. Make collision masks intentional and test self-collision exclusions.

Start with the existing 0.002 s timestep, Newton solver and documented contact values as candidate settings. Establish stability and compare representative runs at 0.001 s. Start physics and logging at 500 Hz; tune control update rate only through explicit experiments. Never tune friction simply to force a desired outcome.

Use joint encoders, IMU, four real contact/bumper regions and downward-looking edge range sensors as appropriate. Derive sensor orientation and ray direction from documentation. Keep simulator ground truth available for scoring; disclose whether the controller itself uses ground truth or an estimator. Noise and latency are configurable seeded models, not measurements of real hardware.

### 4.3 Brush and cleaning

Use a transverse cylindrical brush with joint actuation, bounded speed and torque, and a compliant normal slide/mount if stable. Treat 900 RPM as a candidate setting, not a proven safe speed. Regulate load and speed; test jam/overload handling. Separate force estimates from true available sensor signals.

Represent soil as a panel-local 2D field, not thousands of rigid dust particles. Update only cells touched by the brush while contact/load/RPM conditions qualify. A candidate model is `D_next = D * exp(-k * contact_dose)`, with dose defined from contact time, normal load and speed. Label k and functional dependence as phenomenological assumptions until calibrated; sweep them. Repeated passes cannot remove more dust than exists.

Maintain separate quantities: geometric visited coverage, brush-contact coverage, cleaned coverage under a declared threshold, and residual soil. Keep a dust texture/heatmap synchronised with this field. Dirt disappearing is a visualisation of the proxy model, not proof of molecular cleaning physics.

### 4.4 Panel structural response and power

Core milestone: measure brush load and chassis acceleration honestly. Do not label them panel deflection. Optional next milestone: compliant panel/support model with mass, stiffness and damping validated through static load and free-decay tests. If used, label deformation as a reduced-order structural proxy. Material stress, coating wear and micro-cracking require additional validated models/experiments.

For relative energy yield, integrate a sourced or explicitly assumed soil-to-transmittance mapping. If initial clean-relative loss is L and removed-loss fraction is eta, then `P_before/P_clean = 1-L`, `P_after/P_clean = 1-L+eta*L`, and relative gain is `eta*L/(1-L)`. Distinguish percentage points recovered from percent gain relative to soiled output. Do not equate swept area with full loss recovery.

Mechanical actuator work comes from torque × angular velocity or force × linear velocity, integrated over time. Electrical energy additionally needs declared efficiencies, electronics overhead and regeneration assumptions. Report the distinction and units.

## 5. Control architecture

Use classical closed-loop control first. No foundation model in the real-time safety loop. Reinforcement learning is an optional later comparison only after the deterministic baseline and evaluation pipeline work.

State machine: `INIT -> SELF_CHECK -> DOCKED -> APPROACH -> SWEEP -> DECELERATE -> TURN -> ROW_SHIFT -> ALIGN -> SWEEP -> RETURN -> DOCKED`. Safety states: `RECOVERY`, `SAFE_STOP`, `ABORT`. Direction is explicit sweep metadata. Cover every transition with a reason/event and avoid instantaneous direction reversals.

Pipeline: path generator -> path-relative position/heading error -> bounded speed/yaw command -> left/right target velocities -> drive PI/PID -> torque limits -> MuJoCo. Add anti-windup, filtered derivative if used, acceleration limits, integrator resets on relevant transitions, actuator saturation reporting and timeout guards.

For nominal differential drive, `v_L = v - b*omega/2`, `v_R = v + b*omega/2`; divide by effective drive radius for angular targets. Verify motor sign conventions in a flat-ground test. For skid steer, effective track width is a modelling approximation and needs calibration. Correct cross-track drift by feasible heading/traction changes, not a fictitious independent lateral motor.

Planner shrinks usable space by the full swept robot/brush envelope, not just chassis centre. Include stopping distance, latency, uncertainty and slope effects in margins. Turn feasibility must be checked with the actual brush offset and rectangular footprint. If a U-turn cannot fit, use a physically feasible multi-point manoeuvre or explicitly exclude the unreachable border.

Baseline: same model, planner, actuator limits and safety envelope; simple feedback without proposed slip adaptation. Proposed: cross-track PI/heading control, bounded slip-aware speed/load adjustment and recovery. Ablate adaptation separately so improvement has an interpretable cause.

At very low velocity, ratio-based slip is unstable: log absolute slip speed and flag ratio validity. Define slip using drive/roller contact kinematics and measured panel-relative chassis motion; calibrate straight-line and turning behaviour before thresholding.

## 6. Fault handling and tests

| Injected fault | Detect from | Required behaviour |
|---|---|---|
| Low friction / sustained slip | Valid slip estimate, drift, loss of progress | Slow/unload, bounded retry, abort if traction unavailable. |
| Edge approach / bumper contact | Footprint margin, edge sensor/contact | Brake before boundary where physically feasible; stop brush; retreat only if safe. |
| Brush jam | Speed tracking error + effort/load | Ramp down, bounded retry or abort; no infinite stall. |
| Sensor dropout / stale data | Timestamp and validity checks | Declare fault and enter justified degraded/stop mode. |
| Excessive tilt / contact loss | IMU, orientation, support contacts | Stop cleaning and mark unsafe; do not conceal falling/sliding. |
| NaN / solver instability | Finite-state checks and solver warnings | End run as failed with diagnostic artifact; never count as success. |
| Output/disk failure | Write/flush error | Fail visibly and preserve available metadata; never claim saved data. |
| Mission timeout | Simulation-time and progress guards | Explicit timeout status and partial metrics. |

An unpowered crawler can slide. A software stop is not a mechanical brake. Model a brake/tether only if its mechanism and limits are explicit; do not freeze qpos or add invisible holding forces.

Test gates:

1. Exact XML exists and compiles; expected joints, sensors and actuators resolve by name.
2. Finite state, correct mass/CoM, no severe initial interpenetration; stationary contact test.
3. Flat straight drive, reverse, left/right turn, torque saturation and brush rotation tests.
4. Incline equilibrium and friction threshold sanity checks; compare to analytical bounds.
5. Single-row tracking, braking, turn envelope, row shift and return.
6. Full nominal mission: no pose overwrites, unique coverage, task-completion outcome.
7. Fault injections above, including physically unrecoverable cases.
8. Replay same seed/config/model revision and compare within a documented tolerance.
9. Recompute summaries from telemetry, plots from summaries, and economics from declared inputs.
10. Fresh-clone reproduction in isolated dependency environment, with headless and viewer paths verified separately.

Use unit tests for geometry, frames, coverage and formulas; simulation integration tests for contact, control and faults. Avoid snapshot tests that merely preserve a bug. Failed trials remain in the dataset.

## 7. Telemetry and evaluation

Use simulation time from MuJoCo. Retain full timestamp precision at 0.002 s; rounding to two decimals would corrupt 500 Hz timestamps. Rendering at 30/60 FPS is independent of physics/logging. Headless trials must not require the viewer.

Per-run manifest: run ID, seed, controller variant, config hash, MJCF hash, commit SHA, dependency versions, randomised inputs, timestep, logging rate, termination reason and timestamps. Log parameter distributions and realised draws. Do not claim bitwise reproducibility across all machines.

Telemetry: time, panel-frame pose/velocity, yaw, reference, tracking error, joint velocities, actuator forces/torques, brush speed/load, contact status, slip validity/value, coverage, soil removed, cumulative mechanical work, FSM state and event IDs. Keep failure outcomes. Distinguish commanded control from measured actuator force.

Trial summaries include tracking RMSE, completion/abort, mission duration, coverage, residual soil, slip distance, edge violations, brush-load peak, mechanical work, control effort and model-based recovered yield. For mixed translational/rotary actuators, report squared-effort integrals separately because units differ. A torque-only drive permits a clearly defined sum of torque-squared terms.

Primary hypothesis: lower cross-track RMSE under a predefined disturbed condition. Secondary outcomes: completion, slip distance, cleaning efficiency and energy. Do not select the primary endpoint after seeing results.

Protocol: pilot a few runs first, estimate runtime/storage, then freeze a separate evaluation seed set. Core: baseline and proposed at 20 degrees, at least 30 each. Stronger study: 10/20/30 degrees × 2 controllers × 50 runs = 300 missions, with predefined disturbance distributions. Reuse matched scenarios for a paired comparison if selected in advance; use an appropriately paired test and paired effect-size definition. If the course requires Welch's t-test and pooled Cohen's d, use independent evaluation groups for that analysis and state the design. Do not apply unpaired inference to paired observations without justification.

Experimental unit is a complete run, not every 500 Hz row. Report N, means/SD, exact p-value, df, appropriate effect size and 95% CI of the difference. Use t-based intervals when appropriate. Compare failure rates with suitable intervals; do not silently remove failed runs from continuous-metric plots. Report conditional-on-completion metrics with their denominator. Exploratory secondary comparisons are labelled; correct multiplicity when making multiple confirmatory claims. Do not tune for p < 0.05 or d > 0.8.

Figures: reference/actual trajectory over dust field; error/slip/effort with state bands; baseline/proposed distributions and CIs; failure/completion rates; energy versus cleaning; economic sensitivity. Export at 300 DPI and verify PNG metadata/dimensions. No synthetic target inputs in result plotting.

## 8. Business model

Compute throughput from completed runs and include recovery/failure downtime. Labour reclaimed subtracts setup, supervision and maintenance. Source inputs where possible; otherwise label assumptions and sweep at least ±30% or a defensible scenario range.

Normalise all financial quantities consistently to annual manual baseline cost. Calculate kappa, `NCRI = 1-kappa`, annual savings and payback. Non-positive savings produce an explicit no-payback result. Report payback months and the dossier's dimensionless lifetime-normalised payback separately. Do not confuse years/months with dimensionless ratios.

Queue: define a cleaning job (row or array), lambda jobs/hour, mu jobs/hour and crawler count c. For M/M/1, rho=lambda/mu and `Wq = rho/(mu-lambda)` only if rho<1. Flag unstable queues otherwise. Deterministic scheduled cleaning does not naturally satisfy Poisson/exponential assumptions; use M/M/1 as an explicitly labelled rubric approximation and optionally compare against discrete-event scheduling.

FMEA: at least traction loss, edge fall, brush overload/coating damage, and sensor failure. Score S/O/D and RPN before/after; justify each mitigation with a test. Do not lower severity merely because detection improves, or claim scratch prevention from a force limit alone.

Sensitivity: friction/tilt affects completion and service capacity; cleaning coefficient affects recovery; supervision, brush replacement and capital ratio affect payback. Plot break-even crossings and uncertainty, including cases where the robot is not economically attractive. Avoid claiming measured real-world electrical savings from a simulated proxy.

## 9. Visual demonstration

Use MuJoCo's native viewer first, with a tidy roof/rack, recognisable cells, chassis/brush details, good lighting and three cameras: overview, follow and brush/contact close-up. Decorative geometry must not alter mass/contact unintentionally.

Show state, seed, speed, coverage, residual soil, slip validity, brush RPM/load, elapsed simulation time and safety status. Show planned and actual path overlays plus a footprint/edge margin. Clearly distinguish live data from replay. A lightweight dashboard is optional after the viewer works; it consumes telemetry and cannot become a required control dependency.

Live story: start deterministic nominal mission -> display path/brush cleaning -> inject a seeded disturbance -> show detected event and recovery/abort -> compare baseline plot -> show economic break-even. Reset starts the same documented seed. Controls: pause/resume, reset, camera switch, fault injection, telemetry toggle. No internet/API calls during the demo.

3:45 video target: 0:00–0:20 problem/team; 0:20–1:40 live simulation + handled fault; 1:40–2:20 actual results; 2:20–3:00 business sensitivity/queue/FMEA; 3:00–3:45 individual contributions and AI verification. Every member appears and speaks. No PPT. Keep a clearly labelled recorded backup, but rehearse the required live demonstration from a fresh clone.

## 10. Team ownership and delivery sequence

Arush: MJCF, mass/CoM, propulsion/contact validation, edge geometry and dynamics tests. Ronit: brush/contact control, path tracking, FSM, telemetry QA and fault tests. Harshvardhan: sources, economics, queue/FMEA, statistics and reproducible plots. All understand the whole system; roles are ownership, not knowledge silos. Students make genuine commits from their own identities; never manufacture attribution.

Branch names follow assigned roster: `feat/e048-lead-tracked-crawler`, `feat/e052-waterless-rotary-bru`, `feat/e058-csbs-photovoltaic-de`. Never direct-push main. Check incoming changes before integration; no blind pull/reset. Push feature work and open a reviewable PR when implementation is actually requested and ready.

Deadline-aware order (repository dates: 26 Oct 23:59 IST submission, 31 Oct showcase; video requested by 25 Oct 18:00 IST):

1. **Gate A — truthful physics:** environment, exact-model compilation, propulsion, brush and stationary/drive tests. If this fails, defer cosmetic work.
2. **Gate B — complete mission:** feasible path/FSM, safety guards, complete 20-degree run, honest coverage and 500 Hz logs.
3. **Gate C — evidence:** frozen baseline/proposed experiment, required N, statistics, genuine plots, complete economics and fault demonstration.
4. **Gate D — submission:** source verification, Word/PDF dossier, video, genuine team contributions, peer review, fresh-clone rehearsal and individual turn-in.
5. **Stretch before showcase only if core is stable:** compliant panel proxy, broader slope grid, adaptive brush, richer visuals, additional ablations.

If runtime is scarce, reduce extra scenarios before reducing required replication or dropping mandatory dossier evidence. Benchmark pilot runs before promising 300 full missions. Estimate rows as runs × duration / 0.002; stream outputs and bound worker count by measured CPU/RAM/storage. Keep agreed CSV evidence, manifests and summaries in the group folder; do not commit virtual environments, raw videos or unnecessary large binaries. Decide raw-data retention transparently before finalising the experiment; do not silently downsample required evidence.

## 11. Proposed file structure (future work, not created now)

Preserve expected entry points; add small modules rather than one giant script:

```text
Group_06_Arush_Ronit_Harshvardhan/
  models/solar_cleaning_crawler.xml
  src/crawler_cleaning_controller.py   # maintained executable entry point
  src/simulation.py                   # MuJoCo stepping and state access
  src/planning.py                     # feasible coverage paths
  src/control.py                      # tracking/drive/brush controllers
  src/safety.py                       # supervisor and fault logic
  src/cleaning.py                     # soil field and contact dose
  src/telemetry.py                    # buffered logging and manifests
  src/run_trials.py                   # headless evaluation
  src/test_env.py                     # strict exact-model smoke test
  config/                            # validated named scenarios
  tests/                             # unit and simulation tests
  analytics/photovoltaic_degradation_economics.py
  analytics/generate_paper_figures.py  # changed to read measured data
  analytics/*_real_trials.csv
  analytics/trial_summary.csv
  docs/figures/
  docs/CLAIM_VERIFICATION.md
  docs/AI_AUDIT.md
  docs/EXPERIMENT_PROTOCOL.md
  docs/MDRIIA_Group_06_Technical_Dossier.docx
  docs/MDRIIA_Group_06_Technical_Dossier.pdf
```

Add reproducible group-local dependency pins after a tested environment exists; root requirements are unpinned and outside editing scope. Any future reusable environment instructions must use existing checkouts, not create a worktree unless explicitly requested.

## 12. Which AI models/tools to use

Choose by capability and availability, not a guarantee that a model cannot make mistakes. Recommendations refer to model options exposed in this session; availability elsewhere can differ.

| Task | Recommended choice | Output that must be checked |
|---|---|---|
| Physics architecture, dimensional reasoning, difficult diagnosis | GPT-6-astra at high reasoning, if available | Derivations checked against docs, units and runtime. |
| Main implementation, small diffs, test-driven fixes | GPT-6.1-sol / Codex with repository and terminal access | Working changes plus actual command output. |
| Repetitive documentation/data-schema tasks | Smaller available model such as GPT-6-luna | Schema validation and human review. |
| Independent review | Fresh session/model with code + protocol | Specific counterexamples and failed assumptions. |
| Scientific claims and citations | Primary papers, MuJoCo docs, standard scope text | Exact bibliographic match and supporting passage. |

Do not add an LLM, image generator, vision network or RL policy just for branding. Core runtime needs MuJoCo, NumPy, SciPy, pandas, Matplotlib, test tooling and optional video tooling. Python must reproduce results without an AI subscription. Visual assets may be procedural; generated robot pictures do not supply valid mechanical models.

## 13. Copy-paste development prompts

Use the common contract with every prompt:

> Work only inside Group_06_Arush_Ronit_Harshvardhan in the existing checkout. Read current files and newer rubric/dossier before editing. Preserve unrelated changes. Use a feature branch, never main. Implement only the requested phase. Do not fabricate citations, telemetry, test results or authorship. Do not change tests to hide failures. Separate assumptions from measured quantities and model limitations. Use installed-version official MuJoCo documentation for unfamiliar APIs. Run meaningful checks and report exact commands, outcomes and remaining limitations. Do not push or publish as part of this prompt. End with a short explanation the students can defend in a viva.

### Prompt 1 — environment and reproducibility

> Prepare a group-local reproducible Python environment using the repository dependency requirements. Inspect available tooling first. Pin a tested compatible set without modifying root requirements. Run the exact group smoke test and diagnose every failure. Do not use fallback substitute XML as readiness evidence. Verify headless stepping independently of viewer rendering. Save reproducible instructions and report version/platform limits. Do not implement the mission controller yet.

### Prompt 2 — physical model

> Audit and repair solar_cleaning_crawler.xml for a torque-driven skid-steer crawler approximation with a rotary brush. Verify root-body/freejoint rules, transmission attributes, mass/CoM, contact frame and friction semantics, brush orientation and actual dimensions. Implement named joints and bounded drive/brush actuators. State clearly that driven rollers approximate tracks. Run sustained stationary, straight, reverse, turning and incline tests. No qpos/qvel overwrites during a mission, no hidden holding forces, no invented sensors. Show analytic sanity checks and compiled model counts.

### Prompt 3 — feasible autonomy

> Implement a modular coverage planner, closed-loop drive/brush controller and explicit mission FSM using actual MuJoCo state. Plan in panel coordinates with robot/brush footprint and stopping margins. Implement physical turn/row-shift trajectories, saturation, anti-windup, state guards and timeouts. Compare against a simple baseline on identical physics. First prove one row and one safe turn, then a complete mission. Demonstrate disturbance recovery and physically honest abort behaviour.

### Prompt 4 — measured cleaning and telemetry

> Add a seeded soil field and clearly labelled contact-dose cleaning proxy. Separate visited, brush-contact and cleaned coverage; handle overlaps and borders. Log genuine physics/sensor state at 500 Hz with full time precision, events, seeds and manifest hashes. Compute slip with a low-speed validity rule, effort with correct units and mechanical work from actuator motion/force. Keep predicted energy recovery separate from measured motion. Add tests proving cleaning does not occur without qualifying brush contact.

### Prompt 5 — safety and adversarial tests

> Try to break the crawler using low friction, excessive tilt, edge approach, brush jam, sensor dropout, bad config, logging failure and timeout. Add deterministic regression tests for each diagnosed fault. Require explicit failure outcomes and bounded retries. Confirm zero control does not falsely imply stationary safety on a slope. Do not freeze state to make tests pass. Report the validated operating envelope and cases that remain unsafe.

### Prompt 6 — experimental evaluation

> Write and freeze an evaluation protocol before the final runs. Select a primary endpoint, baseline, scenario distributions, independent seeds and an appropriate paired or independent design. Pilot runtime/storage, then run at least 30 missions per controller per condition, aiming for 50. Retain failures and seed/config metadata. Compute run-level RMSE/effort/task metrics, t-test with df and exact p, defined Cohen effect size and CI. Regenerate 300 DPI plots from real-run CSVs only. Never use starter target data or count time steps as independent trials.

### Prompt 7 — economics and evidence

> Replace hard-coded output claims with a dimensionless economic analysis using measured throughput plus sourced or labelled uncertain inputs. Calculate labour reclaimed, kappa, NCRI, payback months, lifetime-normalised payback, and a queue model with stated assumptions. Handle unstable queues and no-payback cases. Add sensitivity and break-even plots and four evidence-backed FMEA modes. Verify all literature metadata and supporting passages independently; unresolved claims stay labelled unverified.

### Prompt 8 — demonstration and submission

> Add a clean native MuJoCo demonstration with state/telemetry overlays, path/dust display, documented cameras, deterministic reset and seeded fault injection. Keep rendering separate from physics. Prepare a 3–4 minute no-slides script with speaking roles for all members, genuine result plots and business sensitivity. Produce a dossier evidence checklist without inventing signatures, consent, peer-review scores or personal details. Rehearse from a fresh clone and report which display/headless paths were actually tested.

### Prompt 9 — independent final review

> Review this project as a sceptical robotics examiner. Trace every reported metric to raw MuJoCo telemetry, every economic output to declared inputs, and every claim to a source or stated assumption. Inspect for teleportation, unconstrained propulsion, invalid contact semantics, silent sensor failures, data leakage, cherry-picked trials, pseudo-replication and unsupported glass-safety claims. Reproduce a nominal run and an injected failure. List issues by severity with file/line evidence. Do not approve based on attractive screenshots or passing imports.

Bug-fix prompt after any failure:

> Here is the exact command, output, config, seed and commit. Reproduce the failure, isolate the smallest cause, check relevant official documentation, make the smallest justified fix and rerun the failing case plus directly affected regression tests. Preserve the original evidence. Do not lower acceptance criteria or change unrelated code. Explain what would have falsified your diagnosis.

## 14. Final acceptance checklist

- Exact model compiles and sustained dynamics remain finite.
- Crawler movement is driven through documented physical actuators.
- Full nominal mission, feasible turns and an injected failure are demonstrated.
- Safety limitations, locomotion approximation and cleaning proxy are disclosed.
- Every reported run has seed, configuration, model/code provenance and outcome.
- Actual 500 Hz logs, required N per condition and failed trials are present.
- Plots and statistics regenerate without target data or manual result editing.
- Business numbers recalculate, units/normalisation are consistent, break-even is shown.
- Claims/DOIs/standard applicability are independently checked.
- Three real AI-error audit cases are documented from actual interactions and verification; none invented.
- Team IDs are confirmed; contributions and git history match reality.
- Completed Word dossier preserves controls; PDF, video and peer review are complete.
- Each member performs their own Teams turn-in and can explain the whole project.
- Fresh-clone setup, live demo and backup path are rehearsed before showcase.

The first implementation task is Gate A. Do not spend the first development session on a dashboard, a learning algorithm or cinematic assets while the physical model and evidence path remain unresolved.
