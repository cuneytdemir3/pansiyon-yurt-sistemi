import os
import re
import subprocess
import time
import urllib.request

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())

def kill_old_processes():
    print("🧹 Eski bağlantılar temizleniyor...")
    subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, capture_output=True)
    time.sleep(1)

def ensure_cloudflared():
    exe_name = "cloudflared.exe"
    if not os.path.exists(exe_name):
        print("🌐 Tünel uygulaması indiriliyor...")
        urllib.request.urlretrieve("https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe", exe_name)
    return exe_name

def start_tunnel():
    exe_name = ensure_cloudflared()
    log_file = "tunnel.log"
    if os.path.exists(log_file): os.remove(log_file)
    
    print("🚀 Mobil Senkronizasyon Tüneli Açılıyor...")
    os.system(f'start "MOBIL_VERI_TUNELI" /MIN cmd /c "{exe_name} tunnel --url http://127.0.0.1:3001 > {log_file} 2>&1"')
    time.sleep(3)

# =========================================================================
# WHATSAPP BOT & 3 SANİYELİK KALP ATIŞI (HEARTBEAT) SİSTEMİ
# =========================================================================
WHATSAPP_BOT_JS = r"""
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors({ origin: '*', methods: ['GET', 'POST', 'PUT', 'OPTIONS'] }));
app.use(express.json({ limit: '15mb' }));

const DATA_FILE = path.join(__dirname, 'pansiyon_kalici_veri.json');

function readPersistentStore() {
    try { if (fs.existsSync(DATA_FILE)) return JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8')); } catch (e) {}
    return null;
}

function writePersistentStore(store) {
    try { fs.writeFileSync(DATA_FILE, JSON.stringify(store, null, 2), 'utf-8'); return true; } catch (e) { return false; }
}

// -------------------------------------------------------------------
// KESİN ÇÖZÜM: 3 SANİYELİK VERCEL KALP ATIŞI (HEARTBEAT)
// Bu sistem Vercel'in belleği silinse bile 3 saniye içinde geri doldurur.
// -------------------------------------------------------------------
async function heartbeatVercel() {
    try {
        const currentStore = readPersistentStore();
        if (!currentStore) return;
        
        let tunnelUrl = '';
        try {
            const log = fs.readFileSync('tunnel.log', 'utf-8');
            const match = log.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
            if (match) tunnelUrl = match[0];
        } catch(e) {}

        await fetch('https://pansiyon-yurt-sistemi.vercel.app/api/pansiyon', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'sync_full_store', store: currentStore, tunnelUrl: tunnelUrl })
        });
    } catch(e) {
        // Hata olursa sessizce geç, 3 saniye sonra tekrar deneyecek.
    }
}

// Sistemi açar açmaz Vercel'i güncelle ve her 3 saniyede bir tekrar et
heartbeatVercel();
setInterval(heartbeatVercel, 3000);


app.get('/store', (req, res) => {
    res.setHeader('Cache-Control', 'no-store');
    res.json({ success: true, store: readPersistentStore() });
});

app.post('/store', (req, res) => {
    if (req.body.store) writePersistentStore(req.body.store);
    res.json({ success: true });
});

// -------------------------------------------------------------------
// CHROME DÜZELTMESİ (PUPPETEER HATASINI ENGELLER)
// -------------------------------------------------------------------
const chromePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
];

let targetExecutable = null;
for (const p of chromePaths) {
    if (fs.existsSync(p)) { targetExecutable = p; break; }
}

let isReady = false;

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './.wwebjs_auth' }),
    puppeteer: {
        headless: false,
        executablePath: targetExecutable,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', (qr) => {
    console.log('\n📱 LÜTFEN AÇILAN PENCEREDEKİ VEYA AŞAĞIDAKİ QR KODU OKUTUN:\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    console.log('\n✅ [BAŞARILI] WhatsApp Botu ve 7/24 Kesintisiz Kalp Atışı Devrede!\n');
    console.log('👉 Artık sayfayı yenileseniz de hiçbir veri silinmeyecek.\n');
});

client.on('disconnected', (reason) => {
    isReady = false;
    console.log('⚠️ WhatsApp bağlantısı koptu:', reason);
});

function formatTurkishPhone(rawPhone) {
    let cleaned = String(rawPhone || '').replace(/\D/g, '');
    if (cleaned.startsWith('0090')) cleaned = cleaned.substring(2);
    else if (cleaned.length === 11 && cleaned.startsWith('0')) cleaned = '90' + cleaned.substring(1);
    else if (cleaned.length === 10 && !cleaned.startsWith('90')) cleaned = '90' + cleaned;
    return cleaned;
}

app.get('/status', (req, res) => { res.json({ ready: isReady }); });

app.post('/send-otp', async (req, res) => {
    const { phone, code, customMessage } = req.body;
    if (!isReady) return res.status(503).json({ success: false, message: 'WhatsApp hazır değil.' });

    try {
        const formatted = formatTurkishPhone(phone);
        const numberDetails = await client.getNumberId(formatted);
        const targetChatId = numberDetails ? numberDetails._serialized : `${formatted}@c.us`;
        const text = customMessage ? customMessage : `*Prof. Dr. Mümtaz Turhan SBL*\n\nGiriş Kodunuz: *${code}*`;
        await client.sendMessage(targetChatId, text);
        console.log(`📩 [WHATSAPP GÖNDERİLDİ] -> ${formatted}`);
        return res.json({ success: true, message: 'Mesaj iletildi.' });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
});

app.listen(3001, '0.0.0.0', () => {
    console.log(`🌐 Kalıcı Veri Köprüsü (Port 3001) çalışıyor.`);
    client.initialize();
});
"""

def main():
    print("=========================================================")
    print("   SAYFA YENİLEME HATASI KÖKTEN ÇÖZÜLÜYOR")
    print("=========================================================")
    
    kill_old_processes()
    start_tunnel()
    
    write_file("whatsapp-bot.js", WHATSAPP_BOT_JS)
    
    print("\n🚀 BOT VE KESİNTİSİZ SENKRONİZASYON BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')
    
    print("\n🎉 İŞLEM TAMAMLANDI! (Vercel derlemesi beklemenize gerek yok)")
    print("👉 Bundan sonra sistemi açmak için hep 'python sistemi_baslat.py' komutunu kullanın.")

if __name__ == "__main__":
    main()