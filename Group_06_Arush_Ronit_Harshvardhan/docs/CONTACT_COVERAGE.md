# Contact coverage audit and development route experiment

The original retained route reaches and settles at its endpoint, but does not clean the entire panel. A new coverage audit separates path geometry from intermittent contact. Existing result fields retain the original grid so old comparisons remain reproducible. `coverage_metrics_v2` uses uniform 5 cm cell centres and actual model radius/half-width, with brush centre and projected axle measured from MuJoCo. It is still a **rectangular footprint approximation activated by aggregate contact**, not a resolved bristle-contact map. A single contact does not prove that every cell across the brush width physically touched glass.

The whole-panel denominator is always 24 m². A separately declared interior rectangle x ∈ (−2.55, 2.55), y ∈ (−1.55, 1.55) has area 15.81 m². This is a reporting region, not a guarantee of reachability or an excuse to omit borders. Soil attenuation remains the same uncalibrated exponential proxy, rate 2/s while force >0.1 N, brush speed >1 rad/s and state is SWEEP. The 50%-soil-proxy threshold is an explicit descriptive threshold, not calibrated cleaning success. Geometric footprint includes all states; qualifying contact includes only SWEEP.

## Original-route reproduction

`analytics/coverage_audit_seed0.csv.gz` records 122263 samples at 500 Hz. The robot DOCKED at 244.526 s, with the exact same motion/legacy coverage as the previous docking run. The new map reports:

- Projected footprint: 55.906% of the whole panel.
- Qualifying contact footprint: 55.885% of the whole panel; 84.266% of the separately declared interior.
- Never projected: 44.094% of the whole panel. Projected but never qualified: 0.0208%.
- At least 50% soil-proxy removal: 30.677% of the whole panel. Mean proxy removal: 29.531%.
- Qualifying contact on 34.371% of SWEEP samples; median measured normal force 0 N, 95th percentile 114.395 N, maximum 282.897 N.

This distinguishes **union coverage** from **contact dose**: intermittent contact does not leave many entirely unvisited cells inside the swept projection, but it changes dose and loads substantially. The force peaks are dynamic simulation contact forces, not a safe design load; compare the 8.5 kg robot's weight (~83.4 N) and investigate dynamics before hardware claims. Improving contact alone cannot fix cells outside the path. Never increase friction, freeze the chassis, weaken edge guards or alter force thresholds to fabricate success.

`analytics/coverage_audit_seed0_report.json` hashes its three source artifacts. Reproduce analysis into fresh filenames:

```
python analytics/audit_contact_coverage.py analytics/coverage_audit_seed0.csv.gz --report analytics/new_audit.json --figure docs/validation/new_audit.png
```

The saved `.coverage.npz` contains cell coordinates, geometric and qualifying masks, residual soil and the interior mask. Added CSV fields give measured brush centre and projected axle for future independent replay.

## Expanded-route pilot (development, not final evaluation)

The optional `--layout expanded` retains eight bidirectional rows and 0.65 m inward connectors, extends centre endpoints to ±2.40 m and outer rows to ±1.35 m. Its initial placement follows the first planned point. It uses unchanged physics, actuation, guard radius, braking supervisor and controller gains. Nominal planned centre clearance is at least 0.15 m; actual clearance must be measured because tracking error can consume that margin. The default `standard` route remains available and existing historical data are preserved.

Seeds 0/1/2, 420 s limit, proposed controller are development checks chosen before running this pilot. They cannot be counted as independent held-out evaluation. Retain aborts and timeouts. Read `analytics/expanded_seed*.csv.json` for actual outcomes. A wider route is not automatically a safe route, and coverage remains a proxy even after route completion.

### Pilot outcomes and retained candidate

All three `expanded` pilots increased whole-panel qualifying coverage to 63.94–64.40%, but stopped with EDGE_MARGIN after 15 of 16 waypoints, before docking. Seed 0 triggered at x=−2.279 m, y=−1.507 m during the low return: the original planned 0.20 m lower-edge clearance was consumed by measured drift. The guard was not relaxed. STOPPED is a successful settled fault stop here, **not mission success**. All raw logs/manifests remain in `analytics/expanded_seed*`.

The added optional `expanded_safe_return` variant retains the expanded x endpoints and upper row, but restores the original lower row at y=−1.20 m. This targets the observed return failure with more geometric clearance, without changing physics, limits or safety criteria. Subsequent development seeds 0/1/2 all completed 16 waypoints and reached settled DOCKED in 255.400–257.176 s. Whole-panel qualifying coverage was 61.323%, 61.719% and 61.406%, respectively. Interior qualifying coverage was 89.55–89.66%. Minimum logged conservative clearance was 0.1452–0.1527 m. These are observed development outcomes, not guaranteed margins under arbitrary disturbance.

`analytics/expanded_safe_return_checks.json` records independent CSV checks of positive clearance, 500 Hz timestamps, endpoint position, all waypoints and the final 0.5 s planar/angular/brush settling window. The original standard route stays the default to preserve existing workflows. Run the new candidate explicitly:

```
python src/crawler_cleaning_controller.py --layout expanded_safe_return --seed 0 --duration 420 --output analytics/NEW_UNIQUE_NAME.csv.gz
```

Contact coverage improved by approximately 5.4–5.8 percentage points compared with the seed-0 standard-route audit using the same v2 grid definition. This is a development comparison, not independent inference. The seed-0 fraction exceeding 50% soil-proxy removal is 30.125%, slightly lower than the original route's 30.677% despite its larger contact union. Thus a wider contact union must not be presented as a uniform improvement in cleaning dose. Full-panel cleaning remains unsolved.
