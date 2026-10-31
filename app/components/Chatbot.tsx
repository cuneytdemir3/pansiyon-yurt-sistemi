"use client";
import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  sender: 'bot' | 'user';
  text: string;
}

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [showIntro, setShowIntro] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, sender: 'bot', text: 'Merhaba! SBL Dijital Asistanına hoş geldiniz. Size nasıl yardımcı olabilirim? (Örn: İzin, Yoklama, Şifre)' }
  ]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Mesajlar güncellendiğinde en alta kaydır
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isOpen, showIntro]);

  // Butona tıklandığında lale animasyonunu oynat ve sohbeti aç
  const toggleChat = () => {
    if (!isOpen) {
      setIsOpen(true);
      setShowIntro(true);
      // Animasyon süresini 2 saniyeye çıkardık (izleme keyfi için)
      setTimeout(() => {
        setShowIntro(false);
      }, 2000);
    } else {
      setIsOpen(false);
      setShowIntro(false);
    }
  };

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
      
      {/* ÖZEL ANİMASYON CSS'LERİ */}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes bloom {
          0% { transform: scale(0) translateY(50px); opacity: 0; }
          60% { transform: scale(1.1) translateY(-10px); opacity: 1; }
          100% { transform: scale(1) translateY(0); opacity: 1; }
        }
        @keyframes sway {
          0%, 100% { transform: rotate(-3deg); }
          50% { transform: rotate(3deg); }
        }
        @keyframes petal-pulse {
          0%, 100% { transform: scale(1); filter: brightness(1); }
          50% { transform: scale(1.05); filter: brightness(1.2); }
        }
        @keyframes glowing-bg {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .animate-bloom { animation: bloom 1s cubic-bezier(0.25, 1, 0.5, 1) forwards; transform-origin: bottom center; }
        .animate-sway { animation: sway 3s ease-in-out infinite; transform-origin: bottom center; }
        .animate-petal { animation: petal-pulse 2s ease-in-out infinite; transform-origin: bottom center; }
        .glowing-bg { background-size: 200% 200%; animation: glowing-bg 3s ease infinite; }
      `}} />

      {/* CHAT PENCERESİ */}
      {isOpen && (
        <div className="bg-white w-80 sm:w-96 h-[28rem] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden mb-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
          
          {showIntro ? (
            /* ETKİLEYİCİ LALE (TULIP) ANİMASYONU EKRANI */
            <div className="flex-1 flex flex-col items-center justify-center bg-gradient-to-br from-rose-50 via-white to-emerald-50 glowing-bg relative overflow-hidden">
              
              {/* Arka plan parlama efekti (Glow) */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-48 h-48 bg-rose-200/50 rounded-full blur-3xl animate-pulse"></div>
              </div>

              {/* Lale İkonu - Bloom ve Sway (Büyüme ve Salınım) Kombinasyonu */}
              <div className="relative animate-bloom">
                <div className="animate-sway">
                  <svg viewBox="0 0 100 100" className="w-40 h-40 drop-shadow-2xl">
                    {/* Gövde ve Yapraklar */}
                    <path d="M50 90 Q 50 60 50 50" stroke="#16a34a" strokeWidth="5" fill="transparent" strokeLinecap="round" />
                    <path d="M50 85 Q 25 70 25 45 Q 35 55 50 65" fill="#22c55e" className="animate-petal" style={{ animationDelay: '0.2s' }} />
                    <path d="M50 75 Q 75 65 75 45 Q 65 55 50 60" fill="#22c55e" className="animate-petal" style={{ animationDelay: '0.5s' }} />
                    
                    {/* Kırmızı/Pembe Lale Çiçeği */}
                    <g className="animate-petal">
                      {/* Arka Taç Yaprak */}
                      <path d="M35 40 C 35 60 45 75 50 75 C 55 75 65 60 65 40 C 65 20 55 15 50 35 C 45 15 35 20 35 40 Z" fill="#be185d" />
                      {/* Sol Taç Yaprak */}
                      <path d="M25 45 C 25 70 40 75 50 75 C 50 75 40 50 35 30 C 30 15 25 25 25 45 Z" fill="#e11d48" />
                      {/* Sağ Taç Yaprak */}
                      <path d="M75 45 C 75 70 60 75 50 75 C 50 75 60 50 65 30 C 70 15 75 25 75 45 Z" fill="#e11d48" />
                      {/* Orta Parlak Yaprak */}
                      <path d="M42 35 C 42 60 48 70 50 70 C 52 70 58 60 58 35 C 58 15 52 10 50 30 C 48 10 42 15 42 35 Z" fill="#fbcfe8" />
                    </g>
                  </svg>
                </div>
              </div>
              
              <h3 className="mt-8 font-black text-rose-600 text-2xl tracking-widest z-10 animate-in fade-in slide-in-from-bottom-2 duration-700 delay-500">SBL ASİSTAN</h3>
              <p className="text-[11px] font-bold text-slate-400 mt-2 z-10 animate-pulse">Lütfen bekleyin...</p>
            </div>
          ) : (
            /* MESAJLAŞMA ARAYÜZÜ */
            <>
              {/* Lale Temalı Üst Bilgi Barı */}
              <div className="bg-gradient-to-r from-rose-600 to-[#006bb6] p-4 text-white flex justify-between items-center shadow-md">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 bg-emerald-300 rounded-full animate-pulse"></div>
                  <span className="font-extrabold text-sm">SBL Dijital Asistan</span>
                </div>
                <button onClick={toggleChat} className="text-white hover:text-rose-200 transition font-bold text-xl leading-none">&times;</button>
              </div>

              {/* Mesajlaşma Alanı */}
              <div className="flex-1 p-4 overflow-y-auto bg-slate-50 space-y-4 text-sm">
                {messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] p-3 rounded-2xl ${msg.sender === 'user' ? 'bg-gradient-to-r from-rose-500 to-rose-600 text-white rounded-br-sm shadow-md' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm'}`}>
                      {msg.text.split('\n').map((line, i) => <React.Fragment key={i}>{line}<br/></React.Fragment>)}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Hızlı Yanıt Butonları */}
              <div className="bg-white border-t border-slate-100 p-2 flex gap-2 overflow-x-auto whitespace-nowrap">
                <button onClick={() => handleQuickReply('Yoklama saatleri')} className="bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-100 px-3 py-1.5 rounded-full text-[11px] font-bold transition">Yoklamalar</button>
                <button onClick={() => handleQuickReply('İzin nasıl alınır?')} className="bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-100 px-3 py-1.5 rounded-full text-[11px] font-bold transition">İzin Alma</button>
                <button onClick={() => handleQuickReply('Şifremi unuttum')} className="bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-100 px-3 py-1.5 rounded-full text-[11px] font-bold transition">Şifre İşlemleri</button>
              </div>

              {/* Mesaj Yazma Alanı */}
              <form onSubmit={handleSend} className="bg-white border-t border-slate-200 p-3 flex gap-2">
                <input 
                  type="text" 
                  placeholder="Bir soru sorun..." 
                  value={inputText} 
                  onChange={(e) => setInputText(e.target.value)}
                  className="flex-1 p-2 bg-slate-100 border-none rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-rose-500 transition"
                />
                <button type="submit" disabled={!inputText.trim()} className="bg-rose-600 hover:bg-rose-700 disabled:bg-slate-300 text-white w-10 h-10 rounded-xl flex items-center justify-center font-bold transition shadow-sm">
                  ➤
                </button>
              </form>
            </>
          )}
        </div>
      )}

      {/* YÜZEN CHAT BUTONU (LALE İKONU) */}
      <button 
        onClick={toggleChat} 
        className={`${isOpen ? 'bg-slate-800 hover:bg-slate-900' : 'bg-gradient-to-br from-rose-500 to-[#006bb6] hover:from-rose-600 hover:to-[#005694]'} text-white w-16 h-16 rounded-full flex items-center justify-center shadow-2xl transition transform hover:scale-105 active:scale-95 ml-auto`}
      >
        {isOpen ? (
          <span className="text-2xl font-bold">&times;</span>
        ) : (
          /* Minimalist Çizgi Lale (Tulip) İkonu */
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8">
            <path d="M12 22v-7" />
            <path d="M12 15C8 15 5 12 5 8c0-2 1-4 3-5 1 2 2 4 4 4 2 0 3-2 4-4 2 1 3 3 3 5 0 4-3 7-7 7z" />
            <path d="M8 22s-2-2-2-4 1-3 2-3" />
            <path d="M16 22s2-2 2-4-1-3-2-3" />
          </svg>
        )}
      </button>
    </div>
  );
}