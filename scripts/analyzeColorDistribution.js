#!/usr/bin/env node

/**
 * Analyze mutation data distribution and generate optimal color scale configuration
 * This script should be run once to determine the proper breakpoints for the color scale
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Open database
const dbPath = path.join(__dirname, '../database/oncohotspot.db');
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY);

// Fetch all significance scores
const query = `
  SELECT significance_score
  FROM mutations
  WHERE significance_score IS NOT NULL
  ORDER BY significance_score ASC
`;

db.all(query, [], (err, rows) => {
  if (err) {
    console.error('Error fetching data:', err);
    process.exit(1);
  }

  const values = rows.map(r => r.significance_score);
  console.log(`\n📊 Analyzing ${values.length} mutation significance values...\n`);

  // Calculate percentiles
  const percentile = (arr, p) => {
    const index = Math.ceil((p / 100) * arr.length) - 1;
    return arr[Math.max(0, index)];
  };

  const stats = {
    count: values.length,
    min: Math.min(...values),
    max: Math.max(...values),
    mean: values.reduce((a, b) => a + b, 0) / values.length,
    median: percentile(values, 50),
    percentiles: {
      p1: percentile(values, 1),
      p5: percentile(values, 5),
      p10: percentile(values, 10),
      p20: percentile(values, 20),
      p25: percentile(values, 25),
      p30: percentile(values, 30),
      p40: percentile(values, 40),
      p50: percentile(values, 50),
      p60: percentile(values, 60),
      p70: percentile(values, 70),
      p75: percentile(values, 75),
      p80: percentile(values, 80),
      p90: percentile(values, 90),
      p95: percentile(values, 95),
      p99: percentile(values, 99)
    }
  };

  // Calculate standard deviation
  const variance = values.reduce((sum, val) => sum + Math.pow(val - stats.mean, 2), 0) / values.length;
  stats.std = Math.sqrt(variance);

  // Display statistics
  console.log('📈 DISTRIBUTION STATISTICS:');
  console.log('─'.repeat(50));
  console.log(`Count:      ${stats.count}`);
  console.log(`Min:        ${stats.min.toFixed(4)}`);
  console.log(`Max:        ${stats.max.toFixed(4)}`);
  console.log(`Mean:       ${stats.mean.toFixed(4)}`);
  console.log(`Median:     ${stats.median.toFixed(4)}`);
  console.log(`Std Dev:    ${stats.std.toFixed(4)}`);
  
  console.log('\n📊 PERCENTILES:');
  console.log('─'.repeat(50));
  Object.entries(stats.percentiles).forEach(([key, value]) => {
    const percent = key.substring(1);
    const bar = '█'.repeat(Math.round(value * 50));
    console.log(`${percent.padStart(3)}%: ${value.toFixed(4)} ${bar}`);
  });

  // Count values in ranges
  const ranges = [
    { label: '0.0-0.1', min: 0.0, max: 0.1 },
    { label: '0.1-0.2', min: 0.1, max: 0.2 },
    { label: '0.2-0.3', min: 0.2, max: 0.3 },
    { label: '0.3-0.4', min: 0.3, max: 0.4 },
    { label: '0.4-0.5', min: 0.4, max: 0.5 },
    { label: '0.5-0.6', min: 0.5, max: 0.6 },
    { label: '0.6-0.7', min: 0.6, max: 0.7 },
    { label: '0.7-0.8', min: 0.7, max: 0.8 },
    { label: '0.8-0.9', min: 0.8, max: 0.9 },
    { label: '0.9-1.0', min: 0.9, max: 1.0 }
  ];

  console.log('\n📊 DISTRIBUTION BY RANGE:');
  console.log('─'.repeat(50));
  ranges.forEach(range => {
    const count = values.filter(v => v >= range.min && v < range.max).length;
    const percent = (count / values.length * 100).toFixed(1);
    const bar = '█'.repeat(Math.round(count / values.length * 100));
    console.log(`${range.label}: ${count.toString().padStart(6)} (${percent}%) ${bar}`);
  });

  // Generate optimal breakpoints
  console.log('\n🎯 RECOMMENDED COLOR SCALE BREAKPOINTS:');
  console.log('─'.repeat(50));
  
  // Option 1: Equal perception (each color range contains similar amount of data)
  const equalPerceptionBreaks = {
    white_to_light_blue: [stats.min, stats.percentiles.p20],
    light_blue_to_yellow: [stats.percentiles.p20, stats.percentiles.p50],
    yellow_to_orange: [stats.percentiles.p50, stats.percentiles.p80],
    orange_to_red: [stats.percentiles.p80, stats.percentiles.p95],
    red_to_dark_red: [stats.percentiles.p95, stats.max]
  };

  console.log('\nOption 1 - EQUAL PERCEPTION (20-30-30-15-5% distribution):');
  Object.entries(equalPerceptionBreaks).forEach(([label, [min, max]]) => {
    console.log(`  ${label.padEnd(25)}: ${min.toFixed(4)} - ${max.toFixed(4)}`);
  });

  // Option 2: Emphasize extremes (compress middle values)
  const emphasizeExtremesBreaks = {
    white_to_light_blue: [stats.min, stats.percentiles.p10],
    light_blue_to_yellow: [stats.percentiles.p10, stats.percentiles.p60],
    yellow_to_orange: [stats.percentiles.p60, stats.percentiles.p90],
    orange_to_red: [stats.percentiles.p90, stats.percentiles.p99],
    red_to_dark_red: [stats.percentiles.p99, stats.max]
  };

  console.log('\nOption 2 - EMPHASIZE EXTREMES (10-50-30-9-1% distribution):');
  Object.entries(emphasizeExtremesBreaks).forEach(([label, [min, max]]) => {
    console.log(`  ${label.padEnd(25)}: ${min.toFixed(4)} - ${max.toFixed(4)}`);
  });

  // Option 3: Clinical significance (based on typical mutation frequencies)
  const clinicalBreaks = {
    white_to_light_blue: [stats.min, 0.4],      // Very rare (<1% frequency)
    light_blue_to_yellow: [0.4, 0.7],           // Rare (1-10% frequency)
    yellow_to_orange: [0.7, 0.85],              // Common (10-30% frequency)
    orange_to_red: [0.85, 0.95],                // Very common (30-60% frequency)
    red_to_dark_red: [0.95, stats.max]          // Highly prevalent (>60% frequency)
  };

  console.log('\nOption 3 - CLINICAL SIGNIFICANCE (fixed biological thresholds):');
  Object.entries(clinicalBreaks).forEach(([label, [min, max]]) => {
    const count = values.filter(v => v >= min && v <= max).length;
    const percent = (count / values.length * 100).toFixed(1);
    console.log(`  ${label.padEnd(25)}: ${min.toFixed(4)} - ${max.toFixed(4)} (${percent}% of data)`);
  });

  // Generate TypeScript code
  console.log('\n💻 TYPESCRIPT IMPLEMENTATION:');
  console.log('─'.repeat(50));
  console.log('Copy this into your heatmap component:\n');
  
  console.log(`const colorScale = d3.scaleSequential()
  .domain([${stats.min}, ${stats.max}])
  .interpolator((t: number) => {
    const value = ${stats.min} + t * (${stats.max} - ${stats.min});
    
    // Breakpoints based on data distribution (Option 1 - Equal Perception)
    if (value <= ${stats.percentiles.p20.toFixed(4)}) {
      // Bottom 20% - White to light blue
      const localT = (value - ${stats.min}) / (${stats.percentiles.p20.toFixed(4)} - ${stats.min});
      return d3.interpolateRgb('#ffffff', '#e3f2fd')(localT);
    } else if (value <= ${stats.percentiles.p50.toFixed(4)}) {
      // 20-50 percentile - Light blue to yellow
      const localT = (value - ${stats.percentiles.p20.toFixed(4)}) / (${stats.percentiles.p50.toFixed(4)} - ${stats.percentiles.p20.toFixed(4)});
      return d3.interpolateRgb('#e3f2fd', '#ffeb3b')(localT * 0.8 + 0.2);
    } else if (value <= ${stats.percentiles.p80.toFixed(4)}) {
      // 50-80 percentile - Yellow to orange
      const localT = (value - ${stats.percentiles.p50.toFixed(4)}) / (${stats.percentiles.p80.toFixed(4)} - ${stats.percentiles.p50.toFixed(4)});
      return d3.interpolateRgb('#ffeb3b', '#ff9800')(localT);
    } else if (value <= ${stats.percentiles.p95.toFixed(4)}) {
      // 80-95 percentile - Orange to red
      const localT = (value - ${stats.percentiles.p80.toFixed(4)}) / (${stats.percentiles.p95.toFixed(4)} - ${stats.percentiles.p80.toFixed(4)});
      return d3.interpolateRgb('#ff9800', '#f44336')(localT);
    } else {
      // Top 5% - Red to dark red
      const localT = (value - ${stats.percentiles.p95.toFixed(4)}) / (${stats.max} - ${stats.percentiles.p95.toFixed(4)});
      return d3.interpolateRgb('#f44336', '#b71c1c')(localT);
    }
  })
  .clamp(true);`);

  console.log('\n✅ Analysis complete!\n');
  
  db.close();
});