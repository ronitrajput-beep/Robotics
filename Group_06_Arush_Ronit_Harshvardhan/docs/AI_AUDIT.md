# AI interaction audit — candidates for student verification

These are actual issues found during this chat's development. Students must inspect the evidence and explain the correction themselves before entering them as personally verified cases in the dossier.

| Case | AI-produced mistake | How detected | Correction / evidence |
|---|---|---|---|
| Python import scope | A conditional `import mujoco.viewer` inside mission made `mujoco` local, causing earlier model construction to raise UnboundLocalError | Running the first physics mission produced the exception | Import viewer under a separate alias. Current mission integration tests execute the earlier model construction successfully. Python import statements bind names in the containing function. |
| Wrong tracking metric | Initial controller summary used RMS distance to the next waypoint as if it represented path tracking | Inspecting the implementation and trajectory showed large distance even on a perfect straight segment | Project position onto the active path segment and measure residual distance. tests/test_geometry_economics.py verifies a point 0.2 m from a straight segment has 0.2 m error. This remains geometric rather than time-indexed trajectory error. |
| Misleading provenance | Model/controller hashes were computed when a run finished, allowing edits during execution to label results with different source files | Concurrent development runs ended after model edits; physical results matched the earlier model but hash did not | Capture source hashes at launch; keep source immutable during batches. Prior corrected manifests explicitly record the correction. Final tracking batch verifies unique model/controller/planner hashes across its 60 runs. |

Additional lesson: a spring-mounted brush was proposed as a contact improvement, but measured contact duty decreased. It was rejected and the failed experiment retained. Plausible mechanics changes still require comparative tests.
