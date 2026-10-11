import { Pool } from 'pg';
import fs from 'fs';
import path from 'path';

// Neon PostgreSQL Bağlantı Havuzu
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL ? { rejectUnauthorized: false } : false,
});

const DATA_DIR = path.join(process.cwd(), 'data');

export async function query(text: string, params?: any[]) {
  if (!process.env.DATABASE_URL) {
    throw new Error('DATABASE_URL not configured');
  }
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
}

// Fallback JSON Fonksiyonları (Lokal geliştirme ve kesinti koruması için)
export function loadFallbackData(filename: string) {
  try {
    const filePath = path.join(DATA_DIR, filename);
    if (fs.existsSync(filePath)) {
      const fileData = fs.readFileSync(filePath, 'utf-8');
      return JSON.parse(fileData);
    }
  } catch (e) {
    console.error('Fallback read error:', e);
  }
  return [];
}

export function saveFallbackData(filename: string, data: any) {
  try {
    const filePath = path.join(DATA_DIR, filename);
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (e) {
    console.error('Fallback write error:', e);
    return false;
  }
}
