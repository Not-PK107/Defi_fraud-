# DeFi Fraud Detection AI & On-Chain Logger

A full-stack Monorepo for detecting fraudulent Ethereum/DeFi wallets using Machine Learning (XGBoost), explaining the reasoning via SHAP, and permanently logging high-risk threats to the Sepolia Blockchain using Smart Contracts.

## 🚀 Features

- **Live On-Chain Data**: Pulls live normal transactions, ERC20 transfers, and ETH balances from Etherscan.
- **Machine Learning (AI)**: Converts raw blockchain data into 39 mathematical features and runs them through a highly accurate XGBoost fraud detection model.
- **Explainable AI (SHAP)**: Doesn't just flag a wallet as "Fraud" — uses SHAP to translate complex model influences into plain English to explain *why* the wallet was flagged.
- **Smart Contract Logging**: Automatically writes high-risk (Score > 70) wallets permanently onto the Ethereum Sepolia testnet via a deployed Solidity Smart Contract.
- **Monorepo Architecture**: Cleanly separates the `backend` (Python), `blockchain` (Solidity), `notebooks` (Data Science), and `frontend` (Web).

## 📂 Repository Structure

```
├── backend/            # Python API, Wallet Fetching, ML Prediction, Blockchain Logging
├── blockchain/         # Solidity Smart Contracts (FraudLogger.sol) & Datasets
├── notebooks/          # Data Science EDA, Model Training, Imputers
├── frontend/           # Web Interface (To be implemented)
├── .env.example        # Example environment variables required to run the project
└── .gitignore          # Git ignore file
```

## 🛠 Setup & Installation

**1. Clone the repository:**
```bash
git clone https://github.com/Not-PK107/Defi_fraud-.git
cd Defi_fraud-
```

**2. Setup a Python Virtual Environment:**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

**3. Install Dependencies:**
```bash
pip install pandas numpy xgboost shap joblib python-dotenv web3 requests
```

**4. Environment Variables:**
Create a `.env` file in the root directory based on `.env.example`:
```
ETHERSCAN_API_KEY=your_key
SEPOLIA_RPC_URL=your_rpc_url
PRIVATE_KEY=your_private_key
CONTRACT_ADDRESS=your_contract_address
```

## ⚡ Usage

Run the master orchestrator script to analyze a wallet, generate a SHAP report, and conditionally log it to the blockchain:

```bash
# Example: Testing a Fraud Wallet
python backend/analyze_and_log.py 0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A

# Example: Testing a Legitimate Wallet
python backend/analyze_and_log.py 0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe
```
