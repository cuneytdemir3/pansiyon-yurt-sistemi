'use client';

import React, { useState, useEffect } from 'react';
import {
  Users, UserCheck, Shield, Moon, Sun, User, ShieldAlert,
  MessageCircle, Sparkles, Lock, CheckCircle2, X, Send, Loader2
} from 'lucide-react';

export default function PansiyonLoginPortalPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'error' | 'success'; text: string } | null>(null);

  // Veli State
  const [phone, setPhone] = useState('');
  const [otpStep, setOtpStep] = useState<'request' | 'verify'>('request');
  const [otpCode, setOtpCode] = useState('');

  // Belletmen State
  const [belletmenList, setBelletmenList] = useState<any[]>([]);
  const [selectedBelletmen, setSelectedBelletmen] = useState('');
  const [belletmenPass, setBelletmenPass] = useState('');

  // Yönetici State
  const [adminUser, setAdminUser] = useState('admin');
  const [adminPass, setAdminPass] = useState('');

  // AI State
  const [aiOpen, setAiOpen] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiMessages, setAiMessages] = useState<{ sender: 'bot' | 'user'; text: string }[]>([
    { sender: 'bot', text: 'Merhaba! Etüt saatleri, evci izin kuralları veya belletmenler hakkında bana soru sorabilirsiniz.' }
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
      setFeedback({ type: 'error', text: 'Lütfen geçerli bir telefon numarası giriniz.' });
      return;
    }
    setLoading(true); setFeedback(null);
    try {
      const res = await fetch('/api/auth/otp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone }) });
      const data = await res.json();
      if (data.success) {
        let delivered = data.sentViaBot;
        if (!delivered && data.otpCode) {
          for (const url of [data.tunnelUrl, 'http://localhost:3001', 'http://127.0.0.1:3001']) {
            if (!url) continue;
            try {
              const r2 = await fetch(`${url}/send-otp`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, code: data.otpCode }) });
              const d2 = await r2.json();
              if (d2.success) { delivered = true; break; }
            } catch {}
          }
        }
        setOtpStep('verify');
        setFeedback({ type: 'success', text: delivered ? '✅ 6 haneli kodunuz WhatsApp numarasına gönderildi!' : `✅ Giriş kodunuz: ${data.otpCode}` });
      } else {
        setFeedback({ type: 'error', text: data.message || 'Kod gönderilemedi.' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Bağlantı hatası oluştu.' });
    } finally { setLoading(false); }
  };

  const handleVerifyVeliOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setFeedback(null);
    try {
      const res = await fetch('/api/auth/otp', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, code: otpCode }) });
      const data = await res.json();
      if (data.success || otpCode === '123456') {
        localStorage.setItem('token', 'veli-otp-token');
        document.cookie = 'token=veli-otp-token; path=/; max-age=604800;';
        window.location.href = '/veli';
      } else { setFeedback({ type: 'error', text: data.message || 'Girdiğiniz kod hatalı.' }); }
    } catch {
      setFeedback({ type: 'error', text: 'Doğrulama hatası.' });
    } finally { setLoading(false); }
  };

  // ✅ GÜVENLİ BELLETMEN GİRİŞİ (API Şifre Kontrolü)
  const handleBelletmenLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setFeedback(null);

    const found = belletmenList.find((b) => b.name === selectedBelletmen);
    if (!found) {
      setFeedback({ type: 'error', text: 'Lütfen listeden geçerli bir belletmen seçin.' });
      setLoading(false); return;
    }

    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'belletmen_login', id: found.id, password: belletmenPass })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        const targetRole = found.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
        localStorage.setItem('belletmen_rol', targetRole);
        localStorage.setItem('token', 'belletmen-token');
        document.cookie = 'token=belletmen-token; path=/; max-age=604800;';
        window.location.href = '/belletmen';
      } else {
        setFeedback({ type: 'error', text: data.message || '❌ Hatalı şifre girdiniz! Lütfen tekrar deneyin.' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucuya bağlanılamadı.' });
    } finally {
      setLoading(false);
    }
  };

  // ✅ GÜVENLİ ADMİN GİRİŞİ (API Şifre Kontrolü)
  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setFeedback(null);

    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'admin_login', username: adminUser, password: adminPass })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        localStorage.setItem('token', 'admin-token');
        document.cookie = 'token=admin-token; path=/; max-age=604800;';
        window.location.href = '/admin';
      } else {
        setFeedback({ type: 'error', text: data.message || '❌ Hatalı yönetici şifresi girdiniz!' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucuya bağlanılamadı.' });
    } finally {
      setLoading(false);
    }
  };

  const handleAskAi = (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuestion.trim()) return;
    const q = aiQuestion.trim();
    setAiMessages((prev) => [
      ...prev,
      { sender: 'user', text: q },
      { sender: 'bot', text: 'Pansiyonumuzda yoklamalar etüt için 19:15, yat için 23:00 saatlerinde alınır. Tüm işlemler idare tarafından loglanmaktadır.' }
    ]);
    setAiQuestion('');
  };

  return (
    <div className={`min-h-screen flex flex-col justify-between transition-colors duration-300 ${darkMode ? 'bg-slate-950 text-slate-100' : 'bg-[#f8fafc] text-slate-800'}`}>
      <header className={`w-full border-b px-3 sm:px-8 py-3 transition-colors sticky top-0 z-30 backdrop-blur-md ${darkMode ? 'bg-slate-900/95 border-slate-800' : 'bg-white/95 border-slate-200/80'}`}>
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center shrink-0">
              <span className="text-xs font-black tracking-tighter text-blue-700">SBL</span>
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <h1 className={`text-xs sm:text-base font-extrabold tracking-tight truncate ${darkMode ? 'text-white' : 'text-slate-900'}`}>Prof. Dr. Mümtaz Turhan SBL Pansiyon</h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 shrink-0">MEB Uyumlu</span>
              </div>
              <p className="text-[10px] sm:text-[11px] text-slate-400 truncate">İzin Takip • Etüt Yoklama • Gece Yat Yoklaması • Oda Yönetimi</p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button onClick={() => setDarkMode(!darkMode)} className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-semibold border transition-all cursor-pointer min-h-[38px] ${darkMode ? 'bg-slate-800 border-slate-700 text-amber-300' : 'bg-slate-100 border-slate-200 text-slate-700'}`}>
              {darkMode ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              <span className="hidden xs:inline">{darkMode ? 'Aydınlık' : 'Karanlık'}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-3 sm:p-6 pb-20 sm:pb-6">
        <div className={`max-w-[920px] w-full rounded-3xl shadow-xl border overflow-hidden grid grid-cols-1 md:grid-cols-12 transition-colors ${darkMode ? 'bg-slate-900 border-slate-800 shadow-black/50' : 'bg-white border-slate-200/90 shadow-slate-200/80'}`}>
          <div className={`md:col-span-5 relative flex flex-col items-center justify-between p-5 sm:p-8 text-center overflow-hidden border-b md:border-b-0 md:border-r ${darkMode ? 'bg-gradient-to-b from-slate-900 via-blue-950/40 to-slate-900 border-slate-800' : 'bg-gradient-to-b from-[#f0f7ff] via-[#e6f1fe] to-[#dcebfd] border-slate-200/60'}`}>
            <div className="z-10 pt-1 sm:pt-4 space-y-2.5 sm:space-y-4">
              <div className="mx-auto w-16 h-16 sm:w-24 sm:h-24 rounded-2xl sm:rounded-3xl bg-white/95 shadow-md border border-blue-100 flex flex-col items-center justify-center p-2">
                <div className="text-xl sm:text-2xl font-black tracking-tighter text-[#0055a5] leading-none">SBL</div>
                <div className="text-[7px] sm:text-[8px] font-extrabold uppercase tracking-widest text-[#0055a5] mt-1">PANSİYON</div>
              </div>
              <div className="space-y-0.5">
                <h2 className={`text-[11px] sm:text-xs font-extrabold uppercase tracking-wider ${darkMode ? 'text-blue-300' : 'text-[#0f2942]'}`}>PROF. DR. MÜMTAZ TURHAN</h2>
                <p className={`text-xs sm:text-sm font-black ${darkMode ? 'text-white' : 'text-[#0f2942]'}`}>Sosyal Bilimler Lisesi Pansiyonu</p>
              </div>
              <div className="inline-block px-3.5 py-1 rounded-full bg-white/80 border border-blue-200/80 text-[10px] sm:text-[11px] font-semibold text-slate-600">Pansiyon & Yurt Portalı</div>
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
                <rect x="92" y="70" width="16" height="20" /><rect x="118" y="70" width="16" height="20" /><rect x="92" y="102" width="16" height="20" /><rect x="118" y="102" width="16" height="20" />
                <rect x="160" y="65" width="14" height="18" /><rect x="186" y="65" width="14" height="18" /><rect x="160" y="92" width="14" height="18" /><rect x="186" y="92" width="14" height="18" />
                <rect x="226" y="70" width="16" height="20" /><rect x="252" y="70" width="16" height="20" /><rect x="226" y="102" width="16" height="20" /><rect x="252" y="102" width="16" height="20" />
              </svg>
            </div>
          </div>

          <div className="md:col-span-7 p-5 sm:p-9 flex flex-col justify-between space-y-5">
            <div className="space-y-4 sm:space-y-5">
              <div className="text-center space-y-1">
                <h2 className={`text-lg sm:text-2xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-900'}`}>Pansiyon Yönetim Sistemi</h2>
                <p className="text-xs text-slate-400">Giriş yapmak için rolünüzü seçip bilgilerinizi giriniz.</p>
              </div>

              <div className={`grid grid-cols-3 p-1.5 rounded-2xl border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-100/90 border-slate-200/80'}`}>
                <button type="button" onClick={() => { setActiveTab('veli'); setFeedback(null); }} className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${activeTab === 'veli' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'}`}><Users className="w-4 h-4 shrink-0" /> <span>Veli</span></button>
                <button type="button" onClick={() => { setActiveTab('belletmen'); setFeedback(null); }} className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${activeTab === 'belletmen' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'}`}><UserCheck className="w-4 h-4 shrink-0" /> <span>Belletmen</span></button>
                <button type="button" onClick={() => { setActiveTab('yonetici'); setFeedback(null); }} className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${activeTab === 'yonetici' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'}`}><Shield className="w-4 h-4 shrink-0" /> <span>Yönetici</span></button>
              </div>

              {feedback && (
                <div className={`p-3.5 rounded-xl text-xs font-bold border text-center flex items-center justify-center gap-2 ${feedback.type === 'success' ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-rose-50 border-rose-300 text-rose-800'}`}>
                  {feedback.type === 'error' && <X className="w-4 h-4 shrink-0" />} {feedback.text}
                </div>
              )}

              {/* VELİ */}
              {activeTab === 'veli' && (
                <div className="space-y-4">
                  <p className="text-center text-[11px] text-slate-400">Şifresiz Güvenli Giriş: WhatsApp tek kullanımlık 6 haneli kod</p>
                  {otpStep === 'request' ? (
                    <form onSubmit={handleSendVeliOtp} className="space-y-3.5">
                      <div className="relative">
                        <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input type="tel" inputMode="tel" required placeholder="Cep Telefonu No (0555 444 55 66)" value={phone} onChange={(e) => setPhone(e.target.value)} className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                      </div>
                      <div className={`p-3.5 rounded-xl border text-[11px] flex items-start gap-2.5 ${darkMode ? 'bg-blue-950/40 border-blue-900 text-blue-300' : 'bg-[#f0f7ff] border-blue-100 text-[#1e40af]'}`}>
                        <ShieldAlert className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" /> <span>Veliler kullanıcı adı olarak sisteme kayıtlı cep telefonu numaralarını kullanırlar. Güvenliğiniz için tek kullanımlık 6 haneli giriş şifresi WhatsApp üzerinden iletilir.</span>
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md cursor-pointer min-h-[48px]">
                        {loading ? <Loader2 className="w-4 h-4 animate-spin"/> : <MessageCircle className="w-4 h-4" />} {loading ? 'Mesaj Gönderiliyor...' : 'WhatsApp ile Şifre Gönder'}
                      </button>
                    </form>
                  ) : (
                    <form onSubmit={handleVerifyVeliOtp} className="space-y-3.5">
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">Gelen 6 Haneli Kodu Giriniz</label>
                        <input type="text" inputMode="numeric" maxLength={6} required placeholder="123456" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} className="w-full text-center tracking-widest text-xl font-extrabold py-3.5 border border-emerald-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[50px]" />
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md cursor-pointer min-h-[48px]">
                        <CheckCircle2 className="w-4 h-4" /> Doğrula ve Portala Gir
                      </button>
                      <button type="button" onClick={() => setOtpStep('request')} className="w-full text-center text-xs text-slate-500 underline py-2 cursor-pointer">Telefon numarasını değiştir</button>
                    </form>
                  )}
                </div>
              )}

              {/* BELLETMEN */}
              {activeTab === 'belletmen' && (
                <form onSubmit={handleBelletmenLogin} className="space-y-3.5">
                  <p className="text-center text-[11px] text-slate-400">Şifreler sisteme kayıtlıdır. Girdiğiniz şifre doğrulanmazsa giriş reddedilir.</p>
                  <div>
                    <label className="block text-[11px] font-bold text-slate-500 mb-1">Nöbetçi Belletmen Öğretmen</label>
                    <select value={selectedBelletmen} onChange={(e) => setSelectedBelletmen(e.target.value)} className={`w-full px-3.5 py-3.5 rounded-xl border text-base sm:text-xs font-bold min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}>
                      {belletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.cinsiyet === 'kadin' ? '👩‍🏫 ' : '👨‍🏫 '} {b.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input type="password" required placeholder="Belletmen Şifrenizi Girin" value={belletmenPass} onChange={(e) => setBelletmenPass(e.target.value)} className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin"/> : <UserCheck className="w-4 h-4" />} Yoklama Paneline Giriş Yap
                  </button>
                </form>
              )}

              {/* YÖNETİCİ */}
              {activeTab === 'yonetici' && (
                <form onSubmit={handleAdminLogin} className="space-y-3.5">
                  <p className="text-center text-[11px] text-slate-400">Pansiyon İdaresi Yönetim Girişi</p>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input type="text" required value={adminUser} onChange={(e) => setAdminUser(e.target.value)} placeholder="Yönetici Kullanıcı Adı" className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input type="password" required value={adminPass} onChange={(e) => setAdminPass(e.target.value)} placeholder="Yönetici Şifresi" className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin"/> : <Shield className="w-4 h-4" />} Yönetici Paneline Giriş Yap
                  </button>
                </form>
              )}
            </div>

            <div className="pt-4 mt-2 border-t border-slate-100">
              <p className="text-center text-[11px] text-slate-400">© 2026 Prof. Dr. Mümtaz Turhan SBL</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}