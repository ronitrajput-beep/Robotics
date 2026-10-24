# Current implementation status

The mission is still under development. Do not submit current development figures as final evaluation.

## Changes after initial handoff

- Added a panel-frame raster and projected segment lookahead in src/planning.py.
- Replaced waypoint-distance RMS with distance to the active reference segment. This is geometric path-tracking error, not time-indexed trajectory error.
- Boundary check now encloses the full robot in a conservative 0.45 m radius. This checks present clearance; predictive braking margins remain unfinished.
- Initial pose moved to upper-left before stepping, then raster proceeds downhill. Initial placement is not a runtime teleport.
- First revised low-edge approach aborted at 10.95 s. It demonstrated why turning at a low edge is unsafe. The later upper-left plan is being validated.
- Added controller and planner content hashes to result metadata.
- Economics now computes ratios, payback, reclaimed labour and M/M/1 queue delay. Defaults are explicitly assumptions, not experimentally validated inputs. Nonpositive savings and unstable queues return null instead of fabricated finite benefits.
- Four automated tests pass: path projection, footprint clearance, economic edge cases, repeated seed/500 Hz integration.

## Remaining engineering risks

Current post-step CSV mixes pre-step position/reference with post-step actuator/contact fields. Align state sampling before final data generation. Controller integral resets/anti-windup need proper conditional integration. Brush dose is an uncalibrated time-only proxy; measure normal force and actual speed before claiming adaptive cleaning. Full docking, predictive edge braking, safe-stop dynamics, faults, baseline comparisons and Monte Carlo analysis remain unfinished. Runtime ground truth is used directly and must be disclosed. The rigid panel cannot establish glass deflection or scratch prevention.

The scripts use real physics, but these limitations prevent final readiness claims.

## Turn-dynamics resolution

The retained planner alternates forward/reverse sweeps, connecting rows diagonally 0.65 m inward. This avoids 180-degree skid pivots. Seeds 0, 1 and 2 all completed 16 waypoints with the rigid brush, approximately 244 s and 0.044 m geometric path RMSE. Seed 0 conservative footprint clearance stayed above 0.2028 m. Its 122001 logged rows have spacing 0.002 s to floating-point tolerance. Results: analytics/reverse_sweep_real_trials.* and docs/validation/route_seed_checks.json. These are developmental seeds, not final Monte Carlo evidence.

Telemetry now samples pre-step pose/reference/contact/actuation at a consistent time. Content hashes are captured at launch rather than completion. Earlier two seed manifests and the brush experiment required explicit provenance corrections because source/model edits occurred while those runs were in progress. The corrected manifests record that fact. Do not edit model/controller during future batches.

A spring-mounted brush experiment completed but reduced brush-contact duty from roughly 34% to 16% and was rejected. Evidence retained in analytics/compliant_brush_real_trials.*. The original rigid brush geometry and 8.5 kg mass budget are restored; serialization changed the model file hash without changing its mechanics. The full physics validation and all four automated tests pass after restoration. Rendering succeeded through EGL at 640x480, inspected in docs/validation/physics_view.png; interactive viewer is not yet verified.

Remaining: normal-load/contact analysis, cleaning-dose calibration, complete coverage definition, predictive braking/fault handling, baseline/proposed trials, economics input sourcing, final figures and dossier. No need for another model switch solely because a milestone completed.

## Workspace recovery, coverage audit and route pilots

The newest checkpoint is in `CONTINUE_HERE.md` (25 October 2026) and detailed in `CONTACT_COVERAGE.md`. 18 tests and physics checks pass. Optional `expanded_safe_return` completes and settles on three development seeds with 61.3–61.7% whole-panel qualifying projected coverage. Failed ~64% lower-edge pilots and all severe traction-loss failures are retained. New maps distinguish footprint, contact and dose; no complete-cleaning claim is supported. Synthetic figure generation and unsupported starter manuscript claims have been replaced with real-data analysis and an evidence draft. Sources, calibration, final full-mission evaluation and human submission requirements remain incomplete.
