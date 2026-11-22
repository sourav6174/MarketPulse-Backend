import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.routes.index_routes import index_bp

def create_app():
    application = Flask(__name__)

    # =====================================
    # CORS
    # =====================================

    frontend_origins = os.getenv(
        "FRONTEND_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500"
    )
    allowed_origins = [
        origin.strip().rstrip("/")
        for origin in frontend_origins.split(",")
        if origin.strip()
    ]
    CORS(
        application,
        resources={
            r"/api/*": {
                "origins": allowed_origins
            }
        }
    )

    # =====================================
    # REGISTER ROUTES
    # =====================================

    application.register_blueprint(index_bp)

    # =====================================
    # HEALTH CHECK
    # =====================================

    @application.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "success": True,
            "application": "MarketPulse Backend",
            "module": "Indexes",
            "status": "online"
        }), 200

    # =====================================
    # ROOT ROUTE
    # =====================================

    @application.route("/", methods=["GET"])
    def home():
        return jsonify({
            "application": "MarketPulse Backend",
            "version": "1.0.0",
            "message": "MarketPulse API is running.",
            "endpoints": [
                "/api/health",
                "/api/indexes",
                "/api/indexes/list",
                "/api/indexes/nifty50"
            ]
        }), 200
    return application
app = create_app()