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
    print("🧹 Açık kalan eski Node.js ve Tünel işlemleri temizleniyor...")
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

    print("🚀 WhatsApp Botu için güvenli HTTPS tüneli açılıyor...")
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
        print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

def main():
    print("=========================================================")
    print("   BELLETMEN YOKLAMA MODÜLÜ VE OTOMATİK KURULUM")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        print("⚠️ Tünel başlatılamadı, yerel adres kullanılacak.")
        tunnel_url = "http://localhost:3001"

    print(f"🌍 [AKTİF BOT TÜNELİ]: {tunnel_url}")

    # 1. Belletmen Yoklama API Rotası
    yoklama_api = """import { NextResponse } from 'next/server';

declare global {
  var __pansiyonYoklamaDB: any[] | undefined;
}

if (!globalThis.__pansiyonYoklamaDB) {
  globalThis.__pansiyonYoklamaDB = [
    { id: '1', adSoyad: 'Ahmet Yılmaz', sinif: '10-A', odaNo: '201', veliTelefon: '05416571469', durum: 'burada' },
    { id: '2', adSoyad: 'Mehmet Demir', sinif: '11-B', odaNo: '201', veliTelefon: '05410000002', durum: 'izinli', izinDetay: 'Hafta Sonu Evci İzni' },
    { id: '3', adSoyad: 'Can Kaya', sinif: '9-C', odaNo: '202', veliTelefon: '05410000003', durum: 'burada' },
    { id: '4', adSoyad: 'Burak Şahin', sinif: '12-A', odaNo: '203', veliTelefon: '05410000004', durum: 'yok' },
    { id: '5', adSoyad: 'Emre Çelik', sinif: '10-B', odaNo: '204', veliTelefon: '05410000005', durum: 'revir', izinDetay: 'Baş Ağrısı / Revirde' },
  ];
}

export async function GET() {
  return NextResponse.json({ success: true, data: globalThis.__pansiyonYoklamaDB });
}

export async function POST(request: Request) {
  try {
    const { seans, records } = await request.json();
    if (Array.isArray(records)) {
      globalThis.__pansiyonYoklamaDB = records;
    }
    return NextResponse.json({
      success: true,
      message: `${seans === 'etut' ? '19:15 Etüt' : '23:00 Yat'} yoklaması başarıyla kaydedildi.`,
      updatedCount: records?.length || 0
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
"""
    write_file("app/api/belletmen/yoklama/route.ts", yoklama_api)

    # 2. Belletmen Yoklama Sayfası (Düz string ve replace ile tünel adresi gömülür, syntax hatası yapmaz)
    yoklama_page = """'use client';

import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  Send, 
  Save, 
  Search
} from 'lucide-react';

interface Ogrenci {
  id: string;
  adSoyad: string;
  sinif: string;
  odaNo: string;
  veliTelefon: string;
  durum: 'burada' | 'yok' | 'izinli' | 'revir';
  izinDetay?: string;
}

const TUNNEL_URL = '__TUNNEL_URL_PLACEHOLDER__';

export default function BelletmenYoklamaPage() {
  const [ogrenciler, setOgrenciler] = useState<Ogrenci[]>([]);
  const [seans, setSeans] = useState<'etut' | 'yat'>('etut');
  const [katFiltresi, setKatFiltresi] = useState<string>('hepsi');
  const [arama, setArama] = useState('');
  const [saving, setSaving] = useState(false);
  const [bilgiMesaji, setBilgiMesaji] = useState('');
  const [sendingAlerts, setSendingAlerts] = useState(false);

  const yoklamaGetir = async () => {
    try {
      const res = await fetch('/api/belletmen/yoklama');
      const data = await res.json();
      if (data.success && data.data) {
        setOgrenciler(data.data);
      }
    } catch (err) {
      console.error('Yoklama yüklenemedi:', err);
    }
  };

  useEffect(() => {
    yoklamaGetir();
  }, []);

  const durumGuncelle = (id: string, yeniDurum: Ogrenci['durum']) => {
    setOgrenciler(prev => prev.map(ogr => ogr.id === id ? { ...ogr, durum: yeniDurum } : ogr));
  };

  const tumunuBuradaYap = () => {
    setOgrenciler(prev => prev.map(ogr => ogr.durum === 'izinli' ? ogr : { ...ogr, durum: 'burada' }));
  };

  const filtreliOgrenciler = ogrenciler.filter(ogr => {
    const isimEslesir = ogr.adSoyad.toLowerCase().includes(arama.toLowerCase()) || ogr.odaNo.includes(arama);
    const katEslesir = katFiltresi === 'hepsi' || ogr.odaNo.startsWith(katFiltresi);
    return isimEslesir && katEslesir;
  });

  const ozet = {
    toplam: ogrenciler.length,
    burada: ogrenciler.filter(o => o.durum === 'burada').length,
    yok: ogrenciler.filter(o => o.durum === 'yok').length,
    izinli: ogrenciler.filter(o => o.durum === 'izinli').length,
    revir: ogrenciler.filter(o => o.durum === 'revir').length,
  };

  const handleYoklamaKaydet = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/belletmen/yoklama', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seans, records: ogrenciler })
      });
      const data = await res.json();
      if (data.success) {
        setBilgiMesaji(data.message);
        setTimeout(() => setBilgiMesaji(''), 4000);
      }
    } catch {
      setBilgiMesaji('Kayıt sırasında bağlantı hatası oluştu.');
    } finally {
      setSaving(false);
    }
  };

  const handleYokOlanlaraWhatsAppGonder = async () => {
    const yokOlanlar = ogrenciler.filter(o => o.durum === 'yok');
    if (yokOlanlar.length === 0) return;

    setSendingAlerts(true);
    let basarili = 0;

    for (const ogr of yokOlanlar) {
      const seansAdi = seans === 'etut' ? '19:15 Etüt' : '23:00 Yat';
      const mesaj = `Sayın Velimiz, öğrenciniz ${ogr.adSoyad} pansiyonumuzun bu akşamki (${seansAdi}) yoklamasında bulunamamıştır. Lütfen nöbetçi belletmen ile iletişime geçiniz.`;
      
      for (const targetUrl of [TUNNEL_URL, 'http://localhost:3001']) {
        try {
          const res = await fetch(`${targetUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: ogr.veliTelefon, code: mesaj })
          });
          if (res.ok) {
            basarili++;
            break;
          }
        } catch {}
      }
    }

    setSendingAlerts(false);
    setBilgiMesaji(`${basarili} öğrenci velisine WhatsApp uyarısı iletildi.`);
    setTimeout(() => setBilgiMesaji(''), 5000);
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6 pb-24">
      <div className="max-w-4xl mx-auto space-y-6">
        
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md">
              Nöbetçi Belletmen Paneli
            </span>
            <h1 className="text-xl md:text-2xl font-extrabold text-slate-800 mt-1">Pansiyon Akşam Yoklaması</h1>
            <p className="text-xs text-slate-500">Öğrencilerin pansiyon mevcudiyet durumunu anlık işaretleyin.</p>
          </div>

          <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 w-full sm:w-auto">
            <button
              onClick={() => setSeans('etut')}
              className={`flex-1 sm:flex-initial px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                seans === 'etut' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              19:15 Etüt
            </button>
            <button
              onClick={() => setSeans('yat')}
              className={`flex-1 sm:flex-initial px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                seans === 'yat' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              23:00 Yat Yoklaması
            </button>
          </div>
        </div>

        {bilgiMesaji && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-semibold text-center">
            {bilgiMesaji}
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">Mevcut (Burada)</div>
            <div className="text-2xl font-bold text-emerald-600 mt-1">{ozet.burada} / {ozet.toplam}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">Yok / Habersiz</div>
            <div className="text-2xl font-bold text-rose-600 mt-1">{ozet.yok}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">İzinli (Evci)</div>
            <div className="text-2xl font-bold text-blue-600 mt-1">{ozet.izinli}</div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <div className="text-xs text-slate-500 font-medium">Revir / Rapor</div>
            <div className="text-2xl font-bold text-amber-600 mt-1">{ozet.revir}</div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Öğrenci veya Oda No ara..."
              value={arama}
              onChange={(e) => setArama(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="flex gap-2 w-full md:w-auto">
            <select
              value={katFiltresi}
              onChange={(e) => setKatFiltresi(e.target.value)}
              className="text-xs border border-slate-200 rounded-xl px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="hepsi">Tüm Katlar</option>
              <option value="1">1. Kat (100'ler)</option>
              <option value="2">2. Kat (200'ler)</option>
              <option value="3">3. Kat (300'ler)</option>
            </select>

            <button
              onClick={tumunuBuradaYap}
              className="text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-xl transition-all cursor-pointer"
            >
              Kalanları 'Burada' Yap
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {filtreliOgrenciler.map((ogr) => (
            <div
              key={ogr.id}
              className={`bg-white rounded-2xl p-4 border transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm ${
                ogr.durum === 'yok' 
                  ? 'border-rose-300 bg-rose-50/20' 
                  : ogr.durum === 'izinli' 
                  ? 'border-blue-200 bg-blue-50/20' 
                  : 'border-slate-200'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 text-sm">{ogr.adSoyad}</span>
                  <span className="text-[11px] font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md">
                    Oda: {ogr.odaNo}
                  </span>
                  <span className="text-[11px] text-slate-400">{ogr.sinif}</span>
                </div>
                {ogr.izinDetay && (
                  <div className="text-xs text-blue-600 font-medium flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> {ogr.izinDetay}
                  </div>
                )}
              </div>

              <div className="flex items-center gap-1.5 w-full sm:w-auto">
                <button
                  onClick={() => durumGuncelle(ogr.id, 'burada')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'burada'
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <CheckCircle2 className="w-3.5 h-3.5" /> Burada
                </button>

                <button
                  onClick={() => durumGuncelle(ogr.id, 'yok')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'yok'
                      ? 'bg-rose-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <XCircle className="w-3.5 h-3.5" /> Yok
                </button>

                <button
                  onClick={() => durumGuncelle(ogr.id, 'izinli')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'izinli'
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  İzinli
                </button>

                <button
                  onClick={() => durumGuncelle(ogr.id, 'revir')}
                  className={`flex-1 sm:flex-initial px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                    ogr.durum === 'revir'
                      ? 'bg-amber-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  Revir
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200 shadow-lg flex flex-col sm:flex-row justify-between items-center gap-3">
          <div className="text-xs text-slate-500 text-center sm:text-left">
            {ozet.yok > 0 ? (
              <span className="text-rose-600 font-semibold flex items-center gap-1">
                <AlertTriangle className="w-4 h-4 inline" /> {ozet.yok} öğrenci yoklamada bulunamadı!
              </span>
            ) : (
              <span className="text-emerald-600 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4 inline" /> Tüm öğrenciler eksiksiz veya izinli.
              </span>
            )}
          </div>

          <div className="flex gap-2 w-full sm:w-auto">
            {ozet.yok > 0 && (
              <button
                onClick={handleYokOlanlaraWhatsAppGonder}
                disabled={sendingAlerts}
                className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" /> {sendingAlerts ? 'Gönderiliyor...' : `Velilere Bildir (${ozet.yok})`}
              </button>
            )}

            <button
              onClick={handleYoklamaKaydet}
              disabled={saving}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
            >
              <Save className="w-3.5 h-3.5" /> {saving ? 'Kaydediliyor...' : 'Yoklamayı Onayla'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
""".replace('__TUNNEL_URL_PLACEHOLDER__', tunnel_url)

    write_file("app/belletmen/yoklama/page.tsx", yoklama_page)

    # 3. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 4. Derleme & Git Senkronizasyonu
    if not run_command("npm run build", "Next.js derleme testi yapılıyor"):
        print("❌ Derleme hatası! Lütfen terminal çıktısını inceleyin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Belletmen yoklama sayfasi ve string formati duzeltildi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 BELLETMEN YOKLAMA MODÜLÜ BAŞARIYLA DERLENDİ VE GÖNDERİLDİ!")
    print("👉 Yoklama ekranı:")
    print("   https://pansiyon-yurt-sistemi.vercel.app/belletmen/yoklama")
    print("=========================================================")

if __name__ == "__main__":
    main()