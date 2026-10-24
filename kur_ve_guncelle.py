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
        print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

# -------------------------------------------------------------------------
# KURUMSAL VE GÖRSEL OLARAK ZENGİNLEŞTİRİLMİŞ ANA SAYFA (app/page.tsx)
# -------------------------------------------------------------------------
HOME_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Users,
  UserCheck,
  Building2,
  Clock,
  FileText,
  PhoneCall,
  ArrowRight,
  CheckCircle2,
  Calendar,
  Lock,
  Sparkles,
  BookOpen,
  BellRing,
  Award,
  MapPin
} from 'lucide-react';

export default function CorporateHomePage() {
  const [stats, setStats] = useState({
    toplamOgrenci: 8,
    mevcutOgrenci: 4,
    izinliOgrenci: 3,
    belletmenSayisi: 8,
    bugunkuNobetciErkek: 'Cüneyt DEMİR & Ali BEY',
    bugunkuNobetciKadin: 'Ayşenur KAYA & Fatma YILMAZ',
  });

  useEffect(() => {
    const fetchLiveStats = async () => {
      try {
        const res = await fetch('/api/pansiyon');
        const data = await res.json();
        if (data.success && data.store) {
          const st = data.store.students || [];
          const bl = data.store.belletmenler || [];
          const nb = data.store.aylikNobetler || [];
          const todayStr = new Date().toISOString().split('T')[0];
          const todayDuty = nb.find((d: any) => d.tarih === todayStr) || nb[0];

          setStats({
            toplamOgrenci: st.length,
            mevcutOgrenci: st.filter((s: any) => s.status === 'var').length,
            izinliOgrenci: st.filter((s: any) => s.status === 'izinli').length,
            belletmenSayisi: bl.length,
            bugunkuNobetciErkek: todayDuty ? `${todayDuty.erkek1} & ${todayDuty.erkek2}` : 'Cüneyt DEMİR & Ali BEY',
            bugunkuNobetciKadin: todayDuty ? `${todayDuty.kadin1} & ${todayDuty.kadin2}` : 'Ayşenur KAYA & Fatma YILMAZ',
          });
        }
      } catch {}
    };
    fetchLiveStats();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between text-slate-900">
      {/* ÜST KURUMSAL DUYURU ŞERİDİ */}
      <div className="bg-slate-950 text-slate-300 text-[11px] py-2 px-4 border-b border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-semibold text-white">T.C. Millî Eğitim Bakanlığı</span>
            <span className="text-slate-600">|</span>
            <span>Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Öğrenci Pansiyonu</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span className="flex items-center gap-1">
              <BellRing className="w-3.5 h-3.5 text-amber-400" /> WhatsApp Otomasyon Köprüsü: <strong className="text-emerald-400">Aktif</strong>
            </span>
            <span className="hidden md:inline text-slate-600">|</span>
            <span className="hidden md:flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-blue-400" /> Yenibosna, Bahçelievler / İstanbul
            </span>
          </div>
        </div>
      </div>

      {/* ANA NAVİGASYON BAR */}
      <header className="bg-white/90 backdrop-blur-md sticky top-0 z-30 border-b border-slate-200/80 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-900 via-indigo-900 to-slate-900 text-white flex items-center justify-center shadow-md border border-blue-800">
              <Building2 className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-extrabold uppercase tracking-widest px-2 py-0.5 rounded-md bg-blue-50 text-blue-800 border border-blue-200">
                  Resmî Dijital Pansiyon Sistemi
                </span>
              </div>
              <h1 className="text-base sm:text-lg font-extrabold text-slate-900 tracking-tight mt-0.5">
                Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi
              </h1>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-2.5">
            <a
              href="/veli/login"
              className="px-4 py-2 rounded-xl text-xs font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 transition-all"
            >
              Veli Girişi
            </a>
            <a
              href="/belletmen"
              className="px-4 py-2 rounded-xl text-xs font-bold text-blue-800 bg-blue-50 hover:bg-blue-100 border border-blue-200 transition-all"
            >
              Belletmen Portalı
            </a>
            <a
              href="/admin"
              className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 shadow-xs transition-all"
            >
              Yönetici Paneli
            </a>
          </nav>
        </div>
      </header>

      {/* HERO (KARŞILAMA) VE CANLI ÖZET PANELİ */}
      <main className="flex-1">
        <section className="relative overflow-hidden bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 text-white py-12 md:py-16 px-4 sm:px-6 border-b border-slate-800">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            
            {/* Sol Tanıtım Sütunu */}
            <div className="lg:col-span-7 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 border border-white/15 text-amber-300 text-xs font-bold">
                <Sparkles className="w-4 h-4" /> Yeni Nesil Akıllı Pansiyon & Yoklama Otomasyonu
              </div>

              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight leading-tight">
                Güvenli, Şeffaf ve <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-300 to-emerald-300">Anlık WhatsApp</span> Entegreli Pansiyon Yönetimi
              </h2>

              <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
                Öğrencilerimizin huzuru ve güvenliği için geliştirilen dijital pansiyon yönetim platformu; veli izin taleplerini, akşam etüt/yat yoklamalarını ve resmî nöbet defteri süreçlerini tek merkezde buluşturur.
              </p>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <a
                  href="/veli/login"
                  className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold px-6 py-3.5 rounded-2xl text-xs sm:text-sm shadow-lg shadow-emerald-950/50 transition-all"
                >
                  <ShieldCheck className="w-4 h-4" /> Veli WhatsApp Girişi <ArrowRight className="w-4 h-4" />
                </a>
                <a
                  href="/belletmen"
                  className="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white border border-white/20 font-bold px-6 py-3.5 rounded-2xl text-xs sm:text-sm transition-all"
                >
                  <UserCheck className="w-4 h-4 text-blue-300" /> Nöbetçi Belletmen Ekranı
                </a>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/10 text-xs text-slate-300">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Şifresiz WhatsApp OTP Doğrulama</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Otomatik Evci & Çarşı İzin Eşleşmesi</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>MEB Standartlarında Nöbet Tutanağı</span>
                </div>
              </div>
            </div>

            {/* Sağ Canlı Pansiyon Durum Kartı */}
            <div className="lg:col-span-5">
              <div className="bg-white/10 backdrop-blur-xl border border-white/15 rounded-3xl p-6 space-y-5 shadow-2xl">
                <div className="flex items-center justify-between border-b border-white/10 pb-4">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-amber-300">Canlı Pansiyon Panosu</span>
                    <h3 className="text-base font-extrabold text-white mt-0.5">Günlük Yoklama & Nöbet Özeti</h3>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-[11px] font-bold">
                    Canlı Veri
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-900/70 border border-white/10 p-4 rounded-2xl">
                    <span className="text-[11px] text-slate-400">Kayıtlı Pansiyoner</span>
                    <div className="text-2xl font-extrabold text-white mt-1">{stats.toplamOgrenci} Öğrenci</div>
                  </div>
                  <div className="bg-emerald-950/60 border border-emerald-500/30 p-4 rounded-2xl">
                    <span className="text-[11px] text-emerald-300">Pansiyonda Mevcut</span>
                    <div className="text-2xl font-extrabold text-emerald-400 mt-1">{stats.mevcutOgrenci} Öğrenci</div>
                  </div>
                  <div className="bg-amber-950/60 border border-amber-500/30 p-4 rounded-2xl">
                    <span className="text-[11px] text-amber-300">Evci / İzinli</span>
                    <div className="text-2xl font-extrabold text-amber-400 mt-1">{stats.izinliOgrenci} Öğrenci</div>
                  </div>
                  <div className="bg-blue-950/60 border border-blue-500/30 p-4 rounded-2xl">
                    <span className="text-[11px] text-blue-300">Görevli Belletmen</span>
                    <div className="text-2xl font-extrabold text-blue-400 mt-1">{stats.belletmenSayisi} Öğretmen</div>
                  </div>
                </div>

                <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 space-y-2 text-xs">
                  <div className="font-bold text-amber-300 flex items-center gap-1.5">
                    <Calendar className="w-4 h-4" /> Bugünün Nöbetçi Belletmen Öğretmenleri (4 Öğretmen)
                  </div>
                  <div className="flex justify-between text-slate-300 pt-1">
                    <span>👨 Erkek Pansiyonu:</span>
                    <strong className="text-white">{stats.bugunkuNobetciErkek}</strong>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>👩 Kız Pansiyonu:</span>
                    <strong className="text-white">{stats.bugunkuNobetciKadin}</strong>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* 3 ANA MODÜL KARTLARI */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 -mt-8 relative z-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* 1. Veli Portalı Kartı */}
            <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200/90 shadow-xl hover:shadow-2xl transition-all flex flex-col justify-between space-y-6 group">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform">
                    <ShieldCheck className="w-7 h-7" />
                  </div>
                  <span className="text-[11px] font-extrabold uppercase tracking-wider bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full border border-emerald-200">
                    WhatsApp OTP Girişli
                  </span>
                </div>

                <div>
                  <h3 className="text-xl font-extrabold text-slate-900">Veli İzin & Takip Portalı</h3>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    Velilerimiz cep telefonlarına gelen tek kullanımlık WhatsApp kodu ile giriş yaparak öğrencilerinin pansiyon yoklama durumunu görebilir ve izin talebi oluşturabilir.
                  </p>
                </div>

                <ul className="space-y-2 text-xs text-slate-600 pt-2 border-t border-slate-100">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> Hafta sonu evci ve çarşı izni oluşturma
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> Anlık etüt ve gece yat yoklaması takibi
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> Otomatik WhatsApp izin onay bildirimi
                  </li>
                </ul>
              </div>

              <div className="space-y-2 pt-2">
                <a
                  href="/veli/login"
                  className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 rounded-2xl text-xs shadow-sm transition-all"
                >
                  Veli Giriş Ekranına Git <ArrowRight className="w-4 h-4" />
                </a>
                <a
                  href="/veli"
                  className="w-full block text-center text-[11px] font-semibold text-slate-500 hover:text-emerald-700 py-1"
                >
                  Hızlı Veli Paneli Önizlemesi →
                </a>
              </div>
            </div>

            {/* 2. Nöbetçi Belletmen Portalı Kartı */}
            <div className="bg-white rounded-3xl p-6 sm:p-7 border-2 border-blue-600/20 shadow-xl hover:shadow-2xl transition-all flex flex-col justify-between space-y-6 group">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-14 h-14 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform">
                    <UserCheck className="w-7 h-7" />
                  </div>
                  <span className="text-[11px] font-extrabold uppercase tracking-wider bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-200">
                    Erkek / Kız Ayrı Yetki
                  </span>
                </div>

                <div>
                  <h3 className="text-xl font-extrabold text-slate-900">Nöbetçi Belletmen Portalı</h3>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    Erkek belletmenlerin sadece erkek öğrencileri, kadın belletmenlerin sadece kız öğrencileri görüp yoklama alabildiği şifreli nöbet ekranı.
                  </p>
                </div>

                <ul className="space-y-2 text-xs text-slate-600 pt-2 border-t border-slate-100">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" /> 19:15 Etüt ve 23:00 Yat yoklaması modülü
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" /> Yoklamada olmayan öğrencinin velisine tek tıkla mesaj
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" /> 4 Belletmen imzalı Resmî MEB Nöbet Defteri PDF
                  </li>
                </ul>
              </div>

              <div className="space-y-2 pt-2">
                <a
                  href="/belletmen"
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-2xl text-xs shadow-sm transition-all"
                >
                  Belletmen Yoklama Ekranına Git <ArrowRight className="w-4 h-4" />
                </a>
                <span className="w-full block text-center text-[11px] text-slate-400 py-1">
                  Günlük 2 Erkek + 2 Kadın Nöbetçi Öğretmen
                </span>
              </div>
            </div>

            {/* 3. İdare & Yönetici Paneli Kartı */}
            <div className="bg-white rounded-3xl p-6 sm:p-7 border border-slate-200/90 shadow-xl hover:shadow-2xl transition-all flex flex-col justify-between space-y-6 group">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-14 h-14 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center shadow-xs group-hover:scale-105 transition-transform">
                    <Lock className="w-7 h-7" />
                  </div>
                  <span className="text-[11px] font-extrabold uppercase tracking-wider bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full border border-indigo-200">
                    Pansiyon İdaresi
                  </span>
                </div>

                <div>
                  <h3 className="text-xl font-extrabold text-slate-900">Yönetici & İdare Paneli</h3>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    Pansiyon müdür yardımcılığı tarafından öğrenci/oda kayıtlarının, belletmen şifrelerinin ve aylık nöbet listelerinin yönetildiği merkez.
                  </p>
                </div>

                <ul className="space-y-2 text-xs text-slate-600 pt-2 border-t border-slate-100">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0" /> Excel / e-Okul ile toplu öğrenci ve belletmen yükleme
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0" /> Belletmen şifre görüntüleme ve değiştirme
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0" /> Otomatik 30 günlük aylık nöbet çizelgesi dağıtımı
                  </li>
                </ul>
              </div>

              <div className="space-y-2 pt-2">
                <a
                  href="/admin"
                  className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-bold py-3.5 rounded-2xl text-xs shadow-sm transition-all"
                >
                  İdare Yönetim Paneline Git <ArrowRight className="w-4 h-4" />
                </a>
                <span className="w-full block text-center text-[11px] text-slate-400 py-1">
                  Yetkili İdareci Girişi
                </span>
              </div>
            </div>

          </div>
        </section>

        {/* PANSİYON GÜNLÜK ZAMAN ÇİZELGESİ VE KURUMSAL ÖZELLİKLER */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 py-14 space-y-10">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <span className="text-xs font-extrabold uppercase tracking-wider text-blue-700 bg-blue-50 px-3 py-1 rounded-full">
              Pansiyon Günlük Akışı
            </span>
            <h3 className="text-2xl font-extrabold text-slate-900">
              Disiplinli Çalışma ve Güvenli Konaklama Düzeni
            </h3>
            <p className="text-xs sm:text-sm text-slate-500">
              Pansiyonumuzda kalan öğrencilerimizin akademik başarılarını destekleyen günlük etüt, yemek ve yoklama saatleri.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-lg">07:00 - 08:15</span>
                <Clock className="w-4 h-4 text-slate-400" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">Sabah Kahvaltısı & Okula Hazırlık</h4>
              <p className="text-xs text-slate-500">Oda tertip kontrolü, kahvaltı ve ders ziline hazırlık.</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg">17:30 - 19:00</span>
                <Clock className="w-4 h-4 text-slate-400" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">Akşam Yemeği & Serbest Zaman</h4>
              <p className="text-xs text-slate-500">Okul çıkışı dinlenme, yemekhane saatleri ve sosyal etkinlikler.</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border-2 border-blue-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-blue-800 bg-blue-100 px-2.5 py-1 rounded-lg">19:15 - 21:30</span>
                <BookOpen className="w-4 h-4 text-blue-600" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">Akşam Etüdü & 1. Yoklama</h4>
              <p className="text-xs text-slate-500">Nöbetçi belletmenler eşliğinde sessiz bireysel çalışma ve etüt yoklaması.</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border-2 border-indigo-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-indigo-800 bg-indigo-100 px-2.5 py-1 rounded-lg">23:00</span>
                <BellRing className="w-4 h-4 text-indigo-600" />
              </div>
              <h4 className="font-bold text-slate-900 text-sm">Gece Yat Yoklaması & İstirahat</h4>
              <p className="text-xs text-slate-500">Oda bazlı son yoklama kontrolü ve resmî nöbet defterinin kapatılması.</p>
            </div>
          </div>
        </section>
      </main>

      {/* KURUMSAL ALT BİLGİ (FOOTER) */}
      <footer className="bg-slate-950 text-slate-400 border-t border-slate-800 py-8 px-4 sm:px-6 text-xs">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-blue-900 text-amber-400 flex items-center justify-center font-bold">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <p className="font-bold text-white">Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Müdürlüğü</p>
              <p className="text-[11px] text-slate-500">Erkek ve Kız Öğrenci Pansiyonu Dijital Yoklama & İzin Otomasyonu</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-[11px]">
            <a href="/veli/login" className="hover:text-white transition-colors">Veli Girişi</a>
            <span>•</span>
            <a href="/belletmen" className="hover:text-white transition-colors">Belletmen Girişi</a>
            <span>•</span>
            <a href="/admin" className="hover:text-white transition-colors">Yönetici Paneli</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
'''

def main():
    print("=========================================================")
    print("   KURUMSAL VE ZENGİN ANA SAYFA TASARIMI YÜKLENİYOR")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 1. Yeni Kurumsal Ana Sayfayı Yaz
    write_file("app/page.tsx", HOME_PAGE_TSX)

    # 2. Aktif Tünel Adresini API Rotalarında Güncelle
    bildirim_api = f"""import {{ NextResponse }} from 'next/server';

const BOT_URLS = ['{tunnel_url}', 'http://127.0.0.1:3001', 'http://localhost:3001'];

export async function POST(request: Request) {{
  try {{
    const {{ phone, ogrenciAd, odaNo, tarih, seans, veliTipi }} = await request.json();
    if (!phone) {{
      return NextResponse.json({{ success: false, message: 'Telefon numarası eksik.' }}, {{ status: 400 }});
    }}

    let customMessage = '';
    if (seans === 'izin_onay') {{
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz,\\nÖğrenciniz *${{ogrenciAd}}* (Oda: ${{odaNo}}) için *${{tarih}}* tarihli izin talebiniz (*${{veliTipi}}*) onaylanmış ve nöbetçi belletmen yoklama sistemine *Otomatik İzinli* olarak işlenmiştir.`;
    }} else {{
      const seansMetni = seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)';
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz (${{veliTipi || 'Veli'}}),\\nÖğrenciniz *${{ogrenciAd}}* (Oda: ${{odaNo}}), *${{tarih}}* tarihli *${{seansMetni}}* yoklamasında pansiyonda *BULUNAMAMIŞTIR (YOK)*.\\n\\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;
    }}

    let lastError = 'WhatsApp Botuna ulaşılamadı.';
    for (const botUrl of BOT_URLS) {{
      try {{
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(`${{botUrl}}/send-otp`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ phone, customMessage }}),
          signal: controller.signal
        }});
        clearTimeout(tid);

        const data = await res.json();
        if (res.ok && data.success) {{
          return NextResponse.json({{
            success: true,
            message: `✅ ${{ogrenciAd}} velisine (${{phone}}) WhatsApp bildirimi başarıyla gönderildi!`
          }});
        }} else {{
          lastError = data.message || lastError;
        }}
      }} catch (e) {{}}
    }}

    return NextResponse.json({{
      success: false,
      message: lastError,
      customMessage,
      tunnelUrl: '{tunnel_url}'
    }}, {{ status: 200 }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}
"""
    write_file("app/api/belletmen/bildirim/route.ts", bildirim_api)

    # 3. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 4. Derleme ve GitHub/Vercel Gönderimi
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Kurumsal ve zenginlestirilmis ana sayfa tasarimi eklendi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 YENİ KURUMSAL ANA SAYFA CANLIYA ALINDI!")
    print("👉 Ana Sayfa: https://pansiyon-yurt-sistemi.vercel.app")
    print("=========================================================")

if __name__ == "__main__":
    main()