#!/usr/bin/env python3
"""
CIViC (Clinical Interpretation of Variants in Cancer) Extractor
Fetches curated variant interpretations and therapeutic associations
API Documentation: https://civicdb.org/api/graphql
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


class CIViCExtractor(BaseExtractor):
    """Extract variant and therapeutic data from CIViC database"""
    
    def __init__(self):
        super().__init__()
        self.api_url = "https://civicdb.org/api/graphql"
        self.rest_api = "https://civicdb.org/api"
        self.rate_limit_delay = 0.2  # 5 requests per second
        self.output_dir = Path("bronze/data/civic")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract(self, gene_symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract data from CIViC
        
        Args:
            gene_symbols: Optional list of gene symbols to filter
            
        Returns:
            Dictionary containing variants, genes, and therapeutics
        """
        logger.info("Starting CIViC extraction")
        
        result = {
            "variants": [],
            "genes": [],
            "therapies": [],
            "evidence_items": [],
            "assertions": []
        }
        
        try:
            # Fetch genes
            logger.info("Fetching genes from CIViC")
            genes = self._fetch_genes(gene_symbols)
            result["genes"] = genes
            logger.info(f"Fetched {len(genes)} genes")
            
            # Fetch variants for each gene
            logger.info("Fetching variants")
            for gene in genes[:500]:  # Limit to top 500 genes
                gene_id = gene.get("id")
                gene_symbol = gene.get("name")
                
                if gene_id:
                    variants = self._fetch_variants_for_gene(gene_id, gene_symbol)
                    result["variants"].extend(variants)
                    time.sleep(self.rate_limit_delay)
            
            logger.info(f"Fetched {len(result['variants'])} variants")
            
            # Fetch therapies
            logger.info("Fetching therapies")
            therapies = self._fetch_therapies()
            result["therapies"] = therapies
            logger.info(f"Fetched {len(therapies)} therapies")
            
            # Fetch evidence items (variant-therapy associations)
            logger.info("Fetching evidence items")
            evidence = self._fetch_evidence_items()
            result["evidence_items"] = evidence
            logger.info(f"Fetched {len(evidence)} evidence items")
            
            # Save raw data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"civic_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Saved CIViC data to {output_file}")
            
            # Save metadata
            metadata = {
                "source": "civic",
                "timestamp": timestamp,
                "gene_count": len(result["genes"]),
                "variant_count": len(result["variants"]),
                "therapy_count": len(result["therapies"]),
                "evidence_count": len(result["evidence_items"])
            }
            
            metadata_file = self.output_dir / f"civic_{timestamp}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error extracting CIViC data: {str(e)}")
            raise
            
        return result
    
    def _fetch_genes(self, gene_symbols: Optional[List[str]] = None) -> List[Dict]:
        """Fetch genes from CIViC"""
        genes = []
        
        # GraphQL query for genes
        query = """
        query Genes($after: String) {
            genes(first: 100, after: $after) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    name
                    entrezId
                    description
                    sources {
                        id
                        name
                    }
                    variants {
                        totalCount
                    }
                }
            }
        }
        """
        
        has_next = True
        after_cursor = None
        
        while has_next and len(genes) < 1000:  # Limit to 1000 genes
            try:
                variables = {"after": after_cursor} if after_cursor else {}
                
                response = requests.post(
                    self.api_url,
                    json={"query": query, "variables": variables},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                data = response.json()
                
                if "data" in data and "genes" in data["data"]:
                    gene_data = data["data"]["genes"]
                    genes.extend(gene_data.get("nodes", []))
                    
                    page_info = gene_data.get("pageInfo", {})
                    has_next = page_info.get("hasNextPage", False)
                    after_cursor = page_info.get("endCursor")
                else:
                    break
                    
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error fetching genes: {str(e)}")
                break
        
        # Filter by gene symbols if provided
        if gene_symbols:
            genes = [g for g in genes if g.get("name") in gene_symbols]
        
        return genes
    
    def _fetch_variants_for_gene(self, gene_id: int, gene_symbol: str) -> List[Dict]:
        """Fetch variants for a specific gene"""
        variants = []
        
        query = """
        query GeneVariants($geneId: Int!) {
            gene(id: $geneId) {
                variants(first: 50) {
                    nodes {
                        id
                        name
                        variantTypes
                        coordinates {
                            chromosome
                            start
                            stop
                            reference
                            variant
                        }
                        singleVariantMolecularProfile {
                            id
                            evidenceItems {
                                totalCount
                            }
                        }
                    }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.api_url,
                json={"query": query, "variables": {"geneId": gene_id}},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data and "gene" in data["data"]:
                gene_data = data["data"]["gene"]
                if gene_data and "variants" in gene_data:
                    variant_nodes = gene_data["variants"].get("nodes", [])
                    # Add gene symbol to each variant
                    for variant in variant_nodes:
                        variant["gene_symbol"] = gene_symbol
                    variants.extend(variant_nodes)
                    
        except Exception as e:
            logger.error(f"Error fetching variants for gene {gene_symbol}: {str(e)}")
        
        return variants
    
    def _fetch_therapies(self) -> List[Dict]:
        """Fetch therapies from CIViC"""
        therapies = []
        
        query = """
        query Therapies($after: String) {
            therapies(first: 100, after: $after) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    name
                    ncitId
                    therapyAliases
                }
            }
        }
        """
        
        has_next = True
        after_cursor = None
        
        while has_next and len(therapies) < 2000:  # Limit to 2000 therapies
            try:
                variables = {"after": after_cursor} if after_cursor else {}
                
                response = requests.post(
                    self.api_url,
                    json={"query": query, "variables": variables},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                data = response.json()
                
                if "data" in data and "therapies" in data["data"]:
                    therapy_data = data["data"]["therapies"]
                    therapies.extend(therapy_data.get("nodes", []))
                    
                    page_info = therapy_data.get("pageInfo", {})
                    has_next = page_info.get("hasNextPage", False)
                    after_cursor = page_info.get("endCursor")
                else:
                    break
                    
                time.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error fetching therapies: {str(e)}")
                break
        
        return therapies
    
    def _fetch_evidence_items(self) -> List[Dict]:
        """Fetch evidence items (variant-therapy associations)"""
        evidence_items = []
        
        # Use REST API for evidence items as it's more efficient
        endpoint = f"{self.rest_api}/evidence_items"
        
        try:
            # Fetch predictive evidence (therapeutic associations)
            params = {
                "evidence_type": "Predictive",
                "status": "accepted",
                "count": 500  # Get top 500 evidence items
            }
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "records" in data:
                evidence_items = data["records"]
                logger.info(f"Fetched {len(evidence_items)} predictive evidence items")
            
        except Exception as e:
            logger.error(f"Error fetching evidence items: {str(e)}")
        
        return evidence_items


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    extractor = CIViCExtractor()
    result = extractor.extract()
    
    print(f"Extracted {len(result['genes'])} genes")
    print(f"Extracted {len(result['variants'])} variants")
    print(f"Extracted {len(result['therapies'])} therapies")
    print(f"Extracted {len(result['evidence_items'])} evidence items")