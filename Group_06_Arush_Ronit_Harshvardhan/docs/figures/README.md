# Starter figures: NOT experimental results

> **Reference starter figures built on synthetic data (np.random). Re-plot them from your own `analytics/*_real_trials.csv` before using them anywhere.**

The `figure*.png` files here were produced by `analytics/generate_paper_figures.py` from generated target numbers
(see `analytics/SIMULATED_*.csv`). They only show the expected layout of your plots.

1. Run your Monte Carlo trials in MuJoCo (N ≥ 30 per condition) and log them to `analytics/*_real_trials.csv`.
2. Re-plot every figure from **your** CSV and replace or delete these files.

Starter figures in this folder: `figure1_system_architecture.png`, `figure2_kinematic_telemetry.png`, `figure3_comparative_performance.png`, `video_poster.png`

The old synthetic generator has now been replaced. The original images and SIMULATED CSV remain preserved and excluded from evidence. Current usage requires genuine physics telemetry:

```
python analytics/generate_paper_figures.py --input analytics/coverage_audit_seed0.csv.gz --output docs/validation/new_telemetry.png
```

This command plots recorded state, segment error, normal force and brush speed; it does not claim measured slip, panel deflection or power recovery. It refuses existing output files and starter benchmark columns.
