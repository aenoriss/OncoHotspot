#!/usr/bin/env python3
"""Quick script to fix mutation frequencies using existing silver data"""

import json
import logging
from gold.aggregators.mutation_aggregator import MutationAggregator
from gold.aggregators.database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🔧 Fixing mutation frequencies using existing silver data...")
    
    # Load existing silver mutations
    silver_file = 'silver/data/mutations/cbioportal_mutations_20250812_015940.json'
    
    try:
        with open(silver_file, 'r') as f:
            silver_mutations = json.load(f)
        
        print(f"📊 Loaded {len(silver_mutations)} silver mutations")
        
        # Initialize aggregator and database loader
        aggregator = MutationAggregator()
        db_loader = DatabaseLoader()
        
        # Clear existing data
        print("🗑️ Clearing existing mutation data...")
        cleared = db_loader.clear_existing_data('mutations')
        print(f"Cleared {cleared} mutation records")
        
        # Aggregate with fixed frequencies
        print("⚙️ Aggregating mutations with fixed frequencies...")
        result = aggregator.aggregate_for_heatmap(silver_mutations)
        
        # Show sample of fixed frequencies
        print("\n✅ Fixed frequencies sample:")
        print("Gene | Cancer | Mutated | Total | Frequency")
        print("-" * 50)
        for mut in result['mutations'][:10]:
            print(f"{mut['gene_symbol']:<8} | {mut['cancer_type']:<7} | {mut.get('mutated_samples', 0):>7} | {mut['sample_count']:>5} | {mut['frequency']:>6.2f}%")
        
        # Load into database
        print(f"\n💾 Loading {len(result['mutations'])} mutations into database...")
        stats = db_loader.load_mutations(result['mutations'])
        
        print(f"\n🎉 Database loading complete!")
        print(f"   Inserted: {stats['inserted']}")
        print(f"   Updated: {stats['updated']}")
        print(f"   Failed: {stats['failed']}")
        
        # Get final stats
        db_stats = db_loader.get_statistics()
        print(f"\n📈 Final database statistics:")
        print(f"   Mutations: {db_stats['mutations_count']}")
        print(f"   Genes: {db_stats['genes_count']}")
        print(f"   Cancer types: {db_stats['cancer_types_count']}")
        
    except Exception as e:
        logger.error(f"Failed to fix frequencies: {e}")
        raise

if __name__ == "__main__":
    main()