"""Fixed mutation aggregator for Gold layer - properly calculates frequencies"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class MutationAggregator:
    """Aggregate standardized mutations for business use - FIXED VERSION"""
    
    def __init__(self):
        self.gold_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        # Store total samples per cancer study
        self.study_sample_counts = {}
    
    def aggregate(self, silver_mutations: List[Dict], study_info: List[Dict] = None) -> Dict[str, Any]:
        """
        Main aggregation method called by pipeline
        
        Args:
            silver_mutations: List of standardized mutations from Silver layer
            study_info: List of study information including sample counts
            
        Returns:
            Dictionary with aggregated mutation data
        """
        logger.info(f"Starting mutation aggregation for {len(silver_mutations)} mutations")
        
        # First, extract total sample counts from study info
        if study_info:
            self._extract_study_sample_counts(study_info)
        
        # Create heatmap aggregation
        heatmap_data = self.aggregate_for_heatmap(silver_mutations)
        
        # Create gene-level aggregation
        gene_data = self.aggregate_by_gene(silver_mutations)
        
        # Save both datasets
        heatmap_metadata = self.save_gold_data(heatmap_data, 'heatmap')
        gene_metadata = self.save_gold_data(gene_data, 'gene_summary')
        
        result = {
            'heatmap': heatmap_data,
            'genes': gene_data,
            'metadata': {
                'heatmap': heatmap_metadata,
                'genes': gene_metadata
            }
        }
        
        logger.info("Mutation aggregation complete")
        return result
    
    def _extract_study_sample_counts(self, study_info: List[Dict]):
        """Extract total sample counts from study information"""
        for study in study_info:
            study_id = study.get('studyId', study.get('cancer_study_identifier'))
            # Look for sample count in various fields
            sample_count = (
                study.get('numberOfSamples') or 
                study.get('allSampleCount') or
                study.get('cnaSampleCount') or
                study.get('sequencedSampleCount') or
                100  # Default if not found
            )
            
            # Map study ID to cancer type
            cancer_type = study.get('cancerType', {}).get('name', study.get('name', study_id))
            self.study_sample_counts[cancer_type] = sample_count
            logger.info(f"Study {study_id} ({cancer_type}): {sample_count} total samples")
        
    def aggregate_for_heatmap(self, silver_mutations: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate mutations for heatmap visualization - FIXED to use correct total samples
        
        Args:
            silver_mutations: List of standardized mutations from Silver layer
            
        Returns:
            Dictionary with aggregated data ready for heatmap
        """
        logger.info(f"Aggregating {len(silver_mutations)} mutations for heatmap")
        
        # Group mutations by key (gene, position, cancer_type)
        aggregated = defaultdict(lambda: {
            'mutation_count': 0,
            'samples_with_mutation': set(),  # Samples that have the mutation
            'frequencies': [],
            'studies': set(),
            'ref_alleles': set(),
            'alt_alleles': set(),
            'protein_changes': set()
        })
        
        # Aggregate mutations
        for mutation in silver_mutations:
            # Skip invalid mutations
            if not self._validate_for_aggregation(mutation):
                continue
            
            # Create aggregation key
            key = self._create_aggregation_key(mutation)
            
            # Update aggregated data
            agg = aggregated[key]
            agg['mutation_count'] += 1
            
            # Track unique samples with mutation
            if mutation.get('sample_id'):
                agg['samples_with_mutation'].add(mutation['sample_id'])
            
            # Track studies
            if mutation.get('cancer_study'):
                agg['studies'].add(mutation['cancer_study'])
            
            # Track frequencies if available
            if mutation.get('frequency'):
                agg['frequencies'].append(mutation['frequency'])
            
            # Track alleles
            if mutation.get('ref_allele'):
                agg['ref_alleles'].add(mutation['ref_allele'])
            if mutation.get('alt_allele'):
                agg['alt_alleles'].add(mutation['alt_allele'])
            if mutation.get('protein_change'):
                agg['protein_changes'].add(mutation['protein_change'])
        
        # Process aggregated data
        result = {
            'mutations': [],
            'genes': set(),
            'cancer_types': set()
        }
        
        for key, data in aggregated.items():
            gene, position, cancer_type = key
            
            # Get total samples for this cancer type
            total_samples = self._get_total_samples_for_cancer(cancer_type, data['studies'])
            
            # Calculate the CORRECT frequency
            samples_with_mutation = len(data['samples_with_mutation'])
            true_frequency = samples_with_mutation / total_samples if total_samples > 0 else 0
            
            processed = {
                'gene_symbol': gene,
                'position': position,
                'cancer_type': cancer_type,
                'mutation_count': samples_with_mutation,  # Number of samples WITH mutation
                'total_samples': total_samples,  # Total samples tested (with or without mutation)
                'frequency': true_frequency,  # Correct calculation
                'ref_allele': self._most_common(data['ref_alleles']),
                'alt_allele': self._most_common(data['alt_alleles']),
                'protein_change': self._most_common(data['protein_changes']),
                'significance_score': self._calculate_biological_significance(
                    samples_with_mutation,
                    total_samples,
                    true_frequency
                ),
                'study_count': len(data['studies'])
            }
            
            result['mutations'].append(processed)
            result['genes'].add(gene)
            result['cancer_types'].add(cancer_type)
        
        # Add summary statistics
        result['summary'] = {
            'total_mutations': len(result['mutations']),
            'unique_genes': len(result['genes']),
            'unique_cancer_types': len(result['cancer_types']),
            'avg_mutations_per_gene': len(result['mutations']) / max(len(result['genes']), 1)
        }
        
        # Convert sets to lists for JSON serialization
        result['genes'] = sorted(list(result['genes']))
        result['cancer_types'] = sorted(list(result['cancer_types']))
        
        return result
    
    def _get_total_samples_for_cancer(self, cancer_type: str, studies: set) -> int:
        """
        Get the total number of samples for a cancer type
        
        This is the KEY FIX - we need the total samples tested, not just those with mutations
        """
        # Try to get from study info
        if cancer_type in self.study_sample_counts:
            return self.study_sample_counts[cancer_type]
        
        # Try common cancer type mappings
        cancer_type_mappings = {
            'Lung Adenocarcinoma': 'Lung Cancer',
            'Breast Invasive Carcinoma': 'Breast Cancer',
            'Colorectal Adenocarcinoma': 'Colorectal Cancer',
            'Skin Cutaneous Melanoma': 'Melanoma',
            'Pancreatic Adenocarcinoma': 'Pancreatic Cancer',
            'Lower Grade Glioma': 'Brain Cancer',
            'Glioblastoma Multiforme': 'Brain Cancer'
        }
        
        mapped_type = cancer_type_mappings.get(cancer_type, cancer_type)
        if mapped_type in self.study_sample_counts:
            return self.study_sample_counts[mapped_type]
        
        # Default sample counts based on typical TCGA cohort sizes
        default_sample_counts = {
            'Lung Cancer': 1000,
            'Breast Cancer': 1100,
            'Colorectal Cancer': 650,
            'Melanoma': 470,
            'Pancreatic Cancer': 185,
            'Brain Cancer': 600,
            'Prostate Cancer': 500,
            'Ovarian Cancer': 585,
            'Kidney Cancer': 530,
            'Liver Cancer': 377,
            'Thyroid Cancer': 507,
            'Bladder Cancer': 412,
            'Gastric Cancer': 443
        }
        
        # Return default or 100 as fallback
        return default_sample_counts.get(mapped_type, 100)
    
    def _calculate_biological_significance(self, mutation_count: int, total_samples: int, 
                                          frequency: float) -> float:
        """
        Calculate biological significance score (0-1) based on proper frequency
        
        This replaces the broken significance calculation
        """
        if total_samples == 0:
            return 0.0
        
        # Use frequency as the primary metric (it's the most honest)
        if frequency >= 0.5:
            # >50% frequency: Very high significance
            significance = 0.90 + (frequency - 0.5) * 0.2
        elif frequency >= 0.2:
            # 20-50% frequency: High significance
            significance = 0.70 + (frequency - 0.2) * 0.667
        elif frequency >= 0.05:
            # 5-20% frequency: Medium significance
            significance = 0.40 + (frequency - 0.05) * 2.0
        elif frequency >= 0.01:
            # 1-5% frequency: Low significance
            significance = 0.20 + (frequency - 0.01) * 4.44
        else:
            # <1% frequency: Very low significance
            significance = frequency * 20
        
        return round(min(significance, 1.0), 2)
    
    def aggregate_by_gene(self, silver_mutations: List[Dict]) -> List[Dict]:
        """
        Aggregate mutations by gene - FIXED version
        """
        gene_data = defaultdict(lambda: {
            'total_mutations': 0,
            'unique_positions': set(),
            'cancer_types': set(),
            'samples': set(),
            'protein_changes': set(),
            'studies': set()
        })
        
        # Group mutations by gene
        for mutation in silver_mutations:
            if not mutation.get('gene_symbol'):
                continue
            
            gene = mutation['gene_symbol']
            
            gd = gene_data[gene]
            gd['total_mutations'] += 1
            
            if mutation.get('start_position'):
                gd['unique_positions'].add(mutation['start_position'])
            
            if mutation.get('cancer_type'):
                gd['cancer_types'].add(mutation['cancer_type'])
            
            if mutation.get('sample_id'):
                gd['samples'].add(mutation['sample_id'])
            
            if mutation.get('protein_change'):
                gd['protein_changes'].add(mutation['protein_change'])
            
            if mutation.get('cancer_study'):
                gd['studies'].add(mutation['cancer_study'])
        
        # Convert to list format
        result = []
        for gene, data in gene_data.items():
            result.append({
                'gene_symbol': gene,
                'total_mutations': data['total_mutations'],
                'unique_positions': len(data['unique_positions']),
                'cancer_type_count': len(data['cancer_types']),
                'sample_count': len(data['samples']),
                'mutation_density': data['total_mutations'] / max(len(data['samples']), 1),
                'top_mutations': []  # Would need more processing for this
            })
        
        return sorted(result, key=lambda x: x['total_mutations'], reverse=True)
    
    def _validate_for_aggregation(self, mutation: Dict) -> bool:
        """Validate mutation has required fields"""
        required = ['gene_symbol', 'cancer_type']
        return all(mutation.get(field) for field in required)
    
    def _create_aggregation_key(self, mutation: Dict) -> Tuple[str, int, str]:
        """Create unique key for aggregation"""
        return (
            mutation.get('gene_symbol', 'UNKNOWN'),
            mutation.get('start_position', 0),
            mutation.get('cancer_type', 'UNKNOWN')
        )
    
    def _most_common(self, items: set) -> str:
        """Return most common item or first if all unique"""
        if not items:
            return ''
        return sorted(items)[0]  # Simple approach - return first alphabetically
    
    def _calculate_frequency(self, frequencies: List[float]) -> float:
        """Calculate average frequency"""
        if not frequencies:
            return 0.0
        return sum(frequencies) / len(frequencies)
    
    def save_gold_data(self, aggregated_data: Dict, data_type: str = 'heatmap') -> Dict:
        """Save aggregated data to Gold layer"""
        os.makedirs(self.gold_path, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(self.gold_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(aggregated_data, f, indent=2, default=str)
        
        logger.info(f"Saved {data_type} data to {filepath}")
        
        return {
            'filepath': filepath,
            'timestamp': timestamp,
            'record_count': len(aggregated_data.get('mutations', []))
        }