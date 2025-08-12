"""Cancer type standardization mapper"""

import os
import yaml
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CancerTypeMapper:
    """Map cancer types from various sources to standardized names"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize cancer type mapper
        
        Args:
            config_path: Path to cancer type mappings configuration
        """
        self.mappings = self._load_mappings(config_path)
        self._build_reverse_mappings()
        
    def _load_mappings(self, config_path: Optional[str]) -> Dict[str, str]:
        """Load cancer type mappings from configuration"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'cancer_types.yaml'
            )
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('cancer_type_mappings', {})
        except FileNotFoundError:
            logger.warning(f"Cancer type config not found at {config_path}, using defaults")
            return self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict[str, str]:
        """Get default cancer type mappings"""
        return {
            # Lung cancers
            'LUAD': 'NSCLC',
            'LUSC': 'NSCLC',
            'Lung Adenocarcinoma': 'NSCLC',
            'Lung Squamous Cell Carcinoma': 'NSCLC',
            'Non-Small Cell Lung Cancer': 'NSCLC',
            'SCLC': 'SCLC',
            'Small Cell Lung Cancer': 'SCLC',
            
            # Breast cancers
            'BRCA': 'Breast',
            'Breast Invasive Carcinoma': 'Breast',
            'Breast Cancer': 'Breast',
            
            # Colorectal cancers
            'COAD': 'Colorectal',
            'READ': 'Colorectal',
            'COADREAD': 'Colorectal',
            'Colon Adenocarcinoma': 'Colorectal',
            'Rectum Adenocarcinoma': 'Colorectal',
            
            # Skin cancers
            'SKCM': 'Melanoma',
            'Skin Cutaneous Melanoma': 'Melanoma',
            'Cutaneous Melanoma': 'Melanoma',
            
            # Pancreatic cancers
            'PAAD': 'Pancreatic',
            'Pancreatic Adenocarcinoma': 'Pancreatic',
            'Pancreatic Cancer': 'Pancreatic',
            
            # Other major types
            'GBM': 'Glioblastoma',
            'Glioblastoma Multiforme': 'Glioblastoma',
            'OV': 'Ovarian',
            'Ovarian Serous Cystadenocarcinoma': 'Ovarian',
            'LIHC': 'Liver',
            'Liver Hepatocellular Carcinoma': 'Liver',
            'KIRC': 'Kidney',
            'Kidney Renal Clear Cell Carcinoma': 'Kidney',
            'BLCA': 'Bladder',
            'Bladder Urothelial Carcinoma': 'Bladder',
            'PRAD': 'Prostate',
            'Prostate Adenocarcinoma': 'Prostate',
            'STAD': 'Gastric',
            'Stomach Adenocarcinoma': 'Gastric',
            'HNSC': 'Head and Neck',
            'Head and Neck Squamous Cell Carcinoma': 'Head and Neck',
            'THCA': 'Thyroid',
            'Thyroid Carcinoma': 'Thyroid',
            'LAML': 'AML',
            'Acute Myeloid Leukemia': 'AML'
        }
    
    def _build_reverse_mappings(self):
        """Build reverse mappings for lookup"""
        self.reverse_mappings = {}
        for source, standard in self.mappings.items():
            if standard not in self.reverse_mappings:
                self.reverse_mappings[standard] = []
            self.reverse_mappings[standard].append(source)
    
    def map_to_standard(self, cancer_type: str) -> str:
        """
        Map a cancer type to its standardized name
        
        Args:
            cancer_type: Original cancer type name
            
        Returns:
            Standardized cancer type name
        """
        if not cancer_type:
            return 'Unknown'
        
        # Direct mapping
        if cancer_type in self.mappings:
            return self.mappings[cancer_type]
        
        # Case-insensitive search
        cancer_type_lower = cancer_type.lower()
        for original, standard in self.mappings.items():
            if original.lower() == cancer_type_lower:
                return standard
        
        # Partial matching for common patterns
        if 'lung' in cancer_type_lower:
            if 'small cell' in cancer_type_lower:
                return 'SCLC'
            else:
                return 'NSCLC'
        elif 'breast' in cancer_type_lower:
            return 'Breast'
        elif 'colon' in cancer_type_lower or 'colorectal' in cancer_type_lower:
            return 'Colorectal'
        elif 'melanoma' in cancer_type_lower:
            return 'Melanoma'
        elif 'pancrea' in cancer_type_lower:
            return 'Pancreatic'
        elif 'glioblastoma' in cancer_type_lower or 'gbm' in cancer_type_lower:
            return 'Glioblastoma'
        elif 'prostate' in cancer_type_lower:
            return 'Prostate'
        elif 'kidney' in cancer_type_lower or 'renal' in cancer_type_lower:
            return 'Kidney'
        elif 'bladder' in cancer_type_lower:
            return 'Bladder'
        elif 'liver' in cancer_type_lower or 'hepato' in cancer_type_lower:
            return 'Liver'
        elif 'ovarian' in cancer_type_lower or 'ovary' in cancer_type_lower:
            return 'Ovarian'
        elif 'thyroid' in cancer_type_lower:
            return 'Thyroid'
        elif 'gastric' in cancer_type_lower or 'stomach' in cancer_type_lower:
            return 'Gastric'
        elif 'head' in cancer_type_lower and 'neck' in cancer_type_lower:
            return 'Head and Neck'
        elif 'aml' in cancer_type_lower or 'acute myeloid' in cancer_type_lower:
            return 'AML'
        
        # If no mapping found, return cleaned original
        return self._clean_cancer_type(cancer_type)
    
    def _clean_cancer_type(self, cancer_type: str) -> str:
        """Clean and format cancer type string"""
        # Remove common suffixes
        cleaned = cancer_type.replace('Cancer', '').replace('Carcinoma', '')
        cleaned = cleaned.replace('Adenocarcinoma', '').strip()
        
        # Title case
        return cleaned.title() if cleaned else cancer_type
    
    def get_all_standard_types(self) -> list:
        """Get list of all standard cancer types"""
        return sorted(list(set(self.mappings.values())))
    
    def get_aliases(self, standard_type: str) -> list:
        """
        Get all aliases for a standard cancer type
        
        Args:
            standard_type: Standard cancer type name
            
        Returns:
            List of aliases/alternative names
        """
        return self.reverse_mappings.get(standard_type, [])