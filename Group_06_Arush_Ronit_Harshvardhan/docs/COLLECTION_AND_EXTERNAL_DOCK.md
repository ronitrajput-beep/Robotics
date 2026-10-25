# Collection and external dock prototype

The new `combined` scenario uses `models/collection_cleaning_crawler.xml`, preserving the previous guarded model and recordings. It adds a coplanar platform outside the upper-left glass edge. The robot's home centre is (-3.65, 1.53) m in panel coordinates; its entire chassis and fixed brush fit off the glass. Real roller contact supports it on the platform. An opening replaces the left guard/trim at the entrance. Transparent normal-only guards still provide containment; there are no pose clamps.

The fixed rotary brush has two visible support arms, cross mounts, an intake slot, a duct, an onboard bin and blower housing. These structural representations share the existing 8.5 kg rigid-body mass budget and are noncolliding. Their structural strength, attachment loads, seals and manufacture have not been validated. The robot is not fitted with a telescoping brush.

## Where dirt goes

The intended architecture is **brush-assisted vacuum collection**: the brush loosens/sweeps fine material toward the intake, a blower draws it into a filtered onboard bin, and the station empties the bin. This is a proposed hardware architecture, not proof that the current physical brush geometry or suction system will work on hardware.

The simulation implements an explicit reduced-order capture model rather than resolved airflow. Existing contact/load/speed/gap conditions reduce each soil patch. The removed mass enters the onboard bin in the same timestep. Patch area × an assumed 20 g/m² sets initial mass; the remaining soil, onboard bin and station waste must balance at every sample. Below the 10% residual display threshold, some soil remains in the mass balance even though its patch is no longer drawn.

The blower consumes an assumed 20 W during cleaning states. After a settled final return, an eight-second dock service transfers material at up to 2 g/s into the station waste cartridge and credits 30 W of charging energy. These are assumed rates, not a battery, airflow, electrical connector or self-emptying mechanism validation. Charging adds energy; it does not claim a fully recharged battery. A service hose/contacts and bin cutaway are presentation representations. Their animation does not control perception or physics.

A suitable explanation is: “The design uses a brush to feed fine dust into a vacuum intake and filtered onboard bin. The dock is intended to recharge and empty the bin. This simulation models dust capture and service with explicit mass and energy accounting; it does not resolve suction airflow.”

## Larger objects

A permanent lower catch tray, floor and retaining lips exist from the start in the physical model. A 70 × 70 × 50 mm, 120 g wood-like block is released with the fine grains. After release it remains a dynamic rigid body: no removal, teleport, kinematic attachment or conversion into a dust patch. Brush contact and gravity must move it off the glass and leave it retained in the tray.

The controlled scenario places this block in the bottom-row handling corridor. A predefined reverse-brush bottom row accompanies the dust sweep. RGB contamination triggers departure and supplies residual targets, while navigation still uses simulator pose. There is no arbitrary solid classification, dedicated object planner, scratch model or demonstrated glass-safe contact load. Peak block contact force is measured and must be reported, including an unsafe/high result. A successful nominal demonstration is not hardware safety certification.

## Reproduce and inspect

Use Python 3.12 with the group requirements and ffmpeg. Set `MUJOCO_GL=egl` before Python imports MuJoCo in headless environments.

```sh
python src/build_collection_model.py
MUJOCO_GL=egl python src/vision_mission.py --scenario combined --duration 900 --output-dir analytics/new_collection_run
python src/verify_collection_run.py analytics/new_collection_run
MUJOCO_GL=egl python src/vision_mission.py --scenario combined --duration 900 --cinematic --output-dir docs/validation/new_collection_video
python src/verify_collection_run.py docs/validation/new_collection_video
```

Every output directory must be new. Telemetry, camera observations, source hashes, dust mass/energy accounting and persistent solid trajectory are saved. The independent validator checks RGB-triggered departure, external settled home, no-lift bounds, dust residuals, mass conservation, service-only transfer/charging, physical block contact/ejection/retention and continuous motion after release. It does not relax the existing 90% whole-panel footprint flag to make a run pass.

Pilot1 had prolonged entrance alignment and timed out with residual soil. Pilot2 removed the unnecessary entrance waypoint, cleared all 32 dust patches and completed dock service, but left the rigid block on glass. Both are rejected combined-collection runs. A subsequent controlled lower-strip handling diagnostic succeeded with measured contact, ejection and tray retention; its source/log are preserved. The combined scenario therefore declares a lower-strip block location and a reverse-brush bottom row. Arbitrary central-block collection remains unvalidated.

Pilot3 and recording draft v1 were interrupted after observing insufficient qualifying contact dose on new upper-left patches. The frozen replacement slows entry to 0.10 m/s and permits upper-left camera revisits via the new dock opening. Pilot4 cleared every dust patch and physically caught/retained the solid, but exceeded a 650 s horizon during return from one revisit. Recording draft v2 was superseded; v3 uses a 900 s horizon. None of these partial runs are a completed service cycle. The declared final solid release location is (-0.8, -1.78, 0.12) m in panel coordinates, at 3 s; gravity/contact determine its subsequent motion.

A later audit of pilot4 found 3.699 mm chassis rise as the passive brush crossed onto the higher-friction dock, failing the existing .123 m limit. A controlled return diagnostic isolated the friction mismatch. Dock friction now matches glass (.4 sliding, .005 torsional, .0001 rolling); quality thresholds are unchanged. Fresh full-run validation is required after this correction.
