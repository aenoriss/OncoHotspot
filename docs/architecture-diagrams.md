# OncoHotspot Architecture Diagrams

## ETL Pipeline - Medallion Architecture

```mermaid
graph TB
    subgraph "External Data Sources"
        A[cBioPortal API]
        B[DGIdb API]
        C[CIViC Database]
        D[Open Targets]
    end
    
    subgraph "Bronze Layer - Raw Ingestion"
        E[Raw Mutation Data]
        F[Drug Interactions]
        G[Clinical Annotations]
        H[Target Associations]
    end
    
    subgraph "Silver Layer - Standardization"
        I[Gene Symbol Normalization]
        J[Mutation Format Validation]
        K[Data Quality Checks]
        L[Deduplication Engine]
    end
    
    subgraph "Gold Layer - Business Logic"
        M[Mutation Aggregation]
        N[Significance Scoring]
        O[Therapeutic Matching]
        P[Heatmap Preparation]
    end
    
    subgraph "Application Layer"
        Q[(SQLite Database)]
        R[REST API]
        S[React Frontend]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
    
    E --> I
    F --> J
    G --> K
    H --> L
    
    I --> M
    J --> N
    K --> O
    L --> P
    
    M --> Q
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R
    R --> S
```

## Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Data Ingestion"
        A[Scheduled ETL Jobs] --> B{Data Source Available?}
        B -->|Yes| C[Extract Raw Data]
        B -->|No| D[Log Error & Retry]
        C --> E[Rate Limiting Check]
        E --> F[Store in Bronze]
    end
    
    subgraph "Data Processing"
        F --> G[Schema Validation]
        G --> H{Valid Format?}
        H -->|No| I[Error Logging]
        H -->|Yes| J[Gene Symbol Mapping]
        J --> K[Mutation Standardization]
        K --> L[Store in Silver]
    end
    
    subgraph "Business Intelligence"
        L --> M[Frequency Calculation]
        M --> N[Significance Analysis]
        N --> O[Statistical Scoring]
        O --> P[Therapeutic Associations]
        P --> Q[Store in Gold]
    end
    
    subgraph "Application Services"
        Q --> R[(Production Database)]
        R --> S[Mutation Service]
        R --> T[Gene Service]
        R --> U[Therapeutic Service]
    end
    
    S --> V[Heatmap API]
    T --> W[Filter API]
    U --> X[Association API]
    
    V --> Y[Frontend Components]
    W --> Y
    X --> Y
```

## Frontend Component Architecture

```mermaid
graph LR
    subgraph "Application Shell"
        A[App.tsx] --> B[QueryClientProvider]
        B --> C[ThemeProvider]
        C --> D[Main Layout]
    end
    
    subgraph "Core Components"
        D --> E[Navigation Bar]
        D --> F[Control Bar]
        D --> G[Heatmap Container]
        D --> H[Filter Drawer]
    end
    
    subgraph "Heatmap System"
        G --> I[IntelligentHeatmap]
        I --> J[D3.js Renderer]
        I --> K[Data Processor]
        I --> L[Interaction Handler]
    end
    
    subgraph "Control Systems"
        F --> M[View Selector]
        F --> N[Threshold Slider]
        F --> O[Selection Display]
        H --> P[Gene Filter]
        H --> Q[Cancer Type Filter]
    end
    
    subgraph "Data Management"
        R[useMutationData Hook] --> S[React Query Cache]
        S --> T[API Client]
        T --> U[Backend Services]
        
        K --> R
        P --> R
        Q --> R
    end
    
    subgraph "State Management"
        V[Component State] --> W[Selected Mutations]
        V --> X[Filter State]  
        V --> Y[UI State]
        
        L --> V
        M --> V
        N --> V
    end
```

## Database Schema Relationships

```mermaid
erDiagram
    GENES ||--o{ MUTATIONS : contains
    CANCER_TYPES ||--o{ MUTATIONS : affects
    MUTATIONS ||--o{ MUTATION_THERAPEUTICS : targets
    THERAPEUTICS ||--o{ MUTATION_THERAPEUTICS : treats
    
    GENES {
        int gene_id PK
        string gene_symbol
        string gene_name
        text description
        string pathway
        datetime created_at
    }
    
    CANCER_TYPES {
        int cancer_type_id PK
        string cancer_name
        string tcga_code
        text description
        datetime created_at
    }
    
    MUTATIONS {
        int mutation_id PK
        int gene_id FK
        int cancer_type_id FK
        int position
        string ref_allele
        string alt_allele
        int mutation_count
        float significance_score
        float frequency
        float p_value
        string mutation_type
        datetime created_at
    }
    
    THERAPEUTICS {
        int therapeutic_id PK
        string drug_name
        string mechanism
        string approval_status
        text indications
        datetime created_at
    }
    
    MUTATION_THERAPEUTICS {
        int association_id PK
        int mutation_id FK
        int therapeutic_id FK
        string evidence_level
        text clinical_notes
        datetime created_at
    }
```

## System Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        A[Local Development]
        A1[React Dev Server :3000]
        A2[Node.js API :3001]
        A3[SQLite Database]
        A --> A1
        A --> A2
        A --> A3
    end
    
    subgraph "Data Processing Pipeline"
        B[ETL Scheduler]
        B1[Python Workers]
        B2[Data Validation]
        B3[Error Handling]
        B --> B1
        B1 --> B2
        B2 --> B3
    end
    
    subgraph "Production Deployment"
        C[Load Balancer]
        C1[Frontend Servers]
        C2[API Servers]
        C3[Database Cluster]
        C --> C1
        C --> C2
        C2 --> C3
    end
    
    subgraph "Monitoring & Logging"
        D[Application Logs]
        D1[Performance Metrics]
        D2[Error Tracking]
        D3[Health Checks]
        D --> D1
        D --> D2
        D --> D3
    end
    
    B3 --> C3
    C1 --> D
    C2 --> D
    C3 --> D
```

## Data Significance Analysis Pipeline

```mermaid
flowchart LR
    subgraph "Raw Data Analysis"
        A[77,131 Records] --> B[Extract Significance Values]
        B --> C[Statistical Analysis]
    end
    
    subgraph "Distribution Analysis"
        C --> D[Min: 0.1]
        C --> E[Q25: 0.25]
        C --> F[Median: 0.55]
        C --> G[Q75: 0.75] 
        C --> H[Max: 1.0]
    end
    
    subgraph "Color Scale Design"
        D --> I[Very Light Blue]
        E --> J[Light Blue]
        F --> K[Yellow]
        G --> L[Orange]
        H --> M[Deep Red]
    end
    
    subgraph "Custom Interpolation"
        I --> N[t < 0.4: Linear Scale]
        J --> O[0.4 ≤ t < 0.6: Power 0.7]
        K --> P[0.6 ≤ t < 0.8: Power 0.8]
        L --> Q[t ≥ 0.8: Power 1.2]
    end
    
    subgraph "Visual Output"
        N --> R[Optimized Gradient]
        O --> R
        P --> R
        Q --> R
        R --> S[Heatmap Rendering]
    end
```