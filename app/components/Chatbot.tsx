"use client";
import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  sender: 'bot' | 'user';
  text: string;
}

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, sender: 'bot', text: 'Merhaba! SBL Pansiyon Asistanına hoş geldiniz. Size nasıl yardımcı olabilirim? (Örn: İzin, Yoklama, Şifre)' }
  ]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Mesajlar güncellendiğinde en alta kaydır
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen]);

  // Basit Kural Tabanlı Bot Mantığı
  const getBotResponse = (text: string) => {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('izin') || lowerText.includes('evci')) {
      return '🟡 İzin işlemleri: Veli onaylı izinler, idare veya belletmen öğretmenler tarafından sisteme girilmektedir. Lütfen nöbetçi öğretmenle iletişime geçin.';
    }
    if (lowerText.includes('yoklama') || lowerText.includes('saat') || lowerText.includes('etüt')) {
      return '📚 Yoklama Saatleri: \n- 1. Etüt: 19:30\n- 2. Etüt: 20:30\n- Gece Yat: 22:00';
    }
    if (lowerText.includes('şifre') || lowerText.includes('giremiyorum')) {
      return '🔑 Şifre İşlemleri: Belletmen giriş ekranındaki "Şifremi Unuttum" butonuna tıklayarak kayıtlı telefonunuza WhatsApp üzerinden şifre isteyebilirsiniz.';
    }
    if (lowerText.includes('iletişim') || lowerText.includes('telefon') || lowerText.includes('müdür')) {
      return '📞 Prof. Dr. Mümtaz Turhan SBL Pansiyon İdaresine okulun resmi iletişim kanallarından ulaşabilirsiniz.';
    }
    
    return 'Bunu tam anlayamadım. Lütfen "izin", "yoklama saatleri", "şifremi unuttum" gibi anahtar kelimeler kullanın.';
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMsg: Message = { id: Date.now(), sender: 'user', text: inputText.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');

    // Bota biraz "düşünme" payı verip yanıt verdiriyoruz
    setTimeout(() => {
      const botMsg: Message = { id: Date.now() + 1, sender: 'bot', text: getBotResponse(userMsg.text) };
      setMessages((prev) => [...prev, botMsg]);
    }, 600);
  };

  const handleQuickReply = (text: string) => {
    setInputText(text);
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* CHAT PENCERESİ */}
      {isOpen && (
        <div className="bg-white w-80 sm:w-96 h-[28rem] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden mb-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Üst Kısım */}
          <div className="bg-[#006bb6] p-4 text-white flex justify-between items-center shadow-md">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              <span className="font-extrabold text-sm">SBL Dijital Asistan</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-white hover:text-rose-200 transition font-bold text-lg leading-none">&times;</button>
          </div>

          {/* Mesajlaşma Alanı */}
          <div className="flex-1 p-4 overflow-y-auto bg-slate-50 space-y-4 text-sm">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl ${msg.sender === 'user' ? 'bg-[#006bb6] text-white rounded-br-sm' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm'}`}>
                  {msg.text.split('\n').map((line, i) => <React.Fragment key={i}>{line}<br/></React.Fragment>)}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Hızlı Yanıt Butonları */}
          <div className="bg-white border-t border-slate-100 p-2 flex gap-2 overflow-x-auto whitespace-nowrap">
            <button onClick={() => handleQuickReply('Yoklama saatleri')} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full text-[11px] font-bold transition">Yoklamalar</button>
            <button onClick={() => handleQuickReply('İzin nasıl alınır?')} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full text-[11px] font-bold transition">İzin Alma</button>
            <button onClick={() => handleQuickReply('Şifremi unuttum')} className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-full text-[11px] font-bold transition">Şifre İşlemleri</button>
          </div>

          {/* Mesaj Yazma Alanı */}
          <form onSubmit={handleSend} className="bg-white border-t border-slate-200 p-3 flex gap-2">
            <input 
              type="text" 
              placeholder="Bir soru sorun..." 
              value={inputText} 
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 p-2 bg-slate-100 border-none rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#006bb6] transition"
            />
            <button type="submit" disabled={!inputText.trim()} className="bg-[#006bb6] disabled:bg-slate-300 text-white w-10 h-10 rounded-xl flex items-center justify-center font-bold transition shadow-sm">
              ➤
            </button>
          </form>
        </div>
      )}

      {/* YÜZEN CHAT BUTONU */}
      <button 
        onClick={() => setIsOpen(!isOpen)} 
        className={`${isOpen ? 'bg-rose-500 hover:bg-rose-600' : 'bg-[#006bb6] hover:bg-[#005694]'} text-white w-14 h-14 rounded-full flex items-center justify-center shadow-2xl transition transform hover:scale-105 active:scale-95 ml-auto`}
      >
        {isOpen ? (
          <span className="text-2xl font-bold">&times;</span>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-7 h-7">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>
    </div>
  );
}