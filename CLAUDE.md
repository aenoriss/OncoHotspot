# OncoHotspot Development Notes

## Project Overview
OncoHotspot is a cancer mutation visualization tool that provides interactive heatmaps showing mutation frequencies across different cancer types with therapeutic information.

## Key Technical Fixes

### Drag Scrolling Implementation
**Issue**: Horizontal drag scrolling was not working in the heatmap component after layout changes.

**Root Cause**: Event listeners were being attached before the SVG elements were fully rendered, and there were mismatches between D3 selections vs DOM elements.

**Solution**: 
1. Attach drag event listeners AFTER SVG is fully rendered (inside the main heatmap useEffect)
2. Use `svgRef.current` (DOM element) instead of d3 selection for addEventListener/removeEventListener
3. Attach mousedown events to the SVG element directly, not container divs
4. Use proper offset calculations with `scrollContainer.offsetLeft`

**Working Code Pattern**:
```typescript
// In the main heatmap rendering useEffect, after all SVG elements are created:
const scrollContainer = scrollContainerRef.current;
const svgElement = svgRef.current;
if (scrollContainer && svgElement) {
  const handleMouseDown = (e: MouseEvent) => {
    // ... drag logic
  };
  
  // Attach to actual DOM element, not D3 selection
  svgElement.addEventListener('mousedown', handleMouseDown);
  document.addEventListener('mouseup', handleMouseUp);
  document.addEventListener('mousemove', handleMouseMove);
}
```

**Key Lessons**:
- Event listeners must be attached after DOM elements are fully rendered
- Use DOM element refs, not D3 selections, for native event handling
- Attach drag events to the content (SVG) but scroll the container
- Clean up previous listeners before adding new ones to avoid duplicates

## Critical Data Quality Fixes

### Mutation Frequency Calculation
**Issue**: All mutations were showing 50-100% frequency because denominators were using only samples WITH mutations, not total samples tested.

**Root Cause**: The aggregator was counting `len(data['samples'])` which only included samples that had mutations, not the total sample count for each study.

**Solution**:
1. Extract actual sample counts from cBioPortal API (`allSampleCount` field)
2. Store study sample counts in bronze layer data
3. Use real denominators in frequency calculation: `mutated_samples / total_samples`
4. Only include data where we have actual sample counts (no estimates)

**Result**: Biologically accurate frequencies (e.g., IDH1 in LGG: 74%, BRAF in melanoma: 44%, KRAS in pancreatic: 59%)

### Therapeutic Data Integration
**Issue**: Manual curation was limited and incomplete (only 32 drugs for 15 genes).

**Solution**: 
1. Switched from DGIdb REST API (broken) to GraphQL API
2. Automated extraction for all clinically actionable genes
3. Result: 3,812 drug-gene interactions covering 145 genes

### Y-Axis Alignment
**Issue**: Y-axis labels didn't align with heatmap rows due to different margins and height calculations.

**Solution**:
1. Unified margin.top to 80px for both heatmap and Y-axis
2. Used identical height calculation formula for both
3. Added small adjustments for labels (`dy: -0.2em`) and tick lines (`translate(0, -3)`)

## Database Schema
- Uses SQLite for development
- Main tables: genes, mutations, therapeutics, cancer_types
- Mutation frequencies stored as decimals (0.0-1.0), not percentages
- Total sample counts from cBioPortal stored per study

## Frontend Architecture
- React with TypeScript
- D3.js for heatmap visualization
- MUI for UI components
- Custom hooks for data fetching and drag scrolling
- Therapeutic indicators: pill emoji (💊) below gene names
- Cell spacing: 20px horizontal, 15px vertical

## Pipeline
- Bronze → Silver → Gold medallion architecture
- Sources: cBioPortal (primary), DGIdb (therapeutics via GraphQL)
- 37,953 mutation records across 32 TCGA cancer studies
- 10,967 total samples analyzed
- Real sample counts, no estimates