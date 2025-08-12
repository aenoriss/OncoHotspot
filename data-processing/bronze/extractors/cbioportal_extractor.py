"""cBioPortal data extractor for Bronze layer"""

import requests
from typing import List, Dict, Any, Optional
import logging
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class CBioPortalExtractor(BaseExtractor):
    """Extract mutation data from cBioPortal API"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.base_url = self.config['sources']['cbioportal']['base_url']
        self.session = requests.Session()
        self._load_clinically_actionable_genes()
        
    def extract(self, genes: Optional[List[str]] = None, 
                studies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract mutation data from cBioPortal
        
        Args:
            genes: List of gene symbols to extract
            studies: List of study IDs to extract from
            
        Returns:
            Dictionary containing raw mutation data
        """
        # Use configured genes and studies if not provided
        if not genes:
            # Use clinically actionable genes if available, otherwise fall back to config
            if hasattr(self, 'clinically_actionable_genes'):
                genes = self.clinically_actionable_genes
            else:
                genes = (self.config['target_genes']['oncogenes'] + 
                        self.config['target_genes']['tumor_suppressors'])
        
        if not studies:
            studies = self.config['target_studies']['cbioportal']
        
        raw_data = {
            'mutations': [],
            'studies': [],
            'genes': [],
            'clinical_samples': [],
            'study_sample_counts': {}  # Add mapping of study_id -> total sample count
        }
        
        # First, get gene information
        logger.info("Fetching gene information...")
        gene_data = self._get_genes(genes)
        raw_data['genes'] = gene_data
        
        # Create gene symbol to Entrez ID mapping
        gene_id_map = {g['hugoGeneSymbol']: g['entrezGeneId'] 
                      for g in gene_data if 'entrezGeneId' in g}
        
        if not gene_id_map:
            logger.error("Failed to fetch gene information - gene_id_map is empty")
            logger.error("Cannot proceed with mutation extraction without gene IDs")
            return raw_data
        
        # Get study information
        logger.info("Fetching study information...")
        for study_id in studies:
            study_info = self._get_study_info(study_id)
            if study_info:
                raw_data['studies'].append(study_info)
                # Store actual sample count from study
                if 'allSampleCount' in study_info:
                    raw_data['study_sample_counts'][study_id] = study_info['allSampleCount']
                    logger.info(f"Study {study_id} has {study_info['allSampleCount']} total samples")
        
        # Extract mutations for each study
        for study_id in studies:
            logger.info(f"Extracting mutations from study: {study_id}")
            
            # Get molecular profile ID (usually study_id + "_mutations")
            profile_id = f"{study_id}_mutations"
            
            # Get mutations for all genes in this study
            mutations = self._get_mutations_by_study(study_id, profile_id, gene_id_map)
            raw_data['mutations'].extend(mutations)
            
            # Get sample clinical data
            clinical_data = self._get_clinical_data(study_id)
            if clinical_data:
                raw_data['clinical_samples'].extend(clinical_data)
            
            # Apply rate limiting
            self.rate_limit('cbioportal')
        
        # Save raw data
        metadata = self.save_raw(raw_data, 'cbioportal')
        logger.info(f"Extraction complete. Checksum: {metadata['checksum']}")
        
        return raw_data
    
    def _get_genes(self, gene_symbols: List[str]) -> List[Dict]:
        """Get gene information from cBioPortal"""
        if not gene_symbols:
            logger.warning("No gene symbols provided to _get_genes")
            return []
            
        all_genes = []
        logger.info(f"Fetching information for {len(gene_symbols)} genes")
        
        # Fetch genes one by one using keyword search
        # This is more reliable than bulk endpoints
        endpoint = f"{self.base_url}/genes"
        
        for i, gene_symbol in enumerate(gene_symbols):
            try:
                response = self.session.get(
                    endpoint,
                    params={
                        'keyword': gene_symbol,
                        'projection': 'DETAILED'
                    }
                )
                response.raise_for_status()
                genes = response.json()
                
                # Find exact match
                matched_gene = None
                for gene in genes:
                    if gene.get('hugoGeneSymbol', '').upper() == gene_symbol.upper():
                        matched_gene = gene
                        break
                
                if matched_gene:
                    all_genes.append(matched_gene)
                    if (i + 1) % 10 == 0:
                        logger.info(f"Fetched {i + 1}/{len(gene_symbols)} genes")
                else:
                    logger.debug(f"Gene {gene_symbol} not found in cBioPortal")
                    
                # Rate limiting - be nice to the API
                if (i + 1) % 20 == 0:
                    import time
                    time.sleep(0.5)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch gene {gene_symbol}: {e}")
                continue
        
        logger.info(f"Total genes fetched: {len(all_genes)} (requested: {len(gene_symbols)})")
        return all_genes
    
    def _load_clinically_actionable_genes(self):
        """Load 150+ clinically actionable genes from config"""
        import yaml
        import os
        
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config',
            'clinically_actionable_genes.yaml'
        )
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            genes = []
            for category in config['clinically_actionable_genes'].values():
                if isinstance(category, list):
                    genes.extend(category)
            
            # Remove duplicates
            self.clinically_actionable_genes = list(set(genes))
            logger.info(f"Loaded {len(self.clinically_actionable_genes)} clinically actionable genes")
            
        except FileNotFoundError:
            logger.warning("Clinically actionable genes config not found, using default genes")
            self.clinically_actionable_genes = []
    
    def _get_study_info(self, study_id: str) -> Optional[Dict]:
        """Get study information"""
        endpoint = f"{self.base_url}/studies/{study_id}"
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"Failed to fetch study {study_id}")
            return None
    
    def _get_mutations_by_study(self, study_id: str, profile_id: str, 
                               gene_id_map: Dict[str, int]) -> List[Dict]:
        """Get mutations for multiple genes in a study"""
        endpoint = f"{self.base_url}/molecular-profiles/{profile_id}/mutations/fetch"
        
        mutations = []
        gene_ids = list(gene_id_map.values())
        
        if not gene_ids:
            logger.warning(f"No gene IDs available for study {study_id}, skipping mutation extraction")
            return mutations
        
        # Get all samples in the study
        sample_ids = self._get_sample_ids(study_id)
        if not sample_ids:
            return mutations
        
        # Limit samples for large studies to speed up extraction
        max_samples = 500  # Process max 500 samples per study
        if len(sample_ids) > max_samples:
            logger.info(f"Study {study_id} has {len(sample_ids)} samples, limiting to {max_samples}")
            sample_ids = sample_ids[:max_samples]
        
        # Batch process samples to avoid API limits
        batch_size = 100
        for i in range(0, len(sample_ids), batch_size):
            batch_samples = sample_ids[i:i+batch_size]
            
            try:
                response = self.session.post(
                    endpoint,
                    json={
                        'entrezGeneIds': gene_ids,
                        'sampleIds': batch_samples
                    },
                    params={'projection': 'DETAILED'}
                )
                response.raise_for_status()
                batch_mutations = response.json()
                
                # Add study context to each mutation
                for mutation in batch_mutations:
                    mutation['studyId'] = study_id
                    mutations.append(mutation)
                
                logger.info(f"Fetched {len(batch_mutations)} mutations from batch {i//batch_size + 1}")
                
            except requests.exceptions.RequestException as e:
                self.handle_error(e, f"Failed to fetch mutations for study {study_id}")
            
            # Rate limiting
            self.rate_limit('cbioportal')
        
        return mutations
    
    def _get_sample_ids(self, study_id: str) -> List[str]:
        """Get all sample IDs for a study"""
        endpoint = f"{self.base_url}/studies/{study_id}/samples"
        
        try:
            response = self.session.get(
                endpoint,
                params={'projection': 'ID'}
            )
            response.raise_for_status()
            samples = response.json()
            return [s['sampleId'] for s in samples]
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"Failed to fetch samples for study {study_id}")
            return []
    
    def _get_clinical_data(self, study_id: str) -> List[Dict]:
        """Get clinical data for samples in a study"""
        endpoint = f"{self.base_url}/studies/{study_id}/clinical-data"
        
        try:
            response = self.session.get(
                endpoint,
                params={
                    'clinicalDataType': 'SAMPLE',
                    'projection': 'DETAILED'
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"Failed to fetch clinical data for study {study_id}")
            return []