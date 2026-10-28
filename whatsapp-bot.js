const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(cors({ origin: '*', methods: ['GET', 'POST', 'PUT', 'OPTIONS'] }));
app.use(express.json({ limit: '15mb' }));

async function syncTunnelToNeon() {
    try {
        if (!fs.existsSync('tunnel.log')) return;
        const log = fs.readFileSync('tunnel.log', 'utf-8');
        const match = log.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
        if (match) {
            const tunnelUrl = match[0];
            await fetch('https://pansiyon-yurt-sistemi.vercel.app/api/pansiyon', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'update_tunnel_url', tunnelUrl })
            });
            console.log('☁️ [NEON DB] WhatsApp Tünel Adresi Buluta İşlendi:', tunnelUrl);
        }
    } catch (e) {}
}

const chromePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
];
let targetExecutable = null;
for (const p of chromePaths) { if (fs.existsSync(p)) { targetExecutable = p; break; } }

let isReady = false;
const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './.wwebjs_auth' }),
    puppeteer: { headless: false, executablePath: targetExecutable, args: ['--no-sandbox', '--disable-setuid-sandbox'] }
});

client.on('qr', (qr) => {
    console.log('\n📱 LÜTFEN WHATSAPP QR KODUNU OKUTUN:\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    console.log('\n✅ [BAŞARILI] WhatsApp Bildirim Sunucusu Hazır!');
    syncTunnelToNeon();
    setInterval(syncTunnelToNeon, 60000);
});

app.post('/send-otp', async (req, res) => {
    const { phone, code, customMessage } = req.body;
    
    if (!isReady) return res.status(503).json({ success: false, message: 'WhatsApp hazır değil.' });
    
    // VERCEL'DEN GELEN İSTEĞİ TERMİNALDE GÖSTEREN YENİ SİSTEM
    console.log(`\n🔔 [YENİ İSTEK] Vercel'den mesaj talebi geldi!`);
    console.log(`👉 Veritabanından Çekilen Hedef Numara: ${phone}`);

    try {
        let cleaned = String(phone || '').replace(/\D/g, '');
        if (cleaned.length === 10) cleaned = '90' + cleaned;
        if (cleaned.length === 11 && cleaned.startsWith('0')) cleaned = '90' + cleaned.substring(1);
        
        const numberDetails = await client.getNumberId(cleaned);
        const targetChatId = numberDetails ? numberDetails._serialized : `${cleaned}@c.us`;
        
        const text = customMessage ? customMessage : `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nGiriş Kodunuz: *${code}*`;
        
        await client.sendMessage(targetChatId, text);
        console.log(`✅ [BAŞARILI] Mesaj Gönderildi -> ${cleaned}`);
        return res.json({ success: true, message: 'Mesaj iletildi.' });
    } catch (err) {
        console.error(`❌ [HATA] Mesaj Gönderilemedi:`, err.message);
        return res.status(500).json({ success: false, message: err.message });
    }
});

app.listen(3001, '0.0.0.0', () => {
    console.log('🌐 WhatsApp Sunucusu (Port 3001) çalışıyor.');
    syncTunnelToNeon();
    client.initialize();
});