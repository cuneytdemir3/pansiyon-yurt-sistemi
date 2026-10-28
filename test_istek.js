const URL = 'https://pansiyon-yurt-sistemi.vercel.app/api/pansiyon';
const USERS = 900; // 900 Eşzamanlı Kullanıcı

async function run() {
  console.log(`🚀 ${USERS} eşzamanlı istek gönderiliyor... Lütfen bekleyin.`);
  const start = Date.now();

  const promises = Array.from({ length: USERS }, async (_, i) => {
    try {
      const res = await fetch(URL + '?t=' + Math.random());
      return { id: i + 1, status: res.status };
    } catch (e) {
      return { id: i + 1, error: e.message };
    }
  });

  const results = await Promise.all(promises);
  const duration = Date.now() - start;
  const successCount = results.filter(r => r.status === 200).length;
  const failCount = results.length - successCount;

  console.log(`\n========================================`);
  console.log(`⏱️ Toplam Süre: ${duration} ms`);
  console.log(`✅ Başarılı İstek (200 OK): ${successCount} / ${USERS}`);
  console.log(`❌ Hatalı / Takılan İstek: ${failCount}`);
  console.log(`========================================\n`);
}

run();