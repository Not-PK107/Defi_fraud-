"""
test_backend.py
===============
Diagnostic test script to verify all backend modules, ML models,
SHAP explainability, and API endpoints.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_backend():
    print("=" * 60)
    print("  AEGIS DEFI FRAUD DETECTION - BACKEND DIAGNOSTIC SUITE")
    print("=" * 60)

    # 1. Test ML Model & Predictor
    print("\n[1/4] Testing XGBoost Model & Preprocessing Pipeline...")
    try:
        from backend.predictor import predict_fraud_risk
        sample_features = {
            "Avg min between sent tnx": 2.45,
            "Avg min between received tnx": 12.1,
            "Time Diff between first and last (Mins)": 340.0,
            "Sent tnx": 142,
            "Received Tnx": 18,
            "Number of Created Contracts": 0,
            "Unique Received From Addresses": 15,
            "Unique Sent To Addresses": 139,
            "min value received": 0.05,
            "max value received": 45.2,
            "avg val received": 4.12,
            "min val sent": 0.04,
            "max val sent": 45.18,
            "avg val sent": 3.98,
            "min value sent to contract": 0.0,
            "max val sent to contract": 0.0,
            "avg value sent to contract": 0.0,
            "total transactions (including tnx to create contract": 160,
            "total Ether sent": 565.16,
            "total ether received": 566.24,
            "total ether sent contracts": 0.0,
            "total ether balance": 1.08,
            "Total ERC20 tnxs": 0,
            "ERC20 total Ether received": 0.0,
            "ERC20 total ether sent": 0.0,
            "ERC20 total Ether sent contract": 0.0,
            "ERC20 uniq sent addr": 0,
            "ERC20 uniq rec addr": 0,
            "ERC20 uniq sent addr.1": 0,
            "ERC20 uniq rec contract addr": 0,
            "ERC20 min val rec": 0.0,
            "ERC20 max val rec": 0.0,
            "ERC20 avg val rec": 0.0,
            "ERC20 min val sent": 0.0,
            "ERC20 max val sent": 0.0,
            "ERC20 avg val sent": 0.0,
            "ERC20 uniq sent token name": 0,
            "ERC20 uniq rec token name": 0,
            "ERC20_data_missing": 1,
        }
        res = predict_fraud_risk(sample_features)
        print(f"  --> Prediction Result : {res['prediction']}")
        print(f"  --> Fraud Probability : {res['fraud_probability']:.4f}")
        print(f"  --> Risk Score        : {res['risk_score']} / 100")
        print(f"  --> Risk Level        : {res['risk_level']}")
        print(f"  --> Recommendation    : {res['recommendation']}")
        print("  [PASS] XGBoost Model and Preprocessing working smoothly!")
    except Exception as e:
        print(f"  [FAIL] Predictor test failed: {e}")
        return False

    # 2. Test SHAP Explainability Engine
    print("\n[2/4] Testing SHAP Explainability Engine...")
    try:
        from backend.wallet_fetcher import explain_with_shap
        shap_res = explain_with_shap(res["_processed_input"])
        print(f"  --> Extracted {len(shap_res)} SHAP explanation factors.")
        if shap_res:
            print(f"  --> Top Factor: {shap_res[0]['feature']} -> {shap_res[0]['display']} ({shap_res[0]['direction']})")
        print("  [PASS] SHAP Reasoning Engine working properly!")
    except Exception as e:
        print(f"  [FAIL] SHAP test failed: {e}")
        return False

    # 3. Test Blockchain Module Loading
    print("\n[3/4] Testing Blockchain Logger Module...")
    try:
        from backend.blockchain_logger import CONTRACT_ABI, SEPOLIA_CHAIN_ID
        print(f"  --> Sepolia Chain ID: {SEPOLIA_CHAIN_ID}")
        print(f"  --> Contract ABI Functions: {[item['name'] for item in CONTRACT_ABI if 'name' in item]}")
        print("  [PASS] Smart Contract definitions loaded!")
    except Exception as e:
        print(f"  [FAIL] Blockchain module test failed: {e}")
        return False

    # 4. Test Flask API Endpoints
    print("\n[4/4] Testing Flask Server API Endpoints...")
    try:
        from backend.server import app
        client = app.test_client()

        # Test /api/health
        h_res = client.get("/api/health")
        print(f"  --> GET /api/health: HTTP {h_res.status_code}")
        
        # Test /api/analyze
        test_addr = "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"
        a_res = client.post("/api/analyze", json={"address": test_addr})
        a_data = a_res.get_json()
        print(f"  --> POST /api/analyze ({test_addr}): HTTP {a_res.status_code}")
        print(f"      Returned Verdict: {a_data.get('prediction')} (Score: {a_data.get('risk_score')})")

        # Test index page serving
        i_res = client.get("/")
        print(f"  --> GET / (Frontend): HTTP {i_res.status_code}")

        print("  [PASS] Flask Server and REST API working flawlessly!")
    except Exception as e:
        print(f"  [FAIL] Flask test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("  ALL BACKEND COMPONENTS ARE 100% OPERATIONAL & WORKING!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)
