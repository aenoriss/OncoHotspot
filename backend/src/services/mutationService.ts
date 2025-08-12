import { Database } from '../config/database';

interface MutationData {
  gene: string;
  position: number;
  cancerType: string;
  mutationCount: number;
  significance: number;
  frequency?: number;
  pValue?: number;
  totalSamples?: number;
}

interface MutationFilters {
  genes?: string[];
  cancerTypes?: string[];
  minCount?: number;
  maxCount?: number;
}

export class MutationService {
  private db: Database;

  constructor() {
    this.db = Database.getInstance();
  }

  async getAllMutations() {
    try {
      const query = `
        SELECT 
          g.gene_symbol as gene,
          m.position,
          ct.cancer_name as cancerType,
          m.mutation_count as mutationCount,
          m.significance_score as significance,
          m.frequency,
          m.total_samples as totalSamples,
          m.p_value as pValue,
          m.ref_allele,
          m.alt_allele,
          m.mutation_type
        FROM mutations m
        JOIN genes g ON m.gene_id = g.gene_id
        JOIN cancer_types ct ON m.cancer_type_id = ct.cancer_type_id
        ORDER BY m.frequency DESC, m.mutation_count DESC
      `;

      return await this.db.query(query);
    } catch (error) {
      console.error('Error fetching all mutations:', error);
      throw new Error('Failed to fetch all mutations');
    }
  }

  async getMutations(filters: MutationFilters, page: number, limit: number) {
    try {
      let whereClause = '';
      const params: any[] = [];
      const conditions: string[] = [];

      // Build WHERE clause based on filters
      if (filters.genes && filters.genes.length > 0) {
        const placeholders = filters.genes.map(() => '?').join(',');
        conditions.push(`g.gene_symbol IN (${placeholders})`);
        params.push(...filters.genes);
      }

      if (filters.cancerTypes && filters.cancerTypes.length > 0) {
        const placeholders = filters.cancerTypes.map(() => '?').join(',');
        conditions.push(`ct.cancer_name IN (${placeholders})`);
        params.push(...filters.cancerTypes);
      }

      if (filters.minCount !== undefined) {
        conditions.push(`m.mutation_count >= ?`);
        params.push(filters.minCount);
      }

      if (filters.maxCount !== undefined) {
        conditions.push(`m.mutation_count <= ?`);
        params.push(filters.maxCount);
      }

      if (conditions.length > 0) {
        whereClause = 'WHERE ' + conditions.join(' AND ');
      }

      // Get total count for pagination
      const countQuery = `
        SELECT COUNT(*) as total
        FROM mutations m
        JOIN genes g ON m.gene_id = g.gene_id
        JOIN cancer_types ct ON m.cancer_type_id = ct.cancer_type_id
        ${whereClause}
      `;

      const countResult = await this.db.get(countQuery, params);
      const total = countResult.total;

      // Get paginated data
      const offset = (page - 1) * limit;
      const dataQuery = `
        SELECT 
          g.gene_symbol as gene,
          m.position,
          ct.cancer_name as cancerType,
          m.mutation_count as mutationCount,
          m.significance_score as significance,
          m.frequency,
          m.p_value as pValue,
          m.ref_allele,
          m.alt_allele,
          m.mutation_type
        FROM mutations m
        JOIN genes g ON m.gene_id = g.gene_id
        JOIN cancer_types ct ON m.cancer_type_id = ct.cancer_type_id
        ${whereClause}
        ORDER BY m.significance_score DESC, m.mutation_count DESC
        LIMIT ? OFFSET ?
      `;

      const mutations = await this.db.query(dataQuery, [...params, limit, offset]);

      return {
        data: mutations,
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit)
      };
    } catch (error) {
      console.error('Error fetching mutations:', error);
      throw new Error('Failed to fetch mutations');
    }
  }

  async getMutationsByGene(geneName: string) {
    try {
      const query = `
        SELECT 
          g.gene_symbol as gene,
          m.position,
          ct.cancer_name as cancerType,
          m.mutation_count as mutationCount,
          m.significance_score as significance,
          m.frequency,
          m.p_value as pValue,
          m.ref_allele,
          m.alt_allele,
          m.mutation_type
        FROM mutations m
        JOIN genes g ON m.gene_id = g.gene_id
        JOIN cancer_types ct ON m.cancer_type_id = ct.cancer_type_id
        WHERE g.gene_symbol = ?
        ORDER BY m.mutation_count DESC
      `;

      return await this.db.query(query, [geneName]);
    } catch (error) {
      console.error('Error fetching mutations by gene:', error);
      throw new Error('Failed to fetch mutations by gene');
    }
  }

  async getAllGenes() {
    try {
      const query = `
        SELECT DISTINCT g.gene_symbol as name, COUNT(m.mutation_id) as mutationCount
        FROM genes g 
        LEFT JOIN mutations m ON g.gene_id = m.gene_id
        GROUP BY g.gene_symbol
        ORDER BY mutationCount DESC, g.gene_symbol ASC
      `;

      return await this.db.query(query);
    } catch (error) {
      console.error('Error fetching all genes:', error);
      throw new Error('Failed to fetch genes');
    }
  }

  async getAllCancerTypes() {
    try {
      const query = `
        SELECT DISTINCT ct.cancer_name as name, COUNT(m.mutation_id) as mutationCount
        FROM cancer_types ct 
        LEFT JOIN mutations m ON ct.cancer_type_id = m.cancer_type_id
        GROUP BY ct.cancer_name
        ORDER BY mutationCount DESC, ct.cancer_name ASC
      `;

      return await this.db.query(query);
    } catch (error) {
      console.error('Error fetching all cancer types:', error);
      throw new Error('Failed to fetch cancer types');
    }
  }

  async getMutationStatistics() {
    try {
      const queries = {
        totalMutations: 'SELECT COUNT(*) as count FROM mutations',
        uniqueGenes: 'SELECT COUNT(DISTINCT gene_id) as count FROM mutations',
        uniqueCancerTypes: 'SELECT COUNT(DISTINCT cancer_type_id) as count FROM mutations',
        avgMutationCount: 'SELECT AVG(mutation_count) as avg FROM mutations'
      };

      const [totalMutations, uniqueGenes, uniqueCancerTypes, avgMutationCount] = await Promise.all([
        this.db.get(queries.totalMutations),
        this.db.get(queries.uniqueGenes),
        this.db.get(queries.uniqueCancerTypes),
        this.db.get(queries.avgMutationCount)
      ]);

      return {
        totalMutations: totalMutations.count,
        uniqueGenes: uniqueGenes.count,
        uniqueCancerTypes: uniqueCancerTypes.count,
        avgMutationCount: Math.round(avgMutationCount.avg || 0)
      };
    } catch (error) {
      console.error('Error fetching mutation statistics:', error);
      throw new Error('Failed to fetch mutation statistics');
    }
  }
}