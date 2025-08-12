-- OncoHotspot Sample Data for Development
-- Populate database with realistic sample data for testing

-- Insert sample genes
INSERT INTO genes (gene_symbol, gene_name, chromosome, start_position, end_position, strand, gene_type, description) VALUES
('TP53', 'Tumor protein p53', '17', 7661779, 7687538, '-', 'protein_coding', 'Guardian of the genome, critical tumor suppressor'),
('KRAS', 'KRAS proto-oncogene', '12', 25205246, 25250929, '-', 'protein_coding', 'Key regulator of cell proliferation and differentiation'),
('EGFR', 'Epidermal growth factor receptor', '7', 55019017, 55207338, '+', 'protein_coding', 'Transmembrane protein involved in cell growth and survival'),
('BRAF', 'B-Raf proto-oncogene', '7', 140719327, 140924929, '-', 'protein_coding', 'Serine/threonine kinase in MAPK pathway'),
('PIK3CA', 'Phosphatidylinositol-4,5-bisphosphate 3-kinase catalytic subunit alpha', '3', 179148114, 179240093, '+', 'protein_coding', 'Key enzyme in PI3K/AKT pathway'),
('BRCA1', 'BRCA1 DNA repair associated', '17', 43044295, 43170245, '-', 'protein_coding', 'Tumor suppressor involved in DNA repair'),
('BRCA2', 'BRCA2 DNA repair associated', '13', 32315086, 32400268, '+', 'protein_coding', 'Tumor suppressor involved in homologous recombination');

-- Insert cancer types
INSERT INTO cancer_types (cancer_name, cancer_category, tissue_origin, description) VALUES
('Breast Cancer', 'Carcinoma', 'Breast tissue', 'Malignant tumor arising from breast tissue'),
('Lung Cancer', 'Carcinoma', 'Lung tissue', 'Malignant tumor of the lungs, often linked to smoking'),
('Colorectal Cancer', 'Carcinoma', 'Colon/Rectum', 'Cancer of the colon or rectum'),
('Prostate Cancer', 'Carcinoma', 'Prostate gland', 'Cancer of the prostate gland in men'),
('Melanoma', 'Melanoma', 'Skin', 'Malignant tumor of melanocytes'),
('Ovarian Cancer', 'Carcinoma', 'Ovary', 'Cancer arising from ovarian tissue'),
('Pancreatic Cancer', 'Carcinoma', 'Pancreas', 'Aggressive cancer of pancreatic tissue');

-- Insert sample mutations
INSERT INTO mutations (gene_id, cancer_type_id, position, ref_allele, alt_allele, mutation_type, mutation_count, total_samples, frequency, significance_score, p_value) VALUES
-- TP53 mutations
(1, 1, 273, 'C', 'T', 'missense', 45, 150, 0.30, 0.95, 0.0001),
(1, 2, 273, 'C', 'T', 'missense', 78, 200, 0.39, 0.98, 0.00005),
(1, 1, 175, 'C', 'T', 'missense', 32, 150, 0.21, 0.89, 0.001),
(1, 3, 248, 'C', 'T', 'missense', 28, 120, 0.23, 0.87, 0.002),

-- KRAS mutations
(2, 3, 12, 'G', 'A', 'missense', 92, 180, 0.51, 0.97, 0.00001),
(2, 7, 12, 'G', 'A', 'missense', 134, 220, 0.61, 0.99, 0.000001),
(2, 2, 13, 'G', 'A', 'missense', 45, 160, 0.28, 0.91, 0.0005),
(2, 3, 61, 'A', 'T', 'missense', 67, 180, 0.37, 0.93, 0.0002),

-- EGFR mutations
(3, 2, 858, 'T', 'G', 'missense', 67, 130, 0.52, 0.94, 0.0001),
(3, 2, 790, 'T', 'C', 'missense', 43, 130, 0.33, 0.88, 0.001),
(3, 2, 719, 'G', 'A', 'deletion', 29, 130, 0.22, 0.85, 0.003),

-- BRAF mutations
(4, 5, 600, 'T', 'A', 'missense', 156, 180, 0.87, 0.96, 0.00001),
(4, 3, 600, 'T', 'A', 'missense', 23, 120, 0.19, 0.82, 0.005),

-- PIK3CA mutations
(5, 1, 545, 'G', 'A', 'missense', 43, 150, 0.29, 0.89, 0.0008),
(5, 1, 1047, 'A', 'G', 'missense', 38, 150, 0.25, 0.86, 0.002),
(5, 6, 545, 'G', 'A', 'missense', 31, 90, 0.34, 0.91, 0.0005);

-- Insert therapeutic targets
INSERT INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer) VALUES
(3, 'Erlotinib', 'EGFR tyrosine kinase inhibitor', 'Approved', 'Non-small cell lung cancer', '2004-11-18', 'Genentech'),
(3, 'Gefitinib', 'EGFR tyrosine kinase inhibitor', 'Approved', 'Non-small cell lung cancer', '2003-05-05', 'AstraZeneca'),
(3, 'Osimertinib', 'Third-generation EGFR inhibitor', 'Approved', 'EGFR T790M mutant NSCLC', '2015-11-13', 'AstraZeneca'),
(4, 'Vemurafenib', 'BRAF V600E inhibitor', 'Approved', 'Melanoma with BRAF V600E mutation', '2011-08-17', 'Genentech'),
(4, 'Dabrafenib', 'BRAF inhibitor', 'Approved', 'Melanoma, anaplastic thyroid cancer', '2013-05-29', 'GSK'),
(6, 'Olaparib', 'PARP inhibitor', 'Approved', 'BRCA-mutated ovarian cancer', '2014-12-19', 'AstraZeneca'),
(7, 'Olaparib', 'PARP inhibitor', 'Approved', 'BRCA-mutated breast cancer', '2018-01-12', 'AstraZeneca'),
(5, 'Alpelisib', 'PI3K alpha inhibitor', 'Approved', 'PIK3CA-mutated breast cancer', '2019-05-24', 'Novartis');

-- Link therapeutics to cancer types
INSERT INTO therapeutic_cancer_types (therapeutic_id, cancer_type_id, efficacy_rating, response_rate, progression_free_survival, overall_survival) VALUES
(1, 2, 'High', 65.2, 13.1, 19.3),
(2, 2, 'High', 71.0, 10.9, 18.8),
(3, 2, 'High', 81.0, 18.9, 38.6),
(4, 5, 'High', 48.4, 5.3, 13.6),
(5, 5, 'High', 51.0, 5.1, 12.7),
(6, 6, 'Medium', 34.0, 7.0, 15.9),
(7, 1, 'Medium', 59.9, 7.0, 19.3),
(8, 1, 'Medium', 26.6, 11.0, 39.3);

-- Insert mutation hotspots
INSERT INTO mutation_hotspots (gene_id, position_start, position_end, hotspot_name, mutation_density, clinical_significance, domain_annotation) VALUES
(1, 270, 280, 'TP53 DNA-binding domain hotspot', 0.85, 'High', 'DNA-binding domain'),
(1, 170, 180, 'TP53 L2 loop', 0.72, 'High', 'L2 loop region'),
(2, 10, 15, 'KRAS G12/G13 hotspot', 0.95, 'Critical', 'GTP-binding domain'),
(2, 59, 63, 'KRAS Q61 hotspot', 0.88, 'High', 'GTP-binding domain'),
(3, 855, 865, 'EGFR kinase domain', 0.91, 'High', 'Tyrosine kinase domain'),
(3, 790, 795, 'EGFR T790M region', 0.67, 'High', 'Tyrosine kinase domain'),
(4, 598, 602, 'BRAF V600 hotspot', 0.98, 'Critical', 'Serine/threonine kinase domain'),
(5, 542, 548, 'PIK3CA helical domain', 0.79, 'High', 'Helical domain'),
(5, 1043, 1050, 'PIK3CA kinase domain', 0.73, 'High', 'Kinase domain');

-- Sample clinical studies
INSERT INTO clinical_studies (nct_id, title, phase, status, start_date, completion_date, participant_count, primary_endpoint) VALUES
('NCT02151981', 'Osimertinib vs Standard EGFR-TKI as First-Line Treatment', 'Phase III', 'Completed', '2014-05-30', '2018-10-31', 556, 'Progression-free survival'),
('NCT01639508', 'Vemurafenib in BRAF V600 Mutant Melanoma', 'Phase III', 'Completed', '2012-06-01', '2016-12-31', 675, 'Overall survival'),
('NCT02000622', 'Olaparib vs Chemotherapy in BRCA-mutated Breast Cancer', 'Phase III', 'Completed', '2014-02-05', '2018-09-30', 302, 'Progression-free survival');

-- Link studies to therapeutics
INSERT INTO study_therapeutics (study_id, therapeutic_id, arm_description, dosage, administration_route) VALUES
(1, 3, 'Osimertinib treatment arm', '80 mg once daily', 'Oral'),
(2, 4, 'Vemurafenib treatment arm', '960 mg twice daily', 'Oral'),
(3, 6, 'Olaparib treatment arm', '300 mg twice daily', 'Oral');

COMMIT;