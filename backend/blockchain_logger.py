"""Score Ethereum wallet features and optionally log fraud alerts on Sepolia."""

import os
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from web3 import Web3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "notebooks" / "models"
SEPOLIA_CHAIN_ID = 11155111

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "_walletAddress", "type": "address"},
            {"internalType": "uint256", "name": "_riskScore", "type": "uint256"},
            {"internalType": "string", "name": "_fraudCategory", "type": "string"},
        ],
        "name": "logFraud",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getFraudAlertCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def _environment_value(name: str) -> str:
    """Return a required environment value without exposing its contents."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is missing from the environment")
    return value


def load_prediction_artifacts():
    """Load the exact model, feature order, and imputer produced by training."""
    return (
        joblib.load(MODEL_DIR / "fraud_model.pkl"),
        joblib.load(MODEL_DIR / "feature_columns.pkl"),
        joblib.load(MODEL_DIR / "median_imputer.pkl"),
    )


def predict_fraud_risk(wallet_features: dict | pd.DataFrame, threshold: float = 0.50) -> dict:
    """Assess one wallet and return a deployment-ready fraud decision."""
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1")

    if isinstance(wallet_features, dict):
        wallet_frame = pd.DataFrame([wallet_features])
    elif isinstance(wallet_features, pd.DataFrame) and len(wallet_features) == 1:
        wallet_frame = wallet_features.copy()
    else:
        raise TypeError("wallet_features must be a dict or a one-row DataFrame")

    wallet_frame.columns = wallet_frame.columns.str.strip()
    if "ERC20_data_missing" not in wallet_frame.columns:
        if "Total ERC20 tnxs" not in wallet_frame.columns:
            raise ValueError("Provide Total ERC20 tnxs or ERC20_data_missing")
        wallet_frame["ERC20_data_missing"] = wallet_frame["Total ERC20 tnxs"].isna().astype(int)

    model, feature_columns, imputer = load_prediction_artifacts()
    missing_features = [
        feature for feature in feature_columns if feature not in wallet_frame.columns
    ]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")

    model_input = wallet_frame.reindex(columns=feature_columns)
    model_input = pd.DataFrame(
        imputer.transform(model_input), columns=feature_columns
    )
    probability = float(model.predict_proba(model_input)[0, 1])
    risk_score = round(probability * 100, 2)

    if risk_score <= 30:
        risk_level, recommendation = "LOW", "PROCEED"
    elif risk_score <= 70:
        risk_level, recommendation = "MEDIUM", "PROCEED WITH CAUTION"
    else:
        risk_level, recommendation = "HIGH", "AVOID TRANSACTION"

    return {
        "prediction": "FRAUD" if probability >= threshold else "LEGITIMATE",
        "fraud_probability": round(probability, 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
    }


def get_contract():
    """Connect to the configured Sepolia fraud-logger contract."""
    load_dotenv(PROJECT_ROOT / ".env")
    rpc_url = _environment_value("SEPOLIA_RPC_URL")
    contract_address = Web3.to_checksum_address(_environment_value("CONTRACT_ADDRESS"))

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise ConnectionError("Could not connect to Sepolia")
    return web3, web3.eth.contract(address=contract_address, abi=CONTRACT_ABI)


def log_fraud_on_chain(wallet_address: str, risk_score: float, fraud_category: str) -> dict:
    """Submit one confirmed fraud alert to Sepolia and return receipt metadata."""
    load_dotenv(PROJECT_ROOT / ".env")
    private_key = _environment_value("PRIVATE_KEY")
    web3, contract = get_contract()
    account = web3.eth.account.from_key(private_key)

    transaction = contract.functions.logFraud(
        Web3.to_checksum_address(wallet_address),
        int(round(risk_score)),
        fraud_category,
    ).build_transaction(
        {
            "from": account.address,
            "nonce": web3.eth.get_transaction_count(account.address),
            "chainId": SEPOLIA_CHAIN_ID,
            "gas": 300000,
            "maxFeePerGas": web3.to_wei(30, "gwei"),
            "maxPriorityFeePerGas": web3.to_wei(1, "gwei"),
        }
    )
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return {
        "transaction_hash": web3.to_hex(tx_hash),
        "block_number": receipt["blockNumber"],
        "status": receipt["status"],
    }


def predict_and_log_fraud(
    wallet_address: str,
    wallet_features: dict | pd.DataFrame,
    threshold: float = 0.50,
) -> dict:
    """Score a wallet and record every model assessment on-chain."""
    assessment = predict_fraud_risk(wallet_features, threshold)
    assessment["blockchain"] = log_fraud_on_chain(
        wallet_address,
        assessment["risk_score"],
        f"ML prediction: {assessment['prediction'].lower()} "
        f"({assessment['risk_level'].lower()} risk)",
    )
    return assessment


if __name__ == "__main__":
    web3, contract = get_contract()
    print("Connected to Sepolia. Chain ID:", web3.eth.chain_id)
    print("Fraud alerts stored:", contract.functions.getFraudAlertCount().call())
    print("No transaction was sent. Call predict_and_log_fraud(...) to assess a wallet.")
