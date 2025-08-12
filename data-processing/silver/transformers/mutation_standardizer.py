"""Mutation data standardizer for Silver layer"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import yaml
from .cancer_type_mapper import CancerTypeMapper
from .variant_harmonizer import VariantHarmonizer

logger = logging.getLogger(__name__)


class MutationStandardizer:
    """Standardize mutation data from various sources into a unified format"""
    
    def __init__(self):
        self.cancer_mapper = CancerTypeMapper()
        self.variant_harmonizer = VariantHarmonizer()
        self.silver_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        
    def standardize_batch(self, mutations: List[Dict], source: str = 'cbioportal') -> List[Dict]:
        """
        Standardize a batch of mutations from any source
        
        Args:
            mutations: List of mutation records
            source: Source system (cbioportal, civic, etc.)
            
        Returns:
            List of standardized mutation records
        """
        if source == 'cbioportal':
            return self.standardize_cbioportal({'mutations': mutations})
        else:
            logger.warning(f"Unknown source {source}, falling back to cBioPortal standardization")
            return self.standardize_cbioportal({'mutations': mutations})

    def standardize_cbioportal(self, bronze_data: Dict[str, Any]) -> List[Dict]:
        """
        Standardize cBioPortal mutation data
        
        Args:
            bronze_data: Raw data from cBioPortal extractor
            
        Returns:
            List of standardized mutation records
        """
        silver_mutations = []
        
        for mutation in bronze_data.get('mutations', []):
            try:
                standardized = self._standardize_cbioportal_mutation(mutation)
                if standardized and self._validate_mutation(standardized):
                    silver_mutations.append(standardized)
            except Exception as e:
                logger.error(f"Error standardizing mutation: {e}")
                continue
        
        logger.info(f"Standardized {len(silver_mutations)} cBioPortal mutations")
        return silver_mutations
    
    def _standardize_cbioportal_mutation(self, mutation: Dict) -> Optional[Dict]:
        """Standardize a single cBioPortal mutation record"""
        
        # Extract cancer type from study ID
        study_id = mutation.get('studyId', '')
        cancer_type = self._extract_cancer_type_from_study(study_id)
        
        # Calculate allele frequency
        alt_count = mutation.get('tumorAltCount', 0)
        ref_count = mutation.get('tumorRefCount', 0)
        total_count = alt_count + ref_count
        
        allele_frequency = alt_count / total_count if total_count > 0 else 0
        
        # Handle nested gene structure
        gene_info = mutation.get('gene', {})
        gene_symbol = gene_info.get('hugoGeneSymbol', '') or mutation.get('hugoGeneSymbol', '')
        entrez_id = mutation.get('entrezGeneId') or gene_info.get('entrezGeneId')
        
        standardized = {
            # Gene information
            'gene_symbol': gene_symbol.upper() if gene_symbol else '',
            'entrez_gene_id': entrez_id,
            
            # Genomic coordinates
            'chromosome': str(mutation.get('chr', '')),
            'start_position': mutation.get('startPosition'),
            'end_position': mutation.get('endPosition'),
            'strand': mutation.get('strand'),
            
            # Variant information
            'reference_allele': mutation.get('referenceAllele', ''),
            'variant_allele': mutation.get('variantAllele', ''),
            'variant_type': mutation.get('variantType', ''),
            'variant_classification': mutation.get('variantClassification', ''),
            
            # Protein change
            'protein_change': self.variant_harmonizer.harmonize_protein_change(
                mutation.get('proteinChange', '')
            ),
            'hgvsp': mutation.get('hgvsp', ''),
            'hgvsc': mutation.get('hgvsc', ''),
            
            # Cancer and sample information
            'cancer_type': self.cancer_mapper.map_to_standard(cancer_type),
            'cancer_study': study_id,
            'sample_id': mutation.get('sampleId'),
            'patient_id': mutation.get('patientId'),
            
            # Frequency and counts
            'allele_frequency': round(allele_frequency, 4),
            'tumor_alt_count': alt_count,
            'tumor_ref_count': ref_count,
            'normal_alt_count': mutation.get('normalAltCount', 0),
            'normal_ref_count': mutation.get('normalRefCount', 0),
            
            # Clinical significance
            'mutation_status': mutation.get('mutationStatus'),
            'validation_status': mutation.get('validationStatus'),
            'functional_impact_score': mutation.get('functionalImpactScore'),
            
            # Metadata
            'source': 'cbioportal',
            'source_id': mutation.get('mutationId'),
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        return standardized
    
    def standardize_cosmic(self, bronze_data: Dict[str, Any]) -> List[Dict]:
        """
        Standardize COSMIC mutation data
        
        Args:
            bronze_data: Raw data from COSMIC extractor
            
        Returns:
            List of standardized mutation records
        """
        silver_mutations = []
        
        for mutation in bronze_data.get('mutations', []):
            try:
                standardized = self._standardize_cosmic_mutation(mutation)
                if standardized and self._validate_mutation(standardized):
                    silver_mutations.append(standardized)
            except Exception as e:
                logger.error(f"Error standardizing COSMIC mutation: {e}")
                continue
        
        logger.info(f"Standardized {len(silver_mutations)} COSMIC mutations")
        return silver_mutations
    
    def _standardize_cosmic_mutation(self, mutation: Dict) -> Optional[Dict]:
        """Standardize a single COSMIC mutation record"""
        
        # Parse protein change
        protein_change = mutation.get('protein_change', '')
        if not protein_change:
            protein_change = mutation.get('MutationAA', '')
        
        # Parse CDS change to extract alleles
        cds_change = mutation.get('cds_change', '') or mutation.get('MutationCDS', '')
        ref_allele, alt_allele = self._parse_cds_change(cds_change)
        
        # Map cancer type from histology and site
        histology = mutation.get('primary_histology', '')
        site = mutation.get('primary_site', '')
        cancer_type = self._map_cosmic_cancer_type(histology, site)
        
        standardized = {
            # Gene information
            'gene_symbol': mutation.get('gene', '').upper(),
            'gene_name': mutation.get('gene_name', ''),
            
            # Genomic coordinates (may need to parse from genome_position)
            'chromosome': self._extract_chromosome(mutation.get('genome_position', '')),
            'start_position': self._extract_position(mutation.get('genome_position', '')),
            'end_position': None,  # Not always available in COSMIC
            
            # Variant information
            'reference_allele': ref_allele,
            'variant_allele': alt_allele,
            'variant_type': self._infer_variant_type(ref_allele, alt_allele),
            
            # Protein change
            'protein_change': self.variant_harmonizer.harmonize_protein_change(protein_change),
            'cds_change': cds_change,
            
            # Cancer information
            'cancer_type': self.cancer_mapper.map_to_standard(cancer_type),
            'primary_histology': histology,
            'primary_site': site,
            
            # COSMIC specific
            'cosmic_id': mutation.get('mutation_id'),
            
            # Metadata
            'source': 'cosmic',
            'source_id': mutation.get('mutation_id'),
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        return standardized
    
    def _validate_mutation(self, mutation: Dict) -> bool:
        """
        Validate that a mutation record has required fields
        
        Args:
            mutation: Standardized mutation record
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['gene_symbol', 'reference_allele', 'variant_allele']
        
        for field in required_fields:
            if not mutation.get(field):
                logger.debug(f"Missing required field: {field}")
                return False
        
        # Additional validation
        if mutation.get('allele_frequency') and mutation['allele_frequency'] > 1:
            logger.warning(f"Invalid allele frequency: {mutation['allele_frequency']}")
            return False
        
        return True
    
    def _extract_cancer_type_from_study(self, study_id: str) -> str:
        """Extract cancer type from study ID"""
        # Common patterns in study IDs
        if 'brca' in study_id.lower():
            return 'Breast'
        elif 'luad' in study_id.lower() or 'lusc' in study_id.lower():
            return 'NSCLC'
        elif 'coad' in study_id.lower() or 'read' in study_id.lower():
            return 'Colorectal'
        elif 'paad' in study_id.lower():
            return 'Pancreatic'
        elif 'skcm' in study_id.lower():
            return 'Melanoma'
        elif 'gbm' in study_id.lower():
            return 'Glioblastoma'
        else:
            # Try to extract from study ID parts
            parts = study_id.split('_')
            if parts:
                return parts[0].upper()
            return study_id
    
    def _parse_cds_change(self, cds_change: str) -> tuple:
        """Parse CDS change to extract reference and alternate alleles"""
        if not cds_change:
            return '', ''
        
        # Handle format like c.35G>A
        import re
        match = re.search(r'c\.\d+([ACGT]+)>([ACGT]+)', cds_change)
        if match:
            return match.group(1), match.group(2)
        
        return '', ''
    
    def _map_cosmic_cancer_type(self, histology: str, site: str) -> str:
        """Map COSMIC histology and site to standard cancer type"""
        histology_lower = histology.lower() if histology else ''
        site_lower = site.lower() if site else ''
        
        if 'lung' in site_lower:
            if 'small cell' in histology_lower:
                return 'SCLC'
            else:
                return 'NSCLC'
        elif 'breast' in site_lower:
            return 'Breast'
        elif 'colon' in site_lower or 'rectum' in site_lower:
            return 'Colorectal'
        elif 'skin' in site_lower and 'melanoma' in histology_lower:
            return 'Melanoma'
        elif 'pancreas' in site_lower:
            return 'Pancreatic'
        elif 'liver' in site_lower:
            return 'Liver'
        elif 'ovary' in site_lower:
            return 'Ovarian'
        elif 'brain' in site_lower:
            return 'Glioblastoma'
        else:
            return histology or site
    
    def _extract_chromosome(self, genome_position: str) -> str:
        """Extract chromosome from genome position string"""
        if not genome_position:
            return ''
        
        # Format might be like "17:7577121-7577121"
        parts = genome_position.split(':')
        if parts:
            return parts[0]
        return ''
    
    def _extract_position(self, genome_position: str) -> Optional[int]:
        """Extract position from genome position string"""
        if not genome_position:
            return None
        
        # Format might be like "17:7577121-7577121"
        import re
        match = re.search(r':(\d+)', genome_position)
        if match:
            return int(match.group(1))
        return None
    
    def _infer_variant_type(self, ref: str, alt: str) -> str:
        """Infer variant type from reference and alternate alleles"""
        if not ref or not alt:
            return 'unknown'
        
        ref_len = len(ref)
        alt_len = len(alt)
        
        if ref_len == alt_len:
            if ref_len == 1:
                return 'SNP'
            else:
                return 'MNP'
        elif ref_len > alt_len:
            return 'deletion'
        else:
            return 'insertion'
    
    def save_silver_data(self, mutations: List[Dict], source: str) -> Dict:
        """
        Save standardized mutations to Silver layer
        
        Args:
            mutations: List of standardized mutations
            source: Data source name
            
        Returns:
            Metadata about saved data
        """
        timestamp = datetime.utcnow()
        
        # Create directory
        mutations_dir = os.path.join(self.silver_path, 'mutations')
        os.makedirs(mutations_dir, exist_ok=True)
        
        # Save data
        filename = f"{source}_mutations_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(mutations_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(mutations, f, indent=2, default=str)
        
        metadata = {
            'source': source,
            'record_count': len(mutations),
            'timestamp': timestamp.isoformat(),
            'file': filepath
        }
        
        logger.info(f"Saved {len(mutations)} standardized mutations to {filepath}")
        return metadata