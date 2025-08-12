#!/usr/bin/env python3
"""
Enhanced ETL Pipeline for OncoHotspot
Integrates multiple data sources with 10-100x more data
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import yaml
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Bronze layer extractors
from bronze.extractors.cbioportal_extractor import CBioPortalExtractor
from bronze.extractors.civic_extractor import CIViCExtractor
from bronze.extractors.opentargets_extractor import OpenTargetsExtractor

# Silver layer transformers
from silver.transformers.mutation_standardizer import MutationStandardizer
from silver.transformers.therapeutic_standardizer import TherapeuticStandardizer

# Gold layer aggregators
from gold.aggregators.mutation_aggregator import MutationAggregator
from gold.aggregators.database_loader import DatabaseLoader

# Services
from services.description_service import DescriptionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExpandedPipeline:
    """Enhanced ETL pipeline with multiple data sources"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.load_configs()
        
        # Initialize components
        self.description_service = DescriptionService()
        
        # Pipeline statistics
        self.stats = {
            "start_time": None,
            "end_time": None,
            "sources": [],
            "bronze": {},
            "silver": {},
            "gold": {},
            "database": {}
        }
    
    def load_configs(self):
        """Load all configuration files"""
        # Load expanded gene list
        gene_file = self.config_dir / "expanded_cancer_genes.yaml"
        if gene_file.exists():
            with open(gene_file, 'r') as f:
                self.gene_config = yaml.safe_load(f)
                # Flatten all gene lists
                self.all_genes = []
                for category, genes in self.gene_config['cancer_genes'].items():
                    if isinstance(genes, list):
                        self.all_genes.extend(genes)
                logger.info(f"Loaded {len(self.all_genes)} genes from expanded config")
        else:
            # Fall back to original gene list
            gene_file = self.config_dir / "clinically_actionable_genes.yaml"
            with open(gene_file, 'r') as f:
                self.gene_config = yaml.safe_load(f)
                self.all_genes = self._extract_genes_from_config(self.gene_config)
                logger.info(f"Loaded {len(self.all_genes)} genes from original config")
        
        # Load source configuration
        source_file = self.config_dir / "sources.yaml"
        with open(source_file, 'r') as f:
            self.source_config = yaml.safe_load(f)
        
        # Load cancer types
        cancer_file = self.config_dir / "cancer_types.yaml"
        with open(cancer_file, 'r') as f:
            self.cancer_config = yaml.safe_load(f)
    
    def _extract_genes_from_config(self, config: Dict) -> List[str]:
        """Extract gene symbols from configuration"""
        genes = []
        
        if 'clinically_actionable_genes' in config:
            for category, gene_list in config['clinically_actionable_genes'].items():
                if isinstance(gene_list, list):
                    for item in gene_list:
                        if isinstance(item, str):
                            genes.append(item)
                        elif isinstance(item, dict):
                            genes.extend(item.keys())
        
        return list(set(genes))
    
    def run_bronze_layer(self, sources: List[str]) -> Dict[str, Any]:
        """Run bronze layer extraction from multiple sources"""
        logger.info("=" * 60)
        logger.info("BRONZE LAYER: Raw Data Extraction")
        logger.info("=" * 60)
        
        bronze_data = {}
        
        # 1. cBioPortal extraction (expanded)
        if 'cbioportal' in sources:
            logger.info("\n[1/3] Extracting from cBioPortal...")
            try:
                extractor = CBioPortalExtractor()
                
                # Use top 500 genes and all 33 TCGA studies
                top_genes = self.all_genes[:500]
                all_studies = self.source_config['target_studies']['cbioportal']
                
                logger.info(f"Fetching {len(top_genes)} genes from {len(all_studies)} studies")
                
                cbio_data = extractor.extract(
                    genes=top_genes,
                    studies=all_studies
                )
                
                bronze_data['cbioportal'] = cbio_data
                self.stats['bronze']['cbioportal'] = {
                    'status': 'success',
                    'mutation_count': len(cbio_data.get('mutations', [])),
                    'study_count': len(all_studies),
                    'gene_count': len(top_genes)
                }
                logger.info(f"✓ cBioPortal: {len(cbio_data.get('mutations', []))} mutations")
                
            except Exception as e:
                logger.error(f"✗ cBioPortal extraction failed: {e}")
                self.stats['bronze']['cbioportal'] = {'status': 'failed', 'error': str(e)}
        
        # 2. CIViC extraction
        if 'civic' in sources:
            logger.info("\n[2/3] Extracting from CIViC...")
            try:
                extractor = CIViCExtractor()
                civic_data = extractor.extract(gene_symbols=self.all_genes[:500])
                
                bronze_data['civic'] = civic_data
                self.stats['bronze']['civic'] = {
                    'status': 'success',
                    'variant_count': len(civic_data.get('variants', [])),
                    'therapy_count': len(civic_data.get('therapies', [])),
                    'evidence_count': len(civic_data.get('evidence_items', []))
                }
                logger.info(f"✓ CIViC: {len(civic_data.get('variants', []))} variants, "
                          f"{len(civic_data.get('therapies', []))} therapies")
                
            except Exception as e:
                logger.error(f"✗ CIViC extraction failed: {e}")
                self.stats['bronze']['civic'] = {'status': 'failed', 'error': str(e)}
        
        # 3. OpenTargets extraction
        if 'opentargets' in sources:
            logger.info("\n[3/3] Extracting from OpenTargets...")
            try:
                extractor = OpenTargetsExtractor()
                ot_data = extractor.extract(gene_symbols=self.all_genes[:200])
                
                bronze_data['opentargets'] = ot_data
                self.stats['bronze']['opentargets'] = {
                    'status': 'success',
                    'target_count': len(ot_data.get('targets', [])),
                    'drug_count': len(ot_data.get('drugs', [])),
                    'interaction_count': len(ot_data.get('drug_target_interactions', []))
                }
                logger.info(f"✓ OpenTargets: {len(ot_data.get('drugs', []))} drugs, "
                          f"{len(ot_data.get('drug_target_interactions', []))} interactions")
                
            except Exception as e:
                logger.error(f"✗ OpenTargets extraction failed: {e}")
                self.stats['bronze']['opentargets'] = {'status': 'failed', 'error': str(e)}
        
        return bronze_data
    
    def run_silver_layer(self, bronze_data: Dict) -> Dict[str, Any]:
        """Run silver layer transformation"""
        logger.info("\n" + "=" * 60)
        logger.info("SILVER LAYER: Data Standardization")
        logger.info("=" * 60)
        
        silver_data = {}
        
        # 1. Standardize cBioPortal mutations
        if 'cbioportal' in bronze_data:
            logger.info("\n[1/3] Standardizing cBioPortal mutations...")
            try:
                standardizer = MutationStandardizer()
                mutations = bronze_data['cbioportal'].get('mutations', [])
                
                standardized = standardizer.standardize_batch(mutations, source='cbioportal')
                silver_data['mutations'] = standardized
                
                self.stats['silver']['mutations'] = {
                    'status': 'success',
                    'input_count': len(mutations),
                    'output_count': len(standardized)
                }
                logger.info(f"✓ Standardized {len(standardized)} mutations")
                
            except Exception as e:
                logger.error(f"✗ Mutation standardization failed: {e}")
                self.stats['silver']['mutations'] = {'status': 'failed', 'error': str(e)}
        
        # 2. Standardize CIViC therapeutics
        if 'civic' in bronze_data:
            logger.info("\n[2/3] Standardizing CIViC therapeutics...")
            try:
                standardizer = TherapeuticStandardizer()
                
                # Combine therapies and evidence
                therapies = bronze_data['civic'].get('therapies', [])
                evidence = bronze_data['civic'].get('evidence_items', [])
                
                standardized_therapies = []
                for therapy in therapies:
                    std_therapy = standardizer.standardize(therapy, source='civic')
                    if std_therapy:
                        standardized_therapies.append(std_therapy)
                
                silver_data['civic_therapeutics'] = {
                    'therapies': standardized_therapies,
                    'evidence': evidence
                }
                
                self.stats['silver']['civic_therapeutics'] = {
                    'status': 'success',
                    'therapy_count': len(standardized_therapies),
                    'evidence_count': len(evidence)
                }
                logger.info(f"✓ Standardized {len(standardized_therapies)} CIViC therapeutics")
                
            except Exception as e:
                logger.error(f"✗ CIViC standardization failed: {e}")
                self.stats['silver']['civic_therapeutics'] = {'status': 'failed', 'error': str(e)}
        
        # 3. Standardize OpenTargets drugs
        if 'opentargets' in bronze_data:
            logger.info("\n[3/3] Standardizing OpenTargets drugs...")
            try:
                standardizer = TherapeuticStandardizer()
                
                drugs = bronze_data['opentargets'].get('drugs', [])
                interactions = bronze_data['opentargets'].get('drug_target_interactions', [])
                
                standardized_drugs = []
                for drug in drugs:
                    std_drug = standardizer.standardize(drug, source='opentargets')
                    if std_drug:
                        standardized_drugs.append(std_drug)
                
                silver_data['opentargets_therapeutics'] = {
                    'drugs': standardized_drugs,
                    'interactions': interactions
                }
                
                self.stats['silver']['opentargets_therapeutics'] = {
                    'status': 'success',
                    'drug_count': len(standardized_drugs),
                    'interaction_count': len(interactions)
                }
                logger.info(f"✓ Standardized {len(standardized_drugs)} OpenTargets drugs")
                
            except Exception as e:
                logger.error(f"✗ OpenTargets standardization failed: {e}")
                self.stats['silver']['opentargets_therapeutics'] = {'status': 'failed', 'error': str(e)}
        
        return silver_data
    
    def run_gold_layer(self, silver_data: Dict) -> Dict[str, Any]:
        """Run gold layer aggregation"""
        logger.info("\n" + "=" * 60)
        logger.info("GOLD LAYER: Business Aggregation")
        logger.info("=" * 60)
        
        gold_data = {}
        
        # 1. Aggregate mutations
        logger.info("\n[1/3] Aggregating mutations...")
        try:
            aggregator = MutationAggregator()
            
            mutations = silver_data.get('mutations', [])
            aggregated_result = aggregator.aggregate(mutations)
            
            gold_data['mutations'] = aggregated_result
            
            # Extract heatmap mutations for stats
            heatmap_mutations = aggregated_result.get('heatmap', {}).get('mutations', [])
            heatmap_summary = aggregated_result.get('heatmap', {}).get('summary', {})
            
            self.stats['gold']['mutations'] = {
                'status': 'success',
                'total_mutations': heatmap_summary.get('total_mutations', len(heatmap_mutations)),
                'unique_genes': heatmap_summary.get('unique_genes', 0),
                'unique_cancer_types': heatmap_summary.get('unique_cancer_types', 0)
            }
            logger.info(f"✓ Aggregated {heatmap_summary.get('total_mutations', 0)} mutations across "
                       f"{heatmap_summary.get('unique_genes', 0)} genes and {heatmap_summary.get('unique_cancer_types', 0)} cancer types")
            
        except Exception as e:
            logger.error(f"✗ Mutation aggregation failed: {e}")
            self.stats['gold']['mutations'] = {'status': 'failed', 'error': str(e)}
        
        # 2. Aggregate therapeutic associations
        logger.info("\n[2/3] Creating therapeutic associations...")
        try:
            all_therapeutics = []
            all_associations = []
            
            # Combine therapeutics from all sources
            if 'civic_therapeutics' in silver_data:
                all_therapeutics.extend(silver_data['civic_therapeutics']['therapies'])
            
            if 'opentargets_therapeutics' in silver_data:
                all_therapeutics.extend(silver_data['opentargets_therapeutics']['drugs'])
            
            # Create associations
            # This is simplified - in production, use evidence and interaction data
            gene_drug_map = {}
            
            if 'opentargets_therapeutics' in silver_data:
                for interaction in silver_data['opentargets_therapeutics']['interactions']:
                    gene = interaction.get('target_symbol')
                    drug = interaction.get('drug_name')
                    
                    if gene and drug:
                        if gene not in gene_drug_map:
                            gene_drug_map[gene] = []
                        gene_drug_map[gene].append(drug)
            
            gold_data['therapeutics'] = all_therapeutics
            gold_data['gene_drug_associations'] = gene_drug_map
            
            self.stats['gold']['therapeutics'] = {
                'status': 'success',
                'total_drugs': len(all_therapeutics),
                'genes_with_drugs': len(gene_drug_map),
                'total_associations': sum(len(drugs) for drugs in gene_drug_map.values())
            }
            logger.info(f"✓ Created {self.stats['gold']['therapeutics']['total_associations']} "
                       f"associations for {len(gene_drug_map)} genes")
            
        except Exception as e:
            logger.error(f"✗ Therapeutic aggregation failed: {e}")
            self.stats['gold']['therapeutics'] = {'status': 'failed', 'error': str(e)}
        
        # 3. Add descriptions
        logger.info("\n[3/3] Adding gene and drug descriptions...")
        try:
            # Get unique genes and drugs
            unique_genes = set()
            if 'mutations' in gold_data:
                # Extract genes from heatmap data
                heatmap_data = gold_data['mutations'].get('heatmap', {})
                if 'genes' in heatmap_data:
                    unique_genes.update(heatmap_data['genes'])
                elif 'mutations' in heatmap_data:
                    unique_genes.update(m.get('gene_symbol', '') for m in heatmap_data['mutations'])
            
            unique_drugs = set()
            if 'therapeutics' in gold_data:
                unique_drugs.update(t.get('drug_name', t.get('name', '')) for t in gold_data['therapeutics'])
            
            # Batch fetch descriptions
            logger.info(f"Fetching descriptions for {len(unique_genes)} genes...")
            gene_descriptions = self.description_service.batch_get_gene_descriptions(list(unique_genes)[:100])
            
            logger.info(f"Fetching descriptions for {len(unique_drugs)} drugs...")
            drug_descriptions = self.description_service.batch_get_drug_descriptions(list(unique_drugs)[:50])
            
            gold_data['descriptions'] = {
                'genes': gene_descriptions,
                'drugs': drug_descriptions
            }
            
            # Get description service stats
            desc_stats = self.description_service.get_stats()
            self.stats['gold']['descriptions'] = {
                'status': 'success',
                'gene_descriptions': len(gene_descriptions),
                'drug_descriptions': len(drug_descriptions),
                'cache_hit_rate': desc_stats['cache_hit_rate'],
                'claude_api_calls': desc_stats['claude_api_calls'],
                'estimated_claude_cost': desc_stats['estimated_claude_cost']
            }
            
            logger.info(f"✓ Added {len(gene_descriptions)} gene and {len(drug_descriptions)} drug descriptions")
            logger.info(f"  Cache hit rate: {desc_stats['cache_hit_rate']:.1%}")
            logger.info(f"  Claude API calls: {desc_stats['claude_api_calls']}")
            logger.info(f"  Estimated Claude cost: ${desc_stats['estimated_claude_cost']:.2f}")
            
        except Exception as e:
            logger.error(f"✗ Description fetching failed: {e}")
            self.stats['gold']['descriptions'] = {'status': 'failed', 'error': str(e)}
        
        return gold_data
    
    def load_to_database(self, gold_data: Dict):
        """Load data to database"""
        logger.info("\n" + "=" * 60)
        logger.info("DATABASE: Loading to SQLite")
        logger.info("=" * 60)
        
        try:
            loader = DatabaseLoader()
            
            # Load mutations - extract from heatmap data
            mutation_data = gold_data.get('mutations', {})
            if isinstance(mutation_data, dict) and 'heatmap' in mutation_data:
                mutations = mutation_data['heatmap'].get('mutations', [])
            else:
                mutations = mutation_data if isinstance(mutation_data, list) else []
            
            load_stats = loader.load_mutations(mutations)
            
            # Load therapeutics
            therapeutics = gold_data.get('therapeutics', [])
            loader.load_therapeutics(therapeutics)
            
            # Load associations
            associations = gold_data.get('gene_drug_associations', {})
            loader.load_associations(associations)
            
            # Load descriptions
            descriptions = gold_data.get('descriptions', {})
            loader.load_descriptions(descriptions)
            
            # Get database statistics
            db_stats = loader.get_statistics()
            
            self.stats['database'] = {
                'status': 'success',
                'mutations_loaded': db_stats['mutations'],
                'therapeutics_loaded': db_stats['therapeutics'],
                'associations_loaded': db_stats['associations'],
                'genes_count': db_stats['genes'],
                'cancer_types_count': db_stats['cancer_types']
            }
            
            logger.info(f"✓ Database loading complete:")
            logger.info(f"  - {db_stats['mutations']} mutations")
            logger.info(f"  - {db_stats['therapeutics']} therapeutics")
            logger.info(f"  - {db_stats['associations']} associations")
            logger.info(f"  - {db_stats['genes']} genes")
            logger.info(f"  - {db_stats['cancer_types']} cancer types")
            
        except Exception as e:
            logger.error(f"✗ Database loading failed: {e}")
            self.stats['database'] = {'status': 'failed', 'error': str(e)}
    
    def run(self, sources: List[str] = None, skip_layers: List[str] = None):
        """Run the complete pipeline"""
        self.stats['start_time'] = datetime.now()
        
        # Default sources if not specified
        if not sources:
            sources = ['cbioportal', 'civic', 'opentargets']
        
        self.stats['sources'] = sources
        
        # Skip layers if specified
        skip_layers = skip_layers or []
        
        logger.info("=" * 60)
        logger.info("ENHANCED ONCOHOTSPOT ETL PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Sources: {', '.join(sources)}")
        logger.info(f"Genes: {len(self.all_genes)}")
        logger.info(f"Studies: {len(self.source_config['target_studies']['cbioportal'])}")
        logger.info("=" * 60)
        
        # Run pipeline layers
        bronze_data = {}
        silver_data = {}
        gold_data = {}
        
        if 'bronze' not in skip_layers:
            bronze_data = self.run_bronze_layer(sources)
        
        if 'silver' not in skip_layers and bronze_data:
            silver_data = self.run_silver_layer(bronze_data)
        
        if 'gold' not in skip_layers and silver_data:
            gold_data = self.run_gold_layer(silver_data)
        
        if 'database' not in skip_layers and gold_data:
            self.load_to_database(gold_data)
        
        # Complete pipeline
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        self.stats['duration_seconds'] = duration
        
        # Save pipeline statistics
        self.save_stats()
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info(f"Status: SUCCESS")
        
        self.print_summary()
    
    def save_stats(self):
        """Save pipeline statistics"""
        stats_dir = Path("logs")
        stats_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_file = stats_dir / f"pipeline_expanded_{timestamp}.json"
        
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        
        logger.info(f"Statistics saved to {stats_file}")
    
    def print_summary(self):
        """Print pipeline summary"""
        print("\n" + "=" * 60)
        print("PIPELINE SUMMARY")
        print("=" * 60)
        
        # Bronze layer summary
        print("\nBRONZE LAYER:")
        for source, stats in self.stats.get('bronze', {}).items():
            if stats.get('status') == 'success':
                print(f"  ✓ {source}: Success")
                for key, value in stats.items():
                    if key != 'status':
                        print(f"    - {key}: {value}")
            else:
                print(f"  ✗ {source}: Failed")
        
        # Gold layer summary
        if 'gold' in self.stats:
            print("\nGOLD LAYER:")
            if 'mutations' in self.stats['gold']:
                m = self.stats['gold']['mutations']
                if m.get('status') == 'success':
                    print(f"  ✓ Mutations: {m['total_mutations']} across {m['unique_genes']} genes")
            
            if 'therapeutics' in self.stats['gold']:
                t = self.stats['gold']['therapeutics']
                if t.get('status') == 'success':
                    print(f"  ✓ Therapeutics: {t['total_drugs']} drugs, {t['total_associations']} associations")
            
            if 'descriptions' in self.stats['gold']:
                d = self.stats['gold']['descriptions']
                if d.get('status') == 'success':
                    print(f"  ✓ Descriptions: {d['gene_descriptions']} genes, {d['drug_descriptions']} drugs")
                    print(f"    - Claude API cost: ${d['estimated_claude_cost']:.2f}")
        
        # Database summary
        if 'database' in self.stats and self.stats['database'].get('status') == 'success':
            print("\nDATABASE:")
            db = self.stats['database']
            print(f"  ✓ Loaded: {db['mutations_loaded']} mutations")
            print(f"  ✓ Loaded: {db['therapeutics_loaded']} therapeutics")
            print(f"  ✓ Loaded: {db['associations_loaded']} associations")
            print(f"  ✓ Total: {db['genes_count']} genes, {db['cancer_types_count']} cancer types")
        
        print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced OncoHotspot ETL Pipeline")
    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['cbioportal', 'civic', 'opentargets'],
        default=['cbioportal', 'civic', 'opentargets'],
        help='Data sources to use'
    )
    parser.add_argument(
        '--skip',
        nargs='+',
        choices=['bronze', 'silver', 'gold', 'database'],
        default=[],
        help='Pipeline layers to skip'
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = ExpandedPipeline()
    pipeline.run(sources=args.sources, skip_layers=args.skip)


if __name__ == "__main__":
    main()