# Revised plan: simple fixed-brush crawler with vision-triggered cleaning

Planning revision, 25 October 2026. The latest user instruction accepts roughly 90% whole-panel coverage to reduce mechanical complexity, cancels telescoping/deploying brushes and permits an invisible simulation boundary to prevent falls. This supersedes the earlier 100%-coverage/telescoping-tool proposal. No robot or controller code is changed by this planning revision.

## Latest presentation requirement — visible chassis reaches the edges

The demonstration requires the robot chassis to visibly reach/touch the panel edges, with approximately 90% actual cleaning coverage as the engineering target. This section supersedes earlier requirements for removing arbitrary edge deposits or proving every corner cleaned in the final demonstration.

The main demonstration will deliberately deposit dust/physical crumbs in a predefined central service region. The region and deposition distribution must be stored in its scenario metadata. This selected scene does not test arbitrary perimeter contamination. Detection must still operate on actual camera images; central deposition must not become a timed command for the robot to leave home.

**Required visible behaviour:** a perimeter pass in which the chassis itself approaches/touches each of the four inner panel boundaries, followed by an overlapping sweep of the panel and actual removal of the central deposited dirt. A brush tip reaching the boundary while the body stays far inward does not satisfy the requested visual behaviour. Include sufficiently wide, uninterrupted views that body position against the frame can be seen. Test feasible corner transitions rather than promising unsupported body positions at corners.

Use the fixed-brush mechanism and the authorised concealed collision guard. Validate body-to-frame gap/contact, roller support, brush/frame collisions and guard reaction forces during each edge approach. Plan headings deliberately: a forward brush projecting beyond the chassis can hit a frame before the body reaches it, so a suitable sideways/tangential approach may be required. If the current geometry prevents body contact, investigate a simple fixed geometry/frame adjustment with explicit collision behaviour rather than pose resets or clipping through the frame. No telescoping tool is introduced.

Maintain two distinct outcomes: (1) the robot visibly performs its edge/perimeter pass; (2) measured qualifying cleaning coverage targets approximately 90% of all 24 m² and central deposited dirt is actually removed. Neither result is established by the current ~61–62% prototype. The main scene need not contain edge dirt. Keep actual coverage and residual metrics unchanged by presentation choices; do not turn chassis proximity into a cleaning/contact measurement. A future wider brush is a proposed hardware change, not an implemented capability.

Final storyboard: idle at home → central dirt falls → RGB detection/confirmation → physical departure → deliberate body-to-edge perimeter pass and overlapping cleaning sweep (order chosen for a feasible route) → targeted central cleaning/reinspection → return home and settle. The guard may remain invisible in the main render as requested, with its presence and modelling role recorded in the technical documentation. This checkpoint revises the plan only.

## 1. Decisions and unchanged requirements

- **Cancel the telescopic/articulated edge-tool solution.** There will be no deployment sequence or time spent extending a tool. A rotating brush is still required, but its mount/overhang remains fixed.
- Start with the existing 0.55 m main brush. Investigate a wider/repositioned fixed brush or simple permanently extended sweep attachments only if geometric reach analysis shows they are necessary. Every added component must still have credible mass, collision/contact geometry and any required actuation.
- Target **at least 90% of the original 24 m² glass surface** in the declared nominal scenario, with the remaining area and locations reported. This is a target, not a result: the current best demonstrated candidate is approximately 61–62%.
- For the selected central-deposition demonstration, remove all detected central targets and attempt the full planned sweep/perimeter pass. Arbitrary edge-deposit removal is outside this demonstration scope. If used in a diagnostic test, an unreachable target is still logged rather than falsely marked removed.
- Keep camera-based detection, idle-at-home behaviour, thresholded triggering, targeted revisits, a whole-panel sweep attempt, verification and return home.
- Larger physical crumbs must actually be pushed, swept off or collected through modelled contact. They may not vanish under a dirt texture mask.
- Aesthetic scenery remains deferred.

## 2. Current truth

The 8.5 kg crawler has four torque-driven rollers approximating tracks and a fixed transverse rotary brush of radius 0.06 m, full width 0.55 m, mounted 0.29 m ahead of the chassis. The brush is the blue cylinder in the video. The rack is tilted 20 degrees and its perimeter is raised about 0.05 m above the glass.

There are still no model cameras, RGB dirt detector, visible falling dirt or monitoring trigger. Navigation uses simulator ground-truth pose. The soil array is invisible and uses an uncalibrated removal proxy. No new requirement in this plan is implemented yet.

The former 0.45 m circular clearance guard encloses both chassis and brush. It is conservative, and shrinking the allowed cleaning area follows directly from it. Earlier expanded routes also showed real downhill drift, so not every lost area is caused by conservative geometry alone. The active safety system brakes the wheels; it does not provide a passive holding mechanism or a guarantee against falling.

## 3. First gate: geometric reach with a fixed brush

Separate the **support envelope** (roller contact/chassis support) from the **cleaning footprint** (fixed overhanging brush). Replace the one-radius planning approximation only after checking the actual oriented geometry and swept motion. Do not equate brush overhang with wheel overhang or mark a chassis partly outside its supported region as safely supported.

Compute brush reach along all four edges and corners, frame collisions, turning space, uncertainty and stopping margin. Generate a candidate overlapping lane/edge route and rasterise it against the full panel before attempting long missions. Use real tracking/contact measurements to validate its coverage afterward.

The 90% target requires reaching substantially closer to the perimeter: for illustration, an otherwise completely covered 6 m × 4 m rectangle with a uniform uncleaned border reaches 90% only when that border is about 0.123 m wide. This is a geometric sanity check, not a permissible chassis clearance. Brush overhang may allow the chassis to remain farther inward while reaching this cleaning boundary.

Try, in order:

1. The existing fixed brush with improved footprint-aware routing and support-envelope analysis.
2. A modest fixed brush width/position change or permanent sweep attachment if needed, checking added load and collisions.
3. Supported direction changes or separate edge passes where feasible. Never conceal unsuccessful turns by resetting pose.

If 90% remains unreachable, report the reach map and identify the smallest physical change required. Do not generate a route that scores 90% on geometry while actual contact only cleans 60%.

## 4. Fall prevention: guarded simulation and free-crawler evidence

The user authorises an invisible boundary. Implement this as an explicitly documented **collision guard/catch rail** around the rack, preferably matching a plausible physical perimeter restraint. It may be transparent in the main view, but must be visible in a debug view and identified in the final explanation. Its location, height, collision geometry and reactions must be specified.

A collision guard can prevent exit from the panel edge within tested trajectories; it does not create tyre grip, stop all sliding or prove physical impossibility of falling in every state. Check whether the robot can tip, climb or pass over it and whether it obstructs the brush or home route. If the physical guard cannot guarantee containment in a fault, report that result and revise it.

Keep two named evaluation configurations:

- **Guard-assisted demo:** the disclosed collision boundary is enabled. Report guard contacts/reaction forces and whether the robot relies on the guard during the route.
- **Free-crawler diagnostic:** the added guard is disabled. Retain traction/slide/fall results to distinguish control/traction performance from containment.

No silent qpos/qvel clamps, arbitrary friction increases, hidden forces that hold the robot to glass or scoring failures as successful cleaning. If a hard positional constraint is ever desired as an animation-only mode, it must be labelled nonphysical and cannot supply physics/traction evidence. The planned main demonstration uses physical collision containment instead.

## 5. Traction on the incline: what exists and what must be tested

Traction is already simulated through real motor torques, roller contacts and friction. It is not currently validated against a physical prototype. The model uses an assumed roller sliding-friction coefficient of 1.2; effective contacts depend on MuJoCo mixing and load distribution. This is not measured rubber-on-dusty-glass data. Four bounded wheel-speed controllers provide active holding/braking when traction is available; this does not hold the robot after power loss.

A useful ideal static check is mu >= tan(theta). At 20 degrees this is about 0.364. For 8.5 kg under gravity alone, downhill force is about 28.5 N and normal load about 78.4 N. These are whole-body ideal estimates, not per-wheel contact forces or a dynamic safety certificate. Brush forces, turns, transient load transfer and contamination affect the result.

Existing checks found about 3.7 mm downhill drift during active stationary holding and about 0.292 m downhill displacement during a turning test. Severe low-friction injections reached the edge in all three development seeds. These failures demonstrate that 'we will use grippy wheels' is not sufficient evidence.

Planned work:

1. Measure roller slip speed from encoder motion versus estimated chassis velocity, with a low-speed validity rule. Separate simulation scoring velocity from the navigation estimate.
2. Use low speed, acceleration/yaw limits, suitable mass distribution and the bidirectional route to reduce aggressive skid turns.
3. Test assumed friction across a declared range, incline changes, brush on/off, loads, straight motion, turning, idle and braking. Include conditions below the ideal static bound rather than excluding all failures.
4. Validate bounded slip-aware slowdown/stop behaviour. If gravity exceeds available tangential contact force, software wheel control cannot guarantee holding; containment/tether/brake must supply an explicit physical mechanism.
5. For a future prototype, propose a nonmarking high-friction rubber/EPDM or silicone tread only as a candidate. Measure actual grip on the relevant clean/dusty/wet glass and check coating compatibility before selecting a material or claiming safety. Include a real perimeter restraint/tether or other engineered fall protection where appropriate.

The viva explanation must distinguish assumed friction, demonstrated nominal simulation, failed low-friction trials, the added simulated guard and the physical testing still required. No claim that a tyre material automatically solves the slope problem.

## 6. Visible debris and actual brush interaction

Prototype tens of small physical grains/flakes falling under gravity and colliding with the panel. Fine deposited dust can then use a persistent visible surface field, with the conversion from representative grains logged as an explicit hybrid abstraction. This is not a resolved aerosol/adhesion model.

Surface dirt fades only under qualified **local** tool contact, measured load, brush rotation and dwell. Aggregate force at one end must not clean the whole width. Add a segmented-contact/contact-patch approximation and test no-contact, brush-off and insufficient-dose cases. Use stripes or noncolliding bristle visuals so actual actuator rotation is obvious.

Larger crumbs stay as rigid bodies and are moved by actual brush/crumb/panel contacts. Decide and model their removal destination: off-glass into an external collection region, or into a simple explicit catch tray. Score actual positions and retained mass/object IDs. If a crumb becomes trapped at the frame, it remains a failed target until genuinely moved. Test both physical feasibility and solver/runtime cost before promising all debris sizes.

## 7. Cameras, localisation and dirt estimates

Add a forward/downward robot camera plus overlapping fixed cameras at raised panel-edge/corner brackets, without obstructing the glass. Use an independent presentation camera.

Calibrate the camera views and panel projection. Begin with RGB appearance/reference differences, connected components and temporal persistence. Fuse observations into a dirt/confidence/unknown map. Treat shadows, reflections, robot occlusion and stale images explicitly. Unknown is not clean.

The detector reads RGB images and calibration, not hidden soil/object IDs or the deposition schedule. Hidden truth is isolated for evaluation. Prototype actual camera-based robot localisation using fiducials, with wheel encoders/IMU for continuity. If ground-truth navigation is retained temporarily, label it; camera-based dirt detection alone does not imply vision-based localisation.

Benchmark a candidate 5–10 Hz camera pipeline while retaining 500 Hz physics. Choose detectable patch/crumb size and scoring resolution based on actual camera visibility before freezing evaluation thresholds.

## 8. Event-driven mission and coverage-aware routing

HOME_MONITOR → DIRT_CONFIRM → PLAN → UNDOCK → TARGETED_CLEAN + PANEL_SWEEP → VERIFY/REVISIT → RETURN_HOME → SETTLE → HOME_MONITOR.

A subthreshold amount stays on the estimated map while the robot remains home. Dirt area/confidence must exceed the configured trigger for a declared persistence interval. A significant single patch can have its own trigger. Once triggered, perform the planned sweep and revisit detected dirt; do not continually restart the mission from repeated detections.

Track estimated dirt, qualified physical contact/dose and hidden evaluation truth separately. Newly deposited dirt queues another inspection/pass. Bound retries and mission time; an unreachable or persistent patch yields INCOMPLETE. Leave home physically and check pose/orientation and planar/angular/brush settling on return. A supported adjacent home bay may be needed so a parked robot does not hide or permanently occupy dirty glass.

## 9. Acceptance and test gates

Primary nominal target: at least 90% **measured qualified coverage of the original 24 m²**, plus removal of every detected target within the supported/reachable debris domain. Report every uncovered area, unknown cell and failed target. A literal 100%/microscopic-cleanliness claim is no longer required or supported. Do not equate geometric sweep, qualifying contact, dose and residue.

Required cases:

- Long clean idle and subthreshold deposits: no unwanted launch or slide.
- Significant central deposit: image-triggered departure, physical removal, sweep and home return.
- Edge/corner deposits: reach/remove or explicitly flag unreachable; never silently ignore them.
- Multiple patches and new debris during motion: queue/revisit/verify.
- Larger crumbs: genuine displacement/removal, with retained physics evidence.
- Lost brush contact: persistent dirt and retry/INCOMPLETE.
- Camera occlusion/dropout or lighting change: unknown/stale handling, no false clean.
- Jam, excessive load, low friction, incline and power/holding assumptions: explicit safe response or documented failure.
- Guard on/off: report contact forces and whether containment is carrying the robot.
- Numerical/timestep consistency and repeatable seeds; no state forcing.

Develop on pilot seeds, then freeze camera/trigger/removal thresholds, geometry, controller, guarded mode, scenario distributions and success rules before held-out trials. For statistical comparisons run at least 30 complete missions per controller/condition and retain failures; the old 30-second tracking study is not a substitute. Log actual contact/load/speed, support and guard reactions, detections, confidence, physical crumbs, contamination accounting, pose estimate versus scoring truth, coverage and docking. Pilot runtime/storage before the final batch.

## 10. Final recording and deferred scenery

Show home idle, visible falling dirt, actual camera detection with mapped location, triggered departure, visible rotating brush and genuine crumb interaction, panel sweep/edge approaches, residual inspection/revisits and settled return home. Display measured whole-panel percentage and remaining targets. Label accelerated playback and the invisible collision guard. Do not animate the overlay to 100% or imply complete coverage if the measured result is around 90%.

Balcony/rooftop, sun/sky/clouds and city meshes follow the functional gates. Start with primitives or licensed assets; no external model is required now. Keep scenery noncolliding unless intentionally physical, and rerun vision checks when lighting changes.

## 11. Execution order and deliverables

1. Fixed-brush reach map, support-aware route and disclosed guard design; prove whether >=90% is geometrically and dynamically plausible.
2. Traction/containment checks and local brush contact validation.
3. Visible falling dust plus real physical crumbs and contact-gated removal.
4. RGB camera detector, mapped targets and localisation interface.
5. Idle trigger, mission lifecycle, targeted revisits, verification and home return.
6. Integrated development tests, held-out evaluation and real-data figures.
7. Record actual behaviour; then add scenery and prepare the human team submission.

Extend the existing model/planning/controller/safety modules and add separate debris, vision, mission-management, local-contact and isolated-evaluation modules as needed. Preserve historical evidence and push reviewable milestones. No telescoping mechanism, API credential or neural service is a prerequisite. Only the plan changes in this checkpoint; implementation starts in a subsequent work step.
