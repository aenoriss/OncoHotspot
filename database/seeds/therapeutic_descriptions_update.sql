-- Comprehensive Therapeutic Descriptions with Mechanism and Clinical Data
-- Based on 2024 clinical data and FDA approvals

-- Add detailed therapeutic descriptions with mechanism, efficacy, and resistance information
UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Third-generation irreversible EGFR TKI that covalently binds to cysteine-797 in the ATP-binding site. Highly selective for EGFR-activating mutations and T790M resistance mutation, with ~200-fold selectivity over wild-type EGFR.

CLINICAL EFFICACY (FLAURA Trial): 
- First-line PFS: 18.9 months vs 10.2 months (gefitinib/erlotinib)
- Overall survival: 38.6 months vs 31.8 months
- CNS metastases PFS: 15.2 months vs 9.6 months
- Objective response rate: 80% vs 76%

RESISTANCE PATTERNS: Inevitable resistance develops after ~19 months in first-line therapy. Main mechanisms include:
- C797S mutation (~25% of cases) - prevents covalent binding
- MET amplification (~25%) - bypass pathway activation
- Histologic transformation (~14%) - small cell transformation
- TP53 co-mutations reduce PFS significantly

CLINICAL NOTES: Standard first-line therapy for EGFR-mutated NSCLC. Superior CNS penetration compared to earlier-generation TKIs. 2024 research emphasizes biomarker-driven combination strategies.',
    side_effects = 'Most common (≥20%): Diarrhea (58%), skin reactions (45%), nail toxicity (35%), stomatitis (29%), decreased appetite (27%). Serious: Interstitial lung disease (<1%), QT prolongation (<1%), cardiomyopathy (<1%). Generally better tolerated than first/second-generation EGFR TKIs with less skin toxicity.'
WHERE drug_name = 'Osimertinib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Covalent KRAS G12C inhibitor that forms irreversible bond with cysteine-12 in mutant KRAS protein. Constrains KRAS G12C to GDP-bound inactive state, preventing downstream signaling through RAF/MEK/ERK and PI3K/AKT pathways.

CLINICAL EFFICACY (CodeBreak 100):
- Objective response rate: 37.1% in previously treated NSCLC
- Median PFS: 6.8 months
- Median overall survival: 12.5 months
- Disease control rate: 80.6%
- CNS response rate: 23% in patients with brain metastases

RESISTANCE MECHANISMS: Primary and acquired resistance common. Secondary KRAS mutations include:
- Y96D/Y96S (~15% of resistant cases)
- G12C/R68S, G12C/Y96C double mutants
- Alternative pathway activation (RTK bypass)

CLINICAL NOTES: First-in-class KRAS G12C inhibitor. FDA accelerated approval May 2021. Limited efficacy due to intrinsic resistance in many patients. Combination strategies with SHP2 inhibitors, MEK inhibitors being explored.',
    side_effects = 'Most common (≥20%): Diarrhea (42%), musculoskeletal pain (39%), nausea (32%), fatigue (24%), hepatotoxicity (21%). Serious: Elevated ALT/AST (4%), hepatic dysfunction. Monitor liver function regularly. Generally manageable toxicity profile.'
WHERE drug_name = 'Sotorasib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Covalent KRAS G12C inhibitor with similar mechanism to sotorasib but enhanced pharmacokinetic properties and CNS penetration. Irreversibly binds cysteine-12 to lock KRAS in inactive GDP-bound state.

CLINICAL EFFICACY (KRYSTAL-1):
- Objective response rate: 42.9% in NSCLC
- Median PFS: 6.5 months in NSCLC
- CNS objective response rate: 33.3%
- KRYSTAL-12 Phase III: PFS 5.49 months vs 3.84 months (docetaxel)

RESISTANCE PATTERNS: Similar to sotorasib with some differences:
- G13D, R68M, A59S, A59T mutations remain sensitive to adagrasib
- Q99L mutation resistant to adagrasib but sensitive to sotorasib
- H95D, H95Q, H95R mutations remain sensitive

CLINICAL NOTES: FDA accelerated approval December 2022. Better CNS penetration than sotorasib. KRYSTAL-7 trial: 63% ORR when combined with pembrolizumab in PD-L1 high patients. Potential advantage in brain metastases.',
    side_effects = 'Most common (≥20%): Diarrhea (53%), nausea (44%), vomiting (30%), decreased appetite (28%), dehydration (23%). Lower hepatotoxicity risk vs sotorasib but higher risk of GI toxicity and serious adverse events overall. Monitor hydration status.'
WHERE drug_name = 'Adagrasib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: BRAF V600E/K inhibitor that blocks constitutive MAPK pathway activation. Selective ATP-competitive inhibitor of BRAF kinase domain. Paradoxically can activate pathway in wild-type BRAF cells.

CLINICAL EFFICACY (Melanoma):
- Objective response rate: 48% as monotherapy
- Median PFS: 5.3 months monotherapy, 9.3 months with cobimetinib
- Overall survival: 13.6 months monotherapy
- Response rates higher in BRAF V600E vs V600K mutations

RESISTANCE MECHANISMS: Rapid resistance development (median 6-8 months):
- NRAS mutations (~20% of cases)
- MEK1/2 mutations
- BRAF splice variants/amplification
- PI3K/AKT pathway activation
- COT upregulation

CLINICAL NOTES: First FDA-approved BRAF inhibitor (2011). Combination with MEK inhibitors standard to prevent resistance. Significant survival benefit in V600E-mutant melanoma. Also active in V600E-mutant colorectal cancer and thyroid cancer.',
    side_effects = 'Most common (≥20%): Arthralgia (53%), rash (37%), fatigue (37%), alopecia (36%), nausea (35%). Serious: Secondary malignancies (24%), photosensitivity, QT prolongation. Paradoxical activation can cause keratoacanthomas/cutaneous SCCs. Requires dermatologic monitoring.'
WHERE drug_name = 'Vemurafenib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: HER2-targeted antibody-drug conjugate combining trastuzumab with DM1 cytotoxic payload. Binds HER2, internalizes, releases DM1 to cause microtubule disruption and cell death.

CLINICAL EFFICACY (EMILIA Trial):
- Median PFS: 9.6 months vs 6.4 months (lapatinib+capecitabine)
- Median OS: 30.9 months vs 25.1 months
- Objective response rate: 43.6% vs 30.8%
- Lower CNS progression than comparator

RESISTANCE MECHANISMS:
- Loss of HER2 expression (~15% of cases)
- Impaired T-DM1 trafficking/processing
- Multidrug resistance proteins (MDR1)
- Alternative pathway activation (PI3K/AKT)
- Epithelial-mesenchymal transition

CLINICAL NOTES: Second-line standard for HER2+ metastatic breast cancer after trastuzumab-based therapy. Combines targeted delivery with cytotoxic payload. Better CNS control than lapatinib combinations. Bystander effect may kill neighboring low-HER2 cells.',
    side_effects = 'Most common (≥20%): Fatigue (36%), nausea (40%), musculoskeletal pain (36%), hemorrhage (29%), thrombocytopenia (28%). Serious: Hepatotoxicity (8%), left ventricular dysfunction (2%), thrombocytopenia (12.9%). Monitor cardiac function and liver enzymes. Infusion reactions rare.'
WHERE drug_name = 'T-DM1';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Selective RET kinase inhibitor with high potency against RET fusions and mutations. Designed to minimize off-target effects and overcome resistance mutations that affect multi-kinase inhibitors.

CLINICAL EFFICACY (LIBRETTO-001):
- RET-fusion NSCLC: ORR 61.3%, median PFS 16.5 months
- RET-mutant medullary thyroid cancer: ORR 69%, median PFS not reached
- CNS response rate: 91% in measurable CNS lesions
- Durable responses in most patients

RESISTANCE MECHANISMS: Emerging resistance patterns include:
- RET kinase domain mutations (G810R, G810S)
- Bypass pathway activation (MET, HER3)
- Histologic transformation
- Alternative RET fusion partners

CLINICAL NOTES: FDA approved September 2020 for RET-altered cancers. Superior to multi-kinase RET inhibitors with better selectivity and CNS penetration. Tissue-agnostic approval for RET fusions. Standard first-line therapy for RET+ NSCLC and thyroid cancers.',
    side_effects = 'Most common (≥20%): Dry mouth (37%), diarrhea (36%), hypertension (28%), fatigue (27%), constipation (25%). Serious: Hepatotoxicity (9%), QT prolongation (6%), interstitial lung disease (<1%). Generally well-tolerated with manageable toxicity profile. Monitor blood pressure and liver function.'
WHERE drug_name = 'Selpercatinib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: FLT3 inhibitor with dual activity against FLT3-ITD and FLT3-TKD mutations. More selective for FLT3 than first-generation inhibitors with improved CNS penetration.

CLINICAL EFFICACY (ADMIRAL Trial):
- Median overall survival: 9.3 months vs 5.6 months (salvage chemotherapy)  
- Composite complete remission: 21.1% vs 2.5%
- Median event-free survival: 2.8 months vs 0.7 months
- Response rates higher in FLT3-ITD high allelic ratio patients

RESISTANCE MECHANISMS:
- FLT3 kinase domain mutations (D835Y, F691L)
- FLT3-ITD length variations
- Alternative pathway activation (AXL, PI3K)
- Clonal evolution with FLT3-independent clones

CLINICAL NOTES: FDA approved November 2018 for relapsed/refractory FLT3+ AML. Superior to standard chemotherapy in previously treated patients. Combination with chemotherapy under investigation for newly diagnosed AML. Requires continuous dosing for optimal efficacy.',
    side_effects = 'Most common (≥30%): Diarrhea (42%), fatigue (40%), edema (36%), nausea (32%), anemia (32%). Serious: Differentiation syndrome (6%), QT prolongation (4%), posterior reversible encephalopathy syndrome (<1%). Monitor QT interval and electrolytes. CYP3A4 interactions common.'
WHERE drug_name = 'Gilteritinib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Selective PIK3CA inhibitor designed to specifically target the H1047R, E545K, and E542K hotspot mutations. Allosterically inhibits PI3K alpha while sparing beta/gamma/delta isoforms.

CLINICAL EFFICACY (SOLAR-1 Trial):
- Median PFS: 11.0 months vs 5.7 months (fulvestrant alone)
- Objective response rate: 26.6% vs 12.8%
- Clinical benefit rate: 61% vs 45%
- Benefit maintained across PIK3CA mutation subtypes

RESISTANCE MECHANISMS:
- Secondary PIK3CA mutations
- PTEN loss compensation
- mTORC1 feedback activation
- Alternative pathway activation (MAPK, Wnt)
- ESR1 mutations emergence

CLINICAL NOTES: FDA approved May 2019 for PIK3CA-mutated, hormone receptor-positive, HER2-negative metastatic breast cancer. Requires companion diagnostic for PIK3CA mutations. Combination with fulvestrant is standard. Unique toxicity profile requires careful monitoring.',
    side_effects = 'Most common (≥20%): Diarrhea (58%), nausea (45%), decreased appetite (36%), rash (36%), hyperglycemia (65%). Serious: Hyperglycemia (36%), diarrhea (7%), rash (9%). Requires diabetes monitoring/management. Stevens-Johnson syndrome risk. Dose modifications common for hyperglycemia.'
WHERE drug_name = 'Alpelisib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: PARP1/2 inhibitor that exploits synthetic lethality in homologous recombination-deficient tumors. Traps PARP enzymes on DNA, preventing repair of single-strand breaks leading to replication fork collapse.

CLINICAL EFFICACY:
- BRCA-mutant breast cancer (OlympiAD): PFS 7.0 months vs 4.2 months (chemotherapy)
- BRCA-mutant ovarian cancer (SOLO-1): 60% reduction in progression/death risk
- HRD-positive ovarian cancer: significant PFS benefit as maintenance
- gBRCA pancreatic cancer: active as maintenance therapy

RESISTANCE MECHANISMS:
- BRCA reversion mutations (~50% of resistant cases)
- Loss of 53BP1, RIF1 (restore HR capacity) 
- PARP1 mutations preventing trapping
- Multidrug resistance pump upregulation
- Fork replication rescue pathways

CLINICAL NOTES: First PARP inhibitor approved (2014). Multiple indications across breast, ovarian, pancreatic, and prostate cancers. Biomarker-driven therapy requiring BRCA testing or HRD assessment. Combination strategies expanding indications.',
    side_effects = 'Most common (≥20%): Nausea (58%), fatigue (42%), anemia (40%), vomiting (30%), diarrhea (29%). Serious: Myelodysplastic syndrome (<1.5%), acute leukemia (<0.8%), pneumonitis (1.0%). Monitor blood counts regularly. CYP3A4 interactions. Contraception required due to teratogenicity.'
WHERE drug_name = 'Olaparib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Immune checkpoint inhibitor targeting PD-1 receptor on T cells. Blocks PD-1/PD-L1 interaction to restore T-cell activation and anti-tumor immunity. Particularly effective in tumors with high mutation burden.

CLINICAL EFFICACY (Multiple Indications):
- Advanced melanoma: 5-year OS rate 34% (previously treated)
- MSI-high solid tumors: ORR 39.6% tissue-agnostic
- PD-L1+ NSCLC first-line: OS 26.3 months vs 13.4 months (chemotherapy)
- Triple-negative breast cancer: improved pCR rates with chemotherapy

BIOMARKER ASSOCIATIONS:
- PD-L1 expression (>50% strong predictor)
- Microsatellite instability/mismatch repair deficiency
- High tumor mutation burden (≥10 mutations/Mb)
- Tumor-infiltrating lymphocytes presence

CLINICAL NOTES: FDA approved 2014, first for advanced melanoma. Now approved for 20+ cancer types based on biomarkers or tissue of origin. Landmark drug establishing immunotherapy as standard of care. Combination strategies expanding across multiple tumor types.',
    side_effects = 'Most common (≥20%): Fatigue (27%), musculoskeletal pain (26%), decreased appetite (23%), pruritus (23%), diarrhea (20%). Serious: Pneumonitis (3.4%), hepatitis (0.7%), colitis (1.7%), endocrinopathies (4.3%). Requires immune-related adverse event monitoring and corticosteroid management protocols.'
WHERE drug_name = 'Pembrolizumab';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: HIF-2α inhibitor that blocks hypoxia-inducible factor signaling. Specifically designed for VHL-deficient tumors where HIF-2α accumulation drives tumor growth and angiogenesis.

CLINICAL EFFICACY (LITESPARK-004):
- VHL-associated RCC: ORR 49%, median PFS 11.2 months
- VHL-associated CNS hemangioblastomas: ORR 30%
- VHL-associated pancreatic NETs: durable responses observed
- Non-renal lesions also responsive

RESISTANCE MECHANISMS: Limited data due to recent approval:
- HIF-2α binding site mutations emerging
- Alternative angiogenic pathway activation
- VHL-independent HIF regulation

CLINICAL NOTES: FDA approved August 2021 for VHL-associated tumors. First drug targeting HIF-2α pathway directly. Represents precision medicine approach for rare hereditary cancer syndrome. Oral daily dosing with manageable toxicity profile.',
    side_effects = 'Most common (≥20%): Anemia (90%), fatigue (66%), dyspnea (43%), dizziness (33%), nausea (30%). Serious: Anemia (27%), hypoxia (8%), retinal detachment (2%). Monitor hemoglobin closely - dose modifications common for anemia. Generally well-tolerated long-term.'
WHERE drug_name = 'Belzutifan';

-- Update additional key therapeutics
UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Irreversible ALK/ROS1/MET multi-kinase inhibitor. First ALK inhibitor approved, binding to ATP-binding site and inhibiting downstream signaling pathways.

CLINICAL EFFICACY:
- ALK+ NSCLC: ORR 65%, median PFS 7.7 months vs chemotherapy
- ROS1+ NSCLC: ORR 72%, median PFS 19.2 months  
- Response rates similar across ALK fusion variants
- Limited CNS penetration compared to newer ALK inhibitors

RESISTANCE MECHANISMS: Multiple secondary mutations:
- L1196M (most common, ~25% of cases)
- C1156Y, G1269A, S1206Y
- ALK amplification
- EGFR/KIT bypass pathway activation

CLINICAL NOTES: Historic first ALK inhibitor (FDA 2011). Now primarily first-line option where newer agents unavailable. Sequential therapy paradigm: crizotinib → alectinib → lorlatinib addresses resistance patterns.',
    side_effects = 'Most common (≥25%): Vision disorders (60%), diarrhea (53%), nausea (53%), edema (49%), constipation (42%). Serious: Hepatotoxicity (16%), pneumonitis (4%), QT prolongation (4%). Unique visual side effects (light trails, halos) in majority of patients but rarely dose-limiting.'
WHERE drug_name = 'Crizotinib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Highly selective, irreversible ALK inhibitor with excellent CNS penetration. Designed to overcome crizotinib resistance mutations while maintaining potency against native ALK.

CLINICAL EFFICACY (ALEX Trial):
- Treatment-naive ALK+ NSCLC: PFS 34.8 months vs 10.9 months (crizotinib)
- CNS progression: 12% vs 45% with crizotinib
- ORR: 82.9% vs 75.5%
- Superior efficacy across all ALK fusion variants

RESISTANCE MECHANISMS: 
- I1171T/N/S mutations (~25% of cases)
- V1180L, L1198F mutations
- G1202R (sensitive to lorlatinib)
- Compound mutations (multiple ALK mutations)

CLINICAL NOTES: Preferred first-line ALK inhibitor based on superior CNS control and PFS. FDA approved 2015. Standard of care for treatment-naive ALK+ NSCLC. Sequential therapy to lorlatinib for progression.',
    side_effects = 'Most common (≥20%): Constipation (36%), edema (30%), myalgia (29%), cough (21%), rash (21%). Serious: Hepatotoxicity (9%), interstitial lung disease (0.4%), bradycardia (1.2%). Generally better tolerated than crizotinib without visual disturbances. Monitor liver enzymes and heart rate.'
WHERE drug_name = 'Alectinib';

UPDATE therapeutics SET 
    efficacy_data = 'MECHANISM: Third-generation ALK/ROS1 inhibitor designed to overcome resistance mutations from prior ALK inhibitors. Potent against compound mutations and excellent CNS penetration.

CLINICAL EFFICACY:
- Treatment-naive ALK+ NSCLC: PFS 64% at 12 months
- Crizotinib-resistant: ORR 69.5%, intracranial ORR 87%
- Alectinib-resistant: ORR 39%, intracranial ORR 56%
- Active against most ALK resistance mutations

RESISTANCE MECHANISMS:
- L1198Q/H mutations (most common)
- D1203N, E1210K mutations
- ALK-independent mechanisms (NRAS, EGFR)
- Compound mutations affecting multiple residues

CLINICAL NOTES: Most potent ALK inhibitor available. Reserved for progression on other ALK inhibitors due to CNS toxicity concerns. Can be considered first-line in patients with brain metastases. Represents current pinnacle of ALK-targeted therapy.',
    side_effects = 'Most common (≥20%): Hypercholesterolemia (70%), edema (56%), weight gain (31%), cognitive effects (21%). Serious: CNS effects (mood changes, cognitive impairment, hallucinations) in 21% of patients. Requires neuropsychological monitoring and possible dose modifications for CNS toxicity.'
WHERE drug_name = 'Lorlatinib';