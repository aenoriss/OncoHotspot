import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { useMutationData, MutationData } from '../../hooks/useMutationData';

interface MutationHeatmapProps {
  onMutationSelect?: (mutation: { gene: string; position: number; cancerType: string } | undefined) => void;
  hiddenGenes?: string[];
  hiddenCancerTypes?: string[];
}

const MutationHeatmap: React.FC<MutationHeatmapProps> = ({ 
  onMutationSelect, 
  hiddenGenes = [], 
  hiddenCancerTypes = [] 
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedMutation, setSelectedMutation] = useState<MutationData | null>(null);
  const [clickedMutation, setClickedMutation] = useState<MutationData | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  
  const { data: mutationData, isLoading, error } = useMutationData();

  useEffect(() => {
    const updateDimensions = () => {
      const width = window.innerWidth;
      const height = window.innerHeight - 48;
      setDimensions({ width, height });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!mutationData || !svgRef.current || dimensions.width === 0) return;

    const filteredData = mutationData.filter((d: MutationData) => 
      !hiddenGenes.includes(d.gene) && !hiddenCancerTypes.includes(d.cancerType)
    );

    if (filteredData.length === 0) {
      const svg = d3.select(svgRef.current);
      svg.selectAll("*").remove();
      return;
    }

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const genes = Array.from(new Set(filteredData.map((d: MutationData) => d.gene)));
    const cancerTypes = Array.from(new Set(filteredData.map((d: MutationData) => d.cancerType)));

    const margin = { 
      top: Math.max(80, dimensions.height * 0.08), 
      right: Math.max(30, dimensions.width * 0.03), 
      bottom: Math.max(100, dimensions.height * 0.12), 
      left: Math.max(150, dimensions.width * 0.1) 
    };
    
    const idealCellSize = 20;
    const minHeatmapWidth = genes.length * idealCellSize;
    const availableHeight = dimensions.height - margin.top - margin.bottom;
    const availableWidth = Math.max(dimensions.width - margin.left - margin.right, minHeatmapWidth);
    
    const width = Math.max(minHeatmapWidth, availableWidth);
    const height = availableHeight;

    const g = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleBand()
      .domain(genes)
      .range([0, width])
      .padding(0.05);

    const yScale = d3.scaleBand()
      .domain(cancerTypes)
      .range([0, height])
      .padding(0.05);

    const maxCount = d3.max(filteredData, (d: MutationData) => d.mutationCount) || 1;
    const colorScale = d3.scaleSequential()
      .domain([Math.sqrt(1), Math.sqrt(Math.min(maxCount, 20))])
      .interpolator(d3.interpolateRgb('#00ff00', '#ff0000'))
      .clamp(true);

    const squareSize = Math.min(xScale.bandwidth(), yScale.bandwidth());
    const xOffset = (xScale.bandwidth() - squareSize) / 2;
    const yOffset = (yScale.bandwidth() - squareSize) / 2;

    g.selectAll('.cell')
      .data(filteredData)
      .enter()
      .append('rect')
      .attr('class', 'cell')
      .attr('x', (d: MutationData) => (xScale(d.gene) || 0) + xOffset)
      .attr('y', (d: MutationData) => (yScale(d.cancerType) || 0) + yOffset)
      .attr('width', squareSize)
      .attr('height', squareSize)
      .style('fill', (d: MutationData) => colorScale(Math.sqrt(d.mutationCount)))
      .style('stroke', '#fff')
      .style('stroke-width', 1)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d: MutationData) {
        d3.select(this).style('stroke-width', 2).style('stroke', '#333');
        setSelectedMutation(d);
      })
      .on('mouseout', function() {
        d3.select(this).style('stroke-width', 1).style('stroke', '#fff');
        setSelectedMutation(null);
      })
      .on('click', function(event, d: MutationData) {
        if (event.defaultPrevented) return;
        
        setClickedMutation(d);
        if (onMutationSelect) {
          onMutationSelect({
            gene: d.gene,
            position: d.position,
            cancerType: d.cancerType
          });
        }
      });

    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

    g.append('g')
      .call(d3.axisLeft(yScale));



  }, [mutationData, hiddenGenes, hiddenCancerTypes, dimensions]);

  if (isLoading) {
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
          Loading mutation data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center',
        height: '100%',
        bgcolor: 'background.default'
      }}>
        <Typography variant="h6" color="error">
          Error loading mutation data
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {error.message}
        </Typography>
      </Box>
    );
  }

  const allGenesHidden = mutationData && hiddenGenes.length > 0 && 
    mutationData.every((d: MutationData) => hiddenGenes.includes(d.gene));

  if (allGenesHidden) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center',
        height: '100%',
        bgcolor: 'background.default',
        p: 3
      }}>
        <Typography variant="h6" gutterBottom>
          All genes are currently hidden
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Use the filters panel (☰) to show genes and view the heatmap.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      bgcolor: 'background.default',
      position: 'relative'
    }}>
      {/* Selection Alert */}
      {clickedMutation && (
        <Alert 
          severity="info" 
          onClose={() => {
            setClickedMutation(null);
            if (onMutationSelect) {
              onMutationSelect(undefined);
            }
          }}
          sx={{ 
            position: 'absolute',
            top: 16,
            left: 16,
            right: 16,
            zIndex: 10,
            maxWidth: 600
          }}
        >
          <strong>Selected:</strong> {clickedMutation.gene} at position {clickedMutation.position} in {clickedMutation.cancerType}
          <br />
          <Typography variant="caption">
            Count: {clickedMutation.mutationCount} | Frequency: {((clickedMutation.frequency ?? clickedMutation.significance) * 100).toFixed(2)}%
          </Typography>
        </Alert>
      )}
      
      {/* Full-screen SVG */}
      <svg 
        ref={svgRef}
        style={{ 
          display: 'block',
          userSelect: 'none',
          WebkitUserSelect: 'none'
        }}
      />
    </Box>
  );
};

export default MutationHeatmap;