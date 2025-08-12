"""Database loader for Gold layer data"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Load aggregated data into OncoHotspot database"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database loader
        
        Args:
            db_path: Path to SQLite database
        """
        if not db_path:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                'database',
                'oncohotspot.db'
            )
        
        self.db_path = db_path
        logger.info(f"Database loader initialized with: {db_path}")
    
    def load_mutations(self, mutations: List[Dict]) -> Dict[str, Any]:
        """
        Load mutation data into database
        
        Args:
            mutations: List of aggregated mutations
            
        Returns:
            Loading statistics
        """
        stats = {
            'total_records': len(mutations),
            'inserted': 0,
            'updated': 0,
            'failed': 0,
            'genes_added': 0,
            'cancer_types_added': 0
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # First, ensure all genes and cancer types exist
            genes = set(m['gene_symbol'] for m in mutations if m.get('gene_symbol'))
            cancer_types = set(m['cancer_type'] for m in mutations if m.get('cancer_type'))
            
            stats['genes_added'] = self._ensure_genes(cursor, genes)
            stats['cancer_types_added'] = self._ensure_cancer_types(cursor, cancer_types)
            
            # Load mutations
            for mutation in mutations:
                try:
                    if self._upsert_mutation(cursor, mutation):
                        stats['inserted'] += 1
                    else:
                        stats['updated'] += 1
                except Exception as e:
                    logger.error(f"Failed to load mutation: {e}")
                    stats['failed'] += 1
            
            conn.commit()
            logger.info(f"Database loading complete: {stats}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Database loading failed: {e}")
            raise
        finally:
            conn.close()
        
        return stats
    
    def _ensure_genes(self, cursor: sqlite3.Cursor, genes: set) -> int:
        """Ensure all genes exist in database"""
        added = 0
        
        for gene in genes:
            # Check if gene exists
            cursor.execute(
                "SELECT gene_id FROM genes WHERE gene_symbol = ?",
                (gene,)
            )
            
            if not cursor.fetchone():
                # Insert new gene
                cursor.execute(
                    """
                    INSERT INTO genes (gene_symbol, gene_name, created_at, updated_at)
                    VALUES (?, ?, datetime('now'), datetime('now'))
                    """,
                    (gene, gene)  # Use symbol as name if not available
                )
                added += 1
                logger.debug(f"Added new gene: {gene}")
        
        return added
    
    def _ensure_cancer_types(self, cursor: sqlite3.Cursor, cancer_types: set) -> int:
        """Ensure all cancer types exist in database"""
        added = 0
        
        for cancer_type in cancer_types:
            # Check if cancer type exists
            cursor.execute(
                "SELECT cancer_type_id FROM cancer_types WHERE cancer_name = ?",
                (cancer_type,)
            )
            
            if not cursor.fetchone():
                # Insert new cancer type
                cursor.execute(
                    """
                    INSERT INTO cancer_types (cancer_name, created_at)
                    VALUES (?, datetime('now'))
                    """,
                    (cancer_type,)
                )
                added += 1
                logger.debug(f"Added new cancer type: {cancer_type}")
        
        return added
    
    def _upsert_mutation(self, cursor: sqlite3.Cursor, mutation: Dict) -> bool:
        """
        Insert or update a mutation record
        
        Args:
            cursor: Database cursor
            mutation: Mutation data
            
        Returns:
            True if inserted, False if updated
        """
        # Get gene_id
        cursor.execute(
            "SELECT gene_id FROM genes WHERE gene_symbol = ?",
            (mutation['gene_symbol'],)
        )
        gene_result = cursor.fetchone()
        if not gene_result:
            raise ValueError(f"Gene not found: {mutation['gene_symbol']}")
        gene_id = gene_result[0]
        
        # Get cancer_type_id
        cursor.execute(
            "SELECT cancer_type_id FROM cancer_types WHERE cancer_name = ?",
            (mutation['cancer_type'],)
        )
        cancer_result = cursor.fetchone()
        if not cancer_result:
            raise ValueError(f"Cancer type not found: {mutation['cancer_type']}")
        cancer_type_id = cancer_result[0]
        
        # Check if mutation exists
        cursor.execute(
            """
            SELECT mutation_id FROM mutations
            WHERE gene_id = ? AND cancer_type_id = ? AND position = ?
                AND ref_allele = ? AND alt_allele = ?
            """,
            (
                gene_id,
                cancer_type_id,
                mutation.get('position', 0),
                mutation.get('ref_allele', ''),
                mutation.get('alt_allele', '')
            )
        )
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing mutation
            cursor.execute(
                """
                UPDATE mutations
                SET mutation_count = ?,
                    total_samples = ?,
                    frequency = ?,
                    significance_score = ?,
                    updated_at = datetime('now')
                WHERE mutation_id = ?
                """,
                (
                    mutation.get('mutation_count', 0),
                    mutation.get('sample_count', 0),
                    mutation.get('frequency', 0),
                    mutation.get('significance_score', 0),
                    existing[0]
                )
            )
            return False
        else:
            # Insert new mutation
            cursor.execute(
                """
                INSERT INTO mutations (
                    gene_id, cancer_type_id, position, ref_allele, alt_allele,
                    mutation_type, mutation_count, total_samples, frequency,
                    significance_score, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    gene_id,
                    cancer_type_id,
                    mutation.get('position', 0),
                    mutation.get('ref_allele', ''),
                    mutation.get('alt_allele', ''),
                    mutation.get('mutation_type', 'missense'),
                    mutation.get('mutation_count', 0),
                    mutation.get('sample_count', 0),
                    mutation.get('frequency', 0),
                    mutation.get('significance_score', 0)
                )
            )
            return True
    
    def load_therapeutics(self, therapeutics: List[Dict]) -> Dict[str, Any]:
        """
        Load therapeutic data into database
        
        Args:
            therapeutics: List of therapeutic associations
            
        Returns:
            Loading statistics
        """
        stats = {
            'total_records': len(therapeutics),
            'inserted': 0,
            'updated': 0,
            'failed': 0
        }
        
        if not therapeutics:
            logger.info("No therapeutic data to load")
            return stats
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for therapeutic in therapeutics:
                try:
                    # Insert therapeutic (simplified version)
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO therapeutics (
                            therapeutic_name, target_gene, indication, status,
                            mechanism_of_action, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                        """,
                        (
                            therapeutic.get('name', ''),
                            therapeutic.get('target_gene', ''),
                            therapeutic.get('indication', ''),
                            therapeutic.get('status', 'investigational'),
                            therapeutic.get('mechanism', '')
                        )
                    )
                    if cursor.rowcount > 0:
                        stats['inserted'] += 1
                    else:
                        stats['updated'] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to load therapeutic {therapeutic}: {e}")
                    stats['failed'] += 1
                    
            conn.commit()
            logger.info(f"Loaded {stats['inserted']} therapeutics, updated {stats['updated']}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            conn.close()
            
        return stats
    
    def load_associations(self, associations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load gene-drug associations into database
        
        Args:
            associations: Dictionary of gene-drug associations
            
        Returns:
            Loading statistics
        """
        stats = {
            'total_records': len(associations) if isinstance(associations, dict) else 0,
            'inserted': 0,
            'failed': 0
        }
        
        if not associations:
            logger.info("No association data to load")
            return stats
        
        # For now, just log the associations (could be expanded to store in a separate table)
        logger.info(f"Would load {stats['total_records']} gene-drug associations")
        return stats
    
    def clear_existing_data(self, table: str = 'mutations') -> int:
        """
        Clear existing data from a table
        
        Args:
            table: Table name to clear
            
        Returns:
            Number of rows deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"DELETE FROM {table}")
            conn.commit()
            
            logger.info(f"Cleared {count} rows from {table}")
            return count
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to clear {table}: {e}")
            raise
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Count records in each table
            tables = ['genes', 'cancer_types', 'mutations', 'therapeutics']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Get unique combinations
            cursor.execute("""
                SELECT COUNT(DISTINCT gene_id || '-' || cancer_type_id)
                FROM mutations
            """)
            stats['unique_gene_cancer_pairs'] = cursor.fetchone()[0]
            
            return stats
            
        finally:
            conn.close()