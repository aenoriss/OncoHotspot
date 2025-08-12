-- Add comprehensive mutations for existing genes and cancer types

-- EGFR mutations (lung cancer)
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 858, 'L', 'R', 'missense', 256, 0.49, 0.98, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'EGFR' AND ct.cancer_name = 'Lung Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 790, 'T', 'M', 'missense', 78, 0.15, 0.94, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'EGFR' AND ct.cancer_name = 'Lung Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 719, 'G', 'S', 'missense', 34, 0.07, 0.86, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'EGFR' AND ct.cancer_name = 'Lung Cancer';

-- BRAF mutations (melanoma)
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 600, 'V', 'E', 'missense', 487, 0.66, 0.99, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'BRAF' AND ct.cancer_name = 'Melanoma';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 600, 'V', 'K', 'missense', 34, 0.05, 0.85, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'BRAF' AND ct.cancer_name = 'Melanoma';

-- TP53 mutations (multiple cancers)
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 273, 'R', 'H', 'missense', 234, 0.96, 0.99, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Ovarian Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 273, 'R', 'H', 'missense', 178, 0.56, 0.98, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Lung Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 273, 'R', 'H', 'missense', 89, 0.31, 0.94, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Breast Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 273, 'R', 'H', 'missense', 112, 0.25, 0.93, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Colorectal Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 175, 'R', 'H', 'missense', 134, 0.42, 0.96, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Lung Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 248, 'R', 'Q', 'missense', 67, 0.23, 0.91, 0.00005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Breast Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 248, 'R', 'W', 'missense', 156, 0.64, 0.97, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Ovarian Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 273, 'R', 'C', 'missense', 89, 0.44, 0.93, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Glioblastoma';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 220, 'Y', 'C', 'missense', 43, 0.28, 0.88, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Pancreatic Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 249, 'R', 'S', 'missense', 98, 0.41, 0.94, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'TP53' AND ct.cancer_name = 'Liver Cancer';

-- PIK3CA mutations (breast cancer)
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 1047, 'H', 'R', 'missense', 167, 0.58, 0.97, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'PIK3CA' AND ct.cancer_name = 'Breast Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 545, 'E', 'K', 'missense', 134, 0.47, 0.95, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'PIK3CA' AND ct.cancer_name = 'Breast Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 545, 'E', 'K', 'missense', 45, 0.10, 0.85, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'PIK3CA' AND ct.cancer_name = 'Colorectal Cancer';

-- APC mutations (colorectal cancer)  
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 1450, 'Q', 'X', 'nonsense', 234, 0.53, 0.98, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'APC' AND ct.cancer_name = 'Colorectal Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 1309, 'E', 'X', 'nonsense', 178, 0.40, 0.96, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'APC' AND ct.cancer_name = 'Colorectal Cancer';

-- IDH1 mutations (glioblastoma)
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 132, 'R', 'H', 'missense', 178, 0.88, 0.99, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'IDH1' AND ct.cancer_name = 'Glioblastoma';

-- More KRAS mutations
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 12, 'G', 'V', 'missense', 156, 0.40, 0.96, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'KRAS' AND ct.cancer_name = 'Pancreatic Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 12, 'G', 'V', 'missense', 92, 0.21, 0.92, 0.00005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'KRAS' AND ct.cancer_name = 'Colorectal Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 12, 'G', 'C', 'missense', 45, 0.14, 0.88, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'KRAS' AND ct.cancer_name = 'Lung Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 13, 'G', 'D', 'missense', 45, 0.11, 0.88, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'KRAS' AND ct.cancer_name = 'Pancreatic Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 13, 'G', 'D', 'missense', 67, 0.15, 0.91, 0.00005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'KRAS' AND ct.cancer_name = 'Colorectal Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 61, 'Q', 'H', 'missense', 42, 0.13, 0.87, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'KRAS' AND ct.cancer_name = 'Lung Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 61, 'Q', 'R', 'missense', 38, 0.09, 0.84, 0.0005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'KRAS' AND ct.cancer_name = 'Colorectal Cancer';

-- PTEN mutations
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 130, 'R', 'X', 'nonsense', 89, 0.44, 0.93, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'PTEN' AND ct.cancer_name = 'Glioblastoma';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 173, 'R', 'C', 'missense', 34, 0.12, 0.84, 0.0005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'PTEN' AND ct.cancer_name = 'Breast Cancer';

-- BRCA1/BRCA2 mutations
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 1694, 'S', 'X', 'nonsense', 89, 0.31, 0.93, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'BRCA1' AND ct.cancer_name = 'Breast Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 1694, 'S', 'X', 'nonsense', 112, 0.46, 0.95, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'BRCA1' AND ct.cancer_name = 'Ovarian Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 3036, 'E', 'X', 'nonsense', 67, 0.23, 0.90, 0.00005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'BRCA2' AND ct.cancer_name = 'Breast Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 3036, 'E', 'X', 'nonsense', 78, 0.32, 0.92, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'BRCA2' AND ct.cancer_name = 'Ovarian Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 3036, 'E', 'X', 'nonsense', 23, 0.15, 0.81, 0.001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'BRCA2' AND ct.cancer_name = 'Pancreatic Cancer';

-- MYC amplifications
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 0, 'WT', 'AMP', 'amplification', 145, 0.32, 0.94, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'MYC' AND ct.cancer_name = 'Lung Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 0, 'WT', 'AMP', 'amplification', 89, 0.18, 0.89, 0.00005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'MYC' AND ct.cancer_name = 'Breast Cancer';

-- HER2 amplifications
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 0, 'WT', 'AMP', 'amplification', 234, 0.25, 0.97, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'HER2' AND ct.cancer_name = 'Breast Cancer';

-- ALK fusions
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 0, 'WT', 'EML4-ALK', 'fusion', 67, 0.04, 0.92, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'ALK' AND ct.cancer_name = 'Lung Cancer';

-- NRAS mutations
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 61, 'Q', 'R', 'missense', 234, 0.32, 0.95, 0.00001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'NRAS' AND ct.cancer_name = 'Melanoma';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 61, 'Q', 'R', 'missense', 56, 0.13, 0.86, 0.0001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'NRAS' AND ct.cancer_name = 'Colorectal Cancer';

-- CTNNB1 mutations
INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 45, 'S', 'F', 'missense', 67, 0.28, 0.90, 0.00005
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'CTNNB1' AND ct.cancer_name = 'Liver Cancer';

INSERT OR IGNORE INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, 41, 'T', 'A', 'missense', 34, 0.08, 0.80, 0.001
FROM genes g, cancer_types ct WHERE g.gene_symbol = 'CTNNB1' AND ct.cancer_name = 'Colorectal Cancer';

SELECT COUNT(*) as total_mutations FROM mutations;