# Visible panel inspection cameras

Two visible camera units now correspond to `edge_left` and `edge_right`. Each has a housing, sun hood, black bezel, blue lens, status LED, mounting arm, cable, roof-supported post and brace to the panel frame. The existing onboard camera stays visible.

The housings follow the actual sensor positions and orientation matrices. The panel sensors retain their calibrated panel-local positions (-2.7, 0, 5) m and (2.7, 0, 5) m, 70° vertical field of view and optical direction normal toward the glass. They are elevated overhead inspection cameras. Their mounting arrangement is a visual representation; structural and wind-load engineering are not validated. No camera calibration, robot dynamics, collision geometry or controller settings changed.

Watch `validation/panel_camera_rig_v4/panel_camera_tour.mp4` for the 20-second equipment tour: whole installation, left camera, right camera, onboard camera and live detector feeds. It records actual stepping at 1×. Its deliberately short horizon ends before the cleaning mission completes; the previous complete collection recording remains in `validation/collection_demo_v6`.

Checks: all 49 tests pass; a final presentation-isolation check also passes. The tour's model/controller hashes, telemetry prefix, camera observations and all 27 saved detector RGB images match the corresponding part of validated full-run pilot8 exactly. All 500 video frames decode. Presentation fixtures do not enter the controlled sensor render, matching the existing approach used for the robot camera housing and rooftop scenery.

Reproduce with a fresh output directory:

```sh
MUJOCO_GL=egl python src/record_panel_cameras.py --output-dir docs/validation/NEW_CAMERA_TOUR
```

Earlier visual drafts v1–v3 are retained with notes; v4 is the finished preview. The shared `RooftopScene` includes these camera rigs in future cinematic renders.
