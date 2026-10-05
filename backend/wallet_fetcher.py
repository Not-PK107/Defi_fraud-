"""
wallet_fetcher.py
=================
Fetches real Ethereum wallet transaction data from Etherscan,
computes the 39 model features, and runs the fraud prediction.

Pipeline
--------
Wallet Address
    -> Etherscan API (normal transactions + ERC20 transactions + balance)
    -> Compute all 39 features
    -> predict_fraud_risk()
    -> Print full fraud assessment

Usage
-----
    cd C:\\Users\\PK\\OneDrive\\Desktop\\defi
    .\\venv\\Scripts\\python.exe backend\\wallet_fetcher.py <wallet_address>

Example
-------
    .\\venv\\Scripts\\python.exe backend\\wallet_fetcher.py 0xABC123...
"""

import os
import sys
import time
import requests
import numpy as np
import pandas as pd
import shap
import joblib
from pathlib import Path
from dotenv import load_dotenv

# ---- Model artifacts path ----
_MODEL_DIR = Path(__file__).resolve().parent.parent / "notebooks" / "models"

# ---- Make sure the project root is on the Python path ----
_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from backend.blacklist_checker import check_blacklist

# ---- Load environment variables (.env file) ----
load_dotenv(_PROJECT_ROOT / ".env")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_BASE = "https://api.etherscan.io/v2/api"

# ---- ETH unit conversion ----
WEI_TO_ETH = 1e-18


# ---------------------------------------------------------------------------
# Step 1: Fetch data from Etherscan
# ---------------------------------------------------------------------------

def _etherscan_get(params: dict) -> dict:
    """Make a single Etherscan API request and return the JSON response."""
    params["chainid"] = "1"
    params["apikey"] = ETHERSCAN_API_KEY
    try:
        resp = requests.get(ETHERSCAN_BASE, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise ConnectionError(f"Etherscan request failed: {e}") from e


def fetch_normal_transactions(address: str) -> list:
    """Return all normal ETH transactions for a wallet address."""
    data = _etherscan_get({
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
    })
    if data.get("status") == "1":
        return data["result"]
    # status 0 can mean no transactions (not necessarily an error)
    return []


def fetch_erc20_transactions(address: str) -> list:
    """Return all ERC20 token transactions for a wallet address."""
    # Brief pause to respect Etherscan free-tier rate limit (5 req/s)
    time.sleep(0.25)
    data = _etherscan_get({
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
    })
    if data.get("status") == "1":
        return data["result"]
    return []


def fetch_eth_balance(address: str) -> float:
    """Return the current ETH balance for a wallet address."""
    time.sleep(0.25)
    data = _etherscan_get({
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
    })
    if data.get("status") == "1":
        return float(data["result"]) * WEI_TO_ETH
    return 0.0


# ---------------------------------------------------------------------------
# Step 2: Compute all 39 model features from raw transaction data
# ---------------------------------------------------------------------------

def _avg_min_between(txs: list) -> float:
    """Average time in minutes between consecutive transactions."""
    timestamps = sorted(int(tx["timeStamp"]) for tx in txs)
    if len(timestamps) < 2:
        return 0.0
    diffs = [(timestamps[i + 1] - timestamps[i]) / 60.0
             for i in range(len(timestamps) - 1)]
    return float(np.mean(diffs))


def _safe_min(vals):
    return float(min(vals)) if vals else 0.0

def _safe_max(vals):
    return float(max(vals)) if vals else 0.0

def _safe_mean(vals):
    return float(np.mean(vals)) if vals else 0.0


def compute_features(address: str,
                     normal_txs: list,
                     erc20_txs: list,
                     balance: float) -> dict:
    """
    Compute the exact 39 features the XGBoost model was trained on.

    Parameters
    ----------
    address    : wallet address (checksummed or lowercase)
    normal_txs : list of normal transaction dicts from Etherscan
    erc20_txs  : list of ERC20 token transaction dicts from Etherscan
    balance    : current ETH balance in ETH (not Wei)

    Returns
    -------
    dict of feature_name -> value  (NaN where appropriate)
    """
    addr = address.lower()

    # ------------------------------------------------------------------ #
    # Normal transaction partitions
    # ------------------------------------------------------------------ #
    sent_txs = [tx for tx in normal_txs if tx["from"].lower() == addr]
    recv_txs = [tx for tx in normal_txs if tx["to"].lower() == addr]

    # Contract creation: tx["to"] is empty string
    contract_create_txs = [tx for tx in sent_txs if tx.get("to", "") == ""]

    # Sent to an existing contract: has non-trivial input data
    sent_to_contract_txs = [
        tx for tx in sent_txs
        if tx.get("to", "") != "" and tx.get("input", "0x") not in ("0x", "")
    ]

    # ------------------------------------------------------------------ #
    # Counts
    # ------------------------------------------------------------------ #
    sent_count  = len(sent_txs)
    recv_count  = len(recv_txs)
    contract_count = len(contract_create_txs)
    total_txs   = len(normal_txs)

    # ------------------------------------------------------------------ #
    # Unique addresses
    # ------------------------------------------------------------------ #
    unique_recv_from = len({tx["from"].lower() for tx in recv_txs})
    unique_sent_to   = len({tx["to"].lower()   for tx in sent_txs if tx.get("to")})

    # ------------------------------------------------------------------ #
    # Time features
    # ------------------------------------------------------------------ #
    avg_min_sent = _avg_min_between(sent_txs)
    avg_min_recv = _avg_min_between(recv_txs)

    if normal_txs:
        ts_all = sorted(int(tx["timeStamp"]) for tx in normal_txs)
        time_diff_first_last = (ts_all[-1] - ts_all[0]) / 60.0
    else:
        time_diff_first_last = 0.0

    # ------------------------------------------------------------------ #
    # ETH value features (convert Wei -> ETH)
    # ------------------------------------------------------------------ #
    recv_vals             = [float(tx["value"]) * WEI_TO_ETH for tx in recv_txs]
    sent_vals             = [float(tx["value"]) * WEI_TO_ETH for tx in sent_txs]
    sent_to_contract_vals = [float(tx["value"]) * WEI_TO_ETH for tx in sent_to_contract_txs]

    # Filter zero-value transactions for min/max/avg (mirrors dataset behaviour)
    recv_vals_nonzero             = [v for v in recv_vals             if v > 0]
    sent_vals_nonzero             = [v for v in sent_vals             if v > 0]
    sent_to_contract_vals_nonzero = [v for v in sent_to_contract_vals if v > 0]

    min_val_recv = _safe_min(recv_vals_nonzero)
    max_val_recv = _safe_max(recv_vals_nonzero)
    avg_val_recv = _safe_mean(recv_vals_nonzero)

    min_val_sent = _safe_min(sent_vals_nonzero)
    max_val_sent = _safe_max(sent_vals_nonzero)
    avg_val_sent = _safe_mean(sent_vals_nonzero)

    min_val_sent_contract = _safe_min(sent_to_contract_vals_nonzero)
    max_val_sent_contract = _safe_max(sent_to_contract_vals_nonzero)
    avg_val_sent_contract = _safe_mean(sent_to_contract_vals_nonzero)

    total_eth_sent          = sum(sent_vals)
    total_eth_recv          = sum(recv_vals)
    total_eth_sent_contracts = sum(sent_to_contract_vals)

    # ------------------------------------------------------------------ #
    # ERC20 features
    # ------------------------------------------------------------------ #
    erc20_missing = 1 if not erc20_txs else 0

    if not erc20_missing:
        erc20_sent = [tx for tx in erc20_txs if tx["from"].lower() == addr]
        erc20_recv = [tx for tx in erc20_txs if tx["to"].lower()   == addr]

        # ERC20 tokens sent TO contracts (contractAddress in tx is the token contract)
        # "sent contract" means the token transfer goes to a contract, not an EOA.
        # We approximate this as transfers where the token contract itself is the destination.
        erc20_sent_to_contract = erc20_sent   # conservative — treat all sent as potentially to contract

        erc20_total = len(erc20_txs)

        def erc20_value(tx):
            """Convert ERC20 raw value to human-readable units."""
            decimals = int(tx.get("tokenDecimal") or 18)
            return float(tx.get("value", 0)) / (10 ** decimals)

        erc20_recv_vals = [erc20_value(tx) for tx in erc20_recv]
        erc20_sent_vals = [erc20_value(tx) for tx in erc20_sent]
        erc20_sent_contract_vals = [erc20_value(tx) for tx in erc20_sent_to_contract]

        erc20_total_recv          = sum(erc20_recv_vals)
        erc20_total_sent          = sum(erc20_sent_vals)
        erc20_total_sent_contract = sum(erc20_sent_contract_vals)

        # Unique addresses
        # "ERC20 uniq sent addr"   = unique wallet addresses this wallet sent ERC20 to
        # "ERC20 uniq sent addr.1" = unique token contract addresses used when sending
        erc20_uniq_sent_addr  = len({tx["to"].lower()               for tx in erc20_sent})
        erc20_uniq_recv_addr  = len({tx["from"].lower()             for tx in erc20_recv})
        erc20_uniq_sent_addr1 = len({tx["contractAddress"].lower()  for tx in erc20_sent
                                     if tx.get("contractAddress")})
        erc20_uniq_recv_contract_addr = len({tx["contractAddress"].lower() for tx in erc20_recv
                                             if tx.get("contractAddress")})

        # ERC20 value stats
        erc20_recv_vals_nz = [v for v in erc20_recv_vals if v > 0]
        erc20_sent_vals_nz = [v for v in erc20_sent_vals if v > 0]
        erc20_sent_contract_vals_nz = [v for v in erc20_sent_contract_vals if v > 0]

        erc20_min_val_rec  = _safe_min(erc20_recv_vals_nz)
        erc20_max_val_rec  = _safe_max(erc20_recv_vals_nz)
        erc20_avg_val_rec  = _safe_mean(erc20_recv_vals_nz)
        erc20_min_val_sent = _safe_min(erc20_sent_vals_nz)
        erc20_max_val_sent = _safe_max(erc20_sent_vals_nz)
        erc20_avg_val_sent = _safe_mean(erc20_sent_vals_nz)
        erc20_min_val_sent_contract = _safe_min(erc20_sent_contract_vals_nz)
        erc20_max_val_sent_contract = _safe_max(erc20_sent_contract_vals_nz)
        erc20_avg_val_sent_contract = _safe_mean(erc20_sent_contract_vals_nz)

        # ERC20 average time between transactions (in minutes)
        erc20_avg_time_sent      = _avg_min_between(erc20_sent)
        erc20_avg_time_recv      = _avg_min_between(erc20_recv)
        erc20_avg_time_recv2     = _avg_min_between(erc20_recv)  # mirror of recv
        erc20_avg_time_contract  = _avg_min_between(erc20_sent_to_contract)

        # Unique token names
        erc20_uniq_sent_token = len({tx.get("tokenSymbol", "") for tx in erc20_sent})
        erc20_uniq_recv_token = len({tx.get("tokenSymbol", "") for tx in erc20_recv})

    else:
        # No ERC20 activity — use NaN so the imputer fills with training medians
        erc20_total = np.nan
        erc20_total_recv = np.nan
        erc20_total_sent = np.nan
        erc20_total_sent_contract = np.nan
        erc20_uniq_sent_addr = np.nan
        erc20_uniq_recv_addr = np.nan
        erc20_uniq_sent_addr1 = np.nan
        erc20_uniq_recv_contract_addr = np.nan
        erc20_min_val_rec = np.nan
        erc20_max_val_rec = np.nan
        erc20_avg_val_rec = np.nan
        erc20_min_val_sent = np.nan
        erc20_max_val_sent = np.nan
        erc20_avg_val_sent = np.nan
        erc20_min_val_sent_contract = np.nan
        erc20_max_val_sent_contract = np.nan
        erc20_avg_val_sent_contract = np.nan
        erc20_avg_time_sent = np.nan
        erc20_avg_time_recv = np.nan
        erc20_avg_time_recv2 = np.nan
        erc20_avg_time_contract = np.nan
        erc20_uniq_sent_token = np.nan
        erc20_uniq_recv_token = np.nan

    # ------------------------------------------------------------------ #
    # Assemble the 50-feature dict (39 original + 11 new)
    # ------------------------------------------------------------------ #
    return {
        "Avg min between sent tnx":                          avg_min_sent,
        "Avg min between received tnx":                      avg_min_recv,
        "Time Diff between first and last (Mins)":           time_diff_first_last,
        "Sent tnx":                                          sent_count,
        "Received Tnx":                                      recv_count,
        "Number of Created Contracts":                       contract_count,
        "Unique Received From Addresses":                    unique_recv_from,
        "Unique Sent To Addresses":                          unique_sent_to,
        "min value received":                                min_val_recv,
        "max value received":                                max_val_recv,
        "avg val received":                                  avg_val_recv,
        "min val sent":                                      min_val_sent,
        "max val sent":                                      max_val_sent,
        "avg val sent":                                      avg_val_sent,
        "min value sent to contract":                        min_val_sent_contract,
        "max val sent to contract":                          max_val_sent_contract,
        "avg value sent to contract":                        avg_val_sent_contract,
        "total transactions (including tnx to create contract": total_txs,
        "total Ether sent":                                  total_eth_sent,
        "total ether received":                              total_eth_recv,
        "total ether sent contracts":                        total_eth_sent_contracts,
        "total ether balance":                               balance,
        "Total ERC20 tnxs":                                  erc20_total,
        "ERC20 total Ether received":                        erc20_total_recv,
        "ERC20 total ether sent":                            erc20_total_sent,
        "ERC20 total Ether sent contract":                   erc20_total_sent_contract,
        "ERC20 uniq sent addr":                              erc20_uniq_sent_addr,
        "ERC20 uniq rec addr":                               erc20_uniq_recv_addr,
        "ERC20 uniq sent addr.1":                            erc20_uniq_sent_addr1,
        "ERC20 uniq rec contract addr":                      erc20_uniq_recv_contract_addr,
        "ERC20 avg time between sent tnx":                   erc20_avg_time_sent,
        "ERC20 avg time between rec tnx":                    erc20_avg_time_recv,
        "ERC20 avg time between rec 2 tnx":                  erc20_avg_time_recv2,
        "ERC20 avg time between contract tnx":               erc20_avg_time_contract,
        "ERC20 min val rec":                                 erc20_min_val_rec,
        "ERC20 max val rec":                                 erc20_max_val_rec,
        "ERC20 avg val rec":                                 erc20_avg_val_rec,
        "ERC20 min val sent":                                erc20_min_val_sent,
        "ERC20 max val sent":                                erc20_max_val_sent,
        "ERC20 avg val sent":                                erc20_avg_val_sent,
        "ERC20 min val sent contract":                       erc20_min_val_sent_contract,
        "ERC20 max val sent contract":                       erc20_max_val_sent_contract,
        "ERC20 avg val sent contract":                       erc20_avg_val_sent_contract,
        "ERC20 uniq sent token name":                        erc20_uniq_sent_token,
        "ERC20 uniq rec token name":                         erc20_uniq_recv_token,
        "ERC20_data_missing":                                erc20_missing,
        # --- 5 new engineered features ---
        "sent_recv_ratio":    sent_count / (recv_count + 1),
        "eth_velocity":       total_eth_sent / (total_eth_recv + 1e-9),
        "balance_retention":  balance / (total_eth_recv + 1e-9),
        "recv_concentration": unique_recv_from / (recv_count + 1),
        "erc20_engagement":   (erc20_total if not np.isnan(erc20_total) else 0) / (total_txs + 1),
    }


# ---------------------------------------------------------------------------
# Step 3: SHAP Explainability
# ---------------------------------------------------------------------------

def explain_with_shap(processed_df: pd.DataFrame, top_n: int = 8) -> list:
    """
    Compute SHAP values for a single preprocessed wallet feature row.

    Parameters
    ----------
    processed_df : pd.DataFrame  One-row DataFrame (already imputed, in model column order)
    top_n        : int           Number of top features to return

    Returns
    -------
    List of dicts: [{feature, shap_value, direction, display}, ...]
    sorted by absolute SHAP value descending.
    """
    model = joblib.load(_MODEL_DIR / "fraud_model.pkl")
    feature_columns = joblib.load(_MODEL_DIR / "feature_columns.pkl")

    # Clean infinity values and cap to float32 max to prevent SHAP DMatrix crashes
    # (Some spam tokens send uint256.max which is ~1e59 and exceeds float32 limits)
    processed_df = processed_df.replace([np.inf, -np.inf], np.nan)
    processed_df = processed_df.astype(float).clip(lower=-3.4e38, upper=3.4e38)

    # Use TreeExplainer — fastest and most accurate for XGBoost
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(processed_df)

    # shap_values shape: (1, n_features) — take the first (only) row
    values = shap_values[0]

    explanations = []
    for i, col in enumerate(feature_columns):
        sv = float(values[i])
        explanations.append({
            "feature": col,
            "shap_value": sv,
            "direction": "towards FRAUD" if sv > 0 else "towards LEGIT",
            "display": f"+{sv:.4f}" if sv > 0 else f"{sv:.4f}",
        })

    # Sort by magnitude (most influential first)
    explanations.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    return explanations[:top_n]


# ---------------------------------------------------------------------------
# Step 4: Full pipeline — address -> prediction
# ---------------------------------------------------------------------------

def analyze_wallet(address: str) -> dict:
    """
    Full pipeline: fetch live data for a wallet and return its fraud assessment
    including SHAP explainability.

    Parameters
    ----------
    address : str  Ethereum wallet address (0x...)

    Returns
    -------
    dict with keys: prediction, fraud_probability, risk_score,
                    risk_level, recommendation, features_used, shap_explanation
    """
    from backend.predictor import predict_fraud_risk

    if not ETHERSCAN_API_KEY:
        raise ValueError(
            "ETHERSCAN_API_KEY is missing from .env. "
            "Get a free key at https://etherscan.io/myapikey"
        )

    print(f"Fetching data for wallet: {address}")
    print("  [1/4] Fetching normal transactions...")
    normal_txs = fetch_normal_transactions(address)
    print(f"        Found {len(normal_txs)} normal transactions")

    print("  [2/4] Fetching ERC20 transactions...")
    erc20_txs = fetch_erc20_transactions(address)
    print(f"        Found {len(erc20_txs)} ERC20 transactions")

    print("  [3/4] Fetching ETH balance...")
    balance = fetch_eth_balance(address)
    print(f"        Balance: {balance:.6f} ETH")

    print()
    print("Checking blacklist...")
    blacklist_result = check_blacklist(address)

    print("Computing features...")
    features = compute_features(address, normal_txs, erc20_txs, balance)

    print("Running ML prediction...")
    result = predict_fraud_risk(features)

    # ---- Override result if wallet is blacklisted (takes priority over ML) ---
    if blacklist_result["is_blacklisted"]:
        result["prediction"] = "FRAUD"
        result["risk_score"] = 100.0
        result["fraud_probability"] = 1.0
        result["risk_level"] = "CRITICAL"
        result["recommendation"] = "AVOID TRANSACTION"

    result["blacklist"] = blacklist_result

    # ---- SHAP explainability ------------------------------------------------
    print("Running SHAP explanation...")
    try:
        # Replicate the same preprocessing done in predictor.py
        feature_columns = joblib.load(_MODEL_DIR / "feature_columns.pkl")
        imputer = joblib.load(_MODEL_DIR / "median_imputer.pkl")
        raw_df = pd.DataFrame([features])
        raw_df.columns = raw_df.columns.str.strip()
        processed_df = raw_df.reindex(columns=feature_columns)
        processed_df = pd.DataFrame(
            imputer.transform(processed_df), columns=feature_columns
        )
        shap_explanation = explain_with_shap(processed_df)
    except Exception as e:
        shap_explanation = [{"feature": "SHAP error", "display": str(e),
                             "direction": "", "shap_value": 0.0}]

    result["features_used"] = features
    result["shap_explanation"] = shap_explanation
    return result


# ---------------------------------------------------------------------------
# CLI entry point — run directly: python wallet_fetcher.py <address>
# ---------------------------------------------------------------------------

LAYMAN_EXPLANATIONS = {
    "Avg min between sent tnx": "Average time between sending transactions",
    "Avg min between received tnx": "Average time between receiving transactions",
    "Time Diff between first and last (Mins)": "Account lifespan (time between first and last transaction)",
    "Sent tnx": "Total number of transactions sent",
    "Received Tnx": "Total number of transactions received",
    "Number of Created Contracts": "Number of smart contracts created by this wallet",
    "Unique Received From Addresses": "Number of unique addresses that sent money to this wallet",
    "Unique Sent To Addresses": "Number of unique addresses this wallet sent money to",
    "min value received": "Smallest amount of ETH received",
    "max value received": "Largest amount of ETH received",
    "avg val received": "Average amount of ETH received",
    "min val sent": "Smallest amount of ETH sent",
    "max val sent": "Largest amount of ETH sent",
    "avg val sent": "Average amount of ETH sent",
    "min value sent to contract": "Smallest amount of ETH sent to a smart contract",
    "max val sent to contract": "Largest amount of ETH sent to a smart contract",
    "avg value sent to contract": "Average amount of ETH sent to a smart contract",
    "total transactions (including tnx to create contract": "Total number of transactions (including contract creations)",
    "total Ether sent": "Total amount of ETH sent",
    "total ether received": "Total amount of ETH received",
    "total ether sent contracts": "Total amount of ETH sent to smart contracts",
    "total ether balance": "Current ETH balance",
    "Total ERC20 tnxs": "Total number of ERC20 token transactions",
    "ERC20 total Ether received": "Total value of ERC20 tokens received",
    "ERC20 total ether sent": "Total value of ERC20 tokens sent",
    "ERC20 total Ether sent contract": "Total value of ERC20 tokens sent to contracts",
    "ERC20 uniq sent addr": "Number of unique addresses this wallet sent ERC20 tokens to",
    "ERC20 uniq rec addr": "Number of unique addresses that sent ERC20 tokens to this wallet",
    "ERC20 uniq sent addr.1": "Number of unique ERC20 token contracts interacted with (sent)",
    "ERC20 uniq rec contract addr": "Number of unique ERC20 token contracts interacted with (received)",
    "ERC20 min val rec": "Smallest amount of ERC20 tokens received",
    "ERC20 max val rec": "Largest amount of ERC20 tokens received",
    "ERC20 avg val rec": "Average amount of ERC20 tokens received",
    "ERC20 min val sent": "Smallest amount of ERC20 tokens sent",
    "ERC20 max val sent": "Largest amount of ERC20 tokens sent",
    "ERC20 avg val sent": "Average amount of ERC20 tokens sent",
    "ERC20 uniq sent token name": "Number of different types of ERC20 tokens sent",
    "ERC20 uniq rec token name": "Number of different types of ERC20 tokens received",
    "ERC20_data_missing": "Wallet has never interacted with custom ERC20 tokens",
}

def _print_result(address: str, result: dict) -> None:
    """Print the full fraud assessment including SHAP explanation."""
    features = result.pop("features_used", {})
    shap_explanation = result.pop("shap_explanation", [])
    blacklist_info = result.pop("blacklist", None)
    result.pop("_processed_input", None)

    sep = "=" * 60
    print()
    print(sep)
    print("  DEFI FRAUD DETECTION - WALLET ANALYSIS")
    print(sep)
    print(f"  Wallet   : {address}")
    print(sep)

    # ---- Blacklist warning (shown prominently before the result) ----------
    if blacklist_info and blacklist_info.get("is_blacklisted"):
        print(f"  !! BLACKLIST ALERT !!")
        print(f"  Source    : {blacklist_info['source']}")
        print(f"  Reason    : {blacklist_info['reason']}")
        print(sep)

    label_icon = "FRAUD" if result["prediction"] == "FRAUD" else "LEGITIMATE"
    print(f"  Result        : {label_icon}")
    print(f"  Probability   : {result['fraud_probability']:.4f}  ({result['fraud_probability']*100:.2f}%)")
    print(f"  Risk Score    : {result['risk_score']} / 100")
    print(f"  Risk Level    : {result['risk_level']}")
    print(f"  Recommendation: {result['recommendation']}")
    print(sep)

    print()
    print("  KEY FEATURES COMPUTED FROM BLOCKCHAIN DATA")
    print("-" * 60)
    important = [
        "Sent tnx", "Received Tnx", "Time Diff between first and last (Mins)",
        "total ether balance", "total Ether sent", "total ether received",
        "Total ERC20 tnxs", "Unique Sent To Addresses",
        "Unique Received From Addresses", "ERC20_data_missing",
    ]
    for feat in important:
        val = features.get(feat, "N/A")
        if isinstance(val, float):
            print(f"  {feat:<45}: {val:.4f}")
        else:
            print(f"  {feat:<45}: {val}")

    # ---- SHAP Explanation section ------------------------------------------
    if shap_explanation:
        is_fraud = result["prediction"] == "FRAUD"

        # Filter: only keep features that agree with the final verdict
        if is_fraud:
            relevant = [x for x in shap_explanation if x["shap_value"] > 0]
            section_title = "  WHY THIS WALLET IS FLAGGED AS FRAUD"
            note = "  These features most strongly indicate fraudulent behaviour."
        else:
            relevant = [x for x in shap_explanation if x["shap_value"] < 0]
            section_title = "  WHY THIS WALLET IS CONSIDERED LEGITIMATE"
            note = "  These features most strongly indicate normal, legitimate behaviour."

        # Sort by absolute impact descending, show top 5
        relevant.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        relevant = relevant[:5]

        if relevant:
            print()
            print(sep)
            print(section_title)
            print(sep)
            for i, item in enumerate(relevant, 1):
                impact = abs(item["shap_value"])
                bar = "#" * min(int(impact * 15), 20)
                raw_feature = item['feature']
                friendly_name = LAYMAN_EXPLANATIONS.get(raw_feature, raw_feature)
                print(f"  {i}. {friendly_name}")
                print(f"     Influence: {impact:.4f}  [{bar}]")
            print()
            print(note)
    print()



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python wallet_fetcher.py <ethereum_wallet_address>")
        print()
        print("Example:")
        print("  python wallet_fetcher.py 0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE")
        sys.exit(1)

    wallet_address = sys.argv[1].strip()
    try:
        result = analyze_wallet(wallet_address)
        _print_result(wallet_address, result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
