'use client';

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