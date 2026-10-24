# Evidence draft — simulated inclined-panel cleaning crawler

This replaces the starter manuscript's unsupported claims. It is a working evidence outline, not a completed four-page submission. Team members must review the Word dossier, confirm identities/contributions and complete their own signatures and video participation.

## Research question and scope

Retain the authorised question about an autonomous crawler recovering soiling-induced losses on inclined commercial solar arrays while reducing cleaning expenditure. The original question's **15–18% monthly loss** is an unverified contextual premise here, not a measurement from this project. No measured photovoltaic energy recovery or real-world cost saving has been established.

## System and methods

The 8.5 kg simulated robot operates on a 6 m × 4 m rigid panel at 20 degrees. Four torque-driven rollers approximate skid-steer tracks; they are not resolved continuous belts. MuJoCo integrates at 0.002 s. The brush is a rigid cylinder, with speed and torque limits. Neither panel bending nor coating damage is modelled.

The planner uses alternating forward/reverse sweeps with inward diagonal row connectors to avoid large pivot turns near edges. Ground-truth panel-frame pose feeds the controller directly. The proposed controller uses segment lookahead and wheel-speed integral feedback; the baseline uses waypoint pursuit and proportional wheel-speed feedback. This comparison does not isolate a slip-adaptation mechanism. A latched active-braking supervisor checks a conservative full-body envelope and measured settling; it is not a passive brake or certified safety system.

## Evidence that currently exists

### Initial-sweep tracking experiment

The retained independent groups contain 30 baseline seeds and 30 proposed seeds, each run for **30 seconds**, with initial-position perturbations of only ±0.01 m. All end TIMEOUT by protocol. They are not full cleaning missions.

Run-level mean geometric tracking RMSE was 0.116846 m (baseline) and 0.022748 m (proposed). Proposed minus baseline was −0.094098 m, Welch 95% CI [−0.094537, −0.093658] m. The saved analysis reports t=−432.778, df=40.534, p=6.62045×10⁻⁷⁶ and pooled-SD Cohen's d=−111.743. These extreme values reflect tiny variance in a narrowly perturbed deterministic simulation. They do not establish broad robustness, hardware performance, superiority over manual cleaning or whole-mission cleaning efficacy. Source: `analytics/tracking_benchmark/statistics.json`, protocol, summaries and raw per-run telemetry.

### Full-route development and contact audit

The retained standard seed-0 run completes all 16 waypoints and reaches settled DOCKED at 244.526 s, with 0.10096 m endpoint error and 0.00463 m/s terminal planar speed. The coverage audit reproduces those dynamics and records 122263 samples. Whole-panel qualifying projected footprint is 55.885% using the new area-weighted grid; legacy coverage is 55.167%. These are different discretisations, not evidence of improved control. Contact-force and projected-footprint assumptions are detailed in `CONTACT_COVERAGE.md`.

Whole-panel geometric coverage, qualifying contact, residual-soil proxy and mission outcome must be reported separately. New expanded-layout pilots, including stopped returns, are development experiments and must remain separate from held-out evaluation. Their individual manifests record outcomes; no failed run may be silently excluded.

### Fault evidence

The three-seed development matrix reproduces settled stops for pose dropout and brush jam. All three severe traction-loss cases cross the safe envelope and end ABORT_EDGE. This is an unresolved unsafe operating condition, not demonstrated fault recovery. See `SAFETY_VALIDATION.md` and `analytics/fault_matrix_v1`.

## Business analysis

The script computes dimensionless cost ratio, net cost reduction, labour reclaimed, payback, lifetime-normalised payback and M/M/1 queue delay. Nonpositive savings have no finite payback and unstable queues have no finite delay. All current cost and arrival/service inputs are assumptions. A recorded route duration cannot be treated as a whole-panel cleaning service time when coverage is partial. Demonstrate sensitivity rather than claiming a measured commercial return.

## Figures and provenance

Use actual telemetry via `analytics/generate_paper_figures.py --input <mission.csv.gz> --output <new.png>`, the tracking analysis, and the coverage audit. The figure generator now refuses starter synthetic benchmark data and never generates observations. Old images under `docs/figures` and `SIMULATED_solar_cleaning_benchmark.csv` are retained as explicitly excluded starter material, not scientific results.

## Unfinished requirements

Verify primary literature and standard applicability before adding citations or safety thresholds. Complete full-mission evaluation with predefined scenarios after engineering development, cleaning-dose calibration or explicit sensitivity, broader fault validation, desktop viewer rehearsal and sourced business inputs. Final dossier, team sign-off, signatures, 3–4 minute video, real post URL, peer review and individual Teams submissions remain outstanding. Do not assert completion or invent human actions.
