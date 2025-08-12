#!/usr/bin/env python3
"""
Description Service with multiple sources and Claude fallback
Prioritizes free sources before using Claude API
"""

import os
import json
import logging
import time
from typing import Dict, Optional, List
from pathlib import Path
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DescriptionService:
    """Service to fetch descriptions from multiple sources with caching"""
    
    def __init__(self, cache_dir: str = "cache/descriptions"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache files
        self.gene_cache_file = self.cache_dir / "gene_descriptions.json"
        self.drug_cache_file = self.cache_dir / "drug_descriptions.json"
        
        # Load existing caches
        self.gene_cache = self._load_cache(self.gene_cache_file)
        self.drug_cache = self._load_cache(self.drug_cache_file)
        
        # API endpoints
        self.civic_api = "https://civicdb.org/api/graphql"
        self.opentargets_api = "https://api.platform.opentargets.org/api/v4"
        
        # Claude API configuration (only if available)
        self.claude_api_key = os.getenv("CLAUDE_API_KEY", "")
        self.use_claude = bool(self.claude_api_key)
        
        # Statistics
        self.stats = {
            "civic_hits": 0,
            "opentargets_hits": 0,
            "cache_hits": 0,
            "claude_calls": 0,
            "fallback_used": 0
        }
    
    def _load_cache(self, cache_file: Path) -> Dict:
        """Load cache from file"""
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache {cache_file}: {e}")
        return {}
    
    def _save_cache(self, cache_file: Path, cache_data: Dict):
        """Save cache to file"""
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache {cache_file}: {e}")
    
    def get_gene_description(self, gene_symbol: str) -> str:
        """
        Get gene description from multiple sources
        Priority: Cache -> CIViC -> OpenTargets -> Claude -> Default
        """
        gene_symbol = gene_symbol.upper()
        
        # Check cache first
        if gene_symbol in self.gene_cache:
            self.stats["cache_hits"] += 1
            return self.gene_cache[gene_symbol]
        
        description = None
        
        # Try CIViC
        description = self._get_civic_gene_description(gene_symbol)
        if description:
            self.stats["civic_hits"] += 1
            self.gene_cache[gene_symbol] = description
            self._save_cache(self.gene_cache_file, self.gene_cache)
            return description
        
        # Try OpenTargets
        description = self._get_opentargets_gene_description(gene_symbol)
        if description:
            self.stats["opentargets_hits"] += 1
            self.gene_cache[gene_symbol] = description
            self._save_cache(self.gene_cache_file, self.gene_cache)
            return description
        
        # Try Claude if available and configured
        if self.use_claude:
            description = self._get_claude_gene_description(gene_symbol)
            if description:
                self.stats["claude_calls"] += 1
                self.gene_cache[gene_symbol] = description
                self._save_cache(self.gene_cache_file, self.gene_cache)
                return description
        
        # Fallback to generic description
        self.stats["fallback_used"] += 1
        description = f"{gene_symbol} is a cancer-associated gene"
        self.gene_cache[gene_symbol] = description
        self._save_cache(self.gene_cache_file, self.gene_cache)
        
        return description
    
    def get_drug_description(self, drug_name: str) -> str:
        """
        Get drug description from multiple sources
        Priority: Cache -> OpenTargets -> ChEMBL -> Claude -> Default
        """
        # Check cache first
        if drug_name in self.drug_cache:
            self.stats["cache_hits"] += 1
            return self.drug_cache[drug_name]
        
        description = None
        
        # Try OpenTargets
        description = self._get_opentargets_drug_description(drug_name)
        if description:
            self.stats["opentargets_hits"] += 1
            self.drug_cache[drug_name] = description
            self._save_cache(self.drug_cache_file, self.drug_cache)
            return description
        
        # Try Claude if available
        if self.use_claude:
            description = self._get_claude_drug_description(drug_name)
            if description:
                self.stats["claude_calls"] += 1
                self.drug_cache[drug_name] = description
                self._save_cache(self.drug_cache_file, self.drug_cache)
                return description
        
        # Fallback
        self.stats["fallback_used"] += 1
        description = f"{drug_name} is a cancer therapeutic agent"
        self.drug_cache[drug_name] = description
        self._save_cache(self.drug_cache_file, self.drug_cache)
        
        return description
    
    def _get_civic_gene_description(self, gene_symbol: str) -> Optional[str]:
        """Fetch gene description from CIViC"""
        try:
            query = """
            query GeneDescription($name: String!) {
                genes(name: $name) {
                    nodes {
                        name
                        description
                    }
                }
            }
            """
            
            response = requests.post(
                self.civic_api,
                json={
                    "query": query,
                    "variables": {"name": gene_symbol}
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                genes = data.get("data", {}).get("genes", {}).get("nodes", [])
                if genes and genes[0].get("description"):
                    return genes[0]["description"]
        except Exception as e:
            logger.debug(f"CIViC query failed for {gene_symbol}: {e}")
        
        return None
    
    def _get_opentargets_gene_description(self, gene_symbol: str) -> Optional[str]:
        """Fetch gene description from OpenTargets"""
        try:
            # Search for gene
            search_url = f"{self.opentargets_api}/target/search"
            params = {"q": gene_symbol, "size": 1}
            
            response = requests.get(search_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    target = data["data"][0]
                    
                    # Get function descriptions
                    functions = target.get("functionDescriptions", [])
                    if functions:
                        # Combine first few function descriptions
                        desc_parts = []
                        for func in functions[:2]:  # Take first 2 descriptions
                            if isinstance(func, str):
                                desc_parts.append(func)
                        
                        if desc_parts:
                            return " ".join(desc_parts)[:500]  # Limit length
                    
                    # Fall back to approved name
                    if target.get("approvedName"):
                        return target["approvedName"]
        except Exception as e:
            logger.debug(f"OpenTargets query failed for {gene_symbol}: {e}")
        
        return None
    
    def _get_opentargets_drug_description(self, drug_name: str) -> Optional[str]:
        """Fetch drug description from OpenTargets"""
        try:
            # Search for drug
            search_url = f"{self.opentargets_api}/drug/search"
            params = {"q": drug_name, "size": 1}
            
            response = requests.get(search_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    drug = data["data"][0]
                    
                    # Get description or mechanism
                    if drug.get("description"):
                        return drug["description"]
                    elif drug.get("mechanismOfAction"):
                        return drug["mechanismOfAction"]
        except Exception as e:
            logger.debug(f"OpenTargets drug query failed for {drug_name}: {e}")
        
        return None
    
    def _get_claude_gene_description(self, gene_symbol: str) -> Optional[str]:
        """Get gene description from Claude API"""
        if not self.use_claude:
            return None
        
        try:
            import anthropic
            
            client = anthropic.Client(api_key=self.claude_api_key)
            
            prompt = f"""Provide a one-line description (max 100 characters) for the cancer gene {gene_symbol}. 
            Focus on its function and role in cancer. Be concise and factual."""
            
            response = client.completions.create(
                model="claude-3-haiku-20240307",
                prompt=prompt,
                max_tokens=50,
                temperature=0
            )
            
            if response and response.completion:
                return response.completion.strip()
        except Exception as e:
            logger.debug(f"Claude API failed for gene {gene_symbol}: {e}")
        
        return None
    
    def _get_claude_drug_description(self, drug_name: str) -> Optional[str]:
        """Get drug description from Claude API"""
        if not self.use_claude:
            return None
        
        try:
            import anthropic
            
            client = anthropic.Client(api_key=self.claude_api_key)
            
            prompt = f"""Provide a one-line description (max 100 characters) for the cancer drug {drug_name}. 
            Focus on its mechanism and cancer indications. Be concise and factual."""
            
            response = client.completions.create(
                model="claude-3-haiku-20240307",
                prompt=prompt,
                max_tokens=50,
                temperature=0
            )
            
            if response and response.completion:
                return response.completion.strip()
        except Exception as e:
            logger.debug(f"Claude API failed for drug {drug_name}: {e}")
        
        return None
    
    def batch_get_gene_descriptions(self, gene_symbols: List[str]) -> Dict[str, str]:
        """Get descriptions for multiple genes"""
        descriptions = {}
        
        for symbol in gene_symbols:
            descriptions[symbol] = self.get_gene_description(symbol)
            time.sleep(0.1)  # Rate limiting
        
        return descriptions
    
    def batch_get_drug_descriptions(self, drug_names: List[str]) -> Dict[str, str]:
        """Get descriptions for multiple drugs"""
        descriptions = {}
        
        for drug in drug_names:
            descriptions[drug] = self.get_drug_description(drug)
            time.sleep(0.1)  # Rate limiting
        
        return descriptions
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        total_queries = sum(self.stats.values())
        
        return {
            "total_queries": total_queries,
            "cache_hit_rate": self.stats["cache_hits"] / max(total_queries, 1),
            "civic_hits": self.stats["civic_hits"],
            "opentargets_hits": self.stats["opentargets_hits"],
            "claude_api_calls": self.stats["claude_calls"],
            "fallback_used": self.stats["fallback_used"],
            "estimated_claude_cost": self.stats["claude_calls"] * 0.0015  # Rough estimate
        }
    
    def preload_common_genes(self):
        """Preload descriptions for common cancer genes"""
        common_genes = [
            "TP53", "KRAS", "EGFR", "BRAF", "PIK3CA", "PTEN", "APC",
            "BRCA1", "BRCA2", "MYC", "ALK", "RET", "ROS1", "MET",
            "ERBB2", "CDK4", "CDK6", "NRAS", "IDH1", "IDH2", "FLT3",
            "NPM1", "JAK2", "KIT", "PDGFRA", "VHL", "RB1", "NF1",
            "ATM", "CDKN2A", "MLH1", "MSH2", "MSH6", "PMS2"
        ]
        
        logger.info(f"Preloading descriptions for {len(common_genes)} common genes")
        
        for gene in common_genes:
            self.get_gene_description(gene)
            time.sleep(0.1)
        
        logger.info(f"Preloading complete. Stats: {self.get_stats()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the service
    service = DescriptionService()
    
    # Preload common genes
    service.preload_common_genes()
    
    # Test individual queries
    print(f"EGFR: {service.get_gene_description('EGFR')}")
    print(f"Osimertinib: {service.get_drug_description('Osimertinib')}")
    
    # Print statistics
    print(f"\nStatistics: {json.dumps(service.get_stats(), indent=2)}")