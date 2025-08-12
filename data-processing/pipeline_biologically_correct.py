#!/usr/bin/env python3
"""
OncoHotspot ETL Pipeline - BIOLOGICALLY CORRECT VERSION
Only calculates frequencies when we have proper denominators
"""

import sys
import os
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from scipy import stats
import numpy as np

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Bronze layer extractors
from bronze.extractors import CBioPortalExtractor, CosmicExtractor
from bronze.extractors.dgidb_extractor import DGIdbExtractor

# Import Silver layer transformers
from silver.transformers import MutationStandardizer
from silver.transformers.therapeutic_standardizer import TherapeuticStandardizer

# Import Gold layer aggregators
from gold.aggregators import DatabaseLoader
from gold.aggregators.therapeutic_aggregator import TherapeuticAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BiologicallyCorrectAggregator:
    """Aggregator that only calculates frequencies when statistically valid"""
    
    def __init__(self):
        self.gold_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        # Known biological frequencies for validation
        self.known_frequencies = {
            ('KRAS', 'Pancreatic Cancer'): (0.30, 0.40),  # Expected 30-40%
            ('BRAF', 'Melanoma'): (0.40, 0.50),  # Expected 40-50%
            ('TP53', 'Lung Cancer'): (0.40, 0.60),  # Expected 40-60%
            ('EGFR', 'Lung Adenocarcinoma'): (0.10, 0.20),  # Expected 10-20%
        }
    
    def aggregate_with_validation(self, mutations_by_source: Dict[str, List[Dict]], 
                                 study_info_by_source: Dict[str, List[Dict]]) -> Dict:
        """
        Aggregate mutations with proper biological validation
        
        Args:
            mutations_by_source: Mutations grouped by data source
            study_info_by_source: Study information grouped by source
        """
        logger.info("Starting biologically correct aggregation")
        
        result = {
            'frequency_data': [],  # Only data with valid frequencies
            'occurrence_data': [],  # Data without denominators (COSMIC, CIViC)
            'validation_warnings': [],
            'statistics': {}
        }
        
        # Process cBioPortal data (has proper denominators)
        if 'cbioportal' in mutations_by_source:
            cbio_frequencies = self._process_cbioportal_frequencies(
                mutations_by_source['cbioportal'],
                study_info_by_source.get('cbioportal', [])
            )
            result['frequency_data'].extend(cbio_frequencies)
            
            # Validate against known biology
            warnings = self._validate_frequencies(cbio_frequencies)
            result['validation_warnings'].extend(warnings)
        
        # Process COSMIC data (no denominators - just catalog)
        if 'cosmic' in mutations_by_source:
            cosmic_catalog = self._process_cosmic_catalog(
                mutations_by_source['cosmic']
            )
            result['occurrence_data'].extend(cosmic_catalog)
        
        # Calculate statistics
        result['statistics'] = self._calculate_statistics(result)
        
        return result
    
    def _process_cbioportal_frequencies(self, mutations: List[Dict], 
                                       study_info: List[Dict]) -> List[Dict]:
        """Process cBioPortal data with proper frequency calculation"""
        
        # Build study sample count lookup
        study_samples = {}
        for study in study_info:
            study_id = study.get('studyId')
            # Use sequenced sample count as most relevant
            sample_count = (
                study.get('sequencedSampleCount') or
                study.get('allSampleCount') or
                0
            )
            if study_id and sample_count > 0:
                study_samples[study_id] = sample_count
                logger.info(f"Study {study_id}: {sample_count} sequenced samples")
        
        # Aggregate mutations by gene-cancer-position
        from collections import defaultdict
        aggregated = defaultdict(lambda: {
            'samples_with_mutation': set(),
            'total_samples': 0,
            'studies': set(),
            'protein_changes': set()
        })
        
        for mutation in mutations:
            study_id = mutation.get('studyId')
            if study_id not in study_samples:
                continue  # Skip if we don't have denominator
            
            key = (
                mutation.get('gene_symbol'),
                mutation.get('cancer_type'),
                mutation.get('protein_change')
            )
            
            agg = aggregated[key]
            agg['samples_with_mutation'].add(mutation.get('sample_id'))
            agg['studies'].add(study_id)
            if mutation.get('protein_change'):
                agg['protein_changes'].add(mutation['protein_change'])
        
        # Calculate frequencies with confidence intervals
        results = []
        for (gene, cancer, protein_change), data in aggregated.items():
            if not gene or not cancer:
                continue
            
            # Sum total samples from all studies involved
            total_samples = sum(
                study_samples[study_id] 
                for study_id in data['studies'] 
                if study_id in study_samples
            )
            
            if total_samples == 0:
                continue
            
            mutation_count = len(data['samples_with_mutation'])
            
            # Calculate frequency with Wilson confidence interval
            freq_data = self._calculate_frequency_with_ci(
                mutation_count, total_samples
            )
            
            results.append({
                'gene_symbol': gene,
                'cancer_type': cancer,
                'protein_change': protein_change,
                'mutation_count': mutation_count,
                'total_samples': total_samples,
                'frequency': freq_data['frequency'],
                'ci_95_low': freq_data['ci_low'],
                'ci_95_high': freq_data['ci_high'],
                'source': 'cbioportal',
                'study_count': len(data['studies']),
                'is_frequency_valid': True
            })
        
        return results
    
    def _calculate_frequency_with_ci(self, successes: int, trials: int) -> Dict:
        """Calculate frequency with 95% Wilson confidence interval"""
        if trials == 0:
            return {'frequency': 0, 'ci_low': 0, 'ci_high': 0}
        
        # Wilson score interval
        z = 1.96  # 95% confidence
        p_hat = successes / trials
        
        denominator = 1 + z**2 / trials
        center = (p_hat + z**2 / (2 * trials)) / denominator
        margin = z * np.sqrt(p_hat * (1 - p_hat) / trials + z**2 / (4 * trials**2)) / denominator
        
        return {
            'frequency': round(p_hat, 4),
            'ci_low': round(max(0, center - margin), 4),
            'ci_high': round(min(1, center + margin), 4)
        }
    
    def _validate_frequencies(self, frequencies: List[Dict]) -> List[str]:
        """Validate calculated frequencies against known biology"""
        warnings = []
        
        for freq_data in frequencies:
            gene = freq_data['gene_symbol']
            cancer = freq_data['cancer_type']
            frequency = freq_data['frequency']
            
            # Check against known frequencies
            key = (gene, cancer)
            if key in self.known_frequencies:
                expected_min, expected_max = self.known_frequencies[key]
                if not (expected_min <= frequency <= expected_max):
                    warning = (
                        f"WARNING: {gene} in {cancer} has frequency {frequency:.1%}, "
                        f"expected {expected_min:.0%}-{expected_max:.0%}"
                    )
                    warnings.append(warning)
                    logger.warning(warning)
            
            # General sanity checks
            if frequency > 0.95:
                warning = f"SUSPICIOUS: {gene} in {cancer} has >95% frequency"
                warnings.append(warning)
                logger.warning(warning)
            
            # Check confidence interval width
            ci_width = freq_data['ci_95_high'] - freq_data['ci_95_low']
            if ci_width > 0.3:  # CI wider than 30%
                warning = (
                    f"LOW CONFIDENCE: {gene} in {cancer} has wide CI "
                    f"({freq_data['ci_95_low']:.1%}-{freq_data['ci_95_high']:.1%})"
                )
                warnings.append(warning)
        
        return warnings
    
    def _process_cosmic_catalog(self, mutations: List[Dict]) -> List[Dict]:
        """Process COSMIC as a mutation catalog (no frequencies)"""
        from collections import defaultdict
        
        catalog = defaultdict(lambda: {
            'occurrence_count': 0,
            'protein_changes': set(),
            'histologies': set()
        })
        
        for mutation in mutations:
            gene = mutation.get('gene_name') or mutation.get('gene')
            if not gene:
                continue
            
            key = (gene, mutation.get('primary_site', 'Unknown'))
            cat = catalog[key]
            cat['occurrence_count'] += 1
            
            if mutation.get('protein_change'):
                cat['protein_changes'].add(mutation['protein_change'])
            if mutation.get('primary_histology'):
                cat['histologies'].add(mutation['primary_histology'])
        
        results = []
        for (gene, site), data in catalog.items():
            results.append({
                'gene_symbol': gene,
                'primary_site': site,
                'occurrence_count': data['occurrence_count'],
                'unique_variants': len(data['protein_changes']),
                'histology_count': len(data['histologies']),
                'source': 'cosmic',
                'is_frequency_valid': False,  # No denominator available
                'note': 'Occurrence count only - no frequency calculation possible'
            })
        
        return results
    
    def _calculate_statistics(self, result: Dict) -> Dict:
        """Calculate summary statistics"""
        freq_data = result['frequency_data']
        
        if not freq_data:
            return {'error': 'No frequency data available'}
        
        frequencies = [d['frequency'] for d in freq_data]
        
        return {
            'total_frequency_calculations': len(freq_data),
            'total_occurrence_records': len(result['occurrence_data']),
            'mean_frequency': round(np.mean(frequencies), 4),
            'median_frequency': round(np.median(frequencies), 4),
            'frequency_range': (round(min(frequencies), 4), round(max(frequencies), 4)),
            'validation_warning_count': len(result['validation_warnings']),
            'high_confidence_count': sum(
                1 for d in freq_data 
                if (d['ci_95_high'] - d['ci_95_low']) < 0.1
            )
        }
    
    def save_results(self, results: Dict) -> str:
        """Save aggregated results"""
        os.makedirs(self.gold_path, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"biologically_correct_{timestamp}.json"
        filepath = os.path.join(self.gold_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Saved biologically correct data to {filepath}")
        return filepath


class BiologicallyCorrectPipeline:
    """Pipeline that maintains biological and statistical validity"""
    
    def __init__(self):
        self.extractors = {
            'cbioportal': CBioPortalExtractor(),
            'cosmic': CosmicExtractor()
        }
        self.standardizer = MutationStandardizer()
        self.aggregator = BiologicallyCorrectAggregator()
        self.loader = DatabaseLoader()
    
    def run(self, sources: Optional[List[str]] = None):
        """Run the biologically correct pipeline"""
        if not sources:
            sources = ['cbioportal', 'cosmic']
        
        logger.info("="*60)
        logger.info("Starting Biologically Correct Pipeline")
        logger.info("="*60)
        
        # Extract data by source
        bronze_data = {}
        study_info = {}
        
        for source in sources:
            if source not in self.extractors:
                continue
            
            logger.info(f"Extracting from {source}...")
            data = self.extractors[source].extract()
            bronze_data[source] = data
            
            # Store study info separately
            if 'studies' in data:
                study_info[source] = data['studies']
        
        # Standardize mutations by source
        silver_data = {}
        for source, data in bronze_data.items():
            logger.info(f"Standardizing {source} data...")
            
            if source == 'cbioportal':
                mutations = self.standardizer.standardize_cbioportal(data)
            elif source == 'cosmic':
                mutations = self.standardizer.standardize_cosmic(data)
            else:
                continue
            
            silver_data[source] = mutations
        
        # Aggregate with biological validation
        logger.info("Aggregating with biological validation...")
        gold_data = self.aggregator.aggregate_with_validation(
            silver_data, study_info
        )
        
        # Save results
        filepath = self.aggregator.save_results(gold_data)
        
        # Print summary
        print("\n" + "="*60)
        print("BIOLOGICALLY CORRECT PIPELINE SUMMARY")
        print("="*60)
        
        stats = gold_data['statistics']
        print(f"Frequency calculations: {stats.get('total_frequency_calculations', 0)}")
        print(f"Occurrence records: {stats.get('total_occurrence_records', 0)}")
        print(f"Mean frequency: {stats.get('mean_frequency', 0):.1%}")
        print(f"High confidence: {stats.get('high_confidence_count', 0)}")
        
        if gold_data['validation_warnings']:
            print(f"\n⚠️  {len(gold_data['validation_warnings'])} validation warnings")
            for warning in gold_data['validation_warnings'][:5]:
                print(f"  - {warning}")
        
        print(f"\nResults saved to: {filepath}")
        
        return gold_data


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='OncoHotspot Pipeline - Biologically Correct Version'
    )
    parser.add_argument('--sources', nargs='+', 
                       choices=['cbioportal', 'cosmic'],
                       help='Data sources to use')
    
    args = parser.parse_args()
    
    pipeline = BiologicallyCorrectPipeline()
    results = pipeline.run(args.sources)
    
    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main()