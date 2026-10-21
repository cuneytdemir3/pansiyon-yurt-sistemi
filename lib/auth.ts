// lib/auth.ts
export function cleanMobileInput(input: string): string {
  if (!input) return '';
  return input
    .replace(/[\u200B-\u200D\uFEFF]/g, '') // Sıfır genişlikli boşluklar
    .replace(/[*_`#]/g, '') // Markdown karakterleri
    .replace(/['"]/g, '') // Tırnaklar
    .replace(/İ/g, 'i').replace(/I/g, 'ı').toLowerCase() // Türkçe karakter normalizasyonu
    .trim();
}

export function verifyUserCredentials(identifier: string, usersList: any[]) {
  const cleanId = cleanMobileInput(identifier);
  return usersList.find(u => 
    cleanMobileInput(u.tc || '') === cleanId ||
    cleanMobileInput(u.username || '') === cleanId ||
    cleanMobileInput(u.phone || '') === cleanId ||
    cleanMobileInput(u.name || '') === cleanId
  );
}