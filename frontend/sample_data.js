/**
 * sample_data.js
 * Comprehensive sample datasets, known wallet profiles, and 39-feature dictionary
 * for the DeFi Fraud Detection AI & On-Chain Audit Logger.
 */

const FEATURE_METADATA = {
  // Category 1: Transaction Velocities & Volumes
  "Sent tnx": {
    category: "Transactions",
    title: "Sent Transactions",
    description: "Total count of outgoing transactions initiated by this wallet.",
    unit: "txs",
    importance: "High",
    icon: "arrow-up-right"
  },
  "Received Tnx": {
    category: "Transactions",
    title: "Received Transactions",
    description: "Total count of incoming transactions received by this wallet.",
    unit: "txs",
    importance: "High",
    icon: "arrow-down-left"
  },
  "total transactions (including tnx to create contract": {
    category: "Transactions",
    title: "Total Transactions",
    description: "Sum of all incoming, outgoing, and contract creation transactions.",
    unit: "txs",
    importance: "Medium",
    icon: "layers"
  },
  "Number of Created Contracts": {
    category: "Transactions",
    title: "Contracts Created",
    description: "Number of smart contract deployment transactions initiated by this wallet.",
    unit: "contracts",
    importance: "High",
    icon: "code-square"
  },
  "Avg min between sent tnx": {
    category: "Transactions",
    title: "Avg Interval: Sent Txs",
    description: "Average interval in minutes between consecutive outgoing transactions.",
    unit: "mins",
    importance: "Critical",
    icon: "clock-history"
  },
  "Avg min between received tnx": {
    category: "Transactions",
    title: "Avg Interval: Received Txs",
    description: "Average interval in minutes between consecutive incoming transactions.",
    unit: "mins",
    importance: "Medium",
    icon: "hourglass-split"
  },
  "Time Diff between first and last (Mins)": {
    category: "Transactions",
    title: "Wallet Active Lifespan",
    description: "Total elapsed time in minutes between the very first and most recent transaction.",
    unit: "mins",
    importance: "Critical",
    icon: "calendar-range"
  },

  // Category 2: Address Counterparty Diversity
  "Unique Sent To Addresses": {
    category: "Counterparties",
    title: "Unique Destination Addrs",
    description: "Distinct destination addresses this wallet has sent funds to.",
    unit: "addrs",
    importance: "High",
    icon: "people"
  },
  "Unique Received From Addresses": {
    category: "Counterparties",
    title: "Unique Source Addrs",
    description: "Distinct origin addresses that have sent funds into this wallet.",
    unit: "addrs",
    importance: "High",
    icon: "person-check"
  },

  // Category 3: ETH Value Dynamics
  "min val sent": {
    category: "ETH Value",
    title: "Min Value Sent",
    description: "Minimum non-zero amount of ETH transferred in a single outgoing transaction.",
    unit: "ETH",
    importance: "Medium",
    icon: "cash-stack"
  },
  "max val sent": {
    category: "ETH Value",
    title: "Max Value Sent",
    description: "Maximum amount of ETH transferred in a single outgoing transaction.",
    unit: "ETH",
    importance: "High",
    icon: "graph-up-arrow"
  },
  "avg val sent": {
    category: "ETH Value",
    title: "Avg Value Sent",
    description: "Mean ETH value across all outgoing non-zero transfers.",
    unit: "ETH",
    importance: "Medium",
    icon: "calculator"
  },
  "min value received": {
    category: "ETH Value",
    title: "Min Value Received",
    description: "Minimum non-zero amount of ETH received in a single transfer.",
    unit: "ETH",
    importance: "Low",
    icon: "cash"
  },
  "max value received": {
    category: "ETH Value",
    title: "Max Value Received",
    description: "Maximum amount of ETH received in a single incoming transfer.",
    unit: "ETH",
    importance: "High",
    icon: "graph-up"
  },
  "avg val received": {
    category: "ETH Value",
    title: "Avg Value Received",
    description: "Mean ETH value across all incoming non-zero transfers.",
    unit: "ETH",
    importance: "Medium",
    icon: "pie-chart"
  },
  "total Ether sent": {
    category: "ETH Value",
    title: "Cumulative ETH Sent",
    description: "Total historical ETH outflow from this wallet.",
    unit: "ETH",
    importance: "Critical",
    icon: "box-arrow-up-right"
  },
  "total ether received": {
    category: "ETH Value",
    title: "Cumulative ETH Received",
    description: "Total historical ETH inflow into this wallet.",
    unit: "ETH",
    importance: "Critical",
    icon: "box-arrow-in-down-left"
  },
  "total ether balance": {
    category: "ETH Value",
    title: "Current ETH Balance",
    description: "Live unspent Ethereum balance residing in the wallet.",
    unit: "ETH",
    importance: "Critical",
    icon: "wallet2"
  },
  "min value sent to contract": {
    category: "ETH Value",
    title: "Min Sent to Contract",
    description: "Minimum non-zero ETH value sent in a direct smart contract interaction.",
    unit: "ETH",
    importance: "Low",
    icon: "file-earmark-code"
  },
  "max val sent to contract": {
    category: "ETH Value",
    title: "Max Sent to Contract",
    description: "Maximum ETH value sent in a direct smart contract interaction.",
    unit: "ETH",
    importance: "Medium",
    icon: "file-earmark-arrow-up"
  },
  "avg value sent to contract": {
    category: "ETH Value",
    title: "Avg Sent to Contract",
    description: "Mean ETH value sent across contract call transactions.",
    unit: "ETH",
    importance: "Medium",
    icon: "file-earmark-spreadsheet"
  },
  "total ether sent contracts": {
    category: "ETH Value",
    title: "Total ETH Sent to Contracts",
    description: "Cumulative ETH volume transacted directly to smart contracts.",
    unit: "ETH",
    importance: "High",
    icon: "file-earmark-lock"
  },

  // Category 4: ERC-20 Token Ecosystem
  "Total ERC20 tnxs": {
    category: "ERC-20 Tokens",
    title: "Total ERC20 Transfers",
    description: "Total number of ERC20 token transfer events recorded for this address.",
    unit: "txs",
    importance: "Critical",
    icon: "coin"
  },
  "ERC20 total Ether received": {
    category: "ERC-20 Tokens",
    title: "ERC20 Cumulative Received",
    description: "Aggregate volume of all ERC20 tokens received normalized to standard units.",
    unit: "Tokens",
    importance: "High",
    icon: "download"
  },
  "ERC20 total ether sent": {
    category: "ERC-20 Tokens",
    title: "ERC20 Cumulative Sent",
    description: "Aggregate volume of all ERC20 tokens dispatched.",
    unit: "Tokens",
    importance: "High",
    icon: "upload"
  },
  "ERC20 total Ether sent contract": {
    category: "ERC-20 Tokens",
    title: "ERC20 Sent to Contracts",
    description: "Total ERC20 token volume transferred directly into smart contract pools.",
    unit: "Tokens",
    importance: "Medium",
    icon: "arrow-repeat"
  },
  "ERC20 uniq sent addr": {
    category: "ERC-20 Tokens",
    title: "Unique ERC20 Recipients",
    description: "Count of distinct destination addresses that received tokens from this wallet.",
    unit: "addrs",
    importance: "Medium",
    icon: "person-dash"
  },
  "ERC20 uniq rec addr": {
    category: "ERC-20 Tokens",
    title: "Unique ERC20 Senders",
    description: "Count of distinct source addresses that sent tokens to this wallet.",
    unit: "addrs",
    importance: "Medium",
    icon: "person-plus"
  },
  "ERC20 uniq sent addr.1": {
    category: "ERC-20 Tokens",
    title: "Unique Token Contracts Sent",
    description: "Number of distinct ERC20 contract addresses the wallet initiated sends with.",
    unit: "tokens",
    importance: "High",
    icon: "collection"
  },
  "ERC20 uniq rec contract addr": {
    category: "ERC-20 Tokens",
    title: "Unique Token Contracts Recv",
    description: "Number of distinct ERC20 token contracts from which wallet received tokens.",
    unit: "tokens",
    importance: "High",
    icon: "collection-play"
  },
  "ERC20 min val rec": {
    category: "ERC-20 Tokens",
    title: "ERC20 Min Value Received",
    description: "Smallest token amount received in a single ERC20 transfer.",
    unit: "Tokens",
    importance: "Low",
    icon: "dash-circle"
  },
  "ERC20 max val rec": {
    category: "ERC-20 Tokens",
    title: "ERC20 Max Value Received",
    description: "Largest token amount received in a single ERC20 transfer.",
    unit: "Tokens",
    importance: "High",
    icon: "plus-circle"
  },
  "ERC20 avg val rec": {
    category: "ERC-20 Tokens",
    title: "ERC20 Avg Value Received",
    description: "Mean token volume across all incoming ERC20 transfer events.",
    unit: "Tokens",
    importance: "Medium",
    icon: "graph-down"
  },
  "ERC20 min val sent": {
    category: "ERC-20 Tokens",
    title: "ERC20 Min Value Sent",
    description: "Smallest token amount sent in a single ERC20 transfer.",
    unit: "Tokens",
    importance: "Low",
    icon: "dash-square"
  },
  "ERC20 max val sent": {
    category: "ERC-20 Tokens",
    title: "ERC20 Max Value Sent",
    description: "Largest token amount sent in a single ERC20 transfer.",
    unit: "Tokens",
    importance: "High",
    icon: "plus-square"
  },
  "ERC20 avg val sent": {
    category: "ERC-20 Tokens",
    title: "ERC20 Avg Value Sent",
    description: "Mean token volume across all outgoing ERC20 transfer events.",
    unit: "Tokens",
    importance: "Medium",
    icon: "bar-chart-line"
  },
  "ERC20 uniq sent token name": {
    category: "ERC-20 Tokens",
    title: "Unique Token Names Sent",
    description: "Total number of distinctly named tokens transferred out of this account.",
    unit: "names",
    importance: "Medium",
    icon: "tag"
  },
  "ERC20 uniq rec token name": {
    category: "ERC-20 Tokens",
    title: "Unique Token Names Recv",
    description: "Total number of distinctly named tokens deposited into this account.",
    unit: "names",
    importance: "Medium",
    icon: "tags"
  },
  "ERC20_data_missing": {
    category: "ERC-20 Tokens",
    title: "ERC20 Activity Missing Flag",
    description: "Binary flag indicating whether this wallet has zero recorded ERC20 interaction (1 = No ERC20, 0 = Has ERC20).",
    unit: "binary",
    importance: "Critical",
    icon: "shield-exclamation"
  }
};

const SAMPLE_WALLETS = [
  {
    address: "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A",
    label: "Phishing Drainer / Sybil Bot",
    tag: "Known Fraud",
    badgeType: "danger",
    description: "High-velocity automated wallet exhibiting rapid flash deposits, immediate full-drain ETH outflows, and zero ERC20 token diversification.",
    expectedRisk: "HIGH",
    expectedScore: 98.64,
    features: {
      "Avg min between sent tnx": 2.45,
      "Avg min between received tnx": 12.10,
      "Time Diff between first and last (Mins)": 340.5,
      "Sent tnx": 142,
      "Received Tnx": 18,
      "Number of Created Contracts": 0,
      "Unique Received From Addresses": 15,
      "Unique Sent To Addresses": 139,
      "min value received": 0.05,
      "max value received": 45.20,
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
      "ERC20_data_missing": 1
    },
    shap: [
      { feature: "Time Diff between first and last (Mins)", display: "Account lifespan is extremely short (<6 hours) with heavy activity", direction: "increases_fraud", shap_value: 3.42 },
      { feature: "ERC20_data_missing", display: "Zero ERC-20 token history indicating burner/drainer behavior", direction: "increases_fraud", shap_value: 2.85 },
      { feature: "Avg min between sent tnx", display: "Extremely rapid automated transaction bursts (~2.4 mins)", direction: "increases_fraud", shap_value: 2.18 },
      { feature: "total ether balance", display: "Negligible persistent balance compared to massive cumulative churn", direction: "increases_fraud", shap_value: 1.45 },
      { feature: "Unique Sent To Addresses", display: "High dispersion of funds to 139 single-use recipient addresses", direction: "increases_fraud", shap_value: 0.98 }
    ],
    blockchain: {
      transaction_hash: "0x8f2d9c10b45a6712ee498e9104b2c1598471e98da6931fbca08c734958de617c",
      block_number: 6842109,
      status: 1,
      contract_address: "0xb797682C896f6004B76f75fcf9589dD67634f19e",
      timestamp: "2026-09-28 14:22:10 UTC"
    }
  },
  {
    address: "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    label: "Vitalik Buterin (vitalik.eth)",
    tag: "Verified Clean Whale",
    badgeType: "success",
    description: "Long-standing historical Ethereum ecosystem pioneer wallet with multi-year organic transaction frequency, extensive ERC20 holding diversity, and stable balances.",
    expectedRisk: "LOW",
    expectedScore: 2.15,
    features: {
      "Avg min between sent tnx": 1845.30,
      "Avg min between received tnx": 120.45,
      "Time Diff between first and last (Mins)": 3840290.0,
      "Sent tnx": 1250,
      "Received Tnx": 9480,
      "Number of Created Contracts": 12,
      "Unique Received From Addresses": 6120,
      "Unique Sent To Addresses": 480,
      "min value received": 0.001,
      "max value received": 25000.0,
      "avg val received": 18.5,
      "min val sent": 0.01,
      "max val sent": 15000.0,
      "avg val sent": 84.2,
      "min value sent to contract": 0.01,
      "max val sent to contract": 5000.0,
      "avg value sent to contract": 32.1,
      "total transactions (including tnx to create contract": 10742,
      "total Ether sent": 105250.0,
      "total ether received": 175400.0,
      "total ether sent contracts": 45000.0,
      "total ether balance": 70150.0,
      "Total ERC20 tnxs": 4820,
      "ERC20 total Ether received": 1285000.0,
      "ERC20 total ether sent": 450000.0,
      "ERC20 total Ether sent contract": 310000.0,
      "ERC20 uniq sent addr": 310,
      "ERC20 uniq rec addr": 2400,
      "ERC20 uniq sent addr.1": 180,
      "ERC20 uniq rec contract addr": 490,
      "ERC20 min val rec": 0.0001,
      "ERC20 max val rec": 1000000.0,
      "ERC20 avg val rec": 850.0,
      "ERC20 min val sent": 0.001,
      "ERC20 max val sent": 250000.0,
      "ERC20 avg val sent": 1200.0,
      "ERC20 uniq sent token name": 150,
      "ERC20 uniq rec token name": 380,
      "ERC20_data_missing": 0
    },
    shap: [
      { feature: "Time Diff between first and last (Mins)", display: "Extensive multi-year lifespan indicating established organic history", direction: "decreases_fraud", shap_value: -4.10 },
      { feature: "ERC20 uniq rec token name", display: "High diversity of recognized DeFi tokens received (380+ tokens)", direction: "decreases_fraud", shap_value: -3.20 },
      { feature: "total ether balance", display: "Substantial steady ETH holding over long periods", direction: "decreases_fraud", shap_value: -2.85 },
      { feature: "Number of Created Contracts", display: "Legitimate contract authoring and deployment track record", direction: "decreases_fraud", shap_value: -1.90 },
      { feature: "Avg min between sent tnx", display: "Natural human-paced intervals between transactions (~30.7 hours)", direction: "decreases_fraud", shap_value: -1.65 }
    ],
    blockchain: null
  },
  {
    address: "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",
    label: "Ethereum Foundation Multi-Sig",
    tag: "Legitimate Protocol",
    badgeType: "success",
    description: "Official core development & grants treasury with consistent multi-year institutional activity, large verified contract interactions, and trusted multi-party signing.",
    expectedRisk: "LOW",
    expectedScore: 0.85,
    features: {
      "Avg min between sent tnx": 4320.0,
      "Avg min between received tnx": 860.0,
      "Time Diff between first and last (Mins)": 4120000.0,
      "Sent tnx": 890,
      "Received Tnx": 1240,
      "Number of Created Contracts": 4,
      "Unique Received From Addresses": 890,
      "Unique Sent To Addresses": 430,
      "min value received": 0.1,
      "max value received": 100000.0,
      "avg val received": 250.0,
      "min val sent": 0.5,
      "max val sent": 50000.0,
      "avg val sent": 420.0,
      "min value sent to contract": 1.0,
      "max val sent to contract": 20000.0,
      "avg value sent to contract": 350.0,
      "total transactions (including tnx to create contract": 2134,
      "total Ether sent": 373800.0,
      "total ether received": 410000.0,
      "total ether sent contracts": 95000.0,
      "total ether balance": 36200.0,
      "Total ERC20 tnxs": 1240,
      "ERC20 total Ether received": 890000.0,
      "ERC20 total ether sent": 210000.0,
      "ERC20 total Ether sent contract": 90000.0,
      "ERC20 uniq sent addr": 120,
      "ERC20 uniq rec addr": 340,
      "ERC20 uniq sent addr.1": 45,
      "ERC20 uniq rec contract addr": 82,
      "ERC20 min val rec": 1.0,
      "ERC20 max val rec": 500000.0,
      "ERC20 avg val rec": 2500.0,
      "ERC20 min val sent": 5.0,
      "ERC20 max val sent": 100000.0,
      "ERC20 avg val sent": 1800.0,
      "ERC20 uniq sent token name": 35,
      "ERC20 uniq rec token name": 68,
      "ERC20_data_missing": 0
    },
    shap: [
      { feature: "Time Diff between first and last (Mins)", display: "Proven historic multi-year chain presence", direction: "decreases_fraud", shap_value: -4.50 },
      { feature: "total ether balance", display: "Sustained high capitalization with no fast-dump liquidation", direction: "decreases_fraud", shap_value: -3.80 },
      { feature: "Avg min between sent tnx", display: "Scheduled institutional treasury batch cadence", direction: "decreases_fraud", shap_value: -2.40 }
    ],
    blockchain: null
  },
  {
    address: "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE",
    label: "Suspicious Arbitrage / MEV Bot",
    tag: "Moderate Caution",
    badgeType: "warning",
    description: "High-frequency smart contract executor with sporadic multi-token swaps, zero long-term holding, and irregular profit-sweeping patterns.",
    expectedRisk: "MEDIUM",
    expectedScore: 54.30,
    features: {
      "Avg min between sent tnx": 14.5,
      "Avg min between received tnx": 45.2,
      "Time Diff between first and last (Mins)": 45200.0,
      "Sent tnx": 680,
      "Received Tnx": 95,
      "Number of Created Contracts": 2,
      "Unique Received From Addresses": 18,
      "Unique Sent To Addresses": 42,
      "min value received": 0.1,
      "max value received": 25.0,
      "avg val received": 2.4,
      "min val sent": 0.05,
      "max val sent": 24.5,
      "avg val sent": 1.8,
      "min value sent to contract": 0.05,
      "max val sent to contract": 24.5,
      "avg value sent to contract": 1.8,
      "total transactions (including tnx to create contract": 777,
      "total Ether sent": 1224.0,
      "total ether received": 1228.0,
      "total ether sent contracts": 1224.0,
      "total ether balance": 4.0,
      "Total ERC20 tnxs": 410,
      "ERC20 total Ether received": 150000.0,
      "ERC20 total ether sent": 148000.0,
      "ERC20 total Ether sent contract": 148000.0,
      "ERC20 uniq sent addr": 12,
      "ERC20 uniq rec addr": 8,
      "ERC20 uniq sent addr.1": 15,
      "ERC20 uniq rec contract addr": 15,
      "ERC20 min val rec": 10.0,
      "ERC20 max val rec": 80000.0,
      "ERC20 avg val rec": 1200.0,
      "ERC20 min val sent": 10.0,
      "ERC20 max val sent": 80000.0,
      "ERC20 avg val sent": 1190.0,
      "ERC20 uniq sent token name": 8,
      "ERC20 uniq rec token name": 8,
      "ERC20_data_missing": 0
    },
    shap: [
      { feature: "total ether sent contracts", display: "Nearly 100% of volume routed through rapid routing contracts", direction: "increases_fraud", shap_value: 1.85 },
      { feature: "Avg min between sent tnx", display: "High execution velocity with automated frequency", direction: "increases_fraud", shap_value: 1.40 },
      { feature: "Time Diff between first and last (Mins)", display: "Moderate lifespan provides partial mitigating legitimacy", direction: "decreases_fraud", shap_value: -1.25 }
    ],
    blockchain: null
  }
];

const ON_CHAIN_REGISTRY_FIXTURES = [
  {
    wallet: "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A",
    riskScore: 99,
    category: "ML:fraud prob=0.9998 level=high",
    timestamp: 1727533330,
    formattedDate: "Sep 28, 2026, 02:22 PM UTC",
    reporter: "0x4A13b82cD46960F1749Ceeb3f8863A75A38411C2",
    txHash: "0x8f2d9c10b45a6712ee498e9104b2c1598471e98da6931fbca08c734958de617c",
    blockNumber: 6842109,
    status: "Confirmed"
  },
  {
    wallet: "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    riskScore: 94,
    category: "ML:fraud prob=0.9412 level=high",
    timestamp: 1727411200,
    formattedDate: "Sep 27, 2026, 04:26 AM UTC",
    reporter: "0x4A13b82cD46960F1749Ceeb3f8863A75A38411C2",
    txHash: "0x3e18a901ffc33b7082914101e4a119741284bbad309e1c29e1c028ba68b44910",
    blockNumber: 6839215,
    status: "Confirmed"
  },
  {
    wallet: "0x912a78129329ecb71a064821a8d0554bb70e0f31",
    riskScore: 88,
    category: "ML:fraud prob=0.8845 level=high",
    timestamp: 1727184000,
    formattedDate: "Sep 24, 2026, 01:20 PM UTC",
    reporter: "0x4A13b82cD46960F1749Ceeb3f8863A75A38411C2",
    txHash: "0x110bc59a19c9e83ba51042aa37be005b823e4210f91bc743e0129031dcf73041",
    blockNumber: 6831045,
    status: "Confirmed"
  }
];

// Export to window object for browser access
if (typeof window !== "undefined") {
  window.FEATURE_METADATA = FEATURE_METADATA;
  window.SAMPLE_WALLETS = SAMPLE_WALLETS;
  window.ON_CHAIN_REGISTRY_FIXTURES = ON_CHAIN_REGISTRY_FIXTURES;
}
