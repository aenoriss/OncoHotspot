import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import BiotechIcon from '@mui/icons-material/Biotech';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import axios from 'axios';

interface Gene {
  gene_id: number;
  gene_symbol: string;
  gene_name: string;
  chromosome: string;
  gene_type: string;
  description: string;
}

interface GeneInfoPanelProps {
  selectedGene?: string;
  selectedMutation?: {
    gene: string;
    position: number;
    cancerType: string;
  };
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const GeneInfoPanel: React.FC<GeneInfoPanelProps> = ({ selectedGene, selectedMutation }) => {
  const [geneData, setGeneData] = useState<Gene | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedGene) {
      fetchGeneData();
    } else {
      setGeneData(null);
      setError(null);
    }
  }, [selectedGene]);

  const fetchGeneData = async () => {
    if (!selectedGene) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_BASE_URL}/api/genes/${selectedGene}`);
      setGeneData(response.data);
    } catch (error) {
      console.error('Error fetching gene data:', error);
      setError('Failed to load gene information');
    } finally {
      setLoading(false);
    }
  };

  const getGeneTypeColor = (geneType: string) => {
    switch (geneType?.toLowerCase()) {
      case 'oncogene':
        return 'error';
      case 'tumor_suppressor':
        return 'primary';
      case 'context':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getGeneTypeIcon = (geneType: string) => {
    switch (geneType?.toLowerCase()) {
      case 'oncogene':
        return <WarningIcon sx={{ fontSize: 16 }} />;
      case 'tumor_suppressor':
        return <SecurityIcon sx={{ fontSize: 16 }} />;
      default:
        return <BiotechIcon sx={{ fontSize: 16 }} />;
    }
  };

  const formatGeneDescription = (description: string) => {
    if (!description) return null;

    // Split by cancer types if they exist in the description
    const sections = description.split(/\n\n(?=[A-Z][A-Z\s]+:)/);
    
    return sections.map((section, index) => {
      // Check if this section is a cancer-specific description
      const cancerMatch = section.match(/^([A-Z][A-Z\s]+):\s*(.*)/s);
      
      if (cancerMatch && index > 0) {
        const [, cancerType, content] = cancerMatch;
        const isSelectedCancer = selectedMutation?.cancerType.toLowerCase().includes(cancerType.toLowerCase()) ||
                                cancerType.toLowerCase().includes(selectedMutation?.cancerType.toLowerCase() || '');
        
        return (
          <Box key={index} sx={{ mb: 2 }}>
            <Accordion 
              defaultExpanded={isSelectedCancer}
              sx={{ 
                boxShadow: isSelectedCancer ? 2 : 1,
                border: isSelectedCancer ? '2px solid' : '1px solid',
                borderColor: isSelectedCancer ? 'primary.main' : 'divider'
              }}
            >
              <AccordionSummary 
                expandIcon={<ExpandMoreIcon />}
                sx={{ 
                  backgroundColor: isSelectedCancer ? 'primary.50' : 'grey.50',
                  '& .MuiAccordionSummary-content': { alignItems: 'center' }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <InfoOutlinedIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {cancerType}
                  </Typography>
                  {isSelectedCancer && (
                    <Chip 
                      label="Current Selection" 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                  {content.trim()}
                </Typography>
              </AccordionDetails>
            </Accordion>
          </Box>
        );
      } else {
        // General description
        return (
          <Box key={index} sx={{ mb: 2, p: 2, backgroundColor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
            <Typography variant="body2" sx={{ lineHeight: 1.6, mb: 1 }}>
              {section.trim()}
            </Typography>
          </Box>
        );
      }
    });
  };

  if (!selectedGene) {
    return (
      <Paper sx={{ p: 2, mb: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Select a gene to view detailed information
        </Typography>
      </Paper>
    );
  }

  if (loading) {
    return (
      <Paper sx={{ p: 2, mb: 2, textAlign: 'center' }}>
        <CircularProgress size={24} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Loading gene information...
        </Typography>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 2, mb: 2 }}>
        <Alert severity="warning">{error}</Alert>
      </Paper>
    );
  }

  if (!geneData) {
    return (
      <Paper sx={{ p: 2, mb: 2 }}>
        <Alert severity="info">No information available for {selectedGene}</Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <BiotechIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Gene Information</Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 1 }}>
          {geneData.gene_symbol}
        </Typography>
        
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 1 }}>
          {geneData.gene_name}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Chip
            icon={getGeneTypeIcon(geneData.gene_type)}
            label={geneData.gene_type?.replace('_', ' ').toUpperCase() || 'Unknown'}
            size="small"
            color={getGeneTypeColor(geneData.gene_type) as any}
          />
          <Typography variant="caption" color="text.secondary">
            Chromosome {geneData.chromosome}
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ mb: 2 }} />

      <Box>
        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2, display: 'flex', alignItems: 'center' }}>
          <InfoOutlinedIcon sx={{ mr: 0.5, fontSize: 16 }} />
          Detailed Description
        </Typography>
        
        {formatGeneDescription(geneData.description)}
      </Box>
    </Paper>
  );
};

export default GeneInfoPanel;