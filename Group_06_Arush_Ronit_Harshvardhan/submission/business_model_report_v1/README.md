# Group 06 business model package

The report is in docs/ in the ZIP. It covers the proposed commercial model, assumptions, equations, measured simulation calibration, costs, labour, payback, queueing, sensitivity and FMEA. Commercial values are assumptions, not field savings or supplier quotes. The rubric requires the executable business script in the faculty GitHub group folder; this report is supporting documentation.

Use Python 3.12. From the extracted Group06_Business_Model folder, create/activate a virtual environment and install requirements-business.txt, or use your existing project environment. Then run:

```bash
python analytics/final_business_model.py --validation-dir analytics/final_validation_v1 --output-dir analytics/business_recalculated
python -m unittest discover -s tests -p test_final_business.py
```

Choose a new output folder on each run. No MuJoCo simulation is rerun: this calculation reads the retained final evaluation summary/protocol/statistics. The calibration includes all 30 proposed 20-degree attempts, with failures retained by selection. The complete 180-attempt summary is included. Actual 500 Hz CSV/XZ trial streams remain in the full Robotics repository and are not duplicated in this business-only ZIP.

Read ASSIGNMENT_CHECKLIST.md for Teams, faculty GitHub and LinkedIn requirements. Each member turns in the final signed dossier PDF individually on Teams. Use your latest locally signed dossier, including the final public video URL. Optional research consent can remain blank. This package does not overwrite your dossier or submit anything externally.

Report roles follow the latest user correction: Harshvardhan led the business-model script/economics; Ronit supported business and robot/XML work; Arush led physics/control/simulation. AI assistance is disclosed. Sources, calculation comparisons and file hashes are provided in the JSON receipts.
