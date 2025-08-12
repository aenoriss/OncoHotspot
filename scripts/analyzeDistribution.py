#!/usr/bin/env python3

import sqlite3
import numpy as np
from pathlib import Path

# Connect to database
db_path = Path(__file__).parent.parent / 'database' / 'oncohotspot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch all significance scores
cursor.execute("SELECT significance_score FROM mutations ORDER BY significance_score")
values = np.array([row[0] for row in cursor.fetchall()])

print(f"\n📊 Analyzing {len(values)} mutation significance values...\n")

# Calculate statistics
stats = {
    'count': len(values),
    'min': np.min(values),
    'max': np.max(values),
    'mean': np.mean(values),
    'median': np.median(values),
    'std': np.std(values)
}

# Calculate percentiles
percentiles = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99]
percentile_values = {}
for p in percentiles:
    percentile_values[f'p{p}'] = np.percentile(values, p)

# Display statistics
print('📈 DISTRIBUTION STATISTICS:')
print('─' * 50)
print(f"Count:      {stats['count']}")
print(f"Min:        {stats['min']:.4f}")
print(f"Max:        {stats['max']:.4f}")
print(f"Mean:       {stats['mean']:.4f}")
print(f"Median:     {stats['median']:.4f}")
print(f"Std Dev:    {stats['std']:.4f}")

print('\n📊 PERCENTILES:')
print('─' * 50)
for p in percentiles:
    val = percentile_values[f'p{p}']
    bar = '█' * int(val * 50)
    print(f"{p:3}%: {val:.4f} {bar}")

# Count values in ranges
ranges = [
    (0.0, 0.1),
    (0.1, 0.2),
    (0.2, 0.3),
    (0.3, 0.4),
    (0.4, 0.5),
    (0.5, 0.6),
    (0.6, 0.7),
    (0.7, 0.8),
    (0.8, 0.9),
    (0.9, 1.0)
]

print('\n📊 DISTRIBUTION BY RANGE:')
print('─' * 50)
for min_val, max_val in ranges:
    count = np.sum((values >= min_val) & (values < max_val))
    percent = count / len(values) * 100
    bar = '█' * int(percent)
    print(f"{min_val:.1f}-{max_val:.1f}: {count:6} ({percent:5.1f}%) {bar}")

# Generate optimal breakpoints
print('\n🎯 RECOMMENDED COLOR SCALE CONFIGURATION:')
print('─' * 50)

# OPTION 1: Maximize distinction between 50% and 90%
print('\n✨ OPTIMAL: Maximize 50-90 percentile distinction')
print('─' * 50)
p50 = percentile_values['p50']
p90 = percentile_values['p90']
print(f"Problem: p50={p50:.4f} and p90={p90:.4f} are too close!")
print(f"Only {p90-p50:.4f} difference for 40% of the data!\n")

# Solution: Use non-linear breakpoints
optimal_breaks = {
    'white_to_very_light_blue': (stats['min'], percentile_values['p10']),  # Bottom 10%
    'very_light_blue_to_light_blue': (percentile_values['p10'], percentile_values['p30']),  # 10-30%
    'light_blue_to_yellow': (percentile_values['p30'], percentile_values['p60']),  # 30-60%
    'yellow_to_orange': (percentile_values['p60'], percentile_values['p85']),  # 60-85%
    'orange_to_red': (percentile_values['p85'], percentile_values['p95']),  # 85-95%
    'red_to_dark_red': (percentile_values['p95'], stats['max'])  # Top 5%
}

print('Breakpoints for maximum visual distinction:')
for label, (min_v, max_v) in optimal_breaks.items():
    count = np.sum((values >= min_v) & (values <= max_v))
    percent = count / len(values) * 100
    print(f"  {label:35}: {min_v:.4f} - {max_v:.4f} ({percent:5.1f}% of data)")

# Generate the actual TypeScript code
print('\n💻 COPY THIS INTO IntelligentHeatmap.tsx:')
print('─' * 50)
print('''
    // Data-driven color scale with optimized breakpoints
    // Designed to maximize visual distinction between p50 and p90
    const colorScale = d3.scaleSequential()
      .domain([{:.4f}, {:.4f}])  // min to max
      .interpolator((t: number) => {{
        const value = {:.4f} + t * ({:.4f} - {:.4f});
        
        // Optimized breakpoints based on actual data distribution
        if (value <= {:.4f}) {{
          // Bottom 10% - White to very light blue
          const localT = (value - {:.4f}) / ({:.4f} - {:.4f});
          return d3.interpolateRgb('#ffffff', '#f0f8ff')(localT);
        }} else if (value <= {:.4f}) {{
          // 10-30 percentile - Very light blue to light blue
          const localT = (value - {:.4f}) / ({:.4f} - {:.4f});
          return d3.interpolateRgb('#f0f8ff', '#e3f2fd')(localT);
        }} else if (value <= {:.4f}) {{
          // 30-60 percentile - Light blue to yellow
          const localT = (value - {:.4f}) / ({:.4f} - {:.4f});
          return d3.interpolateRgb('#e3f2fd', '#ffeb3b')(Math.pow(localT, 0.7));
        }} else if (value <= {:.4f}) {{
          // 60-85 percentile - Yellow to orange (KEY RANGE)
          const localT = (value - {:.4f}) / ({:.4f} - {:.4f});
          return d3.interpolateRgb('#ffeb3b', '#ff9800')(Math.pow(localT, 0.8));
        }} else if (value <= {:.4f}) {{
          // 85-95 percentile - Orange to red
          const localT = (value - {:.4f}) / ({:.4f} - {:.4f});
          return d3.interpolateRgb('#ff9800', '#d32f2f')(Math.pow(localT, 0.9));
        }} else {{
          // Top 5% - Red to dark red
          const localT = (value - {:.4f}) / ({:.4f} - {:.4f});
          return d3.interpolateRgb('#d32f2f', '#8b0000')(Math.pow(localT, 1.2));
        }}
      }})
      .clamp(true);
'''.format(
    stats['min'], stats['max'],
    stats['min'], stats['max'], stats['min'],
    percentile_values['p10'],
    stats['min'], percentile_values['p10'], stats['min'],
    percentile_values['p30'],
    percentile_values['p10'], percentile_values['p30'], percentile_values['p10'],
    percentile_values['p60'],
    percentile_values['p30'], percentile_values['p60'], percentile_values['p30'],
    percentile_values['p85'],
    percentile_values['p60'], percentile_values['p85'], percentile_values['p60'],
    percentile_values['p95'],
    percentile_values['p85'], percentile_values['p95'], percentile_values['p85'],
    percentile_values['p95'], stats['max'], percentile_values['p95']
))

conn.close()
print('\n✅ Analysis complete!\n')