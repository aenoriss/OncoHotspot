import sqlite3 from 'sqlite3';
import path from 'path';
import { Pool } from 'pg';

// Try multiple possible database locations
const fs = require('fs');

// Railway provides RAILWAY_VOLUME_MOUNT_PATH for volumes
const volumePath = process.env.RAILWAY_VOLUME_MOUNT_PATH;
const possiblePaths = [
  process.env.DATABASE_PATH,
  volumePath ? path.join(volumePath, 'oncohotspot.db') : null,   // Railway volume mount
  path.resolve(__dirname, '../../database/oncohotspot.db'),      // dist/config -> database
  path.resolve(__dirname, '../database/oncohotspot.db'),         // dist -> database  
  path.resolve(__dirname, '../../../database/oncohotspot.db'),   // src/config -> database
  path.resolve('/app/database/oncohotspot.db'),                  // absolute path in container
  path.resolve('/app/backend/database/oncohotspot.db'),          // alternate absolute path
  path.resolve('/app/backend/dist/database/oncohotspot.db'),     // copied to dist
  path.resolve('./database/oncohotspot.db'),                     // relative to cwd
].filter(Boolean);

// Find the first path that exists
let dbPath: string = '';
for (const p of possiblePaths) {
  if (p && fs.existsSync(p)) {
    dbPath = p;
    console.log('Found database at:', dbPath);
    break;
  }
}

if (!dbPath) {
  console.error('Database not found in any of these locations:', possiblePaths);
  dbPath = possiblePaths.find(p => p) || path.resolve(__dirname, '../../database/oncohotspot.db'); // fallback
}

// Enable verbose mode for development
const sqlite = process.env.NODE_ENV === 'development' ? sqlite3.verbose() : sqlite3;

export class Database {
  private static instance: Database;
  private db: sqlite3.Database;

  private constructor() {
    console.log('Attempting to connect to database at:', dbPath);
    console.log('Current directory:', __dirname);
    console.log('NODE_ENV:', process.env.NODE_ENV);
    console.log('DATABASE_PATH env:', process.env.DATABASE_PATH);
    
    this.db = new sqlite.Database(dbPath, (err) => {
      if (err) {
        console.error('Error opening database:', err.message);
        console.error('Failed path was:', dbPath);
        
        // Check if file exists
        const fs = require('fs');
        if (!fs.existsSync(dbPath)) {
          console.error('Database file does not exist at path:', dbPath);
          console.error('Contents of database directory:');
          const dbDir = path.dirname(dbPath);
          if (fs.existsSync(dbDir)) {
            console.error(fs.readdirSync(dbDir));
          } else {
            console.error('Database directory does not exist:', dbDir);
          }
        }
        throw err;
      }
      console.log('Connected to SQLite database at:', dbPath);
    });

    // Enable foreign keys
    this.db.run('PRAGMA foreign_keys = ON');
  }

  public static getInstance(): Database {
    if (!Database.instance) {
      Database.instance = new Database();
    }
    return Database.instance;
  }

  public getDatabase(): sqlite3.Database {
    return this.db;
  }

  public close(): void {
    this.db.close((err) => {
      if (err) {
        console.error('Error closing database:', err.message);
      } else {
        console.log('Database connection closed.');
      }
    });
  }

  // Helper method to run queries with promises
  public query(sql: string, params: any[] = []): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Helper method to run single queries (INSERT, UPDATE, DELETE)
  public run(sql: string, params: any[] = []): Promise<sqlite3.RunResult> {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(this);
        }
      });
    });
  }

  // Helper method to get a single row
  public get(sql: string, params: any[] = []): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }
}