const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const http = require('http');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

let isReady = false;

client.on('qr', (qr) => {
    console.log('\n================================================');
    console.log('[!] LÜTFEN AŞAĞIDAKİ QR KODU WHATSAPP İLE OKUTUN:');
    console.log('================================================\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    console.log('\n✅ [BAŞARILI] Kişisel WhatsApp Botu bağlandı ve mesaj göndermeye hazır!\n');
});

client.on('disconnected', () => {
    isReady = false;
    console.log('\n❌ [UYARI] WhatsApp bağlantısı koptu!\n');
});

client.initialize();

const server = http.createServer(async (req, res) => {
    // Tarayıcıdan (Vercel veya localhost) doğrudan erişim için CORS izinleri
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
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
                    res.end(JSON.stringify({ success: false, message: 'WhatsApp Botu henüz hazır değil (QR okutulmadı).' }));
                    return;
                }

                const { phone, code } = JSON.parse(body);
                if (!phone || !code) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: false, message: 'Telefon veya kod eksik.' }));
                    return;
                }

                let cleanPhone = phone.replace(/\D/g, '');
                if (cleanPhone.startsWith('0')) cleanPhone = cleanPhone.substring(1);
                if (!cleanPhone.startsWith('90')) cleanPhone = '90' + cleanPhone;
                const chatId = `${cleanPhone}@c.us`;

                const message = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nVeli Portalı Tek Kullanımlık Giriş Kodunuz: *${code}*\n\nBu kod 3 dakika geçerlidir. Güvenliğiniz için kimseyle paylaşmayınız.`;

                await client.sendMessage(chatId, message);
                console.log(`📨 [MESAJ GÖNDERİLDİ] ${cleanPhone} -> Kod: ${code}`);

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, message: 'WhatsApp mesajı başarıyla gönderildi.' }));
            } catch (err) {
                console.error('[HATA] Mesaj gönderilemedi:', err.message);
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
    console.log('🚀 [SUNUCU] WhatsApp Bot Köprüsü http://localhost:3001 adresinde dinleniyor...');
});