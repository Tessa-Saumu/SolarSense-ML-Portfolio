# SolarSense — personal-fork release check

Date: 2026-10-13. Baseline `52b8416`. This is a bounded engineering prototype, eligible for a supporting case-study presentation with the qualifications below; not a flagship or validated energy/finance product.

| Requirement | Result | Evidence |
|---|---|---|
| Personal permitted copy | PASS | Tessa-Saumu/SolarSense-ML-Portfolio is a fork of SolarSense-Capstone/DSE-models; no upstream edits |
| Real artifact startup | PASS | Isolated CPython 3.12.0; committed requirements install; consumption and XGBoost artifacts load |
| Local complete analysis | PASS within prototype scope | `scripts/portfolio_smoke.py`; fictional Nairobi input; real artifacts; threaded loopback self-HTTP |
| Formula result | PASS | Expected/observed 2700 kWh/month; not GBR predictive validation |
| Country assumption | PASS within coarse-box scope | Explicit Kenya tariff gives grid monthly cost 459; ambiguous no-hint request rejects with 400; hints outside bounds reject |
| Auth rejection | PASS for tested endpoint | Missing-key `/analyze` returns 401 |
| Current component tests | PASS | 211 passed, 50 in-memory limiter warnings; 197 component checks plus 14 country regressions |
| Historical contract reconciliation | PASS | 36 initial failures reconciled: malformed JSON/type rejection fixed; formula tests now verify numerical outputs and no model/scaler calls; response codes/ranges aligned |
| Portability cleanup | PASS | Removed machine-specific debug writes, ignore conflict markers and tracked bytecode |
| Attribution | PASS as qualified history | Candidate commits identified; Bella owner/Tessa updates preserved; no sole-author claim |
| Historical model metrics | PARTIAL, deliberately not current headline | Model 1 card/changelog disagreement remains; served formula bypasses model prediction; Model 2 historical training not rerun |
| Domain/financial validity | NOT ESTABLISHED | Coarse boxes, static tariffs/cost factors, heuristics and confidence are assumptions; no validated African savings/prediction claim |
| Hosted CI/deployment | NOT VERIFIED | Offline workflow authored; no GitHub Actions success observed; no deployment |

The first smoke receipt exposed Nairobi being resolved as Tanzania. That receipt is kept as `evidence/portfolio_smoke.before-country-fix.json` and is **defect evidence, not valid recommendation evidence**. `evidence/portfolio_smoke.json` is the corrected execution receipt with an explicit country assumption and artifact/source hashes. Both record fictional input, not customer impact.

Default pytest now deliberately collects active component suites and the new country regressions. Archived experiments and manual live-HTTP scripts are separate historical/integration tiers, not hidden passing coverage. No tests were skipped or xfailed to hide the initial failures. Final scoped suite: 211 passed; default-command verification follows the same collection.

Environment: Flask 3.0.2, NumPy 2.4.1, pandas 2.2.2, scikit-learn 1.8.0, XGBoost 3.1.3, pytest 7.4.0. Unit and smoke logs persist in the working checkout. Models/data were not retrained or overwritten.

Stop engineering here for a supporting prototype. Further investment requires model-artifact provenance and independent domain evaluation; rewriting the orchestration or collecting a new dataset is outside this consolidation.
