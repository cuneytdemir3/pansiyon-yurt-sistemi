'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Shield, UserCheck, Users, Lock, LogIn, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const [role, setRole] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');
  const [identity, setIdentity] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role, identity, password })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        if (role === 'veli') router.push('/veli');
        else if (role === 'belletmen') router.push('/belletmen');
        else if (role === 'yonetici') router.push('/yonetici');
      } else {
        setError(data.message || 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.');
      }
    } catch (err) {
      setError('Sunucu bağlantı hatası oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-blue-900 via-indigo-900 to-slate-900">
      <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-md p-8 border border-white/20">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-600 text-white mb-4 shadow-lg shadow-blue-500/30">
            <Shield className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">MEB Pansiyon Takip</h1>
          <p className="text-sm text-slate-600 mt-1">T.C. Millî Eğitim Bakanlığı Standart Otomasyonu</p>
        </div>

        <div className="grid grid-cols-3 gap-2 mb-6">
          <button
            type="button"
            onClick={() => setRole('veli')}
            className={`flex flex-col items-center p-3 rounded-xl border text-xs font-medium transition-all ${
              role === 'veli'
                ? 'bg-blue-600 text-white border-blue-600 shadow-md'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <Users className="w-5 h-5 mb-1" />
            Veli Portal
          </button>
          <button
            type="button"
            onClick={() => setRole('belletmen')}
            className={`flex flex-col items-center p-3 rounded-xl border text-xs font-medium transition-all ${
              role === 'belletmen'
                ? 'bg-blue-600 text-white border-blue-600 shadow-md'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <UserCheck className="w-5 h-5 mb-1" />
            Belletmen
          </button>
          <button
            type="button"
            onClick={() => setRole('yonetici')}
            className={`flex flex-col items-center p-3 rounded-xl border text-xs font-medium transition-all ${
              role === 'yonetici'
                ? 'bg-blue-600 text-white border-blue-600 shadow-md'
                : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <Shield className="w-5 h-5 mb-1" />
            Yönetici
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
              {role === 'veli' ? 'Öğrenci T.C. No / Veli Telefon' : 'T.C. No / Kullanıcı Adı / Ad Soyad'}
            </label>
            <input
              type="text"
              required
              value={identity}
              onChange={(e) => setIdentity(e.target.value)}
              placeholder={role === 'veli' ? 'Örn: 12345678901 veya 0535...' : 'Örn: mustafa.demir'}
              className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-900"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
              Şifre / PIN
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:outline-none text-slate-900"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg shadow-blue-600/30 transition-all flex items-center justify-center space-x-2"
          >
            {loading ? (
              <span>Giriş Yapılıyor...</span>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                <span>Sisteme Giriş Yap</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-100 text-center text-xs text-slate-500 flex items-center justify-center space-x-1">
          <Sparkles className="w-4 h-4 text-amber-500" />
          <span>Gemini AI Destekli MEB Pansiyon Asistanı Aktif</span>
        </div>
      </div>
    </main>
  );
}