"""Variant notation harmonizer for standardizing mutation nomenclature"""

import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VariantHarmonizer:
    """Harmonize variant notations from different sources"""
    
    # Three-letter to one-letter amino acid code mapping
    AA_3TO1 = {
        'Ala': 'A', 'Arg': 'R', 'Asn': 'N', 'Asp': 'D',
        'Cys': 'C', 'Gln': 'Q', 'Glu': 'E', 'Gly': 'G',
        'His': 'H', 'Ile': 'I', 'Leu': 'L', 'Lys': 'K',
        'Met': 'M', 'Phe': 'F', 'Pro': 'P', 'Ser': 'S',
        'Thr': 'T', 'Trp': 'W', 'Tyr': 'Y', 'Val': 'V',
        'Ter': '*', 'Stop': '*'
    }
    
    # One-letter to three-letter amino acid code mapping
    AA_1TO3 = {v: k for k, v in AA_3TO1.items()}
    
    def harmonize_protein_change(self, protein_change: str) -> str:
        """
        Harmonize protein change notation to standard format (p.X###Y)
        
        Args:
            protein_change: Protein change in various formats
            
        Returns:
            Standardized protein change notation
        """
        if not protein_change:
            return ''
        
        # Remove whitespace and convert to uppercase for processing
        cleaned = protein_change.strip()
        
        # Handle different formats
        if self._is_standard_format(cleaned):
            return cleaned
        
        # Try to parse and standardize
        parsed = self._parse_protein_change(cleaned)
        if parsed:
            return self._format_protein_change(*parsed)
        
        # If parsing fails, return cleaned original
        return cleaned
    
    def _is_standard_format(self, protein_change: str) -> bool:
        """Check if protein change is already in standard format"""
        # Standard format: p.X###Y where X and Y are amino acids, ### is position
        pattern = r'^p\.[A-Z]\d+[A-Z*]$'
        return bool(re.match(pattern, protein_change))
    
    def _parse_protein_change(self, protein_change: str) -> Optional[Tuple[str, int, str]]:
        """
        Parse protein change into components
        
        Returns:
            Tuple of (ref_aa, position, alt_aa) or None
        """
        # Remove p. prefix if present
        cleaned = protein_change
        if cleaned.startswith('p.'):
            cleaned = cleaned[2:]
        
        # Pattern 1: V600E (one letter codes)
        match = re.match(r'^([A-Z])(\d+)([A-Z*])$', cleaned)
        if match:
            return match.group(1), int(match.group(2)), match.group(3)
        
        # Pattern 2: Val600Glu (three letter codes)
        match = re.match(r'^([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2}|\*)$', cleaned)
        if match:
            ref_aa = self.AA_3TO1.get(match.group(1), match.group(1))
            alt_aa = self.AA_3TO1.get(match.group(3), match.group(3))
            return ref_aa, int(match.group(2)), alt_aa
        
        # Pattern 3: 600V>E or 600V/E
        match = re.match(r'^(\d+)([A-Z])[\/>]([A-Z*])$', cleaned)
        if match:
            return match.group(2), int(match.group(1)), match.group(3)
        
        # Pattern 4: Frameshift (fs)
        if 'fs' in cleaned.lower():
            match = re.search(r'([A-Z])?(\d+)', cleaned)
            if match:
                ref_aa = match.group(1) or 'X'
                position = int(match.group(2))
                return ref_aa, position, 'fs'
        
        # Pattern 5: Deletion (del)
        if 'del' in cleaned.lower():
            match = re.search(r'([A-Z])?(\d+)', cleaned)
            if match:
                ref_aa = match.group(1) or 'X'
                position = int(match.group(2))
                return ref_aa, position, 'del'
        
        # Pattern 6: Insertion (ins)
        if 'ins' in cleaned.lower():
            match = re.search(r'(\d+)', cleaned)
            if match:
                position = int(match.group(1))
                return 'X', position, 'ins'
        
        # Pattern 7: Duplication (dup)
        if 'dup' in cleaned.lower():
            match = re.search(r'([A-Z])?(\d+)', cleaned)
            if match:
                ref_aa = match.group(1) or 'X'
                position = int(match.group(2))
                return ref_aa, position, 'dup'
        
        # Pattern 8: Complex substitution V600_K601delinsE
        match = re.match(r'^([A-Z])(\d+)_([A-Z])(\d+)delins([A-Z]+)$', cleaned)
        if match:
            return match.group(1), int(match.group(2)), match.group(5)
        
        return None
    
    def _format_protein_change(self, ref_aa: str, position: int, alt_aa: str) -> str:
        """
        Format protein change in standard notation
        
        Args:
            ref_aa: Reference amino acid
            position: Position in protein
            alt_aa: Alternate amino acid
            
        Returns:
            Formatted protein change string
        """
        # Handle special cases
        if alt_aa in ['fs', 'del', 'ins', 'dup']:
            return f"p.{ref_aa}{position}{alt_aa}"
        
        # Standard substitution
        return f"p.{ref_aa}{position}{alt_aa}"
    
    def extract_position(self, protein_change: str) -> Optional[int]:
        """
        Extract position from protein change notation
        
        Args:
            protein_change: Protein change notation
            
        Returns:
            Position number or None
        """
        if not protein_change:
            return None
        
        # Search for digits in the string
        match = re.search(r'\d+', protein_change)
        if match:
            return int(match.group())
        
        return None
    
    def is_hotspot_position(self, gene: str, position: int) -> bool:
        """
        Check if a position is a known hotspot
        
        Args:
            gene: Gene symbol
            position: Protein position
            
        Returns:
            True if position is a known hotspot
        """
        hotspots = {
            'KRAS': [12, 13, 61, 117, 146],
            'BRAF': [600],
            'EGFR': [719, 746, 747, 748, 749, 750, 751, 752, 790, 858],
            'TP53': [175, 245, 248, 249, 273, 282],
            'PIK3CA': [542, 545, 546, 1047],
            'NRAS': [12, 13, 61],
            'IDH1': [132],
            'IDH2': [140, 172],
            'FLT3': [835],
            'KIT': [816, 820],
            'ERBB2': [755, 769, 770],
            'AKT1': [17],
            'PTEN': [130, 173, 233, 267]
        }
        
        gene_hotspots = hotspots.get(gene.upper(), [])
        return position in gene_hotspots
    
    def classify_variant_impact(self, variant_type: str, variant_classification: str = '') -> str:
        """
        Classify the functional impact of a variant
        
        Args:
            variant_type: Type of variant (SNP, insertion, deletion, etc.)
            variant_classification: Variant classification if available
            
        Returns:
            Impact classification (high, moderate, low, modifier)
        """
        high_impact = [
            'nonsense', 'frame_shift_del', 'frame_shift_ins',
            'splice_acceptor_variant', 'splice_donor_variant',
            'stop_gained', 'frameshift_variant', 'stop_lost',
            'start_lost', 'transcript_ablation'
        ]
        
        moderate_impact = [
            'missense', 'missense_mutation', 'missense_variant',
            'in_frame_del', 'in_frame_ins', 'inframe_deletion',
            'inframe_insertion', 'protein_altering_variant'
        ]
        
        low_impact = [
            'synonymous', 'synonymous_variant', 'stop_retained_variant',
            'start_retained_variant'
        ]
        
        classification_lower = variant_classification.lower()
        type_lower = variant_type.lower() if variant_type else ''
        
        # Check classification first
        if any(term in classification_lower for term in high_impact):
            return 'high'
        elif any(term in classification_lower for term in moderate_impact):
            return 'moderate'
        elif any(term in classification_lower for term in low_impact):
            return 'low'
        
        # Check variant type
        if 'frameshift' in type_lower or 'nonsense' in type_lower:
            return 'high'
        elif 'missense' in type_lower or 'snp' in type_lower:
            return 'moderate'
        elif 'synonymous' in type_lower or 'silent' in type_lower:
            return 'low'
        
        return 'modifier'