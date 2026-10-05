"""
server.py
=========
Flask REST API server + static frontend host for DeFi Fraud Detection.

Serving the frontend through Flask eliminates all CORS issues because
the browser sees everything as the same origin (http://localhost:5000).

Endpoints
---------
GET  /                  -- Serves the frontend (index.html)
GET  /api/health        -- Health check
POST /api/analyze       -- Full wallet analysis pipeline

Usage
-----
    cd C:\\Users\\PK\\OneDrive\\Desktop\\defi
    .\\venv\\Scripts\\python.exe backend\\server.py

Then open:  http://localhost:5000
"""

import sys
import re
import traceback
from pathlib import Path

# Ensure project root is on the path
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"
sys.path.insert(0, str(_PROJECT_ROOT))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from backend.analyze_and_log import analyze_and_log

app = Flask(__name__, static_folder=str(_FRONTEND_DIR), static_url_path="")
CORS(app)


# ---------------------------------------------------------------------------
# Serve Frontend Static Files
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the main frontend page."""
    return send_from_directory(_FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    """Serve any other frontend file (CSS, JS, manifest.json, etc.)."""
    return send_from_directory(_FRONTEND_DIR, filename)


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    The frontend calls this on load to confirm the backend is live.
    """
    return jsonify({
        "status": "ok",
        "service": "DeFi Fraud Detection API",
        "version": "2.0.0",
        "features": {
            "blacklist_check": True,
            "ml_model": True,
            "shap_explanation": True,
            "blockchain_logging": True,
        }
    }), 200


# ---------------------------------------------------------------------------
# POST /api/analyze
# ---------------------------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Full wallet analysis pipeline.

    Request  : POST { "address": "0x..." }
    Response : Full assessment JSON (see analyze_and_log docs)
    """
    data = request.get_json(silent=True)

    if not data or "address" not in data:
        return jsonify({
            "error": "Missing required field: address",
            "details": "Send JSON body: { \"address\": \"0x...\" }"
        }), 400

    address = data["address"].strip()

    if not re.match(r"^0x[a-fA-F0-9]{40}$", address):
        return jsonify({
            "error": "Invalid Ethereum address",
            "details": f"'{address}' is not a valid 42-character 0x address"
        }), 400

    try:
        result = analyze_and_log(address)

        # Strip internal keys not needed by the frontend
        result.pop("_processed_input", None)

        # Normalise SHAP explanation
        shap_raw = result.get("shap_explanation", [])
        result["shap_explanation"] = [
            {
                "feature":    item.get("feature", ""),
                "display":    item.get("display", item.get("feature", "")),
                "direction":  item.get("direction", ""),
                "shap_value": float(item.get("shap_value", 0)),
                "bar":        item.get("bar", ""),
            }
            for item in shap_raw
        ]

        # Add wallet to result
        result["wallet"] = address

        # Normalise blockchain receipt
        chain = result.get("blockchain")
        if chain and "transaction_hash" in chain:
            result["blockchain"] = {
                "transaction_hash": chain["transaction_hash"],
                "block_number":     chain.get("block_number"),
                "status":           chain.get("status"),
                "explorer_url":     f"https://sepolia.etherscan.io/tx/{chain['transaction_hash']}"
            }

        # Normalise blacklist info
        bl = result.get("blacklist", {})
        result["blacklist"] = {
            "is_blacklisted": bool(bl.get("is_blacklisted", False)),
            "source":         bl.get("source", "CLEAN"),
            "reason":         bl.get("reason", ""),
            "severity":       bl.get("severity", "CLEAN"),
        }

        # Fix NaN/Infinity values in features (invalid in JSON)
        import math
        features = result.get("features_used", {})
        for k, v in features.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                features[k] = 0.0

        return jsonify(result), 200

    except Exception as exc:
        traceback.print_exc()
        return jsonify({
            "error": "Analysis failed",
            "details": str(exc)
        }), 500


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  DeFi Fraud Detection - Full Stack Server")
    print("=" * 60)
    print(f"  Frontend     : http://localhost:5000")
    print(f"  Health check : http://localhost:5000/api/health")
    print(f"  Analyze API  : POST http://localhost:5000/api/analyze")
    print("=" * 60)
    print()
    app.run(host="0.0.0.0", port=5000, debug=False)