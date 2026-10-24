# Evaluation protocol — draft, not final results

The current robot is a four-roller skid-steer approximation with a rigid rotary brush. It uses MuJoCo ground truth for control and evaluation. No sensor-based localisation claim is made.

## Primary question

Does segment-lookahead path tracking with wheel-speed integral control reduce run-level geometric path-tracking RMSE relative to waypoint pursuit with proportional wheel-speed control, on the same mechanically feasible bidirectional route?

Freeze controller/model/config hashes before evaluation. Pilot seeds 0–9 are excluded. Evaluate 30 independent runs per controller (aim 50 if time permits), using disjoint seed sets 1000–1029 and 2000–2029. Initial x/y perturbations uniform ±0.01 m are the currently implemented source of variation. This is a narrow repeatability study, not broad robustness validation. Add independently justified friction/mass/sensor scenarios before claiming robustness to those quantities.

Use identical robot, route, limits and safety criteria for both controllers. Declare gain differences before running. Primary endpoint: per-run geometric path RMSE over each full run. Also report mission completion and conditional-on-completion duration, contact coverage, force peaks, control effort and mechanical work. Runs ending early must not be silently excluded or given favourable interpretation due to short duration.

Compare independent run metrics with two-sided Welch's t-test, report df, exact p, mean difference and Welch t-based 95% CI. Report pooled-SD Cohen's d with its definition; distinguish it from Welch's unequal-variance test. Never treat 500 Hz rows as independent trials. No guaranteed significance or effect size.

## Spatial metrics

The panel is 6 m × 4 m. Whole-panel contact coverage remains the principal geometric denominator. A safe interior service region may be defined geometrically before final trials, but report its area and coverage separately and show the omitted border. Never relabel interior coverage as whole-panel coverage. Contact footprint and soil attenuation are reduced-order proxies. A qualifying cleaning update requires positive normal force above 0.1 N and brush angular speed above 1 rad/s. These are numerical activation thresholds, not coating-safety thresholds. The attenuation coefficient is uncalibrated and must undergo sensitivity analysis.

## Integrity

Store sample timestamps without rounding, 500 Hz CSV, seed, realised inputs, code/model/planner hashes captured at launch, explicit exit status and simulation duration. Keep terminal abort events separately. Do not mutate code/model during a batch. Protect existing outputs from overwrites. Failed/aborted development runs are retained and labelled.

No final evaluation batch has been run yet. This protocol needs actual load/slip telemetry, fault handling and frozen baseline implementation before execution.
