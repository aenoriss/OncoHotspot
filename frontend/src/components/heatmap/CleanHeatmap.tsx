import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { 
  Typography, 
  Box, 
  CircularProgress, 
  Alert,
  Chip,
  Paper,
  Tooltip
} from '@mui/material';
import { useMutationData } from '../../hooks/useMutationData';
import { MutationData } from '../../services/dataAggregationService';

interface CleanHeatmapProps {
  onCellSelect?: (cell: any) => void;
  minFrequency?: number;
  showClinicalOnly?: boolean;
}

const CleanHeatmap: React.FC<CleanHeatmapProps> = ({ 
  onCellSelect,
  minFrequency = 0.001,
  showClinicalOnly = false
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const { data: mutations, isLoading, error } = useMutationData();
  const [tooltip, setTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    content: any;
  }>({ visible: false, x: 0, y: 0, content: null });

  useEffect(() => {
    if (!mutations || mutations.length === 0 || !svgRef.current) return;

    d3.select(svgRef.current).selectAll("*").remove();

    let filteredData = mutations.filter((m: MutationData) => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      return freq >= minFrequency;
    });
    if (showClinicalOnly) {
      filteredData = filteredData.filter((m: MutationData) => m.significance >= 0.7);
    }

    const genes = Array.from(new Set(filteredData.map(m => m.gene))).sort();
    const cancerTypes = Array.from(new Set(filteredData.map(m => m.cancerType))).sort();

    const margin = { top: 100, right: 150, bottom: 50, left: 150 };
    const cellSize = 20;
    const width = genes.length * cellSize + margin.left + margin.right;
    const height = cancerTypes.length * cellSize + margin.top + margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleBand()
      .domain(genes)
      .range([0, genes.length * cellSize])
      .padding(0.05);

    const yScale = d3.scaleBand()
      .domain(cancerTypes)
      .range([0, cancerTypes.length * cellSize])
      .padding(0.05);

    const colorScale = d3.scaleSequential()
      .domain([0, 0.5])  // 0-50% frequency range
      .interpolator((t: number) => {
        if (t < 0.2) return d3.interpolateRgb('#ffffff', '#e3f2fd')(t * 5);
        if (t < 0.4) return d3.interpolateRgb('#e3f2fd', '#64b5f6')((t - 0.2) * 5);
        if (t < 0.6) return d3.interpolateRgb('#64b5f6', '#1976d2')((t - 0.4) * 5);
        if (t < 0.8) return d3.interpolateRgb('#1976d2', '#0d47a1')((t - 0.6) * 5);
        return d3.interpolateRgb('#0d47a1', '#000051')((t - 0.8) * 5);
      });

    // Draw cells
    const cells = g.selectAll('.cell')
      .data(filteredData)
      .enter().append('rect')
      .attr('class', 'cell')
      .attr('x', d => xScale(d.gene) || 0)
      .attr('y', d => yScale(d.cancerType) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', (d: MutationData) => {
        const freq = d.frequency !== undefined ? d.frequency : d.significance;
        const effectiveFreq = d.significance >= 0.7 ? 
          Math.min(freq * 1.5, 0.5) : freq;
        return colorScale(effectiveFreq);
      })
      .attr('stroke', d => d.significance >= 0.7 ? '#ff9800' : '#ddd')
      .attr('stroke-width', d => d.significance >= 0.7 ? 2 : 0.5)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
          d3.select(this)
          .attr('stroke', '#333')
          .attr('stroke-width', 2);

          const rect = (event.target as SVGElement).getBoundingClientRect();
        setTooltip({
          visible: true,
          x: rect.left + rect.width / 2,
          y: rect.top - 10,
          content: d
        });
      })
      .on('mouseout', function(event, d) {
          d3.select(this)
          .attr('stroke', d.significance >= 0.7 ? '#ff9800' : '#ddd')
          .attr('stroke-width', d.significance >= 0.7 ? 2 : 0.5);

          setTooltip({ visible: false, x: 0, y: 0, content: null });
      })
      .on('click', (event, d) => {
        if (onCellSelect) onCellSelect(d);
      });

    g.selectAll('.gene-label')
      .data(genes)
      .enter().append('text')
      .attr('class', 'gene-label')
      .attr('x', d => (xScale(d) || 0) + xScale.bandwidth() / 2)
      .attr('y', -5)
      .attr('text-anchor', 'start')
      .attr('transform', d => `rotate(-45, ${(xScale(d) || 0) + xScale.bandwidth() / 2}, -5)`)
      .style('font-size', '10px')
      .style('font-weight', d => {
        const keyGenes = ['TP53', 'KRAS', 'BRAF', 'EGFR', 'PIK3CA'];
        return keyGenes.includes(d) ? 'bold' : 'normal';
      })
      .text(d => d);

    g.selectAll('.cancer-label')
      .data(cancerTypes)
      .enter().append('text')
      .attr('class', 'cancer-label')
      .attr('x', -5)
      .attr('y', d => (yScale(d) || 0) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'end')
      .attr('alignment-baseline', 'middle')
      .style('font-size', '10px')
      .text(d => d.length > 30 ? d.substring(0, 30) + '...' : d);

    const legendWidth = 200;
    const legendHeight = 20;
    
    const legend = svg.append('g')
      .attr('transform', `translate(${width - margin.right - legendWidth}, ${height - margin.bottom + 20})`);

    const gradientId = 'frequency-gradient';
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', gradientId)
      .attr('x1', '0%')
      .attr('x2', '100%');

    const stops = d3.range(0, 1.1, 0.1);
    stops.forEach(stop => {
      gradient.append('stop')
        .attr('offset', `${stop * 100}%`)
        .attr('stop-color', colorScale(stop * 0.5));
    });

    legend.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', `url(#${gradientId})`);

    legend.append('text')
      .attr('x', 0)
      .attr('y', -5)
      .style('font-size', '10px')
      .text('0%');

    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -5)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .text('25%');

    legend.append('text')
      .attr('x', legendWidth)
      .attr('y', -5)
      .attr('text-anchor', 'end')
      .style('font-size', '10px')
      .text('50%+');

    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', legendHeight + 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('font-weight', 'bold')
      .text('Mutation Frequency');

    const clinicalLegend = svg.append('g')
      .attr('transform', `translate(${width - margin.right - legendWidth}, ${margin.top})`);

    clinicalLegend.append('rect')
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#e3f2fd')
      .attr('stroke', '#ff9800')
      .attr('stroke-width', 2);

    clinicalLegend.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .style('font-size', '11px')
      .text('Clinically Actionable');

  }, [mutations, minFrequency, showClinicalOnly]);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load mutation data: {error.message}
      </Alert>
    );
  }

  if (!mutations || mutations.length === 0) {
    return (
      <Alert severity="info">
        No mutation data available
      </Alert>
    );
  }

  const stats = {
    total: mutations.length,
    filtered: mutations.filter((m: MutationData) => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      return freq >= minFrequency;
    }).length,
    clinical: mutations.filter((m: MutationData) => m.significance >= 0.7).length,
    avgFreq: mutations.reduce((sum, m: MutationData) => {
      const freq = m.frequency !== undefined ? m.frequency : m.significance;
      return sum + freq;
    }, 0) / mutations.length
  };

  return (
    <Box>
      <Box mb={2}>
        <Typography variant="h5" gutterBottom>
          Cancer Mutation Frequency Heatmap
        </Typography>
        <Box display="flex" gap={2} mb={2}>
          <Chip 
            label={`${stats.filtered} mutations shown`} 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            label={`${stats.clinical} clinically actionable`} 
            color="warning" 
            variant="outlined" 
          />
          <Chip 
            label={`Avg frequency: ${(stats.avgFreq * 100).toFixed(1)}%`} 
            color="info" 
            variant="outlined" 
          />
        </Box>
      </Box>

      <Box 
        sx={{ 
          overflowX: 'auto', 
          overflowY: 'auto', 
          maxHeight: '80vh',
          border: '1px solid #ddd',
          borderRadius: 1,
          backgroundColor: '#fafafa'
        }}
      >
        <svg ref={svgRef}></svg>
      </Box>

      {tooltip.visible && tooltip.content && (
        <Paper
          elevation={3}
          sx={{
            position: 'fixed',
            left: tooltip.x,
            top: tooltip.y,
            transform: 'translate(-50%, -100%)',
            padding: 2,
            pointerEvents: 'none',
            zIndex: 9999,
            minWidth: 250
          }}
        >
          <Typography variant="subtitle2" fontWeight="bold">
            {tooltip.content.gene} at position {tooltip.content.position}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {tooltip.content.cancerType}
          </Typography>
          <Box mt={1}>
            <Typography variant="body2">
              Frequency: {((tooltip.content.frequency !== undefined ? tooltip.content.frequency : tooltip.content.significance) * 100).toFixed(2)}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              ({tooltip.content.mutationCount} mutations)
            </Typography>
          </Box>
          {(tooltip.content.frequency !== undefined ? tooltip.content.frequency : tooltip.content.significance) >= 0.01 && (
            <Box mt={1}>
              <Chip 
                label="High Frequency (≥1%)" 
                size="small" 
                color="warning" 
              />
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default CleanHeatmap;