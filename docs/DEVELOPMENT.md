# Development Guide

## Development Environment Setup

### Prerequisites

#### Required Software
- **Node.js**: v16.0.0 or higher
- **Python**: 3.8 or higher
- **npm**: 7.0.0 or higher
- **Git**: 2.0 or higher
- **SQLite3**: 3.0 or higher

#### Recommended Tools
- **VS Code**: With extensions for TypeScript, Python, and React
- **Postman**: For API testing
- **DB Browser for SQLite**: For database inspection
- **Chrome DevTools**: For frontend debugging

### Initial Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/oncohotspot.git
cd oncohotspot
```

2. **Setup Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
cd data-processing
pip install -r requirements.txt
```

3. **Install Node Dependencies**
```bash
# Frontend dependencies
cd frontend
npm install

# Backend dependencies
cd ../backend
npm install
```

4. **Initialize Database**
```bash
cd database
sqlite3 oncohotspot.db < schema.sql
```

5. **Run Initial Data Pipeline**
```bash
cd data-processing
python pipeline.py
```

## Project Structure

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── heatmap/      # D3.js visualization
│   │   ├── gene/         # Gene-related UI
│   │   ├── cancer/       # Cancer type UI
│   │   └── common/       # Shared components
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API client
│   ├── types/            # TypeScript definitions
│   └── utils/            # Utility functions
├── public/               # Static assets
├── tsconfig.json         # TypeScript config
└── package.json          # Dependencies
```

### Backend (Node.js + Express)
```
backend/
├── src/
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic
│   ├── middleware/       # Express middleware
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── database/             # SQLite database
├── tsconfig.json         # TypeScript config
└── package.json          # Dependencies
```

### Data Processing (Python)
```
data-processing/
├── bronze/               # Raw data extraction
├── silver/               # Data standardization
├── gold/                 # Business aggregation
├── config/               # Configuration files
├── scripts/              # Utility scripts
└── pipeline.py           # Main orchestrator
```

## Development Workflow

### 1. Starting Development Servers

**Frontend Development Server**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
# Hot reload enabled
```

**Backend Development Server**
```bash
cd backend
npm run dev
# Runs on http://localhost:5000
# Nodemon watches for changes
```

### 2. Making Code Changes

#### Frontend Development

**Creating a New Component**
```typescript
// src/components/MyComponent.tsx
import React from 'react';

interface MyComponentProps {
  title: string;
  onAction: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title, onAction }) => {
  return (
    <div className="my-component">
      <h2>{title}</h2>
      <button onClick={onAction}>Action</button>
    </div>
  );
};
```

**Adding a Custom Hook**
```typescript
// src/hooks/useMyData.ts
import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';

export const useMyData = (param: string) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiClient.get(`/endpoint/${param}`);
        setData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [param]);

  return { data, loading, error };
};
```

#### Backend Development

**Creating a New Route**
```typescript
// src/routes/myRoute.ts
import { Router, Request, Response } from 'express';
import { MyService } from '../services/myService';

const router = Router();
const service = new MyService();

router.get('/my-endpoint', async (req: Request, res: Response) => {
  try {
    const result = await service.getData(req.query);
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

export default router;
```

**Adding a Service**
```typescript
// src/services/myService.ts
import { Database } from './database';

export class MyService {
  private db: Database;

  constructor() {
    this.db = new Database();
  }

  async getData(params: any) {
    const query = `
      SELECT * FROM my_table
      WHERE condition = ?
    `;
    return await this.db.all(query, [params.value]);
  }
}
```

#### Data Pipeline Development

**Adding a New Extractor**
```python
# bronze/extractors/my_extractor.py
from .base_extractor import BaseExtractor
import requests

class MyExtractor(BaseExtractor):
    def __init__(self):
        super().__init__("my_source")
        self.api_url = "https://api.example.com"
    
    def extract(self):
        response = self.fetch_with_retry(f"{self.api_url}/data")
        self.save_raw_data(response.json())
        return response.json()
```

### 3. Testing

#### Frontend Testing
```bash
cd frontend
npm test                  # Run tests
npm run test:coverage     # Run with coverage
npm run test:watch       # Watch mode
```

**Writing Tests**
```typescript
// src/components/__tests__/MyComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  it('renders title', () => {
    render(<MyComponent title="Test" onAction={() => {}} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('calls onAction when button clicked', () => {
    const mockAction = jest.fn();
    render(<MyComponent title="Test" onAction={mockAction} />);
    fireEvent.click(screen.getByRole('button'));
    expect(mockAction).toHaveBeenCalled();
  });
});
```

#### Backend Testing
```bash
cd backend
npm test                  # Run tests
npm run test:integration  # Integration tests
npm run test:e2e         # End-to-end tests
```

**Writing API Tests**
```typescript
// src/routes/__tests__/myRoute.test.ts
import request from 'supertest';
import app from '../../app';

describe('GET /api/my-endpoint', () => {
  it('returns data successfully', async () => {
    const response = await request(app)
      .get('/api/my-endpoint')
      .expect(200);
    
    expect(response.body.success).toBe(true);
    expect(response.body.data).toBeDefined();
  });
});
```

#### Pipeline Testing
```bash
cd data-processing
python -m pytest tests/          # Run all tests
python -m pytest tests/test_extractors.py  # Specific test
python -m pytest -v             # Verbose output
```

### 4. Database Management

#### Schema Changes
```sql
-- database/migrations/001_add_new_table.sql
CREATE TABLE IF NOT EXISTS new_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field1 VARCHAR(100) NOT NULL,
    field2 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index
CREATE INDEX idx_new_table_field1 ON new_table(field1);
```

#### Running Migrations
```bash
cd database
sqlite3 oncohotspot.db < migrations/001_add_new_table.sql
```

#### Database Backup
```bash
# Create backup
sqlite3 oncohotspot.db ".backup backup.db"

# Restore from backup
sqlite3 oncohotspot.db < backup.db
```

### 5. Debugging

#### Frontend Debugging

**Using React DevTools**
1. Install React Developer Tools Chrome extension
2. Open Chrome DevTools → Components tab
3. Inspect component props and state

**Debug Configuration (VS Code)**
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Debug Frontend",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

#### Backend Debugging

**Using Node Inspector**
```bash
# Start with inspector
node --inspect src/index.js

# Or with nodemon
nodemon --inspect src/index.js
```

**Debug Configuration (VS Code)**
```json
// .vscode/launch.json
{
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Backend",
      "program": "${workspaceFolder}/backend/src/index.js",
      "envFile": "${workspaceFolder}/backend/.env"
    }
  ]
}
```

#### Pipeline Debugging

**Enable Debug Logging**
```python
# Set in pipeline.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via command line
python pipeline.py --debug
```

**Interactive Debugging**
```python
# Add breakpoints in code
import pdb
pdb.set_trace()

# Or use iPython
import IPython
IPython.embed()
```

## Code Style Guidelines

### TypeScript/JavaScript

**ESLint Configuration**
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended"
  ],
  "rules": {
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
```

**Prettier Configuration**
```json
// .prettierrc
{
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2,
  "semi": true,
  "printWidth": 100
}
```

### Python

**Black Configuration**
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
```

**Flake8 Configuration**
```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation

### Commit Messages
```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

**Example:**
```
feat(heatmap): add cancer type filtering

- Added CancerTypeControl component
- Updated MutationHeatmap to support filtering
- Added hiddenCancerTypes state management

Closes #123
```

### Pull Request Process
1. Create feature branch from `main`
2. Make changes and commit
3. Push branch to remote
4. Create pull request
5. Code review
6. Merge to main

## Performance Optimization

### Frontend Optimization

**Component Memoization**
```typescript
import React, { memo, useMemo } from 'react';

export const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => {
    return data.map(item => /* expensive operation */);
  }, [data]);

  return <div>{/* render */}</div>;
});
```

**Lazy Loading**
```typescript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Backend Optimization

**Database Query Optimization**
```typescript
// Use indexes
await db.run('CREATE INDEX idx_mutations_gene ON mutations(gene_id)');

// Use prepared statements
const stmt = db.prepare('SELECT * FROM mutations WHERE gene_id = ?');
const results = stmt.all(geneId);

// Batch operations
await db.run('BEGIN TRANSACTION');
for (const item of items) {
  await stmt.run(item);
}
await db.run('COMMIT');
```

**Caching**
```typescript
import NodeCache from 'node-cache';

const cache = new NodeCache({ stdTTL: 600 });

async function getCachedData(key: string) {
  let data = cache.get(key);
  if (!data) {
    data = await fetchFromDatabase(key);
    cache.set(key, data);
  }
  return data;
}
```

## Deployment

### Building for Production

**Frontend Build**
```bash
cd frontend
npm run build
# Output in build/ directory
```

**Backend Build**
```bash
cd backend
npm run build
# Output in dist/ directory
```

### Environment Variables

**Frontend (.env)**
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WS_URL=ws://localhost:5000/ws
```

**Backend (.env)**
```env
NODE_ENV=development
PORT=5000
DATABASE_PATH=./database/oncohotspot.db
CORS_ORIGIN=http://localhost:3000
```

### Docker Setup

**Dockerfile (Frontend)**
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

**Dockerfile (Backend)**
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 5000
CMD ["node", "dist/index.js"]
```

**docker-compose.yml**
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:5000/api
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./database:/app/database
    environment:
      - DATABASE_PATH=/app/database/oncohotspot.db

  pipeline:
    build: ./data-processing
    volumes:
      - ./database:/app/database
    command: python pipeline.py
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 PID  # macOS/Linux
taskkill /PID PID /F  # Windows
```

#### Database Locked
```bash
# Check for locks
fuser database/oncohotspot.db

# Remove lock file if exists
rm database/oncohotspot.db-journal
```

#### Module Not Found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
pip install -r requirements.txt --force-reinstall
```

## Resources

### Documentation
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [D3.js Documentation](https://d3js.org/)
- [Express.js Guide](https://expressjs.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Tools
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Redux DevTools](https://github.com/reduxjs/redux-devtools)
- [Postman](https://www.postman.com/)
- [DB Browser for SQLite](https://sqlitebrowser.org/)

### Learning Resources
- [Cancer Genomics](https://www.cancer.gov/about-cancer/causes-prevention/genetics)
- [cBioPortal API](https://www.cbioportal.org/api/swagger-ui.html)
- [HGVS Nomenclature](https://varnomen.hgvs.org/)
- [FDA Approved Drugs](https://www.fda.gov/drugs)