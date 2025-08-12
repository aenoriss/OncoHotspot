import React, { useState, useEffect } from 'react';
import { 
  Paper, 
  Typography, 
  FormGroup, 
  FormControlLabel, 
  Checkbox, 
  Box, 
  Button,
  Chip,
  IconButton,
  Collapse
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { useMutationData } from '../../hooks/useMutationData';

interface GeneFilterPanelProps {
  onGenesChange?: (hiddenGenes: string[]) => void;
}

const GeneFilterPanel: React.FC<GeneFilterPanelProps> = ({ onGenesChange }) => {
  const { data: mutationData } = useMutationData();
  const [availableGenes, setAvailableGenes] = useState<string[]>([]);
  const [hiddenGenes, setHiddenGenes] = useState<string[]>([]);
  const [expanded, setExpanded] = useState(true);

  useEffect(() => {
    if (mutationData && mutationData.length > 0) {
      // Extract unique genes from mutation data
      const genes = Array.from(new Set(mutationData.map(d => d.gene))).sort();
      setAvailableGenes(genes);
    }
  }, [mutationData]);

  const handleGeneToggle = (gene: string) => {
    let newHiddenGenes: string[];
    if (hiddenGenes.includes(gene)) {
      // Show the gene (remove from hidden list)
      newHiddenGenes = hiddenGenes.filter(g => g !== gene);
    } else {
      // Hide the gene (add to hidden list)
      newHiddenGenes = [...hiddenGenes, gene];
    }
    setHiddenGenes(newHiddenGenes);
    
    if (onGenesChange) {
      onGenesChange(newHiddenGenes);
    }
  };

  const showAllGenes = () => {
    setHiddenGenes([]);
    if (onGenesChange) {
      onGenesChange([]);
    }
  };

  const hideAllGenes = () => {
    setHiddenGenes(availableGenes);
    if (onGenesChange) {
      onGenesChange(availableGenes);
    }
  };

  const toggleAllGenes = () => {
    if (hiddenGenes.length === availableGenes.length) {
      showAllGenes();
    } else {
      hideAllGenes();
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FilterListIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Gene Filter</Typography>
          {hiddenGenes.length > 0 && (
            <Chip 
              label={`${hiddenGenes.length} hidden`} 
              size="small" 
              color="warning" 
              sx={{ ml: 1 }}
            />
          )}
        </Box>
        <IconButton 
          size="small"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>
      
      <Collapse in={expanded}>
        <Box sx={{ mb: 1, display: 'flex', gap: 1 }}>
          <Button 
            size="small" 
            variant="outlined"
            startIcon={<VisibilityIcon />}
            onClick={showAllGenes}
            disabled={hiddenGenes.length === 0}
          >
            Show All
          </Button>
          <Button 
            size="small" 
            variant="outlined"
            startIcon={<VisibilityOffIcon />}
            onClick={hideAllGenes}
            disabled={hiddenGenes.length === availableGenes.length}
          >
            Hide All
          </Button>
        </Box>

        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
          Visible Genes ({availableGenes.length - hiddenGenes.length}/{availableGenes.length})
        </Typography>
        
        <FormGroup sx={{ maxHeight: 250, overflow: 'auto' }}>
          {availableGenes.map((gene) => {
            const isVisible = !hiddenGenes.includes(gene);
            return (
              <FormControlLabel
                key={gene}
                control={
                  <Checkbox
                    checked={isVisible}
                    onChange={() => handleGeneToggle(gene)}
                    size="small"
                    color="primary"
                    icon={<VisibilityOffIcon />}
                    checkedIcon={<VisibilityIcon />}
                  />
                }
                label={
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      textDecoration: isVisible ? 'none' : 'line-through',
                      color: isVisible ? 'text.primary' : 'text.disabled'
                    }}
                  >
                    {gene}
                  </Typography>
                }
                sx={{ 
                  '& .MuiFormControlLabel-label': { fontSize: '0.875rem' },
                  height: 30,
                  opacity: isVisible ? 1 : 0.6
                }}
              />
            );
          })}
        </FormGroup>
      </Collapse>
    </Paper>
  );
};

export default GeneFilterPanel;