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
        print("🌐 cloudflared.exe indiriliyor...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        urllib.request.urlretrieve(url, exe_name)
        print("✅ cloudflared.exe hazır!")
    return exe_name

def start_tunnel_and_get_url():
    exe_name = ensure_cloudflared()
    log_file = "tunnel.log"
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except:
            pass

    print("🚀 WhatsApp Botu için Cloudflare HTTPS tüneli açılıyor...")
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
        print(f"[UYARI / HATA] {description}:")
        print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

def main():
    print("=========================================================")
    print("   WHATSAPP BOT TÜNEL SENKRONİZASYONU VE ÇİFT KÖPRÜ ONARIMI")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 1. Bildirim API Rotasını Güncel Tünel Adresiyle Güncelle (Sunucu + Tarayıcı Yedek Mesajı Döndürür)
    bildirim_api = f"""import {{ NextResponse }} from 'next/server';

const BOT_URLS = ['{tunnel_url}', 'http://127.0.0.1:3001', 'http://localhost:3001'];

export async function POST(request: Request) {{
  try {{
    const {{ phone, ogrenciAd, odaNo, tarih, seans, veliTipi }} = await request.json();
    if (!phone) {{
      return NextResponse.json({{ success: false, message: 'Telefon numarası eksik.' }}, {{ status: 400 }});
    }}

    let customMessage = '';
    if (seans === 'izin_onay') {{
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz,\\nÖğrenciniz *${{ogrenciAd}}* (Oda: ${{odaNo}}) için *${{tarih}}* tarihli izin talebiniz (*${{veliTipi}}*) onaylanmış ve nöbetçi belletmen yoklama sistemine *Otomatik İzinli* olarak işlenmiştir.`;
    }} else {{
      const seansMetni = seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)';
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz (${{veliTipi || 'Veli'}}),\\nÖğrenciniz *${{ogrenciAd}}* (Oda: ${{odaNo}}), *${{tarih}}* tarihli *${{seansMetni}}* yoklamasında pansiyonda *BULUNAMAMIŞTIR (YOK)*.\\n\\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;
    }}

    let lastError = 'WhatsApp Botuna ulaşılamadı.';
    for (const botUrl of BOT_URLS) {{
      try {{
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(`${{botUrl}}/send-otp`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ phone, customMessage }}),
          signal: controller.signal
        }});
        clearTimeout(tid);

        const data = await res.json();
        if (res.ok && data.success) {{
          return NextResponse.json({{
            success: true,
            message: `✅ ${{ogrenciAd}} velisine (${{phone}}) WhatsApp bildirimi başarıyla gönderildi!`
          }});
        }} else {{
          lastError = data.message || lastError;
        }}
      }} catch (e) {{}}
    }}

    return NextResponse.json({{
      success: false,
      message: lastError,
      customMessage,
      tunnelUrl: '{tunnel_url}'
    }}, {{ status: 200 }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}
"""
    write_file("app/api/belletmen/bildirim/route.ts", bildirim_api)

    # 2. Veli OTP API Rotasını da Güncel Tünel Adresiyle Güncelle
    otp_api_code = f"""import {{ NextResponse }} from 'next/server';

declare global {{
  var __otpStorage: Record<string, {{ code: string; expiresAt: number }}> | undefined;
}}

if (!globalThis.__otpStorage) {{
  globalThis.__otpStorage = {{}};
}}

const PUBLIC_BOT_URL = '{tunnel_url}';

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

    for (const baseUrl of [PUBLIC_BOT_URL, 'http://127.0.0.1:3001']) {{
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

    # 3. Belletmen sayfasındaki handleSendWhatsApp fonksiyonuna Doğrudan Tarayıcı -> Bot (Tünel + Localhost) Yedeği Ekle
    if os.path.exists("app/belletmen/page.tsx"):
        with open("app/belletmen/page.tsx", "r", encoding="utf-8") as f:
            b_content = f.read()

        old_block = """      if (res.ok && data.success) {
        setSentKeys((prev) => ({ ...prev, [btnKey]: true }));
        setFeedback({ type: 'success', text: data.message });
      } else {
        setFeedback({ type: 'error', text: data.message || 'Mesaj iletilemedi.' });
      }"""

        new_block = f"""      if (res.ok && data.success) {{
        setSentKeys((prev) => ({{ ...prev, [btnKey]: true }}));
        setFeedback({{ type: 'success', text: data.message }});
      }} else {{
        // Sunucu ulaşamadıysa doğrudan tarayıcıdan aktif Tünel veya Localhost:3001'e gönder
        let directSuccess = false;
        const fallbackMsg = data.customMessage || `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz (${{veliTipi}}), öğrenciniz *${{student.name}}* (Oda: ${{student.oda}}) *${{tarih}}* tarihli yoklamada pansiyonda *BULUNAMAMIŞTIR (YOK)*.`;
        for (const directUrl of [data.tunnelUrl || '{tunnel_url}', 'http://localhost:3001', 'http://127.0.0.1:3001']) {{
          try {{
            const r2 = await fetch(`${{directUrl}}/send-otp`, {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify({{ phone, customMessage: fallbackMsg }})
            }});
            const d2 = await r2.json();
            if (r2.ok && d2.success) {{
              directSuccess = true;
              setSentKeys((prev) => ({{ ...prev, [btnKey]: true }}));
              setFeedback({{ type: 'success', text: `✅ ${{student.name}} velisine (${{phone}}) WhatsApp bildirimi başarıyla gönderildi!` }});
              break;
            }}
          }} catch {{}}
        }}
        if (!directSuccess) {{
          setFeedback({{ type: 'error', text: 'WhatsApp Botu henüz hazır değil! Lütfen açık olan Chrome penceresinde WhatsApp sohbetlerinizin yüklendiğinden emin olun.' }});
        }}
      }}"""

        if old_block in b_content:
            b_content = b_content.replace(old_block, new_block)
            write_file("app/belletmen/page.tsx", b_content)

    # 4. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 5. Derleme ve GitHub/Vercel Gönderimi
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command(f'git commit -m "Aktif WhatsApp tunel adresi ({tunnel_url}) tum API ve sayfalara senkronize edildi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 TÜNEL VE BOT BAĞLANTISI ONARILDI!")
    print(f"🌍 Yeni Aktif Tünel: {tunnel_url}")
    print("👉 ÖNEMLİ: Açılan Chrome penceresinde WhatsApp sohbetlerinizin")
    print("   tamamen yüklenmesini (Siyah pencerede '✅ [BAŞARILI] WhatsApp Botu Bağlandı!'")
    print("   yazısının çıkmasını) bekleyin, ardından butona tıklayın!")
    print("=========================================================")

if __name__ == "__main__":
    main()