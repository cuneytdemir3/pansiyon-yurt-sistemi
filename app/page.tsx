"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

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
  const router = useRouter();
  const [roleTab, setRoleTab] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');

  // Veli Giriş Durumları
  const [phone, setPhone] = useState('');
  const [otpInput, setOtpInput] = useState('');
  const [generatedOtp, setGeneratedOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp' | 'portal'>('phone');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [infoMsg, setInfoMsg] = useState('');

  // Sadece Veliye Ait Öğrenciler ve İzinler
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
        if (list.length === 0) {
          sessionStorage.removeItem('pansiyon_veli_tel');
          setStep('phone');
          setErrorMsg('Adınıza kayıtlı öğrenci gözükmemektedir');
          return;
        }
        setMyStudents(list);
        setMyLeaves(data.store.leaves || []);
        if (!selectedStudentId) {
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
    setErrorMsg('');
    setInfoMsg('');
    setLoading(true);

    try {
      // 1) Önce veritabanında bu numaraya kayıtlı öğrenci var mı kontrol et
      const verifyRes = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'verify_parent_phone', phone })
      });
      const verifyData = await verifyRes.json();

      // Öğrenci yoksa ŞİFRE ÜRETME ve direkt hata mesajını göster!
      if (!verifyRes.ok || !verifyData.success) {
        setErrorMsg(verifyData.message || 'Adınıza kayıtlı öğrenci gözükmemektedir');
        setLoading(false);
        return;
      }

      // 2) Öğrenci varsa 6 haneli gizli şifre üret (EKRANDA ASLA GÖSTERİLMEZ!)
      const secretCode = Math.floor(100000 + Math.random() * 900000).toString();
      setGeneratedOtp(secretCode);

      const childNames = (verifyData.students || []).map((s: any) => s.name).join(', ');
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${childNames}),\nVeli Portalı Giriş Şifreniz: *${secretCode}*\n\n_Güvenliğiniz için bu kodu kimseyle paylaşmayınız._`;

      let sentSuccess = false;

      // Önce aktif Cloudflare tünelinden WhatsApp botuna gönder
      if (verifyData.tunnelUrl) {
        try {
          const wpRes = await fetch(`${verifyData.tunnelUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code: secretCode, customMessage })
          });
          if (wpRes.ok) sentSuccess = true;
        } catch {}
      }

      // Yerel bilgisayar üzerinden test ediliyorsa localhost:3001 dene
      if (!sentSuccess) {
        try {
          const localRes = await fetch('http://127.0.0.1:3001/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code: secretCode, customMessage })
          });
          if (localRes.ok) sentSuccess = true;
        } catch {}
      }

      if (!sentSuccess) {
        setErrorMsg('WhatsApp bildirim sunucusuna şu an ulaşılamıyor. Lütfen nöbetçi belletmen veya okul idaresi ile iletişime geçiniz.');
        setLoading(false);
        return;
      }

      setStep('otp');
      // Ekranda şifre KESİNLİKLE yazmaz, sadece WhatsApp'a gönderildiği bilgisi verilir
      setInfoMsg('Tek kullanımlık 6 haneli giriş şifreniz cep telefonunuzdaki WhatsApp uygulamasına gönderilmiştir.');
    } catch {
      setErrorMsg('Sunucu bağlantı hatası oluştu.');
    }
    setLoading(false);
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    if (!generatedOtp || otpInput.trim() !== generatedOtp) {
      setErrorMsg('Girdiğiniz doğrulama kodu hatalı! Lütfen WhatsApp mesajınızı kontrol ediniz.');
      return;
    }
    sessionStorage.setItem('pansiyon_veli_tel', phone);
    await loadParentData(phone);
    setStep('portal');
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
    setGeneratedOtp('');
    setInfoMsg('');
    setErrorMsg('');
  };

  const activeStudent = myStudents.find((s) => s.id === selectedStudentId) || myStudents[0];
  const activeStudentLeaves = myLeaves.filter((l) => activeStudent && l.studentId === activeStudent.id);

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex flex-col justify-between">
      {/* ÜST BAŞLIK ÇUBUĞU */}
      <header className="bg-white border-b border-slate-200 px-6 py-3.5">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center font-extrabold text-blue-700 text-xs">
              SBL
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 text-sm md:text-base">
                  Prof. Dr. Mümtaz Turhan SBL Pansiyon
                </span>
                <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full text-[11px] font-semibold">
                  MEB Uyumlu
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                İzin Takip • Etüt Yoklama • Gece Yat Yoklaması • Oda Yönetimi
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* ANA İÇERİK */}
      <main className="flex-1 flex items-center justify-center p-4 md:p-8">
        {step !== 'portal' ? (
          /* GİRİŞ KARTI (Ekran görüntüsündeki kurumsal tasarım) */
          <div className="bg-white rounded-3xl shadow-xl border border-slate-100 max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden">
            {/* SOL PANEL */}
            <div className="md:col-span-5 bg-gradient-to-b from-[#eef4ff] to-[#e0ebff] p-8 flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-white rounded-2xl shadow-md flex flex-col items-center justify-center mb-5 border border-blue-100">
                <span className="text-xl font-black text-blue-700 leading-none">SBL</span>
                <span className="text-[9px] font-bold text-blue-500 tracking-wider mt-1">PANSİYON</span>
              </div>
              <h2 className="font-extrabold text-slate-800 text-base">
                PROF. DR. MÜMTAZ TURHAN
              </h2>
              <p className="font-bold text-slate-700 text-sm mb-4">
                Sosyal Bilimler Lisesi Pansiyonu
              </p>
              <span className="bg-white/80 text-slate-600 text-xs font-semibold px-4 py-1.5 rounded-full shadow-sm border border-blue-100">
                Pansiyon & Yurt Portalı
              </span>
            </div>

            {/* SAĞ PANEL */}
            <div className="md:col-span-7 p-8 md:p-10 flex flex-col justify-center">
              <div className="text-center mb-6">
                <h1 className="text-2xl font-extrabold text-slate-900">Pansiyon Yönetim Sistemi</h1>
                <p className="text-xs text-slate-500 mt-1">
                  Giriş yapmak için rolünüzü seçip bilgilerinizi giriniz.
                </p>
              </div>

              {/* ROL SEKMELERİ */}
              <div className="grid grid-cols-3 bg-slate-100 p-1.5 rounded-2xl mb-6 text-xs font-bold">
                <button
                  type="button"
                  onClick={() => { setRoleTab('veli'); setErrorMsg(''); }}
                  className={`py-2.5 rounded-xl transition ${
                    roleTab === 'veli' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  👥 Veli
                </button>
                <button
                  type="button"
                  onClick={() => router.push('/belletmen')}
                  className="py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition"
                >
                  👨‍🏫 Belletmen
                </button>
                <button
                  type="button"
                  onClick={() => router.push('/admin')}
                  className="py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition"
                >
                  🛡️ Yönetici
                </button>
              </div>

              {/* HATA MESAJI KUTUSU ("Adınıza kayıtlı öğrenci gözükmemektedir") */}
              {errorMsg && (
                <div className="mb-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold text-center">
                  ⚠️ {errorMsg}
                </div>
              )}

              {/* BİLGİ MESAJI KUTUSU (ŞİFRE İÇERMEZ, SADECE WHATSAPP BİLGİSİ VERİR) */}
              {infoMsg && (
                <div className="mb-4 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold text-center">
                  📲 {infoMsg}
                </div>
              )}

              {step === 'phone' ? (
                <form onSubmit={handleSendOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">
                      Kayıtlı Veli Cep Telefonu Numaranız
                    </label>
                    <input
                      type="tel"
                      required
                      placeholder="05XX XXX XX XX"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold tracking-wider focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition"
                  >
                    {loading ? 'Öğrenci Kaydı Kontrol Ediliyor...' : '📲 WhatsApp İle Giriş Kodu Gönder'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <p className="text-[11px] text-slate-500 text-center">
                    Şifresiz Güvenli Giriş: WhatsApp mesajınıza gelen 6 haneli kodu giriniz
                  </p>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5 text-center">
                      Gelen 6 Haneli Kodu Giriniz
                    </label>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      placeholder="••••••"
                      value={otpInput}
                      onChange={(e) => setOtpInput(e.target.value)}
                      className="w-full p-3.5 border border-emerald-400 rounded-xl text-center text-2xl font-extrabold tracking-widest focus:outline-none focus:ring-2 focus:ring-emerald-600"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition"
                  >
                    ✅ Doğrula ve Portala Gir
                  </button>
                  <button
                    type="button"
                    onClick={() => { setStep('phone'); setInfoMsg(''); setErrorMsg(''); setOtpInput(''); }}
                    className="w-full text-xs text-slate-500 hover:text-slate-800 underline py-1"
                  >
                    Telefon numarasını değiştir
                  </button>
                </form>
              )}

              <div className="mt-8 pt-4 border-t border-slate-100 text-center text-[11px] text-slate-400">
                © 2026 Prof. Dr. Mümtaz Turhan SBL
              </div>
            </div>
          </div>
        ) : (
          /* VELİ ÖZEL PORTALI (SADECE KENDİ ÖĞRENCİSİ GÖRÜNÜR) */
          <div className="max-w-5xl w-full space-y-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex flex-wrap justify-between items-center gap-4">
              <div>
                <span className="text-xs font-bold uppercase text-emerald-600">
                  ✅ Doğrulanmış Veli Oturumu ({phone})
                </span>
                <h2 className="text-xl font-extrabold text-slate-900">
                  Öğrenci Bilgileri, İstatistikler ve İzin Paneli
                </h2>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => loadParentData(phone)}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold transition"
                >
                  🔄 Yenile
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-xl text-xs font-bold transition"
                >
                  Çıkış Yap
                </button>
              </div>
            </div>

            {myStudents.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-1">
                {myStudents.map((st) => (
                  <button
                    key={st.id}
                    onClick={() => setSelectedStudentId(st.id)}
                    className={`px-4 py-2 rounded-xl font-bold text-xs transition ${
                      activeStudent?.id === st.id
                        ? 'bg-blue-600 text-white shadow'
                        : 'bg-white border text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    👤 {st.name} (Oda {st.oda})
                  </button>
                ))}
              </div>
            )}

            {activeStudent && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* ÖĞRENCİ BİLGİ VE İSTATİSTİK KARTI */}
                <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-4">
                  <div className="flex items-center justify-between border-b pb-3">
                    <div>
                      <span className="text-[11px] font-bold uppercase text-blue-600">Öğrenciniz</span>
                      <h3 className="text-xl font-extrabold text-slate-900">{activeStudent.name}</h3>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold ${
                        activeStudent.status === 'var'
                          ? 'bg-emerald-100 text-emerald-800'
                          : activeStudent.status === 'izinli'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {activeStudent.status === 'var'
                        ? '🟢 Yurtta (Var)'
                        : activeStudent.status === 'izinli'
                        ? '🟡 İzinli'
                        : '🔴 Yoklamada Yok'}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-slate-400 block">Pansiyon Bloğu</span>
                      <strong className="text-slate-800">
                        {activeStudent.cinsiyet === 'kiz' ? 'Kız Pansiyonu' : 'Erkek Pansiyonu'}
                      </strong>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-slate-400 block">Kat / Oda</span>
                      <strong className="text-slate-800">
                        {activeStudent.kat}. Kat - Oda {activeStudent.oda}
                      </strong>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-xl border border-blue-100 col-span-2">
                      <span className="text-blue-600 block">Toplam Kullanılan İzin Sayısı</span>
                      <strong className="text-base font-extrabold text-blue-900">
                        {activeStudentLeaves.length} İzin Kaydı
                      </strong>
                    </div>
                  </div>
                </div>

                {/* SADECE KENDİ ÖĞRENCİSİNE İZİN ALMA FORMU */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
                    <h3 className="text-base font-extrabold text-slate-900 mb-1">
                      📝 {activeStudent.name} İçin İzin Talebi Gönder
                    </h3>
                    <p className="text-xs text-slate-500 mb-4">
                      Bu ekrandan yalnızca kendi öğrenciniz için izin talebi oluşturabilirsiniz.
                    </p>
                    <form onSubmit={handleCreateLeave} className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">Öğrenci</label>
                        <input
                          type="text"
                          disabled
                          value={`${activeStudent.name} (Oda ${activeStudent.oda})`}
                          className="w-full p-2.5 bg-slate-100 border rounded-xl font-bold text-slate-700"
                        />
                      </div>
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">İzin Türü</label>
                        <select
                          value={leaveType}
                          onChange={(e) => setLeaveType(e.target.value)}
                          className="w-full p-2.5 border rounded-xl font-semibold"
                        >
                          <option value="Hafta Sonu Evci İzni">Hafta Sonu Evci İzni</option>
                          <option value="Aile Yanı Ev İzni">Aile Yanı Ev İzni</option>
                          <option value="Sağlık / Hastane İzni">Sağlık / Hastane İzni</option>
                          <option value="Çarşı / Kurs İzni">Çarşı / Kurs İzni</option>
                        </select>
                      </div>
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">Başlangıç Tarihi</label>
                        <input
                          type="date"
                          required
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="w-full p-2.5 border rounded-xl"
                        />
                      </div>
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">Dönüş Tarihi</label>
                        <input
                          type="date"
                          required
                          value={endDate}
                          onChange={(e) => setEndDate(e.target.value)}
                          className="w-full p-2.5 border rounded-xl"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="font-bold text-slate-600 block mb-1">Açıklama / Adres</label>
                        <input
                          type="text"
                          required
                          placeholder="İzin süresince bulunacağı adres veya açıklama..."
                          value={leaveNote}
                          onChange={(e) => setLeaveNote(e.target.value)}
                          className="w-full p-2.5 border rounded-xl"
                        />
                      </div>
                      <div className="md:col-span-2 flex justify-end">
                        <button
                          type="submit"
                          disabled={loading}
                          className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-xl font-bold shadow transition"
                        >
                          {loading ? 'Kaydediliyor...' : '✅ İzin Talebini Onayla'}
                        </button>
                      </div>
                    </form>
                  </div>

                  {/* GEÇMİŞ İZİNLER */}
                  <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
                    <h3 className="text-base font-extrabold text-slate-900 mb-3">
                      📅 {activeStudent.name} - Geçmiş İzinleri ({activeStudentLeaves.length})
                    </h3>
                    {activeStudentLeaves.length === 0 ? (
                      <p className="text-xs text-slate-400 italic">Henüz izin kaydı bulunmamaktadır.</p>
                    ) : (
                      <div className="space-y-2 text-xs">
                        {activeStudentLeaves.map((lv) => (
                          <div key={lv.id} className="p-3 border rounded-xl bg-slate-50 flex justify-between items-center">
                            <div>
                              <span className="font-bold text-blue-700">{lv.tip}</span>
                              <p className="text-slate-600 mt-0.5">{lv.aciklama}</p>
                            </div>
                            <div className="text-right font-semibold text-slate-500">
                              {lv.baslangic} → {lv.bitis}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* ALT BİLGİ */}
      <footer className="border-t border-slate-200 bg-white px-6 py-3 text-[11px] text-slate-400">
        <div className="max-w-6xl mx-auto flex justify-between">
          <span>© 2026 Pansiyon ve Yurt Takip Sistemi • MEB Standartlarına Uygun</span>
          <span>Güvenli Veritabanı • Rol Tabanlı Doğrulama</span>
        </div>
      </footer>
    </div>
  );
}