"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function AdminPage() {
  const [store, setStore] = useState<any>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState<'ogrenciler' | 'belletmenler' | 'nobet' | 'defter' | 'loglar'>('ogrenciler');
  const [loading, setLoading] = useState(false);

  // Öğrenci Formu
  const [stForm, setStForm] = useState({
    name: '', cinsiyet: 'erkek', kat: '1', oda: '101',
    anneAdi: '', anneTel: '', babaAdi: '', babaTel: ''
  });

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

  // ÖĞRENCİ İŞLEMLERİ
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

  const handleLoadSampleStudents = async () => {
    setLoading(true);
    const sampleRows = [
      { name: 'Kerem Aksoy', cinsiyet: 'Erkek', kat: 1, oda: '101', anneAdi: 'sevgi Aksoy', anneTel: '', babaAdi: 'Murat Aksoy', babaTel: '' },
      { name: 'Emirhan Yıldız', cinsiyet: 'Erkek', kat: 2, oda: '201', anneAdi: 'Seda Yıldız', anneTel: '', babaAdi: 'Orhan Yıldız', babaTel: '' },
      { name: 'ZeynepSu Demir', cinsiyet: 'Kız', kat: 1, oda: 'K-101', anneAdi: 'Gül Demir', anneTel: '', babaAdi: 'Cüneyt Demir', babaTel: '' },
      { name: 'Elif Naz Kaya', cinsiyet: 'Kız', kat: 2, oda: 'K-202', anneAdi: 'Ayşe Kaya', anneTel: '', babaAdi: 'Kemal Kaya', babaTel: '' }
    ];
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows: sampleRows })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      alert(data.message);
    }
    setLoading(false);
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

  // BELLETMEN İŞLEMLERİ
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

  // AYLIK NÖBET EKLEME VE İSİM DÜZENLEME
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

  // NÖBET DEFTERİ (TUTANAK) BELLETMEN İSİMLERİNİ DÜZENLEME
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
      alert('Nöbet defterindeki belletmen isimleri ve notlar güncellendi!');
    }
    setLoading(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 p-4">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
          <h2 className="text-2xl font-extrabold text-center mb-2 text-slate-900">⚙️ SBL İdare Paneli</h2>
          <p className="text-xs text-center text-slate-500 mb-6">Öğrenci, Belletmen ve Nöbet Defteri Yönetimi</p>
          <input
            type="password"
            placeholder="Yönetici Şifresi (123456)"
            className="w-full p-3 border rounded-xl mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit" disabled={loading} className="w-full bg-indigo-600 text-white p-3 rounded-xl font-bold hover:bg-indigo-700 transition">
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-wrap justify-between items-center gap-3 mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900">🏫 Pansiyon Yönetim Paneli</h1>
            <p className="text-xs text-slate-500">Neon PostgreSQL 7/24 Kalıcı Bulut Senkronizasyonu Aktif</p>
          </div>
          <div className="flex gap-2">
            <Link href="/" className="bg-slate-200 hover:bg-slate-300 text-slate-800 px-4 py-2 rounded-lg text-sm font-bold">
              🏠 Veli Portalı
            </Link>
            <Link href="/belletmen" className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-bold">
              👨‍🏫 Belletmen Ekranı
            </Link>
            <button onClick={() => setIsLoggedIn(false)} className="bg-rose-600 text-white px-4 py-2 rounded-lg text-sm font-bold">
              Çıkış
            </button>
          </div>
        </header>

        {/* SEKMELER */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
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
              className={`px-5 py-2.5 rounded-xl font-bold text-sm transition whitespace-nowrap ${
                activeTab === t.id ? 'bg-indigo-600 text-white shadow-md' : 'bg-white text-slate-600 border hover:bg-slate-100'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* 1) ÖĞRENCİLER SEKMESİ */}
        {activeTab === 'ogrenciler' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border">
              <div className="flex flex-wrap justify-between items-center gap-2 mb-4">
                <h2 className="text-lg font-extrabold">➕ Yeni Öğrenci Ekle</h2>
                <button
                  type="button"
                  onClick={handleLoadSampleStudents}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-xs font-bold shadow"
                >
                  ✨ Tek Tıkla Örnek Öğrencileri Yükle
                </button>
              </div>
              <form onSubmit={handleAddStudent} className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <input required placeholder="Öğrenci Adı Soyadı" className="p-2.5 border rounded-lg" value={stForm.name} onChange={(e) => setStForm({ ...stForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-lg font-semibold" value={stForm.cinsiyet} onChange={(e) => setStForm({ ...stForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Pansiyonu</option>
                  <option value="kiz">👩 Kız Pansiyonu</option>
                </select>
                <input required placeholder="Kat (1-4)" type="number" className="p-2.5 border rounded-lg" value={stForm.kat} onChange={(e) => setStForm({ ...stForm, kat: e.target.value })} />
                <input required placeholder="Oda No (Örn: 101)" className="p-2.5 border rounded-lg" value={stForm.oda} onChange={(e) => setStForm({ ...stForm, oda: e.target.value })} />
                <input required placeholder="Anne Adı" className="p-2.5 border rounded-lg" value={stForm.anneAdi} onChange={(e) => setStForm({ ...stForm, anneAdi: e.target.value })} />
                <input required placeholder="Anne Telefon (05XX...)" className="p-2.5 border rounded-lg" value={stForm.anneTel} onChange={(e) => setStForm({ ...stForm, anneTel: e.target.value })} />
                <input required placeholder="Baba Adı" className="p-2.5 border rounded-lg" value={stForm.babaAdi} onChange={(e) => setStForm({ ...stForm, babaAdi: e.target.value })} />
                <input required placeholder="Baba Telefon (05XX...)" className="p-2.5 border rounded-lg" value={stForm.babaTel} onChange={(e) => setStForm({ ...stForm, babaTel: e.target.value })} />
                <div className="md:col-span-4 flex justify-end">
                  <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl font-bold">
                    Öğrenciyi Kaydet
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-sm">
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
                      <td className="p-3">{s.anneAdi} ({s.anneTel})</td>
                      <td className="p-3">{s.babaAdi} ({s.babaTel})</td>
                      <td className="p-3 font-bold">{s.status.toUpperCase()}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteStudent(s.id)} className="bg-rose-500 text-white px-3 py-1 rounded text-xs font-bold">
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
              <h2 className="text-lg font-extrabold mb-4">➕ Yeni Belletmen Öğretmen Ekle</h2>
              <form onSubmit={handleAddBelletmen} className="grid grid-cols-1 md:grid-cols-5 gap-3">
                <input required placeholder="Ad Soyad" className="p-2.5 border rounded-lg" value={belForm.name} onChange={(e) => setBelForm({ ...belForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-lg font-semibold" value={belForm.cinsiyet} onChange={(e) => setBelForm({ ...belForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Belletmen</option>
                  <option value="kadin">👩 Kadın Belletmen</option>
                </select>
                <input required placeholder="Branş" className="p-2.5 border rounded-lg" value={belForm.brans} onChange={(e) => setBelForm({ ...belForm, brans: e.target.value })} />
                <input required placeholder="Telefon" className="p-2.5 border rounded-lg" value={belForm.phone} onChange={(e) => setBelForm({ ...belForm, phone: e.target.value })} />
                <input required placeholder="Şifre" className="p-2.5 border rounded-lg" value={belForm.password} onChange={(e) => setBelForm({ ...belForm, password: e.target.value })} />
                <div className="md:col-span-5 flex justify-end">
                  <button type="submit" className="bg-indigo-600 text-white px-6 py-2.5 rounded-xl font-bold">
                    Belletmeni Kaydet
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-sm">
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
                      <td className="p-3">{b.phone}</td>
                      <td className="p-3 font-mono">{b.password}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteBelletmen(b.id)} className="bg-rose-500 text-white px-3 py-1 rounded text-xs font-bold">
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

        {/* 3) AYLIK NÖBET ÇİZELGESİ (BELLETMEN İSİMLERİNİ DÜZENLEME DESTEKLİ) */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            <div className={`p-6 rounded-2xl shadow-sm border ${isEditingDuty ? 'bg-amber-50 border-amber-300' : 'bg-white'}`}>
              <h2 className="text-lg font-extrabold mb-4">
                {isEditingDuty ? `✏️ ${dutyForm.tarih} Günü Nöbetçi Belletmen İsimlerini Düzenle` : '➕ Nöbet Günü Ekle / Güncelle'}
              </h2>
              <form onSubmit={handleDutySubmit} className="grid grid-cols-1 md:grid-cols-5 gap-3">
                <input type="date" required className="p-2.5 border rounded-lg" value={dutyForm.tarih} onChange={(e) => setDutyForm({ ...dutyForm, tarih: e.target.value })} />
                <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-lg" value={dutyForm.erkek1} onChange={(e) => setDutyForm({ ...dutyForm, erkek1: e.target.value })} />
                <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-lg" value={dutyForm.erkek2} onChange={(e) => setDutyForm({ ...dutyForm, erkek2: e.target.value })} />
                <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-lg" value={dutyForm.kadin1} onChange={(e) => setDutyForm({ ...dutyForm, kadin1: e.target.value })} />
                <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-lg" value={dutyForm.kadin2} onChange={(e) => setDutyForm({ ...dutyForm, kadin2: e.target.value })} />
                <div className="md:col-span-5 flex justify-end gap-2">
                  {isEditingDuty && (
                    <button type="button" onClick={() => { setIsEditingDuty(false); setDutyForm({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' }); }} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                  )}
                  <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold">
                    {isEditingDuty ? '💾 Güncellemeyi Kaydet' : 'Kaydet'}
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-sm">
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
                      <td className="p-3 text-center space-x-2">
                        <button
                          onClick={() => { setDutyForm(d); setIsEditingDuty(true); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                          className="bg-amber-500 text-white px-3 py-1 rounded text-xs font-bold"
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

        {/* 4) PANSİYON NÖBET DEFTERİ (TUTANAKLARDAKİ BELLETMEN İSİMLERİNİ DÜZENLEME) */}
        {activeTab === 'defter' && (
          <div className="space-y-6">
            {editingLog && (
              <div className="bg-amber-50 border border-amber-300 p-6 rounded-2xl shadow-sm">
                <h2 className="text-lg font-extrabold mb-3">
                  ✏️ Pansiyon Nöbet Defteri Kaydını ve Belletmen İsimlerini Düzenle ({editingLog.tarih})
                </h2>
                <form onSubmit={handleUpdateDutyLog} className="grid grid-cols-1 md:grid-cols-4 gap-3">
                  <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-lg bg-white" value={editingLog.erkekBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen1: e.target.value })} />
                  <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-lg bg-white" value={editingLog.erkekBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen2: e.target.value })} />
                  <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-lg bg-white" value={editingLog.kizBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen1: e.target.value })} />
                  <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-lg bg-white" value={editingLog.kizBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen2: e.target.value })} />
                  <textarea rows={3} placeholder="Nöbet Notları" className="md:col-span-4 p-2.5 border rounded-lg bg-white" value={editingLog.notlar || ''} onChange={(e) => setEditingLog({ ...editingLog, notlar: e.target.value })} />
                  <div className="md:col-span-4 flex justify-end gap-2">
                    <button type="button" onClick={() => setEditingLog(null)} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                    <button type="submit" className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-2 rounded-xl font-bold">
                      💾 Nöbet Defterini Güncelle
                    </button>
                  </div>
                </form>
              </div>
            )}

            <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
              <h2 className="text-lg font-extrabold">📖 Kayıtlı Pansiyon Nöbet Defteri Tutanakları</h2>
              {(store?.dutyLogs || []).length === 0 ? (
                <p className="text-sm text-slate-500 italic">Henüz nöbet defteri tutanağı girilmemiş.</p>
              ) : (
                (store?.dutyLogs || []).map((log: any) => (
                  <div key={log.id} className="p-4 border rounded-xl bg-slate-50 space-y-2">
                    <div className="flex flex-wrap justify-between items-center gap-2">
                      <span className="font-extrabold text-indigo-900">📅 {log.tarih} — {log.seans}</span>
                      <button
                        onClick={() => setEditingLog(log)}
                        className="bg-amber-500 hover:bg-amber-600 text-white px-3 py-1 rounded-lg text-xs font-bold"
                      >
                        ✏️ Belletmen İsimlerini / Notu Düzenle
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs bg-white p-3 rounded-lg border">
                      <div><strong>👨 Erkek Pansiyonu Nöbetçileri:</strong> {log.erkekBelletmen1 || '-'}, {log.erkekBelletmen2 || '-'}</div>
                      <div><strong>👩 Kız Pansiyonu Nöbetçileri:</strong> {log.kizBelletmen1 || '-'}, {log.kizBelletmen2 || '-'}</div>
                    </div>
                    <p className="text-sm text-slate-700"><strong>Notlar:</strong> {log.notlar}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* 5) DENETİM GÜNLÜĞÜ */}
        {activeTab === 'loglar' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6">
            <h2 className="text-lg font-extrabold mb-4">📋 Sistem Denetim Günlüğü</h2>
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
      </div>
    </div>
  );
}