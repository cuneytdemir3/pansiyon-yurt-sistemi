const URL = 'https://pansiyon-yurt-sistemi.vercel.app/api/pansiyon';
const TOTAL_USERS = 100; // Aynı anda istek atacak kullanıcı sayısı

async function sendRequest(id) {
    const start = Date.now();
    try {
        const res = await fetch(URL + '?t=' + Math.random());
        const duration = Date.now() - start;
        console.log(`👤 Kullanıcı ${id}: Durum ${res.status} (${duration}ms)`);
    } catch (err) {
        console.log(`❌ Kullanıcı ${id} Hata:`, err.message);
    }
}

async function runTest() {
    console.log(`🚀 ${TOTAL_USERS} eşzamanlı kullanıcı testi başlatılıyor...`);
    const promises = [];
    for (let i = 1; i <= TOTAL_USERS; i++) {
        promises.push(sendRequest(i));
    }
    await Promise.all(promises);
    console.log(`✅ Test tamamlandı!`);
}

runTest();