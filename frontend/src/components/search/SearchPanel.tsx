import React, { useState } from 'react';
import { Paper, TextField, Autocomplete, Typography, Box, Chip } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import BiotechIcon from '@mui/icons-material/Biotech';

const ONCOGENES = [
  'TP53', 'KRAS', 'EGFR', 'PIK3CA', 'APC', 'BRCA1', 'BRCA2', 
  'PTEN', 'RB1', 'MYC', 'BRAF', 'NRAS', 'IDH1', 'IDH2', 'CDKN2A',
  'ALK', 'HER2', 'MET', 'RET', 'FLT3', 'JAK2', 'KIT', 'VHL',
  'CTNNB1', 'SMAD4', 'MLH1', 'MSH2', 'ATM', 'STK11', 'NF1',
  'FBXW7', 'KEAP1', 'ARID1A', 'TSC1', 'TSC2', 'FGFR3', 'CDK4'
];

interface SearchPanelProps {
  onGeneSelect?: (gene: string | undefined) => void;
}

const SearchPanel: React.FC<SearchPanelProps> = ({ onGeneSelect }) => {
  const [selectedGenes, setSelectedGenes] = useState<string[]>([]);

  const handleGeneChange = (newValue: string[]) => {
    setSelectedGenes(newValue);
    // Call the callback with the first selected gene
    if (onGeneSelect) {
      onGeneSelect(newValue.length > 0 ? newValue[0] : undefined);
    }
  };

  const getGeneTypeColor = (gene: string): "default" | "primary" | "secondary" => {
    // Color code by gene type
    if (['TP53', 'APC', 'PTEN', 'RB1', 'BRCA1', 'BRCA2', 'VHL', 'STK11', 'NF1', 'MLH1', 'MSH2', 'ATM'].includes(gene)) {
      return 'secondary'; // Tumor suppressors - red/pink
    } else if (['KRAS', 'EGFR', 'BRAF', 'PIK3CA', 'MYC', 'ALK', 'HER2', 'MET', 'RET', 'FLT3', 'JAK2', 'KIT'].includes(gene)) {
      return 'primary'; // Oncogenes - blue
    }
    return 'default';
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <SearchIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Gene Search</Typography>
      </Box>
      
      <Autocomplete
        multiple
        options={ONCOGENES}
        value={selectedGenes}
        onChange={(_, newValue) => handleGeneChange(newValue)}
        renderTags={(value, getTagProps) =>
          value.map((option, index) => {
            const { key, ...chipProps } = getTagProps({ index });
            return (
              <Chip
                key={key}
                variant="outlined"
                label={option}
                size="small"
                color={getGeneTypeColor(option)}
                icon={<BiotechIcon />}
                {...chipProps}
              />
            );
          })
        }
        renderInput={(params) => (
          <TextField
            {...params}
            label="Search Oncogenes & Tumor Suppressors"
            placeholder="Type gene names..."
            variant="outlined"
            size="small"
            helperText={selectedGenes.length > 0 ? `${selectedGenes.length} gene(s) selected` : 'Start typing to search genes'}
          />
        )}
      />
      
      {selectedGenes.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            <strong>Selected:</strong> {selectedGenes.join(', ')}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default SearchPanel;