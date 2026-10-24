# Settled endpoint docking

The planner's final waypoint is (0, -1) m in panel coordinates. On reaching within 0.10 m, the controller enters DOCKING, turns off the brush and commands zero roller speed through the existing bounded drive regulators. It continues physics integration; it does not overwrite pose or velocity.

Completion requires all of the following continuously for 0.5 s:

- Planar chassis speed below 0.02 m/s.
- Chassis angular-speed magnitude below 0.05 rad/s.
- Brush speed magnitude below 1 rad/s.

After settling, endpoint error must be at most 0.12 m. Outcome is DOCKED only when both conditions hold. Otherwise outcomes include ABORT_DOCK_POSITION, ABORT_UNSTOPPED (3 s settling timeout), or ABORT_EDGE. The same angular/brush criteria strengthen fault-stop validation.

This is simulated endpoint settling. There is no charging connector, mechanical dock latch, physical brake or hardware docking sensor. DOCKED does not certify full cleaning or passive stability after motor power removal.

The 60-run initial-sweep study predates docking/supervisor changes and retains its original hashes; it should not be relabelled as validation of the new final controller.
