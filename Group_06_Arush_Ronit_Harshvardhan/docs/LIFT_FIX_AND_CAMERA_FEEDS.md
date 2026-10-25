# Corner lift, edge-pass policy and visible RGB feeds

The prior rooftop video at approximately 1:53 shows the lower-right corner near simulation t=373.8 s. The old guard geometry inherited wheel contact friction via MuJoCo mixing and the old planner initiated row changes beside the wall. New diagnostics log normal chassis height, chassis tilt and guard forces at 500 Hz. Contact guards now have priority 2, condim 1 and zero friction: they provide containment normal force without wheel/guard tangential climbing friction. Robot pose is never clamped.

Frictionless contact alone is not a complete remedy: diagnostic runs on the old route still showed tilts of several degrees. The new optional inward_turns route reverses straight inward before making a shallow row connector, and keeps ordinary rows clear of the perimeter. The first scattered pilot completes with maximum tilt 0.1243 degrees, maximum height 0.120483 m (initial normal height 0.120 m) and zero guard impulse. This is the relevant no-lift result, not an assumption based on guard coefficients.

Ordinary coverage no longer intentionally rides a wall. A dedicated bottom-edge cleaning route is scheduled only from current RGB targets below panel y=-1.65 m. VISION_EDGE_SERVICE records the observed targets. Actual edge cleaning uses the EDGE_CLEAN_BOTTOM state and is displayed as vision-requested in the recording. No all-four-edge wall-following animation is added.

The scattered scenario adds irregular, seeded deposition clusters across the panel and a lower-edge deposit. The first pilot has 24 underlying patches. Its ordinary contact coverage is 89.1875%, and it ends VERIFICATION_MISS: four residual patches remained while camera estimates became clean as the rendered spots shrank below detection resolution. That failed pilot is retained. Follow-up changes must preserve detectable residual visuals and require successful camera reinspection before claiming completion.

The cinematic layout now shows raw edge_left, edge_right and robot_camera RGB inputs, their actual acquisition timestamps (2 Hz), and image-derived green bounding boxes. These are the same arrays passed to detect_dirt, not a second illustrative camera simulation. Presentation drawing copies the RGB arrays and does not modify detector inputs. Unit tests check the overlay and preservation of the source pixels.

The first checkpoint passes 36 tests. The full new recording and successful scattered cleaning remain to be validated at this point.
