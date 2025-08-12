import express from 'express';
import { getMutations, getAllMutations, getMutationsByGene, getMutationStats, getAllGenes, getAllCancerTypes } from '../controllers/mutationController';

const router = express.Router();

// GET /api/mutations - Get all mutations with filters
router.get('/', getMutations);

// GET /api/mutations/all - Get ALL mutations without pagination
router.get('/all', getAllMutations);

// GET /api/mutations/genes - Get all genes
router.get('/genes', getAllGenes);

// GET /api/mutations/cancer-types - Get all cancer types  
router.get('/cancer-types', getAllCancerTypes);

// GET /api/mutations/gene/:geneName - Get mutations for specific gene
router.get('/gene/:geneName', getMutationsByGene);

// GET /api/mutations/stats - Get mutation statistics
router.get('/stats', getMutationStats);

export default router;