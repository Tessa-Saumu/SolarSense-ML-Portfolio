"""Local deterministic scenario endpoints, separate from legacy authenticated APIs."""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from .core import calculate, load_evidence, ScenarioValidationError
from .assessment import assess, load_assessment_evidence
blueprint = Blueprint("scenario", __name__)
@blueprint.get("/api/v1/scenario/evidence")
def evidence():
    return jsonify(load_evidence())
@blueprint.post("/api/v1/scenario")
def scenario():
    try:
        if not request.is_json:
            return jsonify(error="Provide application/json."), 400
        return jsonify(calculate(request.get_json()))
    except (ScenarioValidationError, BadRequest) as exc:
        return jsonify(error=str(exc)), 400
    except (RuntimeError, FileNotFoundError, KeyError):
        return jsonify(error="Verified scenario artifacts unavailable; regenerate evaluation artifacts."), 503

@blueprint.get("/api/v1/assessment/evidence")
def assessment_evidence():
    try:
        return jsonify(load_assessment_evidence())
    except (RuntimeError, FileNotFoundError, KeyError):
        return jsonify(error="Verified assessment artifacts unavailable."), 503

@blueprint.post("/api/v1/assessment")
def assessment():
    try:
        if not request.is_json:
            return jsonify(error="Provide application/json."), 400
        return jsonify(assess(request.get_json()))
    except (ScenarioValidationError, BadRequest) as exc:
        return jsonify(error=str(exc)), 400
    except (RuntimeError, FileNotFoundError, KeyError):
        return jsonify(error="Verified assessment artifacts unavailable."), 503
