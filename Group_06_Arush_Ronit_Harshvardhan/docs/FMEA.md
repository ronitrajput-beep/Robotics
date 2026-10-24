# FMEA draft — engineering judgement, not field reliability evidence

Scores must be reviewed by the team. S, O, D use 1–10 ordinal scales; RPN = S × O × D. A lower detection score means easier detection. Severity is unchanged by software detection alone.

| Failure | Effect | S/O/D before | RPN | Existing mitigation/evidence | Post-mitigation status |
|---|---|---|---|---|---|
| Traction loss on incline | Drift and possible fall | 9/5/7 | 315 | Bidirectional shallow turns; geometry boundary abort; development logs | No post-score claimed until low-friction fault trials |
| Edge approach | Loss of support | 10/4/6 | 240 | Conservative whole-body radius; observed edge abort in old planner | Predictive braking and persistent abort dynamics still required |
| Brush overload/coating damage | Module damage and downtime | 8/4/8 | 256 | Torque bounds and measured contact-force logging | No coating safety model; force limit alone does not prove no scratches |
| Brush contact loss | Incomplete cleaning | 5/6/7 | 210 | Contact-force/rotation gate prevents unsupported cleaning increments | Contact efficacy and recovery remain under development |
| Invalid/stale sensor state | Incorrect actuation | 9/3/8 | 216 | Finite-state/solver warning checks | Uses ground truth; dropout/watchdog fault tests required |
| Logging failure | Missing reproducibility evidence | 6/3/5 | 90 | Exceptions propagate; no fabricated replacement data | Atomic manifest/failure handling required |

Do not fill optimistic post-mitigation RPNs without evidence. Inspection, tethering and real glass/load qualification remain hardware deployment considerations outside this simulation's demonstrated capability.

## New evidence

Pose validity failure and dissipative brush-jam injections now trigger latched active braking, with measured settling in the seed-0 runs. Severe friction loss still exits the support envelope. See SAFETY_VALIDATION.md and raw logs. These observations support improved detection, but one run per fault does not estimate occurrence probability; no numerical post-mitigation RPN has been invented.
