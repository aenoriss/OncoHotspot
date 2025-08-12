import React, { useState, useEffect } from 'react';
import { 
  Paper, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  Chip, 
  Box,
  Divider,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Collapse,
  CardActions,
  Button
} from '@mui/material';
import LocalPharmacyIcon from '@mui/icons-material/LocalPharmacy';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ScienceIcon from '@mui/icons-material/Science';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import WarningIcon from '@mui/icons-material/Warning';
import axios from 'axios';

interface Therapeutic {
  therapeutic_id: number;
  drug_name: string;
  mechanism_of_action: string;
  clinical_status: string;
  indication: string;
  fda_approval_date: string;
  manufacturer: string;
  target_mutations: string;
  gene_symbol: string;
  efficacy_data?: string;
  side_effects?: string;
}

interface TherapeuticPanelProps {
  selectedGene?: string;
  selectedMutation?: {
    gene: string;
    position: number;
    cancerType: string;
  };
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const TherapeuticPanel: React.FC<TherapeuticPanelProps> = ({ selectedGene, selectedMutation }) => {
  const [therapeutics, setTherapeutics] = useState<Therapeutic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

  useEffect(() => {
    fetchTherapeutics();
  }, [selectedGene, selectedMutation]);

  const fetchTherapeutics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // If a specific gene is selected, fetch therapeutics for that gene
      const endpoint = selectedGene 
        ? `${API_BASE_URL}/api/therapeutics/gene/${selectedGene}`
        : `${API_BASE_URL}/api/therapeutics`;
        
      const response = await axios.get(endpoint);
      setTherapeutics(response.data.data || response.data || []);
    } catch (err) {
      console.error('Error fetching therapeutics:', err);
      setError('Failed to load therapeutics');
      // Fallback to sample data for demo
      setTherapeutics(SAMPLE_THERAPEUTICS);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'success';
      case 'phase iii':
      case 'phase ii':
        return 'warning';
      case 'phase i':
      case 'preclinical':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    if (status?.toLowerCase() === 'approved') {
      return <CheckCircleIcon sx={{ fontSize: 16 }} />;
    }
    return <ScienceIcon sx={{ fontSize: 16 }} />;
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
  };

  const toggleCardExpansion = (therapeuticId: number) => {
    const newExpanded = new Set(expandedCards);
    if (newExpanded.has(therapeuticId)) {
      newExpanded.delete(therapeuticId);
    } else {
      newExpanded.add(therapeuticId);
    }
    setExpandedCards(newExpanded);
  };

  const formatDetailedText = (text: string) => {
    if (!text) return null;
    return text.split('\n').map((line, index) => (
      <Typography key={index} variant="body2" sx={{ mb: 1 }}>
        {line}
      </Typography>
    ));
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <LocalPharmacyIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Therapeutic Options</Typography>
      </Box>
      
      {selectedMutation && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Showing treatments for <strong>{selectedMutation.gene}</strong> mutations in <strong>{selectedMutation.cancerType}</strong>
        </Alert>
      )}

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {therapeutics.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
            {selectedGene 
              ? `No approved therapeutics found for ${selectedGene}`
              : 'Select a mutation to see therapeutic options'}
          </Typography>
        ) : (
          <List sx={{ pt: 0 }}>
            {therapeutics.map((therapeutic, index) => {
              const isExpanded = expandedCards.has(therapeutic.therapeutic_id || index);
              return (
                <React.Fragment key={therapeutic.therapeutic_id || index}>
                  <Card sx={{ mb: 2, boxShadow: isExpanded ? 3 : 1, transition: 'box-shadow 0.3s' }}>
                    <CardContent sx={{ pb: 1, '&:last-child': { pb: 1 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                            {therapeutic.drug_name}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <Chip 
                              icon={getStatusIcon(therapeutic.clinical_status)}
                              label={therapeutic.clinical_status || 'Unknown'}
                              size="small"
                              color={getStatusColor(therapeutic.clinical_status) as any}
                            />
                            {therapeutic.fda_approval_date && (
                              <Typography variant="caption" color="text.secondary">
                                FDA: {formatDate(therapeutic.fda_approval_date)}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>Mechanism:</strong> {therapeutic.mechanism_of_action}
                      </Typography>
                      
                      {therapeutic.indication && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          <strong>Indication:</strong> {therapeutic.indication}
                        </Typography>
                      )}
                      
                      {therapeutic.target_mutations && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            <strong>Targets:</strong> {therapeutic.target_mutations}
                          </Typography>
                        </Box>
                      )}
                      
                      {therapeutic.manufacturer && (
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                          {therapeutic.manufacturer}
                        </Typography>
                      )}
                    </CardContent>

                    <CardActions sx={{ pt: 0, pb: 1, px: 2 }}>
                      <Button
                        size="small"
                        onClick={() => toggleCardExpansion(therapeutic.therapeutic_id || index)}
                        startIcon={isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        sx={{ textTransform: 'none' }}
                      >
                        {isExpanded ? 'Less Details' : 'More Details'}
                      </Button>
                    </CardActions>

                    <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                      <CardContent sx={{ pt: 0, pb: 2 }}>
                        <Divider sx={{ mb: 2 }} />
                        
                        {therapeutic.efficacy_data && (
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'success.main', mb: 1, display: 'flex', alignItems: 'center' }}>
                              <ScienceIcon sx={{ mr: 0.5, fontSize: 16 }} />
                              Clinical Efficacy & Mechanism
                            </Typography>
                            <Box sx={{ backgroundColor: 'success.50', p: 1.5, borderRadius: 1, border: '1px solid', borderColor: 'success.200' }}>
                              {formatDetailedText(therapeutic.efficacy_data)}
                            </Box>
                          </Box>
                        )}

                        {therapeutic.side_effects && (
                          <Box sx={{ mb: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'warning.main', mb: 1, display: 'flex', alignItems: 'center' }}>
                              <WarningIcon sx={{ mr: 0.5, fontSize: 16 }} />
                              Safety Profile & Side Effects
                            </Typography>
                            <Box sx={{ backgroundColor: 'warning.50', p: 1.5, borderRadius: 1, border: '1px solid', borderColor: 'warning.200' }}>
                              {formatDetailedText(therapeutic.side_effects)}
                            </Box>
                          </Box>
                        )}
                      </CardContent>
                    </Collapse>
                  </Card>
                </React.Fragment>
              );
            })}
          </List>
        )}
      </Box>
      
      <Divider sx={{ mt: 2, mb: 1 }} />
      
      <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center' }}>
        {therapeutics.length} therapeutic option{therapeutics.length !== 1 ? 's' : ''} available
      </Typography>
    </Paper>
  );
};

// Fallback sample data
const SAMPLE_THERAPEUTICS: Therapeutic[] = [
  {
    therapeutic_id: 1,
    gene_symbol: 'EGFR',
    drug_name: 'Osimertinib (Tagrisso)',
    mechanism_of_action: 'Third-generation EGFR TKI',
    clinical_status: 'Approved',
    indication: 'NSCLC with EGFR T790M',
    fda_approval_date: '2015-11-13',
    manufacturer: 'AstraZeneca',
    target_mutations: 'L858R, T790M, exon 19 del'
  },
  {
    therapeutic_id: 2,
    gene_symbol: 'BRAF',
    drug_name: 'Vemurafenib (Zelboraf)',
    mechanism_of_action: 'BRAF V600E inhibitor',
    clinical_status: 'Approved',
    indication: 'Melanoma with BRAF V600E',
    fda_approval_date: '2011-08-17',
    manufacturer: 'Roche/Genentech',
    target_mutations: 'V600E'
  },
  {
    therapeutic_id: 3,
    gene_symbol: 'ALK',
    drug_name: 'Alectinib (Alecensa)',
    mechanism_of_action: 'Second-generation ALK inhibitor',
    clinical_status: 'Approved',
    indication: 'ALK-positive NSCLC',
    fda_approval_date: '2015-12-11',
    manufacturer: 'Roche/Genentech',
    target_mutations: 'ALK fusions'
  }
];

export default TherapeuticPanel;