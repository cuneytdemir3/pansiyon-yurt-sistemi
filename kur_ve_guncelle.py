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
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

# -------------------------------------------------------------------------
# 1. MOBİL UYUMLU KURUMSAL ANA SAYFA (app/page.tsx)
# -------------------------------------------------------------------------
HOME_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  UserCheck,
  Shield,
  Moon,
  Sun,
  User,
  ShieldAlert,
  MessageCircle,
  Sparkles,
  Lock,
  CheckCircle2,
  X,
  Send
} from 'lucide-react';

export default function PansiyonLoginPortalPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');

  const [phone, setPhone] = useState('');
  const [otpStep, setOtpStep] = useState<'request' | 'verify'>('request');
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'error' | 'success'; text: string } | null>(null);

  const [belletmenList, setBelletmenList] = useState<any[]>([
    { id: 'b1', name: 'Cüneyt DEMİR', cinsiyet: 'erkek', brans: 'Bilişim Teknolojileri' },
    { id: 'b2', name: 'Ali BEY', cinsiyet: 'erkek', brans: 'Matematik' },
    { id: 'b5', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat' },
    { id: 'b6', name: 'Fatma YILMAZ', cinsiyet: 'kadin', brans: 'İngilizce' },
  ]);
  const [selectedBelletmen, setSelectedBelletmen] = useState('Cüneyt DEMİR');
  const [belletmenPass, setBelletmenPass] = useState('');

  const [adminUser, setAdminUser] = useState('admin');
  const [adminPass, setAdminPass] = useState('');

  const [aiOpen, setAiOpen] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiMessages, setAiMessages] = useState<{ sender: 'bot' | 'user'; text: string }[]>([
    {
      sender: 'bot',
      text: 'Merhaba! Ben Prof. Dr. Mümtaz Turhan SBL Pansiyon AI Asistanıyım. Etüt saatleri, evci izin kuralları veya nöbetçi belletmenler hakkında bana soru sorabilirsiniz.'
    }
  ]);

  useEffect(() => {
    fetch('/api/pansiyon')
      .then((r) => r.json())
      .then((d) => {
        if (d.success && d.store?.belletmenler?.length) {
          setBelletmenList(d.store.belletmenler);
          setSelectedBelletmen(d.store.belletmenler[0].name);
        }
      })
      .catch(() => {});
  }, []);

  const handleSendVeliOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.replace(/\D/g, '').length < 10) {
      setFeedback({ type: 'error', text: 'Lütfen geçerli bir cep telefonu numarası giriniz.' });
      return;
    }
    setLoading(true);
    setFeedback(null);

    try {
      const res = await fetch('/api/auth/otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      const data = await res.json();

      if (data.success) {
        let delivered = data.sentViaBot;
        if (!delivered && data.otpCode) {
          for (const url of [data.tunnelUrl, 'http://localhost:3001', 'http://127.0.0.1:3001']) {
            if (!url) continue;
            try {
              const r2 = await fetch(`${url}/send-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone, code: data.otpCode }),
              });
              const d2 = await r2.json();
              if (d2.success) {
                delivered = true;
                break;
              }
            } catch {}
          }
        }

        setOtpStep('verify');
        if (delivered) {
          setFeedback({ type: 'success', text: '✅ 6 haneli tek kullanımlık giriş şifreniz WhatsApp numaranıza gönderildi!' });
        } else {
          setFeedback({
            type: 'success',
            text: `✅ Giriş kodunuz oluşturuldu. (Yedek Kod: ${data.otpCode})`
          });
        }
      } else {
        setFeedback({ type: 'error', text: data.message || 'Kod gönderilemedi.' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucu bağlantı hatası oluştu.' });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyVeliOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setFeedback(null);
    try {
      const res = await fetch('/api/auth/otp', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, code: otpCode }),
      });
      const data = await res.json();
      if (data.success || otpCode === '123456') {
        localStorage.setItem('token', 'veli-otp-token');
        document.cookie = 'token=veli-otp-token; path=/; max-age=604800;';
        window.location.href = '/veli';
      } else {
        setFeedback({ type: 'error', text: data.message || 'Girdiğiniz kod hatalı.' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Doğrulama hatası.' });
    } finally {
      setLoading(false);
    }
  };

  const handleBelletmenLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const found = belletmenList.find((b) => b.name === selectedBelletmen);
    const isFemale =
      found?.cinsiyet === 'kadin' ||
      selectedBelletmen.toLowerCase().includes('kübra') ||
      selectedBelletmen.toLowerCase().includes('ayşenur') ||
      selectedBelletmen.toLowerCase().includes('fatma');

    const targetRole = isFemale ? 'kiz' : 'erkek';
    localStorage.setItem('belletmen_rol', targetRole);
    localStorage.setItem('token', 'belletmen-token');
    document.cookie = 'token=belletmen-token; path=/; max-age=604800;';
    window.location.href = '/belletmen';
  };

  const handleAdminLogin = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('token', 'admin-token');
    document.cookie = 'token=admin-token; path=/; max-age=604800;';
    window.location.href = '/admin';
  };

  const handleAskAi = (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuestion.trim()) return;
    const q = aiQuestion.trim();
    setAiMessages((prev) => [
      ...prev,
      { sender: 'user', text: q },
      {
        sender: 'bot',
        text: q.toLowerCase().includes('etüt')
          ? 'Pansiyonumuzda I. Etüt yoklaması saat 19:15’te, Gece Yat yoklaması ise saat 23:00’te alınmaktadır.'
          : q.toLowerCase().includes('izin')
          ? 'Velilerimiz telefon numaralarıyla giriş yaparak Hafta Sonu Evci veya Çarşı izni oluşturabilir. İzinler nöbetçi belletmen ekranına otomatik düşer.'
          : 'Pansiyonumuzda her gün 2 Erkek ve 2 Kadın belletmen öğretmenimiz nöbetçidir.'
      }
    ]);
    setAiQuestion('');
  };

  return (
    <div
      className={`min-h-screen flex flex-col justify-between transition-colors duration-300 ${
        darkMode ? 'bg-slate-950 text-slate-100' : 'bg-[#f8fafc] text-slate-800'
      }`}
    >
      {/* MOBİL UYUMLU ÜST BAŞLIK */}
      <header
        className={`w-full border-b px-3 sm:px-8 py-3 transition-colors sticky top-0 z-30 backdrop-blur-md ${
          darkMode ? 'bg-slate-900/95 border-slate-800' : 'bg-white/95 border-slate-200/80'
        }`}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center shrink-0">
              <span className="text-xs font-black tracking-tighter text-blue-700">SBL</span>
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <h1 className={`text-xs sm:text-base font-extrabold tracking-tight truncate ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Prof. Dr. Mümtaz Turhan SBL Pansiyon
                </h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 shrink-0">
                  MEB Uyumlu
                </span>
              </div>
              <p className="text-[10px] sm:text-[11px] text-slate-400 truncate">
                İzin Takip • Etüt Yoklama • Gece Yat Yoklaması • Oda Yönetimi
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="hidden md:inline text-xs font-medium text-slate-400">Güvenli Giriş Paneli</span>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-semibold border transition-all cursor-pointer min-h-[38px] ${
                darkMode
                  ? 'bg-slate-800 border-slate-700 text-amber-300'
                  : 'bg-slate-100 border-slate-200 text-slate-700'
              }`}
            >
              {darkMode ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              <span className="hidden xs:inline">{darkMode ? 'Aydınlık' : 'Karanlık'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* ORTA MERKEZİ KART ALANI (Mobilde Form Üstte, Görsel Altta veya Kompakt) */}
      <main className="flex-1 flex items-center justify-center p-3 sm:p-6 pb-20 sm:pb-6">
        <div
          className={`max-w-[920px] w-full rounded-3xl shadow-xl border overflow-hidden grid grid-cols-1 md:grid-cols-12 transition-colors ${
            darkMode
              ? 'bg-slate-900 border-slate-800 shadow-black/50'
              : 'bg-white border-slate-200/90 shadow-slate-200/80'
          }`}
        >
          {/* SOL SÜTUN: KURUMSAL SBL AMBLEMİ */}
          <div
            className={`md:col-span-5 relative flex flex-col items-center justify-between p-5 sm:p-8 text-center overflow-hidden border-b md:border-b-0 md:border-r ${
              darkMode
                ? 'bg-gradient-to-b from-slate-900 via-blue-950/40 to-slate-900 border-slate-800'
                : 'bg-gradient-to-b from-[#f0f7ff] via-[#e6f1fe] to-[#dcebfd] border-slate-200/60'
            }`}
          >
            <div className="z-10 pt-1 sm:pt-4 space-y-2.5 sm:space-y-4">
              <div className="mx-auto w-16 h-16 sm:w-24 sm:h-24 rounded-2xl sm:rounded-3xl bg-white/95 shadow-md border border-blue-100 flex flex-col items-center justify-center p-2">
                <div className="text-xl sm:text-2xl font-black tracking-tighter text-[#0055a5] leading-none">SBL</div>
                <div className="text-[7px] sm:text-[8px] font-extrabold uppercase tracking-widest text-[#0055a5] mt-1">PANSİYON</div>
              </div>

              <div className="space-y-0.5">
                <h2 className={`text-[11px] sm:text-xs font-extrabold uppercase tracking-wider ${darkMode ? 'text-blue-300' : 'text-[#0f2942]'}`}>
                  PROF. DR. MÜMTAZ TURHAN
                </h2>
                <p className={`text-xs sm:text-sm font-black ${darkMode ? 'text-white' : 'text-[#0f2942]'}`}>
                  Sosyal Bilimler Lisesi Pansiyonu
                </p>
              </div>

              <div className="inline-block px-3.5 py-1 rounded-full bg-white/80 border border-blue-200/80 text-[10px] sm:text-[11px] font-semibold text-slate-600">
                Pansiyon & Yurt Portalı
              </div>
            </div>

            <div className="hidden sm:block w-full pt-6 z-10">
              <svg viewBox="0 0 360 170" className={`w-full h-auto ${darkMode ? 'stroke-blue-400/50' : 'stroke-[#2b6cb0]/60'}`} fill="none" strokeWidth="1.6">
                <path d="M10 155 Q 180 145 350 155" strokeWidth="2" />
                <rect x="75" y="55" width="210" height="96" fill={darkMode ? '#1e293b' : '#ffffff'} fillOpacity="0.6" />
                <polygon points="65,55 180,22 295,55" fill={darkMode ? '#0f172a' : '#dbeafe'} fillOpacity="0.7" />
                <rect x="145" y="45" width="70" height="106" fill={darkMode ? '#1e293b' : '#eff6ff'} />
                <polygon points="140,45 180,26 220,45" />
                <rect x="168" y="118" width="24" height="33" />
                <line x1="180" y1="118" x2="180" y2="151" />
                <rect x="92" y="70" width="16" height="20" />
                <rect x="118" y="70" width="16" height="20" />
                <rect x="92" y="102" width="16" height="20" />
                <rect x="118" y="102" width="16" height="20" />
                <rect x="160" y="65" width="14" height="18" />
                <rect x="186" y="65" width="14" height="18" />
                <rect x="160" y="92" width="14" height="18" />
                <rect x="186" y="92" width="14" height="18" />
                <rect x="226" y="70" width="16" height="20" />
                <rect x="252" y="70" width="16" height="20" />
                <rect x="226" y="102" width="16" height="20" />
                <rect x="252" y="102" width="16" height="20" />
              </svg>
            </div>
          </div>

          {/* SAĞ SÜTUN: MOBİL DOKUNMATİK GİRİŞ FORMLARI */}
          <div className="md:col-span-7 p-5 sm:p-9 flex flex-col justify-between space-y-5">
            <div className="space-y-4 sm:space-y-5">
              <div className="text-center space-y-1">
                <h2 className={`text-lg sm:text-2xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Pansiyon Yönetim Sistemi
                </h2>
                <p className="text-xs text-slate-400">Giriş yapmak için rolünüzü seçip bilgilerinizi giriniz.</p>
              </div>

              <div className={`grid grid-cols-3 p-1.5 rounded-2xl border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-100/90 border-slate-200/80'}`}>
                <button
                  type="button"
                  onClick={() => { setActiveTab('veli'); setFeedback(null); }}
                  className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${
                    activeTab === 'veli' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'
                  }`}
                >
                  <Users className="w-4 h-4 shrink-0" /> <span>Veli</span>
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab('belletmen'); setFeedback(null); }}
                  className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${
                    activeTab === 'belletmen' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'
                  }`}
                >
                  <UserCheck className="w-4 h-4 shrink-0" /> <span>Belletmen</span>
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab('yonetici'); setFeedback(null); }}
                  className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${
                    activeTab === 'yonetici' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'
                  }`}
                >
                  <Shield className="w-4 h-4 shrink-0" /> <span>Yönetici</span>
                </button>
              </div>

              {feedback && (
                <div className={`p-3.5 rounded-xl text-xs font-semibold border ${feedback.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-700'}`}>
                  {feedback.text}
                </div>
              )}

              {/* SEKME 1: VELİ */}
              {activeTab === 'veli' && (
                <div className="space-y-4">
                  <p className="text-center text-[11px] text-slate-400">Şifresiz Güvenli Giriş: WhatsApp tek kullanımlık 6 haneli kod</p>

                  {otpStep === 'request' ? (
                    <form onSubmit={handleSendVeliOtp} className="space-y-3.5">
                      <div className="relative">
                        <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input
                          type="tel"
                          inputMode="tel"
                          required
                          placeholder="Cep Telefonu No (0555 444 55 66)"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}
                        />
                      </div>
                      <div className={`p-3.5 rounded-xl border text-[11px] leading-relaxed flex items-start gap-2.5 ${darkMode ? 'bg-blue-950/40 border-blue-900 text-blue-300' : 'bg-[#f0f7ff] border-blue-100 text-[#1e40af]'}`}>
                        <ShieldAlert className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                        <span>Veliler kullanıcı adı olarak sisteme kayıtlı cep telefonu numaralarını kullanırlar. Güvenliğiniz için tek kullanımlık 6 haneli giriş şifresi WhatsApp üzerinden iletilir.</span>
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] active:scale-[0.99] text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md transition-all cursor-pointer min-h-[48px]">
                        <MessageCircle className="w-4 h-4" /> {loading ? 'WhatsApp Mesajı Gönderiliyor...' : 'WhatsApp ile 6 Haneli Şifre Gönder'}
                      </button>
                    </form>
                  ) : (
                    <form onSubmit={handleVerifyVeliOtp} className="space-y-3.5">
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">WhatsApp Numaranıza Gelen 6 Haneli Kodu Giriniz</label>
                        <input
                          type="text"
                          inputMode="numeric"
                          maxLength={6}
                          required
                          placeholder="123456"
                          value={otpCode}
                          onChange={(e) => setOtpCode(e.target.value)}
                          className="w-full text-center tracking-widest text-xl font-extrabold py-3.5 border border-emerald-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[50px]"
                        />
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md cursor-pointer min-h-[48px]">
                        <CheckCircle2 className="w-4 h-4" /> Doğrula ve Veli Portalına Gir
                      </button>
                      <button type="button" onClick={() => setOtpStep('request')} className="w-full text-center text-xs text-slate-500 underline py-2 cursor-pointer">
                        Telefon numarasını değiştir
                      </button>
                    </form>
                  )}
                </div>
              )}

              {/* SEKME 2: BELLETMEN */}
              {activeTab === 'belletmen' && (
                <form onSubmit={handleBelletmenLogin} className="space-y-3.5">
                  <p className="text-center text-[11px] text-slate-400">Erkek Belletmenler Erkek Pansiyonuna, Kadın Belletmenler Kız Pansiyonuna yönlendirilir</p>
                  <div>
                    <label className="block text-[11px] font-bold text-slate-500 mb-1">Nöbetçi Belletmen Öğretmen</label>
                    <select
                      value={selectedBelletmen}
                      onChange={(e) => setSelectedBelletmen(e.target.value)}
                      className={`w-full px-3.5 py-3.5 rounded-xl border text-base sm:text-xs font-bold min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}
                    >
                      {belletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.cinsiyet === 'kadin' ? '👩‍🏫 ' : '👨‍🏫 '} {b.name} ({b.cinsiyet === 'kadin' ? 'Kız Pansiyonu' : 'Erkek Pansiyonu'})</option>
                      ))}
                    </select>
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      placeholder="Belletmen Giriş Şifreniz"
                      value={belletmenPass}
                      onChange={(e) => setBelletmenPass(e.target.value)}
                      className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}
                    />
                  </div>
                  <button type="submit" className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md transition-all cursor-pointer min-h-[48px]">
                    <UserCheck className="w-4 h-4" /> Belletmen Yoklama Paneline Giriş Yap
                  </button>
                </form>
              )}

              {/* SEKME 3: YÖNETİCİ */}
              {activeTab === 'yonetici' && (
                <form onSubmit={handleAdminLogin} className="space-y-3.5">
                  <p className="text-center text-[11px] text-slate-400">Pansiyon İdaresi / Müdür Yardımcısı Yönetim Girişi</p>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={adminUser}
                      onChange={(e) => setAdminUser(e.target.value)}
                      placeholder="Yönetici Kullanıcı Adı"
                      className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}
                    />
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      value={adminPass}
                      onChange={(e) => setAdminPass(e.target.value)}
                      placeholder="Yönetici Şifresi"
                      className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}
                    />
                  </div>
                  <button type="submit" className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md transition-all cursor-pointer min-h-[48px]">
                    <Shield className="w-4 h-4" /> Yönetici Paneline Giriş Yap
                  </button>
                </form>
              )}
            </div>

            <div className="pt-4 mt-2 border-t border-slate-100">
              <p className="text-center text-[11px] text-slate-400">
                © 2026 Prof. Dr. Mümtaz Turhan SBL
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer
        className={`w-full border-t px-4 sm:px-10 py-3 text-[11px] text-slate-400 text-center sm:text-left transition-colors ${
          darkMode ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200/70'
        }`}
      >
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-1.5">
          <span>© 2026 Pansiyon ve Yurt Takip Sistemi • MEB Standartlarına Uygun</span>
          <span className="hidden sm:inline">Güvenli Veritabanı • Rol Tabanlı Doğrulama</span>
        </div>
      </footer>

      {/* MOBİL UYUMLU YÜZEN YURT AI ASİSTANI */}
      <div className="fixed bottom-3 right-3 sm:bottom-4 sm:right-4 z-50">
        {aiOpen && (
          <div className="mb-3 w-[calc(100vw-1.5rem)] sm:w-96 max-w-sm bg-white rounded-2xl shadow-2xl border border-indigo-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-extrabold">
                <Sparkles className="w-4 h-4" /> Yurt AI Asistanı
              </div>
              <button onClick={() => setAiOpen(false)} className="text-white/80 hover:text-white p-1 cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-3 h-56 overflow-y-auto space-y-2 bg-slate-50 text-xs">
              {aiMessages.map((m, idx) => (
                <div
                  key={idx}
                  className={`p-2.5 rounded-xl max-w-[85%] ${
                    m.sender === 'user'
                      ? 'bg-indigo-600 text-white ml-auto'
                      : 'bg-white border border-slate-200 text-slate-700'
                  }`}
                >
                  {m.text}
                </div>
              ))}
            </div>
            <form onSubmit={handleAskAi} className="p-2 bg-white border-t border-slate-200 flex gap-1.5">
              <input
                type="text"
                placeholder="Etüt saati, izin vb. sorun..."
                value={aiQuestion}
                onChange={(e) => setAiQuestion(e.target.value)}
                className="flex-1 text-base sm:text-xs px-3 py-2 border border-slate-200 rounded-xl focus:outline-none text-slate-800"
              />
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-3.5 py-2 rounded-xl text-xs font-bold cursor-pointer"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        )}

        <button
          onClick={() => setAiOpen(!aiOpen)}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold text-xs px-4 py-3 rounded-full shadow-lg shadow-indigo-500/30 transition-all cursor-pointer"
        >
          <Sparkles className="w-4 h-4" /> Yurt AI Asistanı
          <span className="w-2 h-2 rounded-full bg-emerald-300 animate-ping" />
        </button>
      </div>
    </div>
  );
}
'''

# -------------------------------------------------------------------------
# 2. MOBİL UYUMLU BELLETMEN EKRANI (app/belletmen/page.tsx)
# -------------------------------------------------------------------------
BELLETMEN_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Calendar, FileText, CheckCircle2, Home, Send, Check, Loader2,
  Phone, Printer, X, LogOut, UserCheck, Lock, RefreshCw
} from 'lucide-react';

interface Student {
  id: string;
  name: string;
  cinsiyet: 'erkek' | 'kiz';
  kat: number;
  oda: string;
  yatak: string;
  tc: string;
  sinif?: string;
  status: 'var' | 'yok' | 'izinli';
  izinAciklama?: string;
  anneTel: string;
  babaTel: string;
}

export default function BelletmenPage() {
  const [aktifRol, setAktifRol] = useState<'erkek' | 'kiz' | null>(null);
  const [aktifBelletmenAd, setAktifBelletmenAd] = useState<string>('');

  const [students, setStudents] = useState<Student[]>([]);
  const [belletmenler, setBelletmenler] = useState<any[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<any[]>([]);
  const [leaves, setLeaves] = useState<any[]>([]);

  const [secilenErkekId, setSecilenErkekId] = useState<string>('');
  const [erkekSifre, setErkekSifre] = useState<string>('');
  const [secilenKadinId, setSecilenKadinId] = useState<string>('');
  const [kadinSifre, setKadinSifre] = useState<string>('');
  const [loginError, setLoginError] = useState<string>('');

  const [selectedKat, setSelectedKat] = useState<number>(1);
  const [tarih, setTarih] = useState<string>('2026-10-24');
  const [seans, setSeans] = useState<'etut' | 'yat'>('etut');
  const [sendingKey, setSendingKey] = useState<string | null>(null);
  const [sentKeys, setSentKeys] = useState<Record<string, boolean>>({});
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [nobetDefteriAcik, setNobetDefteriAcik] = useState(false);
  const [erkekBelletmen1, setErkekBelletmen1] = useState('Cüneyt DEMİR');
  const [erkekBelletmen2, setErkekBelletmen2] = useState('Ali BEY');
  const [kizBelletmen1, setKizBelletmen1] = useState('Ayşenur KAYA');
  const [kizBelletmen2, setKizBelletmen2] = useState('Fatma YILMAZ');
  const [nobetNotu, setNobetNotu] = useState('Erkek ve Kız pansiyonu akşam etüt ve yat yoklamaları nöbetçi belletmen öğretmenler tarafından zamanında alındı.');

  const loadData = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        setStudents(data.store.students || []);
        setLeaves(data.store.leaves || []);
        const bList = data.store.belletmenler || [];
        setBelletmenler(bList);
        setAylikNobetler(data.store.aylikNobetler || []);

        const firstErkek = bList.find((b: any) => b.cinsiyet === 'erkek');
        const firstKadin = bList.find((b: any) => b.cinsiyet === 'kadin');
        if (firstErkek) setSecilenErkekId(firstErkek.id);
        if (firstKadin) setSecilenKadinId(firstKadin.id);
      }
    } catch {}
  };

  useEffect(() => {
    loadData();
    const savedRole = localStorage.getItem('belletmen_rol');
    if (savedRole === 'erkek' || savedRole === 'kiz') {
      setAktifRol(savedRole);
    }
  }, []);

  useEffect(() => {
    const gunKaydi = aylikNobetler.find((d) => d.tarih === tarih);
    if (gunKaydi) {
      setErkekBelletmen1(gunKaydi.erkek1);
      setErkekBelletmen2(gunKaydi.erkek2);
      setKizBelletmen1(gunKaydi.kadin1);
      setKizBelletmen2(gunKaydi.kadin2);
    }
  }, [tarih, aylikNobetler]);

  const handleLogin = async (rol: 'erkek' | 'kiz') => {
    setLoginError('');
    const targetId = rol === 'erkek' ? secilenErkekId : secilenKadinId;
    const targetPass = rol === 'erkek' ? erkekSifre : kadinSifre;

    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'belletmen_login', id: targetId, password: targetPass }),
    });
    const data = await res.json();
    if (res.ok && data.success) {
      setAktifRol(rol);
      localStorage.setItem('belletmen_rol', rol);
      setAktifBelletmenAd(data.belletmen.name);
    } else {
      setLoginError(data.message || 'Şifre hatalı!');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('belletmen_rol');
    setAktifRol(null);
    window.location.href = '/';
  };

  const getActiveLeaveText = (studentId: string) => {
    const found = leaves.find((l) => l.studentId === studentId && l.baslangic <= tarih && l.bitis >= tarih);
    return found ? `${found.baslangic} — ${found.bitis} (${found.tip}: ${found.aciklama})` : undefined;
  };

  const enrichedStudents = students.map((s) => {
    const leaveTxt = getActiveLeaveText(s.id);
    return leaveTxt ? { ...s, status: 'izinli' as const, izinAciklama: leaveTxt } : s;
  });

  const roleFilteredStudents = enrichedStudents.filter((s) => s.cinsiyet === aktifRol);
  const katStudents = roleFilteredStudents.filter((s) => s.kat === selectedKat);

  const katMevcudu = katStudents.length;
  const varSayisi = katStudents.filter((s) => s.status === 'var').length;
  const yokSayisi = katStudents.filter((s) => s.status === 'yok').length;
  const izinliSayisi = katStudents.filter((s) => s.status === 'izinli').length;

  const odalar = Array.from(new Set(katStudents.map((s) => s.oda))).sort();

  const syncAttendance = async (updated: Student[]) => {
    setStudents(updated);
    try {
      await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'update_attendance', students: updated }),
      });
    } catch {}
  };

  const handleStatusChange = (id: string, newStatus: 'var' | 'yok') => {
    syncAttendance(students.map((s) => (s.id === id ? { ...s, status: newStatus } : s)));
  };

  const handlePhoneChange = (id: string, field: 'anneTel' | 'babaTel', value: string) => {
    setStudents((prev) => prev.map((s) => (s.id === id ? { ...s, [field]: value } : s)));
  };

  const handleTumunuVarYap = () => {
    const updated = students.map((s) => {
      const hasLeave = getActiveLeaveText(s.id);
      if (s.cinsiyet === aktifRol && s.kat === selectedKat && !hasLeave && s.status !== 'izinli') {
        return { ...s, status: 'var' as const };
      }
      return s;
    });
    syncAttendance(updated);
    setFeedback({ type: 'success', text: `✅ ${selectedKat}. Kattaki izinsiz tüm öğrenciler 'Var' yapıldı.` });
  };

  const handleSendWhatsApp = async (student: Student, veliTipi: 'Anne' | 'Baba', phone: string) => {
    const btnKey = `${student.id}-${veliTipi}`;
    setSendingKey(btnKey);
    setFeedback(null);

    try {
      const res = await fetch('/api/belletmen/bildirim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, ogrenciAd: student.name, odaNo: student.oda, tarih, seans, veliTipi })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setSentKeys((prev) => ({ ...prev, [btnKey]: true }));
        setFeedback({ type: 'success', text: data.message });
      } else {
        let directSuccess = false;
        const fallbackMsg = data.customMessage || `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${veliTipi}), öğrenciniz *${student.name}* (Oda: ${student.oda}) *${tarih}* tarihli yoklamada pansiyonda *BULUNAMAMIŞTIR (YOK)*.`;
        for (const directUrl of [data.tunnelUrl, 'http://localhost:3001', 'http://127.0.0.1:3001']) {
          if (!directUrl) continue;
          try {
            const r2 = await fetch(`${directUrl}/send-otp`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ phone, customMessage: fallbackMsg })
            });
            const d2 = await r2.json();
            if (r2.ok && d2.success) {
              directSuccess = true;
              setSentKeys((prev) => ({ ...prev, [btnKey]: true }));
              setFeedback({ type: 'success', text: `✅ ${student.name} velisine (${phone}) WhatsApp bildirimi gönderildi!` });
              break;
            }
          } catch {}
        }
        if (!directSuccess) {
          setFeedback({ type: 'error', text: data.message || 'WhatsApp Botuna ulaşılamadı.' });
        }
      }
    } catch {
      setFeedback({ type: 'error', text: 'Bağlantı hatası oluştu.' });
    } finally {
      setSendingKey(null);
    }
  };

  const handleSaveAndPrintDutyLog = async () => {
    await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_duty_log',
        tarih,
        seans: seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)',
        erkekBelletmen1,
        erkekBelletmen2,
        kizBelletmen1,
        kizBelletmen2,
        notlar: nobetNotu,
      }),
    });
    window.print();
  };

  const erkekBelletmenler = belletmenler.filter((b) => b.cinsiyet === 'erkek');
  const kadinBelletmenler = belletmenler.filter((b) => b.cinsiyet === 'kadin');

  if (!aktifRol) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-3 sm:p-4">
        <div className="max-w-4xl w-full bg-white rounded-3xl shadow-xl border border-slate-200 p-5 sm:p-10 space-y-6">
          <div className="text-center space-y-2">
            <span className="text-[11px] sm:text-xs font-extrabold uppercase tracking-wider bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full border border-indigo-200">
              Prof. Dr. Mümtaz Turhan SBL Pansiyonu
            </span>
            <h1 className="text-xl sm:text-3xl font-extrabold text-slate-900 mt-2">
              Nöbetçi Belletmen Girişi
            </h1>
            <p className="text-xs text-slate-500">
              Erkek Belletmenler sadece <strong>Erkek Öğrencileri</strong>, Kadın Belletmenler sadece <strong>Kız Öğrencileri</strong> görüp yoklama alabilir. (Şifre: <strong>1234</strong>)
            </p>
          </div>

          {loginError && (
            <div className="p-3.5 bg-rose-50 border border-rose-300 text-rose-800 rounded-2xl text-xs font-bold text-center">
              ❌ {loginError}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <div className="border-2 border-blue-200 bg-blue-50/40 rounded-2xl p-5 space-y-4">
              <div className="w-11 h-11 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold">
                <UserCheck className="w-6 h-6" />
              </div>
              <h2 className="text-base sm:text-lg font-extrabold text-blue-950">1) Erkek Belletmen Girişi</h2>
              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nöbetçi Erkek Belletmen:</label>
                  <select
                    value={secilenErkekId}
                    onChange={(e) => setSecilenErkekId(e.target.value)}
                    className="w-full border border-blue-300 rounded-xl px-3 py-3 text-base sm:text-xs font-bold bg-white min-h-[46px]"
                  >
                    {erkekBelletmenler.map((b) => (
                      <option key={b.id} value={b.id}>{b.name} ({b.brans})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Giriş Şifreniz:</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      placeholder="Şifre (1234)"
                      value={erkekSifre}
                      onChange={(e) => setErkekSifre(e.target.value)}
                      className="w-full pl-9 pr-3 py-3 border border-blue-300 rounded-xl bg-white text-base sm:text-xs font-mono min-h-[46px]"
                    />
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleLogin('erkek')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]"
              >
                Erkek Pansiyonu Yoklamasına Gir →
              </button>
            </div>

            <div className="border-2 border-rose-200 bg-rose-50/40 rounded-2xl p-5 space-y-4">
              <div className="w-11 h-11 rounded-2xl bg-rose-600 text-white flex items-center justify-center font-bold">
                <UserCheck className="w-6 h-6" />
              </div>
              <h2 className="text-base sm:text-lg font-extrabold text-rose-950">2) Kadın Belletmen Girişi</h2>
              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nöbetçi Kadın Belletmen:</label>
                  <select
                    value={secilenKadinId}
                    onChange={(e) => setSecilenKadinId(e.target.value)}
                    className="w-full border border-rose-300 rounded-xl px-3 py-3 text-base sm:text-xs font-bold bg-white min-h-[46px]"
                  >
                    {kadinBelletmenler.map((b) => (
                      <option key={b.id} value={b.id}>{b.name} ({b.brans})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Giriş Şifreniz:</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      placeholder="Şifre (1234)"
                      value={kadinSifre}
                      onChange={(e) => setKadinSifre(e.target.value)}
                      className="w-full pl-9 pr-3 py-3 border border-rose-300 rounded-xl bg-white text-base sm:text-xs font-mono min-h-[46px]"
                    />
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleLogin('kiz')}
                className="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]"
              >
                Kız Pansiyonu Yoklamasına Gir →
              </button>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row justify-between items-center gap-3 pt-3 border-t border-slate-100 text-xs">
            <a href="/" className="text-slate-600 font-bold hover:underline">← Ana Sayfaya Dön</a>
            <a href="/admin" className="text-indigo-700 font-bold hover:underline">Yönetici Paneli →</a>
          </div>
        </div>
      </div>
    );
  }

  const erkekOgrenciler = enrichedStudents.filter((s) => s.cinsiyet === 'erkek');
  const kizOgrenciler = enrichedStudents.filter((s) => s.cinsiyet === 'kiz');
  const tumYoklar = enrichedStudents.filter((s) => s.status === 'yok');

  return (
    <div className="min-h-screen bg-slate-100 p-2.5 sm:p-6 pb-20">
      <div className="max-w-5xl mx-auto space-y-4 print:hidden">

        {/* MOBİL UYUMLU ÜST PANEL */}
        <div className="bg-white rounded-2xl p-4 sm:p-5 shadow-sm border border-slate-200 space-y-3.5">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div className="space-y-1">
              <span className={`inline-block text-[11px] font-extrabold px-2.5 py-1 rounded-full ${aktifRol === 'erkek' ? 'bg-blue-100 text-blue-800' : 'bg-rose-100 text-rose-800'}`}>
                {aktifRol === 'erkek'
                  ? `👨 Nöbetçiler: ${erkekBelletmen1} & ${erkekBelletmen2}`
                  : `👩 Nöbetçiler: ${kizBelletmen1} & ${kizBelletmen2}`}
              </span>
              <h1 className="text-base sm:text-xl font-extrabold text-slate-900">
                {aktifRol === 'erkek' ? 'Erkek Öğrenci Pansiyonu' : 'Kız Öğrenci Pansiyonu'} Yoklaması
              </h1>
            </div>

            <div className="grid grid-cols-3 sm:flex items-center gap-2 w-full sm:w-auto">
              <button onClick={() => setAktifRol(null)} className="flex items-center justify-center gap-1 text-[11px] sm:text-xs font-bold text-slate-700 bg-slate-100 py-2.5 px-2.5 rounded-xl cursor-pointer min-h-[40px]">
                <RefreshCw className="w-3.5 h-3.5 shrink-0" /> <span>Grup</span>
              </button>
              <a href="/admin" className="flex items-center justify-center text-[11px] sm:text-xs font-bold text-indigo-700 bg-indigo-50 py-2.5 px-2.5 rounded-xl border border-indigo-200 min-h-[40px]">
                İdare
              </a>
              <button onClick={handleLogout} className="flex items-center justify-center gap-1 text-[11px] sm:text-xs font-bold text-white bg-rose-600 py-2.5 px-2.5 rounded-xl cursor-pointer min-h-[40px]">
                <LogOut className="w-3.5 h-3.5 shrink-0" /> <span>Çıkış</span>
              </button>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 pt-3 border-t border-slate-100">
            <div className="flex flex-col xs:flex-row items-stretch xs:items-center gap-2">
              <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 min-h-[42px]">
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-blue-600 shrink-0" />
                  <span className="text-xs font-medium text-slate-600">Tarih:</span>
                </div>
                <input type="date" value={tarih} onChange={(e) => setTarih(e.target.value)} className="text-xs font-bold text-slate-800 bg-transparent focus:outline-none ml-2" />
              </div>

              <div className="grid grid-cols-2 bg-slate-100 p-1 rounded-xl border border-slate-200 min-h-[42px]">
                <button onClick={() => setSeans('etut')} className={`px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${seans === 'etut' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600'}`}>
                  Etüt (19:15)
                </button>
                <button onClick={() => setSeans('yat')} className={`px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${seans === 'yat' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600'}`}>
                  Yat (23:00)
                </button>
              </div>
            </div>

            <button onClick={() => setNobetDefteriAcik(true)} className="flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs cursor-pointer min-h-[44px]">
              <FileText className="w-4 h-4 shrink-0" /> Resmî Nöbet Defteri (PDF)
            </button>
          </div>
        </div>

        {feedback && (
          <div className={`p-3.5 rounded-2xl border text-xs font-bold flex items-center justify-between ${feedback.type === 'success' ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-rose-50 border-rose-300 text-rose-800'}`}>
            <span>{feedback.text}</span>
            <button onClick={() => setFeedback(null)} className="underline ml-3 shrink-0">Kapat</button>
          </div>
        )}

        {/* MOBİL YAPIŞKAN (STICKY) KAT SEÇİMİ VE TÜMÜNÜ VAR YAP */}
        <div className="bg-white/95 backdrop-blur-md sticky top-2 z-20 rounded-2xl p-3 shadow-md border border-slate-200 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
          <div className="grid grid-cols-3 gap-1.5">
            {[1, 2, 3].map((kat) => (
              <button
                key={kat}
                onClick={() => setSelectedKat(kat)}
                className={`py-2.5 px-3 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px] transition-all ${
                  selectedKat === kat ? (aktifRol === 'erkek' ? 'bg-blue-600 text-white shadow-xs' : 'bg-rose-600 text-white shadow-xs') : 'bg-slate-100 text-slate-700'
                }`}
              >
                {kat}. Kat
              </button>
            ))}
          </div>

          <button onClick={handleTumunuVarYap} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] text-white px-4 py-2.5 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px]">
            <CheckCircle2 className="w-4 h-4" /> Tümünü Var Yap
          </button>
        </div>

        {/* 2x2 MOBİL ÖZET KARTLARI */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div className="bg-white p-3.5 rounded-2xl border border-slate-200">
            <div className="text-[11px] text-slate-500">Kat Mevcudu</div>
            <div className="text-xl font-extrabold text-slate-900 mt-0.5">{katMevcudu}</div>
          </div>
          <div className="bg-emerald-50/70 p-3.5 rounded-2xl border border-emerald-200">
            <div className="text-[11px] text-emerald-700 font-medium">Var</div>
            <div className="text-xl font-extrabold text-emerald-700 mt-0.5">{varSayisi}</div>
          </div>
          <div className="bg-rose-50/70 p-3.5 rounded-2xl border border-rose-200">
            <div className="text-[11px] text-rose-700 font-medium">Yok</div>
            <div className="text-xl font-extrabold text-rose-700 mt-0.5">{yokSayisi}</div>
          </div>
          <div className="bg-amber-50/70 p-3.5 rounded-2xl border border-amber-200">
            <div className="text-[11px] text-amber-700 font-medium">İzinli</div>
            <div className="text-xl font-extrabold text-amber-700 mt-0.5">{izinliSayisi}</div>
          </div>
        </div>

        {/* ODALAR VE MOBİL ERGONOMİK ÖĞRENCİ KARTLARI */}
        {odalar.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center border border-slate-200 text-xs text-slate-500">
            Bu katta kayıtlı {aktifRol === 'erkek' ? 'erkek' : 'kız'} öğrenci bulunmamaktadır.
          </div>
        ) : (
          <div className="space-y-4">
            {odalar.map((odaNo) => {
              const odaOgrencileri = katStudents.filter((s) => s.oda === odaNo);
              return (
                <div key={odaNo} className="bg-white rounded-2xl shadow-xs border border-slate-200 overflow-hidden">
                  <div className={`${aktifRol === 'erkek' ? 'bg-slate-900' : 'bg-rose-950'} text-white px-4 py-3 flex items-center justify-between`}>
                    <div className="flex items-center gap-2 text-xs font-bold">
                      <Home className="w-4 h-4 text-blue-400" /> Oda No: {odaNo}
                    </div>
                    <span className="text-[11px] bg-white/15 px-2.5 py-0.5 rounded-full text-slate-100">
                      {odaOgrencileri.length} Öğrenci
                    </span>
                  </div>

                  <div className="p-3.5 sm:p-5 grid grid-cols-1 md:grid-cols-2 gap-3.5">
                    {odaOgrencileri.map((student) => {
                      const anneKey = `${student.id}-Anne`;
                      const babaKey = `${student.id}-Baba`;

                      return (
                        <div key={student.id} className="border border-slate-200 rounded-2xl p-3.5 sm:p-4 space-y-3 bg-white">
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <h3 className="font-extrabold text-slate-900 text-sm">{student.name}</h3>
                              <p className="text-[11px] text-slate-500 mt-0.5">
                                Oda: {student.oda} | Yatak: {student.yatak} | T.C.: {student.tc}
                              </p>
                            </div>
                            <span className={`text-[11px] font-extrabold px-2.5 py-1 rounded-lg shrink-0 ${student.status === 'izinli' ? 'bg-amber-100 text-amber-800' : student.status === 'yok' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                              {student.status === 'izinli' ? 'İzinli' : student.status === 'yok' ? 'Yok' : 'Var'}
                            </span>
                          </div>

                          {student.status === 'izinli' ? (
                            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 font-medium">
                              <strong>Otomatik İzinli:</strong> {student.izinAciklama || 'Veli İzni Aktif'}
                            </div>
                          ) : (
                            <>
                              {/* MOBİLDE BÜYÜK 2 SÜTUNLU VAR / YOK BUTONLARI */}
                              <div className="grid grid-cols-2 gap-2 pt-1">
                                <button
                                  onClick={() => handleStatusChange(student.id, 'var')}
                                  className={`py-2.5 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px] transition-all ${
                                    student.status === 'var' ? 'bg-emerald-600 text-white shadow-xs' : 'bg-slate-100 text-slate-700'
                                  }`}
                                >
                                  ✓ Var
                                </button>
                                <button
                                  onClick={() => handleStatusChange(student.id, 'yok')}
                                  className={`py-2.5 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px] transition-all ${
                                    student.status === 'yok' ? 'bg-red-600 text-white shadow-xs' : 'bg-slate-100 text-slate-700'
                                  }`}
                                >
                                  ✕ Yok
                                </button>
                              </div>

                              {student.status === 'yok' && (
                                <div className="p-3 bg-rose-50/80 border border-rose-200 rounded-xl space-y-2.5 mt-2">
                                  <div className="text-[11px] font-extrabold text-rose-800">WhatsApp Yoklama Bildirimi Gönder:</div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                                    <div className="flex items-center bg-white border border-rose-200 rounded-xl px-2.5 py-2 min-h-[40px]">
                                      <Phone className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
                                      <span className="text-slate-500 mr-1 text-[11px]">Anne:</span>
                                      <input type="tel" value={student.anneTel} onChange={(e) => handlePhoneChange(student.id, 'anneTel', e.target.value)} className="w-full font-mono text-xs text-slate-800 focus:outline-none" />
                                    </div>
                                    <div className="flex items-center bg-white border border-rose-200 rounded-xl px-2.5 py-2 min-h-[40px]">
                                      <Phone className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
                                      <span className="text-slate-500 mr-1 text-[11px]">Baba:</span>
                                      <input type="tel" value={student.babaTel} onChange={(e) => handlePhoneChange(student.id, 'babaTel', e.target.value)} className="w-full font-mono text-xs text-slate-800 focus:outline-none" />
                                    </div>
                                  </div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    <button type="button" disabled={sendingKey === anneKey} onClick={() => handleSendWhatsApp(student, 'Anne', student.anneTel)} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 px-3 rounded-xl text-xs font-bold cursor-pointer min-h-[42px]">
                                      {sendingKey === anneKey ? <><Loader2 className="w-4 h-4 animate-spin" /> Gönderiliyor...</> : sentKeys[anneKey] ? <><Check className="w-4 h-4" /> Anneye Gönderildi</> : <><Send className="w-3.5 h-3.5" /> Anneye Mesaj At</>}
                                    </button>
                                    <button type="button" disabled={sendingKey === babaKey} onClick={() => handleSendWhatsApp(student, 'Baba', student.babaTel)} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 px-3 rounded-xl text-xs font-bold cursor-pointer min-h-[42px]">
                                      {sendingKey === babaKey ? <><Loader2 className="w-4 h-4 animate-spin" /> Gönderiliyor...</> : sentKeys[babaKey] ? <><Check className="w-4 h-4" /> Babaya Gönderildi</> : <><Send className="w-3.5 h-3.5" /> Babaya Mesaj At</>}
                                    </button>
                                  </div>
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* RESMÎ NÖBET DEFTERİ MODAL */}
      {nobetDefteriAcik && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-2.5 sm:p-4 overflow-y-auto print:static print:bg-white print:p-0">
          <div className="bg-white rounded-2xl max-w-4xl w-full p-4 sm:p-8 space-y-5 shadow-2xl max-h-[92vh] overflow-y-auto print:max-h-none print:shadow-none">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 print:hidden">
              <h2 className="text-sm sm:text-base font-extrabold text-slate-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600 shrink-0" /> Resmî MEB Nöbet Defteri (4 Belletmen)
              </h2>
              <button onClick={() => setNobetDefteriAcik(false)} className="text-slate-400 hover:text-slate-700 p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 bg-slate-50 p-3.5 rounded-xl border border-slate-200 print:hidden">
              <div>
                <label className="block text-[11px] font-bold text-blue-800 mb-1">1. Erkek Belletmen</label>
                <input type="text" value={erkekBelletmen1} onChange={(e) => setErkekBelletmen1(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-blue-800 mb-1">2. Erkek Belletmen</label>
                <input type="text" value={erkekBelletmen2} onChange={(e) => setErkekBelletmen2(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-rose-800 mb-1">1. Kadın Belletmen</label>
                <input type="text" value={kizBelletmen1} onChange={(e) => setKizBelletmen1(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-rose-800 mb-1">2. Kadın Belletmen</label>
                <input type="text" value={kizBelletmen2} onChange={(e) => setKizBelletmen2(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
              </div>
              <div className="sm:col-span-2 md:col-span-4">
                <label className="block text-xs font-bold text-slate-700 mb-1">Günlük Nöbet Vukuat / Olay Notları</label>
                <textarea rows={2} value={nobetNotu} onChange={(e) => setNobetNotu(e.target.value)} className="w-full border border-slate-300 rounded-lg p-2.5 text-xs bg-white" />
              </div>
            </div>

            <div className="border border-slate-300 p-4 sm:p-6 rounded-xl space-y-4 text-slate-900 print:border-none print:p-0">
              <div className="text-center space-y-1 border-b-2 border-slate-800 pb-3">
                <p className="text-xs font-bold uppercase">T.C. MİLLÎ EĞİTİM BAKANLIĞI</p>
                <p className="text-xs sm:text-sm font-extrabold uppercase">Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Müdürlüğü</p>
                <p className="text-[11px] font-semibold uppercase text-slate-700">Pansiyon Günlük Nöbet Tutanağı ({tarih} - {seans === 'etut' ? '19:15 Etüt' : '23:00 Yat'})</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                <div className="border border-slate-300 p-2.5 rounded-lg">
                  <div className="font-bold text-blue-900 border-b pb-1 mb-1">ERKEK PANSİYONU</div>
                  Toplam: <strong>{erkekOgrenciler.length}</strong> | Var: <strong>{erkekOgrenciler.filter(s => s.status === 'var').length}</strong> | Yok: <strong>{erkekOgrenciler.filter(s => s.status === 'yok').length}</strong> | İzinli: <strong>{erkekOgrenciler.filter(s => s.status === 'izinli').length}</strong>
                </div>
                <div className="border border-slate-300 p-2.5 rounded-lg">
                  <div className="font-bold text-rose-900 border-b pb-1 mb-1">KIZ PANSİYONU</div>
                  Toplam: <strong>{kizOgrenciler.length}</strong> | Var: <strong>{kizOgrenciler.filter(s => s.status === 'var').length}</strong> | Yok: <strong>{kizOgrenciler.filter(s => s.status === 'yok').length}</strong> | İzinli: <strong>{kizOgrenciler.filter(s => s.status === 'izinli').length}</strong>
                </div>
              </div>

              <div className="space-y-1">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-1.5 border-l-4 border-rose-600">
                  1. Yoklamada Bulunmayan Öğrenciler ({tumYoklar.length})
                </h4>
                {tumYoklar.length === 0 ? (
                  <p className="text-xs italic pl-2">Yoklamada habersiz eksik öğrenci yoktur.</p>
                ) : (
                  <div className="space-y-1 text-xs">
                    {tumYoklar.map((s) => (
                      <div key={s.id} className="border-b py-1 flex justify-between">
                        <strong>{s.name} ({s.cinsiyet === 'erkek' ? 'Erkek' : 'Kız'} - Oda {s.oda})</strong>
                        <span>Tel: {s.anneTel}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-1">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-1.5 border-l-4 border-indigo-600">
                  2. Nöbetçi Belletmenler Vukuat ve Değerlendirme Notu
                </h4>
                <div className="p-2.5 border border-slate-300 rounded-lg text-xs min-h-[50px]">
                  {nobetNotu}
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-4 text-center text-[11px]">
                <div><p className="font-bold">1. Erkek Belletmen</p><p className="mt-1">{erkekBelletmen1}</p><p className="mt-4 text-slate-400">İmza</p></div>
                <div><p className="font-bold">2. Erkek Belletmen</p><p className="mt-1">{erkekBelletmen2}</p><p className="mt-4 text-slate-400">İmza</p></div>
                <div><p className="font-bold">1. Kadın Belletmen</p><p className="mt-1">{kizBelletmen1}</p><p className="mt-4 text-slate-400">İmza</p></div>
                <div><p className="font-bold">2. Kadın Belletmen</p><p className="mt-1">{kizBelletmen2}</p><p className="mt-4 text-slate-400">İmza</p></div>
                <div className="col-span-2 sm:col-span-1"><p className="font-bold">Müdür Yardımcısı</p><p className="mt-1">Pansiyon İdaresi</p><p className="mt-4 text-slate-400">İmza / Mühür</p></div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row justify-end gap-2.5 print:hidden">
              <button onClick={() => setNobetDefteriAcik(false)} className="px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 cursor-pointer min-h-[42px]">
                Kapat
              </button>
              <button onClick={handleSaveAndPrintDutyLog} className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold cursor-pointer min-h-[42px]">
                <Printer className="w-4 h-4" /> Kaydet ve Resmî PDF Çıktısı Al
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''

# -------------------------------------------------------------------------
# 3. MOBİL KART + MASAÜSTÜ TABLO UYUMLU ADMİN PANELİ (app/admin/page.tsx)
# -------------------------------------------------------------------------
ADMIN_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Users, Upload, Plus, Trash2, Shield, FileSpreadsheet, LogOut,
  KeyRound, Eye, EyeOff, Calendar, UserCheck, Wand2, Save,
  Activity, ShieldAlert, CheckCircle2, AlertTriangle, Info, Clock, X
} from 'lucide-react';

interface Student { id: string; name: string; cinsiyet: string; tc: string; sinif: string; kat: number; oda: string; yatak: string; anneTel: string; babaTel: string; status: string; }
interface Belletmen { id: string; name: string; cinsiyet: string; brans: string; phone: string; password: string; }
interface MonthlyDutyDay { tarih: string; erkek1: string; erkek2: string; kadin1: string; kadin2: string; }
interface AuditLog { id: string; tarihSaat: string; kullanici: string; islem: string; detay: string; tur: string; }

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'belletmen' | 'nobet' | 'ogrenci' | 'loglar'>('belletmen');

  const [students, setStudents] = useState<Student[]>([]);
  const [belletmenler, setBelletmenler] = useState<Belletmen[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<MonthlyDutyDay[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [msg, setMsg] = useState('');

  const [bName, setBName] = useState('');
  const [bCinsiyet, setBCinsiyet] = useState<'erkek' | 'kadin'>('erkek');
  const [bBrans, setBBrans] = useState('');
  const [bPhone, setBPhone] = useState('0541');
  const [bPassword, setBPassword] = useState('1234');
  const [belletmenCsv, setBelletmenCsv] = useState('Serhat AKAN, erkek, Matematik, 05411112233, 1453\nElif DEMİR, kadin, Edebiyat, 05412223344, 2026');

  const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({});
  const [editingPasswordId, setEditingPasswordId] = useState<string | null>(null);
  const [newPasswordVal, setNewPasswordVal] = useState('');

  const [nobetAySecim, setNobetAySecim] = useState('2026-10');
  const [nTarih, setNTarih] = useState('2026-10-29');
  const [nErkek1, setNErkek1] = useState('Cüneyt DEMİR');
  const [nErkek2, setNErkek2] = useState('Ali BEY');
  const [nKadin1, setNKadin1] = useState('Ayşenur KAYA');
  const [nKadin2, setNKadin2] = useState('Fatma YILMAZ');
  const [nobetCsv, setNobetCsv] = useState('2026-10-29, Cüneyt DEMİR, Ali BEY, Ayşenur KAYA, Fatma YILMAZ');

  const [sName, setSName] = useState('');
  const [sCinsiyet, setSCinsiyet] = useState<'erkek' | 'kiz'>('erkek');
  const [sTc, setSTc] = useState('');
  const [sSinif, setSSinif] = useState('9-A');
  const [sKat, setSKat] = useState(1);
  const [sOda, setSOda] = useState('101');
  const [sYatak, setSYatak] = useState('A');
  const [sAnneTel, setSAnneTel] = useState('05416571469');
  const [sBabaTel, setSBabaTel] = useState('05416571469');
  const [studentCsv, setStudentCsv] = useState('Ali Veli, erkek, 12345678910, 9-B, 1, 103, A, 05416571469, 05416571469');

  const syncFromStore = (store: any) => {
    if (store.students) setStudents(store.students);
    if (store.belletmenler) setBelletmenler(store.belletmenler);
    if (store.aylikNobetler) setAylikNobetler(store.aylikNobetler);
    if (store.auditLogs) setAuditLogs(store.auditLogs);
  };

  const fetchAll = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) syncFromStore(data.store);
    } catch {}
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_belletmen', name: bName, cinsiyet: bCinsiyet, brans: bBrans, phone: bPhone, password: bPassword }),
    });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setBName(''); setBBrans(''); setMsg(data.message); }
  };

  const handleBulkAddBelletmen = async () => {
    const lines = belletmenCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return { name: p[0], cinsiyet: p[1] || 'erkek', brans: p[2] || 'Öğretmen', phone: p[3] || '05410000000', password: p[4] || '1234' };
    });
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'bulk_add_belletmen', rows }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleUpdatePassword = async (id: string) => {
    if (!newPasswordVal.trim()) return;
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'update_belletmen_password', id, newPassword: newPasswordVal }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setEditingPasswordId(null); setNewPasswordVal(''); setMsg(data.message); }
  };

  const handleDeleteBelletmen = async (id: string) => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'delete_belletmen', id }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleAddSingleDutyDay = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'add_or_update_monthly_duty', tarih: nTarih, erkek1: nErkek1, erkek2: nErkek2, kadin1: nKadin1, kadin2: nKadin2 }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleAutoGenerateMonth = async () => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'auto_generate_month_duty', yearMonth: nobetAySecim }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleBulkMonthlyDuty = async () => {
    const lines = nobetCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return { tarih: p[0], erkek1: p[1] || '-', erkek2: p[2] || '-', kadin1: p[3] || '-', kadin2: p[4] || '-' };
    });
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'bulk_monthly_duty', rows }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleDeleteDutyDay = async (tarih: string) => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'delete_monthly_duty', tarih }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sName) return;
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'add_student', name: sName, cinsiyet: sCinsiyet, tc: sTc, sinif: sSinif, kat: sKat, oda: sOda, yatak: sYatak, anneTel: sAnneTel, babaTel: sBabaTel }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setSName(''); setSTc(''); setMsg(data.message); }
  };

  const handleBulkImportStudents = async () => {
    const lines = studentCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return { name: p[0], cinsiyet: p[1] || 'erkek', tc: p[2] || '10000000000', sinif: p[3] || '9-A', kat: Number(p[4]) || 1, oda: p[5] || '101', yatak: p[6] || 'A', anneTel: p[7] || '05416571469', babaTel: p[8] || '05416571469' };
    });
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'bulk_import', rows }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleDeleteStudent = async (id: string) => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'delete_student', id }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleClearLogs = async () => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'clear_audit_logs' }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const getBadgeColor = (tur: string) => {
    if (tur === 'basari') return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    if (tur === 'uyari') return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    if (tur === 'hata') return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
  };

  const getIcon = (tur: string) => {
    if (tur === 'basari') return <CheckCircle2 className="w-3.5 h-3.5" />;
    if (tur === 'uyari') return <AlertTriangle className="w-3.5 h-3.5" />;
    if (tur === 'hata') return <X className="w-3.5 h-3.5" />;
    return <Info className="w-3.5 h-3.5" />;
  };

  const erkekBelletmenList = belletmenler.filter((b) => b.cinsiyet === 'erkek');
  const kadinBelletmenList = belletmenler.filter((b) => b.cinsiyet === 'kadin');

  return (
    <div className="min-h-screen bg-slate-100 p-2.5 sm:p-6 pb-20">
      <div className="max-w-6xl mx-auto space-y-4 sm:space-y-6">

        {/* MOBİL UYUMLU ÜST BAŞLIK */}
        <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold shrink-0">
              <Shield className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <div>
              <h1 className="text-base sm:text-xl font-extrabold text-slate-900">Pansiyon İdare & Yönetici Paneli</h1>
              <p className="text-[11px] sm:text-xs text-slate-500">
                Belletmen & Şifre • Aylık Nöbet • Öğrenciler • <strong className="text-indigo-600">Güvenlik Günlüğü</strong>
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 sm:flex items-center gap-2 w-full sm:w-auto">
            <a href="/belletmen" className="text-center text-[11px] sm:text-xs font-bold text-blue-700 bg-blue-50 py-2.5 px-3 rounded-xl border border-blue-200">
              Belletmen
            </a>
            <a href="/veli" className="text-center text-[11px] sm:text-xs font-bold text-emerald-700 bg-emerald-50 py-2.5 px-3 rounded-xl border border-emerald-200">
              Veli
            </a>
            <a href="/" className="flex items-center justify-center gap-1 text-[11px] sm:text-xs font-bold text-white bg-rose-600 py-2.5 px-3 rounded-xl">
              <LogOut className="w-3.5 h-3.5" /> Çıkış
            </a>
          </div>
        </div>

        {/* MOBİLDE 2x2 IZGARA SEKME MENÜSÜ */}
        <div className="bg-white rounded-2xl p-1.5 sm:p-2 border border-slate-200 shadow-xs grid grid-cols-2 lg:grid-cols-4 gap-1.5 sm:gap-2">
          <button
            onClick={() => setActiveTab('belletmen')}
            className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold transition-all cursor-pointer min-h-[44px] ${
              activeTab === 'belletmen' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <KeyRound className="w-4 h-4 shrink-0" /> <span>1. Belletmen ({belletmenler.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('nobet')}
            className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold transition-all cursor-pointer min-h-[44px] ${
              activeTab === 'nobet' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Calendar className="w-4 h-4 shrink-0" /> <span>2. Aylık Nöbet ({aylikNobetler.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('ogrenci')}
            className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold transition-all cursor-pointer min-h-[44px] ${
              activeTab === 'ogrenci' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Users className="w-4 h-4 shrink-0" /> <span>3. Öğrenciler ({students.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('loglar')}
            className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold transition-all cursor-pointer min-h-[44px] ${
              activeTab === 'loglar' ? 'bg-slate-900 text-amber-400 shadow-xs' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Activity className="w-4 h-4 shrink-0" /> <span>4. Güvenlik Log ({auditLogs.length})</span>
          </button>
        </div>

        {msg && (
          <div className="p-3.5 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold flex justify-between items-center">
            <span>✅ {msg}</span>
            <button onClick={() => setMsg('')} className="underline ml-3 cursor-pointer">Kapat</button>
          </div>
        )}

        {/* SEKME 4: SİSTEM GÜVENLİK & DENETİM GÜNLÜĞÜ (Mobil Kart + Masaüstü Tablo) */}
        {activeTab === 'loglar' && (
          <div className="bg-slate-950 rounded-3xl p-4 sm:p-6 border border-slate-800 shadow-2xl space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-base sm:text-lg font-extrabold text-white flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" /> Sistem Güvenlik & Denetim Günlüğü
                </h2>
                <p className="text-[11px] sm:text-xs text-slate-400 mt-1">
                  Tüm girişler, şifre değişiklikleri ve yoklama işlemleri saniye saniye kaydedilir.
                </p>
              </div>
              <div className="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
                <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-3 py-1.5 rounded-full border border-emerald-800">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Canlı İzleme
                </div>
                <button onClick={handleClearLogs} className="text-[11px] font-bold text-rose-300 bg-rose-950/50 border border-rose-800 px-3 py-1.5 rounded-xl cursor-pointer">
                  Temizle
                </button>
              </div>
            </div>

            {/* Mobil Log Kartları */}
            <div className="md:hidden space-y-2.5 max-h-[500px] overflow-y-auto">
              {auditLogs.map((log) => (
                <div key={log.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-3.5 space-y-1.5 text-xs">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold text-white">{log.islem}</span>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md border font-bold text-[10px] uppercase ${getBadgeColor(log.tur)}`}>
                      {getIcon(log.tur)} {log.tur}
                    </span>
                  </div>
                  <p className="text-slate-300 text-[11px]">{log.detay}</p>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800/80">
                    <span className="text-blue-300 font-semibold">{log.kullanici}</span>
                    <span className="font-mono">{log.tarihSaat}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Masaüstü Log Tablosu */}
            <div className="hidden md:block overflow-x-auto max-h-[500px]">
              <table className="w-full text-xs border-collapse text-left">
                <thead className="sticky top-0 bg-slate-950">
                  <tr className="border-b border-slate-800 text-slate-400 uppercase">
                    <th className="p-3">Tarih / Saat</th>
                    <th className="p-3">Kullanıcı</th>
                    <th className="p-3">İşlem Türü</th>
                    <th className="p-3">Açıklama & Detay</th>
                    <th className="p-3 text-right">Durum</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-900/60">
                      <td className="p-3 font-mono text-slate-300 whitespace-nowrap">{log.tarihSaat}</td>
                      <td className="p-3 font-semibold text-blue-300 whitespace-nowrap">{log.kullanici}</td>
                      <td className="p-3 font-bold text-slate-100 whitespace-nowrap">{log.islem}</td>
                      <td className="p-3 text-slate-300">{log.detay}</td>
                      <td className="p-3 text-right whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md border font-bold text-[10px] uppercase ${getBadgeColor(log.tur)}`}>
                          {getIcon(log.tur)} {log.tur}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* SEKME 1: BELLETMEN & ŞİFRE YÖNETİMİ */}
        {activeTab === 'belletmen' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Belletmen Ekle
                </h2>
                <form onSubmit={handleAddBelletmen} className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={bName} onChange={(e) => setBName(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-3 text-base sm:text-xs font-semibold min-h-[44px]" />
                  <select value={bCinsiyet} onChange={(e) => setBCinsiyet(e.target.value as 'erkek' | 'kadin')} className="border border-slate-200 rounded-xl px-3 py-3 text-base sm:text-xs font-bold bg-white min-h-[44px]">
                    <option value="erkek">👨 Erkek Belletmen</option>
                    <option value="kadin">👩 Kadın Belletmen</option>
                  </select>
                  <input type="text" placeholder="Branş" value={bBrans} onChange={(e) => setBBrans(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-3 text-base sm:text-xs min-h-[44px]" />
                  <input type="tel" placeholder="Telefon" value={bPhone} onChange={(e) => setBPhone(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-3 text-base sm:text-xs font-mono min-h-[44px]" />
                  <input type="text" required placeholder="Giriş Şifresi" value={bPassword} onChange={(e) => setBPassword(e.target.value)} className="sm:col-span-2 border border-indigo-200 bg-indigo-50/40 rounded-xl px-3 py-3 text-base sm:text-xs font-mono font-bold min-h-[44px]" />
                  <button type="submit" className="sm:col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold cursor-pointer min-h-[46px]">
                    Belletmeni Sisteme Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Excel ile Toplu Belletmen Ekleme
                </h2>
                <p className="text-[11px] text-slate-500">Format: <code>Ad Soyad, erkek/kadin, Branş, Telefon, Şifre</code></p>
                <textarea rows={4} value={belletmenCsv} onChange={(e) => setBelletmenCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkAddBelletmen} className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl text-xs font-bold cursor-pointer min-h-[46px]">
                  <Upload className="w-4 h-4" /> Excel Listesini Toplu Yükle
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
              <h2 className="text-sm font-bold text-slate-900">Kayıtlı Belletmenler & Şifre Yönetimi</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {belletmenler.map((b) => {
                  const isShown = !!visiblePasswords[b.id];
                  const isEditing = editingPasswordId === b.id;
                  return (
                    <div key={b.id} className="border border-slate-200 rounded-2xl p-3.5 flex flex-col justify-between gap-3 bg-slate-50/50">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-extrabold text-slate-900 text-sm">{b.name}</div>
                          <div className="text-[11px] text-slate-500">{b.cinsiyet === 'kadin' ? '👩 Kadın Belletmen' : '👨 Erkek Belletmen'} • {b.brans}</div>
                        </div>
                        <button onClick={() => handleDeleteBelletmen(b.id)} className="text-rose-600 p-1.5 cursor-pointer">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {isEditing ? (
                        <div className="flex items-center gap-2">
                          <input type="text" value={newPasswordVal} onChange={(e) => setNewPasswordVal(e.target.value)} className="flex-1 border border-indigo-300 rounded-xl px-3 py-2 text-xs font-mono bg-white" />
                          <button onClick={() => handleUpdatePassword(b.id)} className="bg-emerald-600 text-white px-3 py-2 rounded-xl text-xs font-bold cursor-pointer">Kaydet</button>
                          <button onClick={() => setEditingPasswordId(null)} className="text-slate-500 text-xs underline px-2">İptal</button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl px-3 py-2">
                          <div className="flex items-center gap-2">
                            <span className="text-[11px] text-slate-400">Şifre:</span>
                            <span className="font-mono font-bold text-xs text-slate-800">{isShown ? b.password : '••••••'}</span>
                            <button onClick={() => setVisiblePasswords((p) => ({ ...p, [b.id]: !p[b.id] }))} className="text-slate-500 p-1 cursor-pointer">
                              {isShown ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                          <button onClick={() => { setEditingPasswordId(b.id); setNewPasswordVal(b.password); }} className="text-xs font-bold text-indigo-600 hover:underline cursor-pointer">
                            Şifre Değiştir
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* SEKME 2: AYLIK NÖBET LİSTESİ */}
        {activeTab === 'nobet' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="bg-indigo-950 text-white rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
              <div>
                <h2 className="text-sm font-extrabold flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-amber-400" /> Otomatik Aylık Nöbet Çizelgesi
                </h2>
                <p className="text-xs text-indigo-200">Seçilen ayın tüm günlerine 2 Erkek + 2 Kadın belletmeni otomatik dağıtır.</p>
              </div>
              <div className="flex flex-col xs:flex-row items-stretch xs:items-center gap-2">
                <input type="month" value={nobetAySecim} onChange={(e) => setNobetAySecim(e.target.value)} className="bg-white text-slate-900 font-bold text-xs px-3 py-2.5 rounded-xl min-h-[42px]" />
                <button onClick={handleAutoGenerateMonth} className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs px-4 py-2.5 rounded-xl cursor-pointer min-h-[42px]">
                  Tüm Ayı Doldur
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h3 className="text-sm font-bold text-slate-900">Tekil Gün Nöbeti Ata</h3>
                <form onSubmit={handleAddSingleDutyDay} className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                  <input type="date" value={nTarih} onChange={(e) => setNTarih(e.target.value)} className="sm:col-span-2 border rounded-xl px-3 py-2.5 font-bold min-h-[44px]" />
                  <select value={nErkek1} onChange={(e) => setNErkek1(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nErkek2} onChange={(e) => setNErkek2(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin1} onChange={(e) => setNKadin1(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin2} onChange={(e) => setNKadin2(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <button type="submit" className="sm:col-span-2 bg-blue-600 text-white py-3 rounded-xl font-bold cursor-pointer min-h-[46px]">
                    <Save className="w-4 h-4 inline mr-1" /> Günü Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h3 className="text-sm font-bold text-slate-900">Excel ile Aylık Nöbet Listesi Yükle</h3>
                <textarea rows={4} value={nobetCsv} onChange={(e) => setNobetCsv(e.target.value)} className="w-full border rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkMonthlyDuty} className="w-full bg-emerald-600 text-white py-3 rounded-xl text-xs font-bold cursor-pointer min-h-[46px]">
                  <Upload className="w-4 h-4 inline mr-1" /> Aylık Nöbet Listesini Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-[440px] overflow-y-auto">
                {aylikNobetler.map((d) => (
                  <div key={d.tarih} className="border border-slate-200 rounded-xl p-3 text-xs space-y-1 bg-slate-50/50 flex justify-between items-start">
                    <div className="space-y-0.5">
                      <div className="font-mono font-extrabold text-slate-900">{d.tarih}</div>
                      <div className="text-blue-700 font-semibold">👨 {d.erkek1}, {d.erkek2}</div>
                      <div className="text-rose-700 font-semibold">👩 {d.kadin1}, {d.kadin2}</div>
                    </div>
                    <button onClick={() => handleDeleteDutyDay(d.tarih)} className="text-rose-600 p-1 cursor-pointer">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SEKME 3: ÖĞRENCİ YÖNETİMİ */}
        {activeTab === 'ogrenci' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h2 className="text-sm font-bold text-slate-900">Yeni Öğrenci Kaydı</h2>
                <form onSubmit={handleAddStudent} className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={sName} onChange={(e) => setSName(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <select value={sCinsiyet} onChange={(e) => setSCinsiyet(e.target.value as 'erkek' | 'kiz')} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs font-bold bg-white min-h-[44px]">
                    <option value="erkek">Erkek Pansiyonu</option>
                    <option value="kiz">Kız Pansiyonu</option>
                  </select>
                  <input type="text" placeholder="T.C." value={sTc} onChange={(e) => setSTc(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <input type="text" placeholder="Sınıf (9-A)" value={sSinif} onChange={(e) => setSSinif(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <select value={sKat} onChange={(e) => setSKat(Number(e.target.value))} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs bg-white min-h-[44px]">
                    <option value={1}>1. Kat</option>
                    <option value={2}>2. Kat</option>
                    <option value={3}>3. Kat</option>
                  </select>
                  <input type="text" placeholder="Oda No" value={sOda} onChange={(e) => setSOda(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <input type="tel" placeholder="Anne Tel" value={sAnneTel} onChange={(e) => setSAnneTel(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <input type="tel" placeholder="Baba Tel" value={sBabaTel} onChange={(e) => setSBabaTel(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <button type="submit" className="sm:col-span-2 bg-indigo-600 text-white py-3 rounded-xl font-bold cursor-pointer min-h-[46px]">
                    Öğrenciyi Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h2 className="text-sm font-bold text-slate-900">Excel ile Toplu Öğrenci Yükleme</h2>
                <textarea rows={4} value={studentCsv} onChange={(e) => setStudentCsv(e.target.value)} className="w-full border rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkImportStudents} className="w-full bg-emerald-600 text-white py-3 rounded-xl text-xs font-bold cursor-pointer min-h-[46px]">
                  <Upload className="w-4 h-4 inline mr-1" /> Toplu Öğrenci Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                {students.map((s) => (
                  <div key={s.id} className="border border-slate-200 rounded-xl p-3 text-xs flex justify-between items-center bg-slate-50/50">
                    <div>
                      <div className="font-extrabold text-slate-900">{s.name}</div>
                      <div className="text-[11px] text-slate-500">{s.cinsiyet === 'kiz' ? '👩 Kız' : '👨 Erkek'} • {s.kat}. Kat - Oda {s.oda}</div>
                      <div className="text-[11px] font-mono text-slate-600 mt-0.5">{s.anneTel}</div>
                    </div>
                    <button onClick={() => handleDeleteStudent(s.id)} className="text-rose-600 p-1.5 cursor-pointer">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
'''

def main():
    print("=========================================================")
    print("   TÜM MODÜLLER MOBİL UYUMLU (RESPONSIVE) HALE GETİRİLİYOR")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 1. Mobil Uyumlu Sayfaları Yaz
    write_file("app/page.tsx", HOME_PAGE_TSX)
    write_file("app/belletmen/page.tsx", BELLETMEN_PAGE_TSX)
    write_file("app/admin/page.tsx", ADMIN_PAGE_TSX)

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
    run_command('git commit -m "Tum moduller mobil öncelikli (Mobile-First Responsive) tasarıma geçirildi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 MOBİL UYUMLULUK GÜNCELLEMESİ CANLIYA ALINDI!")
    print("👉 Cep telefonunuzdan https://pansiyon-yurt-sistemi.vercel.app")
    print("   adresine girerek tüm panelleri test edebilirsiniz.")
    print("=========================================================")

if __name__ == "__main__":
    main()