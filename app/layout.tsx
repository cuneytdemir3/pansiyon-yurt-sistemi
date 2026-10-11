import './globals.css';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Prof. Dr. Mümtaz Turhan SBL Pansiyon',
  description: 'T.C. Millî Eğitim Bakanlığı Standartlarına Uygun Pansiyon Otomasyonu',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body className="bg-slate-50 text-slate-900 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
