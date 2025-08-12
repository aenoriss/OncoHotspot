#!/usr/bin/env python3
"""Calculate estimated API cost for fetching descriptions"""

import yaml
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load genes from config
config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'config',
    'clinically_actionable_genes.yaml'
)

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Count unique genes
genes = set()
for category in config['clinically_actionable_genes'].values():
    if isinstance(category, list):
        genes.update(category)

# Count unique therapeutics
therapeutics = set()
for gene_drugs in config.get('therapeutic_associations', {}).values():
    for drugs in gene_drugs.values():
        if isinstance(drugs, list):
            therapeutics.update(drugs)

# Add common FDA drugs (from script)
common_drugs = [
    'Osimertinib', 'Erlotinib', 'Gefitinib', 'Afatinib',
    'Crizotinib', 'Alectinib', 'Brigatinib', 'Lorlatinib',
    'Vemurafenib', 'Dabrafenib', 'Encorafenib',
    'Sotorasib', 'Adagrasib',
    'Trastuzumab', 'Pertuzumab', 'T-DM1',
    'Imatinib', 'Dasatinib', 'Nilotinib',
    'Olaparib', 'Rucaparib', 'Niraparib', 'Talazoparib',
    'Alpelisib', 'Everolimus',
    'Palbociclib', 'Ribociclib', 'Abemaciclib',
    'Pembrolizumab', 'Nivolumab', 'Atezolizumab', 'Ipilimumab',
    'Larotrectinib', 'Entrectinib',
    'Selpercatinib', 'Pralsetinib',
    'Capmatinib', 'Tepotinib',
    'Erdafitinib', 'Pemigatinib',
    'Ivosidenib', 'Enasidenib',
    'Midostaurin', 'Gilteritinib',
    'Ruxolitinib', 'Fedratinib',
    'Venetoclax', 'Ibrutinib',
    'Mobocertinib', 'Amivantamab',
    'Neratinib', 'Tucatinib',
    'Repotrectinib', 'Infigratinib',
    'Quizartinib', 'Tazemetostat'
]
therapeutics.update(common_drugs)

print("=" * 60)
print("API COST ESTIMATION FOR DESCRIPTION FETCHING")
print("=" * 60)

print(f'\nData Volume:')
print(f'  Unique genes: {len(genes)}')
print(f'  Unique therapeutics: {len(therapeutics)}')
print(f'  Total items: {len(genes) + len(therapeutics)}')

# Calculate API calls
gene_batches = (len(genes) + 19) // 20  # 20 genes per batch
drug_batches = (len(therapeutics) + 14) // 15  # 15 drugs per batch
total_api_calls = gene_batches + drug_batches

print(f'\nAPI Calls:')
print(f'  Gene batches (20 per batch): {gene_batches}')
print(f'  Drug batches (15 per batch): {drug_batches}')
print(f'  Total API calls: {total_api_calls}')

# Estimate tokens
avg_prompt_tokens_per_call = 250  # Conservative estimate
avg_output_tokens_per_call = 400  # For JSON responses
total_input_tokens = total_api_calls * avg_prompt_tokens_per_call
total_output_tokens = total_api_calls * avg_output_tokens_per_call

print(f'\nToken Estimates:')
print(f'  Input tokens: ~{total_input_tokens:,}')
print(f'  Output tokens: ~{total_output_tokens:,}')
print(f'  Total tokens: ~{total_input_tokens + total_output_tokens:,}')

# Claude 3 Sonnet pricing (as of 2024)
input_price_per_1k = 0.003  # $3 per million
output_price_per_1k = 0.015  # $15 per million

estimated_cost = (total_input_tokens * input_price_per_1k / 1000) + (total_output_tokens * output_price_per_1k / 1000)

print(f'\nCost Breakdown (Claude 3 Sonnet):')
print(f'  Input cost: ${total_input_tokens * input_price_per_1k / 1000:.4f}')
print(f'  Output cost: ${total_output_tokens * output_price_per_1k / 1000:.4f}')
print(f'  Total estimated cost: ${estimated_cost:.4f}')
print(f'  With 50% safety margin: ${estimated_cost * 1.5:.4f}')

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Expected cost: ${estimated_cost:.2f} - ${estimated_cost * 1.5:.2f}")
print("This is a one-time cost to fetch all descriptions.")
print("=" * 60)