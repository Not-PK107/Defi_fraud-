"""
analyze_and_log.py
==================
Full DeFi Fraud Detection Pipeline:

  Wallet Address
      → Etherscan API (fetch live transactions)
      → Compute 39 features
      → XGBoost ML model (predict fraud risk)
      → If HIGH risk: log permanently to Sepolia blockchain
      → Print full report

Usage
-----
    cd C:\\Users\\PK\\OneDrive\\Desktop\\defi
    .\\venv\\Scripts\\python.exe backend\\analyze_and_log.py <wallet_address>

Example
-------
    .\\venv\\Scripts\\python.exe backend\\analyze_and_log.py 0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A
"""

import sys
from pathlib import Path

# Make sure project root is on path
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.wallet_fetcher import (
    fetch_normal_transactions,
    fetch_erc20_transactions,
    fetch_eth_balance,
    compute_features,
    _print_result,
    ETHERSCAN_API_KEY,
    explain_with_shap,
)
from backend.blockchain_logger import log_fraud_on_chain
from backend.predictor import predict_fraud_risk
import pandas as pd
import joblib


# ── Risk threshold for on-chain logging ────────────────────────────────────
LOG_THRESHOLD = 70  # Only log wallets with risk score > 70


def analyze_and_log(address: str) -> dict:
    """
    Full pipeline:
      1. Fetch live Etherscan data
      2. Compute 39 model features
      3. Run XGBoost fraud prediction
      4. If HIGH risk → log to Sepolia blockchain
      5. Return full assessment dict
    """
    if not ETHERSCAN_API_KEY:
        raise ValueError(
            "ETHERSCAN_API_KEY missing from .env. "
            "Get a free key at https://etherscan.io/myapikey"
        )

    # ── Step 1: Fetch blockchain data ───────────────────────────────────────
    print(f"\nAnalyzing wallet: {address}")
    print("-" * 60)
    print("  [1/4] Fetching normal transactions...")
    normal_txs = fetch_normal_transactions(address)
    print(f"        Found {len(normal_txs)} normal transactions")

    print("  [2/4] Fetching ERC20 transactions...")
    erc20_txs = fetch_erc20_transactions(address)
    print(f"        Found {len(erc20_txs)} ERC20 transactions")

    print("  [3/4] Fetching ETH balance...")
    balance = fetch_eth_balance(address)
    print(f"        Balance: {balance:.6f} ETH")

    # ── Step 2 & 3: Compute features + predict ──────────────────────────────
    print("  [4/4] Computing features & running ML prediction...")
    features = compute_features(address, normal_txs, erc20_txs, balance)
    result = predict_fraud_risk(features)
    result["features_used"] = features

    # ---- SHAP explainability ----
    try:
        _MODEL_DIR = _PROJECT_ROOT / "notebooks" / "models"
        feature_columns = joblib.load(_MODEL_DIR / "feature_columns.pkl")
        imputer = joblib.load(_MODEL_DIR / "median_imputer.pkl")
        raw_df = pd.DataFrame([features])
        raw_df.columns = raw_df.columns.str.strip()
        processed_df = raw_df.reindex(columns=feature_columns)
        processed_df = pd.DataFrame(
            imputer.transform(processed_df), columns=feature_columns
        )
        result["shap_explanation"] = explain_with_shap(processed_df)
    except Exception as e:
        result["shap_explanation"] = [{"feature": "SHAP error", "display": str(e),
                                       "direction": "", "shap_value": 0.0}]

    # ── Step 4: Log to blockchain if HIGH risk ──────────────────────────────
    risk_score = result["risk_score"]
    risk_level = result["risk_level"]

    if risk_score > LOG_THRESHOLD:
        print()
        print(f"  [!] Risk Score {risk_score} > {LOG_THRESHOLD} -- logging to Sepolia blockchain...")
        try:
            fraud_category = (
                f"ML:{result['prediction'].lower()} "
                f"prob={result['fraud_probability']:.4f} "
                f"level={risk_level.lower()}"
            )
            chain_receipt = log_fraud_on_chain(address, risk_score, fraud_category)
            result["blockchain"] = chain_receipt
            print(f"  [OK] Logged on-chain!")
            print(f"     TX Hash   : {chain_receipt['transaction_hash']}")
            print(f"     Block     : {chain_receipt['block_number']}")
            print(f"     Status    : {'Success' if chain_receipt['status'] == 1 else 'Failed'}")
        except Exception as e:
            print(f"  [FAIL] Blockchain logging failed: {e}")
            result["blockchain"] = {"error": str(e)}
    else:
        print(f"\n  [INFO] Risk Score {risk_score} <= {LOG_THRESHOLD} -- NOT logged to blockchain (below threshold).")
        result["blockchain"] = None

    return result


def _print_full_report(address: str, result: dict) -> None:
    """Print the complete fraud assessment report."""
    chain_info = result.pop("blockchain", None)

    # Use wallet_fetcher's print function for the main report
    _print_result(address, result)

    # Append blockchain info if available
    if chain_info and "transaction_hash" in chain_info:
        sep = "=" * 60
        print(sep)
        print("  BLOCKCHAIN RECORD (Sepolia Testnet)")
        print(sep)
        print(f"  TX Hash   : {chain_info['transaction_hash']}")
        print(f"  Block     : {chain_info['block_number']}")
        print(f"  Status    : {'[Confirmed]' if chain_info['status'] == 1 else '[Failed]'}")
        print(f"  Explorer  : https://sepolia.etherscan.io/tx/{chain_info['transaction_hash']}")
        print(sep)
        print()
    elif chain_info and "error" in chain_info:
        print(f"\n  ⚠  Blockchain logging error: {chain_info['error']}\n")
    else:
        print("\n  ℹ  This wallet was NOT logged to blockchain (risk below threshold).\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_and_log.py <ethereum_wallet_address>")
        print()
        print("Examples:")
        print("  python analyze_and_log.py 0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A  # Fraud")
        print("  python analyze_and_log.py 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045  # Legit")
        sys.exit(1)

    wallet = sys.argv[1].strip()
    try:
        assessment = analyze_and_log(wallet)
        _print_full_report(wallet, assessment)
    except Exception as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
