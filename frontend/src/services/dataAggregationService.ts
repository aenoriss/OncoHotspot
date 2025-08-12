
export interface MutationData {
  gene: string;
  position: number;
  cancerType: string;
  mutationCount: number;
  significance: number;
  frequency?: number;
}

export interface AggregatedCell {
  gene: string;
  cancerType: string;
  totalMutations: number;
  avgSignificance: number;
  maxSignificance: number;
  positions: number[];
  representativeMutation: MutationData;
}

export interface ViewLevel {
  name: string;
  maxGenes: number;
  maxCancerTypes: number;
  minSignificance: number;
  description: string;
}

export class DataAggregationService {
  
  static readonly VIEW_LEVELS: ViewLevel[] = [
    {
      name: 'overview',
      maxGenes: 50,
      maxCancerTypes: 15,
      minSignificance: 0.01,  // 1% frequency threshold
      description: 'Top 50 most frequent mutations across major cancer types'
    },
    {
      name: 'detailed',
      maxGenes: 150,
      maxCancerTypes: 25,
      minSignificance: 0.005,  // 0.5% frequency threshold
      description: 'Extended view with moderate frequency mutations'
    },
    {
      name: 'comprehensive',
      maxGenes: 300,
      maxCancerTypes: 29,
      minSignificance: 0.001,  // 0.1% frequency threshold
      description: 'Most genes with clinically relevant mutations'
    },
    {
      name: 'complete',
      maxGenes: Number.MAX_SAFE_INTEGER, // No gene limit
      maxCancerTypes: Number.MAX_SAFE_INTEGER, // No cancer type limit
      minSignificance: 0.0,
      description: 'All available data (performance intensive)'
    }
  ];

  static aggregateToHeatmapCells(mutations: MutationData[]): Map<string, AggregatedCell> {
    const cellMap = new Map<string, AggregatedCell>();

    mutations.forEach(mutation => {
      const key = `${mutation.gene}:${mutation.cancerType}`;
      
      if (cellMap.has(key)) {
        const cell = cellMap.get(key)!;
        cell.totalMutations += mutation.mutationCount;
        cell.positions.push(mutation.position);
        
        const freq = mutation.frequency !== undefined ? mutation.frequency : mutation.significance;
        const cellFreq = cell.representativeMutation.frequency !== undefined ? cell.representativeMutation.frequency : cell.representativeMutation.significance;
        const totalCount = cell.totalMutations + mutation.mutationCount;
        cell.avgSignificance = (cell.avgSignificance * cell.totalMutations + 
                              freq * mutation.mutationCount) / totalCount;
        cell.maxSignificance = Math.max(cell.maxSignificance, freq);
        
        if (freq > cellFreq) {
          cell.representativeMutation = mutation;
        }
      } else {
        cellMap.set(key, {
          gene: mutation.gene,
          cancerType: mutation.cancerType,
          totalMutations: mutation.mutationCount,
          avgSignificance: mutation.frequency !== undefined ? mutation.frequency : mutation.significance,
          maxSignificance: mutation.frequency !== undefined ? mutation.frequency : mutation.significance,
          positions: [mutation.position],
          representativeMutation: mutation
        });
      }
    });

    return cellMap;
  }

  static filterForViewLevel(
    mutations: MutationData[], 
    viewLevel: ViewLevel,
    hiddenGenes: string[] = [],
    hiddenCancerTypes: string[] = []
  ): MutationData[] {
    
    let filtered = mutations.filter(m => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      return !hiddenGenes.includes(m.gene) &&
        !hiddenCancerTypes.includes(m.cancerType) &&
        freq >= viewLevel.minSignificance;
    });

    const geneStats = new Map<string, {count: number, maxSig: number, avgSig: number}>();
    filtered.forEach(m => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      if (geneStats.has(m.gene)) {
        const stats = geneStats.get(m.gene)!;
        stats.count += m.mutationCount;
        stats.maxSig = Math.max(stats.maxSig, freq);
        stats.avgSig = (stats.avgSig + freq) / 2;
      } else {
        geneStats.set(m.gene, {
          count: m.mutationCount,
          maxSig: freq,
          avgSig: freq
        });
      }
    });

    const rankedGenes = Array.from(geneStats.entries())
      .sort((a, b) => (b[1].count * b[1].maxSig) - (a[1].count * a[1].maxSig))
      .slice(0, viewLevel.maxGenes)
      .map(([gene]) => gene);

    const cancerStats = new Map<string, {count: number, maxSig: number}>();
    filtered.forEach(m => {
      if (cancerStats.has(m.cancerType)) {
        const stats = cancerStats.get(m.cancerType)!;
        stats.count += m.mutationCount;
        stats.maxSig = Math.max(stats.maxSig, m.frequency !== undefined ? m.frequency : m.significance);
      } else {
        cancerStats.set(m.cancerType, {
          count: m.mutationCount,
          maxSig: m.frequency !== undefined ? m.frequency : m.significance
        });
      }
    });

    const rankedCancerTypes = Array.from(cancerStats.entries())
      .sort((a, b) => (b[1].count * b[1].maxSig) - (a[1].count * a[1].maxSig))
      .slice(0, viewLevel.maxCancerTypes)
      .map(([cancerType]) => cancerType);

    return filtered.filter(m => 
      rankedGenes.includes(m.gene) && 
      rankedCancerTypes.includes(m.cancerType)
    );
  }

  static sampleMutations(mutations: MutationData[], maxSamples: number = 5000): MutationData[] {
    if (mutations.length <= maxSamples) {
      return mutations;
    }

    const highFreq = mutations.filter(m => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      return freq >= 0.01; // 1% or higher
    });
    const medFreq = mutations.filter(m => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      return freq >= 0.001 && freq < 0.01; // 0.1% to 1%
    });
    const lowFreq = mutations.filter(m => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      return freq < 0.001; // Less than 0.1%
    });

    const highSample = Math.min(highFreq.length, Math.floor(maxSamples * 0.6));
    const medSample = Math.min(medFreq.length, Math.floor(maxSamples * 0.3));
    const lowSample = maxSamples - highSample - medSample;

    return [
      ...this.randomSample(highFreq, highSample),
      ...this.randomSample(medFreq, medSample),
      ...this.randomSample(lowFreq, lowSample)
    ];
  }

  private static randomSample<T>(array: T[], size: number): T[] {
    const shuffled = [...array].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, size);
  }

  static calculateOptimalCellSize(
    screenWidth: number,
    screenHeight: number,
    geneCount: number,
    cancerTypeCount: number
  ): {cellWidth: number, cellHeight: number, feasible: boolean} {
    
    const availableWidth = screenWidth * 0.8;
    const availableHeight = screenHeight * 0.8;
    
    const minCellSize = 3;
    const idealCellSize = 15;
    const maxCellSize = 50;
    
    const cellWidth = Math.max(minCellSize, Math.min(idealCellSize, availableWidth / geneCount));
    const cellHeight = Math.max(minCellSize, Math.min(idealCellSize, availableHeight / cancerTypeCount));
    
    const feasible = cellWidth >= minCellSize && cellHeight >= minCellSize && 
                    geneCount * cancerTypeCount < 10000;
    
    return {
      cellWidth: Math.min(cellWidth, maxCellSize),
      cellHeight: Math.min(cellHeight, maxCellSize),
      feasible
    };
  }

  static getRecommendedViewLevel(screenWidth: number, screenHeight: number): ViewLevel {
    const screenArea = screenWidth * screenHeight;
    
    if (screenArea > 2000000) {
      return this.VIEW_LEVELS[2];
    } else if (screenArea > 1000000) {
      return this.VIEW_LEVELS[1];
    } else {
      return this.VIEW_LEVELS[0];
    }
  }
}