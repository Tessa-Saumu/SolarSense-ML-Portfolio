# SolarSense: my team integration work

I worked on a team prototype that turns a small business's inputs into consumption estimates, solar-generation estimates and an assumption-based cost report. This personal fork makes my contribution and the limits of those estimates easier to inspect.

It is a working local engineering prototype. It has not been validated as an African energy predictor or a financial recommendation tool.

## My contribution

I made consumption and integration corrections recorded under Tessa-Saumu in commits `6bb92fb`, `4c3b058`, `35d35d7` and `fc29516`. The recommendation module credits Bella as its owner and me for updates. This fork retains the other contributors and the team's history; I do not claim I built the whole system alone.

The portfolio cleanup removed machine-specific debug writes, corrected ambiguous country selection, reconciled tests with the actual calculation contract and added a repeatable local example. No model was retrained.

## How it works

A Flask gateway routes requests between three calculations and the recommendation rules:

- **Consumption:** a formula based on floor area, opening hours, refrigeration units and a city climate factor. The endpoint loads a historical Gradient Boosting model but does not use its prediction for the returned value.
- **Solar generation:** a saved XGBoost model estimates a typical month from historical climate data. Further scaling and country adjustments use fixed assumptions.
- **Costs and recommendations:** arithmetic and rules using configured prices, tariffs and lifetime assumptions. ROI means return on investment; here it is a calculated scenario, not a measured return. Confidence scores are rules of thumb, not calibrated probabilities.

Country lookup uses coarse geographic boxes. If more than one box matches, the request must provide an explicit `country`, such as `Kenya`. The hint must match a supported box. It selects assumptions; it does not prove the coordinate's country or validate the tariff.

## What was checked

On 13 October 2026, an isolated Python 3.12 environment loaded the committed artifacts and completed one fictional local Nairobi analysis. The formula returned **2700 kWh/month**; the configured Kenya tariff produced **459 USD/month** in grid cost. These are reproducible calculations, not an observed business outcome.

The active suite passed **211 tests**, including 14 country-selection checks. The local example also checks that an ambiguous request without a country returns 400 and a request without its API key returns 401. The run produced 50 warnings about in-memory rate limiting, which is suitable only for the bounded local setup.

The first run had selected Tanzania for Nairobi because the boxes overlap. Its separate receipt is retained as defect evidence. The corrected [execution receipt](evidence/portfolio_smoke.json) records the input, output, environment and model-file hashes.

## Run locally

From the repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/portfolio_smoke.py --output evidence/portfolio_smoke.json
.\.venv\Scripts\python.exe -m pytest -q
```

The script creates a temporary local key, starts a threaded server on the local machine, calls `/analyze` using real saved artifacts, checks the result and shuts down. It does not contact a deployed service or external data provider. Default tests cover active components; archived experiments and manual live-service scripts are separate checks.

For manual use, set `API_KEY` and `MODELS_BASE_URL=http://127.0.0.1:8000/api/v1`, then run `python -m api.main`. Keep the service local and threaded because it calls its sibling endpoints over HTTP. A healthy gateway alone does not establish that its dependencies are ready.

## Limits

The historical consumption model's card and changelog disagree on training rows and scores. Those model metrics do not evaluate the served formula. The solar model's historical validation results do not establish accuracy for new locations or the adjusted cost report.

Prices, climate adjustments, lifetime rules and confidence scores need independent domain evaluation. I do not claim measured savings, adoption, a current deployment or production readiness. The [historical team README](docs/TEAM_README.historical.md) preserves the original setup and development record.
