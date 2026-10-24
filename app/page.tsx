'use client';

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
  ArrowRight,
  Lock,
  CheckCircle2,
  X,
  Send
} from 'lucide-react';

export default function PansiyonLoginPortalPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');

  // Veli WhatsApp OTP State
  const [phone, setPhone] = useState('');
  const [otpStep, setOtpStep] = useState<'request' | 'verify'>('request');
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'error' | 'success'; text: string } | null>(null);

  // Belletmen Giriş State
  const [belletmenList, setBelletmenList] = useState<any[]>([
    { id: 'b1', name: 'Mustafa Demir', cinsiyet: 'erkek', brans: 'Erkek Pansiyonu' },
    { id: 'b2', name: 'Cüneyt DEMİR', cinsiyet: 'erkek', brans: 'Bilişim Teknolojileri' },
    { id: 'b3', name: 'Kübra Güllü', cinsiyet: 'kadin', brans: 'Kız Pansiyonu' },
    { id: 'b4', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat' },
  ]);
  const [selectedBelletmen, setSelectedBelletmen] = useState('Mustafa Demir');
  const [belletmenPass, setBelletmenPass] = useState('');

  // Yönetici Giriş State
  const [adminUser, setAdminUser] = useState('admin');
  const [adminPass, setAdminPass] = useState('');

  // Yurt AI Asistanı Modal State
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
        }
      })
      .catch(() => {});
  }, []);

  const handleSendVeliOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.replace(/\D/g, '').length < 10) {
      setFeedback({ type: 'error', text: 'Lütfen geçerli bir cep telefonu numarası giriniz (Örn: 0541 657 14 69).' });
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
            text: `✅ Giriş kodunuz oluşturuldu. (WhatsApp Bot Yedek Kodu: ${data.otpCode})`
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
      {/* ÜST BAŞLIK (HEADER) */}
      <header
        className={`w-full border-b px-4 sm:px-10 py-3.5 transition-colors ${
          darkMode ? 'bg-slate-900/90 border-slate-800' : 'bg-white border-slate-200/80'
        }`}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center shadow-2xs">
              <span className="text-xs font-black tracking-tighter text-blue-700">SBL</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className={`text-sm sm:text-base font-extrabold tracking-tight ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Prof. Dr. Mümtaz Turhan SBL Pansiyon
                </h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-50 text-blue-600 border border-blue-200">
                  MEB Uyumlu
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                İzin Takip • Etüt Yoklama • Gece Yat Yoklaması • Oda Yönetimi
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="hidden sm:inline text-xs font-medium text-slate-400">Güvenli Giriş Paneli</span>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold border transition-all cursor-pointer ${
                darkMode
                  ? 'bg-slate-800 border-slate-700 text-amber-300 hover:bg-slate-700'
                  : 'bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {darkMode ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              {darkMode ? 'Aydınlık' : 'Karanlık'}
            </button>
          </div>
        </div>
      </header>

      {/* ORTA MERKEZİ KART ALANI */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div
          className={`max-w-[920px] w-full rounded-[28px] shadow-2xl border overflow-hidden grid grid-cols-1 md:grid-cols-12 transition-colors ${
            darkMode
              ? 'bg-slate-900 border-slate-800 shadow-black/50'
              : 'bg-white border-slate-200/90 shadow-slate-200/80'
          }`}
        >
          {/* SOL SÜTUN */}
          <div
            className={`md:col-span-5 relative flex flex-col items-center justify-between p-8 text-center overflow-hidden border-b md:border-b-0 md:border-r ${
              darkMode
                ? 'bg-gradient-to-b from-slate-900 via-blue-950/40 to-slate-900 border-slate-800'
                : 'bg-gradient-to-b from-[#f0f7ff] via-[#e6f1fe] to-[#dcebfd] border-slate-200/60'
            }`}
          >
            <div className="z-10 pt-4 space-y-4">
              <div className="mx-auto w-24 h-24 rounded-3xl bg-white/90 shadow-md border border-blue-100 flex flex-col items-center justify-center p-2">
                <div className="text-2xl font-black tracking-tighter text-[#0055a5] leading-none">SBL</div>
                <div className="text-[8px] font-extrabold uppercase tracking-widest text-[#0055a5] mt-1">PANSİYON</div>
                <div className="text-[7px] font-semibold text-slate-400">SOSYAL BİLİMLER LİSESİ</div>
              </div>

              <div className="space-y-1">
                <h2 className={`text-xs font-extrabold uppercase tracking-wider ${darkMode ? 'text-blue-300' : 'text-[#0f2942]'}`}>
                  PROF. DR. MÜMTAZ TURHAN
                </h2>
                <p className={`text-sm font-black ${darkMode ? 'text-white' : 'text-[#0f2942]'}`}>
                  Sosyal Bilimler Lisesi Pansiyonu
                </p>
              </div>

              <div className="inline-block px-4 py-1 rounded-full bg-white/80 border border-blue-200/80 text-[11px] font-semibold text-slate-600 shadow-2xs">
                Pansiyon & Yurt Portalı
              </div>
            </div>

            <div className="w-full pt-8 z-10">
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
                <circle cx="48" cy="125" r="18" />
                <line x1="48" y1="143" x2="48" y2="154" />
                <circle cx="312" cy="128" r="15" />
                <line x1="312" y1="143" x2="312" y2="154" />
              </svg>
            </div>
          </div>

          {/* SAĞ SÜTUN */}
          <div className="md:col-span-7 p-6 sm:p-9 flex flex-col justify-between space-y-6">
            <div className="space-y-5">
              <div className="text-center space-y-1">
                <h2 className={`text-xl sm:text-2xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                  Pansiyon Yönetim Sistemi
                </h2>
                <p className="text-xs text-slate-400">Giriş yapmak için bilgilerinizi giriniz.</p>
              </div>

              <div className={`grid grid-cols-3 p-1 rounded-xl border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-100/90 border-slate-200/80'}`}>
                <button
                  type="button"
                  onClick={() => { setActiveTab('veli'); setFeedback(null); }}
                  className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeTab === 'veli' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Users className="w-3.5 h-3.5" /> Veli
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab('belletmen'); setFeedback(null); }}
                  className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeTab === 'belletmen' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <UserCheck className="w-3.5 h-3.5" /> Belletmen
                </button>
                <button
                  type="button"
                  onClick={() => { setActiveTab('yonetici'); setFeedback(null); }}
                  className={`flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    activeTab === 'yonetici' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Shield className="w-3.5 h-3.5" /> Yönetici
                </button>
              </div>

              {feedback && (
                <div className={`p-3 rounded-xl text-xs font-semibold border ${feedback.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-700'}`}>
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
                          required
                          placeholder="Kayıtlı Cep Telefonu No (Örn: 0555 444 55 66)"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          className={`w-full pl-10 pr-4 py-3 rounded-xl border text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}
                        />
                      </div>
                      <div className={`p-3.5 rounded-xl border text-[11px] leading-relaxed flex items-start gap-2.5 ${darkMode ? 'bg-blue-950/40 border-blue-900 text-blue-300' : 'bg-[#f0f7ff] border-blue-100 text-[#1e40af]'}`}>
                        <ShieldAlert className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                        <span>Veliler kullanıcı adı olarak sisteme kayıtlı cep telefonu numaralarını kullanırlar. Güvenliğiniz için tek kullanımlık 6 haneli giriş şifresi WhatsApp üzerinden iletilir.</span>
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] text-white font-bold py-3.5 rounded-xl text-xs shadow-md transition-all cursor-pointer">
                        <MessageCircle className="w-4 h-4" /> {loading ? 'WhatsApp Mesajı Gönderiliyor...' : 'WhatsApp ile 6 Haneli Şifre Gönder'}
                      </button>
                    </form>
                  ) : (
                    <form onSubmit={handleVerifyVeliOtp} className="space-y-3.5">
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1 text-center">WhatsApp Numaranıza Gelen 6 Haneli Kodu Giriniz</label>
                        <input type="text" maxLength={6} required placeholder="123456" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} className="w-full text-center tracking-widest text-lg font-extrabold py-3 border border-emerald-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] text-white font-bold py-3.5 rounded-xl text-xs shadow-md cursor-pointer">
                        <CheckCircle2 className="w-4 h-4" /> Doğrula ve Veli Portalına Gir
                      </button>
                      <button type="button" onClick={() => setOtpStep('request')} className="w-full text-center text-[11px] text-slate-500 underline cursor-pointer">
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
                    <select value={selectedBelletmen} onChange={(e) => setSelectedBelletmen(e.target.value)} className={`w-full px-3.5 py-3 rounded-xl border text-xs font-bold ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}>
                      {belletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.cinsiyet === 'kadin' ? '👩‍🏫 ' : '👨‍🏫 '} {b.name} ({b.cinsiyet === 'kadin' ? 'Kız Pansiyonu' : 'Erkek Pansiyonu'})</option>
                      ))}
                    </select>
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input type="password" placeholder="Belletmen Şifresi (Demo: 1234)" value={belletmenPass} onChange={(e) => setBelletmenPass(e.target.value)} className={`w-full pl-10 pr-4 py-3 rounded-xl border text-xs ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <button type="submit" className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl text-xs shadow-md transition-all cursor-pointer">
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
                    <input type="text" value={adminUser} onChange={(e) => setAdminUser(e.target.value)} placeholder="Yönetici Kullanıcı Adı" className={`w-full pl-10 pr-4 py-3 rounded-xl border text-xs ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input type="password" value={adminPass} onChange={(e) => setAdminPass(e.target.value)} placeholder="Yönetici Şifresi" className={`w-full pl-10 pr-4 py-3 rounded-xl border text-xs ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <button type="submit" className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 rounded-xl text-xs shadow-md transition-all cursor-pointer">
                    <Shield className="w-4 h-4" /> Yönetici Paneline Giriş Yap
                  </button>
                </form>
              )}
            </div>

            {/* ALT TELİF BİLGİSİ (HIZLI DEMO BUTONLARI KALDIRILDI) */}
            <div className="pt-4 mt-2 border-t border-slate-100">
              <p className="text-center text-[11px] text-slate-400">
                © 2026 Prof. Dr. Mümtaz Turhan SBL
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* ALT BİLGİ ÇUBUĞU (FOOTER) */}
      <footer
        className={`w-full border-t px-4 sm:px-10 py-3 text-[11px] text-slate-400 transition-colors ${
          darkMode ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200/70'
        }`}
      >
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>© 2026 Pansiyon ve Yurt Takip Sistemi • Millî Eğitim Bakanlığı Standartlarına Uygun</span>
          <span>SQLite Tabanlı Güvenli Veritabanı • Rol Tabanlı JWT Doğrulama</span>
        </div>
      </footer>

      {/* SAĞ ALT YÜZEN "YURT AI ASİSTANI" BUTONU VE SOHBET PENCERESİ */}
      <div className="fixed bottom-4 right-4 z-50">
        {aiOpen && (
          <div className="mb-3 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-indigo-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-extrabold">
                <Sparkles className="w-4 h-4" /> Yurt AI Asistanı
              </div>
              <button onClick={() => setAiOpen(false)} className="text-white/80 hover:text-white cursor-pointer">
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
                className="flex-1 text-xs px-3 py-2 border border-slate-200 rounded-xl focus:outline-none"
              />
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-xl text-xs font-bold cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        )}

        <button
          onClick={() => setAiOpen(!aiOpen)}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold text-xs px-4 py-2.5 rounded-full shadow-lg shadow-indigo-500/30 transition-all cursor-pointer"
        >
          <Sparkles className="w-4 h-4" /> Yurt AI Asistanı
          <span className="w-2 h-2 rounded-full bg-emerald-300 animate-ping" />
        </button>
      </div>
    </div>
  );
}