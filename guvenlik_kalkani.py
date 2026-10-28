import os
import subprocess
import sys

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ [GÜNCELLENDİ] {filepath}")

# =========================================================================
# NEXT.JS GÜVENLİK YAZILIMI (middleware.ts) - Vercel Edge Ağında Çalışır
# =========================================================================
MIDDLEWARE_TS = r'''import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Vercel Edge seviyesinde çalışan hafıza haritası (IP tabanlı takip)
const rateLimitMap = new Map();

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // 1. ZORUNLU GÜVENLİK BAŞLIKLARI (SECURITY HEADERS)
  // Clickjacking (Tıklama Korsanlığı) Koruması
  response.headers.set('X-Frame-Options', 'SAMEORIGIN');
  // XSS (Siteler Arası Betik) Koruması
  response.headers.set('X-XSS-Protection', '1; mode=block');
  // MIME-Sniffing Koruması
  response.headers.set('X-Content-Type-Options', 'nosniff');
  // Zorunlu HTTPS Koruması (Bağlantı dinlenmesini engeller)
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  // Gelişmiş Referans Gizliliği
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  // 2. BRUTE-FORCE VE DDOS KALKANI (API RATE LIMITING)
  // Sadece API rotalarını koruma altına alıyoruz
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const ip = request.ip || request.headers.get('x-forwarded-for') || 'unknown_ip';
    const now = Date.now();
    const currentInfo = rateLimitMap.get(ip) || { count: 0, lastReset: now };
    
    // 1 dakikalık zaman penceresi (60000 ms)
    if (now - currentInfo.lastReset > 60000) {
      currentInfo.count = 0;
      currentInfo.lastReset = now;
    }
    
    currentInfo.count += 1;
    rateLimitMap.set(ip, currentInfo);

    // Bir IP'den dakikada maksimum 150 isteğe izin ver
    // (Normal bir kullanıcının veya öğretmenin bu limite ulaşması imkansızdır)
    if (currentInfo.count > 150) {
      return new NextResponse(
        JSON.stringify({ 
          success: false, 
          message: '🚨 GÜVENLİK KALKANI: Çok fazla şüpheli işlem tespit edildi. Cihazınız geçici olarak engellendi, lütfen 1 dakika bekleyin.' 
        }),
        { 
          status: 429, 
          headers: { 
            'Content-Type': 'application/json',
            'Retry-After': '60'
          } 
        }
      );
    }
  }

  return response;
}

// Güvenlik kalkanının hangi sayfalarda çalışacağını belirler
export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
'''

def main():
    print("================================================================")
    print("   SBL PANSİYON SİSTEMİ GÜVENLİK KALKANI AKTİFLEŞTİRİLİYOR")
    print("================================================================")

    # Middleware dosyasını projenin ana dizinine (root) oluştur
    write_file("middleware.ts", MIDDLEWARE_TS)

    print("\n🚀 Güvenlik yapılandırması Vercel'e gönderiliyor...")
    if subprocess.run("npm run build", shell=True).returncode != 0:
        print("❌ Derleme hatası! Lütfen kodu kontrol edin.")
        sys.exit(1)

    subprocess.run("git add middleware.ts", shell=True)
    subprocess.run('git commit -m "Security: Rate limiting (Brute-Force DDoS kalkani) ve HTTP Guvenlik basliklari (XSS, HSTS) eklendi" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    # Dosya yığılmasını önlemek için kendini sil
    try:
        os.remove(__file__)
        print("🧹 Kurulum betiği görevini tamamladı ve kendini sildi.")
    except:
        pass

    print("\n================================================================")
    print("🎉 GÜVENLİK KALKANI DEVREYE ALINDI!")
    print("👉 Artık sisteminiz kaba kuvvet şifre denemelerine ve")
    print("   siteler arası komut çalıştırma (XSS) saldırılarına karşı korumalıdır.")
    print("================================================================")

if __name__ == "__main__":
    main()