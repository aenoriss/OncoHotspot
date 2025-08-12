#!/usr/bin/env python3
"""
Fetch gene and therapeutic descriptions using Claude API
"""

import os
import sys
import json
import yaml
import time
from typing import Dict, List
import anthropic
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_genes_from_config() -> List[str]:
    """Load gene list from config file"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'config',
        'clinically_actionable_genes.yaml'
    )
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    genes = []
    for category in config['clinically_actionable_genes'].values():
        if isinstance(category, list):
            genes.extend(category)
    
    # Remove duplicates
    return list(set(genes))


def load_therapeutics_from_config() -> List[str]:
    """Load therapeutic list from config file"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'config',
        'clinically_actionable_genes.yaml'
    )
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    therapeutics = set()
    for gene_drugs in config.get('therapeutic_associations', {}).values():
        for drugs in gene_drugs.values():
            if isinstance(drugs, list):
                therapeutics.update(drugs)
    
    # Add common FDA-approved drugs
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
    
    return sorted(list(therapeutics))


def fetch_gene_descriptions(client: anthropic.Anthropic, genes: List[str]) -> Dict[str, str]:
    """Fetch descriptions for genes using Claude API"""
    print(f"\nFetching descriptions for {len(genes)} genes...")
    descriptions = {}
    
    # Process in batches to avoid rate limits
    batch_size = 20
    for i in range(0, len(genes), batch_size):
        batch = genes[i:i+batch_size]
        gene_list = ', '.join(batch)
        
        prompt = f"""Please provide a brief one-line description (max 100 characters) for each of these cancer-related genes. 
Format your response as JSON with gene symbol as key and description as value.

Genes: {gene_list}

Example format:
{{"EGFR": "Receptor tyrosine kinase frequently mutated in lung cancer"}}

Provide only the JSON, no other text."""
        
        try:
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = message.content[0].text.strip()
            # Clean up response if needed
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            batch_descriptions = json.loads(response_text)
            descriptions.update(batch_descriptions)
            
            print(f"  Processed batch {i//batch_size + 1}/{(len(genes) + batch_size - 1)//batch_size}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error processing batch {i//batch_size + 1}: {e}")
            # Add placeholder descriptions for failed batch
            for gene in batch:
                descriptions[gene] = "Cancer-associated gene"
    
    return descriptions


def fetch_therapeutic_descriptions(client: anthropic.Anthropic, therapeutics: List[str]) -> Dict[str, str]:
    """Fetch descriptions for therapeutics using Claude API"""
    print(f"\nFetching descriptions for {len(therapeutics)} therapeutics...")
    descriptions = {}
    
    # Process in batches
    batch_size = 15
    for i in range(0, len(therapeutics), batch_size):
        batch = therapeutics[i:i+batch_size]
        drug_list = ', '.join(batch)
        
        prompt = f"""Please provide a brief one-line description (max 100 characters) for each of these cancer drugs.
Format your response as JSON with drug name as key and description as value.

Drugs: {drug_list}

Example format:
{{"Osimertinib": "3rd gen EGFR inhibitor for T790M-positive NSCLC"}}

Provide only the JSON, no other text."""
        
        try:
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            response_text = message.content[0].text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            batch_descriptions = json.loads(response_text)
            descriptions.update(batch_descriptions)
            
            print(f"  Processed batch {i//batch_size + 1}/{(len(therapeutics) + batch_size - 1)//batch_size}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error processing batch {i//batch_size + 1}: {e}")
            # Add placeholder descriptions
            for drug in batch:
                descriptions[drug] = "Cancer therapeutic agent"
    
    return descriptions


def save_descriptions(gene_descriptions: Dict, therapeutic_descriptions: Dict):
    """Save descriptions to file"""
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        'descriptions'
    )
    os.makedirs(output_dir, exist_ok=True)
    
    # Save gene descriptions
    gene_file = os.path.join(output_dir, 'gene_descriptions.json')
    with open(gene_file, 'w') as f:
        json.dump(gene_descriptions, f, indent=2)
    print(f"\nSaved gene descriptions to {gene_file}")
    
    # Save therapeutic descriptions
    drug_file = os.path.join(output_dir, 'therapeutic_descriptions.json')
    with open(drug_file, 'w') as f:
        json.dump(therapeutic_descriptions, f, indent=2)
    print(f"Saved therapeutic descriptions to {drug_file}")
    
    # Create combined file
    combined = {
        'genes': gene_descriptions,
        'therapeutics': therapeutic_descriptions,
        'metadata': {
            'gene_count': len(gene_descriptions),
            'therapeutic_count': len(therapeutic_descriptions),
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    combined_file = os.path.join(output_dir, 'all_descriptions.json')
    with open(combined_file, 'w') as f:
        json.dump(combined, f, indent=2)
    print(f"Saved combined descriptions to {combined_file}")


def main():
    """Main function"""
    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nTo use this script:")
        print("1. Get your API key from https://console.anthropic.com/")
        print("2. Set it as an environment variable:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("3. Run this script again")
        return 1
    
    # Initialize Claude client
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load genes and therapeutics
    print("Loading genes and therapeutics from config...")
    genes = load_genes_from_config()
    therapeutics = load_therapeutics_from_config()
    
    print(f"Found {len(genes)} unique genes")
    print(f"Found {len(therapeutics)} unique therapeutics")
    
    # Fetch descriptions
    gene_descriptions = fetch_gene_descriptions(client, genes)
    therapeutic_descriptions = fetch_therapeutic_descriptions(client, therapeutics)
    
    # Save results
    save_descriptions(gene_descriptions, therapeutic_descriptions)
    
    # Print summary
    print("\n" + "="*60)
    print("Summary:")
    print(f"  Gene descriptions fetched: {len(gene_descriptions)}")
    print(f"  Therapeutic descriptions fetched: {len(therapeutic_descriptions)}")
    print("="*60)
    
    # Show sample
    print("\nSample gene descriptions:")
    for gene in list(gene_descriptions.keys())[:5]:
        print(f"  {gene}: {gene_descriptions[gene]}")
    
    print("\nSample therapeutic descriptions:")
    for drug in list(therapeutic_descriptions.keys())[:5]:
        print(f"  {drug}: {therapeutic_descriptions[drug]}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())