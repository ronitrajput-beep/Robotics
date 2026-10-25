# Implementation plan: vision-triggered cleaning of the entire panel

Planning checkpoint, 25 October 2026. This document changes the implementation objective; it does not claim these features already work. User requested a plan before implementation. No robot, physics, sensing or controller implementation is changed by this checkpoint. This plan takes precedence over older plans where they assume an always-starting fixed raster.

## 1. Required behaviour

The robot rests at a repeatable home position with its brush off. Cameras on the robot and at the panel edges monitor the glass. Visible dirt falls onto the panel after the simulation starts. Camera observations, not the deposition schedule or a hidden dirt array, decide whether contamination is sufficient to trigger cleaning. Below the configured trigger threshold the robot stays home. Once triggered, it covers the complete glass surface, including edges and corners, deliberately revisits detected dirty locations, verifies the result with cameras and returns home. After settling, it continues monitoring rather than endlessly driving the same route.

The priority order is physical feasibility and safety, measurable full-surface cleaning, vision and event-driven autonomy, reproducible evidence, then environment aesthetics. We will build and test these components in that dependency order, then demonstrate them together. No new external model assets are required to begin.

## 2. Current implementation and why it is insufficient

- The panel is 6 m × 4 m, tilted 20 degrees. Four driven rollers approximate tracks on an 8.5 kg free-moving chassis.
- A transverse blue cylinder at the front is the actual actuated brush: radius 0.06 m, width 0.55 m, offset 0.29 m ahead of the chassis. It is visible, but its cylindrical shape makes rotation hard to see.
- There are no model cameras, image-processing detector or monitoring/trigger state. The mission starts on invocation and uses simulator ground-truth pose.
- Current soil is an initially uniform numeric array. It is not rendered as dirt. A contact/speed gate activates exponential attenuation across an approximate rectangular brush footprint. Aggregate contact does not establish contact across the whole brush width.
- The best current candidate covers roughly 61–62% of the whole panel with a qualifying projected footprint. This does not satisfy the new objective. The 100% denominator remains all 24 m² of glass, not an interior rectangle.
- The planner uses a 0.45 m enclosing radius for both support and brush clearance. That protects the robot but excludes borders. One wider pilot stopped at the lower edge. The raised perimeter also affects access: its top is 0.05 m above the glass surface.
- Docking currently means settling near a point, not entering a modelled home station or engaging a latch. Severe traction loss is unsafe. These limitations must be resolved or retained as explicit failed operating conditions.

## 3. Meaning of full cleaning and valid physics

We cannot promise atom-level cleanliness, perfect perception, or flawless real-world physics. MuJoCo is an approximate rigid-body/contact simulator. The deliverable will be a tested operating envelope with explicit numerical, sensing and cleaning assumptions.

For this simulation, define the entire glass polygon as the cleaning domain, including boundary cells and corners. Start with a 1 cm scoring grid (600 × 400 cells); clip boundary-cell areas to the actual glass polygon. Verify whether camera resolution supports the chosen visible-debris size and scoring resolution before freezing them. The grid is a finite-resolution acceptance definition, not proof about microscopic dust. Report narrower unsensed/subcell limitations explicitly; never silently shrink the domain.

A successful mission must satisfy all of the following:

1. 100% of glass cells receive a validated cleaning-tool sweep, with no missing perimeter/corner cells. Tool passage alone is not a contact-dose guarantee.
2. Every deposited visible dirt patch above the declared detectable size is reduced below the frozen residual threshold, including adversarial edge/corner patches.
3. The camera verifier observes the whole panel after cleaning and reports no unresolved target-sized patch. Occluded/uncertain cells are UNKNOWN and require another view; they do not count as clean.
4. Independent hidden scoring confirms residual dirt and coverage. Hidden truth can fail the mission but cannot guide its ordinary trigger, targeting or completion decision.
5. No fall, invalid state, support-envelope violation or force/actuation-limit violation occurs; the robot returns home and settles.

Any remaining dirty or unverified cell means INCOMPLETE, not CLEAN. Freeze patch-size, confidence, residual and contact-dose thresholds after pilots but before held-out evaluation. Publish actual values and their assumptions. If mechanics cannot reach every cell safely, redesign the mechanism before declaring the milestone complete.

## 4. Phase A — prove full-surface mechanical reach

This is the first implementation gate. Better vision cannot repair unreachable glass.

### Proposed mechanism

Retain the crawler for interior cleaning and investigate a lightweight articulated/telescoping edge-cleaning tool with a rotating end brush. The main brush handles wide interior lanes. The auxiliary brush reaches strips and corners while the rollers/chassis stay supported. It must have explicit joints, mass, inertia, actuator limits, physical collision geometry and normal compliance/load measurement. It cannot be a cleaning radius that reaches through space.

First calculate the required reach from a safe chassis pose to the farthest corner. For example, a centre 0.45 m inward from two edges is about 0.636 m from their intersection before including uncertainty, stopping margin and tool geometry. This is a geometric estimate, not a selected safe arm length. Derive arm dimensions and mass through reach and stability analysis, including the raised perimeter and brush contact surface.

Separate three constraints: the roller/chassis support envelope, the articulated tool's swept collision envelope, and the glass cleaning footprint. The support envelope stays on supported surface. A brush may reach farther while remaining over glass, subject to arm collisions and tipping/contact-force checks. Never simply remove the old safety guard to gain coverage.

Consider a home bay adjacent to and mechanically supported with the rack, with a level transition/ramp where needed. Its geometry and access must be explicit; it must not cover an uncleanable patch of the 24 m² glass. If a robot parked on glass occludes its starting patch, leaving, cleaning and re-verifying that patch is part of the mission.

### Required checks

- Static reach map for all glass cells, all four boundary strips and four corners; tool/frame/chassis collision checks along transitions.
- Static support, centre-of-mass and contact-force checks for the extended arm in the worst slope direction; dynamic checks under turning and braking.
- Measured motor torque/speed saturation, normal contact load, support contacts, chassis roll/pitch and clearance.
- Flat drive/turn tests, then incline tests; timestep comparison at 0.002 and 0.001 s for representative nominal and edge manoeuvres.
- Determine a validated friction/tilt/load envelope. Address sliding through credible operating restrictions and, if required, a visibly modelled tether/brake with actual limits. No invisible holding forces or frozen robot state.

If the proposed tool cannot satisfy reach/stability, compare a different brush arrangement or explicitly supported edge mechanism. Do not choose an expensive full-perception implementation before passing this gate. No material, force limit or glass-safety claim is validated merely by making a simulation stable.

## 5. Phase B — visible debris and an honest cleaning interaction

Use a hybrid scene rather than thousands of expensive contact bodies.

- Represent a limited number of visible falling flecks/grains as actual MuJoCo bodies with gravity, collision and declared size/mass/friction. Use small spheres/flakes, not one oversized cube standing in for all dust. Prototype tens of representative particles first and measure solver/runtime behaviour.
- After physical panel contact and a declared settling/deposition rule, optionally convert deposited fine debris into a persistent surface dirt field rendered on the glass. This is an explicit hybrid abstraction: representative falling grains become a surface layer, with deposition accounting recorded. It does not claim resolved aerosol, adhesion or particulate microphysics.
- Keep larger crumbs as physical objects if we show them being pushed. They do not disappear simply because a cleaning mask overlaps them. Their trajectory/capture/removal must be physically represented or excluded from the supported debris class.
- Render the surface field as visible brown/grey patches or an updated texture on the glass. Rendering should be recognisable in robot and edge-camera RGB images. Physics/camera materials and texture updates must be tested before selecting the approach.
- A local dirt value decreases only under a physically qualified tool contact: actual tool position, local panel gap/contact support, measured load, tool speed and dwell. The whole brush rectangle must not be marked cleaned because one end touched. Prototype segmented contact sensing/contact-patch bounds or a validated local-contact approximation.
- Dirt fades/disappears progressively in those cells. No disappearance on camera detection, waypoint arrival, chassis proximity or elapsed mission time. No-contact and brush-off tests must preserve dirt.

Visible fade is acceptable as the requested easy-to-understand cleaning effect. Its coefficient and load/speed response remain a labelled removal proxy until calibrated. We will distinguish removal from collection: a disappearing surface proxy does not establish a real vacuum/bin mechanism. Fine grains/soil rendering will be confirmed as consistent across all cameras.

## 6. Phase C — real RGB vision on robot and panel edges

Add one forward/downward robot camera and fixed cameras on small raised brackets at the panel corners/edges. Start with four edge cameras with overlapping views; use visibility tests to adjust placement. No camera support may create an uncleanable patch on the glass. Add a top-down presentation camera separately; it is not secretly the detector.

Pipeline:

1. Calibrate camera intrinsics/extrinsics and the panel plane, using declared fiducials or a known camera mounting model. Project detected image regions onto panel coordinates with homography/ray-plane intersection, checking distortion, frame boundaries and uncertainty.
2. Maintain a clean reference and panel mask per camera. Prototype colour/appearance differences plus connected components and temporal persistence in controlled illumination. OpenCV-style classical vision is sufficient initially; a trained neural detector is not mandatory for camera-based sensing.
3. Fuse detections across views into an estimated dirty-probability/uncertainty map. Account for robot/tool shadows, occlusions, frame structure and stale images. Robot-camera close views verify suspicious cells and fine residuals.
4. Detect the visible fall/arrival where possible and confirm persistent deposited contamination. Do not trigger from the scenario's spawn notification or hidden dirt field.
5. Measure detection rate, false alarms, localisation error and latency, especially for corners, panel texture, robot occlusion and different lighting.

The detector receives RGB images, camera calibration and its own history—not segmentation IDs, object labels, hidden contamination masks or the injection schedule. Ground truth remains isolated for scoring. Camera rendering can naturally depend on the actual dirt field; reading pixels of that rendering is the intended sensing route.

Camera-known calibration does not prove vision-based robot localisation. Replace direct ground-truth navigation input in stages with fiducial localisation from edge views and robot encoders/IMU, keeping simulator state solely for scoring. If a ground-truth control mode is retained for diagnostic comparison, label it explicitly and never present it as vision localisation. Start with a feasible camera rate, e.g. 5–10 Hz, and benchmark; preserve 500 Hz physics with timestamped latest observations and stale-data guards.

## 7. Phase D — start only when sufficiently dirty

Implement a monitoring state machine:

HOME_MONITOR → DIRT_CONFIRM → PLAN → UNDOCK → SPOT_CLEAN / FULL_COVERAGE → EDGE_AND_CORNER_CLEAN → VERIFY → RETURN_HOME → DOCK_AND_SETTLE → HOME_MONITOR.

FAULT_BRAKE and INCOMPLETE are explicit alternatives; they cannot transition into a clean-success state without valid evidence.

- At home, observe periodically with the drive/brush off or the explicit holding mechanism engaged. Long idle tests must establish that the robot does not slide.
- Accumulate dirty area/confidence over multiple frames and use hysteresis. A small transient speck below the configured trigger stays on the map but does not launch a mission. Several small patches can accumulate past the trigger. Define a separate rule for a single significant patch.
- Once the threshold persists for the declared confirmation time, latch a mission request. Repeated detections must not repeatedly restart the mission.
- Clean the whole panel once the mission is triggered, as requested, and prioritise or explicitly revisit detected dirty regions. Return home after verification and wait for genuinely new contamination. No endless loop.
- Newly falling dirt during cleaning updates the estimated map and queues revisits. Bound retries and mission time; persistent replenishment or undetectable/uncleanable material yields INCOMPLETE rather than an infinite run.

Trigger thresholds are configurable and visible in the evidence; "do not move for too little dirt" and "remove dirt wherever it exists once triggered" are separate requirements. The demonstration will show both a subthreshold idle case and an above-threshold cleaning case.

## 8. Phase E — routing that guarantees the planned glass sweep

Use complete coverage planning with measured tool footprints, not a fixed centre-only route. Combine overlapping interior lanes with explicit boundary-strip and corner passes using the edge tool. Compute overlap from effective cleaning width and validated pose/tracking uncertainty, not the brush's decorative width.

Before execution, rasterise the swept tool footprint against every glass cell and reject a plan with holes. Check supported chassis trajectories and arm collision/stability continuously along transitions. Include safe approach, turn, retreat and return-home segments. Never assume that the planner's geometric pass means actual contact occurred.

During execution, maintain three separate maps: camera-estimated contamination/unknown, physically qualified cleaning dose, and independent hidden evaluation truth. Track actual progress; missed-contact cells get replanned. Camera-detected patches get targeted revisits even when nominal coverage says they were visited. If cameras see a clean surface but actual physical coverage is incomplete, the full-sweep requirement still fails.

The completion condition includes actual full-surface passage, visually verified residual thresholds, valid observations, no unresolved targets and safe return/settling. Homing must check pose, orientation and translation/rotation/brush speeds over a settling window, not just arrival at a waypoint. Home is a physical repeatable place, not a runtime robot teleport.

## 9. Phase F — test gates before the final clip

| Case | Required evidence |
|---|---|
| Clean panel, long idle | No spontaneous departure, no sliding, no rotating brush |
| Small/subthreshold debris | Persistent mapped detection if visible; stays home until trigger criterion is met |
| Central significant patch | Camera-based trigger, targeted pass, full-surface sweep, verification, settled home |
| Four edges and four corners | Each individual worst-case patch removed; 100% glass-grid sweep; no cropped denominator |
| Multiple separated patches | All local targets cleared, no target silently dropped |
| Deliberately interrupted brush contact | Dirt remains where contact/dose was absent; retry or INCOMPLETE |
| Dirt added during mission | New target queued and re-verified before success |
| Shadows/lighting change, clean glass | No unsupported dirt trigger; uncertainty tracked |
| Camera occlusion/dropout | Unknown/stale observations detected; safe response; no false clean |
| Jam or excessive brush load | Bounded response and honest outcome |
| Low friction/unsafe incline | Physically justified braking/holding or explicit failure, never frozen state |
| Timeout and unreachable target | INCOMPLETE with remaining dirty/unknown cells reported |
| Repeated seed and timestep test | Consistent qualitative outcome, quantified numerical differences |

Develop on pilot seeds first. Freeze scene parameters, detector/trigger thresholds, supported debris class, controller/mechanism versions, scenario distribution and success metrics before held-out runs. Then run at least 30 full missions per compared controller/condition where a statistical comparison is claimed, retaining failures. Do not reuse the old 30-second benchmark or tune on held-out failures. Use run-level statistics and coverage/residual maps rather than treating video frames as independent trials.

Log image timestamps/camera IDs, detections, confidence/uncertainty, event reasons, estimated pose and scoring pose separately, initial/deposited/residual soil, physical contact/load/brush speed, full-cell coverage, actuator effort, state transitions, faults and docking. Hash code/model/config/scenario at launch. Measure rendering and storage cost before large batches; save selected camera frames and full detection logs rather than every high-resolution image indefinitely.

## 10. Final simulation storyboard

1. Show the entire panel and home station, with robot stationary and brush off. Overlay HOME_MONITOR and estimated dirty area.
2. Show a small subthreshold deposit and no launch, then a clearly visible significant fall onto the panel including an edge/corner patch.
3. Briefly show the actual edge/robot camera feed, detection outline, confidence and mapped panel location. Trigger is traceable to image evidence.
4. Robot leaves home physically, cleans significant patches and performs overlapping full-panel coverage. Brush rotation is visible through a striped texture or lightweight noncolliding bristle visuals matching the real actuated brush.
5. Show close views of dirt fading only under qualified tool contact, plus edge/corner tool operation. The coverage overlay must show measured progress, not a preprogrammed 100% animation.
6. Show residual checks and any required revisit. Finish with full-domain scoring and a camera verification map, including previously occluded home cells.
7. Robot returns home, stops the brush, settles and stays there. Overlay actual outcome and remaining-dirt count. Any accelerated playback is labelled; do not fabricate a successful run with edits.

Record a complete successful trace after validation, with raw evidence preserved. Also retain an honest fault clip. The required human team presentation remains a separate deliverable.

## 11. Aesthetics: deferred and isolated

Once behaviour gates pass, add a balcony/rooftop, sky/sun lighting, clouds and contextual buildings. MuJoCo supports cameras, lights, textures, skyboxes and mesh visuals; an entire city is optional and may be imported or rendered with an external visual workflow. Background geometry should normally be noncolliding unless intentionally part of the physical environment. Keep simulation/sensor and presentation camera roles explicit; scenery changes that affect sensor lighting require perception regression checks.

Begin with primitives or freely licensed assets if sufficient. Ask the user for models only if a specific visual requirement cannot be met efficiently. Check licence, units, orientation, mesh complexity and file format support before importing; convert unsupported scene formats through a documented asset pipeline. No asset hunt is a prerequisite for mechanics or cameras. A polished scene must not hide missed dirt or substitute for physical validation.

## 12. Planned files and work order

Existing model/controller/planning/safety modules will be extended only after this planning checkpoint. Add modules with clear boundaries, provisionally:

- `src/debris.py`: physical deposition events, surface field and visual representation.
- `src/vision.py`: RGB processing, calibration/projection, confidence and camera fusion.
- `src/coverage_planner.py`: full-glass interior/boundary/corner paths and hole checks.
- `src/mission_manager.py`: idle/trigger/task/retry/verify/home lifecycle.
- `src/contact_cleaning.py`: local contact/dose updates and independent physical coverage.
- `src/localisation.py`: explicit image/encoder/IMU navigation estimate.
- `src/evaluation.py`: isolated truth scoring, manifests and completion checks.
- `tests/`: geometry/reach, debris persistence, image detections, triggers, contact cleaning, complete missions, edge/corner cases and faults.

Keep existing historical telemetry and models reproducible through commits; do not relabel old outcomes as results of the new architecture. Push reviewable milestones after (A) mechanics/reach, (B) visible deposition/contact removal, (C–D) camera detection and idle trigger, (E) integrated routing/verification/home, and (F) held-out evidence. Update CONTINUE_HERE at each milestone.

The first next action after this plan is approved for execution is a mechanical reach/stability prototype and camera/debris rendering feasibility check—not background modelling or a final statistical batch. No secret/API key or neural-model service is currently needed. Major geometry choices remain conditional on the first physical gate. If a required gate fails, report its measured failure and revise the design rather than weakening the completion definition.
