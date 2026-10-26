"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import SblLogo from '../components/SblLogo';

export default function AdminPage() {
  const [store, setStore] = useState<any>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState<'ogrenciler' | 'belletmenler' | 'nobet' | 'defter' | 'loglar'>('ogrenciler');
  const [loading, setLoading] = useState(false);

  // Öğrenci Formu (Varsayılan telefonlar tamamen BOŞ!)
  const [stForm, setStForm] = useState({
    name: '', cinsiyet: 'erkek', kat: '1', oda: '101',
    anneAdi: '', anneTel: '', babaAdi: '', babaTel: ''
  });
  const [bulkText, setBulkText] = useState('');

  // Belletmen Formu
  const [belForm, setBelForm] = useState({
    name: '', cinsiyet: 'erkek', brans: '', phone: '', password: '1234'
  });

  // Aylık Nöbet Formu + Düzenleme Modu
  const [dutyForm, setDutyForm] = useState({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' });
  const [isEditingDuty, setIsEditingDuty] = useState(false);

  // Nöbet Defteri (Tutanak) Düzenleme Modu
  const [editingLog, setEditingLog] = useState<any>(null);

  const fetchStore = async () => {
    try {
      const res = await fetch('/api/pansiyon?t=' + Date.now(), { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setStore(data.store);
      }
    } catch (error) {
      console.error('Veri çekme hatası:', error);
    }
  };

  useEffect(() => {
    if (sessionStorage.getItem('pansiyon_admin_logged') === 'true') {
      setIsLoggedIn(true);
    }
  }, []);

  useEffect(() => {
    if (isLoggedIn) fetchStore();
  }, [isLoggedIn]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'admin_login', username: 'admin', password })
      });
      const data = await res.json();
      if (data.success) {
        sessionStorage.setItem('pansiyon_admin_logged', 'true');
        setIsLoggedIn(true);
        setStore(data.store);
      } else {
        alert(data.message || 'Hatalı şifre!');
      }
    } catch {
      alert('Giriş yapılamadı.');
    }
    setLoading(false);
  };

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_student', ...stForm })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setStForm({ name: '', cinsiyet: 'erkek', kat: '1', oda: '101', anneAdi: '', anneTel: '', babaAdi: '', babaTel: '' });
    }
    setLoading(false);
  };

  // Excel'den Kopyala-Yapıştır ile Toplu Öğrenci Yükleme (Numara boşsa boş kalır!)
  const handleBulkPasteImport = async () => {
    if (!bulkText.trim()) return;
    const lines = bulkText.trim().split('\n');
    const rows = lines.map((line) => {
      const parts = line.split(/\t|;|,/);
      return {
        name: (parts[0] || '').trim(),
        cinsiyet: (parts[1] || 'Erkek').trim(),
        kat: (parts[2] || '1').trim(),
        oda: (parts[3] || '101').trim(),
        anneAdi: (parts[4] || '').trim(),
        anneTel: (parts[5] || '').trim(),
        babaAdi: (parts[6] || '').trim(),
        babaTel: (parts[7] || '').trim()
      };
    }).filter((r) => r.name.length > 1);

    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setBulkText('');
      alert(data.message);
    }
    setLoading(false);
  };

  const handleClearAllStudents = async () => {
    if (!confirm('Tüm öğrenci listesini ve eski test numaralarını sıfırlamak istediğinize emin misiniz?')) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'clear_all_students' })
    });
    const data = await res.json();
    if (data.success) setStore(data.store);
  };

  const handleDeleteStudent = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_student', id })
    });
    const data = await res.json();
    if (data.success) setStore(data.store);
  };

  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_belletmen', ...belForm })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setBelForm({ name: '', cinsiyet: 'erkek', brans: '', phone: '', password: '1234' });
    }
    setLoading(false);
  };

  const handleDeleteBelletmen = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_belletmen', id })
    });
    const data = await res.json();
    if (data.success) setStore(data.store);
  };

  const handleDutySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_or_update_monthly_duty', ...dutyForm })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setDutyForm({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' });
      setIsEditingDuty(false);
    }
    setLoading(false);
  };

  const handleUpdateDutyLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingLog) return;
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'update_duty_log', ...editingLog })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setEditingLog(null);
      alert('Nöbet defterindeki belletmen isimleri güncellendi!');
    }
    setLoading(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f0f6ff] p-4">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-3xl shadow-xl border w-full max-w-md text-center">
          <div className="flex justify-center mb-4">
            <SblLogo size="lg" showText={false} />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900">SBL Pansiyon İdare Paneli</h2>
          <p className="text-xs text-slate-500 mt-1 mb-6">Öğrenci, Belletmen ve Nöbet Defteri Yönetimi</p>
          <input
            type="password"
            placeholder="Yönetici Şifresi"
            className="w-full p-3.5 border rounded-xl mb-4 text-center text-lg font-bold focus:outline-none focus:ring-2 focus:ring-[#006bb6]"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit" disabled={loading} className="w-full bg-[#006bb6] text-white p-3.5 rounded-xl font-bold hover:bg-[#005694] transition">
            {loading ? 'Giriş Yapılıyor...' : 'Yönetim Paneline Gir'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f8fc] text-slate-800">
      <header className="bg-white border-b sticky top-0 z-20 px-4 md:px-8 py-3">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-3">
          <SblLogo size="sm" />
          <div className="flex gap-2">
            <Link href="/" className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-2 rounded-xl text-xs font-bold">
              🏠 Ana Sayfa / Veli
            </Link>
            <Link href="/belletmen" className="bg-[#006bb6] hover:bg-[#005694] text-white px-3.5 py-2 rounded-xl text-xs font-bold">
              👨‍🏫 Belletmen Ekranı
            </Link>
            <button
              onClick={() => { sessionStorage.removeItem('pansiyon_admin_logged'); setIsLoggedIn(false); }}
              className="bg-rose-600 text-white px-3.5 py-2 rounded-xl text-xs font-bold"
            >
              Çıkış
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4 md:p-6 space-y-6">
        <div className="flex gap-2 overflow-x-auto pb-1">
          {[
            { id: 'ogrenciler', label: `👨‍🎓 Öğrenciler (${store?.students?.length || 0})` },
            { id: 'belletmenler', label: `👨‍🏫 Belletmenler (${store?.belletmenler?.length || 0})` },
            { id: 'nobet', label: `📅 Aylık Nöbet Çizelgesi (${store?.aylikNobetler?.length || 0})` },
            { id: 'defter', label: `📖 Pansiyon Nöbet Defteri (${store?.dutyLogs?.length || 0})` },
            { id: 'loglar', label: `📋 Denetim Günlüğü` }
          ].map((t: any) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-5 py-2.5 rounded-xl font-bold text-xs transition whitespace-nowrap ${
                activeTab === t.id ? 'bg-[#006bb6] text-white shadow' : 'bg-white text-slate-600 border hover:bg-slate-50'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* 1) ÖĞRENCİLER SEKMESİ */}
        {activeTab === 'ogrenciler' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border space-y-4">
              <div className="flex flex-wrap justify-between items-center gap-2">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">➕ Yeni Öğrenci Ekle</h2>
                  <p className="text-xs text-slate-500">Veli numarası boş bırakılırsa sistem artık otomatik numara atamaz, boş kaydeder.</p>
                </div>
                <button
                  type="button"
                  onClick={handleClearAllStudents}
                  className="bg-rose-100 hover:bg-rose-200 text-rose-700 px-3.5 py-2 rounded-xl text-xs font-bold"
                >
                  🗑️ Eski Test Öğrencilerini Sıfırla
                </button>
              </div>

              <form onSubmit={handleAddStudent} className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                <input required placeholder="Öğrenci Adı Soyadı" className="p-2.5 border rounded-xl" value={stForm.name} onChange={(e) => setStForm({ ...stForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-xl font-bold" value={stForm.cinsiyet} onChange={(e) => setStForm({ ...stForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Pansiyonu</option>
                  <option value="kiz">👩 Kız Pansiyonu</option>
                </select>
                <input required placeholder="Kat (1-4)" type="number" className="p-2.5 border rounded-xl" value={stForm.kat} onChange={(e) => setStForm({ ...stForm, kat: e.target.value })} />
                <input required placeholder="Oda No (Örn: 101)" className="p-2.5 border rounded-xl" value={stForm.oda} onChange={(e) => setStForm({ ...stForm, oda: e.target.value })} />
                <input placeholder="Anne Adı (İsteğe Bağlı)" className="p-2.5 border rounded-xl" value={stForm.anneAdi} onChange={(e) => setStForm({ ...stForm, anneAdi: e.target.value })} />
                <input placeholder="Anne Tel (Boş bırakılabilir)" className="p-2.5 border rounded-xl" value={stForm.anneTel} onChange={(e) => setStForm({ ...stForm, anneTel: e.target.value })} />
                <input placeholder="Baba Adı (İsteğe Bağlı)" className="p-2.5 border rounded-xl" value={stForm.babaAdi} onChange={(e) => setStForm({ ...stForm, babaAdi: e.target.value })} />
                <input placeholder="Baba Tel (Boş bırakılabilir)" className="p-2.5 border rounded-xl" value={stForm.babaTel} onChange={(e) => setStForm({ ...stForm, babaTel: e.target.value })} />
                <div className="md:col-span-4 flex justify-end">
                  <button type="submit" className="bg-[#006bb6] hover:bg-[#005694] text-white px-6 py-2.5 rounded-xl font-bold">
                    Öğrenciyi Kaydet
                  </button>
                </div>
              </form>

              {/* EXCEL KOPYALA YAPIŞTIR ALANI */}
              <div className="pt-4 border-t">
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  📥 Excel'den Toplu Yapıştır (Ad Soyad | Cinsiyet | Kat | Oda | Anne Adı | Anne Tel | Baba Adı | Baba Tel)
                </label>
                <textarea
                  rows={3}
                  placeholder="Excel tablonuzdaki satırları kopyalayıp buraya yapıştırın..."
                  value={bulkText}
                  onChange={(e) => setBulkText(e.target.value)}
                  className="w-full p-2.5 border rounded-xl text-xs font-mono"
                />
                <div className="flex justify-end mt-2">
                  <button
                    type="button"
                    onClick={handleBulkPasteImport}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-xl text-xs font-bold"
                  >
                    📥 Yapıştırılan Listeyi Buluta Aktar
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="p-3">Ad Soyad</th>
                    <th className="p-3">Pansiyon</th>
                    <th className="p-3">Kat / Oda</th>
                    <th className="p-3">Anne (Tel)</th>
                    <th className="p-3">Baba (Tel)</th>
                    <th className="p-3">Durum</th>
                    <th className="p-3 text-center">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  {(store?.students || []).map((s: any) => (
                    <tr key={s.id} className="border-t hover:bg-slate-50">
                      <td className="p-3 font-bold">{s.name}</td>
                      <td className="p-3">{s.cinsiyet === 'kiz' ? '👩 Kız' : '👨 Erkek'}</td>
                      <td className="p-3">{s.kat}. Kat / {s.oda}</td>
                      <td className="p-3">{s.anneAdi || '-'} ({s.anneTel || 'Numara Yok'})</td>
                      <td className="p-3">{s.babaAdi || '-'} ({s.babaTel || 'Numara Yok'})</td>
                      <td className="p-3 font-bold">{s.status.toUpperCase()}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteStudent(s.id)} className="bg-rose-500 text-white px-3 py-1 rounded-lg font-bold">
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 2) BELLETMENLER SEKMESİ */}
        {activeTab === 'belletmenler' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border">
              <h2 className="text-base font-extrabold mb-4">➕ Yeni Belletmen Öğretmen Ekle</h2>
              <form onSubmit={handleAddBelletmen} className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
                <input required placeholder="Ad Soyad" className="p-2.5 border rounded-xl" value={belForm.name} onChange={(e) => setBelForm({ ...belForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-xl font-bold" value={belForm.cinsiyet} onChange={(e) => setBelForm({ ...belForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Belletmen</option>
                  <option value="kadin">👩 Kadın Belletmen</option>
                </select>
                <input required placeholder="Branş" className="p-2.5 border rounded-xl" value={belForm.brans} onChange={(e) => setBelForm({ ...belForm, brans: e.target.value })} />
                <input placeholder="Telefon (İsteğe Bağlı)" className="p-2.5 border rounded-xl" value={belForm.phone} onChange={(e) => setBelForm({ ...belForm, phone: e.target.value })} />
                <input required placeholder="Şifre" className="p-2.5 border rounded-xl" value={belForm.password} onChange={(e) => setBelForm({ ...belForm, password: e.target.value })} />
                <div className="md:col-span-5 flex justify-end">
                  <button type="submit" className="bg-[#006bb6] text-white px-6 py-2.5 rounded-xl font-bold">
                    Belletmeni Kaydet
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="p-3">Ad Soyad</th>
                    <th className="p-3">Görev Bloğu</th>
                    <th className="p-3">Branş</th>
                    <th className="p-3">Telefon</th>
                    <th className="p-3">Şifre</th>
                    <th className="p-3 text-center">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  {(store?.belletmenler || []).map((b: any) => (
                    <tr key={b.id} className="border-t">
                      <td className="p-3 font-bold">{b.name}</td>
                      <td className="p-3">{b.cinsiyet === 'kadin' ? '👩 Kız Pansiyonu' : '👨 Erkek Pansiyonu'}</td>
                      <td className="p-3">{b.brans}</td>
                      <td className="p-3">{b.phone || '-'}</td>
                      <td className="p-3 font-mono">{b.password}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteBelletmen(b.id)} className="bg-rose-500 text-white px-3 py-1 rounded-lg font-bold">
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 3) AYLIK NÖBET ÇİZELGESİ (İSİM DÜZENLEME MODU) */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            <div className={`p-6 rounded-2xl shadow-sm border ${isEditingDuty ? 'bg-amber-50 border-amber-300' : 'bg-white'}`}>
              <h2 className="text-base font-extrabold mb-4">
                {isEditingDuty ? `✏️ ${dutyForm.tarih} Günü Nöbetçi Belletmen İsimlerini Düzenle` : '➕ Nöbet Günü Ekle / Güncelle'}
              </h2>
              <form onSubmit={handleDutySubmit} className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
                <input type="date" required className="p-2.5 border rounded-xl" value={dutyForm.tarih} onChange={(e) => setDutyForm({ ...dutyForm, tarih: e.target.value })} />
                <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-xl" value={dutyForm.erkek1} onChange={(e) => setDutyForm({ ...dutyForm, erkek1: e.target.value })} />
                <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-xl" value={dutyForm.erkek2} onChange={(e) => setDutyForm({ ...dutyForm, erkek2: e.target.value })} />
                <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-xl" value={dutyForm.kadin1} onChange={(e) => setDutyForm({ ...dutyForm, kadin1: e.target.value })} />
                <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-xl" value={dutyForm.kadin2} onChange={(e) => setDutyForm({ ...dutyForm, kadin2: e.target.value })} />
                <div className="md:col-span-5 flex justify-end gap-2">
                  {isEditingDuty && (
                    <button type="button" onClick={() => { setIsEditingDuty(false); setDutyForm({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' }); }} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                  )}
                  <button type="submit" className="bg-[#006bb6] text-white px-6 py-2 rounded-xl font-bold">
                    {isEditingDuty ? '💾 İsimleri Güncelle' : 'Kaydet'}
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="p-3">Tarih</th>
                    <th className="p-3">Erkek 1</th>
                    <th className="p-3">Erkek 2</th>
                    <th className="p-3">Kız 1</th>
                    <th className="p-3">Kız 2</th>
                    <th className="p-3 text-center">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  {(store?.aylikNobetler || []).map((d: any) => (
                    <tr key={d.tarih} className="border-t">
                      <td className="p-3 font-bold">{d.tarih}</td>
                      <td className="p-3">{d.erkek1}</td>
                      <td className="p-3">{d.erkek2}</td>
                      <td className="p-3">{d.kadin1}</td>
                      <td className="p-3">{d.kadin2}</td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => { setDutyForm(d); setIsEditingDuty(true); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                          className="bg-amber-500 text-white px-3 py-1 rounded-lg font-bold"
                        >
                          ✏️ İsimleri Düzenle
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 4) PANSİYON NÖBET DEFTERİ (BELLETMEN İSİMLERİNİ DÜZENLEME) */}
        {activeTab === 'defter' && (
          <div className="space-y-6">
            {editingLog && (
              <div className="bg-amber-50 border border-amber-300 p-6 rounded-2xl shadow-sm">
                <h2 className="text-base font-extrabold mb-3">
                  ✏️ Pansiyon Nöbet Defteri Belletmen İsimlerini Düzenle ({editingLog.tarih})
                </h2>
                <form onSubmit={handleUpdateDutyLog} className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                  <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-xl bg-white" value={editingLog.erkekBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen1: e.target.value })} />
                  <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-xl bg-white" value={editingLog.erkekBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen2: e.target.value })} />
                  <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-xl bg-white" value={editingLog.kizBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen1: e.target.value })} />
                  <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-xl bg-white" value={editingLog.kizBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen2: e.target.value })} />
                  <textarea rows={3} placeholder="Nöbet Notları" className="md:col-span-4 p-2.5 border rounded-xl bg-white" value={editingLog.notlar || ''} onChange={(e) => setEditingLog({ ...editingLog, notlar: e.target.value })} />
                  <div className="md:col-span-4 flex justify-end gap-2">
                    <button type="button" onClick={() => setEditingLog(null)} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                    <button type="submit" className="bg-amber-600 text-white px-6 py-2 rounded-xl font-bold">
                      💾 Nöbet Defterini Güncelle
                    </button>
                  </div>
                </form>
              </div>
            )}

            <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
              <h2 className="text-base font-extrabold">📖 Kayıtlı Pansiyon Nöbet Defteri Tutanakları</h2>
              {(store?.dutyLogs || []).length === 0 ? (
                <p className="text-xs text-slate-400 italic">Henüz nöbet defteri tutanağı girilmemiş.</p>
              ) : (
                (store?.dutyLogs || []).map((log: any) => (
                  <div key={log.id} className="p-4 border rounded-xl bg-slate-50 space-y-2 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-extrabold text-[#006bb6]">📅 {log.tarih} — {log.seans}</span>
                      <button
                        onClick={() => setEditingLog(log)}
                        className="bg-amber-500 hover:bg-amber-600 text-white px-3 py-1 rounded-lg font-bold"
                      >
                        ✏️ Belletmen İsimlerini Düzenle
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 bg-white p-3 rounded-lg border">
                      <div><strong>👨 Erkek Pansiyonu Nöbetçileri:</strong> {log.erkekBelletmen1 || '-'}, {log.erkekBelletmen2 || '-'}</div>
                      <div><strong>👩 Kız Pansiyonu Nöbetçileri:</strong> {log.kizBelletmen1 || '-'}, {log.kizBelletmen2 || '-'}</div>
                    </div>
                    <p className="text-slate-700"><strong>Notlar:</strong> {log.notlar}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* 5) DENETİM GÜNLÜĞÜ */}
        {activeTab === 'loglar' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6">
            <h2 className="text-base font-extrabold mb-4">📋 Sistem Denetim Günlüğü</h2>
            <div className="space-y-2 text-xs">
              {(store?.auditLogs || []).map((l: any) => (
                <div key={l.id} className="p-2.5 border rounded-lg flex justify-between">
                  <div><strong>{l.kullanici}</strong> — {l.islem}: {l.detay}</div>
                  <span className="text-slate-400">{l.tarihSaat}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}