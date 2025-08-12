"""DGIdb (Drug-Gene Interaction Database) extractor for therapeutic data"""

import requests
from typing import List, Dict, Any, Optional
import logging
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class DGIdbExtractor(BaseExtractor):
    """Extract drug-gene interaction data from DGIdb API"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.base_url = "https://dgidb.org/api/v2"
        self.session = requests.Session()
        
    def extract(self, genes: Optional[List[str]] = None, use_local: bool = False) -> Dict[str, Any]:
        """
        Extract therapeutic data from DGIdb
        
        Args:
            genes: List of gene symbols to extract therapeutics for
            
        Returns:
            Dictionary containing drug-gene interactions
        """
        # Use configured genes if not provided
        if not genes:
            # Load from clinically actionable genes config
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
            except FileNotFoundError:
                # Fallback to original gene list
                genes = (self.config['target_genes']['oncogenes'] + 
                        self.config['target_genes']['tumor_suppressors'])
        
        raw_data = {
            'interactions': [],
            'drugs': [],
            'genes': [],
            'sources': []
        }
        
        # Try to use local therapeutic data first
        if use_local:
            local_data = self._load_local_therapeutic_data()
            if local_data:
                logger.info("Using local therapeutic data")
                raw_data = local_data
            else:
                logger.info("No local data found, trying API")
                use_local = False
        
        # If not using local or local failed, try API
        if not use_local:
            # Process genes in batches
            batch_size = 50
            for i in range(0, len(genes), batch_size):
                batch = genes[i:i+batch_size]
                logger.info(f"Extracting drug interactions for batch {i//batch_size + 1} ({len(batch)} genes)")
                
                interactions = self._get_interactions(batch)
                if interactions:
                    raw_data['interactions'].extend(interactions)
                
                # Apply rate limiting
                self.rate_limit('dgidb')
        
        # Extract unique drugs and sources
        raw_data['drugs'] = self._extract_unique_drugs(raw_data['interactions'])
        raw_data['sources'] = self._extract_sources(raw_data['interactions'])
        raw_data['genes'] = genes
        
        # Save raw data
        metadata = self.save_raw(raw_data, 'dgidb')
        logger.info(f"DGIdb extraction complete. Found {len(raw_data['interactions'])} interactions")
        
        return raw_data
    
    def _get_interactions(self, genes: List[str]) -> List[Dict]:
        """
        Get drug-gene interactions using GraphQL API
        
        Args:
            genes: List of gene symbols
            
        Returns:
            List of interaction records
        """
        graphql_url = "https://dgidb.org/api/graphql"
        
        # Create GraphQL query for multiple genes
        gene_names = ', '.join([f'"{gene}"' for gene in genes])
        query = f'''
        {{
          genes(names: [{gene_names}]) {{
            nodes {{
              name
              interactions {{
                drug {{
                  name
                  approved
                  conceptId
                }}
                interactionTypes {{
                  type
                }}
                sources {{
                  sourceDbName
                }}
                publications {{
                  pmid
                }}
              }}
            }}
          }}
        }}
        '''
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = self.session.post(
                graphql_url, 
                json={'query': query}, 
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return []
            
            interactions = []
            
            # Parse GraphQL response
            genes_data = data.get('data', {}).get('genes', {}).get('nodes', [])
            
            for gene_data in genes_data:
                gene_name = gene_data.get('name')
                
                for interaction in gene_data.get('interactions', []):
                    drug = interaction.get('drug', {})
                    interaction_types = interaction.get('interactionTypes', [])
                    sources = interaction.get('sources', [])
                    publications = interaction.get('publications', [])
                    
                    interaction_record = {
                        'gene_name': gene_name,
                        'gene_categories': ['cancer gene'],  # Default category
                        'drug_name': drug.get('name'),
                        'drug_concept_id': drug.get('conceptId'),
                        'interaction_types': [it.get('type') for it in interaction_types if it.get('type')],
                        'interaction_claim_source': sources[0].get('sourceDbName') if sources else 'DGIdb',
                        'interaction_id': f"{gene_name}_{drug.get('name', '')}",
                        'pmids': [pub.get('pmid') for pub in publications if pub.get('pmid')],
                        'drug_attributes': {
                            'fda_approved': drug.get('approved', False),
                            'anti-neoplastic': True,  # Default for cancer context
                            'targeted_therapy': True
                        },
                        'sources': [src.get('sourceDbName') for src in sources if src.get('sourceDbName')]
                    }
                    interactions.append(interaction_record)
            
            logger.info(f"Retrieved {len(interactions)} interactions for {len(genes)} genes")
            return interactions
            
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"Failed to fetch interactions via GraphQL")
            return []
    
    def _parse_drug_attributes(self, interaction: Dict) -> Dict:
        """Parse drug attributes from interaction"""
        attributes = {}
        
        drug_attrs = interaction.get('drugAttributes', {})
        
        # Common attributes to extract
        important_attrs = [
            'Approved',
            'FDA Approved',
            'Immunotherapy',
            'Anti-neoplastic',
            'Targeted Therapy',
            'Chemotherapy'
        ]
        
        for attr in important_attrs:
            if attr in drug_attrs:
                attributes[attr.lower().replace(' ', '_')] = drug_attrs[attr]
        
        return attributes
    
    def _extract_unique_drugs(self, interactions: List[Dict]) -> List[Dict]:
        """Extract unique drugs from interactions"""
        drugs = {}
        
        for interaction in interactions:
            drug_name = interaction.get('drug_name')
            if drug_name and drug_name not in drugs:
                drugs[drug_name] = {
                    'drug_name': drug_name,
                    'drug_concept_id': interaction.get('drug_concept_id'),
                    'attributes': interaction.get('drug_attributes', {}),
                    'targeted_genes': []
                }
            
            if drug_name:
                gene = interaction.get('gene_name')
                if gene and gene not in drugs[drug_name]['targeted_genes']:
                    drugs[drug_name]['targeted_genes'].append(gene)
        
        return list(drugs.values())
    
    def _extract_sources(self, interactions: List[Dict]) -> List[str]:
        """Extract unique data sources"""
        sources = set()
        
        for interaction in interactions:
            if interaction.get('interaction_claim_source'):
                sources.add(interaction['interaction_claim_source'])
            for source in interaction.get('sources', []):
                sources.add(source)
        
        return sorted(list(sources))
    
    def _load_local_therapeutic_data(self) -> Optional[Dict]:
        """Load local therapeutic data if available"""
        import os
        import json
        import glob
        
        # Look for manual therapeutic data files
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'bronze', 'data', 'dgidb'
        )
        
        if not os.path.exists(data_dir):
            return None
        
        # Find the most recent manual file
        manual_files = glob.glob(os.path.join(data_dir, 'dgidb_manual_*.json'))
        if not manual_files:
            return None
        
        # Sort by modification time and get the newest
        latest_file = max(manual_files, key=os.path.getmtime)
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded therapeutic data from {latest_file}")
                return data
        except Exception as e:
            logger.error(f"Failed to load local therapeutic data: {e}")
            return None
    
    def get_drug_details(self, drug_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific drug
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Drug details or None
        """
        endpoint = f"{self.base_url}/drugs.json"
        params = {'drugs': drug_name}
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('matchedTerms'):
                return data['matchedTerms'][0]
            
        except requests.exceptions.RequestException as e:
            self.handle_error(e, f"Failed to fetch drug details for {drug_name}")
        
        return None
    
    def get_categories_for_genes(self, genes: List[str]) -> Dict[str, List[str]]:
        """
        Get categories (e.g., kinase, tumor suppressor) for genes
        
        Args:
            genes: List of gene symbols
            
        Returns:
            Dictionary mapping genes to their categories
        """
        endpoint = f"{self.base_url}/genes.json"
        params = {'genes': ','.join(genes)}
        
        categories = {}
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            for matched_term in data.get('matchedTerms', []):
                gene_name = matched_term.get('geneName')
                gene_categories = matched_term.get('geneCategories', [])
                categories[gene_name] = gene_categories
            
        except requests.exceptions.RequestException as e:
            self.handle_error(e, "Failed to fetch gene categories")
        
        return categories