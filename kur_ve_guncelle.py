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
    print("🧹 Eski açık işlemler temizleniyor...")
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
    print("   MEB PANSİYON - WHATSAPP BOT VE CANLIYA ALMA SİSTEMİ")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # WhatsApp Bot Kodu (whatsapp-bot.js)
    whatsapp_bot_code = """
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const http = require('http');
const fs = require('fs');

const possiblePaths = [
    'C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe',
    'C:\\\\Program Files (x86)\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe',
    (process.env.LOCALAPPDATA || '') + '\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe',
    'C:\\\\Program Files (x86)\\\\Microsoft\\\\Edge\\\\Application\\\\msedge.exe',
    'C:\\\\Program Files\\\\Microsoft\\\\Edge\\\\Application\\\\msedge.exe'
];

let executablePath = undefined;
for (const path of possiblePaths) {
    if (fs.existsSync(path)) {
        executablePath = path;
        break;
    }
}

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        executablePath: executablePath,
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

let isReady = false;

client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    console.log('\\n✅ [BAŞARILI] WhatsApp Botu Bağlandı ve Mesaj Göndermeye Hazır!\\n');
});

client.on('disconnected', () => {
    isReady = false;
});

client.initialize();

const server = http.createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
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
                    res.end(JSON.stringify({ success: false, message: 'WhatsApp Web henüz hazır değil.' }));
                    return;
                }

                const { phone, code, customMessage } = JSON.parse(body);
                let cleanPhone = (phone || '').replace(/\\D/g, '');
                if (cleanPhone.startsWith('0')) cleanPhone = cleanPhone.substring(1);
                if (!cleanPhone.startsWith('90')) cleanPhone = '90' + cleanPhone;

                let message = customMessage || `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nVeli Giriş Kodunuz: *${code}*`;

                console.log(`⏳ [GÖNDERİLİYOR] Hedef: ${cleanPhone}`);

                let targetChatId = `${cleanPhone}@c.us`;
                if (client.info && client.info.wid && client.info.wid.user === cleanPhone) {
                    targetChatId = client.info.wid._serialized;
                } else {
                    const numberDetails = await client.getNumberId(cleanPhone);
                    if (!numberDetails) {
                        res.writeHead(404, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ success: false, message: `Numara (${cleanPhone}) WhatsApp'ta bulunamadı.` }));
                        return;
                    }
                    targetChatId = numberDetails._serialized;
                }

                await client.sendMessage(targetChatId, message, { sendSeen: false });
                console.log(`✅ [MESAJ İLETİLDİ] -> ${cleanPhone}`);

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, message: 'WhatsApp bildirimi başarıyla gönderildi.' }));
            } catch (err) {
                console.error('❌ Hata:', err.message);
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
    console.log('🚀 [BOT SUNUCUSU] http://localhost:3001 adresinde dinleniyor...');
});
"""
    write_file("whatsapp-bot.js", whatsapp_bot_code)

    # API Rotası (app/api/belletmen/bildirim/route.ts)
    bildirim_api = f"""import {{ NextResponse }} from 'next/server';

const BOT_URLS = ['{tunnel_url}', 'http://127.0.0.1:3001'];

export async function POST(request: Request) {{
  try {{
    const {{ phone, ogrenciAd, odaNo, tarih, seans, veliTipi }} = await request.json();
    if (!phone) {{
      return NextResponse.json({{ success: false, message: 'Telefon numarası eksik.' }}, {{ status: 400 }});
    }}

    const seansMetni = seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)';
    const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz (${{veliTipi || 'Veli'}}),\\nÖğrenciniz *${{ogrenciAd}}* (Oda: ${{odaNo}}), *${{tarih}}* tarihli *${{seansMetni}}* yoklamasında pansiyonda *BULUNAMAMIŞTIR (YOK)*.\\n\\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;

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
            message: `✅ ${{ogrenciAd}} velisine (${{phone}}) WhatsApp bildirimi gönderildi!`
          }});
        }} else {{
          lastError = data.message || lastError;
        }}
      }} catch (e) {{}}
    }}

    return NextResponse.json({{ success: false, message: lastError }}, {{ status: 500 }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}
"""
    write_file("app/api/belletmen/bildirim/route.ts", bildirim_api)

    # WhatsApp Botunu Yeni Pencerede Başlat
    print("\n🚀 WHATSAPP BOT PENCERESİ BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # Derleme & Vercel Push
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Belletmen bildirim API ve guncel arayuz yayina alindi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 HER ŞEY HAZIR VE CANLIYA GÖNDERİLDİ!")
    print("👉 Açılan Chrome'da WhatsApp Web'in yüklenmesini bekleyin.")
    print("👉 Yaklaşık 45 saniye sonra https://pansiyon-yurt-sistemi.vercel.app/belletmen")
    print("   sayfasını yenileyip 'Anneye Mesaj At' butonuna tıklayarak test edebilirsiniz.")
    print("=========================================================")

if __name__ == "__main__":
    main()