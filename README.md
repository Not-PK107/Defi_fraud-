# DeFi Fraud Detection AI & On-Chain Logger

A full-stack application for detecting fraudulent Ethereum/DeFi wallets using Machine Learning (XGBoost), explaining predictions via SHAP, and permanently logging high-risk threats to the Sepolia Blockchain using Smart Contracts.

## 🎨 Beautiful Classic Theme Frontend

![Frontend Demo](https://img.shields.io/badge/Frontend-Classic%20Theme-gold)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![ML](https://img.shields.io/badge/ML-XGBoost-green)
![Blockchain](https://img.shields.io/badge/Blockchain-Sepolia-purple)

### ✨ Key Features

#### 🎯 **Core Functionality**
- **Live On-Chain Data**: Pulls live normal transactions, ERC20 transfers, and ETH balances from Etherscan API
- **Machine Learning (AI)**: Converts raw blockchain data into 39 mathematical features and runs them through a highly accurate XGBoost fraud detection model
- **Explainable AI (SHAP)**: Doesn't just flag a wallet as "Fraud" — uses SHAP to translate complex model influences into plain English explanations
- **Smart Contract Logging**: Automatically writes high-risk (Score > 70) wallets permanently onto the Ethereum Sepolia testnet
- **Beautiful UI**: Stunning classic theme with dark/light modes, animations, and responsive design

#### 🚀 **Enhanced Features**
- **📊 Analytics Dashboard**: Track your scan history, view statistics, and export data
- **🔔 Real-time Notifications**: Toast notifications for analysis results with sound effects
- **📋 Bulk Analysis**: Analyze multiple wallets at once and export results to CSV
- **🧪 What-If Simulator**: Interactive sliders to test how feature changes affect fraud scores
- **📱 Progressive Web App**: Install as a mobile/desktop app with offline capabilities
- **⚖️ Side-by-Side Comparison**: Compare fraud vs legitimate wallets visually
- **📜 Audit Certificates**: Generate and export professional PDF-ready audit reports
- **⌨️ Keyboard Shortcuts**: Quick access with Ctrl+Enter, Ctrl+K, and more

## 🚀 Quick Start

### Option 1: Automated Start (Recommended)

**Windows:**
```bash
start.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env  # Edit with your API keys

# 5. Start server
python backend/server.py
```

Then open: **http://localhost:5000**

### Option 3: Frontend Only (Demo Mode)

Simply open `frontend/index.html` in your browser. Works offline with built-in simulation engine!

## 📂 Repository Structure

```
├── backend/                  # Python API, ML Models, Blockchain Integration
│   ├── server.py            # Flask web server with REST API
│   ├── predictor.py         # ML prediction engine
│   ├── wallet_fetcher.py    # Etherscan API integration
│   ├── blockchain_logger.py # Smart contract interaction
│   ├── analyze_and_log.py   # Complete pipeline
│   └── test_predictor.py    # Unit tests
├── blockchain/              # Solidity Smart Contracts & Datasets
│   ├── FraudLogger.sol      # On-chain fraud logging contract
│   └── dataset/             # Training data
├── notebooks/               # Data Science & Model Training
│   ├── 01_EDA.ipynb         # Exploratory analysis & training
│   └── models/              # Trained ML artifacts
│       ├── fraud_model.pkl
│       ├── feature_columns.pkl
│       └── median_imputer.pkl
├── frontend/                # Beautiful Classic Theme Web Interface
│   ├── index.html           # Main application page
│   ├── app.js               # Core application logic
│   ├── styles.css           # Classic theme styles
│   ├── enhanced-features.js # Advanced features
│   ├── enhanced-styles.css  # Enhanced styling
│   ├── sample_data.js       # Demo data & feature metadata
│   ├── manifest.json        # PWA configuration
│   └── README.md            # Frontend documentation
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── SETUP_GUIDE.md           # Detailed setup instructions
├── start.bat                # Windows quick start script
└── start.sh                 # Mac/Linux quick start script
```

## 🛠 Setup & Installation

### Prerequisites
- Python 3.8+ (Recommended: 3.10 or 3.11)
- Etherscan API Key (free tier available)
- Ethereum Sepolia RPC URL (Infura, Alchemy, etc.)
- Ethereum wallet with test ETH (for blockchain logging)

### Detailed Setup

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for comprehensive installation instructions, including:
- Step-by-step setup process
- API key acquisition
- Smart contract deployment
- Troubleshooting guide
- Production deployment tips

## ⚡ Usage

### Web Interface (Recommended)

1. **Start the server:**
   ```bash
   python backend/server.py
   ```

2. **Open browser:**
   Navigate to `http://localhost:5000`

3. **Analyze a wallet:**
   - Enter wallet address (0x...)
   - Or click a sample wallet chip
   - View results in beautiful dashboard

### Command Line Interface

**Quick analysis:**
```bash
python backend/wallet_fetcher.py 0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A
```

**Analysis with blockchain logging:**
```bash
python backend/analyze_and_log.py 0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A
```

### API Endpoints

```bash
# Health check
GET http://localhost:5000/api/health

# Analyze wallet
POST http://localhost:5000/api/analyze
Content-Type: application/json
{"address": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"}

# Get blockchain status
GET http://localhost:5000/api/blockchain/status

# Get recent alerts
GET http://localhost:5000/api/alerts
```

## 🎨 Frontend Features

### Classic Theme Design
- **Dark Mode**: Obsidian background with burnished gold accents
- **Light Mode**: Parchment background with brass accents
- **Responsive**: Perfect on mobile, tablet, and desktop
- **Animations**: Smooth transitions and loading states

### Interactive Components
- **Tachometer Gauge**: Animated SVG risk meter (0-100)
- **SHAP Explanations**: Visual feature importance bars
- **39-Feature Ledger**: Searchable, filterable feature grid
- **What-If Simulator**: Real-time ML predictions with sliders

### Advanced Tools
- **Analytics Dashboard**: Track scan history and statistics
- **Bulk Analysis**: Process multiple wallets simultaneously
- **Export Features**: PDF certificates and CSV data export
- **Keyboard Shortcuts**: 
  - `Ctrl/Cmd + Enter` - Analyze wallet
  - `Ctrl/Cmd + K` - Focus search
  - `Esc` - Close modals

## 🔬 Machine Learning Model

### Features (39 Total)
- **Transaction Patterns**: Frequency, intervals, volumes
- **Counterparty Analysis**: Unique addresses, diversity
- **ETH Dynamics**: Sent/received amounts, balances
- **ERC-20 Activity**: Token transfers, contract interactions

### Model Performance
- **Algorithm**: XGBoost Gradient Boosting
- **Accuracy**: 98%+ on test set
- **Inference Time**: <50ms
- **Explainability**: SHAP values for every prediction

### Risk Scoring
- **0-29**: LOW RISK → Proceed
- **30-69**: MEDIUM RISK → Proceed with caution
- **70-100**: HIGH RISK → Avoid transaction

## ⛓ Blockchain Integration

### Smart Contract (Sepolia)
- **Contract**: `FraudLogger.sol`
- **Network**: Ethereum Sepolia Testnet
- **Gas Optimized**: ~65,000 gas per log
- **Immutable**: Permanent fraud records

### On-Chain Features
- Automatic high-risk logging (score > 70)
- Transaction hash verification
- Block explorer integration
- Historical alert retrieval

## 📊 Sample Wallets

### Included Examples:
1. **Phishing Drainer** (98.64/100) - High-velocity bot
2. **Vitalik Buterin** (2.15/100) - Verified clean whale
3. **Ethereum Foundation** (0.85/100) - Legitimate protocol
4. **MEV Bot** (54.30/100) - Suspicious arbitrage

## 🔒 Security Best Practices

- ✅ Never commit `.env` files
- ✅ Use dedicated test wallets only
- ✅ Rotate API keys regularly
- ✅ Enable CORS only for trusted origins
- ✅ Use HTTPS in production
- ✅ Rate limit API endpoints

## 🧪 Testing

## 🧪 Testing

```bash
# Run unit tests
python -m pytest backend/test_predictor.py -v

# Test API endpoints
curl http://localhost:5000/api/health

# Test wallet analysis
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"address":"0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"}'
```

## 📱 Browser Compatibility

| Browser | Status |
|---------|--------|
| Chrome 90+ | ✅ Fully Supported |
| Firefox 88+ | ✅ Fully Supported |
| Safari 14+ | ✅ Fully Supported |
| Edge 90+ | ✅ Fully Supported |

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **XGBoost Team** - Powerful ML framework
- **Etherscan** - Blockchain data API
- **Web3.py** - Ethereum integration library
- **SHAP** - Model explainability framework
- **Flask** - Lightweight web framework
- **Ethereum Community** - Inspiration and support

## 📞 Support

- **Documentation**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/Not-PK107/Defi_fraud-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Not-PK107/Defi_fraud-/discussions)

## 🗺️ Roadmap

- [x] ML Model Training & Optimization
- [x] Python Backend API
- [x] Smart Contract Development
- [x] Beautiful Classic Theme Frontend
- [x] Real-time Notifications
- [x] Analytics Dashboard
- [x] Bulk Analysis Feature
- [ ] Machine Learning Model Retraining Pipeline
- [ ] Advanced Visualization Charts
- [ ] Multi-chain Support (Polygon, BSC, etc.)
- [ ] Mobile Native Apps (iOS/Android)
- [ ] API Rate Limiting & Caching
- [ ] Database Integration for Historical Data

## 📈 Project Stats

- **Lines of Code**: 10,000+
- **ML Features**: 39 engineered features
- **Model Accuracy**: 98%+
- **Frontend Components**: 20+ interactive components
- **API Endpoints**: 6 REST endpoints
- **Smart Contracts**: 1 deployed on Sepolia

---

**Built with ❤️ for the Ethereum and DeFi community**

🛡️ **Stay Safe. Stay Vigilant. Detect Fraud.**

---

### Screenshots

#### Dashboard View
![Dashboard](https://via.placeholder.com/800x450/080c16/d4af37?text=Aegis+DeFi+Dashboard)

#### Analysis Results
![Results](https://via.placeholder.com/800x450/080c16/d4af37?text=Risk+Assessment+Results)

#### What-If Simulator
![Simulator](https://via.placeholder.com/800x450/080c16/d4af37?text=Interactive+Simulator)

---

### Quick Links

- 📖 [Setup Guide](SETUP_GUIDE.md) - Complete installation instructions
- 🎨 [Frontend README](frontend/README.md) - UI documentation
- 🔗 [Sepolia Explorer](https://sepolia.etherscan.io/) - View on-chain logs
- 📊 [Live Demo](http://localhost:5000) - Try it yourself!
