-- Comprehensive Gene Descriptions with Cancer-Specific Information
-- Based on 2024 research and clinical data

-- Update genes with detailed descriptions and cancer-specific roles
UPDATE genes SET description = 'Guardian of the genome - TP53 is the most frequently mutated gene in human cancers, encoding p53 protein that regulates cell cycle, apoptosis, and DNA repair. Functions as a transcription factor controlling cell fate decisions in response to cellular stress.

LUNG CANCER: Mutated in ~50-55% of NSCLC and >69% of SCLC cases. TP53 mutations are associated with poor prognosis, treatment resistance, and aggressive tumor behavior. Recent 2024 research shows expanded p53 functions in metabolism, ferroptosis, and immunity.

BREAST CANCER: Somatic TP53 mutations occur in 20-40% of breast cancers. Mutant p53 tumors tend to be more aggressive, resistant to therapy, and associated with poorer outcomes compared to wild-type p53 tumors.

COLORECTAL CANCER: Mutations found in 40-70% of cases. The R248Q mutation is associated with hyperactive STAT3/JAK signaling, promoting tumor growth and invasion through gain-of-function mechanisms.'
WHERE gene_symbol = 'TP53';

UPDATE genes SET description = 'Critical oncogenic driver - KRAS encodes a GTPase protein essential for cellular signaling pathways controlling proliferation, differentiation, and survival. Mutations constitutively activate RAS signaling, promoting uncontrolled cell growth.

LUNG CANCER: Drives ~32% of lung cancers, predominantly NSCLC. KRAS G12C mutations (13% of NSCLC) are now targetable with FDA-approved inhibitors sotorasib and adagrasib. Associated with resistance to EGFR TKIs.

COLORECTAL CANCER: Mutated in ~40% of cases, primarily G12D, G12V, and G13D variants. KRAS mutations predict resistance to anti-EGFR therapies (cetuximab, panitumumab). New G12C inhibitors show promise in treatment-refractory cases.

PANCREATIC CANCER: The most RAS-addicted cancer with 85-90% mutation frequency. Drives extensive metabolic reprogramming including increased glycolysis and glutamine addiction. Novel inhibitors like MRTX1133 (G12D-specific) show promising preclinical activity.'
WHERE gene_symbol = 'KRAS';

UPDATE genes SET description = 'Receptor tyrosine kinase oncogene - EGFR regulates cell proliferation, survival, and migration through multiple downstream pathways. Activating mutations and amplifications drive oncogenic transformation in various cancers.

LUNG CANCER: Activating mutations in ~15% of Caucasian and ~50% of Asian NSCLC patients. Common mutations include L858R and exon 19 deletions, both sensitive to EGFR TKIs. T790M resistance mutation develops in ~60% of cases treated with first/second-generation TKIs.

THERAPEUTIC TARGETING: Osimertinib is the current standard first-line therapy for EGFR-mutated NSCLC. Resistance mechanisms include C797S mutations (~25% of cases), MET amplification, and histologic transformation. 2024 research emphasizes combination strategies and biomarker-driven approaches.

RESISTANCE PATTERNS: Inevitable resistance develops after ~19 months in first-line and ~11 months in second-line settings. TP53 co-mutations significantly reduce progression-free survival on osimertinib therapy.'
WHERE gene_symbol = 'EGFR';

UPDATE genes SET description = 'PI3K pathway oncogene - PIK3CA encodes the catalytic subunit of PI3K, a key regulator of cell growth, metabolism, and survival. Activating mutations lead to constitutive PI3K/AKT/mTOR pathway activation.

BREAST CANCER: Mutated in ~40% of hormone receptor-positive breast cancers. Hotspot mutations H1047R, E545K, and E542K are the most common. FDA-approved inhibitor alpelisib combined with fulvestrant shows efficacy in PIK3CA-mutated, hormone receptor-positive metastatic breast cancer.

COLORECTAL CANCER: Mutations occur in ~15-20% of cases, often co-occurring with KRAS mutations. Associated with resistance to anti-EGFR therapies and poor prognosis in certain contexts.

THERAPEUTIC TARGETING: Selective PIK3CA inhibitors (alpelisib, inavolisib) provide targeted therapy options. Resistance mechanisms include secondary mutations and pathway bypass through alternative growth signals.'
WHERE gene_symbol = 'PIK3CA';

UPDATE genes SET description = 'WNT pathway tumor suppressor - APC is the gatekeeper of colorectal cancer, regulating β-catenin levels and preventing aberrant WNT signaling activation. Loss of function leads to constitutive proliferative signals.

COLORECTAL CANCER: The most frequently mutated gene in colorectal cancer (~80% of cases), typically occurring early in the adenoma-carcinoma sequence. Truncating mutations lead to loss of β-catenin regulation and uncontrolled WNT pathway activation.

FAMILIAL ADENOMATOUS POLYPOSIS: Germline APC mutations cause FAP syndrome, characterized by hundreds to thousands of colorectal polyps and near-certain cancer development without prophylactic surgery.

THERAPEUTIC IMPLICATIONS: APC mutations predict sensitivity to WNT pathway inhibitors and immune checkpoint inhibitors in certain contexts. Combination strategies targeting WNT signaling and immune pathways show promise in preclinical studies.'
WHERE gene_symbol = 'APC';

UPDATE genes SET description = 'DNA repair tumor suppressor - BRCA1 is essential for homologous recombination DNA repair, maintaining genomic stability. Loss of function creates homologous recombination deficiency (HRD), making cells vulnerable to PARP inhibition.

BREAST CANCER: Germline mutations confer 50-85% lifetime breast cancer risk, typically triple-negative or high-grade tumors. BRCA1-mutated tumors show distinct molecular signatures and treatment sensitivities.

OVARIAN CANCER: Germline mutations present in ~15% of ovarian cancers, with additional somatic mutations bringing total to ~25%. BRCA1-mutated tumors are highly sensitive to platinum chemotherapy and PARP inhibitors.

THERAPEUTIC TARGETING: PARP inhibitors (olaparib, niraparib, rucaparib, talazoparib) exploit synthetic lethality in BRCA1-deficient tumors. FDA-approved for both treatment and maintenance therapy in BRCA-mutated breast and ovarian cancers.'
WHERE gene_symbol = 'BRCA1';

UPDATE genes SET description = 'DNA repair tumor suppressor - BRCA2 functions in homologous recombination repair, working with BRCA1 to maintain genomic integrity. Mutations create DNA repair deficiency exploitable by targeted therapies.

BREAST CANCER: Germline mutations confer 40-85% lifetime breast cancer risk. BRCA2-mutated breast cancers are often hormone receptor-positive and show better prognosis than BRCA1-mutated tumors when treated appropriately.

OVARIAN CANCER: Present in ~10-15% of ovarian cancers. BRCA2-mutated tumors typically respond well to platinum-based chemotherapy and PARP inhibitors, with longer progression-free survival compared to BRCA-wild-type tumors.

PANCREATIC CANCER: BRCA2 mutations found in 5-10% of pancreatic cancers, associated with better response to platinum-based chemotherapy and improved survival outcomes. PARP inhibitors show activity in BRCA2-mutated pancreatic cancer.'
WHERE gene_symbol = 'BRCA2';

UPDATE genes SET description = 'PI3K/AKT pathway tumor suppressor - PTEN negatively regulates PI3K/AKT signaling, controlling cell growth, survival, and metabolism. Loss of function leads to pathway hyperactivation and oncogenic transformation.

GLIOBLASTOMA: Deleted or mutated in ~40% of GBMs, contributing to therapy resistance and poor prognosis. PTEN loss is associated with mesenchymal subtype and resistance to anti-angiogenic therapy.

BREAST CANCER: PTEN loss occurs in ~30% of breast cancers, particularly triple-negative subtype. Associated with resistance to HER2-targeted therapy and sensitivity to PI3K/AKT inhibitors.

PROSTATE CANCER: Frequently lost in advanced and metastatic disease. PTEN loss promotes androgen receptor signaling and resistance to hormonal therapies, making it a key driver of disease progression.'
WHERE gene_symbol = 'PTEN';

UPDATE genes SET description = 'MAPK pathway oncogene - BRAF encodes a serine/threonine kinase in the RAS/RAF/MEK/ERK pathway. V600E mutation constitutively activates the pathway, driving uncontrolled proliferation.

MELANOMA: V600E mutation present in ~50% of cutaneous melanomas. Highly sensitive to BRAF inhibitors (vemurafenib, dabrafenib, encorafenib) and MEK inhibitors. Combination BRAF+MEK inhibition is standard of care.

COLORECTAL CANCER: V600E mutations in ~8-10% of cases, associated with poor prognosis and resistance to anti-EGFR therapy. BRAF inhibitors combined with anti-EGFR antibodies show efficacy in treatment-refractory disease.

THYROID CANCER: V600E mutations common in papillary thyroid cancer (~45%) and anaplastic thyroid cancer (~25%). BRAF inhibitors show activity in radioiodine-refractory disease.'
WHERE gene_symbol = 'BRAF';

UPDATE genes SET description = 'Receptor tyrosine kinase oncogene - ALK normally regulates nervous system development. Chromosomal rearrangements create oncogenic fusion proteins that drive constitutive kinase activity.

LUNG CANCER: ALK rearrangements in ~3-5% of NSCLC, predominantly in young, light smokers with adenocarcinoma histology. EML4-ALK is the most common fusion variant. Highly sensitive to ALK inhibitors with multiple generations available.

THERAPEUTIC TARGETING: Sequential ALK inhibitor therapy is standard approach: crizotinib → alectinib/ceritinib → lorlatinib for resistance management. Each generation addresses specific resistance mutations while maintaining CNS activity.

RESISTANCE PATTERNS: Resistance develops through secondary ALK mutations (G1269A, C1156Y, L1196M), bypass pathway activation (EGFR, KIT), or histologic transformation. Combination strategies are being explored to prevent resistance.'
WHERE gene_symbol = 'ALK';

UPDATE genes SET description = 'Receptor tyrosine kinase oncogene - RET regulates cell growth, differentiation, and survival. Activating mutations and chromosomal rearrangements drive oncogenic signaling in multiple cancer types.

THYROID CANCER: RET/PTC rearrangements in ~20% of papillary thyroid cancers, particularly radiation-induced tumors. Point mutations (M918T, C634R) drive medullary thyroid cancer (~95% of hereditary cases).

LUNG CANCER: RET fusions in ~1-2% of NSCLC, typically young patients with adenocarcinoma histology. KIF5B-RET and CCDC6-RET are most common fusion partners.

THERAPEUTIC TARGETING: Selective RET inhibitors (selpercatinib, pralsetinib) provide targeted therapy with high response rates (~70%) and excellent CNS penetration. FDA-approved for RET-altered thyroid and lung cancers.'
WHERE gene_symbol = 'RET';

UPDATE genes SET description = 'Receptor tyrosine kinase oncogene - FLT3 regulates hematopoietic stem cell proliferation and survival. Activating mutations drive constitutive signaling and leukemic transformation.

ACUTE MYELOID LEUKEMIA: FLT3 mutations in ~30% of AML patients, including internal tandem duplications (ITD, ~25%) and tyrosine kinase domain mutations (TKD, ~7%). FLT3-ITD associated with poor prognosis and increased relapse risk.

THERAPEUTIC TARGETING: FLT3 inhibitors (midostaurin, gilteritinib, quizartinib) improve outcomes when combined with chemotherapy. Midostaurin + chemotherapy is standard for newly diagnosed FLT3+ AML. Gilteritinib approved for relapsed/refractory disease.

RESISTANCE MECHANISMS: Point mutations in kinase domain, alternative pathway activation, and clonal evolution drive resistance. Combination approaches and next-generation inhibitors are being developed.'
WHERE gene_symbol = 'FLT3';

UPDATE genes SET description = 'JAK/STAT pathway oncogene - JAK2 transmits cytokine signals controlling hematopoiesis. V617F mutation leads to constitutive activation and myeloproliferative disorders.

MYELOPROLIFERATIVE NEOPLASMS: V617F mutation in ~95% of polycythemia vera, ~55% of essential thrombocythemia, and ~65% of myelofibrosis cases. Drives excessive blood cell production and disease complications.

THERAPEUTIC TARGETING: JAK inhibitors (ruxolitinib, fedratinib, pacritinib) provide symptomatic relief and spleen reduction in myelofibrosis. Ruxolitinib also effective in polycythemia vera resistant to hydroxyurea.

DISEASE MONITORING: JAK2 V617F allele burden correlates with disease severity and can be monitored to assess treatment response and disease progression.'
WHERE gene_symbol = 'JAK2';

UPDATE genes SET description = 'Receptor tyrosine kinase oncogene - KIT regulates cell survival, proliferation, and differentiation. Activating mutations drive constitutive signaling in gastrointestinal stromal tumors and other malignancies.

GASTROINTESTINAL STROMAL TUMORS: KIT mutations in ~85% of GISTs, most commonly in exons 11 (~70%) and 9 (~15%). Exon 11 mutations are more sensitive to imatinib therapy than exon 9 mutations.

THERAPEUTIC TARGETING: Sequential tyrosine kinase inhibitor therapy: imatinib → sunitinib → regorafenib → ripretinib for progressive disease. Each agent addresses specific resistance patterns while maintaining clinical benefit.

RESISTANCE PATTERNS: Secondary KIT mutations develop in ~50% of imatinib-resistant cases. Common resistance mutations include T670I, D816V, and N822K, each requiring specific therapeutic approaches.'
WHERE gene_symbol = 'KIT';

UPDATE genes SET description = 'Hypoxia response tumor suppressor - VHL regulates cellular oxygen sensing through HIF-α degradation. Loss of function leads to constitutive hypoxic response and angiogenesis activation.

RENAL CELL CARCINOMA: VHL mutations/deletions in ~80% of clear cell RCC cases. Loss of VHL function leads to HIF-2α accumulation, driving angiogenesis and metabolic reprogramming characteristic of ccRCC.

VON HIPPEL-LINDAU SYNDROME: Germline VHL mutations cause hereditary cancer syndrome with predisposition to clear cell RCC, pheochromocytoma, pancreatic neuroendocrine tumors, and CNS hemangioblastomas.

THERAPEUTIC TARGETING: HIF-2α inhibitor belzutifan provides targeted therapy for VHL-associated tumors. Anti-angiogenic agents (sunitinib, pazopanib, cabozantinib) exploit VHL-driven angiogenesis dependence.'
WHERE gene_symbol = 'VHL';

-- Update remaining genes with comprehensive descriptions
UPDATE genes SET description = 'DNA mismatch repair tumor suppressor - MLH1 is essential for correcting DNA replication errors. Loss of function leads to microsatellite instability (MSI) and increased mutation burden.

COLORECTAL CANCER: MLH1 promoter hypermethylation in ~15% of cases causes MSI-high phenotype. Associated with better prognosis and high response rates to immune checkpoint inhibitors.

LYNCH SYNDROME: Germline MLH1 mutations cause hereditary nonpolyposis colorectal cancer with increased risk of colorectal, endometrial, and other cancers.

THERAPEUTIC IMPLICATIONS: MSI-high tumors are highly responsive to PD-1/PD-L1 inhibitors due to high neoantigen burden. Pembrolizumab approved for MSI-high solid tumors regardless of site of origin.'
WHERE gene_symbol = 'MLH1';

UPDATE genes SET description = 'DNA mismatch repair tumor suppressor - MSH2 works with MLH1 to correct DNA replication errors. Mutations lead to mismatch repair deficiency and microsatellite instability.

COLORECTAL CANCER: MSH2 mutations cause Lynch syndrome with high colorectal cancer risk. MSH2-deficient tumors show MSI-high phenotype with characteristic molecular features.

ENDOMETRIAL CANCER: MSH2 mutations associated with increased endometrial cancer risk in Lynch syndrome patients. MSI-high endometrial cancers respond well to immune checkpoint inhibitors.

BIOMARKER UTILITY: MSH2 protein loss by immunohistochemistry is used to identify mismatch repair-deficient tumors eligible for immune checkpoint inhibitor therapy.'
WHERE gene_symbol = 'MSH2';

UPDATE genes SET description = 'DNA damage response tumor suppressor - ATM coordinates cellular responses to DNA double-strand breaks through checkpoint activation and DNA repair. Mutations impair DNA repair capacity.

CHRONIC LYMPHOCYTIC LEUKEMIA: ATM deletions/mutations in ~10-15% of CLL cases, associated with poor prognosis and treatment resistance. Predicts sensitivity to DNA-damaging agents.

BREAST CANCER: ATM mutations confer moderate breast cancer risk and may predict PARP inhibitor sensitivity through DNA repair deficiency mechanisms.

THERAPEUTIC TARGETING: ATM inhibitors in clinical development exploit synthetic lethality in DNA repair-deficient cancers. Combination with DNA-damaging agents shows synergistic activity.'
WHERE gene_symbol = 'ATM';

UPDATE genes SET description = 'SWI/SNF chromatin remodeling tumor suppressor - ARID1A regulates gene expression through chromatin remodeling. Loss of function alters transcriptional programs and promotes tumorigenesis.

OVARIAN CANCER: ARID1A mutations in ~50% of clear cell and ~30% of endometrioid ovarian cancers. Associated with better prognosis and potential sensitivity to PARP inhibitors.

GASTRIC CANCER: Mutations in ~10-15% of cases. ARID1A-deficient tumors show distinct molecular features and may respond differently to targeted therapies.

THERAPEUTIC TARGETING: ARID1A-deficient tumors may be vulnerable to EZH2 inhibitors, PARP inhibitors, and immune checkpoint inhibitors through synthetic lethality mechanisms.'
WHERE gene_symbol = 'ARID1A';

UPDATE genes SET description = 'Developmental signaling oncogene - NOTCH1 regulates cell fate decisions during development and tissue homeostasis. Activating mutations drive constitutive pathway activation.

T-CELL ACUTE LYMPHOBLASTIC LEUKEMIA: NOTCH1 mutations in >60% of T-ALL cases, typically involving PEST domain deletions that prevent protein degradation. Key driver of leukemic transformation.

CHRONIC LYMPHOCYTIC LEUKEMIA: NOTCH1 mutations in ~10% of CLL cases, associated with poor prognosis and resistance to standard therapies. Predicts shorter overall survival.

THERAPEUTIC TARGETING: γ-secretase inhibitors block NOTCH activation but cause significant toxicity. Selective NOTCH1 inhibitors and antibodies are in clinical development.'
WHERE gene_symbol = 'NOTCH1';

UPDATE genes SET description = 'Nucleolar oncogene - NPM1 regulates ribosome biogenesis, protein transport, and p53 pathway. Mutations create aberrant cytoplasmic localization and oncogenic functions.

ACUTE MYELOID LEUKEMIA: NPM1 mutations in ~35% of AML cases, particularly normal karyotype AML. Associated with better prognosis when not accompanied by FLT3-ITD mutations.

BIOMARKER UTILITY: NPM1 mutations define a distinct AML subtype with characteristic gene expression profile and favorable response to intensive chemotherapy.

THERAPEUTIC TARGETING: NPM1-mutated AML may be sensitive to nuclear export inhibitors (selinexor) and specific targeted agents exploiting the aberrant cytoplasmic localization.'
WHERE gene_symbol = 'NPM1';