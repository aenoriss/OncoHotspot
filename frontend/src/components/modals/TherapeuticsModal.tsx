import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LocalPharmacyIcon from '@mui/icons-material/LocalPharmacy';

interface TherapeuticsModalProps {
  open: boolean;
  onClose: () => void;
  gene: string;
}

interface TherapeuticData {
  drug_name: string;
  mechanism_of_action: string;
  clinical_status: string;
  indication: string;
  fda_approval_date: string;
  manufacturer: string;
  target_mutations: string;
  efficacy_data: string;
  side_effects: string;
}

const TherapeuticsModal: React.FC<TherapeuticsModalProps> = ({ open, onClose, gene }) => {
  const [therapeutics, setTherapeutics] = useState<TherapeuticData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && gene) {
      fetchTherapeutics(gene);
    }
  }, [open, gene]);

  const fetchTherapeutics = async (geneSymbol: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:3001/api/therapeutics/gene/${geneSymbol}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch therapeutic data: ${response.status}`);
      }
      const result = await response.json();
      setTherapeutics(result.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setTherapeutics([]);
    } finally {
      setLoading(false);
    }
  };


  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Approved': return 'success';
      case 'Phase III': return 'info';
      case 'Phase II': return 'warning';
      case 'Phase I': return 'secondary';
      case 'Preclinical': return 'default';
      default: return 'default';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
        <LocalPharmacyIcon />
        <Typography variant="h6" component="div">
          Therapeutic Options for {gene}
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ p: 3 }}>
        {loading && (
          <Box display="flex" justifyContent="center" alignItems="center" py={4}>
            <CircularProgress />
            <Typography variant="body2" sx={{ ml: 2 }}>
              Loading therapeutic data...
            </Typography>
          </Box>
        )}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {!loading && !error && therapeutics.length === 0 && (
          <Alert severity="info">
            No therapeutic options found for {gene}
          </Alert>
        )}
        
        {!loading && therapeutics.length > 0 && (
          <Box>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              Found {therapeutics.length} therapeutic option{therapeutics.length !== 1 ? 's' : ''} for {gene}
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              {therapeutics.map((therapeutic, index) => (
                <Accordion key={index} sx={{ mb: 1, '&:before': { display: 'none' } }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: 'grey.50' }}>
                    <Box display="flex" alignItems="center" gap={2} width="100%">
                      <Typography variant="subtitle1" fontWeight="bold">
                        {therapeutic.drug_name}
                      </Typography>
                      <Chip 
                        label={therapeutic.clinical_status} 
                        color={getStatusColor(therapeutic.clinical_status) as any}
                        size="small"
                      />
                      {therapeutic.manufacturer && (
                        <Typography variant="caption" color="text.secondary">
                          {therapeutic.manufacturer}
                        </Typography>
                      )}
                    </Box>
                  </AccordionSummary>
                  
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      {therapeutic.mechanism_of_action && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            Mechanism of Action
                          </Typography>
                          <Typography variant="body2">
                            {therapeutic.mechanism_of_action}
                          </Typography>
                        </Box>
                      )}
                      
                      {therapeutic.indication && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            Indication
                          </Typography>
                          <Typography variant="body2">
                            {therapeutic.indication}
                          </Typography>
                        </Box>
                      )}
                      
                      {therapeutic.target_mutations && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            Target Mutations
                          </Typography>
                          <Typography variant="body2">
                            {therapeutic.target_mutations}
                          </Typography>
                        </Box>
                      )}
                      
                      {therapeutic.fda_approval_date && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            FDA Approval Date
                          </Typography>
                          <Typography variant="body2">
                            {new Date(therapeutic.fda_approval_date).toLocaleDateString()}
                          </Typography>
                        </Box>
                      )}
                      
                      {therapeutic.efficacy_data && (
                        <Box>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            Efficacy Data
                          </Typography>
                          <Typography variant="body2">
                            {therapeutic.efficacy_data}
                          </Typography>
                        </Box>
                      )}
                      
                      {therapeutic.side_effects && (
                        <Box>
                          <Typography variant="subtitle2" color="warning.main" gutterBottom>
                            Side Effects
                          </Typography>
                          <Typography variant="body2">
                            {therapeutic.side_effects}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions sx={{ p: 2, bgcolor: 'grey.50' }}>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TherapeuticsModal;