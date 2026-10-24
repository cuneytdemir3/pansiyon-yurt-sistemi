'use client';

import React, { useState } from 'react';
import { Calendar, FileText, CheckCircle2, Home, Send, Check, Loader2, Phone } from 'lucide-react';

interface Student {
  id: string;
  name: string;
  kat: number;
  oda: string;
  yatak: string;
  tc: string;
  status: 'var' | 'yok' | 'izinli';
  izinAciklama?: string;
  anneTel: string;
  babaTel: string;
}

const initialStudents: Student[] = [
  {
    id: '1',
    name: 'Ahmet Yılmaz',
    kat: 1,
    oda: '101',
    yatak: 'A',
    tc: '12345678901',
    status: 'izinli',
    izinAciklama: '2026-10-21 — 2026-10-30 (Ev İzni: akraba ziyareti)',
    anneTel: '05416571469',
    babaTel: '05416571469',
  },
  {
    id: '2',
    name: 'Mehmet Demir',
    kat: 1,
    oda: '101',
    yatak: 'B',
    tc: '12345678902',
    status: 'izinli',
    izinAciklama: '2026-10-20 — 2026-10-25 (Ev İzni: Aile ziyareti ve hafta sonu ev izni)',
    anneTel: '05416571469',
    babaTel: '05416571469',
  },
  {
    id: '3',
    name: 'Canberk Öztürk',
    kat: 1,
    oda: '102',
    yatak: 'A',
    tc: '12345678905',
    status: 'yok',
    anneTel: '05416571469',
    babaTel: '05556667788',
  },
  {
    id: '4',
    name: 'Burak Kaya',
    kat: 2,
    oda: '201',
    yatak: 'A',
    tc: '12345678908',
    status: 'var',
    anneTel: '05416571469',
    babaTel: '05416571469',
  },
  {
    id: '5',
    name: 'Emre Çelik',
    kat: 3,
    oda: '301',
    yatak: 'A',
    tc: '12345678909',
    status: 'var',
    anneTel: '05416571469',
    babaTel: '05416571469',
  }
];

export default function BelletmenPage() {
  const [students, setStudents] = useState<Student[]>(initialStudents);
  const [selectedKat, setSelectedKat] = useState<number>(1);
  const [tarih, setTarih] = useState<string>('2026-10-24');
  const [seans, setSeans] = useState<'etut' | 'yat'>('etut');
  const [sendingKey, setSendingKey] = useState<string | null>(null);
  const [sentKeys, setSentKeys] = useState<Record<string, boolean>>({});
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [nobetDefteriAcik, setNobetDefteriAcik] = useState(false);
  const [nobetNotu, setNobetNotu] = useState('');

  const katStudents = students.filter((s) => s.kat === selectedKat);
  const katMevcudu = katStudents.length;
  const varSayisi = katStudents.filter((s) => s.status === 'var').length;
  const yokSayisi = katStudents.filter((s) => s.status === 'yok').length;
  const izinliSayisi = katStudents.filter((s) => s.status === 'izinli').length;

  const odalar = Array.from(new Set(katStudents.map((s) => s.oda))).sort();

  const handleStatusChange = (id: string, newStatus: 'var' | 'yok') => {
    setStudents((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: newStatus } : s))
    );
  };

  const handlePhoneChange = (id: string, field: 'anneTel' | 'babaTel', value: string) => {
    setStudents((prev) =>
      prev.map((s) => (s.id === id ? { ...s, [field]: value } : s))
    );
  };

  const handleTumunuVarYap = () => {
    setStudents((prev) =>
      prev.map((s) =>
        s.kat === selectedKat && s.status !== 'izinli' ? { ...s, status: 'var' } : s
      )
    );
  };

  const handleSendWhatsApp = async (student: Student, veliTipi: 'Anne' | 'Baba', phone: string) => {
    const btnKey = `${student.id}-${veliTipi}`;
    setSendingKey(btnKey);
    setFeedback(null);

    try {
      const res = await fetch('/api/belletmen/bildirim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          ogrenciAd: student.name,
          odaNo: student.oda,
          tarih,
          seans,
          veliTipi
        })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        setSentKeys((prev) => ({ ...prev, [btnKey]: true }));
        setFeedback({ type: 'success', text: data.message });
      } else {
        setFeedback({
          type: 'error',
          text: data.message || 'WhatsApp mesajı iletilemedi. WhatsApp botunun açık olduğundan emin olun.'
        });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucuya bağlanırken hata oluştu.' });
    } finally {
      setSendingKey(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-5xl mx-auto space-y-5">

        {/* Üst Bilgi ve Tarih / Seans Seçimi */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
            <div>
              <h1 className="text-lg md:text-xl font-bold text-slate-800">Nöbetçi Belletmen Yoklama & İzin Ekranı</h1>
              <p className="text-xs text-slate-500">
                Etüt (19:15) ve Yat Yoklaması (23:00) • Veli izin tarihleri arasında öğrenciler otomatik İzinli sayılır
              </p>
            </div>
            <span className="text-xs font-semibold bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full border border-emerald-200">
              WhatsApp Bot Entegre
            </span>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5">
                <Calendar className="w-4 h-4 text-blue-600" />
                <span className="text-xs font-medium text-slate-600">Yoklama Tarihi:</span>
                <input
                  type="date"
                  value={tarih}
                  onChange={(e) => setTarih(e.target.value)}
                  className="text-xs font-bold text-slate-800 bg-transparent focus:outline-none"
                />
              </div>

              <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
                <button
                  onClick={() => setSeans('etut')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    seans === 'etut' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'
                  }`}
                >
                  Etüt (19:15)
                </button>
                <button
                  onClick={() => setSeans('yat')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    seans === 'yat' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'
                  }`}
                >
                  Yat (23:00)
                </button>
              </div>
            </div>

            <button
              onClick={() => setNobetDefteriAcik(!nobetDefteriAcik)}
              className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
            >
              <FileText className="w-4 h-4" /> (Resmî Nöbet Defteri)
            </button>
          </div>

          {nobetDefteriAcik && (
            <div className="p-4 bg-indigo-50/60 border border-indigo-200 rounded-xl space-y-3">
              <h3 className="text-xs font-bold text-indigo-950">Günlük Nöbet Defteri Olay / Vukuat Kaydı</h3>
              <textarea
                rows={3}
                value={nobetNotu}
                onChange={(e) => setNobetNotu(e.target.value)}
                placeholder="Nöbet süresince yaşanan önemli durumları buraya yazabilirsiniz..."
                className="w-full p-3 text-xs bg-white border border-indigo-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={() => {
                  setFeedback({ type: 'success', text: '✅ Nöbet defteri kaydı başarıyla eklendi.' });
                  setNobetDefteriAcik(false);
                }}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-xs font-bold cursor-pointer"
              >
                Nöbet Defterini Kaydet
              </button>
            </div>
          )}
        </div>

        {/* Bildirim Durum Mesajı */}
        {feedback && (
          <div
            className={`p-4 rounded-2xl border text-xs font-bold flex items-center justify-between shadow-sm ${
              feedback.type === 'success'
                ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                : 'bg-rose-50 border-rose-300 text-rose-800'
            }`}
          >
            <span>{feedback.text}</span>
            <button onClick={() => setFeedback(null)} className="text-xs underline ml-4">Kapat</button>
          </div>
        )}

        {/* Kat Seçimi ve Tümünü Var Yap */}
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {[1, 2, 3].map((kat) => (
              <button
                key={kat}
                onClick={() => setSelectedKat(kat)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  selectedKat === kat
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {kat}. Kat
              </button>
            ))}
          </div>

          <button
            onClick={handleTumunuVarYap}
            className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4" /> Tümünü Var Yap
          </button>
        </div>

        {/* Özet Kartları */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs text-slate-500">Kat Mevcudu</div>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{katMevcudu}</div>
          </div>
          <div className="bg-emerald-50/70 p-4 rounded-2xl border border-emerald-200 shadow-sm">
            <div className="text-xs text-emerald-700 font-medium">Var</div>
            <div className="text-xl font-extrabold text-emerald-700 mt-1">{varSayisi}</div>
          </div>
          <div className="bg-rose-50/70 p-4 rounded-2xl border border-rose-200 shadow-sm">
            <div className="text-xs text-rose-700 font-medium">Yok</div>
            <div className="text-xl font-extrabold text-rose-700 mt-1">{yokSayisi}</div>
          </div>
          <div className="bg-amber-50/70 p-4 rounded-2xl border border-amber-200 shadow-sm">
            <div className="text-xs text-amber-700 font-medium">Veli İzinli (Otomatik)</div>
            <div className="text-xl font-extrabold text-amber-700 mt-1">{izinliSayisi}</div>
          </div>
        </div>

        {/* Odalar ve Öğrenci Kartları */}
        <div className="space-y-5">
          {odalar.map((odaNo) => {
            const odaOgrencileri = katStudents.filter((s) => s.oda === odaNo);
            return (
              <div key={odaNo} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="bg-slate-900 text-white px-5 py-3 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold">
                    <Home className="w-4 h-4 text-blue-400" /> Oda No: {odaNo}
                  </div>
                  <span className="text-[11px] bg-slate-800 px-2.5 py-0.5 rounded-full text-slate-300">
                    {odaOgrencileri.length} Öğrenci
                  </span>
                </div>

                <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {odaOgrencileri.map((student) => {
                    const anneKey = `${student.id}-Anne`;
                    const babaKey = `${student.id}-Baba`;

                    return (
                      <div
                        key={student.id}
                        className="border border-slate-200 rounded-xl p-4 space-y-3 bg-white shadow-xs"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-bold text-slate-900 text-sm">{student.name}</h3>
                            <p className="text-[11px] text-slate-500 mt-0.5">
                              Oda: {student.oda} | Yatak: {student.yatak} | T.C.: {student.tc}
                            </p>
                          </div>

                          <span
                            className={`text-[11px] font-bold px-2.5 py-0.5 rounded-md ${
                              student.status === 'izinli'
                                ? 'bg-amber-100 text-amber-800'
                                : student.status === 'yok'
                                ? 'bg-rose-100 text-rose-700'
                                : 'bg-emerald-100 text-emerald-700'
                            }`}
                          >
                            {student.status === 'izinli' ? 'İzinli' : student.status === 'yok' ? 'Yok' : 'Var'}
                          </span>
                        </div>

                        {student.status === 'izinli' ? (
                          <div className="p-2.5 bg-amber-50 border border-amber-200 rounded-lg text-[11px] text-amber-900 font-medium">
                            <strong>Otomatik İzinli:</strong> {student.izinAciklama}
                          </div>
                        ) : (
                          <>
                            <div className="flex items-center gap-2 pt-1">
                              <button
                                onClick={() => handleStatusChange(student.id, 'var')}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                                  student.status === 'var'
                                    ? 'bg-emerald-600 text-white shadow-xs'
                                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                                }`}
                              >
                                Var
                              </button>
                              <button
                                onClick={() => handleStatusChange(student.id, 'yok')}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                                  student.status === 'yok'
                                    ? 'bg-red-600 text-white shadow-xs'
                                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                                }`}
                              >
                                Yok
                              </button>
                            </div>

                            {student.status === 'yok' && (
                              <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-xl space-y-2.5 mt-2">
                                <div className="text-[11px] font-bold text-rose-800">
                                  WhatsApp Yoklama Bildirimi Gönder:
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                                  <div className="flex items-center bg-white border border-rose-200 rounded-lg px-2 py-1">
                                    <Phone className="w-3 h-3 text-slate-400 mr-1" />
                                    <span className="text-slate-500 mr-1">Anne:</span>
                                    <input
                                      type="text"
                                      value={student.anneTel}
                                      onChange={(e) => handlePhoneChange(student.id, 'anneTel', e.target.value)}
                                      className="w-full font-mono text-slate-800 focus:outline-none"
                                    />
                                  </div>
                                  <div className="flex items-center bg-white border border-rose-200 rounded-lg px-2 py-1">
                                    <Phone className="w-3 h-3 text-slate-400 mr-1" />
                                    <span className="text-slate-500 mr-1">Baba:</span>
                                    <input
                                      type="text"
                                      value={student.babaTel}
                                      onChange={(e) => handlePhoneChange(student.id, 'babaTel', e.target.value)}
                                      className="w-full font-mono text-slate-800 focus:outline-none"
                                    />
                                  </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                  <button
                                    type="button"
                                    disabled={sendingKey === anneKey}
                                    onClick={() => handleSendWhatsApp(student, 'Anne', student.anneTel)}
                                    className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white py-2 px-3 rounded-lg text-[11px] font-bold transition-all cursor-pointer shadow-xs"
                                  >
                                    {sendingKey === anneKey ? (
                                      <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Gönderiliyor...</>
                                    ) : sentKeys[anneKey] ? (
                                      <><Check className="w-3.5 h-3.5" /> Anneye Gönderildi</>
                                    ) : (
                                      <><Send className="w-3.5 h-3.5" /> Anneye Mesaj At ({student.anneTel})</>
                                    )}
                                  </button>

                                  <button
                                    type="button"
                                    disabled={sendingKey === babaKey}
                                    onClick={() => handleSendWhatsApp(student, 'Baba', student.babaTel)}
                                    className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white py-2 px-3 rounded-lg text-[11px] font-bold transition-all cursor-pointer shadow-xs"
                                  >
                                    {sendingKey === babaKey ? (
                                      <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Gönderiliyor...</>
                                    ) : sentKeys[babaKey] ? (
                                      <><Check className="w-3.5 h-3.5" /> Babaya Gönderildi</>
                                    ) : (
                                      <><Send className="w-3.5 h-3.5" /> Babaya Mesaj At ({student.babaTel})</>
                                    )}
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

      </div>
    </div>
  );
}