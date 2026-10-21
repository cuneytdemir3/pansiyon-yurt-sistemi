// lib/auth.ts
import { SignJWT, jwtVerify } from 'jose';
import crypto from 'crypto';

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'meb-pansiyon-yurt-takip-gizli-anahtar-2026'
);

export function normalizeTurkishText(input: string): string {
  if (!input) return '';
  return input
    .replace(/İ/g, 'i')
    .replace(/I/g, 'ı')
    .replace(/Ğ/g, 'ğ')
    .replace(/Ü/g, 'ü')
    .replace(/Ş/g, 'ş')
    .replace(/Ö/g, 'ö')
    .replace(/Ç/g, 'ç')
    .toLowerCase()
    .trim();
}

export function cleanMobileInput(input: string): string {
  if (!input) return '';
  return input
    .replace(/[\u200B-\u200D\uFEFF]/g, '') // Sıfır genişlikli boşluklar
    .replace(/[*_`#~]/g, '') // Markdown yıldızları ve işaretleri
    .replace(/['"“”‘’]/g, '') // Tırnak işaretleri
    .replace(/İ/g, 'i')
    .replace(/I/g, 'ı')
    .toLowerCase()
    .trim();
}

export async function signToken(payload: any): Promise<string> {
  return await new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(JWT_SECRET);
}

export async function verifyToken(token: string): Promise<any> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    return payload;
  } catch {
    return null;
  }
}

export function hashPassword(password: string, salt = 'meb_salt_2026'): string {
  return crypto
    .createHash('sha256')
    .update(password + salt)
    .digest('hex');
}

export function verifyUserCredentials(identifier: string, usersList: any[]) {
  const cleanId = cleanMobileInput(identifier);
  return usersList.find(
    (u) =>
      cleanMobileInput(u.tc || '') === cleanId ||
      cleanMobileInput(u.username || '') === cleanId ||
      cleanMobileInput(u.phone || '') === cleanId ||
      cleanMobileInput(u.name || '') === cleanId
  );
}