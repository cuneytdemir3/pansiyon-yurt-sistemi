'use client';

import React, { useState, useEffect } from 'react';
import { Users, Upload, Plus, Trash2, Home, Shield, FileSpreadsheet, CheckCircle2 } from 'lucide-react';

export default function AdminDashboardPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [nobetciler, setNobetciler] = useState<any[]>([]);
  const [dutyLogs, setDutyLogs] = useState<any[]>([]);
  const [msg, setMsg] = useState('');

  // Yeni Öğrenci Form State
  const [name, setName] = useState('');
  const [tc, setTc] = useState('');
  const [sinif, setSinif] = useState('9-A');
  const [kat, setKat] = useState(1);
  const [oda, setOda] = useState('101');
  const [yatak, setYatak] = useState('A');
  const [anneTel, setAnneTel] = useState('05416571469');
  const [babaTel, setBabaTel] = useState('05416571469');

  // Toplu CSV / Excel Yükleme State
  const [csvText, setCsvText] = useState(
    'Ali Veli, 12345678910, 9-B, 1, 103, A, 05416571469, 05416571469\nAyşe Fatma, 12345678911, 10-A, 2, 202, B, 05416571469, 05416571469'
  );

  const fetchAll = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        setStudents(data.store.students);
        setNobetciler(data.store.nobetciler || []);
        setDutyLogs(data.store.dutyLogs || []);
      }
    } catch {}
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_student',
        name,
        tc,
        sinif,
        kat,
        oda,
        yatak,
        anneTel,
        babaTel,
      }),
    });
    const data = await res.json();
    if (data.success) {
      setStudents(data.store.students);
      setName('');
      setTc('');
      setMsg(data.message);
    }
  };

  const handleBulkImport = async () => {
    const lines = csvText.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const parts = line.split(',').map((p) => p.trim());
      return {
        name: parts[0],
        tc: parts[1] || '10000000000',
        sinif: parts[2] || '9-A',
        kat: Number(parts[3]) || 1,
        oda: parts[4] || '101',
        yatak: parts[5] || 'A',
        anneTel: parts[6] || '05416571469',
        babaTel: parts[7] || '05416571469',
      };
    });

    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows }),
    });
    const data = await res.json();
    if (data.success) {
      setStudents(data.store.students);
      setMsg(data.message);
    }
  };

  const handleDelete = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_student', id }),
    });
    const data = await res.json();
    if (data.success) {
      setStudents(data.store.students);
      setMsg('Öğrenci silindi.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-6xl mx-auto space-y-6">

        {/* Üst Başlık */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg md:text-xl font-extrabold text-slate-900">Pansiyon İdare & Yönetici Paneli</h1>
              <p className="text-xs text-slate-500">e-Okul Excel öğrenci yükleme, oda/yatak yerleştirme ve nöbet defteri arşivi</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a href="/belletmen" className="text-xs font-bold text-blue-700 bg-blue-50 px-3 py-2 rounded-xl border border-blue-200">
              Belletmen Yoklama Ekranı
            </a>
            <a href="/veli" className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200">
              Veli İzin Portalı
            </a>
          </div>
        </div>

        {msg && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold flex justify-between">
            <span>✅ {msg}</span>
            <button onClick={() => setMsg('')} className="underline">Kapat</button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Tekli Öğrenci Ekleme */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Plus className="w-4 h-4 text-indigo-600" /> Yeni Öğrenci & Oda Kaydı
            </h2>
            <form onSubmit={handleAddStudent} className="grid grid-cols-2 gap-3 text-xs">
              <input
                type="text"
                required
                placeholder="Ad Soyad"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2"
              />
              <input
                type="text"
                placeholder="T.C. Kimlik No"
                value={tc}
                onChange={(e) => setTc(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2"
              />
              <input
                type="text"
                placeholder="Sınıf (Örn: 10-A)"
                value={sinif}
                onChange={(e) => setSinif(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2"
              />
              <select
                value={kat}
                onChange={(e) => setKat(Number(e.target.value))}
                className="border border-slate-200 rounded-xl px-3 py-2 bg-white"
              >
                <option value={1}>1. Kat</option>
                <option value={2}>2. Kat</option>
                <option value={3}>3. Kat</option>
              </select>
              <input
                type="text"
                placeholder="Oda No (Örn: 102)"
                value={oda}
                onChange={(e) => setOda(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2"
              />
              <input
                type="text"
                placeholder="Yatak (A, B, C, D)"
                value={yatak}
                onChange={(e) => setYatak(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2"
              />
              <input
                type="text"
                placeholder="Anne WhatsApp Tel"
                value={anneTel}
                onChange={(e) => setAnneTel(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2"
              />
              <input
                type="text"
                placeholder="Baba WhatsApp Tel"
                value={babaTel}
                onChange={(e) => setBabaTel(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2"
              />
              <button
                type="submit"
                className="col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-bold cursor-pointer"
              >
                Öğrenciyi Pansiyona Kaydet
              </button>
            </form>
          </div>

          {/* e-Okul / Excel (CSV) Toplu Öğrenci Aktarımı */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> e-Okul / Excel Toplu Öğrenci Yükleme
            </h2>
            <p className="text-[11px] text-slate-500">
              Format: <code>Ad Soyad, TC, Sınıf, Kat, Oda, Yatak, AnneTel, BabaTel</code> (Her satıra 1 öğrenci)
            </p>
            <textarea
              rows={4}
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
              className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50"
            />
            <button
              onClick={handleBulkImport}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer"
            >
              <Upload className="w-4 h-4" /> Listeyi Toplu Olarak Sisteme Aktar
            </button>
          </div>
        </div>

        {/* Kayıtlı Öğrenciler ve Oda Yerleşim Tablosu */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" /> Pansiyon Öğrenci ve Oda Yerleşim Listesi ({students.length} Öğrenci)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-700 text-left">
                  <th className="p-2.5 rounded-l-lg">Ad Soyad</th>
                  <th className="p-2.5">Sınıf</th>
                  <th className="p-2.5">Kat / Oda / Yatak</th>
                  <th className="p-2.5">Anne Tel</th>
                  <th className="p-2.5">Baba Tel</th>
                  <th className="p-2.5">Son Durum</th>
                  <th className="p-2.5 rounded-r-lg text-right">İşlem</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {students.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="p-2.5 font-bold text-slate-900">{s.name}</td>
                    <td className="p-2.5">{s.sinif}</td>
                    <td className="p-2.5 font-semibold text-blue-700">{s.kat}. Kat — Oda {s.oda} ({s.yatak})</td>
                    <td className="p-2.5 font-mono">{s.anneTel}</td>
                    <td className="p-2.5 font-mono">{s.babaTel}</td>
                    <td className="p-2.5">
                      <span className="px-2 py-0.5 rounded-md bg-slate-100 font-bold text-[11px]">
                        {s.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-2.5 text-right">
                      <button
                        onClick={() => handleDelete(s.id)}
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

        {/* Nöbetçi Belletmen Çizelgesi & Nöbet Defteri Arşivi */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900">Haftalık Nöbetçi Belletmen Çizelgesi</h3>
            <div className="space-y-2 text-xs">
              {nobetciler.map((n, idx) => (
                <div key={idx} className="p-3 bg-slate-50 rounded-xl flex justify-between items-center">
                  <strong className="text-slate-800">{n.gun}</strong>
                  <span className="font-bold text-indigo-700">{n.belletmen}</span>
                  <span className="text-slate-500">{n.kat}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900">Son Kaydedilen Resmî Nöbet Tutanakları</h3>
            <div className="space-y-2 text-xs">
              {dutyLogs.map((log) => (
                <div key={log.id} className="p-3 bg-indigo-50/50 border border-indigo-100 rounded-xl space-y-1">
                  <div className="flex justify-between font-bold text-indigo-950">
                    <span>{log.tarih} ({log.seans})</span>
                    <span>{log.belletmenAd}</span>
                  </div>
                  <p className="text-slate-600">{log.notlar}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}