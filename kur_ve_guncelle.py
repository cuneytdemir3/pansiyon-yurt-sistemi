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
    print("🧹 Açık kalan Node.js ve Tünel işlemleri temizleniyor...")
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
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False
    else:
        print(f"[BAŞARILI] {description} tamamlandı.")
        return True

# -------------------------------------------------------------------------
# ADMİN PANELİ (.xlsx / .xls / .csv Dosya Yükleme ve Şablon İndirme)
# -------------------------------------------------------------------------
ADMIN_PAGE_TSX = r''''use client';

import React, { useState, useEffect, useRef } from 'react';
import * as XLSX from 'xlsx';
import {
  Users, Upload, Plus, Trash2, Shield, FileSpreadsheet, LogOut,
  KeyRound, Eye, EyeOff, Calendar, UserCheck, Wand2, Save,
  Activity, ShieldAlert, CheckCircle2, AlertTriangle, Info, Clock, X, Download, FolderUp
} from 'lucide-react';

interface Student { id: string; name: string; cinsiyet: string; tc: string; sinif: string; kat: number; oda: string; yatak: string; anneTel: string; babaTel: string; status: string; }
interface Belletmen { id: string; name: string; cinsiyet: string; brans: string; phone: string; password: string; }
interface MonthlyDutyDay { tarih: string; erkek1: string; erkek2: string; kadin1: string; kadin2: string; }
interface AuditLog { id: string; tarihSaat: string; kullanici: string; islem: string; detay: string; tur: string; }

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'belletmen' | 'nobet' | 'ogrenci' | 'loglar'>('ogrenci');

  const [students, setStudents] = useState<Student[]>([]);
  const [belletmenler, setBelletmenler] = useState<Belletmen[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<MonthlyDutyDay[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Dosya Input Referansları
  const studentFileRef = useRef<HTMLInputElement | null>(null);
  const belletmenFileRef = useRef<HTMLInputElement | null>(null);
  const nobetFileRef = useRef<HTMLInputElement | null>(null);

  // Tekil Belletmen State
  const [bName, setBName] = useState('');
  const [bCinsiyet, setBCinsiyet] = useState<'erkek' | 'kadin'>('erkek');
  const [bBrans, setBBrans] = useState('');
  const [bPhone, setBPhone] = useState('0541');
  const [bPassword, setBPassword] = useState('1234');
  const [belletmenCsv, setBelletmenCsv] = useState('Serhat AKAN, erkek, Matematik, 05411112233, 1453\nElif DEMİR, kadin, Edebiyat, 05412223344, 2026');

  const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({});
  const [editingPasswordId, setEditingPasswordId] = useState<string | null>(null);
  const [newPasswordVal, setNewPasswordVal] = useState('');

  // Aylık Nöbet State
  const [nobetAySecim, setNobetAySecim] = useState('2026-10');
  const [nTarih, setNTarih] = useState('2026-10-29');
  const [nErkek1, setNErkek1] = useState('Cüneyt DEMİR');
  const [nErkek2, setNErkek2] = useState('Ali BEY');
  const [nKadin1, setNKadin1] = useState('Ayşenur KAYA');
  const [nKadin2, setNKadin2] = useState('Fatma YILMAZ');
  const [nobetCsv, setNobetCsv] = useState('2026-10-29, Cüneyt DEMİR, Ali BEY, Ayşenur KAYA, Fatma YILMAZ');

  // Tekil Öğrenci State
  const [sName, setSName] = useState('');
  const [sCinsiyet, setSCinsiyet] = useState<'erkek' | 'kiz'>('erkek');
  const [sTc, setSTc] = useState('');
  const [sSinif, setSSinif] = useState('9-A');
  const [sKat, setSKat] = useState(1);
  const [sOda, setSOda] = useState('101');
  const [sYatak, setSYatak] = useState('A');
  const [sAnneTel, setSAnneTel] = useState('05416571469');
  const [sBabaTel, setSBabaTel] = useState('05416571469');
  const [studentCsv, setStudentCsv] = useState('Ali Veli, erkek, 12345678910, 9-B, 1, 103, A, 05416571469, 05416571469');

  const syncFromStore = (store: any) => {
    if (store.students) setStudents(store.students);
    if (store.belletmenler) setBelletmenler(store.belletmenler);
    if (store.aylikNobetler) setAylikNobetler(store.aylikNobetler);
    if (store.auditLogs) setAuditLogs(store.auditLogs);
  };

  const fetchAll = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) syncFromStore(data.store);
    } catch {}
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 8000);
    return () => clearInterval(interval);
  }, []);

  // =========================================================================
  // 1) GERÇEK EXCEL (.XLSX / .XLS / .CSV) DOSYASI OKUMA VE YÜKLEME FONKSİYONLARI
  // =========================================================================

  // ÖĞRENCİ EXCEL DOSYASI YÜKLEME
  const handleStudentExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setMsg('Excel dosyası okunuyor...');

    try {
      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: 'array' });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const rawRows: any[][] = XLSX.utils.sheet_to_json(firstSheet, { header: 1, defval: '' });

      // Başlık satırını atla (İlk hücrede "Ad" veya "İsim" geçiyorsa)
      const dataRows = rawRows.filter((r, idx) => {
        if (!r || r.length === 0 || !String(r[0] || '').trim()) return false;
        const firstCell = String(r[0]).toLowerCase();
        if (idx === 0 && (firstCell.includes('ad') || firstCell.includes('isim') || firstCell.includes('öğrenci'))) return false;
        return true;
      });

      const formattedRows = dataRows.map((p) => ({
        name: String(p[0] || '').trim(),
        cinsiyet: String(p[1] || 'erkek').trim(),
        tc: String(p[2] || '10000000000').trim(),
        sinif: String(p[3] || '9-A').trim(),
        kat: Number(p[4]) || 1,
        oda: String(p[5] || '101').trim(),
        yatak: String(p[6] || 'A').trim(),
        anneTel: String(p[7] || '05416571469').trim(),
        babaTel: String(p[8] || '05416571469').trim(),
      }));

      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'bulk_import', rows: formattedRows }),
      });
      const data = await res.json();
      if (data.success) {
        syncFromStore(data.store);
        setMsg(`📁 "${file.name}" dosyasından ${formattedRows.length} öğrenci başarıyla yüklendi!`);
      }
    } catch {
      setMsg('Excel dosyası okunurken hata oluştu.');
    } finally {
      setLoading(false);
      if (studentFileRef.current) studentFileRef.current.value = '';
    }
  };

  // BELLETMEN EXCEL DOSYASI YÜKLEME
  const handleBelletmenExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setMsg('Belletmen Excel dosyası okunuyor...');

    try {
      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: 'array' });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const rawRows: any[][] = XLSX.utils.sheet_to_json(firstSheet, { header: 1, defval: '' });

      const dataRows = rawRows.filter((r, idx) => {
        if (!r || r.length === 0 || !String(r[0] || '').trim()) return false;
        const firstCell = String(r[0]).toLowerCase();
        if (idx === 0 && (firstCell.includes('ad') || firstCell.includes('isim') || firstCell.includes('belletmen'))) return false;
        return true;
      });

      const formattedRows = dataRows.map((p) => ({
        name: String(p[0] || '').trim(),
        cinsiyet: String(p[1] || 'erkek').trim(),
        brans: String(p[2] || 'Öğretmen').trim(),
        phone: String(p[3] || '05416571469').trim(),
        password: String(p[4] || '1234').trim(),
      }));

      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'bulk_add_belletmen', rows: formattedRows }),
      });
      const data = await res.json();
      if (data.success) {
        syncFromStore(data.store);
        setMsg(`📁 "${file.name}" dosyasından ${formattedRows.length} belletmen öğretmen başarıyla yüklendi!`);
      }
    } catch {
      setMsg('Excel dosyası okunurken hata oluştu.');
    } finally {
      setLoading(false);
      if (belletmenFileRef.current) belletmenFileRef.current.value = '';
    }
  };

  // AYLIK NÖBET EXCEL DOSYASI YÜKLEME
  const handleNobetExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);

    try {
      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: 'array' });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const rawRows: any[][] = XLSX.utils.sheet_to_json(firstSheet, { header: 1, defval: '' });

      const dataRows = rawRows.filter((r, idx) => {
        if (!r || r.length === 0 || !String(r[0] || '').trim()) return false;
        const firstCell = String(r[0]).toLowerCase();
        if (idx === 0 && firstCell.includes('tarih')) return false;
        return true;
      });

      const formattedRows = dataRows.map((p) => ({
        tarih: String(p[0] || '').trim(),
        erkek1: String(p[1] || '-').trim(),
        erkek2: String(p[2] || '-').trim(),
        kadin1: String(p[3] || '-').trim(),
        kadin2: String(p[4] || '-').trim(),
      }));

      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'bulk_monthly_duty', rows: formattedRows }),
      });
      const data = await res.json();
      if (data.success) {
        syncFromStore(data.store);
        setMsg(`📁 "${file.name}" dosyasından ${formattedRows.length} günlük nöbet listesi yüklendi!`);
      }
    } catch {
      setMsg('Nöbet Excel dosyası okunurken hata oluştu.');
    } finally {
      setLoading(false);
      if (nobetFileRef.current) nobetFileRef.current.value = '';
    }
  };

  // =========================================================================
  // 2) ÖRNEK EXCEL (.XLSX) ŞABLONU İNDİRME FONKSİYONLARI
  // =========================================================================
  const downloadStudentTemplate = () => {
    const ws = XLSX.utils.aoa_to_sheet([
      ['Ad Soyad', 'Cinsiyet (erkek/kiz)', 'TC Kimlik', 'Sınıf', 'Kat', 'Oda No', 'Yatak', 'Anne Telefon', 'Baba Telefon'],
      ['Emre Demir', 'erkek', '12345678920', '9-A', 1, '103', 'A', '05416571469', '05416571469'],
      ['Zeynep Kaya', 'kiz', '12345678921', '10-B', 1, 'K-102', 'B', '05416571469', '05416571469']
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Ogrenci_Listesi');
    XLSX.writeFile(wb, 'Ornek_Ogrenci_Yukleme_Sablonu.xlsx');
  };

  const downloadBelletmenTemplate = () => {
    const ws = XLSX.utils.aoa_to_sheet([
      ['Ad Soyad', 'Cinsiyet (erkek/kadin)', 'Branş', 'Telefon', 'Giriş Şifresi'],
      ['Serhat AKAN', 'erkek', 'Matematik', '05416571469', '1453'],
      ['Elif DEMİR', 'kadin', 'Türk Dili ve Edebiyatı', '05416571469', '2026']
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Belletmen_Listesi');
    XLSX.writeFile(wb, 'Ornek_Belletmen_Yukleme_Sablonu.xlsx');
  };

  const downloadNobetTemplate = () => {
    const ws = XLSX.utils.aoa_to_sheet([
      ['Tarih (YYYY-AA-GG)', '1. Erkek Belletmen', '2. Erkek Belletmen', '1. Kadın Belletmen', '2. Kadın Belletmen'],
      ['2026-10-29', 'Cüneyt DEMİR', 'Ali BEY', 'Ayşenur KAYA', 'Fatma YILMAZ'],
      ['2026-10-30', 'Furkan DEMİR', 'Hasan ÇELİK', 'Zeynep ŞAHİN', 'Merve AYDIN']
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Aylik_Nobet');
    XLSX.writeFile(wb, 'Ornek_Aylik_Nobet_Sablonu.xlsx');
  };

  // --- METİN KUTUSU AYRIŞTIRICI ---
  const parseExcelData = (text: string) => {
    const lines = text.split('\n').map((l) => l.trim()).filter(Boolean);
    return lines.map((line) => {
      const separator = line.includes('\t') ? '\t' : ',';
      return line.split(separator).map((x) => x.trim());
    });
  };

  // --- BELLETMEN İŞLEMLERİ ---
  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bName) return;
    setLoading(true);
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'add_belletmen', name: bName, cinsiyet: bCinsiyet, brans: bBrans, phone: bPhone, password: bPassword }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setBName(''); setBBrans(''); setMsg(data.message); }
    setLoading(false);
  };

  const handleBulkAddBelletmen = async () => {
    if (!belletmenCsv.trim()) return;
    setLoading(true);
    const parsed = parseExcelData(belletmenCsv);
    const rows = parsed.map(p => ({ name: p[0], cinsiyet: p[1] || 'erkek', brans: p[2] || 'Öğretmen', phone: p[3] || '05416571469', password: p[4] || '1234' }));
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'bulk_add_belletmen', rows }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setBelletmenCsv(''); setMsg(data.message); }
    setLoading(false);
  };

  const handleUpdatePassword = async (id: string) => {
    if (!newPasswordVal.trim()) return;
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'update_belletmen_password', id, newPassword: newPasswordVal }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setEditingPasswordId(null); setNewPasswordVal(''); setMsg(data.message); }
  };

  const handleDeleteBelletmen = async (id: string) => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'delete_belletmen', id }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  // --- AYLIK NÖBET İŞLEMLERİ ---
  const handleAddSingleDutyDay = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'add_or_update_monthly_duty', tarih: nTarih, erkek1: nErkek1, erkek2: nErkek2, kadin1: nKadin1, kadin2: nKadin2 }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
    setLoading(false);
  };

  const handleAutoGenerateMonth = async () => {
    setLoading(true);
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'auto_generate_month_duty', yearMonth: nobetAySecim }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
    setLoading(false);
  };

  const handleBulkMonthlyDuty = async () => {
    if (!nobetCsv.trim()) return;
    setLoading(true);
    const parsed = parseExcelData(nobetCsv);
    const rows = parsed.map(p => ({ tarih: p[0], erkek1: p[1] || '-', erkek2: p[2] || '-', kadin1: p[3] || '-', kadin2: p[4] || '-' }));
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'bulk_monthly_duty', rows }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setNobetCsv(''); setMsg(data.message); }
    setLoading(false);
  };

  const handleDeleteDutyDay = async (tarih: string) => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'delete_monthly_duty', tarih }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  // --- ÖĞRENCİ İŞLEMLERİ ---
  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sName) return;
    setLoading(true);
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'add_student', name: sName, cinsiyet: sCinsiyet, tc: sTc, sinif: sSinif, kat: sKat, oda: sOda, yatak: sYatak, anneTel: sAnneTel, babaTel: sBabaTel }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setSName(''); setSTc(''); setMsg(data.message); }
    setLoading(false);
  };

  const handleBulkImportStudents = async () => {
    if (!studentCsv.trim()) return;
    setLoading(true);
    const parsed = parseExcelData(studentCsv);
    const rows = parsed.map(p => ({ name: p[0], cinsiyet: p[1] || 'erkek', tc: p[2] || '10000000000', sinif: p[3] || '9-A', kat: Number(p[4]) || 1, oda: p[5] || '101', yatak: p[6] || 'A', anneTel: p[7] || '05416571469', babaTel: p[8] || '05416571469' }));
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'bulk_import', rows }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setStudentCsv(''); setMsg(data.message); }
    setLoading(false);
  };

  const handleDeleteStudent = async (id: string) => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'delete_student', id }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const handleClearLogs = async () => {
    const res = await fetch('/api/pansiyon', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'clear_audit_logs' }) });
    const data = await res.json();
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
  };

  const getBadgeColor = (tur: string) => {
    if (tur === 'basari') return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    if (tur === 'uyari') return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    if (tur === 'hata') return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
  };

  const getIcon = (tur: string) => {
    if (tur === 'basari') return <CheckCircle2 className="w-3.5 h-3.5" />;
    if (tur === 'uyari') return <AlertTriangle className="w-3.5 h-3.5" />;
    if (tur === 'hata') return <X className="w-3.5 h-3.5" />;
    return <Info className="w-3.5 h-3.5" />;
  };

  const erkekBelletmenList = belletmenler.filter((b) => b.cinsiyet === 'erkek');
  const kadinBelletmenList = belletmenler.filter((b) => b.cinsiyet === 'kadin');

  return (
    <div className="min-h-screen bg-slate-100 p-2.5 sm:p-6 pb-20">
      <div className="max-w-6xl mx-auto space-y-4 sm:space-y-6">

        {/* ÜST BAŞLIK */}
        <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold shrink-0">
              <Shield className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <div>
              <h1 className="text-base sm:text-xl font-extrabold text-slate-900">Pansiyon İdare & Yönetici Paneli</h1>
              <p className="text-[11px] sm:text-xs text-slate-500">
                Excel (.xlsx) Dosyası ile Öğrenci & Belletmen Yükleme • Aylık Nöbet • Güvenlik Günlüğü
              </p>
            </div>
          </div>
          <div className="grid grid-cols-3 sm:flex items-center gap-2 w-full sm:w-auto">
            <a href="/belletmen" className="text-center text-[11px] sm:text-xs font-bold text-blue-700 bg-blue-50 py-2.5 px-3 rounded-xl border border-blue-200">Belletmen</a>
            <a href="/veli" className="text-center text-[11px] sm:text-xs font-bold text-emerald-700 bg-emerald-50 py-2.5 px-3 rounded-xl border border-emerald-200">Veli</a>
            <a href="/" className="flex items-center justify-center gap-1 text-[11px] sm:text-xs font-bold text-white bg-rose-600 py-2.5 px-3 rounded-xl"><LogOut className="w-3.5 h-3.5" /> Çıkış</a>
          </div>
        </div>

        {/* SEKMELER */}
        <div className="bg-white rounded-2xl p-1.5 sm:p-2 border border-slate-200 shadow-xs grid grid-cols-2 lg:grid-cols-4 gap-1.5 sm:gap-2">
          <button onClick={() => setActiveTab('ogrenci')} className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold cursor-pointer min-h-[44px] ${activeTab === 'ogrenci' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'}`}>
            <Users className="w-4 h-4 shrink-0" /> <span>1. Öğrenci Yükle ({students.length})</span>
          </button>
          <button onClick={() => setActiveTab('belletmen')} className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold cursor-pointer min-h-[44px] ${activeTab === 'belletmen' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'}`}>
            <KeyRound className="w-4 h-4 shrink-0" /> <span>2. Belletmen Yükle ({belletmenler.length})</span>
          </button>
          <button onClick={() => setActiveTab('nobet')} className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold cursor-pointer min-h-[44px] ${activeTab === 'nobet' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'}`}>
            <Calendar className="w-4 h-4 shrink-0" /> <span>3. Aylık Nöbet ({aylikNobetler.length} Gün)</span>
          </button>
          <button onClick={() => setActiveTab('loglar')} className={`flex items-center justify-center gap-1.5 py-3 px-2 rounded-xl text-[11px] sm:text-xs font-extrabold cursor-pointer min-h-[44px] ${activeTab === 'loglar' ? 'bg-slate-900 text-amber-400 shadow-xs' : 'text-slate-600 hover:bg-slate-100'}`}>
            <Activity className="w-4 h-4 shrink-0" /> <span>4. Güvenlik Log ({auditLogs.length})</span>
          </button>
        </div>

        {msg && (
          <div className="p-3.5 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold flex justify-between items-center shadow-xs">
            <span>✅ {msg}</span>
            <button onClick={() => setMsg('')} className="underline ml-3 cursor-pointer">Kapat</button>
          </div>
        )}

        {/* ===================================================================
            SEKME 1: ÖĞRENCİ YÖNETİMİ VE EXCEL DOSYASI (.XLSX) İLE TOPLU YÜKLEME
        =================================================================== */}
        {activeTab === 'ogrenci' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              {/* EXCEL DOSYASI SEÇEREK VEYA YAPIŞTIRARAK TOPLU ÖĞRENCİ YÜKLEME */}
              <div className="bg-white rounded-2xl p-4 sm:p-5 border-2 border-emerald-200 shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                  <h2 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                    <FileSpreadsheet className="w-5 h-5 text-emerald-600" /> Excel Dosyası (.xlsx) ile Toplu Öğrenci Yükle
                  </h2>
                  <button
                    type="button"
                    onClick={downloadStudentTemplate}
                    className="inline-flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 rounded-xl cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" /> Örnek Excel İndir (.xlsx)
                  </button>
                </div>

                {/* Doğrudan Excel Dosyası Seçme Alanı */}
                <div className="p-4 bg-emerald-50/60 border-2 border-dashed border-emerald-300 rounded-2xl text-center space-y-2.5">
                  <input
                    ref={studentFileRef}
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleStudentExcelUpload}
                    className="hidden"
                    id="student-excel-input"
                  />
                  <label
                    htmlFor="student-excel-input"
                    className="w-full inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs py-3.5 px-4 rounded-xl shadow-sm cursor-pointer transition-all min-h-[46px]"
                  >
                    <FolderUp className="w-4 h-4" />
                    {loading ? 'Excel Dosyası Yükleniyor...' : 'Bilgisayardan / Telefondan Excel Dosyası Seç (.xlsx / .xls)'}
                  </label>
                  <p className="text-[11px] text-slate-500">
                    Sütun Sırası: <code>Ad Soyad | erkek/kiz | TC | Sınıf | Kat | Oda | Yatak | AnneTel | BabaTel</code>
                  </p>
                </div>

                {/* Alternatif: Kopyala-Yapıştır Alanı */}
                <div className="space-y-2 pt-1">
                  <label className="block text-[11px] font-bold text-slate-500">
                    Veya Excel tablosundan kopyalayıp aşağıya yapıştırın:
                  </label>
                  <textarea
                    rows={3}
                    value={studentCsv}
                    onChange={(e) => setStudentCsv(e.target.value)}
                    className="w-full border border-slate-200 rounded-xl p-2.5 text-xs font-mono bg-slate-50"
                  />
                  <button
                    onClick={handleBulkImportStudents}
                    disabled={loading}
                    className="w-full bg-slate-800 hover:bg-slate-900 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer flex items-center justify-center gap-2"
                  >
                    <Upload className="w-3.5 h-3.5" /> Yapıştırılan Metni Aktar
                  </button>
                </div>
              </div>

              {/* TEKİL ÖĞRENCİ KAYDI */}
              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Öğrenci Kaydı
                </h2>
                <form onSubmit={handleAddStudent} className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={sName} onChange={(e) => setSName(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <select value={sCinsiyet} onChange={(e) => setSCinsiyet(e.target.value as 'erkek' | 'kiz')} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs font-bold bg-white min-h-[44px]">
                    <option value="erkek">Erkek Pansiyonu</option>
                    <option value="kiz">Kız Pansiyonu</option>
                  </select>
                  <input type="text" placeholder="T.C." value={sTc} onChange={(e) => setSTc(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <input type="text" placeholder="Sınıf (9-A)" value={sSinif} onChange={(e) => setSSinif(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <select value={sKat} onChange={(e) => setSKat(Number(e.target.value))} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs bg-white min-h-[44px]">
                    <option value={1}>1. Kat</option>
                    <option value={2}>2. Kat</option>
                    <option value={3}>3. Kat</option>
                  </select>
                  <input type="text" placeholder="Oda No (101 / K-101)" value={sOda} onChange={(e) => setSOda(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <input type="tel" placeholder="Anne Tel" value={sAnneTel} onChange={(e) => setSAnneTel(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <input type="tel" placeholder="Baba Tel" value={sBabaTel} onChange={(e) => setSBabaTel(e.target.value)} className="border rounded-xl px-3 py-2.5 text-base sm:text-xs min-h-[44px]" />
                  <button type="submit" disabled={loading} className="sm:col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold cursor-pointer min-h-[46px]">
                    Öğrenciyi Kaydet
                  </button>
                </form>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3">
              <h3 className="text-sm font-bold text-slate-900">Kayıtlı Öğrenciler ({students.length})</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                {students.map((s) => (
                  <div key={s.id} className="border border-slate-200 rounded-xl p-3 text-xs flex justify-between items-center bg-slate-50/50">
                    <div>
                      <div className="font-extrabold text-slate-900">{s.name}</div>
                      <div className="text-[11px] text-slate-500">{s.cinsiyet === 'kiz' ? '👩 Kız' : '👨 Erkek'} • {s.kat}. Kat - Oda {s.oda}</div>
                      <div className="text-[11px] font-mono text-slate-600 mt-0.5">{s.anneTel}</div>
                    </div>
                    <button onClick={() => handleDeleteStudent(s.id)} className="text-rose-600 p-1.5 cursor-pointer"><Trash2 className="w-4 h-4" /></button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            SEKME 2: BELLETMEN YÖNETİMİ VE EXCEL DOSYASI (.XLSX) İLE TOPLU YÜKLEME
        =================================================================== */}
        {activeTab === 'belletmen' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              {/* EXCEL DOSYASI İLE TOPLU BELLETMEN YÜKLEME */}
              <div className="bg-white rounded-2xl p-4 sm:p-5 border-2 border-emerald-200 shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                  <h2 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                    <FileSpreadsheet className="w-5 h-5 text-emerald-600" /> Excel Dosyası (.xlsx) ile Belletmen Yükle
                  </h2>
                  <button
                    type="button"
                    onClick={downloadBelletmenTemplate}
                    className="inline-flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 rounded-xl cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" /> Örnek Excel İndir (.xlsx)
                  </button>
                </div>

                <div className="p-4 bg-emerald-50/60 border-2 border-dashed border-emerald-300 rounded-2xl text-center space-y-2.5">
                  <input
                    ref={belletmenFileRef}
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleBelletmenExcelUpload}
                    className="hidden"
                    id="belletmen-excel-input"
                  />
                  <label
                    htmlFor="belletmen-excel-input"
                    className="w-full inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs py-3.5 px-4 rounded-xl shadow-sm cursor-pointer transition-all min-h-[46px]"
                  >
                    <FolderUp className="w-4 h-4" />
                    {loading ? 'Excel Dosyası Yükleniyor...' : 'Bilgisayardan / Telefondan Excel Dosyası Seç (.xlsx / .xls)'}
                  </label>
                  <p className="text-[11px] text-slate-500">
                    Sütun Sırası: <code>Ad Soyad | erkek/kadin | Branş | Telefon | Şifre</code>
                  </p>
                </div>

                <div className="space-y-2 pt-1">
                  <label className="block text-[11px] font-bold text-slate-500">
                    Veya Excel tablosundan kopyalayıp aşağıya yapıştırın:
                  </label>
                  <textarea rows={3} value={belletmenCsv} onChange={(e) => setBelletmenCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-2.5 text-xs font-mono bg-slate-50" />
                  <button onClick={handleBulkAddBelletmen} disabled={loading} className="w-full bg-slate-800 hover:bg-slate-900 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer flex justify-center gap-2">
                    <Upload className="w-3.5 h-3.5" /> Yapıştırılan Metni Aktar
                  </button>
                </div>
              </div>

              {/* TEKİL BELLETMEN EKLEME */}
              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Belletmen Ekle
                </h2>
                <form onSubmit={handleAddBelletmen} className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={bName} onChange={(e) => setBName(e.target.value)} className="border rounded-xl px-3 py-3 text-base sm:text-xs font-semibold min-h-[44px]" />
                  <select value={bCinsiyet} onChange={(e) => setBCinsiyet(e.target.value as 'erkek' | 'kadin')} className="border rounded-xl px-3 py-3 text-base sm:text-xs font-bold bg-white min-h-[44px]">
                    <option value="erkek">👨 Erkek Belletmen</option>
                    <option value="kadin">👩 Kadın Belletmen</option>
                  </select>
                  <input type="text" placeholder="Branş" value={bBrans} onChange={(e) => setBBrans(e.target.value)} className="border rounded-xl px-3 py-3 text-base sm:text-xs min-h-[44px]" />
                  <input type="tel" placeholder="Telefon (0541...)" value={bPhone} onChange={(e) => setBPhone(e.target.value)} className="border rounded-xl px-3 py-3 text-base sm:text-xs font-mono min-h-[44px]" />
                  <input type="text" required placeholder="Giriş Şifresi" value={bPassword} onChange={(e) => setBPassword(e.target.value)} className="sm:col-span-2 border border-indigo-200 bg-indigo-50/40 rounded-xl px-3 py-3 text-base sm:text-xs font-mono font-bold min-h-[44px]" />
                  <button type="submit" className="sm:col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold cursor-pointer min-h-[46px]">
                    Belletmeni Sisteme Kaydet
                  </button>
                </form>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs">
              <h2 className="text-sm font-bold text-slate-900 mb-4">Kayıtlı Belletmenler & Şifre Görme / Değiştirme ({belletmenler.length})</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {belletmenler.map((b) => {
                  const isShown = !!visiblePasswords[b.id];
                  const isEditing = editingPasswordId === b.id;
                  return (
                    <div key={b.id} className="border rounded-2xl p-3.5 flex flex-col justify-between gap-3 bg-slate-50/50">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-extrabold text-sm">{b.name}</div>
                          <div className="text-[11px] text-slate-500">{b.cinsiyet === 'kadin' ? '👩 Kadın' : '👨 Erkek'} • {b.brans}</div>
                          <div className="text-[11px] font-mono text-slate-500">{b.phone}</div>
                        </div>
                        <button onClick={() => handleDeleteBelletmen(b.id)} className="text-rose-600 p-1 cursor-pointer"><Trash2 className="w-4 h-4" /></button>
                      </div>
                      {isEditing ? (
                        <div className="flex gap-2">
                          <input type="text" value={newPasswordVal} onChange={(e) => setNewPasswordVal(e.target.value)} className="flex-1 border rounded-xl px-3 py-1.5 text-xs font-mono bg-white" />
                          <button onClick={() => handleUpdatePassword(b.id)} className="bg-emerald-600 text-white px-3 py-1.5 rounded-xl text-xs font-bold cursor-pointer">Kaydet</button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between border rounded-xl px-3 py-2 bg-white">
                          <div className="flex items-center gap-2">
                            <span className="text-[11px] text-slate-400">Şifre:</span>
                            <span className="font-mono font-bold text-xs">{isShown ? b.password : '••••••'}</span>
                            <button onClick={() => setVisiblePasswords((p) => ({ ...p, [b.id]: !p[b.id] }))} className="text-slate-500 cursor-pointer">
                              {isShown ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                            </button>
                          </div>
                          <button onClick={() => { setEditingPasswordId(b.id); setNewPasswordVal(b.password); }} className="text-xs font-bold text-indigo-600 hover:underline cursor-pointer">
                            Değiştir
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            SEKME 3: AYLIK NÖBET LİSTESİ (OTOMATİK + EXCEL DOSYASI İLE YÜKLEME)
        =================================================================== */}
        {activeTab === 'nobet' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="bg-indigo-950 text-white rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
              <div>
                <h2 className="text-sm font-extrabold flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-amber-400" /> Otomatik Aylık Nöbet Çizelgesi Oluştur
                </h2>
                <p className="text-xs text-indigo-200">Seçilen ayın tüm günlerine 2 Erkek + 2 Kadın belletmeni sırayla otomatik dağıtır.</p>
              </div>
              <div className="flex flex-col xs:flex-row items-stretch xs:items-center gap-2">
                <input type="month" value={nobetAySecim} onChange={(e) => setNobetAySecim(e.target.value)} className="bg-white text-slate-900 font-bold text-xs px-3 py-2.5 rounded-xl min-h-[42px]" />
                <button onClick={handleAutoGenerateMonth} className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs px-4 py-2.5 rounded-xl cursor-pointer min-h-[42px]">
                  Tüm Ayı Otomatik Doldur
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              <div className="bg-white rounded-2xl p-4 sm:p-5 border-2 border-emerald-200 shadow-xs space-y-3.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900">Excel Dosyası (.xlsx) ile Aylık Nöbet Yükle</h3>
                  <button type="button" onClick={downloadNobetTemplate} className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 cursor-pointer">
                    <Download className="w-3 h-3 inline mr-1" /> Şablon İndir
                  </button>
                </div>
                <input ref={nobetFileRef} type="file" accept=".xlsx,.xls,.csv" onChange={handleNobetExcelUpload} className="hidden" id="nobet-excel-input" />
                <label htmlFor="nobet-excel-input" className="w-full inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-3 rounded-xl cursor-pointer">
                  <FolderUp className="w-4 h-4" /> Nöbet Excel Dosyası Seç (.xlsx)
                </label>
                <textarea rows={3} value={nobetCsv} onChange={(e) => setNobetCsv(e.target.value)} className="w-full border rounded-xl p-2.5 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkMonthlyDuty} className="w-full bg-slate-800 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  Yapıştırılan Nöbet Listesini Aktar
                </button>
              </div>

              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h3 className="text-sm font-bold text-slate-900">Tekil Gün Nöbeti Ata</h3>
                <form onSubmit={handleAddSingleDutyDay} className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                  <input type="date" value={nTarih} onChange={(e) => setNTarih(e.target.value)} className="sm:col-span-2 border rounded-xl px-3 py-2.5 font-bold min-h-[44px]" />
                  <select value={nErkek1} onChange={(e) => setNErkek1(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nErkek2} onChange={(e) => setNErkek2(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin1} onChange={(e) => setNKadin1(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin2} onChange={(e) => setNKadin2(e.target.value)} className="border rounded-xl px-2.5 py-2.5 bg-white min-h-[44px]">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <button type="submit" className="sm:col-span-2 bg-blue-600 text-white py-3 rounded-xl font-bold cursor-pointer min-h-[46px]">
                    <Save className="w-4 h-4 inline mr-1" /> Günü Kaydet
                  </button>
                </form>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-[420px] overflow-y-auto">
                {aylikNobetler.map((d) => (
                  <div key={d.tarih} className="border border-slate-200 rounded-xl p-3 text-xs space-y-1 bg-slate-50/50 flex justify-between items-start">
                    <div>
                      <div className="font-mono font-extrabold text-slate-900">{d.tarih}</div>
                      <div className="text-blue-700 font-semibold">👨 {d.erkek1}, {d.erkek2}</div>
                      <div className="text-rose-700 font-semibold">👩 {d.kadin1}, {d.kadin2}</div>
                    </div>
                    <button onClick={() => handleDeleteDutyDay(d.tarih)} className="text-rose-600 p-1 cursor-pointer"><Trash2 className="w-4 h-4" /></button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SEKME 4: SİSTEM GÜVENLİK LOGLARI */}
        {activeTab === 'loglar' && (
          <div className="bg-slate-950 rounded-3xl p-4 sm:p-6 border border-slate-800 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h2 className="text-base font-extrabold text-white flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-amber-400" /> Sistem Güvenlik & Denetim Günlüğü
              </h2>
              <button onClick={handleClearLogs} className="text-xs font-bold text-rose-300 border border-rose-800 px-3 py-1.5 rounded-xl cursor-pointer">
                Temizle
              </button>
            </div>
            <div className="space-y-2.5 max-h-[500px] overflow-y-auto">
              {auditLogs.map((log) => (
                <div key={log.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-3.5 space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white">{log.islem}</span>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md border font-bold text-[10px] uppercase ${getBadgeColor(log.tur)}`}>
                      {getIcon(log.tur)} {log.tur}
                    </span>
                  </div>
                  <p className="text-slate-300 text-[11px]">{log.detay}</p>
                  <div className="flex justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800">
                    <span className="text-blue-300 font-semibold">{log.kullanici}</span>
                    <span className="font-mono">{log.tarihSaat}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
'''

def main():
    print("=========================================================")
    print("   GERÇEK EXCEL (.XLSX) DOSYASI YÜKLEME SİSTEMİ KURULUYOR")
    print("=========================================================")

    kill_old_processes()

    # 1. Excel okuyucu (xlsx) paketini projeye kur
    run_command("npm install xlsx", "Excel (.xlsx) okuyucu kütüphanesi kuruluyor")

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 2. Admin sayfasını güncelle
    write_file("app/admin/page.tsx", ADMIN_PAGE_TSX)

    # 3. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 4. Derleme ve GitHub/Vercel Gönderimi
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Yonetim paneline dogrudan Excel (.xlsx/.xls) dosyasi secerek ogrenci ve belletmen yukleme eklendi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 EXCEL (.XLSX) DOSYASI YÜKLEME SİSTEMİ CANLIYA ALINDI!")
    print("👉 Yönetici Paneli: https://pansiyon-yurt-sistemi.vercel.app/admin")
    print("=========================================================")

if __name__ == "__main__":
    main()