# External dock and collection prototype

The `combined` scenario loads `models/collection_cleaning_crawler.xml`. The previous guarded model and its evidence remain separate. Full-run acceptance is pending until its independent checks and recorded video are complete.

## Current mechanism

- A physical, coplanar platform extends from the upper-left edge. Home is (-3.85, 1.53) m in panel coordinates, outside the 6 × 4 m glass. The platform top matches glass z=.02 m. Rollers actually contact it; an opening replaces the adjacent trim/guard. All tools fit off glass at rest, including the forward guide. Transparent physical guards still assist containment; there are no pose clamps.
- The fixed rotary brush has a 0.8 m straight cleaning span and 0.92 m overall rounded contact envelope. It has visible support arms and cross mounts, an intake slot, a duct, a filtered-bin representation and a blower housing. A softer contact law represents bristle compliance; individual bristles and airflow are not resolved.
- A **fixed diagonal solids guide** sits ahead of the brush. Its bottom is nominally 10 mm above glass. Fine dust passes underneath to the brush/intake; the 50 mm tall test block hits the guide and is redirected toward the lower tray before entering the wheels. It has real collision geometry and 0.15 kg mass. Chassis mass is reduced by that amount to retain the assumed 8.5 kg total robot budget. This is a proposed rigid mechanism, not manufactured or structurally validated hardware.
- The permanent lower catch tray, floor and retaining lips exist from the beginning. After release, the 70 × 70 × 50 mm, 120 g wood-like block remains a dynamic rigid body. It is never removed or attached to the robot kinematically. Contact must move it off glass and leave it retained in the tray.

The block is placed in a declared lower-strip handling corridor. The guide is not an autonomous arbitrary-object collector. There is no general solid classification or scratch/damage model. Measured tool loads are reported, not declared glass-safe.

## Where fine dirt goes

The intended architecture is **brush-assisted vacuum collection**. The brush feeds an intake, a blower draws fine dust into a filtered onboard bin, and the station empties that bin. The simulation uses contact-gated, reduced-order capture rather than solved suction airflow, filtration or seals.

Eight representative falling grains each carry 0.5 g. On physical glass contact, a grain converts into four irregular soil patches; its mass is divided by patch area, preserving the grain-to-layer inventory. Removed layer mass enters the onboard bin in the same timestep. Fine dirt therefore begins with 4 g in this selected scenario. The soil model retains any below-threshold residual in the mass balance even when its visible patch disappears at the 10% residual display threshold. Manual test patches without assigned grain mass use a separately declared 20 g/m² fallback.

The surface, onboard bin and station waste must balance at every sample, and their deposited total must match the converted representative-grain mass. This is inventory accounting: payload-dependent inertia, resolved airborne dust and microscopic brush capture are not solved. The inactive grain bodies are retired surrogate states, not additional collected material.

The blower uses an assumed 20 W during cleaning. After final camera verification and a settled return, an eight-second station service transfers up to 2 g/s into its waste cartridge and credits 30 W of charging energy. The video shows a bin cutaway, service hose and charging indicator. Rates, electrical contacts, self-emptying hardware and battery behaviour remain assumptions; eight seconds does not imply a fully charged battery.

A suitable explanation is: “Our design uses a rotary brush and vacuum intake to collect fine dust in a filtered bin. A fixed guide handles larger objects separately, directing them into a tray. The dock is intended to charge and empty the bin. Dust capture, charging and bin transfer are simplified simulation models.”

## Sensing and control

Actual RGB images from the two edge cameras and onboard camera detect controlled-colour contamination. Persistent significant targets trigger departure. Image targets request slower passes near dirt and residual revisits. Navigation still uses simulator pose; camera detection does not establish visual localisation. A local six-second speed hold bridges temporary tool occlusion. Return uses bounded torque control and no powered brush command.

The rooftop, bin cutaway and service indicators are presentation-only. Tests compare raw sensor RGB and physical state before/after presentation rendering, including the service visuals. Camera feeds shown in the video are actual detector inputs with timestamps and pixel boxes.

## Validation and reproduction

Use Python 3.12, the pinned requirements and ffmpeg. In headless Linux set EGL before importing MuJoCo. Every output directory must be new.

```sh
python src/build_collection_model.py
MUJOCO_GL=egl python src/vision_mission.py --scenario combined --duration 1000 --output-dir analytics/NEW_COLLECTION_RUN
python src/verify_collection_run.py analytics/NEW_COLLECTION_RUN
MUJOCO_GL=egl python src/vision_mission.py --scenario combined --duration 1000 --cinematic --output-dir docs/validation/NEW_COLLECTION_VIDEO
python src/verify_collection_run.py docs/validation/NEW_COLLECTION_VIDEO
python src/plot_collection_evidence.py docs/validation/NEW_COLLECTION_VIDEO
python src/extract_solid_replay.py docs/validation/NEW_COLLECTION_VIDEO
```

The validator requires completion, dust thresholds, fixed motion limits, settled external home, grain-to-soil and bin/station mass conservation, service-only transfer/charging, actual tool contact before solid ejection, tray retention and continuous block motion. Whole-panel footprint is reported separately; there is no silent relaxation of the 90% flag. The optional `--legacy-inventory` is only for prototypes predating grain-mass transfer, and explicitly labels its narrower inventory check.

## Preserved development evidence

Early collection pilots and recording drafts are rejected or interrupted and labelled. Pilot1/2 failed solid retention. Pilot3 exposed insufficient entry dose. Pilot4 exceeded its horizon and failed the dock motion gate. Dock friction matching reduced that transition. Pilot5/6 and a repeated force trace exposed a deeper rigid-brush/glass numerical instability during return. The captured state/control sequence reproduced a launch with the old .005 s contact law (>4 kN at initial detection, >14 kN in the diagnostic replay); .01–.04 s contact laws avoided that launch in the controlled replay. The current brush uses .02 s and unchanged effective friction. A regression test uses this captured state.

Static-block tests found numerical drift with the original contact impedance, including unsuccessful no-slip postprocessing trials. Higher block contact impedance reduced 400 s drift to ~2 mm while keeping it dynamic. A brush-only solid test still pulled blocks underneath and was rejected. The fixed guide then passed four declared lower-strip positions: physical contact, ejection and retention, ~5–6 N peak load and <0.024° chassis tilt in that controlled diagnostic. Full mission evidence remains separate.

These are nominal simulation development results, not statistical robustness, scratch safety, structural validation or hardware certification. All source snapshots and failed data remain available.

Pilot7 completed physical collection, all dust thresholds and dock service, but a 3.96 mm interior brush-contact transient failed the unchanged .123 m height gate. The next model replaces the long cylinder contact with a capsule: 0.8 m straight span plus rounded end caps. The coverage/soil model still scores the conservative 0.8 m straight span. Support representations move outside the caps. Pilot8 is the fresh full mission with this model and exact grain-to-soil mass transfer; do not claim success until its checks pass. Forty-nine tests pass, including captured-instability regression and hybrid mass transfer.
