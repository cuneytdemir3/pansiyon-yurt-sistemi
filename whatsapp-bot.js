const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const http = require('http');
const fs = require('fs');

const possiblePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    (process.env.LOCALAPPDATA || '') + '\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
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
    console.log('\n✅ [BAŞARILI] WhatsApp Botu Bağlandı ve Hazır!\n');
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
                let cleanPhone = (phone || '').replace(/\D/g, '');
                if (cleanPhone.startsWith('0')) cleanPhone = cleanPhone.substring(1);
                if (!cleanPhone.startsWith('90')) cleanPhone = '90' + cleanPhone;

                // Özel mesaj verilmişse onu at, yoksa standart OTP kalıbını kullan
                let message = customMessage;
                if (!message) {
                    message = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nVeli Portalı Tek Kullanımlık Giriş Kodunuz: *${code}*\n\nBu kod 3 dakika geçerlidir.`;
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