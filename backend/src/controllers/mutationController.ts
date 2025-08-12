import { Request, Response } from 'express';
import { MutationService } from '../services/mutationService';

const mutationService = new MutationService();

export const getMutations = async (req: Request, res: Response) => {
  try {
    const { 
      genes, 
      cancerTypes, 
      minCount, 
      maxCount, 
      page = 1, 
      limit = 1000 
    } = req.query;

    const filters = {
      genes: genes ? String(genes).split(',') : undefined,
      cancerTypes: cancerTypes ? String(cancerTypes).split(',') : undefined,
      minCount: minCount ? parseInt(String(minCount)) : undefined,
      maxCount: maxCount ? parseInt(String(maxCount)) : undefined
    };

    const mutations = await mutationService.getMutations(
      filters, 
      parseInt(String(page)), 
      parseInt(String(limit))
    );

    res.json(mutations);
  } catch (error) {
    console.error('Error fetching mutations:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const getAllMutations = async (req: Request, res: Response) => {
  try {
    const mutations = await mutationService.getAllMutations();
    res.json({ data: mutations });
  } catch (error) {
    console.error('Error fetching all mutations:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const getMutationsByGene = async (req: Request, res: Response) => {
  try {
    const { geneName } = req.params;
    const mutations = await mutationService.getMutationsByGene(geneName);
    res.json(mutations);
  } catch (error) {
    console.error('Error fetching mutations by gene:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const getMutationStats = async (req: Request, res: Response) => {
  try {
    const stats = await mutationService.getMutationStatistics();
    res.json(stats);
  } catch (error) {
    console.error('Error fetching mutation stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const getAllGenes = async (req: Request, res: Response) => {
  try {
    const genes = await mutationService.getAllGenes();
    res.json({ data: genes });
  } catch (error) {
    console.error('Error fetching all genes:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const getAllCancerTypes = async (req: Request, res: Response) => {
  try {
    const cancerTypes = await mutationService.getAllCancerTypes();
    res.json({ data: cancerTypes });
  } catch (error) {
    console.error('Error fetching all cancer types:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};