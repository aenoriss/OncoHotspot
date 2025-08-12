# OncoHotspot Scripts

## fetch_descriptions.py

Fetches brief descriptions for genes and therapeutics using the Claude API.

### Setup

1. Get your Anthropic API key from https://console.anthropic.com/
2. Set it as an environment variable:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

### Usage

```bash
# From the data-processing directory
cd /home/aenoris/masterProjects/oncohotspot/data-processing

# Run the script
python scripts/fetch_descriptions.py
```

### Output

The script will create three files in `data/descriptions/`:
- `gene_descriptions.json` - Descriptions for all genes
- `therapeutic_descriptions.json` - Descriptions for all drugs
- `all_descriptions.json` - Combined file with metadata

### Features

- Loads 150+ genes from `config/clinically_actionable_genes.yaml`
- Extracts all therapeutics from the config
- Processes in batches to avoid rate limits
- Provides fallback descriptions on API errors
- Saves results in JSON format

### Sample Output

```json
{
  "EGFR": "Receptor tyrosine kinase frequently mutated in lung cancer",
  "BRAF": "Serine/threonine kinase with V600E hotspot in melanoma",
  "KRAS": "GTPase commonly mutated in pancreatic and colorectal cancers"
}
```