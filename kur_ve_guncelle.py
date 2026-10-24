import os
import re
import subprocess
import sys
import time
import urllib.request

def write_file(filepath, content):
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"[DOSYA GÜNCELLENDİ] {filepath}")

def kill_old_processes():
    print("🧹 Açık kalan eski Node.js ve Tünel işlemleri temizleniyor...")
    subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, capture_output=True)
    time.sleep(1)

def ensure_cloudflared():
    exe_name = "cloudflared.exe"
    if not os.path.exists(exe_name):
        print("🌐 Ücretsiz HTTPS Tünel aracı (cloudflared.exe) indiriliyor (Yaklaşık 10-15 sn)...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        urllib.request.urlretrieve(url, exe_name)
        print("✅ cloudflared.exe başarıyla indirildi!")
    return exe_name

def start_tunnel_and_get_url():
    exe_name = ensure_cloudflared()
    log_file = "tunnel.log"
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except:
            pass

    print("🚀 WhatsApp Botu için güvenli HTTPS tüneli açılıyor...")
    # Tüneli arka planda başlat ve çıktıyı tunnel.log dosyasına yaz
    os.system(f'start "CLOUDFLARE_HTTPS_TUNELI" /MIN cmd /c "{exe_name} tunnel --url http://127.0.0.1:3001 > {log_file} 2>&1"')

    tunnel_url = None
    for _ in range(30):
        time.sleep(1)
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", text)
                if match:
                    tunnel_url = match.group(0)
                    break

    return tunnel_url

def run_command(command, description):
    print(f"\n[İŞLEM] {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[UYARI] {description}:")
        print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

def main():
    print("=========================================================")
    print("   MEB PANSİYON - CANLI (VERCEL) WHATSAPP BOT KÖPRÜSÜ")
    print("=========================================================")

    kill_old_processes()

    # 1. Güvenli HTTPS Tünelini Başlat ve Adresi Al
    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        print("❌ Tünel adresi alınamadı! İnternet bağlantınızı kontrol edin.")
        sys.exit(1)

    print(f"\n🌍 [CANLI TÜNEL ADRESİ OLUŞTURULDU]: {tunnel_url}\n")

    # 2. .gitignore içine cloudflared.exe ve tunnel.log ekle (GitHub'a büyük exe gitmesin)
    gitignore_path = ".gitignore"
    existing_ignore = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing_ignore = f.read()
    with open(gitignore_path, "a", encoding="utf-8") as f:
        for item in ["cloudflared.exe", "tunnel.log", ".wwebjs_auth/", ".wwebjs_cache/"]:
            if item not in existing_ignore:
                f.write(f"\n{item}")

    # 3. OTP API Rotasını Canlı Tünel Adresiyle Güncelle
    otp_api_code = f"""
import {{ NextResponse }} from 'next/server';

declare global {{
  var __otpStorage: Record<string, {{ code: string; expiresAt: number }}> | undefined;
}}

if (!globalThis.__otpStorage) {{
  globalThis.__otpStorage = {{}};
}}

const PUBLIC_BOT_URL = process.env.WHATSAPP_BOT_URL || '{tunnel_url}';

export async function POST(request: Request) {{
  try {{
    const {{ phone, tc }} = await request.json();
    if (!phone && !tc) {{
      return NextResponse.json({{ success: false, message: 'Lütfen telefon numarası girin.' }}, {{ status: 400 }});
    }}

    const otpCode = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = Date.now() + 3 * 60 * 1000;
    let targetKey = (phone || tc).replace(/\\D/g, '');
    if (targetKey.startsWith('0')) targetKey = targetKey.substring(1);

    globalThis.__otpStorage![targetKey] = {{ code: otpCode, expiresAt }};

    let sentViaBot = false;
    let botError = '';

    // Önce Canlı HTTPS Tünelinden (Vercel -> Bilgisayarınızdaki Bot) göndermeyi dene
    const urlsToTry = [PUBLIC_BOT_URL, 'http://127.0.0.1:3001'];

    for (const baseUrl of urlsToTry) {{
      if (!baseUrl) continue;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000);
      try {{
        const botRes = await fetch(`${{baseUrl}}/send-otp`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ phone: targetKey, code: otpCode }}),
          signal: controller.signal,
        }});
        clearTimeout(timeoutId);
        const botData = await botRes.json();
        if (botRes.ok && botData.success) {{
          sentViaBot = true;
          break;
        }} else {{
          botError = botData.message || 'Bot yanıt vermedi.';
        }}
      }} catch {{
        clearTimeout(timeoutId);
      }}
    }}

    return NextResponse.json({{
      success: true,
      sentViaBot,
      botError,
      otpCode,
      tunnelUrl: PUBLIC_BOT_URL
    }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}

export async function PUT(request: Request) {{
  try {{
    const {{ phone, tc, code }} = await request.json();
    let targetKey = (phone || tc).replace(/\\D/g, '');
    if (targetKey.startsWith('0')) targetKey = targetKey.substring(1);

    const record = globalThis.__otpStorage?.[targetKey];

    if (!record || Date.now() > record.expiresAt || record.code !== code.trim()) {{
      return NextResponse.json({{ success: false, message: 'Kod hatalı veya süresi dolmuş.' }}, {{ status: 400 }});
    }}

    delete globalThis.__otpStorage![targetKey];
    return NextResponse.json({{ success: true, message: 'Giriş başarılı.', token: 'veli-otp-token' }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}
"""
    write_file("app/api/auth/otp/route.ts", otp_api_code)

    # 4. Veli Login Sayfasını Güncelle (Hem Tünel hem Localhost Destekli, Ekranda Yedek Kod Göstermeyen Temiz Mod)
    veli_login_code = f"""
'use client';

import React, {{ useState }} from 'react';
import {{ ShieldCheck, Phone, CheckCircle, ArrowRight }} from 'lucide-react';

const TUNNEL_URL = '{tunnel_url}';

export default function VeliLoginPage() {{
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleRequestOtp = async (e: React.FormEvent) => {{
    e.preventDefault();
    if (!phone || phone.replace(/\\D/g, '').length < 10) {{
      setErrorMsg('Lütfen geçerli bir telefon numarası girin (Örn: 0541 657 14 69).');
      return;
    }}
    setLoading(true);
    setErrorMsg('');

    try {{
      const res = await fetch('/api/auth/otp', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ phone }}),
      }});
      const data = await res.json();

      if (data.success) {{
        let delivered = data.sentViaBot;

        // Sunucu ulaşamadıysa tarayıcıdan HTTPS Tünel adresine istek at
        if (!delivered && data.otpCode) {{
          for (const url of [TUNNEL_URL, 'http://localhost:3001']) {{
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 6000);
            try {{
              const botRes = await fetch(`${{url}}/send-otp`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ phone, code: data.otpCode }}),
                signal: controller.signal,
              }});
              clearTimeout(tid);
              const botData = await botRes.json();
              if (botData.success) {{
                delivered = true;
                break;
              }}
            }} catch {{
              clearTimeout(tid);
            }}
          }}
        }}

        if (delivered) {{
          setStep('otp');
          setSuccessMsg('Tek kullanımlık şifreniz WhatsApp numaranıza başarıyla gönderildi!');
        }} else {{
          setErrorMsg('WhatsApp Botuna ulaşılamadı. Lütfen bilgisayarda WhatsApp Bot penceresinin açık olduğundan emin olun.');
        }}
      }} else {{
        setErrorMsg(data.message || 'Kod gönderilemedi.');
      }}
    }} catch {{
      setErrorMsg('Sunucu bağlantı hatası oluştu.');
    }} finally {{
      setLoading(false);
    }}
  }};

  const handleVerifyOtp = async (e: React.FormEvent) => {{
    e.preventDefault();
    if (!otpCode || otpCode.trim().length !== 6) {{
      setErrorMsg('Lütfen WhatsApp’a gelen 6 haneli kodu eksiksiz girin.');
      return;
    }}
    setLoading(true);
    setErrorMsg('');
    try {{
      const res = await fetch('/api/auth/otp', {{
        method: 'PUT',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ phone, code: otpCode }}),
      }});
      const data = await res.json();
      if (data.success) {{
        localStorage.setItem('token', data.token);
        document.cookie = `token=${{data.token}}; path=/; max-age=604800;`;
        window.location.href = '/veli';
      }} else {{
        setErrorMsg(data.message || 'Girdiğiniz kod hatalı veya süresi dolmuş.');
      }}
    }} catch {{
      setErrorMsg('Doğrulama sırasında hata oluştu.');
    }} finally {{
      setLoading(false);
    }}
  }};

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

        {{errorMsg && <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs font-medium">{{errorMsg}}</div>}}
        {{successMsg && <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-xs font-medium">{{successMsg}}</div>}}

        {{step === 'phone' ? (
          <form onSubmit={{handleRequestOtp}} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">WhatsApp Cep Telefonu Numaranız</label>
              <div className="relative">
                <Phone className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  required
                  placeholder="0555 000 00 00"
                  value={{phone}}
                  onChange={{(e) => setPhone(e.target.value)}}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={{loading}}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-semibold text-sm shadow-sm transition-all cursor-pointer"
            >
              {{loading ? 'WhatsApp Mesajı Gönderiliyor...' : 'WhatsApp ile Kod Gönder'}} <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          <form onSubmit={{handleVerifyOtp}} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">WhatsApp'a Gelen 6 Haneli Kod</label>
              <input
                type="text"
                maxLength={{6}}
                required
                placeholder="123456"
                value={{otpCode}}
                onChange={{(e) => setOtpCode(e.target.value)}}
                className="w-full text-center tracking-widest text-xl font-bold py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <button
              type="submit"
              disabled={{loading}}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-semibold text-sm shadow-sm transition-all cursor-pointer"
            >
              {{loading ? 'Doğrulanıyor...' : 'Giriş Yap'}} <CheckCircle className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={{() => setStep('phone')}}
              className="w-full text-center text-xs text-gray-500 hover:text-gray-800 underline pt-2"
            >
              Numarayı değiştir / Kodu tekrar gönder
            </button>
          </form>
        )}}
      </div>
    </div>
  );
}}
"""
    write_file("app/veli/login/page.tsx", veli_login_code)

    # 5. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 6. GitHub ve Vercel'e Gönder
    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command(f'git commit -m "Canli WhatsApp HTTPS Tunel baglantisi ({tunnel_url}) eklendi" --allow-empty', "Git commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor (Canlıya alınıyor)")

    print("\n=========================================================")
    print("🎉 TEBRİKLER! SİSTEM CANLIYA (ONLINE) BAĞLANDI!")
    print(f"🌍 Aktif HTTPS Tüneliniz: {tunnel_url}")
    print("👉 1. Açılan Chrome penceresinde WhatsApp Web'in yüklenmesini bekleyin.")
    print("👉 2. Vercel derlemesi bittiğinde (yaklaşık 45 saniye sonra) doğrudan")
    print("      https://pansiyon-yurt-sistemi.vercel.app/veli/login")
    print("      adresinden (veya cep telefonunuzdan) giriş yapabilirsiniz!")
    print("=========================================================")

if __name__ == "__main__":
    main()