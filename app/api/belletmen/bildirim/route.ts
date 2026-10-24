import { NextResponse } from 'next/server';

const BOT_URLS = ['https://preventing-maria-lloyd-wheels.trycloudflare.com', 'http://127.0.0.1:3001', 'http://localhost:3001'];

export async function POST(request: Request) {
  try {
    const { phone, ogrenciAd, odaNo, tarih, seans, veliTipi } = await request.json();
    if (!phone) {
      return NextResponse.json({ success: false, message: 'Telefon numarası eksik.' }, { status: 400 });
    }

    let customMessage = '';
    if (seans === 'izin_onay') {
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz,\nÖğrenciniz *${ogrenciAd}* (Oda: ${odaNo}) için *${tarih}* tarihli izin talebiniz (*${veliTipi}*) onaylanmış ve nöbetçi belletmen yoklama sistemine *Otomatik İzinli* olarak işlenmiştir.`;
    } else {
      const seansMetni = seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)';
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${veliTipi || 'Veli'}),\nÖğrenciniz *${ogrenciAd}* (Oda: ${odaNo}), *${tarih}* tarihli *${seansMetni}* yoklamasında pansiyonda *BULUNAMAMIŞTIR (YOK)*.\n\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;
    }

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
            message: `✅ ${ogrenciAd} velisine (${phone}) WhatsApp bildirimi başarıyla gönderildi!`
          });
        } else {
          lastError = data.message || lastError;
        }
      } catch (e) {}
    }

    return NextResponse.json({
      success: false,
      message: lastError,
      customMessage,
      tunnelUrl: 'https://preventing-maria-lloyd-wheels.trycloudflare.com'
    }, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}