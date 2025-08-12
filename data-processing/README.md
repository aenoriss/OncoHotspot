# OncoHotspot ETL Pipeline

A medallion architecture ETL pipeline for fetching cancer mutation data from open sources.

## Architecture

```
🥉 BRONZE → 🥈 SILVER → 🥇 GOLD → 💾 DATABASE
Raw Data    Cleaned    Aggregated   Loaded
```

### Layers

1. **Bronze Layer**: Raw data extraction from APIs
   - cBioPortal API
   - COSMIC NIH API
   - Preserves original data format

2. **Silver Layer**: Data standardization
   - Unified mutation format
   - Cancer type mapping
   - Variant harmonization

3. **Gold Layer**: Business-ready aggregations
   - Mutation frequency calculations
   - Significance scoring
   - Heatmap-optimized format

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Run Full Pipeline

```bash
# Extract from all sources
python pipeline.py

# Extract from specific sources
python pipeline.py --sources cbioportal cosmic

# Clear existing data first
python pipeline.py --clear

# Verbose logging
python pipeline.py --verbose
```

### Run Individual Components

```python
from bronze.extractors import CBioPortalExtractor
from silver.transformers import MutationStandardizer
from gold.aggregators import MutationAggregator

# Extract raw data
extractor = CBioPortalExtractor()
raw_data = extractor.extract(genes=['TP53', 'KRAS'])

# Standardize data
standardizer = MutationStandardizer()
clean_data = standardizer.standardize_cbioportal(raw_data)

# Aggregate for visualization
aggregator = MutationAggregator()
heatmap_data = aggregator.aggregate_for_heatmap(clean_data)
```

## Data Sources

### cBioPortal
- **API**: https://www.cbioportal.org/api
- **Authentication**: None required
- **Rate Limit**: 10 requests/second
- **Studies**: MSK-IMPACT, TCGA, GENIE

### COSMIC NIH
- **API**: https://clinicaltables.nlm.nih.gov/api/cosmic/v3
- **Authentication**: None required
- **Rate Limit**: 5 requests/second
- **Limitation**: Max 10,000 results per query

## Configuration

Edit `config/sources.yaml` to customize:
- Target genes
- Cancer studies
- API endpoints
- Rate limits

Edit `config/cancer_types.yaml` to customize:
- Cancer type mappings
- Standardization rules

## Output

### Bronze Layer
- Location: `bronze/data/{source}/`
- Format: Raw JSON with metadata
- Retention: 30 days

### Silver Layer
- Location: `silver/data/mutations/`
- Format: Standardized JSON
- Fields: gene, position, cancer_type, frequency

### Gold Layer
- Location: `gold/data/heatmap_data/`
- Format: Aggregated JSON
- Ready for visualization

### Database
- Location: `../database/oncohotspot.db`
- Schema: See `database/schemas/`

## Monitoring

Pipeline statistics are saved to `logs/` including:
- Record counts per layer
- Processing times
- Error logs
- Data quality metrics

## Scheduling

For automated updates:

```bash
# Daily updates (cron)
0 2 * * * cd /path/to/oncohotspot/data-processing && python pipeline.py

# Weekly full refresh
0 3 * * 0 cd /path/to/oncohotspot/data-processing && python pipeline.py --clear
```

## Data Quality

The pipeline includes quality checks at each layer:
- **Bronze**: API response validation
- **Silver**: Required field validation, duplicate detection
- **Gold**: Aggregation accuracy, significance validation

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Adjust `rate_limit` in `config/sources.yaml`
2. **Memory Issues**: Process in smaller batches
3. **Database Locks**: Ensure no concurrent access

### Logs

Check `logs/` directory for detailed pipeline execution logs.

## Future Enhancements

- [ ] Add OncoKB integration
- [ ] Implement Redis caching
- [ ] Add Airflow orchestration
- [ ] Create data quality dashboard
- [ ] Add real-time streaming updates

## License

MIT