import sqlite3 from 'sqlite3';
import path from 'path';

// Use absolute path to the database file
const dbPath = process.env.NODE_ENV === 'production' 
  ? path.resolve(__dirname, '../../../database/oncohotspot.db')
  : path.resolve(__dirname, '../../../database/oncohotspot.db');

// Enable verbose mode for development
const sqlite = process.env.NODE_ENV === 'development' ? sqlite3.verbose() : sqlite3;

export class Database {
  private static instance: Database;
  private db: sqlite3.Database;

  private constructor() {
    this.db = new sqlite.Database(dbPath, (err) => {
      if (err) {
        console.error('Error opening database:', err.message);
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