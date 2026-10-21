import { NextResponse } from 'next/server';

declare global {
  var __otpStorage: Record<string, { code: string; expiresAt: number }> | undefined;
}

if (!globalThis.__otpStorage) {
  globalThis.__otpStorage = {};
}

export async function POST(request: Request) {
  try {
    const { phone, tc } = await request.json();
    if (!phone && !tc) {
      return NextResponse.json({ success: false, message: 'Lütfen telefon numarası girin.' }, { status: 400 });
    }
    const otpCode = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = Date.now() + 3 * 60 * 1000;
    const targetKey = phone || tc;
    globalThis.__otpStorage![targetKey] = { code: otpCode, expiresAt };

    return NextResponse.json({
      success: true,
      message: 'Doğrulama kodu oluşturuldu.',
      debugCode: otpCode
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const { phone, tc, code } = await request.json();
    const targetKey = phone || tc;
    const record = globalThis.__otpStorage?.[targetKey];

    if (!record || Date.now() > record.expiresAt || record.code !== code) {
      return NextResponse.json({ success: false, message: 'Kod hatalı veya süresi dolmuş.' }, { status: 400 });
    }

    delete globalThis.__otpStorage![targetKey];
    return NextResponse.json({ success: true, message: 'Giriş başarılı.', token: 'veli-otp-token' });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}