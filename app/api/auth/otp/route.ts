// app/api/auth/otp/route.ts
import { NextResponse } from 'next/server';

// Bellek tabanlı geçici OTP saklama (Gerçek projede Redis veya PostgreSQL kullanılabilir)
declare global {
  // eslint-disable-next-line no-var
  var __otpStorage: Record<string, { code: string; expiresAt: number }> | undefined;
}

if (!globalThis.__otpStorage) {
  globalThis.__otpStorage = {};
}

// 1. Aşama: Kod Gönder (WhatsApp üzerinden)
export async function POST(request: Request) {
  try {
    const { phone, tc } = await request.json();

    if (!phone && !tc) {
      return NextResponse.json({ success: false, message: 'Lütfen T.C. Kimlik veya Telefon numarası girin.' }, { status: 400 });
    }

    // 6 haneli rastgele tek kullanımlık kod üret
    const otpCode = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = Date.now() + 3 * 60 * 1000; // 3 dakika geçerli

    const targetKey = phone || tc;
    globalThis.__otpStorage![targetKey] = { code: otpCode, expiresAt };

    // WhatsApp API Bağlantısı (Evolution API, Twilio veya Meta Cloud API ile entegre edilebilir)
    // Şimdilik veliye doğrudan açılacak bir WhatsApp Web URL köprüsü veya otomatik tetikleyici hazırlıyoruz.
    const message = `Prof. Dr. Mümtaz Turhan SBL Pansiyon Sistemi Tek Kullanımlık Giriş Kodunuz: *${otpCode}*. Bu kod 3 dakika geçerlidir. Lütfen kimseyle paylaşmayın.`;
    
    // Eğer telefon numarası verilmişse direkt WhatsApp linki döndürülür
    const cleanPhone = phone ? phone.replace(/\D/g, '') : '905550000000';
    const whatsappUrl = `https://wa.me/9${cleanPhone}?text=${encodeURIComponent(message)}`;

    return NextResponse.json({
      success: true,
      message: 'Doğrulama kodu oluşturuldu.',
      whatsappUrl, // Velinin WhatsApp'ına yönlendirmek veya otomatik tetiklemek için
      debugCode: otpCode // Test kolaylığı için
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Bilinmeyen hata';
    return NextResponse.json({ success: false, message }, { status: 500 });
  }
}

// 2. Aşama: Kodu Doğrula ve Oturum Aç
export async function PUT(request: Request) {
  try {
    const { phone, tc, code } = await request.json();
    const targetKey = phone || tc;

    const record = globalThis.__otpStorage?.[targetKey];

    if (!record) {
      return NextResponse.json({ success: false, message: 'Önce doğrulama kodu talep etmelisiniz.' }, { status: 400 });
    }

    if (Date.now() > record.expiresAt) {
      return NextResponse.json({ success: false, message: 'Doğrulama kodunun süresi dolmuş. Lütfen yeni kod isteyin.' }, { status: 400 });
    }

    if (record.code !== code) {
      return NextResponse.json({ success: false, message: 'Girdiğiniz kod hatalı. Lütfen kontrol edin.' }, { status: 400 });
    }

    // Kod doğru! Kaydı temizle ve başarılı yanıt dön
    delete globalThis.__otpStorage![targetKey];

    return NextResponse.json({
      success: true,
      message: 'Giriş başarılı.',
      token: 'veli-otp-verified-token-2026'
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Bilinmeyen hata';
    return NextResponse.json({ success: false, message }, { status: 500 });
  }
}