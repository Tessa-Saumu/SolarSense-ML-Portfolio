# Nairobi scenario extension

This personal, AI-assisted extension is separate from inherited team endpoints. It supports only Nairobi, Kenya, with explicit coordinates (-1.2921, 36.8219). No geographic inference or Africa-wide validity is claimed. Inherited team modules retain their credit and original interfaces.

## Components and units
Consumption is a transparent formula: average electrical load (kW) × hours/day × representative days/month. Alternatively enter a measured monthly bill quantity in kWh. Annual consumption is twelve identical representative months. Fictional bakery, grocery and butchery presets illustrate usage; they are not SME observations.

The solar component loads the exact train-only held-out evaluation artifact `models/solar_generation/models/flagship_solar_xgb.json`, verifying its model checksum and matching metadata to the evaluation receipt on each request. Its 12 Nairobi predictions are typical daily kWh for the documented reference system. Scaling uses panel area/reference area × efficiency/reference efficiency; calendar-month days convert daily to monthly generation. This derived solar target is not installed-system metering.

Self-consumption fraction is a user assumption. Usable offset is capped against consumption **each month**. No export payment is assumed. Annual avoided variable grid cost equals offset kWh × KES/kWh. PV operating cost adds annual maintenance. Simple payback divides installation cost by positive annual net saving; nonpositive saving produces no payback estimate. No confidence score or learned financial model is attached.

## Inputs and provenance
Default tariff KES 25/kWh, cost KES 300,000, maintenance KES 3,000/year and self-consumption 80% are fictional demonstration assumptions created 2026-10-13, not researched Kenyan rates. Users should enter their own figures. Default sources and limitations travel in every response and download. No currency conversions are performed.

Fixed charges, taxation, finance, discounting, batteries, inverter losses, roof orientation, shading, replacement and degradation are omitted. Tariff sensitivity evaluates 80%, 100%, 120% of the entered rate; it is arithmetic, not a forecast.

## Local endpoints
`POST /api/v1/scenario` accepts a JSON object; `{}` runs the fictional bakery example. `GET /api/v1/scenario/evidence` returns exact evaluated artifact predictions and metadata. These deterministic local demo endpoints contain no credentials or personal data and do not require API keys. Historical team endpoints retain authentication. Invalid, unknown, out-of-scope or nonfinite inputs return HTTP 400. Artifact mismatch fails closed with HTTP 503.

Run `python scripts/export_demo.py` after reproducing evaluation to refresh browser evidence. `web-demo/data/scenario-evidence.json` includes exact model hash and seven Python parity vectors; browser arithmetic is verified against them. Static demonstration uses exported predictions, not an in-browser model or a live Python backend.

## Local baseline result and serving policy
Nairobi was excluded from training. XGBoost MAPE on Nairobi is 12.5268%, worse than the training-city monthly mean baseline at 8.4342%. Across five held-out cities, XGBoost MAPE is 11.2056% against baseline 16.0544%. These are different scopes. The scenario defaults to the baseline, exposes XGBoost as a comparison, and exports both profiles from the same evidence record. Choosing the baseline after observing this local comparison is a presentation policy, not new independent validation. Monthly self-consumption remains optimistic without hourly load/solar overlap data.
