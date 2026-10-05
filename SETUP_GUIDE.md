# 🛡️ DeFi Fraud Detection AI - Complete Setup Guide

A comprehensive guide to setting up and running the DeFi Fraud Detection system with the beautiful Classic Theme frontend.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)
8. [Features Overview](#features-overview)

---

## Prerequisites

### Required Software
- **Python 3.8+** (Recommended: Python 3.10 or 3.11)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Modern web browser** (Chrome, Firefox, Edge, Safari)

### Required API Keys
- **Etherscan API Key** (Free tier available)
- **Ethereum Sepolia RPC URL** (Infura, Alchemy, or any provider)
- **Ethereum Wallet Private Key** (for blockchain logging)

---

## Quick Start

### 1. Clone & Navigate
```bash
cd Defi_fraud-
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy the example environment file
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Mac/Linux
```

Edit `.env` file with your credentials:
```env
ETHERSCAN_API_KEY=your_etherscan_api_key_here
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/your_project_id
PRIVATE_KEY=your_wallet_private_key_here
CONTRACT_ADDRESS=your_deployed_contract_address_here
```

### 5. Launch the Server
```bash
python backend/server.py
```

### 6. Open Your Browser
Navigate to: **http://localhost:5000**

🎉 **You're ready to analyze wallets!**

---

## Detailed Installation

### Step 1: Get API Keys

#### Etherscan API Key
1. Visit: https://etherscan.io/register
2. Create a free account
3. Navigate to: https://etherscan.io/myapikey
4. Create a new API key
5. Copy the API key

#### Sepolia RPC URL (Infura)
1. Visit: https://infura.io/register
2. Create a free account
3. Create a new project
4. Select "Ethereum" → "Sepolia" network
5. Copy the HTTPS endpoint URL

#### Alternative RPC Providers
- **Alchemy**: https://www.alchemy.com/
- **QuickNode**: https://www.quicknode.com/
- **Public RPC**: https://sepolia.infura.io/v3/

#### Ethereum Wallet Setup
1. Install MetaMask: https://metamask.io/
2. Create a new wallet or use existing
3. Switch to Sepolia Testnet
4. Get test ETH from faucet: https://sepoliafaucet.com/
5. Export private key (Settings → Security & Privacy → Reveal Private Key)

**⚠️ WARNING: Never use a wallet with real funds! Create a dedicated wallet for testing.**

### Step 2: Deploy Smart Contract (Optional)

If you want to log fraud alerts on-chain:

1. Install Hardhat or Remix IDE
2. Deploy `blockchain/FraudLogger.sol` to Sepolia
3. Copy the deployed contract address
4. Add to `.env` file

**Quick Deploy with Remix:**
1. Visit: https://remix.ethereum.org/
2. Create new file: `FraudLogger.sol`
3. Paste contract code from `blockchain/FraudLogger.sol`
4. Compile (Solidity 0.8.20)
5. Deploy to Sepolia via MetaMask
6. Copy contract address

### Step 3: Verify Models

Ensure ML model files exist in `notebooks/models/`:
- `fraud_model.pkl` - Trained XGBoost model
- `feature_columns.pkl` - Feature order specification
- `median_imputer.pkl` - Data preprocessing transformer

If missing, run the training notebook:
```bash
jupyter notebook notebooks/01_EDA.ipynb
```

---

## Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `ETHERSCAN_API_KEY` | Etherscan API key for transaction data | Yes | `ABC123XYZ...` |
| `SEPOLIA_RPC_URL` | Ethereum Sepolia RPC endpoint | Yes | `https://sepolia.infura.io/v3/...` |
| `PRIVATE_KEY` | Wallet private key for signing transactions | Yes* | `0x1234...` |
| `CONTRACT_ADDRESS` | Deployed FraudLogger contract address | Yes* | `0xabcd...` |

*Required only if using blockchain logging features

### Frontend Configuration

Edit `frontend/app.js` to customize:

```javascript
const STATE = {
  apiEndpoint: "http://localhost:5000",  // Change if hosting elsewhere
  // ... other settings
};
```

### Backend Configuration

Edit `backend/server.py` to customize:

```python
app.run(
    host='0.0.0.0',      # Change to '127.0.0.1' for localhost only
    port=5000,           # Change port if needed
    debug=True,          # Set to False in production
    threaded=True
)
```

---

## Running the Application

### Method 1: Full Stack (Recommended)

Run the Flask server with integrated frontend:

```bash
python backend/server.py
```

Then open: **http://localhost:5000**

### Method 2: Frontend Only (Demo Mode)

Open `frontend/index.html` directly in your browser. The frontend includes a built-in simulation engine that works offline!

### Method 3: Python CLI Analysis

Analyze wallets directly from command line:

```bash
# Quick analysis
python backend/wallet_fetcher.py 0xYourWalletAddressHere

# Analysis with blockchain logging
python backend/analyze_and_log.py 0xYourWalletAddressHere
```

---

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "backend": "operational",
  "blockchain": {
    "status": "connected",
    "network": "sepolia",
    "chain_id": 11155111,
    "alerts_stored": 125
  },
  "ml_models": "loaded"
}
```

#### 2. Analyze Wallet
```http
POST /api/analyze
Content-Type: application/json

{
  "address": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"
}
```

**Response:**
```json
{
  "wallet": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A",
  "prediction": "FRAUD",
  "fraud_probability": 0.9864,
  "risk_score": 98.64,
  "risk_level": "HIGH",
  "recommendation": "AVOID TRANSACTION",
  "features_used": { ... },
  "shap_explanation": [ ... ],
  "blockchain": {
    "transaction_hash": "0x8f2d9c...",
    "block_number": 6842109,
    "status": 1
  }
}
```

#### 3. Get Blockchain Status
```http
GET /api/blockchain/status
```

**Response:**
```json
{
  "connected": true,
  "network": "sepolia",
  "chain_id": 11155111,
  "block_number": 6842150,
  "contract_address": "0xb797682C896f6004B76f75fcf9589dD67634f19e",
  "total_alerts": 125
}
```

#### 4. Get Recent Alerts
```http
GET /api/alerts
```

**Response:**
```json
{
  "total_alerts": 125,
  "recent_alerts": [
    {
      "index": 124,
      "wallet_address": "0x1da5821...",
      "risk_score": 99,
      "fraud_category": "ML:fraud prob=0.9998",
      "timestamp": 1727533330,
      "reported_by": "0x4A13b82...",
      "block_explorer_url": "https://sepolia.etherscan.io/address/0x1da5821..."
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
**Error:** `Address already in use`

**Solution:**
```bash
# Windows - Find process using port 5000
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Mac/Linux
lsof -i :5000
kill -9 <process_id>

# Or change port in server.py
```

#### 2. Missing Dependencies
**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt

# Or install individually
pip install flask flask-cors web3 pandas numpy xgboost shap
```

#### 3. Etherscan API Rate Limit
**Error:** `Rate limit exceeded`

**Solution:**
- Wait 1 second between requests (built-in delays)
- Upgrade to paid Etherscan plan
- Use multiple API keys (rotate them)

#### 4. Blockchain Connection Failed
**Error:** `Could not connect to Sepolia`

**Solution:**
- Check RPC URL is correct
- Verify internet connection
- Try alternative RPC provider
- Check Infura project status

#### 5. Model Files Not Found
**Error:** `FileNotFoundError: fraud_model.pkl`

**Solution:**
```bash
# Ensure you're in project root
cd Defi_fraud-

# Check model files exist
ls notebooks/models/

# If missing, train models using notebook
jupyter notebook notebooks/01_EDA.ipynb
```

#### 6. Private Key Invalid
**Error:** `Invalid private key format`

**Solution:**
- Ensure private key starts with `0x`
- Remove any spaces or newlines
- Verify it's 66 characters (including 0x)
- Never share or commit your private key!

---

## Features Overview

### 🎯 Core Features

#### 1. **Live Wallet Analysis**
- Fetches real transaction data from Etherscan
- Computes 39 behavioral features
- ML-powered fraud detection (XGBoost)
- Real-time risk scoring (0-100)

#### 2. **Explainable AI (SHAP)**
- Shows WHY a wallet was flagged
- Feature importance breakdown
- Plain-English explanations
- Visual contribution bars

#### 3. **Blockchain Logging**
- Permanent on-chain fraud records
- Smart contract integration (Sepolia)
- Immutable audit trail
- Etherscan verification links

#### 4. **Interactive Dashboard**
- Beautiful classic theme UI
- Dark/Light mode toggle
- Responsive mobile design
- Real-time animations

#### 5. **What-If Simulator**
- Adjust features with sliders
- See live ML predictions
- Understand model behavior
- Educational tool

### 🚀 Enhanced Features

#### 6. **Notification System**
- Real-time toast notifications
- Success/warning/error alerts
- Sound notifications (optional)
- Non-intrusive design

#### 7. **Analytics Dashboard**
- Track scan history
- View statistics
- Export data to JSON
- Risk detection metrics

#### 8. **Bulk Analysis**
- Analyze multiple wallets at once
- Batch processing
- Export results to CSV
- Progress tracking

#### 9. **Sample Wallets**
- Pre-loaded known fraud cases
- Verified clean wallets
- One-click testing
- Educational examples

#### 10. **Export & Reports**
- Generate audit certificates
- Print-friendly format
- PDF export ready
- Professional formatting

---

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| Opera | 76+ | ✅ Fully Supported |

---

## Performance

- **Analysis Time:** 3-8 seconds (depends on transaction history)
- **ML Inference:** <50ms
- **Blockchain Logging:** 10-30 seconds (gas-dependent)
- **Frontend Load:** <1 second
- **API Response:** 50-200ms (cached features)

---

## Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use dedicated test wallet** - Don't risk real funds
3. **Rotate API keys regularly** - Free tier limits
4. **Enable CORS only for known origins** - Production security
5. **Use HTTPS in production** - Encrypt traffic
6. **Sanitize user inputs** - Prevent injection attacks
7. **Rate limit API endpoints** - Prevent abuse

---

## Production Deployment

### Deploy to Heroku

1. Create `Procfile`:
```
web: gunicorn backend.server:app
```

2. Install Gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku config:set ETHERSCAN_API_KEY=your_key
heroku config:set SEPOLIA_RPC_URL=your_url
heroku open
```

### Deploy to Vercel/Netlify (Frontend Only)

1. Build static frontend
2. Deploy `frontend/` folder
3. Configure API endpoint to point to backend

### Deploy to AWS/Azure/GCP

Use Docker container or direct Python deployment

---

## Support & Contributing

- **Issues**: Report bugs via GitHub Issues
- **Feature Requests**: Submit via GitHub Discussions
- **Pull Requests**: Contributions welcome!
- **Documentation**: Help improve this guide

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- **XGBoost Team** - ML framework
- **Etherscan** - Blockchain data API
- **Web3.py** - Ethereum integration
- **SHAP** - Model explainability
- **Flask** - Web framework

---

## Contact

For questions or support:
- GitHub: [Your Repository]
- Email: [Your Email]
- Twitter: [Your Twitter]

---

**Built with ❤️ for the Ethereum and DeFi community**

🛡️ **Stay Safe. Stay Vigilant. Detect Fraud.**
