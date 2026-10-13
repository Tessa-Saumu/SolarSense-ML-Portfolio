"""Run a fictional local analysis with committed artifacts, never external services."""

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import secrets
import sys
import threading

import requests
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Start a threaded local gateway and record a sanitized execution receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'portfolio_smoke.json')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    key = secrets.token_urlsafe(24)
    os.environ['API_KEY'] = key
    os.environ['MODELS_BASE_URL'] = 'http://127.0.0.1:1/api/v1'
    from api.main import app
    from models.recommendations import model4_app

    server = make_server('127.0.0.1', 0, app, threaded=True)
    base = f'http://127.0.0.1:{server.server_port}'
    model4_app.MODELS_BASE_URL = base + '/api/v1'
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    payload = {
        'business_name': 'Fictional Nairobi Grocery',
        'business_type': 'grocery',
        'location': 'Nairobi, Kenya',
        'country': 'Kenya',
        'country': 'Kenya',
        'latitude': -1.2921,
        'longitude': 36.8219,
        'sqft_m2': 150,
        'operating_hours_weekly': 84,
        'num_refrigeration_units': 3,
    }
    try:
        response = requests.post(
            base + '/api/v1/analyze', json=payload,
            headers={'X-API-KEY': key}, timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        if not math.isclose(result['current_energy_cost']['grid_monthly'], 459.0, abs_tol=0.01):
            raise RuntimeError('Nairobi example did not use the explicit Kenya tariff assumption')
        ambiguous_payload = {k: v for k, v in payload.items() if k != 'country'}
        ambiguous = requests.post(
            base + '/api/v1/analyze', json=ambiguous_payload,
            headers={'X-API-KEY': key}, timeout=10,
        )
        if ambiguous.status_code != 400:
            raise RuntimeError('Ambiguous country request must fail rather than guess a tariff')
        from models.recommendations.model4_app import resolve_country_and_tariff
        if resolve_country_and_tariff(payload['latitude'], payload['longitude'], 'Kenya')['country'] != 'Kenya':
            raise RuntimeError('Country assumption resolution mismatch')
        ambiguous = requests.post(base + '/api/v1/analyze',
            json={k: v for k, v in payload.items() if k != 'country'},
            headers={'X-API-KEY': key}, timeout=10)
        if ambiguous.status_code != 400:
            raise RuntimeError('Ambiguous country was not rejected')
        denied = requests.post(base + '/api/v1/analyze', json=payload, timeout=10)
        if denied.status_code != 401:
            raise RuntimeError(f'Missing-key request returned {denied.status_code}')
        consumption = requests.post(
            base + '/api/v1/estimate-consumption', json=payload,
            headers={'X-API-KEY': key}, timeout=10,
        )
        consumption.raise_for_status()
        from models.energy_consumption.src.app_ml import get_climate_factor
        expected = (150 * 10 + 3 * 250) * get_climate_factor(payload['location'])
        observed = consumption.json()['estimated_consumption_kwh_monthly']
        if not math.isclose(observed, expected, abs_tol=0.01):
            raise RuntimeError(f'Formula contract mismatch: {observed} vs {expected}')
        artifacts = [
            ROOT / 'models/energy_consumption/models/energy_consumption_model_v1.joblib',
            ROOT / 'models/solar_generation/models/xgboost_climatological_model_v2.json',
        ]
        receipt = {
            'scope': 'Local execution, not predictive accuracy or domain validation',
            'input': payload, 'analysis': result,
            'consumption_formula_expected': expected,
            'consumption_observed': observed, 'missing_key_status': denied.status_code,
            'ambiguous_country_status': ambiguous.status_code,
            'tariff_assumption': 'Explicit Kenya hint; coarse bounds, not geospatial validation',
            'ambiguous_location_status': ambiguous.status_code,
            'country_assumption': 'Kenya; validated against coarse bounds only',
            'python': sys.version.split()[0],
            'versions': {name: importlib.metadata.version(name) for name in
                         ['Flask', 'numpy', 'pandas', 'scikit-learn', 'xgboost']},
            'artifact_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in artifacts},
            'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                             ['api/main.py', 'models/recommendations/model4_app.py',
                              'models/energy_consumption/src/app_ml.py']},
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        print(f'PASS: local analysis, formula contract and missing-key rejection; receipt: {args.output}')
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == '__main__':
    main()
