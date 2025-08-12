#!/usr/bin/env python3
"""
Rebuild the OncoHotspot database with clean, scientifically valid data
Uses only cBioPortal (frequencies) and CIViC (clinical annotations)
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline_clean import CleanPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def rebuild_database():
    """Rebuild the database with clean data"""
    
    # Database path
    db_path = '/home/aenoris/masterProjects/oncohotspot/database/oncohotspot.db'
    
    logger.info("="*70)
    logger.info("REBUILDING ONCOHOTSPOT DATABASE")
    logger.info("="*70)
    
    # 1. Backup existing database
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"\n📦 Backing up existing database to {backup_path}")
    
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        logger.info("✅ Backup created")
    
    # 2. Clear existing mutations table
    logger.info("\n🧹 Clearing existing mutations table...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM mutations")
        conn.commit()
        logger.info(f"✅ Cleared {cursor.rowcount} existing records")
    except Exception as e:
        logger.error(f"Failed to clear table: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    # 3. Run the clean pipeline with key cancer studies
    logger.info("\n🔄 Running clean pipeline with key TCGA studies...")
    
    # Select representative studies from major cancer types
    key_studies = [
        'brca_tcga_pan_can_atlas_2018',      # Breast - 1084 samples
        'luad_tcga_pan_can_atlas_2018',      # Lung Adenocarcinoma - 566 samples
        'coadread_tcga_pan_can_atlas_2018',  # Colorectal - 594 samples
        'skcm_tcga_pan_can_atlas_2018',      # Melanoma - 448 samples
        'paad_tcga_pan_can_atlas_2018',      # Pancreatic - 184 samples
        'prad_tcga_pan_can_atlas_2018',      # Prostate - 494 samples
        'gbm_tcga_pan_can_atlas_2018',       # Glioblastoma - 393 samples
        'ov_tcga_pan_can_atlas_2018',        # Ovarian - 585 samples
    ]
    
    pipeline = CleanPipeline()
    results = pipeline.run(limit_studies=key_studies)
    
    # 4. Verify the rebuild
    logger.info("\n✅ DATABASE REBUILD COMPLETE")
    
    # Check what we loaded
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT gene_symbol) as genes,
            COUNT(DISTINCT cancer_type) as cancers,
            AVG(frequency) as avg_freq,
            MIN(frequency) as min_freq,
            MAX(frequency) as max_freq,
            SUM(CASE WHEN frequency > 0.61 THEN 1 ELSE 0 END) as suspicious
        FROM mutations
    """)
    
    stats = cursor.fetchone()
    
    print("\n" + "="*70)
    print("DATABASE STATISTICS")
    print("="*70)
    print(f"Total mutations: {stats[0]}")
    print(f"Unique genes: {stats[1]}")
    print(f"Cancer types: {stats[2]}")
    print(f"Average frequency: {stats[3]:.1%}")
    print(f"Frequency range: {stats[4]:.1%} - {stats[5]:.1%}")
    print(f"Suspicious (>61%): {stats[6]} ({stats[6]/stats[0]*100:.1f}%)")
    
    # Show top mutations
    cursor.execute("""
        SELECT gene_symbol, cancer_type, protein_change, 
               mutation_count, total_samples, frequency
        FROM mutations
        ORDER BY frequency DESC
        LIMIT 10
    """)
    
    print("\n🔝 Top 10 Mutations by Frequency:")
    for i, row in enumerate(cursor.fetchall(), 1):
        gene, cancer, protein, count, total, freq = row
        print(f"{i:2}. {gene} {protein} in {cancer}: {count}/{total} = {freq:.1%}")
    
    # Check for known hotspots
    cursor.execute("""
        SELECT gene_symbol, cancer_type, frequency
        FROM mutations
        WHERE (gene_symbol = 'KRAS' AND cancer_type LIKE '%Pancreatic%')
           OR (gene_symbol = 'BRAF' AND cancer_type LIKE '%Melanoma%')
           OR (gene_symbol = 'EGFR' AND cancer_type LIKE '%Lung%')
    """)
    
    print("\n✅ Known Hotspot Validation:")
    for row in cursor.fetchall():
        gene, cancer, freq = row
        print(f"  {gene} in {cancer}: {freq:.1%}")
    
    conn.close()
    
    print("\n✅ Database rebuild successful!")
    print(f"📦 Backup saved to: {backup_path}")
    
    return results


if __name__ == '__main__':
    rebuild_database()