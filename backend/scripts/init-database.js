#!/usr/bin/env node

// Initialize empty database if needed
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = process.env.DATABASE_PATH || 
               (process.env.RAILWAY_VOLUME_MOUNT_PATH ? 
                path.join(process.env.RAILWAY_VOLUME_MOUNT_PATH, 'oncohotspot.db') :
                '/data/oncohotspot.db');

const dbDir = path.dirname(dbPath);

console.log('Checking database at:', dbPath);

// Create directory if it doesn't exist
if (!fs.existsSync(dbDir)) {
  console.log('Creating directory:', dbDir);
  fs.mkdirSync(dbDir, { recursive: true });
}

// Check if database exists
if (!fs.existsSync(dbPath)) {
  console.log('Database not found. Creating empty database at:', dbPath);
  
  const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
      console.error('Error creating database:', err);
      process.exit(1);
    }
    
    console.log('Empty database created successfully');
    
    // Create basic schema
    db.serialize(() => {
      db.run(`CREATE TABLE IF NOT EXISTS genes (
        id INTEGER PRIMARY KEY,
        symbol TEXT UNIQUE NOT NULL,
        name TEXT,
        description TEXT
      )`);
      
      db.run(`CREATE TABLE IF NOT EXISTS mutations (
        id INTEGER PRIMARY KEY,
        gene_id INTEGER,
        cancer_type_id INTEGER,
        frequency REAL
      )`);
      
      console.log('Basic schema created');
    });
    
    db.close();
  });
} else {
  console.log('Database already exists at:', dbPath);
}