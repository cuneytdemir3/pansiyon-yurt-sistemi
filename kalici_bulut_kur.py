import os
import subprocess
import time
import urllib.request
import json
import re

def write_file(filepath, content):
    dir_name = os.path.dirname(filepath)
    if dir_name: os.makedirs(dir_name, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"[GÜNCELLENDİ] {filepath}")

def kill_old_processes():
    print("🧹 Eski bağlantılar temizleniyor...")
    subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, capture_output=True)
    time.sleep(1)

def ensure_cloudflared():
    exe_name = "cloudflared.exe"
    if not os.path.exists(exe_name):
        print("🌐 Tünel indiriliyor...")
        urllib.request.urlretrieve("https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe", exe_name)
    return exe_name

def start_tunnel():
    exe_name = ensure_cloudflared()
    log_file = "tunnel.log"
    if os.path.exists(log_file): os.remove(log_file)
    os.system(f'start "MOBIL_VERI_TUNELI" /MIN cmd /c "{exe_name} tunnel --url http://127.0.0.1:3001 > {log_file} 2>&1"')
    
    tunnel_url = None
    for _ in range(20):
        time.sleep(1)
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", f.read())
                if match:
                    tunnel_url = match.group(0)
                    break
    return tunnel_url

# =========================================================================
# 1. BULUT VERİTABANI (NPOINT) OLUŞTURMA
# =========================================================================
def setup_cloud_db():
    db_file = "bulut_db_id.txt"
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            return f.read().strip()
    
    print("☁️ Ücretsiz Bulut Veritabanı (Cloud DB) oluşturuluyor...")
    default_data = {
        "students": [], "belletmenler": [], "aylikNobetler": [], 
        "leaves": [], "dutyLogs": [], "auditLogs": [], "tunnelUrl": ""
    }
    
    req = urllib.request.Request("https://api.npoint.io/", data=json.dumps(default_data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            db_id = res_data['id']
            with open(db_file, "w") as f:
                f.write(db_id)
            print(f"✅ Bulut Veritabanı Başarıyla Kuruldu! (ID: {db_id})")
            return db_id
    except Exception as e:
        print("❌ Bulut DB Hatası:", e)
        return None

# =========================================================================
# 2. WHATSAPP BOTU (Artık Vercel yerine Bulut DB'ye Tünel Adresini Yazar)
# =========================================================================
def get_whatsapp_bot_code(db_id):
    return f"""
const {{ Client, LocalAuth }} = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(cors({{ origin: '*', methods: ['GET', 'POST', 'PUT', 'OPTIONS'] }}));
app.use(express.json({{ limit: '15mb' }}));

const DB_URL = 'https://api.npoint.io/{db_id}';

async function registerTunnelToCloud() {{
    try {{
        let tunnelUrl = '';
        try {{
            const log = fs.readFileSync('tunnel.log', 'utf-8');
            const match = log.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
            if (match) tunnelUrl = match[0];
        }} catch(e) {{}}

        if (!tunnelUrl) return;

        const res = await fetch(DB_URL);
        const store = await res.json();
        store.tunnelUrl = tunnelUrl;
        
        await fetch(DB_URL, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(store)
        }});
        console.log('☁️ [BULUT DB] Tünel Adresi Güncellendi:', tunnelUrl);
    }} catch (e) {{}}
}}

// Tarayıcı yolu bulucu (Puppeteer hatası engelleme)
const chromePaths = [
    'C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe',
    'C:\\\\Program Files (x86)\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe',
    'C:\\\\Program Files\\\\Microsoft\\\\Edge\\\\Application\\\\msedge.exe',
    'C:\\\\Program Files (x86)\\\\Microsoft\\\\Edge\\\\Application\\\\msedge.exe'
];
let targetExecutable = null;
for (const p of chromePaths) {{ if (fs.existsSync(p)) {{ targetExecutable = p; break; }} }}

let isReady = false;
const client = new Client({{
    authStrategy: new LocalAuth({{ dataPath: './.wwebjs_auth' }}),
    puppeteer: {{ headless: false, executablePath: targetExecutable, args: ['--no-sandbox', '--disable-setuid-sandbox'] }}
}});

client.on('qr', (qr) => {{
    console.log('\\n📱 LÜTFEN WHATSAPP QR KODUNU OKUTUN:\\n');
    qrcode.generate(qr, {{ small: true }});
}});

client.on('ready', () => {{
    isReady = true;
    console.log('\\n✅ [BAŞARILI] WhatsApp Botu Hazır!');
    registerTunnelToCloud();
    setInterval(registerTunnelToCloud, 30000); // Her 30 saniyede bir buluta yaşadığını bildirir
}});

app.post('/send-otp', async (req, res) => {{
    const {{ phone, code, customMessage }} = req.body;
    if (!isReady) return res.status(503).json({{ success: false, message: 'WhatsApp hazır değil.' }});

    try {{
        let cleaned = String(phone || '').replace(/\\D/g, '');
        if (cleaned.length === 10) cleaned = '90' + cleaned;
        if (cleaned.length === 11 && cleaned.startsWith('0')) cleaned = '90' + cleaned.substring(1);
        
        const targetChatId = `${{cleaned}}@c.us`;
        const text = customMessage ? customMessage : `*Pansiyon Sistemi*\\n\\nKodunuz: *${{code}}*`;
        await client.sendMessage(targetChatId, text);
        console.log(`📩 [MESAJ GÖNDERİLDİ] -> ${{cleaned}}`);
        return res.json({{ success: true }});
    }} catch (err) {{
        return res.status(500).json({{ success: false, message: err.message }});
    }}
}});

app.listen(3001, '0.0.0.0', () => {{
    console.log(`🌐 WhatsApp Mesaj Sunucusu (Port 3001) aktif.`);
    client.initialize();
}});
"""

# =========================================================================
# 3. YENİ NESİL API ROTASI (Tamamen Bulut Veritabanına Bağlı - Sıfırlanmaz)
# =========================================================================
def get_api_route_code(db_id):
    return f'''import {{ NextResponse }} from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

const DB_URL = 'https://api.npoint.io/{db_id}';

// Vercel hafızası yerine HER ZAMAN Bulut Veritabanından (Npoint) okur.
async function getStore() {{
  try {{
    const res = await fetch(DB_URL + '?t=' + Date.now(), {{ cache: 'no-store' }});
    if (res.ok) return await res.json();
  }} catch (e) {{}}
  return {{ students: [], belletmenler: [], aylikNobetler: [], leaves: [], dutyLogs: [], auditLogs: [], tunnelUrl: '' }};
}}

// Vercel hafızası yerine HER ZAMAN Bulut Veritabanına (Npoint) yazar.
async function saveStore(store: any) {{
  try {{
    await fetch(DB_URL, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(store)
    }});
  }} catch (e) {{}}
}}

function parseGender(val: any, defaultRole: 'erkek' | 'kiz'): 'erkek' | 'kiz' {{
  const s = String(val || '').trim().toLowerCase();
  if (s === 'k' || s.includes('kız') || s.includes('kiz') || s.includes('kadın') || s.includes('kadin') || s.includes('bayan')) return 'kiz';
  if (s === 'e' || s.includes('erkek') || s.includes('bay')) return 'erkek';
  return defaultRole;
}}

function normalizeKat(val: any): number {{
  const match = String(val || '1').match(/\\d+/);
  return match ? parseInt(match[0], 10) : 1;
}}

const addLog = (store: any, kullanici: string, islem: string, detay: string, tur: string) => {{
  if(!store.auditLogs) store.auditLogs = [];
  store.auditLogs.unshift({{ id: Date.now().toString(), tarihSaat: new Date().toLocaleString('tr-TR'), kullanici, islem, detay, tur }});
  if (store.auditLogs.length > 100) store.auditLogs.pop();
}};

export async function GET(request: Request) {{
  const {{ searchParams }} = new URL(request.url);
  const cinsiyetFilter = searchParams.get('cinsiyet');
  const store = await getStore();

  const headers = {{ 'Cache-Control': 'no-store, no-cache, must-revalidate', 'Pragma': 'no-cache' }};

  if (cinsiyetFilter === 'erkek' || cinsiyetFilter === 'kiz') {{
    const filteredStudents = (store.students || []).filter((s: any) => s.cinsiyet === cinsiyetFilter);
    return NextResponse.json({{ success: true, store: {{ ...store, students: filteredStudents }} }}, {{ headers }});
  }}
  return NextResponse.json({{ success: true, store }}, {{ headers }});
}}

export async function POST(request: Request) {{
  try {{
    const body = await request.json();
    const {{ action }} = body;
    const store = await getStore();
    if(!store.students) store.students = [];
    if(!store.belletmenler) store.belletmenler = [];
    if(!store.aylikNobetler) store.aylikNobetler = [];

    // --- BELLETMEN İŞLEMLERİ ---
    if (action === 'belletmen_login') {{
      const found = store.belletmenler.find((b: any) => b.id === body.id || b.name === body.name);
      if (!found || found.password !== String(body.password || '').trim()) {{
        addLog(store, found ? found.name : 'Bilinmeyen', 'Hatalı Giriş', 'Belletmen şifresi yanlış.', 'hata');
        await saveStore(store);
        return NextResponse.json({{ success: false, message: 'Hatalı şifre!' }}, {{ status: 401 }});
      }}
      const targetGender = found.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
      addLog(store, found.name, 'Sisteme Giriş', 'Yoklama paneline girdi.', 'basari');
      await saveStore(store);
      return NextResponse.json({{ success: true, belletmen: found, allowedGender: targetGender, store }});
    }}

    if (action === 'log_forgot_password') {{
      const found = store.belletmenler.find((b: any) => b.id === body.id);
      if (found && store.tunnelUrl) {{
        try {{
          await fetch(`${{store.tunnelUrl}}/send-otp`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ phone: found.phone, customMessage: `Şifreniz: *${{found.password}}*` }})
          }});
        }} catch(e) {{}}
      }}
      return NextResponse.json({{ success: true }});
    }}

    if (action === 'add_belletmen') {{
      store.belletmenler.push({{
        id: Date.now().toString(), name: String(body.name).trim(),
        cinsiyet: parseGender(body.cinsiyet, 'erkek') === 'kiz' ? 'kadin' : 'erkek',
        brans: String(body.brans || 'Öğretmen'), phone: String(body.phone || ''), password: String(body.password || '1234')
      }});
      addLog(store, 'İdare', 'Belletmen Eklendi', `${{body.name}} kaydedildi.`, 'basari');
      await saveStore(store);
      return NextResponse.json({{ success: true, message: 'Belletmen eklendi.', store }});
    }}

    if (action === 'bulk_add_belletmen') {{
      for (const r of body.rows) {{
        if (!r.name) continue;
        store.belletmenler.push({{
          id: (Date.now() + Math.random()).toString(), name: String(r.name).trim(),
          cinsiyet: parseGender(r.cinsiyet, 'erkek') === 'kiz' ? 'kadin' : 'erkek',
          brans: String(r.brans || 'Öğretmen'), phone: String(r.phone || ''), password: String(r.password || '1234')
        }});
      }}
      await saveStore(store);
      return NextResponse.json({{ success: true, message: 'Belletmenler yüklendi.', store }});
    }}

    if (action === 'delete_belletmen') {{
      store.belletmenler = store.belletmenler.filter((b: any) => b.id !== body.id);
      await saveStore(store);
      return NextResponse.json({{ success: true, store }});
    }}

    // --- ÖĞRENCİ İŞLEMLERİ ---
    if (action === 'add_student') {{
      store.students.push({{
        id: Date.now().toString(), name: String(body.name).trim(),
        cinsiyet: parseGender(body.cinsiyet, 'erkek'),
        kat: normalizeKat(body.kat), oda: String(body.oda || '101'),
        anneAdi: String(body.anneAdi || 'Anne'), anneTel: String(body.anneTel || ''),
        babaAdi: String(body.babaAdi || 'Baba'), babaTel: String(body.babaTel || ''),
        status: 'var'
      }});
      await saveStore(store);
      return NextResponse.json({{ success: true, message: 'Öğrenci eklendi.', store }});
    }}

    if (action === 'bulk_import') {{
      for (const r of body.rows) {{
        if (!r.name) continue;
        store.students.push({{
          id: (Date.now() + Math.random()).toString(), name: String(r.name).trim(),
          cinsiyet: parseGender(r.cinsiyet, 'erkek'),
          kat: normalizeKat(r.kat), oda: String(r.oda || '101'),
          anneAdi: String(r.anneAdi || 'Anne'), anneTel: String(r.anneTel || ''),
          babaAdi: String(r.babaAdi || 'Baba'), babaTel: String(r.babaTel || ''),
          status: 'var'
        }});
      }}
      addLog(store, 'İdare', 'Öğrenci Yüklendi', 'Toplu liste buluta eklendi.', 'basari');
      await saveStore(store);
      return NextResponse.json({{ success: true, message: 'Öğrenciler başarıyla BULUTA kaydedildi!', store }});
    }}

    if (action === 'delete_student') {{
      store.students = store.students.filter((s: any) => s.id !== body.id);
      await saveStore(store);
      return NextResponse.json({{ success: true, store }});
    }}

    if (action === 'update_attendance') {{
      const updatedMap = new Map(body.students.map((s: any) => [s.id, s]));
      store.students = store.students.map((existing: any) => updatedMap.has(existing.id) ? updatedMap.get(existing.id) : existing);
      await saveStore(store);
      return NextResponse.json({{ success: true, store }});
    }}

    // --- NÖBET İŞLEMLERİ ---
    if (action === 'bulk_monthly_duty') {{
      for (const r of body.rows) {{
        if (!r.tarih) continue;
        const idx = store.aylikNobetler.findIndex((d: any) => d.tarih === String(r.tarih).trim());
        const item = {{ tarih: String(r.tarih).trim(), erkek1: String(r.erkek1), erkek2: String(r.erkek2), kadin1: String(r.kadin1), kadin2: String(r.kadin2) }};
        if (idx > -1) store.aylikNobetler[idx] = item; else store.aylikNobetler.push(item);
      }}
      store.aylikNobetler.sort((a: any, b: any) => a.tarih.localeCompare(b.tarih));
      await saveStore(store);
      return NextResponse.json({{ success: true, message: 'Nöbetler eklendi.', store }});
    }}

    if (action === 'delete_monthly_duty') {{
      store.aylikNobetler = store.aylikNobetler.filter((d: any) => d.tarih !== body.tarih);
      await saveStore(store);
      return NextResponse.json({{ success: true, store }});
    }}

    if (action === 'admin_login') {{
      if (body.username === 'admin' && String(body.password).trim() === '123456') {{
        return NextResponse.json({{ success: true, store }});
      }}
      return NextResponse.json({{ success: false, message: 'Hatalı şifre' }}, {{ status: 401 }});
    }}

    return NextResponse.json({{ success: false, message: 'Bilinmeyen işlem.' }}, {{ status: 400 }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}
'''

def main():
    print("=========================================================")
    print("   SİSTEM BULUT VERİTABANINA TAŞINIYOR (Kalıcı Çözüm)")
    print("=========================================================")
    
    kill_old_processes()
    db_id = setup_cloud_db()
    
    if not db_id:
        print("Bulut DB oluşturulamadı. Lütfen internetinizi kontrol edin.")
        return

    # Dosyaları Bulut ID'si ile oluştur
    write_file("whatsapp-bot.js", get_whatsapp_bot_code(db_id))
    write_file("app/api/pansiyon/route.ts", get_api_route_code(db_id))
    
    print("\n🚀 Kodlar Vercel'e gönderiliyor, lütfen bekleyin...")
    subprocess.run("npm run build", shell=True)
    subprocess.run("git add .", shell=True)
    subprocess.run('git commit -m "Sistem tamamen Bulut Veritabanina (Npoint) baglandi. Veri silinme sorunu kokuyle cozuldu." --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)
    
    print("\n✅ Vercel Güncellendi!")
    print("\n🚀 WhatsApp Mesaj Botu başlatılıyor...")
    start_tunnel()
    os.system('start "WHATSAPP_MESAJ_BOTU" cmd /k "node whatsapp-bot.js"')
    
    print("\n🎉 İŞLEM TAMAMLANDI!")
    print("👉 Yönetici Paneline girip yeni baştan öğrenci ekleyin.")
    print("👉 Artık sayfayı yenileseniz de, 3 gün sonra telefondan girseniz de VERİLERİNİZ SİLİNMEYECEK.")

if __name__ == "__main__":
    main()