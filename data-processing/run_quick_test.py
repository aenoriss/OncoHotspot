#!/usr/bin/env python3
"""Quick test of the pipeline with limited data to verify it works"""

import sys
import os
import logging

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import OncoHotspotPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 60)
    print("QUICK PIPELINE TEST")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = OncoHotspotPipeline()
    
    # Clear existing data
    pipeline.clear_database()
    
    # Run with just cBioPortal, limited to a few key genes
    # This will use the genes from config which should be ~30 genes
    print("\nRunning pipeline with cBioPortal only...")
    print("This should fetch data for configured genes (~30 genes)")
    
    stats = pipeline.run_full_pipeline(['cbioportal'])
    
    # Print results
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Status: {stats['status']}")
    print(f"Duration: {stats.get('duration_seconds', 0):.2f} seconds")
    
    if 'bronze' in stats:
        print(f"\nBronze layer:")
        for source, info in stats['bronze'].items():
            print(f"  {source}: {info.get('record_count', 0)} records")
    
    if 'silver' in stats:
        print(f"\nSilver layer:")
        for source, info in stats['silver'].items():
            print(f"  {source}: {info.get('output_count', 0)} standardized")
    
    if 'gold' in stats:
        print(f"\nGold layer:")
        gold = stats['gold']
        print(f"  Unique mutations: {gold.get('output_count', 0)}")
        print(f"  Unique genes: {gold.get('unique_genes', 0)}")
        print(f"  Unique cancer types: {gold.get('unique_cancer_types', 0)}")
    
    if 'database' in stats:
        print(f"\nDatabase:")
        db = stats['database']
        print(f"  Inserted: {db.get('inserted', 0)}")
        print(f"  Updated: {db.get('updated', 0)}")
        print(f"  Failed: {db.get('failed', 0)}")
    
    print("=" * 60)
    
    return 0 if stats['status'] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())