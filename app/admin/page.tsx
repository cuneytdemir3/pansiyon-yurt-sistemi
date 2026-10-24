'use client';

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