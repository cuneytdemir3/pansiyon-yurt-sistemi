"use client";

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