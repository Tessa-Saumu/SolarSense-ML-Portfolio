# SolarSense personal portfolio — gap audit

Assessment: 2026-10-13. Fork baseline: `52b8416`, originating from SolarSense-Capstone/DSE-models. This is a personal presentation/repair fork of a team project, not a newly solo-authored system. Team source is never modified.

## Scope and current evidence

The gateway combines consumption estimation, solar climatology, deterministic ROI and recommendations. Direct inspection of `models/energy_consumption/src/app_ml.py` shows the served consumption result uses floor-area/hours, refrigeration-unit and climate formulas. It requires loaded artifacts and label encoders, but never calls `best_model.predict`. Historical Gradient Boosting metrics therefore do not evaluate this endpoint. Model 2 calls a serialized XGBoost climatology model; ROI and recommendation logic are primarily deterministic assumptions.

Full history is available in this fork. Tessa-Saumu authored substantive consumption/orchestration corrections, including `6bb92fb`, `4c3b058`, `35d35d7` and `fc29516`. The recommendations module explicitly credits Bella as owner and Tessa for updates. Commit counts are not percentages of code ownership. Do not claim sole implementation of all components.

## Finite backlog

| ID | Gap | Why it matters | Priority | Acceptance |
|---|---|---|---|---|
| S1 | README presents all services as trained ML | Served output differs from claimed method | P0 | Formula/ML boundaries prominent; historic scores qualified |
| S2 | Real artifact/environment load not yet reproduced | Mock tests cannot establish runtime | P0 | Pinned environment, real startup, one recorded local analysis or explicit failure |
| S3 | Model 1 card and changelog disagree | Results mix historical versions | P0 for metric claims | Historical records retained, no current headline R2/MAPE without provenance |
| S4 | User-specific debug writes and conflict markers | Fresh copy is not clean/portable | P1 | Remove debug writes; resolve ignore markers; preserve load errors |
| S5 | Local `/analyze` configuration unclear | Self-HTTP calls need a running threaded service | P1 | Verified local command with API_KEY, MODELS_API_KEY and MODELS_BASE_URL; no deployment claim |
| S6 | API contract tests disagree on 400/422 | Interface contract ambiguous | P1 | Diagnose and reconcile expected malformed-coordinate behavior without hiding other failures |

## Definition of done

Narrow engineering-prototype presentation; exact team contribution boundaries; a repeatable local example; current relevant tests recorded; model metrics and assumptions honestly qualified. Domain validation, production readiness and predictive skill are not implied by reaching this finish line.

## Out of scope

New African-data collection, retraining/tuning, frontend rebuild, cloud deployment, finance advice, calibrated uncertainty, new storage/services, and broad error-format redesign. Preserve historical artifacts rather than rewriting prior results.


## Final current checkpoint — 2026-10-13

S1/S3: current claims narrowed; historical card caveated; no current formula R2/MAPE. S2/S5: isolated pinned real-artifact load and threaded local analysis pass. S4: debug writes and ignore conflict removed; tracked bytecode removed from index. S6: actual malformed JSON/type failures fixed and stale contract/formula expectations reconciled; 211 active tests pass. New S7: ambiguous country boxes reject without an explicit supported-country hint; 14 regressions and real smoke verify Kenya tariff and rejection. Source/model hashes in the corrected receipt. No training, deployment or domain-validation claim. See PORTFOLIO_RELEASE_AUDIT.md; stop at qualified supporting prototype.
