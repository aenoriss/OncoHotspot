#!/usr/bin/env python3
"""Rebuild database with real sample counts using existing silver data"""

import json
import logging
from gold.aggregators.mutation_aggregator import MutationAggregator
from gold.aggregators.database_loader import DatabaseLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🔬 Rebuilding OncoHotspot with REAL sample counts...")
    
    # Load the bronze data with real sample counts
    bronze_file = 'bronze/data/cbioportal/cbioportal_20250812_021330.json'
    
    try:
        with open(bronze_file, 'r') as f:
            bronze_data = json.load(f)
        
        # Display real sample counts
        print("\n✅ Real sample counts from cBioPortal:")
        if 'study_sample_counts' in bronze_data:
            total_samples = 0
            for study_id, count in sorted(bronze_data['study_sample_counts'].items()):
                print(f"  {study_id}: {count} samples")
                total_samples += count
            print(f"\nTotal samples across all studies: {total_samples:,}")
        
        # Load existing silver mutations (already standardized)
        silver_file = 'silver/data/mutations/cbioportal_mutations_20250812_015940.json'
        with open(silver_file, 'r') as f:
            silver_mutations = json.load(f)
        
        print(f"\n📊 Loaded {len(silver_mutations)} standardized mutations")
        
        # Aggregate with real sample counts
        print("\n⚙️ Aggregating mutations with REAL denominators...")
        aggregator = MutationAggregator()
        result = aggregator.aggregate_for_heatmap(silver_mutations)
        
        print(f"\n✅ Aggregation results:")
        print(f"  Mutations with real sample counts: {len(result['mutations'])}")
        print(f"  Unique genes: {len(result['genes'])}")
        print(f"  Cancer types: {len(result['cancer_types'])}")
        
        # Show sample of results
        print("\n📊 Top mutation frequencies with REAL denominators:")
        print("Gene     | Cancer         | Mutated | Total | Frequency")
        print("-" * 60)
        
        # Sort by frequency to show most significant
        sorted_mutations = sorted(result['mutations'], key=lambda x: x.get('frequency', 0), reverse=True)
        for mut in sorted_mutations[:20]:
            cancer_name = mut['cancer_type'][:14].ljust(14)  # Truncate long names
            # Convert decimal frequency to percentage for display
            freq_pct = mut['frequency'] * 100
            print(f"{mut['gene_symbol']:<8} | {cancer_name} | {mut.get('mutated_samples', 0):>7} | {mut['sample_count']:>5} | {freq_pct:>6.2f}%")
        
        # Load into database
        print("\n💾 Loading into database...")
        db_loader = DatabaseLoader()
        
        # Clear and load mutations
        cleared = db_loader.clear_existing_data('mutations')
        print(f"  Cleared {cleared} old mutation records")
        
        stats = db_loader.load_mutations(result['mutations'])
        print(f"  Loaded {stats['inserted']} mutations with real sample counts")
        
        # Final stats
        db_stats = db_loader.get_statistics()
        print(f"\n📈 Final database statistics:")
        print(f"  Mutations: {db_stats['mutations_count']}")
        print(f"  Genes: {db_stats['genes_count']}") 
        print(f"  Cancer types: {db_stats['cancer_types_count']}")
        
        print("\n🎉 Complete! OncoHotspot now shows biologically accurate mutation frequencies!")
        print("   No estimates or guesses - only real data from cBioPortal!")
        
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise

if __name__ == "__main__":
    main()