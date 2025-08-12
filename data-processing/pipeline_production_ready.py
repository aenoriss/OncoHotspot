#!/usr/bin/env python3
"""
OncoHotspot ETL Pipeline - PRODUCTION READY VERSION
Scientifically valid frequency calculations with proper data segregation
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bronze.extractors import CBioPortalExtractor, CosmicExtractor
from bronze.extractors.civic_extractor import CIViCExtractor
from silver.transformers import MutationStandardizer
from gold.aggregators import DatabaseLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataQuality(Enum):
    """Data quality tiers for different types of mutation data"""
    POPULATION_FREQUENCY = "population_frequency"  # Has denominator (cBioPortal)
    OCCURRENCE_COUNT = "occurrence_count"  # No denominator (COSMIC)
    CLINICAL_ANNOTATION = "clinical_annotation"  # Actionability (CIViC)


@dataclass
class MutationFrequency:
    """Properly structured mutation frequency data"""
    gene_symbol: str
    cancer_type: str
    protein_change: str
    samples_with_mutation: int
    total_samples_tested: int
    frequency: float
    ci_95_low: float
    ci_95_high: float
    source: str
    study_ids: List[str]
    quality_tier: DataQuality
    
    def __post_init__(self):
        # Validate data integrity
        assert self.samples_with_mutation <= self.total_samples_tested, \
            f"Invalid: {self.samples_with_mutation} mutations in {self.total_samples_tested} samples"
        assert 0 <= self.frequency <= 1, f"Invalid frequency: {self.frequency}"
        assert self.ci_95_low <= self.frequency <= self.ci_95_high, \
            "Frequency must be within confidence interval"


class ProductionAggregator:
    """Production-ready aggregator with proper data handling"""
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'gold', 'data')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Biological validation thresholds
        self.known_hotspots = {
            ('KRAS', 'G12D'): {'min_freq': 0.05, 'cancer_types': ['Pancreatic', 'Colorectal']},
            ('BRAF', 'V600E'): {'min_freq': 0.30, 'cancer_types': ['Melanoma', 'Thyroid']},
            ('EGFR', 'L858R'): {'min_freq': 0.10, 'cancer_types': ['Lung Adenocarcinoma']},
            ('TP53', '*'): {'min_freq': 0.20, 'cancer_types': ['*']},  # Common across cancers
        }
    
    def process_cbioportal_with_frequencies(self, mutations: List[Dict], studies: List[Dict]) -> List[MutationFrequency]:
        """
        Process cBioPortal data with proper frequency calculation
        Only this source has the denominators needed for frequency
        """
        # Build study lookup with sample counts
        study_denominators = {}
        for study in studies:
            study_id = study.get('studyId')
            # Use sequenced sample count as most accurate denominator
            sample_count = study.get('sequencedSampleCount', 0) or study.get('allSampleCount', 0)
            
            if study_id and sample_count > 0:
                study_denominators[study_id] = {
                    'total_samples': sample_count,
                    'cancer_type': study.get('cancerType', {}).get('name', 'Unknown')
                }
                logger.info(f"Study {study_id}: {sample_count} samples for frequency calculation")
        
        # Aggregate mutations by gene-cancer-variant
        from collections import defaultdict
        aggregated = defaultdict(lambda: {
            'samples': set(),
            'studies': set(),
            'study_denominators': {}
        })
        
        for mut in mutations:
            study_id = mut.get('studyId')
            if study_id not in study_denominators:
                logger.warning(f"Skipping mutation from study {study_id} - no denominator available")
                continue
            
            key = (
                mut.get('gene', {}).get('hugoGeneSymbol', 'Unknown'),
                study_denominators[study_id]['cancer_type'],
                mut.get('proteinChange', 'Unknown')
            )
            
            agg = aggregated[key]
            agg['samples'].add(f"{study_id}:{mut.get('sampleId')}")
            agg['studies'].add(study_id)
            agg['study_denominators'][study_id] = study_denominators[study_id]['total_samples']
        
        # Calculate frequencies with proper statistics
        results = []
        for (gene, cancer, protein), data in aggregated.items():
            # Sum denominators from all contributing studies
            total_samples = sum(data['study_denominators'].values())
            mutation_count = len(data['samples'])
            
            if total_samples == 0:
                continue
            
            # Calculate Wilson confidence interval
            freq, ci_low, ci_high = self._calculate_wilson_ci(mutation_count, total_samples)
            
            try:
                mutation_freq = MutationFrequency(
                    gene_symbol=gene,
                    cancer_type=cancer,
                    protein_change=protein,
                    samples_with_mutation=mutation_count,
                    total_samples_tested=total_samples,
                    frequency=freq,
                    ci_95_low=ci_low,
                    ci_95_high=ci_high,
                    source='cbioportal',
                    study_ids=list(data['studies']),
                    quality_tier=DataQuality.POPULATION_FREQUENCY
                )
                
                # Validate against known biology
                if self._validate_frequency(mutation_freq):
                    results.append(mutation_freq)
                else:
                    logger.warning(f"Rejected biologically implausible: {gene} {protein} in {cancer} = {freq:.1%}")
                    
            except AssertionError as e:
                logger.error(f"Data integrity error: {e}")
                continue
        
        return results
    
    def process_cosmic_as_catalog(self, mutations: List[Dict]) -> List[Dict]:
        """
        Process COSMIC as a mutation catalog ONLY
        No frequency calculations - we don't have denominators
        """
        from collections import defaultdict
        
        catalog = defaultdict(lambda: {
            'occurrences': 0,
            'unique_samples': set(),
            'protein_variants': set(),
            'tissues': set()
        })
        
        for mut in mutations:
            gene = mut.get('gene_name', 'Unknown')
            protein = mut.get('protein_change', '')
            
            if not gene or gene == 'Unknown':
                continue
            
            key = gene
            cat = catalog[key]
            cat['occurrences'] += 1
            
            if mut.get('sample_id'):
                cat['unique_samples'].add(mut['sample_id'])
            if protein:
                cat['protein_variants'].add(protein)
            if mut.get('primary_site'):
                cat['tissues'].add(mut['primary_site'])
        
        results = []
        for gene, data in catalog.items():
            results.append({
                'gene_symbol': gene,
                'total_occurrences': data['occurrences'],
                'unique_samples': len(data['unique_samples']),
                'variant_count': len(data['protein_variants']),
                'tissue_count': len(data['tissues']),
                'top_variants': list(data['protein_variants'])[:5],
                'source': 'cosmic',
                'quality_tier': DataQuality.OCCURRENCE_COUNT.value,
                'note': 'Catalog data only - no frequency calculation possible without denominators'
            })
        
        return results
    
    def process_civic_annotations(self, civic_data: Dict) -> List[Dict]:
        """
        Process CIViC for clinical annotations ONLY
        These are curated therapeutic associations, not frequencies
        """
        annotations = []
        
        for variant in civic_data.get('variants', []):
            gene = variant.get('gene', {}).get('name', 'Unknown')
            
            # Extract evidence items
            evidence_items = variant.get('evidence_items', [])
            therapies = set()
            evidence_levels = set()
            
            for evidence in evidence_items:
                if evidence.get('therapies'):
                    for therapy in evidence['therapies']:
                        therapies.add(therapy.get('name', 'Unknown'))
                if evidence.get('evidence_level'):
                    evidence_levels.add(evidence['evidence_level'])
            
            if therapies:  # Only include if has therapeutic relevance
                annotations.append({
                    'gene_symbol': gene,
                    'variant_name': variant.get('name', 'Unknown'),
                    'therapies': list(therapies),
                    'evidence_levels': list(evidence_levels),
                    'clinical_significance': variant.get('clinical_significance', 'Unknown'),
                    'source': 'civic',
                    'quality_tier': DataQuality.CLINICAL_ANNOTATION.value,
                    'note': 'Clinical annotation - not a frequency measurement'
                })
        
        return annotations
    
    def _calculate_wilson_ci(self, successes: int, trials: int, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculate Wilson score confidence interval for binomial proportion
        More accurate than normal approximation for small samples
        """
        if trials == 0:
            return 0.0, 0.0, 0.0
        
        p_hat = successes / trials
        z = stats.norm.ppf((1 + confidence) / 2)
        
        denominator = 1 + z**2 / trials
        center = (p_hat + z**2 / (2 * trials)) / denominator
        
        margin = z * np.sqrt(p_hat * (1 - p_hat) / trials + z**2 / (4 * trials**2)) / denominator
        
        return (
            round(p_hat, 4),
            round(max(0, center - margin), 4),
            round(min(1, center + margin), 4)
        )
    
    def _validate_frequency(self, mutation: MutationFrequency) -> bool:
        """
        Validate frequency against known biological constraints
        Reject obviously wrong data
        """
        # Check for impossible frequencies
        if mutation.frequency > 0.95:
            logger.warning(f"Suspiciously high frequency: {mutation.gene_symbol} = {mutation.frequency:.1%}")
            return False  # Likely data error
        
        # Check against known hotspots
        for (gene, variant), constraints in self.known_hotspots.items():
            if mutation.gene_symbol == gene:
                if variant == '*' or variant in mutation.protein_change:
                    if mutation.frequency < constraints['min_freq'] * 0.1:  # 10x lower than expected
                        logger.warning(f"Frequency too low for known hotspot: {gene} {variant}")
                        return False
        
        # Check confidence interval width
        ci_width = mutation.ci_95_high - mutation.ci_95_low
        if ci_width > 0.5:  # CI spans more than 50%
            logger.warning(f"Confidence interval too wide: {mutation.gene_symbol} CI width = {ci_width:.1%}")
            return False  # Not enough data for reliable estimate
        
        return True
    
    def create_final_database_records(self, frequencies: List[MutationFrequency], 
                                     catalog: List[Dict], 
                                     annotations: List[Dict]) -> List[Dict]:
        """
        Create final database records with proper data segregation
        """
        records = []
        
        # Add frequency data (highest quality)
        for freq in frequencies:
            records.append({
                'gene_symbol': freq.gene_symbol,
                'cancer_type': freq.cancer_type,
                'protein_change': freq.protein_change,
                'mutation_count': freq.samples_with_mutation,
                'total_samples': freq.total_samples_tested,
                'frequency': freq.frequency,
                'frequency_ci_low': freq.ci_95_low,
                'frequency_ci_high': freq.ci_95_high,
                'significance_score': freq.frequency,  # Use frequency as significance
                'data_quality': freq.quality_tier.value,
                'source': freq.source,
                'has_denominator': True,
                'is_validated': True
            })
        
        # Add catalog data (no frequencies)
        for cat in catalog:
            records.append({
                'gene_symbol': cat['gene_symbol'],
                'cancer_type': 'Multiple',  # COSMIC covers multiple cancer types
                'protein_change': ', '.join(cat['top_variants']) if cat['top_variants'] else 'Various',
                'mutation_count': cat['total_occurrences'],
                'total_samples': None,  # Unknown denominator
                'frequency': None,  # Cannot calculate
                'significance_score': min(cat['total_occurrences'] / 1000, 1.0),  # Rough estimate
                'data_quality': cat['quality_tier'],
                'source': cat['source'],
                'has_denominator': False,
                'is_validated': False
            })
        
        return records


class ProductionPipeline:
    """Production-ready pipeline with proper data handling"""
    
    def __init__(self):
        self.cbio_extractor = CBioPortalExtractor()
        self.cosmic_extractor = CosmicExtractor()
        self.civic_extractor = CIViCExtractor()
        self.standardizer = MutationStandardizer()
        self.aggregator = ProductionAggregator()
        self.loader = DatabaseLoader()
    
    def run(self):
        """Run the production pipeline"""
        logger.info("="*70)
        logger.info("PRODUCTION PIPELINE - Scientifically Valid Implementation")
        logger.info("="*70)
        
        results = {
            'frequency_data': [],
            'catalog_data': [],
            'annotation_data': [],
            'database_records': [],
            'validation_report': {}
        }
        
        # 1. Extract cBioPortal data (has denominators for frequencies)
        logger.info("\n📊 Extracting cBioPortal data (with sample counts)...")
        cbio_data = self.cbio_extractor.extract()
        
        if cbio_data.get('mutations') and cbio_data.get('studies'):
            logger.info(f"Got {len(cbio_data['mutations'])} mutations from {len(cbio_data['studies'])} studies")
            
            # Calculate real frequencies
            frequencies = self.aggregator.process_cbioportal_with_frequencies(
                cbio_data['mutations'], 
                cbio_data['studies']
            )
            results['frequency_data'] = frequencies
            logger.info(f"✅ Calculated {len(frequencies)} valid frequencies")
        
        # 2. Extract COSMIC data (catalog only - no denominators)
        logger.info("\n📚 Extracting COSMIC catalog data...")
        cosmic_data = self.cosmic_extractor.extract()
        
        if cosmic_data.get('mutations'):
            catalog = self.aggregator.process_cosmic_as_catalog(cosmic_data['mutations'])
            results['catalog_data'] = catalog
            logger.info(f"✅ Cataloged {len(catalog)} genes from COSMIC")
        
        # 3. Extract CIViC annotations (therapeutic relevance)
        logger.info("\n💊 Extracting CIViC clinical annotations...")
        try:
            civic_data = self.civic_extractor.extract()
            if civic_data.get('variants'):
                annotations = self.aggregator.process_civic_annotations(civic_data)
                results['annotation_data'] = annotations
                logger.info(f"✅ Found {len(annotations)} clinically annotated variants")
        except Exception as e:
            logger.warning(f"CIViC extraction failed: {e}")
        
        # 4. Create database records with proper data quality tiers
        logger.info("\n💾 Creating database records...")
        db_records = self.aggregator.create_final_database_records(
            results['frequency_data'],
            results['catalog_data'],
            results['annotation_data']
        )
        results['database_records'] = db_records
        
        # 5. Generate validation report
        results['validation_report'] = self._generate_validation_report(results)
        
        # 6. Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.aggregator.output_dir, f'production_pipeline_{timestamp}.json')
        
        # Convert MutationFrequency objects to dicts for JSON serialization
        results_json = {
            'frequency_data': [vars(f) for f in results['frequency_data']],
            'catalog_data': results['catalog_data'],
            'annotation_data': results['annotation_data'],
            'database_records': results['database_records'],
            'validation_report': results['validation_report']
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_json, f, indent=2, default=str)
        
        # 7. Load to database
        logger.info("\n🗄️ Loading to database...")
        self.loader.load_mutations(db_records)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _generate_validation_report(self, results: Dict) -> Dict:
        """Generate validation report for data quality"""
        report = {
            'total_frequency_calculations': len(results['frequency_data']),
            'total_catalog_entries': len(results['catalog_data']),
            'total_clinical_annotations': len(results['annotation_data']),
            'data_quality_distribution': {
                'population_frequency': len(results['frequency_data']),
                'occurrence_count': len(results['catalog_data']),
                'clinical_annotation': len(results['annotation_data'])
            }
        }
        
        if results['frequency_data']:
            frequencies = [f.frequency for f in results['frequency_data']]
            report['frequency_statistics'] = {
                'mean': round(np.mean(frequencies), 4),
                'median': round(np.median(frequencies), 4),
                'std': round(np.std(frequencies), 4),
                'min': round(min(frequencies), 4),
                'max': round(max(frequencies), 4)
            }
            
            # Check for known hotspots
            hotspot_validations = []
            for freq in results['frequency_data']:
                if freq.gene_symbol == 'KRAS' and 'Pancreatic' in freq.cancer_type:
                    hotspot_validations.append(f"KRAS in Pancreatic: {freq.frequency:.1%}")
                elif freq.gene_symbol == 'BRAF' and 'Melanoma' in freq.cancer_type:
                    hotspot_validations.append(f"BRAF in Melanoma: {freq.frequency:.1%}")
            
            report['hotspot_validations'] = hotspot_validations
        
        return report
    
    def _print_summary(self, results: Dict):
        """Print pipeline execution summary"""
        print("\n" + "="*70)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*70)
        
        report = results['validation_report']
        
        print(f"\n📊 Frequency Calculations (with denominators):")
        print(f"   Total: {report['total_frequency_calculations']}")
        if 'frequency_statistics' in report:
            stats = report['frequency_statistics']
            print(f"   Mean frequency: {stats['mean']:.1%}")
            print(f"   Median frequency: {stats['median']:.1%}")
            print(f"   Range: {stats['min']:.1%} - {stats['max']:.1%}")
        
        print(f"\n📚 Catalog Entries (no denominators):")
        print(f"   COSMIC genes: {report['total_catalog_entries']}")
        
        print(f"\n💊 Clinical Annotations:")
        print(f"   CIViC variants: {report['total_clinical_annotations']}")
        
        if report.get('hotspot_validations'):
            print(f"\n✅ Hotspot Validation:")
            for validation in report['hotspot_validations']:
                print(f"   {validation}")
        
        print(f"\n📁 Total database records: {len(results['database_records'])}")
        print("="*70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='OncoHotspot Production Pipeline - Scientifically Valid'
    )
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()
    
    try:
        pipeline = ProductionPipeline()
        results = pipeline.run()
        return 0
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())