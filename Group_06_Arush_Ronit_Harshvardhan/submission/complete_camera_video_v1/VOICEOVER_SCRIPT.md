# Group 06 — voice-over for the complete camera simulation


Video length: **03:21** (201.52 seconds). The MP4 is silent so the three members can record their own voices. Intro/outro face clips are separate. For a five-minute final post, the combined face introduction and conclusion budget is approximately **98 seconds**.


Speak at the rates shown below; short pauses can follow the camera and solid-object close-ups. These are suggested project-contribution statements based on the team roles supplied by the user.


## 00:00–01:30 | Arush


174 words; approximately 116 words/minute.


My main contribution was the 3D robot model, controller coding and integration of this MuJoCo simulation.

These close-ups show both panel inspection cameras and the onboard camera at their calibrated sensor positions. Their actual RGB inputs appear on the right, with green detection boxes.

The robot begins at an external dock. Persistent dirt detections trigger its mission. I modelled mass, motor limits, rotating joints and collision geometry, then linked these to the controller.

I used a back-and-forth coverage route with proportional-integral wheel-speed control. Motor torques are bounded, and the safety supervisor monitors chassis height, tilt and stopping behaviour. Camera observations can request local slowdowns and targeted revisits when dirt remains. Position feedback currently comes from the simulator.

The brush is physically connected to the chassis. Fine-dirt patches shrink when the rotating brush makes qualifying contact, and removed mass is tracked through the onboard bin. This capture process is a reduced-order model; suction airflow is not resolved. The completed run clears all thirty-two selected patches below the threshold, with approximately ninety percent qualifying brush-contact coverage.


## 01:30–02:23 | Ronit


106 words; approximately 120 words/minute.


I helped refine the 3D model and contributed to the business modelling. The design connects an external docking platform, fixed brush supports, a solids guide and a permanent catch tray. Keeping the home platform off the glass also leaves that corner available for the cleaning route.

Here, the larger object is a persistent rigid body with mass and gravity. The diagonal guide physically redirects it off the glass into the tray through collision contact. This test uses a prescribed handling corridor.

The fixed mechanism keeps the concept relatively simple. I also helped connect practical operating requirements, including supervision, maintenance and panel-to-panel transfer, to the economic analysis.


## 02:23–03:21 | Harshvardhan


118 words; approximately 121 words/minute.


My focus was the business and economics of the product. I worked on capital and operating costs, labour requirements, payback and sensitivity analysis. The robot finishes its cycle by returning to the dock for modelled emptying and charging service.

The operating model uses measured simulation throughput, while commercial inputs remain declared assumptions. It includes human supervision, maintenance and manual transfer between separate panel sections.

Under this scenario, the model estimates about 38 percent normalised cost reduction, a 20.5-month simple payback and 57 person-hours reclaimed per month. These are scenario outputs, not measured commercial savings.

The final graph shows how the conclusion changes with supervision and other uncertain inputs. Prototype traction, coating safety and suction performance remain future tests.


## On-screen editing cues

- 00:00–00:08: home platform, falling dirt and the RGB trigger.

- 00:08–00:25: wide camera rigs, left camera, right camera and onboard camera close-ups; actual RGB inputs stay visible.

- 02:08: first physical guide/object contact; 02:11: object reaches the tray.

- 03:06: held measured cleaning result; 03:09: assumption-based business graph.

- Traversal acceleration is labelled in the footage. This is recorded fresh simulation, not a continuously live feed.

- Fine dust and dock service are reduced-order models; the larger block uses actual contact dynamics. Navigation uses simulator pose.
