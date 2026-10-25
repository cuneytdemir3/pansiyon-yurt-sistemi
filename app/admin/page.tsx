'use client';

import React, { useState, useEffect, useRef } from 'react';
import * as XLSX from 'xlsx';
import {
  Users, Upload, Plus, Trash2, Shield, FileSpreadsheet, LogOut,
  KeyRound, Eye, EyeOff, Calendar, Wand2, Save,
  Activity, ShieldAlert, CheckCircle2, AlertTriangle, Info, X, Download, FolderUp, Sparkles
} from 'lucide-react';

interface Student { id: string; name: string; cinsiyet: string; tc: string; sinif: string; kat: number; oda: string; yatak: string; anneTel: string; babaTel: string; status: string; }
interface Belletmen { id: string; name: string; cinsiyet: string; brans: string; phone: string; password: string; }
interface MonthlyDutyDay { tarih: string; erkek1: string; erkek2: string; kadin1: string; kadin2: string; }
interface AuditLog { id: string; tarihSaat: string; kullanici: string; islem: string; detay: string; tur: string; }

const SAMPLE_STUDENT_ROWS = [
  { name: 'Kerem Aksoy', cinsiyet: 'erkek', tc: '12345678930', sinif: '9-A', kat: 1, oda: '103', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469' },
  { name: 'Emirhan Yıldız', cinsiyet: 'erkek', tc: '12345678931', sinif: '10-B', kat: 2, oda: '202', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469' },
  { name: 'Yağmur Koç', cinsiyet: 'kiz', tc: '12345678933', sinif: '9-B', kat: 1, oda: 'K-102', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469' },
  { name: 'Defne Arslan', cinsiyet: 'kiz', tc: '12345678934', sinif: '11-A', kat: 2, oda: 'K-202', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469' },
];

const SAMPLE_BELLETMEN_ROWS = [
  { name: 'Serhat AKAN', cinsiyet: 'erkek', brans: 'Matematik', phone: '05416571469', password: '1453' },
  { name: 'Mustafa DEMİR', cinsiyet: 'erkek', brans: 'Tarih', phone: '05416571469', password: '1234' },
  { name: 'Kübra GÜLLÜ', cinsiyet: 'kadin', brans: 'Edebiyat', phone: '05416571469', password: '2026' },
  { name: 'Elif KAYA', cinsiyet: 'kadin', brans: 'İngilizce', phone: '05416571469', password: '1234' },
];

const SAMPLE_NOBET_ROWS = [
  { tarih: '2026-10-27', erkek1: 'Cüneyt DEMİR', erkek2: 'Ali BEY', kadin1: 'Ayşenur KAYA', kadin2: 'Fatma YILMAZ' },
  { tarih: '2026-10-28', erkek1: 'Furkan DEMİR', erkek2: 'Hasan ÇELİK', kadin1: 'Zeynep ŞAHİN', kadin2: 'Merve AYDIN' },
  { tarih: '2026-10-29', erkek1: 'Cüneyt DEMİR', erkek2: 'Furkan DEMİR', kadin1: 'Ayşenur KAYA', kadin2: 'Zeynep ŞAHİN' },
];

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'belletmen' | 'nobet' | 'ogrenci' | 'loglar'>('ogrenci');

  const [students, setStudents] = useState<Student[]>([]);
  const [belletmenler, setBelletmenler] = useState<Belletmen[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<MonthlyDutyDay[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const studentFileRef = useRef<HTMLInputElement | null>(null);
  const belletmenFileRef = useRef<HTMLInputElement | null>(null);
  const nobetFileRef = useRef<HTMLInputElement | null>(null);

  const [bName, setBName] = useState('');
  const [bCinsiyet, setBCinsiyet] = useState<'erkek' | 'kadin'>('erkek');
  const [bBrans, setBBrans] = useState('');
  const [bPhone, setBPhone] = useState('05416571469');
  const [bPassword, setBPassword] = useState('1234');
  const [belletmenCsv, setBelletmenCsv] = useState(
    'Serhat AKAN, erkek, Matematik, 05416571469, 1453\nKübra GÜLLÜ, kadin, Edebiyat, 05416571469, 2026'
  );

  const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({});
  const [editingPasswordId, setEditingPasswordId] = useState<string | null>(null);
  const [newPasswordVal, setNewPasswordVal] = useState('');

  const [nobetAySecim, setNobetAySecim] = useState('2026-10');
  const [nTarih, setNTarih] = useState('2026-10-29');
  const [nErkek1, setNErkek1] = useState('Cüneyt DEMİR');
  const [nErkek2, setNErkek2] = useState('Ali BEY');
  const [nKadin1, setNKadin1] = useState('Ayşenur KAYA');
  const [nKadin2, setNKadin2] = useState('Fatma YILMAZ');
  const [nobetCsv, setNobetCsv] = useState(
    '2026-10-27, Cüneyt DEMİR, Ali BEY, Ayşenur KAYA, Fatma YILMAZ\n2026-10-28, Furkan DEMİR, Hasan ÇELİK, Zeynep ŞAHİN, Merve AYDIN'
  );

  const [sName, setSName] = useState('');
  const [sCinsiyet, setSCinsiyet] = useState<'erkek' | 'kiz'>('erkek');
  const [sTc, setSTc] = useState('');
  const [sSinif, setSSinif] = useState('9-A');
  const [sKat, setSKat] = useState(1);
  const [sOda, setSOda] = useState('101');
  const [sYatak, setSYatak] = useState('A');
  const [sAnneTel, setSAnneTel] = useState('05416571469');
  const [sBabaTel, setSBabaTel] = useState('05416571469');
  const [studentCsv, setStudentCsv] = useState(
    'Kerem Aksoy, erkek, 12345678930, 9-A, 1, 103, A, 05416571469, 05416571469\nYağmur Koç, kiz, 12345678933, 9-B, 1, K-102, A, 05416571469, 05416571469'
  );

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
  // 1) TEK TIKLA ÖRNEK VERİ YÜKLEME (DOSYA SEÇMEDEN HIZLI TEST)
  // =========================================================================
  const handleLoadSampleStudents = async () => {
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows: SAMPLE_STUDENT_ROWS }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg('✅ Örnek Excel listesindeki 4 öğrenci (2 Erkek, 2 Kız) tek tıkla sisteme yüklendi!');
    }
    setLoading(false);
  };

  const handleLoadSampleBelletmen = async () => {
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_add_belletmen', rows: SAMPLE_BELLETMEN_ROWS }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg('✅ Örnek Excel listesindeki 4 Belletmen Öğretmen (2 Erkek, 2 Kadın) sisteme yüklendi!');
    }
    setLoading(false);
  };

  const handleLoadSampleNobet = async () => {
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_monthly_duty', rows: SAMPLE_NOBET_ROWS }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg('✅ Örnek Excel nöbet çizelgesindeki 3 günlük nöbet listesi sisteme yüklendi!');
    }
    setLoading(false);
  };

  // =========================================================================
  // 2) GERÇEK EXCEL (.XLSX / .XLS / .CSV) DOSYASI SEÇEREK YÜKLEME
  // =========================================================================
  const handleStudentExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
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

  const handleBelletmenExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
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
        setMsg(`📁 "${file.name}" dosyasından ${formattedRows.length} belletmen başarıyla yüklendi!`);
      }
    } catch {
      setMsg('Excel dosyası okunurken hata oluştu.');
    } finally {
      setLoading(false);
      if (belletmenFileRef.current) belletmenFileRef.current.value = '';
    }
  };

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
  // 3) ÖRNEK EXCEL (.XLSX) ŞABLONU İNDİRME FONKSİYONLARI
  // =========================================================================
  const downloadStudentTemplate = () => {
    const ws = XLSX.utils.aoa_to_sheet([
      ['Ad Soyad', 'Cinsiyet (erkek/kiz)', 'TC Kimlik', 'Sınıf', 'Kat', 'Oda No', 'Yatak', 'Anne Telefon', 'Baba Telefon'],
      ...SAMPLE_STUDENT_ROWS.map((r) => [r.name, r.cinsiyet, r.tc, r.sinif, r.kat, r.oda, r.yatak, r.anneTel, r.babaTel]),
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Ogrenci_Listesi');
    XLSX.writeFile(wb, 'Ornek_Ogrenci_Yukleme_Sablonu.xlsx');
  };

  const downloadBelletmenTemplate = () => {
    const ws = XLSX.utils.aoa_to_sheet([
      ['Ad Soyad', 'Cinsiyet (erkek/kadin)', 'Branş', 'Telefon', 'Giriş Şifresi'],
      ...SAMPLE_BELLETMEN_ROWS.map((r) => [r.name, r.cinsiyet, r.brans, r.phone, r.password]),
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Belletmen_Listesi');
    XLSX.writeFile(wb, 'Ornek_Belletmen_Yukleme_Sablonu.xlsx');
  };

  const downloadNobetTemplate = () => {
    const ws = XLSX.utils.aoa_to_sheet([
      ['Tarih (YYYY-AA-GG)', '1. Erkek Belletmen', '2. Erkek Belletmen', '1. Kadın Belletmen', '2. Kadın Belletmen'],
      ...SAMPLE_NOBET_ROWS.map((r) => [r.tarih, r.erkek1, r.erkek2, r.kadin1, r.kadin2]),
    ]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Aylik_Nobet');
    XLSX.writeFile(wb, 'Ornek_Aylik_Nobet_Sablonu.xlsx');
  };

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
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
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
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
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
    if (data.success) { syncFromStore(data.store); setMsg(data.message); }
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
                Örnek Excel (.xlsx) Şablonları • Toplu Öğrenci & Belletmen Yükleme • Güvenlik Günlüğü
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
            <span>{msg}</span>
            <button onClick={() => setMsg('')} className="underline ml-3 cursor-pointer">Kapat</button>
          </div>
        )}

        {/* ===================================================================
            SEKME 1: ÖĞRENCİ EXCEL YÜKLEME ÖRNEĞİ VE FORMU
        =================================================================== */}
        {activeTab === 'ogrenci' && (
          <div className="space-y-4 sm:space-y-6">

            {/* GÖRSEL EXCEL ÖRNEK TABLOSU KARTI */}
            <div className="bg-white rounded-2xl p-4 sm:p-5 border-2 border-emerald-200 shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
                <div>
                  <h2 className="text-sm sm:text-base font-extrabold text-slate-900 flex items-center gap-2">
                    <FileSpreadsheet className="w-5 h-5 text-emerald-600" /> Öğrenci Excel Yükleme Örneği (Sütun Sırası)
                  </h2>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Hazırlayacağınız Excel (`.xlsx`) dosyasının sütunları aşağıdaki örnek tabloyla aynı sırada olmalıdır:
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={downloadStudentTemplate}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-800 bg-emerald-100 hover:bg-emerald-200 px-3.5 py-2 rounded-xl cursor-pointer"
                  >
                    <Download className="w-4 h-4" /> Örnek Excel (.xlsx) İndir
                  </button>
                  <button
                    type="button"
                    onClick={handleLoadSampleStudents}
                    disabled={loading}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 px-3.5 py-2 rounded-xl cursor-pointer shadow-xs"
                  >
                    <Sparkles className="w-4 h-4" /> Tek Tıkla Bu Örneği Sisteme Yükle
                  </button>
                </div>
              </div>

              {/* Örnek Excel Görsel Önizleme Tablosu */}
              <div className="overflow-x-auto border border-emerald-200 rounded-xl">
                <table className="w-full text-[11px] border-collapse text-left">
                  <thead>
                    <tr className="bg-emerald-700 text-white font-bold">
                      <th className="p-2 border-r border-emerald-600">A: Ad Soyad</th>
                      <th className="p-2 border-r border-emerald-600">B: Cinsiyet</th>
                      <th className="p-2 border-r border-emerald-600">C: TC Kimlik</th>
                      <th className="p-2 border-r border-emerald-600">D: Sınıf</th>
                      <th className="p-2 border-r border-emerald-600">E: Kat</th>
                      <th className="p-2 border-r border-emerald-600">F: Oda No</th>
                      <th className="p-2 border-r border-emerald-600">G: Yatak</th>
                      <th className="p-2 border-r border-emerald-600">H: Anne Telefon</th>
                      <th className="p-2">I: Baba Telefon</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-emerald-100 bg-emerald-50/30 font-mono">
                    {SAMPLE_STUDENT_ROWS.map((row, i) => (
                      <tr key={i}>
                        <td className="p-2 font-sans font-bold text-slate-800 border-r border-emerald-100">{row.name}</td>
                        <td className="p-2 border-r border-emerald-100">{row.cinsiyet}</td>
                        <td className="p-2 border-r border-emerald-100">{row.tc}</td>
                        <td className="p-2 border-r border-emerald-100">{row.sinif}</td>
                        <td className="p-2 border-r border-emerald-100">{row.kat}</td>
                        <td className="p-2 border-r border-emerald-100 font-bold">{row.oda}</td>
                        <td className="p-2 border-r border-emerald-100">{row.yatak}</td>
                        <td className="p-2 border-r border-emerald-100">{row.anneTel}</td>
                        <td className="p-2">{row.babaTel}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Dosya Seçme Kutusu */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2">
                <div className="p-4 bg-emerald-50/70 border-2 border-dashed border-emerald-300 rounded-2xl flex flex-col justify-center items-center text-center space-y-2">
                  <input ref={studentFileRef} type="file" accept=".xlsx,.xls,.csv" onChange={handleStudentExcelUpload} className="hidden" id="student-excel-input" />
                  <label htmlFor="student-excel-input" className="w-full inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs py-3.5 px-4 rounded-xl shadow-sm cursor-pointer min-h-[46px]">
                    <FolderUp className="w-4 h-4" /> Bilgisayardan / Telefondan Excel Dosyası Seç (.xlsx / .xls)
                  </label>
                  <span className="text-[11px] text-slate-500">Seçtiğiniz anda otomatik okunur ve listeye eklenir.</span>
                </div>

                <div className="space-y-2">
                  <label className="block text-[11px] font-bold text-slate-600">Veya Excel satırlarını kopyalayıp buraya yapıştırın:</label>
                  <textarea rows={2} value={studentCsv} onChange={(e) => setStudentCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-2.5 text-xs font-mono bg-slate-50" />
                  <button onClick={handleBulkImportStudents} disabled={loading} className="w-full bg-slate-800 hover:bg-slate-900 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer flex items-center justify-center gap-2">
                    <Upload className="w-3.5 h-3.5" /> Yapıştırılan Öğrenci Listesini Aktar
                  </button>
                </div>
              </div>
            </div>

            {/* TEKİL ÖĞRENCİ EKLEME & LİSTE */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
              <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3.5">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Öğrenci Ekle
                </h2>
                <form onSubmit={handleAddStudent} className="grid grid-cols-1 gap-2.5 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={sName} onChange={(e) => setSName(e.target.value)} className="border rounded-xl px-3 py-2.5" />
                  <select value={sCinsiyet} onChange={(e) => setSCinsiyet(e.target.value as 'erkek' | 'kiz')} className="border rounded-xl px-3 py-2.5 font-bold bg-white">
                    <option value="erkek">👨 Erkek Pansiyonu</option>
                    <option value="kiz">👩 Kız Pansiyonu</option>
                  </select>
                  <div className="grid grid-cols-2 gap-2">
                    <select value={sKat} onChange={(e) => setSKat(Number(e.target.value))} className="border rounded-xl px-3 py-2.5 bg-white">
                      <option value={1}>1. Kat</option>
                      <option value={2}>2. Kat</option>
                      <option value={3}>3. Kat</option>
                    </select>
                    <input type="text" placeholder="Oda No (101)" value={sOda} onChange={(e) => setSOda(e.target.value)} className="border rounded-xl px-3 py-2.5" />
                  </div>
                  <input type="tel" placeholder="Anne Tel" value={sAnneTel} onChange={(e) => setSAnneTel(e.target.value)} className="border rounded-xl px-3 py-2.5" />
                  <button type="submit" className="bg-indigo-600 text-white py-2.5 rounded-xl font-bold cursor-pointer">Kaydet</button>
                </form>
              </div>

              <div className="lg:col-span-2 bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs space-y-3">
                <h3 className="text-sm font-bold text-slate-900">Kayıtlı Öğrenciler ({students.length})</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-[360px] overflow-y-auto">
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
          </div>
        )}

        {/* ===================================================================
            SEKME 2: BELLETMEN EXCEL YÜKLEME ÖRNEĞİ VE FORMU
        =================================================================== */}
        {activeTab === 'belletmen' && (
          <div className="space-y-4 sm:space-y-6">
            <div className="bg-white rounded-2xl p-4 sm:p-5 border-2 border-emerald-200 shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
                <div>
                  <h2 className="text-sm sm:text-base font-extrabold text-slate-900 flex items-center gap-2">
                    <FileSpreadsheet className="w-5 h-5 text-emerald-600" /> Belletmen Excel Yükleme Örneği (Sütun Sırası)
                  </h2>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Belletmen öğretmenlerinizi Excel ile toplu yüklerken kullanacağınız örnek tablo yapısı:
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button type="button" onClick={downloadBelletmenTemplate} className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-800 bg-emerald-100 hover:bg-emerald-200 px-3.5 py-2 rounded-xl cursor-pointer">
                    <Download className="w-4 h-4" /> Örnek Excel (.xlsx) İndir
                  </button>
                  <button type="button" onClick={handleLoadSampleBelletmen} disabled={loading} className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 px-3.5 py-2 rounded-xl cursor-pointer">
                    <Sparkles className="w-4 h-4" /> Tek Tıkla Bu Örneği Sisteme Yükle
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto border border-emerald-200 rounded-xl">
                <table className="w-full text-[11px] border-collapse text-left">
                  <thead>
                    <tr className="bg-emerald-700 text-white font-bold">
                      <th className="p-2 border-r border-emerald-600">A: Ad Soyad</th>
                      <th className="p-2 border-r border-emerald-600">B: Cinsiyet (erkek/kadin)</th>
                      <th className="p-2 border-r border-emerald-600">C: Branş</th>
                      <th className="p-2 border-r border-emerald-600">D: Telefon (WhatsApp Şifre İçin)</th>
                      <th className="p-2">E: Giriş Şifresi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-emerald-100 bg-emerald-50/30 font-mono">
                    {SAMPLE_BELLETMEN_ROWS.map((row, i) => (
                      <tr key={i}>
                        <td className="p-2 font-sans font-bold text-slate-800 border-r border-emerald-100">{row.name}</td>
                        <td className="p-2 border-r border-emerald-100">{row.cinsiyet}</td>
                        <td className="p-2 font-sans border-r border-emerald-100">{row.brans}</td>
                        <td className="p-2 border-r border-emerald-100">{row.phone}</td>
                        <td className="p-2 font-bold text-indigo-700">{row.password}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2">
                <div className="p-4 bg-emerald-50/70 border-2 border-dashed border-emerald-300 rounded-2xl flex flex-col justify-center items-center text-center space-y-2">
                  <input ref={belletmenFileRef} type="file" accept=".xlsx,.xls,.csv" onChange={handleBelletmenExcelUpload} className="hidden" id="belletmen-excel-input" />
                  <label htmlFor="belletmen-excel-input" className="w-full inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs py-3.5 px-4 rounded-xl cursor-pointer min-h-[46px]">
                    <FolderUp className="w-4 h-4" /> Belletmen Excel Dosyası Seç (.xlsx / .xls)
                  </label>
                </div>

                <div className="space-y-2">
                  <textarea rows={2} value={belletmenCsv} onChange={(e) => setBelletmenCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-2.5 text-xs font-mono bg-slate-50" />
                  <button onClick={handleBulkAddBelletmen} disabled={loading} className="w-full bg-slate-800 hover:bg-slate-900 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                    Yapıştırılan Belletmen Listesini Aktar
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200 shadow-xs">
              <h2 className="text-sm font-bold text-slate-900 mb-4">Kayıtlı Belletmenler & Şifre Yönetimi ({belletmenler.length})</h2>
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
            SEKME 3: AYLIK NÖBET EXCEL ÖRNEĞİ VE OTOMATİK ATAMA
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
              <div className="flex items-center gap-2">
                <input type="month" value={nobetAySecim} onChange={(e) => setNobetAySecim(e.target.value)} className="bg-white text-slate-900 font-bold text-xs px-3 py-2.5 rounded-xl" />
                <button onClick={handleAutoGenerateMonth} className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs px-4 py-2.5 rounded-xl cursor-pointer">
                  Tüm Ayı Otomatik Doldur
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-4 sm:p-5 border-2 border-emerald-200 shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-5 h-5 text-emerald-600" /> Aylık Nöbet Excel Yükleme Örneği
                </h3>
                <div className="flex flex-wrap gap-2">
                  <button type="button" onClick={downloadNobetTemplate} className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-800 bg-emerald-100 px-3 py-1.5 rounded-xl cursor-pointer">
                    <Download className="w-3.5 h-3.5" /> Örnek Nöbet Excel (.xlsx) İndir
                  </button>
                  <button type="button" onClick={handleLoadSampleNobet} className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-indigo-600 px-3 py-1.5 rounded-xl cursor-pointer">
                    <Sparkles className="w-3.5 h-3.5" /> Tek Tıkla Örnek Nöbetleri Yükle
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto border border-emerald-200 rounded-xl">
                <table className="w-full text-[11px] border-collapse text-left">
                  <thead>
                    <tr className="bg-emerald-700 text-white font-bold">
                      <th className="p-2 border-r border-emerald-600">A: Tarih (YYYY-AA-GG)</th>
                      <th className="p-2 border-r border-emerald-600">B: 1. Erkek Belletmen</th>
                      <th className="p-2 border-r border-emerald-600">C: 2. Erkek Belletmen</th>
                      <th className="p-2 border-r border-emerald-600">D: 1. Kadın Belletmen</th>
                      <th className="p-2">E: 2. Kadın Belletmen</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-emerald-100 bg-emerald-50/30">
                    {SAMPLE_NOBET_ROWS.map((r, i) => (
                      <tr key={i}>
                        <td className="p-2 font-mono font-bold border-r border-emerald-100">{r.tarih}</td>
                        <td className="p-2 border-r border-emerald-100 text-blue-800 font-semibold">{r.erkek1}</td>
                        <td className="p-2 border-r border-emerald-100 text-blue-800 font-semibold">{r.erkek2}</td>
                        <td className="p-2 border-r border-emerald-100 text-rose-800 font-semibold">{r.kadin1}</td>
                        <td className="p-2 text-rose-800 font-semibold">{r.kadin2}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <input ref={nobetFileRef} type="file" accept=".xlsx,.xls,.csv" onChange={handleNobetExcelUpload} className="hidden" id="nobet-excel-input" />
              <label htmlFor="nobet-excel-input" className="w-full inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-3 rounded-xl cursor-pointer">
                <FolderUp className="w-4 h-4" /> Nöbet Excel Dosyası Seç (.xlsx / .xls)
              </label>
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