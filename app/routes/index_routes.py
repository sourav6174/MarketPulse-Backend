from flask import Blueprint, jsonify, request
from app.config.indexes import INDEX_CONFIG
from app.services.yahoo_finance import (
    fetch_all_indexes,
    fetch_index_by_id
)

index_bp = Blueprint("indexes", __name__)

def refresh_requested():
    return (
        request.args.get("refresh", "false").lower() == "true"
    )

# =========================================
# GET ALL INDEXES
# =========================================

@index_bp.route("/api/indexes", methods=["GET"])
def get_all_indexes():
    response = fetch_all_indexes(
        force_refresh=refresh_requested()
    )
    status_code = 200 if response["success"] else 503
    return jsonify(response), status_code

# =========================================
# GET ONE INDEX
# =========================================

@index_bp.route("/api/indexes/<index_id>", methods=["GET"])
def get_single_index(index_id):
    if index_id not in INDEX_CONFIG:
        return jsonify({
            "success": False,
            "message": "Index not found.",
            "availableIndexes": list(INDEX_CONFIG.keys())
        }), 404
    result = fetch_index_by_id(
        index_id,
        force_refresh=refresh_requested()
    )

    if result["status"] != "success":
        return jsonify({
            "success": False,
            "message": "Unable to fetch index data.",
            "data": result
        }), 503

    return jsonify({
        "success": True,
        "data": result
    }), 200

# =========================================
# GET AVAILABLE INDEX LIST
# =========================================

@index_bp.route("/api/indexes/list", methods=["GET"])
def get_index_list():
    indexes = []
    for index_id, config in INDEX_CONFIG.items():
        indexes.append({
            "id": index_id,
            "name": config["name"],
            "symbol": config["symbol"],
            "category": config["category"],
            "featured": config["featured"]
        })

    return jsonify({
        "success": True,
        "count": len(indexes),
        "data": indexes
    }), 200