# Aegis DeFi Fraud Detection — Classic Theme Frontend

An executive, user-friendly, and attractive Classic Theme web application for inspecting Ethereum wallet addresses, assessing fraud probability via XGBoost Machine Learning, explaining model classifications with SHAP, and reviewing on-chain smart contract logs on the Sepolia testnet.

---

## 🏛️ Classic Theme Design Philosophy
- **Aesthetic**: Deep obsidian/royal navy palette paired with brushed antique gold borders, warm parchment typography, classical security seals, and tachometer dial gauges.
- **Theme Modes**: Supports both **Dark Classic** (Obsidian & Burnished Gold) and **Light Classic** (Parchment & Brass) modes with a single click.
- **Responsiveness**: Fully responsive across mobile, tablet, desktop, and ultra-wide displays.

---

## 🚀 Key Features

1. **Executive Command Bar & Wallet Scanner**
   - Instant validation of 42-character checksummed Ethereum addresses.
   - 1-Click Curated Presets: *Phishing Drainer / Sybil Bot*, *Vitalik Buterin (vitalik.eth)*, *Ethereum Foundation Multi-Sig*, and *MEV Arbitrage Bot*.
   - 5-stage animated scan progression tracker.

2. **Executive Verdict & SVG Tachometer Gauge**
   - Circular animated tachometer dial reflecting the 0–100 Fraud Risk Index.
   - Official Security Verdict Seals (*High Fraud Threat*, *Elevated Caution*, *Verified Clean Wallet*).
   - Clear probability metrics and actionable recommendations (*PROCEED*, *PROCEED WITH CAUTION*, *AVOID TRANSACTION*).

3. **Explainable AI (SHAP) Reasoning Engine**
   - Mathematical decomposition translated into plain-English layman explanations.
   - Directional contribution indicators showing which behaviors raised or lowered risk.

4. **39-Feature Forensic Ledger**
   - Filterable by 4 categories: *Velocities & Volumes*, *Counterparty Diversity*, *ETH Dynamics*, and *ERC-20 Token Ecosystem*.
   - Live search box with instantaneous feature lookup.

5. **Interactive "What-If" Simulation Sandbox**
   - Interactive sliders allowing security analysts to test how changes in transaction counts, lifespans, and token activity shift the live ML fraud score.

6. **On-Chain Sepolia Threat Registry**
   - Direct smart contract ledger displaying high-risk alerts recorded to `FraudLogger.sol` with transaction links.

7. **Side-by-Side Comparison & Formal Audit Certificate**
   - Compare safe and fraudulent addresses simultaneously.
   - Export printable PDF-ready security audit certificates with official crests.

---

## 💻 How to Run

### Method 1: Direct Browser Launch (No Installation Required)
Simply open [`frontend/index.html`](file:///D:/Defi/Defi_fraud-/frontend/index.html) directly in any modern browser (Chrome, Edge, Firefox, Safari). The frontend includes a built-in forensic simulation engine that functions offline immediately!

### Method 2: Launch with Python Flask Server (Full Monorepo Integration)
```bash
# From the project root
python backend/server.py
```
Then visit: **`http://localhost:5000`** in your browser.
