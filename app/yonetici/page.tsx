'use client';
import { useState } from 'react';
import { Shield, Upload, Users, Database, FileSpreadsheet, LogOut, Activity } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function YoneticiPortal() {
  const router = useRouter();
  const [uploaded, setUploaded] = useState(false);

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    setUploaded(true);
  };

  return (
    <div className="min-h-screen bg-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8 bg-white p-6 rounded-2xl shadow-sm">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Pansiyon Yöneticisi Paneli</h1>
            <p className="text-sm text-slate-600">Müdür Yardımcısı & Yönetim Modülü</p>
          </div>
          <button 
            onClick={() => router.push('/')}
            className="flex items-center space-x-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-xl text-slate-700 text-sm font-medium"
          >
            <LogOut className="w-4 h-4" />
            <span>Çıkış Yap</span>
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <span className="text-xs font-semibold text-slate-400 uppercase">Toplam Öğrenci</span>
            <div className="text-3xl font-bold text-slate-900 mt-2">199</div>
            <p className="text-xs text-emerald-600 mt-1">99 Erkek | 100 Kız</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <span className="text-xs font-semibold text-slate-400 uppercase">Yurtta Kalan</span>
            <div className="text-3xl font-bold text-blue-600 mt-2">185</div>
            <p className="text-xs text-slate-500 mt-1">Doluluk Oranı: %93</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <span className="text-xs font-semibold text-slate-400 uppercase">İzinli Öğrenci</span>
            <div className="text-3xl font-bold text-amber-600 mt-2">14</div>
            <p className="text-xs text-slate-500 mt-1">Otomatik Onaylı</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <span className="text-xs font-semibold text-slate-400 uppercase">Belletmen Kadrosu</span>
            <div className="text-3xl font-bold text-slate-900 mt-2">3 Aktif</div>
            <p className="text-xs text-slate-500 mt-1">Nöbet çizelgesi hazır</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white rounded-2xl shadow-sm p-8 border border-slate-200">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
              <span>Excel ile Toplu Veri Yükleme</span>
            </h2>
            <p className="text-sm text-slate-600 mb-6">
              e-Okul'dan alınan erkek ve kız öğrenci listeleri ile öğretmen listesini sisteme yükleyin; veli hesapları otomatik oluşturulsun.
            </p>

            {uploaded ? (
              <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl">
                <p className="font-semibold">Excel dosyaları başarıyla işlendi!</p>
                <p className="text-xs text-emerald-700 mt-1">99 erkek öğrenci, 100 kız öğrenci ve 3 öğretmen odalara atandı.</p>
              </div>
            ) : (
              <form onSubmit={handleUpload} className="space-y-4">
                <div className="border-2 border-dashed border-slate-300 rounded-2xl p-6 text-center hover:bg-slate-50 transition-all cursor-pointer">
                  <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-slate-700">Excel Dosyalarını Sürükleyin veya Seçin</p>
                  <p className="text-xs text-slate-400 mt-1">(.xlsx formatında öğrenci ve öğretmen listeleri)</p>
                </div>
                <button type="submit" className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-600/30 transition-all">
                  Toplu Listeleri İçeri Aktar ve Sistemi Başlat
                </button>
              </form>
            )}
          </div>

          <div className="bg-white rounded-2xl shadow-sm p-8 border border-slate-200">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center space-x-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <span>Sistem Denetim Günlüğü (Audit Log)</span>
            </h2>
            <div className="space-y-3 text-sm">
              <div className="p-3 bg-slate-50 rounded-xl flex justify-between items-center">
                <div>
                  <p className="font-semibold text-slate-800">Akşam Etüt Yoklaması Alındı</p>
                  <p className="text-xs text-slate-500">1. Kat Belletmen Öğretmeni</p>
                </div>
                <span className="text-xs font-mono text-slate-400">19:15</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl flex justify-between items-center">
                <div>
                  <p className="font-semibold text-slate-800">Veli İzin Onayı (Otomatik)</p>
                  <p className="text-xs text-slate-500">Çağan Efe Zeybek - Ev İzni</p>
                </div>
                <span className="text-xs font-mono text-slate-400">18:40</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl flex justify-between items-center">
                <div>
                  <p className="font-semibold text-slate-800">Excel Listesi Senkronizasyonu</p>
                  <p className="text-xs text-slate-500">Yönetici Paneli</p>
                </div>
                <span className="text-xs font-mono text-slate-400">17:00</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}