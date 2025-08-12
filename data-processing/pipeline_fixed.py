#!/usr/bin/env python3
"""
OncoHotspot ETL Pipeline - FIXED VERSION
Properly handles total sample counts for accurate frequency calculations
"""

import sys
import os
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Bronze layer extractors
from bronze.extractors import CBioPortalExtractor, CosmicExtractor
from bronze.extractors.dgidb_extractor import DGIdbExtractor

# Import Silver layer transformers
from silver.transformers import MutationStandardizer
from silver.transformers.therapeutic_standardizer import TherapeuticStandardizer

# Import Gold layer aggregators - USE FIXED VERSION
from gold.aggregators.mutation_aggregator_fixed import MutationAggregator
from gold.aggregators import DatabaseLoader
from gold.aggregators.therapeutic_aggregator import TherapeuticAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OncoHotspotPipeline:
    """Main ETL pipeline orchestrator - FIXED to handle sample counts properly"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the pipeline
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        
        # Initialize components
        self.extractors = {
            'cbioportal': CBioPortalExtractor(config_path),
            'cosmic': CosmicExtractor(config_path),
            'dgidb': DGIdbExtractor(config_path)
        }
        
        self.mutation_standardizer = MutationStandardizer()
        self.therapeutic_standardizer = TherapeuticStandardizer()
        self.mutation_aggregator = MutationAggregator()  # Fixed version
        self.therapeutic_aggregator = TherapeuticAggregator()
        self.loader = DatabaseLoader()
        
        self.pipeline_start = datetime.utcnow()
        
        # Store study information for sample counts
        self.study_info = []
        
    def run_full_pipeline(self, sources: Optional[List[str]] = None) -> Dict:
        """
        Run the complete ETL pipeline
        
        Args:
            sources: List of sources to extract from (default: all)
            
        Returns:
            Pipeline execution statistics
        """
        logger.info("=" * 60)
        logger.info("Starting OncoHotspot ETL Pipeline (FIXED VERSION)")
        logger.info("=" * 60)
        
        if not sources:
            sources = list(self.extractors.keys())
        
        stats = {
            'pipeline_start': self.pipeline_start.isoformat(),
            'sources': sources,
            'bronze': {},
            'silver': {},
            'gold': {},
            'database': {}
        }
        
        try:
            # BRONZE LAYER: Extract raw data INCLUDING STUDY INFO
            logger.info("\n🥉 BRONZE LAYER - Extracting raw data...")
            bronze_data = self._extract_bronze(sources, stats)
            
            # SILVER LAYER: Standardize data
            logger.info("\n🥈 SILVER LAYER - Standardizing data...")
            silver_data = self._process_silver(bronze_data, stats)
            
            # THERAPEUTIC DATA: Extract if not already in bronze_data
            if 'dgidb' not in bronze_data and 'dgidb' not in sources:
                logger.info("\n💊 EXTRACTING - Therapeutic data...")
                therapeutic_bronze = self._extract_therapeutics(stats)
                bronze_data.update(therapeutic_bronze)
            
            # SILVER LAYER - Therapeutics: Standardize therapeutic data
            logger.info("\n🥈 SILVER LAYER - Standardizing therapeutics...")
            silver_therapeutics = self._process_silver_therapeutics(bronze_data, stats)
            
            # GOLD LAYER: Aggregate data WITH STUDY INFO
            logger.info("\n🥇 GOLD LAYER - Aggregating data...")
            gold_data = self._process_gold(silver_data, stats)
            
            # GOLD LAYER - Therapeutics: Associate mutations with therapeutics
            logger.info("\n🥇 GOLD LAYER - Associating mutations with therapeutics...")
            therapeutic_associations = self._process_therapeutic_associations(
                gold_data, silver_therapeutics, stats
            )
            
            # LOAD: Insert into database
            logger.info("\n💾 LOADING - Inserting into database...")
            self._load_to_database(gold_data, stats)
            self._load_therapeutics_to_database(therapeutic_associations, stats)
            
            # Calculate pipeline duration
            pipeline_end = datetime.utcnow()
            duration = (pipeline_end - self.pipeline_start).total_seconds()
            stats['pipeline_end'] = pipeline_end.isoformat()
            stats['duration_seconds'] = duration
            stats['status'] = 'success'
            
            # Save pipeline stats
            self._save_stats(stats)
            
            logger.info("\n" + "=" * 60)
            logger.info(f"✅ Pipeline completed successfully in {duration:.2f} seconds")
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            stats['status'] = 'failed'
            stats['error'] = str(e)
            self._save_stats(stats)
            raise
    
    def _extract_bronze(self, sources: List[str], stats: Dict) -> Dict[str, Dict]:
        """Extract data from sources (Bronze layer) - FIXED to capture study info"""
        bronze_data = {}
        
        for source in sources:
            if source in self.extractors:
                logger.info(f"Extracting from {source}...")
                try:
                    extractor = self.extractors[source]
                    data = extractor.extract()
                    bronze_data[source] = data
                    
                    # CRITICAL FIX: Extract and store study information
                    if 'studies' in data and data['studies']:
                        logger.info(f"Found {len(data['studies'])} studies with sample count information")
                        self.study_info.extend(data['studies'])
                        
                        # Log sample counts for verification
                        for study in data['studies']:
                            study_id = study.get('studyId', study.get('name', 'Unknown'))
                            sample_count = (
                                study.get('numberOfSamples') or 
                                study.get('allSampleCount') or
                                study.get('sequencedSampleCount') or
                                'Unknown'
                            )
                            logger.info(f"  Study {study_id}: {sample_count} samples")
                    
                    # Update stats
                    stats['bronze'][source] = {
                        'status': 'success',
                        'record_count': len(data.get('mutations', [])),
                        'study_count': len(data.get('studies', []))
                    }
                    
                    logger.info(f"✓ Extracted {stats['bronze'][source]['record_count']} mutations from {source}")
                    
                except Exception as e:
                    logger.error(f"Failed to extract from {source}: {e}")
                    stats['bronze'][source] = {'status': 'failed', 'error': str(e)}
            else:
                logger.warning(f"No extractor available for {source}")
        
        return bronze_data
    
    def _process_silver(self, bronze_data: Dict, stats: Dict) -> List[Dict]:
        """Standardize data (Silver layer)"""
        all_silver_mutations = []
        
        for source, data in bronze_data.items():
            # Skip therapeutic sources in mutation processing
            if source in ['dgidb']:
                continue
                
            logger.info(f"Standardizing {source} data...")
            
            try:
                if source == 'cbioportal':
                    mutations = self.mutation_standardizer.standardize_cbioportal(data)
                elif source == 'cosmic':
                    mutations = self.mutation_standardizer.standardize_cosmic(data)
                else:
                    logger.warning(f"No mutation standardizer for {source}")
                    continue
                
                all_silver_mutations.extend(mutations)
                
                # Save silver data
                metadata = self.mutation_standardizer.save_silver(mutations, source)
                
                stats['silver'][source] = {
                    'status': 'success',
                    'input_count': len(data.get('mutations', [])),
                    'output_count': len(mutations),
                    'file': metadata['file']
                }
                
                logger.info(f"✓ Standardized {len(mutations)} mutations from {source}")
                
            except Exception as e:
                logger.error(f"Failed to standardize {source}: {e}")
                stats['silver'][source] = {'status': 'failed', 'error': str(e)}
        
        return all_silver_mutations
    
    def _process_gold(self, silver_mutations: List[Dict], stats: Dict) -> Dict:
        """Aggregate data (Gold layer) - FIXED to pass study info"""
        logger.info("Aggregating mutations for heatmap...")
        
        try:
            # CRITICAL FIX: Pass study info to aggregator
            logger.info(f"Passing {len(self.study_info)} study records to aggregator")
            gold_data = self.mutation_aggregator.aggregate(silver_mutations, self.study_info)
            
            # Get the heatmap data specifically
            heatmap_data = gold_data.get('heatmap', {})
            
            # Save gold data
            metadata = self.mutation_aggregator.save_gold_data(heatmap_data, 'heatmap')
            
            stats['gold'] = {
                'status': 'success',
                'input_count': len(silver_mutations),
                'output_count': len(heatmap_data.get('mutations', [])),
                'unique_genes': len(heatmap_data.get('genes', [])),
                'unique_cancer_types': len(heatmap_data.get('cancer_types', [])),
                'study_count': len(self.study_info),
                'file': metadata.get('filepath', 'N/A')
            }
            
            logger.info(f"✓ Aggregated {stats['gold']['output_count']} unique mutation-cancer combinations")
            logger.info(f"✓ Using sample counts from {stats['gold']['study_count']} studies")
            
            # Log some example frequencies to verify the fix
            if heatmap_data.get('mutations'):
                logger.info("\nSample frequency calculations (first 5):")
                for mut in heatmap_data['mutations'][:5]:
                    logger.info(f"  {mut.get('gene_symbol')} in {mut.get('cancer_type')}: "
                              f"{mut.get('mutation_count')}/{mut.get('total_samples')} = "
                              f"{mut.get('frequency', 0):.3f}")
            
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Failed to aggregate data: {e}")
            stats['gold'] = {'status': 'failed', 'error': str(e)}
            raise
    
    def _extract_therapeutics(self, stats: Dict) -> Dict[str, Dict]:
        """Extract therapeutic data"""
        bronze_data = {}
        
        if 'dgidb' in self.extractors:
            logger.info("Extracting from DGIdb...")
            try:
                extractor = self.extractors['dgidb']
                data = extractor.extract()
                bronze_data['dgidb'] = data
                
                stats['bronze']['dgidb'] = {
                    'status': 'success',
                    'record_count': len(data.get('interactions', []))
                }
                
                logger.info(f"✓ Extracted {stats['bronze']['dgidb']['record_count']} drug-gene interactions")
                
            except Exception as e:
                logger.error(f"Failed to extract from DGIdb: {e}")
                stats['bronze']['dgidb'] = {'status': 'failed', 'error': str(e)}
        
        return bronze_data
    
    def _process_silver_therapeutics(self, bronze_data: Dict, stats: Dict) -> List[Dict]:
        """Standardize therapeutic data"""
        all_silver_therapeutics = []
        
        if 'dgidb' in bronze_data:
            logger.info("Standardizing DGIdb therapeutic data...")
            
            try:
                therapeutics = self.therapeutic_standardizer.standardize_dgidb(bronze_data['dgidb'])
                all_silver_therapeutics.extend(therapeutics)
                
                # Save silver therapeutics
                metadata = self.therapeutic_standardizer.save_silver_therapeutics(therapeutics, 'dgidb')
                
                stats['silver']['dgidb'] = {
                    'status': 'success',
                    'input_count': len(bronze_data['dgidb'].get('interactions', [])),
                    'output_count': len(therapeutics),
                    'file': metadata['file']
                }
                
                logger.info(f"✓ Standardized {len(therapeutics)} therapeutic associations")
                
            except Exception as e:
                logger.error(f"Failed to standardize DGIdb: {e}")
                stats['silver']['dgidb'] = {'status': 'failed', 'error': str(e)}
        
        return all_silver_therapeutics
    
    def _process_therapeutic_associations(self, gold_mutations: Dict, 
                                         silver_therapeutics: List[Dict], 
                                         stats: Dict) -> List[Dict]:
        """Associate mutations with therapeutics"""
        logger.info("Associating mutations with therapeutics...")
        
        try:
            associations = self.therapeutic_aggregator.associate(
                gold_mutations.get('mutations', []),
                silver_therapeutics
            )
            
            # Save associations
            metadata = self.therapeutic_aggregator.save_associations(associations)
            
            stats['gold']['therapeutics'] = {
                'status': 'success',
                'mutation_count': len(gold_mutations.get('mutations', [])),
                'therapeutic_count': len(silver_therapeutics),
                'association_count': len(associations),
                'file': metadata['file']
            }
            
            logger.info(f"✓ Created {len(associations)} mutation-therapeutic associations")
            
            return associations
            
        except Exception as e:
            logger.error(f"Failed to associate therapeutics: {e}")
            stats['gold']['therapeutics'] = {'status': 'failed', 'error': str(e)}
            return []
    
    def _load_to_database(self, gold_data: Dict, stats: Dict):
        """Load aggregated data into database"""
        logger.info("Loading mutations into database...")
        
        try:
            load_stats = self.loader.load_mutations(gold_data.get('mutations', []))
            
            stats['database']['mutations'] = load_stats
            
            logger.info(f"✓ Loaded {load_stats['inserted']} new and updated {load_stats['updated']} existing mutations")
            
        except Exception as e:
            logger.error(f"Failed to load mutations: {e}")
            stats['database']['mutations'] = {'status': 'failed', 'error': str(e)}
    
    def _load_therapeutics_to_database(self, associations: List[Dict], stats: Dict):
        """Load therapeutic associations into database"""
        if not associations:
            logger.info("No therapeutic associations to load")
            return
        
        logger.info("Loading therapeutic associations into database...")
        
        try:
            load_stats = self.loader.load_therapeutics(associations)
            
            stats['database']['therapeutics'] = load_stats
            
            logger.info(f"✓ Loaded {load_stats.get('inserted', 0)} therapeutic associations")
            
        except Exception as e:
            logger.error(f"Failed to load therapeutics: {e}")
            stats['database']['therapeutics'] = {'status': 'failed', 'error': str(e)}
    
    def _save_stats(self, stats: Dict):
        """Save pipeline execution statistics"""
        stats_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logs'
        )
        os.makedirs(stats_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        stats_file = os.path.join(stats_dir, f'pipeline_stats_{timestamp}.json')
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        logger.info(f"Pipeline statistics saved to {stats_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='OncoHotspot ETL Pipeline')
    parser.add_argument('--sources', nargs='+', 
                       choices=['cbioportal', 'cosmic', 'dgidb'],
                       help='Sources to extract from')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--skip-bronze', action='store_true',
                       help='Skip Bronze layer (use existing raw data)')
    parser.add_argument('--skip-silver', action='store_true', 
                       help='Skip Silver layer (use existing standardized data)')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode with limited data')
    
    args = parser.parse_args()
    
    # Initialize and run pipeline
    pipeline = OncoHotspotPipeline(config_path=args.config)
    
    # Run full pipeline
    stats = pipeline.run_full_pipeline(sources=args.sources)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    print(f"Status: {stats['status']}")
    print(f"Duration: {stats.get('duration_seconds', 0):.2f} seconds")
    
    if 'gold' in stats:
        print(f"Mutations processed: {stats['gold'].get('output_count', 0)}")
        print(f"Unique genes: {stats['gold'].get('unique_genes', 0)}")
        print(f"Unique cancer types: {stats['gold'].get('unique_cancer_types', 0)}")
        print(f"Studies with sample counts: {stats['gold'].get('study_count', 0)}")
    
    if 'database' in stats and 'mutations' in stats['database']:
        db_stats = stats['database']['mutations']
        print(f"Database: {db_stats.get('inserted', 0)} inserted, {db_stats.get('updated', 0)} updated")
    
    return 0 if stats['status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())