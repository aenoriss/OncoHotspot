# OncoHotspot API Reference

Base URL: `http://localhost:3001/api`

## Authentication

Currently, the API is open for development. In production, API keys or JWT tokens will be required.

```http
Authorization: Bearer <jwt_token>
```

## Mutations API

### Get Mutations
Retrieve mutation data with optional filters.

```http
GET /api/mutations
```

**Query Parameters:**
- `genes` (string): Comma-separated gene names (e.g., "TP53,KRAS")
- `cancerTypes` (string): Comma-separated cancer types
- `minCount` (number): Minimum mutation count
- `maxCount` (number): Maximum mutation count
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 100)

**Example Request:**
```http
GET /api/mutations?genes=TP53,KRAS&cancerTypes=Breast Cancer&page=1&limit=50
```

**Response:**
```json
{
  "data": [
    {
      "gene": "TP53",
      "cancerType": "Breast Cancer",
      "position": 273,
      "mutationCount": 45,
      "significance": 0.95,
      "frequency": 0.30,
      "pValue": 0.0001
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 50,
  "totalPages": 3
}
```

### Get Mutations by Gene
Retrieve all mutations for a specific gene.

```http
GET /api/mutations/gene/:geneName
```

**Parameters:**
- `geneName` (string): Gene symbol (e.g., "TP53")

**Example Request:**
```http
GET /api/mutations/gene/TP53
```

**Response:**
```json
[
  {
    "gene": "TP53",
    "cancerType": "Breast Cancer",
    "position": 273,
    "mutationCount": 45,
    "significance": 0.95
  }
]
```

### Get Mutation Statistics
Retrieve overall mutation statistics.

```http
GET /api/mutations/stats
```

**Response:**
```json
{
  "totalMutations": 8,
  "uniqueGenes": 5,
  "uniqueCancerTypes": 7,
  "avgMutationCount": 65
}
```

## Genes API

### Get All Genes
Retrieve list of all oncogenes.

```http
GET /api/genes
```

**Response:**
```json
{
  "genes": [
    "TP53",
    "KRAS",
    "EGFR",
    "BRAF",
    "PIK3CA",
    "BRCA1",
    "BRCA2"
  ]
}
```

### Search Genes
Search for genes by name.

```http
GET /api/genes/search?q=<search_term>
```

**Query Parameters:**
- `q` (string): Search term

**Example Request:**
```http
GET /api/genes/search?q=BRCA
```

**Response:**
```json
{
  "genes": [
    "BRCA1",
    "BRCA2"
  ]
}
```

## Therapeutics API

### Get All Therapeutics
Retrieve all therapeutic targets.

```http
GET /api/therapeutics
```

**Response:**
```json
{
  "therapeutics": [
    {
      "gene": "EGFR",
      "drug": "Erlotinib",
      "mechanism": "Tyrosine kinase inhibitor",
      "clinicalStatus": "Approved",
      "cancerTypes": ["Lung Cancer"]
    }
  ]
}
```

### Get Therapeutics by Gene
Retrieve therapeutics for a specific gene.

```http
GET /api/therapeutics/gene/:geneName
```

**Parameters:**
- `geneName` (string): Gene symbol

**Example Request:**
```http
GET /api/therapeutics/gene/EGFR
```

**Response:**
```json
{
  "therapeutics": [
    {
      "gene": "EGFR",
      "drug": "Erlotinib",
      "mechanism": "Tyrosine kinase inhibitor",
      "clinicalStatus": "Approved",
      "cancerTypes": ["Lung Cancer"]
    },
    {
      "gene": "EGFR",
      "drug": "Gefitinib",
      "mechanism": "Tyrosine kinase inhibitor",
      "clinicalStatus": "Approved",
      "cancerTypes": ["Lung Cancer"]
    }
  ]
}
```

## Health Check

### Server Health
Check server status.

```http
GET /health
```

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Error Handling

All API endpoints return standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": {
    "message": "Error description",
    "timestamp": "2024-01-01T00:00:00.000Z",
    "path": "/api/mutations",
    "method": "GET"
  }
}
```

## Rate Limiting

Development: No rate limiting
Production: 1000 requests per hour per IP

## Data Formats

### Mutation Object
```json
{
  "gene": "string",
  "cancerType": "string",
  "position": "number",
  "refAllele": "string",
  "altAllele": "string",
  "mutationCount": "number",
  "totalSamples": "number",
  "frequency": "number",
  "significance": "number",
  "pValue": "number"
}
```

### Therapeutic Object
```json
{
  "gene": "string",
  "drug": "string",
  "mechanism": "string",
  "clinicalStatus": "enum[Preclinical, Phase I, Phase II, Phase III, Approved]",
  "cancerTypes": "array[string]",
  "fdaApprovalDate": "date",
  "manufacturer": "string"
}
```

## SDK Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:3001/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Get mutations for TP53
const mutations = await client.get('/mutations/gene/TP53');
console.log(mutations.data);

// Search with filters
const filtered = await client.get('/mutations', {
  params: {
    genes: 'TP53,KRAS',
    minCount: 10
  }
});
```

### Python
```python
import requests

base_url = 'http://localhost:3001/api'

# Get mutations for EGFR
response = requests.get(f'{base_url}/mutations/gene/EGFR')
mutations = response.json()

# Search with parameters
params = {
    'genes': 'TP53,KRAS',
    'cancerTypes': 'Breast Cancer',
    'limit': 50
}
response = requests.get(f'{base_url}/mutations', params=params)
results = response.json()
```

### cURL
```bash
# Get all mutations
curl "http://localhost:3001/api/mutations"

# Get mutations with filters
curl "http://localhost:3001/api/mutations?genes=TP53&cancerTypes=Breast%20Cancer"

# Get therapeutics for BRAF
curl "http://localhost:3001/api/therapeutics/gene/BRAF"
```