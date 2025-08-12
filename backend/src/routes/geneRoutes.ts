import express from 'express';
import { Database } from '../config/database';

const router = express.Router();
const db = Database.getInstance();

// GET /api/genes - Get all genes
router.get('/', async (req, res) => {
  try {
    const query = `
      SELECT 
        gene_id,
        gene_symbol,
        gene_name,
        chromosome,
        gene_type,
        description
      FROM genes
      ORDER BY gene_symbol ASC
    `;
    
    const genes = await db.query(query);
    res.json({ 
      data: genes,
      total: genes.length 
    });
  } catch (error) {
    console.error('Error fetching genes:', error);
    res.status(500).json({ error: 'Failed to fetch genes' });
  }
});

// GET /api/genes/search - Search genes
router.get('/search', async (req, res) => {
  try {
    const { q } = req.query;
    const searchTerm = q ? String(q).toLowerCase() : '';
    
    const query = `
      SELECT 
        gene_id,
        gene_symbol,
        gene_name,
        chromosome,
        gene_type,
        description
      FROM genes
      WHERE gene_symbol LIKE ? OR gene_name LIKE ?
      ORDER BY 
        CASE WHEN gene_symbol LIKE ? THEN 1 ELSE 2 END,
        gene_symbol ASC
      LIMIT 50
    `;
    
    const searchPattern = `%${searchTerm}%`;
    const exactPattern = `${searchTerm}%`;
    const genes = await db.query(query, [searchPattern, searchPattern, exactPattern]);
    
    res.json({ 
      data: genes,
      total: genes.length,
      query: searchTerm
    });
  } catch (error) {
    console.error('Error searching genes:', error);
    res.status(500).json({ error: 'Failed to search genes' });
  }
});

// GET /api/genes/:geneSymbol - Get specific gene details
router.get('/:geneSymbol', async (req, res) => {
  try {
    const { geneSymbol } = req.params;
    
    const query = `
      SELECT 
        gene_id,
        gene_symbol,
        gene_name,
        chromosome,
        start_position,
        end_position,
        strand,
        gene_type,
        description,
        created_at,
        updated_at
      FROM genes
      WHERE gene_symbol = ?
    `;
    
    const gene = await db.get(query, [geneSymbol.toUpperCase()]);
    
    if (!gene) {
      return res.status(404).json({ error: 'Gene not found' });
    }
    
    res.json(gene);
  } catch (error) {
    console.error('Error fetching gene details:', error);
    res.status(500).json({ error: 'Failed to fetch gene details' });
  }
});

// GET /api/genes/:geneSymbol/mutations - Get mutations for specific gene
router.get('/:geneSymbol/mutations', async (req, res) => {
  try {
    const { geneSymbol } = req.params;
    const { cancerType } = req.query;
    
    let query = `
      SELECT 
        m.*,
        g.gene_symbol,
        ct.cancer_name
      FROM mutations m
      JOIN genes g ON m.gene_id = g.gene_id
      JOIN cancer_types ct ON m.cancer_type_id = ct.cancer_type_id
      WHERE g.gene_symbol = ?
    `;
    
    const params = [geneSymbol.toUpperCase()];
    
    if (cancerType) {
      query += ' AND ct.cancer_name LIKE ?';
      params.push(`%${cancerType}%`);
    }
    
    query += ' ORDER BY m.frequency DESC, m.mutation_count DESC';
    
    const mutations = await db.query(query, params);
    
    res.json({ 
      data: mutations,
      total: mutations.length,
      gene: geneSymbol,
      cancerType: cancerType || null
    });
  } catch (error) {
    console.error('Error fetching gene mutations:', error);
    res.status(500).json({ error: 'Failed to fetch gene mutations' });
  }
});

// GET /api/genes/:geneSymbol/therapeutics - Get therapeutics for specific gene
router.get('/:geneSymbol/therapeutics', async (req, res) => {
  try {
    const { geneSymbol } = req.params;
    
    const query = `
      SELECT 
        t.*,
        g.gene_symbol
      FROM therapeutics t
      JOIN genes g ON t.gene_id = g.gene_id
      WHERE g.gene_symbol = ?
      ORDER BY t.clinical_status = 'Approved' DESC, t.drug_name ASC
    `;
    
    const therapeutics = await db.query(query, [geneSymbol.toUpperCase()]);
    
    res.json({ 
      data: therapeutics,
      total: therapeutics.length,
      gene: geneSymbol
    });
  } catch (error) {
    console.error('Error fetching gene therapeutics:', error);
    res.status(500).json({ error: 'Failed to fetch gene therapeutics' });
  }
});

// GET /api/genes/stats/summary - Get gene statistics
router.get('/stats/summary', async (req, res) => {
  try {
    const stats = await db.get(`
      SELECT 
        COUNT(*) as total_genes,
        COUNT(CASE WHEN gene_type = 'oncogene' THEN 1 END) as oncogenes,
        COUNT(CASE WHEN gene_type = 'tumor_suppressor' THEN 1 END) as tumor_suppressors,
        COUNT(CASE WHEN gene_type = 'context' THEN 1 END) as context_dependent
      FROM genes
    `);
    
    res.json(stats);
  } catch (error) {
    console.error('Error fetching gene stats:', error);
    res.status(500).json({ error: 'Failed to fetch gene statistics' });
  }
});

export default router;