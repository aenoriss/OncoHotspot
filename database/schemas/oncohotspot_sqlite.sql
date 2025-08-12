-- OncoHotspot SQLite Database Schema
-- Cancer mutation heatmap and therapeutic targets database

-- Genes table - stores oncogene information
CREATE TABLE genes (
    gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_symbol VARCHAR(50) NOT NULL UNIQUE,
    gene_name VARCHAR(255),
    chromosome VARCHAR(10),
    start_position INTEGER,
    end_position INTEGER,
    strand VARCHAR(1) CHECK (strand IN ('+', '-')),
    gene_type VARCHAR(50),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gene_symbol ON genes(gene_symbol);
CREATE INDEX idx_chromosome ON genes(chromosome);

-- Cancer types table
CREATE TABLE cancer_types (
    cancer_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cancer_name VARCHAR(100) NOT NULL UNIQUE,
    cancer_category VARCHAR(50),
    tissue_origin VARCHAR(100),
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cancer_name ON cancer_types(cancer_name);
CREATE INDEX idx_cancer_category ON cancer_types(cancer_category);

-- Mutations table - stores mutation data
CREATE TABLE mutations (
    mutation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id INTEGER NOT NULL,
    cancer_type_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    ref_allele VARCHAR(10),
    alt_allele VARCHAR(10),
    mutation_type VARCHAR(50),
    mutation_count INTEGER DEFAULT 1,
    total_samples INTEGER,
    frequency DECIMAL(5,4),
    significance_score DECIMAL(3,2),
    p_value DECIMAL(15,10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id),
    FOREIGN KEY (cancer_type_id) REFERENCES cancer_types(cancer_type_id)
);

CREATE INDEX idx_gene_cancer ON mutations(gene_id, cancer_type_id);
CREATE INDEX idx_position ON mutations(position);
CREATE INDEX idx_frequency ON mutations(frequency);
CREATE INDEX idx_significance ON mutations(significance_score);
CREATE UNIQUE INDEX unique_mutation ON mutations(gene_id, cancer_type_id, position, ref_allele, alt_allele);

-- Therapeutic targets table
CREATE TABLE therapeutics (
    therapeutic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id INTEGER NOT NULL,
    drug_name VARCHAR(100) NOT NULL,
    mechanism_of_action VARCHAR(255),
    clinical_status VARCHAR(20) CHECK (clinical_status IN ('Preclinical', 'Phase I', 'Phase II', 'Phase III', 'Approved', 'Withdrawn')),
    indication TEXT,
    fda_approval_date DATE,
    manufacturer VARCHAR(100),
    target_mutations TEXT,
    efficacy_data TEXT, -- JSON as TEXT in SQLite
    side_effects TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE INDEX idx_drug_name ON therapeutics(drug_name);
CREATE INDEX idx_clinical_status ON therapeutics(clinical_status);
CREATE INDEX idx_gene_drug ON therapeutics(gene_id, drug_name);

-- Cancer type - therapeutic relationships
CREATE TABLE therapeutic_cancer_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    therapeutic_id INTEGER NOT NULL,
    cancer_type_id INTEGER NOT NULL,
    efficacy_rating VARCHAR(10) CHECK (efficacy_rating IN ('Low', 'Medium', 'High')),
    response_rate DECIMAL(5,2),
    progression_free_survival DECIMAL(6,2),
    overall_survival DECIMAL(6,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (therapeutic_id) REFERENCES therapeutics(therapeutic_id),
    FOREIGN KEY (cancer_type_id) REFERENCES cancer_types(cancer_type_id),
    UNIQUE (therapeutic_id, cancer_type_id)
);

-- Clinical studies table
CREATE TABLE clinical_studies (
    study_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nct_id VARCHAR(20) UNIQUE,
    title VARCHAR(500),
    phase VARCHAR(20) CHECK (phase IN ('Phase I', 'Phase II', 'Phase III', 'Phase IV')),
    status VARCHAR(50),
    start_date DATE,
    completion_date DATE,
    participant_count INTEGER,
    primary_endpoint TEXT,
    secondary_endpoints TEXT,
    inclusion_criteria TEXT,
    exclusion_criteria TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nct_id ON clinical_studies(nct_id);
CREATE INDEX idx_phase ON clinical_studies(phase);
CREATE INDEX idx_status ON clinical_studies(status);

-- Link studies to therapeutics
CREATE TABLE study_therapeutics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_id INTEGER NOT NULL,
    therapeutic_id INTEGER NOT NULL,
    arm_description TEXT,
    dosage VARCHAR(100),
    administration_route VARCHAR(50),
    FOREIGN KEY (study_id) REFERENCES clinical_studies(study_id),
    FOREIGN KEY (therapeutic_id) REFERENCES therapeutics(therapeutic_id),
    UNIQUE (study_id, therapeutic_id)
);

-- Mutation hotspots for quick heatmap generation
CREATE TABLE mutation_hotspots (
    hotspot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id INTEGER NOT NULL,
    position_start INTEGER NOT NULL,
    position_end INTEGER NOT NULL,
    hotspot_name VARCHAR(100),
    mutation_density DECIMAL(6,3),
    clinical_significance VARCHAR(50),
    domain_annotation VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE INDEX idx_gene_position ON mutation_hotspots(gene_id, position_start, position_end);
CREATE INDEX idx_mutation_density ON mutation_hotspots(mutation_density);

-- Triggers to update updated_at timestamp
CREATE TRIGGER update_genes_updated_at 
AFTER UPDATE ON genes
FOR EACH ROW
BEGIN
    UPDATE genes SET updated_at = CURRENT_TIMESTAMP WHERE gene_id = NEW.gene_id;
END;

CREATE TRIGGER update_mutations_updated_at 
AFTER UPDATE ON mutations
FOR EACH ROW
BEGIN
    UPDATE mutations SET updated_at = CURRENT_TIMESTAMP WHERE mutation_id = NEW.mutation_id;
END;

CREATE TRIGGER update_therapeutics_updated_at 
AFTER UPDATE ON therapeutics
FOR EACH ROW
BEGIN
    UPDATE therapeutics SET updated_at = CURRENT_TIMESTAMP WHERE therapeutic_id = NEW.therapeutic_id;
END;