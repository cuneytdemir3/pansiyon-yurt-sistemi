const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors({ origin: '*', methods: ['GET', 'POST', 'PUT', 'OPTIONS'] }));
app.use(express.json({ limit: '15mb' }));

// KALICI VERİTABANI DOSYASI (Bilgisayar ve Mobil Cihazlar İçin Ortak Kaynak)
const DATA_FILE = path.join(__dirname, 'pansiyon_kalici_veri.json');

function readPersistentStore() {
    try {
        if (fs.existsSync(DATA_FILE)) {
            return JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
        }
    } catch (e) {
        console.error('Veri okuma hatası:', e.message);
    }
    return null;
}

function writePersistentStore(store) {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(store, null, 2), 'utf-8');
        return true;
    } catch (e) {
        console.error('Veri yazma hatası:', e.message);
        return false;
    }
}

// MOBİL VE WEB SENKRONİZASYON UÇ NOKTALARI (/store)
app.get('/store', (req, res) => {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
    const store = readPersistentStore();
    res.json({ success: true, store });
});

app.post('/store', (req, res) => {
    const { store } = req.body;
    if (store) {
        writePersistentStore(store);
        console.log(`🔄 [CANLI SENKRONİZASYON] Veritabanı güncellendi (${store.students?.length || 0} Öğrenci, ${store.belletmenler?.length || 0} Belletmen)`);
    }
    res.json({ success: true });
});

let isReady = false;

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './.wwebjs_auth' }),
    puppeteer: {
        headless: false,
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

app.get('/status', (req, res) => {
    res.json({ ready: isReady });
});

app.post('/send-otp', async (req, res) => {
    const { phone, code, customMessage } = req.body;
    if (!isReady) {
        return res.status(503).json({
            success: false,
            message: 'WhatsApp Botu henüz hazır değil. Lütfen QR kodu okutun.'
        });
    }

    try {
        const formatted = formatTurkishPhone(phone);
        const numberDetails = await client.getNumberId(formatted);
        const targetChatId = numberDetails ? numberDetails._serialized : `${formatted}@c.us`;

        const text = customMessage
            ? customMessage
            : `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nVeli Giriş Kodunuz: *${code}*\n\nBu kodu kimseyle paylaşmayınız.`;

        await client.sendMessage(targetChatId, text);
        console.log(`📩 [WHATSAPP GÖNDERİLDİ] -> ${formatted}`);
        return res.json({ success: true, message: 'Mesaj başarıyla iletildi.' });
    } catch (err) {
        console.error('❌ [WHATSAPP HATASI]:', err.message);
        return res.status(500).json({ success: false, message: err.message });
    }
});

const PORT = 3001;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🌐 WhatsApp & Mobil Veri Köprüsü http://127.0.0.1:${PORT} üzerinde çalışıyor.`);
    client.initialize();
});