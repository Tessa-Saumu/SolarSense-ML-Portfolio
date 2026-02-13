Detailed Analysis of All Three API Files
Below is the full analysis you asked for, one file at a time.
Model 1 – Energy Consumption (models/energy_consumption/src/app_ml.py)
1. Imports (categorised)
Standard library
os
logging
from pathlib import Path
from typing import Optional
Third‑party (pip)
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import numpy as np
import joblib
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
Local / relative
None – no from . or import models.energy_consumption... style imports.
2. Local modules / helper files used at runtime
There are no Python local-module imports in this file. All intra-project runtime dependencies here are data/model artefacts loaded from disk, not Python modules.
Runtime “local dependencies” that must remain co‑located (in the same model subtree):
The joblib artefacts, loaded based on __file__:
  BASE_DIR = Path(__file__).resolve().parent  MODELS_DIR = BASE_DIR.parent / "models"  MODEL_PATH = MODELS_DIR / "energy_consumption_model_v1.joblib"  SCALER_PATH = MODELS_DIR / "energy_scaler_v1.joblib"  FEATURE_COLS_PATH = MODELS_DIR / "feature_columns_v1.joblib"  MAPPINGS_PATH = MODELS_DIR / "sme_mappings_v1.joblib"
These four files (inside MODELS_DIR) are strict runtime dependencies; they must stay in a location that matches this relative layout.
3. Data / model / config files referenced by path
Exact path expressions in code:
MODEL_PATH = MODELS_DIR / "energy_consumption_model_v1.joblib"
SCALER_PATH = MODELS_DIR / "energy_scaler_v1.joblib"
FEATURE_COLS_PATH = MODELS_DIR / "feature_columns_v1.joblib"
MAPPINGS_PATH = MODELS_DIR / "sme_mappings_v1.joblib"
Where:
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR.parent / "models"
So at runtime, the expected on-disk layout (relative to app_ml.py) is:
<this_file_dir>/../models/energy_consumption_model_v1.joblib
<this_file_dir>/../models/energy_scaler_v1.joblib
<this_file_dir>/../models/feature_columns_v1.joblib
<this_file_dir>/../models/sme_mappings_v1.joblib
No other explicit file paths (JSON, CSV, etc.) are referenced.
4. Flask app object and startup pattern
Factory function:
  def create_app(      model_path: Optional[Path] = None,      scaler_path: Optional[Path] = None,      feature_cols_path: Optional[Path] = None,      mappings_path: Optional[Path] = None,      test_mode: bool = False,      api_key: Optional[str] = None,      disable_auth: bool = False  ) -> Flask:      ...      app = Flask(__name__)      ...      return app
App object name(s):
Inside create_app, a local app is created and returned.
At module bottom:
    if __name__ == '__main__':        app = create_app()        port = int(os.getenv('MODEL1_PORT', 8001))        app.run(host='0.0.0.0', port=port, debug=True)    else:        # For imports (like in tests), create a lazy app instance that won't load models        app = None
So:
When run as a script, a module-level app is created and run.
When imported, app is set to None, and consumers are expected to call create_app().
Startup pattern:
Standalone: python app_ml.py → calls create_app() → app.run(...).
Factory: external code should call create_app(...) to obtain a Flask app.
5. Registered routes (paths + HTTP methods)
All routes are attached to the app created inside create_app.
POST /api/v1/estimate-consumption
Decorators:
    @app.route('/api/v1/estimate-consumption', methods=['POST'])    @limiter.limit("100 per minute")    @require_api_key
Description: Main prediction endpoint for SME energy consumption estimation.
GET /api/v1/health
Definition:
    @app.route('/api/v1/health', methods=['GET'])    def health():        """Health check endpoint (no authentication
Description: Simple health check for the Energy Consumption service.
GET /
Definition:
    @app.route("/")    def home():   
Description: Root-level home/status message for this service when run directly.
These three routes are the complete set for Model 1.
Model 2 – Solar Generation (models/solar_generation/solar_climatology_api.py)
1. Imports (categorised)
Standard library
import json
import logging
import os
from typing import Any, Dict, List, Optional
Third‑party (pip)
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import BadRequest
from dotenv import load_dotenv
Local / relative
from solar_climatology_service import ( DRY_MONTHS, get_model_paths, load_model_artifacts, predict_lifetime_generation, predict_solar_generation, validate_coordinates )
solar_climatology_service is a local module in the same package/folder (or on the Python path) and is a hard runtime dependency.
2. Local modules / helper files used at runtime
Local module: solar_climatology_service
Provides:
DRY_MONTHS
get_model_paths
load_model_artifacts
predict_lifetime_generation
predict_solar_generation
validate_coordinates
This file/module must stay co-located with solar_climatology_api.py (both considered part of the Model 2 runtime).
Indirect artefacts via helper functions:
load_model_artifacts() – almost certainly loads model artefacts (.joblib / .pkl / .json / etc.).
get_model_paths() – used in _load_metadata() to locate metadata file(s).
These helper functions live in solar_climatology_service and encapsulate file paths, so they (and whatever files they expect) must remain in the Model 2 runtime area.
3. Data / model / config files referenced by path
In this file, all file paths are indirect, encapsulated by solar_climatology_service. Direct string paths here:
In _load_metadata():
  paths = get_model_paths()  if not paths.metadata_path.exists():      raise FileNotFoundError(          "Metadata file not found. Run the climatological notebook to save model artifacts."      )  return json.loads(paths.metadata_path.read_text())
No literal filenames like "model.joblib" appear directly; instead:
paths.metadata_path is expected to be a JSON file path returned by get_model_paths().
Also, the API relies on load_model_artifacts() inside the route functions:
/api/v1/health:
  _, _, metadata = load_model_artifacts()
/api/v1/model-info:
  _, feature_cols, metadata = load_model_artifacts()
So all model artefact paths (models, feature columns, metadata JSON, etc.) are determined and loaded in solar_climatology_service and must remain accessible within the solar_generation model tree.
No other explicit data/config file paths are hardcoded in this file.
4. Flask app object and startup pattern
Globals/config:
  load_dotenv()  API_KEY = os.getenv("API_KEY")  limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])  logger = logging.getLogger("solar_climatology_api")
Application factory:
  def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:      app = Flask(__name__)      CORS(app)      ...      limiter.init_app(app)      ...      api_key = (config.get("api_key") if config else None) or API_KEY      @app.before_request      def security_and_logging() -> Optional[Any]:          ...          # API key auth for /api/*      ...      register_routes(app)      return app
App object name(s):
Module-level:
    app = create_app()
So when imported as solar_climatology_api, there is already a fully constructed app object at module level.
Startup pattern:
At bottom:
    if __name__ == "__main__":        port = int(os.getenv("PORT", "8000"))        app.run(host="0.0.0.0", port=port, debug=False)
Standalone: python solar_climatology_api.py → uses module-level app and app.run(...).
Factory: external code may call create_app(config=...) if needed.
5. Registered routes (paths + HTTP methods)
Routes are defined inside register_routes(app):
GET /api/v1/health
  @app.route("/api/v1/health", methods=["GET"])  @limiter.limit("100 per minute")  def health() -> Any:      ...
Description: Health check that returns model metadata (type, last trained time, validation MAPE). Returns generic 500 without stack traces on error.
GET /api/v1/model-info
  @app.route("/api
Description: Model metadata and training configuration (model type, validation MAPE, training locations, feature columns).
POST /api/v1/predict-generation
  @app.route("/
Description: Main climatological solar generation prediction endpoint, with optional lifetime projection.
No root / route is defined in this file; the only routes are the three under /api/v1/....
This set is the complete route list for Model 2.
Model 3 – ROI Calculation (models/roi_calculation/src/roi_calculation_api.py)
1. Imports (categorised)
Standard library
import os
Third‑party (pip)
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
Local / relative
None – all logic (including pure ROI computation) is contained in this single module.
2. Local modules / helper files used at runtime
There are no local Python module imports.
All helper functions are defined in the same file:
calculate_roi(...)
_validate_float_field(...)
_validate_optional_hours(...)
_validate_optional_units(...)
_validate_optional_string(...)
require_api_key() (registered via @app.before_request)
Error handlers: request_entity_too_large, ratelimit_handler, internal_server_error
create_app(config_overrides: dict | None = None) -> Flask
There are no external data/model files used by this service – it is purely calculation-based using request JSON and environment variable API_KEY / PORT.
3. Data / model / config files referenced by path
The only external configuration is via environment variables; there are no file path references at all.
load_dotenv() – pulls from .env but the filename is implicit and not referenced directly.
API_KEY = os.getenv("API_KEY")
At the bottom:
  port = int(os.getenv("PORT", 5000))  app.run(host="0.0.0.0", port=port, debug=False)
So there are no .pkl, .joblib, .json, .csv, etc. paths referenced in this file.
4. Flask app object and startup pattern
Global app and limiter:
  limiter = Limiter(      key_func=get_remote_address,      default_limits=["100 per minute"],  )  app = Flask(__name__)  app.config["MAX_CONTENT_LENGTH"] = 100 * 1024  CORS(app)  limiter.init_app(app)
API key:
  load_dotenv()  API_KEY = os.getenv("API_KEY")
App object name(s):
app is a module-level Flask app object.
There is also a create_app(config_overrides: dict | None = None) -> Flask which returns this same app (after applying optional config overrides).
Startup pattern:
  if __name__ == "__main__":      port = int(os.getenv("PORT", 5000))      app.run(host="0.0.0.0", port=port, debug=False)
Standalone: python roi_calculation_api.py → module-level app.run(...).
For other code, create_app() returns the existing configured app.
5. Registered routes (paths + HTTP methods)
Global request hook (not a route)
  @app.before_request
POST /api/v1/calculate-roi
  @app.route("/api/v1/calculate-roi", methods=["POST"])  @limiter.limit("100 per minute")  def roi_endpoint():      """Model 3 ROI calculation endpoint."""      ...
Description: Main ROI calculator endpoint taking consumption, generation, tariff, and system cost and returning ROI metrics.
GET / (current health/home route – to be changed in Step 5)
  @app.route("/")  def home():      return jsonify({"message": "ROI ENGINE API running"}), 200
Description: Root-level health/home message for this service when run directly.
Error handlers
  @app.errorhandler(413)  def request_entity_too_large(e): ...
  @app.errorhandler(429)  def ratelimit_handler(e): ...
  @app.errorhandler(500)  def internal_server_error(e): ...
These are error handlers, not standalone HTTP routes (they apply globally when those status codes are raised).
So, the effective public routes are:
POST /api/v1/calculate-roi
GET / (to be updated to /api/v1/health per your Step 5 instructions, without changing logic beyond that path and payload shape)
