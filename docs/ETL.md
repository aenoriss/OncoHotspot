# ETL Pipeline Documentation

## Overview

The OncoHotspot ETL (Extract, Transform, Load) pipeline implements a **Medallion Architecture** pattern to process cancer mutation and therapeutic data from multiple sources into a unified, analysis-ready format.

## Architecture

```
External APIs → Bronze Layer → Silver Layer → Gold Layer → SQLite Database
```

### Why Medallion Architecture?

1. **Data Quality**: Progressive refinement ensures high-quality output
2. **Debugging**: Raw data preserved for troubleshooting
3. **Reprocessing**: Easy to re-run specific layers
4. **Scalability**: Clear separation of concerns
5. **Industry Standard**: Proven pattern used in data lakes

## Pipeline Components

### 1. Bronze Layer - Raw Data Extraction

**Purpose**: Extract and store raw data exactly as received from external sources

#### Extractors

##### cBioPortal Extractor
```python
# Location: bronze/extractors/cbioportal_extractor.py
class CBioPortalExtractor:
    - Fetches mutation data from TCGA studies
    - Retrieves data for 182 clinically actionable genes
    - Implements rate limiting (10 requests/second)
    - Handles API pagination
```

**Data Sources**:
- 13 TCGA cancer studies
- ~27,000 mutation records per run
- Gene information for targeted genes

##### DGIdb Extractor
```python
# Location: bronze/extractors/dgidb_extractor.py
class DGIdbExtractor:
    - Fetches drug-gene interactions
    - Falls back to local data if API unavailable
    - 104 drug-gene interactions
```

#### Output Format
```json
{
  "source": "cbioportal",
  "timestamp": "2025-08-11T16:27:30",
  "data": [
    {
      "sampleId": "TCGA-XX-XXXX",
      "gene": {
        "hugoGeneSymbol": "EGFR",
        "entrezGeneId": 1956
      },
      "proteinChange": "L858R",
      "mutationType": "Missense_Mutation",
      "alleleFrequency": 0.45
    }
  ]
}
```

### 2. Silver Layer - Data Standardization

**Purpose**: Clean, validate, and standardize data into consistent format

#### Transformers

##### Mutation Standardizer
```python
# Location: silver/transformers/mutation_standardizer.py
class MutationStandardizer:
    - Normalizes gene symbols to HUGO standards
    - Standardizes protein change notation
    - Validates mutation types
    - Removes duplicates
    - Handles nested data structures
```

**Standardization Rules**:
1. Gene symbols: Uppercase, HUGO-compliant
2. Protein changes: HGVS notation (e.g., p.L858R)
3. Cancer types: Consistent naming (e.g., "Lung Adenocarcinoma")
4. Frequencies: Normalized to 0-1 range

##### Therapeutic Standardizer
```python
# Location: silver/transformers/therapeutic_standardizer.py
class TherapeuticStandardizer:
    - Normalizes drug names
    - Standardizes gene targets
    - Validates FDA approval status
    - Adds drug categories
```

#### Output Format
```json
{
  "gene_symbol": "EGFR",
  "cancer_type": "Lung Adenocarcinoma",
  "protein_change": "p.L858R",
  "mutation_type": "missense",
  "frequency": 0.45,
  "sample_count": 150,
  "total_samples": 500
}
```

### 3. Gold Layer - Business Aggregation

**Purpose**: Aggregate and enrich data for specific business use cases

#### Aggregators

##### Mutation Aggregator
```python
# Location: gold/aggregators/mutation_aggregator.py
class MutationAggregator:
    - Groups mutations by gene and cancer type
    - Calculates aggregate frequencies
    - Generates significance scores
    - Creates heatmap-ready datasets
```

**Aggregation Logic**:
1. Group by (gene, cancer_type, protein_change)
2. Calculate total mutation count
3. Compute frequency as count/total_samples
4. Generate significance score based on:
   - Mutation frequency
   - Known hotspot status
   - Functional impact

##### Therapeutic Aggregator
```python
# Location: gold/aggregators/therapeutic_aggregator.py
class TherapeuticAggregator:
    - Associates mutations with therapeutics
    - Implements three-level matching
    - Prioritizes FDA-approved drugs
```

**Association Levels**:
1. **Mutation-specific**: Exact protein change match (e.g., EGFR L858R → Osimertinib)
2. **Gene-level**: Any mutation in gene (e.g., any BRAF mutation → Vemurafenib)
3. **Hotspot**: Known hotspot regions (e.g., KRAS G12 → Sotorasib)

#### Output Format
```json
{
  "gene": "EGFR",
  "cancer_type": "Lung Adenocarcinoma",
  "mutations": [
    {
      "protein_change": "L858R",
      "frequency": 0.15,
      "count": 75,
      "significance_score": 0.92,
      "therapeutics": ["Osimertinib", "Erlotinib"]
    }
  ],
  "total_mutations": 150,
  "actionable_mutations": 68
}
```

### 4. Database Loading

**Purpose**: Load processed data into SQLite database

#### Database Loader
```python
# Location: gold/aggregators/database_loader.py
class DatabaseLoader:
    - Manages database connections
    - Handles transactions
    - Updates or inserts records
    - Maintains referential integrity
```

**Loading Process**:
1. Begin transaction
2. Upsert genes table
3. Upsert cancer_types table
4. Load mutations with foreign keys
5. Create therapeutic associations
6. Commit transaction

## Configuration

### Gene Configuration
```yaml
# Location: config/clinically_actionable_genes.yaml
genes:
  rtk_pathway:
    - EGFR:
        description: "Epidermal growth factor receptor"
        mutations:
          L858R: ["Osimertinib", "Erlotinib"]
          T790M: ["Osimertinib"]
    - ERBB2:
        description: "Human epidermal growth factor receptor 2"
```

### Pipeline Configuration
```python
# Location: config/pipeline_config.py
PIPELINE_CONFIG = {
    "bronze": {
        "rate_limit": 10,  # requests per second
        "retry_attempts": 3,
        "timeout": 30
    },
    "silver": {
        "batch_size": 1000,
        "validation_strict": True
    },
    "gold": {
        "min_frequency": 0.01,
        "significance_threshold": 0.5
    }
}
```

## Running the Pipeline

### Full Pipeline Run
```bash
cd data-processing
python pipeline.py
```

### Selective Layer Execution
```bash
# Only run bronze layer
python pipeline.py --layers bronze

# Skip bronze, run silver and gold
python pipeline.py --skip-bronze

# Only specific sources
python pipeline.py --sources cbioportal
```

### Command Line Options
```
Options:
  --sources SOURCES     Comma-separated list of sources (cbioportal,dgidb)
  --layers LAYERS       Comma-separated list of layers (bronze,silver,gold)
  --skip-bronze        Skip bronze layer extraction
  --skip-silver        Skip silver layer transformation
  --skip-gold          Skip gold layer aggregation
  --skip-database      Skip database loading
  --force              Force re-extraction even if data exists
  --debug              Enable debug logging
```

## Data Flow Examples

### Example 1: Mutation Processing
```
1. Bronze: Raw cBioPortal mutation
   {
     "gene": {"hugoGeneSymbol": "egfr"},
     "proteinChange": "L858R",
     "alleleFrequency": 0.45
   }

2. Silver: Standardized mutation
   {
     "gene_symbol": "EGFR",
     "protein_change": "p.L858R",
     "frequency": 0.45
   }

3. Gold: Aggregated with therapeutics
   {
     "gene": "EGFR",
     "protein_change": "L858R",
     "frequency": 0.15,
     "significance_score": 0.92,
     "therapeutics": ["Osimertinib"]
   }

4. Database: Stored with relations
   mutations.mutation_id = 1234
   genes.gene_id = 56 (EGFR)
   mutation_therapeutics (1234 → Osimertinib)
```

### Example 2: Therapeutic Association
```
1. Input: BRAF V600E mutation in melanoma

2. Association Check:
   - Level 1: Check config for BRAF V600E
     → Found: ["Vemurafenib", "Dabrafenib"]
   
3. Output: Create associations
   - mutation_id: 5678
   - therapeutic_ids: [12, 13]
   - association_level: "mutation_specific"
```

## Performance Metrics

### Typical Pipeline Run
- **Duration**: ~3 minutes
- **Data Processed**: 
  - 27,000+ raw mutations
  - 21,000+ standardized records
  - 2,000+ unique gene-cancer pairs
- **Memory Usage**: <500MB
- **Disk Space**: <100MB

### Optimization Strategies
1. **Batch Processing**: Process in chunks of 1000 records
2. **Indexing**: Pre-index lookups for O(1) access
3. **Caching**: Cache API responses for 24 hours
4. **Parallel Processing**: Run extractors concurrently

## Error Handling

### Retry Logic
```python
@retry(attempts=3, delay=1, backoff=2)
def fetch_with_retry(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### Error Types
1. **API Errors**: Retry with exponential backoff
2. **Validation Errors**: Log and skip record
3. **Database Errors**: Rollback transaction
4. **Critical Errors**: Stop pipeline, preserve state

## Monitoring

### Logging
```
logs/
├── pipeline_run_20250811_162730.json  # Structured run log
├── pipeline_errors.log                # Error details
└── pipeline_debug.log                 # Debug information
```

### Metrics Tracked
- Records processed per layer
- Processing time per stage
- Error rates
- Data quality scores
- API call counts

## Data Quality Checks

### Bronze Layer
- Schema validation
- Required fields present
- Data type validation

### Silver Layer
- Gene symbol validation (HUGO)
- Mutation notation validation (HGVS)
- Frequency range validation (0-1)
- Duplicate detection

### Gold Layer
- Aggregation accuracy
- Association validity
- Significance score validation
- Reference integrity

## Troubleshooting

### Common Issues

#### 1. API Rate Limiting
**Error**: `429 Too Many Requests`
**Solution**: Adjust rate_limit in config or add delays

#### 2. Gene Symbol Mismatch
**Error**: `Gene XXX not found in config`
**Solution**: Update clinically_actionable_genes.yaml

#### 3. Database Lock
**Error**: `database is locked`
**Solution**: Ensure no other process accessing database

#### 4. Memory Issues
**Error**: `MemoryError`
**Solution**: Reduce batch_size in config

### Debug Mode
```bash
# Enable verbose logging
python pipeline.py --debug

# Check specific layer output
ls -la bronze/data/cbioportal/
ls -la silver/data/mutations/
ls -la gold/data/heatmap_data/
```

## Extending the Pipeline

### Adding New Data Source
1. Create extractor in `bronze/extractors/`
2. Implement `BaseExtractor` interface
3. Add transformer in `silver/transformers/`
4. Update pipeline.py to include source

### Adding New Gene
1. Edit `config/clinically_actionable_genes.yaml`
2. Add gene symbol, description, and therapeutics
3. Re-run pipeline

### Custom Aggregation
1. Create aggregator in `gold/aggregators/`
2. Implement aggregation logic
3. Register in pipeline.py

## Best Practices

1. **Always preserve raw data** in bronze layer
2. **Validate early** in silver layer
3. **Test incrementally** with small datasets
4. **Monitor performance** metrics
5. **Document changes** in configuration
6. **Use transactions** for database operations
7. **Implement idempotency** for re-runs