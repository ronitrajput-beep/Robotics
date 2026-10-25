# Submission readiness — working development demo, incomplete submission

## Current demonstrated capabilities

- A guarded camera-triggered fine-dirt mission completes CLEAN_AND_HOME at 487.602 simulated seconds.
- Six representative physical grains fall and contact glass before converting into a visible surface dirt proxy. Persistent RGB detections trigger departure at 4 s.
- A fixed 0.8 m rotary brush, physical containment and perimeter-aware route produce 92.083% qualifying projected footprint over the original 24 m²; chassis contact reaches all four boundaries.
- The first sweep leaves one camera target. One image-directed revisit clears it; all six patches finish below the declared 0.1 residual threshold, followed by settled home return.
- Clean and subthreshold 12 s scenarios remain home; the one subthreshold patch persists. No endless cleaning loop is commanded.
- Actual RGB camera checks detect three controlled patches with approximately 1 cm position error and no clean-scene false detections in that test.
- A separate physical larger-crumb pilot moves a persistent rigid body off glass into a catch tray. This is not yet integrated arbitrary central-crumb collection.
- 32 automated tests pass, plus recorded-run independent checks and a complete ffmpeg video decode. Original telemetry is retained in docs/validation/vision_demo_v1; the newer polished video and independent checks are in docs/validation/cinematic_demo_v2.
- The original 60-run tracking benchmark remains a narrow 30-second comparison under its older configuration; it is not evidence for the new full-mission architecture.

## Remaining engineering and validation

1. Approximately 92% projected contact coverage is not 100% cleaning or a calibrated physical dirt-removal measurement. Brush-local dose and field rendering remain explicit reduced-order assumptions.
2. The transparent physical guard restrains the body/rollers and is relied upon. Brush/guard collision is excluded as a flexible-overhang approximation. These choices do not establish unrestricted traction, power-off holding or hardware safety. Wider friction/tilt/load/fault tests remain required.
3. RGB detection is controlled-colour perception. Lighting variation, reflections, occlusion/unknown regions and a broader supported debris class need validation. Navigation and moving-camera calibration still use simulator truth; visual localisation is unfinished.
4. General central-crumb routing/collection, a supported home bay and fully interactive integrated dirt viewer remain incomplete. The current end-to-end pipeline supports headless RGB rendering and MP4.
5. Freeze the new full-mission protocol and run held-out baseline/proposed conditions with sufficient runs, retaining failures. Development seeds and the old short study do not substitute for this evaluation.
6. Harden output/exception handling and test remaining sensor/numeric faults. Earlier invalid pilots and the corrected final-report serialization failure are explicitly retained and labelled.
7. Verify primary references, standards applicability and economic inputs. Cost/queue assumptions are not measured commercial benefits; a partial-coverage route is not a whole-panel cleaning service time.
8. A procedural rooftop/deck/skyline and cinematic close-ups are now recorded at 720p. Higher-fidelity assets and final team presentation remain separate work.

## Submission and human actions

- Complete/review the original Word dossier while preserving controls; produce the required four-page PDF and genuine signatures.
- Confirm exact IDs and actual contributions. Do not manufacture teammate authorship or commits.
- Every member must appear and speak in the required 3–4 minute video; create the actual post and add its real URL. The 69.96 s development simulation clip is not that presentation.
- Complete actual peer reviews for Groups 07 and 12.
- Every member must turn in the identical final PDF individually on Teams.
- Nothing has been submitted to faculty, Teams or LinkedIn by this implementation.

Recorded project deadline: 26 October 2026, 23:59 IST; showcase 31 October. Check official course instructions for changes. See CONTINUE_HERE.md, GUARDED_IMPLEMENTATION.md and RUN_AND_DEMO.md for current source/evidence locations. Historical synthetic starter data/images remain excluded from results.

Latest explicit edge test clears four of six deposits and reports two unreachable left-strip patches as INCOMPLETE. The prior detector miss is corrected and covered by RGB regression fixtures. The new larger-solid video uses a 120 g physical block and catch tray; high contact loads remain unvalidated for glass safety. See POLISH_AND_EDGE_TESTS.md.
