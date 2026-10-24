import { NextResponse } from 'next/server';

declare global {
  var __otpStorage: Record<string, { code: string; expiresAt: number }> | undefined;
}

if (!globalThis.__otpStorage) {
  globalThis.__otpStorage = {};
}

const PUBLIC_BOT_URL = process.env.WHATSAPP_BOT_URL || 'https://envelope-deserve-unknown-answered.trycloudflare.com';

export async function POST(request: Request) {
  try {
    const { phone, tc } = await request.json();
    if (!phone && !tc) {
      return NextResponse.json({ success: false, message: 'Lütfen telefon numarası girin.' }, { status: 400 });
    }

    const otpCode = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = Date.now() + 3 * 60 * 1000;
    let targetKey = (phone || tc).replace(/\D/g, '');
    if (targetKey.startsWith('0')) targetKey = targetKey.substring(1);

    globalThis.__otpStorage![targetKey] = { code: otpCode, expiresAt };

    let sentViaBot = false;
    let botError = '';

    // Önce Canlı HTTPS Tünelinden (Vercel -> Bilgisayarınızdaki Bot) göndermeyi dene
    const urlsToTry = [PUBLIC_BOT_URL, 'http://127.0.0.1:3001'];

    for (const baseUrl of urlsToTry) {
      if (!baseUrl) continue;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000);
      try {
        const botRes = await fetch(`${baseUrl}/send-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: targetKey, code: otpCode }),
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
        const botData = await botRes.json();
        if (botRes.ok && botData.success) {
          sentViaBot = true;
          break;
        } else {
          botError = botData.message || 'Bot yanıt vermedi.';
        }
      } catch {
        clearTimeout(timeoutId);
      }
    }

    return NextResponse.json({
      success: true,
      sentViaBot,
      botError,
      otpCode,
      tunnelUrl: PUBLIC_BOT_URL
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const { phone, tc, code } = await request.json();
    let targetKey = (phone || tc).replace(/\D/g, '');
    if (targetKey.startsWith('0')) targetKey = targetKey.substring(1);

    const record = globalThis.__otpStorage?.[targetKey];

    if (!record || Date.now() > record.expiresAt || record.code !== code.trim()) {
      return NextResponse.json({ success: false, message: 'Kod hatalı veya süresi dolmuş.' }, { status: 400 });
    }

    delete globalThis.__otpStorage![targetKey];
    return NextResponse.json({ success: true, message: 'Giriş başarılı.', token: 'veli-otp-token' });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}