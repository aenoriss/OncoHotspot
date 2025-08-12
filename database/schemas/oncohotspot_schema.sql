-- OncoHotspot Database Schema
-- Cancer mutation heatmap and therapeutic targets database

CREATE DATABASE IF NOT EXISTS oncohotspot;
USE oncohotspot;

-- Genes table - stores oncogene information
CREATE TABLE genes (
    gene_id INT PRIMARY KEY AUTO_INCREMENT,
    gene_symbol VARCHAR(50) NOT NULL UNIQUE,
    gene_name VARCHAR(255),
    chromosome VARCHAR(10),
    start_position BIGINT,
    end_position BIGINT,
    strand ENUM('+', '-'),
    gene_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_gene_symbol (gene_symbol),
    INDEX idx_chromosome (chromosome)
);

-- Cancer types table
CREATE TABLE cancer_types (
    cancer_type_id INT PRIMARY KEY AUTO_INCREMENT,
    cancer_name VARCHAR(100) NOT NULL UNIQUE,
    cancer_category VARCHAR(50),
    tissue_origin VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cancer_name (cancer_name),
    INDEX idx_cancer_category (cancer_category)
);

-- Mutations table - stores mutation data
CREATE TABLE mutations (
    mutation_id INT PRIMARY KEY AUTO_INCREMENT,
    gene_id INT NOT NULL,
    cancer_type_id INT NOT NULL,
    position INT NOT NULL,
    ref_allele VARCHAR(10),
    alt_allele VARCHAR(10),
    mutation_type VARCHAR(50),
    mutation_count INT DEFAULT 1,
    total_samples INT,
    frequency DECIMAL(5,4),
    significance_score DECIMAL(3,2),
    p_value DECIMAL(15,10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id),
    FOREIGN KEY (cancer_type_id) REFERENCES cancer_types(cancer_type_id),
    INDEX idx_gene_cancer (gene_id, cancer_type_id),
    INDEX idx_position (position),
    INDEX idx_frequency (frequency),
    INDEX idx_significance (significance_score),
    UNIQUE KEY unique_mutation (gene_id, cancer_type_id, position, ref_allele, alt_allele)
);

-- Therapeutic targets table
CREATE TABLE therapeutics (
    therapeutic_id INT PRIMARY KEY AUTO_INCREMENT,
    gene_id INT NOT NULL,
    drug_name VARCHAR(100) NOT NULL,
    mechanism_of_action VARCHAR(255),
    clinical_status ENUM('Preclinical', 'Phase I', 'Phase II', 'Phase III', 'Approved', 'Withdrawn'),
    indication TEXT,
    fda_approval_date DATE,
    manufacturer VARCHAR(100),
    target_mutations TEXT,
    efficacy_data JSON,
    side_effects TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id),
    INDEX idx_drug_name (drug_name),
    INDEX idx_clinical_status (clinical_status),
    INDEX idx_gene_drug (gene_id, drug_name)
);

-- Cancer type - therapeutic relationships
CREATE TABLE therapeutic_cancer_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    therapeutic_id INT NOT NULL,
    cancer_type_id INT NOT NULL,
    efficacy_rating ENUM('Low', 'Medium', 'High'),
    response_rate DECIMAL(5,2),
    progression_free_survival DECIMAL(6,2),
    overall_survival DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (therapeutic_id) REFERENCES therapeutics(therapeutic_id),
    FOREIGN KEY (cancer_type_id) REFERENCES cancer_types(cancer_type_id),
    UNIQUE KEY unique_therapeutic_cancer (therapeutic_id, cancer_type_id)
);

-- Clinical studies table
CREATE TABLE clinical_studies (
    study_id INT PRIMARY KEY AUTO_INCREMENT,
    nct_id VARCHAR(20) UNIQUE,
    title VARCHAR(500),
    phase ENUM('Phase I', 'Phase II', 'Phase III', 'Phase IV'),
    status VARCHAR(50),
    start_date DATE,
    completion_date DATE,
    participant_count INT,
    primary_endpoint TEXT,
    secondary_endpoints TEXT,
    inclusion_criteria TEXT,
    exclusion_criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nct_id (nct_id),
    INDEX idx_phase (phase),
    INDEX idx_status (status)
);

-- Link studies to therapeutics
CREATE TABLE study_therapeutics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    study_id INT NOT NULL,
    therapeutic_id INT NOT NULL,
    arm_description TEXT,
    dosage VARCHAR(100),
    administration_route VARCHAR(50),
    FOREIGN KEY (study_id) REFERENCES clinical_studies(study_id),
    FOREIGN KEY (therapeutic_id) REFERENCES therapeutics(therapeutic_id),
    UNIQUE KEY unique_study_therapeutic (study_id, therapeutic_id)
);

-- Mutation hotspots for quick heatmap generation
CREATE TABLE mutation_hotspots (
    hotspot_id INT PRIMARY KEY AUTO_INCREMENT,
    gene_id INT NOT NULL,
    position_start INT NOT NULL,
    position_end INT NOT NULL,
    hotspot_name VARCHAR(100),
    mutation_density DECIMAL(6,3),
    clinical_significance VARCHAR(50),
    domain_annotation VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id),
    INDEX idx_gene_position (gene_id, position_start, position_end),
    INDEX idx_mutation_density (mutation_density)
);