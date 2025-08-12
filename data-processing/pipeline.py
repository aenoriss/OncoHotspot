#!/usr/bin/env python3
"""
OncoHotspot ETL Pipeline - Medallion Architecture
Fetches cancer mutation data from open sources and loads into database
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

# Import Gold layer aggregators
from gold.aggregators import MutationAggregator, DatabaseLoader
from gold.aggregators.therapeutic_aggregator import TherapeuticAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OncoHotspotPipeline:
    """Main ETL pipeline orchestrator"""
    
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
        self.mutation_aggregator = MutationAggregator()
        self.therapeutic_aggregator = TherapeuticAggregator()
        self.loader = DatabaseLoader()
        
        self.pipeline_start = datetime.utcnow()
        
    def run_full_pipeline(self, sources: Optional[List[str]] = None) -> Dict:
        """
        Run the complete ETL pipeline
        
        Args:
            sources: List of sources to extract from (default: all)
            
        Returns:
            Pipeline execution statistics
        """
        logger.info("=" * 60)
        logger.info("Starting OncoHotspot ETL Pipeline")
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
            # BRONZE LAYER: Extract raw data
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
            
            # GOLD LAYER: Aggregate data
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
            self._save_pipeline_stats(stats)
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Pipeline completed successfully!")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Mutations loaded: {stats['database'].get('inserted', 0) + stats['database'].get('updated', 0)}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            stats['status'] = 'failed'
            stats['error'] = str(e)
            raise
        
        return stats
    
    def _extract_bronze(self, sources: List[str], stats: Dict) -> Dict[str, Dict]:
        """Extract data from sources (Bronze layer)"""
        bronze_data = {}
        
        for source in sources:
            if source in self.extractors:
                logger.info(f"Extracting from {source}...")
                try:
                    extractor = self.extractors[source]
                    data = extractor.extract()
                    bronze_data[source] = data
                    
                    # Update stats
                    stats['bronze'][source] = {
                        'status': 'success',
                        'record_count': len(data.get('mutations', []))
                    }
                    
                    logger.info(f"✓ Extracted {stats['bronze'][source]['record_count']} mutations from {source}")
                    
                except Exception as e:
                    logger.error(f"Failed to extract from {source}: {e}")
                    stats['bronze'][source] = {
                        'status': 'failed',
                        'error': str(e)
                    }
        
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
                metadata = self.mutation_standardizer.save_silver_data(mutations, source)
                
                stats['silver'][source] = {
                    'status': 'success',
                    'input_count': len(data.get('mutations', [])),
                    'output_count': len(mutations),
                    'file': metadata['file']
                }
                
                logger.info(f"✓ Standardized {len(mutations)} mutations from {source}")
                
            except Exception as e:
                logger.error(f"Failed to standardize {source}: {e}")
                stats['silver'][source] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        logger.info(f"Total standardized mutations: {len(all_silver_mutations)}")
        return all_silver_mutations
    
    def _extract_therapeutics(self, stats: Dict) -> Dict:
        """Extract therapeutic data"""
        therapeutic_bronze = {}
        
        try:
            logger.info("Extracting therapeutic data from DGIdb...")
            extractor = self.extractors['dgidb']
            data = extractor.extract()
            therapeutic_bronze['dgidb'] = data
            
            stats['bronze']['dgidb'] = {
                'status': 'success',
                'record_count': len(data.get('interactions', []))
            }
            
            logger.info(f"✓ Extracted {stats['bronze']['dgidb']['record_count']} drug interactions")
            
        except Exception as e:
            logger.error(f"Failed to extract therapeutics: {e}")
            stats['bronze']['dgidb'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return therapeutic_bronze
    
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
                
                logger.info(f"✓ Standardized {len(therapeutics)} therapeutics")
                
            except Exception as e:
                logger.error(f"Failed to standardize therapeutics: {e}")
                stats['silver']['dgidb'] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return all_silver_therapeutics
    
    def _process_therapeutic_associations(self, gold_data: Dict, silver_therapeutics: List[Dict], 
                                         stats: Dict) -> Dict:
        """Associate mutations with therapeutics"""
        try:
            # Get mutations from gold data
            mutations = gold_data.get('mutations', [])
            
            # Associate with therapeutics
            associations = self.therapeutic_aggregator.associate_mutations_with_therapeutics(
                mutations, silver_therapeutics
            )
            
            # Save associations
            metadata = self.therapeutic_aggregator.save_associations(associations)
            
            stats['gold']['therapeutics'] = {
                'status': 'success',
                'actionable_mutations': len(associations.get('mutation_therapeutics', [])),
                'genes_with_therapeutics': len(associations.get('gene_therapeutics', [])),
                'unique_drugs': associations.get('summary', {}).get('unique_drugs', 0),
                'file': metadata['file']
            }
            
            logger.info(f"✓ Associated {stats['gold']['therapeutics']['actionable_mutations']} mutations with therapeutics")
            
            return associations
            
        except Exception as e:
            logger.error(f"Failed to process therapeutic associations: {e}")
            stats['gold']['therapeutics'] = {
                'status': 'failed',
                'error': str(e)
            }
            return {}
    
    def _load_therapeutics_to_database(self, associations: Dict, stats: Dict):
        """Load therapeutic associations to database"""
        if not associations:
            return
            
        logger.info("Loading therapeutic associations to database...")
        
        # TODO: Implement database loading for therapeutics
        # For now, the associations are saved as JSON in the Gold layer
        
        stats['database']['therapeutics'] = {
            'status': 'success',
            'associations_loaded': len(associations.get('mutation_therapeutics', []))
        }
        
        logger.info(f"✓ Therapeutic associations saved (database loading pending)")
    
    def _process_gold(self, silver_mutations: List[Dict], stats: Dict) -> Dict:
        """Aggregate data (Gold layer)"""
        logger.info("Aggregating mutations for heatmap...")
        
        try:
            # Aggregate for heatmap
            gold_data = self.mutation_aggregator.aggregate_for_heatmap(silver_mutations)
            
            # Save gold data
            metadata = self.mutation_aggregator.save_gold_data(gold_data, 'heatmap')
            
            stats['gold'] = {
                'status': 'success',
                'input_count': len(silver_mutations),
                'output_count': len(gold_data.get('mutations', [])),
                'unique_genes': len(gold_data.get('genes', [])),
                'unique_cancer_types': len(gold_data.get('cancer_types', [])),
                'file': metadata['file']
            }
            
            logger.info(f"✓ Aggregated {stats['gold']['output_count']} unique mutation-cancer combinations")
            logger.info(f"  - Genes: {stats['gold']['unique_genes']}")
            logger.info(f"  - Cancer types: {stats['gold']['unique_cancer_types']}")
            
        except Exception as e:
            logger.error(f"Failed to aggregate data: {e}")
            stats['gold'] = {
                'status': 'failed',
                'error': str(e)
            }
            raise
        
        return gold_data
    
    def _load_to_database(self, gold_data: Dict, stats: Dict):
        """Load data into database"""
        logger.info("Loading data into database...")
        
        try:
            # Load mutations
            db_stats = self.loader.load_mutations(gold_data.get('mutations', []))
            
            stats['database'] = db_stats
            stats['database']['status'] = 'success'
            
            # Get final database statistics
            final_stats = self.loader.get_statistics()
            stats['database']['final_counts'] = final_stats
            
            logger.info(f"✓ Database loading complete:")
            logger.info(f"  - Inserted: {db_stats['inserted']}")
            logger.info(f"  - Updated: {db_stats['updated']}")
            logger.info(f"  - Failed: {db_stats['failed']}")
            logger.info(f"  - Total mutations in DB: {final_stats.get('mutations_count', 0)}")
            
        except Exception as e:
            logger.error(f"Failed to load to database: {e}")
            stats['database'] = {
                'status': 'failed',
                'error': str(e)
            }
            raise
    
    def _save_pipeline_stats(self, stats: Dict):
        """Save pipeline execution statistics"""
        stats_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logs'
        )
        os.makedirs(stats_dir, exist_ok=True)
        
        filename = f"pipeline_run_{self.pipeline_start.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(stats_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        logger.info(f"Pipeline statistics saved to: {filepath}")
    
    def run_incremental(self, source: str = 'cbioportal') -> Dict:
        """
        Run incremental update from a specific source
        
        Args:
            source: Data source to update from
            
        Returns:
            Update statistics
        """
        logger.info(f"Running incremental update from {source}")
        return self.run_full_pipeline([source])
    
    def clear_database(self):
        """Clear existing mutation data from database"""
        logger.warning("Clearing existing mutation data...")
        count = self.loader.clear_existing_data('mutations')
        logger.info(f"Cleared {count} mutation records")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='OncoHotspot ETL Pipeline - Fetch and process cancer mutation data'
    )
    
    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['cbioportal', 'cosmic'],
        help='Data sources to extract from (default: all)'
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data before loading'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize pipeline
    pipeline = OncoHotspotPipeline(args.config)
    
    # Clear database if requested
    if args.clear:
        pipeline.clear_database()
    
    # Run pipeline
    try:
        stats = pipeline.run_full_pipeline(args.sources)
        
        # Print summary
        print("\n📊 Pipeline Summary:")
        print(f"  Status: {stats['status']}")
        print(f"  Duration: {stats.get('duration_seconds', 0):.2f} seconds")
        print(f"  Sources processed: {', '.join(stats['sources'])}")
        
        if stats.get('database'):
            print(f"  Mutations loaded: {stats['database'].get('inserted', 0) + stats['database'].get('updated', 0)}")
        
        return 0 if stats['status'] == 'success' else 1
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())