# Group 06 — solar-panel cleaning crawler

Current submission: signed filled dossier, executable live MuJoCo controller, genuine180-attempt evidence and simulation-calibrated business analysis. User-supplied final team video: https://lnkd.in/p/d_en8Zas.

## Start here

- [Technical dossier Word](docs/MDRIIA_Group_06_Technical_Dossier.docx) / [PDF](docs/MDRIIA_Group_06_Technical_Dossier.pdf)
- [Business report Word](docs/Group06_Business_Model_Report.docx) / [PDF](docs/Group06_Business_Model_Report.pdf)
- [Four-minute jury plan](docs/JURY_PRESENTATION.md) and [current run commands](docs/RUN_AND_DEMO.md)
- [Team roster](docs/TEAM_ROSTER.json), including actual user-reported roles and video link.

Mac, from this folder and activated Python 3.12 environment: `MUJOCO_GL=cgl mjpython src/run_live.py --speed 6`. Linux desktop uses `MUJOCO_GL=glfw python src/run_live.py --speed 6`. The speed option changes pacing only, not physics; actual throughput depends on the computer. Use **P** to pause/resume. No slides.

## Evidence and scope

All 180 frozen attempts remain in analytics/final_validation_v1 with original seeds, result/coverage reports, protocol, statistics, source snapshot and model hashes. The six analytics/primary_windows/*_real_trials.csv.gz files copy actual500 Hz0–30 s samples for every attempt:2,700,000 samples. They are explicitly primary statistical windows, not full trajectories. Two complete nominal20°traces are also included. All 180original full telemetry streams remain accessible by pinned hash/URL in analytics/FULL_RAW_DATA_MANIFEST.json. This avoids duplicating8.1 GB of bulk development telemetry.

`python analytics/reproduce_compact_validation.py --output-dir analytics/NEW_check` recomputes the primary RMSE/effort statistics and a graph. `python analytics/final_business_model.py --validation-dir analytics/final_validation_v1 --output-dir analytics/NEW_business` recalculates the business case. Use fresh output directories. Full-data fetch is an explicit optional operation, not needed for these complete primary comparisons or the live demo.

The primary comparison uses the same0–30 sexposure per trial; complete-cycle outcomes are separate. At 20°both controllers complete30/30 selected trials; mean RMSE is about 0.100061 m baseline and0.0118225 m proposed. Trial variability is narrow and controlled, not a field-reliability or universal superiority study. The current nominal demonstration reports about89.98%qualifying whole-panel footprint, not 100% coverage.

Business base case: approximately38.0% normalised operating-cost reduction,20.5 months simple payback and57.1 person-h/month reclaimed under explicitly assumed commercial inputs. Actual simulator timing/work calibrates the model; these are not measured field savings, sourced supplier quotations or PV electrical-yield recovery.

## Mechanism and limitations

The8.5 kg model uses four driven rollers as a track approximation, a rotary brush, fixed supports/solid guide, an external dock and a permanent tray. Actual rendered RGB drives contamination decisions; navigation uses simulator pose. Fine dirt uses a contact-gated mass/capture model; a120 g block uses collision pushing in a prescribed corridor. Containment guards, reduced-order vacuum/charging and fixed lighting/colours are disclosed. Real traction, coating/structural compatibility and suction/charging hardware are not validated.

Current files are the entry points above. Inherited SIMULATED_* targets, old starter plots and historical scaffold economics are not final experimental evidence. No other group’s files are changed by this submission. Optional research consent remains blank; signatures were supplied by the team.
