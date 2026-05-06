"""
Flask Application Entry Point — Simulator Suite
"""

import os
from flask import Flask, render_template
from flask_cors import CORS
from config import get_config
from routes.api_routes import api_bp


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load config
    cfg = get_config()
    app.config.from_object(cfg)

    # Enable CORS
    CORS(app, origins=cfg.CORS_ORIGINS)

    # Register blueprints
    app.register_blueprint(api_bp)

    # SPA catch-all: serve index.html for any non-API route
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        return render_template("index.html")

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({"status": "error", "message": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        from flask import jsonify
        return jsonify({"status": "error", "message": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        from flask import jsonify
        return jsonify({"status": "error", "message": "Internal server error."}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
