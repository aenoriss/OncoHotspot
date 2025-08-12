# OncoHotspot

**Where Mutations Meet Their Match** - A comprehensive cancer mutation visualization and therapeutic association platform.

*Created by Joaquin Quiroga*

## 🎯 Overview

OncoHotspot is a data-driven platform that visualizes cancer mutation hotspots across multiple cancer types and associates them with FDA-approved targeted therapies. The system combines mutation data from major cancer genomics databases with drug-gene interaction information to provide actionable insights for precision oncology.

### Key Features
- **Interactive Mutation Heatmap**: D3.js-powered visualization with 34,871+ TCGA mutation records across 31 cancer types
- **Scientific Color Scale**: Progressive white-to-red gradient calibrated to actual mutation frequency distribution (0-2.78% range covers 99.9% of data)
- **Fixed Data Pipeline**: Properly calculates mutation frequencies using total samples tested, not just mutated samples
- **Expert UI Design**: Professional interface with centered selection area and logical control grouping
- **Complete Dataset Access**: Loads all mutations from 32 TCGA cancer studies without pagination limits
- **Intelligent Filtering**: Dynamic frequency threshold controls (0-0.55% range) with real-time updates
- **Responsive Design**: Horizontal scrolling with enhanced drag interactions and smooth animations
- **Clean Data Sources**: Uses only cBioPortal (provides denominators) and CIViC (clinical annotations)
- **Therapeutic Associations**: Automatic matching of mutations to FDA-approved targeted therapies

## 📊 Current Data Coverage

Based on the latest TCGA dataset:
- **Total Records**: 34,871 mutation records from TCGA studies
- **Cancer Studies**: 32 TCGA cancer studies with complete sample counts
- **Cancer Types**: 31 unique cancer types with proper frequency calculations
- **Frequency Distribution**: 
  - Median: 0.0003 (0.03%)
  - 90th percentile: 0.0019 (0.19%)
  - 99.9th percentile: 0.0278 (2.78%)
- **Data Sources**: cBioPortal (TCGA mutations with denominators) and CIViC (clinical annotations)
- **Color Scale**: White-to-red gradient optimized for 0-2.78% frequency range

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- SQLite3

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/oncohotspot.git
cd oncohotspot

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
npm install

# Install Python dependencies for data pipeline
cd ../data-processing
pip install -r requirements.txt
```

### Running the Application

```bash
# Terminal 1: Start the backend server
cd backend
npm run dev

# Terminal 2: Start the frontend application
cd frontend
npm run dev

# Access the application at http://localhost:3000
```

### Running the Data Pipeline

```bash
cd data-processing
python pipeline.py

# To fetch specific data sources
python pipeline.py --sources cbioportal dgidb

# To skip certain layers
python pipeline.py --skip-bronze --skip-silver
```

## 📁 Project Structure

```
oncohotspot/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── heatmap/    # D3.js heatmap visualization
│   │   │   ├── gene/       # Gene filtering and info
│   │   │   ├── cancer/     # Cancer type controls
│   │   │   └── therapeutics/ # Drug associations
│   │   ├── hooks/          # Custom React hooks
│   │   └── services/       # API client services
│   └── package.json
│
├── backend/                 # Node.js Express API
│   ├── src/
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── models/         # Data models
│   ├── database/           # SQLite database file
│   └── package.json
│
├── data-processing/         # Python ETL pipeline
│   ├── bronze/             # Raw data extraction
│   │   └── extractors/     # API clients
│   ├── silver/             # Data standardization
│   │   └── transformers/   # Data processors
│   ├── gold/               # Business aggregation
│   │   └── aggregators/    # Data enrichment
│   ├── config/             # Configuration files
│   │   └── clinically_actionable_genes.yaml
│   └── pipeline.py         # Main orchestrator
│
├── database/               # Database schemas
│   ├── schema.sql         # Table definitions
│   └── migrations/        # Schema migrations
│
└── docs/                  # Documentation
    └── ARCHITECTURE.md    # System architecture
```

## 🔄 Data Pipeline (ETL)

The data pipeline follows a **Medallion Architecture** pattern:

### Bronze Layer (Raw Data)
- Fetches raw mutation data from cBioPortal API
- Retrieves drug-gene interactions from DGIdb
- Preserves data exactly as received
- Implements rate limiting and error handling

### Silver Layer (Standardized)
- Normalizes gene symbols to HUGO standards
- Standardizes mutation notation (HGVS format)
- Validates and cleans data
- Removes duplicates

### Gold Layer (Business-Ready)
- Aggregates mutations by gene and cancer type
- Calculates mutation frequencies
- Associates mutations with therapeutics
- Generates heatmap-ready datasets

### Data Sources
- **cBioPortal**: TCGA mutation data from 13 cancer studies
- **DGIdb**: Drug-gene interaction database
- **Local Config**: Curated list of clinically actionable genes

## 🎨 Frontend Features

### Advanced Mutation Heatmap
- **D3.js Visualization**: Interactive heatmap with 34,871+ TCGA mutation records
- **Scientific Color Scale**: White-to-red gradient calibrated to actual frequency distribution (0-2.78%)
- **Professional Animations**: Staggered cell animations with smooth transitions and stable hover colors
- **Enhanced Drag Scrolling**: Horizontal scroll with improved drag interactions that don't interfere with cell clicks
- **Square Cell Design**: Consistent cell aspect ratios with no borders for clean visualization
- **Smart Scaling**: Dynamic cell sizing based on container dimensions and data volume

### Expert UI Controls
- **Centered Selection Area**: Prominently displayed with green highlighting when active
- **View Level Controls**: Dynamic view switching with intelligent data sampling
- **Significance Threshold**: Real-time filtering with slider control and percentage display
- **Professional Layout**: Grouped controls with consistent spacing and visual hierarchy
- **Filter Status Indicators**: Visual chips showing current filtering state

### Advanced Interactions
- **Cell Selection**: Click to select gene-cancer combinations with detailed information
- **Hover Effects**: Smooth scaling and stroke effects with data tooltips
- **Data Tooltips**: Comprehensive mutation information on hover
- **Smooth Transitions**: Professional animations throughout the interface

### Data Management
- **Complete Dataset Access**: All 77,131 records loaded without pagination limits
- **Intelligent Sampling**: Smart sampling for different view levels while maintaining data integrity
- **Real-time Updates**: Immediate visual updates based on filter changes
- **Memory Optimization**: Efficient data processing for large datasets

## 🔌 API Endpoints

### Mutations
- `GET /api/mutations` - Get paginated mutations with optional filtering
- `GET /api/mutations/all` - Get ALL mutations without pagination (77,131+ records)
- `GET /api/mutations/gene/:symbol` - Get mutations for specific gene

### Genes
- `GET /api/genes` - List all genes
- `GET /api/genes/:symbol` - Get gene details
- `GET /api/genes/:symbol/therapeutics` - Get associated drugs

### Cancer Types
- `GET /api/cancer-types` - List all cancer types
- `GET /api/cancer-types/:id/mutations` - Get mutations for cancer type

### Therapeutics
- `GET /api/therapeutics` - List all therapeutics
- `GET /api/therapeutics/associations` - Get mutation-drug associations

## 🗄️ Database Schema

### Core Tables
- **genes**: Gene information and descriptions
- **cancer_types**: Cancer type metadata
- **mutations**: Mutation records with frequencies
- **therapeutics**: Drug information
- **mutation_therapeutics**: Association table

### Key Indexes
- Gene symbol for fast lookups
- Cancer type for filtering
- Mutation frequency for sorting
- Composite indexes for joins

## 🧬 Clinically Actionable Genes

The platform focuses on 182 genes organized by pathway:

### Receptor Tyrosine Kinases (RTKs)
EGFR, ERBB2, ERBB3, MET, ALK, ROS1, RET, NTRK1, NTRK2, NTRK3, etc.

### MAPK Pathway
KRAS, NRAS, HRAS, BRAF, RAF1, MAP2K1, MAP2K2, MAPK1, MAPK3, etc.

### PI3K/AKT/mTOR Pathway
PIK3CA, PIK3CB, PIK3R1, PTEN, AKT1, AKT2, AKT3, MTOR, etc.

### Cell Cycle Regulators
CDK4, CDK6, CCND1, CCND2, CCND3, CDKN2A, CDKN2B, RB1, etc.

### DNA Damage Response
TP53, ATM, ATR, CHEK1, CHEK2, BRCA1, BRCA2, PALB2, etc.

### Transcription Factors
MYC, MYCN, JUN, FOS, STAT3, STAT5A, STAT5B, etc.

## ⚡ Technical Achievements

### Performance Optimizations
- **Complete Data Loading**: Successfully handles 77,131+ records without pagination limits
- **Efficient Memory Management**: Optimized data structures for large dataset visualization
- **Smart Sampling**: Intelligent data sampling for different view levels while maintaining accuracy
- **Responsive Rendering**: Smooth animations and interactions even with large datasets

### Data Analysis Insights
- **Significance Distribution Analysis**: 57% of mutations clustered around 0.55 significance
- **Custom Color Scale**: Data-driven color interpolation with 4-stage progression
- **Statistical Optimization**: Quantile-based scaling for better visual discrimination

### UI/UX Excellence
- **Expert Design**: Professional layout with centered selection area and logical grouping
- **Responsive Architecture**: Horizontal scrolling with drag support for dataset exploration
- **Visual Hierarchy**: Clear information architecture with consistent spacing and typography
- **Smooth Interactions**: Professional-grade animations and transitions throughout

## 🚧 Known Considerations

- SQLite database architecture suitable for current dataset size
- Optimized for mutation significance visualization and analysis
- Focus on actionable mutation data with therapeutic associations
- Professional visualization prioritizing data clarity and user experience

## 🔮 Future Enhancements

- [ ] Add more cancer types from non-TCGA sources
- [ ] Implement user authentication for saved analyses
- [ ] Add pathway-level visualization
- [ ] Include clinical trial data
- [ ] Support for combination therapies
- [ ] Export functionality for figures
- [ ] Integration with additional databases (COSMIC, OncoKB)
- [ ] Machine learning for mutation significance prediction

## 📚 Documentation

- [Architecture Diagrams](docs/architecture-diagrams.md) - Visual system architecture with Mermaid diagrams
- [Technical Overview](docs/technical-overview.md) - Engineering decisions and implementation details
- [Architecture Documentation](docs/ARCHITECTURE.md) - Detailed system design
- [API Documentation](docs/API.md) - Complete API reference
- [ETL Pipeline Guide](docs/ETL.md) - Data processing details
- [Development Guide](docs/DEVELOPMENT.md) - Setup and contribution guide

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Developer

**Joaquin Quiroga** - Full-stack developer and biomedical data scientist

- Designed and implemented the complete application architecture
- Developed the data-driven visualization system with D3.js
- Created the expert UI design with professional user experience
- Optimized the backend for complete dataset access and performance
- Conducted statistical analysis of significance distribution for color scale optimization

## 🙏 Acknowledgments

- TCGA for providing comprehensive cancer genomics data
- cBioPortal for accessible API and data aggregation  
- CIViC (Clinical Interpretations of Variants in Cancer) for mutation significance data
- DGIdb for drug-gene interaction data
- Open Targets Platform for therapeutic associations
- D3.js community for advanced visualization tools
- Material-UI team for professional React components