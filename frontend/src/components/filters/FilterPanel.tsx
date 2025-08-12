import React, { useState } from 'react';
import { 
  Paper, 
  Typography, 
  FormGroup, 
  FormControlLabel, 
  Checkbox, 
  Box, 
  Slider,
  Button,
  Divider,
  Chip
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';

const CANCER_TYPES = [
  'Lung Cancer',
  'Breast Cancer',
  'Colorectal Cancer',
  'Melanoma',
  'Pancreatic Cancer',
  'Liver Cancer',
  'Ovarian Cancer',
  'Glioblastoma'
];

const CLINICAL_STATUS = [
  'FDA Approved',
  'Clinical Trial',
  'Preclinical'
];

interface FilterPanelProps {
  onFiltersChange?: (filters: {
    cancerTypes: string[];
    mutationCount: number[];
    clinicalStatus: string[];
  }) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ onFiltersChange }) => {
  const [selectedCancerTypes, setSelectedCancerTypes] = useState<string[]>([]);
  const [mutationCountRange, setMutationCountRange] = useState<number[]>([0, 500]);
  const [selectedClinicalStatus, setSelectedClinicalStatus] = useState<string[]>([]);
  const [activeFilters, setActiveFilters] = useState(0);

  const handleCancerTypeChange = (cancerType: string, checked: boolean) => {
    let newSelection: string[];
    if (checked) {
      newSelection = [...selectedCancerTypes, cancerType];
    } else {
      newSelection = selectedCancerTypes.filter(type => type !== cancerType);
    }
    setSelectedCancerTypes(newSelection);
    updateFilters(newSelection, mutationCountRange, selectedClinicalStatus);
  };

  const handleClinicalStatusChange = (status: string, checked: boolean) => {
    let newSelection: string[];
    if (checked) {
      newSelection = [...selectedClinicalStatus, status];
    } else {
      newSelection = selectedClinicalStatus.filter(s => s !== status);
    }
    setSelectedClinicalStatus(newSelection);
    updateFilters(selectedCancerTypes, mutationCountRange, newSelection);
  };

  const handleMutationCountChange = (event: Event, newValue: number | number[]) => {
    const range = newValue as number[];
    setMutationCountRange(range);
  };

  const handleMutationCountCommit = (event: Event | React.SyntheticEvent, newValue: number | number[]) => {
    const range = newValue as number[];
    updateFilters(selectedCancerTypes, range, selectedClinicalStatus);
  };

  const updateFilters = (cancerTypes: string[], mutationCount: number[], clinicalStatus: string[]) => {
    const filterCount = cancerTypes.length + (mutationCount[0] > 0 || mutationCount[1] < 500 ? 1 : 0) + clinicalStatus.length;
    setActiveFilters(filterCount);
    
    if (onFiltersChange) {
      onFiltersChange({
        cancerTypes,
        mutationCount,
        clinicalStatus
      });
    }
  };

  const clearAllFilters = () => {
    setSelectedCancerTypes([]);
    setMutationCountRange([0, 500]);
    setSelectedClinicalStatus([]);
    setActiveFilters(0);
    
    if (onFiltersChange) {
      onFiltersChange({
        cancerTypes: [],
        mutationCount: [0, 500],
        clinicalStatus: []
      });
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FilterListIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6">Filters</Typography>
          {activeFilters > 0 && (
            <Chip 
              label={activeFilters} 
              size="small" 
              color="primary" 
              sx={{ ml: 1 }}
            />
          )}
        </Box>
        {activeFilters > 0 && (
          <Button 
            size="small" 
            startIcon={<ClearIcon />}
            onClick={clearAllFilters}
          >
            Clear
          </Button>
        )}
      </Box>
      
      {/* Cancer Types Filter */}
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
        Cancer Types
      </Typography>
      <FormGroup sx={{ mb: 2, maxHeight: 200, overflow: 'auto' }}>
        {CANCER_TYPES.map((cancerType) => (
          <FormControlLabel
            key={cancerType}
            control={
              <Checkbox
                checked={selectedCancerTypes.includes(cancerType)}
                onChange={(e) => handleCancerTypeChange(cancerType, e.target.checked)}
                size="small"
                color="primary"
              />
            }
            label={cancerType}
            sx={{ 
              '& .MuiFormControlLabel-label': { fontSize: '0.875rem' },
              height: 30
            }}
          />
        ))}
      </FormGroup>
      
      <Divider sx={{ my: 2 }} />
      
      {/* Mutation Count Range */}
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
        Mutation Count Range
      </Typography>
      <Box sx={{ px: 2, mb: 2 }}>
        <Slider
          value={mutationCountRange}
          onChange={handleMutationCountChange}
          onChangeCommitted={handleMutationCountCommit}
          valueLabelDisplay="auto"
          min={0}
          max={500}
          size="small"
          marks={[
            { value: 0, label: '0' },
            { value: 100, label: '100' },
            { value: 250, label: '250' },
            { value: 500, label: '500+' }
          ]}
        />
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center' }}>
          {mutationCountRange[0]} - {mutationCountRange[1]} mutations
        </Typography>
      </Box>
      
      <Divider sx={{ my: 2 }} />
      
      {/* Treatment Status Filter */}
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
        Treatment Status
      </Typography>
      <FormGroup>
        {CLINICAL_STATUS.map((status) => (
          <FormControlLabel
            key={status}
            control={
              <Checkbox
                checked={selectedClinicalStatus.includes(status)}
                onChange={(e) => handleClinicalStatusChange(status, e.target.checked)}
                size="small"
                color="primary"
              />
            }
            label={status}
            sx={{ 
              '& .MuiFormControlLabel-label': { fontSize: '0.875rem' },
              height: 30
            }}
          />
        ))}
      </FormGroup>
    </Paper>
  );
};

export default FilterPanel;