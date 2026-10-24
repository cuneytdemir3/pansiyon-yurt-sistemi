import { NextResponse } from 'next/server';

const BOT_URLS = ['https://beginning-wine-mode-empirical.trycloudflare.com', 'http://127.0.0.1:3001'];

export async function POST(request: Request) {
  try {
    const { phone, ogrenciAd, odaNo, tarih, seans, veliTipi } = await request.json();
    if (!phone) {
      return NextResponse.json({ success: false, message: 'Telefon numarası eksik.' }, { status: 400 });
    }

    const seansMetni = seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)';
    const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${veliTipi || 'Veli'}),\nÖğrenciniz *${ogrenciAd}* (Oda: ${odaNo}), *${tarih}* tarihli *${seansMetni}* yoklamasında pansiyonda *BULUNAMAMIŞTIR (YOK)*.\n\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;

    let lastError = 'WhatsApp Botuna ulaşılamadı.';
    for (const botUrl of BOT_URLS) {
      try {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(`${botUrl}/send-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone, customMessage }),
          signal: controller.signal
        });
        clearTimeout(tid);

        const data = await res.json();
        if (res.ok && data.success) {
          return NextResponse.json({
            success: true,
            message: `✅ ${ogrenciAd} velisine (${phone}) WhatsApp bildirimi gönderildi!`
          });
        } else {
          lastError = data.message || lastError;
        }
      } catch (e) {}
    }

    return NextResponse.json({ success: false, message: lastError }, { status: 500 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}