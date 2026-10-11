import { jwtVerify, SignJWT } from 'jose';

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'meb-pansiyon-secret-key-2026-secure-hash'
);

export async function signToken(payload: any) {
  return await new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(JWT_SECRET);
}

export async function verifyToken(token: string) {
  try {
    const verified = await jwtVerify(token, JWT_SECRET);
    return verified.payload;
  } catch (err) {
    return null;
  }
}

// Mobil Girdi Temizleyici (Zero-width space, markdown, Turkish casing)
export function cleanMobileInput(input: string): string {
  if (!input) return '';
  return input
    .replace(/[\u200B-\u200D\uFEFF]/g, '')
    .replace(/[*_`]/g, '')
    .trim()
    .toLocaleLowerCase('tr-TR');
}