#!/usr/bin/env python3
"""
Test script for stream-to-database pipeline
Tests API connections, rate limits, and database operations
"""

import os
import sys
import json
import time
import sqlite3
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PipelineTestSuite:
    """Test suite for the efficient pipeline"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "api_limits": {},
            "recommendations": []
        }
        
        # Test database path
        self.test_db = Path("test_oncohotspot.db")
        if self.test_db.exists():
            self.test_db.unlink()  # Remove old test database
    
    def test_cbioportal_api(self) -> Tuple[bool, Dict]:
        """Test cBioPortal API connection and rate limits"""
        logger.info("\n" + "="*50)
        logger.info("Testing cBioPortal API...")
        logger.info("="*50)
        
        base_url = "https://www.cbioportal.org/api"
        results = {
            "status": "unknown",
            "response_time": 0,
            "rate_limit_test": {},
            "data_test": {}
        }
        
        try:
            # Test 1: Basic connection
            start = time.time()
            response = requests.get(f"{base_url}/studies", params={"projection": "ID"})
            results["response_time"] = time.time() - start
            
            if response.status_code == 200:
                studies = response.json()
                logger.info(f"✓ Connection successful. Found {len(studies)} studies")
                logger.info(f"  Response time: {results['response_time']:.2f}s")
                results["status"] = "connected"
                results["study_count"] = len(studies)
            else:
                logger.error(f"✗ Connection failed: {response.status_code}")
                results["status"] = "failed"
                return False, results
            
            # Test 2: Rate limit testing (10 rapid requests)
            logger.info("\nTesting rate limits with 10 rapid requests...")
            rate_times = []
            rate_errors = 0
            
            for i in range(10):
                start = time.time()
                resp = requests.get(f"{base_url}/genes/TP53")
                elapsed = time.time() - start
                rate_times.append(elapsed)
                
                if resp.status_code == 429:  # Too Many Requests
                    rate_errors += 1
                    logger.warning(f"  Request {i+1}: Rate limited!")
                elif resp.status_code == 200:
                    logger.info(f"  Request {i+1}: OK ({elapsed:.2f}s)")
                else:
                    logger.warning(f"  Request {i+1}: Status {resp.status_code}")
                
                # No delay - testing limits
            
            avg_time = sum(rate_times) / len(rate_times)
            results["rate_limit_test"] = {
                "requests_sent": 10,
                "rate_limited": rate_errors,
                "avg_response_time": avg_time,
                "max_response_time": max(rate_times),
                "safe_delay": 0.1 if rate_errors == 0 else 0.5
            }
            
            logger.info(f"\nRate limit test results:")
            logger.info(f"  - Rate limited: {rate_errors}/10 requests")
            logger.info(f"  - Avg response: {avg_time:.2f}s")
            logger.info(f"  - Recommended delay: {results['rate_limit_test']['safe_delay']}s")
            
            # Test 3: Data fetching test
            logger.info("\nTesting mutation data fetching...")
            test_study = "luad_tcga_pan_can_atlas_2018"
            test_genes = ["EGFR", "KRAS", "TP53"]
            
            # Get molecular profile
            profile_resp = requests.get(f"{base_url}/studies/{test_study}/molecular-profiles")
            if profile_resp.status_code == 200:
                profiles = profile_resp.json()
                mutation_profile = next((p for p in profiles if "mutations" in p["molecularProfileId"]), None)
                
                if mutation_profile:
                    profile_id = mutation_profile["molecularProfileId"]
                    
                    # Fetch mutations
                    mutations_url = f"{base_url}/molecular-profiles/{profile_id}/mutations/fetch"
                    payload = {
                        "sampleListId": f"{test_study}_all",
                        "entrezGeneIds": [1956, 3845, 7157]  # EGFR, KRAS, TP53
                    }
                    
                    mut_resp = requests.post(mutations_url, json=payload)
                    if mut_resp.status_code == 200:
                        mutations = mut_resp.json()
                        logger.info(f"✓ Fetched {len(mutations)} mutations for {len(test_genes)} genes")
                        results["data_test"] = {
                            "success": True,
                            "mutations_fetched": len(mutations),
                            "genes_tested": test_genes
                        }
                    else:
                        logger.error(f"✗ Failed to fetch mutations: {mut_resp.status_code}")
                        results["data_test"]["success"] = False
            
            return rate_errors == 0, results
            
        except Exception as e:
            logger.error(f"✗ cBioPortal test failed: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
            return False, results
    
    def test_civic_api(self) -> Tuple[bool, Dict]:
        """Test CIViC GraphQL API"""
        logger.info("\n" + "="*50)
        logger.info("Testing CIViC API...")
        logger.info("="*50)
        
        api_url = "https://civicdb.org/api/graphql"
        results = {
            "status": "unknown",
            "response_time": 0,
            "rate_limit_test": {},
            "data_test": {}
        }
        
        try:
            # Test 1: Basic GraphQL connection
            query = """
            query TestConnection {
                genes(first: 1) {
                    totalCount
                }
            }
            """
            
            start = time.time()
            response = requests.post(
                api_url,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            results["response_time"] = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    total_genes = data["data"]["genes"]["totalCount"]
                    logger.info(f"✓ Connection successful. Found {total_genes} genes in CIViC")
                    logger.info(f"  Response time: {results['response_time']:.2f}s")
                    results["status"] = "connected"
                    results["total_genes"] = total_genes
                else:
                    logger.error(f"✗ Unexpected response format")
                    results["status"] = "failed"
                    return False, results
            else:
                logger.error(f"✗ Connection failed: {response.status_code}")
                results["status"] = "failed"
                return False, results
            
            # Test 2: Rate limit testing
            logger.info("\nTesting rate limits with 10 rapid requests...")
            rate_times = []
            rate_errors = 0
            
            simple_query = """
            query QuickTest {
                therapies(first: 1) {
                    totalCount
                }
            }
            """
            
            for i in range(10):
                start = time.time()
                resp = requests.post(
                    api_url,
                    json={"query": simple_query},
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                elapsed = time.time() - start
                rate_times.append(elapsed)
                
                if resp.status_code == 429:
                    rate_errors += 1
                    logger.warning(f"  Request {i+1}: Rate limited!")
                elif resp.status_code == 200:
                    logger.info(f"  Request {i+1}: OK ({elapsed:.2f}s)")
                else:
                    logger.warning(f"  Request {i+1}: Status {resp.status_code}")
            
            avg_time = sum(rate_times) / len(rate_times)
            results["rate_limit_test"] = {
                "requests_sent": 10,
                "rate_limited": rate_errors,
                "avg_response_time": avg_time,
                "safe_delay": 0.2 if rate_errors == 0 else 1.0
            }
            
            logger.info(f"\nRate limit test results:")
            logger.info(f"  - Rate limited: {rate_errors}/10 requests")
            logger.info(f"  - Avg response: {avg_time:.2f}s")
            logger.info(f"  - Recommended delay: {results['rate_limit_test']['safe_delay']}s")
            
            # Test 3: Data fetching
            logger.info("\nTesting variant data fetching...")
            variant_query = """
            query GetVariants {
                genes(name: "BRAF") {
                    nodes {
                        name
                        variants(first: 5) {
                            nodes {
                                name
                                variantTypes
                            }
                        }
                    }
                }
            }
            """
            
            resp = requests.post(
                api_url,
                json={"query": variant_query},
                headers={"Content-Type": "application/json"}
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if "data" in data and data["data"]["genes"]["nodes"]:
                    gene_data = data["data"]["genes"]["nodes"][0]
                    variant_count = len(gene_data["variants"]["nodes"])
                    logger.info(f"✓ Fetched {variant_count} variants for BRAF")
                    results["data_test"] = {
                        "success": True,
                        "variants_fetched": variant_count
                    }
            
            return rate_errors == 0, results
            
        except Exception as e:
            logger.error(f"✗ CIViC test failed: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
            return False, results
    
    def test_opentargets_api(self) -> Tuple[bool, Dict]:
        """Test OpenTargets API"""
        logger.info("\n" + "="*50)
        logger.info("Testing OpenTargets API...")
        logger.info("="*50)
        
        graphql_url = "https://api.platform.opentargets.org/api/v4/graphql"
        results = {
            "status": "unknown",
            "response_time": 0,
            "rate_limit_test": {},
            "data_test": {}
        }
        
        try:
            # Test 1: Basic connection with correct query structure
            # OpenTargets API doesn't have a meta endpoint, use a simple target query
            query = """
            query targetInfo {
                target(ensemblId: "ENSG00000157764") {
                    id
                    approvedSymbol
                    biotype
                }
            }
            """
            
            start = time.time()
            response = requests.post(
                graphql_url,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            results["response_time"] = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "target" in data["data"]:
                    target = data["data"]["target"]
                    logger.info(f"✓ Connection successful - Target: {target.get('approvedSymbol', 'BRAF')}")
                    logger.info(f"  Response time: {results['response_time']:.2f}s")
                    results["status"] = "connected"
                    results["target_symbol"] = target.get('approvedSymbol', 'BRAF')
                else:
                    logger.error(f"✗ Unexpected response format: {data}")
                    results["status"] = "failed"
                    return False, results
            else:
                logger.error(f"✗ Connection failed: {response.status_code}")
                if response.text:
                    logger.error(f"  Response: {response.text[:200]}")
                results["status"] = "failed"
                return False, results
            
            # Test 2: Rate limits
            logger.info("\nTesting rate limits with 10 rapid requests...")
            rate_times = []
            rate_errors = 0
            
            simple_query = """
            query simpleTarget {
                target(ensemblId: "ENSG00000157764") {
                    id
                    approvedSymbol
                }
            }
            """
            
            for i in range(10):
                start = time.time()
                resp = requests.post(
                    graphql_url,
                    json={"query": simple_query},
                    headers={"Content-Type": "application/json"}
                )
                elapsed = time.time() - start
                rate_times.append(elapsed)
                
                if resp.status_code == 429:
                    rate_errors += 1
                    logger.warning(f"  Request {i+1}: Rate limited!")
                elif resp.status_code == 200:
                    logger.info(f"  Request {i+1}: OK ({elapsed:.2f}s)")
                else:
                    logger.warning(f"  Request {i+1}: Status {resp.status_code}")
            
            avg_time = sum(rate_times) / len(rate_times)
            results["rate_limit_test"] = {
                "requests_sent": 10,
                "rate_limited": rate_errors,
                "avg_response_time": avg_time,
                "safe_delay": 0.1 if rate_errors == 0 else 0.5
            }
            
            logger.info(f"\nRate limit test results:")
            logger.info(f"  - Rate limited: {rate_errors}/10 requests")
            logger.info(f"  - Avg response: {avg_time:.2f}s")
            logger.info(f"  - Recommended delay: {results['rate_limit_test']['safe_delay']}s")
            
            # Test 3: Drug data
            logger.info("\nTesting drug-target data fetching...")
            drug_query = """
            query targetDrugs {
                target(ensemblId: "ENSG00000157764") {
                    id
                    approvedSymbol
                    knownDrugs {
                        uniqueDrugs
                        rows {
                            drug {
                                id
                                name
                                isApproved
                            }
                            phase
                        }
                    }
                }
            }
            """
            
            drug_resp = requests.post(
                graphql_url,
                json={"query": drug_query},
                headers={"Content-Type": "application/json"}
            )
            
            if drug_resp.status_code == 200:
                data = drug_resp.json()
                if "data" in data and "target" in data["data"]:
                    target_data = data["data"]["target"]
                    if target_data and "knownDrugs" in target_data:
                        drug_count = target_data["knownDrugs"].get("uniqueDrugs", 0)
                        rows = target_data["knownDrugs"].get("rows", [])
                        logger.info(f"✓ Found {drug_count} unique drugs for BRAF")
                        logger.info(f"  Total drug associations: {len(rows)}")
                        results["data_test"] = {
                            "success": True,
                            "unique_drugs": drug_count,
                            "drug_associations": len(rows)
                        }
            
            return rate_errors == 0, results
            
        except Exception as e:
            logger.error(f"✗ OpenTargets test failed: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
            return False, results
    
    def test_database_operations(self) -> Tuple[bool, Dict]:
        """Test database creation and operations"""
        logger.info("\n" + "="*50)
        logger.info("Testing Database Operations...")
        logger.info("="*50)
        
        results = {
            "status": "unknown",
            "tables_created": [],
            "insert_test": {},
            "performance": {}
        }
        
        try:
            # Create test database
            conn = sqlite3.connect(str(self.test_db))
            cursor = conn.cursor()
            
            # Create tables
            logger.info("Creating tables...")
            
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS genes (
                    gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gene_symbol VARCHAR(50) UNIQUE NOT NULL,
                    gene_name VARCHAR(200),
                    description TEXT
                );
                
                CREATE TABLE IF NOT EXISTS cancer_types (
                    cancer_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cancer_name VARCHAR(100) NOT NULL,
                    cancer_code VARCHAR(50)
                );
                
                CREATE TABLE IF NOT EXISTS mutations (
                    mutation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gene_id INTEGER NOT NULL,
                    cancer_type_id INTEGER NOT NULL,
                    protein_change VARCHAR(100),
                    mutation_count INTEGER DEFAULT 1,
                    frequency REAL,
                    FOREIGN KEY (gene_id) REFERENCES genes(gene_id),
                    FOREIGN KEY (cancer_type_id) REFERENCES cancer_types(cancer_type_id)
                );
                
                CREATE TABLE IF NOT EXISTS therapeutics (
                    therapeutic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    drug_name VARCHAR(100) NOT NULL,
                    drug_class VARCHAR(100),
                    description TEXT
                );
            """)
            
            conn.commit()
            logger.info("✓ Tables created successfully")
            results["tables_created"] = ["genes", "cancer_types", "mutations", "therapeutics"]
            
            # Test insertions
            logger.info("\nTesting batch insertions...")
            
            # Insert test data
            start_time = time.time()
            
            # Insert genes
            test_genes = [("EGFR",), ("KRAS",), ("TP53",), ("BRAF",), ("PIK3CA",)]
            cursor.executemany("INSERT OR IGNORE INTO genes (gene_symbol) VALUES (?)", test_genes)
            
            # Insert cancer types
            test_cancers = [("Lung Adenocarcinoma",), ("Breast Cancer",), ("Colorectal Cancer",)]
            cursor.executemany("INSERT OR IGNORE INTO cancer_types (cancer_name) VALUES (?)", test_cancers)
            
            # Insert mutations (1000 test mutations)
            test_mutations = []
            for i in range(1000):
                gene_id = (i % 5) + 1
                cancer_id = (i % 3) + 1
                protein_change = f"p.{chr(65 + (i % 26))}{i}{chr(65 + ((i+1) % 26))}"
                frequency = 0.01 + (i % 100) / 1000
                test_mutations.append((gene_id, cancer_id, protein_change, i+1, frequency))
            
            cursor.executemany("""
                INSERT INTO mutations (gene_id, cancer_type_id, protein_change, mutation_count, frequency)
                VALUES (?, ?, ?, ?, ?)
            """, test_mutations)
            
            conn.commit()
            insert_time = time.time() - start_time
            
            # Verify insertions
            cursor.execute("SELECT COUNT(*) FROM mutations")
            mutation_count = cursor.fetchone()[0]
            
            logger.info(f"✓ Inserted {mutation_count} mutations in {insert_time:.2f}s")
            logger.info(f"  Rate: {mutation_count/insert_time:.0f} mutations/second")
            
            results["insert_test"] = {
                "success": True,
                "mutations_inserted": mutation_count,
                "time_taken": insert_time,
                "rate": mutation_count/insert_time
            }
            
            # Test query performance
            logger.info("\nTesting query performance...")
            
            # Create indexes
            cursor.execute("CREATE INDEX idx_mut_gene ON mutations(gene_id)")
            cursor.execute("CREATE INDEX idx_mut_cancer ON mutations(cancer_type_id)")
            cursor.execute("CREATE INDEX idx_mut_freq ON mutations(frequency DESC)")
            
            # Test queries
            query_start = time.time()
            cursor.execute("""
                SELECT g.gene_symbol, c.cancer_name, COUNT(*) as mut_count
                FROM mutations m
                JOIN genes g ON m.gene_id = g.gene_id
                JOIN cancer_types c ON m.cancer_type_id = c.cancer_type_id
                GROUP BY g.gene_symbol, c.cancer_name
            """)
            results_data = cursor.fetchall()
            query_time = time.time() - query_start
            
            logger.info(f"✓ Complex query returned {len(results_data)} results in {query_time:.3f}s")
            
            results["performance"] = {
                "complex_query_time": query_time,
                "results_returned": len(results_data)
            }
            
            # Check database size
            db_size = os.path.getsize(self.test_db) / 1024 / 1024  # MB
            logger.info(f"✓ Database size: {db_size:.2f} MB")
            results["database_size_mb"] = db_size
            
            conn.close()
            results["status"] = "success"
            return True, results
            
        except Exception as e:
            logger.error(f"✗ Database test failed: {str(e)}")
            results["status"] = "error"
            results["error"] = str(e)
            return False, results
        finally:
            # Clean up test database
            if self.test_db.exists():
                self.test_db.unlink()
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("\n" + "="*60)
        logger.info("ONCOHOTSPOT PIPELINE TEST SUITE")
        logger.info("="*60)
        
        all_passed = True
        
        # Test each API
        apis_to_test = [
            ("cBioPortal", self.test_cbioportal_api),
            ("CIViC", self.test_civic_api),
            ("OpenTargets", self.test_opentargets_api),
            ("Database", self.test_database_operations)
        ]
        
        for api_name, test_func in apis_to_test:
            passed, results = test_func()
            self.test_results["tests"][api_name] = results
            
            if not passed:
                all_passed = False
                self.test_results["recommendations"].append(
                    f"⚠️ {api_name} had issues - consider adjusting rate limits or error handling"
                )
            
            # Extract rate limit recommendations
            if "rate_limit_test" in results:
                self.test_results["api_limits"][api_name] = {
                    "safe_delay_seconds": results["rate_limit_test"].get("safe_delay", 0.5),
                    "rate_limited": results["rate_limit_test"].get("rate_limited", 0) > 0
                }
        
        # Generate summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        return all_passed
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        # API Status
        logger.info("\nAPI Connectivity:")
        for api_name, results in self.test_results["tests"].items():
            status = results.get("status", "unknown")
            symbol = "✓" if status == "connected" or status == "success" else "✗"
            logger.info(f"  {symbol} {api_name}: {status}")
        
        # Rate Limits
        logger.info("\nRecommended Rate Limits:")
        for api_name, limits in self.test_results["api_limits"].items():
            delay = limits.get("safe_delay_seconds", 0.5)
            limited = limits.get("rate_limited", False)
            status = "⚠️ Rate limited" if limited else "✓ No limits detected"
            logger.info(f"  {api_name}: {delay}s delay ({status})")
        
        # Performance
        logger.info("\nPerformance Metrics:")
        
        # Database performance
        if "Database" in self.test_results["tests"]:
            db_test = self.test_results["tests"]["Database"]
            if "insert_test" in db_test and db_test["insert_test"].get("success"):
                rate = db_test["insert_test"]["rate"]
                logger.info(f"  Database insert rate: {rate:.0f} records/second")
        
        # API response times
        for api_name, results in self.test_results["tests"].items():
            if "response_time" in results:
                logger.info(f"  {api_name} response: {results['response_time']:.2f}s")
        
        # Recommendations
        if self.test_results["recommendations"]:
            logger.info("\nRecommendations:")
            for rec in self.test_results["recommendations"]:
                logger.info(f"  {rec}")
        else:
            logger.info("\n✅ All tests passed! Pipeline is ready to run.")
        
        # Estimated full pipeline metrics
        logger.info("\nEstimated Full Pipeline Metrics:")
        logger.info("  Expected mutations: ~200,000")
        logger.info("  Expected duration: 2-3 hours")
        logger.info("  Expected disk usage: 5GB peak, 150MB final")
        logger.info("  Expected API calls: ~5,000")
        
        logger.info("="*60)
    
    def save_results(self):
        """Save test results to file"""
        results_file = Path("test_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        logger.info(f"\nTest results saved to {results_file}")


def main():
    """Run test suite"""
    tester = PipelineTestSuite()
    all_passed = tester.run_all_tests()
    
    if all_passed:
        logger.info("\n✅ All tests passed! You can run the efficient pipeline with:")
        logger.info("   python pipeline_efficient.py")
    else:
        logger.info("\n⚠️ Some tests failed. Review the recommendations above.")
        logger.info("   You may need to adjust rate limits or error handling.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())