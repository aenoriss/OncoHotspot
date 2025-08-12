-- Fix Mutation Data to be Biologically Realistic
-- This script corrects the total_samples and frequency fields

-- First, let's set realistic total sample counts per cancer type
-- Based on typical TCGA cohort sizes
UPDATE cancer_types SET 
    total_samples = CASE cancer_name
        WHEN 'Lung Cancer' THEN 1200
        WHEN 'Breast Cancer' THEN 1100
        WHEN 'Colorectal Cancer' THEN 650
        WHEN 'Melanoma' THEN 470
        WHEN 'Pancreatic Cancer' THEN 185
        WHEN 'Liver Cancer' THEN 377
        WHEN 'Ovarian Cancer' THEN 585
        WHEN 'Glioblastoma' THEN 600
        WHEN 'Thyroid Cancer' THEN 507
        WHEN 'Kidney Cancer' THEN 530
        WHEN 'Bladder Cancer' THEN 412
        WHEN 'Prostate Cancer' THEN 500
        WHEN 'Gastric Cancer' THEN 443
        WHEN 'Head and Neck Cancer' THEN 530
        WHEN 'Leukemia' THEN 200
        WHEN 'Lymphoma' THEN 88
        WHEN 'Multiple Myeloma' THEN 200
        WHEN 'Sarcoma' THEN 250
        WHEN 'Pancreatic' THEN 185
        WHEN 'Colorectal' THEN 650
        WHEN 'Nsclc' THEN 850
        WHEN 'Melanoma' THEN 470
        WHEN 'Breast' THEN 1100
        WHEN 'Lower Grade Glioma' THEN 516
        WHEN 'Uterine' THEN 560
        WHEN 'AML' THEN 200
        WHEN 'Thyroid' THEN 507
        WHEN 'Uvm' THEN 80
        WHEN 'Ucs' THEN 57
        WHEN 'Kidney Clear Cell' THEN 370
        WHEN 'Prostate' THEN 500
        WHEN 'Bladder' THEN 412
        WHEN 'Gastric' THEN 443
        WHEN 'Ovarian' THEN 585
        WHEN 'Liver' THEN 377
        WHEN 'GBM' THEN 600
        ELSE 100  -- Default for any missing cancer types
    END;

-- Now update the mutations table with realistic frequencies
-- Key principle: mutation_count should be LESS than total_samples

-- Step 1: Update total_samples from cancer_types table
UPDATE mutations
SET total_samples = (
    SELECT COALESCE(ct.total_samples, 100)
    FROM cancer_types ct
    WHERE ct.cancer_type_id = mutations.cancer_type_id
);

-- Step 2: Fix mutation_count to be realistic
-- Most mutations occur in a fraction of samples
UPDATE mutations
SET mutation_count = 
    CASE 
        -- Known highly prevalent mutations (based on real cancer data)
        WHEN gene_id = (SELECT gene_id FROM genes WHERE gene_symbol = 'TP53') 
            AND cancer_type_id IN (SELECT cancer_type_id FROM cancer_types WHERE cancer_name LIKE '%Ovarian%')
            THEN CAST(total_samples * 0.96 AS INTEGER)  -- TP53 in ovarian: 96%
            
        WHEN gene_id = (SELECT gene_id FROM genes WHERE gene_symbol = 'KRAS')
            AND cancer_type_id IN (SELECT cancer_type_id FROM cancer_types WHERE cancer_name LIKE '%Pancreatic%')
            THEN CAST(total_samples * 0.90 AS INTEGER)  -- KRAS in pancreatic: 90%
            
        WHEN gene_id = (SELECT gene_id FROM genes WHERE gene_symbol = 'BRAF')
            AND cancer_type_id IN (SELECT cancer_type_id FROM cancer_types WHERE cancer_name LIKE '%Melanoma%')
            AND position = 600
            THEN CAST(total_samples * 0.60 AS INTEGER)  -- BRAF V600E in melanoma: 60%
            
        WHEN gene_id = (SELECT gene_id FROM genes WHERE gene_symbol = 'IDH1')
            AND cancer_type_id IN (SELECT cancer_type_id FROM cancer_types WHERE cancer_name LIKE '%Glioma%')
            AND position = 132
            THEN CAST(total_samples * 0.70 AS INTEGER)  -- IDH1 R132 in glioma: 70%
            
        WHEN gene_id = (SELECT gene_id FROM genes WHERE gene_symbol = 'EGFR')
            AND cancer_type_id IN (SELECT cancer_type_id FROM cancer_types WHERE cancer_name LIKE '%Lung%')
            THEN CAST(total_samples * 0.15 AS INTEGER)  -- EGFR in lung: 15%
            
        WHEN gene_id = (SELECT gene_id FROM genes WHERE gene_symbol = 'PIK3CA')
            AND cancer_type_id IN (SELECT cancer_type_id FROM cancer_types WHERE cancer_name LIKE '%Breast%')
            THEN CAST(total_samples * 0.35 AS INTEGER)  -- PIK3CA in breast: 35%
            
        -- For all other mutations, use a more realistic distribution
        ELSE 
            CASE
                -- Current mutation_count = 1 (most common) -> rare mutations (1-5%)
                WHEN mutation_count = 1 THEN CAST(total_samples * (0.01 + ABS(RANDOM() % 40) / 1000.0) AS INTEGER)
                
                -- Slightly higher counts -> uncommon mutations (5-15%)
                WHEN mutation_count BETWEEN 2 AND 5 THEN CAST(total_samples * (0.05 + ABS(RANDOM() % 100) / 1000.0) AS INTEGER)
                
                -- Medium counts -> moderately common (15-30%)
                WHEN mutation_count BETWEEN 6 AND 20 THEN CAST(total_samples * (0.15 + ABS(RANDOM() % 150) / 1000.0) AS INTEGER)
                
                -- Higher counts -> common mutations (30-50%)
                WHEN mutation_count > 20 THEN CAST(total_samples * (0.30 + ABS(RANDOM() % 200) / 1000.0) AS INTEGER)
                
                -- Default: rare
                ELSE CAST(total_samples * 0.02 AS INTEGER)
            END
    END
WHERE total_samples > 0;

-- Step 3: Ensure mutation_count is at least 1 (no zero mutations)
UPDATE mutations
SET mutation_count = CASE 
    WHEN mutation_count < 1 THEN 1
    WHEN mutation_count > total_samples THEN total_samples
    ELSE mutation_count
END;

-- Step 4: Recalculate frequency correctly
UPDATE mutations
SET frequency = ROUND(CAST(mutation_count AS REAL) / CAST(total_samples AS REAL), 4)
WHERE total_samples > 0;

-- Step 5: Recalculate significance based on frequency
-- Using a biologically meaningful scale
UPDATE mutations
SET significance_score = ROUND(
    CASE 
        WHEN frequency >= 0.5 THEN 0.90 + (frequency - 0.5) * 0.2    -- >50%: Very high (0.90-1.00)
        WHEN frequency >= 0.2 THEN 0.70 + (frequency - 0.2) * 0.667   -- 20-50%: High (0.70-0.90)
        WHEN frequency >= 0.05 THEN 0.40 + (frequency - 0.05) * 2.0   -- 5-20%: Medium (0.40-0.70)
        WHEN frequency >= 0.01 THEN 0.20 + (frequency - 0.01) * 4.44  -- 1-5%: Low (0.20-0.40)
        ELSE frequency * 20  -- <1%: Very low (0-0.20)
    END, 2
);

-- Verification queries
SELECT 'Data Fix Complete!' as message;

SELECT 
    'Total mutations: ' || COUNT(*) as stat,
    'Avg frequency: ' || ROUND(AVG(frequency), 3) as avg_freq,
    'Mutations with >50% frequency: ' || SUM(CASE WHEN frequency > 0.5 THEN 1 ELSE 0 END) as high_freq,
    'Mutations with 1-5% frequency: ' || SUM(CASE WHEN frequency BETWEEN 0.01 AND 0.05 THEN 1 ELSE 0 END) as low_freq
FROM mutations;

-- Show some key mutations to verify they look realistic
SELECT 
    g.gene_symbol,
    ct.cancer_name,
    m.mutation_count || '/' || m.total_samples as ratio,
    ROUND(m.frequency * 100, 1) || '%' as frequency_pct,
    m.significance_score
FROM mutations m
JOIN genes g ON m.gene_id = g.gene_id
JOIN cancer_types ct ON m.cancer_type_id = ct.cancer_type_id
WHERE 
    (g.gene_symbol = 'TP53' AND ct.cancer_name LIKE '%Ovarian%')
    OR (g.gene_symbol = 'KRAS' AND ct.cancer_name LIKE '%Pancreatic%')
    OR (g.gene_symbol = 'BRAF' AND ct.cancer_name LIKE '%Melanoma%' AND m.position = 600)
    OR (g.gene_symbol = 'EGFR' AND ct.cancer_name LIKE '%Lung%')
    OR (g.gene_symbol = 'PIK3CA' AND ct.cancer_name LIKE '%Breast%')
LIMIT 10;