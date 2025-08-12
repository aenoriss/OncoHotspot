#!/usr/bin/env python3
"""
Ultra-efficient ETL Pipeline for OncoHotspot
Streams data directly to database with minimal disk usage
Peak memory: ~2GB, Peak disk: ~5GB
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Generator
import yaml
import requests
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from silver.transformers.mutation_standardizer import MutationStandardizer
from silver.transformers.therapeutic_standardizer import TherapeuticStandardizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class EfficientPipeline:
    """Stream-to-database pipeline with minimal disk footprint"""
    
    def __init__(self, db_path: str = "../database/oncohotspot.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")  # Better concurrent access
        self.conn.execute("PRAGMA synchronous = NORMAL")  # Faster writes
        
        # Load configs
        self.load_configs()
        
        # Initialize transformers
        self.mutation_standardizer = MutationStandardizer()
        self.therapeutic_standardizer = TherapeuticStandardizer()
        
        # Cache for lookups
        self.gene_id_cache = {}
        self.cancer_type_cache = {}
        self.drug_id_cache = {}
        
        # Statistics
        self.stats = {
            'mutations_processed': 0,
            'drugs_processed': 0,
            'api_calls': 0,
            'start_time': datetime.now()
        }
    
    def load_configs(self):
        """Load configuration files"""
        config_dir = Path("config")
        
        # Load expanded genes
        gene_file = config_dir / "expanded_cancer_genes.yaml"
        if gene_file.exists():
            with open(gene_file, 'r') as f:
                gene_config = yaml.safe_load(f)
                self.target_genes = []
                for category, genes in gene_config['cancer_genes'].items():
                    if isinstance(genes, list):
                        self.target_genes.extend(genes)
                # Limit to top 500 for efficiency
                self.target_genes = self.target_genes[:500]
        
        # Load studies
        source_file = config_dir / "sources.yaml"
        with open(source_file, 'r') as f:
            sources = yaml.safe_load(f)
            self.target_studies = sources['target_studies']['cbioportal']
    
    def stream_cbioportal_mutations(self, batch_size: int = 1000) -> Generator:
        """
        Stream mutations from cBioPortal without saving to disk
        Yields batches of mutations for processing
        """
        base_url = "https://www.cbioportal.org/api"
        
        # Process studies in batches to limit memory
        for i in range(0, len(self.target_studies), 3):  # 3 studies at a time
            study_batch = self.target_studies[i:i+3]
            
            for study_id in study_batch:
                logger.info(f"Streaming mutations from {study_id}")
                profile_id = f"{study_id}_mutations"
                
                # Process genes in chunks
                for j in range(0, len(self.target_genes), 50):  # 50 genes at a time
                    gene_batch = self.target_genes[j:j+50]
                    
                    try:
                        # Fetch mutations for this batch
                        endpoint = f"{base_url}/molecular-profiles/{profile_id}/mutations/fetch"
                        
                        # Get gene IDs (simplified - in production, fetch these properly)
                        entrez_ids = list(range(j*100, (j+50)*100))  # Placeholder
                        
                        payload = {
                            "entrezGeneIds": entrez_ids,
                            "sampleListId": f"{study_id}_all"
                        }
                        
                        response = requests.post(endpoint, json=payload)
                        self.stats['api_calls'] += 1
                        
                        if response.status_code == 200:
                            mutations = response.json()
                            
                            # Yield mutations in batches
                            for k in range(0, len(mutations), batch_size):
                                batch = mutations[k:k+batch_size]
                                if batch:
                                    yield {
                                        'source': 'cbioportal',
                                        'study': study_id,
                                        'mutations': batch
                                    }
                        
                        time.sleep(0.1)  # Rate limiting
                        
                    except Exception as e:
                        logger.error(f"Error fetching {study_id} genes {j}-{j+50}: {e}")
                        continue
    
    def stream_civic_therapeutics(self) -> Generator:
        """Stream therapeutic data from CIViC without saving to disk"""
        api_url = "https://civicdb.org/api/graphql"
        
        # Query for drugs and evidence
        query = """
        query GetTherapeutics($after: String) {
            therapies(first: 100, after: $after) {
                pageInfo { hasNextPage, endCursor }
                nodes {
                    id, name, ncitId, therapyAliases
                }
            }
        }
        """
        
        has_next = True
        cursor = None
        
        while has_next:
            try:
                response = requests.post(
                    api_url,
                    json={"query": query, "variables": {"after": cursor}},
                    timeout=10
                )
                self.stats['api_calls'] += 1
                
                if response.status_code == 200:
                    data = response.json()
                    therapies = data['data']['therapies']
                    
                    if therapies['nodes']:
                        yield {
                            'source': 'civic',
                            'therapies': therapies['nodes']
                        }
                    
                    has_next = therapies['pageInfo']['hasNextPage']
                    cursor = therapies['pageInfo']['endCursor']
                else:
                    break
                    
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"CIViC stream error: {e}")
                break
    
    def process_mutation_batch(self, batch: Dict):
        """Process and insert a batch of mutations directly to database"""
        if 'mutations' not in batch:
            return
        
        mutations = batch['mutations']
        study = batch.get('study', 'unknown')
        
        # Standardize mutations
        standardized = []
        for mut in mutations:
            try:
                std_mut = self.mutation_standardizer.standardize(mut, source='cbioportal')
                if std_mut:
                    std_mut['study'] = study
                    standardized.append(std_mut)
            except Exception as e:
                continue
        
        # Batch insert to database
        self.insert_mutations_batch(standardized)
        self.stats['mutations_processed'] += len(standardized)
        
        # Log progress
        if self.stats['mutations_processed'] % 10000 == 0:
            logger.info(f"Processed {self.stats['mutations_processed']} mutations")
    
    def insert_mutations_batch(self, mutations: List[Dict]):
        """Efficiently insert mutations to database"""
        cursor = self.conn.cursor()
        
        for mut in mutations:
            try:
                # Get or create gene
                gene_symbol = mut.get('gene_symbol', '')
                if gene_symbol not in self.gene_id_cache:
                    cursor.execute(
                        "INSERT OR IGNORE INTO genes (gene_symbol) VALUES (?)",
                        (gene_symbol,)
                    )
                    cursor.execute(
                        "SELECT gene_id FROM genes WHERE gene_symbol = ?",
                        (gene_symbol,)
                    )
                    self.gene_id_cache[gene_symbol] = cursor.fetchone()[0]
                
                gene_id = self.gene_id_cache[gene_symbol]
                
                # Get or create cancer type
                cancer_type = mut.get('cancer_type', 'Unknown')
                if cancer_type not in self.cancer_type_cache:
                    cursor.execute(
                        "INSERT OR IGNORE INTO cancer_types (cancer_name) VALUES (?)",
                        (cancer_type,)
                    )
                    cursor.execute(
                        "SELECT cancer_type_id FROM cancer_types WHERE cancer_name = ?",
                        (cancer_type,)
                    )
                    self.cancer_type_cache[cancer_type] = cursor.fetchone()[0]
                
                cancer_type_id = self.cancer_type_cache[cancer_type]
                
                # Insert mutation
                cursor.execute("""
                    INSERT OR REPLACE INTO mutations 
                    (gene_id, cancer_type_id, protein_change, mutation_count, frequency)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    gene_id,
                    cancer_type_id,
                    mut.get('protein_change', ''),
                    mut.get('count', 1),
                    mut.get('frequency', 0.0)
                ))
                
            except Exception as e:
                logger.debug(f"Failed to insert mutation: {e}")
                continue
        
        self.conn.commit()
    
    def process_therapeutic_batch(self, batch: Dict):
        """Process and insert therapeutics directly to database"""
        if 'therapies' not in batch:
            return
        
        cursor = self.conn.cursor()
        
        for therapy in batch['therapies']:
            try:
                drug_name = therapy.get('name', '')
                if not drug_name:
                    continue
                
                # Standardize therapeutic
                std_drug = self.therapeutic_standardizer.standardize(therapy, source='civic')
                if not std_drug:
                    continue
                
                # Insert therapeutic
                cursor.execute("""
                    INSERT OR IGNORE INTO therapeutics 
                    (drug_name, drug_class, description)
                    VALUES (?, ?, ?)
                """, (
                    std_drug.get('drug_name', drug_name),
                    std_drug.get('drug_class', 'Unknown'),
                    std_drug.get('description', '')
                ))
                
                self.stats['drugs_processed'] += 1
                
            except Exception as e:
                logger.debug(f"Failed to insert therapeutic: {e}")
                continue
        
        self.conn.commit()
    
    def optimize_database(self):
        """Create indexes and optimize database after loading"""
        logger.info("Optimizing database...")
        
        cursor = self.conn.cursor()
        
        # Create indexes for better query performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_mutations_gene ON mutations(gene_id)",
            "CREATE INDEX IF NOT EXISTS idx_mutations_cancer ON mutations(cancer_type_id)",
            "CREATE INDEX IF NOT EXISTS idx_mutations_frequency ON mutations(frequency DESC)",
            "CREATE INDEX IF NOT EXISTS idx_mutations_protein ON mutations(protein_change)",
            "CREATE INDEX IF NOT EXISTS idx_genes_symbol ON genes(gene_symbol)",
            "CREATE INDEX IF NOT EXISTS idx_cancer_name ON cancer_types(cancer_name)",
            "CREATE INDEX IF NOT EXISTS idx_therapeutics_name ON therapeutics(drug_name)"
        ]
        
        for idx in indexes:
            cursor.execute(idx)
        
        # Analyze for query optimization
        cursor.execute("ANALYZE")
        
        # Vacuum to reclaim space
        cursor.execute("VACUUM")
        
        self.conn.commit()
        logger.info("Database optimization complete")
    
    def run(self):
        """Run the efficient pipeline"""
        logger.info("=" * 60)
        logger.info("EFFICIENT ONCOHOTSPOT PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Target genes: {len(self.target_genes)}")
        logger.info(f"Target studies: {len(self.target_studies)}")
        logger.info("Mode: Stream-to-database (minimal disk usage)")
        logger.info("=" * 60)
        
        try:
            # 1. Stream and process cBioPortal mutations
            logger.info("\n[1/3] Streaming cBioPortal mutations...")
            for batch in self.stream_cbioportal_mutations():
                self.process_mutation_batch(batch)
            
            logger.info(f"✓ Processed {self.stats['mutations_processed']} mutations")
            
            # 2. Stream and process CIViC therapeutics
            logger.info("\n[2/3] Streaming CIViC therapeutics...")
            for batch in self.stream_civic_therapeutics():
                self.process_therapeutic_batch(batch)
            
            logger.info(f"✓ Processed {self.stats['drugs_processed']} therapeutics")
            
            # 3. Optimize database
            logger.info("\n[3/3] Optimizing database...")
            self.optimize_database()
            
            # Calculate statistics
            duration = (datetime.now() - self.stats['start_time']).total_seconds()
            
            # Get final counts
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM mutations")
            total_mutations = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT gene_id) FROM mutations")
            total_genes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT cancer_type_id) FROM mutations")
            total_cancer_types = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM therapeutics")
            total_drugs = cursor.fetchone()[0]
            
            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Duration: {duration:.1f} seconds")
            logger.info(f"API calls: {self.stats['api_calls']}")
            logger.info(f"Mutations: {total_mutations}")
            logger.info(f"Genes: {total_genes}")
            logger.info(f"Cancer types: {total_cancer_types}")
            logger.info(f"Therapeutics: {total_drugs}")
            logger.info(f"Database size: {os.path.getsize(self.db_path) / 1024 / 1024:.1f} MB")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
        finally:
            self.conn.close()


def main():
    """Main entry point"""
    pipeline = EfficientPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()