"""Mutation aggregator for Gold layer"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class MutationAggregator:
    """Aggregate standardized mutations for business use"""
    
    def __init__(self):
        self.gold_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
    
    def aggregate(self, silver_mutations: List[Dict]) -> Dict[str, Any]:
        """
        Main aggregation method called by pipeline
        
        Args:
            silver_mutations: List of standardized mutations from Silver layer
            
        Returns:
            Dictionary with aggregated mutation data
        """
        logger.info(f"Starting mutation aggregation for {len(silver_mutations)} mutations")
        
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
        
    def aggregate_for_heatmap(self, silver_mutations: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate mutations for heatmap visualization
        
        Args:
            silver_mutations: List of standardized mutations from Silver layer
            
        Returns:
            Dictionary with aggregated data ready for heatmap
        """
        logger.info(f"Aggregating {len(silver_mutations)} mutations for heatmap")
        
        # First, extract study sample counts from cBioPortal metadata
        study_sample_counts = self._extract_study_sample_counts(silver_mutations)
        
        # Group mutations by key (gene, position, cancer_type)
        aggregated = defaultdict(lambda: {
            'mutation_count': 0,
            'sample_count': 0,
            'frequencies': [],
            'samples': set(),
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
            
            # Track unique samples
            if mutation.get('sample_id'):
                agg['samples'].add(mutation['sample_id'])
            
            # Track studies
            if mutation.get('cancer_study'):
                agg['studies'].add(mutation['cancer_study'])
            
            # Track alleles
            if mutation.get('reference_allele'):
                agg['ref_alleles'].add(mutation['reference_allele'])
            if mutation.get('variant_allele'):
                agg['alt_alleles'].add(mutation['variant_allele'])
            
            # Track protein changes
            if mutation.get('protein_change'):
                agg['protein_changes'].add(mutation['protein_change'])
            
            # Collect frequencies
            if mutation.get('allele_frequency') is not None:
                agg['frequencies'].append(mutation['allele_frequency'])
        
        # Process aggregated data
        result = {
            'mutations': [],
            'genes': set(),
            'cancer_types': set(),
            'summary': {}
        }
        
        for key, data in aggregated.items():
            gene, position, cancer_type = key
            
            # Calculate proper total samples for this gene-cancer combination
            total_samples = self._calculate_total_samples(gene, cancer_type, data['studies'], study_sample_counts)
            
            # Skip mutations where we don't have total sample count data
            if total_samples is None:
                logger.debug(f"Skipping {gene}:{cancer_type} - no sample count data")
                continue
            
            mutated_samples = len(data['samples'])
            
            # Calculate proper mutation frequency as decimal (0.0 to 1.0)
            mutation_frequency = round(mutated_samples / total_samples, 4)
            
            # Calculate statistics
            processed = {
                'gene_symbol': gene,
                'position': position,
                'cancer_type': cancer_type,
                'mutation_count': data['mutation_count'],
                'sample_count': total_samples,  # Use total samples, not just mutated samples
                'mutated_samples': mutated_samples,  # Track actual mutated samples
                'ref_allele': self._most_common(data['ref_alleles']),
                'alt_allele': self._most_common(data['alt_alleles']),
                'protein_change': self._most_common(data['protein_changes']),
                'frequency': mutation_frequency,  # Use calculated percentage
                'significance_score': self._calculate_significance(
                    data['mutation_count'],
                    total_samples,
                    data['frequencies']
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
        
        logger.info(f"Aggregation complete: {result['summary']}")
        
        return result
    
    def aggregate_by_gene(self, silver_mutations: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate mutations by gene
        
        Args:
            silver_mutations: List of standardized mutations
            
        Returns:
            Dictionary with gene-level aggregations
        """
        gene_data = defaultdict(lambda: {
            'total_mutations': 0,
            'unique_positions': set(),
            'cancer_types': set(),
            'samples': set(),
            'hotspot_mutations': 0,
            'protein_changes': defaultdict(int)
        })
        
        for mutation in silver_mutations:
            gene = mutation.get('gene_symbol')
            if not gene:
                continue
            
            gd = gene_data[gene]
            gd['total_mutations'] += 1
            
            if mutation.get('start_position'):
                gd['unique_positions'].add(mutation['start_position'])
            
            if mutation.get('cancer_type'):
                gd['cancer_types'].add(mutation['cancer_type'])
            
            if mutation.get('sample_id'):
                gd['samples'].add(mutation['sample_id'])
            
            protein_change = mutation.get('protein_change')
            if protein_change:
                gd['protein_changes'][protein_change] += 1
        
        # Process gene data
        result = {}
        for gene, data in gene_data.items():
            # Find most frequent mutations
            top_mutations = sorted(
                data['protein_changes'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            result[gene] = {
                'gene_symbol': gene,
                'total_mutations': data['total_mutations'],
                'unique_positions': len(data['unique_positions']),
                'cancer_type_count': len(data['cancer_types']),
                'sample_count': len(data['samples']),
                'mutation_density': data['total_mutations'] / max(len(data['samples']), 1),
                'top_mutations': [
                    {'protein_change': pc, 'count': count}
                    for pc, count in top_mutations
                ],
                'cancer_types': sorted(list(data['cancer_types']))
            }
        
        return result
    
    def _extract_study_sample_counts(self, silver_mutations: List[Dict]) -> Dict[str, int]:
        """
        Extract total sample counts for each study from cBioPortal data
        
        Returns actual sample counts from study metadata, not estimates.
        """
        import json
        import os
        import glob
        
        # Find the most recent cBioPortal bronze data file
        bronze_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'bronze', 'data', 'cbioportal'
        )
        bronze_files = glob.glob(os.path.join(bronze_path, 'cbioportal_*.json'))
        
        study_counts = {}
        
        if bronze_files:
            # Sort by modification time, get most recent
            latest_file = max(bronze_files, key=os.path.getmtime)
            
            try:
                with open(latest_file, 'r') as f:
                    bronze_data = json.load(f)
                    
                # Extract study sample counts from bronze data
                if 'study_sample_counts' in bronze_data:
                    study_counts = bronze_data['study_sample_counts']
                    logger.info(f"Loaded actual sample counts for {len(study_counts)} studies from bronze data")
                elif 'studies' in bronze_data:
                    # Fallback: extract from studies array
                    for study in bronze_data['studies']:
                        if 'studyId' in study and 'allSampleCount' in study:
                            study_counts[study['studyId']] = study['allSampleCount']
                    logger.info(f"Extracted sample counts for {len(study_counts)} studies from study info")
                else:
                    logger.warning("No sample count data found in bronze layer")
            except Exception as e:
                logger.error(f"Failed to load bronze data: {e}")
        else:
            logger.warning("No bronze data files found")
        
        # Log studies without sample counts
        studies_in_mutations = set(m.get('cancer_study') for m in silver_mutations if m.get('cancer_study'))
        missing_studies = studies_in_mutations - set(study_counts.keys())
        if missing_studies:
            logger.warning(f"No sample counts for studies: {missing_studies}")
        
        return study_counts
    
    def _calculate_total_samples(self, gene: str, cancer_type: str, studies: set, 
                               study_sample_counts: Dict[str, int]) -> Optional[int]:
        """
        Calculate total samples tested for a gene-cancer type combination
        
        Args:
            gene: Gene symbol
            cancer_type: Cancer type
            studies: Set of studies containing this gene-cancer combination
            study_sample_counts: Dictionary of study -> total sample count
            
        Returns:
            Total number of samples tested, or None if no sample count data available
        """
        total_samples = 0
        missing_data = False
        
        for study in studies:
            if study in study_sample_counts:
                total_samples += study_sample_counts[study]
            else:
                # We don't have sample count for this study
                missing_data = True
                logger.debug(f"Missing sample count for study: {study}")
        
        # Only return total if we have complete data
        if missing_data or total_samples == 0:
            return None
        
        return total_samples
    
    def _validate_for_aggregation(self, mutation: Dict) -> bool:
        """Validate mutation has required fields for aggregation"""
        required = ['gene_symbol', 'cancer_type']
        return all(mutation.get(field) for field in required)
    
    def _create_aggregation_key(self, mutation: Dict) -> Tuple[str, int, str]:
        """Create aggregation key from mutation"""
        gene = mutation.get('gene_symbol', 'UNKNOWN')
        cancer_type = mutation.get('cancer_type', 'Unknown')
        
        # Extract position from protein change or genomic position
        position = None
        if mutation.get('protein_change'):
            import re
            match = re.search(r'\d+', mutation['protein_change'])
            if match:
                position = int(match.group())
        
        if position is None:
            position = mutation.get('start_position', 0)
        
        return (gene, position, cancer_type)
    
    def _most_common(self, items: set) -> str:
        """Get most common item from a set"""
        if not items:
            return ''
        if len(items) == 1:
            return list(items)[0]
        # Return first item alphabetically for consistency
        return sorted(list(items))[0]
    
    def _calculate_frequency(self, frequencies: List[float]) -> float:
        """Calculate average frequency"""
        if not frequencies:
            return 0.0
        
        # Remove outliers
        if len(frequencies) > 3:
            frequencies = self._remove_outliers(frequencies)
        
        return round(np.mean(frequencies), 4)
    
    def _remove_outliers(self, values: List[float]) -> List[float]:
        """Remove outliers using IQR method"""
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [v for v in values if lower_bound <= v <= upper_bound]
    
    def _calculate_significance(self, mutation_count: int, sample_count: int, 
                               frequencies: List[float]) -> float:
        """
        Calculate clinical significance score (0-1)
        
        Factors:
        - Recurrence (how many times seen)
        - Frequency (allele frequency)
        - Sample coverage (how many samples)
        """
        # Base score from frequency
        avg_frequency = self._calculate_frequency(frequencies) if frequencies else 0
        freq_score = min(avg_frequency * 2, 0.5)  # Max 0.5 from frequency
        
        # Recurrence score (logarithmic scale)
        recurrence_score = min(np.log10(mutation_count + 1) / 3, 0.3)  # Max 0.3
        
        # Sample coverage score
        coverage_score = min(sample_count / 100, 0.2)  # Max 0.2
        
        # Combine scores
        significance = freq_score + recurrence_score + coverage_score
        
        return round(min(significance, 1.0), 2)
    
    def save_gold_data(self, aggregated_data: Dict, data_type: str = 'heatmap') -> Dict:
        """
        Save aggregated data to Gold layer
        
        Args:
            aggregated_data: Aggregated data dictionary
            data_type: Type of aggregation (heatmap, gene_summary, etc.)
            
        Returns:
            Metadata about saved data
        """
        timestamp = datetime.utcnow()
        
        # Create directory
        data_dir = os.path.join(self.gold_path, f'{data_type}_data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Save data
        filename = f"{data_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(aggregated_data, f, indent=2, default=str)
        
        metadata = {
            'data_type': data_type,
            'record_count': len(aggregated_data.get('mutations', [])),
            'timestamp': timestamp.isoformat(),
            'file': filepath,
            'summary': aggregated_data.get('summary', {})
        }
        
        logger.info(f"Saved {data_type} data to {filepath}")
        return metadata