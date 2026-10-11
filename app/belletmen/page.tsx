'use client';
import { useState } from 'react';
import { UserCheck, CheckCircle2, MessageSquare, FileText, LogOut, Sparkles, Send } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function BelletmenPortal() {
  const router = useRouter();
  const [selectedFloor, setSelectedFloor] = useState(1);
  const [sessionType, setSessionType] = useState('Etüt (19:15)');
  const [attendance, setAttendance] = useState<Record<number, string>>({
    101: 'Var', 102: 'Var', 103: 'İzinli', 104: 'Var', 105: 'Var', 106: 'Var', 108: 'Var', 109: 'Var', 110: 'Var'
  });
  const [savedSuccess, setSavedSuccess] = useState(false);

  // AI Chat state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([
    { role: 'assistant', text: 'Merhaba Nöbetçi Öğretmenim! Etüt ve yat yoklaması süreçlerinde size yardımcı olmaya hazırım.' }
  ]);

  const handleAllPresent = () => {
    const updated: Record<number, string> = {};
    [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15].forEach(num => {
      const roomNo = selectedFloor * 100 + num;
      if (roomNo !== selectedFloor * 100 + 7) { // 107, 207, 307 hariç
        updated[roomNo] = 'Var';
      }
    });
    setAttendance(updated);
  };

  const handleSaveAttendance = async () => {
    try {
      const res = await fetch('/api/attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ floor: selectedFloor, sessionType, records: attendance })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 4000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleWhatsApp = (roomNo: number, studentName: string) => {
    const text = `Sayın Veli, öğrenciniz ${studentName} (Oda: ${roomNo}) pansiyon akşam ${sessionType} yoklamasında Mazeretsiz Yok/Geç yazılmıştır. Bilgilerinizi rica ederiz.`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
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
            <p className="text-[11px] text-slate-500">Nöbetçi Belletmen Öğretmen Portalı</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-lg font-semibold border border-blue-200">Belletmen Modülü</span>
          <button onClick={() => router.push('/')} className="p-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 transition-all">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-6 space-y-6">
        
        {/* Kat ve Oturum Seçim Kartları */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3].map((floor) => (
            <button
              key={floor}
              onClick={() => setSelectedFloor(floor)}
              className={`p-5 rounded-2xl border text-left transition-all ${
                selectedFloor === floor
                  ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-500/20'
                  : 'bg-white text-slate-800 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <div className="text-[11px] font-semibold uppercase opacity-80">Kat Seçimi</div>
              <div className="text-lg font-bold mt-0.5">{floor}. Kat Odaları</div>
              <div className="text-xs opacity-80 mt-1">Oda Aralığı: {floor}01 - {floor}15</div>
            </button>
          ))}
          <div className="bg-amber-50 border border-amber-200 p-5 rounded-2xl text-amber-900 flex flex-col justify-center">
            <div className="text-[11px] font-semibold uppercase text-amber-700">Mimari Kural</div>
            <div className="text-xs font-bold mt-0.5">107, 207, 307 Nolu Odalar Depodur</div>
            <div className="text-[11px] mt-0.5 text-amber-800">Sistemden otomatik hariç tutulmuştur.</div>
          </div>
        </div>

        {/* Hızlı Yoklama Tablosu */}
        <div className="bg-white rounded-2xl shadow-xs p-8 border border-slate-200">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                <UserCheck className="w-5 h-5 text-blue-600" />
                <span>{selectedFloor}. Kat Hızlı Yoklama Listesi ({sessionType})</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">Öğrencilerin yoklama durumlarını güncelleyin ve velilere tek tıkla WhatsApp bildirimi gönderin.</p>
            </div>

            <div className="flex flex-wrap gap-2">
              <select 
                value={sessionType} 
                onChange={(e) => setSessionType(e.target.value)}
                className="px-3 py-2 rounded-xl border border-slate-300 text-xs bg-white font-medium"
              >
                <option>Etüt (19:15)</option>
                <option>Gece Yat Yoklaması (23:00)</option>
              </select>

              <button 
                onClick={handleAllPresent}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Tümünü Var Yap</span>
              </button>

              <button 
                onClick={handleSaveAttendance}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all"
              >
                Yoklamayı Kaydet
              </button>
            </div>
          </div>

          {savedSuccess && (
            <div className="mb-6 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-medium">
              ✓ {selectedFloor}. Kat {sessionType} yoklaması başarıyla veritabanına kaydedildi!
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-[11px] font-semibold text-slate-400 uppercase">
                  <th className="py-3 px-4">Oda No</th>
                  <th className="py-3 px-4">Öğrenci Adı Soyadı</th>
                  <th className="py-3 px-4">Anlık Statü</th>
                  <th className="py-3 px-4">Yoklama Durumu</th>
                  <th className="py-3 px-4 text-right">WhatsApp Bildirim Köprüsü</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {[1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15].map((num) => {
                  const roomNo = selectedFloor * 100 + num;
                  if (roomNo === selectedFloor * 100 + 7) return null; // 107, 207, 307 atla

                  const studentName = roomNo === 103 ? 'Zeynep Kaya' : roomNo === 101 ? 'Çağan Efe Zeybek' : roomNo === 102 ? 'Metehan Çelik' : `Öğrenci ${roomNo}`;
                  const status = attendance[roomNo] || 'Var';

                  return (
                    <tr key={roomNo} className="hover:bg-slate-50">
                      <td className="py-3 px-4 font-bold text-slate-800">{roomNo}</td>
                      <td className="py-3 px-4 font-medium text-slate-900">{studentName}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                          status === 'İzinli' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                        }`}>
                          {status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <select 
                          value={status} 
                          disabled={status === 'İzinli'}
                          onChange={(e) => setAttendance({...attendance, [roomNo]: e.target.value})}
                          className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs bg-white font-medium"
                        >
                          <option value="Var">Var</option>
                          <option value="Yok">Yok</option>
                          <option value="Geç">Geç</option>
                          <option value="İzinli">İzinli (Kilitli)</option>
                        </select>
                      </td>
                      <td className="py-3 px-4 text-right">
                        {status === 'Yok' || status === 'Geç' ? (
                          <button 
                            onClick={() => handleWhatsApp(roomNo, studentName)}
                            className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[11px] font-semibold shadow-xs transition-all"
                          >
                            <MessageSquare className="w-3.5 h-3.5" />
                            <span>WhatsApp Bildir</span>
                          </button>
                        ) : (
                          <span className="text-slate-400 font-normal">Normal</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
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
              placeholder="Yoklama ve mevzuat hakkında soru sorun..." 
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
