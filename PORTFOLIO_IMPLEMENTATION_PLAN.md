# SolarSense — bounded implementation plan

Created 2026-10-13 because this fork has no prior gap/implementation plan. Source selection and investment gate remain the central PROJECT_PORTFOLIO_AUDIT.md.

## 1. Reconcile and remove misleading presentation

S1/S3: retain historical README as a reference, replace front page with actual served behavior, team contributions and clear model limits. Add caveat to Model 1 card. S4: remove user-specific instrumentation and resolve ignore conflict markers. No model output changes intended.

## 2. Verify the permitted local path

S2/S5/S6: install committed pinned requirements in isolated Python 3.12 environment; run current component unit tests; inspect failing coordinate-contract checks. Start gateway with a generated local-only test key and explicit local HTTP base URL. Submit one fictional business request with real artifacts. Save sanitized input/output and source/artifact identity. Check formula result and output consistency; this is execution evidence, not domain accuracy.

## 3. Package and stop

Record exact test/run outcome, environment and remaining gates in PORTFOLIO_RELEASE_AUDIT.md. Add a repeatable smoke command. If artifact compatibility or model provenance cannot be established without retraining, retain repair-before-decision status and document smallest next step. Do not upgrade mocked tests to a real-model success claim.

## Checkpoint

Personal fork created; main baseline 52b8416. Inspection found loaded consumption model is bypassed by formula output. Real environment installation in progress. Existing historical metric disagreement remains unresolved; claims will be narrowed rather than manufacturing a final metric.


## Final current checkpoint — 2026-10-13

S1/S3: current claims narrowed; historical card caveated; no current formula R2/MAPE. S2/S5: isolated pinned real-artifact load and threaded local analysis pass. S4: debug writes and ignore conflict removed; tracked bytecode removed from index. S6: actual malformed JSON/type failures fixed and stale contract/formula expectations reconciled; 211 active tests pass. New S7: ambiguous country boxes reject without an explicit supported-country hint; 14 regressions and real smoke verify Kenya tariff and rejection. Source/model hashes in the corrected receipt. No training, deployment or domain-validation claim. See PORTFOLIO_RELEASE_AUDIT.md; stop at qualified supporting prototype.
