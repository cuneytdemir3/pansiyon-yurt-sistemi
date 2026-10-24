'use client';

import React, { useState, useEffect } from 'react';
import {
  Users, Upload, Plus, Trash2, Shield, FileSpreadsheet, LogOut,
  KeyRound, Eye, EyeOff, Calendar, UserCheck, Wand2, Save
} from 'lucide-react';

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'belletmen' | 'nobet' | 'ogrenci'>('belletmen');

  const [students, setStudents] = useState<any[]>([]);
  const [belletmenler, setBelletmenler] = useState<any[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<any[]>([]);
  const [msg, setMsg] = useState('');

  // --- 1) TEKİL BELLETMEN EKLEME STATE ---
  const [bName, setBName] = useState('');
  const [bCinsiyet, setBCinsiyet] = useState<'erkek' | 'kadin'>('erkek');
  const [bBrans, setBBrans] = useState('');
  const [bPhone, setBPhone] = useState('0541');
  const [bPassword, setBPassword] = useState('1234');

  // --- EXCEL / CSV İLE TOPLU BELLETMEN EKLEME STATE ---
  const [belletmenCsv, setBelletmenCsv] = useState(
    'Serhat AKAN, erkek, Matematik, 05411112233, 1453\nElif DEMİR, kadin, Türk Dili ve Edebiyatı, 05412223344, 2026'
  );

  // --- ŞİFRE GÖRME VE DEĞİŞTİRME STATE ---
  const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({});
  const [editingPasswordId, setEditingPasswordId] = useState<string | null>(null);
  const [newPasswordVal, setNewPasswordVal] = useState('');

  // --- 2) AYLIK NÖBET LİSTESİ STATE ---
  const [nobetAySecim, setNobetAySecim] = useState('2026-10');
  const [nTarih, setNTarih] = useState('2026-10-29');
  const [nErkek1, setNErkek1] = useState('Cüneyt DEMİR');
  const [nErkek2, setNErkek2] = useState('Ali BEY');
  const [nKadin1, setNKadin1] = useState('Ayşenur KAYA');
  const [nKadin2, setNKadin2] = useState('Fatma YILMAZ');

  const [nobetCsv, setNobetCsv] = useState(
    '2026-10-29, Cüneyt DEMİR, Ali BEY, Ayşenur KAYA, Fatma YILMAZ\n2026-10-30, Furkan DEMİR, Hasan ÇELİK, Zeynep ŞAHİN, Merve AYDIN\n2026-10-31, Cüneyt DEMİR, Furkan DEMİR, Ayşenur KAYA, Merve AYDIN'
  );

  // --- 3) ÖĞRENCİ EKLEME STATE ---
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
    setStudents(store.students || []);
    setBelletmenler(store.belletmenler || []);
    setAylikNobetler(store.aylikNobetler || []);
  };

  const fetchAll = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        syncFromStore(data.store);
      }
    } catch {}
  };

  useEffect(() => {
    fetchAll();
  }, []);

  // --- BELLETMEN FONKSİYONLARI ---
  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_belletmen',
        name: bName,
        cinsiyet: bCinsiyet,
        brans: bBrans,
        phone: bPhone,
        password: bPassword,
      }),
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
      const parts = line.split(',').map((p) => p.trim());
      return {
        name: parts[0],
        cinsiyet: parts[1] || 'erkek',
        brans: parts[2] || 'Öğretmen',
        phone: parts[3] || '05410000000',
        password: parts[4] || '1234',
      };
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

  // --- AYLIK NÖBET FONKSİYONLARI ---
  const handleAddSingleDutyDay = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_or_update_monthly_duty',
        tarih: nTarih,
        erkek1: nErkek1,
        erkek2: nErkek2,
        kadin1: nKadin1,
        kadin2: nKadin2,
      }),
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
      return {
        tarih: p[0],
        erkek1: p[1] || '-',
        erkek2: p[2] || '-',
        kadin1: p[3] || '-',
        kadin2: p[4] || '-',
      };
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

  // --- ÖĞRENCİ FONKSİYONLARI ---
  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_student',
        name: sName,
        cinsiyet: sCinsiyet,
        tc: sTc,
        sinif: sSinif,
        kat: sKat,
        oda: sOda,
        yatak: sYatak,
        anneTel: sAnneTel,
        babaTel: sBabaTel,
      }),
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
      const parts = line.split(',').map((p) => p.trim());
      return {
        name: parts[0],
        cinsiyet: parts[1] || 'erkek',
        tc: parts[2] || '10000000000',
        sinif: parts[3] || '9-A',
        kat: Number(parts[4]) || 1,
        oda: parts[5] || '101',
        yatak: parts[6] || 'A',
        anneTel: parts[7] || '05416571469',
        babaTel: parts[8] || '05416571469',
      };
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
                Belletmen Şifre & Excel Yönetimi • Aylık Nöbet Listesi • Öğrenci & Oda Yönetimi
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
            <a href="/" className="flex items-center gap-1 text-xs font-bold text-white bg-rose-600 px-3 py-2 rounded-xl">
              <LogOut className="w-3.5 h-3.5" /> Çıkış
            </a>
          </div>
        </div>

        {/* SEKME MENÜSÜ */}
        <div className="bg-white rounded-2xl p-2 border border-slate-200 shadow-xs flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTab('belletmen')}
            className={`flex-1 min-w-[200px] flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'belletmen' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <KeyRound className="w-4 h-4" /> 1. Belletmen & Şifre Yönetimi ({belletmenler.length})
          </button>
          <button
            onClick={() => setActiveTab('nobet')}
            className={`flex-1 min-w-[200px] flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'nobet' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Calendar className="w-4 h-4" /> 2. Aylık Nöbet Listesi ({aylikNobetler.length} Gün)
          </button>
          <button
            onClick={() => setActiveTab('ogrenci')}
            className={`flex-1 min-w-[200px] flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'ogrenci' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Users className="w-4 h-4" /> 3. Öğrenci & Oda Yönetimi ({students.length})
          </button>
        </div>

        {msg && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold flex justify-between items-center">
            <span>✅ {msg}</span>
            <button onClick={() => setMsg('')} className="underline ml-4">Kapat</button>
          </div>
        )}

        {/* ======================================================================= */}
        {/* SEKME 1: BELLETMEN EKLEME (TEKİL & EXCEL) VE ŞİFRE GÖRME / DEĞİŞTİRME */}
        {/* ======================================================================= */}
        {activeTab === 'belletmen' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tekil Belletmen Ekleme */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Belletmen Öğretmen Ekle
                </h2>
                <form onSubmit={handleAddBelletmen} className="grid grid-cols-2 gap-3 text-xs">
                  <input
                    type="text"
                    required
                    placeholder="Ad Soyad (Örn: Cüneyt DEMİR)"
                    value={bName}
                    onChange={(e) => setBName(e.target.value)}
                    className="border border-slate-200 rounded-xl px-3 py-2.5 font-semibold"
                  />
                  <select
                    value={bCinsiyet}
                    onChange={(e) => setBCinsiyet(e.target.value as 'erkek' | 'kadin')}
                    className="border border-slate-200 rounded-xl px-3 py-2.5 font-bold bg-white"
                  >
                    <option value="erkek">👨 Erkek Belletmen</option>
                    <option value="kadin">👩 Kadın Belletmen</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Branş (Örn: Bilişim / Matematik)"
                    value={bBrans}
                    onChange={(e) => setBBrans(e.target.value)}
                    className="border border-slate-200 rounded-xl px-3 py-2.5"
                  />
                  <input
                    type="text"
                    placeholder="Telefon (0541...)"
                    value={bPhone}
                    onChange={(e) => setBPhone(e.target.value)}
                    className="border border-slate-200 rounded-xl px-3 py-2.5 font-mono"
                  />
                  <div className="col-span-2">
                    <label className="block text-[11px] font-bold text-slate-600 mb-1">Belletmen Giriş Şifresi:</label>
                    <input
                      type="text"
                      required
                      placeholder="Giriş Şifresi Belirleyin (Örn: 1234)"
                      value={bPassword}
                      onChange={(e) => setBPassword(e.target.value)}
                      className="w-full border border-indigo-200 bg-indigo-50/40 rounded-xl px-3 py-2.5 font-mono font-bold text-indigo-950"
                    />
                  </div>
                  <button
                    type="submit"
                    className="col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-bold cursor-pointer"
                  >
                    Belletmeni Sisteme Kaydet
                  </button>
                </form>
              </div>

              {/* Excel / CSV ile Toplu Belletmen Ekleme */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Excel / CSV ile Toplu Belletmen Ekleme
                </h2>
                <p className="text-[11px] text-slate-500">
                  Her satıra 1 öğretmen gelecek şekilde Excel’den yapıştırın:<br />
                  Format: <code>Ad Soyad, erkek/kadin, Branş, Telefon, Şifre</code>
                </p>
                <textarea
                  rows={4}
                  value={belletmenCsv}
                  onChange={(e) => setBelletmenCsv(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50"
                />
                <button
                  onClick={handleBulkAddBelletmen}
                  className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer"
                >
                  <Upload className="w-4 h-4" /> Excel Belletmen Listesini Toplu Yükle
                </button>
              </div>
            </div>

            {/* Belletmen Listesi + Şifre Görme ve Değiştirme Tablosu */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-indigo-600" /> Kayıtlı Belletmen Öğretmenler & Şifre Yönetimi ({belletmenler.length})
                </h2>
                <span className="text-[11px] text-slate-500">
                  👁️ Göz ikonuna tıklayarak şifreyi görebilir veya <strong>Şifre Değiştir</strong> ile yeni şifre atayabilirsiniz.
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-100 text-slate-700 text-left">
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Görev Grubu</th>
                      <th className="p-2.5">Branş</th>
                      <th className="p-2.5">Telefon</th>
                      <th className="p-2.5">Giriş Şifresi (Gör / Değiştir)</th>
                      <th className="p-2.5 text-right">İşlem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {belletmenler.map((b) => {
                      const isShown = !!visiblePasswords[b.id];
                      const isEditing = editingPasswordId === b.id;

                      return (
                        <tr key={b.id} className="hover:bg-slate-50">
                          <td className="p-2.5 font-extrabold text-slate-900">{b.name}</td>
                          <td className="p-2.5">
                            <span
                              className={`px-2.5 py-0.5 rounded-md font-bold text-[11px] ${
                                b.cinsiyet === 'kadin' ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {b.cinsiyet === 'kadin' ? '👩 Kadın Belletmen' : '👨 Erkek Belletmen'}
                            </span>
                          </td>
                          <td className="p-2.5 text-slate-600">{b.brans}</td>
                          <td className="p-2.5 font-mono">{b.phone}</td>
                          <td className="p-2.5">
                            {isEditing ? (
                              <div className="flex items-center gap-1.5">
                                <input
                                  type="text"
                                  value={newPasswordVal}
                                  onChange={(e) => setNewPasswordVal(e.target.value)}
                                  placeholder="Yeni şifre..."
                                  className="border border-indigo-300 rounded-lg px-2 py-1 text-xs font-mono w-28 bg-white"
                                />
                                <button
                                  onClick={() => handleUpdatePassword(b.id)}
                                  className="bg-emerald-600 text-white px-2.5 py-1 rounded-lg font-bold text-[11px] cursor-pointer"
                                >
                                  Kaydet
                                </button>
                                <button
                                  onClick={() => setEditingPasswordId(null)}
                                  className="text-slate-500 underline text-[11px] cursor-pointer"
                                >
                                  İptal
                                </button>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2">
                                <span className="font-mono font-bold bg-slate-100 px-2.5 py-1 rounded-lg text-slate-800">
                                  {isShown ? b.password : '••••••'}
                                </span>
                                <button
                                  type="button"
                                  onClick={() =>
                                    setVisiblePasswords((prev) => ({ ...prev, [b.id]: !prev[b.id] }))
                                  }
                                  className="p-1 text-slate-500 hover:text-indigo-600 cursor-pointer"
                                  title={isShown ? 'Şifreyi Gizle' : 'Şifreyi Gör'}
                                >
                                  {isShown ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setEditingPasswordId(b.id);
                                    setNewPasswordVal(b.password);
                                  }}
                                  className="text-[11px] font-bold text-indigo-600 hover:underline cursor-pointer"
                                >
                                  Şifre Değiştir
                                </button>
                              </div>
                            )}
                          </td>
                          <td className="p-2.5 text-right">
                            <button
                              onClick={() => handleDeleteBelletmen(b.id)}
                              className="text-rose-600 hover:text-rose-800 p-1 cursor-pointer"
                            >
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

        {/* ======================================================================= */}
        {/* SEKME 2: AYLIK NÖBET LİSTESİ EKLEME (OTOMATİK, EXCEL VE TEKİL GÜN)       */}
        {/* ======================================================================= */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            {/* Otomatik Ay Dağıtıcı Bar */}
            <div className="bg-indigo-950 text-white rounded-2xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="space-y-1">
                <h2 className="text-sm font-extrabold flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-amber-400" /> Kayıtlı Belletmenlerden Otomatik Aylık Nöbet Çizelgesi Oluştur
                </h2>
                <p className="text-xs text-indigo-200">
                  Seçtiğiniz ayın tüm günleri için (1’inden 30/31’ine kadar) her güne 2 Erkek + 2 Kadın belletmeni sırayla otomatik atar.
                </p>
              </div>
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <input
                  type="month"
                  value={nobetAySecim}
                  onChange={(e) => setNobetAySecim(e.target.value)}
                  className="bg-white text-slate-900 font-bold text-xs px-3 py-2.5 rounded-xl"
                />
                <button
                  onClick={handleAutoGenerateMonth}
                  className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs px-4 py-2.5 rounded-xl cursor-pointer whitespace-nowrap"
                >
                  Tüm Ayı Otomatik Doldur
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tekil Gün Nöbeti Ekle / Güncelle */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-blue-600" /> Günlük Nöbetçi Ata / Güncelle (2 Erkek + 2 Kadın)
                </h3>
                <form onSubmit={handleAddSingleDutyDay} className="grid grid-cols-2 gap-3 text-xs">
                  <div className="col-span-2">
                    <label className="block text-[11px] font-bold text-slate-600 mb-1">Nöbet Tarihi:</label>
                    <input
                      type="date"
                      required
                      value={nTarih}
                      onChange={(e) => setNTarih(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-3 py-2 font-bold"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-blue-700 mb-1">1. Erkek Belletmen:</label>
                    <select
                      value={nErkek1}
                      onChange={(e) => setNErkek1(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {erkekBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-blue-700 mb-1">2. Erkek Belletmen:</label>
                    <select
                      value={nErkek2}
                      onChange={(e) => setNErkek2(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {erkekBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-rose-700 mb-1">1. Kadın Belletmen:</label>
                    <select
                      value={nKadin1}
                      onChange={(e) => setNKadin1(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {kadinBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-rose-700 mb-1">2. Kadın Belletmen:</label>
                    <select
                      value={nKadin2}
                      onChange={(e) => setNKadin2(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {kadinBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <button
                    type="submit"
                    className="col-span-2 flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl font-bold cursor-pointer"
                  >
                    <Save className="w-4 h-4" /> Seçili Günün Nöbetçilerini Kaydet
                  </button>
                </form>
              </div>

              {/* Excel / CSV ile Aylık Toplu Nöbet Listesi Yükleme */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Excel ile Aylık Nöbet Listesi Toplu Yükleme
                </h3>
                <p className="text-[11px] text-slate-500">
                  Format: <code>YYYY-AA-GG, 1.Erkek, 2.Erkek, 1.Kadın, 2.Kadın</code>
                </p>
                <textarea
                  rows={5}
                  value={nobetCsv}
                  onChange={(e) => setNobetCsv(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50"
                />
                <button
                  onClick={handleBulkMonthlyDuty}
                  className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer"
                >
                  <Upload className="w-4 h-4" /> Aylık Nöbet Listesini Sisteme Aktar
                </button>
              </div>
            </div>

            {/* Aylık Nöbet Çizelgesi Tablosu */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900">
                Aktif Aylık Nöbet Çizelgesi ({aylikNobetler.length} Gün Kayıtlı)
              </h3>
              <div className="overflow-x-auto max-h-[480px]">
                <table className="w-full text-xs border-collapse">
                  <thead className="sticky top-0 bg-slate-100 text-slate-700 text-left">
                    <tr>
                      <th className="p-2.5">Tarih</th>
                      <th className="p-2.5 text-blue-800">1. Erkek Belletmen</th>
                      <th className="p-2.5 text-blue-800">2. Erkek Belletmen</th>
                      <th className="p-2.5 text-rose-800">1. Kadın Belletmen</th>
                      <th className="p-2.5 text-rose-800">2. Kadın Belletmen</th>
                      <th className="p-2.5 text-right">İşlem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {aylikNobetler.map((d) => (
                      <tr key={d.tarih} className="hover:bg-slate-50">
                        <td className="p-2.5 font-extrabold text-slate-900 font-mono">{d.tarih}</td>
                        <td className="p-2.5 font-semibold text-blue-700">👨 {d.erkek1}</td>
                        <td className="p-2.5 font-semibold text-blue-700">👨 {d.erkek2}</td>
                        <td className="p-2.5 font-semibold text-rose-700">👩 {d.kadin1}</td>
                        <td className="p-2.5 font-semibold text-rose-700">👩 {d.kadin2}</td>
                        <td className="p-2.5 text-right">
                          <button
                            onClick={() => handleDeleteDutyDay(d.tarih)}
                            className="text-rose-600 hover:text-rose-800 p-1 cursor-pointer"
                          >
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

        {/* ======================================================================= */}
        {/* SEKME 3: ÖĞRENCİ EKLEME (TEKİL & EXCEL) VE ODA LİSTESİ                  */}
        {/* ======================================================================= */}
        {activeTab === 'ogrenci' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Yeni Öğrenci & Oda Kaydı
                </h2>
                <form onSubmit={handleAddStudent} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={sName} onChange={(e) => setSName(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <select value={sCinsiyet} onChange={(e) => setSCinsiyet(e.target.value as 'erkek' | 'kiz')} className="border border-slate-200 rounded-xl px-3 py-2 font-bold bg-white">
                    <option value="erkek">Erkek Pansiyonu</option>
                    <option value="kiz">Kız Pansiyonu</option>
                  </select>
                  <input type="text" placeholder="T.C. Kimlik No" value={sTc} onChange={(e) => setSTc(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Sınıf (Örn: 10-A)" value={sSinif} onChange={(e) => setSSinif(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <select value={sKat} onChange={(e) => setSKat(Number(e.target.value))} className="border border-slate-200 rounded-xl px-3 py-2 bg-white">
                    <option value={1}>1. Kat</option>
                    <option value={2}>2. Kat</option>
                    <option value={3}>3. Kat</option>
                  </select>
                  <input type="text" placeholder="Oda No (Örn: 102 / K-101)" value={sOda} onChange={(e) => setSOda(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Anne WhatsApp Tel" value={sAnneTel} onChange={(e) => setSAnneTel(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Baba WhatsApp Tel" value={sBabaTel} onChange={(e) => setSBabaTel(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <button type="submit" className="col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    Öğrenciyi Pansiyona Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> e-Okul / Excel Toplu Öğrenci Yükleme
                </h2>
                <p className="text-[11px] text-slate-500">
                  Format: <code>Ad Soyad, erkek/kiz, TC, Sınıf, Kat, Oda, Yatak, AnneTel, BabaTel</code>
                </p>
                <textarea rows={4} value={studentCsv} onChange={(e) => setStudentCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkImportStudents} className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4" /> Öğrenci Listesini Toplu Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-600" /> Kayıtlı Öğrenciler ({students.length})
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-100 text-slate-700 text-left">
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Bölüm</th>
                      <th className="p-2.5">Kat / Oda / Yatak</th>
                      <th className="p-2.5">Anne Tel</th>
                      <th className="p-2.5">Durum</th>
                      <th className="p-2.5 text-right">İşlem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {students.map((s) => (
                      <tr key={s.id} className="hover:bg-slate-50">
                        <td className="p-2.5 font-bold text-slate-900">{s.name}</td>
                        <td className="p-2.5">
                          <span className={`px-2 py-0.5 rounded-md font-bold text-[11px] ${s.cinsiyet === 'kiz' ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'}`}>
                            {s.cinsiyet === 'kiz' ? 'Kız' : 'Erkek'}
                          </span>
                        </td>
                        <td className="p-2.5 font-semibold">{s.kat}. Kat — Oda {s.oda} ({s.yatak})</td>
                        <td className="p-2.5 font-mono">{s.anneTel}</td>
                        <td className="p-2.5 font-bold">{s.status.toUpperCase()}</td>
                        <td className="p-2.5 text-right">
                          <button onClick={() => handleDeleteStudent(s.id)} className="text-rose-600 hover:text-rose-800 p-1 cursor-pointer">
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