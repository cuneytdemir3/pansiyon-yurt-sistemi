import os
import re
import subprocess
import sys
import time
import urllib.request

def write_file(filepath, content):
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"[DOSYA GÜNCELLENDİ] {filepath}")

def kill_old_processes():
    print("🧹 Açık kalan eski Node.js ve Tünel işlemleri temizleniyor...")
    subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, capture_output=True)
    time.sleep(1)

def ensure_cloudflared():
    exe_name = "cloudflared.exe"
    if not os.path.exists(exe_name):
        print("🌐 cloudflared.exe indiriliyor...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        urllib.request.urlretrieve(url, exe_name)
        print("✅ cloudflared.exe hazır!")
    return exe_name

def start_tunnel_and_get_url():
    exe_name = ensure_cloudflared()
    log_file = "tunnel.log"
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except:
            pass

    print("🚀 WhatsApp Botu için Cloudflare HTTPS tüneli açılıyor...")
    os.system(f'start "CLOUDFLARE_HTTPS_TUNELI" /MIN cmd /c "{exe_name} tunnel --url http://127.0.0.1:3001 > {log_file} 2>&1"')

    tunnel_url = None
    for _ in range(30):
        time.sleep(1)
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", text)
                if match:
                    tunnel_url = match.group(0)
                    break

    return tunnel_url

def run_command(command, description):
    print(f"\n[İŞLEM] {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[UYARI / HATA] {description}:")
        print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

# -------------------------------------------------------------------------
# 1. VELİ PORTALI SAYFASI (/veli - Güvenli Çıkış Butonu Eklendi)
# -------------------------------------------------------------------------
VELI_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import { ShieldCheck, Calendar, Clock, Send, LogOut } from 'lucide-react';

export default function VeliPortalPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [leaves, setLeaves] = useState<any[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<string>('1');
  const [tip, setTip] = useState('Ev İzni (Hafta Sonu)');
  const [baslangic, setBaslangic] = useState('2026-10-24');
  const [bitis, setBitis] = useState('2026-10-26');
  const [aciklama, setAciklama] = useState('');
  const [veliTel, setVeliTel] = useState('05416571469');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  const fetchStore = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        setStudents(data.store.students);
        setLeaves(data.store.leaves);
      }
    } catch {}
  };

  useEffect(() => {
    fetchStore();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    document.cookie = 'token=; path=/; max-age=0;';
    window.location.href = '/veli/login';
  };

  const currentStudent = students.find((s) => s.id === selectedStudentId) || students[0];
  const studentLeaves = leaves.filter((l) => l.studentId === (currentStudent?.id || '1'));

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg('');
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add_leave',
          studentId: currentStudent?.id || '1',
          tip,
          baslangic,
          bitis,
          aciklama,
          veliTel,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setStudents(data.store.students);
        setLeaves(data.store.leaves);
        setAciklama('');
        setMsg('✅ İzin talebiniz onaylandı! Nöbetçi belletmen ekranına Otomatik İzinli olarak yansıtıldı.');

        await fetch('/api/belletmen/bildirim', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            phone: veliTel,
            ogrenciAd: currentStudent?.name || 'Öğrenci',
            odaNo: currentStudent?.oda || '101',
            tarih: `${baslangic} / ${bitis}`,
            seans: 'izin_onay',
            veliTipi: `${tip} Onayı: ${aciklama || 'Veli İzin Talebi'}`
          }),
        });
      }
    } catch {
      setMsg('İzin kaydedilirken hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-4xl mx-auto space-y-6">

        {/* Üst Başlık ve Çıkış Butonu */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full">
                Prof. Dr. Mümtaz Turhan SBL Pansiyonu
              </span>
              <h1 className="text-lg md:text-xl font-extrabold text-slate-900 mt-0.5">Veli İzin & Öğrenci Takip Portalı</h1>
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <a href="/belletmen" className="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-2 rounded-xl hover:bg-blue-100">
              Belletmen Ekranı
            </a>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 px-4 py-2 rounded-xl shadow-xs transition-all cursor-pointer"
            >
              <LogOut className="w-4 h-4" /> Çıkış Yap
            </button>
          </div>
        </div>

        {/* Öğrenci Seçimi ve Durum Kartı */}
        {currentStudent && (
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-100 pb-4">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase">Öğrenci Seçimi</label>
                <select
                  value={selectedStudentId}
                  onChange={(e) => setSelectedStudentId(e.target.value)}
                  className="mt-1 text-sm font-bold text-slate-800 border border-slate-200 rounded-xl px-3 py-2 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} — Oda: {s.oda} ({s.sinif})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Anlık Pansiyon Durumu:</span>
                <span
                  className={`text-xs font-extrabold px-3 py-1 rounded-full ${
                    currentStudent.status === 'izinli'
                      ? 'bg-amber-100 text-amber-800'
                      : currentStudent.status === 'yok'
                      ? 'bg-rose-100 text-rose-700'
                      : 'bg-emerald-100 text-emerald-700'
                  }`}
                >
                  {currentStudent.status === 'izinli'
                    ? 'İzinli (Evci/Çarşı)'
                    : currentStudent.status === 'yok'
                    ? 'Yoklamada Bulunamadı'
                    : 'Pansiyonda (Mevcut)'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">Oda / Yatak</span>
                <strong className="text-slate-800 text-sm">Oda {currentStudent.oda} - Yatak {currentStudent.yatak}</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">Bulunduğu Kat</span>
                <strong className="text-slate-800 text-sm">{currentStudent.kat}. Kat</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">Sınıfı</span>
                <strong className="text-slate-800 text-sm">{currentStudent.sinif}</strong>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block">T.C. Kimlik</span>
                <strong className="text-slate-800 text-sm">{currentStudent.tc}</strong>
              </div>
            </div>
          </div>
        )}

        {msg && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold shadow-xs">
            {msg}
          </div>
        )}

        {/* Yeni Evci / Çarşı İzin Talep Formu */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-emerald-600" /> Yeni Evci / Çarşı İzin Talebi Oluştur
          </h2>
          <p className="text-xs text-slate-500">
            Oluşturduğunuz izinler anında nöbetçi belletmen yoklama ekranına <strong>Otomatik İzinli</strong> olarak düşer.
          </p>

          <form onSubmit={handleCreateLeave} className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">İzin Türü</label>
              <select
                value={tip}
                onChange={(e) => setTip(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-semibold bg-white"
              >
                <option value="Ev İzni">Hafta Sonu Evci İzni</option>
                <option value="Çarşı İzni">Günlük Çarşı / Kurs İzni</option>
                <option value="Sağlık / Rapor İzni">Sağlık / Hastane İzni</option>
                <option value="Özel Aile İzni">Özel Aile Ziyareti İzni</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Bilgilendirilecek WhatsApp No</label>
              <input
                type="text"
                value={veliTel}
                onChange={(e) => setVeliTel(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Başlangıç Tarihi</label>
              <input
                type="date"
                required
                value={baslangic}
                onChange={(e) => setBaslangic(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Dönüş (Bitiş) Tarihi</label>
              <input
                type="date"
                required
                value={bitis}
                onChange={(e) => setBitis(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold text-slate-700 mb-1">İzin Açıklaması / Gidilecek Adres Özeti</label>
              <input
                type="text"
                required
                placeholder="Örn: Hafta sonu aile ziyareti / Ev izni"
                value={aciklama}
                onChange={(e) => setAciklama(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-3 py-2.5 text-xs"
              />
            </div>

            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
              >
                <Send className="w-4 h-4" />
                {loading ? 'İzin Kaydediliyor ve WhatsApp Onayı Gönderiliyor...' : 'İzin Talebini Onayla ve Gönder'}
              </button>
            </div>
          </form>
        </div>

        {/* Geçmiş İzinler */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-600" /> Öğrencinin Aktif ve Geçmiş İzin Kayıtları
          </h3>
          {studentLeaves.length === 0 ? (
            <p className="text-xs text-slate-400">Henüz kayıtlı izin bulunmuyor.</p>
          ) : (
            <div className="space-y-2">
              {studentLeaves.map((l) => (
                <div key={l.id} className="p-3 bg-amber-50/70 border border-amber-200 rounded-xl flex flex-col sm:flex-row justify-between gap-2 text-xs">
                  <div>
                    <strong className="text-amber-900">{l.tip}:</strong>{' '}
                    <span className="text-amber-800">{l.baslangic} — {l.bitis} ({l.aciklama})</span>
                  </div>
                  <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-md self-start">
                    Onaylandı (Otomatik İzinli)
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
'''

# -------------------------------------------------------------------------
# 2. BELLETMEN EKRANI (/belletmen - Güvenli Çıkış Butonu Eklendi)
# -------------------------------------------------------------------------
BELLETMEN_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import { Calendar, FileText, CheckCircle2, Home, Send, Check, Loader2, Phone, Printer, X, LogOut } from 'lucide-react';

interface Student {
  id: string;
  name: string;
  kat: number;
  oda: string;
  yatak: string;
  tc: string;
  sinif?: string;
  status: 'var' | 'yok' | 'izinli';
  izinAciklama?: string;
  anneTel: string;
  babaTel: string;
}

export default function BelletmenPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [leaves, setLeaves] = useState<any[]>([]);
  const [selectedKat, setSelectedKat] = useState<number>(1);
  const [tarih, setTarih] = useState<string>('2026-10-24');
  const [seans, setSeans] = useState<'etut' | 'yat'>('etut');
  const [sendingKey, setSendingKey] = useState<string | null>(null);
  const [sentKeys, setSentKeys] = useState<Record<string, boolean>>({});
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [nobetDefteriAcik, setNobetDefteriAcik] = useState(false);
  const [belletmenAd, setBelletmenAd] = useState('Cüneyt DEMİR');
  const [nobetNotu, setNobetNotu] = useState('Pansiyon akşam etüt ve yat yoklamaları zamanında alındı. Katlarda asayiş ve düzen sağlandı.');

  const loadData = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        setStudents(data.store.students);
        setLeaves(data.store.leaves);
      }
    } catch {}
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    document.cookie = 'token=; path=/; max-age=0;';
    window.location.href = '/';
  };

  const getActiveLeaveText = (studentId: string) => {
    const found = leaves.find(
      (l) => l.studentId === studentId && l.baslangic <= tarih && l.bitis >= tarih
    );
    if (found) {
      return `${found.baslangic} — ${found.bitis} (${found.tip}: ${found.aciklama})`;
    }
    return undefined;
  };

  const enrichedStudents = students.map((s) => {
    const leaveTxt = getActiveLeaveText(s.id);
    if (leaveTxt) {
      return { ...s, status: 'izinli' as const, izinAciklama: leaveTxt };
    }
    return s;
  });

  const katStudents = enrichedStudents.filter((s) => s.kat === selectedKat);
  const katMevcudu = katStudents.length;
  const varSayisi = katStudents.filter((s) => s.status === 'var').length;
  const yokSayisi = katStudents.filter((s) => s.status === 'yok').length;
  const izinliSayisi = katStudents.filter((s) => s.status === 'izinli').length;

  const odalar = Array.from(new Set(katStudents.map((s) => s.oda))).sort();

  const syncAttendance = async (updated: Student[]) => {
    setStudents(updated);
    try {
      await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'update_attendance', students: updated }),
      });
    } catch {}
  };

  const handleStatusChange = (id: string, newStatus: 'var' | 'yok') => {
    const updated = students.map((s) => (s.id === id ? { ...s, status: newStatus } : s));
    syncAttendance(updated);
  };

  const handlePhoneChange = (id: string, field: 'anneTel' | 'babaTel', value: string) => {
    setStudents((prev) => prev.map((s) => (s.id === id ? { ...s, [field]: value } : s)));
  };

  const handleTumunuVarYap = () => {
    const updated = students.map((s) => {
      const hasLeave = getActiveLeaveText(s.id);
      if (s.kat === selectedKat && !hasLeave && s.status !== 'izinli') {
        return { ...s, status: 'var' as const };
      }
      return s;
    });
    syncAttendance(updated);
    setFeedback({ type: 'success', text: `✅ ${selectedKat}. Kattaki izinsiz tüm öğrenciler 'Var' olarak işaretlendi.` });
  };

  const handleSendWhatsApp = async (student: Student, veliTipi: 'Anne' | 'Baba', phone: string) => {
    const btnKey = `${student.id}-${veliTipi}`;
    setSendingKey(btnKey);
    setFeedback(null);

    try {
      const res = await fetch('/api/belletmen/bildirim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          ogrenciAd: student.name,
          odaNo: student.oda,
          tarih,
          seans,
          veliTipi
        })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        setSentKeys((prev) => ({ ...prev, [btnKey]: true }));
        setFeedback({ type: 'success', text: data.message });
      } else {
        setFeedback({
          type: 'error',
          text: data.message || 'WhatsApp mesajı iletilemedi. Botun açık olduğundan emin olun.'
        });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucuya bağlanırken hata oluştu.' });
    } finally {
      setSendingKey(null);
    }
  };

  const handleSaveAndPrintDutyLog = async () => {
    await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_duty_log',
        tarih,
        seans: seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)',
        belletmenAd,
        notlar: nobetNotu,
      }),
    });
    window.print();
  };

  const tumYoklar = enrichedStudents.filter((s) => s.status === 'yok');
  const tumIzinliler = enrichedStudents.filter((s) => s.status === 'izinli');

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-5xl mx-auto space-y-5 print:hidden">

        {/* Üst Bilgi, Navigasyon ve Çıkış Butonu */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <h1 className="text-lg md:text-xl font-bold text-slate-800">Nöbetçi Belletmen Yoklama & İzin Ekranı</h1>
              <p className="text-xs text-slate-500">
                Etüt (19:15) ve Yat Yoklaması (23:00) • Veli izin tarihleri arasında öğrenciler otomatik İzinli sayılır
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <a href="/veli" className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200 hover:bg-emerald-100">
                Veli Portalı
              </a>
              <a href="/admin" className="text-xs font-bold text-indigo-700 bg-indigo-50 px-3 py-2 rounded-xl border border-indigo-200 hover:bg-indigo-100">
                Yönetici Paneli
              </a>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 px-4 py-2 rounded-xl shadow-xs transition-all cursor-pointer"
              >
                <LogOut className="w-4 h-4" /> Çıkış Yap
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5">
                <Calendar className="w-4 h-4 text-blue-600" />
                <span className="text-xs font-medium text-slate-600">Yoklama Tarihi:</span>
                <input
                  type="date"
                  value={tarih}
                  onChange={(e) => setTarih(e.target.value)}
                  className="text-xs font-bold text-slate-800 bg-transparent focus:outline-none"
                />
              </div>

              <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
                <button
                  onClick={() => setSeans('etut')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    seans === 'etut' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'
                  }`}
                >
                  Etüt (19:15)
                </button>
                <button
                  onClick={() => setSeans('yat')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                    seans === 'yat' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'
                  }`}
                >
                  Yat (23:00)
                </button>
              </div>
            </div>

            <button
              onClick={() => setNobetDefteriAcik(true)}
              className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
            >
              <FileText className="w-4 h-4" /> Resmî Nöbet Defteri & PDF Çıktı
            </button>
          </div>
        </div>

        {/* Bildirim Durum Mesajı */}
        {feedback && (
          <div
            className={`p-4 rounded-2xl border text-xs font-bold flex items-center justify-between shadow-sm ${
              feedback.type === 'success'
                ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                : 'bg-rose-50 border-rose-300 text-rose-800'
            }`}
          >
            <span>{feedback.text}</span>
            <button onClick={() => setFeedback(null)} className="text-xs underline ml-4">Kapat</button>
          </div>
        )}

        {/* Kat Seçimi ve Tümünü Var Yap */}
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {[1, 2, 3].map((kat) => (
              <button
                key={kat}
                onClick={() => setSelectedKat(kat)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  selectedKat === kat
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {kat}. Kat
              </button>
            ))}
          </div>

          <button
            onClick={handleTumunuVarYap}
            className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4" /> Tümünü Var Yap
          </button>
        </div>

        {/* Özet Kartları */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div className="text-xs text-slate-500">Kat Mevcudu</div>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{katMevcudu}</div>
          </div>
          <div className="bg-emerald-50/70 p-4 rounded-2xl border border-emerald-200 shadow-sm">
            <div className="text-xs text-emerald-700 font-medium">Var</div>
            <div className="text-xl font-extrabold text-emerald-700 mt-1">{varSayisi}</div>
          </div>
          <div className="bg-rose-50/70 p-4 rounded-2xl border border-rose-200 shadow-sm">
            <div className="text-xs text-rose-700 font-medium">Yok</div>
            <div className="text-xl font-extrabold text-rose-700 mt-1">{yokSayisi}</div>
          </div>
          <div className="bg-amber-50/70 p-4 rounded-2xl border border-amber-200 shadow-sm">
            <div className="text-xs text-amber-700 font-medium">Veli İzinli (Otomatik)</div>
            <div className="text-xl font-extrabold text-amber-700 mt-1">{izinliSayisi}</div>
          </div>
        </div>

        {/* Odalar ve Öğrenci Kartları */}
        <div className="space-y-5">
          {odalar.map((odaNo) => {
            const odaOgrencileri = katStudents.filter((s) => s.oda === odaNo);
            return (
              <div key={odaNo} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="bg-slate-900 text-white px-5 py-3 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold">
                    <Home className="w-4 h-4 text-blue-400" /> Oda No: {odaNo}
                  </div>
                  <span className="text-[11px] bg-slate-800 px-2.5 py-0.5 rounded-full text-slate-300">
                    {odaOgrencileri.length} Öğrenci
                  </span>
                </div>

                <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {odaOgrencileri.map((student) => {
                    const anneKey = `${student.id}-Anne`;
                    const babaKey = `${student.id}-Baba`;

                    return (
                      <div
                        key={student.id}
                        className="border border-slate-200 rounded-xl p-4 space-y-3 bg-white shadow-xs"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-bold text-slate-900 text-sm">{student.name}</h3>
                            <p className="text-[11px] text-slate-500 mt-0.5">
                              Oda: {student.oda} | Yatak: {student.yatak} | T.C.: {student.tc}
                            </p>
                          </div>

                          <span
                            className={`text-[11px] font-bold px-2.5 py-0.5 rounded-md ${
                              student.status === 'izinli'
                                ? 'bg-amber-100 text-amber-800'
                                : student.status === 'yok'
                                ? 'bg-rose-100 text-rose-700'
                                : 'bg-emerald-100 text-emerald-700'
                            }`}
                          >
                            {student.status === 'izinli' ? 'İzinli' : student.status === 'yok' ? 'Yok' : 'Var'}
                          </span>
                        </div>

                        {student.status === 'izinli' ? (
                          <div className="p-2.5 bg-amber-50 border border-amber-200 rounded-lg text-[11px] text-amber-900 font-medium">
                            <strong>Otomatik İzinli:</strong> {student.izinAciklama || 'Veli İzni Aktif'}
                          </div>
                        ) : (
                          <>
                            <div className="flex items-center gap-2 pt-1">
                              <button
                                onClick={() => handleStatusChange(student.id, 'var')}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                                  student.status === 'var'
                                    ? 'bg-emerald-600 text-white shadow-xs'
                                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                                }`}
                              >
                                Var
                              </button>
                              <button
                                onClick={() => handleStatusChange(student.id, 'yok')}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                                  student.status === 'yok'
                                    ? 'bg-red-600 text-white shadow-xs'
                                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                                }`}
                              >
                                Yok
                              </button>
                            </div>

                            {student.status === 'yok' && (
                              <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-xl space-y-2.5 mt-2">
                                <div className="text-[11px] font-bold text-rose-800">
                                  WhatsApp Yoklama Bildirimi Gönder:
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                                  <div className="flex items-center bg-white border border-rose-200 rounded-lg px-2 py-1">
                                    <Phone className="w-3 h-3 text-slate-400 mr-1" />
                                    <span className="text-slate-500 mr-1">Anne:</span>
                                    <input
                                      type="text"
                                      value={student.anneTel}
                                      onChange={(e) => handlePhoneChange(student.id, 'anneTel', e.target.value)}
                                      className="w-full font-mono text-slate-800 focus:outline-none"
                                    />
                                  </div>
                                  <div className="flex items-center bg-white border border-rose-200 rounded-lg px-2 py-1">
                                    <Phone className="w-3 h-3 text-slate-400 mr-1" />
                                    <span className="text-slate-500 mr-1">Baba:</span>
                                    <input
                                      type="text"
                                      value={student.babaTel}
                                      onChange={(e) => handlePhoneChange(student.id, 'babaTel', e.target.value)}
                                      className="w-full font-mono text-slate-800 focus:outline-none"
                                    />
                                  </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                  <button
                                    type="button"
                                    disabled={sendingKey === anneKey}
                                    onClick={() => handleSendWhatsApp(student, 'Anne', student.anneTel)}
                                    className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white py-2 px-3 rounded-lg text-[11px] font-bold transition-all cursor-pointer shadow-xs"
                                  >
                                    {sendingKey === anneKey ? (
                                      <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Gönderiliyor...</>
                                    ) : sentKeys[anneKey] ? (
                                      <><Check className="w-3.5 h-3.5" /> Anneye Gönderildi</>
                                    ) : (
                                      <><Send className="w-3.5 h-3.5" /> Anneye Mesaj At ({student.anneTel})</>
                                    )}
                                  </button>

                                  <button
                                    type="button"
                                    disabled={sendingKey === babaKey}
                                    onClick={() => handleSendWhatsApp(student, 'Baba', student.babaTel)}
                                    className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white py-2 px-3 rounded-lg text-[11px] font-bold transition-all cursor-pointer shadow-xs"
                                  >
                                    {sendingKey === babaKey ? (
                                      <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Gönderiliyor...</>
                                    ) : sentKeys[babaKey] ? (
                                      <><Check className="w-3.5 h-3.5" /> Babaya Gönderildi</>
                                    ) : (
                                      <><Send className="w-3.5 h-3.5" /> Babaya Mesaj At ({student.babaTel})</>
                                    )}
                                  </button>
                                </div>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* RESMÎ MEB NÖBET DEFTERİ MODAL VE YAZDIRMA EKRANI */}
      {nobetDefteriAcik && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto print:static print:bg-white print:p-0">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 md:p-8 space-y-6 shadow-2xl print:shadow-none print:rounded-none">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-4 print:hidden">
              <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600" /> Resmî MEB Pansiyon Nöbet Defteri ve PDF Raporu
              </h2>
              <button onClick={() => setNobetDefteriAcik(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 print:hidden">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Nöbetçi Belletmen Öğretmen</label>
                <input
                  type="text"
                  value={belletmenAd}
                  onChange={(e) => setBelletmenAd(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-bold bg-white"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Yoklama Tarihi / Seans</label>
                <input
                  type="text"
                  readOnly
                  value={`${tarih} — ${seans === 'etut' ? '19:15 Etüt Yoklaması' : '23:00 Yat Yoklaması'}`}
                  className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs bg-slate-100"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 mb-1">Nöbet Vukuat / Revir / Olay Notları</label>
                <textarea
                  rows={3}
                  value={nobetNotu}
                  onChange={(e) => setNobetNotu(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-3 text-xs bg-white"
                />
              </div>
            </div>

            <div className="border border-slate-300 p-6 rounded-xl space-y-5 text-slate-900 print:border-none print:p-0">
              <div className="text-center space-y-1 border-b-2 border-slate-800 pb-4">
                <p className="text-xs font-bold uppercase">T.C.</p>
                <p className="text-xs font-bold uppercase">MİLLÎ EĞİTİM BAKANLIĞI</p>
                <p className="text-sm font-extrabold uppercase">Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Müdürlüğü</p>
                <p className="text-xs font-semibold uppercase text-slate-700">Öğrenci Pansiyonu Günlük Nöbet ve Yoklama Tutanağı</p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs border border-slate-300 p-3 rounded-lg">
                <div><strong>Tarih:</strong> {tarih}</div>
                <div><strong>Seans:</strong> {seans === 'etut' ? '19:15 Etüt' : '23:00 Yat'}</div>
                <div><strong>Toplam Kayıtlı:</strong> {enrichedStudents.length}</div>
                <div><strong>Mevcut (Var):</strong> {enrichedStudents.filter(s => s.status === 'var').length}</div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-2 border-l-4 border-rose-600">
                  1. Yoklamada Bulunmayan (Yok / Habersiz) Öğrenciler ({tumYoklar.length})
                </h4>
                {tumYoklar.length === 0 ? (
                  <p className="text-xs text-slate-600 italic pl-2">Yoklamada habersiz eksik öğrenci bulunmamaktadır.</p>
                ) : (
                  <table className="w-full text-xs border-collapse border border-slate-300">
                    <thead>
                      <tr className="bg-slate-100">
                        <th className="border border-slate-300 p-1.5 text-left">Ad Soyad</th>
                        <th className="border border-slate-300 p-1.5 text-left">Oda / Yatak</th>
                        <th className="border border-slate-300 p-1.5 text-left">T.C. Kimlik</th>
                        <th className="border border-slate-300 p-1.5 text-left">Veli İletişim</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tumYoklar.map((s) => (
                        <tr key={s.id}>
                          <td className="border border-slate-300 p-1.5 font-bold">{s.name}</td>
                          <td className="border border-slate-300 p-1.5">Oda {s.oda} ({s.yatak})</td>
                          <td className="border border-slate-300 p-1.5">{s.tc}</td>
                          <td className="border border-slate-300 p-1.5">{s.anneTel}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-2 border-l-4 border-amber-500">
                  2. İzinli (Evci / Çarşı / Raporlu) Öğrenciler ({tumIzinliler.length})
                </h4>
                {tumIzinliler.length === 0 ? (
                  <p className="text-xs text-slate-600 italic pl-2">İzinli öğrenci bulunmamaktadır.</p>
                ) : (
                  <table className="w-full text-xs border-collapse border border-slate-300">
                    <thead>
                      <tr className="bg-slate-100">
                        <th className="border border-slate-300 p-1.5 text-left">Ad Soyad</th>
                        <th className="border border-slate-300 p-1.5 text-left">Oda</th>
                        <th className="border border-slate-300 p-1.5 text-left">İzin Detayı</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tumIzinliler.map((s) => (
                        <tr key={s.id}>
                          <td className="border border-slate-300 p-1.5 font-bold">{s.name}</td>
                          <td className="border border-slate-300 p-1.5">Oda {s.oda}</td>
                          <td className="border border-slate-300 p-1.5">{s.izinAciklama || 'Veli İzni'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-2 border-l-4 border-indigo-600">
                  3. Nöbetçi Belletmen Günlük Vukuat ve Değerlendirme Notu
                </h4>
                <div className="p-3 border border-slate-300 rounded-lg text-xs min-h-[70px] whitespace-pre-wrap">
                  {nobetNotu}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-8 pt-8 text-center text-xs">
                <div>
                  <p className="font-bold">Nöbetçi Belletmen Öğretmen</p>
                  <p className="mt-1 text-slate-700">{belletmenAd}</p>
                  <p className="mt-6 text-slate-400">İmza</p>
                </div>
                <div>
                  <p className="font-bold">Pansiyondan Sorumlu Müdür Yardımcısı</p>
                  <p className="mt-1 text-slate-700">İdare Onayı</p>
                  <p className="mt-6 text-slate-400">İmza / Mühür</p>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 print:hidden">
              <button
                onClick={() => setNobetDefteriAcik(false)}
                className="px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-100 cursor-pointer"
              >
                Kapat
              </button>
              <button
                onClick={handleSaveAndPrintDutyLog}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold shadow-md cursor-pointer"
              >
                <Printer className="w-4 h-4" /> Kaydet ve Resmî PDF / Yazıcı Çıktısı Al
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
'''

def main():
    print("=========================================================")
    print("   VELİ VE BELLETMEN ÇIKIŞ BUTONU GÜNCELLEMESİ")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    write_file("app/veli/page.tsx", VELI_PAGE_TSX)
    write_file("app/belletmen/page.tsx", BELLETMEN_PAGE_TSX)

    # Bildirim API rotasını güncel tünel adresiyle tazele
    bildirim_api = f"""import {{ NextResponse }} from 'next/server';

const BOT_URLS = ['{tunnel_url}', 'http://127.0.0.1:3001'];

export async function POST(request: Request) {{
  try {{
    const {{ phone, ogrenciAd, odaNo, tarih, seans, veliTipi }} = await request.json();
    if (!phone) {{
      return NextResponse.json({{ success: false, message: 'Telefon numarası eksik.' }}, {{ status: 400 }});
    }}

    let customMessage = '';
    if (seans === 'izin_onay') {{
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz,\\nÖğrenciniz *${{ogrenciAd}}* (Oda: ${{odaNo}}) için *${{tarih}}* tarihli izin talebiniz (*${{veliTipi}}*) onaylanmış ve nöbetçi belletmen yoklama sistemine *Otomatik İzinli* olarak işlenmiştir.`;
    }} else {{
      const seansMetni = seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)';
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz (${{veliTipi || 'Veli'}}),\\nÖğrenciniz *${{ogrenciAd}}* (Oda: ${{odaNo}}), *${{tarih}}* tarihli *${{seansMetni}}* yoklamasında pansiyonda *BULUNAMAMIŞTIR (YOK)*.\\n\\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;
    }}

    let lastError = 'WhatsApp Botuna ulaşılamadı.';
    for (const botUrl of BOT_URLS) {{
      try {{
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(`${{botUrl}}/send-otp`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ phone, customMessage }}),
          signal: controller.signal
        }});
        clearTimeout(tid);

        const data = await res.json();
        if (res.ok && data.success) {{
          return NextResponse.json({{
            success: true,
            message: `✅ ${{ogrenciAd}} velisine (${{phone}}) WhatsApp bildirimi başarıyla gönderildi!`
          }});
        }} else {{
          lastError = data.message || lastError;
        }}
      }} catch (e) {{}}
    }}

    return NextResponse.json({{ success: false, message: lastError }}, {{ status: 500 }});
  }} catch (err: any) {{
    return NextResponse.json({{ success: false, message: err.message }}, {{ status: 500 }});
  }}
}}
"""
    write_file("app/api/belletmen/bildirim/route.ts", bildirim_api)

    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Veli ve Belletmen panellerine guvenli Cikis Yap butonu eklendi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 ÇIKIŞ BUTONLARI EKLENDİ VE CANLIYA GÖNDERİLDİ!")
    print("=========================================================")

if __name__ == "__main__":
    main()