# ⚠️ Backend Setup Required

## 🔧 Backend Has Been Reverted to Original

The backend now requires **full configuration** to work with live wallet analysis.

---

## ✅ What Works Now

### **Without Backend Configuration:**
- ✅ Frontend loads
- ✅ Sample wallet chips work (pre-loaded results)
- ✅ UI is fully functional
- ✅ Offline simulation mode
- ❌ **Live wallet analysis DOES NOT WORK**
- ❌ **Real Etherscan data DOES NOT WORK**

### **With Full Backend Configuration:**
- ✅ Everything above, PLUS:
- ✅ Live wallet analysis
- ✅ Real Etherscan transaction data
- ✅ ML predictions on real wallets
- ✅ Blockchain logging (high-risk wallets)
- ✅ Full feature set

---

## 🚀 Required Setup Steps

### **Step 1: Get API Keys**

#### **1. Etherscan API Key** (Required for live analysis)
```
1. Visit: https://etherscan.io/register
2. Create free account
3. Go to: https://etherscan.io/myapikey
4. Create new API key
5. Copy the key
```

#### **2. Infura/Alchemy RPC URL** (Required for blockchain)
```
Infura (Recommended):
1. Visit: https://infura.io/register
2. Create free account
3. Create new project → Ethereum → Sepolia
4. Copy HTTPS endpoint: https://sepolia.infura.io/v3/YOUR_PROJECT_ID

Or use Alchemy:
1. Visit: https://www.alchemy.com/
2. Create app → Sepolia
3. Copy HTTPS URL
```

#### **3. MetaMask Wallet** (Required for blockchain logging)
```
⚠️ CREATE A NEW TEST WALLET - DO NOT USE YOUR REAL WALLET!

1. Install MetaMask: https://metamask.io/
2. Create NEW wallet (dedicated for testing)
3. Switch to Sepolia Testnet
4. Get free test ETH: https://sepoliafaucet.com/
5. Export private key:
   - Click account menu
   - Account details
   - Export Private Key
   - Enter password
   - Copy the key (starts with 0x)
```

#### **4. Deploy Smart Contract** (Required for blockchain logging)
```
Option A - Using Remix (Easiest):
1. Go to: https://remix.ethereum.org/
2. Create new file: FraudLogger.sol
3. Copy code from: blockchain/FraudLogger.sol
4. Compile with Solidity 0.8.20
5. Deploy tab → Environment: Injected Provider - MetaMask
6. Connect MetaMask (Sepolia network)
7. Click Deploy
8. Confirm transaction in MetaMask
9. Copy deployed contract address

Option B - Using Hardhat:
(See blockchain deployment documentation)
```

---

### **Step 2: Configure .env File**

Edit your `.env` file in the project root:

```env
# Etherscan API Key (get from https://etherscan.io/myapikey)
ETHERSCAN_API_KEY=YOUR_REAL_ETHERSCAN_API_KEY_HERE

# Sepolia RPC URL (get from Infura or Alchemy)
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID_HERE

# MetaMask Private Key (TEST WALLET ONLY!)
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE_64_CHARACTERS

# Deployed Contract Address
CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS_HERE_42_CHARACTERS
```

**Example (with real values):**
```env
ETHERSCAN_API_KEY=ABC123DEF456GHI789JKL012MNO345PQ
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/1234567890abcdef1234567890abcdef
PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
CONTRACT_ADDRESS=0x1234567890123456789012345678901234567890
```

---

### **Step 3: Verify Model Files**

Check that ML model files exist:
```bash
dir notebooks\models

# Should see:
# - fraud_model.pkl
# - feature_columns.pkl  
# - median_imputer.pkl
```

If missing, train the model:
```bash
jupyter notebook notebooks/01_EDA.ipynb
# Run all cells to generate model files
```

---

### **Step 4: Start the Server**

```bash
# Make sure virtual environment is activated
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Start server
python backend/server.py
```

---

### **Step 5: Test**

1. **Open:** http://localhost:5000
2. **Try sample wallet first** (should work with pre-loaded data)
3. **Try a real address** to test live analysis

---

## 🧪 Testing Without Full Setup

### **Option 1: Sample Wallets Only**
- Just open frontend in browser
- Click sample wallet chips
- Everything works with pre-loaded data

### **Option 2: Frontend Demo Mode**
- Open `frontend/index.html` directly in browser
- Works completely offline
- Uses built-in simulation engine

---

## 🆘 Troubleshooting

### **Error: "Backend not available"**
```
✅ This is expected if .env is not configured
✅ Sample wallets will still work
❌ Live analysis requires configuration
```

### **Error: "hex string" in backend**
```
❌ Your .env still has placeholder values
✅ Replace ALL "your_..." placeholders with real values
```

### **Error: "Rate limit exceeded"**
```
❌ Etherscan free tier: 5 req/sec, 100k/day
✅ Wait between requests or upgrade plan
```

### **Error: "Connection refused"**
```
❌ Server not running
✅ Run: python backend/server.py
```

### **Error: "Transaction failed"**
```
❌ Not enough test ETH in wallet
✅ Get more: https://sepoliafaucet.com/
```

---

## 📊 What Each API Key Does

| Key | Purpose | Free Tier | Required For |
|-----|---------|-----------|--------------|
| **ETHERSCAN_API_KEY** | Fetch transaction data | Yes (100k/day) | Live analysis ✅ |
| **SEPOLIA_RPC_URL** | Connect to blockchain | Yes (limited) | Blockchain features ✅ |
| **PRIVATE_KEY** | Sign transactions | N/A | Blockchain logging ✅ |
| **CONTRACT_ADDRESS** | Smart contract location | N/A | Blockchain logging ✅ |

---

## 🎯 Configuration Checklist

- [ ] Created Etherscan account
- [ ] Got Etherscan API key
- [ ] Created Infura/Alchemy account  
- [ ] Got Sepolia RPC URL
- [ ] Created test MetaMask wallet
- [ ] Got test ETH from faucet
- [ ] Exported private key
- [ ] Deployed smart contract
- [ ] Updated .env file with ALL keys
- [ ] Verified model files exist
- [ ] Started server successfully
- [ ] Tested sample wallet
- [ ] Tested real wallet analysis

---

## 🔒 Security Reminders

⚠️ **NEVER use your real wallet with real funds!**
⚠️ **NEVER commit .env file to Git**
⚠️ **NEVER share your private key**
⚠️ **Use Sepolia testnet only**

---

## 💡 Quick Start Options

### **Just Want to See It Work?**
```bash
# Open frontend directly (no backend needed)
start frontend/index.html

# Click sample wallet chips
# Everything works with pre-loaded data!
```

### **Want Full Features?**
```
Follow all setup steps above
Configure all API keys
Start backend server
Analyze real wallets!
```

---

## 📞 Need Help?

**Documentation:**
- SETUP_GUIDE.md - Comprehensive guide
- API_DOCUMENTATION.md - API reference
- README.md - Project overview

**Common Issues:**
- Backend won't start → Check .env configuration
- Analysis fails → Verify all API keys are correct
- Blockchain errors → Check contract deployment
- Model errors → Retrain model with notebook

---

**The backend now works EXACTLY as you originally designed it!**
**Full configuration required for live analysis.** ✅
