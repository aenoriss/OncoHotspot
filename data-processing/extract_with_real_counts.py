#!/usr/bin/env python3
"""Extract cBioPortal data with real sample counts"""

import json
import logging
from bronze.extractors.cbioportal_extractor import CBioPortalExtractor
from silver.transformers.mutation_standardizer import MutationStandardizer
from gold.aggregators.mutation_aggregator import MutationAggregator
from gold.aggregators.database_loader import DatabaseLoader
from bronze.extractors.dgidb_extractor import DGIdbExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🔬 Extracting OncoHotspot data with REAL sample counts...")
    
    # Initialize extractors
    cbio_extractor = CBioPortalExtractor()
    dgidb_extractor = DGIdbExtractor()
    
    # Extract cBioPortal data with real sample counts
    print("\n📊 Extracting cBioPortal mutations with sample counts...")
    cbio_data = cbio_extractor.extract()
    
    # Show sample counts
    print("\n✅ Real sample counts from cBioPortal:")
    if 'study_sample_counts' in cbio_data:
        for study_id, count in sorted(cbio_data['study_sample_counts'].items()):
            print(f"  {study_id}: {count} samples")
        print(f"\nTotal studies with sample counts: {len(cbio_data['study_sample_counts'])}")
    else:
        print("  WARNING: No sample count data found!")
    
    # Standardize mutations
    print("\n⚙️ Standardizing mutations...")
    standardizer = MutationStandardizer()
    silver_mutations = []
    
    for mutation in cbio_data.get('mutations', []):
        standardized = standardizer.standardize(mutation, 'cbioportal')
        if standardized:
            silver_mutations.append(standardized)
    
    print(f"  Standardized {len(silver_mutations)} mutations")
    
    # Aggregate with real sample counts (will skip mutations without sample data)
    print("\n📈 Aggregating mutations (only including those with real sample counts)...")
    aggregator = MutationAggregator()
    result = aggregator.aggregate_for_heatmap(silver_mutations)
    
    print(f"\n✅ Aggregation results:")
    print(f"  Total mutations with proper denominators: {len(result['mutations'])}")
    print(f"  Unique genes: {len(result['genes'])}")
    print(f"  Cancer types: {len(result['cancer_types'])}")
    
    # Show sample of results
    print("\n📊 Sample of mutation frequencies with REAL denominators:")
    print("Gene     | Cancer    | Mutated | Total | Frequency")
    print("-" * 55)
    
    # Sort by frequency to show most significant
    sorted_mutations = sorted(result['mutations'], key=lambda x: x.get('frequency', 0), reverse=True)
    for mut in sorted_mutations[:15]:
        print(f"{mut['gene_symbol']:<8} | {mut['cancer_type']:<9} | {mut.get('mutated_samples', 0):>7} | {mut['sample_count']:>5} | {mut['frequency']:>6.2f}%")
    
    # Extract therapeutics for genes we have good data on
    print("\n💊 Extracting therapeutics from DGIdb...")
    unique_genes = list(result['genes'])
    print(f"  Fetching therapeutics for {len(unique_genes)} genes...")
    
    therapeutics_data = dgidb_extractor.extract(genes=unique_genes)
    print(f"  Found {len(therapeutics_data.get('interactions', []))} drug-gene interactions")
    
    # Load into database
    print("\n💾 Loading into database...")
    db_loader = DatabaseLoader()
    
    # Clear and load mutations
    cleared = db_loader.clear_existing_data('mutations')
    print(f"  Cleared {cleared} old mutation records")
    
    stats = db_loader.load_mutations(result['mutations'])
    print(f"  Loaded {stats['inserted']} mutations with real sample counts")
    
    # Load therapeutics
    if therapeutics_data.get('interactions'):
        therapeutic_stats = db_loader.load_therapeutics(therapeutics_data['interactions'])
        print(f"  Loaded {therapeutic_stats['inserted']} therapeutics")
    
    print("\n🎉 Complete! OncoHotspot now has biologically accurate mutation frequencies!")

if __name__ == "__main__":
    main()