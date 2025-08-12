import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { 
  Typography, 
  Box, 
  CircularProgress, 
  Alert
} from '@mui/material';
import { useMutationData } from '../../hooks/useMutationData';
import { 
  DataAggregationService, 
  ViewLevel, 
  MutationData, 
  AggregatedCell 
} from '../../services/dataAggregationService';

interface IntelligentHeatmapProps {
  onMutationSelect?: (mutation: { gene: string; position: number; cancerType: string } | undefined) => void;
  onCellSelect?: (cell: AggregatedCell | null) => void;
  onTherapeuticGeneClick?: (gene: string) => void;
  hiddenGenes?: string[];
  hiddenCancerTypes?: string[];
  initialViewLevel?: ViewLevel;
  significanceThreshold?: number;
}


const IntelligentHeatmap: React.FC<IntelligentHeatmapProps> = ({ 
  onMutationSelect,
  onCellSelect,
  onTherapeuticGeneClick,
  hiddenGenes = [], 
  hiddenCancerTypes = [],
  initialViewLevel = DataAggregationService.VIEW_LEVELS[1],
  significanceThreshold = 0.5
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const preventClick = useRef(false);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  
  const [currentViewLevel, setCurrentViewLevel] = useState<ViewLevel>(
    DataAggregationService.VIEW_LEVELS.find(v => v.name === 'complete') || initialViewLevel
  );
  const [isProcessing, setIsProcessing] = useState(false);
  const [therapeuticGenes, setTherapeuticGenes] = useState<string[]>([]);
  const [selectedCell, setSelectedCell] = useState<AggregatedCell | null>(null);
  
  const { data: rawMutationData, isLoading, error } = useMutationData();

  useEffect(() => {
    const fetchTherapeuticGenes = async () => {
      try {
        const response = await fetch('http://localhost:3001/api/therapeutics');
        if (response.ok) {
          const result = await response.json();
          const genes = Array.from(new Set(result.data?.map((t: any) => t.gene_symbol) || [])) as string[];
          setTherapeuticGenes(genes);
        } else {
          console.warn('Therapeutics API not available, status:', response.status);
        }
      } catch (err) {
        console.error('Could not fetch therapeutic genes:', err);
        // Don't let this break the heatmap
      }
    };

    fetchTherapeuticGenes();
  }, []);

  // Drag scroll state
  const dragState = useRef({
    isMouseDown: false,
    startX: 0,
    scrollLeft: 0,
    hasMoved: false
  });

  useEffect(() => {
    const updateDimensions = () => {
      const scrollContainer = scrollContainerRef.current;
      const containerWidth = scrollContainer?.clientWidth || (window.innerWidth - 280);
      const containerHeight = scrollContainer?.clientHeight || (window.innerHeight - 120);
      setDimensions({ width: containerWidth, height: containerHeight });
      
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const processedData = useMemo(() => {
    if (!rawMutationData || rawMutationData.length === 0) return null;
    
    setIsProcessing(true);
    
    try {
      const viewLevelCopy = { ...currentViewLevel, minSignificance: significanceThreshold };
      const filtered = DataAggregationService.filterForViewLevel(
        rawMutationData,
        viewLevelCopy,
        hiddenGenes,
        hiddenCancerTypes
      );
      
      const sampleLimit = currentViewLevel.name === 'complete' ? 100000 : 50000;
      const sampled = DataAggregationService.sampleMutations(filtered, sampleLimit);
      
      const cellMap = DataAggregationService.aggregateToHeatmapCells(sampled);
      const cells = Array.from(cellMap.values());
      
      const genes = Array.from(new Set(cells.map(c => c.gene))).sort((a, b) => a.localeCompare(b));
      const cancerTypes = Array.from(new Set(cells.map(c => c.cancerType))).sort((a, b) => a.localeCompare(b));
      
      const cellSizing = DataAggregationService.calculateOptimalCellSize(
        dimensions.width,
        dimensions.height,
        genes.length,
        cancerTypes.length
      );
      
      setIsProcessing(false);
      
      return {
        cells,
        genes,
        cancerTypes,
        cellSizing,
        stats: {
          originalCount: rawMutationData.length,
          filteredCount: filtered.length,
          sampledCount: sampled.length,
          cellCount: cells.length
        }
      };
      
    } catch (err) {
      setIsProcessing(false);
      console.error('Data processing error:', err);
      return null;
    }
  }, [rawMutationData, currentViewLevel, significanceThreshold, hiddenGenes, hiddenCancerTypes, dimensions]);

  useEffect(() => {
    if (!processedData || !svgRef.current || dimensions.width === 0) return;
    
    const { cells, genes, cancerTypes, cellSizing } = processedData;
    
    if (!cellSizing.feasible) {
      console.warn('Data too large for current screen, some cells may not render properly');
    }

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 80, right: 50, bottom: 80, left: 0 };
    
    const idealCellSize = 20;
    const idealCellHeightSize = 15; // Reduced vertical spacing
    const absoluteMinWidth = 2000;
    const minHeatmapWidth = genes.length * idealCellSize;
    const minHeatmapHeight = cancerTypes.length * idealCellHeightSize;
    
    const availableHeight = dimensions.height - margin.top - margin.bottom;
    const heatmapHeight = Math.max(minHeatmapHeight, availableHeight);
    
    const availableWidth = dimensions.width - margin.left - margin.right;
    const dataWidth = genes.length * idealCellSize;
    const heatmapWidth = Math.max(4000, absoluteMinWidth, minHeatmapWidth, dataWidth);
    
    const svgWidth = heatmapWidth + margin.left + margin.right;
    const svgHeight = heatmapHeight + margin.top + margin.bottom;

    svg.attr('width', svgWidth).attr('height', svgHeight);
    
    if (containerRef.current) {
      containerRef.current.style.width = `${svgWidth}px`;
      containerRef.current.style.minWidth = `${svgWidth}px`;
    }
    

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleBand()
      .domain(genes)
      .range([0, heatmapWidth])
      .padding(0);

    const yScale = d3.scaleBand()
      .domain(cancerTypes)
      .range([0, heatmapHeight])
      .padding(0);

    const dataForColorScale = rawMutationData || [];
    const allFrequencyValues = dataForColorScale.length > 0 
      ? dataForColorScale.map(d => d.frequency ?? d.significance) 
      : cells.map(d => d.representativeMutation.frequency ?? d.maxSignificance);
    const globalMaxFrequency = d3.max(allFrequencyValues) || 1;
    const globalMinFrequency = d3.min(allFrequencyValues) || 0;
    const globalMedianFrequency = d3.median(allFrequencyValues) || 0.5;
    const globalQ25Frequency = d3.quantile(allFrequencyValues.sort((a, b) => a - b), 0.25) || 0;
    const globalQ75Frequency = d3.quantile(allFrequencyValues.sort((a, b) => a - b), 0.75) || 0.75;
    const hasFrequencyField = rawMutationData && rawMutationData.length > 0 && 
                             rawMutationData[0].frequency !== undefined;
    const colorScale = (value: number) => {
      const t = Math.max(0, Math.min(value, 0.05));
      
      if (t < 0.0001) {
        return '#ffffff';
      } else if (t < 0.001) {
        const localT = (t - 0.0001) / 0.0009;
        const r = 255;
        const g = Math.round(255 - localT * 5);
        const b = Math.round(255 - localT * 5);
        return `rgb(${r},${g},${b})`;
      } else if (t < 0.005) {
        const localT = (t - 0.001) / 0.004;
        const r = 255;
        const g = Math.round(250 - localT * 30);
        const b = Math.round(250 - localT * 30);
        return `rgb(${r},${g},${b})`;
      } else if (t < 0.01) {
        const localT = (t - 0.005) / 0.005;
        const r = 255;
        const g = Math.round(220 - localT * 70);
        const b = Math.round(220 - localT * 70);
        return `rgb(${r},${g},${b})`;
      } else if (t < 0.02) {
        const localT = (t - 0.01) / 0.01;
        const r = Math.round(255 - localT * 51);
        const g = Math.round(150 - localT * 150);
        const b = Math.round(150 - localT * 150);
        return `rgb(${r},${g},${b})`;
      } else {
        return '#cc0000';
      }
    };

    const cellLookup = new Map<string, AggregatedCell>();
    cells.forEach(cell => {
      cellLookup.set(`${cell.gene}:${cell.cancerType}`, cell);
    });

    genes.forEach(gene => {
      cancerTypes.forEach(cancerType => {
        const cell = cellLookup.get(`${gene}:${cancerType}`);
        
        if (cell) {
          const cellGroup = g.append('g')
            .datum(cell);
            
          // Make squares with no gaps - use the smaller dimension
          const squareSize = Math.min(xScale.bandwidth(), yScale.bandwidth());
          // Position at the start of each band (no centering offset)
          const xOffset = 0;
          const yOffset = 0;
          
          const freqValue = cell.representativeMutation.frequency ?? cell.maxSignificance;
          
          const rect = cellGroup.append('rect')
            .attr('x', xScale(gene)! + xOffset)
            .attr('y', yScale(cancerType)! + yOffset)
            .attr('width', 0)
            .attr('height', 0)
            .style('fill', colorScale(freqValue))
            .style('stroke', 'none')
            .style('cursor', 'grab')
            .style('opacity', 0);

          rect
            .transition()
            .duration(800)
            .delay((genes.indexOf(gene) + cancerTypes.indexOf(cancerType)) * 5)
            .ease(d3.easeCubicOut)
            .attr('width', squareSize)
            .attr('height', squareSize)
            .style('opacity', 1.0);
            
          cellGroup
            .on('mousedown', function(event) {
            })
            .on('mouseover', function(event, d) {
              const rect = d3.select(this).select('rect');
              rect.style('cursor', 'pointer');
              
              rect
                .transition()
                .duration(200)
                .ease(d3.easeQuadOut)
                .style('stroke', '#1976d2')
                .style('stroke-width', 2);
              
              
              g.selectAll('.tick text')
                .filter((tickData: any) => tickData === d.gene)
                .transition()
                .duration(150)
                .style('font-weight', 'bold')
                .style('fill', '#1976d2')
                .style('font-size', '14px');
              
              d3.select('#fixed-y-axis')
                .selectAll('.tick text')
                .filter((tickData: any) => tickData === d.cancerType)
                .transition()
                .duration(150)
                .style('font-weight', 'bold')
                .style('fill', '#1976d2')
                .style('font-size', '14px');
              
              // Don't change size or position on hover
              // Just add visual emphasis without moving
              rect
                .transition()
                .duration(200);
            })
            .on('mouseout', function(event, d) {
              const rect = d3.select(this).select('rect');
              
              // Don't clear stroke if this is the selected cell
              if (!rect.classed('selected-cell')) {
                rect
                  .style('cursor', 'grab')
                  .transition()
                  .duration(300)
                  .ease(d3.easeQuadOut)
                  .style('stroke', 'none')
                  .style('stroke-width', 0);
              } else {
                // Keep selection styling but reset cursor
                rect.style('cursor', 'grab');
              }
              
              
              g.selectAll('.tick text')
                .transition()
                .duration(300)
                .style('font-weight', '500')
                .style('fill', '#616161')
                .style('font-size', Math.max(8, Math.min(12, cellSizing.cellWidth * 0.8)) + 'px');
              
              d3.select('#fixed-y-axis')
                .selectAll('.tick text')
                .transition()
                .duration(300)
                .style('font-weight', '500')
                .style('fill', '#616161')
                .style('font-size', Math.max(8, Math.min(12, cellSizing.cellHeight * 0.8)) + 'px');
              
              // Don't change size or position on mouseout
              // Position and size should remain constant
            })
            .on('click', function(event, d) {
              if (preventClick.current) {
                return;
              }
              
              // Clear previous selection
              g.selectAll('.selected-cell')
                .style('stroke', 'none')
                .style('stroke-width', 0)
                .classed('selected-cell', false);
              
              // Set new selection
              setSelectedCell(d);
              const rect = d3.select(this).select('rect');
              rect
                .classed('selected-cell', true)
                .transition()
                .duration(100)
                .ease(d3.easeQuadInOut)
                .style('stroke', '#d32f2f')
                .style('stroke-width', 3)
                .transition()
                .duration(200)
                .style('stroke', '#ff9800')
                .style('stroke-width', 3);
              
              if (onCellSelect) {
                onCellSelect(d);
              }
              if (onMutationSelect) {
                onMutationSelect({
                  gene: d.gene,
                  position: d.representativeMutation.position,
                  cancerType: d.cancerType
                });
              }
            });
        }
      });
    });

    const xAxis = g.append('g')
      .attr('transform', `translate(0,${heatmapHeight})`)
      .style('opacity', 0)
      .call(d3.axisBottom(xScale));
    
    xAxis
      .transition()
      .duration(1000)
      .delay(200)
      .style('opacity', 1);
      
    xAxis.selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)')
      .style('font-size', Math.max(8, Math.min(12, cellSizing.cellWidth * 0.8)) + 'px')
      .style('fill', '#616161')
      .style('font-weight', '500');

    genes.forEach(gene => {
      if (therapeuticGenes.includes(gene)) {
        const therapeuticSymbol = g.append('text')
          .attr('class', 'therapeutic-symbol')
          .attr('x', xScale(gene)! + xScale.bandwidth() / 2)
          .attr('y', heatmapHeight + 50)
          .attr('text-anchor', 'middle')
          .style('font-size', '16px')
          .style('cursor', 'pointer')
          .style('opacity', 0)
          .text('💊')
          .on('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            if (onTherapeuticGeneClick) {
              onTherapeuticGeneClick(gene);
            }
          })
          .on('mouseover', function() {
            d3.select(this)
              .style('font-size', '20px')
              .style('filter', 'drop-shadow(0 0 4px rgba(76, 175, 80, 0.8))');
            
            // Add column highlight
            const columnHighlight = g.append('rect')
              .attr('class', 'hover-column-highlight')
              .attr('x', xScale(gene)!)
              .attr('y', 0)
              .attr('width', xScale.bandwidth())
              .attr('height', heatmapHeight)
              .style('fill', 'rgba(144, 238, 144, 0.2)')
              .style('stroke', '#90EE90')
              .style('stroke-width', 2)
              .style('pointer-events', 'none')
              .style('opacity', 0);
            
            columnHighlight
              .transition()
              .duration(200)
              .style('opacity', 1);
          })
          .on('mouseout', function() {
            d3.select(this)
              .style('font-size', '16px')
              .style('filter', 'none');
            
            // Remove column highlight
            g.selectAll('.hover-column-highlight')
              .transition()
              .duration(200)
              .style('opacity', 0)
              .remove();
          });
          
        therapeuticSymbol
          .transition()
          .duration(800)
          .delay(genes.indexOf(gene) * 100)
          .style('opacity', 1);
      }
    });

    g.selectAll('.domain')
      .style('stroke', 'rgba(97, 97, 97, 0.3)')
      .style('stroke-width', 2);
    
    g.selectAll('.tick line')
      .style('stroke', 'rgba(97, 97, 97, 0.2)')
      .style('stroke-width', 1);

    // Add drag scrolling functionality
    const scrollContainer = scrollContainerRef.current;
    if (scrollContainer) {
      const handleMouseDown = (e: MouseEvent) => {
        dragState.current.isMouseDown = true;
        dragState.current.hasMoved = false;
        scrollContainer.style.cursor = 'grabbing';
        scrollContainer.style.userSelect = 'none';
        dragState.current.startX = e.pageX - scrollContainer.offsetLeft;
        dragState.current.scrollLeft = scrollContainer.scrollLeft;
        e.preventDefault();
      };

      const handleMouseUp = () => {
        dragState.current.isMouseDown = false;
        scrollContainer.style.cursor = 'grab';
        scrollContainer.style.userSelect = '';
        
        if (dragState.current.hasMoved) {
          preventClick.current = true;
          setTimeout(() => {
            preventClick.current = false;
          }, 10);
        }
      };

      const handleMouseMove = (e: MouseEvent) => {
        if (!dragState.current.isMouseDown) return;
        e.preventDefault();
        
        const x = e.pageX - scrollContainer.offsetLeft;
        const walk = (x - dragState.current.startX) * 1.5;
        scrollContainer.scrollLeft = dragState.current.scrollLeft - walk;
        
        if (Math.abs(walk) > 3) {
          dragState.current.hasMoved = true;
        }
      };

      // Clean up previous listeners
      const svgElement = svgRef.current;
      if (svgElement) {
        svgElement.removeEventListener('mousedown', handleMouseDown);
        document.removeEventListener('mouseup', handleMouseUp);
        document.removeEventListener('mousemove', handleMouseMove);

        // Add new listeners
        svgElement.addEventListener('mousedown', handleMouseDown);
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('mousemove', handleMouseMove);
      }
      
      scrollContainer.style.cursor = 'grab';
    }

  }, [processedData, dimensions, currentViewLevel]);

  useEffect(() => {
    if (!processedData || dimensions.width === 0) return;
    
    const { cancerTypes, cellSizing } = processedData;
    const yAxisSvg = d3.select('#fixed-y-axis');
    yAxisSvg.selectAll("*").remove();
    
    const margin = { top: 80, right: 0, bottom: 80, left: 280 }; // Match heatmap margin.top
    // Use exact same calculation as heatmap
    const idealCellHeightSize = 15;
    const minHeatmapHeight = cancerTypes.length * idealCellHeightSize;
    const availableHeight = dimensions.height - margin.top - margin.bottom;
    const heatmapHeight = Math.max(minHeatmapHeight, availableHeight);
    
    const yScale = d3.scaleBand()
      .domain(cancerTypes)
      .range([0, heatmapHeight])
      .padding(0);

    const yAxis = yAxisSvg.append('g')
      .attr('transform', `translate(279,${margin.top})`)
      .call(d3.axisLeft(yScale))
      .style('opacity', 0);
      
    yAxis
      .transition()
      .duration(1000)
      .delay(200)
      .style('opacity', 1);
      
    yAxis.selectAll('text')
      .style('font-size', Math.max(8, Math.min(12, cellSizing.cellHeight * 0.8)) + 'px')
      .style('fill', '#616161')
      .style('font-weight', '500')
      .attr('dy', '-0.2em'); // Shift labels up slightly to align with cell centers
    
    yAxis.selectAll('.domain')
      .style('stroke', 'rgba(97, 97, 97, 0.3)')
      .style('stroke-width', 2);
    
    yAxis.selectAll('.tick line')
      .style('stroke', 'rgba(97, 97, 97, 0.2)')
      .style('stroke-width', 1)
      .attr('transform', 'translate(0, -3)'); // Move tick lines up to match label adjustment
      
  }, [processedData, dimensions]);

  if (isLoading || isProcessing) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center',
        height: '100%',
        bgcolor: 'background.default'
      }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          {isLoading ? 'Loading mutation data...' : 'Processing large dataset...'}
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          <Typography variant="h6">Error loading mutation data</Typography>
          <Typography variant="body2">{error.message}</Typography>
        </Alert>
      </Box>
    );
  }

  if (!processedData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          No data available for current filters
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      bgcolor: 'background.default',
      position: 'relative',
      display: 'flex',
      overflow: 'hidden'
    }}>
      
      <Box sx={{ 
        width: 280,
        height: '100%',
        position: 'relative',
        bgcolor: '#fafafa',
        borderRight: '1px solid #e0e0e0',
        zIndex: 1
      }}>
        <svg 
          id="fixed-y-axis"
          style={{ 
            width: '100%',
            height: '100%',
            display: 'block'
          }}
        />
      </Box>

      <Box
        ref={scrollContainerRef}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            // Clear visual selection
            setSelectedCell(null);
            const svg = d3.select(svgRef.current);
            svg.selectAll('.selected-cell')
              .style('stroke', 'none')
              .style('stroke-width', 0)
              .classed('selected-cell', false);
            
            if (onCellSelect) onCellSelect(null);
            if (onMutationSelect) onMutationSelect(undefined);
          }
        }}
        sx={{
          width: 'calc(100% - 280px)',
          height: '100%',
          position: 'absolute',
          left: 280,
          top: 0,
          overflowX: 'auto',
          overflowY: 'hidden',
          cursor: 'grab',
          '&:active': {
            cursor: 'grabbing'
          },
          '&::-webkit-scrollbar': {
            height: 8
          },
          '&::-webkit-scrollbar-track': {
            bgcolor: '#f1f1f1'
          },
          '&::-webkit-scrollbar-thumb': {
            bgcolor: '#888',
            borderRadius: 4
          }
        }}
      >
        <div 
          ref={containerRef}
          style={{
            height: '100%',
            pointerEvents: 'auto',
            position: 'relative'
            // Width will be set dynamically in useEffect
          }}
        >
          <svg 
            ref={svgRef}
            style={{ 
              display: 'block',
              userSelect: 'none',
              WebkitUserSelect: 'none',
              MozUserSelect: 'none',
              msUserSelect: 'none',
              pointerEvents: 'auto'
            }}
          />
        </div>
      </Box>
      
    </Box>
  );
};

export default IntelligentHeatmap;