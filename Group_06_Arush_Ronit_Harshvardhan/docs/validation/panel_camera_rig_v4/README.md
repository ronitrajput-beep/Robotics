# Finished camera hardware tour

`panel_camera_tour.mp4`: 20 seconds, 1280×720 H.264 at 25 fps, 500 decoded frames, actual stepping at 1×.

The panel cameras now have visible housings, lenses, status LEDs, cables, mounting arms and frame-supported overhead posts. Their positions/optical axes correspond to the unchanged `edge_left` and `edge_right` sensor feeds. The tour also inspects the onboard camera and displays all three actual RGB detector inputs.

This is an intentionally short equipment preview. The saved mission status is INCOMPLETE/TIMEOUT because the 20-second horizon precedes the full cleaning cycle, not because the visual change failed. The complete validated cycle remains in collection_demo_v6.

`camera_rig_checks.json` verifies unchanged model/controller hashes, exact telemetry prefix, identical camera observations and 27 identical saved RGB inputs against full-run pilot8. All 49 tests and the final presentation-isolation test pass. Source snapshots and decode evidence are retained. The fixtures are presentation geometry; mounts/structural loads are not physically validated hardware.
