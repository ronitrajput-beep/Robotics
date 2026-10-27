# Complete camera-hardware and cleaning recording

Fresh actual-physics combined mission: CLEAN_AND_HOME at 610.858 simulated seconds. Raw movie cinematic_cleaning.mp4 is 189.52 s (4738 frames, 1280x720/25fps). It includes both panel inspection rigs and the onboard camera in explicit close-ups at t=8..25 simulated seconds, with the three true RGB detector inputs visible throughout the mission. Longer traversals are labelled 12x; initial deposition, camera inspection, brush inspection, physical solid contact/tray landing and dock service are 1x. Final measured result is held for three seconds.

Independent collection checks pass. Actual telemetry, surface/bin/station mass accounting, rigid-solid logs and camera observation streams match validated headless collection_pilot8 exactly after lossless decompression. All captured frame indices map to actual simulation times in frame_map.csv. Executed source snapshots and model hashes match launch_manifest.json. This is new integration/rendering, not robot-pose replay or a splice of an unrelated camera tour.

All 32 selected dirt patches are below the defined residual threshold; whole-panel qualifying contact footprint is 89.97917% and the exact-90 flag stays false. The 120 g rigid object is physically retained in the permanent tray. Dust capture and dock service remain reduced-order models, guards provide containment and navigation uses simulator pose. General visual dirt recognition, arbitrary solid planning, real adhesion/traction, coating safety and vacuum/charging hardware remain unvalidated.

The shareable cut is submission/complete_camera_video_v1/Group06_Complete_Simulation_With_Cameras.mp4: 201.52 s / 5038 decoded frames, with a clearly labelled additional 12-second business-scenario card. It is silent for your own narration. The paired Word/PDF/text/Markdown script gives Arush the model/code/simulation explanation, Ronit model refinement and business support, and Harshvardhan economics, based on the roles supplied by the user. Economic inputs remain labelled assumptions and no measured PV yield uplift is claimed.

Reproduce using a NEW directory:

    MUJOCO_GL=egl python src/record_complete_camera_demo.py --output-dir docs/validation/NEW_CAMERA_RUN
    python src/verify_collection_run.py docs/validation/NEW_CAMERA_RUN
    python submission/finish_camera_video.py --run-dir docs/validation/NEW_CAMERA_RUN --output-dir submission/NEW_CAMERA_VIDEO

Presentation-only controls are separate from sensing and physics. Earlier videos and datasets are preserved. The short analytics/camera_complete_preview_v1 run is an intentionally incomplete camera/framing preview, excluded from full-cycle evidence.
