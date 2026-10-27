"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import SblLogo from '../components/SblLogo';

export default function BelletmenPage() {
  const [store, setStore] = useState<any>(null);
  const [loggedBelletmen, setLoggedBelletmen] = useState<any>(null);
  const [allowedGender, setAllowedGender] = useState<'erkek' | 'kiz'>('erkek');

  const [selectedId, setSelectedId] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [infoMsg, setInfoMsg] = useState('');

  const [activeDate, setActiveDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [activeSeans, setActiveSeans] = useState('1. Etüt Yoklaması (19:30)');
  const [selectedKat, setSelectedKat] = useState<number | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'yoklama' | 'defter' | 'izinler'>('yoklama');
  const [saving, setSaving] = useState(false);

  const [dutyLogForm, setDutyLogForm] = useState({
    tarih: new Date().toISOString().split('T')[0],
    seans: 'Gece Yat Yoklaması (22:00)',
    erkekBelletmen1: '',
    erkekBelletmen2: '',
    kizBelletmen1: '',
    kizBelletmen2: '',
    notlar: ''
  });
  const [editingLogId, setEditingLogId] = useState<string | null>(null);

  // PDF Önizleme Modalı İçin Durum
  const [pdfModalLog, setPdfModalLog] = useState<any>(null);

  const loadData = async (genderFilter?: 'erkek' | 'kiz') => {
    const g = genderFilter || allowedGender;
    const url = loggedBelletmen
      ? `/api/pansiyon?cinsiyet=${g}&t=${Date.now()}`
      : `/api/pansiyon?t=${Date.now()}`;
    const res = await fetch(url, { cache: 'no-store' });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      if (!selectedId && data.store?.belletmenler?.length > 0) {
        setSelectedId(data.store.belletmenler[0].id);
      }
    }
  };

  useEffect(() => {
    const saved = sessionStorage.getItem('pansiyon_belletmen_session');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setLoggedBelletmen(parsed.belletmen);
        setAllowedGender(parsed.allowedGender);
        loadData(parsed.allowedGender);
        return;
      } catch {}
    }
    loadData();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'belletmen_login', id: selectedId, password })
    });
    const data = await res.json();
    if (data.success) {
      setLoggedBelletmen(data.belletmen);
      setAllowedGender(data.allowedGender);
      sessionStorage.setItem('pansiyon_belletmen_session', JSON.stringify({
        belletmen: data.belletmen,
        allowedGender: data.allowedGender
      }));
      loadData(data.allowedGender);
    } else {
      setErrorMsg(data.message || 'Hatalı şifre!');
    }
  };

  const handleForgotPassword = async () => {
    if (!selectedId) return;
    setErrorMsg('');
    setInfoMsg('');
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'log_forgot_password', id: selectedId })
    });
    const data = await res.json();
    if (data.success && data.belletmen) {
      const msg = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın ${data.belletmen.name},\nBelletmen Yoklama Ekranı Giriş Şifreniz: *${data.belletmen.password}*`;
      let sent = false;
      if (data.tunnelUrl) {
        try {
          const r = await fetch(`${data.tunnelUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: data.belletmen.phone, code: data.belletmen.password, customMessage: msg })
          });
          if (r.ok) sent = true;
        } catch {}
      }
      if (sent) setInfoMsg('Şifreniz kayıtlı WhatsApp numaranıza gönderildi.');
      else setErrorMsg('WhatsApp sunucusu kapalı olduğu için gönderilemedi.');
    }
  };

  const handleStatusChange = async (studentId: string, newStatus: 'var' | 'yok' | 'izinli') => {
    if (!store?.students) return;
    let changedObj: any = null;
    const updatedStudents = store.students.map((s: any) => {
      if (s.id === studentId) {
        changedObj = { ...s, status: newStatus };
        return changedObj;
      }
      return s;
    });
    setStore({ ...store, students: updatedStudents });
    setSaving(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update_attendance',
        students: updatedStudents,
        changedStudent: changedObj,
        tarih: activeDate,
        seans: activeSeans,
        belletmenName: loggedBelletmen?.name || 'Nöbetçi Belletmen'
      })
    });
    const data = await res.json();
    if (data.success) setStore(data.store);
    setSaving(false);
  };

  const handleArchiveFullSession = async () => {
    const allGenderStudents = (store?.students || []).filter((s: any) => s.cinsiyet === allowedGender);
    setSaving(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update_attendance',
        students: allGenderStudents,
        archiveAll: true,
        tarih: activeDate,
        seans: activeSeans,
        belletmenName: loggedBelletmen?.name || 'Nöbetçi Belletmen'
      })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      alert(`✅ ${activeDate} — ${activeSeans} yoklaması tüm öğrenciler için arşivlendi ve Veli Portalı geçmişine işlendi!`);
    }
    setSaving(false);
  };

  const sendAbsenceWhatsApp = async (student: any, parentType: 'anne' | 'baba') => {
    const targetPhone = parentType === 'anne' ? student.anneTel : student.babaTel;
    const parentName = parentType === 'anne' ? student.anneAdi : student.babaAdi;
    if (!targetPhone) {
      alert('Bu velinin telefon numarası sistemde kayıtlı değil!');
      return;
    }
    const text = `*Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Pansiyonu*\n\nSayın ${parentName || 'Velimiz'},\nÖğrencimiz *${student.name}* (Oda ${student.oda}), ${activeDate} tarihli *${activeSeans}* yoklamasında *YOK* olarak işaretlenmiştir.\n\nBilgilerinize sunar, acil durumda nöbetçi belletmen öğretmenimizle iletişime geçmenizi rica ederiz.`;

    let sent = false;
    if (store?.tunnelUrl) {
      try {
        const r = await fetch(`${store.tunnelUrl}/send-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: targetPhone, code: 'YOKLAMA', customMessage: text })
        });
        if (r.ok) sent = true;
      } catch {}
    }
    if (sent) {
      alert(`✅ ${student.name} için ${parentType.toUpperCase()} numarasına (${targetPhone}) WhatsApp devamsızlık bildirimi gönderildi!`);
    } else {
      const clean = String(targetPhone).replace(/\D/g, '').slice(-10);
      window.open(`https://wa.me/90${clean}?text=${encodeURIComponent(text)}`, '_blank');
    }
  };

  const handleSaveOrUpdateDutyLog = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const payload = editingLogId
      ? { action: 'update_duty_log', id: editingLogId, ...dutyLogForm }
      : { action: 'add_duty_log', ...dutyLogForm };

    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      await loadData(allowedGender);
      setEditingLogId(null);
      setDutyLogForm({
        tarih: new Date().toISOString().split('T')[0],
        seans: 'Gece Yat Yoklaması (22:00)',
        erkekBelletmen1: '',
        erkekBelletmen2: '',
        kizBelletmen1: '',
        kizBelletmen2: '',
        notlar: ''
      });
      alert(editingLogId ? 'Nöbet defteri tutanağı güncellendi!' : 'Resmî nöbet tutanağı kaydedildi!');
    }
    setSaving(false);
  };

  const startEditLog = (log: any) => {
    setEditingLogId(log.id);
    setDutyLogForm({
      tarih: log.tarih || '',
      seans: log.seans || 'Gece Yat Yoklaması (22:00)',
      erkekBelletmen1: log.erkekBelletmen1 || '',
      erkekBelletmen2: log.erkekBelletmen2 || '',
      kizBelletmen1: log.kizBelletmen1 || '',
      kizBelletmen2: log.kizBelletmen2 || '',
      notlar: log.notlar || ''
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!loggedBelletmen) {
    return (
      <div className="min-h-screen bg-slate-100 flex flex-col justify-between">
        <header className="bg-white border-b px-6 py-3 flex justify-between items-center shadow-sm">
          <SblLogo size="sm" />
          <Link href="/" className="text-xs font-bold text-[#006bb6] hover:underline">← Ana Sayfaya Dön</Link>
        </header>
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-200 border-t-[6px] border-t-[#006bb6] max-w-md w-full">
            <div className="flex justify-center mb-4"><SblLogo size="md" showText={false} /></div>
            <h1 className="text-xl font-extrabold text-center text-slate-900">Nöbetçi Belletmen Girişi</h1>
            <p className="text-xs text-center text-slate-500 mb-6">Kız ve Erkek pansiyonu yoklama ekranları izole edilmiştir.</p>
            {errorMsg && <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold rounded-xl text-center">{errorMsg}</div>}
            {infoMsg && <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold rounded-xl text-center">{infoMsg}</div>}
            <form onSubmit={handleLogin} className="space-y-4">
              <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)} className="w-full p-3.5 border rounded-xl font-bold text-sm bg-slate-50">
                {(store?.belletmenler || []).map((b: any) => (
                  <option key={b.id} value={b.id}>{b.cinsiyet === 'kadin' ? '👩 ' : '👨 '} {b.name} ({b.brans})</option>
                ))}
              </select>
              <input type="password" required placeholder="Şifreniz" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-3.5 border rounded-xl text-center text-lg font-bold bg-slate-50" />
              <button type="submit" className="w-full bg-[#006bb6] hover:bg-[#005694] text-white py-3.5 rounded-xl font-bold text-sm shadow">Yoklama Ekranına Gir</button>
              <button type="button" onClick={handleForgotPassword} className="w-full text-xs text-[#006bb6] font-semibold hover:underline py-1">📲 Şifremi Unuttum (WhatsApp Gönder)</button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  const allStudents = (store?.students || []).filter((s: any) => s.cinsiyet === allowedGender);
  const filteredStudents = allStudents.filter((s: any) => {
    const katMatch = selectedKat === 'all' || Number(s.kat) === Number(selectedKat);
    const searchMatch = !searchTerm || s.name.toLowerCase().includes(searchTerm.toLowerCase()) || String(s.oda).toLowerCase().includes(searchTerm.toLowerCase());
    return katMatch && searchMatch;
  });

  const varCount = allStudents.filter((s: any) => s.status === 'var').length;
  const yokCount = allStudents.filter((s: any) => s.status === 'yok').length;
  const izinCount = allStudents.filter((s: any) => s.status === 'izinli').length;

  // PDF için devamsızlar
  const pdfYokStudents = allStudents.filter((s: any) => s.status === 'yok');

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <header className="bg-white border-b sticky top-0 z-20 px-4 md:px-8 py-3 shadow-sm">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-3">
          <div className="flex items-center gap-3">
            <SblLogo size="sm" showText={false} />
            <div>
              <span className="text-xs font-extrabold uppercase text-[#006bb6]">
                {allowedGender === 'kiz' ? '👩 KIZ PANSİYONU' : '👨 ERKEK PANSİYONU'} NÖBET EKRANI
              </span>
              <h1 className="text-base font-black text-slate-900">{loggedBelletmen.name}</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {saving && <span className="text-xs font-bold text-amber-600 animate-pulse">💾 Kaydediliyor...</span>}
            <button onClick={() => loadData(allowedGender)} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-2 rounded-xl text-xs font-bold border">🔄 Listeyi Yenile</button>
            <button onClick={() => { sessionStorage.removeItem('pansiyon_belletmen_session'); setLoggedBelletmen(null); }} className="bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-2 rounded-xl text-xs font-bold">Çıkış</button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4 md:p-6 space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm"><span className="text-xs text-slate-500 font-bold">Toplam Öğrenci</span><p className="text-2xl font-black text-slate-900">{allStudents.length}</p></div>
          <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-2xl"><span className="text-xs text-emerald-700 font-bold">🟢 Yurtta (Var)</span><p className="text-2xl font-black text-emerald-900">{varCount}</p></div>
          <div className="bg-rose-50 border border-rose-200 p-4 rounded-2xl"><span className="text-xs text-rose-700 font-bold">🔴 Yoklamada Yok</span><p className="text-2xl font-black text-rose-900">{yokCount}</p></div>
          <div className="bg-amber-50 border border-amber-200 p-4 rounded-2xl"><span className="text-xs text-amber-700 font-bold">🟡 Evci / İzinli</span><p className="text-2xl font-black text-amber-900">{izinCount}</p></div>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          <button onClick={() => setActiveTab('yoklama')} className={`px-5 py-2.5 rounded-xl font-bold text-xs transition ${activeTab === 'yoklama' ? 'bg-[#006bb6] text-white shadow' : 'bg-white border text-slate-600'}`}>📋 Etüt & Yat Yoklaması ({allStudents.length})</button>
          <button onClick={() => setActiveTab('defter')} className={`px-5 py-2.5 rounded-xl font-bold text-xs transition ${activeTab === 'defter' ? 'bg-[#006bb6] text-white shadow' : 'bg-white border text-slate-600'}`}>📖 Nöbet Defteri & PDF Çıktı ({store?.dutyLogs?.length || 0})</button>
          <button onClick={() => setActiveTab('izinler')} className={`px-5 py-2.5 rounded-xl font-bold text-xs transition ${activeTab === 'izinler' ? 'bg-[#006bb6] text-white shadow' : 'bg-white border text-slate-600'}`}>🟡 İzinli Öğrenci Listesi ({store?.leaves?.length || 0})</button>
        </div>

        {activeTab === 'yoklama' && (
          <div className="space-y-4">
            <div className="bg-white p-4 rounded-2xl border border-slate-200 border-t-4 border-t-[#006bb6] shadow-sm flex flex-wrap justify-between items-center gap-3">
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="font-extrabold text-slate-700">📅 Yoklama Seansı:</span>
                <input type="date" value={activeDate} onChange={(e) => setActiveDate(e.target.value)} className="p-2 border border-slate-300 rounded-xl font-bold bg-slate-50" />
                <select value={activeSeans} onChange={(e) => setActiveSeans(e.target.value)} className="p-2 border border-slate-300 rounded-xl font-bold bg-slate-50 text-[#006bb6]">
                  <option value="1. Etüt Yoklaması (19:30)">📚 1. Etüt Yoklaması (19:30)</option>
                  <option value="2. Etüt Yoklaması (20:30)">📚 2. Etüt Yoklaması (20:30)</option>
                  <option value="Gece Yat Yoklaması (22:00)">🌙 Gece Yat Yoklaması (22:00)</option>
                </select>
              </div>
              <button type="button" onClick={handleArchiveFullSession} disabled={saving} className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow transition">
                📥 Bu Seansın Yoklamasını Veli Geçmişine Kaydet
              </button>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap justify-between items-center gap-3">
              <div className="flex flex-wrap gap-1.5">
                {(['all', 1, 2, 3, 4] as const).map((k) => (
                  <button key={String(k)} onClick={() => setSelectedKat(k)} className={`px-3.5 py-2 rounded-xl text-xs font-bold transition ${selectedKat === k ? 'bg-[#006bb6] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>
                    {k === 'all' ? 'Tüm Katlar' : `${k}. Kat`}
                  </button>
                ))}
              </div>
              <input type="text" placeholder="🔍 Öğrenci adı veya oda ara..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="p-2.5 border rounded-xl text-xs w-full sm:w-64 bg-slate-50" />
            </div>

            {filteredStudents.length === 0 ? (
              <div className="bg-white p-10 rounded-2xl border text-center text-slate-400 text-sm">Bu filtrede kayıtlı öğrenci bulunmamaktadır.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filteredStudents.map((st: any) => (
                  <div key={st.id} className={`bg-white rounded-2xl border p-4 shadow-sm transition ${st.status === 'yok' ? 'border-rose-400 ring-2 ring-rose-100' : 'border-slate-200'}`}>
                    <div className="flex justify-between items-start gap-2">
                      <div>
                        <span className="text-[11px] font-bold bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full">{st.kat}. Kat • Oda {st.oda}</span>
                        <h3 className="text-base font-extrabold text-slate-900 mt-1">{st.name}</h3>
                      </div>
                      <div className="flex gap-1">
                        <button onClick={() => handleStatusChange(st.id, 'var')} className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${st.status === 'var' ? 'bg-emerald-600 text-white shadow' : 'bg-slate-100 text-slate-600 hover:bg-emerald-50'}`}>Var</button>
                        <button onClick={() => handleStatusChange(st.id, 'yok')} className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${st.status === 'yok' ? 'bg-rose-600 text-white shadow' : 'bg-slate-100 text-slate-600 hover:bg-rose-50'}`}>Yok</button>
                        <button onClick={() => handleStatusChange(st.id, 'izinli')} className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${st.status === 'izinli' ? 'bg-amber-500 text-white shadow' : 'bg-slate-100 text-slate-600 hover:bg-amber-50'}`}>İzinli</button>
                      </div>
                    </div>

                    {st.status === 'yok' && (
                      <div className="mt-3 pt-3 border-t border-rose-100 bg-rose-50/60 p-2.5 rounded-xl flex flex-wrap justify-between items-center gap-2">
                        <span className="text-[11px] font-bold text-rose-800">🚨 Veliye WhatsApp Devamsızlık Mesajı:</span>
                        <div className="flex gap-1.5">
                          <button onClick={() => sendAbsenceWhatsApp(st, 'anne')} className="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold">📲 Anneye Gönder ({st.anneTel || 'Yok'})</button>
                          <button onClick={() => sendAbsenceWhatsApp(st, 'baba')} className="bg-[#006bb6] hover:bg-[#005694] text-white px-2.5 py-1 rounded-lg text-[11px] font-bold">📲 Babaya Gönder ({st.babaTel || 'Yok'})</button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'defter' && (
          <div className="space-y-6">
            <div className={`p-6 rounded-2xl border border-t-4 shadow-sm space-y-4 ${editingLogId ? 'bg-amber-50 border-amber-300 border-t-amber-500' : 'bg-white border-slate-200 border-t-[#006bb6]'}`}>
              <h2 className="text-base font-extrabold text-slate-900">
                {editingLogId ? '✏️ Nöbet Defteri Kaydını ve Belletmen İsimlerini Düzenle' : '📖 Resmî Pansiyon Nöbet Defteri Tutanağı Yaz'}
              </h2>
              <form onSubmit={handleSaveOrUpdateDutyLog} className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                <input type="date" value={dutyLogForm.tarih} onChange={(e) => setDutyLogForm({ ...dutyLogForm, tarih: e.target.value })} className="p-2.5 border rounded-xl bg-white" />
                <select value={dutyLogForm.seans} onChange={(e) => setDutyLogForm({ ...dutyLogForm, seans: e.target.value })} className="p-2.5 border rounded-xl font-bold md:col-span-3 bg-white">
                  <option value="1. Etüt Yoklaması (19:30)">1. Etüt Yoklaması (19:30)</option>
                  <option value="2. Etüt Yoklaması (20:30)">2. Etüt Yoklaması (20:30)</option>
                  <option value="Gece Yat Yoklaması (22:00)">Gece Yat Yoklaması (22:00)</option>
                </select>
                <input placeholder="Erkek Belletmen 1 Adı" value={dutyLogForm.erkekBelletmen1} onChange={(e) => setDutyLogForm({ ...dutyLogForm, erkekBelletmen1: e.target.value })} className="p-2.5 border rounded-xl bg-white" />
                <input placeholder="Erkek Belletmen 2 Adı" value={dutyLogForm.erkekBelletmen2} onChange={(e) => setDutyLogForm({ ...dutyLogForm, erkekBelletmen2: e.target.value })} className="p-2.5 border rounded-xl bg-white" />
                <input placeholder="Kız Belletmen 1 Adı" value={dutyLogForm.kizBelletmen1} onChange={(e) => setDutyLogForm({ ...dutyLogForm, kizBelletmen1: e.target.value })} className="p-2.5 border rounded-xl bg-white" />
                <input placeholder="Kız Belletmen 2 Adı" value={dutyLogForm.kizBelletmen2} onChange={(e) => setDutyLogForm({ ...dutyLogForm, kizBelletmen2: e.target.value })} className="p-2.5 border rounded-xl bg-white" />
                <textarea rows={3} placeholder="Nöbet vukuat ve yoklama notları..." value={dutyLogForm.notlar} onChange={(e) => setDutyLogForm({ ...dutyLogForm, notlar: e.target.value })} className="md:col-span-4 p-2.5 border rounded-xl bg-white" />
                <div className="md:col-span-4 flex justify-end gap-2">
                  {editingLogId && (
                    <button
                      type="button"
                      onClick={() => {
                        setEditingLogId(null);
                        setDutyLogForm({ tarih: new Date().toISOString().split('T')[0], seans: 'Gece Yat Yoklaması (22:00)', erkekBelletmen1: '', erkekBelletmen2: '', kizBelletmen1: '', kizBelletmen2: '', notlar: '' });
                      }}
                      className="bg-slate-400 text-white px-5 py-2.5 rounded-xl font-bold"
                    >
                      İptal
                    </button>
                  )}
                  <button type="submit" className="bg-[#006bb6] hover:bg-[#005694] text-white px-6 py-2.5 rounded-xl font-bold shadow">
                    {editingLogId ? '💾 Değişiklikleri Kaydet' : '✅ Tutanağı Kaydet'}
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-base font-extrabold text-slate-900">
                  🗂️ Kaydedilen Nöbet Defteri Tutanakları ({store?.dutyLogs?.length || 0})
                </h3>
                <span className="text-xs text-slate-500">Butona tıklayarak açılan pencereden direkt PDF çıktısı alabilirsiniz.</span>
              </div>

              {(store?.dutyLogs || []).length === 0 ? (
                <p className="text-xs text-slate-400 italic py-4">Henüz kaydedilmiş bir nöbet tutanağı bulunmamaktadır.</p>
              ) : (
                <div className="space-y-3">
                  {(store?.dutyLogs || []).map((log: any) => (
                    <div key={log.id} className="p-4 border border-slate-200 rounded-2xl bg-slate-50 space-y-3 text-xs">
                      <div className="flex flex-wrap justify-between items-center gap-2">
                        <span className="font-extrabold text-sm text-[#006bb6]">
                          📅 {log.tarih} — {log.seans}
                        </span>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => startEditLog(log)}
                            className="bg-amber-100 hover:bg-amber-500 hover:text-white text-amber-800 border border-amber-200 px-3 py-1.5 rounded-xl font-bold transition"
                          >
                            ✏️ İsimleri / Notu Düzenle
                          </button>
                          <button
                            type="button"
                            onClick={() => setPdfModalLog(log)}
                            className="bg-[#006bb6] hover:bg-[#005694] text-white px-4 py-1.5 rounded-xl font-bold shadow-sm transition flex items-center gap-1.5"
                          >
                            🖨️ Resmî PDF Çıktısı Al
                          </button>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 bg-white p-3 rounded-xl border border-slate-200">
                        <div><strong>👨 Erkek Pansiyonu Nöbetçileri:</strong> {log.erkekBelletmen1 || '-'}, {log.erkekBelletmen2 || '-'}</div>
                        <div><strong>👩 Kız Pansiyonu Nöbetçileri:</strong> {log.kizBelletmen1 || '-'}, {log.kizBelletmen2 || '-'}</div>
                      </div>
                      <div className="bg-white p-3 rounded-xl border border-slate-200 text-slate-700">
                        <strong>Vukuat / Nöbet Notu:</strong> {log.notlar || 'Normal.'}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'izinler' && (
          <div className="bg-white p-6 rounded-2xl border border-slate-200 border-t-4 border-t-[#006bb6] shadow-sm space-y-3">
            <h2 className="text-base font-extrabold text-slate-900">🟡 Veli Onaylı İzinli Öğrenciler</h2>
            {(store?.leaves || []).length === 0 ? (
              <p className="text-xs text-slate-400 italic">Kayıtlı izin bulunmamaktadır.</p>
            ) : (
              (store?.leaves || []).map((lv: any) => (
                <div key={lv.id} className="p-3 border rounded-xl bg-amber-50/40 flex justify-between items-center text-xs">
                  <div>
                    <strong className="text-slate-900">{lv.studentName} (Oda {lv.oda})</strong>
                    <span className="ml-2 bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">{lv.tip}</span>
                    <p className="text-slate-600 mt-1">{lv.aciklama}</p>
                  </div>
                  <div className="text-right font-bold text-slate-600">{lv.baslangic} → {lv.bitis}</div>
                </div>
              ))
            )}
          </div>
        )}
      </main>

      {/* =================================================================== */}
      // 📄 MEB ANTETLİ A4 PDF ÇIKTI MODALI (Tarayıcı Engelini Kesinlikle Aşar)
      {/* =================================================================== */}
      {pdfModalLog && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[95vh] flex flex-col overflow-hidden">
            {/* Modal Üst Bilgi Barı */}
            <div className="bg-[#006bb6] text-white p-4 flex justify-between items-center no-print">
              <span className="font-extrabold text-sm">📄 Resmî Nöbet Defteri Tutanak Önizlemesi</span>
              <div className="flex gap-2">
                <button
                  onClick={() => window.print()}
                  className="bg-white text-[#006bb6] hover:bg-slate-100 px-4 py-2 rounded-xl text-xs font-black shadow transition flex items-center gap-1"
                >
                  🖨️ PDF İndir / Yazdır
                </button>
                <button
                  onClick={() => setPdfModalLog(null)}
                  className="bg-rose-600 hover:bg-rose-700 text-white px-3 py-2 rounded-xl text-xs font-bold transition"
                >
                  ✕ Kapat
                </button>
              </div>
            </div>

            {/* A4 Kağıt Tasarım Alanı */}
            <div className="p-6 sm:p-10 overflow-y-auto bg-slate-100 flex-1 flex justify-center">
              <div className="bg-white shadow-lg border border-slate-300 w-[210mm] min-h-[297mm] p-[15mm] text-slate-900 box-border font-serif text-[11pt] leading-normal">
                {/* Antet */}
                <div className="text-center border-b-2 border-[#006bb6] pb-3 mb-5">
                  <h1 className="m-0 text-[15pt] font-bold uppercase">T.C. MİLLÎ EĞİTİM BAKANLIĞI</h1>
                  <h2 className="m-1 text-[12pt] font-bold text-[#006bb6]">İSTANBUL — PROF. DR. MÜMTAZ TURHAN SOSYAL BİLİMLER LİSESİ</h2>
                  <p className="m-1 text-[10pt] font-bold uppercase">Öğrenci Pansiyonu Günlük Nöbetçi Belletmen Tutanağı</p>
                </div>

                {/* Meta Bilgiler */}
                <table className="w-full border-collapse mb-4 text-[10.5pt]">
                  <tbody>
                    <tr>
                      <td className="border border-slate-400 bg-slate-50 p-2 font-bold w-[22%]">Nöbet Tarihi</td>
                      <td className="border border-slate-400 p-2 w-[28%]">{pdfModalLog.tarih}</td>
                      <td className="border border-slate-400 bg-slate-50 p-2 font-bold w-[22%]">Yoklama Seansı</td>
                      <td className="border border-slate-400 p-2 w-[28%]">{pdfModalLog.seans}</td>
                    </tr>
                    <tr>
                      <td className="border border-slate-400 bg-slate-50 p-2 font-bold">Erkek Pansiyonu Nöbetçileri</td>
                      <td className="border border-slate-400 p-2">{[pdfModalLog.erkekBelletmen1, pdfModalLog.erkekBelletmen2].filter(Boolean).join(' - ') || 'Belirtilmedi'}</td>
                      <td className="border border-slate-400 bg-slate-50 p-2 font-bold">Kız Pansiyonu Nöbetçileri</td>
                      <td className="border border-slate-400 p-2">{[pdfModalLog.kizBelletmen1, pdfModalLog.kizBelletmen2].filter(Boolean).join(' - ') || 'Belirtilmedi'}</td>
                    </tr>
                  </tbody>
                </table>

                {/* Mevcut Özeti */}
                <div className="font-bold text-[#006bb6] text-[11pt] mt-4 mb-1 uppercase border-b border-slate-300 pb-1">
                  1. Pansiyon Yoklama ve Mevcut Özeti ({allowedGender === 'kiz' ? 'Kız Pansiyonu' : 'Erkek Pansiyonu'})
                </div>
                <table className="w-full border-collapse mb-4 text-[10.5pt] text-center">
                  <thead>
                    <tr className="bg-slate-100">
                      <th className="border border-slate-400 p-2">Kayıtlı Toplam</th>
                      <th className="border border-slate-400 p-2">Mevcut (Var)</th>
                      <th className="border border-slate-400 p-2">Evci / İzinli</th>
                      <th className="border border-slate-400 p-2">Yok (Devamsız)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-slate-400 p-2 font-bold text-base">{allStudents.length}</td>
                      <td className="border border-slate-400 p-2 font-bold text-base text-emerald-700">{varCount}</td>
                      <td className="border border-slate-400 p-2 font-bold text-base text-amber-700">{izinCount}</td>
                      <td className="border border-slate-400 p-2 font-bold text-base text-rose-700">{pdfYokStudents.length}</td>
                    </tr>
                  </tbody>
                </table>

                {/* Devamsızlar Listesi */}
                <div className="font-bold text-[#006bb6] text-[11pt] mt-4 mb-1 uppercase border-b border-slate-300 pb-1">
                  2. Yoklamada Bulunmayan (Devamsız) Öğrenciler
                </div>
                <table className="w-full border-collapse mb-4 text-[10.5pt]">
                  <thead>
                    <tr className="bg-slate-100">
                      <th className="border border-slate-400 p-2 w-[12%] text-center">Sıra</th>
                      <th className="border border-slate-400 p-2 text-left">Öğrenci Adı Soyadı</th>
                      <th className="border border-slate-400 p-2 w-[28%] text-center">Kat / Oda No</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pdfYokStudents.length === 0 ? (
                      <tr>
                        <td colSpan={3} className="border border-slate-400 p-3 text-center text-emerald-700 font-bold">
                          Yoklamada devamsız (yok) öğrenci bulunmamaktadır.
                        </td>
                      </tr>
                    ) : (
                      pdfYokStudents.map((s: any, idx: number) => (
                        <tr key={s.id}>
                          <td className="border border-slate-400 p-2 text-center">{idx + 1}</td>
                          <td className="border border-slate-400 p-2 font-bold">{s.name}</td>
                          <td className="border border-slate-400 p-2 text-center">{s.kat}. Kat / Oda {s.oda}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>

                {/* Vukuat ve Notlar */}
                <div className="font-bold text-[#006bb6] text-[11pt] mt-4 mb-1 uppercase border-b border-slate-300 pb-1">
                  3. Nöbet Vukuat Raporu, Etüt ve Gece Yoklaması Notları
                </div>
                <div className="border border-slate-400 bg-slate-50/50 p-3 min-h-[120px] text-[10.5pt] whitespace-pre-wrap">
                  {pdfModalLog.notlar || 'Nöbet süresince herhangi bir olumsuz vukuat yaşanmamış olup etüt ve yat yoklamaları zamanında alınmıştır.'}
                </div>

                {/* İmza Alanları */}
                <table className="w-full mt-8 text-center text-[10pt] border-collapse">
                  <tbody>
                    <tr>
                      <td className="w-1/4 p-2 align-top">
                        <div>Erkek Pansiyonu Belletmen</div>
                        <div className="mt-12 border-t border-dotted border-slate-600 pt-1 font-bold">{pdfModalLog.erkekBelletmen1 || '.........................'}</div>
                        <div className="text-[8.5pt] text-slate-500">İmza</div>
                      </td>
                      <td className="w-1/4 p-2 align-top">
                        <div>Erkek Pansiyonu Belletmen</div>
                        <div className="mt-12 border-t border-dotted border-slate-600 pt-1 font-bold">{pdfModalLog.erkekBelletmen2 || '.........................'}</div>
                        <div className="text-[8.5pt] text-slate-500">İmza</div>
                      </td>
                      <td className="w-1/4 p-2 align-top">
                        <div>Kız Pansiyonu Belletmen</div>
                        <div className="mt-12 border-t border-dotted border-slate-600 pt-1 font-bold">{pdfModalLog.kizBelletmen1 || '.........................'}</div>
                        <div className="text-[8.5pt] text-slate-500">İmza</div>
                      </td>
                      <td className="w-1/4 p-2 align-top">
                        <div>Kız Pansiyonu Belletmen</div>
                        <div className="mt-12 border-t border-dotted border-slate-600 pt-1 font-bold">{pdfModalLog.kizBelletmen2 || '.........................'}</div>
                        <div className="text-[8.5pt] text-slate-500">İmza</div>
                      </td>
                    </tr>
                  </tbody>
                </table>

                {/* Onay */}
                <div className="text-center mt-8 text-[10.5pt]">
                  <div className="font-bold">KONTROL EDEN / ONAYLAYAN</div>
                  <div className="mt-10 font-bold">......................................................</div>
                  <div className="text-[9.5pt]">Pansiyon Müdür Yardımcısı</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}