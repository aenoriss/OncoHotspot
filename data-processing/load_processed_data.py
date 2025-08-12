#!/usr/bin/env python3
"""
Load processed data from gold layer into database
"""

import json
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gold.aggregators.database_loader import DatabaseLoader

def load_latest_data():
    """Load the latest processed data into database"""
    
    # Find latest heatmap data
    heatmap_dir = Path("gold/data/heatmap_data")
    latest_heatmap = max(heatmap_dir.glob("heatmap_*.json"))
    
    print(f"Loading data from: {latest_heatmap}")
    
    # Load heatmap data
    with open(latest_heatmap, 'r') as f:
        heatmap_data = json.load(f)
    
    print(f"Found {len(heatmap_data.get('mutations', []))} mutations")
    print(f"Covering {len(heatmap_data.get('genes', []))} genes")
    print(f"Across {len(heatmap_data.get('cancer_types', []))} cancer types")
    
    # Initialize database loader
    loader = DatabaseLoader()
    
    # Clear existing mutation data
    print("Clearing existing mutation data...")
    cleared_count = loader.clear_existing_data('mutations')
    print(f"Cleared {cleared_count} existing mutations")
    
    # Load new mutation data
    print("Loading new mutation data...")
    mutations = heatmap_data.get('mutations', [])
    
    if mutations:
        load_stats = loader.load_mutations(mutations)
        print(f"Database loading complete:")
        print(f"  Total records: {load_stats['total_records']}")
        print(f"  Inserted: {load_stats['inserted']}")
        print(f"  Updated: {load_stats['updated']}")
        print(f"  Failed: {load_stats['failed']}")
        print(f"  Genes added: {load_stats['genes_added']}")
        print(f"  Cancer types added: {load_stats['cancer_types_added']}")
    else:
        print("No mutations to load!")
    
    # Check final database state
    db_stats = loader.get_statistics()
    print("\nFinal database statistics:")
    for table, count in db_stats.items():
        print(f"  {table}: {count} records")

if __name__ == "__main__":
    load_latest_data()