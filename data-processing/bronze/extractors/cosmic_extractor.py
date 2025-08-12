"""COSMIC NIH data extractor for Bronze layer"""

import requests
from typing import List, Dict, Any, Optional
import logging
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class CosmicExtractor(BaseExtractor):
    """Extract mutation data from COSMIC via NIH Clinical Tables API"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.base_url = self.config['sources']['cosmic_nih']['base_url']
        self.max_results = self.config['sources']['cosmic_nih']['max_results']
        self.session = requests.Session()
        
    def extract(self, genes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract mutation data from COSMIC NIH API
        
        Args:
            genes: List of gene symbols to extract
            
        Returns:
            Dictionary containing raw mutation data
        """
        # Use configured genes if not provided
        if not genes:
            genes = (self.config['target_genes']['oncogenes'] + 
                    self.config['target_genes']['tumor_suppressors'])
        
        raw_data = {
            'mutations': [],
            'genes': genes,
            'source': 'cosmic_nih'
        }
        
        # Extract mutations for each gene
        for gene in genes:
            logger.info(f"Extracting COSMIC data for gene: {gene}")
            
            gene_mutations = self._get_mutations_for_gene(gene)
            if gene_mutations:
                raw_data['mutations'].extend(gene_mutations)
            
            # Apply rate limiting
            self.rate_limit('cosmic_nih')
        
        # Save raw data
        metadata = self.save_raw(raw_data, 'cosmic')
        logger.info(f"COSMIC extraction complete. Total mutations: {len(raw_data['mutations'])}")
        
        return raw_data
    
    def _get_mutations_for_gene(self, gene: str) -> List[Dict]:
        """
        Get mutations for a specific gene from COSMIC
        
        Args:
            gene: Gene symbol
            
        Returns:
            List of mutation records
        """
        params = {
            'terms': gene,
            'maxList': self.max_results,
            'df': 'GeneName,MutationAA,MutationCDS,PrimaryHistology,PrimarySite'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse COSMIC response format
            # The response is an array: [total_count, field_list, field_names, data_rows]
            if len(data) >= 4 and data[0] > 0:
                return self._parse_cosmic_response(data, gene)
            else:
                logger.info(f"No COSMIC data found for gene: {gene}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"Failed to fetch COSMIC data for gene {gene}")
            return []
    
    def _parse_cosmic_response(self, response_data: List, gene: str) -> List[Dict]:
        """
        Parse COSMIC API response format
        
        Args:
            response_data: Raw response from COSMIC API
            gene: Gene symbol for reference
            
        Returns:
            List of parsed mutation records
        """
        mutations = []
        
        try:
            total_count = response_data[0]
            field_info = response_data[1]  # Field metadata
            field_names = response_data[2]  # Field names
            data_rows = response_data[3] if len(response_data) > 3 else []
            
            logger.info(f"Parsing {len(data_rows)} COSMIC records for {gene}")
            
            # Map field indices
            field_indices = {name: i for i, name in enumerate(field_names)}
            
            # Parse each data row
            for row in data_rows:
                mutation = {
                    'gene': gene,
                    'source': 'cosmic'
                }
                
                # Extract available fields
                if 'MutationID' in field_indices:
                    mutation['mutation_id'] = row[field_indices['MutationID']]
                
                if 'GeneName' in field_indices:
                    mutation['gene_name'] = row[field_indices['GeneName']]
                
                if 'MutationAA' in field_indices:
                    mutation['protein_change'] = row[field_indices['MutationAA']]
                
                if 'MutationCDS' in field_indices:
                    mutation['cds_change'] = row[field_indices['MutationCDS']]
                
                if 'PrimaryHistology' in field_indices:
                    mutation['primary_histology'] = row[field_indices['PrimaryHistology']]
                
                if 'PrimarySite' in field_indices:
                    mutation['primary_site'] = row[field_indices['PrimarySite']]
                
                if 'MutationGenomePosition' in field_indices:
                    mutation['genome_position'] = row[field_indices['MutationGenomePosition']]
                
                # Only add if we have meaningful data
                if mutation.get('protein_change') or mutation.get('cds_change'):
                    mutations.append(mutation)
            
            logger.info(f"Successfully parsed {len(mutations)} mutations for {gene}")
            
        except (IndexError, KeyError) as e:
            self.handle_error(e, f"Failed to parse COSMIC response for gene {gene}")
        
        return mutations
    
    def get_detailed_mutation(self, mutation_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific mutation
        
        Args:
            mutation_id: COSMIC mutation ID
            
        Returns:
            Detailed mutation record or None
        """
        params = {
            'terms': mutation_id,
            'maxList': 1
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if len(data) >= 4 and data[0] > 0:
                mutations = self._parse_cosmic_response(data, '')
                return mutations[0] if mutations else None
            
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"Failed to fetch mutation {mutation_id}")
            
        return None