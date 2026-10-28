"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import SblLogo from './components/SblLogo';

interface StudentRecord { id: string; name: string; cinsiyet: 'erkek' | 'kiz'; kat: number; oda: string; anneAdi: string; anneTel: string; babaAdi: string; babaTel: string; status: 'var' | 'yok' | 'izinli'; }
interface LeaveRecord { id: string; studentId: string; studentName: string; oda: string; tip: string; baslangic: string; bitis: string; aciklama: string; veliTel: string; createdAt: string; }
interface AttendanceHistoryRecord { id: string; studentId: string; studentName: string; oda: string; tarih: string; saat: string; seans: string; status: 'var' | 'yok' | 'izinli'; belletmenName: string; }

export default function UnifiedHomePortal() {
  // 1. BÜTÜN HOOKLAR (STATE VE ROUTER) EN ÜSTTE
  const [mounted, setMounted] = React.useState(false);
  const router = useRouter();
  
  const [roleTab, setRoleTab] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');
  const [phone, setPhone] = useState('');
  const [otpInput, setOtpInput] = useState('');
  const [generatedOtp, setGeneratedOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp' | 'portal'>('phone');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [infoMsg, setInfoMsg] = useState('');
  const [belletmenList, setBelletmenList] = useState<any[]>([]);
  const [selectedBelId, setSelectedBelId] = useState('');
  const [belPassword, setBelPassword] = useState('');
  const [adminPassword, setAdminPassword] = useState('');

  // Veliye özel veriler
  const [myStudents, setMyStudents] = useState<StudentRecord[]>([]);
  const [myLeaves, setMyLeaves] = useState<LeaveRecord[]>([]);
  const [myHistory, setMyHistory] = useState<AttendanceHistoryRecord[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [historyFilter, setHistoryFilter] = useState<'all' | 'etut' | 'yat'>('all');

  // İzin Formu
  const [leaveType, setLeaveType] = useState('Hafta Sonu Evci İzni');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [leaveNote, setLeaveNote] = useState('');

  // 2. BÜTÜN USE-EFFECT'LER KESİNTİSİZ OLARAK BURADA
  React.useEffect(() => { setMounted(true); }, []);

  useEffect(() => {
    fetch('/api/pansiyon?mode=init&t=' + Date.now(), { cache: 'no-store' }).then((r) => r.json()).then((d) => {
      if (d.success && d.store?.belletmenler) {
        setBelletmenList(d.store.belletmenler);
        if (d.store.belletmenler.length > 0) setSelectedBelId(d.store.belletmenler[0].id);
      }
    }).catch(() => {});
    const savedPhone = sessionStorage.getItem('pansiyon_veli_tel');
    if (savedPhone) { setPhone(savedPhone); setStep('portal'); loadParentData(savedPhone); }
  }, []);

  // 3. FONKSİYONLAR
  const loadParentData = async (parentPhone: string) => {
    try {
      const res = await fetch(`/api/pansiyon?veliTel=${encodeURIComponent(parentPhone)}&t=${Date.now()}`, { cache: 'no-store' });
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
        setMyHistory(data.store.attendanceHistory || []);
        if (!selectedStudentId) setSelectedStudentId(list[0].id);
      }
    } catch (e) {}
  };

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault(); setErrorMsg(''); setInfoMsg(''); setLoading(true);
    try {
      const verifyRes = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'verify_parent_phone', phone }) });
      const verifyData = await verifyRes.json();
      if (!verifyRes.ok || !verifyData.success) { setErrorMsg(verifyData.message || 'Adınıza kayıtlı öğrenci gözükmemektedir'); setLoading(false); return; }
      const secretCode = Math.floor(100000 + Math.random() * 900000).toString();
      setGeneratedOtp(secretCode);
      const childNames = (verifyData.students || []).map((s: any) => s.name).join(', ');
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${childNames}),\nVeli Portalı Giriş Şifreniz: *${secretCode}*\n\n_Güvenliğiniz için bu kodu kimseyle paylaşmayınız._`;
      let sentSuccess = false;
      if (verifyData.tunnelUrl) { try { const wpRes = await fetch(`${verifyData.tunnelUrl}/send-otp`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, code: secretCode, customMessage }) }); if (wpRes.ok) sentSuccess = true; } catch {} }
      if (!sentSuccess) { try { const localRes = await fetch('http://127.0.0.1:3001/send-otp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, code: secretCode, customMessage }) }); if (localRes.ok) sentSuccess = true; } catch {} }
      if (!sentSuccess) { setErrorMsg('WhatsApp bildirim sunucusuna şu an ulaşılamıyor. Lütfen okul idaresi ile iletişime geçiniz.'); setLoading(false); return; }
      setStep('otp'); setInfoMsg('6 haneli giriş şifreniz cep telefonunuzdaki WhatsApp uygulamasına gönderilmiştir.');
    } catch { setErrorMsg('Sunucu bağlantı hatası oluştu.'); }
    setLoading(false);
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault(); setErrorMsg('');
    if (!generatedOtp || otpInput.trim() !== generatedOtp) { setErrorMsg('Girdiğiniz doğrulama kodu hatalı! Lütfen WhatsApp mesajınızı kontrol ediniz.'); return; }
    sessionStorage.setItem('pansiyon_veli_tel', phone); await loadParentData(phone); setStep('portal');
  };

  const handleBelletmenLogin = async (e: React.FormEvent) => {
    e.preventDefault(); setErrorMsg(''); setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'belletmen_login', id: selectedBelId, password: belPassword }) });
      const data = await res.json();
      if (data.success) { sessionStorage.setItem('pansiyon_belletmen_session', JSON.stringify({ belletmen: data.belletmen, allowedGender: data.allowedGender })); router.push('/belletmen'); }
      else { setErrorMsg(data.message || 'Hatalı belletmen şifresi!'); }
    } catch { setErrorMsg('Giriş yapılırken hata oluştu.'); }
    setLoading(false);
  };

  const handleAdminQuickLogin = async (e: React.FormEvent) => {
    e.preventDefault(); setErrorMsg(''); setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'admin_login', username: 'admin', password: adminPassword }) });
      const data = await res.json();
      if (data.success) { sessionStorage.setItem('pansiyon_admin_logged', 'true'); router.push('/admin'); }
      else { setErrorMsg(data.message || 'Hatalı yönetici şifresi!'); }
    } catch { setErrorMsg('Bağlantı hatası!'); }
    setLoading(false);
  };

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStudentId || !startDate || !endDate) { alert('Lütfen başlangıç ve bitiş tarihlerini seçin.'); return; }
    setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'add_leave', studentId: selectedStudentId, tip: leaveType, baslangic: startDate, bitis: endDate, aciklama: leaveNote || 'Veli Portalı üzerinden izin talebi', veliTel: phone }) });
      const data = await res.json();
      if (data.success) {
        setMyStudents(data.store.students || []);
        setMyLeaves(data.store.leaves || []);
        setMyHistory(data.store.attendanceHistory || []);
        setStartDate(''); setEndDate(''); setLeaveNote('');
        alert(data.message || 'İzin talebiniz başarıyla kaydedildi!');
      } else { alert(data.message || 'İzin kaydedilemedi.'); }
    } catch { alert('Bağlantı hatası!'); }
    setLoading(false);
  };

  const handleLogout = () => { sessionStorage.removeItem('pansiyon_veli_tel'); setStep('phone'); setMyStudents([]); setMyLeaves([]); setMyHistory([]); setOtpInput(''); setGeneratedOtp(''); setInfoMsg(''); setErrorMsg(''); };

  // 4. DEĞİŞKEN HESAPLAMALARI
  const activeStudent = myStudents.find((s) => s.id === selectedStudentId) || myStudents[0];
  const activeStudentLeaves = myLeaves.filter((l) => activeStudent && l.studentId === activeStudent.id);
  const activeStudentHistory = myHistory.filter((h) => activeStudent && h.studentId === activeStudent.id);

  const filteredHistory = activeStudentHistory.filter((h) => {
    if (historyFilter === 'etut') return h.seans.toLowerCase().includes('etüt') || h.seans.toLowerCase().includes('etut');
    if (historyFilter === 'yat') return h.seans.toLowerCase().includes('yat') || h.seans.toLowerCase().includes('gece');
    return true;
  });

  const presentCount = activeStudentHistory.filter((h) => h.status === 'var').length;
  const absentCount = activeStudentHistory.filter((h) => h.status === 'yok').length;

  // 5. ERKEN ÇIKIŞ BURADA OLMALI! Bütün Hook'lar bittikten sonra.
  if (!mounted) return <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center space-y-4"><div className="w-12 h-12 border-4 border-[#006bb6] border-t-transparent rounded-full animate-spin"></div><div className="font-extrabold text-[#006bb6] tracking-widest text-sm animate-pulse">SİSTEM YÜKLENİYOR...</div></div>;

  // 6. ANA SAYFA ÇİZİMİ
  return (
    <div className="min-h-screen bg-slate-100 text-slate-800 flex flex-col justify-between">
      <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-30 px-4 md:px-8 py-3">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-3">
          <SblLogo size="sm" />
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1.5 bg-indigo-50 text-[#006bb6] px-3 py-1 rounded-full text-xs font-bold border border-indigo-100">
              <span className="w-2 h-2 rounded-full bg-[#006bb6] animate-pulse" />
              7/24 Bulut Senkronizasyon
            </span>
            <button onClick={() => router.push('/belletmen')} className="text-xs font-bold text-slate-600 hover:text-[#006bb6] px-3 py-1.5 rounded-lg hover:bg-slate-100 transition">Belletmen Ekranı</button>
            <button onClick={() => router.push('/admin')} className="text-xs font-bold text-slate-600 hover:text-[#006bb6] px-3 py-1.5 rounded-lg hover:bg-slate-100 transition">İdare Paneli</button>
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-4 md:p-8">
        {step !== 'portal' ? (
          <div className="bg-white rounded-3xl shadow-xl border-t-[6px] border-t-[#006bb6] border-slate-200 max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden">
            <div className="md:col-span-5 bg-slate-50 p-8 flex flex-col items-center justify-center text-center relative border-r border-slate-200">
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 mb-5">
                <SblLogo size="xl" showText={false} />
              </div>
              <p className="text-xs font-extrabold tracking-widest text-[#006bb6] uppercase">Prof. Dr. Mümtaz Turhan</p>
              <h2 className="text-xl font-black text-slate-900 tracking-tight mt-0.5">SOSYAL BİLİMLER LİSESİ</h2>
              <p className="text-xs font-semibold text-slate-500 mt-1 mb-5">Pansiyon & Yurt Yönetim Sistemi</p>
            </div>

            <div className="md:col-span-7 p-8 md:p-10 flex flex-col justify-center bg-white">
              <div className="text-center mb-6">
                <h1 className="text-2xl font-extrabold text-slate-900">Sisteme Giriş Yapın</h1>
                <p className="text-xs text-slate-500 mt-1">Lütfen işlem yapmak istediğiniz kullanıcı rolünü seçiniz.</p>
              </div>

              <div className="grid grid-cols-3 bg-slate-100 border border-slate-200 p-1.5 rounded-2xl mb-6 text-xs font-bold shadow-inner">
                <button type="button" onClick={() => { setRoleTab('veli'); setErrorMsg(''); setInfoMsg(''); }} className={`py-2.5 rounded-xl transition ${roleTab === 'veli' ? 'bg-white text-[#006bb6] shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-800'}`}>👥 Veli Girişi</button>
                <button type="button" onClick={() => { setRoleTab('belletmen'); setErrorMsg(''); setInfoMsg(''); }} className={`py-2.5 rounded-xl transition ${roleTab === 'belletmen' ? 'bg-white text-[#006bb6] shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-800'}`}>👨‍🏫 Belletmen</button>
                <button type="button" onClick={() => { setRoleTab('yonetici'); setErrorMsg(''); setInfoMsg(''); }} className={`py-2.5 rounded-xl transition ${roleTab === 'yonetici' ? 'bg-white text-[#006bb6] shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-800'}`}>🛡️ Yönetici</button>
              </div>

              {errorMsg && <div className="mb-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold text-center">⚠️ {errorMsg}</div>}
              {infoMsg && <div className="mb-4 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold text-center">📲 {infoMsg}</div>}

              {roleTab === 'veli' && (
                step === 'phone' ? (
                  <form onSubmit={handleSendOtp} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">Sistemde Kayıtlı Veli Cep Telefonu Numaranız</label>
                      <input type="tel" required placeholder="05XX XXX XX XX" value={phone} onChange={(e) => setPhone(e.target.value)} className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold tracking-wider bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#006bb6] transition" />
                    </div>
                    <button type="submit" disabled={loading} className="w-full bg-[#006bb6] hover:bg-[#005694] text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition">{loading ? 'Kontrol Ediliyor...' : '📲 WhatsApp İle Şifre Gönder'}</button>
                  </form>
                ) : (
                  <form onSubmit={handleVerifyOtp} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5 text-center">WhatsApp Mesajınıza Gelen 6 Haneli Kodu Giriniz</label>
                      <input type="text" required maxLength={6} placeholder="••••••" value={otpInput} onChange={(e) => setOtpInput(e.target.value)} className="w-full p-3.5 border border-emerald-400 rounded-xl text-center text-2xl font-extrabold tracking-widest bg-emerald-50/30 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-600 transition" />
                    </div>
                    <button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition">✅ Doğrula ve Öğrenci Bilgilerimi Aç</button>
                    <button type="button" onClick={() => { setStep('phone'); setInfoMsg(''); setErrorMsg(''); setOtpInput(''); }} className="w-full text-xs text-slate-500 hover:text-slate-800 underline py-1">Telefon numarasını değiştir</button>
                  </form>
                )
              )}

              {roleTab === 'belletmen' && (
                <form onSubmit={handleBelletmenLogin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5">Nöbetçi Belletmen Öğretmen</label>
                    <select value={selectedBelId} onChange={(e) => setSelectedBelId(e.target.value)} className="w-full p-3.5 border border-slate-300 rounded-xl font-bold text-sm bg-slate-50 focus:bg-white">
                      {belletmenList.length === 0 ? <option value="">Henüz belletmen eklenmemiş</option> : belletmenList.map((b) => <option key={b.id} value={b.id}>{b.cinsiyet === 'kadin' ? '👩 ' : '👨 '} {b.name} ({b.brans})</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5">Şifreniz</label>
                    <input type="password" required placeholder="••••" value={belPassword} onChange={(e) => setBelPassword(e.target.value)} className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#006bb6]" />
                  </div>
                  <button type="submit" disabled={loading || belletmenList.length === 0} className="w-full bg-[#006bb6] hover:bg-[#005694] text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition">{loading ? 'Giriş Yapılıyor...' : '👨‍🏫 Yoklama Ekranını Aç'}</button>
                </form>
              )}

              {roleTab === 'yonetici' && (
                <form onSubmit={handleAdminQuickLogin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">Pansiyon İdaresi Yetkili Şifresi</label>
                    <input type="password" required placeholder="Yönetici Şifresi" value={adminPassword} onChange={(e) => setAdminPassword(e.target.value)} className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#006bb6]" />
                  </div>
                  <button type="submit" disabled={loading} className="w-full bg-slate-800 hover:bg-slate-900 text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition">{loading ? 'Doğrulanıyor...' : '🛡️ Yönetim Paneline Giriş Yap'}</button>
                </form>
              )}
            </div>
          </div>
        ) : (
          <div className="max-w-6xl w-full space-y-6">
            <div className="bg-white border-t-4 border-t-[#006bb6] border-x border-b border-slate-200 rounded-2xl p-5 shadow-sm flex flex-wrap justify-between items-center gap-4">
              <div>
                <span className="text-xs font-bold uppercase text-emerald-600">✅ Doğrulanmış Veli Oturumu ({phone})</span>
                <h2 className="text-xl font-extrabold text-slate-900">Öğrenci Bilgileri, Etüt/Yat Yoklama Geçmişi ve İzin Paneli</h2>
              </div>
              <div className="flex gap-2">
                <button onClick={() => loadParentData(phone)} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold border">🔄 Bilgileri Yenile</button>
                <button onClick={handleLogout} className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-xl text-xs font-bold">Çıkış Yap</button>
              </div>
            </div>

            {myStudents.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-1">
                {myStudents.map((st) => (
                  <button key={st.id} onClick={() => setSelectedStudentId(st.id)} className={`px-4 py-2 rounded-xl font-bold text-xs transition ${activeStudent?.id === st.id ? 'bg-[#006bb6] text-white shadow' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'}`}>👤 {st.name} (Oda {st.oda})</button>
                ))}
              </div>
            )}

            {activeStudent && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* SOL KOLON: ÖĞRENCİ BİLGİLERİ VE YOKLAMA İSTATİSTİKLERİ */}
                <div className="bg-white border border-slate-200 border-t-4 border-t-[#006bb6] rounded-2xl shadow-sm p-6 space-y-4 h-fit">
                  <div className="flex items-center justify-between border-b pb-3">
                    <div>
                      <span className="text-[11px] font-bold uppercase text-[#006bb6]">Öğrenciniz</span>
                      <h3 className="text-xl font-extrabold text-slate-900">{activeStudent.name}</h3>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${activeStudent.status === 'var' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : activeStudent.status === 'izinli' ? 'bg-amber-50 border-amber-200 text-amber-700' : 'bg-rose-50 border-rose-200 text-rose-700'}`}>
                      {activeStudent.status === 'var' ? '🟢 Yurtta (Var)' : activeStudent.status === 'izinli' ? '🟡 İzinli' : '🔴 Devamsız'}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                      <span className="text-slate-500 block">Pansiyon Bloğu</span>
                      <strong className="text-slate-800">{activeStudent.cinsiyet === 'kiz' ? 'Kız Pansiyonu' : 'Erkek Pansiyonu'}</strong>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                      <span className="text-slate-500 block">Kat / Oda</span>
                      <strong className="text-slate-800">{activeStudent.kat}. Kat - Oda {activeStudent.oda}</strong>
                    </div>
                    <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200 text-center">
                      <span className="text-emerald-700 block font-semibold">Katıldığı Etüt/Yat</span>
                      <strong className="text-lg font-black text-emerald-900">{presentCount} Yoklama</strong>
                    </div>
                    <div className="bg-rose-50 p-3 rounded-xl border border-rose-200 text-center">
                      <span className="text-rose-700 block font-semibold">Yoklamada Yok</span>
                      <strong className="text-lg font-black text-rose-900">{absentCount} Kez</strong>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-xl border border-blue-200 col-span-2 text-center">
                      <span className="text-[#006bb6] block font-semibold">Toplam Kullanılan İzin</span>
                      <strong className="text-base font-extrabold text-[#006bb6]">{activeStudentLeaves.length} İzin Kaydı</strong>
                    </div>
                  </div>
                </div>

                {/* SAĞ KOLON: GEÇMİŞ ETÜT & YAT YOKLAMALARI + İZİN TALEBİ */}
                <div className="lg:col-span-2 space-y-6">
                  {/* 1) GEÇMİŞ ETÜT VE YAT YOKLAMALARI TABLOSU */}
                  <div className="bg-white border border-slate-200 border-t-4 border-t-[#006bb6] rounded-2xl shadow-sm overflow-hidden">
                    <div className="p-5 border-b border-slate-200 flex flex-wrap justify-between items-center gap-3">
                      <div>
                        <h3 className="text-base font-extrabold text-slate-900">
                          📋 {activeStudent.name} — Geçmiş Etüt & Gece Yat Yoklamaları
                        </h3>
                        <p className="text-xs text-slate-500">
                          Belletmen öğretmenler tarafından alınan etüt ve gece yat yoklama kayıtları
                        </p>
                      </div>
                      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl text-xs font-bold border">
                        <button
                          type="button"
                          onClick={() => setHistoryFilter('all')}
                          className={`px-3 py-1.5 rounded-lg transition ${historyFilter === 'all' ? 'bg-[#006bb6] text-white' : 'text-slate-600'}`}
                        >
                          Tümü ({activeStudentHistory.length})
                        </button>
                        <button
                          type="button"
                          onClick={() => setHistoryFilter('etut')}
                          className={`px-3 py-1.5 rounded-lg transition ${historyFilter === 'etut' ? 'bg-[#006bb6] text-white' : 'text-slate-600'}`}
                        >
                          Etütler
                        </button>
                        <button
                          type="button"
                          onClick={() => setHistoryFilter('yat')}
                          className={`px-3 py-1.5 rounded-lg transition ${historyFilter === 'yat' ? 'bg-[#006bb6] text-white' : 'text-slate-600'}`}
                        >
                          Gece Yat
                        </button>
                      </div>
                    </div>

                    {filteredHistory.length === 0 ? (
                      <div className="p-8 text-center text-xs text-slate-400 italic">
                        Öğrencinize ait geçmiş etüt veya yat yoklama kaydı henüz bulunmamaktadır.
                      </div>
                    ) : (
                      <div className="overflow-x-auto max-h-80">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-[#006bb6] text-white sticky top-0">
                            <tr>
                              <th className="p-3">Tarih / Saat</th>
                              <th className="p-3">Yoklama Seansı (Etüt / Yat)</th>
                              <th className="p-3">Yoklama Durumu</th>
                              <th className="p-3">Nöbetçi Belletmen</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {filteredHistory.map((h) => (
                              <tr key={h.id} className="hover:bg-slate-50">
                                <td className="p-3 font-bold text-slate-800 whitespace-nowrap">
                                  {h.tarih} <span className="text-[10px] text-slate-400 ml-1">{h.saat}</span>
                                </td>
                                <td className="p-3 font-semibold text-slate-700">{h.seans}</td>
                                <td className="p-3">
                                  <span
                                    className={`px-2.5 py-1 rounded-full text-[11px] font-extrabold ${
                                      h.status === 'var'
                                        ? 'bg-emerald-100 text-emerald-800'
                                        : h.status === 'izinli'
                                        ? 'bg-amber-100 text-amber-800'
                                        : 'bg-rose-100 text-rose-800'
                                    }`}
                                  >
                                    {h.status === 'var' ? '🟢 VAR' : h.status === 'izinli' ? '🟡 İZİNLİ' : '🔴 YOK'}
                                  </span>
                                </td>
                                <td className="p-3 text-slate-600">{h.belletmenName || 'Nöbetçi Öğretmen'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* 2) YENİ İZİN TALEBİ FORMU */}
                  <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
                    <h3 className="text-base font-extrabold text-slate-900 mb-1">📝 Yeni İzin Talebi Gönder</h3>
                    <form onSubmit={handleCreateLeave} className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mt-4">
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">İzin Türü</label>
                        <select value={leaveType} onChange={(e) => setLeaveType(e.target.value)} className="w-full p-2.5 border border-slate-300 rounded-xl font-bold bg-slate-50 focus:bg-white">
                          <option value="Hafta Sonu Evci İzni">Hafta Sonu Evci İzni</option>
                          <option value="Aile Yanı Ev İzni">Aile Yanı Ev İzni</option>
                          <option value="Sağlık / Hastane İzni">Sağlık / Hastane İzni</option>
                          <option value="Çarşı / Kurs İzni">Çarşı / Kurs İzni</option>
                        </select>
                      </div>
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">Başlangıç Tarihi</label>
                        <input type="date" required value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full p-2.5 border border-slate-300 rounded-xl bg-slate-50 focus:bg-white" />
                      </div>
                      <div className="md:col-span-2">
                        <label className="font-bold text-slate-600 block mb-1">Dönüş Tarihi</label>
                        <input type="date" required value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full p-2.5 border border-slate-300 rounded-xl bg-slate-50 focus:bg-white" />
                      </div>
                      <div className="md:col-span-2">
                        <label className="font-bold text-slate-600 block mb-1">Açıklama / Adres</label>
                        <input type="text" required placeholder="Gidilecek adres veya kısa açıklama..." value={leaveNote} onChange={(e) => setLeaveNote(e.target.value)} className="w-full p-2.5 border border-slate-300 rounded-xl bg-slate-50 focus:bg-white" />
                      </div>
                      <div className="md:col-span-2 flex justify-end">
                        <button type="submit" disabled={loading} className="bg-[#006bb6] hover:bg-[#005694] text-white px-6 py-2.5 rounded-xl font-bold shadow-md transition">{loading ? 'Kaydediliyor...' : '✅ İzin Talebini Onayla'}</button>
                      </div>
                    </form>
                  </div>

                  {/* 3) GEÇMİŞ İZİNLER */}
                  <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
                    <h3 className="text-base font-extrabold text-slate-900 mb-3">📅 {activeStudent.name} Geçmiş İzinleri ({activeStudentLeaves.length})</h3>
                    {activeStudentLeaves.length === 0 ? (
                      <p className="text-xs text-slate-400 italic">Henüz izin kaydı bulunmamaktadır.</p>
                    ) : (
                      <div className="space-y-2 text-xs">
                        {activeStudentLeaves.map((lv) => (
                          <div key={lv.id} className="p-3 border border-slate-200 rounded-xl bg-slate-50 flex justify-between items-center">
                            <div><span className="font-bold text-[#006bb6]">{lv.tip}</span><p className="text-slate-600 mt-0.5">{lv.aciklama}</p></div>
                            <div className="text-right font-semibold text-slate-500">{lv.baslangic} → {lv.bitis}</div>
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

      <footer className="border-t border-slate-200 bg-white px-6 py-3 text-[11px] text-slate-400">
        <div className="max-w-6xl mx-auto flex justify-between">
          <span>© 2026 Prof. Dr. Mümtaz Turhan SBL Pansiyonu</span>
          <span>Neon Bulut Veritabanı • KVKK Uyumlu</span>
        </div>
      </footer>
    </div>
  );
}