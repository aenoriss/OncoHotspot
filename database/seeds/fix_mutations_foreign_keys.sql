-- Fix foreign key mismatch in mutations table
-- Update cancer_type_id references to match actual cancer_types table IDs

-- First, let's create a mapping and update the mutations table
-- Delete existing mutations and re-insert with correct cancer_type_id references

DELETE FROM mutations;

-- Insert corrected mutation data with proper foreign key relationships
-- TP53 mutations in different cancer types
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    175, 'C', 'A', 'missense', 1245, 15625, 0.08, 0.95, 0.001
FROM genes g WHERE g.gene_symbol = 'TP53';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    248, 'C', 'T', 'missense', 987, 15625, 0.06, 0.94, 0.002
FROM genes g WHERE g.gene_symbol = 'TP53';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    273, 'C', 'T', 'missense', 1156, 15625, 0.07, 0.96, 0.001
FROM genes g WHERE g.gene_symbol = 'TP53';

-- TP53 in Breast Cancer
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    23, -- Breast
    175, 'C', 'A', 'missense', 2341, 19531, 0.12, 0.97, 0.001
FROM genes g WHERE g.gene_symbol = 'TP53';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    23, -- Breast
    248, 'C', 'A', 'missense', 1876, 19531, 0.10, 0.95, 0.002
FROM genes g WHERE g.gene_symbol = 'TP53';

-- KRAS mutations
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    24, -- Colorectal
    12, 'G', 'T', 'missense', 3654, 18742, 0.19, 0.98, 0.001
FROM genes g WHERE g.gene_symbol = 'KRAS';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    24, -- Colorectal
    13, 'G', 'A', 'missense', 2987, 18742, 0.16, 0.97, 0.001
FROM genes g WHERE g.gene_symbol = 'KRAS';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    26, -- Pancreatic
    12, 'G', 'T', 'missense', 4521, 12365, 0.37, 0.99, 0.001
FROM genes g WHERE g.gene_symbol = 'KRAS';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    12, 'G', 'T', 'missense', 1987, 15625, 0.13, 0.96, 0.001
FROM genes g WHERE g.gene_symbol = 'KRAS';

-- EGFR mutations
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    858, 'T', 'G', 'missense', 2145, 15625, 0.14, 0.97, 0.001
FROM genes g WHERE g.gene_symbol = 'EGFR';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    790, 'T', 'C', 'missense', 1234, 15625, 0.08, 0.95, 0.001
FROM genes g WHERE g.gene_symbol = 'EGFR';

-- BRAF mutations
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    25, -- Melanoma
    600, 'T', 'A', 'missense', 4287, 8945, 0.48, 0.99, 0.001
FROM genes g WHERE g.gene_symbol = 'BRAF';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    24, -- Colorectal
    600, 'T', 'A', 'missense', 876, 18742, 0.05, 0.87, 0.005
FROM genes g WHERE g.gene_symbol = 'BRAF';

-- PIK3CA mutations
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    23, -- Breast
    545, 'G', 'A', 'missense', 3214, 19531, 0.16, 0.97, 0.001
FROM genes g WHERE g.gene_symbol = 'PIK3CA';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    23, -- Breast
    1047, 'C', 'T', 'missense', 2987, 19531, 0.15, 0.96, 0.001
FROM genes g WHERE g.gene_symbol = 'PIK3CA';

-- APC mutations
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    24, -- Colorectal
    1450, 'C', 'T', 'truncating', 4987, 18742, 0.27, 0.98, 0.001
FROM genes g WHERE g.gene_symbol = 'APC';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    24, -- Colorectal
    1556, 'G', 'A', 'truncating', 3456, 18742, 0.18, 0.97, 0.001
FROM genes g WHERE g.gene_symbol = 'APC';

-- ALK mutations/fusions
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    1174, 'G', 'T', 'fusion', 876, 15625, 0.06, 0.93, 0.001
FROM genes g WHERE g.gene_symbol = 'ALK';

-- HER2 amplification (represented as position for simplicity)
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    23, -- Breast
    655, 'G', 'A', 'amplification', 3876, 19531, 0.20, 0.98, 0.001
FROM genes g WHERE g.gene_symbol = 'HER2';

-- RET fusions
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    21, -- NSCLC
    918, 'G', 'T', 'fusion', 234, 15625, 0.01, 0.89, 0.01
FROM genes g WHERE g.gene_symbol = 'RET';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    30, -- Thyroid
    918, 'G', 'T', 'fusion', 1456, 5632, 0.26, 0.97, 0.001
FROM genes g WHERE g.gene_symbol = 'RET';

-- FLT3 mutations (AML)
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    32, -- AML
    835, 'G', 'A', 'missense', 987, 3456, 0.29, 0.98, 0.001
FROM genes g WHERE g.gene_symbol = 'FLT3';

-- IDH1 mutations (Glioblastoma)
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    29, -- Glioblastoma
    132, 'C', 'T', 'missense', 1234, 4567, 0.27, 0.97, 0.001
FROM genes g WHERE g.gene_symbol = 'IDH1';

-- VHL mutations (Kidney cancer)
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    31, -- Kidney
    167, 'G', 'A', 'truncating', 2345, 6789, 0.35, 0.98, 0.001
FROM genes g WHERE g.gene_symbol = 'VHL';

-- MYC amplification (Multiple cancer types)
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    35, -- Myeloma
    61, 'G', 'A', 'amplification', 1567, 2345, 0.67, 0.99, 0.001
FROM genes g WHERE g.gene_symbol = 'MYC';

-- PTEN mutations (Multiple cancer types)
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    29, -- Glioblastoma
    130, 'G', 'A', 'truncating', 1876, 4567, 0.41, 0.98, 0.001
FROM genes g WHERE g.gene_symbol = 'PTEN';

INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value)
SELECT 
    g.gene_id, 
    23, -- Breast
    130, 'G', 'A', 'truncating', 1234, 19531, 0.06, 0.91, 0.003
FROM genes g WHERE g.gene_symbol = 'PTEN';