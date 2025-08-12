"""Therapeutic data standardizer for Silver layer"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TherapeuticStandardizer:
    """Standardize therapeutic data from various sources"""
    
    def __init__(self):
        self.silver_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
    
    def standardize(self, therapeutics: List[Dict], source: str = 'generic') -> List[Dict]:
        """
        Main standardization method called by pipeline
        
        Args:
            therapeutics: List of therapeutic records
            source: Source system (civic, opentargets, dgidb)
            
        Returns:
            List of standardized therapeutic records
        """
        logger.info(f"Standardizing {len(therapeutics)} therapeutics from {source}")
        
        if source == 'civic':
            return self.standardize_civic({'therapies': therapeutics})
        elif source == 'opentargets':
            return self.standardize_opentargets({'drugs': therapeutics})
        elif source == 'dgidb':
            return self.standardize_dgidb({'interactions': therapeutics})
        else:
            # Generic standardization
            return self._standardize_generic(therapeutics)
    
    def _standardize_generic(self, therapeutics: List[Dict]) -> List[Dict]:
        """Generic therapeutic standardization"""
        standardized = []
        
        for therapeutic in therapeutics:
            try:
                std = {
                    'name': therapeutic.get('name', therapeutic.get('drug_name', '')),
                    'target_gene': therapeutic.get('target_gene', therapeutic.get('target_symbol', '')),
                    'mechanism': therapeutic.get('mechanism', therapeutic.get('mechanismOfAction', '')),
                    'indication': therapeutic.get('indication', ''),
                    'status': therapeutic.get('status', 'investigational'),
                    'source': therapeutic.get('source', 'unknown'),
                    'drug_id': therapeutic.get('id', therapeutic.get('drug_id', '')),
                    'max_phase': therapeutic.get('max_phase', therapeutic.get('maximumClinicalTrialPhase', 0))
                }
                
                if self._validate_therapeutic(std):
                    standardized.append(std)
                    
            except Exception as e:
                logger.error(f"Error in generic standardization: {e}")
        
        return standardized
    
    def standardize_civic(self, bronze_data: Dict[str, Any]) -> List[Dict]:
        """
        Standardize CIViC therapeutic data
        
        Args:
            bronze_data: Raw data from CIViC extractor
            
        Returns:
            List of standardized therapeutic records
        """
        silver_therapeutics = []
        
        for therapy in bronze_data.get('therapies', []):
            try:
                standardized = {
                    'name': therapy.get('name', ''),
                    'target_gene': '',  # CIViC therapies don't have direct gene targets
                    'mechanism': '',
                    'indication': '',
                    'status': 'investigational',
                    'source': 'civic',
                    'drug_id': therapy.get('id', ''),
                    'aliases': therapy.get('therapyAliases', []),
                    'ncit_id': therapy.get('ncitId', '')
                }
                
                if self._validate_therapeutic(standardized):
                    silver_therapeutics.append(standardized)
                    
            except Exception as e:
                logger.error(f"Error standardizing CIViC therapeutic: {e}")
        
        logger.info(f"Standardized {len(silver_therapeutics)} CIViC therapeutics")
        return silver_therapeutics
    
    def standardize_opentargets(self, bronze_data: Dict[str, Any]) -> List[Dict]:
        """
        Standardize OpenTargets drug data
        
        Args:
            bronze_data: Raw data from OpenTargets extractor
            
        Returns:
            List of standardized therapeutic records
        """
        silver_therapeutics = []
        
        for drug in bronze_data.get('drugs', []):
            try:
                standardized = {
                    'name': drug.get('name', ''),
                    'target_gene': '',  # Will be filled from interactions
                    'mechanism': '',
                    'indication': '',
                    'status': 'approved' if drug.get('hasBeenWithdrawn') == False else 'withdrawn',
                    'source': 'opentargets',
                    'drug_id': drug.get('id', ''),
                    'drug_type': drug.get('drugType', ''),
                    'max_phase': drug.get('maximumClinicalTrialPhase', 0)
                }
                
                if self._validate_therapeutic(standardized):
                    silver_therapeutics.append(standardized)
                    
            except Exception as e:
                logger.error(f"Error standardizing OpenTargets drug: {e}")
        
        logger.info(f"Standardized {len(silver_therapeutics)} OpenTargets drugs")
        return silver_therapeutics
        
    def standardize_dgidb(self, bronze_data: Dict[str, Any]) -> List[Dict]:
        """
        Standardize DGIdb therapeutic data
        
        Args:
            bronze_data: Raw data from DGIdb extractor
            
        Returns:
            List of standardized therapeutic records
        """
        silver_therapeutics = []
        
        for interaction in bronze_data.get('interactions', []):
            try:
                standardized = self._standardize_dgidb_interaction(interaction)
                if standardized and self._validate_therapeutic(standardized):
                    silver_therapeutics.append(standardized)
            except Exception as e:
                logger.error(f"Error standardizing therapeutic: {e}")
                continue
        
        logger.info(f"Standardized {len(silver_therapeutics)} DGIdb therapeutics")
        return silver_therapeutics
    
    def _standardize_dgidb_interaction(self, interaction: Dict) -> Optional[Dict]:
        """Standardize a single DGIdb interaction record"""
        
        drug_attributes = interaction.get('drug_attributes', {})
        
        standardized = {
            # Gene information
            'gene_symbol': interaction.get('gene_name', '').upper(),
            'gene_categories': interaction.get('gene_categories', []),
            
            # Drug information
            'drug_name': self._standardize_drug_name(interaction.get('drug_name', '')),
            'drug_concept_id': interaction.get('drug_concept_id'),
            
            # Interaction details
            'interaction_types': interaction.get('interaction_types', []),
            'interaction_claim_source': interaction.get('interaction_claim_source'),
            'interaction_id': interaction.get('interaction_id'),
            
            # Clinical information
            'fda_approved': drug_attributes.get('fda_approved', False),
            'anti_neoplastic': drug_attributes.get('anti-neoplastic', False),
            'immunotherapy': drug_attributes.get('immunotherapy', False),
            'targeted_therapy': drug_attributes.get('targeted_therapy', False),
            'chemotherapy': drug_attributes.get('chemotherapy', False),
            
            # Evidence
            'pmids': interaction.get('pmids', []),
            'sources': interaction.get('sources', []),
            
            # Metadata
            'source': 'dgidb',
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        # Infer mechanism of action
        standardized['mechanism_of_action'] = self._infer_mechanism(
            standardized['interaction_types'],
            standardized['gene_categories']
        )
        
        # Classify drug type
        standardized['drug_type'] = self._classify_drug_type(standardized)
        
        return standardized
    
    def _standardize_drug_name(self, drug_name: str) -> str:
        """Standardize drug naming conventions"""
        if not drug_name:
            return ''
        
        # Common replacements
        replacements = {
            'TRASTUZUMAB': 'Trastuzumab',
            'OSIMERTINIB': 'Osimertinib',
            'ERLOTINIB': 'Erlotinib',
            'GEFITINIB': 'Gefitinib',
            'CRIZOTINIB': 'Crizotinib',
            'ALECTINIB': 'Alectinib',
            'VEMURAFENIB': 'Vemurafenib',
            'DABRAFENIB': 'Dabrafenib',
            'IMATINIB': 'Imatinib',
            'SUNITINIB': 'Sunitinib',
            'SORAFENIB': 'Sorafenib',
            'REGORAFENIB': 'Regorafenib',
            'PEMBROLIZUMAB': 'Pembrolizumab',
            'NIVOLUMAB': 'Nivolumab',
            'ATEZOLIZUMAB': 'Atezolizumab'
        }
        
        # Check for exact match (case-insensitive)
        upper_name = drug_name.upper()
        if upper_name in replacements:
            return replacements[upper_name]
        
        # Otherwise, capitalize first letter of each word
        return drug_name.title()
    
    def _infer_mechanism(self, interaction_types: List[str], gene_categories: List[str]) -> str:
        """Infer mechanism of action from interaction types and gene categories"""
        
        if not interaction_types:
            return 'Unknown'
        
        # Direct mappings
        if 'inhibitor' in interaction_types:
            if 'kinase' in gene_categories:
                return 'Kinase inhibitor'
            elif 'phosphatase' in gene_categories:
                return 'Phosphatase inhibitor'
            else:
                return 'Inhibitor'
        
        if 'antagonist' in interaction_types:
            if 'receptor' in gene_categories:
                return 'Receptor antagonist'
            else:
                return 'Antagonist'
        
        if 'agonist' in interaction_types:
            return 'Agonist'
        
        if 'blocker' in interaction_types:
            return 'Blocker'
        
        if 'activator' in interaction_types:
            return 'Activator'
        
        if 'antibody' in interaction_types:
            return 'Monoclonal antibody'
        
        return 'Other'
    
    def _classify_drug_type(self, therapeutic: Dict) -> str:
        """Classify the type of drug"""
        
        if therapeutic.get('immunotherapy'):
            return 'Immunotherapy'
        elif therapeutic.get('targeted_therapy'):
            return 'Targeted therapy'
        elif therapeutic.get('chemotherapy'):
            return 'Chemotherapy'
        elif 'antibody' in therapeutic.get('mechanism_of_action', '').lower():
            return 'Monoclonal antibody'
        elif 'inhibitor' in therapeutic.get('mechanism_of_action', '').lower():
            return 'Small molecule inhibitor'
        else:
            return 'Other'
    
    def _validate_therapeutic(self, therapeutic: Dict) -> bool:
        """
        Validate that a therapeutic record has required fields
        
        Args:
            therapeutic: Standardized therapeutic record
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['gene_symbol', 'drug_name']
        
        for field in required_fields:
            if not therapeutic.get(field):
                logger.debug(f"Missing required field: {field}")
                return False
        
        return True
    
    def merge_therapeutic_sources(self, *sources: List[Dict]) -> List[Dict]:
        """
        Merge therapeutic data from multiple sources
        
        Args:
            sources: Multiple lists of standardized therapeutics
            
        Returns:
            Merged and deduplicated list
        """
        merged = {}
        
        for source_list in sources:
            for therapeutic in source_list:
                # Create unique key
                key = (
                    therapeutic.get('gene_symbol'),
                    therapeutic.get('drug_name')
                )
                
                if key not in merged:
                    merged[key] = therapeutic
                else:
                    # Merge information from multiple sources
                    existing = merged[key]
                    
                    # Combine sources
                    existing_sources = set(existing.get('sources', []))
                    new_sources = set(therapeutic.get('sources', []))
                    existing['sources'] = list(existing_sources | new_sources)
                    
                    # Combine PMIDs
                    existing_pmids = set(existing.get('pmids', []))
                    new_pmids = set(therapeutic.get('pmids', []))
                    existing['pmids'] = list(existing_pmids | new_pmids)
                    
                    # Update FDA approval status (true if any source says true)
                    existing['fda_approved'] = existing.get('fda_approved') or therapeutic.get('fda_approved')
        
        return list(merged.values())
    
    def save_silver_therapeutics(self, therapeutics: List[Dict], source: str) -> Dict:
        """
        Save standardized therapeutics to Silver layer
        
        Args:
            therapeutics: List of standardized therapeutics
            source: Data source name
            
        Returns:
            Metadata about saved data
        """
        timestamp = datetime.utcnow()
        
        # Create directory
        therapeutics_dir = os.path.join(self.silver_path, 'therapeutics')
        os.makedirs(therapeutics_dir, exist_ok=True)
        
        # Save data
        filename = f"{source}_therapeutics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(therapeutics_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(therapeutics, f, indent=2, default=str)
        
        metadata = {
            'source': source,
            'record_count': len(therapeutics),
            'timestamp': timestamp.isoformat(),
            'file': filepath
        }
        
        logger.info(f"Saved {len(therapeutics)} standardized therapeutics to {filepath}")
        return metadata