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

    print("🚀 WhatsApp Botu için güvenli HTTPS tüneli açılıyor...")
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
    print("   BELLETMEN WHATSAPP BİLDİRİM ONARIMI & GÜNCELLEME")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF BOT TÜNELİ]: {tunnel_url}")

    # 1. WhatsApp Bot Kodunu Genel Mesaj Gönderebilecek Şekilde Güncelle (whatsapp-bot.js)
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
    console.log('\\n✅ [BAŞARILI] WhatsApp Botu Bağlandı ve Hazır!\\n');
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
                    res.end(JSON.stringify({ success: false, message: 'Bot hazır değil.' }));
                    return;
                }

                const { phone, code, customMessage } = JSON.parse(body);
                let cleanPhone = (phone || '').replace(/\\D/g, '');
                if (cleanPhone.startsWith('0')) cleanPhone = cleanPhone.substring(1);
                if (!cleanPhone.startsWith('90')) cleanPhone = '90' + cleanPhone;

                // Özel mesaj verilmişse onu at, yoksa standart OTP kalıbını kullan
                let message = customMessage;
                if (!message) {
                    message = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nVeli Portalı Tek Kullanımlık Giriş Kodunuz: *${code}*\\n\\nBu kod 3 dakika geçerlidir.`;
                }

                let targetChatId = `${cleanPhone}@c.us`;
                if (client.info && client.info.wid && client.info.wid.user === cleanPhone) {
                    targetChatId = client.info.wid._serialized;
                } else {
                    const numberDetails = await client.getNumberId(cleanPhone);
                    if (numberDetails) {
                        targetChatId = numberDetails._serialized;
                    }
                }

                await client.sendMessage(targetChatId, message, { sendSeen: false });
                console.log(`✅ [MESAJ GÖNDERİLDİ] -> ${cleanPhone}`);

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, message: 'Mesaj iletildi.' }));
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
    console.log('🚀 [BOT SUNUCUSU] http://localhost:3001 adresinde hazır.');
});
"""
    write_file("whatsapp-bot.js", whatsapp_bot_code)

    # 2. Sunucu Taraflı Bildirim API Rotası (app/api/belletmen/bildirim/route.ts)
    bildirim_api_code = f"""import {{ NextResponse }} from 'next/server';

const BOT_URLS = ['{tunnel_url}', 'http://127.0.0.1:3001'];

export async function POST(request: Request) {{
  try {{
    const {{ ogrenciler, seans }} = await request.json();
    if (!Array.isArray(ogrenciler) || ogrenciler.length === 0) {{
      return NextResponse.json({{ success: false, message: 'Bildirilecek öğrenci bulunamadı.' }}, {{ status: 400 }});
    }}

    const seansAdi = seans === 'etut' ? '19:15 Etüt' : '23:00 Yat';
    let basarili = 0;
    let basarisiz = 0;

    for (const ogr of ogrenciler) {{
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz, öğrenciniz *${{ogr.adSoyad}}* (Oda: ${{ogr.odaNo}}) pansiyonumuzun bu akşamki *${{seansAdi}}* yoklamasında bulunamamıştır.\\n\\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;

      let gonderildi = false;
      for (const botUrl of BOT_URLS) {{
        try {{
          const controller = new AbortController();
          const tid = setTimeout(() => controller.abort(), 7000);

          const res = await fetch(`${{botUrl}}/send-otp`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              phone: ogr.veliTelefon,
              customMessage: customMessage
            }}),
            signal: controller.signal
          }});
          clearTimeout(tid);

          const data = await res.json();
          if (res.ok && data.success) {{
            gonderildi = true;
            break;
          }}
        }} catch (e) {{}}
      }}

      if (gonderildi) basarili++;
      else basarisiz++;
    }}

    return NextResponse.json({{
      success: true,
      message: `${{basarili}} veliye WhatsApp bildirimi başarıyla iletildi.${{basarisiz > 0 ? ` (${{basarisiz}} veliye ulaşılamadı)` : ''}}`,
      basarili,
      basarisiz
    }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}
"""
    write_file("app/api/belletmen/bildirim/route.ts", bildirim_api_code)

    # 3. Yoklama Sayfası (app/belletmen/yoklama/page.tsx - Sunucu API'sini Çağırır)
    yoklama_page = """'use client';

import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  Send, 
  Save, 
  Search
} from 'lucide-react';

interface Ogrenci {
  id: string;
  adSoyad: string;
  sinif: string;
  odaNo: string;
  veliTelefon: string;
  durum: 'burada' | 'yok' | 'izinli' | 'revir';
  izinDetay?: string;
}

export default function BelletmenYoklamaPage() {
  const [ogrenciler, setOgrenciler] = useState<Ogrenci[]>([]);
  const [seans, setSeans] = useState<'etut' | 'yat'>('etut');
  const [katFiltresi, setKatFiltresi] = useState<string>('hepsi');
  const [arama, setArama] = useState('');
  const [saving, setSaving] = useState(false);
  const [bilgiMesaji, setBilgiMesaji] = useState('');
  const [sendingAlerts, setSendingAlerts] = useState(false);

  const yoklamaGetir = async () => {
    try {
      const res = await fetch('/api/belletmen/yoklama');
      const data = await res.json();
      if (data.success && data.data) {
        setOgrenciler(data.data);
      }
    } catch (err) {
      console.error('Yoklama yüklenemedi:', err);
    }
  };

  useEffect(() => {
    yoklamaGetir();
  }, []);

  const durumGuncelle = (id: string, yeniDurum: Ogrenci['durum']) => {
    setOgrenciler(prev => prev.map(ogr => ogr.id === id ? { ...ogr, durum: yeniDurum } : ogr));
  };

  const tumunuBuradaYap = () => {
    setOgrenciler(prev => prev.map(ogr => ogr.durum === 'izinli' ? ogr : { ...ogr, durum: 'burada' }));
  };

  const filtreliOgrenciler = ogrenciler.filter(ogr => {
    const isimEslesir = ogr.adSoyad.toLowerCase().includes(arama.toLowerCase()) || ogr.odaNo.includes(arama);
    const katEslesir = katFiltresi === 'hepsi' || ogr.odaNo.startsWith(katFiltresi);
    return isimEslesir && katEslesir;
  });

  const ozet = {
    toplam: ogrenciler.length,
    burada: ogrenciler.filter(o => o.durum === 'burada').length,
    yok: ogrenciler.filter(o => o.durum === 'yok').length,
    izinli: ogrenciler.filter(o => o.durum === 'izinli').length,
    revir: ogrenciler.filter(o => o.durum === 'revir').length,
  };

  const handleYoklamaKaydet = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/belletmen/yoklama', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seans, records: ogrenciler })
      });
      const data = await res.json();
      if (data.success) {
        setBilgiMesaji(data.message);
        setTimeout(() => setBilgiMesaji(''), 4000);
      }
    } catch {
      setBilgiMesaji('Kayıt sırasında bağlantı hatası oluştu.');
    } finally {
      setSaving(false);
    }
  };

  const handleYokOlanlaraWhatsAppGonder = async () => {
    const yokOlanlar = ogrenciler.filter(o => o.durum === 'yok');
    if (yokOlanlar.length === 0) return;

    setSendingAlerts(true);
    setBilgiMesaji('Velilere WhatsApp mesajları gönderiliyor, lütfen bekleyin...');

    try {
      const res = await fetch('/api/belletmen/bildirim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ogrenciler: yokOlanlar, seans })
      });
      const data = await res.json();
      if (data.success) {
        setBilgiMesaji(data.message);
      } else {
        setBilgiMesaji(data.message || 'Bildirim gönderilemedi.');
      }
    } catch {
      setBilgiMesaji('Bildirim sunucusuna ulaşılamadı.');
    } finally {
      setSendingAlerts(false);
      setTimeout(() => setBilgiMesaji(''), 6000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6 pb-24">
      <div className="max-w-4xl mx-auto space-y-6">
        
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md">
              Nöbetçi Belletmen Paneli
            </span>
            <h1 className="text-xl md:text-2xl font-extrabold text-slate-800 mt-1">Pansiyon Akşam Yoklaması</h1>
            <p className="text-xs text-slate-500">Öğrencilerin pansiyon mevcudiyet durumunu anlık işaretleyin.</p>
          </div>

          <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 w-full sm:w-auto">
            <button
              onClick={() => setSeans('etut')}
              className={`flex-1 sm:flex-initial px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                seans === 'etut' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              19:15 Etüt
            </button>
            <button
              onClick={() => setSeans('yat')}
              className={`flex-1 sm:flex-initial px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                seans === 'yat' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              23:00 Yat Yoklaması
            </button>
          </div>
        </div>

        {bilgiMesaji && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-semibold text-center">
            {bilgiMesaji}
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">Mevcut (Burada)</div>
            <div className="text-2xl font-bold text-emerald-600 mt-1">{ozet.burada} / {ozet.toplam}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">Yok / Habersiz</div>
            <div className="text-2xl font-bold text-rose-600 mt-1">{ozet.yok}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">İzinli (Evci)</div>
            <div className="text-2xl font-bold text-blue-600 mt-1">{ozet.izinli}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">Revir / Rapor</div>
            <div className="text-2xl font-bold text-amber-600 mt-1">{ozet.revir}</div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Öğrenci veya Oda No ara..."
              value={arama}
              onChange={(e) => setArama(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="flex gap-2 w-full md:w-auto">
            <select
              value={katFiltresi}
              onChange={(e) => setKatFiltresi(e.target.value)}
              className="text-xs border border-slate-200 rounded-xl px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="hepsi">Tüm Katlar</option>
              <option value="1">1. Kat (100'ler)</option>
              <option value="2">2. Kat (200'ler)</option>
              <option value="3">3. Kat (300'ler)</option>
            </select>

            <button
              onClick={tumunuBuradaYap}
              className="text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-xl transition-all cursor-pointer"
            >
              Kalanları 'Burada' Yap
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {filtreliOgrenciler.map((ogr) => (
            <div
              key={ogr.id}
              className={`bg-white rounded-2xl p-4 border transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm ${
                ogr.durum === 'yok' 
                  ? 'border-rose-300 bg-rose-50/20' 
                  : ogr.durum === 'izinli' 
                  ? 'border-blue-200 bg-blue-50/20' 
                  : 'border-slate-200'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 text-sm">{ogr.adSoyad}</span>
                  <span className="text-[11px] font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md">
                    Oda: {ogr.odaNo}
                  </span>
                  <span className="text-[11px] text-slate-400">{ogr.sinif}</span>
                </div>
                {ogr.izinDetay && (
                  <div className="text-xs text-blue-600 font-medium flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> {ogr.izinDetay}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-1.5 w-full sm:w-auto">
                <button
                  onClick={() => durumGuncelle(ogr.id, 'burada')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'burada'
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <CheckCircle2 className="w-3.5 h-3.5" /> Burada
                </button>

                <button
                  onClick={() => durumGuncelle(ogr.id, 'yok')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'yok'
                      ? 'bg-rose-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <XCircle className="w-3.5 h-3.5" /> Yok
                </button>

                <button
                  onClick={() => durumGuncelle(ogr.id, 'izinli')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'izinli'
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  İzinli
                </button>

                <button
                  onClick={() => durumGuncelle(ogr.id, 'revir')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'revir'
                      ? 'bg-amber-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  Revir
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-lg flex flex-col sm:flex-row justify-between items-center gap-3">
          <div className="text-xs text-slate-500 text-center sm:text-left">
            {ozet.yok > 0 ? (
              <span className="text-rose-600 font-semibold flex items-center gap-1">
                <AlertTriangle className="w-4 h-4 inline" /> {ozet.yok} öğrenci yoklamada bulunamadı!
              </span>
            ) : (
              <span className="text-emerald-600 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4 inline" /> Tüm öğrenciler eksiksiz veya izinli.
              </span>
            )}
          </div>

          <div className="flex gap-2 w-full sm:w-auto">
            {ozet.yok > 0 && (
              <button
                onClick={handleYokOlanlaraWhatsAppGonder}
                disabled={sendingAlerts}
                className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" /> {sendingAlerts ? 'Gönderiliyor...' : `Velilere Bildir (${ozet.yok})`}
              </button>
            )}

            <button
              onClick={handleYoklamaKaydet}
              disabled={saving}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
            >
              <Save className="w-3.5 h-3.5" /> {saving ? 'Kaydediliyor...' : 'Yoklamayı Onayla'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
"""
    write_file("app/belletmen/yoklama/page.tsx", yoklama_page)

    # 4. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 5. Derleme & Git Senkronizasyonu
    if not run_command("npm run build", "Next.js derleme testi yapılıyor"):
        print("❌ Derleme hatası! Lütfen terminal çıktısını inceleyin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Belletmen veli uyarisi WhatsApp sunucu API koprusu kuruldu" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 GÜNCELLEME TAMAMLANDI!")
    print("👉 'Velilere Bildir' butonu artık Next.js sunucu köprüsüyle WhatsApp botuna doğrudan bağlıdır.")
    print("=========================================================")

if __name__ == "__main__":
    main()