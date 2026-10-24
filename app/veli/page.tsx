'use client';

import React, { useState, useEffect } from 'react';
import { ShieldCheck, Calendar, Clock, Send, LogOut } from 'lucide-react';

export default function VeliPortalPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [leaves, setLeaves] = useState<any[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<string>('1');
  const [tip, setTip] = useState('Ev İzni (Hafta Sonu)');
  const [baslangic, setBaslangic] = useState('2026-10-24');
  const [bitis, setBitis] = useState('2026-10-26');
  const [aciklama, setAciklama] = useState('');
  const [veliTel, setVeliTel] = useState('05416571469');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  const fetchStore = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        setStudents(data.store.students);
        setLeaves(data.store.leaves);
      }
    } catch {}
  };

  useEffect(() => {
    fetchStore();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    document.cookie = 'token=; path=/; max-age=0;';
    window.location.href = '/veli/login';
  };

  const currentStudent = students.find((s) => s.id === selectedStudentId) || students[0];
  const studentLeaves = leaves.filter((l) => l.studentId === (currentStudent?.id || '1'));

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg('');
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add_leave',
          studentId: currentStudent?.id || '1',
          tip,
          baslangic,
          bitis,
          aciklama,
          veliTel,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setStudents(data.store.students);
        setLeaves(data.store.leaves);
        setAciklama('');
        setMsg('✅ İzin talebiniz onaylandı! Nöbetçi belletmen ekranına Otomatik İzinli olarak yansıtıldı.');

        await fetch('/api/belletmen/bildirim', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: veliTel,
            ogrenciAd: currentStudent?.name || 'Öğrenci',
            odaNo: currentStudent?.oda || '101',
            tarih: `${baslangic} / ${bitis}`,
            seans: 'izin_onay',
            veliTipi: `${tip} Onayı: ${aciklama || 'Veli İzin Talebi'}`
          }),
        });
      }
    } catch {
      setMsg('İzin kaydedilirken hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-4xl mx-auto space-y-6">

        {/* Üst Başlık ve Çıkış Butonu */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full">
                Prof. Dr. Mümtaz Turhan SBL Pansiyonu
              </span>
              <h1 className="text-lg md:text-xl font-extrabold text-slate-900 mt-0.5">Veli İzin & Öğrenci Takip Portalı</h1>
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <a href="/belletmen" className="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-2 rounded-xl hover:bg-blue-100">
              Belletmen Ekranı
            </a>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 px-4 py-2 rounded-xl shadow-xs transition-all cursor-pointer"
            >
              <LogOut className="w-4 h-4" /> Çıkış Yap
            </button>
          </div>
        </div>

        {/* Öğrenci Seçimi ve Durum Kartı */}
        {currentStudent && (
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-100 pb-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase">Öğrenci Seçimi</label>
                <select
                  value={selectedStudentId}
                  onChange={(e) => setSelectedStudentId(e.target.value)}
                  className="mt-1 text-sm font-bold text-slate-800 border border-slate-200 rounded-xl px-3 py-2 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} — Oda: {s.oda} ({s.sinif})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Anlık Pansiyon Durumu:</span>
                <span
                  className={`text-xs font-extrabold px-3 py-1 rounded-full ${
                    currentStudent.status === 'izinli'
                      ? 'bg-amber-100 text-amber-800'
                      : currentStudent.status === 'yok'
                      ? 'bg-rose-100 text-rose-700'
                      : 'bg-emerald-100 text-emerald-700'
                  }`}
                >
                  {currentStudent.status === 'izinli'
                    ? 'İzinli (Evci/Çarşı)'
                    : currentStudent.status === 'yok'
                    ? 'Yoklamada Bulunamadı'
                    : 'Pansiyonda (Mevcut)'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">Oda / Yatak</span>
                <strong className="text-slate-800 text-sm">Oda {currentStudent.oda} - Yatak {currentStudent.yatak}</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">Bulunduğu Kat</span>
                <strong className="text-slate-800 text-sm">{currentStudent.kat}. Kat</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">Sınıfı</span>
                <strong className="text-slate-800 text-sm">{currentStudent.sinif}</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">T.C. Kimlik</span>
                <strong className="text-slate-800 text-sm">{currentStudent.tc}</strong>
              </div>
            </div>
          </div>
        )}

        {msg && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold shadow-xs">
            {msg}
          </div>
        )}

        {/* Yeni Evci / Çarşı İzin Talep Formu */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-emerald-600" /> Yeni Evci / Çarşı İzin Talebi Oluştur
          </h2>
          <p className="text-xs text-slate-500">
            Oluşturduğunuz izinler anında nöbetçi belletmen yoklama ekranına <strong>Otomatik İzinli</strong> olarak düşer.
          </p>

          <form onSubmit={handleCreateLeave} className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">İzin Türü</label>
              <select
                value={tip}
                onChange={(e) => setTip(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-semibold bg-white"
              >
                <option value="Ev İzni">Hafta Sonu Evci İzni</option>
                <option value="Çarşı İzni">Günlük Çarşı / Kurs İzni</option>
                <option value="Sağlık / Rapor İzni">Sağlık / Hastane İzni</option>
                <option value="Özel Aile İzni">Özel Aile Ziyareti İzni</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Bilgilendirilecek WhatsApp No</label>
              <input
                type="text"
                value={veliTel}
                onChange={(e) => setVeliTel(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Başlangıç Tarihi</label>
              <input
                type="date"
                required
                value={baslangic}
                onChange={(e) => setBaslangic(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Dönüş (Bitiş) Tarihi</label>
              <input
                type="date"
                required
                value={bitis}
                onChange={(e) => setBitis(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 mb-1">İzin Açıklaması / Gidilecek Adres Özeti</label>
              <input
                type="text"
                required
                placeholder="Örn: Hafta sonu aile ziyareti / Ev izni"
                value={aciklama}
                onChange={(e) => setAciklama(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs"
              />
            </div>

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
              >
                <Send className="w-4 h-4" />
                {loading ? 'İzin Kaydediliyor ve WhatsApp Onayı Gönderiliyor...' : 'İzin Talebini Onayla ve Gönder'}
              </button>
            </div>
          </form>
        </div>

        {/* Geçmiş İzinler */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-600" /> Öğrencinin Aktif ve Geçmiş İzin Kayıtları
          </h3>
          {studentLeaves.length === 0 ? (
            <p className="text-xs text-slate-400">Henüz kayıtlı izin bulunmuyor.</p>
          ) : (
            <div className="space-y-2">
              {studentLeaves.map((l) => (
                <div key={l.id} className="p-3 bg-amber-50/70 border border-amber-200 rounded-xl flex flex-col sm:flex-row justify-between gap-2 text-xs">
                  <div>
                    <strong className="text-amber-900">{l.tip}:</strong>{' '}
                    <span className="text-amber-800">{l.baslangic} — {l.bitis} ({l.aciklama})</span>
                  </div>
                  <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-md self-start">
                    Onaylandı (Otomatik İzinli)
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}