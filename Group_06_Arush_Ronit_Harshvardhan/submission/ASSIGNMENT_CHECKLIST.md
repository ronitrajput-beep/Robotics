# Group 06: what to submit

This checklist follows the faculty's current **20-mark capstone rubric**, not the older milestone table. Source: [GRADING_RUBRIC_AND_EVALUATION_POLICY.md](https://github.com/sunny-nanade/NMIMS-MPSTME-MDRIIA-2026/blob/d5b7da279a034fcd08b090766ef96ed31b196684/GRADING_RUBRIC_AND_EVALUATION_POLICY.md), checked against faculty `main` at the same commit.

## 1. MS Teams assignment: every member

- Attach the team's **final signed technical dossier PDF**.
- **Arush, Ronit and Harshvardhan each click Turn in individually**, using the same final group PDF.
- The business-model report PDF can be added as supporting material if the assignment accepts additional attachments. The rubric explicitly requires the dossier PDF on Teams; it does not separately mandate a business-report PDF.

Use the team's latest completed local dossier, with its final public LinkedIn video URL and personal signatures. The latest cloud copy includes the three user-supplied signature photographs; retain any later local edits, including the final video URL. Optional research consent may remain blank as the team requested.

## 2. Faculty GitHub repository: group folder

Repository: `sunny-nanade/NMIMS-MPSTME-MDRIIA-2026`.
Folder: `Group_06_Arush_Ronit_Harshvardhan/`.

| Required material | Location / files |
|---|---|
| Filled dossier Word and matching final PDF | `docs/Group_06_E048_E052_E058_Technical_Dossier.docx` and `.pdf` |
| Actual MuJoCo model | `models/`, including `collection_cleaning_crawler.xml` and model dependencies |
| Controller, vision and live-demo code | `src/`, with the current entry points and dependencies |
| **Executable business model** | `analytics/final_business_model.py` and `analytics/final_business_inputs.json` |
| Business results and graphs | `analytics/final_business_v1/`: inputs, simulation calibration, results, sensitivity CSV and two figures |
| Genuine simulation data and analysis | `analytics/final_validation_v1/`: actual trial telemetry CSV/XZ, protocol, full summary, statistics, analysis and provenance records |
| Reproduction instructions | Requirements and commands for the simulation, business calculation and evidence |

The rubric requests genuine `*_real_trials.csv` evidence and 500 Hz logging. The current final evaluation retains its actual 500 Hz CSV streams compressed as `.csv.xz`; document the paths and lossless decompression/reading instructions. The 180-row `summary.csv` is a run-level summary, not a replacement for those raw streams. Historical earlier-model trials and generated `SIMULATED_*` starter targets are not the final evaluation.

Add the new business report Word/PDF under `docs/` as supporting documentation:

- `docs/Group06_Business_Model_Report.docx`
- `docs/Group06_Business_Model_Report.pdf`

The new business-only package contains the script, declared inputs, final outputs and calibration summary/protocol/statistics. Bulk raw 500 Hz telemetry remains in the full project repository and is not duplicated in that compact package.

Publish faculty-repository changes through the feature-branch/PR workflow required by that repository. The personal `ronitrajput-beep/Robotics` sharing repository is separate from the faculty submission.

## 3. LinkedIn video

- Publish the final team presentation and paste the **actual public post URL** into dossier Section 5 before exporting the submitted PDF.
- The current rubric specifies a 3–4 minute presentation with MuJoCo operation, the business sensitivity graph and every member appearing/speaking on webcam.
- The simulation source clip is available separately; use the team's completed face/voice edit for the public presentation.

## 4. Live showcase / viva

- Rehearse a live MuJoCo mission from the submitted project, including FSM states and one handled failure.
- Show the business sensitivity graph and explain inputs, assumptions, payback, NCRI, queueing and FMEA.
- Each member should be able to explain their own contribution and the overall model.
- The current rubric says **no PPT slides**. A separate four-page IEEE paper is an optional publication track, not a required extra in the current capstone submission list.

## Downloads and latest files

- New report: `submission/business_model_report_v1/Group06_Business_Model_Report.docx` and `.pdf`.
- New business-only ZIP: `submission/business_model_report_v1/Group06_Business_Model_Package.zip`.
- Latest cloud dossier reference: `submission/dossier_revision_v6/Group06_Dossier_Updated.docx` and `.pdf`; retain the team's later signed/local edits.
- Complete camera-inclusive simulation and narration: `submission/complete_camera_video_v1/`.

The new report/package prepares the business evidence. It does not post LinkedIn, upload to the faculty repository or turn in the Teams assignment.
