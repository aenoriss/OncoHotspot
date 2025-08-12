import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Box,
  Switch,
  Chip,
  Button,
  Divider,
  CircularProgress,
  Alert
} from '@mui/material';
import { useMutationData } from '../../hooks/useMutationData';

interface CancerTypeControlProps {
  onCancerTypesChange: (hiddenCancerTypes: string[]) => void;
  onCancerTypeSelect?: (cancerType: string | undefined) => void;
}

const CancerTypeControl: React.FC<CancerTypeControlProps> = ({
  onCancerTypesChange,
  onCancerTypeSelect
}) => {
  const [hiddenCancerTypes, setHiddenCancerTypes] = useState<string[]>([]);
  const [selectedCancerType, setSelectedCancerType] = useState<string | undefined>();
  
  const { data: mutationData, isLoading, error } = useMutationData();

  // Extract unique cancer types from mutation data
  const cancerTypes = React.useMemo(() => {
    if (!mutationData) return [];
    const uniqueCancerTypes = Array.from(new Set(mutationData.map(d => d.cancerType)));
    return uniqueCancerTypes.sort();
  }, [mutationData]);

  // Notify parent when hidden cancer types change
  useEffect(() => {
    onCancerTypesChange(hiddenCancerTypes);
  }, [hiddenCancerTypes, onCancerTypesChange]);

  const handleCancerTypeToggle = (cancerType: string) => {
    let newHiddenCancerTypes: string[];
    if (hiddenCancerTypes.includes(cancerType)) {
      // Show cancer type
      newHiddenCancerTypes = hiddenCancerTypes.filter(ct => ct !== cancerType);
    } else {
      // Hide cancer type
      newHiddenCancerTypes = [...hiddenCancerTypes, cancerType];
    }
    setHiddenCancerTypes(newHiddenCancerTypes);
  };

  const handleCancerTypeClick = (cancerType: string) => {
    const newSelection = selectedCancerType === cancerType ? undefined : cancerType;
    setSelectedCancerType(newSelection);
    if (onCancerTypeSelect) {
      onCancerTypeSelect(newSelection);
    }
  };

  const handleShowAll = () => {
    setHiddenCancerTypes([]);
  };

  const handleHideAll = () => {
    setHiddenCancerTypes([...cancerTypes]);
  };

  const visibleCount = cancerTypes.length - hiddenCancerTypes.length;

  if (isLoading) {
    return (
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={20} />
          <Typography variant="body2">Loading cancer types...</Typography>
        </Box>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 2 }}>
        <Alert severity="error" sx={{ fontSize: '0.875rem' }}>
          Error loading cancer types
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="h3">
          Cancer Types
        </Typography>
        <Chip 
          label={`${visibleCount}/${cancerTypes.length}`} 
          size="small" 
          color="primary"
        />
      </Box>
      
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Button 
          variant="outlined" 
          size="small" 
          onClick={handleShowAll}
          disabled={hiddenCancerTypes.length === 0}
        >
          Show All
        </Button>
        <Button 
          variant="outlined" 
          size="small" 
          onClick={handleHideAll}
          disabled={hiddenCancerTypes.length === cancerTypes.length}
        >
          Hide All
        </Button>
      </Box>

      <Divider sx={{ mb: 2 }} />
      
      <Box sx={{ maxHeight: '300px', overflowY: 'auto' }}>
        {cancerTypes.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No cancer types available
          </Typography>
        ) : (
          cancerTypes.map((cancerType) => {
            const isHidden = hiddenCancerTypes.includes(cancerType);
            const isSelected = selectedCancerType === cancerType;
            
            return (
              <Box key={cancerType} sx={{ mb: 1 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    py: 0.5,
                    px: 1,
                    borderRadius: 1,
                    cursor: 'pointer',
                    bgcolor: isSelected ? 'primary.50' : 'transparent',
                    border: isSelected ? '1px solid' : '1px solid transparent',
                    borderColor: isSelected ? 'primary.main' : 'transparent',
                    '&:hover': {
                      bgcolor: isSelected ? 'primary.100' : 'grey.50',
                    }
                  }}
                  onClick={() => handleCancerTypeClick(cancerType)}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                    <Typography
                      variant="body2"
                      sx={{
                        opacity: isHidden ? 0.5 : 1,
                        fontWeight: isSelected ? 'medium' : 'normal',
                        textDecoration: isHidden ? 'line-through' : 'none'
                      }}
                    >
                      {cancerType}
                    </Typography>
                  </Box>
                  
                  <Switch
                    size="small"
                    checked={!isHidden}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleCancerTypeToggle(cancerType);
                    }}
                    color="primary"
                  />
                </Box>
              </Box>
            );
          })
        )}
      </Box>
      
      {hiddenCancerTypes.length > 0 && (
        <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            {hiddenCancerTypes.length} cancer type{hiddenCancerTypes.length !== 1 ? 's' : ''} hidden
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default CancerTypeControl;