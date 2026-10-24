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
    const targetKey = (phone || tc).replace(/\D/g, '');
    globalThis.__otpStorage![targetKey] = { code: otpCode, expiresAt };

    let sentViaBot = false;
    const botUrl = process.env.WHATSAPP_BOT_URL || 'http://localhost:3001';

    try {
      const botRes = await fetch(`${botUrl}/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: targetKey, code: otpCode }),
      });
      if (botRes.ok) {
        sentViaBot = true;
      }
    } catch {
      // Sunucu Vercel'de ise localhost'a erişemez, istemci (tarayıcı) köprüsü devreye girecek
    }

    return NextResponse.json({
      success: true,
      sentViaBot,
      message: 'Doğrulama kodu üretildi.',
      otpCode, // Yerel WhatsApp bot köprüsünün iletmesi için
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const { phone, tc, code } = await request.json();
    const targetKey = (phone || tc).replace(/\D/g, '');
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