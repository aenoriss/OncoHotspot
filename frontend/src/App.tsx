import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import Chip from '@mui/material/Chip';
import Badge from '@mui/material/Badge';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Slider from '@mui/material/Slider';
import Tooltip from '@mui/material/Tooltip';
import FilterListIcon from '@mui/icons-material/FilterList';
import SettingsIcon from '@mui/icons-material/Settings';
import DatasetIcon from '@mui/icons-material/Dataset';
import TimelineIcon from '@mui/icons-material/Timeline';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import TuneIcon from '@mui/icons-material/Tune';
import InfoIcon from '@mui/icons-material/Info';
import CloseIcon from '@mui/icons-material/Close';
import Divider from '@mui/material/Divider';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Collapse from '@mui/material/Collapse';
import Drawer from '@mui/material/Drawer';
import IntelligentHeatmap from './components/heatmap/IntelligentHeatmap';
import GeneControl from './components/gene/GeneControl';
import CancerTypeControl from './components/cancer/CancerTypeControl';
import TherapeuticPanel from './components/therapeutics/TherapeuticPanel';
import GeneInfoPanel from './components/gene/GeneInfoPanel';
import OncoHotspotLogo from './components/logo/OncoHotspotLogo';
import TherapeuticsModal from './components/modals/TherapeuticsModal';
import { useDragScroll } from './hooks/useDragScroll';
import { useMutationData } from './hooks/useMutationData';
import { DataAggregationService, ViewLevel, AggregatedCell } from './services/dataAggregationService';

const queryClient = new QueryClient();

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // Professional blue
    },
    secondary: {
      main: '#d32f2f', // Medical red for highlights
    },
    background: {
      default: '#fafafa', // Clean light gray
      paper: '#ffffff', // Pure white for panels
    },
    text: {
      primary: '#212121', // Rich dark gray
      secondary: '#616161', // Medium gray for secondary text
    },
    info: {
      main: '#0288d1',
    },
    success: {
      main: '#388e3c',
    },
    warning: {
      main: '#f57c00',
    },
    error: {
      main: '#d32f2f',
    },
    divider: '#e0e0e0',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
      fontSize: '1.75rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.75rem',
      lineHeight: 1.4,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: '12px',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
          fontWeight: 500,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '6px',
        },
      },
    },
  },
});

interface SelectedMutation {
  gene: string;
  position: number;
  cancerType: string;
}

function MainApp() {
  const [selectedMutation, setSelectedMutation] = useState<SelectedMutation | undefined>();
  const [selectedGene, setSelectedGene] = useState<string | undefined>();
  const [selectedCancerType, setSelectedCancerType] = useState<string | undefined>();
  const [hiddenGenes, setHiddenGenes] = useState<string[]>([]);
  const [hiddenCancerTypes, setHiddenCancerTypes] = useState<string[]>([]);
  
  const [filterPanelOpen, setFilterPanelOpen] = useState(false);
  const [detailsPanelOpen, setDetailsPanelOpen] = useState(false);
  const [therapeuticsModalOpen, setTherapeuticsModalOpen] = useState(false);
  const [selectedTherapeuticGene, setSelectedTherapeuticGene] = useState<string>('');
  
  const [currentViewLevel, setCurrentViewLevel] = useState<ViewLevel>(DataAggregationService.VIEW_LEVELS[1]);
  const [frequencyThreshold, setFrequencyThreshold] = useState(0.0019);
  const [selectedCell, setSelectedCell] = useState<AggregatedCell | null>(null);
  
  const { data: mutationData, isLoading: isDataLoading } = useMutationData();
  

  const handleMutationSelect = (mutation: SelectedMutation | undefined) => {
    setSelectedMutation(mutation);
    setSelectedGene(mutation?.gene);
  };

  const handleCellSelect = (cell: AggregatedCell | null) => {
    setSelectedCell(cell);
    if (cell) {
      setSelectedGene(cell.gene);
      setSelectedMutation({
        gene: cell.gene,
        position: cell.representativeMutation.position,
        cancerType: cell.cancerType
      });
    }
  };

  const handleGenesChange = (hidden: string[]) => {
    setHiddenGenes(hidden);
  };

  const handleGeneSelect = (gene: string | undefined) => {
    setSelectedGene(gene);
    if (gene) {
      setDetailsPanelOpen(true);
    }
  };

  const handleCancerTypesChange = (hidden: string[]) => {
    setHiddenCancerTypes(hidden);
  };

  const handleCancerTypeSelect = (cancerType: string | undefined) => {
    setSelectedCancerType(cancerType);
  };

  const handleTherapeuticGeneClick = (gene: string) => {
    setSelectedTherapeuticGene(gene);
    setTherapeuticsModalOpen(true);
  };

  return (
      <>
        <AppBar 
          position="fixed" 
          elevation={0}
          sx={{ 
            zIndex: (theme) => theme.zIndex.drawer + 1,
            bgcolor: 'background.paper',
            borderBottom: '1px solid #e0e0e0',
            height: '64px'
          }}
        >
          <Toolbar sx={{ minHeight: '64px !important' }}>
            <Box sx={{ mr: 2, display: 'flex', alignItems: 'center' }}>
              <OncoHotspotLogo size={36} variant="icon" />
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h5" sx={{ color: 'text.primary', fontWeight: 700 }}>
                OncoHotspot
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.65rem' }}>
                © 2025 Joaquin Quiroga | MIT License
              </Typography>
            </Box>
            
            <ButtonGroup variant="outlined" size="small" sx={{ mr: 2 }}>
              <Button 
                startIcon={<TuneIcon />}
                onClick={() => setFilterPanelOpen(!filterPanelOpen)}
                variant={filterPanelOpen ? "contained" : "outlined"}
              >
                Filters
                {(hiddenGenes.length > 0 || hiddenCancerTypes.length > 0) && (
                  <Badge 
                    badgeContent={hiddenGenes.length + hiddenCancerTypes.length} 
                    color="warning" 
                    sx={{ ml: 1 }}
                  />
                )}
              </Button>
            </ButtonGroup>

            <Tooltip
              title={
                <Box sx={{ p: 1, maxWidth: 400 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Data Sources & Statistics
                  </Typography>
                  
                  <Typography variant="body2" sx={{ mb: 1.5 }}>
                    <strong>Sources:</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 0.5, fontSize: '0.75rem' }}>
                    • CIViC (Clinical Interpretations of Variants in Cancer)
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 0.5, fontSize: '0.75rem' }}>
                    • cBioPortal for Cancer Genomics
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 0.5, fontSize: '0.75rem' }}>
                    • DGIdb (Drug Gene Interaction Database)
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1.5, fontSize: '0.75rem' }}>
                    • Open Targets Platform
                  </Typography>

                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Current Dataset:</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ fontSize: '0.75rem' }}>
                    {isDataLoading ? (
                      "Loading data..."
                    ) : mutationData ? (
                      <>
                        • {mutationData.length.toLocaleString()} mutation records
                        <br />
                        • {new Set(mutationData.map(m => m.gene)).size} unique genes
                        <br />
                        • {new Set(mutationData.map(m => m.cancerType)).size} cancer types
                        <br />
                        • Frequency range: {Math.min(...mutationData.map(m => m.frequency ?? m.significance)).toFixed(4)} - {Math.max(...mutationData.map(m => m.frequency ?? m.significance)).toFixed(4)}
                      </>
                    ) : (
                      "No data available"
                    )}
                  </Typography>
                </Box>
              }
              arrow
              placement="bottom-end"
            >
              <IconButton 
                size="small" 
                sx={{ 
                  ml: 1,
                  color: 'primary.main',
                  '&:hover': {
                    bgcolor: 'rgba(25, 118, 210, 0.04)'
                  }
                }}
              >
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        <Paper 
          elevation={1} 
          sx={{ 
            position: 'fixed',
            top: 64,
            left: 0,
            right: 0,
            zIndex: (theme) => theme.zIndex.drawer - 1,
            borderRadius: 0,
            borderBottom: '1px solid #e0e0e0',
            bgcolor: '#fafafa'
          }}
        >
          <Box sx={{ px: 3, py: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 0, gap: 1 }}>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 2, 
                  px: 2, 
                  py: 1
                }}>
                  <Typography variant="body2" sx={{ color: 'primary.main', fontWeight: 600, fontSize: '0.8rem' }}>
                    Min Frequency:
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 80 }}>
                      <Slider
                        value={frequencyThreshold}
                        onChange={(_, value) => setFrequencyThreshold(value as number)}
                        min={0}
                        max={0.01}
                        step={0.0001}
                        size="small"
                        sx={{ 
                          '& .MuiSlider-thumb': { width: 16, height: 16 },
                          '& .MuiSlider-track': { height: 4 },
                          '& .MuiSlider-rail': { height: 4 }
                        }}
                      />
                    </Box>
                    <Typography variant="body2" sx={{ 
                      color: 'primary.main', 
                      fontWeight: 700, 
                      minWidth: 30,
                      fontSize: '0.8rem'
                    }}>
                      {(frequencyThreshold * 100).toFixed(2)}%
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1, 
                  px: 1.5, 
                  py: 1
                }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.7rem' }}>
                    Frequency:
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.3 }}>
                    <Box sx={{ width: 6, height: 8, bgcolor: '#ffffff', border: '0.5px solid #ddd', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#fff8f8', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#ffeeee', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#ffdddd', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#ffbbbb', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#ff9999', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#ff6666', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#ff4444', borderRadius: 0.5 }} />
                    <Box sx={{ width: 6, height: 8, bgcolor: '#cc0000', borderRadius: 0.5 }} />
                  </Box>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.65rem' }}>
                    0-2%
                  </Typography>
                </Box>
                
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1, 
                  px: 1.5, 
                  py: 1
                }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.7rem' }}>
                    Therapeutic:
                  </Typography>
                  <Box sx={{ fontSize: '12px' }}>💊</Box>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.65rem' }}>
                    Available
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                justifyContent: 'center',
                gap: 2, 
                px: 3,
                minWidth: 600,
                width: 600,
                height: 50,
                minHeight: 50
              }}>
                {selectedCell ? (
                  <Box sx={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    width: '100%',
                    height: '100%',
                    gap: 0.5
                  }}>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      gap: 2
                    }}>
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 1,
                        px: 1.5,
                        py: 0.5,
                        bgcolor: 'primary.main',
                        color: 'white',
                        borderRadius: 1.5,
                        fontSize: '0.9rem',
                        fontWeight: 700,
                        letterSpacing: '0.5px'
                      }}>
                        {selectedCell.gene}
                      </Box>
                      <Typography variant="h6" sx={{ 
                        color: 'text.primary', 
                        fontWeight: 700, 
                        fontSize: '1.1rem',
                        letterSpacing: '0.3px'
                      }}>
                        {selectedCell.cancerType}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedCell(null);
                          setSelectedGene(undefined);
                          setSelectedMutation(undefined);
                        }}
                        sx={{ 
                          color: 'text.disabled',
                          ml: 1,
                          '&:hover': { 
                            color: 'error.main',
                            bgcolor: 'rgba(211, 47, 47, 0.08)'
                          }
                        }}
                      >
                        <CloseIcon sx={{ fontSize: 18 }} />
                      </IconButton>
                    </Box>
                    
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      gap: 2
                    }}>
                      <Typography variant="body2" sx={{ 
                        color: 'text.secondary',
                        fontWeight: 500,
                        fontSize: '0.85rem'
                      }}>
                        {selectedCell.totalMutations} mutations
                      </Typography>
                      
                      <Box sx={{ 
                        px: 1.5, 
                        py: 0.25, 
                        bgcolor: 'warning.light', 
                        color: 'warning.dark',
                        borderRadius: 1,
                        fontSize: '0.8rem',
                        fontWeight: 700
                      }}>
                        {(selectedCell.representativeMutation?.frequency 
                          ? (selectedCell.representativeMutation.frequency * 100).toFixed(1)
                          : (selectedCell.maxSignificance * 100).toFixed(1)
                        )}% frequency
                      </Box>
                      
                      <Typography variant="body2" sx={{ 
                        color: 'text.secondary',
                        fontWeight: 500,
                        fontSize: '0.85rem'
                      }}>
                        {selectedCell.positions.length} positions
                      </Typography>
                      
                      <Button
                        variant="text"
                        size="small"
                        onClick={() => setDetailsPanelOpen(true)}
                        sx={{ 
                          color: 'primary.main',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          textTransform: 'none',
                          px: 1,
                          minWidth: 'auto',
                          '&:hover': {
                            bgcolor: 'rgba(25, 118, 210, 0.04)'
                          }
                        }}
                      >
                        View Details →
                      </Button>
                    </Box>
                  </Box>
                ) : (
                  <Typography variant="body2" sx={{ 
                    color: 'text.disabled', 
                    fontSize: '0.85rem',
                    fontStyle: 'italic',
                    textAlign: 'center'
                  }}>
                    Click on a cell in the heatmap to select data points
                  </Typography>
                )}
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1, justifyContent: 'flex-end' }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1, 
                  px: 2, 
                  py: 1
                }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.75rem' }}>
                    Filters:
                  </Typography>
                  <Chip 
                    size="small" 
                    label={hiddenGenes.length > 0 ? `${hiddenGenes.length} genes hidden` : 'All genes visible'}
                    color={hiddenGenes.length > 0 ? "warning" : "success"}
                    variant="outlined"
                    sx={{ fontSize: '0.7rem', height: 22 }}
                  />
                  <Chip 
                    size="small" 
                    label={hiddenCancerTypes.length > 0 ? `${hiddenCancerTypes.length} types hidden` : 'All types visible'}
                    color={hiddenCancerTypes.length > 0 ? "warning" : "success"}
                    variant="outlined"
                    sx={{ fontSize: '0.7rem', height: 22 }}
                  />
                </Box>
              </Box>
              {selectedGene && !selectedCell ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                    Selected:
                  </Typography>
                  <Chip 
                    size="small"
                    label={selectedGene}
                    color="primary"
                    onDelete={() => {
                      setSelectedGene(undefined);
                      setSelectedMutation(undefined);
                    }}
                  />
                  {selectedMutation && (
                    <Chip 
                      size="small"
                      label={`${selectedMutation.cancerType} (pos: ${selectedMutation.position})`}
                      color="secondary"
                      variant="outlined"
                    />
                  )}
                </Box>
              ) : null}
            </Box>
          </Box>
        </Paper>

        <Box sx={{ 
          display: 'flex',
          height: '100vh',
          pt: '100px', // Account for header + compact control bar
          overflow: 'hidden'
        }}>
          
          <Box sx={{ 
            flexGrow: 1,
            height: '100%',
            position: 'relative',
            bgcolor: '#ffffff',
            display: 'flex'
          }}>
            <IntelligentHeatmap 
              onMutationSelect={handleMutationSelect} 
              onCellSelect={handleCellSelect}
              onTherapeuticGeneClick={handleTherapeuticGeneClick}
              hiddenGenes={hiddenGenes}
              hiddenCancerTypes={hiddenCancerTypes}
              initialViewLevel={currentViewLevel}
              significanceThreshold={frequencyThreshold}
            />
          </Box>
        </Box>

        <Drawer
          anchor="left"
          open={filterPanelOpen}
          onClose={() => setFilterPanelOpen(false)}
          sx={{
            '& .MuiDrawer-paper': {
              width: 360,
              mt: '150px',
              height: 'calc(100vh - 150px)',
              borderRadius: '0 12px 12px 0',
              boxShadow: '4px 0 24px rgba(0,0,0,0.12)'
            }
          }}
        >
          <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
            <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <TuneIcon color="primary" />
              Data Filters
            </Typography>
            
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', fontWeight: 600 }}>
                Gene Filtering
              </Typography>
              <GeneControl 
                onGenesChange={handleGenesChange}
                onGeneSelect={handleGeneSelect}
              />
            </Box>
            
            <Divider sx={{ my: 3 }} />
            
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', fontWeight: 600 }}>
                Cancer Type Filtering
              </Typography>
              <CancerTypeControl 
                onCancerTypesChange={handleCancerTypesChange}
                onCancerTypeSelect={handleCancerTypeSelect}
              />
            </Box>
          </Box>
        </Drawer>

        <Drawer
          anchor="right"
          open={detailsPanelOpen}
          onClose={() => setDetailsPanelOpen(false)}
          sx={{
            '& .MuiDrawer-paper': {
              width: 420,
              mt: '150px',
              height: 'calc(100vh - 150px)',
              borderRadius: '12px 0 0 12px',
              boxShadow: '-4px 0 24px rgba(0,0,0,0.12)'
            }
          }}
        >
          <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
            <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <TimelineIcon color="primary" />
              Analysis Details
            </Typography>
            
            {(selectedMutation || selectedGene) ? (
              <Box>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', fontWeight: 600 }}>
                    Gene Information
                  </Typography>
                  <GeneInfoPanel 
                    selectedGene={selectedGene}
                    selectedMutation={selectedMutation}
                  />
                </Box>
                
                <Divider sx={{ my: 3 }} />
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', fontWeight: 600 }}>
                    Therapeutic Options
                  </Typography>
                  <TherapeuticPanel 
                    selectedGene={selectedGene}
                    selectedMutation={selectedMutation}
                  />
                </Box>
              </Box>
            ) : (
              <Box sx={{ 
                textAlign: 'center', 
                py: 8,
                color: 'text.secondary'
              }}>
                <DatasetIcon sx={{ fontSize: 64, mb: 3, opacity: 0.3 }} />
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  No Selection
                </Typography>
                <Typography variant="body2" sx={{ maxWidth: 280, mx: 'auto' }}>
                  Click on any cell in the heatmap to view detailed gene information and therapeutic options.
                </Typography>
              </Box>
            )}
          </Box>
        </Drawer>

        <TherapeuticsModal
          open={therapeuticsModalOpen}
          onClose={() => setTherapeuticsModalOpen(false)}
          gene={selectedTherapeuticGene}
        />
      </>
  );
}

function App() {
  // Debug: Log the API URL on mount
  React.useEffect(() => {
    console.log('=== OncoHotspot Frontend Debug ===');
    console.log('Environment:', process.env.NODE_ENV);
    console.log('API URL from env:', process.env.REACT_APP_API_URL);
    console.log('API URL being used:', process.env.REACT_APP_API_URL || 'http://localhost:3001');
    
    // Test the API connection
    const testAPI = async () => {
      let apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
      // Add protocol if missing
      if (apiUrl && !apiUrl.startsWith('http')) {
        apiUrl = `https://${apiUrl}`;
      }
      try {
        console.log('Testing backend at:', `${apiUrl}/health`);
        const response = await fetch(`${apiUrl}/health`);
        const text = await response.text();
        console.log('Raw response:', text);
        
        try {
          const data = JSON.parse(text);
          console.log('Backend health check:', data);
        } catch (e) {
          console.error('Response is not JSON:', text.substring(0, 200));
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        console.error('Make sure REACT_APP_API_URL is set correctly in Vercel');
      }
    };
    testAPI();
  }, []);
  
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <MainApp />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;