import os
import subprocess
import sys

def write_file(filepath, content):
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"[DOSYA OLUŞTURULDU / GÜNCELLENDİ] {filepath}")

def append_gitignore():
    gitignore_path = ".gitignore"
    entries = ["\n# WhatsApp Bot Oturum Dosyalari", ".wwebjs_auth/", ".wwebjs_cache/"]
    existing = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing = f.read()
    with open(gitignore_path, "a", encoding="utf-8") as f:
        for entry in entries:
            if entry.strip() not in existing:
                f.write(entry + "\n")
    print("[GÜNCELLENDİ] .gitignore (WhatsApp oturum dosyaları hariç tutuldu)")

def run_command(command, description):
    print(f"\n[İŞLEM] {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[UYARI / HATA] {description} sırasında çıktı:")
        print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        if result.stdout.strip():
            print(result.stdout.strip())
        return True

def main():
    print("=========================================================")
    print("   MEB PANSİYON - WHATSAPP BOT & OTOMATİK KURULUM SİSTEMİ")
    print("=========================================================")

    # 1. WhatsApp Kütüphanelerini Kur
    run_command("npm install whatsapp-web.js qrcode-terminal", "WhatsApp Bot kütüphaneleri kuruluyor")

    # 2. .gitignore Güncellemesi (QR oturumu GitHub'a gitmesin)
    append_gitignore()

    # 3. whatsapp-bot.js Dosyasını Oluştur (CORS destekli, hem yerel hem canlı siteden istek alabilir)
    whatsapp_bot_code = """
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const http = require('http');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

let isReady = false;

client.on('qr', (qr) => {
    console.log('\\n================================================');
    console.log('[!] LÜTFEN AŞAĞIDAKİ QR KODU WHATSAPP İLE OKUTUN:');
    console.log('================================================\\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    console.log('\\n✅ [BAŞARILI] Kişisel WhatsApp Botu bağlandı ve mesaj göndermeye hazır!\\n');
});

client.on('disconnected', () => {
    isReady = false;
    console.log('\\n❌ [UYARI] WhatsApp bağlantısı koptu!\\n');
});

client.initialize();

const server = http.createServer(async (req, res) => {
    // Tarayıcıdan (Vercel veya localhost) doğrudan erişim için CORS izinleri
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    if (req.method === 'POST' && req.url === '/send-otp') {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', async () => {
            try {
                if (!isReady) {
                    res.writeHead(503, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: false, message: 'WhatsApp Botu henüz hazır değil (QR okutulmadı).' }));
                    return;
                }

                const { phone, code } = JSON.parse(body);
                if (!phone || !code) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: false, message: 'Telefon veya kod eksik.' }));
                    return;
                }

                let cleanPhone = phone.replace(/\\D/g, '');
                if (cleanPhone.startsWith('0')) cleanPhone = cleanPhone.substring(1);
                if (!cleanPhone.startsWith('90')) cleanPhone = '90' + cleanPhone;
                const chatId = `${cleanPhone}@c.us`;

                const message = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nVeli Portalı Tek Kullanımlık Giriş Kodunuz: *${code}*\\n\\nBu kod 3 dakika geçerlidir. Güvenliğiniz için kimseyle paylaşmayınız.`;

                await client.sendMessage(chatId, message);
                console.log(`📨 [MESAJ GÖNDERİLDİ] ${cleanPhone} -> Kod: ${code}`);

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, message: 'WhatsApp mesajı başarıyla gönderildi.' }));
            } catch (err) {
                console.error('[HATA] Mesaj gönderilemedi:', err.message);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, message: err.message }));
            }
        });
    } else {
        res.writeHead(404);
        res.end();
    }
});

server.listen(3001, () => {
    console.log('🚀 [SUNUCU] WhatsApp Bot Köprüsü http://localhost:3001 adresinde dinleniyor...');
});
"""
    write_file("whatsapp-bot.js", whatsapp_bot_code)

    # 4. OTP API Rotasını Güncelle (app/api/auth/otp/route.ts)
    otp_api_code = """
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
    const targetKey = (phone || tc).replace(/\\D/g, '');
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
    const targetKey = (phone || tc).replace(/\\D/g, '');
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
"""
    write_file("app/api/auth/otp/route.ts", otp_api_code)

    # 5. Veli Login Sayfasını Güncelle (app/veli/login/page.tsx)
    veli_login_code = """
'use client';

import React, { useState } from 'react';
import { ShieldCheck, Phone, CheckCircle, ArrowRight } from 'lucide-react';

export default function VeliLoginPage() {
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [fallbackHint, setFallbackHint] = useState('');

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.replace(/\\D/g, '').length < 10) {
      setErrorMsg('Lütfen geçerli bir telefon numarası girin (Örn: 0555 111 22 33).');
      return;
    }
    setLoading(true);
    setErrorMsg('');
    setFallbackHint('');

    try {
      const res = await fetch('/api/auth/otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      const data = await res.json();

      if (data.success) {
        let delivered = data.sentViaBot;

        // Eğer sunucu doğrudan bota ulaşamadıysa (Vercel'deyse), bilgisayardaki yerel bota tarayıcıdan istek at
        if (!delivered && data.otpCode) {
          try {
            const localBotRes = await fetch('http://localhost:3001/send-otp', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ phone, code: data.otpCode }),
            });
            const localBotData = await localBotRes.json();
            if (localBotData.success) {
              delivered = true;
            }
          } catch {
            // Yerel bot kapalıysa
          }
        }

        setStep('otp');
        if (delivered) {
          setSuccessMsg('Tek kullanımlık şifreniz WhatsApp numaranıza başarıyla gönderildi!');
        } else {
          setSuccessMsg('Doğrulama kodu oluşturuldu (WhatsApp Botu kapalı olduğu için yedek mod aktif).');
          setFallbackHint(data.otpCode);
        }
      } else {
        setErrorMsg(data.message || 'Kod gönderilemedi.');
      }
    } catch {
      setErrorMsg('Bağlantı hatası oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpCode || otpCode.length !== 6) {
      setErrorMsg('Lütfen 6 haneli kodu eksiksiz girin.');
      return;
    }
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await fetch('/api/auth/otp', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, code: otpCode }),
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('token', data.token);
        document.cookie = `token=${data.token}; path=/; max-age=604800;`;
        window.location.href = '/veli';
      } else {
        setErrorMsg(data.message || 'Doğrulama başarısız.');
      }
    } catch {
      setErrorMsg('Hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 max-w-md w-full p-6 md:p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl mx-auto flex items-center justify-center font-bold">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Veli Portalı WhatsApp Girişi</h1>
          <p className="text-xs md:text-sm text-gray-500">WhatsApp üzerinden gelen tek kullanımlık kod ile şifresiz giriş yapın.</p>
        </div>

        {errorMsg && <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs font-medium">{errorMsg}</div>}
        {successMsg && <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-xs font-medium">{successMsg}</div>}
        {fallbackHint && (
          <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-xs text-center font-mono">
            ⚠️ [Bot Kapalı - Yedek Kod]: <strong>{fallbackHint}</strong>
          </div>
        )}

        {step === 'phone' ? (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">WhatsApp Cep Telefonu Numaranız</label>
              <div className="relative">
                <Phone className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  required
                  placeholder="0555 000 00 00"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-semibold text-sm shadow-sm transition-all cursor-pointer"
            >
              {loading ? 'WhatsApp Mesajı Gönderiliyor...' : 'WhatsApp ile Kod Gönder'} <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">WhatsApp'a Gelen 6 Haneli Kod</label>
              <input
                type="text"
                maxLength={6}
                required
                placeholder="123456"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                className="w-full text-center tracking-widest text-xl font-bold py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-semibold text-sm shadow-sm transition-all cursor-pointer"
            >
              {loading ? 'Doğrulanıyor...' : 'Giriş Yap'} <CheckCircle className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setStep('phone')}
              className="w-full text-center text-xs text-gray-500 hover:text-gray-800 underline pt-2"
            >
              Numarayı değiştir / Kodu tekrar gönder
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
"""
    write_file("app/veli/login/page.tsx", veli_login_code)

    # 6. Build Testi ve GitHub Push
    if not run_command("npm run build", "Next.js üretim derlemesi (build) test ediliyor"):
        print("\n❌ Build hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Otomatik kurulum: Kisisel WhatsApp OTP botu ve koprusu entegre edildi" --allow-empty', "Git commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n🎉 TÜM KURULUM VE GÜNCELLEMELER TAMAMLANDI!")
    print("👉 Şimdi WhatsApp botunu başlatmak için terminalde şu komutu çalıştırın:")
    print("   node whatsapp-bot.js")

if __name__ == "__main__":
    main()