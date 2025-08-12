-- Add FDA-approved targeted cancer therapeutics
-- Each drug is linked to its target gene

-- EGFR inhibitors (for lung cancer with EGFR mutations)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Osimertinib (Tagrisso)', 'Third-generation EGFR TKI', 'Approved', 'NSCLC with EGFR T790M', '2015-11-13', 'AstraZeneca', 'L858R, T790M, exon 19 del'
FROM genes WHERE gene_symbol = 'EGFR';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Erlotinib (Tarceva)', 'First-generation EGFR TKI', 'Approved', 'NSCLC with EGFR mutations', '2004-11-18', 'Genentech/Roche', 'L858R, exon 19 del'
FROM genes WHERE gene_symbol = 'EGFR';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Gefitinib (Iressa)', 'First-generation EGFR TKI', 'Approved', 'NSCLC with EGFR mutations', '2003-05-05', 'AstraZeneca', 'L858R, exon 19 del'
FROM genes WHERE gene_symbol = 'EGFR';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Afatinib (Gilotrif)', 'Second-generation EGFR TKI', 'Approved', 'NSCLC with EGFR mutations', '2013-07-12', 'Boehringer Ingelheim', 'L858R, exon 19 del, uncommon mutations'
FROM genes WHERE gene_symbol = 'EGFR';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Dacomitinib (Vizimpro)', 'Second-generation EGFR TKI', 'Approved', 'NSCLC with EGFR mutations', '2018-09-27', 'Pfizer', 'L858R, exon 19 del'
FROM genes WHERE gene_symbol = 'EGFR';

-- BRAF inhibitors (for melanoma with BRAF V600 mutations)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Vemurafenib (Zelboraf)', 'BRAF V600E inhibitor', 'Approved', 'Melanoma with BRAF V600E', '2011-08-17', 'Roche/Genentech', 'V600E'
FROM genes WHERE gene_symbol = 'BRAF';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Dabrafenib (Tafinlar)', 'BRAF V600E/K inhibitor', 'Approved', 'Melanoma with BRAF V600', '2013-05-29', 'Novartis', 'V600E, V600K'
FROM genes WHERE gene_symbol = 'BRAF';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Encorafenib (Braftovi)', 'BRAF V600E/K inhibitor', 'Approved', 'Melanoma with BRAF V600', '2018-06-27', 'Array BioPharma', 'V600E, V600K'
FROM genes WHERE gene_symbol = 'BRAF';

-- ALK inhibitors (for lung cancer with ALK fusions)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Alectinib (Alecensa)', 'Second-generation ALK inhibitor', 'Approved', 'ALK-positive NSCLC', '2015-12-11', 'Roche/Genentech', 'ALK fusions, ALK resistance mutations'
FROM genes WHERE gene_symbol = 'ALK';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Crizotinib (Xalkori)', 'First-generation ALK inhibitor', 'Approved', 'ALK-positive NSCLC', '2011-08-26', 'Pfizer', 'ALK fusions'
FROM genes WHERE gene_symbol = 'ALK';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Ceritinib (Zykadia)', 'Second-generation ALK inhibitor', 'Approved', 'ALK-positive NSCLC', '2014-04-29', 'Novartis', 'ALK fusions, crizotinib-resistant'
FROM genes WHERE gene_symbol = 'ALK';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Brigatinib (Alunbrig)', 'Second-generation ALK inhibitor', 'Approved', 'ALK-positive NSCLC', '2017-04-28', 'Takeda', 'ALK fusions, ALK resistance mutations'
FROM genes WHERE gene_symbol = 'ALK';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Lorlatinib (Lorbrena)', 'Third-generation ALK inhibitor', 'Approved', 'ALK-positive NSCLC', '2018-11-02', 'Pfizer', 'ALK fusions, multiple resistance mutations'
FROM genes WHERE gene_symbol = 'ALK';

-- HER2 targeted therapies (for breast cancer with HER2 amplification)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Trastuzumab (Herceptin)', 'HER2 monoclonal antibody', 'Approved', 'HER2-positive breast cancer', '1998-09-25', 'Genentech/Roche', 'HER2 amplification/overexpression'
FROM genes WHERE gene_symbol = 'HER2';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Pertuzumab (Perjeta)', 'HER2 dimerization inhibitor', 'Approved', 'HER2-positive breast cancer', '2012-06-08', 'Genentech/Roche', 'HER2 amplification/overexpression'
FROM genes WHERE gene_symbol = 'HER2';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'T-DM1 (Kadcyla)', 'HER2 antibody-drug conjugate', 'Approved', 'HER2-positive breast cancer', '2013-02-22', 'Genentech/Roche', 'HER2 amplification/overexpression'
FROM genes WHERE gene_symbol = 'HER2';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'T-DXd (Enhertu)', 'HER2 antibody-drug conjugate', 'Approved', 'HER2-positive breast cancer', '2019-12-20', 'Daiichi Sankyo/AstraZeneca', 'HER2 amplification/overexpression'
FROM genes WHERE gene_symbol = 'HER2';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Lapatinib (Tykerb)', 'HER2/EGFR dual TKI', 'Approved', 'HER2-positive breast cancer', '2007-03-13', 'GlaxoSmithKline', 'HER2 amplification/overexpression'
FROM genes WHERE gene_symbol = 'HER2';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Neratinib (Nerlynx)', 'Irreversible pan-HER inhibitor', 'Approved', 'HER2-positive breast cancer', '2017-07-17', 'Puma Biotechnology', 'HER2 amplification/overexpression'
FROM genes WHERE gene_symbol = 'HER2';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Tucatinib (Tukysa)', 'Selective HER2 TKI', 'Approved', 'HER2-positive breast cancer', '2020-04-17', 'Seagen', 'HER2 amplification/overexpression'
FROM genes WHERE gene_symbol = 'HER2';

-- KRAS G12C inhibitors (breakthrough drugs for KRAS)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Sotorasib (Lumakras)', 'KRAS G12C covalent inhibitor', 'Approved', 'NSCLC with KRAS G12C', '2021-05-28', 'Amgen', 'G12C'
FROM genes WHERE gene_symbol = 'KRAS';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Adagrasib (Krazati)', 'KRAS G12C covalent inhibitor', 'Approved', 'NSCLC with KRAS G12C', '2022-12-12', 'Mirati', 'G12C'
FROM genes WHERE gene_symbol = 'KRAS';

-- PIK3CA inhibitor (for breast cancer with PIK3CA mutations)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Alpelisib (Piqray)', 'PI3K alpha selective inhibitor', 'Approved', 'HR+/HER2- breast cancer with PIK3CA mutations', '2019-05-24', 'Novartis', 'H1047R, E545K, E542K'
FROM genes WHERE gene_symbol = 'PIK3CA';

-- PARP inhibitors (for BRCA-mutated cancers)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Olaparib (Lynparza)', 'PARP inhibitor', 'Approved', 'BRCA-mutated ovarian cancer', '2014-12-19', 'AstraZeneca', 'BRCA1/2 mutations'
FROM genes WHERE gene_symbol = 'BRCA1';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Rucaparib (Rubraca)', 'PARP inhibitor', 'Approved', 'BRCA-mutated ovarian cancer', '2016-12-19', 'Clovis Oncology', 'BRCA1/2 mutations'
FROM genes WHERE gene_symbol = 'BRCA1';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Niraparib (Zejula)', 'PARP inhibitor', 'Approved', 'Ovarian cancer maintenance', '2017-03-27', 'GSK', 'BRCA1/2 mutations, HRD'
FROM genes WHERE gene_symbol = 'BRCA1';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Talazoparib (Talzenna)', 'PARP inhibitor', 'Approved', 'BRCA-mutated breast cancer', '2018-10-16', 'Pfizer', 'BRCA1/2 mutations'
FROM genes WHERE gene_symbol = 'BRCA1';

-- Also add PARP inhibitors for BRCA2
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Olaparib (Lynparza)', 'PARP inhibitor', 'Approved', 'BRCA-mutated ovarian cancer', '2014-12-19', 'AstraZeneca', 'BRCA1/2 mutations'
FROM genes WHERE gene_symbol = 'BRCA2';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Rucaparib (Rubraca)', 'PARP inhibitor', 'Approved', 'BRCA-mutated ovarian cancer', '2016-12-19', 'Clovis Oncology', 'BRCA1/2 mutations'
FROM genes WHERE gene_symbol = 'BRCA2';

-- IDH inhibitors (for glioma and AML)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Ivosidenib (Tibsovo)', 'IDH1 inhibitor', 'Approved', 'AML with IDH1 mutation', '2018-07-20', 'Servier', 'R132'
FROM genes WHERE gene_symbol = 'IDH1';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Enasidenib (Idhifa)', 'IDH2 inhibitor', 'Approved', 'AML with IDH2 mutation', '2017-08-01', 'Bristol Myers Squibb', 'R140, R172'
FROM genes WHERE gene_symbol = 'IDH2';

-- MET inhibitors
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Capmatinib (Tabrecta)', 'Selective MET inhibitor', 'Approved', 'NSCLC with MET exon 14 skipping', '2020-05-06', 'Novartis', 'MET exon 14 skipping'
FROM genes WHERE gene_symbol = 'MET';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Tepotinib (Tepmetko)', 'Selective MET inhibitor', 'Approved', 'NSCLC with MET exon 14 skipping', '2021-02-03', 'Merck KGaA', 'MET exon 14 skipping'
FROM genes WHERE gene_symbol = 'MET';

-- RET inhibitors
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Selpercatinib (Retevmo)', 'Selective RET inhibitor', 'Approved', 'RET fusion-positive NSCLC and thyroid cancer', '2020-05-08', 'Eli Lilly', 'RET fusions, RET mutations'
FROM genes WHERE gene_symbol = 'RET';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Pralsetinib (Gavreto)', 'Selective RET inhibitor', 'Approved', 'RET fusion-positive NSCLC', '2020-09-04', 'Blueprint Medicines', 'RET fusions'
FROM genes WHERE gene_symbol = 'RET';

-- NRAS targeted therapy (MEK inhibitors are used for NRAS-mutant cancers)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Binimetinib (Mektovi)', 'MEK inhibitor', 'Approved', 'NRAS-mutant melanoma (with encorafenib)', '2018-06-27', 'Array BioPharma', 'NRAS Q61'
FROM genes WHERE gene_symbol = 'NRAS';

-- CDK4 inhibitor (though we might not have CDK4 in genes table)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Palbociclib (Ibrance)', 'CDK4/6 inhibitor', 'Approved', 'HR+ breast cancer', '2015-02-03', 'Pfizer', 'CDK4 amplification'
FROM genes WHERE gene_symbol = 'CDK4';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Ribociclib (Kisqali)', 'CDK4/6 inhibitor', 'Approved', 'HR+ breast cancer', '2017-03-13', 'Novartis', 'CDK4 amplification'
FROM genes WHERE gene_symbol = 'CDK4';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Abemaciclib (Verzenio)', 'CDK4/6 inhibitor', 'Approved', 'HR+ breast cancer', '2017-09-28', 'Eli Lilly', 'CDK4 amplification'
FROM genes WHERE gene_symbol = 'CDK4';

-- FLT3 inhibitors (for AML)
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Midostaurin (Rydapt)', 'Multi-kinase inhibitor', 'Approved', 'FLT3-mutated AML', '2017-04-28', 'Novartis', 'FLT3-ITD, FLT3-TKD'
FROM genes WHERE gene_symbol = 'FLT3';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Gilteritinib (Xospata)', 'Selective FLT3 inhibitor', 'Approved', 'FLT3-mutated AML', '2018-11-28', 'Astellas', 'FLT3-ITD, FLT3-TKD'
FROM genes WHERE gene_symbol = 'FLT3';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Quizartinib (Vanflyta)', 'Selective FLT3 inhibitor', 'Approved', 'FLT3-ITD AML', '2023-07-20', 'Daiichi Sankyo', 'FLT3-ITD'
FROM genes WHERE gene_symbol = 'FLT3';

-- JAK2 inhibitor
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Ruxolitinib (Jakafi)', 'JAK1/2 inhibitor', 'Approved', 'Myelofibrosis with JAK2 V617F', '2011-11-16', 'Incyte/Novartis', 'V617F'
FROM genes WHERE gene_symbol = 'JAK2';

-- FGFR inhibitors
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Erdafitinib (Balversa)', 'Pan-FGFR inhibitor', 'Approved', 'Bladder cancer with FGFR alterations', '2019-04-12', 'Janssen', 'FGFR3 mutations/fusions'
FROM genes WHERE gene_symbol = 'FGFR3';

-- KIT inhibitor
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Imatinib (Gleevec)', 'KIT/PDGFR/BCR-ABL inhibitor', 'Approved', 'GIST with KIT mutations', '2001-05-10', 'Novartis', 'KIT exon 11, exon 9'
FROM genes WHERE gene_symbol = 'KIT';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Sunitinib (Sutent)', 'Multi-kinase inhibitor', 'Approved', 'GIST resistant to imatinib', '2006-01-26', 'Pfizer', 'KIT exon 11, exon 9'
FROM genes WHERE gene_symbol = 'KIT';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Regorafenib (Stivarga)', 'Multi-kinase inhibitor', 'Approved', 'GIST resistant to imatinib/sunitinib', '2013-02-25', 'Bayer', 'KIT multiple resistance mutations'
FROM genes WHERE gene_symbol = 'KIT';

-- Add some experimental/Phase III drugs for completeness
INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'MRTX1133', 'KRAS G12D inhibitor', 'Phase I', 'Solid tumors with KRAS G12D', NULL, 'Mirati', 'G12D'
FROM genes WHERE gene_symbol = 'KRAS';

INSERT OR IGNORE INTO therapeutics (gene_id, drug_name, mechanism_of_action, clinical_status, indication, fda_approval_date, manufacturer, target_mutations) 
SELECT gene_id, 'Lazertinib', 'Third-generation EGFR TKI', 'Phase III', 'NSCLC with EGFR mutations', NULL, 'Yuhan/Janssen', 'L858R, T790M, exon 19 del'
FROM genes WHERE gene_symbol = 'EGFR';

SELECT COUNT(*) as total_therapeutics FROM therapeutics;