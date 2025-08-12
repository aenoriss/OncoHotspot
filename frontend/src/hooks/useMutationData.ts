import { useQuery } from 'react-query';
import axios from 'axios';

export interface MutationData {
  gene: string;
  position: number;
  cancerType: string;
  mutationCount: number;
  significance: number;
  frequency?: number;
}

const MOCK_MUTATION_DATA: MutationData[] = [
  { gene: 'TP53', cancerType: 'Breast Cancer', position: 273, mutationCount: 45, significance: 0.95 },
  { gene: 'TP53', cancerType: 'Lung Cancer', position: 273, mutationCount: 78, significance: 0.98 },
  { gene: 'KRAS', cancerType: 'Colorectal Cancer', position: 12, mutationCount: 92, significance: 0.97 },
  { gene: 'KRAS', cancerType: 'Pancreatic Cancer', position: 12, mutationCount: 134, significance: 0.99 },
  { gene: 'EGFR', cancerType: 'Lung Cancer', position: 858, mutationCount: 67, significance: 0.94 },
  { gene: 'BRAF', cancerType: 'Melanoma', position: 600, mutationCount: 156, significance: 0.96 },
  { gene: 'PIK3CA', cancerType: 'Breast Cancer', position: 545, mutationCount: 43, significance: 0.89 },
  { gene: 'APC', cancerType: 'Colorectal Cancer', position: 1450, mutationCount: 87, significance: 0.92 }
];

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const fetchMutationData = async (): Promise<MutationData[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/mutations/all`);
    console.log('API Response:', response.data);
    if (response.data && response.data.data) {
      console.log(`Fetched ${response.data.data.length} mutations (ALL database records)`);
      return response.data.data;
    }
    return [];
  } catch (error) {
    console.error('Error fetching mutation data:', error);
    if (process.env.NODE_ENV === 'development') {
      console.warn('Using mock data due to API error');
      return MOCK_MUTATION_DATA;
    }
    throw error;
  }
};

export const useMutationData = () => {
  return useQuery<MutationData[], Error>(
    'mutationData',
    fetchMutationData,
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      retry: 2
    }
  );
};