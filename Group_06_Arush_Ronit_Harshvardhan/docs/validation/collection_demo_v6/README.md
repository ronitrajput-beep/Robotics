# Completed combined simulation

`cinematic_cleaning.mp4`: 3:20.40, H.264 1280×720 at 25 fps. All 5010 frames decode. This is fresh integrated physics, not a pose replay; telemetry and physical/dirt/solid/collection outcomes match headless pilot8 exactly.

`solid_contact_slow_motion.mp4`: 15.96 s, labelled 0.25× replay of four seconds from the same recording, showing fixed-guide contact and tray landing. It creates no new physical motion. Its 399 frames decode without errors.

The robot starts entirely off glass on the attached upper-left platform, detects RGB contamination, clears all 32 selected dirt spots below threshold, physically guides a persistent 120 g block into the permanent lower tray, returns off glass and settles. The dock then empties the modelled onboard bin and adds modelled charge energy. A fixed guide is used because fine-dust suction cannot ingest this block. Brush support arms and the intake/bin are visible.

Maximum chassis rise .408684 mm and tilt .093728 degrees pass the unchanged limits. Whole-panel qualifying footprint is 89.97917%; exact-90 is false. Grain/soil/bin/station mass balances, with 4.000 g deposited, 3.98564 g station inventory, 0.01436 g residual soil and zero onboard inventory. This is reduced-order fine-dust capture and service accounting, not solved suction airflow or battery/connector validation. Block motion/ejection/retention use actual rigid-body contact. General object planning, structural strength and scratch safety are unvalidated.

`independent_collection_checks.json`, `headless_recording_comparison.json`, `video_decode_check.json`, trajectory/inventory CSVs, source snapshots and plots retain the evidence. `metadata_annotations.json` explains two descriptive metadata corrections and the legacy solid-force column name; original metadata is preserved. All physical measurements and outcome fields are unchanged.
