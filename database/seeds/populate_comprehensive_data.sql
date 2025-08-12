-- Comprehensive cancer mutation data population script
-- Based on real oncogene data from cancer research

-- Clear existing data (optional - comment out if you want to append)
DELETE FROM study_therapeutics;
DELETE FROM clinical_studies;
DELETE FROM mutation_hotspots;
DELETE FROM therapeutic_cancer_types;
DELETE FROM therapeutics;
DELETE FROM mutations;
DELETE FROM cancer_types;
DELETE FROM genes;

-- Reset auto-increment counters
DELETE FROM sqlite_sequence;

-- Insert major cancer types
INSERT INTO cancer_types (cancer_name, cancer_code, tissue_type, prevalence_per_100k) VALUES
('Lung Cancer', 'LUAD', 'Lung', 57.3),
('Breast Cancer', 'BRCA', 'Breast', 124.7),
('Colorectal Cancer', 'COAD', 'Colon', 38.4),
('Melanoma', 'SKCM', 'Skin', 21.6),
('Pancreatic Cancer', 'PAAD', 'Pancreas', 13.1),
('Liver Cancer', 'LIHC', 'Liver', 8.9),
('Ovarian Cancer', 'OV', 'Ovary', 11.1),
('Glioblastoma', 'GBM', 'Brain', 3.2),
('Thyroid Cancer', 'THCA', 'Thyroid', 13.5),
('Kidney Cancer', 'KIRC', 'Kidney', 16.4),
('Bladder Cancer', 'BLCA', 'Bladder', 19.8),
('Prostate Cancer', 'PRAD', 'Prostate', 109.8),
('Gastric Cancer', 'STAD', 'Stomach', 5.6),
('Head and Neck Cancer', 'HNSC', 'Head/Neck', 14.9),
('Leukemia', 'LAML', 'Blood', 13.7);

-- Insert major oncogenes and tumor suppressors
INSERT INTO genes (gene_symbol, gene_name, chromosome, gene_type, pathway) VALUES
-- Oncogenes
('KRAS', 'KRAS proto-oncogene', '12p12.1', 'oncogene', 'RAS/MAPK'),
('EGFR', 'Epidermal growth factor receptor', '7p11.2', 'oncogene', 'RTK/RAS'),
('BRAF', 'B-Raf proto-oncogene', '7q34', 'oncogene', 'RAS/MAPK'),
('PIK3CA', 'Phosphatidylinositol-3-kinase catalytic alpha', '3q26.32', 'oncogene', 'PI3K/AKT'),
('MYC', 'MYC proto-oncogene', '8q24.21', 'oncogene', 'Cell cycle'),
('ALK', 'Anaplastic lymphoma kinase', '2p23.1', 'oncogene', 'RTK'),
('MET', 'MET proto-oncogene', '7q31.2', 'oncogene', 'RTK/HGF'),
('HER2', 'Human epidermal growth factor receptor 2', '17q12', 'oncogene', 'RTK/RAS'),
('FLT3', 'FMS-like tyrosine kinase 3', '13q12.2', 'oncogene', 'RTK'),
('KIT', 'KIT proto-oncogene', '4q12', 'oncogene', 'RTK'),
('RET', 'RET proto-oncogene', '10q11.21', 'oncogene', 'RTK'),
('NRAS', 'NRAS proto-oncogene', '1p13.2', 'oncogene', 'RAS/MAPK'),
('JAK2', 'Janus kinase 2', '9p24.1', 'oncogene', 'JAK/STAT'),
('IDH1', 'Isocitrate dehydrogenase 1', '2q34', 'oncogene', 'Metabolism'),
('IDH2', 'Isocitrate dehydrogenase 2', '15q26.1', 'oncogene', 'Metabolism'),
-- Tumor suppressors
('TP53', 'Tumor protein p53', '17p13.1', 'tumor_suppressor', 'Cell cycle/Apoptosis'),
('APC', 'Adenomatous polyposis coli', '5q22.2', 'tumor_suppressor', 'WNT'),
('PTEN', 'Phosphatase and tensin homolog', '10q23.31', 'tumor_suppressor', 'PI3K/AKT'),
('RB1', 'Retinoblastoma protein', '13q14.2', 'tumor_suppressor', 'Cell cycle'),
('VHL', 'Von Hippel-Lindau', '3p25.3', 'tumor_suppressor', 'HIF pathway'),
('BRCA1', 'Breast cancer type 1', '17q21.31', 'tumor_suppressor', 'DNA repair'),
('BRCA2', 'Breast cancer type 2', '13q13.1', 'tumor_suppressor', 'DNA repair'),
('ATM', 'Ataxia telangiectasia mutated', '11q22.3', 'tumor_suppressor', 'DNA repair'),
('CDKN2A', 'Cyclin-dependent kinase inhibitor 2A', '9p21.3', 'tumor_suppressor', 'Cell cycle'),
('STK11', 'Serine/threonine kinase 11', '19p13.3', 'tumor_suppressor', 'mTOR'),
('NF1', 'Neurofibromin 1', '17q11.2', 'tumor_suppressor', 'RAS/MAPK'),
('SMAD4', 'SMAD family member 4', '18q21.2', 'tumor_suppressor', 'TGF-β'),
('MLH1', 'MutL homolog 1', '3p22.2', 'tumor_suppressor', 'DNA repair'),
('MSH2', 'MutS homolog 2', '2p21', 'tumor_suppressor', 'DNA repair'),
('CTNNB1', 'Catenin beta 1', '3p21.3', 'oncogene', 'WNT');

-- Insert comprehensive mutation data
-- KRAS mutations (very common in multiple cancers)
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, frequency, significance_score, p_value) VALUES
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PAAD'), 12, 'G', 'D', 'missense', 342, 0.87, 0.99, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 12, 'G', 'D', 'missense', 185, 0.42, 0.97, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 12, 'G', 'D', 'missense', 98, 0.31, 0.95, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PAAD'), 13, 'G', 'D', 'missense', 45, 0.11, 0.88, 0.0001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 13, 'G', 'D', 'missense', 67, 0.15, 0.91, 0.00005),
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 61, 'Q', 'H', 'missense', 42, 0.13, 0.87, 0.0001),

-- EGFR mutations (common in lung cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'EGFR'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 858, 'L', 'R', 'missense', 156, 0.49, 0.98, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'EGFR'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 790, 'T', 'M', 'missense', 78, 0.24, 0.94, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'EGFR'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 719, 'G', 'X', 'missense', 34, 0.11, 0.86, 0.0001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'EGFR'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'GBM'), 289, 'A', 'V', 'missense', 28, 0.18, 0.82, 0.001),

-- BRAF mutations (melanoma signature)
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRAF'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 600, 'V', 'E', 'missense', 487, 0.66, 0.99, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRAF'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'THCA'), 600, 'V', 'E', 'missense', 123, 0.58, 0.96, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRAF'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 600, 'V', 'E', 'missense', 67, 0.15, 0.91, 0.00005),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRAF'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 597, 'V', 'F', 'missense', 12, 0.02, 0.71, 0.01),

-- TP53 mutations (most commonly mutated gene in cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'OV'), 273, 'R', 'H', 'missense', 234, 0.96, 0.99, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 273, 'R', 'H', 'missense', 178, 0.56, 0.98, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 273, 'R', 'H', 'missense', 89, 0.31, 0.94, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 273, 'R', 'H', 'missense', 112, 0.25, 0.93, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'HNSC'), 273, 'R', 'H', 'missense', 145, 0.72, 0.97, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'STAD'), 175, 'R', 'H', 'missense', 67, 0.33, 0.91, 0.00005),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LIHC'), 249, 'R', 'S', 'missense', 98, 0.41, 0.94, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BLCA'), 280, 'R', 'T', 'missense', 76, 0.38, 0.92, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'GBM'), 273, 'R', 'C', 'missense', 89, 0.44, 0.93, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PAAD'), 220, 'Y', 'C', 'missense', 43, 0.28, 0.88, 0.0001),

-- PIK3CA mutations (common in breast cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'PIK3CA'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 1047, 'H', 'R', 'missense', 167, 0.58, 0.97, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'PIK3CA'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 545, 'E', 'K', 'missense', 134, 0.47, 0.95, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'PIK3CA'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 545, 'E', 'K', 'missense', 45, 0.10, 0.85, 0.0001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'PIK3CA'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'HNSC'), 542, 'E', 'K', 'missense', 56, 0.28, 0.89, 0.00005),

-- APC mutations (colorectal cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'APC'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 1450, 'Q', 'X', 'nonsense', 234, 0.53, 0.98, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'APC'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 1309, 'E', 'X', 'nonsense', 178, 0.40, 0.96, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'APC'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'STAD'), 1450, 'Q', 'X', 'nonsense', 34, 0.17, 0.82, 0.001),

-- BRCA1/BRCA2 mutations (breast and ovarian cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRCA1'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 1694, 'S', 'X', 'nonsense', 89, 0.31, 0.93, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRCA1'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'OV'), 1694, 'S', 'X', 'nonsense', 112, 0.46, 0.95, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRCA2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 3036, 'E', 'X', 'nonsense', 67, 0.23, 0.90, 0.00005),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRCA2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'OV'), 3036, 'E', 'X', 'nonsense', 78, 0.32, 0.92, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRCA2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PAAD'), 3036, 'E', 'X', 'nonsense', 23, 0.15, 0.81, 0.001),

-- IDH1/IDH2 mutations (glioblastoma and leukemia)
((SELECT gene_id FROM genes WHERE gene_symbol = 'IDH1'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'GBM'), 132, 'R', 'H', 'missense', 178, 0.88, 0.99, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'IDH2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 140, 'R', 'Q', 'missense', 67, 0.15, 0.91, 0.00005),
((SELECT gene_id FROM genes WHERE gene_symbol = 'IDH2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 172, 'R', 'K', 'missense', 45, 0.10, 0.87, 0.0001),

-- PTEN mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'PTEN'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'GBM'), 130, 'R', 'X', 'nonsense', 89, 0.44, 0.93, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'PTEN'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PRAD'), 233, 'R', 'X', 'nonsense', 56, 0.12, 0.88, 0.0001),

-- VHL mutations (kidney cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'VHL'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'KIRC'), 167, 'R', 'Q', 'missense', 134, 0.52, 0.96, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'VHL'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'KIRC'), 161, 'R', 'C', 'missense', 89, 0.35, 0.92, 0.00001),

-- ALK fusions (lung cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'ALK'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 1269, 'F', 'L', 'missense', 45, 0.14, 0.87, 0.0001),

-- MET mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'MET'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 1010, 'Y', 'N', 'missense', 23, 0.07, 0.79, 0.001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'MET'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'KIRC'), 1250, 'D', 'N', 'missense', 34, 0.13, 0.83, 0.0005),

-- HER2 amplifications (breast cancer)
((SELECT gene_id FROM genes WHERE gene_symbol = 'HER2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 755, 'V', 'I', 'missense', 89, 0.31, 0.93, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'HER2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'STAD'), 755, 'V', 'I', 'missense', 45, 0.22, 0.86, 0.0001),

-- JAK2 mutations (blood cancers)
((SELECT gene_id FROM genes WHERE gene_symbol = 'JAK2'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 617, 'V', 'F', 'missense', 234, 0.54, 0.98, 0.00001),

-- FLT3 mutations (leukemia)
((SELECT gene_id FROM genes WHERE gene_symbol = 'FLT3'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 835, 'D', 'Y', 'missense', 167, 0.39, 0.95, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'FLT3'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 836, 'D', 'N', 'missense', 89, 0.21, 0.90, 0.00005),

-- NRAS mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'NRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 61, 'Q', 'R', 'missense', 234, 0.32, 0.95, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'NRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 12, 'G', 'D', 'missense', 45, 0.10, 0.84, 0.0005),
((SELECT gene_id FROM genes WHERE gene_symbol = 'NRAS'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'THCA'), 61, 'Q', 'K', 'missense', 34, 0.16, 0.82, 0.001),

-- CTNNB1 mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'CTNNB1'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LIHC'), 45, 'S', 'F', 'missense', 67, 0.28, 0.90, 0.00005),
((SELECT gene_id FROM genes WHERE gene_symbol = 'CTNNB1'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 41, 'T', 'A', 'missense', 34, 0.08, 0.80, 0.001),

-- STK11 mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'STK11'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 354, 'Q', 'X', 'nonsense', 45, 0.14, 0.86, 0.0001),

-- CDKN2A mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'CDKN2A'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 80, 'R', 'X', 'nonsense', 123, 0.17, 0.92, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'CDKN2A'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PAAD'), 80, 'R', 'X', 'nonsense', 89, 0.57, 0.96, 0.00001),

-- NF1 mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'NF1'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'GBM'), 1423, 'R', 'X', 'nonsense', 56, 0.28, 0.88, 0.0001),

-- SMAD4 mutations
((SELECT gene_id FROM genes WHERE gene_symbol = 'SMAD4'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PAAD'), 361, 'D', 'H', 'missense', 78, 0.50, 0.94, 0.00001),
((SELECT gene_id FROM genes WHERE gene_symbol = 'SMAD4'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 361, 'D', 'H', 'missense', 34, 0.08, 0.80, 0.001);

-- Insert FDA-approved targeted therapeutics
INSERT INTO therapeutics (drug_name, drug_type, target_gene, mechanism, fda_approval_year, company) VALUES
-- EGFR inhibitors
('Erlotinib', 'small_molecule', 'EGFR', 'EGFR tyrosine kinase inhibitor', 2004, 'Genentech/Roche'),
('Gefitinib', 'small_molecule', 'EGFR', 'EGFR tyrosine kinase inhibitor', 2003, 'AstraZeneca'),
('Osimertinib', 'small_molecule', 'EGFR', 'Third-generation EGFR TKI', 2015, 'AstraZeneca'),
('Afatinib', 'small_molecule', 'EGFR', 'Irreversible EGFR/HER2 inhibitor', 2013, 'Boehringer Ingelheim'),

-- BRAF inhibitors
('Vemurafenib', 'small_molecule', 'BRAF', 'BRAF V600E inhibitor', 2011, 'Roche/Genentech'),
('Dabrafenib', 'small_molecule', 'BRAF', 'BRAF V600E/K inhibitor', 2013, 'Novartis'),
('Encorafenib', 'small_molecule', 'BRAF', 'BRAF V600E/K inhibitor', 2018, 'Array BioPharma'),

-- MEK inhibitors (often combined with BRAF inhibitors)
('Trametinib', 'small_molecule', 'MEK', 'MEK1/2 inhibitor', 2013, 'Novartis'),
('Cobimetinib', 'small_molecule', 'MEK', 'MEK1/2 inhibitor', 2015, 'Genentech/Roche'),
('Binimetinib', 'small_molecule', 'MEK', 'MEK1/2 inhibitor', 2018, 'Array BioPharma'),

-- ALK inhibitors
('Crizotinib', 'small_molecule', 'ALK', 'ALK/ROS1/MET inhibitor', 2011, 'Pfizer'),
('Alectinib', 'small_molecule', 'ALK', 'Second-generation ALK inhibitor', 2015, 'Roche/Genentech'),
('Ceritinib', 'small_molecule', 'ALK', 'Second-generation ALK inhibitor', 2014, 'Novartis'),
('Brigatinib', 'small_molecule', 'ALK', 'Second-generation ALK inhibitor', 2017, 'Takeda'),
('Lorlatinib', 'small_molecule', 'ALK', 'Third-generation ALK inhibitor', 2018, 'Pfizer'),

-- HER2 inhibitors
('Trastuzumab', 'antibody', 'HER2', 'HER2 monoclonal antibody', 1998, 'Genentech/Roche'),
('Pertuzumab', 'antibody', 'HER2', 'HER2 dimerization inhibitor', 2012, 'Genentech/Roche'),
('Lapatinib', 'small_molecule', 'HER2', 'HER2/EGFR dual inhibitor', 2007, 'GlaxoSmithKline'),
('Neratinib', 'small_molecule', 'HER2', 'Irreversible pan-HER inhibitor', 2017, 'Puma Biotechnology'),

-- PARP inhibitors (for BRCA mutations)
('Olaparib', 'small_molecule', 'PARP', 'PARP inhibitor', 2014, 'AstraZeneca'),
('Rucaparib', 'small_molecule', 'PARP', 'PARP inhibitor', 2016, 'Clovis Oncology'),
('Niraparib', 'small_molecule', 'PARP', 'PARP inhibitor', 2017, 'Tesaro/GSK'),
('Talazoparib', 'small_molecule', 'PARP', 'PARP inhibitor', 2018, 'Pfizer'),

-- CDK4/6 inhibitors
('Palbociclib', 'small_molecule', 'CDK4/6', 'CDK4/6 inhibitor', 2015, 'Pfizer'),
('Ribociclib', 'small_molecule', 'CDK4/6', 'CDK4/6 inhibitor', 2017, 'Novartis'),
('Abemaciclib', 'small_molecule', 'CDK4/6', 'CDK4/6 inhibitor', 2017, 'Eli Lilly'),

-- PIK3CA inhibitors
('Alpelisib', 'small_molecule', 'PIK3CA', 'PI3K alpha inhibitor', 2019, 'Novartis'),

-- IDH inhibitors
('Ivosidenib', 'small_molecule', 'IDH1', 'IDH1 inhibitor', 2018, 'Agios'),
('Enasidenib', 'small_molecule', 'IDH2', 'IDH2 inhibitor', 2017, 'Celgene/BMS'),

-- FLT3 inhibitors
('Midostaurin', 'small_molecule', 'FLT3', 'Multi-kinase inhibitor', 2017, 'Novartis'),
('Gilteritinib', 'small_molecule', 'FLT3', 'FLT3/AXL inhibitor', 2018, 'Astellas'),

-- JAK inhibitors
('Ruxolitinib', 'small_molecule', 'JAK2', 'JAK1/2 inhibitor', 2011, 'Incyte/Novartis'),

-- KRAS G12C inhibitors
('Sotorasib', 'small_molecule', 'KRAS', 'KRAS G12C inhibitor', 2021, 'Amgen'),
('Adagrasib', 'small_molecule', 'KRAS', 'KRAS G12C inhibitor', 2022, 'Mirati'),

-- MET inhibitors
('Capmatinib', 'small_molecule', 'MET', 'MET inhibitor', 2020, 'Novartis'),
('Tepotinib', 'small_molecule', 'MET', 'MET inhibitor', 2021, 'Merck KGaA'),

-- RET inhibitors
('Selpercatinib', 'small_molecule', 'RET', 'RET inhibitor', 2020, 'Eli Lilly'),
('Pralsetinib', 'small_molecule', 'RET', 'RET inhibitor', 2020, 'Blueprint Medicines'),

-- Immunotherapy agents
('Pembrolizumab', 'antibody', 'PD-1', 'PD-1 checkpoint inhibitor', 2014, 'Merck'),
('Nivolumab', 'antibody', 'PD-1', 'PD-1 checkpoint inhibitor', 2014, 'Bristol Myers Squibb'),
('Atezolizumab', 'antibody', 'PD-L1', 'PD-L1 checkpoint inhibitor', 2016, 'Genentech/Roche'),
('Ipilimumab', 'antibody', 'CTLA-4', 'CTLA-4 checkpoint inhibitor', 2011, 'Bristol Myers Squibb');

-- Link therapeutics to cancer types
INSERT INTO therapeutic_cancer_types (therapeutic_id, cancer_type_id, efficacy_score, response_rate) VALUES
-- EGFR inhibitors for lung cancer
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Osimertinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.95, 0.71),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Erlotinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.88, 0.62),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Gefitinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.86, 0.60),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Afatinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.89, 0.64),

-- BRAF inhibitors for melanoma
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Vemurafenib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 0.93, 0.68),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Dabrafenib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 0.94, 0.70),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Encorafenib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 0.95, 0.72),

-- HER2 inhibitors for breast cancer
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Trastuzumab'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 0.92, 0.65),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Pertuzumab'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 0.90, 0.63),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Lapatinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 0.85, 0.55),

-- PARP inhibitors for BRCA-mutated cancers
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Olaparib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 0.91, 0.60),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Olaparib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'OV'), 0.93, 0.65),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Rucaparib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'OV'), 0.89, 0.58),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Niraparib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'OV'), 0.88, 0.57),

-- ALK inhibitors for lung cancer
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Alectinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.96, 0.82),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Crizotinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.88, 0.65),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Lorlatinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.94, 0.75),

-- IDH inhibitors for AML and glioblastoma
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Ivosidenib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 0.87, 0.42),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Enasidenib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 0.85, 0.40),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Ivosidenib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'GBM'), 0.82, 0.35),

-- FLT3 inhibitors for leukemia
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Midostaurin'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 0.86, 0.45),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Gilteritinib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 0.90, 0.54),

-- KRAS inhibitors
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Sotorasib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.84, 0.36),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Adagrasib'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.85, 0.38),

-- Immunotherapy (broadly applicable)
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Pembrolizumab'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.88, 0.45),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Pembrolizumab'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 0.91, 0.55),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Nivolumab'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.86, 0.42),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Nivolumab'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 0.90, 0.52),
((SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Atezolizumab'), (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BLCA'), 0.85, 0.40);

-- Insert mutation hotspots
INSERT INTO mutation_hotspots (gene_id, hotspot_region_start, hotspot_region_end, cancer_type_id, frequency, description) VALUES
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), 12, 13, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'PAAD'), 0.88, 'G12/G13 mutations'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS'), 61, 61, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'COAD'), 0.15, 'Q61 mutations'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'EGFR'), 746, 753, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.45, 'Exon 19 deletions'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'EGFR'), 858, 858, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'), 0.40, 'L858R mutation'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'BRAF'), 600, 600, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM'), 0.66, 'V600E/K mutations'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), 175, 175, NULL, 0.08, 'DNA binding domain hotspot'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), 248, 248, NULL, 0.10, 'DNA binding domain hotspot'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'TP53'), 273, 273, NULL, 0.12, 'DNA binding domain hotspot'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'PIK3CA'), 542, 546, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 0.35, 'Helical domain mutations'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'PIK3CA'), 1047, 1047, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA'), 0.30, 'Kinase domain H1047R'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'IDH1'), 132, 132, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'GBM'), 0.88, 'R132 mutations'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'IDH2'), 140, 140, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 0.10, 'R140 mutations'),
((SELECT gene_id FROM genes WHERE gene_symbol = 'IDH2'), 172, 172, (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LAML'), 0.08, 'R172 mutations');

-- Insert clinical studies
INSERT INTO clinical_studies (study_name, study_type, phase, start_year, status, sponsor, cancer_type_id) VALUES
('FLAURA', 'Treatment', 'III', 2016, 'Completed', 'AstraZeneca', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD')),
('COMBI-d', 'Treatment', 'III', 2012, 'Completed', 'Novartis', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'SKCM')),
('CLEOPATRA', 'Treatment', 'III', 2011, 'Completed', 'Roche', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'BRCA')),
('ALEX', 'Treatment', 'III', 2014, 'Completed', 'Roche', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD')),
('KEYNOTE-189', 'Treatment', 'III', 2016, 'Completed', 'Merck', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD')),
('SOLO-1', 'Treatment', 'III', 2014, 'Completed', 'AstraZeneca', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'OV')),
('CodeBreaK 100', 'Treatment', 'II', 2018, 'Active', 'Amgen', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD')),
('CROWN', 'Treatment', 'III', 2017, 'Active', 'Pfizer', (SELECT cancer_type_id FROM cancer_types WHERE cancer_code = 'LUAD'));

-- Link studies to therapeutics
INSERT INTO study_therapeutics (study_id, therapeutic_id, is_combination) VALUES
((SELECT study_id FROM clinical_studies WHERE study_name = 'FLAURA'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Osimertinib'), 0),
((SELECT study_id FROM clinical_studies WHERE study_name = 'COMBI-d'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Dabrafenib'), 1),
((SELECT study_id FROM clinical_studies WHERE study_name = 'COMBI-d'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Trametinib'), 1),
((SELECT study_id FROM clinical_studies WHERE study_name = 'CLEOPATRA'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Pertuzumab'), 1),
((SELECT study_id FROM clinical_studies WHERE study_name = 'CLEOPATRA'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Trastuzumab'), 1),
((SELECT study_id FROM clinical_studies WHERE study_name = 'ALEX'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Alectinib'), 0),
((SELECT study_id FROM clinical_studies WHERE study_name = 'KEYNOTE-189'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Pembrolizumab'), 1),
((SELECT study_id FROM clinical_studies WHERE study_name = 'SOLO-1'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Olaparib'), 0),
((SELECT study_id FROM clinical_studies WHERE study_name = 'CodeBreaK 100'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Sotorasib'), 0),
((SELECT study_id FROM clinical_studies WHERE study_name = 'CROWN'), (SELECT therapeutic_id FROM therapeutics WHERE drug_name = 'Lorlatinib'), 0);

-- Verify data insertion
SELECT 'Data population complete!' as status;
SELECT 'Genes: ' || COUNT(*) FROM genes;
SELECT 'Cancer Types: ' || COUNT(*) FROM cancer_types;
SELECT 'Mutations: ' || COUNT(*) FROM mutations;
SELECT 'Therapeutics: ' || COUNT(*) FROM therapeutics;
SELECT 'Mutation Hotspots: ' || COUNT(*) FROM mutation_hotspots;
SELECT 'Clinical Studies: ' || COUNT(*) FROM clinical_studies;