import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const rateLimitMap = new Map();

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  response.headers.set('X-Frame-Options', 'SAMEORIGIN');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  if (request.nextUrl.pathname.startsWith('/api/')) {
    // Next.js 15+ sürümlerinde request.ip kaldırıldığı için IP doğrudan header'dan alınıyor
    const ip = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown_ip';
    const now = Date.now();
    const currentInfo = rateLimitMap.get(ip) || { count: 0, lastReset: now };
    
    if (now - currentInfo.lastReset > 60000) {
      currentInfo.count = 0;
      currentInfo.lastReset = now;
    }
    
    currentInfo.count += 1;
    rateLimitMap.set(ip, currentInfo);

    if (currentInfo.count > 150) {
      return new NextResponse(
        JSON.stringify({ 
          success: false, 
          message: '🚨 GÜVENLİK KALKANI: Çok fazla şüpheli işlem tespit edildi. Cihazınız geçici olarak engellendi.' 
        }),
        { status: 429, headers: { 'Content-Type': 'application/json', 'Retry-After': '60' } }
      );
    }
  }

  return response;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};