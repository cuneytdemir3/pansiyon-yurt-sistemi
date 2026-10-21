// app/veli/login/page.tsx
'use client';

import React, { useState } from 'react';
import { Send, ShieldCheck, Phone, CheckCircle, ArrowRight } from 'lucide-react';

export default function VeliLoginPage() {
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [debugHint, setDebugHint] = useState('');

  // 1. Adım: Telefon Numarasına Kod Gönder
  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.length < 10) {
      setErrorMsg('Lütfen geçerli bir telefon numarası girin.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const res = await fetch('/api/auth/otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      const data = await res.json();

      if (data.success) {
        setStep('otp');
        setSuccessMsg('Tek kullanımlık doğrulama kodunuz WhatsApp üzerinden gönderildi.');
        if (data.debugCode) setDebugHint(data.debugCode); // Test kolaylığı
        
        // İsteğe bağlı: Velinin WhatsApp'ını otomatik aç
        if (data.whatsappUrl) {
          // window.open(data.whatsappUrl, '_blank');
        }
      } else {
        setErrorMsg(data.message || 'Kod gönderilemedi.');
      }
    } catch {
      setErrorMsg('Sunucu bağlantı hatası oluştu.');
    } finally {
      setLoading(false);
    }
  };

  // 2. Adım: Kodu Doğrula ve Giriş Yap
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpCode || otpCode.length !== 6) {
      setErrorMsg('Lütfen WhatsApp’a gelen 6 haneli kodu eksiksiz girin.');
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
      setErrorMsg('Doğrulama sırasında hata oluştu.');
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
          <p className="text-xs md:text-sm text-gray-500">
            Şifre derdi yok! Numaranıza gönderilecek tek kullanımlık kod ile güvenle giriş yapın.
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs font-medium">
            {errorMsg}
          </div>
        )}

        {successMsg && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-xs font-medium flex items-center gap-2">
            <CheckCircle className="w-4 h-4 shrink-0" /> {successMsg}
          </div>
        )}

        {/* Test ortamı kolaylığı için ekranda kodu gösteren ipucu */}
        {debugHint && (
          <div className="p-3 bg-blue-50 border border-blue-200 text-blue-800 rounded-xl text-xs text-center font-mono">
            💡 [Test Modu] WhatsApp Kodunuz: <strong>{debugHint}</strong>
          </div>
        )}

        {step === 'phone' ? (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Kayıtlı Cep Telefonu Numaranız</label>
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
              {loading ? 'Gönderiliyor...' : 'WhatsApp ile Kod Gönder'} <ArrowRight className="w-4 h-4" />
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
5              disabled={loading}
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