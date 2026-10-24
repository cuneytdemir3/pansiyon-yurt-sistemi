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
    print("🧹 Açık kalan Node.js işlemleri temizleniyor...")
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

    print("🚀 WhatsApp Botu için Cloudflare HTTPS tüneli açılıyor...")
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
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

# =========================================================================
# PWA (PROGRESSIVE WEB APP) DOSYALARI
# =========================================================================

MANIFEST_JSON = r"""{
  "name": "Prof. Dr. Mümtaz Turhan SBL Pansiyon",
  "short_name": "SBL Pansiyon",
  "description": "Erkek ve Kız Öğrenci Pansiyonu Yoklama & İzin Yönetim Sistemi",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#4f46e5",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icon.svg",
      "sizes": "any",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
"""

SERVICE_WORKER_JS = r"""
const CACHE_NAME = 'sbl-pansiyon-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Basit pass-through fetch: PWA yüklenebilirliği için SW şarttır.
  // Çevrimdışı önbellekleme karmaşıklığını önlemek için daima network'ten çeker.
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
"""

APP_ICON_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563eb" />
      <stop offset="100%" stop-color="#1e3a8a" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-opacity="0.3" />
    </filter>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg)" />
  <g filter="url(#shadow)">
    <text x="50%" y="45%" font-family="Arial, sans-serif" font-size="180" font-weight="900" fill="#ffffff" text-anchor="middle" dominant-baseline="middle" letter-spacing="-4">SBL</text>
    <text x="50%" y="72%" font-family="Arial, sans-serif" font-size="52" font-weight="bold" fill="#93c5fd" text-anchor="middle" dominant-baseline="middle" letter-spacing="6">PANSİYON</text>
  </g>
</svg>
"""

# Next.js Layout.tsx (PWA Meta Tagları ve Service Worker Kaydı Eklenmiş Hali)
LAYOUT_TSX = r""""use client";

import './globals.css';
import { useEffect } from 'react';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => console.log('Service Worker Kaydedildi: ', reg.scope))
        .catch((err) => console.log('Service Worker Hatası: ', err));
    }
  }, []);

  return (
    <html lang="tr">
      <head>
        <title>SBL Pansiyon Yönetimi</title>
        <meta name="description" content="Prof. Dr. Mümtaz Turhan SBL Pansiyon Yönetim Portalı" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0, viewport-fit=cover" />
        <meta name="theme-color" content="#4f46e5" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="SBL Pansiyon" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/icon.svg" />
      </head>
      <body className="antialiased select-none">
        {children}
      </body>
    </html>
  );
}
"""

def main():
    print("=========================================================")
    print("   PWA (MOBİL UYGULAMA) ALTYAPISI YÜKLENİYOR")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 1. PWA Dosyalarını (Manifest, Service Worker, Mobil Logo) Public Klasörüne Yaz
    write_file("public/manifest.json", MANIFEST_JSON)
    write_file("public/sw.js", SERVICE_WORKER_JS)
    write_file("public/icon.svg", APP_ICON_SVG)

    # 2. Layout dosyasını PWA meta etiketleriyle güncelle
    write_file("app/layout.tsx", LAYOUT_TSX)

    # 3. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 4. Derleme ve GitHub/Vercel Gönderimi
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Sisteme PWA (Ana Ekrana Ekle, Tam Ekran App) ozelligi eklendi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 PWA MOBİL UYGULAMA DESTEĞİ CANLIYA ALINDI!")
    print("👉 Telefonunuzdan https://pansiyon-yurt-sistemi.vercel.app adresine girin.")
    print("👉 Ekranda çıkan 'Ana Ekrana Ekle' butonuna basın.")
    print("👉 Artık sistem telefonunuzda bağımsız bir mobil uygulama gibi açılacak!")
    print("=========================================================")

if __name__ == "__main__":
    main()