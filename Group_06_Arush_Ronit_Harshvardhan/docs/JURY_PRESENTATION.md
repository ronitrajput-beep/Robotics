# Group 06 — jury demonstration, 31 October 2026

From the supplied class briefing: Robotics Lab, 6th floor; readiness check 12:00–12:45; seated by 12:55; Group 06 ready by 1:40 pm, presentation 1:50–2:00pm. Recording Studio,8th floor, 2:02–2:05pm. Times are Mumbai local time; follow the queue caller.

Today's jury score is **2×A + 2×B + D =20**: real-world value/business/adoption8; technical build/evidence8; individual defence4. The dossier retains its ICA section structure. Every member must explain their own part and its connection to the whole.

## Four-minute pitch; no slides

| Time | Presenter / action | Evidence to show |
|---|---|---|
|0:00–0:30|Ronit: team, problem and customer—compatible commercial rooftop-PV bays and the cleaning operator.|Live model already open. Do not quote unsupported PV-yield percentages.|
|0:30–1:25|Arush: actual RGB-gated controller, physics, brush contact and route.|Live MuJoCo window; describe the current state and visible cleaning. Navigation uses simulator pose.|
|1:25–2:00|Ronit: robot/XML work, cameras, brush support, fixed guide and catch tray.|Rotate/zoom the live model. Larger-object handling is tested in a prescribed lower strip.|
|2:00–2:30|Harsh: business-script inputs and how simulation throughput feeds costs.|Business sensitivity graph;120baseline person-h/month is assumed; all transfers/recovery count as human work.|
|2:30–3:00|Arush:180 complete trial attempts;30/controller/tilt; primary comparison uses equal first 30 seconds.|At 20°, baseline RMSE≈10.006cm versus proposed ≈1.182 cm. Both30/30completed; proposed uses slightly higher first 30-second torque-squared effort.|
|3:00–3:30|Harsh: base-case economics and uncertainty.|NCRI≈38.0%; simple payback≈20.5 months; reclaimed≈57.1 person-h/month. These are scenario outputs. Wilson-lower-bound scenario:32.2%NCRI and24.2months.|
|3:30–4:00|Ronit: realistic next step and conclusion.|Propose a supervised, guarded physical prototype and measured operator/supplier inputs. No customer pilot or partnership is claimed.|

At 4:00 stop. Minutes 4–7 are judge questions; 7–9 advice; 9–10 disconnect. Note actual advice for the studio testimonial.

## Open these before your slot

From the group folder with the existing Mac environment active:

```bash
MUJOCO_GL=cgl mjpython src/run_live.py --speed 6
open analytics/final_business_v1/business_sensitivity.png
open analytics/final_validation_v1/figures/tracking_and_effort.png
```

P pauses/resumes; mouse rotates/zooms. `--speed 6` requests faster wall-clock playback; integration remains0.002 s. Actual speed depends on the laptop. A complete mission is about611 simulated seconds: demonstrate an active live segment within the pitch, rather than waiting silently for the whole cycle. Rehearse and pause at a useful cleaning state before the slot; keep the terminal's actual state/detection counts visible. Use a clearly labelled recording only as a backup, not as a claim of live execution.

To show a handled fault using the existing controller:

```bash
MUJOCO_GL=cgl mjpython src/crawler_cleaning_controller.py --viewer --fault pose_dropout --fault-time 3 --duration 10 --output analytics/jury_pose_dropout_real_trials.csv
```

This is a separate, labelled base-controller fault scenario, not the combined contamination mission. Choose a new output filename. Pose-dropout/brush-jam development tests demonstrate active stopping; severe traction-loss tests are not uniformly safe. Do not claim field certification.

## Be ready to explain

- **Physics:**8.5 kg; four driven rollers approximate tracks;five actuators; 0.002 s integration. A fixed brush contacts the glass. Guards supply containment; tested simulation traction is not proven real-world grip. At 20°, ideal mg·sinθ≈28.519N and μmin = tan20° ≈ 0.364 before contact/load complexities.
- **Control:**wheel PI and bounded torques;FSM waits for persistent dirt detections, cleans/revisits, returns and services. Pose feedback is simulator ground truth; RGB images determine contamination. There is no general trained debris-recognition or SLAM claim.
- **Dust:**representative falling grains feed 32 layer patches, total 4 g. Removal is a contact-gated reduced-order capture/mass model, not resolved vacuum airflow. A120 g block uses genuine collisions with the guide/tray. An 89.97917% nominal qualifying footprint is not 100% coverage.
- **Statistics:**a run is the unit of inference, not each500 Hzsample. The primary RMSE/effort window is0–30 s for all 180attempts. Large effect sizes arise under tightly controlled simulation variation; they do not establish universal hardware superiority.
- **Business:**one annual manual labour cost=1. Capital ratio 0.65;annual operatingκ ≈ 0.61993;NCRI=1−κ. Payback=12×0.65/NCRI. Supervision, transfer, maintenance, efficiency and energy assumptions are explicit. No measured PV electrical recovery or commercial saving is claimed.
- **Queue:**one server;λ=2.625sections/h;μ≈4.541sections/h;ρ≈0.578;M/M/1wait≈18.10min under assumed arrival/service distributions. The observed mean service calibrates capacity, not the distributions.
- **Risk:**RPN=S×O×D. Coating-scratch RPN remains288 because hardware/coating protection is unvalidated. Other detection reductions have only the stated simulation/code evidence.

## Bring / studio

Charged laptop, charger, HDMI/USB-C adapter, formals and visible NMIMS ID. Keep the simulation, figures and final dossier accessible offline. Speak in your own words, not from a phone.

Studio: introduction 15 s; problem 30 s; work 40 s; actual jury advice 30 s; future 25 s; thanks 10 s. Share prompts across members and ensure all three speak. Prompt 4 must use what the jury actually said today. Tell the volunteer if anyone declines appearing in the public studio video; optional dossier research consent remains a separate choice.
