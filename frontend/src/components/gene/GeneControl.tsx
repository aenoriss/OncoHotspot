import React, { useState, useEffect, useMemo } from 'react';
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
  TextField,
  InputAdornment,
  Collapse,
  Tooltip,
  Badge
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import DnaIcon from '@mui/icons-material/Biotech';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import { useMutationData } from '../../hooks/useMutationData';
import { useGenesData } from '../../hooks/useGenesData';

interface GeneControlProps {
  onGenesChange?: (hiddenGenes: string[]) => void;
  onGeneSelect?: (gene: string | undefined) => void;
}

const GeneControl: React.FC<GeneControlProps> = ({ onGenesChange, onGeneSelect }) => {
  const { data: mutationData } = useMutationData();
  const { data: genesData, isLoading: genesLoading, error: genesError } = useGenesData();
  const [availableGenes, setAvailableGenes] = useState<string[]>([]);
  const [hiddenGenes, setHiddenGenes] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGene, setSelectedGene] = useState<string | undefined>();
  const [expanded, setExpanded] = useState(true);

  useEffect(() => {
    // Prioritize genes data from dedicated endpoint
    if (genesData && genesData.length > 0) {
      const genes = genesData.map(g => g.name).sort();
      setAvailableGenes(genes);
    } else if (mutationData && mutationData.length > 0) {
      // Fallback to extracting genes from mutation data
      const genes = Array.from(new Set(mutationData.map(d => d.gene))).sort();
      setAvailableGenes(genes);
    }
  }, [genesData, mutationData]);

  // Filter genes based on search term
  const filteredGenes = useMemo(() => {
    if (!searchTerm) return availableGenes;
    const term = searchTerm.toLowerCase();
    return availableGenes.filter(gene => 
      gene.toLowerCase().includes(term)
    );
  }, [availableGenes, searchTerm]);

  const visibleGenes = filteredGenes.filter(g => !hiddenGenes.includes(g));
  const hiddenFilteredGenes = filteredGenes.filter(g => hiddenGenes.includes(g));

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

  const handleGeneClick = (gene: string) => {
    if (selectedGene === gene) {
      setSelectedGene(undefined);
      if (onGeneSelect) onGeneSelect(undefined);
    } else {
      setSelectedGene(gene);
      if (onGeneSelect) onGeneSelect(gene);
    }
  };

  const showAllGenes = () => {
    setHiddenGenes([]);
    if (onGenesChange) {
      onGenesChange([]);
    }
  };

  const hideAllFiltered = () => {
    const newHidden = Array.from(new Set([...hiddenGenes, ...filteredGenes]));
    setHiddenGenes(newHidden);
    if (onGenesChange) {
      onGenesChange(newHidden);
    }
  };

  const showAllFiltered = () => {
    const newHidden = hiddenGenes.filter(g => !filteredGenes.includes(g));
    setHiddenGenes(newHidden);
    if (onGenesChange) {
      onGenesChange(newHidden);
    }
  };

  const clearSearch = () => {
    setSearchTerm('');
  };

  if (genesLoading) {
    return (
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography>Loading genes...</Typography>
      </Paper>
    );
  }

  if (genesError) {
    return (
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography color="error">Error loading genes: {genesError.message}</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <DnaIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Gene Control ({availableGenes.length} genes)</Typography>
          <Box sx={{ display: 'flex', gap: 0.5, ml: 1 }}>
            {hiddenGenes.length > 0 && (
              <Chip 
                label={`${hiddenGenes.length} hidden`} 
                size="small" 
                color="warning" 
                icon={<VisibilityOffIcon />}
              />
            )}
            {selectedGene && (
              <Chip 
                label={selectedGene} 
                size="small" 
                color="primary"
                onDelete={() => {
                  setSelectedGene(undefined);
                  if (onGeneSelect) onGeneSelect(undefined);
                }}
              />
            )}
          </Box>
        </Box>
        <IconButton 
          size="small"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>
      
      <Collapse in={expanded}>
        {/* Search Field */}
        <TextField
          fullWidth
          size="small"
          placeholder="Search genes..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{ mb: 2 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={clearSearch}>
                  <ClearIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            )
          }}
        />

        {/* Quick Actions */}
        <Box sx={{ mb: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button 
            size="small" 
            variant="outlined"
            startIcon={<VisibilityIcon />}
            onClick={showAllFiltered}
            disabled={hiddenFilteredGenes.length === 0}
          >
            Show {searchTerm ? 'Filtered' : 'All'}
          </Button>
          <Button 
            size="small" 
            variant="outlined"
            startIcon={<VisibilityOffIcon />}
            onClick={hideAllFiltered}
            disabled={visibleGenes.length === 0}
          >
            Hide {searchTerm ? 'Filtered' : 'All'}
          </Button>
          {hiddenGenes.length > 0 && (
            <Button 
              size="small" 
              variant="text"
              color="warning"
              startIcon={<ClearIcon />}
              onClick={showAllGenes}
            >
              Clear Hidden
            </Button>
          )}
        </Box>

        {/* Results Summary */}
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          {searchTerm && (
            <>Showing {filteredGenes.length} of {availableGenes.length} genes • </>
          )}
          {visibleGenes.length} visible, {hiddenFilteredGenes.length} hidden
        </Typography>
        
        {/* Gene List */}
        <Box sx={{ maxHeight: 300, overflow: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1 }}>
          {filteredGenes.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
              No genes found matching "{searchTerm}"
            </Typography>
          ) : (
            <>
              {/* Visible Genes Section */}
              {visibleGenes.length > 0 && (
                <>
                  <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'text.secondary' }}>
                    VISIBLE GENES
                  </Typography>
                  <FormGroup sx={{ mb: hiddenFilteredGenes.length > 0 ? 2 : 0 }}>
                    {visibleGenes.map((gene) => (
                      <Box
                        key={gene}
                        sx={{ 
                          display: 'flex', 
                          alignItems: 'center',
                          '&:hover': { bgcolor: 'action.hover' },
                          borderRadius: 0.5,
                          px: 1
                        }}
                      >
                        <IconButton
                          size="small"
                          onClick={() => handleGeneToggle(gene)}
                          sx={{ p: 0.5 }}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                        <Button
                          variant="text"
                          size="small"
                          onClick={() => handleGeneClick(gene)}
                          sx={{ 
                            justifyContent: 'flex-start',
                            flex: 1,
                            textTransform: 'none',
                            color: selectedGene === gene ? 'primary.main' : 'text.primary',
                            fontWeight: selectedGene === gene ? 'bold' : 'normal',
                            bgcolor: selectedGene === gene ? 'action.selected' : 'transparent'
                          }}
                        >
                          {gene}
                        </Button>
                      </Box>
                    ))}
                  </FormGroup>
                </>
              )}

              {/* Hidden Genes Section */}
              {hiddenFilteredGenes.length > 0 && (
                <>
                  <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'text.secondary' }}>
                    HIDDEN GENES
                  </Typography>
                  <FormGroup>
                    {hiddenFilteredGenes.map((gene) => (
                      <Box
                        key={gene}
                        sx={{ 
                          display: 'flex', 
                          alignItems: 'center',
                          opacity: 0.5,
                          '&:hover': { bgcolor: 'action.hover', opacity: 0.8 },
                          borderRadius: 0.5,
                          px: 1
                        }}
                      >
                        <IconButton
                          size="small"
                          onClick={() => handleGeneToggle(gene)}
                          sx={{ p: 0.5 }}
                        >
                          <VisibilityOffIcon fontSize="small" />
                        </IconButton>
                        <Button
                          variant="text"
                          size="small"
                          onClick={() => handleGeneClick(gene)}
                          disabled
                          sx={{ 
                            justifyContent: 'flex-start',
                            flex: 1,
                            textTransform: 'none',
                            textDecoration: 'line-through'
                          }}
                        >
                          {gene}
                        </Button>
                      </Box>
                    ))}
                  </FormGroup>
                </>
              )}
            </>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default GeneControl;