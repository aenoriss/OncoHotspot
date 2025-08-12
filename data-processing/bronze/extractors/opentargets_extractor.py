#!/usr/bin/env python3
"""
OpenTargets Extractor
Fetches drug-gene interactions and target associations from OpenTargets Platform
API Documentation: https://platform.opentargets.org/api
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from pathlib import Path

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class OpenTargetsExtractor(BaseExtractor):
    """Extract drug-target data from OpenTargets Platform"""
    
    def __init__(self):
        super().__init__()
        self.graphql_url = "https://api.platform.opentargets.org/api/v4/graphql"
        self.rest_url = "https://api.platform.opentargets.org/api/v4"
        self.headers = {"Content-Type": "application/json"}
        self.rate_limit_delay = 0.1  # 10 requests per second
        self.output_dir = Path("bronze/data/opentargets")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract(self, gene_symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract data from OpenTargets
        
        Args:
            gene_symbols: Optional list of gene symbols to filter
            
        Returns:
            Dictionary containing targets, drugs, and associations
        """
        logger.info("Starting OpenTargets extraction")
        
        result = {
            "targets": [],
            "drugs": [],
            "drug_target_interactions": [],
            "cancer_associations": []
        }
        
        try:
            # If gene symbols provided, use them; otherwise get cancer-related targets
            if gene_symbols:
                logger.info(f"Fetching data for {len(gene_symbols)} specified genes")
                targets = self._fetch_targets_by_symbols(gene_symbols)
            else:
                logger.info("Fetching cancer-related targets")
                targets = self._fetch_cancer_targets()
            
            result["targets"] = targets
            logger.info(f"Fetched {len(targets)} targets")
            
            # Extract drug interactions from target data
            logger.info("Processing drug-target interactions")
            all_drugs = {}
            
            for target in targets:
                target_id = target.get("id")
                target_symbol = target.get("approvedSymbol")
                known_drugs = target.get("knownDrugs", {})
                
                if known_drugs and known_drugs.get("rows"):
                    for drug_row in known_drugs["rows"]:
                        drug = drug_row.get("drug", {})
                        drug_id = drug.get("id")
                        
                        if drug_id:
                            # Store unique drugs
                            if drug_id not in all_drugs:
                                all_drugs[drug_id] = drug
                            
                            # Store interaction
                            result["drug_target_interactions"].append({
                                "target_id": target_id,
                                "target_symbol": target_symbol,
                                "drug_id": drug_id,
                                "drug_name": drug.get("name"),
                                "mechanism": drug_row.get("mechanismOfAction", ""),
                                "target_class": drug_row.get("targetClass", ""),
                                "max_phase": drug.get("maximumClinicalTrialPhase", 0)
                            })
            
            result["drugs"] = list(all_drugs.values())
            logger.info(f"Fetched {len(result['drugs'])} unique drugs")
            logger.info(f"Fetched {len(result['drug_target_interactions'])} drug-target interactions")
            
            # Fetch cancer-specific associations
            logger.info("Fetching cancer associations")
            cancer_associations = self._fetch_cancer_associations(targets[:100])
            result["cancer_associations"] = cancer_associations
            logger.info(f"Fetched {len(cancer_associations)} cancer associations")
            
            # Save raw data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"opentargets_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Saved OpenTargets data to {output_file}")
            
            # Save metadata
            metadata = {
                "source": "opentargets",
                "timestamp": timestamp,
                "target_count": len(result["targets"]),
                "drug_count": len(result["drugs"]),
                "interaction_count": len(result["drug_target_interactions"]),
                "cancer_association_count": len(result["cancer_associations"])
            }
            
            metadata_file = self.output_dir / f"opentargets_{timestamp}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error extracting OpenTargets data: {str(e)}")
            raise
            
        return result
    
    def _fetch_targets_by_symbols(self, gene_symbols: List[str]) -> List[Dict]:
        """Fetch targets by gene symbols using GraphQL API"""
        targets = []
        
        # GraphQL query to get drug-target associations
        query = """
        query targetDrugs($ensemblId: String!) {
            target(ensemblId: $ensemblId) {
                id
                approvedSymbol
                approvedName
                biotype
                knownDrugs {
                    uniqueDrugs
                    rows {
                        drug {
                            id
                            name
                            drugType
                            maximumClinicalTrialPhase
                            hasBeenWithdrawn
                        }
                        mechanismOfAction
                        targetClass
                    }
                }
            }
        }
        """
        
        # Known Ensembl IDs for common cancer genes (for testing)
        known_genes = {
            'BRAF': 'ENSG00000157764',
            'TP53': 'ENSG00000141510', 
            'KRAS': 'ENSG00000133703',
            'EGFR': 'ENSG00000146648',
            'BRCA1': 'ENSG00000012048',
            'BRCA2': 'ENSG00000139618',
            'PIK3CA': 'ENSG00000121879'
        }
        
        # Fetch targets for known genes
        for symbol in gene_symbols[:10]:  # Limit to 10 genes
            if symbol in known_genes:
                try:
                    ensembl_id = known_genes[symbol]
                    variables = {"ensemblId": ensembl_id}
                    
                    response = requests.post(
                        self.graphql_url,
                        json={"query": query, "variables": variables},
                        headers=self.headers
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if "data" in data and "target" in data["data"] and data["data"]["target"]:
                        target_data = data["data"]["target"]
                        targets.append(target_data)
                    
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error fetching target for symbol {symbol}: {str(e)}")
        
        return targets
    
    def _fetch_cancer_targets(self) -> List[Dict]:
        """Fetch targets associated with cancer using REST API"""
        targets = []
        
        # Get targets associated with cancer (EFO:0000311)
        endpoint = f"{self.rest_url}/disease/EFO_0000311/associations"
        
        try:
            params = {
                "size": 500,
                "datasources": ["cancer_gene_census", "intogen", "eva_somatic"],
                "fields": ["target.id", "target.approvedSymbol", "target.approvedName", 
                          "target.biotype", "target.functionDescriptions"]
            }
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data"):
                # Extract unique targets
                seen_targets = set()
                for assoc in data["data"]:
                    target = assoc.get("target", {})
                    target_id = target.get("id")
                    
                    if target_id and target_id not in seen_targets:
                        seen_targets.add(target_id)
                        targets.append(target)
            
        except Exception as e:
            logger.error(f"Error fetching cancer targets: {str(e)}")
        
        return targets
    
    def _fetch_drug_interactions(self, target_id: str) -> List[Dict]:
        """Fetch drug interactions for a specific target using GraphQL"""
        interactions = []
        
        # Use GraphQL for drug interactions
        query = """
        query targetDrugs($ensemblId: String!) {
            target(ensemblId: $ensemblId) {
                id
                approvedSymbol
                knownDrugs {
                    uniqueDrugs
                    rows {
                        drug {
                            id
                            name
                            drugType
                            description
                            synonyms
                            isApproved
                        }
                        phase
                        status
                        diseaseFromSource
                        mechanismOfAction
                    }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                json={"query": query, "variables": {"ensemblId": target_id}},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data") and data["data"].get("target") and data["data"]["target"].get("knownDrugs"):
                known_drugs = data["data"]["target"]["knownDrugs"]
                
                # Extract approved and clinical trial drugs
                if known_drugs.get("rows"):
                    for drug_row in known_drugs["rows"]:
                        # Only include drugs in clinical trials or approved
                        phase = drug_row.get("phase", 0)
                        if phase >= 1:  # Phase I or higher
                            interactions.append({
                                "drug": {
                                    "id": drug_row.get("drug", {}).get("id"),
                                    "name": drug_row.get("drug", {}).get("name"),
                                    "type": drug_row.get("drug", {}).get("drugType"),
                                    "description": drug_row.get("drug", {}).get("description"),
                                    "synonyms": drug_row.get("drug", {}).get("synonyms", [])
                                },
                                "mechanismOfAction": drug_row.get("mechanismOfAction"),
                                "phase": phase,
                                "status": drug_row.get("status"),
                                "diseaseLabel": drug_row.get("diseaseFromSource"),
                            })
            
        except Exception as e:
            logger.error(f"Error fetching drug interactions for target {target_id}: {str(e)}")
        
        return interactions
    
    def _fetch_cancer_associations(self, targets: List[Dict]) -> List[Dict]:
        """Fetch cancer-specific associations for targets"""
        associations = []
        
        # Cancer disease IDs in OpenTargets
        cancer_diseases = [
            "EFO_0000311",  # Cancer (general)
            "EFO_0000571",  # Lung cancer
            "EFO_0000305",  # Breast cancer
            "EFO_0000365",  # Colorectal cancer
            "MONDO_0008315",  # Prostate cancer
            "EFO_0000519",  # Leukemia
            "EFO_0005842",  # Melanoma
        ]
        
        for target in targets[:50]:  # Limit to 50 targets for performance
            target_id = target.get("id")
            target_symbol = target.get("approvedSymbol")
            
            if not target_id:
                continue
            
            for disease_id in cancer_diseases:
                try:
                    endpoint = f"{self.rest_url}/evidence"
                    params = {
                        "target": target_id,
                        "disease": disease_id,
                        "datasource": "cancer_gene_census,intogen,eva_somatic",
                        "size": 10,
                        "fields": ["datasourceId", "datatypeId", "score", 
                                 "mutatedSamples", "variantFunctionalConsequence"]
                    }
                    
                    response = requests.get(endpoint, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if data.get("data"):
                        for evidence in data["data"]:
                            associations.append({
                                "target_id": target_id,
                                "target_symbol": target_symbol,
                                "disease_id": disease_id,
                                "datasource": evidence.get("datasourceId"),
                                "datatype": evidence.get("datatypeId"),
                                "score": evidence.get("score"),
                                "mutated_samples": evidence.get("mutatedSamples"),
                                "functional_consequence": evidence.get("variantFunctionalConsequence")
                            })
                    
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.debug(f"No association for {target_symbol} and {disease_id}")
        
        return associations


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    extractor = OpenTargetsExtractor()
    
    # Test with specific genes
    test_genes = ["EGFR", "KRAS", "BRAF", "TP53", "PTEN"]
    result = extractor.extract(test_genes)
    
    print(f"Extracted {len(result['targets'])} targets")
    print(f"Extracted {len(result['drugs'])} drugs")
    print(f"Extracted {len(result['drug_target_interactions'])} interactions")
    print(f"Extracted {len(result['cancer_associations'])} cancer associations")