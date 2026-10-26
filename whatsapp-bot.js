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

app.get('/store', (req, res) => {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
    res.json({ success: true, store: readPersistentStore() });
});

app.post('/store', (req, res) => {
    if (req.body.store) {
        writePersistentStore(req.body.store);
        console.log(`🔄 [CANLI SENKRONİZASYON] Veritabanı güncellendi`);
    }
    res.json({ success: true });
});

// =======================================================================
// KESİN ÇÖZÜM: BİLGİSAYARDAKİ YÜKLÜ CHROME VEYA EDGE'İ BUL
// (Puppeteer'ın kendi eksik dosyalarını indirmeye çalışmasını engeller)
// =======================================================================
const chromePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
];

let targetExecutable = null;
for (const p of chromePaths) {
    if (fs.existsSync(p)) {
        targetExecutable = p;
        break;
    }
}

if (!targetExecutable) {
    console.error("❌ HATA: Bilgisayarınızda Google Chrome veya Edge bulunamadı!");
} else {
    console.log("✅ Sistem Tarayıcısı Bulundu:", targetExecutable);
}

let isReady = false;

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './.wwebjs_auth' }),
    puppeteer: {
        headless: false,
        executablePath: targetExecutable, // Doğrudan bilgisayardaki Chrome'u açar
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', (qr) => {
    console.log('\n================================================');
    console.log('📱 LÜTFEN AÇILAN PENCEREDEKİ VEYA AŞAĞIDAKİ QR KODU OKUTUN:');
    console.log('================================================\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    console.log('\n✅ [BAŞARILI] WhatsApp Botu ve Mobil Senkronizasyon Sunucusu Hazır!\n');
});

client.on('authenticated', () => {
    console.log('🔐 WhatsApp oturumu doğrulandı.');
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
    if (!isReady) return res.status(503).json({ success: false, message: 'WhatsApp Botu hazır değil.' });

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
    console.log(`🌐 WhatsApp & Mobil Veri Köprüsü (Port 3001) çalışıyor.`);
    client.initialize();
});