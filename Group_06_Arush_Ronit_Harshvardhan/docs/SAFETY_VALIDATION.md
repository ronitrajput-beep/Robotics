# Safety supervisor: measured scope

The supervisor latches a stop reason, disables brush rotation and commands zero wheel speed using bounded active motor braking. It does not freeze positions or velocities. It continues MuJoCo stepping while braking. STOPPED requires measured planar speed <0.02 m/s for 0.5 s; this is a planar settling criterion, not a certified safety state or proof that orientation is fixed. If braking cannot settle within 3 s it reports ABORT_UNSTOPPED; crossing the current support-envelope boundary reports ABORT_EDGE sooner.

Predictive margin: 0.02 m + speed × 0.05 s + speed²/(2 × 0.30 m/s²). Deceleration and latency are design assumptions, not validated guarantees for every friction/tilt. The body is enclosed conservatively by a 0.45 m horizontal radius. These margins do not replace a tether or hardware brake.

Injected at simulation t≈3 s, seed 0:

| Fault | Implementation | Measured result |
|---|---|---|
| Pose dropout | Pose-validity flag invalid; ideal wheel-speed feedback remains | STOPPED at 3.544 s; terminal planar speed 0.00153 m/s |
| Brush jam | Brush hinge damping raised to 20 N m s/rad | Detected after sustained <1 rad/s during sweep; STOPPED at 4.038 s, terminal speed 0.00070 m/s |
| Traction loss | Sliding friction set to 0.05 on geoms | Braking triggered at 3.140 s; ABORT_EDGE at 4.370 s, terminal speed 3.982 m/s. Unsafe condition retained. |

Source data are analytics/pose_dropout_real_trials.csv, brush_jam_real_trials.csv and traction_loss_real_trials.csv with accompanying manifests. These are one-seed deterministic development checks, not probabilities of failure. The jam is a dissipative approximation, not a detailed seized-bearing model. The pose dropout is an injected validity failure, not a validated localisation stack.

Ground truth is still used for evaluation and the supervisor's clearance measurement. This architecture does not demonstrate safety with all sensors unavailable. No autonomous retry after latched faults is implemented; reset requires a new run.

CLI examples:
```
python src/crawler_cleaning_controller.py --fault pose_dropout --duration 10 --output analytics/new_dropout.csv
python src/crawler_cleaning_controller.py --fault brush_jam --duration 10 --output analytics/new_jam.csv
python src/crawler_cleaning_controller.py --fault traction_loss --duration 10 --output analytics/new_slip.csv
```
Existing output paths are refused so evidence cannot be silently overwritten.
