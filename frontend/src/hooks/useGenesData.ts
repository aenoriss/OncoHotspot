import { useQuery } from 'react-query';
import axios from 'axios';

interface GeneData {
  name: string;
  mutationCount: number;
}

// Ensure API URL has protocol
let API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';
if (API_BASE_URL && !API_BASE_URL.startsWith('http')) {
  API_BASE_URL = `https://${API_BASE_URL}`;
}

const fetchGenesData = async (): Promise<GeneData[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/mutations/genes`);
    console.log('Genes API Response:', response.data);
    if (response.data && response.data.data) {
      return response.data.data;
    }
    return [];
  } catch (error) {
    console.error('Error fetching genes data:', error);
    throw error;
  }
};

export const useGenesData = () => {
  return useQuery<GeneData[], Error>(
    'genesData',
    fetchGenesData,
    {
      staleTime: 10 * 60 * 1000, // 10 minutes
      cacheTime: 15 * 60 * 1000, // 15 minutes
      retry: 2
    }
  );
};