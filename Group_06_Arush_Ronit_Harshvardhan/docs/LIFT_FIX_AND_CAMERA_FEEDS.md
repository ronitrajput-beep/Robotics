# No-lift route and visible camera detections

## Current verified behaviour

The complete scattered headless scenario (`analytics/scattered_inward_pilot8`) reaches CLEAN_AND_HOME at 485.162 simulated seconds. All 32 rendered dirt patches are below the declared residual threshold, including the bottom-edge cluster. Maximum chassis tilt is 0.08954 degrees; the largest rise above the initial 0.120 m panel-normal height is 0.4828 mm. Full peak-to-peak normal-height variation is 0.6317 mm. These values come from all 242581 samples at 500 Hz, not selected video frames.

`independent_scattered_checks_v2.json` verifies deposition before the RGB trigger, idle before detection, actual bottom-edge request causality, no-lift bounds, every dirt patch below threshold, return-home settling and guard contacts confined to the requested edge task. Actual contact-footprint coverage is 89.03125% of all 24 m². This is slightly below the old exact 90% target; the flag remains false and the percentage is reported honestly. Moving turns inward trades a little footprint for stability. It is not 100% panel cleaning.

## What changed physically

The older footage near video 1:53 shows the lower-right corner. Old wall contacts could inherit wheel friction. New guards use priority 2, condim 1 and zero friction: they supply containment normal force, without tangential wheel/wall climbing friction. This alone did not eliminate all pitch on the old route, so row reversals now retreat straight inward before making shallow connectors.

The ordinary coverage rows stay inside the frame. A bottom-edge service is scheduled only from current RGB dirt targets below y=-1.65 m. Its approach first retreats horizontally at the current safe height, then passes the brush along the detected bottom cluster. The chassis does not need to climb the frame to extend the fixed brush over it. The successful test's guard contact occurs only at simulation t≈353.67–356.00 s, entirely inside the camera-requested bottom task. There is no ordinary wall-following tour on the other edges.

Return-home and revisit transits use shallow cross-slope zigzags instead of abrupt straight-uphill pivots. RETURN_HOME disables the powered cleaning command; passive brush rolling under contact can still occur. Steeper headings have a conservative speed/turn envelope and a separate wheel regulator with target/torque slew and conditional integration. The previously stable cross-slope regulator is retained for ordinary raster motion. No robot position, velocity or attitude is clamped. A gross attitude fault aborts the run, and a stricter independent no-lift gate prevents a tipped but dirt-cleared run being reported as success.

Development variants which stalled, tipped or exceeded the no-lift gate are retained with source snapshots and run notes. In particular, earlier scattered pilots 3/4/7 cleared dirt but were rejected as unsafe. Do not treat their earlier camera-clean label as a physical success. Successful proof comes from pilot8 and the independently checked replacement recording, not from changing a scoring threshold.

## Less uniform dirt, including the bottom edge

The seeded scattered scenario uses eight representative falling grains and a logged hybrid deposition rule that creates 32 surface-layer spots. Positions, radius, elliptical aspect, orientation and shade vary. These are visible dust-layer proxies, not resolved microscopic particles. Overlapping patches may appear as a single image region, so the RGB region count need not equal the underlying patch count.

Residuals retain a minimum displayed radius until they pass the explicit 0.1 residual threshold. This is a declared visual-resolution assumption: dirt must not become invisible to the detector merely because its drawn mark shrinks below a few pixels. Regression checks verify a small dark bottom-edge residual at 0.101 remains detected in both fixed camera views. Local measured brush contact/load/speed still controls removal; detection alone cannot remove dirt.

## Actual camera feeds in the recording

The cinematic sidebar displays the exact RGB arrays passed to detect_dirt from the left panel camera, right panel camera and onboard camera. Each view shows its actual acquisition timestamp (2 Hz) and image-derived green bounding boxes. Rendering annotations copies the arrays and does not modify detector input. The dirt trigger and target positions derive from those RGB observations; navigation remains simulator-pose feedback.

The onboard camera also had a near-clipping defect: parked inactive particles at 100 m enlarged automatic scene bounds. Explicit visible-rack statistics now put its near plane at 0.06 m, allowing it to see nearby glass and the brush. Actual rendered regression tests check this, not just a configuration value. Rooftop scenery stays presentation-only; validated sensor RGB appearance is preserved.

## Evidence and commands

- `docs/validation/no_lift_validation.png`: full-run tilt, normal-height change and guard force, with the authorised bottom task shaded.
- `docs/validation/raw_camera_before_after.png`: actual sensor RGB before/after cleaning.
- `docs/validation/onboard_camera_bounds_fixed.png`: corrected onboard view.
- `analytics/scattered_inward_pilot8/independent_scattered_checks_v2.json`: independent assertions and actual coverage.
- Clean and subthreshold scenarios in `analytics/no_lift_*_check` stay home for 12 seconds; the single subthreshold deposit persists.

From the group folder in the pinned environment, use new output paths:

```
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python src/vision_mission.py --scenario scattered --cinematic --duration 1100 --output-dir analytics/NEW_SCATTERED_RUN
python src/verify_scattered_run.py analytics/NEW_SCATTERED_RUN
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python -m unittest discover -s tests
```

The current suite passes 42 tests. These are nominal development checks, not hardware certification, a full statistical evaluation or unrestricted fault robustness. The replacement recording must independently pass before it is described as completed.
