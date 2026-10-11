'use client';
import { useState, useEffect } from 'react';
import { Users, Calendar, CheckCircle2, LogOut, Sparkles, Send } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function VeliPortal() {
  const router = useRouter();
  const [leaveSubmitted, setLeaveSubmitted] = useState(false);
  const [leaveType, setLeaveType] = useState('Ev İzni');
  const [transport, setTransport] = useState('Veli teslim alacak');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [leaves, setLeaves] = useState<any[]>([]);

  // AI Chat modal state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([
    { role: 'assistant', text: 'Merhaba! Ben Yurt Al Asistanı. Pansiyon izinleri, etüt saatleri ve MEB mevzuatı hakkında sorularınızı yanıtlayabilirim.' }
  ]);

  useEffect(() => {
    fetch('/api/leaves')
      .then(res => res.json())
      .then(data => {
        if (data.success) setLeaves(data.leaves);
      })
      .catch(err => console.error(err));
  }, []);

  const handleLeaveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/leaves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentName: 'Berra Adaçoğlu', leaveType, startDate, endDate, transport, reason })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setLeaveSubmitted(true);
        setLeaves([data.leave, ...leaves]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatInput('');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userMsg })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setMessages(prev => [...prev, { role: 'assistant', text: data.reply }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Üzgünüm, şu anda yanıt veremiyorum.' }]);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 pb-20">
      {/* Üst Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-3 flex justify-between items-center shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-xs">
            SBL
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-900 text-sm">Prof. Dr. Mümtaz Turhan SBL Pansiyon</span>
              <span className="bg-blue-50 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-medium border border-blue-200">MEB Uyumlu</span>
            </div>
            <p className="text-[11px] text-slate-500">Veli Bilgilendirme ve İzin Portalı</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="bg-emerald-50 text-emerald-700 px-3 py-1 rounded-lg font-semibold border border-emerald-200">Veli Modülü</span>
          <button onClick={() => router.push('/')} className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 transition-all">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      <div className="max-w-5xl mx-auto p-6 space-y-6">
        
        {/* Öğrenci Durum Kartları */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-xs border border-slate-200">
            <span className="text-xs font-semibold text-slate-400 uppercase">Öğrenci Statüsü</span>
            <div className="text-2xl font-bold text-emerald-600 mt-2 flex items-center space-x-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Yurtta / Pansiyonda</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">Berra Adaçoğlu • Oda: 3 | Blok: B Kız</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-xs border border-slate-200">
            <span className="text-xs font-semibold text-slate-400 uppercase">Etüt Durumu</span>
            <div className="text-2xl font-bold text-blue-600 mt-2">Aktif Etütte (19:15)</div>
            <p className="text-xs text-slate-500 mt-1">Sabit etüt salonu katılımı onaylandı</p>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-xs border border-slate-200">
            <span className="text-xs font-semibold text-slate-400 uppercase">Gece Yat Yoklaması</span>
            <div className="text-2xl font-bold text-slate-800 mt-2">Var (23:00)</div>
            <p className="text-xs text-slate-500 mt-1">Son yat yoklaması sorunsuz</p>
          </div>
        </div>

        {/* İzin Bildirim Formu */}
        <div className="bg-white rounded-2xl shadow-xs p-8 border border-slate-200">
          <h2 className="text-lg font-bold text-slate-900 mb-2 flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-blue-600" />
            <span>İzin Bildirim Formu (MEB Otomatik Onaylı)</span>
          </h2>
          <p className="text-xs text-slate-500 mb-6">MEB mevzuatına göre veli beyanı esas olduğundan, girilen izin talepleri sisteme kaydedildiği an onaylanır.</p>

          {leaveSubmitted && (
            <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl flex items-center space-x-3 text-xs">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <div>
                <p className="font-semibold">İzin talebiniz başarıyla kaydedildi ve ANINDA ONAYLANDI.</p>
                <p className="text-emerald-700 mt-0.5">Öğrenci statüsü 'İzinli' olarak nöbetçi belletmen öğretmen paneline yansıtıldı.</p>
              </div>
            </div>
          )}

          <form onSubmit={handleLeaveSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">İzin Türü</label>
                <select 
                  value={leaveType} 
                  onChange={(e) => setLeaveType(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm bg-white"
                >
                  <option>Ev İzni</option>
                  <option>Etüt İzni / Mazeret</option>
                  <option>Hafta Sonu İzni</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Ulaşım Biçimi</label>
                <input 
                  type="text" 
                  required 
                  value={transport} 
                  onChange={(e) => setTransport(e.target.value)} 
                  placeholder="Veli teslim alacak / Otobüs" 
                  className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm" 
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Başlangıç Tarih ve Saati</label>
                <input type="datetime-local" required value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm" />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Bitiş Tarih ve Saati</label>
                <input type="datetime-local" required value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Mazeret ve Gidilecek Adres Açıklaması</label>
              <textarea rows={3} required value={reason} onChange={(e) => setReason(e.target.value)} placeholder="İzin gerekçesini detaylı yazınız..." className="w-full px-4 py-3 rounded-xl border border-slate-300 text-sm"></textarea>
            </div>

            <button type="submit" className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg shadow-blue-600/20 transition-all text-sm">
              İzin Talebini Gönder ve Otomatik Onayla
            </button>
          </form>
        </div>

        {/* Geçmiş İzinler Listesi */}
        <div className="bg-white rounded-2xl shadow-xs p-8 border border-slate-200">
          <h3 className="text-sm font-bold text-slate-900 mb-4">Geçmiş ve Aktif İzin Bildirimlerim</h3>
          {leaves.length === 0 ? (
            <p className="text-xs text-slate-500">Henüz kayıtlı bir izin talebi bulunmuyor.</p>
          ) : (
            <div className="space-y-3">
              {leaves.map((l: any, idx: number) => (
                <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex justify-between items-center text-xs">
                  <div>
                    <p className="font-bold text-slate-800">{l.leaveType} • {l.studentName}</p>
                    <p className="text-slate-500 mt-0.5">Mazeret: {l.reason} ({l.transport})</p>
                    <p className="text-[10px] text-slate-400 mt-1">Başlangıç: {l.startDate} | Bitiş: {l.endDate}</p>
                  </div>
                  <span className="px-3 py-1 rounded-full font-semibold bg-emerald-100 text-emerald-800">
                    {l.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Yapay Zeka Asistan Chat Modal / Drawer */}
      {chatOpen && (
        <div className="fixed bottom-20 right-6 z-50 w-96 bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col h-[480px]">
          <div className="bg-indigo-600 text-white px-5 py-4 flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-amber-300" />
              <span className="font-bold text-sm">Yurt Al Asistanı (Gemini AI)</span>
            </div>
            <button onClick={() => setChatOpen(false)} className="text-white/80 hover:text-white font-bold text-sm">✕</button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs bg-slate-50">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl ${m.role === 'user' ? 'bg-indigo-600 text-white rounded-br-xs' : 'bg-white text-slate-800 border border-slate-200 rounded-bl-xs shadow-xs'}`}>
                  {m.text}
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleSendMessage} className="p-3 bg-white border-t border-slate-200 flex space-x-2">
            <input 
              type="text" 
              value={chatInput} 
              onChange={e => setChatInput(e.target.value)} 
              placeholder="Pansiyon kuralları hakkında soru sorun..." 
              className="flex-1 px-3 py-2 rounded-xl border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" 
            />
            <button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold transition-all">
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}

      {/* Sabit Yurt Al Asistanı Butonu */}
      <div className="fixed bottom-6 right-6 z-50">
        <button onClick={() => setChatOpen(!chatOpen)} className="flex items-center space-x-2 px-5 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-2xl font-semibold text-sm transition-all hover:scale-105">
          <Sparkles className="w-4 h-4 text-amber-300 animate-spin" />
          <span>Yurt Al Asistanı</span>
        </button>
      </div>
    </div>
  );
}
