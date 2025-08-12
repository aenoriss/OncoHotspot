-- Comprehensive cancer mutation data population script
-- Adapted for the actual database schema

-- Clear existing data 
DELETE FROM mutations;
DELETE FROM cancer_types;
DELETE FROM genes;
DELETE FROM therapeutics;
DELETE FROM mutation_hotspots;
DELETE FROM clinical_studies;
DELETE FROM study_therapeutics;
DELETE FROM therapeutic_cancer_types;

-- Reset auto-increment counters
DELETE FROM sqlite_sequence;

-- Insert major cancer types
INSERT INTO cancer_types (cancer_name, tissue_type, prevalence_per_100k) VALUES
('Lung Cancer', 'Lung', 57.3),
('Breast Cancer', 'Breast', 124.7),
('Colorectal Cancer', 'Colon', 38.4),
('Melanoma', 'Skin', 21.6),
('Pancreatic Cancer', 'Pancreas', 13.1),
('Liver Cancer', 'Liver', 8.9),
('Ovarian Cancer', 'Ovary', 11.1),
('Glioblastoma', 'Brain', 3.2),
('Thyroid Cancer', 'Thyroid', 13.5),
('Kidney Cancer', 'Kidney', 16.4),
('Bladder Cancer', 'Bladder', 19.8),
('Prostate Cancer', 'Prostate', 109.8),
('Gastric Cancer', 'Stomach', 5.6),
('Head and Neck Cancer', 'Head/Neck', 14.9),
('Leukemia (AML)', 'Blood', 13.7);

-- Insert major oncogenes and tumor suppressors
INSERT INTO genes (gene_symbol, gene_name, chromosome, gene_type, description) VALUES
-- Major oncogenes
('KRAS', 'KRAS proto-oncogene', '12p12.1', 'oncogene', 'RAS family member, frequently mutated in cancer'),
('EGFR', 'Epidermal growth factor receptor', '7p11.2', 'oncogene', 'Receptor tyrosine kinase, driver in lung cancer'),
('BRAF', 'B-Raf proto-oncogene', '7q34', 'oncogene', 'Serine/threonine kinase in MAPK pathway'),
('PIK3CA', 'Phosphatidylinositol-3-kinase catalytic alpha', '3q26.32', 'oncogene', 'PI3K/AKT pathway activator'),
('MYC', 'MYC proto-oncogene', '8q24.21', 'oncogene', 'Transcription factor, cell proliferation'),
('ALK', 'Anaplastic lymphoma kinase', '2p23.1', 'oncogene', 'Receptor tyrosine kinase, fusion driver'),
('MET', 'MET proto-oncogene', '7q31.2', 'oncogene', 'Hepatocyte growth factor receptor'),
('HER2', 'Human epidermal growth factor receptor 2', '17q12', 'oncogene', 'ERBB2, amplified in breast cancer'),
('FLT3', 'FMS-like tyrosine kinase 3', '13q12.2', 'oncogene', 'Receptor tyrosine kinase in AML'),
('KIT', 'KIT proto-oncogene', '4q12', 'oncogene', 'Receptor tyrosine kinase, GIST driver'),
('RET', 'RET proto-oncogene', '10q11.21', 'oncogene', 'Receptor tyrosine kinase, fusion driver'),
('NRAS', 'NRAS proto-oncogene', '1p13.2', 'oncogene', 'RAS family member'),
('JAK2', 'Janus kinase 2', '9p24.1', 'oncogene', 'JAK/STAT signaling pathway'),
('IDH1', 'Isocitrate dehydrogenase 1', '2q34', 'oncogene', 'Metabolic enzyme, neomorphic in cancer'),
('IDH2', 'Isocitrate dehydrogenase 2', '15q26.1', 'oncogene', 'Metabolic enzyme, neomorphic in cancer'),
('FGFR3', 'Fibroblast growth factor receptor 3', '4p16.3', 'oncogene', 'Receptor tyrosine kinase'),
('ERBB3', 'Erb-b2 receptor tyrosine kinase 3', '12q13.2', 'oncogene', 'HER3, EGF receptor family'),
('CDK4', 'Cyclin-dependent kinase 4', '12q14.1', 'oncogene', 'Cell cycle regulator'),
('MDM2', 'MDM2 proto-oncogene', '12q15', 'oncogene', 'p53 negative regulator'),
('CCND1', 'Cyclin D1', '11q13.3', 'oncogene', 'Cell cycle G1/S transition'),

-- Major tumor suppressors
('TP53', 'Tumor protein p53', '17p13.1', 'tumor_suppressor', 'Guardian of the genome, most frequently mutated'),
('APC', 'Adenomatous polyposis coli', '5q22.2', 'tumor_suppressor', 'WNT pathway regulator, colorectal cancer'),
('PTEN', 'Phosphatase and tensin homolog', '10q23.31', 'tumor_suppressor', 'PI3K/AKT pathway antagonist'),
('RB1', 'Retinoblastoma protein', '13q14.2', 'tumor_suppressor', 'Cell cycle checkpoint'),
('VHL', 'Von Hippel-Lindau', '3p25.3', 'tumor_suppressor', 'HIF pathway regulator, kidney cancer'),
('BRCA1', 'Breast cancer type 1', '17q21.31', 'tumor_suppressor', 'DNA damage repair, homologous recombination'),
('BRCA2', 'Breast cancer type 2', '13q13.1', 'tumor_suppressor', 'DNA damage repair, homologous recombination'),
('ATM', 'Ataxia telangiectasia mutated', '11q22.3', 'tumor_suppressor', 'DNA damage checkpoint'),
('CDKN2A', 'Cyclin-dependent kinase inhibitor 2A', '9p21.3', 'tumor_suppressor', 'p16/p14ARF, cell cycle inhibitor'),
('STK11', 'Serine/threonine kinase 11', '19p13.3', 'tumor_suppressor', 'LKB1, mTOR pathway regulator'),
('NF1', 'Neurofibromin 1', '17q11.2', 'tumor_suppressor', 'RAS/MAPK negative regulator'),
('SMAD4', 'SMAD family member 4', '18q21.2', 'tumor_suppressor', 'TGF-β signaling'),
('MLH1', 'MutL homolog 1', '3p22.2', 'tumor_suppressor', 'DNA mismatch repair'),
('MSH2', 'MutS homolog 2', '2p21', 'tumor_suppressor', 'DNA mismatch repair'),
('CTNNB1', 'Catenin beta 1', '3p21.3', 'oncogene', 'Beta-catenin, WNT pathway'),
('FBXW7', 'F-box and WD repeat domain containing 7', '4q31.3', 'tumor_suppressor', 'SCF complex, protein degradation'),
('KEAP1', 'Kelch-like ECH-associated protein 1', '19p13.2', 'tumor_suppressor', 'NRF2 pathway regulator'),
('ARID1A', 'AT-rich interaction domain 1A', '1p36.11', 'tumor_suppressor', 'SWI/SNF chromatin remodeling'),
('TSC1', 'Tuberous sclerosis 1', '9q34.13', 'tumor_suppressor', 'mTOR pathway regulator'),
('TSC2', 'Tuberous sclerosis 2', '16p13.3', 'tumor_suppressor', 'mTOR pathway regulator');

-- Insert comprehensive mutation data with correct schema
-- Using gene_id and cancer_type_id references
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) 
SELECT g.gene_id, ct.cancer_type_id, m.position, m.ref_allele, m.alt_allele, m.mutation_type, m.mutation_count, m.frequency, m.significance_score, m.p_value
FROM (
    -- KRAS mutations (pancreatic, colorectal, lung)
    SELECT 'KRAS' as gene, 'Pancreatic Cancer' as cancer, 12 as position, 'G' as ref_allele, 'D' as alt_allele, 'missense' as mutation_type, 342 as mutation_count, 0.87 as frequency, 0.99 as significance_score, 0.00001 as p_value
    UNION ALL SELECT 'KRAS', 'Colorectal Cancer', 12, 'G', 'D', 'missense', 185, 0.42, 0.97, 0.00001
    UNION ALL SELECT 'KRAS', 'Lung Cancer', 12, 'G', 'D', 'missense', 98, 0.31, 0.95, 0.00001
    UNION ALL SELECT 'KRAS', 'Pancreatic Cancer', 12, 'G', 'V', 'missense', 156, 0.40, 0.96, 0.00001
    UNION ALL SELECT 'KRAS', 'Colorectal Cancer', 12, 'G', 'V', 'missense', 92, 0.21, 0.92, 0.00005
    UNION ALL SELECT 'KRAS', 'Lung Cancer', 12, 'G', 'C', 'missense', 45, 0.14, 0.88, 0.0001
    UNION ALL SELECT 'KRAS', 'Pancreatic Cancer', 13, 'G', 'D', 'missense', 45, 0.11, 0.88, 0.0001
    UNION ALL SELECT 'KRAS', 'Colorectal Cancer', 13, 'G', 'D', 'missense', 67, 0.15, 0.91, 0.00005
    UNION ALL SELECT 'KRAS', 'Lung Cancer', 61, 'Q', 'H', 'missense', 42, 0.13, 0.87, 0.0001
    UNION ALL SELECT 'KRAS', 'Colorectal Cancer', 61, 'Q', 'R', 'missense', 38, 0.09, 0.84, 0.0005
    
    -- EGFR mutations (lung cancer dominant)
    UNION ALL SELECT 'EGFR', 'Lung Cancer', 858, 'L', 'R', 'missense', 256, 0.49, 0.98, 0.00001
    UNION ALL SELECT 'EGFR', 'Lung Cancer', 790, 'T', 'M', 'missense', 78, 0.15, 0.94, 0.00001
    UNION ALL SELECT 'EGFR', 'Lung Cancer', 719, 'G', 'X', 'missense', 34, 0.07, 0.86, 0.0001
    UNION ALL SELECT 'EGFR', 'Lung Cancer', 746, 'E', 'del', 'deletion', 167, 0.32, 0.97, 0.00001
    UNION ALL SELECT 'EGFR', 'Glioblastoma', 289, 'A', 'V', 'missense', 28, 0.18, 0.82, 0.001
    
    -- BRAF mutations (melanoma signature)
    UNION ALL SELECT 'BRAF', 'Melanoma', 600, 'V', 'E', 'missense', 487, 0.66, 0.99, 0.00001
    UNION ALL SELECT 'BRAF', 'Thyroid Cancer', 600, 'V', 'E', 'missense', 123, 0.58, 0.96, 0.00001
    UNION ALL SELECT 'BRAF', 'Colorectal Cancer', 600, 'V', 'E', 'missense', 67, 0.15, 0.91, 0.00005
    UNION ALL SELECT 'BRAF', 'Melanoma', 600, 'V', 'K', 'missense', 34, 0.05, 0.85, 0.0001
    UNION ALL SELECT 'BRAF', 'Lung Cancer', 600, 'V', 'E', 'missense', 12, 0.02, 0.75, 0.01
    
    -- TP53 mutations (universal)
    UNION ALL SELECT 'TP53', 'Ovarian Cancer', 273, 'R', 'H', 'missense', 234, 0.96, 0.99, 0.00001
    UNION ALL SELECT 'TP53', 'Lung Cancer', 273, 'R', 'H', 'missense', 178, 0.56, 0.98, 0.00001
    UNION ALL SELECT 'TP53', 'Breast Cancer', 273, 'R', 'H', 'missense', 89, 0.31, 0.94, 0.00001
    UNION ALL SELECT 'TP53', 'Colorectal Cancer', 273, 'R', 'H', 'missense', 112, 0.25, 0.93, 0.00001
    UNION ALL SELECT 'TP53', 'Head and Neck Cancer', 273, 'R', 'H', 'missense', 145, 0.72, 0.97, 0.00001
    UNION ALL SELECT 'TP53', 'Gastric Cancer', 175, 'R', 'H', 'missense', 67, 0.33, 0.91, 0.00005
    UNION ALL SELECT 'TP53', 'Liver Cancer', 249, 'R', 'S', 'missense', 98, 0.41, 0.94, 0.00001
    UNION ALL SELECT 'TP53', 'Bladder Cancer', 280, 'R', 'T', 'missense', 76, 0.38, 0.92, 0.00001
    UNION ALL SELECT 'TP53', 'Glioblastoma', 273, 'R', 'C', 'missense', 89, 0.44, 0.93, 0.00001
    UNION ALL SELECT 'TP53', 'Pancreatic Cancer', 220, 'Y', 'C', 'missense', 43, 0.28, 0.88, 0.0001
    UNION ALL SELECT 'TP53', 'Lung Cancer', 175, 'R', 'H', 'missense', 134, 0.42, 0.96, 0.00001
    UNION ALL SELECT 'TP53', 'Breast Cancer', 248, 'R', 'Q', 'missense', 67, 0.23, 0.91, 0.00005
    UNION ALL SELECT 'TP53', 'Ovarian Cancer', 248, 'R', 'W', 'missense', 156, 0.64, 0.97, 0.00001
    
    -- PIK3CA mutations (breast cancer)
    UNION ALL SELECT 'PIK3CA', 'Breast Cancer', 1047, 'H', 'R', 'missense', 167, 0.58, 0.97, 0.00001
    UNION ALL SELECT 'PIK3CA', 'Breast Cancer', 545, 'E', 'K', 'missense', 134, 0.47, 0.95, 0.00001
    UNION ALL SELECT 'PIK3CA', 'Colorectal Cancer', 545, 'E', 'K', 'missense', 45, 0.10, 0.85, 0.0001
    UNION ALL SELECT 'PIK3CA', 'Head and Neck Cancer', 542, 'E', 'K', 'missense', 56, 0.28, 0.89, 0.00005
    UNION ALL SELECT 'PIK3CA', 'Breast Cancer', 1043, 'H', 'L', 'missense', 23, 0.08, 0.79, 0.001
    
    -- APC mutations (colorectal)
    UNION ALL SELECT 'APC', 'Colorectal Cancer', 1450, 'Q', 'X', 'nonsense', 234, 0.53, 0.98, 0.00001
    UNION ALL SELECT 'APC', 'Colorectal Cancer', 1309, 'E', 'X', 'nonsense', 178, 0.40, 0.96, 0.00001
    UNION ALL SELECT 'APC', 'Gastric Cancer', 1450, 'Q', 'X', 'nonsense', 34, 0.17, 0.82, 0.001
    UNION ALL SELECT 'APC', 'Colorectal Cancer', 1556, 'S', 'X', 'nonsense', 89, 0.20, 0.91, 0.00005
    
    -- BRCA1/BRCA2 mutations
    UNION ALL SELECT 'BRCA1', 'Breast Cancer', 1694, 'S', 'X', 'nonsense', 89, 0.31, 0.93, 0.00001
    UNION ALL SELECT 'BRCA1', 'Ovarian Cancer', 1694, 'S', 'X', 'nonsense', 112, 0.46, 0.95, 0.00001
    UNION ALL SELECT 'BRCA2', 'Breast Cancer', 3036, 'E', 'X', 'nonsense', 67, 0.23, 0.90, 0.00005
    UNION ALL SELECT 'BRCA2', 'Ovarian Cancer', 3036, 'E', 'X', 'nonsense', 78, 0.32, 0.92, 0.00001
    UNION ALL SELECT 'BRCA2', 'Pancreatic Cancer', 3036, 'E', 'X', 'nonsense', 23, 0.15, 0.81, 0.001
    UNION ALL SELECT 'BRCA1', 'Breast Cancer', 68, 'E', 'X', 'nonsense', 45, 0.16, 0.87, 0.0001
    
    -- IDH1/IDH2 mutations
    UNION ALL SELECT 'IDH1', 'Glioblastoma', 132, 'R', 'H', 'missense', 178, 0.88, 0.99, 0.00001
    UNION ALL SELECT 'IDH1', 'Glioblastoma', 132, 'R', 'C', 'missense', 34, 0.17, 0.91, 0.00005
    UNION ALL SELECT 'IDH2', 'Leukemia (AML)', 140, 'R', 'Q', 'missense', 67, 0.15, 0.91, 0.00005
    UNION ALL SELECT 'IDH2', 'Leukemia (AML)', 172, 'R', 'K', 'missense', 45, 0.10, 0.87, 0.0001
    
    -- PTEN mutations
    UNION ALL SELECT 'PTEN', 'Glioblastoma', 130, 'R', 'X', 'nonsense', 89, 0.44, 0.93, 0.00001
    UNION ALL SELECT 'PTEN', 'Prostate Cancer', 233, 'R', 'X', 'nonsense', 56, 0.12, 0.88, 0.0001
    UNION ALL SELECT 'PTEN', 'Breast Cancer', 173, 'R', 'C', 'missense', 34, 0.12, 0.84, 0.0005
    
    -- VHL mutations (kidney cancer)
    UNION ALL SELECT 'VHL', 'Kidney Cancer', 167, 'R', 'Q', 'missense', 134, 0.52, 0.96, 0.00001
    UNION ALL SELECT 'VHL', 'Kidney Cancer', 161, 'R', 'C', 'missense', 89, 0.35, 0.92, 0.00001
    UNION ALL SELECT 'VHL', 'Kidney Cancer', 158, 'L', 'P', 'missense', 45, 0.17, 0.87, 0.0001
    
    -- ALK mutations/fusions
    UNION ALL SELECT 'ALK', 'Lung Cancer', 1269, 'F', 'L', 'missense', 45, 0.14, 0.87, 0.0001
    UNION ALL SELECT 'ALK', 'Lung Cancer', 1174, 'L', 'M', 'missense', 23, 0.07, 0.81, 0.001
    
    -- MET mutations
    UNION ALL SELECT 'MET', 'Lung Cancer', 1010, 'Y', 'N', 'missense', 23, 0.07, 0.79, 0.001
    UNION ALL SELECT 'MET', 'Kidney Cancer', 1250, 'D', 'N', 'missense', 34, 0.13, 0.83, 0.0005
    
    -- HER2 mutations
    UNION ALL SELECT 'HER2', 'Breast Cancer', 755, 'V', 'I', 'missense', 89, 0.31, 0.93, 0.00001
    UNION ALL SELECT 'HER2', 'Gastric Cancer', 755, 'V', 'I', 'missense', 45, 0.22, 0.86, 0.0001
    UNION ALL SELECT 'HER2', 'Lung Cancer', 776, 'ins', 'YVMA', 'insertion', 34, 0.08, 0.85, 0.0005
    
    -- JAK2 mutations
    UNION ALL SELECT 'JAK2', 'Leukemia (AML)', 617, 'V', 'F', 'missense', 234, 0.54, 0.98, 0.00001
    
    -- FLT3 mutations
    UNION ALL SELECT 'FLT3', 'Leukemia (AML)', 835, 'D', 'Y', 'missense', 167, 0.39, 0.95, 0.00001
    UNION ALL SELECT 'FLT3', 'Leukemia (AML)', 836, 'D', 'N', 'missense', 89, 0.21, 0.90, 0.00005
    
    -- NRAS mutations
    UNION ALL SELECT 'NRAS', 'Melanoma', 61, 'Q', 'R', 'missense', 234, 0.32, 0.95, 0.00001
    UNION ALL SELECT 'NRAS', 'Leukemia (AML)', 12, 'G', 'D', 'missense', 45, 0.10, 0.84, 0.0005
    UNION ALL SELECT 'NRAS', 'Thyroid Cancer', 61, 'Q', 'K', 'missense', 34, 0.16, 0.82, 0.001
    UNION ALL SELECT 'NRAS', 'Colorectal Cancer', 61, 'Q', 'R', 'missense', 56, 0.13, 0.86, 0.0001
    
    -- CTNNB1 mutations
    UNION ALL SELECT 'CTNNB1', 'Liver Cancer', 45, 'S', 'F', 'missense', 67, 0.28, 0.90, 0.00005
    UNION ALL SELECT 'CTNNB1', 'Colorectal Cancer', 41, 'T', 'A', 'missense', 34, 0.08, 0.80, 0.001
    
    -- Additional genes
    UNION ALL SELECT 'STK11', 'Lung Cancer', 354, 'Q', 'X', 'nonsense', 45, 0.14, 0.86, 0.0001
    UNION ALL SELECT 'CDKN2A', 'Melanoma', 80, 'R', 'X', 'nonsense', 123, 0.17, 0.92, 0.00001
    UNION ALL SELECT 'CDKN2A', 'Pancreatic Cancer', 80, 'R', 'X', 'nonsense', 89, 0.57, 0.96, 0.00001
    UNION ALL SELECT 'NF1', 'Glioblastoma', 1423, 'R', 'X', 'nonsense', 56, 0.28, 0.88, 0.0001
    UNION ALL SELECT 'SMAD4', 'Pancreatic Cancer', 361, 'D', 'H', 'missense', 78, 0.50, 0.94, 0.00001
    UNION ALL SELECT 'SMAD4', 'Colorectal Cancer', 361, 'D', 'H', 'missense', 34, 0.08, 0.80, 0.001
    UNION ALL SELECT 'FBXW7', 'Colorectal Cancer', 465, 'R', 'C', 'missense', 45, 0.10, 0.85, 0.0001
    UNION ALL SELECT 'KEAP1', 'Lung Cancer', 334, 'G', 'D', 'missense', 67, 0.16, 0.88, 0.00005
    UNION ALL SELECT 'ARID1A', 'Ovarian Cancer', 2285, 'Q', 'X', 'nonsense', 89, 0.37, 0.92, 0.00001
    UNION ALL SELECT 'ARID1A', 'Gastric Cancer', 1989, 'R', 'X', 'nonsense', 56, 0.28, 0.88, 0.0001
    UNION ALL SELECT 'RB1', 'Lung Cancer', 320, 'R', 'X', 'nonsense', 45, 0.14, 0.86, 0.0001
    UNION ALL SELECT 'ATM', 'Pancreatic Cancer', 2891, 'R', 'X', 'nonsense', 34, 0.22, 0.84, 0.0005
    UNION ALL SELECT 'MLH1', 'Colorectal Cancer', 384, 'K', 'X', 'nonsense', 67, 0.15, 0.88, 0.00005
    UNION ALL SELECT 'MSH2', 'Colorectal Cancer', 689, 'R', 'X', 'nonsense', 56, 0.13, 0.86, 0.0001
    UNION ALL SELECT 'FGFR3', 'Bladder Cancer', 249, 'S', 'C', 'missense', 123, 0.48, 0.95, 0.00001
    UNION ALL SELECT 'ERBB3', 'Breast Cancer', 104, 'V', 'M', 'missense', 23, 0.08, 0.78, 0.001
    UNION ALL SELECT 'CDK4', 'Melanoma', 24, 'R', 'C', 'missense', 34, 0.12, 0.83, 0.0005
    UNION ALL SELECT 'MDM2', 'Liposarcoma', 166, 'amp', 'amp', 'amplification', 145, 0.65, 0.96, 0.00001
    UNION ALL SELECT 'CCND1', 'Breast Cancer', 156, 'amp', 'amp', 'amplification', 67, 0.15, 0.87, 0.0001
) m
JOIN genes g ON g.gene_symbol = m.gene
JOIN cancer_types ct ON ct.cancer_name = m.cancer;

-- Insert FDA-approved targeted therapeutics
INSERT INTO therapeutics (drug_name, target_gene, mechanism, fda_approval_year, company) VALUES
-- EGFR inhibitors
('Erlotinib (Tarceva)', 'EGFR', 'EGFR tyrosine kinase inhibitor', 2004, 'Genentech/Roche'),
('Gefitinib (Iressa)', 'EGFR', 'EGFR tyrosine kinase inhibitor', 2003, 'AstraZeneca'),
('Osimertinib (Tagrisso)', 'EGFR', 'Third-generation EGFR TKI for T790M', 2015, 'AstraZeneca'),
('Afatinib (Gilotrif)', 'EGFR/HER2', 'Irreversible EGFR/HER2 inhibitor', 2013, 'Boehringer Ingelheim'),
('Dacomitinib (Vizimpro)', 'EGFR', 'Second-generation EGFR TKI', 2018, 'Pfizer'),

-- BRAF inhibitors
('Vemurafenib (Zelboraf)', 'BRAF', 'BRAF V600E inhibitor', 2011, 'Roche/Genentech'),
('Dabrafenib (Tafinlar)', 'BRAF', 'BRAF V600E/K inhibitor', 2013, 'Novartis'),
('Encorafenib (Braftovi)', 'BRAF', 'BRAF V600E/K inhibitor', 2018, 'Array BioPharma'),

-- MEK inhibitors
('Trametinib (Mekinist)', 'MEK1/2', 'MEK1/2 inhibitor', 2013, 'Novartis'),
('Cobimetinib (Cotellic)', 'MEK1/2', 'MEK1/2 inhibitor', 2015, 'Genentech/Roche'),
('Binimetinib (Mektovi)', 'MEK1/2', 'MEK1/2 inhibitor', 2018, 'Array BioPharma'),

-- ALK inhibitors
('Crizotinib (Xalkori)', 'ALK/ROS1', 'ALK/ROS1/MET inhibitor', 2011, 'Pfizer'),
('Alectinib (Alecensa)', 'ALK', 'Second-generation ALK inhibitor', 2015, 'Roche/Genentech'),
('Ceritinib (Zykadia)', 'ALK', 'Second-generation ALK inhibitor', 2014, 'Novartis'),
('Brigatinib (Alunbrig)', 'ALK', 'Second-generation ALK inhibitor', 2017, 'Takeda'),
('Lorlatinib (Lorbrena)', 'ALK', 'Third-generation ALK inhibitor', 2018, 'Pfizer'),

-- HER2 targeted therapies
('Trastuzumab (Herceptin)', 'HER2', 'HER2 monoclonal antibody', 1998, 'Genentech/Roche'),
('Pertuzumab (Perjeta)', 'HER2', 'HER2 dimerization inhibitor', 2012, 'Genentech/Roche'),
('Lapatinib (Tykerb)', 'HER2/EGFR', 'HER2/EGFR dual inhibitor', 2007, 'GlaxoSmithKline'),
('Neratinib (Nerlynx)', 'HER2', 'Irreversible pan-HER inhibitor', 2017, 'Puma Biotechnology'),
('Tucatinib (Tukysa)', 'HER2', 'Selective HER2 inhibitor', 2020, 'Seagen'),
('Margetuximab (Margenza)', 'HER2', 'Fc-engineered HER2 antibody', 2020, 'MacroGenics'),

-- PARP inhibitors
('Olaparib (Lynparza)', 'PARP', 'PARP inhibitor for BRCA mutations', 2014, 'AstraZeneca'),
('Rucaparib (Rubraca)', 'PARP', 'PARP inhibitor', 2016, 'Clovis Oncology'),
('Niraparib (Zejula)', 'PARP', 'PARP inhibitor', 2017, 'GSK'),
('Talazoparib (Talzenna)', 'PARP', 'PARP inhibitor', 2018, 'Pfizer'),

-- CDK4/6 inhibitors
('Palbociclib (Ibrance)', 'CDK4/6', 'CDK4/6 inhibitor', 2015, 'Pfizer'),
('Ribociclib (Kisqali)', 'CDK4/6', 'CDK4/6 inhibitor', 2017, 'Novartis'),
('Abemaciclib (Verzenio)', 'CDK4/6', 'CDK4/6 inhibitor', 2017, 'Eli Lilly'),

-- PIK3CA inhibitor
('Alpelisib (Piqray)', 'PIK3CA', 'PI3K alpha inhibitor', 2019, 'Novartis'),
('Capivasertib', 'AKT', 'AKT inhibitor', 2023, 'AstraZeneca'),

-- IDH inhibitors
('Ivosidenib (Tibsovo)', 'IDH1', 'IDH1 inhibitor', 2018, 'Servier'),
('Enasidenib (Idhifa)', 'IDH2', 'IDH2 inhibitor', 2017, 'Bristol Myers Squibb'),

-- FLT3 inhibitors
('Midostaurin (Rydapt)', 'FLT3', 'Multi-kinase inhibitor', 2017, 'Novartis'),
('Gilteritinib (Xospata)', 'FLT3', 'FLT3/AXL inhibitor', 2018, 'Astellas'),
('Quizartinib', 'FLT3', 'Selective FLT3 inhibitor', 2023, 'Daiichi Sankyo'),

-- JAK inhibitors
('Ruxolitinib (Jakafi)', 'JAK1/2', 'JAK1/2 inhibitor', 2011, 'Incyte/Novartis'),

-- KRAS G12C inhibitors
('Sotorasib (Lumakras)', 'KRAS G12C', 'KRAS G12C inhibitor', 2021, 'Amgen'),
('Adagrasib (Krazati)', 'KRAS G12C', 'KRAS G12C inhibitor', 2022, 'Mirati'),

-- MET inhibitors
('Capmatinib (Tabrecta)', 'MET', 'MET inhibitor', 2020, 'Novartis'),
('Tepotinib (Tepmetko)', 'MET', 'MET inhibitor', 2021, 'Merck KGaA'),
('Savolitinib', 'MET', 'Selective MET inhibitor', 2021, 'AstraZeneca'),

-- RET inhibitors
('Selpercatinib (Retevmo)', 'RET', 'Selective RET inhibitor', 2020, 'Eli Lilly'),
('Pralsetinib (Gavreto)', 'RET', 'Selective RET inhibitor', 2020, 'Blueprint Medicines'),

-- FGFR inhibitors
('Erdafitinib (Balversa)', 'FGFR', 'Pan-FGFR inhibitor', 2019, 'Janssen'),
('Pemigatinib (Pemazyre)', 'FGFR', 'FGFR1-3 inhibitor', 2020, 'Incyte'),
('Infigratinib (Truseltiq)', 'FGFR', 'FGFR1-3 inhibitor', 2021, 'QED Therapeutics'),
('Futibatinib (Lytgobi)', 'FGFR2', 'FGFR2 inhibitor', 2022, 'Taiho'),

-- Immunotherapy
('Pembrolizumab (Keytruda)', 'PD-1', 'PD-1 checkpoint inhibitor', 2014, 'Merck'),
('Nivolumab (Opdivo)', 'PD-1', 'PD-1 checkpoint inhibitor', 2014, 'Bristol Myers Squibb'),
('Atezolizumab (Tecentriq)', 'PD-L1', 'PD-L1 checkpoint inhibitor', 2016, 'Genentech/Roche'),
('Ipilimumab (Yervoy)', 'CTLA-4', 'CTLA-4 checkpoint inhibitor', 2011, 'Bristol Myers Squibb'),
('Durvalumab (Imfinzi)', 'PD-L1', 'PD-L1 checkpoint inhibitor', 2017, 'AstraZeneca'),
('Avelumab (Bavencio)', 'PD-L1', 'PD-L1 checkpoint inhibitor', 2017, 'Merck KGaA/Pfizer');

-- Verify data insertion
SELECT 'Data population complete!' as status;
SELECT 'Genes: ' || COUNT(*) FROM genes;
SELECT 'Cancer Types: ' || COUNT(*) FROM cancer_types;
SELECT 'Mutations: ' || COUNT(*) FROM mutations;
SELECT 'Therapeutics: ' || COUNT(*) FROM therapeutics;