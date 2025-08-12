"""Therapeutic aggregator for Gold layer - Associates mutations with therapeutics"""

import json
import os
import yaml
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import logging
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class TherapeuticAggregator:
    """Associate mutations with therapeutic options"""
    
    def __init__(self):
        self.gold_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        self.therapeutic_associations = self._load_therapeutic_associations()
        
    def _load_therapeutic_associations(self) -> Dict:
        """Load mutation-therapeutic associations from config"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config',
            'clinically_actionable_genes.yaml'
        )
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('therapeutic_associations', {})
        except FileNotFoundError:
            logger.warning("Therapeutic associations config not found")
            return {}
    
    def associate_mutations_with_therapeutics(
        self, 
        mutations: List[Dict], 
        therapeutics: List[Dict]
    ) -> Dict[str, Any]:
        """
        Associate aggregated mutations with therapeutic options
        
        This is the KEY FUNCTION that links mutations to drugs!
        
        Args:
            mutations: Aggregated mutations from mutation_aggregator
            therapeutics: Drug-gene interactions from DGIdb
            
        Returns:
            Dictionary with mutation-therapeutic associations
        """
        logger.info(f"Associating {len(mutations)} mutations with {len(therapeutics)} therapeutics")
        
        # Build lookup structures
        gene_to_drugs = self._build_gene_drug_map(therapeutics)
        mutation_to_drugs = self._build_mutation_drug_map()
        
        # Result structure
        associations = {
            'mutation_therapeutics': [],
            'gene_therapeutics': [],
            'hotspot_therapeutics': [],
            'summary': {}
        }
        
        # Process each mutation
        for mutation in mutations:
            gene = mutation.get('gene_symbol')
            protein_change = mutation.get('protein_change', '')
            position = mutation.get('position')
            cancer_type = mutation.get('cancer_type')
            
            # Find therapeutics for this mutation
            therapy_options = self._find_therapeutics_for_mutation(
                gene, protein_change, position, 
                gene_to_drugs, mutation_to_drugs
            )
            
            if therapy_options:
                association = {
                    'gene': gene,
                    'protein_change': protein_change,
                    'position': position,
                    'cancer_type': cancer_type,
                    'mutation_count': mutation.get('mutation_count'),
                    'frequency': mutation.get('frequency'),
                    'significance_score': mutation.get('significance_score'),
                    'therapeutics': therapy_options
                }
                associations['mutation_therapeutics'].append(association)
        
        # Aggregate by gene
        associations['gene_therapeutics'] = self._aggregate_by_gene(
            associations['mutation_therapeutics']
        )
        
        # Identify hotspot therapeutics
        associations['hotspot_therapeutics'] = self._identify_hotspot_therapeutics(
            associations['mutation_therapeutics']
        )
        
        # Generate summary
        associations['summary'] = self._generate_summary(associations)
        
        logger.info(f"Associated {len(associations['mutation_therapeutics'])} mutations with therapeutics")
        
        return associations
    
    def _build_gene_drug_map(self, therapeutics: List[Dict]) -> Dict[str, List[Dict]]:
        """Build gene -> drugs mapping from DGIdb data"""
        gene_drugs = defaultdict(list)
        
        for interaction in therapeutics:
            gene = interaction.get('gene_name')
            drug_name = interaction.get('drug_name')
            
            if gene and drug_name:
                drug_info = {
                    'drug_name': drug_name,
                    'interaction_types': interaction.get('interaction_types', []),
                    'sources': interaction.get('sources', []),
                    'attributes': interaction.get('drug_attributes', {}),
                    'association_type': 'gene_level'
                }
                
                # Avoid duplicates
                if not any(d['drug_name'] == drug_name for d in gene_drugs[gene]):
                    gene_drugs[gene].append(drug_info)
        
        return dict(gene_drugs)
    
    def _build_mutation_drug_map(self) -> Dict[str, Dict]:
        """Build mutation-specific drug associations"""
        mutation_drugs = {}
        
        for gene, mutations in self.therapeutic_associations.items():
            for mutation_key, drugs in mutations.items():
                # Create standardized keys
                keys = self._generate_mutation_keys(gene, mutation_key)
                
                for key in keys:
                    mutation_drugs[key] = {
                        'drugs': drugs,
                        'mutation_type': mutation_key,
                        'association_type': 'mutation_specific'
                    }
        
        return mutation_drugs
    
    def _generate_mutation_keys(self, gene: str, mutation: str) -> List[str]:
        """Generate possible keys for a mutation"""
        keys = []
        
        # Basic key
        keys.append(f"{gene}:{mutation}")
        
        # Handle position-based mutations (e.g., V600E)
        match = re.match(r'([A-Z])(\d+)([A-Z])', mutation)
        if match:
            ref_aa, pos, alt_aa = match.groups()
            keys.append(f"{gene}:{pos}")
            keys.append(f"{gene}:p.{ref_aa}{pos}{alt_aa}")
        
        # Handle special cases
        if mutation == 'fusion':
            keys.append(f"{gene}:fusion")
            keys.append(f"{gene}:rearrangement")
        elif mutation == 'amplification':
            keys.append(f"{gene}:amp")
            keys.append(f"{gene}:amplification")
        elif 'exon' in mutation.lower():
            keys.append(f"{gene}:{mutation}")
            keys.append(f"{gene}:{mutation.replace('exon', 'ex')}")
        
        return keys
    
    def _find_therapeutics_for_mutation(
        self, 
        gene: str, 
        protein_change: str, 
        position: int,
        gene_to_drugs: Dict,
        mutation_to_drugs: Dict
    ) -> List[Dict]:
        """Find all applicable therapeutics for a mutation"""
        therapeutics = []
        
        # Clean protein change notation (remove p. prefix)
        clean_protein_change = protein_change.replace('p.', '') if protein_change else ''
        
        # 1. Check for mutation-specific drugs (highest priority)
        mutation_keys = [
            f"{gene}:{clean_protein_change}",
            f"{gene}:{protein_change}",
            f"{gene}:{position}",
            f"{gene}:{self._extract_mutation_type(protein_change)}"
        ]
        
        for key in mutation_keys:
            if key in mutation_to_drugs:
                mutation_data = mutation_to_drugs[key]
                for drug in mutation_data['drugs']:
                    therapeutics.append({
                        'drug_name': drug,
                        'association_level': 'mutation_specific',
                        'mutation_type': mutation_data['mutation_type'],
                        'confidence': 'high',
                        'fda_approved': self._check_fda_approval(drug)
                    })
                break  # Use first match
        
        # 2. Check for gene-level drugs (always check, not just when no mutation-specific found)
        # This ensures we provide therapeutic options for all mutations in druggable genes
        if gene in gene_to_drugs and len(therapeutics) < 5:  # Limit to avoid too many options
            for drug_info in gene_to_drugs[gene]:
                # Filter for inhibitors/antagonists for oncogenes
                if self._is_relevant_drug(gene, drug_info):
                    therapeutics.append({
                        'drug_name': drug_info['drug_name'],
                        'association_level': 'gene_level',
                        'interaction_types': drug_info.get('interaction_types', []),
                        'confidence': 'medium',
                        'fda_approved': drug_info.get('attributes', {}).get('fda_approved', False)
                    })
        
        # 3. Check for hotspot position drugs
        if position and self._is_hotspot_position(gene, position):
            hotspot_drugs = self._get_hotspot_drugs(gene, position)
            for drug in hotspot_drugs:
                if not any(t['drug_name'] == drug for t in therapeutics):
                    therapeutics.append({
                        'drug_name': drug,
                        'association_level': 'hotspot',
                        'confidence': 'medium',
                        'fda_approved': self._check_fda_approval(drug)
                    })
        
        return therapeutics
    
    def _extract_mutation_type(self, protein_change: str) -> str:
        """Extract mutation type from protein change notation"""
        if not protein_change:
            return ''
        
        # Remove p. prefix
        change = protein_change.replace('p.', '')
        
        # Check for special types
        if 'fs' in change:
            return 'frameshift'
        elif 'del' in change:
            return 'deletion'
        elif 'ins' in change:
            return 'insertion'
        elif 'dup' in change:
            return 'duplication'
        elif '*' in change:
            return 'nonsense'
        
        # Extract position for substitutions
        match = re.search(r'(\d+)', change)
        if match:
            return match.group(1)
        
        return change
    
    def _is_relevant_drug(self, gene: str, drug_info: Dict) -> bool:
        """Check if drug is relevant for the gene"""
        interaction_types = drug_info.get('interaction_types', [])
        
        # Oncogenes need inhibitors
        oncogenes = ['KRAS', 'EGFR', 'BRAF', 'ALK', 'MET', 'RET', 'ROS1', 
                    'FGFR1', 'FGFR2', 'FGFR3', 'PIK3CA', 'ERBB2']
        
        if gene in oncogenes:
            return any(t in ['inhibitor', 'antagonist', 'blocker'] 
                      for t in interaction_types)
        
        # Tumor suppressors might need different approach
        return True
    
    def _is_hotspot_position(self, gene: str, position: int) -> bool:
        """Check if position is a known hotspot"""
        hotspots = {
            'KRAS': [12, 13, 61],
            'BRAF': [600],
            'EGFR': [719, 746, 790, 858],
            'PIK3CA': [542, 545, 1047],
            'TP53': [175, 245, 248, 273],
            'IDH1': [132],
            'IDH2': [140, 172],
            'FLT3': [835]
        }
        
        return position in hotspots.get(gene, [])
    
    def _get_hotspot_drugs(self, gene: str, position: int) -> List[str]:
        """Get drugs for hotspot mutations"""
        hotspot_drugs = {
            'KRAS': {
                12: ['Sotorasib', 'Adagrasib'],
                13: ['Sotorasib', 'Adagrasib'],
                61: ['AMG-510', 'MRTX849']
            },
            'BRAF': {
                600: ['Vemurafenib', 'Dabrafenib', 'Encorafenib']
            },
            'EGFR': {
                790: ['Osimertinib'],
                858: ['Erlotinib', 'Gefitinib', 'Osimertinib']
            }
        }
        
        return hotspot_drugs.get(gene, {}).get(position, [])
    
    def _check_fda_approval(self, drug_name: str) -> bool:
        """Check if drug is FDA approved (simplified)"""
        fda_approved = [
            'Osimertinib', 'Erlotinib', 'Gefitinib', 'Afatinib',
            'Crizotinib', 'Alectinib', 'Brigatinib', 'Lorlatinib',
            'Vemurafenib', 'Dabrafenib', 'Encorafenib',
            'Sotorasib', 'Adagrasib',
            'Trastuzumab', 'Pertuzumab',
            'Imatinib', 'Dasatinib', 'Nilotinib',
            'Olaparib', 'Rucaparib', 'Niraparib',
            'Alpelisib', 'Everolimus',
            'Palbociclib', 'Ribociclib', 'Abemaciclib'
        ]
        
        return drug_name in fda_approved
    
    def _aggregate_by_gene(self, mutation_therapeutics: List[Dict]) -> List[Dict]:
        """Aggregate therapeutic options by gene"""
        gene_aggregates = defaultdict(lambda: {
            'mutations': [],
            'all_drugs': set(),
            'fda_approved_drugs': set(),
            'cancer_types': set(),
            'total_mutations': 0
        })
        
        for mt in mutation_therapeutics:
            gene = mt['gene']
            agg = gene_aggregates[gene]
            
            agg['mutations'].append({
                'protein_change': mt['protein_change'],
                'position': mt['position'],
                'frequency': mt['frequency']
            })
            
            agg['cancer_types'].add(mt['cancer_type'])
            agg['total_mutations'] += mt.get('mutation_count', 0)
            
            for drug in mt['therapeutics']:
                agg['all_drugs'].add(drug['drug_name'])
                if drug.get('fda_approved'):
                    agg['fda_approved_drugs'].add(drug['drug_name'])
        
        # Convert to list
        result = []
        for gene, data in gene_aggregates.items():
            result.append({
                'gene': gene,
                'mutation_count': len(data['mutations']),
                'total_mutations': data['total_mutations'],
                'cancer_types': list(data['cancer_types']),
                'all_drugs': list(data['all_drugs']),
                'fda_approved_drugs': list(data['fda_approved_drugs']),
                'top_mutations': sorted(
                    data['mutations'], 
                    key=lambda x: x.get('frequency', 0), 
                    reverse=True
                )[:5]
            })
        
        return sorted(result, key=lambda x: x['total_mutations'], reverse=True)
    
    def _identify_hotspot_therapeutics(self, mutation_therapeutics: List[Dict]) -> List[Dict]:
        """Identify therapeutics for mutation hotspots"""
        hotspots = []
        
        # Group by gene and position
        position_groups = defaultdict(list)
        
        for mt in mutation_therapeutics:
            key = (mt['gene'], mt.get('position'))
            if key[1]:  # Has position
                position_groups[key].append(mt)
        
        # Find hotspots (positions with multiple cancer types or high frequency)
        for (gene, position), mutations in position_groups.items():
            if len(mutations) >= 2 or any(m.get('frequency', 0) > 0.1 for m in mutations):
                # Collect all drugs for this hotspot
                all_drugs = set()
                for m in mutations:
                    for drug in m.get('therapeutics', []):
                        all_drugs.add(drug['drug_name'])
                
                if all_drugs:
                    hotspots.append({
                        'gene': gene,
                        'position': position,
                        'cancer_types': list(set(m['cancer_type'] for m in mutations)),
                        'total_mutations': sum(m.get('mutation_count', 0) for m in mutations),
                        'max_frequency': max(m.get('frequency', 0) for m in mutations),
                        'therapeutics': list(all_drugs)
                    })
        
        return sorted(hotspots, key=lambda x: x['total_mutations'], reverse=True)
    
    def _generate_summary(self, associations: Dict) -> Dict:
        """Generate summary statistics"""
        return {
            'total_actionable_mutations': len(associations['mutation_therapeutics']),
            'genes_with_therapeutics': len(associations['gene_therapeutics']),
            'hotspot_count': len(associations['hotspot_therapeutics']),
            'unique_drugs': len(set(
                drug['drug_name']
                for mt in associations['mutation_therapeutics']
                for drug in mt.get('therapeutics', [])
            )),
            'fda_approved_drugs': len(set(
                drug['drug_name']
                for mt in associations['mutation_therapeutics']
                for drug in mt.get('therapeutics', [])
                if drug.get('fda_approved')
            ))
        }
    
    def save_associations(self, associations: Dict) -> Dict:
        """Save therapeutic associations to Gold layer"""
        timestamp = datetime.utcnow()
        
        # Create directory
        data_dir = os.path.join(self.gold_path, 'therapeutic_targets')
        os.makedirs(data_dir, exist_ok=True)
        
        # Save data
        filename = f"therapeutic_associations_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(associations, f, indent=2, default=str)
        
        metadata = {
            'timestamp': timestamp.isoformat(),
            'file': filepath,
            'summary': associations.get('summary', {})
        }
        
        logger.info(f"Saved therapeutic associations to {filepath}")
        return metadata