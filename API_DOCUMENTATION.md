# 🔌 API Documentation

Complete REST API documentation for the DeFi Fraud Detection backend.

## Base URL

```
http://localhost:5000/api
```

For production, replace with your deployed URL.

---

## Authentication

Currently, the API does not require authentication. In production, implement API key authentication:

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Health Check

Check if the backend services are operational.

**Endpoint:** `GET /api/health`

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
  "ml_models": "loaded",
  "message": "DeFi Fraud Detection AI Backend Ready"
}
```

**Status Codes:**
- `200 OK` - All services operational
- `500 Internal Server Error` - Service degraded

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

### 2. Analyze Wallet

Perform complete fraud analysis on an Ethereum wallet address.

**Endpoint:** `POST /api/analyze`

**Request Body:**
```json
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
  "features_used": {
    "Avg min between sent tnx": 2.45,
    "Sent tnx": 142,
    "ERC20_data_missing": 1,
    ...
  },
  "shap_explanation": [
    {
      "feature": "Time Diff between first and last (Mins)",
      "display": "Account lifespan is extremely short",
      "direction": "increases_fraud",
      "shap_value": 3.42
    },
    ...
  ],
  "blockchain": {
    "transaction_hash": "0x8f2d9c10b45a6712...",
    "block_number": 6842109,
    "status": 1
  },
  "timestamp": "2026-10-04T12:30:00Z"
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| address | string | Yes | Ethereum wallet address (42 chars, starts with 0x) |

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| wallet | string | Analyzed wallet address |
| prediction | string | FRAUD or LEGITIMATE |
| fraud_probability | float | Probability score (0.0 - 1.0) |
| risk_score | float | Risk score (0 - 100) |
| risk_level | string | LOW, MEDIUM, or HIGH |
| recommendation | string | Actionable advice |
| features_used | object | All 39 computed features |
| shap_explanation | array | SHAP feature importance |
| blockchain | object/null | On-chain logging receipt (if applicable) |
| timestamp | string | Analysis timestamp (ISO 8601) |

**Status Codes:**
- `200 OK` - Analysis successful
- `400 Bad Request` - Invalid address format
- `500 Internal Server Error` - Analysis failed

**Example:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"address":"0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"}'
```

**Python Example:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/analyze',
    json={'address': '0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A'}
)

result = response.json()
print(f"Risk Score: {result['risk_score']}")
print(f"Risk Level: {result['risk_level']}")
```

---

### 3. Direct ML Prediction

Run ML prediction on pre-computed features (without fetching live data).

**Endpoint:** `POST /api/predict`

**Request Body:**
```json
{
  "features": {
    "Avg min between sent tnx": 2.45,
    "Sent tnx": 142,
    "Received Tnx": 18,
    "ERC20_data_missing": 1,
    ...
  }
}
```

**Response:**
```json
{
  "prediction": "FRAUD",
  "fraud_probability": 0.9864,
  "risk_score": 98.64,
  "risk_level": "HIGH",
  "recommendation": "AVOID TRANSACTION"
}
```

**Status Codes:**
- `200 OK` - Prediction successful
- `400 Bad Request` - Missing or invalid features
- `500 Internal Server Error` - Prediction failed

---

### 4. Fetch Wallet Data

Fetch live wallet data from Etherscan without ML analysis.

**Endpoint:** `POST /api/fetch-wallet`

**Request Body:**
```json
{
  "address": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"
}
```

**Response:**
```json
{
  "wallet": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A",
  "features_used": {
    "Sent tnx": 142,
    "Received Tnx": 18,
    "total ether balance": 1.08,
    ...
  },
  "prediction": "FRAUD",
  "fraud_probability": 0.9864,
  "risk_score": 98.64,
  "risk_level": "HIGH",
  "recommendation": "AVOID TRANSACTION",
  "shap_explanation": [...]
}
```

**Status Codes:**
- `200 OK` - Data fetched successfully
- `400 Bad Request` - Invalid address
- `429 Too Many Requests` - Etherscan rate limit
- `500 Internal Server Error` - Fetch failed

---

### 5. Blockchain Status

Get current blockchain connection and contract information.

**Endpoint:** `GET /api/blockchain/status`

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

**Status Codes:**
- `200 OK` - Status retrieved
- `500 Internal Server Error` - Connection failed

**Example:**
```bash
curl http://localhost:5000/api/blockchain/status
```

---

### 6. Log Fraud to Blockchain

Manually log a fraud alert to the blockchain.

**Endpoint:** `POST /api/blockchain/log-fraud`

**Request Body:**
```json
{
  "wallet_address": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A",
  "risk_score": 98.64,
  "fraud_category": "ML:fraud prob=0.9864 level=high"
}
```

**Response:**
```json
{
  "transaction_hash": "0x8f2d9c10b45a6712ee498e9104b2c1598471e98d...",
  "block_number": 6842109,
  "status": 1
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| wallet_address | string | Yes | Ethereum address to log |
| risk_score | float | Yes | Risk score (0-100) |
| fraud_category | string | Yes | Classification description |

**Status Codes:**
- `200 OK` - Logged successfully
- `400 Bad Request` - Missing required fields
- `500 Internal Server Error` - Logging failed

**Note:** This endpoint requires gas fees and will deduct ETH from the configured wallet.

---

### 7. Get Recent Fraud Alerts

Retrieve recent fraud alerts from the blockchain.

**Endpoint:** `GET /api/alerts`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | int | No | 10 | Number of alerts to retrieve |

**Response:**
```json
{
  "total_alerts": 125,
  "recent_alerts": [
    {
      "index": 124,
      "wallet_address": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A",
      "risk_score": 99,
      "fraud_category": "ML:fraud prob=0.9998 level=high",
      "timestamp": 1727533330,
      "reported_by": "0x4A13b82cD46960F1749Ceeb3f8863A75A38411C2",
      "block_explorer_url": "https://sepolia.etherscan.io/address/0x1da5821..."
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Alerts retrieved
- `500 Internal Server Error` - Retrieval failed

**Example:**
```bash
curl http://localhost:5000/api/alerts?limit=20
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error type",
  "details": "Detailed error message",
  "wallet": "0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"
}
```

**Common Error Codes:**

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Endpoint doesn't exist |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error - Server issue |
| 503 | Service Unavailable - Service down |

---

## Rate Limiting

### Etherscan API Limits
- **Free Tier**: 5 requests/second, 100,000 requests/day
- **Standard Tier**: 5 requests/second, unlimited requests/day

Built-in delays (0.25s) prevent exceeding rate limits.

### Recommended Client-Side Limits
- Max 3 simultaneous analyses
- 1 second delay between bulk operations
- Implement exponential backoff for retries

---

## CORS Configuration

Cross-Origin Resource Sharing is enabled for all origins by default.

In production, restrict to specific origins:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

## WebSocket Support (Future)

Real-time updates via WebSocket (planned feature):

```javascript
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New fraud alert:', data);
};
```

---

## SDK Examples

### JavaScript/TypeScript

```typescript
class AegisDeFiAPI {
  private baseUrl: string;

  constructor(baseUrl = 'http://localhost:5000/api') {
    this.baseUrl = baseUrl;
  }

  async analyzeWallet(address: string) {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address })
    });
    
    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`);
    }
    
    return await response.json();
  }

  async getHealth() {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }
}

// Usage
const api = new AegisDeFiAPI();
const result = await api.analyzeWallet('0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A');
console.log(`Risk Score: ${result.risk_score}`);
```

### Python

```python
import requests
from typing import Dict, Any

class AegisDeFiAPI:
    def __init__(self, base_url: str = 'http://localhost:5000/api'):
        self.base_url = base_url
        
    def analyze_wallet(self, address: str) -> Dict[str, Any]:
        """Analyze a wallet address for fraud risk."""
        response = requests.post(
            f'{self.base_url}/analyze',
            json={'address': address}
        )
        response.raise_for_status()
        return response.json()
    
    def get_health(self) -> Dict[str, Any]:
        """Check API health status."""
        response = requests.get(f'{self.base_url}/health')
        response.raise_for_status()
        return response.json()
    
    def get_alerts(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent fraud alerts."""
        response = requests.get(
            f'{self.base_url}/alerts',
            params={'limit': limit}
        )
        response.raise_for_status()
        return response.json()

# Usage
api = AegisDeFiAPI()
result = api.analyze_wallet('0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A')
print(f"Risk Score: {result['risk_score']}")
print(f"Recommendation: {result['recommendation']}")
```

---

## Testing

### Health Check Test
```bash
curl -X GET http://localhost:5000/api/health | jq
```

### Analysis Test
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"address":"0x1da5821544e25c636c1417Ba96Ade4Cf6D2f9B5A"}' \
  | jq '.risk_score'
```

### Load Test with Apache Bench
```bash
# 100 requests, 10 concurrent
ab -n 100 -c 10 -p analyze.json \
  -T application/json \
  http://localhost:5000/api/analyze
```

---

## Changelog

### v1.0.0 (Current)
- Initial API release
- 7 REST endpoints
- Full wallet analysis pipeline
- Blockchain integration
- SHAP explanations

### Future Versions
- v1.1.0: WebSocket support
- v1.2.0: API key authentication
- v1.3.0: Rate limiting middleware
- v2.0.0: Multi-chain support

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/Not-PK107/Defi_fraud-/issues
- Email: [your-email]
- Documentation: See SETUP_GUIDE.md

---

**Last Updated:** October 4, 2026
**API Version:** 1.0.0
**Maintained by:** DeFi Fraud Detection Team
