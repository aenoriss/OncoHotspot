# Technical Overview - OncoHotspot

## System Architecture Philosophy

OncoHotspot follows a modern three-tier architecture with clear separation of concerns between data processing, business logic, and presentation layers. The system prioritizes data integrity, performance, and user experience through careful engineering decisions.

## Core Design Principles

### Data-First Approach
Every visualization decision stems from actual data analysis. Rather than applying generic color scales, we analyzed the distribution of 77,131 significance values to discover that 57% cluster around 0.55, informing our custom interpolation strategy.

### Performance Through Intelligence
Instead of naive pagination, the system implements intelligent sampling strategies:
- Complete view: Handles full dataset (77K+ records) 
- Detailed view: Smart sampling to 50K records maintaining statistical validity
- Overview levels: Progressive sampling with significance-weighted selection

### Professional UX Patterns
The interface follows enterprise application patterns with:
- Centered primary actions (selection area)
- Logical control grouping (left: filters, right: status)
- Consistent visual hierarchy
- Smooth, purposeful animations

## Data Processing Architecture

### Medallion Pattern Implementation

**Bronze Layer**: Raw data preservation with minimal transformation
- Maintains original API responses for audit trails
- Implements retry logic for network resilience
- Rate limiting prevents API abuse

**Silver Layer**: Standardization without business logic
- HUGO gene symbol normalization
- HGVS mutation format validation  
- Data quality scoring and flagging

**Gold Layer**: Business-ready aggregations
- Mutation frequency calculations by gene-cancer pairs
- Statistical significance scoring
- Therapeutic association matching

### Quality Gates
Each layer implements validation checkpoints:
- Schema conformance testing
- Referential integrity checks
- Statistical outlier detection
- Completeness validation

## Frontend Engineering

### Component Architecture
The React architecture prioritizes reusability and maintainability:

```typescript
// Smart container pattern
IntelligentHeatmap -> Data processing + D3 rendering
GeneControl -> Filter logic + UI components  
CancerTypeControl -> Selection state + Visual feedback
```

### State Management Strategy
- Local component state for UI interactions
- React Query for server state caching
- Custom hooks for complex business logic
- Minimal prop drilling through strategic composition

### D3.js Integration Philosophy
Rather than fighting React's virtual DOM, we embrace a hybrid approach:
- React manages component lifecycle and state
- D3.js handles SVG manipulation and data binding
- Clear boundaries prevent conflicts

## Database Design Decisions

### Normalization vs Performance
The schema balances normalization with query performance:
- Core entities (genes, cancer_types) normalized for consistency
- Mutations table denormalized with computed fields for speed
- Composite indexes on common query patterns

### Significance Score Computation
```sql
-- Example of computed significance incorporating multiple factors
significance_score = (
    mutation_frequency * frequency_weight +
    statistical_p_value * p_value_weight +
    clinical_evidence_level * evidence_weight
) / total_weights
```

## API Design Philosophy

### Resource-Oriented Design
Endpoints follow REST principles with practical extensions:
- `/api/mutations` - Standard paginated access
- `/api/mutations/all` - Bulk access for visualization needs
- Resource nesting reflects natural relationships

### Performance Considerations
- Query parameter filtering reduces payload sizes
- Selective field inclusion minimizes bandwidth
- Intelligent caching headers improve response times

## Visualization Engineering

### Color Scale Mathematics
The custom color interpolation uses mathematical progression:

```javascript
// Progressive power scaling for better discrimination
if (t < 0.4) return linear_interpolation(t * 2.5);
else if (t < 0.6) return power_interpolation(t, 0.7);
else if (t < 0.8) return power_interpolation(t, 0.8);  
else return power_interpolation(t, 1.2);
```

This provides:
- Linear scaling in low-significance regions (most data)
- Accelerated scaling in medium regions (clinical interest)
- Aggressive scaling in high regions (immediate action)

### Animation Strategy
Animations serve functional purposes beyond aesthetics:
- Staggered cell appearance guides attention through data
- Hover scaling provides immediate visual feedback
- Transition timing prevents jarring state changes

## Scalability Considerations

### Current Architecture Limits
- SQLite suitable for current 77K record dataset
- Single-server architecture appropriate for research use
- Memory-efficient algorithms handle visualization loads

### Growth Path
For larger deployments:
1. PostgreSQL migration maintains schema compatibility
2. API Gateway enables horizontal backend scaling  
3. CDN deployment improves global access
4. Caching layers reduce database load

## Security & Privacy

### Data Handling
- All mutation data derived from public research databases
- No patient-identifiable information processed or stored
- Therapeutic associations limited to FDA-approved drugs

### Application Security
- Input validation prevents injection attacks
- Rate limiting protects against abuse
- Error messages avoid information leakage

## Monitoring & Observability

### Performance Metrics
- API response times tracked per endpoint
- Database query performance logged
- Frontend rendering times measured
- Memory usage patterns monitored

### Business Metrics  
- User interaction patterns analyzed
- Data access patterns inform caching strategies
- Error rates guide reliability improvements

## Development Workflow

### Code Quality
- TypeScript ensures type safety across stack
- ESLint enforces consistent code style
- Prettier handles automatic formatting
- Husky manages git hooks for quality gates

### Testing Strategy
- Unit tests for business logic components
- Integration tests for API endpoints
- Visual regression tests for D3.js components
- End-to-end tests for critical user journeys

This technical approach ensures OncoHotspot delivers both immediate value and long-term maintainability while handling real-world data complexities with professional engineering standards.