import express from 'express';
import { Database } from '../config/database';

const router = express.Router();
const db = Database.getInstance();

// GET /api/therapeutics - Get all therapeutic targets
router.get('/', async (req, res) => {
  try {
    const query = `
      SELECT 
        t.therapeutic_id,
        t.drug_name,
        t.mechanism_of_action,
        t.clinical_status,
        t.indication,
        t.fda_approval_date,
        t.manufacturer,
        t.target_mutations,
        g.gene_symbol
      FROM therapeutics t
      JOIN genes g ON t.gene_id = g.gene_id
      ORDER BY t.clinical_status = 'Approved' DESC, t.drug_name ASC
    `;
    
    const therapeutics = await db.query(query);
    res.json({ 
      data: therapeutics,
      total: therapeutics.length 
    });
  } catch (error) {
    console.error('Error fetching therapeutics:', error);
    res.status(500).json({ error: 'Failed to fetch therapeutics' });
  }
});

// GET /api/therapeutics/gene/:geneName - Get therapeutics for specific gene
router.get('/gene/:geneName', async (req, res) => {
  try {
    const { geneName } = req.params;
    
    const query = `
      SELECT 
        t.therapeutic_id,
        t.drug_name,
        t.mechanism_of_action,
        t.clinical_status,
        t.indication,
        t.fda_approval_date,
        t.manufacturer,
        t.target_mutations,
        g.gene_symbol
      FROM therapeutics t
      JOIN genes g ON t.gene_id = g.gene_id
      WHERE g.gene_symbol = ?
      ORDER BY t.clinical_status = 'Approved' DESC, t.drug_name ASC
    `;
    
    const therapeutics = await db.query(query, [geneName.toUpperCase()]);
    res.json({ 
      data: therapeutics,
      total: therapeutics.length,
      gene: geneName
    });
  } catch (error) {
    console.error('Error fetching therapeutics for gene:', error);
    res.status(500).json({ error: 'Failed to fetch therapeutics' });
  }
});

// GET /api/therapeutics/mutation - Get therapeutics for specific mutation
router.get('/mutation', async (req, res) => {
  try {
    const { gene, position, cancerType } = req.query;
    
    if (!gene) {
      return res.status(400).json({ error: 'Gene parameter is required' });
    }
    
    // First get therapeutics for the gene
    const query = `
      SELECT 
        t.therapeutic_id,
        t.drug_name,
        t.mechanism_of_action,
        t.clinical_status,
        t.indication,
        t.fda_approval_date,
        t.manufacturer,
        t.target_mutations,
        g.gene_symbol,
        CASE 
          WHEN t.target_mutations LIKE '%' || ? || '%' THEN 1
          ELSE 0
        END as mutation_specific
      FROM therapeutics t
      JOIN genes g ON t.gene_id = g.gene_id
      WHERE g.gene_symbol = ?
      ORDER BY mutation_specific DESC, t.clinical_status = 'Approved' DESC, t.drug_name ASC
    `;
    
    const positionStr = position ? `${position}` : '';
    const therapeutics = await db.query(query, [positionStr, gene]);
    
    res.json({ 
      data: therapeutics,
      total: therapeutics.length,
      gene,
      position,
      cancerType
    });
  } catch (error) {
    console.error('Error fetching therapeutics for mutation:', error);
    res.status(500).json({ error: 'Failed to fetch therapeutics' });
  }
});

// GET /api/therapeutics/:id - Get specific therapeutic details
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const query = `
      SELECT 
        t.*,
        g.gene_symbol,
        g.gene_name
      FROM therapeutics t
      JOIN genes g ON t.gene_id = g.gene_id
      WHERE t.therapeutic_id = ?
    `;
    
    const therapeutic = await db.get(query, [id]);
    
    if (!therapeutic) {
      return res.status(404).json({ error: 'Therapeutic not found' });
    }
    
    res.json(therapeutic);
  } catch (error) {
    console.error('Error fetching therapeutic details:', error);
    res.status(500).json({ error: 'Failed to fetch therapeutic details' });
  }
});

// GET /api/therapeutics/stats/summary - Get therapeutic statistics
router.get('/stats/summary', async (req, res) => {
  try {
    const stats = await db.get(`
      SELECT 
        COUNT(*) as total_therapeutics,
        COUNT(DISTINCT gene_id) as targeted_genes,
        COUNT(CASE WHEN clinical_status = 'Approved' THEN 1 END) as approved_drugs,
        COUNT(CASE WHEN clinical_status LIKE 'Phase%' THEN 1 END) as in_trials
      FROM therapeutics
    `);
    
    res.json(stats);
  } catch (error) {
    console.error('Error fetching therapeutic stats:', error);
    res.status(500).json({ error: 'Failed to fetch therapeutic statistics' });
  }
});

export default router;