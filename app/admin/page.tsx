'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  Upload,
  Plus,
  Trash2,
  Shield,
  FileSpreadsheet,
  LogOut,
  KeyRound,
  Eye,
  EyeOff,
  Calendar,
  UserCheck,
  Wand2,
  Save,
  Activity,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
  X
} from 'lucide-react';

interface Student {
  id: string;
  name: string;
  cinsiyet: string;
  tc: string;
  sinif: string;
  kat: number;
  oda: string;
  yatak: string;
  anneTel: string;
  babaTel: string;
  status: string;
}

interface Belletmen {
  id: string;
  name: string;
  cinsiyet: string;
  brans: string;
  phone: string;
  password: string;
}

interface MonthlyDutyDay {
  tarih: string;
  erkek1: string;
  erkek2: string;
  kadin1: string;
  kadin2: string;
}

interface AuditLog {
  id: string;
  tarihSaat: string;
  kullanici: string;
  islem: string;
  detay: string;
  tur: string;
}

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'belletmen' | 'nobet' | 'ogrenci' | 'loglar'>('belletmen');

  const [students, setStudents] = useState<Student[]>([]);
  const [belletmenler, setBelletmenler] = useState<Belletmen[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<MonthlyDutyDay[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [msg, setMsg] = useState('');

  // 1) Belletmen State
  const [bName, setBName] = useState('');
  const [bCinsiyet, setBCinsiyet] = useState<'erkek' | 'kadin'>('erkek');
  const [bBrans, setBBrans] = useState('');
  const [bPhone, setBPhone] = useState('0541');
  const [bPassword, setBPassword] = useState('1234');
  const [belletmenCsv, setBelletmenCsv] = useState(
    'Serhat AKAN, erkek, Matematik, 05411112233, 1453\nElif DEMİR, kadin, Edebiyat, 05412223344, 2026'
  );

  const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({});
  const [editingPasswordId, setEditingPasswordId] = useState<string | null>(null);
  const [newPasswordVal, setNewPasswordVal] = useState('');

  // 2) Aylık Nöbet State
  const [nobetAySecim, setNobetAySecim] = useState('2026-10');
  const [nTarih, setNTarih] = useState('2026-10-29');
  const [nErkek1, setNErkek1] = useState('Cüneyt DEMİR');
  const [nErkek2, setNErkek2] = useState('Ali BEY');
  const [nKadin1, setNKadin1] = useState('Ayşenur KAYA');
  const [nKadin2, setNKadin2] = useState('Fatma YILMAZ');
  const [nobetCsv, setNobetCsv] = useState(
    '2026-10-29, Cüneyt DEMİR, Ali BEY, Ayşenur KAYA, Fatma YILMAZ\n2026-10-30, Furkan DEMİR, Hasan ÇELİK, Zeynep ŞAHİN, Merve AYDIN'
  );

  // 3) Öğrenci State
  const [sName, setSName] = useState('');
  const [sCinsiyet, setSCinsiyet] = useState<'erkek' | 'kiz'>('erkek');
  const [sTc, setSTc] = useState('');
  const [sSinif, setSSinif] = useState('9-A');
  const [sKat, setSKat] = useState(1);
  const [sOda, setSOda] = useState('101');
  const [sYatak, setSYatak] = useState('A');
  const [sAnneTel, setSAnneTel] = useState('05416571469');
  const [sBabaTel, setSBabaTel] = useState('05416571469');
  const [studentCsv, setStudentCsv] = useState(
    'Ali Veli, erkek, 12345678910, 9-B, 1, 103, A, 05416571469, 05416571469\nAyşe Fatma, kiz, 12345678911, 10-A, 1, K-102, B, 05416571469, 05416571469'
  );

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

  // --- BELLETMEN İŞLEMLERİ ---
  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_belletmen', name: bName, cinsiyet: bCinsiyet, brans: bBrans, phone: bPhone, password: bPassword }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setBName('');
      setBBrans('');
      setMsg(data.message);
    }
  };

  const handleBulkAddBelletmen = async () => {
    const lines = belletmenCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return { name: p[0], cinsiyet: p[1] || 'erkek', brans: p[2] || 'Öğretmen', phone: p[3] || '05410000000', password: p[4] || '1234' };
    });
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_add_belletmen', rows }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleUpdatePassword = async (id: string) => {
    if (!newPasswordVal.trim()) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'update_belletmen_password', id, newPassword: newPasswordVal }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setEditingPasswordId(null);
      setNewPasswordVal('');
      setMsg(data.message);
    }
  };

  const handleDeleteBelletmen = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_belletmen', id }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  // --- AYLIK NÖBET İŞLEMLERİ ---
  const handleAddSingleDutyDay = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_or_update_monthly_duty', tarih: nTarih, erkek1: nErkek1, erkek2: nErkek2, kadin1: nKadin1, kadin2: nKadin2 }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleAutoGenerateMonth = async () => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'auto_generate_month_duty', yearMonth: nobetAySecim }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleBulkMonthlyDuty = async () => {
    const lines = nobetCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return { tarih: p[0], erkek1: p[1] || '-', erkek2: p[2] || '-', kadin1: p[3] || '-', kadin2: p[4] || '-' };
    });
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_monthly_duty', rows }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleDeleteDutyDay = async (tarih: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_monthly_duty', tarih }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  // --- ÖĞRENCİ İŞLEMLERİ ---
  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_student', name: sName, cinsiyet: sCinsiyet, tc: sTc, sinif: sSinif, kat: sKat, oda: sOda, yatak: sYatak, anneTel: sAnneTel, babaTel: sBabaTel }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setSName('');
      setSTc('');
      setMsg(data.message);
    }
  };

  const handleBulkImportStudents = async () => {
    const lines = studentCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return { name: p[0], cinsiyet: p[1] || 'erkek', tc: p[2] || '10000000000', sinif: p[3] || '9-A', kat: Number(p[4]) || 1, oda: p[5] || '101', yatak: p[6] || 'A', anneTel: p[7] || '05416571469', babaTel: p[8] || '05416571469' };
    });
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleDeleteStudent = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_student', id }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleClearLogs = async () => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'clear_audit_logs' }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
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
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-6xl mx-auto space-y-6">

        {/* ÜST BAŞLIK */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg md:text-xl font-extrabold text-slate-900">Pansiyon İdare & Yönetici Paneli</h1>
              <p className="text-xs text-slate-500">
                Belletmen Şifre & Excel Yönetimi • Aylık Nöbet Listesi • Öğrenci Yönetimi • <strong className="text-indigo-600">Sistem Güvenlik & Denetim Günlüğü</strong>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <a href="/belletmen" className="text-xs font-bold text-blue-700 bg-blue-50 px-3 py-2 rounded-xl border border-blue-200">
              Belletmen Ekranı
            </a>
            <a href="/veli" className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200">
              Veli Portalı
            </a>
            <a href="/" className="flex items-center gap-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 px-4 py-2 rounded-xl">
              <LogOut className="w-4 h-4" /> Çıkış Yap
            </a>
          </div>
        </div>

        {/* 4 SEKMELİ MENÜ */}
        <div className="bg-white rounded-2xl p-2 border border-slate-200 shadow-xs flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTab('belletmen')}
            className={`flex-1 min-w-[160px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'belletmen' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <KeyRound className="w-4 h-4" /> 1. Belletmen & Şifre ({belletmenler.length})
          </button>
          <button
            onClick={() => setActiveTab('nobet')}
            className={`flex-1 min-w-[160px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'nobet' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Calendar className="w-4 h-4" /> 2. Aylık Nöbet ({aylikNobetler.length} Gün)
          </button>
          <button
            onClick={() => setActiveTab('ogrenci')}
            className={`flex-1 min-w-[160px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'ogrenci' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Users className="w-4 h-4" /> 3. Öğrenciler ({students.length})
          </button>
          <button
            onClick={() => setActiveTab('loglar')}
            className={`flex-1 min-w-[180px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'loglar' ? 'bg-slate-900 text-amber-400 shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Activity className="w-4 h-4" /> 4. Sistem Güvenlik & Denetim Günlüğü ({auditLogs.length})
          </button>
        </div>

        {msg && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold flex justify-between items-center">
            <span>✅ {msg}</span>
            <button onClick={() => setMsg('')} className="underline ml-4 cursor-pointer">Kapat</button>
          </div>
        )}

        {/* SEKME 4: SİSTEM GÜVENLİK & DENETİM GÜNLÜĞÜ */}
        {activeTab === 'loglar' && (
          <div className="bg-slate-950 rounded-3xl p-6 border border-slate-800 shadow-2xl space-y-5">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-amber-400" /> Sistem Güvenlik & Denetim Günlüğü (Audit Log)
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Belletmen girişleri, şifre değişiklikleri, öğrenci/izin hareketleri ve nöbet işlemleri saniye saniye kayıt altına alınır.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-3 py-1.5 rounded-full border border-emerald-800">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Canlı İzleme Aktif
                </div>
                <button
                  onClick={handleClearLogs}
                  className="text-[11px] font-bold text-rose-300 hover:text-white bg-rose-950/50 border border-rose-800 px-3 py-1.5 rounded-xl cursor-pointer"
                >
                  Günlüğü Temizle
                </button>
              </div>
            </div>

            <div className="overflow-x-auto max-h-[500px]">
              <table className="w-full text-xs border-collapse text-left">
                <thead className="sticky top-0 bg-slate-950">
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                    <th className="p-3">Tarih / Saat</th>
                    <th className="p-3">Kullanıcı / Kaynak</th>
                    <th className="p-3">İşlem Türü</th>
                    <th className="p-3">Açıklama & Detay</th>
                    <th className="p-3 text-right">Durum</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-900/60 transition-colors">
                      <td className="p-3 font-mono text-slate-300 flex items-center gap-2 whitespace-nowrap">
                        <Clock className="w-3.5 h-3.5 text-slate-500" /> {log.tarihSaat}
                      </td>
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
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Belletmen Öğretmen Ekle
                </h2>
                <form onSubmit={handleAddBelletmen} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={bName} onChange={(e) => setBName(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2.5 font-semibold" />
                  <select value={bCinsiyet} onChange={(e) => setBCinsiyet(e.target.value as 'erkek' | 'kadin')} className="border border-slate-200 rounded-xl px-3 py-2.5 font-bold bg-white">
                    <option value="erkek">👨 Erkek Belletmen</option>
                    <option value="kadin">👩 Kadın Belletmen</option>
                  </select>
                  <input type="text" placeholder="Branş" value={bBrans} onChange={(e) => setBBrans(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2.5" />
                  <input type="text" placeholder="Telefon" value={bPhone} onChange={(e) => setBPhone(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2.5 font-mono" />
                  <input type="text" required placeholder="Giriş Şifresi" value={bPassword} onChange={(e) => setBPassword(e.target.value)} className="col-span-2 border border-indigo-200 bg-indigo-50/40 rounded-xl px-3 py-2.5 font-mono font-bold" />
                  <button type="submit" className="col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    Belletmeni Sisteme Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Excel ile Toplu Belletmen Ekleme
                </h2>
                <p className="text-[11px] text-slate-500">Format: <code>Ad Soyad, erkek/kadin, Branş, Telefon, Şifre</code></p>
                <textarea rows={4} value={belletmenCsv} onChange={(e) => setBelletmenCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkAddBelletmen} className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4" /> Excel Belletmen Listesini Toplu Yükle
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-indigo-600" /> Kayıtlı Belletmenler & Şifre Görme / Değiştirme
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse text-left">
                  <thead>
                    <tr className="bg-slate-100 text-slate-700">
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Grup</th>
                      <th className="p-2.5">Branş</th>
                      <th className="p-2.5">Şifre (Gör / Değiştir)</th>
                      <th className="p-2.5 text-right">Sil</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {belletmenler.map((b) => {
                      const isShown = !!visiblePasswords[b.id];
                      const isEditing = editingPasswordId === b.id;
                      return (
                        <tr key={b.id} className="hover:bg-slate-50">
                          <td className="p-2.5 font-bold">{b.name}</td>
                          <td className="p-2.5">{b.cinsiyet === 'kadin' ? '👩 Kadın' : '👨 Erkek'}</td>
                          <td className="p-2.5">{b.brans}</td>
                          <td className="p-2.5">
                            {isEditing ? (
                              <div className="flex items-center gap-1.5">
                                <input type="text" value={newPasswordVal} onChange={(e) => setNewPasswordVal(e.target.value)} className="border border-indigo-300 rounded-lg px-2 py-1 text-xs font-mono w-24" />
                                <button onClick={() => handleUpdatePassword(b.id)} className="bg-emerald-600 text-white px-2.5 py-1 rounded-lg font-bold cursor-pointer">Kaydet</button>
                                <button onClick={() => setEditingPasswordId(null)} className="text-slate-500 underline cursor-pointer">İptal</button>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2">
                                <span className="font-mono font-bold bg-slate-100 px-2.5 py-1 rounded-lg">{isShown ? b.password : '••••••'}</span>
                                <button onClick={() => setVisiblePasswords((p) => ({ ...p, [b.id]: !p[b.id] }))} className="text-slate-500 hover:text-indigo-600 cursor-pointer">
                                  {isShown ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                                <button onClick={() => { setEditingPasswordId(b.id); setNewPasswordVal(b.password); }} className="text-indigo-600 font-bold hover:underline cursor-pointer">
                                  Şifre Değiştir
                                </button>
                              </div>
                            )}
                          </td>
                          <td className="p-2.5 text-right">
                            <button onClick={() => handleDeleteBelletmen(b.id)} className="text-rose-600 hover:text-rose-800 cursor-pointer">
                              <Trash2 className="w-4 h-4 inline" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* SEKME 2: AYLIK NÖBET LİSTESİ */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            <div className="bg-indigo-950 text-white rounded-2xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h2 className="text-sm font-extrabold flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-amber-400" /> Otomatik Aylık Nöbet Çizelgesi Oluştur
                </h2>
                <p className="text-xs text-indigo-200">Seçilen ayın tüm günlerine 2 Erkek + 2 Kadın belletmeni otomatik dağıtır.</p>
              </div>
              <div className="flex items-center gap-2">
                <input type="month" value={nobetAySecim} onChange={(e) => setNobetAySecim(e.target.value)} className="bg-white text-slate-900 font-bold text-xs px-3 py-2 rounded-xl" />
                <button onClick={handleAutoGenerateMonth} className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs px-4 py-2 rounded-xl cursor-pointer">
                  Tüm Ayı Otomatik Doldur
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900">Tekil Gün Nöbeti Ata</h3>
                <form onSubmit={handleAddSingleDutyDay} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="date" value={nTarih} onChange={(e) => setNTarih(e.target.value)} className="col-span-2 border rounded-xl px-3 py-2 font-bold" />
                  <select value={nErkek1} onChange={(e) => setNErkek1(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nErkek2} onChange={(e) => setNErkek2(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin1} onChange={(e) => setNKadin1(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin2} onChange={(e) => setNKadin2(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <button type="submit" className="col-span-2 bg-blue-600 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    <Save className="w-4 h-4 inline mr-1" /> Günü Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900">Excel ile Aylık Nöbet Listesi Yükle</h3>
                <textarea rows={4} value={nobetCsv} onChange={(e) => setNobetCsv(e.target.value)} className="w-full border rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkMonthlyDuty} className="w-full bg-emerald-600 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4 inline mr-1" /> Aylık Nöbet Listesini Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
              <div className="overflow-x-auto max-h-[420px]">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100 sticky top-0">
                    <tr>
                      <th className="p-2.5">Tarih</th>
                      <th className="p-2.5 text-blue-800">Erkek Belletmenler</th>
                      <th className="p-2.5 text-rose-800">Kadın Belletmenler</th>
                      <th className="p-2.5 text-right">Sil</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {aylikNobetler.map((d) => (
                      <tr key={d.tarih} className="hover:bg-slate-50">
                        <td className="p-2.5 font-mono font-bold">{d.tarih}</td>
                        <td className="p-2.5 text-blue-700 font-semibold">👨 {d.erkek1} & {d.erkek2}</td>
                        <td className="p-2.5 text-rose-700 font-semibold">👩 {d.kadin1} & {d.kadin2}</td>
                        <td className="p-2.5 text-right">
                          <button onClick={() => handleDeleteDutyDay(d.tarih)} className="text-rose-600 cursor-pointer">
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* SEKME 3: ÖĞRENCİ YÖNETİMİ */}
        {activeTab === 'ogrenci' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900">Yeni Öğrenci Kaydı</h2>
                <form onSubmit={handleAddStudent} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={sName} onChange={(e) => setSName(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <select value={sCinsiyet} onChange={(e) => setSCinsiyet(e.target.value as 'erkek' | 'kiz')} className="border rounded-xl px-3 py-2 font-bold bg-white">
                    <option value="erkek">Erkek Pansiyonu</option>
                    <option value="kiz">Kız Pansiyonu</option>
                  </select>
                  <input type="text" placeholder="T.C." value={sTc} onChange={(e) => setSTc(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Sınıf (9-A)" value={sSinif} onChange={(e) => setSSinif(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <select value={sKat} onChange={(e) => setSKat(Number(e.target.value))} className="border rounded-xl px-3 py-2 bg-white">
                    <option value={1}>1. Kat</option>
                    <option value={2}>2. Kat</option>
                    <option value={3}>3. Kat</option>
                  </select>
                  <input type="text" placeholder="Oda No" value={sOda} onChange={(e) => setSOda(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Anne Tel" value={sAnneTel} onChange={(e) => setSAnneTel(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Baba Tel" value={sBabaTel} onChange={(e) => setSBabaTel(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <button type="submit" className="col-span-2 bg-indigo-600 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    Öğrenciyi Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900">Excel ile Toplu Öğrenci Yükleme</h2>
                <textarea rows={4} value={studentCsv} onChange={(e) => setStudentCsv(e.target.value)} className="w-full border rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkImportStudents} className="w-full bg-emerald-600 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4 inline mr-1" /> Toplu Öğrenci Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100">
                    <tr>
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Bölüm</th>
                      <th className="p-2.5">Kat / Oda</th>
                      <th className="p-2.5">Anne Tel</th>
                      <th className="p-2.5 text-right">Sil</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {students.map((s) => (
                      <tr key={s.id} className="hover:bg-slate-50">
                        <td className="p-2.5 font-bold">{s.name}</td>
                        <td className="p-2.5">{s.cinsiyet === 'kiz' ? '👩 Kız' : '👨 Erkek'}</td>
                        <td className="p-2.5">{s.kat}. Kat - Oda {s.oda}</td>
                        <td className="p-2.5 font-mono">{s.anneTel}</td>
                        <td className="p-2.5 text-right">
                          <button onClick={() => handleDeleteStudent(s.id)} className="text-rose-600 cursor-pointer">
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}