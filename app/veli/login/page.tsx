'use client';

import React, { useState } from 'react';
import { ShieldCheck, Phone, CheckCircle, ArrowRight } from 'lucide-react';

export default function VeliLoginPage() {
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [fallbackHint, setFallbackHint] = useState('');

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.replace(/\D/g, '').length < 10) {
      setErrorMsg('Lütfen geçerli bir telefon numarası girin (Örn: 0555 111 22 33).');
      return;
    }
    setLoading(true);
    setErrorMsg('');
    setFallbackHint('');

    try {
      const res = await fetch('/api/auth/otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      const data = await res.json();

      if (data.success) {
        let delivered = data.sentViaBot;

        // Eğer sunucu doğrudan bota ulaşamadıysa (Vercel'deyse), bilgisayardaki yerel bota tarayıcıdan istek at
        if (!delivered && data.otpCode) {
          try {
            const localBotRes = await fetch('http://localhost:3001/send-otp', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ phone, code: data.otpCode }),
            });
            const localBotData = await localBotRes.json();
            if (localBotData.success) {
              delivered = true;
            }
          } catch {
            // Yerel bot kapalıysa
          }
        }

        setStep('otp');
        if (delivered) {
          setSuccessMsg('Tek kullanımlık şifreniz WhatsApp numaranıza başarıyla gönderildi!');
        } else {
          setSuccessMsg('Doğrulama kodu oluşturuldu (WhatsApp Botu kapalı olduğu için yedek mod aktif).');
          setFallbackHint(data.otpCode);
        }
      } else {
        setErrorMsg(data.message || 'Kod gönderilemedi.');
      }
    } catch {
      setErrorMsg('Bağlantı hatası oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpCode || otpCode.length !== 6) {
      setErrorMsg('Lütfen 6 haneli kodu eksiksiz girin.');
      return;
    }
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await fetch('/api/auth/otp', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, code: otpCode }),
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('token', data.token);
        document.cookie = `token=${data.token}; path=/; max-age=604800;`;
        window.location.href = '/veli';
      } else {
        setErrorMsg(data.message || 'Doğrulama başarısız.');
      }
    } catch {
      setErrorMsg('Hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 max-w-md w-full p-6 md:p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl mx-auto flex items-center justify-center font-bold">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Veli Portalı WhatsApp Girişi</h1>
          <p className="text-xs md:text-sm text-gray-500">WhatsApp üzerinden gelen tek kullanımlık kod ile şifresiz giriş yapın.</p>
        </div>

        {errorMsg && <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs font-medium">{errorMsg}</div>}
        {successMsg && <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-xs font-medium">{successMsg}</div>}
        {fallbackHint && (
          <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-xs text-center font-mono">
            ⚠️ [Bot Kapalı - Yedek Kod]: <strong>{fallbackHint}</strong>
          </div>
        )}

        {step === 'phone' ? (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">WhatsApp Cep Telefonu Numaranız</label>
              <div className="relative">
                <Phone className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  required
                  placeholder="0555 000 00 00"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-semibold text-sm shadow-sm transition-all cursor-pointer"
            >
              {loading ? 'WhatsApp Mesajı Gönderiliyor...' : 'WhatsApp ile Kod Gönder'} <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">WhatsApp'a Gelen 6 Haneli Kod</label>
              <input
                type="text"
                maxLength={6}
                required
                placeholder="123456"
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value)}
                className="w-full text-center tracking-widest text-xl font-bold py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-semibold text-sm shadow-sm transition-all cursor-pointer"
            >
              {loading ? 'Doğrulanıyor...' : 'Giriş Yap'} <CheckCircle className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setStep('phone')}
              className="w-full text-center text-xs text-gray-500 hover:text-gray-800 underline pt-2"
            >
              Numarayı değiştir / Kodu tekrar gönder
            </button>
          </form>
        )}
      </div>
    </div>
  );
}