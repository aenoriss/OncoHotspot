import { Pool } from 'pg';

// For Railway PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

export class Database {
  private static instance: Database;

  private constructor() {
    console.log('Connected to PostgreSQL database');
  }

  public static getInstance(): Database {
    if (!Database.instance) {
      Database.instance = new Database();
    }
    return Database.instance;
  }

  public async query(sql: string, params: any[] = []): Promise<any[]> {
    const result = await pool.query(sql, params);
    return result.rows;
  }

  public async run(sql: string, params: any[] = []): Promise<any> {
    const result = await pool.query(sql, params);
    return { lastID: result.rows[0]?.id, changes: result.rowCount };
  }

  public async get(sql: string, params: any[] = []): Promise<any> {
    const result = await pool.query(sql, params);
    return result.rows[0];
  }

  public close(): void {
    pool.end();
  }
}