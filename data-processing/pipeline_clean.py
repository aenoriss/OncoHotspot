#!/usr/bin/env python3
"""
OncoHotspot ETL Pipeline - CLEAN VERSION
Uses only cBioPortal (frequencies) and CIViC (clinical annotations)
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import numpy as np
from scipy import stats

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bronze.extractors import CBioPortalExtractor
from bronze.extractors.civic_extractor import CIViCExtractor
from silver.transformers import MutationStandardizer
from gold.aggregators import DatabaseLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MutationData:
    """Clean mutation data structure"""
    gene_symbol: str
    cancer_type: str
    protein_change: str
    chromosome: str
    position: int
    ref_allele: str
    alt_allele: str
    # Frequency data (from cBioPortal)
    samples_with_mutation: int
    total_samples_tested: int
    frequency: float
    ci_95_low: float
    ci_95_high: float
    studies: List[str]
    # Clinical data (from CIViC)
    is_clinically_actionable: bool = False
    therapies: List[str] = None
    evidence_level: str = None
    clinical_significance: str = None
    
    def __post_init__(self):
        if self.therapies is None:
            self.therapies = []
        # Validate data
        assert self.samples_with_mutation <= self.total_samples_tested
        assert 0 <= self.frequency <= 1


class CleanAggregator:
    """Clean aggregator using only cBioPortal and CIViC"""
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'gold', 'data')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def aggregate_cbioportal(self, mutations: List[Dict], studies: List[Dict]) -> Dict[str, MutationData]:
        """
        Aggregate cBioPortal mutations with proper frequency calculation
        Returns dict keyed by (gene, protein_change) for CIViC matching
        """
        logger.info(f"Aggregating {len(mutations)} cBioPortal mutations from {len(studies)} studies")
        
        # Build study denominators
        study_info = {}
        for study in studies:
            study_id = study.get('studyId')
            sample_count = (
                study.get('sequencedSampleCount') or 
                study.get('allSampleCount') or 
                0
            )
            cancer_type = study.get('cancerType', {}).get('name', 'Unknown')
            
            if study_id and sample_count > 0:
                study_info[study_id] = {
                    'samples': sample_count,
                    'cancer_type': cancer_type
                }
                logger.info(f"  {study_id}: {sample_count} samples ({cancer_type})")
        
        # Aggregate by gene-cancer-variant
        from collections import defaultdict
        aggregated = defaultdict(lambda: {
            'samples': set(),
            'studies': set(),
            'positions': set(),
            'ref_alleles': set(),
            'alt_alleles': set(),
            'chromosomes': set()
        })
        
        for mut in mutations:
            study_id = mut.get('studyId')
            if study_id not in study_info:
                continue
            
            gene = mut.get('gene', {}).get('hugoGeneSymbol', 'Unknown')
            cancer_type = study_info[study_id]['cancer_type']
            protein_change = mut.get('proteinChange', 'Unknown')
            
            key = (gene, cancer_type, protein_change)
            agg = aggregated[key]
            
            # Track unique samples
            sample_id = f"{study_id}:{mut.get('sampleId')}"
            agg['samples'].add(sample_id)
            agg['studies'].add(study_id)
            
            # Track genomic details
            if mut.get('chr'):
                agg['chromosomes'].add(mut['chr'])
            if mut.get('startPosition'):
                agg['positions'].add(mut['startPosition'])
            if mut.get('referenceAllele'):
                agg['ref_alleles'].add(mut['referenceAllele'])
            if mut.get('variantAllele'):
                agg['alt_alleles'].add(mut['variantAllele'])
        
        # Create MutationData objects
        results = {}
        for (gene, cancer_type, protein_change), data in aggregated.items():
            # Calculate total samples across all studies
            total_samples = sum(
                study_info[study_id]['samples'] 
                for study_id in data['studies']
                if study_id in study_info
            )
            
            mutation_count = len(data['samples'])
            
            # Calculate frequency with Wilson CI
            freq, ci_low, ci_high = self._calculate_wilson_ci(mutation_count, total_samples)
            
            # Create clean mutation record
            mutation = MutationData(
                gene_symbol=gene,
                cancer_type=cancer_type,
                protein_change=protein_change,
                chromosome=list(data['chromosomes'])[0] if data['chromosomes'] else 'Unknown',
                position=list(data['positions'])[0] if data['positions'] else 0,
                ref_allele=list(data['ref_alleles'])[0] if data['ref_alleles'] else '',
                alt_allele=list(data['alt_alleles'])[0] if data['alt_alleles'] else '',
                samples_with_mutation=mutation_count,
                total_samples_tested=total_samples,
                frequency=freq,
                ci_95_low=ci_low,
                ci_95_high=ci_high,
                studies=list(data['studies'])
            )
            
            # Key by gene and protein change for CIViC matching
            lookup_key = f"{gene}:{protein_change}"
            results[lookup_key] = mutation
        
        logger.info(f"Created {len(results)} aggregated mutation records")
        return results
    
    def enrich_with_civic(self, mutations: Dict[str, MutationData], civic_data: Dict) -> None:
        """
        Enrich mutation data with CIViC clinical annotations
        Modifies mutations in place
        """
        logger.info("Enriching with CIViC clinical annotations")
        
        enriched_count = 0
        for variant in civic_data.get('variants', []):
            gene = variant.get('gene', {}).get('name')
            variant_name = variant.get('name', '')
            
            # Try to match with our mutations
            for key, mutation in mutations.items():
                if mutation.gene_symbol == gene:
                    # Check if variant names match (fuzzy matching)
                    if self._variant_matches(mutation.protein_change, variant_name):
                        # Extract therapeutic information
                        therapies = set()
                        evidence_levels = set()
                        
                        for evidence in variant.get('evidence_items', []):
                            # Get therapies
                            for therapy in evidence.get('therapies', []):
                                therapies.add(therapy.get('name'))
                            
                            # Get evidence level
                            if evidence.get('evidence_level'):
                                evidence_levels.add(evidence['evidence_level'])
                        
                        # Update mutation with clinical info
                        if therapies:
                            mutation.is_clinically_actionable = True
                            mutation.therapies = list(therapies)
                            mutation.evidence_level = ', '.join(sorted(evidence_levels))
                            mutation.clinical_significance = variant.get('clinical_significance', 'Unknown')
                            enriched_count += 1
        
        logger.info(f"Enriched {enriched_count} mutations with clinical data")
    
    def _calculate_wilson_ci(self, successes: int, trials: int) -> tuple:
        """Calculate Wilson confidence interval"""
        if trials == 0:
            return 0.0, 0.0, 0.0
        
        p_hat = successes / trials
        z = 1.96  # 95% confidence
        
        denominator = 1 + z**2 / trials
        center = (p_hat + z**2 / (2 * trials)) / denominator
        margin = z * np.sqrt(p_hat * (1 - p_hat) / trials + z**2 / (4 * trials**2)) / denominator
        
        return (
            round(p_hat, 4),
            round(max(0, center - margin), 4),
            round(min(1, center + margin), 4)
        )
    
    def _variant_matches(self, protein_change: str, civic_variant: str) -> bool:
        """Check if protein changes match (simple matching)"""
        if not protein_change or not civic_variant:
            return False
        
        # Normalize formats
        protein_change = protein_change.upper().replace('P.', '')
        civic_variant = civic_variant.upper()
        
        # Direct match
        if protein_change in civic_variant or civic_variant in protein_change:
            return True
        
        # Extract position for position-based matching
        import re
        pos_match = re.search(r'\d+', protein_change)
        if pos_match:
            position = pos_match.group()
            if position in civic_variant:
                return True
        
        return False


class CleanPipeline:
    """Clean pipeline using only cBioPortal and CIViC"""
    
    def __init__(self):
        self.cbio_extractor = CBioPortalExtractor()
        self.civic_extractor = CIViCExtractor()
        self.aggregator = CleanAggregator()
        self.loader = DatabaseLoader()
    
    def run(self, limit_studies: Optional[List[str]] = None) -> Dict:
        """
        Run the clean pipeline
        
        Args:
            limit_studies: Optional list of study IDs to process (for testing)
        """
        logger.info("="*70)
        logger.info("CLEAN PIPELINE - cBioPortal + CIViC Only")
        logger.info("="*70)
        
        # 1. Extract cBioPortal data
        logger.info("\n📊 STEP 1: Extracting cBioPortal data...")
        
        # Use limited studies for testing if specified
        if limit_studies:
            logger.info(f"Limiting to studies: {limit_studies}")
            # Temporarily override config
            original_studies = self.cbio_extractor.config['target_studies']['cbioportal']
            self.cbio_extractor.config['target_studies']['cbioportal'] = limit_studies
        
        cbio_data = self.cbio_extractor.extract()
        
        if limit_studies:
            # Restore original config
            self.cbio_extractor.config['target_studies']['cbioportal'] = original_studies
        
        if not cbio_data.get('mutations') or not cbio_data.get('studies'):
            logger.error("No cBioPortal data extracted")
            return {}
        
        logger.info(f"✅ Extracted {len(cbio_data['mutations'])} mutations from {len(cbio_data['studies'])} studies")
        
        # 2. Aggregate cBioPortal data with frequencies
        logger.info("\n📈 STEP 2: Calculating mutation frequencies...")
        mutations = self.aggregator.aggregate_cbioportal(
            cbio_data['mutations'],
            cbio_data['studies']
        )
        logger.info(f"✅ Calculated frequencies for {len(mutations)} unique mutations")
        
        # 3. Extract CIViC clinical annotations
        logger.info("\n💊 STEP 3: Extracting CIViC clinical annotations...")
        try:
            civic_data = self.civic_extractor.extract()
            logger.info(f"✅ Extracted {len(civic_data.get('variants', []))} CIViC variants")
            
            # 4. Enrich mutations with clinical data
            logger.info("\n🔗 STEP 4: Enriching with clinical annotations...")
            self.aggregator.enrich_with_civic(mutations, civic_data)
            
        except Exception as e:
            logger.warning(f"CIViC enrichment failed: {e}")
        
        # 5. Prepare database records
        logger.info("\n💾 STEP 5: Preparing database records...")
        db_records = self._prepare_database_records(mutations)
        
        # 6. Generate summary statistics
        summary = self._generate_summary(mutations)
        
        # 7. Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.aggregator.output_dir, f'clean_pipeline_{timestamp}.json')
        
        results = {
            'mutations': [asdict(m) for m in mutations.values()],
            'database_records': db_records,
            'summary': summary,
            'timestamp': timestamp
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"✅ Saved results to {output_file}")
        
        # 8. Load to database
        logger.info("\n🗄️ STEP 6: Loading to database...")
        load_stats = self.loader.load_mutations(db_records)
        logger.info(f"✅ Loaded {load_stats.get('inserted', 0)} new, updated {load_stats.get('updated', 0)} existing")
        
        # Print summary
        self._print_summary(summary)
        
        return results
    
    def _prepare_database_records(self, mutations: Dict[str, MutationData]) -> List[Dict]:
        """Convert MutationData to database records"""
        records = []
        
        for mutation in mutations.values():
            # Calculate significance score (frequency-based with clinical boost)
            significance = mutation.frequency
            if mutation.is_clinically_actionable:
                significance = min(significance * 1.5, 1.0)  # Boost for actionable
            
            record = {
                'gene_symbol': mutation.gene_symbol,
                'cancer_type': mutation.cancer_type,
                'protein_change': mutation.protein_change,
                'chromosome': mutation.chromosome,
                'position': mutation.position,
                'ref_allele': mutation.ref_allele,
                'alt_allele': mutation.alt_allele,
                'mutation_count': mutation.samples_with_mutation,
                'total_samples': mutation.total_samples_tested,
                'frequency': mutation.frequency,
                'frequency_ci_low': mutation.ci_95_low,
                'frequency_ci_high': mutation.ci_95_high,
                'significance_score': round(significance, 3),
                'is_clinically_actionable': mutation.is_clinically_actionable,
                'therapies': ', '.join(mutation.therapies) if mutation.therapies else None,
                'evidence_level': mutation.evidence_level,
                'clinical_significance': mutation.clinical_significance,
                'source': 'cbioportal+civic',
                'studies': ', '.join(mutation.studies)
            }
            records.append(record)
        
        return records
    
    def _generate_summary(self, mutations: Dict[str, MutationData]) -> Dict:
        """Generate summary statistics"""
        mutation_list = list(mutations.values())
        
        if not mutation_list:
            return {}
        
        frequencies = [m.frequency for m in mutation_list]
        actionable = [m for m in mutation_list if m.is_clinically_actionable]
        
        # Find top mutations
        top_by_frequency = sorted(mutation_list, key=lambda x: x.frequency, reverse=True)[:10]
        top_actionable = sorted(actionable, key=lambda x: x.frequency, reverse=True)[:10]
        
        # Cancer type distribution
        cancer_types = {}
        for m in mutation_list:
            cancer_types[m.cancer_type] = cancer_types.get(m.cancer_type, 0) + 1
        
        return {
            'total_mutations': len(mutation_list),
            'clinically_actionable': len(actionable),
            'frequency_stats': {
                'mean': round(np.mean(frequencies), 4),
                'median': round(np.median(frequencies), 4),
                'std': round(np.std(frequencies), 4),
                'min': round(min(frequencies), 4),
                'max': round(max(frequencies), 4)
            },
            'top_mutations': [
                {
                    'gene': m.gene_symbol,
                    'cancer': m.cancer_type,
                    'variant': m.protein_change,
                    'frequency': m.frequency,
                    'actionable': m.is_clinically_actionable
                }
                for m in top_by_frequency
            ],
            'top_actionable': [
                {
                    'gene': m.gene_symbol,
                    'variant': m.protein_change,
                    'frequency': m.frequency,
                    'therapies': m.therapies
                }
                for m in top_actionable
            ],
            'cancer_type_distribution': cancer_types,
            'unique_genes': len(set(m.gene_symbol for m in mutation_list)),
            'unique_cancer_types': len(cancer_types)
        }
    
    def _print_summary(self, summary: Dict):
        """Print execution summary"""
        print("\n" + "="*70)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*70)
        
        print(f"\n📊 Total Mutations: {summary['total_mutations']}")
        print(f"💊 Clinically Actionable: {summary['clinically_actionable']} "
              f"({summary['clinically_actionable']/summary['total_mutations']*100:.1f}%)")
        
        print(f"\n📈 Frequency Statistics:")
        stats = summary['frequency_stats']
        print(f"   Mean: {stats['mean']:.1%}")
        print(f"   Median: {stats['median']:.1%}")
        print(f"   Range: {stats['min']:.1%} - {stats['max']:.1%}")
        
        print(f"\n🧬 Coverage:")
        print(f"   Unique genes: {summary['unique_genes']}")
        print(f"   Cancer types: {summary['unique_cancer_types']}")
        
        print(f"\n🔝 Top Mutations by Frequency:")
        for i, mut in enumerate(summary['top_mutations'][:5], 1):
            actionable = "✓" if mut['actionable'] else " "
            print(f"   {i}. {mut['gene']} {mut['variant']} in {mut['cancer']}: "
                  f"{mut['frequency']:.1%} [{actionable}]")
        
        if summary['top_actionable']:
            print(f"\n💊 Top Actionable Mutations:")
            for i, mut in enumerate(summary['top_actionable'][:5], 1):
                therapies = len(mut['therapies']) if mut['therapies'] else 0
                print(f"   {i}. {mut['gene']} {mut['variant']}: "
                      f"{mut['frequency']:.1%} ({therapies} therapies)")
        
        print("="*70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean OncoHotspot Pipeline - cBioPortal + CIViC'
    )
    parser.add_argument(
        '--test', 
        action='store_true', 
        help='Run in test mode with limited data'
    )
    parser.add_argument(
        '--studies',
        nargs='+',
        help='Specific study IDs to process'
    )
    
    args = parser.parse_args()
    
    try:
        pipeline = CleanPipeline()
        
        # Use test studies if in test mode
        if args.test:
            test_studies = [
                'brca_tcga_pan_can_atlas_2018',  # Breast cancer
                'luad_tcga_pan_can_atlas_2018',  # Lung adenocarcinoma
            ]
            results = pipeline.run(limit_studies=test_studies)
        elif args.studies:
            results = pipeline.run(limit_studies=args.studies)
        else:
            results = pipeline.run()
        
        return 0 if results else 1
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())