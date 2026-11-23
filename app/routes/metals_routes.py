# app/routes/metals_routes.py

from flask import Blueprint, jsonify, request
from app.services.metals_service import (
    fetch_all_metals,
    clear_metals_cache
)

metals_bp = Blueprint(
    "metals",
    __name__,
    url_prefix="/api"
)

@metals_bp.route("/metals", methods=["GET"])
def get_metals():
    try:
        # Allow the user to bypass the cache
        refresh = request.args.get(
            "refresh",
            "false"
        ).lower() == "true"
        if refresh:
            clear_metals_cache()
        response = fetch_all_metals()
        return jsonify(response), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "message": "Unable to retrieve metals data",
            "error": str(error)
        }), 500