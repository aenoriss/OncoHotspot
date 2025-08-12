# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently, the API is public and does not require authentication.

## Response Format
All responses are in JSON format with the following structure:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Endpoints

### Mutations

#### Get All Mutations
```http
GET /api/mutations
```

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| gene | string | Filter by gene symbol | `EGFR` |
| cancer_type | string | Filter by cancer type | `Lung Adenocarcinoma` |
| min_frequency | number | Minimum frequency threshold | `0.05` |
| limit | number | Maximum results to return | `100` |
| offset | number | Pagination offset | `0` |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "mutation_id": 1,
      "gene_symbol": "EGFR",
      "cancer_type": "Lung Adenocarcinoma",
      "protein_change": "L858R",
      "frequency": 0.0015,  // Actual mutation frequency (0.15%)
      "count": 75,
      "significance_score": 0.0015  // Legacy field, same as frequency
    }
  ],
  "total": 1500,
  "limit": 100,
  "offset": 0
}
```

#### Get Heatmap Data
```http
GET /api/mutations/heatmap
```

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| genes | string | Comma-separated gene list | `EGFR,KRAS,BRAF` |
| cancer_types | string | Comma-separated cancer types | `LUAD,BRCA` |

**Response:**
```json
{
  "success": true,
  "data": {
    "genes": ["EGFR", "KRAS", "BRAF"],
    "cancerTypes": ["Lung Adenocarcinoma", "Breast Cancer"],
    "matrix": [
      [0.0015, 0.0008],  // EGFR frequencies (0.15%, 0.08%)
      [0.0030, 0.0002],  // KRAS frequencies (0.30%, 0.02%)
      [0.0005, 0.0012]   // BRAF frequencies (0.05%, 0.12%)
    ],
    "mutations": [
      {
        "gene": "EGFR",
        "cancerType": "Lung Adenocarcinoma",
        "frequency": 0.0015,  // 0.15%
        "count": 75,
        "proteinChanges": ["L858R", "T790M"]
      }
    ]
  }
}
```

#### Get Mutations by Gene
```http
GET /api/mutations/gene/:symbol
```

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| symbol | string | Gene symbol | `EGFR` |

**Response:**
```json
{
  "success": true,
  "data": {
    "gene": "EGFR",
    "mutations": [
      {
        "mutation_id": 1,
        "cancer_type": "Lung Adenocarcinoma",
        "protein_change": "L858R",
        "frequency": 0.15,
        "count": 75,
        "therapeutics": ["Osimertinib", "Erlotinib"]
      }
    ],
    "total_mutations": 25,
    "cancer_types_affected": 5
  }
}
```

### Genes

#### Get All Genes
```http
GET /api/genes
```

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| category | string | Filter by gene category | `rtk` |
| search | string | Search gene symbols/names | `kinase` |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "gene_id": 1,
      "gene_symbol": "EGFR",
      "gene_name": "Epidermal Growth Factor Receptor",
      "gene_type": "protein_coding",
      "chromosome": "7",
      "description": "Receptor tyrosine kinase",
      "category": "rtk",
      "mutation_count": 150,
      "therapeutic_count": 5
    }
  ],
  "total": 182
}
```

#### Get Gene Details
```http
GET /api/genes/:symbol
```

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| symbol | string | Gene symbol | `EGFR` |

**Response:**
```json
{
  "success": true,
  "data": {
    "gene_id": 1,
    "gene_symbol": "EGFR",
    "gene_name": "Epidermal Growth Factor Receptor",
    "gene_type": "protein_coding",
    "chromosome": "7",
    "description": "EGFR is a receptor tyrosine kinase...",
    "pathways": ["RTK signaling", "MAPK pathway"],
    "statistics": {
      "total_mutations": 150,
      "cancer_types_affected": 8,
      "average_frequency": 0.12,
      "max_frequency": 0.35,
      "therapeutic_associations": 5
    }
  }
}
```

#### Get Gene Therapeutics
```http
GET /api/genes/:symbol/therapeutics
```

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| symbol | string | Gene symbol | `EGFR` |

**Response:**
```json
{
  "success": true,
  "data": {
    "gene": "EGFR",
    "therapeutics": [
      {
        "drug_name": "Osimertinib",
        "brand_name": "Tagrisso",
        "drug_class": "Tyrosine Kinase Inhibitor",
        "fda_approved": true,
        "specific_mutations": ["L858R", "T790M"],
        "cancer_types": ["NSCLC"]
      }
    ],
    "total": 5
  }
}
```

### Cancer Types

#### Get All Cancer Types
```http
GET /api/cancer-types
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "cancer_type_id": 1,
      "cancer_name": "Lung Adenocarcinoma",
      "cancer_code": "LUAD",
      "cancer_category": "Lung Cancer",
      "tissue_origin": "Lung",
      "description": "Most common type of lung cancer",
      "sample_count": 500,
      "mutation_count": 3500
    }
  ],
  "total": 13
}
```

#### Get Cancer Type Mutations
```http
GET /api/cancer-types/:id/mutations
```

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| id | number | Cancer type ID | `1` |

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| min_frequency | number | Minimum frequency | `0.05` |
| limit | number | Result limit | `50` |

**Response:**
```json
{
  "success": true,
  "data": {
    "cancer_type": "Lung Adenocarcinoma",
    "mutations": [
      {
        "gene": "KRAS",
        "protein_change": "G12C",
        "frequency": 0.30,
        "count": 150
      }
    ],
    "total_mutations": 3500,
    "top_mutated_genes": ["KRAS", "EGFR", "TP53"]
  }
}
```

### Therapeutics

#### Get All Therapeutics
```http
GET /api/therapeutics
```

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| drug_class | string | Filter by drug class | `TKI` |
| fda_approved | boolean | Only FDA approved | `true` |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "therapeutic_id": 1,
      "drug_name": "Osimertinib",
      "brand_name": "Tagrisso",
      "drug_class": "Tyrosine Kinase Inhibitor",
      "targets": ["EGFR"],
      "fda_approved": true,
      "approval_year": 2015,
      "indications": ["NSCLC with EGFR T790M"]
    }
  ],
  "total": 32
}
```

#### Get Therapeutic Associations
```http
GET /api/therapeutics/associations
```

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| gene | string | Filter by gene | `EGFR` |
| mutation | string | Filter by mutation | `L858R` |
| cancer_type | string | Filter by cancer | `LUAD` |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "association_id": 1,
      "gene": "EGFR",
      "protein_change": "L858R",
      "cancer_type": "Lung Adenocarcinoma",
      "drug_name": "Osimertinib",
      "association_level": "mutation_specific",
      "evidence_level": "FDA_approved",
      "clinical_significance": "Predictive"
    }
  ],
  "total": 68
}
```

### Statistics

#### Get Database Statistics
```http
GET /api/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "database": {
      "total_genes": 182,
      "total_cancer_types": 13,
      "total_mutations": 21373,
      "total_therapeutics": 32,
      "total_associations": 68
    },
    "coverage": {
      "genes_with_mutations": 182,
      "genes_with_therapeutics": 35,
      "cancer_types_covered": 13,
      "actionable_mutations": 68
    },
    "last_update": "2025-08-11T16:30:12",
    "pipeline_version": "1.0.0"
  }
}
```

#### Get Pipeline Status
```http
GET /api/stats/pipeline
```

**Response:**
```json
{
  "success": true,
  "data": {
    "last_run": {
      "timestamp": "2025-08-11T16:30:12",
      "duration_seconds": 161,
      "status": "success",
      "records_processed": 27484,
      "records_loaded": 21373
    },
    "sources": {
      "cbioportal": {
        "status": "active",
        "last_fetch": "2025-08-11T16:27:30",
        "records": 27484
      },
      "dgidb": {
        "status": "active",
        "last_fetch": "2025-08-11T16:27:35",
        "records": 104
      }
    }
  }
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|------------|
| `GENE_NOT_FOUND` | Gene symbol not found | 404 |
| `CANCER_TYPE_NOT_FOUND` | Cancer type not found | 404 |
| `INVALID_PARAMETER` | Invalid query parameter | 400 |
| `DATABASE_ERROR` | Database query failed | 500 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |

## Rate Limiting

- **Default Rate Limit**: 100 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **Headers Returned**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Pagination

For endpoints returning lists, pagination is implemented using:

- `limit`: Number of results per page (default: 100, max: 1000)
- `offset`: Number of results to skip (default: 0)

**Example:**
```http
GET /api/mutations?limit=50&offset=100
```

## Filtering

Most list endpoints support filtering through query parameters:

**Example:**
```http
GET /api/mutations?gene=EGFR&cancer_type=LUAD&min_frequency=0.05
```

## Sorting

Sort results using the `sort` parameter:

**Format:** `field:direction`
- `direction`: `asc` or `desc`

**Example:**
```http
GET /api/mutations?sort=frequency:desc
```

## Search

Text search is available for genes:

**Example:**
```http
GET /api/genes?search=kinase
```

## CORS

CORS is enabled for the following origins:
- `http://localhost:3000` (development)
- `https://oncohotspot.com` (production)

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
```

### Events

#### Subscribe to Updates
```json
{
  "type": "subscribe",
  "channel": "mutations",
  "filters": {
    "gene": "EGFR"
  }
}
```

#### Receive Updates
```json
{
  "type": "update",
  "channel": "mutations",
  "data": {
    "mutation_id": 1,
    "gene": "EGFR",
    "change": "frequency_updated",
    "new_value": 0.16
  }
}
```

## Examples

### cURL Examples

#### Get EGFR mutations in lung cancer
```bash
curl -X GET "http://localhost:5000/api/mutations?gene=EGFR&cancer_type=Lung%20Adenocarcinoma"
```

#### Get heatmap data for specific genes
```bash
curl -X GET "http://localhost:5000/api/mutations/heatmap?genes=EGFR,KRAS,BRAF"
```

#### Get therapeutics for a gene
```bash
curl -X GET "http://localhost:5000/api/genes/EGFR/therapeutics"
```

### JavaScript Examples

#### Fetch mutations with error handling
```javascript
async function fetchMutations(gene, cancerType) {
  try {
    const params = new URLSearchParams({
      gene,
      cancer_type: cancerType,
      limit: 100
    });
    
    const response = await fetch(`/api/mutations?${params}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error);
    }
    
    return data.data;
  } catch (error) {
    console.error('Failed to fetch mutations:', error);
    throw error;
  }
}
```

#### Fetch with pagination
```javascript
async function fetchAllMutations() {
  const allMutations = [];
  let offset = 0;
  const limit = 100;
  
  while (true) {
    const response = await fetch(`/api/mutations?limit=${limit}&offset=${offset}`);
    const data = await response.json();
    
    allMutations.push(...data.data);
    
    if (data.data.length < limit) break;
    offset += limit;
  }
  
  return allMutations;
}
```

### Python Examples

#### Using requests library
```python
import requests

# Get mutations for a specific gene
response = requests.get(
    'http://localhost:5000/api/mutations',
    params={
        'gene': 'EGFR',
        'min_frequency': 0.05
    }
)

if response.status_code == 200:
    data = response.json()
    mutations = data['data']
    print(f"Found {len(mutations)} mutations")
else:
    print(f"Error: {response.status_code}")
```

#### Fetch heatmap data
```python
import requests
import numpy as np

response = requests.get(
    'http://localhost:5000/api/mutations/heatmap',
    params={
        'genes': 'EGFR,KRAS,BRAF',
        'cancer_types': 'LUAD,BRCA'
    }
)

if response.status_code == 200:
    data = response.json()['data']
    matrix = np.array(data['matrix'])
    print(f"Heatmap shape: {matrix.shape}")
```

## Testing

### Health Check
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "success": true,
  "message": "API is healthy",
  "timestamp": "2025-08-11T16:45:00Z"
}
```

### Test Database Connection
```bash
curl http://localhost:5000/api/health/db
```

Expected response:
```json
{
  "success": true,
  "message": "Database connection successful",
  "database": "oncohotspot.db",
  "tables": ["genes", "cancer_types", "mutations", "therapeutics"]
}
```