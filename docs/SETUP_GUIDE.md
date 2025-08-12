# OncoHotspot Setup Guide

## Overview
OncoHotspot is a cancer mutation heatmap platform for identifying therapeutic targets in oncogenes. This guide will walk you through setting up the development environment.

## Prerequisites

### System Requirements
- Node.js (v16 or higher)
- npm or yarn
- MySQL/PostgreSQL database
- Python 3.8+ (for data processing scripts)
- Git

### Development Tools
- Visual Studio Code (recommended)
- MySQL Workbench or similar database client
- Postman or similar API testing tool

## Project Structure

```
oncohotspot/
├── frontend/          # React.js frontend application
├── backend/           # Node.js API server
├── data-processing/   # Python data processing scripts
├── database/          # Database schemas and migrations
├── docs/              # Documentation
└── README.md
```

## Installation Steps

### 1. Clone and Setup

```bash
cd oncohotspot
```

### 2. Database Setup

#### Create Database
```bash
# Start MySQL service
sudo service mysql start

# Connect to MySQL
mysql -u root -p

# Create database
source database/schemas/oncohotspot_schema.sql

# Load sample data
source database/seeds/sample_data.sql
```

#### Environment Configuration
Create `.env` files in both frontend and backend directories:

**Backend `.env`:**
```env
NODE_ENV=development
PORT=3001
DB_HOST=localhost
DB_PORT=3306
DB_NAME=oncohotspot
DB_USER=your_username
DB_PASSWORD=your_password
JWT_SECRET=your_jwt_secret_key
CORS_ORIGIN=http://localhost:3000
```

**Frontend `.env`:**
```env
REACT_APP_API_URL=http://localhost:3001/api
REACT_APP_WS_URL=http://localhost:3001
```

### 3. Backend Setup

```bash
cd backend
npm install
npm run build
npm run dev
```

The backend server will start on http://localhost:3001

### 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend application will start on http://localhost:3000

### 5. Data Processing Setup (Optional)

```bash
cd data-processing
pip install -r requirements.txt
```

## API Endpoints

### Mutations
- `GET /api/mutations` - Get all mutations with filters
- `GET /api/mutations/gene/:geneName` - Get mutations for specific gene
- `GET /api/mutations/stats` - Get mutation statistics

### Genes
- `GET /api/genes` - Get all oncogenes
- `GET /api/genes/search?q=term` - Search genes

### Therapeutics
- `GET /api/therapeutics` - Get all therapeutic targets
- `GET /api/therapeutics/gene/:geneName` - Get therapeutics for gene

## Development Workflow

### Running Tests
```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

### Database Migrations
```bash
# Apply new migrations
mysql -u root -p oncohotspot < database/migrations/new_migration.sql
```

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes
3. Run tests: `npm test`
4. Commit changes: `git commit -m "Add new feature"`
5. Create pull request

## Production Deployment

### Environment Variables
Update production environment variables:
- Set `NODE_ENV=production`
- Configure production database credentials
- Set secure JWT secret
- Configure CORS for production domain

### Build Process
```bash
# Build frontend
cd frontend
npm run build

# Build backend
cd backend
npm run build
```

### Database Setup
```bash
# Run migrations on production database
mysql -u prod_user -p oncohotspot_prod < database/migrations/001_initial_schema.sql
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **CORS Issues**
   - Verify `CORS_ORIGIN` in backend `.env`
   - Check frontend API URL configuration

3. **Port Already in Use**
   - Change port in `.env` file
   - Kill existing processes: `lsof -ti:3001 | xargs kill -9`

4. **Dependencies Issues**
   - Clear node modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

### Logs and Debugging

- Backend logs: Check console output when running `npm run dev`
- Frontend logs: Open browser developer tools
- Database logs: Check MySQL error logs

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## Support

For issues and questions:
- Create GitHub issue
- Check documentation in `/docs`
- Review API documentation