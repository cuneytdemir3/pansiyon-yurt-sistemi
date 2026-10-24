import { NextResponse } from 'next/server';

const BOT_URLS = ['https://cookies-dos-enough-nirvana.trycloudflare.com', 'http://127.0.0.1:3001'];

export async function POST(request: Request) {
  try {
    const { ogrenciler, seans } = await request.json();
    if (!Array.isArray(ogrenciler) || ogrenciler.length === 0) {
      return NextResponse.json({ success: false, message: 'Bildirilecek öğrenci bulunamadı.' }, { status: 400 });
    }

    const seansAdi = seans === 'etut' ? '19:15 Etüt' : '23:00 Yat';
    let basarili = 0;
    let basarisiz = 0;

    for (const ogr of ogrenciler) {
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz, öğrenciniz *${ogr.adSoyad}* (Oda: ${ogr.odaNo}) pansiyonumuzun bu akşamki *${seansAdi}* yoklamasında bulunamamıştır.\n\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;

      let gonderildi = false;
      for (const botUrl of BOT_URLS) {
        try {
          const controller = new AbortController();
          const tid = setTimeout(() => controller.abort(), 7000);

          const res = await fetch(`${botUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              phone: ogr.veliTelefon,
              customMessage: customMessage
            }),
            signal: controller.signal
          });
          clearTimeout(tid);

          const data = await res.json();
          if (res.ok && data.success) {
            gonderildi = true;
            break;
          }
        } catch (e) {}
      }

      if (gonderildi) basarili++;
      else basarisiz++;
    }

    return NextResponse.json({
      success: true,
      message: `${basarili} veliye WhatsApp bildirimi başarıyla iletildi.${basarisiz > 0 ? ` (${basarisiz} veliye ulaşılamadı)` : ''}`,
      basarili,
      basarisiz
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}