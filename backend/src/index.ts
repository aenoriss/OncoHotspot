import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { errorHandler } from './middleware/errorHandler';
import mutationRoutes from './routes/mutationRoutes';
import geneRoutes from './routes/geneRoutes';
import therapeuticRoutes from './routes/therapeuticRoutes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check with database test
app.get('/health', async (req, res) => {
  const health: any = { 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV,
    port: PORT
  };

  // Test database connection
  try {
    const { Database } = require('./config/database');
    const db = Database.getInstance();
    
    // Try to query the database
    const result = await db.query('SELECT COUNT(*) as count FROM sqlite_master WHERE type="table"');
    health.database = {
      status: 'connected',
      tables: result[0].count,
      path: process.env.DATABASE_PATH || 'default'
    };

    // Get some basic stats if tables exist
    try {
      const geneCount = await db.query('SELECT COUNT(*) as count FROM genes');
      const mutationCount = await db.query('SELECT COUNT(*) as count FROM mutations');
      health.database.stats = {
        genes: geneCount[0].count,
        mutations: mutationCount[0].count
      };
    } catch (e) {
      health.database.stats = { message: 'Tables exist but no data yet' };
    }
  } catch (error: any) {
    health.database = { 
      status: 'error', 
      message: error.message 
    };
    health.status = 'DEGRADED';
  }

  const statusCode = health.status === 'OK' ? 200 : 503;
  res.status(statusCode).json(health);
});

// Detailed database stats endpoint
app.get('/api/health/database', async (req, res) => {
  try {
    const { Database } = require('./config/database');
    const db = Database.getInstance();
    
    // Get all tables
    const tables = await db.query(`
      SELECT name, sql FROM sqlite_master 
      WHERE type='table' 
      ORDER BY name
    `);
    
    const stats: any = { tables: {} };
    
    // Get row count for each table
    for (const table of tables) {
      try {
        const count = await db.query(`SELECT COUNT(*) as count FROM ${table.name}`);
        stats.tables[table.name] = {
          rowCount: count[0].count,
          schema: table.sql
        };
      } catch (e) {
        stats.tables[table.name] = { error: 'Could not query table' };
      }
    }
    
    // Get database file size if possible
    const fs = require('fs');
    const path = require('path');
    const dbPath = process.env.DATABASE_PATH || '/data/oncohotspot.db';
    
    if (fs.existsSync(dbPath)) {
      const fileStats = fs.statSync(dbPath);
      stats.file = {
        path: dbPath,
        size: `${(fileStats.size / 1024 / 1024).toFixed(2)} MB`,
        modified: fileStats.mtime
      };
    }
    
    res.json(stats);
  } catch (error: any) {
    res.status(500).json({ 
      error: 'Database health check failed', 
      message: error.message 
    });
  }
});

// Routes
app.use('/api/mutations', mutationRoutes);
app.use('/api/genes', geneRoutes);
app.use('/api/therapeutics', therapeuticRoutes);

// Error handling middleware
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`🚀 OncoHotspot API server running on port ${PORT}`);
});