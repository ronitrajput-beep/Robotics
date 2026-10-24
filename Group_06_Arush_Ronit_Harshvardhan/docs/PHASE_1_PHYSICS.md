# Phase 1 physical model

Validated with Python 3.12 and MuJoCo 3.17.0. Run from this group directory:

```
python src/test_env.py
python src/validate_physics.py
```

## Mechanism and repair

The supplied model failed with `unrecognized attribute: body` on motor line 62. Official MuJoCo XML reference specifies joint transmissions for these motors and restricts free joints to children of worldbody. The crawler is now a world child with its initial pose transformed from the inclined panel frame. Four hinge-driven cylinders provide contact propulsion, two per side. These are a skid-steer roller approximation of tracks, not resolved continuous belts. No state is overwritten during validation; controls are bounded joint torques.

Official reference consulted: https://github.com/google-deepmind/mujoco/blob/main/doc/XMLreference.rst (body/joint and actuator/motor sections). The documentation website returned HTTP 403; the official source was accessible. Installed-engine compilation independently verifies accepted syntax.

Robot mass is 8.5 kg: chassis 5.3, four rollers 0.5 each, brush 1.2. Compiled initial CoM in chassis coordinates is (0.040941, 0, -0.015059) metres. This is not height above glass. Roller radius is 0.06 m. Brush radius is 0.06 m, full width 0.55 m, and its cylinder and hinge axes both lie along local Y. Rollers use isotropic sliding friction 1.2; these values are modelling assumptions, not measured rubber/glass properties. Effective contact friction depends on MuJoCo mixing rules. The timestep is 0.002 s with implicitfast integration.

Drive torque commands and output forces are limited to ±3 N m per roller. Brush velocity command is limited to ±100 rad/s, output torque to ±1 N m. A 900 RPM request does NOT imply 900 RPM achieved: the loaded brush reaches only about 9.36 rad/s in the three-second test. Damping/contact and torque saturation limit speed. Speed/load tuning belongs to the next control phase.

## Validation and limits

The deterministic validation script runs four independent seven-second simulations: one second settling followed by six seconds holding or driving on the 20-degree rack. Its test-only proportional wheel-speed regulator commands physical motor torques. Stationary holding is active, not an unpowered brake. Assertions check finite state, solver warnings, displacement direction, turning and actuator bounds. Additional checks verify mass, CoM, axis and brush rotation. Actual outputs are in validation/phase1_results.json.

Forward travel is approximately 0.986 m; reverse -0.981 m. Active stationary drift is about 3.7 mm. Turning changes heading about 1.15 rad but drifts downhill about 0.292 m. This is basic mobility validation, not successful path following or a safety guarantee. The smoke test still has its original fallback behaviour; the new validation script always loads the exact model and fails if missing.

The panel is rigid; glass deformation, coating damage, real cleaning, continuous belts, bumper coverage, edge safety, complete missions and visual rendering are not validated here. Existing mission controller and synthetic benchmark generator remain starter scaffolds. No experiment-result claims should be derived from them.

## Viva explanation

Motor torque rotates the roller hinges. Contact friction transfers tangential force to the rack and moves the free chassis. Equal signed speeds give translation; opposite signed speeds generate yaw with skid. Gravity and contact are integrated by MuJoCo. Moving the free body into worldbody fixes its kinematic hierarchy; converting the initial pose preserves rack-relative placement. Limits expose inadequate brush torque honestly instead of forcing desired motion.
