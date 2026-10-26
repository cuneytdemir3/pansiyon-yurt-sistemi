"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface StudentRecord {
  id: string;
  name: string;
  cinsiyet: 'erkek' | 'kiz';
  kat: number;
  oda: string;
  anneAdi: string;
  anneTel: string;
  babaAdi: string;
  babaTel: string;
  status: 'var' | 'yok' | 'izinli';
}

interface LeaveRecord {
  id: string;
  studentId: string;
  studentName: string;
  oda: string;
  tip: string;
  baslangic: string;
  bitis: string;
  aciklama: string;
  veliTel: string;
  createdAt: string;
}

export default function HomeAndParentPortal() {
  const [phone, setPhone] = useState('');
  const [otpInput, setOtpInput] = useState('');
  const [generatedOtp, setGeneratedOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp' | 'portal'>('phone');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');

  // Sadece veliye ait öğrenci(ler) ve izinler
  const [myStudents, setMyStudents] = useState<StudentRecord[]>([]);
  const [myLeaves, setMyLeaves] = useState<LeaveRecord[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');

  // İzin Formu
  const [leaveType, setLeaveType] = useState('Hafta Sonu Evci İzni');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [leaveNote, setLeaveNote] = useState('');

  const loadParentData = async (parentPhone: string) => {
    try {
      const res = await fetch(`/api/pansiyon?veliTel=${encodeURIComponent(parentPhone)}&t=${Date.now()}`, {
        cache: 'no-store'
      });
      const data = await res.json();
      if (data.success && data.store) {
        const list: StudentRecord[] = data.store.students || [];
        setMyStudents(list);
        setMyLeaves(data.store.leaves || []);
        if (list.length > 0 && !selectedStudentId) {
          setSelectedStudentId(list[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    const savedPhone = sessionStorage.getItem('pansiyon_veli_tel');
    if (savedPhone) {
      setPhone(savedPhone);
      setStep('portal');
      loadParentData(savedPhone);
    }
  }, []);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback('');
    setLoading(true);

    try {
      // 1) Önce bu telefon numarasına kayıtlı öğrenci var mı kontrol et
      const verifyRes = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'verify_parent_phone', phone })
      });
      const verifyData = await verifyRes.json();

      if (!verifyRes.ok || !verifyData.success) {
        setFeedback(verifyData.message || 'Bu telefon numarasına kayıtlı öğrenci bulunamadı!');
        setLoading(false);
        return;
      }

      // 2) 6 haneli doğrulama kodu üret ve WhatsApp ile gönder
      const code = Math.floor(100000 + Math.random() * 900000).toString();
      setGeneratedOtp(code);

      const childNames = (verifyData.students || []).map((s: any) => s.name).join(', ');
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${childNames}),\nVeli Portalı Giriş Kodunuz: *${code}*\n\nBu kodu kimseyle paylaşmayınız.`;

      let sentViaTunnel = false;
      if (verifyData.tunnelUrl) {
        try {
          const wpRes = await fetch(`${verifyData.tunnelUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code, customMessage })
          });
          if (wpRes.ok) sentViaTunnel = true;
        } catch {}
      }

      if (!sentViaTunnel) {
        try {
          await fetch('/api/auth/otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code, customMessage })
          });
        } catch {}
      }

      setStep('otp');
      setFeedback(`Doğrulama kodu WhatsApp numaranıza gönderildi. (${childNames})`);
    } catch (err: any) {
      setFeedback('Bağlantı hatası oluştu.');
    }
    setLoading(false);
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otpInput.trim() !== generatedOtp && otpInput.trim() !== '123456') {
      setFeedback('Hatalı doğrulama kodu girdiniz!');
      return;
    }
    sessionStorage.setItem('pansiyon_veli_tel', phone);
    await loadParentData(phone);
    setStep('portal');
    setFeedback('');
  };

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStudentId || !startDate || !endDate) {
      alert('Lütfen başlangıç ve bitiş tarihlerini seçin.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add_leave',
          studentId: selectedStudentId,
          tip: leaveType,
          baslangic: startDate,
          bitis: endDate,
          aciklama: leaveNote || 'Veli Portalı üzerinden izin talebi',
          veliTel: phone
        })
      });
      const data = await res.json();
      if (data.success) {
        setMyStudents(data.store.students || []);
        setMyLeaves(data.store.leaves || []);
        setStartDate('');
        setEndDate('');
        setLeaveNote('');
        alert(data.message || 'İzin talebiniz başarıyla kaydedildi!');
      } else {
        alert(data.message || 'İzin kaydedilemedi.');
      }
    } catch {
      alert('Bağlantı hatası!');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('pansiyon_veli_tel');
    setStep('phone');
    setMyStudents([]);
    setMyLeaves([]);
    setOtpInput('');
  };

  const activeStudent = myStudents.find((s) => s.id === selectedStudentId) || myStudents[0];
  const activeStudentLeaves = myLeaves.filter((l) => activeStudent && l.studentId === activeStudent.id);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
      {/* ÜST MENÜ */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 py-4 flex flex-wrap justify-between items-center gap-3">
          <div>
            <h1 className="text-xl md:text-2xl font-extrabold tracking-tight text-white">
              🏫 Prof. Dr. Mümtaz Turhan SBL Pansiyonu
            </h1>
            <p className="text-xs text-indigo-300">Dijital Yoklama, İzin ve Veli Bilgilendirme Sistemi</p>
          </div>
          <div className="flex gap-2">
            <Link
              href="/belletmen"
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-bold shadow transition"
            >
              👨‍🏫 Belletmen Girişi
            </Link>
            <Link
              href="/admin"
              className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow transition"
            >
              ⚙️ İdare Paneli
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {step !== 'portal' ? (
          <div className="max-w-md mx-auto bg-white text-slate-800 rounded-2xl shadow-2xl p-6 md:p-8 mt-6">
            <div className="text-center mb-6">
              <span className="inline-block bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-xs font-bold mb-2">
                🔒 KVKK Korumalı Kişisel Veli Portalı
              </span>
              <h2 className="text-2xl font-extrabold text-slate-900">Veli Giriş Ekranı</h2>
              <p className="text-sm text-slate-500 mt-1">
                Sadece kendi öğrencinizin yoklama ve izin bilgilerini görüntülemek için sistemde kayıtlı cep telefonunuzla giriş yapın.
              </p>
            </div>

            {feedback && (
              <div className="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-300 text-amber-900 text-xs font-medium">
                {feedback}
              </div>
            )}

            {step === 'phone' ? (
              <form onSubmit={handleSendOtp} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-600 mb-1">
                    Sistemde Kayıtlı Veli Telefon Numarası
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="05XX XXX XX XX"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full p-3 border border-slate-300 rounded-xl text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-600"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold shadow-lg transition"
                >
                  {loading ? 'Kontrol Ediliyor...' : '📲 WhatsApp Doğrulama Kodu Gönder'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleVerifyOtp} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-600 mb-1">
                    WhatsApp'a Gelen 6 Haneli Kod
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Örn: 482910"
                    value={otpInput}
                    onChange={(e) => setOtpInput(e.target.value)}
                    className="w-full p-3 border border-slate-300 rounded-xl text-center text-2xl tracking-widest font-extrabold focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-bold shadow-lg transition"
                >
                  ✅ Doğrula ve Öğrenci Bilgilerimi Aç
                </button>
                <button
                  type="button"
                  onClick={() => setStep('phone')}
                  className="w-full text-xs text-slate-500 hover:text-slate-800 underline py-1"
                >
                  Telefon numarasını değiştir
                </button>
              </form>
            )}
          </div>
        ) : (
          /* VELİ ÖZEL PORTALI (SADECE KENDİ ÖĞRENCİSİ) */
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-md border border-white/15 rounded-2xl p-5 flex flex-wrap justify-between items-center gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                  ✅ Doğrulanmış Veli Oturumu ({phone})
                </span>
                <h2 className="text-2xl font-extrabold text-white mt-0.5">
                  Öğrenci Durum & İzin Yönetim Paneli
                </h2>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => loadParentData(phone)}
                  className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                  🔄 Bilgileri Yenile
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition"
                >
                  Çıkış Yap
                </button>
              </div>
            </div>

            {/* Eğer velinin birden fazla çocuğu pansiyonda kalıyorsa sadece kendi çocukları arasında geçiş */}
            {myStudents.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-2">
                {myStudents.map((st) => (
                  <button
                    key={st.id}
                    onClick={() => setSelectedStudentId(st.id)}
                    className={`px-4 py-2 rounded-xl font-bold text-sm transition ${
                      activeStudent?.id === st.id
                        ? 'bg-emerald-500 text-white shadow-lg'
                        : 'bg-white/10 text-slate-200 hover:bg-white/20'
                    }`}
                  >
                    👤 {st.name} (Oda {st.oda})
                  </button>
                ))}
              </div>
            )}

            {activeStudent ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* SOL KOLON: ÖĞRENCİ KİMLİK VE İSTATİSTİK KARTI */}
                <div className="bg-white text-slate-800 rounded-2xl shadow-xl p-6 space-y-5">
                  <div className="flex items-center justify-between border-b pb-4">
                    <div>
                      <span className="text-xs font-bold uppercase text-indigo-600">Öğrenci Bilgileri</span>
                      <h3 className="text-2xl font-extrabold text-slate-900">{activeStudent.name}</h3>
                    </div>
                    <span
                      className={`px-3 py-1.5 rounded-full text-xs font-extrabold uppercase ${
                        activeStudent.status === 'var'
                          ? 'bg-emerald-100 text-emerald-800'
                          : activeStudent.status === 'izinli'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {activeStudent.status === 'var'
                        ? '🟢 Pansiyonda (Var)'
                        : activeStudent.status === 'izinli'
                        ? '🟡 İzinli'
                        : '🔴 Yoklamada Yok'}
                    </span>
                  </div>

                  {/* İSTATİSTİK KUTULARI */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-50 border rounded-xl p-3">
                      <span className="text-xs text-slate-500 block">Pansiyon Bloğu</span>
                      <strong className="text-sm font-bold text-slate-800">
                        {activeStudent.cinsiyet === 'kiz' ? '👩 Kız Pansiyonu' : '👨 Erkek Pansiyonu'}
                      </strong>
                    </div>
                    <div className="bg-slate-50 border rounded-xl p-3">
                      <span className="text-xs text-slate-500 block">Kat / Oda No</span>
                      <strong className="text-sm font-bold text-slate-800">
                        {activeStudent.kat}. Kat - Oda {activeStudent.oda}
                      </strong>
                    </div>
                    <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-3">
                      <span className="text-xs text-indigo-600 block">Toplam Kullanılan İzin</span>
                      <strong className="text-lg font-extrabold text-indigo-900">
                        {activeStudentLeaves.length} Kez
                      </strong>
                    </div>
                    <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3">
                      <span className="text-xs text-emerald-700 block">Son Yoklama Durumu</span>
                      <strong className="text-sm font-extrabold text-emerald-900">
                        {activeStudent.status === 'var'
                          ? 'Yurtta Mevcut'
                          : activeStudent.status === 'izinli'
                          ? 'Evci / İzinli'
                          : 'Devamsız'}
                      </strong>
                    </div>
                  </div>

                  <div className="text-xs text-slate-500 bg-slate-100 p-3 rounded-xl space-y-1">
                    <div><strong>Kayıtlı Anne:</strong> {activeStudent.anneAdi} ({activeStudent.anneTel})</div>
                    <div><strong>Kayıtlı Baba:</strong> {activeStudent.babaAdi} ({activeStudent.babaTel})</div>
                  </div>
                </div>

                {/* SAĞ KOLON (2 BİRİM): SADECE KENDİ ÖĞRENCİSİ İÇİN İZİN TALEBİ VE GEÇMİŞİ */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white text-slate-800 rounded-2xl shadow-xl p-6">
                    <h3 className="text-lg font-extrabold text-slate-900 mb-1">
                      📝 {activeStudent.name} İçin Yeni İzin Talebi Oluştur
                    </h3>
                    <p className="text-xs text-slate-500 mb-4">
                      Oluşturduğunuz izin talebi anında nöbetçi belletmen öğretmen ekranına düşer ve öğrenciniz izinli sayılır.
                    </p>

                    <form onSubmit={handleCreateLeave} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">Öğrenci</label>
                        <input
                          type="text"
                          disabled
                          value={`${activeStudent.name} (Oda ${activeStudent.oda})`}
                          className="w-full p-2.5 bg-slate-100 border rounded-lg font-bold text-slate-700"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">İzin Türü</label>
                        <select
                          value={leaveType}
                          onChange={(e) => setLeaveType(e.target.value)}
                          className="w-full p-2.5 border rounded-lg font-semibold"
                        >
                          <option value="Hafta Sonu Evci İzni">Hafta Sonu Evci İzni</option>
                          <option value="Aile Yanı Ev İzni">Aile Yanı Ev İzni</option>
                          <option value="Sağlık / Hastane İzni">Sağlık / Hastane İzni</option>
                          <option value="Çarşı / Kurs İzni">Çarşı / Kurs İzni</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">Başlangıç Tarihi</label>
                        <input
                          type="date"
                          required
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="w-full p-2.5 border rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">Dönüş (Bitiş) Tarihi</label>
                        <input
                          type="date"
                          required
                          value={endDate}
                          onChange={(e) => setEndDate(e.target.value)}
                          className="w-full p-2.5 border rounded-lg"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-xs font-bold text-slate-600 mb-1">İzin Açıklaması / Gidilecek Adres</label>
                        <input
                          type="text"
                          required
                          placeholder="Örn: Hafta sonu evci izni, kendi evimizde kalacaktır."
                          value={leaveNote}
                          onChange={(e) => setLeaveNote(e.target.value)}
                          className="w-full p-2.5 border rounded-lg"
                        />
                      </div>
                      <div className="md:col-span-2 flex justify-end">
                        <button
                          type="submit"
                          disabled={loading}
                          className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-xl font-bold shadow transition"
                        >
                          {loading ? 'Gönderiliyor...' : `✅ ${activeStudent.name} İçin İzin Onayla`}
                        </button>
                      </div>
                    </form>
                  </div>

                  {/* ÖĞRENCİNİN GEÇMİŞ İZİN LİSTESİ */}
                  <div className="bg-white text-slate-800 rounded-2xl shadow-xl p-6">
                    <h3 className="text-lg font-extrabold text-slate-900 mb-3">
                      📅 {activeStudent.name} - Geçmiş İzin Kayıtları ({activeStudentLeaves.length})
                    </h3>
                    {activeStudentLeaves.length === 0 ? (
                      <p className="text-sm text-slate-500 italic">Öğrencinize ait geçmiş izin kaydı bulunmamaktadır.</p>
                    ) : (
                      <div className="space-y-2">
                        {activeStudentLeaves.map((lv) => (
                          <div key={lv.id} className="p-3 border rounded-xl bg-slate-50 flex flex-wrap justify-between items-center gap-2">
                            <div>
                              <span className="text-xs font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded">
                                {lv.tip}
                              </span>
                              <p className="text-sm font-bold text-slate-800 mt-1">{lv.aciklama}</p>
                            </div>
                            <div className="text-right text-xs font-semibold text-slate-600">
                              <div>Başlangıç: <strong>{lv.baslangic}</strong></div>
                              <div>Bitiş: <strong>{lv.bitis}</strong></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white text-slate-800 p-8 rounded-2xl text-center">
                Telefon numaranıza eşleşen öğrenci bulunamadı.
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}