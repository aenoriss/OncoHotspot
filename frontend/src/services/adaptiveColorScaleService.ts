/**
 * Adaptive Color Scale Service
 * Dynamically adjusts color gradients based on actual data distribution
 * 
 * Author: Joaquin Quiroga
 * Purpose: Create scientifically accurate visualizations that adapt to data variability
 */

import * as d3 from 'd3';

export interface DistributionStats {
  min: number;
  max: number;
  mean: number;
  median: number;
  std: number;
  percentiles: {
    p1: number;
    p5: number;
    p10: number;
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
  };
  skewness: number;
  kurtosis: number;
  iqr: number;
  distribution_type: 'normal' | 'skewed_left' | 'skewed_right' | 'bimodal' | 'uniform';
}

export class AdaptiveColorScaleService {
  
  /**
   * Analyze the distribution of significance/frequency values
   */
  static analyzeDistribution(values: number[]): DistributionStats {
    if (values.length === 0) {
      throw new Error('Cannot analyze empty dataset');
    }

    const sorted = [...values].sort((a, b) => a - b);
    const n = sorted.length;
    
    // Basic statistics
    const min = sorted[0];
    const max = sorted[n - 1];
    const mean = d3.mean(sorted) || 0;
    const median = d3.median(sorted) || 0;
    const variance = d3.variance(sorted) || 0;
    const std = Math.sqrt(variance);
    
    // Percentiles
    const percentiles = {
      p1: d3.quantile(sorted, 0.01) || min,
      p5: d3.quantile(sorted, 0.05) || min,
      p10: d3.quantile(sorted, 0.10) || min,
      p25: d3.quantile(sorted, 0.25) || min,
      p50: median,
      p75: d3.quantile(sorted, 0.75) || max,
      p90: d3.quantile(sorted, 0.90) || max,
      p95: d3.quantile(sorted, 0.95) || max,
      p99: d3.quantile(sorted, 0.99) || max
    };
    
    // IQR for outlier detection
    const iqr = percentiles.p75 - percentiles.p25;
    
    // Skewness (simplified Pearson's second skewness coefficient)
    const skewness = std > 0 ? 3 * (mean - median) / std : 0;
    
    // Kurtosis (simplified)
    const meanDiff = values.map(v => Math.pow(v - mean, 4));
    const kurtosis = std > 0 ? (d3.mean(meanDiff) || 0) / Math.pow(std, 4) - 3 : 0;
    
    // Determine distribution type
    const distribution_type = this.classifyDistribution(skewness, kurtosis, percentiles);
    
    return {
      min,
      max,
      mean,
      median,
      std,
      percentiles,
      skewness,
      kurtosis,
      iqr,
      distribution_type
    };
  }
  
  /**
   * Classify the distribution type based on statistical measures
   */
  private static classifyDistribution(
    skewness: number, 
    kurtosis: number,
    percentiles: DistributionStats['percentiles']
  ): DistributionStats['distribution_type'] {
    
    // Check for uniformity
    const range = percentiles.p95 - percentiles.p5;
    const fullRange = percentiles.p99 - percentiles.p1;
    if (range > 0.8 * fullRange) {
      return 'uniform';
    }
    
    // Check for bimodality (simplified - looks for gap in middle)
    const lowerDensity = percentiles.p25 - percentiles.p10;
    const middleDensity = percentiles.p75 - percentiles.p25;
    const upperDensity = percentiles.p90 - percentiles.p75;
    if (middleDensity > 2 * lowerDensity && middleDensity > 2 * upperDensity) {
      return 'bimodal';
    }
    
    // Check skewness
    if (Math.abs(skewness) < 0.5) {
      return 'normal';
    } else if (skewness > 0.5) {
      return 'skewed_right';
    } else {
      return 'skewed_left';
    }
  }
  
  /**
   * Create an adaptive color scale based on data distribution
   * Uses the original color scheme but with smart breakpoints
   */
  static createAdaptiveColorScale(
    values: number[],
    colorScheme: 'original' | 'clinical' | 'heatmap' = 'original'
  ): d3.ScaleSequential<string> {
    
    const stats = this.analyzeDistribution(values);
    
    // Define color schemes
    const colors = {
      original: {
        // Original OncoHotspot colors
        veryLow: '#f8f9ff',      // Very light blue
        low: '#e3f2fd',          // Light blue
        medium: '#ffeb3b',       // Yellow
        high: '#ff9800',         // Orange
        veryHigh: '#d32f2f'      // Deep red
      },
      clinical: {
        veryLow: '#ffffff',      // White
        low: '#e8f5e9',          // Light green
        medium: '#fff59d',       // Light yellow
        high: '#ff6f00',         // Deep orange
        veryHigh: '#b71c1c'      // Dark red
      },
      heatmap: {
        veryLow: '#ffffff',      // White
        low: '#deebf7',          // Light blue
        medium: '#9ecae1',       // Medium blue
        high: '#fc9272',         // Light red
        veryHigh: '#a50f15'      // Dark red
      }
    };
    
    const scheme = colors[colorScheme];
    
    // Create adaptive breakpoints based on distribution
    const breakpoints = this.calculateAdaptiveBreakpoints(stats);
    
    // Create the color scale with adaptive interpolation
    return d3.scaleSequential()
      .domain([stats.min, stats.max])
      .interpolator((t: number) => {
        const value = stats.min + t * (stats.max - stats.min);
        
        // Map value to color based on adaptive breakpoints
        if (value <= breakpoints.veryLow) {
          // Below 10th percentile - very low values
          const localT = (value - stats.min) / (breakpoints.veryLow - stats.min);
          return d3.interpolateRgb(scheme.veryLow, scheme.low)(localT);
          
        } else if (value <= breakpoints.low) {
          // 10th to 25th percentile - low values
          const localT = (value - breakpoints.veryLow) / (breakpoints.low - breakpoints.veryLow);
          return d3.interpolateRgb(scheme.low, scheme.medium)(Math.pow(localT, 0.8));
          
        } else if (value <= breakpoints.medium) {
          // 25th to 75th percentile - medium values (bulk of data)
          const localT = (value - breakpoints.low) / (breakpoints.medium - breakpoints.low);
          // Use gentler progression in the middle range
          return d3.interpolateRgb(scheme.medium, scheme.high)(Math.pow(localT, 0.7));
          
        } else if (value <= breakpoints.high) {
          // 75th to 90th percentile - high values
          const localT = (value - breakpoints.medium) / (breakpoints.high - breakpoints.medium);
          return d3.interpolateRgb(scheme.high, scheme.veryHigh)(Math.pow(localT, 0.8));
          
        } else {
          // Above 90th percentile - very high values
          const localT = Math.min((value - breakpoints.high) / (stats.max - breakpoints.high), 1);
          // Aggressive progression for extreme values
          return d3.interpolateRgb(scheme.veryHigh, '#800000')(Math.pow(localT, 1.2));
        }
      })
      .clamp(true);
  }
  
  /**
   * Calculate adaptive breakpoints based on distribution characteristics
   */
  private static calculateAdaptiveBreakpoints(stats: DistributionStats): {
    veryLow: number;
    low: number;
    medium: number;
    high: number;
  } {
    
    switch (stats.distribution_type) {
      case 'normal':
        // For normal distributions, use standard deviations
        return {
          veryLow: Math.max(stats.mean - 1.5 * stats.std, stats.min),
          low: Math.max(stats.mean - 0.5 * stats.std, stats.min),
          medium: Math.min(stats.mean + 0.5 * stats.std, stats.max),
          high: Math.min(stats.mean + 1.5 * stats.std, stats.max)
        };
        
      case 'skewed_right':
        // For right-skewed (common in mutation data), compress the tail
        return {
          veryLow: stats.percentiles.p5,
          low: stats.percentiles.p25,
          medium: stats.percentiles.p75,
          high: stats.percentiles.p90
        };
        
      case 'skewed_left':
        // For left-skewed, compress the lower tail
        return {
          veryLow: stats.percentiles.p10,
          low: stats.percentiles.p25,
          medium: stats.percentiles.p75,
          high: stats.percentiles.p95
        };
        
      case 'bimodal':
        // For bimodal, emphasize the two peaks
        return {
          veryLow: stats.percentiles.p10,
          low: stats.percentiles.p25,
          medium: stats.percentiles.p75,
          high: stats.percentiles.p90
        };
        
      case 'uniform':
      default:
        // For uniform, use equal intervals
        const range = stats.max - stats.min;
        return {
          veryLow: stats.min + range * 0.2,
          low: stats.min + range * 0.4,
          medium: stats.min + range * 0.6,
          high: stats.min + range * 0.8
        };
    }
  }
  
  /**
   * Generate a report on the color scale configuration
   */
  static generateColorScaleReport(values: number[]): string {
    const stats = this.analyzeDistribution(values);
    const breakpoints = this.calculateAdaptiveBreakpoints(stats);
    
    const report = [
      '=== Adaptive Color Scale Configuration ===\n',
      `Distribution Type: ${stats.distribution_type}`,
      `Data Range: ${stats.min.toFixed(3)} - ${stats.max.toFixed(3)}`,
      `Mean: ${stats.mean.toFixed(3)}, Median: ${stats.median.toFixed(3)}`,
      `Standard Deviation: ${stats.std.toFixed(3)}`,
      `Skewness: ${stats.skewness.toFixed(3)}`,
      '',
      'Percentiles:',
      `  1%: ${stats.percentiles.p1.toFixed(3)}`,
      `  5%: ${stats.percentiles.p5.toFixed(3)}`,
      ` 25%: ${stats.percentiles.p25.toFixed(3)}`,
      ` 50%: ${stats.percentiles.p50.toFixed(3)}`,
      ` 75%: ${stats.percentiles.p75.toFixed(3)}`,
      ` 95%: ${stats.percentiles.p95.toFixed(3)}`,
      ` 99%: ${stats.percentiles.p99.toFixed(3)}`,
      '',
      'Color Scale Breakpoints:',
      `  Very Light (white-blue): ${stats.min.toFixed(3)} - ${breakpoints.veryLow.toFixed(3)}`,
      `  Light (blue): ${breakpoints.veryLow.toFixed(3)} - ${breakpoints.low.toFixed(3)}`,
      `  Medium (yellow): ${breakpoints.low.toFixed(3)} - ${breakpoints.medium.toFixed(3)}`,
      `  High (orange): ${breakpoints.medium.toFixed(3)} - ${breakpoints.high.toFixed(3)}`,
      `  Very High (red): ${breakpoints.high.toFixed(3)} - ${stats.max.toFixed(3)}`,
      '',
      'Interpretation:',
      this.getInterpretation(stats)
    ];
    
    return report.join('\n');
  }
  
  /**
   * Provide interpretation of the distribution
   */
  private static getInterpretation(stats: DistributionStats): string {
    switch (stats.distribution_type) {
      case 'normal':
        return 'Data follows a normal distribution. Colors will be evenly distributed around the mean.';
      case 'skewed_right':
        return 'Data is right-skewed (common for mutation frequencies). Most values are low with a long tail of high values. Color scale compressed in the tail to show more detail in common ranges.';
      case 'skewed_left':
        return 'Data is left-skewed. Most values are high with some low outliers. Color scale adjusted to emphasize variation in the high-value range.';
      case 'bimodal':
        return 'Data shows two distinct peaks. Color scale adjusted to emphasize both clusters.';
      case 'uniform':
        return 'Data is uniformly distributed. Using linear color progression.';
      default:
        return 'Unknown distribution pattern. Using adaptive percentile-based scaling.';
    }
  }
}

export default AdaptiveColorScaleService;