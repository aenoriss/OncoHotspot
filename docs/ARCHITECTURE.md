# OncoHotspot Architecture Documentation

## System Overview

OncoHotspot follows a modern multi-tier architecture with clear separation of concerns between data ingestion, processing, storage, API services, and user interface.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (React + TypeScript + D3.js)                  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                          API Gateway                             │
│                    (Express.js + TypeScript)                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│      Business Logic         │   │       Data Access           │
│        Services              │   │         Layer               │
└─────────────────────────────┘   └─────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Database                                │
│                          (SQLite)                                │
└─────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                      ETL Pipeline                                │
│              (Python - Medallion Architecture)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer

#### Technology Stack
- **React 18**: Component-based UI framework
- **TypeScript**: Type safety and better developer experience
- **D3.js**: Advanced data visualization for heatmaps
- **Material-UI**: Consistent design system
- **React Query**: Server state management

#### Key Components

```
frontend/src/
├── components/
│   ├── heatmap/
│   │   └── MutationHeatmap.tsx      # D3.js heatmap visualization
│   ├── gene/
│   │   ├── GeneControl.tsx          # Gene filtering controls
│   │   └── GeneInfoPanel.tsx        # Gene details display
│   ├── cancer/
│   │   └── CancerTypeControl.tsx    # Cancer type filtering
│   └── therapeutics/
│       └── TherapeuticPanel.tsx     # Drug associations display
├── hooks/
│   └── useMutationData.ts           # Data fetching hook
└── services/
    └── api.ts                        # API client
```

#### State Management
- **Local State**: React useState for UI state
- **Server State**: React Query for API data caching
- **Props Drilling**: Minimal due to component composition

### 2. Backend Layer

#### Technology Stack
- **Node.js**: JavaScript runtime
- **Express.js**: Web application framework
- **TypeScript**: Type safety
- **SQLite3**: Database driver
- **CORS**: Cross-origin resource sharing

#### API Architecture

```
backend/src/
├── routes/
│   ├── mutations.ts      # /api/mutations endpoints
│   ├── genes.ts          # /api/genes endpoints
│   ├── therapeutics.ts  # /api/therapeutics endpoints
│   └── cancerTypes.ts    # /api/cancer-types endpoints
├── services/
│   ├── database.ts       # Database connection management
│   ├── mutationService.ts # Mutation business logic
│   └── cacheService.ts   # Response caching
├── middleware/
│   ├── errorHandler.ts   # Global error handling
│   └── validation.ts     # Request validation
└── models/
    └── types.ts          # TypeScript interfaces
```

#### RESTful API Design
- **Resource-based URLs**: `/api/resource/identifier`
- **HTTP Methods**: GET for reads, POST for writes
- **Status Codes**: Proper HTTP status codes
- **JSON Responses**: Consistent response format

### 3. Database Layer

#### Schema Design

```sql
-- Core Tables
CREATE TABLE genes (
    gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_symbol VARCHAR(50) UNIQUE NOT NULL,
    gene_name VARCHAR(200),
    gene_type VARCHAR(50),
    chromosome VARCHAR(10),
    description TEXT
);

CREATE TABLE cancer_types (
    cancer_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cancer_name VARCHAR(100) NOT NULL,
    cancer_category VARCHAR(50),
    tissue_origin VARCHAR(100),
    description TEXT
);

CREATE TABLE mutations (
    mutation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id INTEGER NOT NULL,
    cancer_type_id INTEGER NOT NULL,
    position INTEGER,
    ref_allele VARCHAR(50),
    alt_allele VARCHAR(50),
    protein_change VARCHAR(100),
    mutation_count INTEGER DEFAULT 1,
    frequency REAL,
    significance_score REAL,
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id),
    FOREIGN KEY (cancer_type_id) REFERENCES cancer_types(cancer_type_id)
);

-- Indexes for Performance
CREATE INDEX idx_mutations_gene ON mutations(gene_id);
CREATE INDEX idx_mutations_cancer ON mutations(cancer_type_id);
CREATE INDEX idx_mutations_frequency ON mutations(frequency DESC);
```

#### Data Integrity
- **Foreign Keys**: Enforce referential integrity
- **Constraints**: NOT NULL for required fields
- **Indexes**: Optimize query performance
- **Transactions**: ACID compliance

### 4. ETL Pipeline (Medallion Architecture)

#### Architecture Pattern
The pipeline follows the Medallion Architecture with three distinct layers:

```
External APIs → Bronze Layer → Silver Layer → Gold Layer → Database
```

#### Bronze Layer (Raw Data)
**Purpose**: Extract and store raw data exactly as received

```python
bronze/
├── extractors/
│   ├── base_extractor.py       # Abstract base class
│   ├── cbioportal_extractor.py # cBioPortal API client
│   ├── cosmic_extractor.py     # COSMIC data fetcher
│   └── dgidb_extractor.py      # Drug-gene interactions
└── data/
    └── [source]/                # Raw JSON files
```

**Features**:
- Rate limiting to respect API constraints
- Error handling and retry logic
- Data validation and checksums
- Raw data preservation

#### Silver Layer (Standardized Data)
**Purpose**: Clean, validate, and standardize data

```python
silver/
├── transformers/
│   ├── mutation_standardizer.py    # Normalize mutations
│   ├── therapeutic_standardizer.py # Standardize drugs
│   └── variant_harmonizer.py       # Harmonize variants
└── data/
    └── [source]/                    # Standardized JSON
```

**Processing**:
- Gene symbol normalization (HUGO standards)
- Mutation notation standardization (HGVS format)
- Data type conversion and validation
- Duplicate removal

#### Gold Layer (Business-Ready Data)
**Purpose**: Aggregate and enrich data for analysis

```python
gold/
├── aggregators/
│   ├── mutation_aggregator.py      # Aggregate by gene/cancer
│   ├── therapeutic_aggregator.py   # Associate drugs
│   └── database_loader.py          # Load to database
└── data/
    └── [analysis]/                  # Aggregated data
```

**Features**:
- Calculate mutation frequencies
- Generate significance scores
- Associate mutations with therapeutics
- Create heatmap-ready datasets

## Data Flow Architecture

### 1. Data Ingestion Flow

```
cBioPortal API → Rate Limiter → Bronze Extractor → Raw JSON
     ↓
COSMIC API → Rate Limiter → Bronze Extractor → Raw JSON
     ↓
DGIdb API → Rate Limiter → Bronze Extractor → Raw JSON
```

### 2. Data Processing Flow

```
Raw JSON → Silver Transformer → Standardized JSON
                ↓
        Validation & QC
                ↓
      Gold Aggregator → Enriched Data
                ↓
        Database Loader → SQLite
```

### 3. Data Serving Flow

```
User Request → API Gateway → Cache Check
                    ↓              ↓
              Cache Hit       Cache Miss
                    ↓              ↓
            Return Cache    Query Database
                              ↓
                        Process & Cache
                              ↓
                        Return Response
```

## Scalability Considerations

### Current Architecture (Small-Medium Scale)
- **SQLite**: Sufficient for <100GB data
- **Single Server**: Handles <1000 concurrent users
- **File-based Cache**: Simple and effective

### Future Scaling Options

#### Database Scaling
```
SQLite → PostgreSQL → PostgreSQL with Read Replicas
                    → Partitioning by cancer type
                    → Sharding by gene
```

#### API Scaling
```
Single Server → Load Balancer → Multiple API Servers
              → Redis Cache → CDN for Static Assets
```

#### Pipeline Scaling
```
Sequential → Parallel Processing → Distributed (Spark)
           → Message Queue (RabbitMQ)
           → Stream Processing (Kafka)
```

## Security Architecture

### API Security
- **CORS**: Configured for allowed origins only
- **Rate Limiting**: Prevent abuse and DoS
- **Input Validation**: Sanitize all inputs
- **SQL Injection Prevention**: Parameterized queries

### Data Security
- **No PII**: No patient-identifiable information
- **Aggregated Data**: Only summary statistics
- **Access Control**: Read-only public access
- **Audit Logging**: Track data access

### Infrastructure Security
- **HTTPS**: Encrypted communication
- **Environment Variables**: Secure configuration
- **Dependencies**: Regular security updates
- **Docker**: Containerized deployment

## Performance Optimization

### Database Optimization
- **Indexes**: On frequently queried columns
- **Query Optimization**: EXPLAIN ANALYZE
- **Connection Pooling**: Reuse connections
- **Batch Operations**: Bulk inserts

### API Optimization
- **Response Caching**: Cache frequent queries
- **Compression**: GZIP responses
- **Pagination**: Limit result sets
- **Field Selection**: Return only needed fields

### Frontend Optimization
- **Code Splitting**: Lazy load components
- **Memoization**: React.memo for expensive renders
- **Virtual Scrolling**: For large lists
- **Debouncing**: Search and filter inputs

## Monitoring & Observability

### Metrics to Track
- **API Response Times**: P50, P95, P99
- **Database Query Times**: Slow query log
- **Pipeline Run Times**: ETL duration
- **Error Rates**: 4xx, 5xx responses

### Logging Strategy
```
Application Logs → Structured JSON → Log Aggregator
                                   ↓
                            Analysis & Alerts
```

### Health Checks
- **API Health**: `/health` endpoint
- **Database Health**: Connection test
- **Pipeline Health**: Last run status
- **Cache Health**: Hit/miss ratio

## Deployment Architecture

### Development Environment
```
Local Development → Git Push → GitHub
                             ↓
                    CI/CD Pipeline
                             ↓
                    Automated Tests
```

### Production Deployment
```
GitHub → Build → Test → Deploy → Monitor
              ↓       ↓       ↓
         Docker   Jest   AWS/GCP
```

### Infrastructure as Code
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  
  backend:
    build: ./backend
    ports: ["5000:5000"]
    volumes:
      - ./database:/app/database
  
  pipeline:
    build: ./data-processing
    volumes:
      - ./database:/app/database
```

## Technology Decisions & Rationale

### Why SQLite?
- **Simplicity**: No server setup required
- **Performance**: Excellent for read-heavy workloads
- **Portability**: Single file database
- **Sufficient Scale**: Handles current data volume

### Why Medallion Architecture?
- **Data Quality**: Progressive refinement
- **Debugging**: Raw data preserved
- **Flexibility**: Easy to reprocess
- **Industry Standard**: Proven pattern

### Why React + D3.js?
- **React**: Component reusability
- **D3.js**: Powerful visualization
- **TypeScript**: Type safety
- **Community**: Large ecosystem

### Why Node.js Backend?
- **Full-stack JavaScript**: Unified language
- **Performance**: Non-blocking I/O
- **Ecosystem**: Rich package ecosystem
- **Development Speed**: Rapid iteration