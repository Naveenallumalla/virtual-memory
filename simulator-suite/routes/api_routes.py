"""
REST API Routes for Simulator Suite.

Blueprint: api
  GET  /health         → server status
  GET  /api/algorithms → list supported algorithms
  POST /api/simulate   → run simulation
"""

import time
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from services.simulator_service import (
    validate_input,
    run_simulation,
    get_algorithms_info,
    ValidationError,
)

api_bp = Blueprint("api", __name__)

# Track server start time for uptime reporting
_SERVER_START = time.time()


def success_response(data: dict, status: int = 200):
    return jsonify({"status": "success", "data": data}), status


def error_response(message: str, status: int = 400):
    return jsonify({"status": "error", "message": message}), status


@api_bp.route("/health", methods=["GET"])
def health():
    """Server health check endpoint."""
    uptime_seconds = round(time.time() - _SERVER_START, 2)
    return success_response({
        "healthy": True,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "app": "Simulator Suite",
    })


@api_bp.route("/api/algorithms", methods=["GET"])
def list_algorithms():
    """Return metadata about all supported algorithms."""
    return success_response({"algorithms": get_algorithms_info()})


@api_bp.route("/api/simulate", methods=["POST"])
def simulate():
    """
    Run page replacement simulation.

    Request body (JSON):
        {
            "reference_string": [1, 2, 3, 4, 1, 2, 5],
            "frames": 3,
            "algorithms": ["fifo", "lru", "optimal"]
        }
    """
    if not request.is_json:
        return error_response("Content-Type must be application/json.", 415)

    data = request.get_json(silent=True)
    if data is None:
        return error_response("Invalid or empty JSON body.", 400)

    try:
        validate_input(data)
    except ValidationError as e:
        return error_response(str(e), 422)

    try:
        result = run_simulation(
            reference_string=data["reference_string"],
            num_frames=data["frames"],
            algorithms=data["algorithms"],
        )
        return success_response(result)
    except Exception as e:
        current_app.logger.error(f"Simulation error: {e}", exc_info=True)
        return error_response("An internal error occurred. Please try again.", 500)
