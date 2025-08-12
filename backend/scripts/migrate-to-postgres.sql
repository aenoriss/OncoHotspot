-- PostgreSQL schema for OncoHotspot
-- Based on SQLite schema

CREATE TABLE IF NOT EXISTS genes (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) UNIQUE NOT NULL,
    name TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cancer_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mutations (
    id SERIAL PRIMARY KEY,
    gene_id INTEGER REFERENCES genes(id),
    cancer_type_id INTEGER REFERENCES cancer_types(id),
    mutation_type VARCHAR(100),
    protein_change VARCHAR(200),
    frequency DECIMAL(5,4),
    sample_count INTEGER,
    total_samples INTEGER,
    clinical_significance TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS therapeutics (
    id SERIAL PRIMARY KEY,
    gene_id INTEGER REFERENCES genes(id),
    drug_name VARCHAR(200) NOT NULL,
    drug_class VARCHAR(200),
    interaction_type VARCHAR(100),
    approval_status VARCHAR(100),
    evidence_level VARCHAR(50),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mutations_gene ON mutations(gene_id);
CREATE INDEX idx_mutations_cancer ON mutations(cancer_type_id);
CREATE INDEX idx_therapeutics_gene ON therapeutics(gene_id);