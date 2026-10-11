# MEB Pansiyon ve Yurt Takip Sistemi

T.C. Millî Eğitim Bakanlığı standartlarına uygun, Next.js 15 ve TypeScript ile geliştirilmiş hibrit bulut mimarili pansiyon otomasyon sistemi.

## Kurulum ve Çalıştırma

1. Bağımlılıkları yükleyin:
   ```bash
   npm install
   ```
2. Geliştirme sunucusunu başlatın:
   ```bash
   npm run dev
   ```

## GitHub ve Vercel Dağıtım Kılavuzu

### 1. GitHub'a Yükleme
Projenizi GitHub'a göndermek için terminalde sırasıyla şu komutları çalıştırın:
```bash
git init
git add .
git commit -m "MEB Pansiyon ve Yurt Takip Sistemi ilk sürüm"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/pansiyon-sistemi.git
git push -u origin main
```

### 2. Vercel Üzerinde Canlıya Alma (Deployment)
1. **[Vercel (vercel.com)](https://vercel.com)** adresine giriş yapın.
2. **"Add New... -> Project"** seçeneğine tıklayın ve GitHub üzerindeki `pansiyon-sistemi` repomuzu seçin.
3. **Environment Variables (Çevre Değişkenleri)** bölümüne şunları ekleyin:
   - `DATABASE_URL`: Neon PostgreSQL bağlantı adresiniz (Boş bırakılırsa otomatik SQLite/JSON fallback devreye girer).
   - `JWT_SECRET`: Güvenli bir gizli anahtar (Örn: `meb-pansiyon-secret-key-2026`).
   - `GEMINI_API_KEY`: Google Gemini API anahtarınız (Yapay zeka asistanı için).
4. **"Deploy"** butonuna basarak saniyeler içinde canlıya alın!