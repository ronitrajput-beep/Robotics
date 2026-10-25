# Presentation polish, edge dirt and solid-object tests

## Edge dirt: measured result, not inferred from body reach

The first explicit edge scenario deposited six representative grains near the perimeter. Four initial positions landed near the intended upper/lower/right edges; a top-left grain contacted the robot and eventually deposited farther down the left side. Score actual deposition coordinates, not intended spawn coordinates.

`analytics/edge_dirt_pilot0` exposed a detector failure: three patches remained while the camera estimate said clean. Its independent dirt score correctly failed. `run_note.json` labels the corrected interpretation VERIFICATION_MISS. Bright edge reflections pushed RGB values outside the old detector bounds. The detector now accepts a wider controlled brown brightness range; regression fixtures recover all six deposited patches in the captured sensor images.

`analytics/edge_dirt_pilot1` uses the corrected detector and bounded revisit geometry. It clears four of six patches, including the right-side target after a camera-directed revisit, then returns home with status INCOMPLETE. Two left-strip patches remain at approximately (−2.85, 0.424) and (−2.700, 1.144) m. The current fixed forward brush and bidirectional heading policy cannot reach that strip. UNREACHABLE_VISION_TARGET events preserve those observations. Do not equate chassis boundary contact with cleaning every boundary. Revisit approaches are clipped to supported centre coordinates so targets cannot lure the robot into an unreachable off-panel waypoint.

The orchestration report now separates camera_estimated_status from final status; a camera-clean estimate with a failed hidden residual check becomes VERIFICATION_MISS. Hidden truth is evaluation-only and does not steer the robot.

## Larger physical solid: visible motion, no deletion

The new `src/solid_object_demo.py` uses a 70 × 70 × 50 mm, 120 g wood-like rigid block initially inboard at x=0.8 m, with the robot at x=0.1 m. Reverse brush rotation and bounded drive torques make real contact. The block is never removed, faded or repositioned after initialisation. It moves across the surface, leaves the lower edge under contact/gravity and lands in an explicit lower catch tray.

`docs/validation/solid_object_demo_v1/solid_object_demo.mp4` shows 29 seconds of actual physics at 1× plus a two-second held summary, 1280×720 H.264, 775 frames. Sensor/control in this dedicated test is scripted, not camera-selected collection. It is separate from the autonomous fine-dirt mission.

Measured events: first brush contact 3.132 s; fully off glass 17.608 s; catch-tray contact 17.710 s. Peak brush-object normal force is about 283.8 N. This high load is an unresolved handling/surface-damage concern; rigid glass does not model scratches or cracking. Successful ejection is not evidence that this handling is safe for arbitrary solids. The clip displays peak force and this limitation. A lighter initial pilot used a 15 g block and lacked a lower tray; its original right-edge-only score was insufficient for detecting lower-edge ejection. Both pilots remain preserved.

## Rooftop presentation architecture

`src/cinematic_scene.py` adds a procedural rooftop deck, railings, panel supports, cell grid/busbars, building skyline, sky/sun/cloud geometry, home marker, metallic body details, sensor housing and small rotating brush details. These are presentation geoms only; they have no mass or collisions and are not used by the dirt detector. Camera viewpoints include an establishing view, deposition view, moving overview and close brush inspections. The result is a stylised procedural scene, not a photorealistic material/structural model.

Render-only framebuffer/shadow settings and model extent are restored before sensor rendering/physics. Tests compare actual sensor RGB before and after a studio render and assert identical model colours, camera/render settings, qpos and qvel. The sensor pipeline retains its validated controlled scene. This proves isolation, not perception robustness under the rooftop's new appearance.

Cinematic recording slows deposition and brush inspections to labelled 1×, using labelled 8× for long traversals. No robot poses are manufactured. Scene complexity was reduced after profiling; the interrupted first cinematic draft is labelled incomplete with source snapshots. The current cinematic_demo_v2 run is being completed and must be checked before publication claims.

## Commands

From the group directory in the pinned Python environment, use fresh output paths:

```
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python src/vision_mission.py --scenario edges --duration 650 --output-dir analytics/NEW_EDGE_TEST
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python src/vision_mission.py --scenario dirty --cinematic --duration 650 --output-dir analytics/NEW_CINEMATIC_RUN
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python src/record_solid_object.py --output-dir analytics/NEW_SOLID_VIDEO
MUJOCO_GL=egl XDG_CACHE_HOME=/workspace/.cache python -m unittest discover -s tests
```

Set MUJOCO_GL before Python imports MuJoCo in a headless environment. The renderer isolation test requires a working OpenGL backend; a late environment change during test discovery cannot initialise a backend already imported. The corrected headless suite passes 32 tests, including bright-edge fixtures, persistent physical solid ejection and sensor/physics presentation isolation.
