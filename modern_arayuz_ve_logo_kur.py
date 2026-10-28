import os
import re
import subprocess
import sys

def write_file(filepath, content):
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ [GÜNCELLENDİ] {filepath}")

def get_saved_db_url():
    if os.path.exists(".env.local"):
        with open(".env.local", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("DATABASE_URL="):
                    return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    if os.path.exists("app/api/pansiyon/route.ts"):
        with open("app/api/pansiyon/route.ts", "r", encoding="utf-8") as f:
            m = re.search(r"postgresql://[^\s'\"`]+", f.read())
            if m:
                return m.group(0)
    return ""

# =========================================================================
# 1. API ROTASI (app/api/pansiyon/route.ts)
#    - Otomatik numara atama (05416571469 fallback) TAMAMEN KALDIRILDI.
#    - Veli KVKK izolasyonu ve Nöbet Defteri isim düzenleme tam aktif.
# =========================================================================
API_ROUTE_TS = r'''import { NextResponse } from 'next/server';
import { neon } from '@neondatabase/serverless';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

const FALLBACK_DB_URL = '__USER_DATABASE_URL__';

function getSql() {
  const url = process.env.DATABASE_URL || FALLBACK_DB_URL;
  if (!url || url.includes('__USER_DATABASE_URL__')) {
    throw new Error('DATABASE_URL tanımlı değil!');
  }
  return neon(url);
}

export interface StudentRecord {
  id: string; name: string; cinsiyet: 'erkek' | 'kiz'; kat: number; oda: string;
  anneAdi: string; anneTel: string; babaAdi: string; babaTel: string; status: 'var' | 'yok' | 'izinli';
}
export interface BelletmenRecord { id: string; name: string; cinsiyet: 'erkek' | 'kadin'; brans: string; phone: string; password: string; }
export interface MonthlyDutyDay { tarih: string; erkek1: string; erkek2: string; kadin1: string; kadin2: string; }
export interface LeaveRecord { id: string; studentId: string; studentName: string; oda: string; tip: string; baslangic: string; bitis: string; aciklama: string; veliTel: string; createdAt: string; }
export interface DutyLogRecord { id: string; tarih: string; seans: string; erkekBelletmen1: string; erkekBelletmen2: string; kizBelletmen1: string; kizBelletmen2: string; notlar: string; }
export interface AuditLogRecord { id: string; tarihSaat: string; kullanici: string; islem: string; detay: string; tur: string; }

export interface StoreData {
  students: StudentRecord[];
  belletmenler: BelletmenRecord[];
  aylikNobetler: MonthlyDutyDay[];
  leaves: LeaveRecord[];
  dutyLogs: DutyLogRecord[];
  auditLogs: AuditLogRecord[];
  updatedAt: number;
  tunnelUrl?: string;
}

const DEFAULT_STORE: StoreData = {
  students: [],
  belletmenler: [],
  aylikNobetler: [],
  leaves: [],
  dutyLogs: [],
  auditLogs: [],
  updatedAt: Date.now(),
  tunnelUrl: ''
};

export function normalizePhone10(raw: any): string {
  const digits = String(raw || '').replace(/\D/g, '');
  if (digits.length >= 10) {
    return digits.slice(-10);
  }
  return digits;
}

async function getStore(): Promise<StoreData> {
  const sql = getSql();
  await sql`
    CREATE TABLE IF NOT EXISTS pansiyon_cloud_state (
      id INT PRIMARY KEY,
      data JSONB NOT NULL,
      updated_at BIGINT NOT NULL
    )
  `;
  const rows = await sql`SELECT data FROM pansiyon_cloud_state WHERE id = 1`;
  if (rows.length === 0) {
    const initial = JSON.parse(JSON.stringify(DEFAULT_STORE)) as StoreData;
    await sql`
      INSERT INTO pansiyon_cloud_state (id, data, updated_at)
      VALUES (1, ${JSON.stringify(initial)}::jsonb, ${Date.now()})
    `;
    return initial;
  }
  return rows[0].data as StoreData;
}

async function saveStore(store: StoreData): Promise<void> {
  const sql = getSql();
  store.updatedAt = Date.now();
  await sql`
    INSERT INTO pansiyon_cloud_state (id, data, updated_at)
    VALUES (1, ${JSON.stringify(store)}::jsonb, ${store.updatedAt})
    ON CONFLICT (id) DO UPDATE SET
      data = EXCLUDED.data,
      updated_at = EXCLUDED.updated_at
  `;
}

function parseStudentGender(val: any): 'erkek' | 'kiz' {
  const s = String(val || '').trim().toLowerCase();
  if (s === 'k' || s.includes('kız') || s.includes('kiz') || s.includes('kadın') || s.includes('kadin') || s.includes('bayan')) return 'kiz';
  if (s === 'e' || s.includes('erkek') || s.includes('bay')) return 'erkek';
  return 'erkek';
}

function parseBelletmenGender(val: any): 'erkek' | 'kadin' {
  const s = String(val || '').trim().toLowerCase();
  if (s === 'k' || s.includes('kız') || s.includes('kiz') || s.includes('kadın') || s.includes('kadin') || s.includes('bayan')) return 'kadin';
  if (s === 'e' || s.includes('erkek') || s.includes('bay')) return 'erkek';
  return 'erkek';
}

function normalizeKat(val: any): number {
  const match = String(val || '1').match(/\d+/);
  return match ? parseInt(match[0], 10) : 1;
}

const addLog = (store: StoreData, kullanici: string, islem: string, detay: string, tur: string) => {
  if (!store.auditLogs) store.auditLogs = [];
  store.auditLogs.unshift({
    id: Date.now().toString() + Math.random().toString(36).substring(2, 6),
    tarihSaat: new Date().toLocaleString('tr-TR'),
    kullanici, islem, detay, tur
  });
  if (store.auditLogs.length > 100) store.auditLogs.pop();
};

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const cinsiyetFilter = searchParams.get('cinsiyet');
    const veliTelFilter = searchParams.get('veliTel');
    const store = await getStore();

    const headers = {
      'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    };

    if (veliTelFilter) {
      const targetPhone = normalizePhone10(veliTelFilter);
      const myStudents = (store.students || []).filter((s) => {
        const anneP = normalizePhone10(s.anneTel);
        const babaP = normalizePhone10(s.babaTel);
        return targetPhone.length === 10 && (anneP === targetPhone || babaP === targetPhone);
      });
      const myStudentIds = new Set(myStudents.map((s) => s.id));
      const myLeaves = (store.leaves || []).filter((l) => myStudentIds.has(l.studentId));

      return NextResponse.json({
        success: true,
        store: {
          students: myStudents,
          leaves: myLeaves,
          belletmenler: [],
          aylikNobetler: [],
          dutyLogs: [],
          auditLogs: [],
          updatedAt: store.updatedAt,
          tunnelUrl: store.tunnelUrl
        }
      }, { headers });
    }

    if (cinsiyetFilter === 'erkek' || cinsiyetFilter === 'kiz') {
      const filteredStudents = (store.students || []).filter((s) => s.cinsiyet === cinsiyetFilter);
      const allowedIds = new Set(filteredStudents.map((s) => s.id));
      const filteredLeaves = (store.leaves || []).filter((l) => allowedIds.has(l.studentId));
      return NextResponse.json({
        success: true,
        store: { ...store, students: filteredStudents, leaves: filteredLeaves }
      }, { headers });
    }

    return NextResponse.json({ success: true, store }, { headers });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = await getStore();

    if (!store.students) store.students = [];
    if (!store.belletmenler) store.belletmenler = [];
    if (!store.aylikNobetler) store.aylikNobetler = [];
    if (!store.leaves) store.leaves = [];
    if (!store.dutyLogs) store.dutyLogs = [];

    if (action === 'update_tunnel_url') {
      store.tunnelUrl = String(body.tunnelUrl || '').trim();
      await saveStore(store);
      return NextResponse.json({ success: true, tunnelUrl: store.tunnelUrl });
    }

    if (action === 'verify_parent_phone') {
      const targetPhone = normalizePhone10(body.phone);
      if (targetPhone.length < 10) {
        return NextResponse.json({
          success: false,
          message: 'Lütfen geçerli bir 10 veya 11 haneli cep telefonu numarası giriniz.'
        }, { status: 400 });
      }

      const matchedStudents = store.students.filter((s) => {
        const aTel = normalizePhone10(s.anneTel);
        const bTel = normalizePhone10(s.babaTel);
        return (aTel.length === 10 && aTel === targetPhone) || (bTel.length === 10 && bTel === targetPhone);
      });

      if (matchedStudents.length === 0) {
        return NextResponse.json({
          success: false,
          message: 'Adınıza kayıtlı öğrenci gözükmemektedir'
        }, { status: 404 });
      }

      return NextResponse.json({
        success: true,
        students: matchedStudents,
        tunnelUrl: store.tunnelUrl
      });
    }

    if (action === 'belletmen_login') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (!found || found.password !== String(body.password || '').trim()) {
        addLog(store, found ? found.name : 'Bilinmeyen', 'Hatalı Belletmen Girişi', 'Şifre yanlış girildi.', 'hata');
        await saveStore(store);
        return NextResponse.json({ success: false, message: 'Hatalı belletmen şifresi girdiniz!' }, { status: 401 });
      }
      const targetStudentGender = found.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
      addLog(store, found.name, 'Belletmen Girişi', `${targetStudentGender === 'kiz' ? 'Kız' : 'Erkek'} Pansiyonu yoklama ekranına giriş yapıldı.`, 'basari');
      await saveStore(store);
      return NextResponse.json({ success: true, belletmen: found, allowedGender: targetStudentGender, store });
    }

    if (action === 'log_forgot_password') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (found) {
        addLog(store, found.name, 'Şifre Hatırlatma', `WhatsApp (${found.phone}) üzerinden şifre gönderildi.`, 'uyari');
        await saveStore(store);
      }
      return NextResponse.json({ success: true, tunnelUrl: store.tunnelUrl, belletmen: found });
    }

    if (action === 'admin_login') {
      if (body.username === 'admin' && String(body.password).trim() === '123456') {
        addLog(store, 'Yönetici (Admin)', 'Yönetim Girişi', 'İdare paneline giriş yapıldı.', 'basari');
        await saveStore(store);
        return NextResponse.json({ success: true, store });
      }
      return NextResponse.json({ success: false, message: 'Hatalı yönetici şifresi!' }, { status: 401 });
    }

    if (action === 'update_attendance') {
      if (Array.isArray(body.students)) {
        const updatedMap = new Map(body.students.map((s: StudentRecord) => [s.id, s]));
        store.students = store.students.map((existing) =>
          updatedMap.has(existing.id) ? (updatedMap.get(existing.id) as StudentRecord) : existing
        );
        await saveStore(store);
      }
      return NextResponse.json({ success: true, message: 'Yoklama buluta kaydedildi.', store });
    }

    // ÖĞRENCİ EKLEME (Numara boşsa kesinlikle boş bırakılır, kendi numaranız atanmaz!)
    if (action === 'add_student') {
      const newStudent: StudentRecord = {
        id: Date.now().toString() + Math.random().toString(36).substring(2, 6),
        name: String(body.name || '').trim(),
        cinsiyet: parseStudentGender(body.cinsiyet),
        kat: normalizeKat(body.kat),
        oda: String(body.oda || '101').trim(),
        anneAdi: String(body.anneAdi || '').trim(),
        anneTel: String(body.anneTel || '').trim(),
        babaAdi: String(body.babaAdi || '').trim(),
        babaTel: String(body.babaTel || '').trim(),
        status: 'var'
      };
      store.students.push(newStudent);
      addLog(store, 'Yönetici', 'Öğrenci Eklendi', `${newStudent.name} (${newStudent.cinsiyet}) eklendi.`, 'basari');
      await saveStore(store);
      return NextResponse.json({ success: true, message: `${newStudent.name} eklendi!`, store });
    }

    if (action === 'bulk_import') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name || !String(r.name).trim()) continue;
          store.students.push({
            id: (Date.now() + Math.random()).toString(),
            name: String(r.name).trim(),
            cinsiyet: parseStudentGender(r.cinsiyet),
            kat: normalizeKat(r.kat),
            oda: String(r.oda || '101').trim(),
            anneAdi: String(r.anneAdi || '').trim(),
            anneTel: String(r.anneTel || '').trim(),
            babaAdi: String(r.babaAdi || '').trim(),
            babaTel: String(r.babaTel || '').trim(),
            status: 'var'
          });
          added++;
        }
      }
      addLog(store, 'Yönetici', 'Toplu Öğrenci Yükleme', `${added} öğrenci yüklendi.`, 'basari');
      await saveStore(store);
      return NextResponse.json({ success: true, message: `${added} öğrenci kalıcı olarak kaydedildi!`, store });
    }

    if (action === 'delete_student') {
      store.students = store.students.filter((s) => s.id !== body.id);
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Öğrenci silindi.', store });
    }

    if (action === 'clear_all_students') {
      store.students = [];
      store.leaves = [];
      addLog(store, 'Yönetici', 'Öğrenci Listesi Sıfırlandı', 'Tüm öğrenci kayıtları temizlendi.', 'uyari');
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Tüm öğrenci listesi temizlendi.', store });
    }

    if (action === 'add_belletmen') {
      store.belletmenler.push({
        id: Date.now().toString(),
        name: String(body.name).trim(),
        cinsiyet: parseBelletmenGender(body.cinsiyet),
        brans: String(body.brans || 'Öğretmen').trim(),
        phone: String(body.phone || '').trim(),
        password: String(body.password || '1234').trim()
      });
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Belletmen eklendi.', store });
    }

    if (action === 'bulk_add_belletmen') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          store.belletmenler.push({
            id: (Date.now() + Math.random()).toString(),
            name: String(r.name).trim(),
            cinsiyet: parseBelletmenGender(r.cinsiyet),
            brans: String(r.brans || 'Öğretmen').trim(),
            phone: String(r.phone || '').trim(),
            password: String(r.password || '1234').trim()
          });
          added++;
        }
      }
      await saveStore(store);
      return NextResponse.json({ success: true, message: `${added} belletmen eklendi!`, store });
    }

    if (action === 'update_belletmen_password') {
      const target = store.belletmenler.find((b) => b.id === body.id);
      if (target) {
        target.password = String(body.newPassword).trim();
        await saveStore(store);
        return NextResponse.json({ success: true, message: 'Şifre güncellendi.', store });
      }
      return NextResponse.json({ success: false, message: 'Bulunamadı.' }, { status: 404 });
    }

    if (action === 'delete_belletmen') {
      store.belletmenler = store.belletmenler.filter((b) => b.id !== body.id);
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Belletmen silindi.', store });
    }

    if (action === 'add_or_update_monthly_duty') {
      const { tarih, erkek1, erkek2, kadin1, kadin2 } = body;
      const idx = store.aylikNobetler.findIndex((d) => d.tarih === tarih);
      const item: MonthlyDutyDay = { tarih, erkek1, erkek2, kadin1, kadin2 };
      if (idx > -1) store.aylikNobetler[idx] = item;
      else { store.aylikNobetler.push(item); store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih)); }
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Nöbet kaydedildi.', store });
    }

    if (action === 'auto_generate_month_duty') {
      const yearMonth = String(body.yearMonth);
      const [yStr, mStr] = yearMonth.split('-');
      const days = new Date(Number(yStr), Number(mStr), 0).getDate();
      const erkekler = store.belletmenler.filter((b) => b.cinsiyet === 'erkek');
      const kadinlar = store.belletmenler.filter((b) => b.cinsiyet === 'kadin');
      store.aylikNobetler = store.aylikNobetler.filter((d) => !d.tarih.startsWith(yearMonth));
      for (let d = 1; d <= days; d++) {
        const dateKey = `${yearMonth}-${d < 10 ? '0'+d : d}`;
        store.aylikNobetler.push({
          tarih: dateKey,
          erkek1: erkekler.length > 0 ? erkekler[(d * 2 - 2) % erkekler.length].name : 'Atanmadı',
          erkek2: erkekler.length > 1 ? erkekler[(d * 2 - 1) % erkekler.length].name : 'Atanmadı',
          kadin1: kadinlar.length > 0 ? kadinlar[(d * 2 - 2) % kadinlar.length].name : 'Atanmadı',
          kadin2: kadinlar.length > 1 ? kadinlar[(d * 2 - 1) % kadinlar.length].name : 'Atanmadı',
        });
      }
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Aylık nöbet oluşturuldu!', store });
    }

    if (action === 'delete_monthly_duty') {
      store.aylikNobetler = store.aylikNobetler.filter((d) => d.tarih !== body.tarih);
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Nöbet silindi.', store });
    }

    if (action === 'add_leave') {
      const { studentId, tip, baslangic, bitis, aciklama, veliTel } = body;
      const st = store.students.find((s) => s.id === studentId);
      if (!st) {
        return NextResponse.json({ success: false, message: 'Öğrenci bulunamadı!' }, { status: 404 });
      }
      if (veliTel) {
        const pNorm = normalizePhone10(veliTel);
        const isOwnChild = normalizePhone10(st.anneTel) === pNorm || normalizePhone10(st.babaTel) === pNorm;
        if (!isOwnChild) {
          return NextResponse.json({ success: false, message: 'Sadece kendi öğrenciniz için izin talebi oluşturabilirsiniz!' }, { status: 403 });
        }
      }

      store.leaves.unshift({
        id: Date.now().toString(),
        studentId: st.id,
        studentName: st.name,
        oda: st.oda,
        tip: tip || 'Evci İzni',
        baslangic,
        bitis,
        aciklama: aciklama || 'Veli talebi',
        veliTel: veliTel || st.anneTel,
        createdAt: new Date().toISOString().split('T')[0]
      });
      st.status = 'izinli';
      addLog(store, `Veli (${veliTel || st.anneTel})`, 'Veli İzin Talebi', `${st.name} için ${baslangic} - ${bitis} arası izin onaylandı.`, 'basari');
      await saveStore(store);

      if (veliTel) {
        const pNorm = normalizePhone10(veliTel);
        const myStudents = store.students.filter((s) => normalizePhone10(s.anneTel) === pNorm || normalizePhone10(s.babaTel) === pNorm);
        const myIds = new Set(myStudents.map((s) => s.id));
        const myLeaves = store.leaves.filter((l) => myIds.has(l.studentId));
        return NextResponse.json({
          success: true,
          message: `${st.name} için izin talebiniz onaylandı!`,
          store: { ...store, students: myStudents, leaves: myLeaves }
        });
      }

      return NextResponse.json({ success: true, message: 'İzin onaylandı.', store });
    }

    if (action === 'add_duty_log') {
      const { tarih, seans, erkekBelletmen1, erkekBelletmen2, kizBelletmen1, kizBelletmen2, notlar } = body;
      store.dutyLogs.unshift({
        id: Date.now().toString(),
        tarih: String(tarih || ''),
        seans: String(seans || ''),
        erkekBelletmen1: String(erkekBelletmen1 || ''),
        erkekBelletmen2: String(erkekBelletmen2 || ''),
        kizBelletmen1: String(kizBelletmen1 || ''),
        kizBelletmen2: String(kizBelletmen2 || ''),
        notlar: String(notlar || '')
      });
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Nöbet defteri kaydedildi.', store });
    }

    if (action === 'update_duty_log') {
      const { id, tarih, seans, erkekBelletmen1, erkekBelletmen2, kizBelletmen1, kizBelletmen2, notlar } = body;
      const idx = store.dutyLogs.findIndex((l) => l.id === id);
      if (idx > -1) {
        store.dutyLogs[idx] = {
          ...store.dutyLogs[idx],
          tarih: String(tarih || store.dutyLogs[idx].tarih),
          seans: String(seans || store.dutyLogs[idx].seans),
          erkekBelletmen1: String(erkekBelletmen1 ?? ''),
          erkekBelletmen2: String(erkekBelletmen2 ?? ''),
          kizBelletmen1: String(kizBelletmen1 ?? ''),
          kizBelletmen2: String(kizBelletmen2 ?? ''),
          notlar: String(notlar ?? '')
        };
        await saveStore(store);
        return NextResponse.json({ success: true, message: 'Nöbet defteri güncellendi!', store });
      }
      return NextResponse.json({ success: false, message: 'Kayıt bulunamadı.' }, { status: 404 });
    }

    if (action === 'delete_duty_log') {
      store.dutyLogs = store.dutyLogs.filter((l) => l.id !== body.id);
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Silindi.', store });
    }

    if (action === 'clear_audit_logs') {
      store.auditLogs = [];
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Günlük temizlendi.', store });
    }

    return NextResponse.json({ success: false, message: 'Bilinmeyen işlem.' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
'''

# =========================================================================
# 2. OKUL LOGOSU BİLEŞENİ (app/components/SblLogo.tsx)
#    Gönderdiğiniz SBL Mavi Lale / Yaprak logosunun yüksek çözünürlüklü SVG hali
# =========================================================================
SBL_LOGO_COMPONENT_TSX = r'''"use client";
import React from 'react';

interface SblLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
}

export default function SblLogo({ size = 'md', showText = true, className = '' }: SblLogoProps) {
  const iconSizes = {
    sm: 'w-9 h-9',
    md: 'w-12 h-12',
    lg: 'w-20 h-20',
    xl: 'w-28 h-28'
  };

  return (
    <div className={`inline-flex items-center gap-3 select-none ${className}`}>
      {/* SBL Mavi Lale ve Yaprak Vektörü (#006bb6) */}
      <div className={`${iconSizes[size]} relative flex-shrink-0 flex items-center justify-center`}>
        <svg viewBox="0 0 220 240" className="w-full h-full drop-shadow-sm" fill="none" xmlns="http://www.w3.org/2000/svg">
          {/* Sol Lale Taç Yaprağı */}
          <path
            d="M66 15 C64 65, 62 110, 102 128 C118 96, 108 48, 66 15 Z"
            fill="#006bb6"
          />
          {/* Sağ Lale Taç Yaprağı */}
          <path
            d="M156 15 C115 48, 105 96, 114 128 C154 112, 160 68, 156 15 Z"
            fill="#006bb6"
          />
          {/* Alt Sol Kıvrımlı Yaprak */}
          <path
            d="M12 88 C28 134, 65 132, 92 178 C98 134, 64 95, 12 88 Z"
            fill="#006bb6"
          />
          {/* Minimalist SBL Tipografi İmzası */}
          <text
            x="104"
            y="188"
            fill="#006bb6"
            fontFamily="Impact, Arial Black, sans-serif"
            fontWeight="900"
            fontSize="58"
            letterSpacing="1"
          >
            SBL
          </text>
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col leading-tight text-left">
          <span className="text-[11px] font-extrabold tracking-wide text-[#006bb6] uppercase">
            Prof. Dr. Mümtaz Turhan
          </span>
          <span className="text-base md:text-lg font-black tracking-tight text-slate-900">
            SOSYAL BİLİMLER LİSESİ
          </span>
          <span className="text-[10px] font-semibold text-slate-500">
            Pansiyon & Yurt Yönetim Portalı
          </span>
        </div>
      )}
    </div>
  );
}
'''

# =========================================================================
# 3. ANA SAYFA VE TÜM ROLLER İÇİN MERKEZİ GİRİŞ PORTALI (app/page.tsx)
# =========================================================================
HOME_PAGE_TSX = r'''"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import SblLogo from './components/SblLogo';

interface StudentRecord {
  id: string;
  name: string;
  cinsiyet: 'erkek' | 'kiz';
  kat: number;
  oda: string;
  anneAdi: string;
  anneTel: string;
  babaAdi: string;
  babaTel: string;
  status: 'var' | 'yok' | 'izinli';
}

interface LeaveRecord {
  id: string;
  studentId: string;
  studentName: string;
  oda: string;
  tip: string;
  baslangic: string;
  bitis: string;
  aciklama: string;
  veliTel: string;
  createdAt: string;
}

export default function UnifiedHomePortal() {
  const router = useRouter();
  const [roleTab, setRoleTab] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');

  // Veli Giriş Durumları
  const [phone, setPhone] = useState('');
  const [otpInput, setOtpInput] = useState('');
  const [generatedOtp, setGeneratedOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp' | 'portal'>('phone');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [infoMsg, setInfoMsg] = useState('');

  // Belletmen Hızlı Giriş Durumları
  const [belletmenList, setBelletmenList] = useState<any[]>([]);
  const [selectedBelId, setSelectedBelId] = useState('');
  const [belPassword, setBelPassword] = useState('');

  // Yönetici Hızlı Giriş Durumu
  const [adminPassword, setAdminPassword] = useState('');

  // Veliye Ait Öğrenci ve İzinler
  const [myStudents, setMyStudents] = useState<StudentRecord[]>([]);
  const [myLeaves, setMyLeaves] = useState<LeaveRecord[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');

  // İzin Formu
  const [leaveType, setLeaveType] = useState('Hafta Sonu Evci İzni');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [leaveNote, setLeaveNote] = useState('');

  useEffect(() => {
    // Belletmen listesini çek
    fetch('/api/pansiyon?t=' + Date.now(), { cache: 'no-store' })
      .then((r) => r.json())
      .then((d) => {
        if (d.success && d.store?.belletmenler) {
          setBelletmenList(d.store.belletmenler);
          if (d.store.belletmenler.length > 0) {
            setSelectedBelId(d.store.belletmenler[0].id);
          }
        }
      })
      .catch(() => {});

    const savedPhone = sessionStorage.getItem('pansiyon_veli_tel');
    if (savedPhone) {
      setPhone(savedPhone);
      setStep('portal');
      loadParentData(savedPhone);
    }
  }, []);

  const loadParentData = async (parentPhone: string) => {
    try {
      const res = await fetch(`/api/pansiyon?veliTel=${encodeURIComponent(parentPhone)}&t=${Date.now()}`, {
        cache: 'no-store'
      });
      const data = await res.json();
      if (data.success && data.store) {
        const list: StudentRecord[] = data.store.students || [];
        if (list.length === 0) {
          sessionStorage.removeItem('pansiyon_veli_tel');
          setStep('phone');
          setErrorMsg('Adınıza kayıtlı öğrenci gözükmemektedir');
          return;
        }
        setMyStudents(list);
        setMyLeaves(data.store.leaves || []);
        if (!selectedStudentId) {
          setSelectedStudentId(list[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  // 1) VELİ WHATSAPP OTP GÖNDERİMİ (Şifre ekranda ASLA görünmez!)
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setInfoMsg('');
    setLoading(true);

    try {
      const verifyRes = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'verify_parent_phone', phone })
      });
      const verifyData = await verifyRes.json();

      if (!verifyRes.ok || !verifyData.success) {
        setErrorMsg(verifyData.message || 'Adınıza kayıtlı öğrenci gözükmemektedir');
        setLoading(false);
        return;
      }

      const secretCode = Math.floor(100000 + Math.random() * 900000).toString();
      setGeneratedOtp(secretCode);

      const childNames = (verifyData.students || []).map((s: any) => s.name).join(', ');
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${childNames}),\nVeli Portalı Giriş Şifreniz: *${secretCode}*\n\n_Güvenliğiniz için bu kodu kimseyle paylaşmayınız._`;

      let sentSuccess = false;

      if (verifyData.tunnelUrl) {
        try {
          const wpRes = await fetch(`${verifyData.tunnelUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code: secretCode, customMessage })
          });
          if (wpRes.ok) sentSuccess = true;
        } catch {}
      }

      if (!sentSuccess) {
        try {
          const localRes = await fetch('http://127.0.0.1:3001/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code: secretCode, customMessage })
          });
          if (localRes.ok) sentSuccess = true;
        } catch {}
      }

      if (!sentSuccess) {
        setErrorMsg('WhatsApp bildirim sunucusuna şu an ulaşılamıyor. Lütfen nöbetçi belletmen veya okul idaresi ile iletişime geçiniz.');
        setLoading(false);
        return;
      }

      setStep('otp');
      setInfoMsg('6 haneli giriş şifreniz cep telefonunuzdaki WhatsApp uygulamasına gönderilmiştir.');
    } catch {
      setErrorMsg('Sunucu bağlantı hatası oluştu.');
    }
    setLoading(false);
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    if (!generatedOtp || otpInput.trim() !== generatedOtp) {
      setErrorMsg('Girdiğiniz doğrulama kodu hatalı! Lütfen WhatsApp mesajınızı kontrol ediniz.');
      return;
    }
    sessionStorage.setItem('pansiyon_veli_tel', phone);
    await loadParentData(phone);
    setStep('portal');
  };

  // 2) BELLETMEN DOĞRUDAN GİRİŞ
  const handleBelletmenLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'belletmen_login', id: selectedBelId, password: belPassword })
      });
      const data = await res.json();
      if (data.success) {
        sessionStorage.setItem('pansiyon_belletmen_session', JSON.stringify({
          belletmen: data.belletmen,
          allowedGender: data.allowedGender
        }));
        router.push('/belletmen');
      } else {
        setErrorMsg(data.message || 'Hatalı belletmen şifresi!');
      }
    } catch {
      setErrorMsg('Giriş yapılırken hata oluştu.');
    }
    setLoading(false);
  };

  // 3) YÖNETİCİ DOĞRUDAN GİRİŞ
  const handleAdminQuickLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'admin_login', username: 'admin', password: adminPassword })
      });
      const data = await res.json();
      if (data.success) {
        sessionStorage.setItem('pansiyon_admin_logged', 'true');
        router.push('/admin');
      } else {
        setErrorMsg(data.message || 'Hatalı yönetici şifresi!');
      }
    } catch {
      setErrorMsg('Bağlantı hatası!');
    }
    setLoading(false);
  };

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedStudentId || !startDate || !endDate) {
      alert('Lütfen başlangıç ve bitiş tarihlerini seçin.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add_leave',
          studentId: selectedStudentId,
          tip: leaveType,
          baslangic: startDate,
          bitis: endDate,
          aciklama: leaveNote || 'Veli Portalı üzerinden izin talebi',
          veliTel: phone
        })
      });
      const data = await res.json();
      if (data.success) {
        setMyStudents(data.store.students || []);
        setMyLeaves(data.store.leaves || []);
        setStartDate('');
        setEndDate('');
        setLeaveNote('');
        alert(data.message || 'İzin talebiniz başarıyla kaydedildi!');
      } else {
        alert(data.message || 'İzin kaydedilemedi.');
      }
    } catch {
      alert('Bağlantı hatası!');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('pansiyon_veli_tel');
    setStep('phone');
    setMyStudents([]);
    setMyLeaves([]);
    setOtpInput('');
    setGeneratedOtp('');
    setInfoMsg('');
    setErrorMsg('');
  };

  const activeStudent = myStudents.find((s) => s.id === selectedStudentId) || myStudents[0];
  const activeStudentLeaves = myLeaves.filter((l) => activeStudent && l.studentId === activeStudent.id);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f0f6ff] via-[#f8fafc] to-white text-slate-800 flex flex-col justify-between">
      {/* MİNİMALİST KURUMSAL ÜST BAR */}
      <header className="bg-white/90 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 px-4 md:px-8 py-3">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-3">
          <SblLogo size="sm" />
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1.5 bg-[#006bb6]/10 text-[#006bb6] px-3 py-1 rounded-full text-xs font-bold">
              <span className="w-2 h-2 rounded-full bg-[#006bb6] animate-pulse" />
              7/24 Bulut Senkronizasyon
            </span>
            <button
              onClick={() => router.push('/belletmen')}
              className="text-xs font-bold text-slate-600 hover:text-[#006bb6] px-3 py-1.5 rounded-lg hover:bg-slate-100 transition"
            >
              Belletmen Ekranı
            </button>
            <button
              onClick={() => router.push('/admin')}
              className="text-xs font-bold text-slate-600 hover:text-[#006bb6] px-3 py-1.5 rounded-lg hover:bg-slate-100 transition"
            >
              İdare Paneli
            </button>
          </div>
        </div>
      </header>

      {/* ANA İÇERİK */}
      <main className="flex-1 flex items-center justify-center p-4 md:p-8">
        {step !== 'portal' ? (
          <div className="bg-white rounded-3xl shadow-2xl shadow-blue-950/5 border border-slate-200/80 max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden">
            {/* SOL KURUMSAL LOGO PANELİ */}
            <div className="md:col-span-5 bg-gradient-to-br from-[#eef6ff] via-[#e0effe] to-[#d0e6fd] p-8 flex flex-col items-center justify-center text-center relative overflow-hidden">
              <div className="bg-white/95 backdrop-blur p-6 rounded-3xl shadow-lg border border-white mb-5">
                <SblLogo size="xl" showText={false} />
              </div>
              <p className="text-xs font-extrabold tracking-widest text-[#006bb6] uppercase">
                Prof. Dr. Mümtaz Turhan
              </p>
              <h2 className="text-xl font-black text-slate-900 tracking-tight mt-0.5">
                SOSYAL BİLİMLER LİSESİ
              </h2>
              <p className="text-xs font-semibold text-slate-600 mt-1 mb-5">
                Pansiyon & Yurt Yönetim Sistemi
              </p>

              <div className="w-full space-y-2 text-left bg-white/70 backdrop-blur-sm p-4 rounded-2xl border border-white/80 text-[11px] text-slate-600 font-medium">
                <div className="flex items-center gap-2">
                  <span className="text-[#006bb6] font-bold">✓</span> KVKK Korumalı Kişisel Veli İzin Sistemi
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#006bb6] font-bold">✓</span> Kat & Oda Bazlı Dijital Belletmen Yoklaması
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#006bb6] font-bold">✓</span> Anlık WhatsApp Veli Devamsızlık Bildirimi
                </div>
              </div>
            </div>

            {/* SAĞ GİRİŞ PANELİ */}
            <div className="md:col-span-7 p-8 md:p-10 flex flex-col justify-center">
              <div className="text-center mb-6">
                <h1 className="text-2xl font-extrabold text-slate-900">Sisteme Giriş Yapın</h1>
                <p className="text-xs text-slate-500 mt-1">
                  Lütfen işlem yapmak istediğiniz kullanıcı rolünü seçiniz.
                </p>
              </div>

              {/* 3'LÜ ROL SEÇİM SEKMESİ */}
              <div className="grid grid-cols-3 bg-slate-100 p-1.5 rounded-2xl mb-6 text-xs font-bold">
                <button
                  type="button"
                  onClick={() => { setRoleTab('veli'); setErrorMsg(''); setInfoMsg(''); }}
                  className={`py-2.5 rounded-xl transition ${
                    roleTab === 'veli' ? 'bg-white text-[#006bb6] shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  👥 Veli Girişi
                </button>
                <button
                  type="button"
                  onClick={() => { setRoleTab('belletmen'); setErrorMsg(''); setInfoMsg(''); }}
                  className={`py-2.5 rounded-xl transition ${
                    roleTab === 'belletmen' ? 'bg-white text-[#006bb6] shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  👨‍🏫 Belletmen
                </button>
                <button
                  type="button"
                  onClick={() => { setRoleTab('yonetici'); setErrorMsg(''); setInfoMsg(''); }}
                  className={`py-2.5 rounded-xl transition ${
                    roleTab === 'yonetici' ? 'bg-white text-[#006bb6] shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  🛡️ Yönetici
                </button>
              </div>

              {/* HATA VE BİLGİ KUTULARI */}
              {errorMsg && (
                <div className="mb-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold text-center">
                  ⚠️ {errorMsg}
                </div>
              )}
              {infoMsg && (
                <div className="mb-4 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold text-center">
                  📲 {infoMsg}
                </div>
              )}

              {/* SEKMELERE GÖRE FORM İÇERİĞİ */}
              {roleTab === 'veli' && (
                step === 'phone' ? (
                  <form onSubmit={handleSendOtp} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">
                        Sistemde Kayıtlı Veli Cep Telefonu Numaranız
                      </label>
                      <input
                        type="tel"
                        required
                        placeholder="05XX XXX XX XX"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold tracking-wider focus:outline-none focus:ring-2 focus:ring-[#006bb6]"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-[#006bb6] hover:bg-[#005694] text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition"
                    >
                      {loading ? 'Öğrenci Kaydı Kontrol Ediliyor...' : '📲 WhatsApp İle Tek Kullanımlık Şifre Gönder'}
                    </button>
                  </form>
                ) : (
                  <form onSubmit={handleVerifyOtp} className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1.5 text-center">
                        WhatsApp Mesajınıza Gelen 6 Haneli Kodu Giriniz
                      </label>
                      <input
                        type="text"
                        required
                        maxLength={6}
                        placeholder="••••••"
                        value={otpInput}
                        onChange={(e) => setOtpInput(e.target.value)}
                        className="w-full p-3.5 border border-emerald-400 rounded-xl text-center text-2xl font-extrabold tracking-widest focus:outline-none focus:ring-2 focus:ring-emerald-600"
                      />
                    </div>
                    <button
                      type="submit"
                      className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition"
                    >
                      ✅ Doğrula ve Öğrenci Bilgilerimi Aç
                    </button>
                    <button
                      type="button"
                      onClick={() => { setStep('phone'); setInfoMsg(''); setErrorMsg(''); setOtpInput(''); }}
                      className="w-full text-xs text-slate-500 hover:text-slate-800 underline py-1"
                    >
                      Telefon numarasını değiştir
                    </button>
                  </form>
                )
              )}

              {roleTab === 'belletmen' && (
                <form onSubmit={handleBelletmenLogin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5">
                      Nöbetçi Belletmen Öğretmen Seçiniz
                    </label>
                    <select
                      value={selectedBelId}
                      onChange={(e) => setSelectedBelId(e.target.value)}
                      className="w-full p-3.5 border border-slate-300 rounded-xl font-bold text-sm bg-white"
                    >
                      {belletmenList.length === 0 ? (
                        <option value="">Henüz belletmen eklenmemiş (İdare panelinden ekleyiniz)</option>
                      ) : (
                        belletmenList.map((b) => (
                          <option key={b.id} value={b.id}>
                            {b.cinsiyet === 'kadin' ? '👩 ' : '👨 '} {b.name} ({b.brans})
                          </option>
                        ))
                      )}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5">
                      Belletmen Giriş Şifreniz
                    </label>
                    <input
                      type="password"
                      required
                      placeholder="••••"
                      value={belPassword}
                      onChange={(e) => setBelPassword(e.target.value)}
                      className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold focus:outline-none focus:ring-2 focus:ring-[#006bb6]"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading || belletmenList.length === 0}
                    className="w-full bg-[#006bb6] hover:bg-[#005694] text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition"
                  >
                    {loading ? 'Giriş Yapılıyor...' : '👨‍🏫 Yoklama ve Nöbet Ekranını Aç'}
                  </button>
                </form>
              )}

              {roleTab === 'yonetici' && (
                <form onSubmit={handleAdminQuickLogin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">
                      Pansiyon İdaresi Yetkili Şifresi
                    </label>
                    <input
                      type="password"
                      required
                      placeholder="Yönetici Şifresi"
                      value={adminPassword}
                      onChange={(e) => setAdminPassword(e.target.value)}
                      className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold focus:outline-none focus:ring-2 focus:ring-[#006bb6]"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-slate-900 hover:bg-slate-800 text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition"
                  >
                    {loading ? 'Doğrulanıyor...' : '🛡️ Yönetim Paneline Giriş Yap'}
                  </button>
                </form>
              )}

              <div className="mt-8 pt-4 border-t border-slate-100 text-center text-[11px] text-slate-400">
                © 2026 Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi
              </div>
            </div>
          </div>
        ) : (
          /* VELİ ÖZEL PORTALI (SADECE KENDİ ÖĞRENCİSİ) */
          <div className="max-w-5xl w-full space-y-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex flex-wrap justify-between items-center gap-4">
              <div>
                <span className="text-xs font-bold uppercase text-emerald-600">
                  ✅ Doğrulanmış Veli Oturumu ({phone})
                </span>
                <h2 className="text-xl font-extrabold text-slate-900">
                  Öğrenci Bilgileri, İstatistikler ve İzin Paneli
                </h2>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => loadParentData(phone)}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold transition"
                >
                  🔄 Yenile
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-xl text-xs font-bold transition"
                >
                  Çıkış Yap
                </button>
              </div>
            </div>

            {myStudents.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-1">
                {myStudents.map((st) => (
                  <button
                    key={st.id}
                    onClick={() => setSelectedStudentId(st.id)}
                    className={`px-4 py-2 rounded-xl font-bold text-xs transition ${
                      activeStudent?.id === st.id
                        ? 'bg-[#006bb6] text-white shadow'
                        : 'bg-white border text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    👤 {st.name} (Oda {st.oda})
                  </button>
                ))}
              </div>
            )}

            {activeStudent && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-4">
                  <div className="flex items-center justify-between border-b pb-3">
                    <div>
                      <span className="text-[11px] font-bold uppercase text-[#006bb6]">Öğrenciniz</span>
                      <h3 className="text-xl font-extrabold text-slate-900">{activeStudent.name}</h3>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold ${
                        activeStudent.status === 'var'
                          ? 'bg-emerald-100 text-emerald-800'
                          : activeStudent.status === 'izinli'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {activeStudent.status === 'var'
                        ? '🟢 Yurtta (Var)'
                        : activeStudent.status === 'izinli'
                        ? '🟡 İzinli'
                        : '🔴 Yoklamada Yok'}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-slate-400 block">Pansiyon Bloğu</span>
                      <strong className="text-slate-800">
                        {activeStudent.cinsiyet === 'kiz' ? 'Kız Pansiyonu' : 'Erkek Pansiyonu'}
                      </strong>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border">
                      <span className="text-slate-400 block">Kat / Oda</span>
                      <strong className="text-slate-800">
                        {activeStudent.kat}. Kat - Oda {activeStudent.oda}
                      </strong>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-xl border border-blue-100 col-span-2">
                      <span className="text-[#006bb6] block">Toplam Kullanılan İzin Sayısı</span>
                      <strong className="text-base font-extrabold text-slate-900">
                        {activeStudentLeaves.length} İzin Kaydı
                      </strong>
                    </div>
                  </div>
                </div>

                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
                    <h3 className="text-base font-extrabold text-slate-900 mb-1">
                      📝 {activeStudent.name} İçin İzin Talebi Gönder
                    </h3>
                    <p className="text-xs text-slate-500 mb-4">
                      Bu ekrandan yalnızca kendi öğrenciniz için izin talebi oluşturabilirsiniz.
                    </p>
                    <form onSubmit={handleCreateLeave} className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">Öğrenci</label>
                        <input
                          type="text"
                          disabled
                          value={`${activeStudent.name} (Oda ${activeStudent.oda})`}
                          className="w-full p-2.5 bg-slate-100 border rounded-xl font-bold text-slate-700"
                        />
                      </div>
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">İzin Türü</label>
                        <select
                          value={leaveType}
                          onChange={(e) => setLeaveType(e.target.value)}
                          className="w-full p-2.5 border rounded-xl font-semibold"
                        >
                          <option value="Hafta Sonu Evci İzni">Hafta Sonu Evci İzni</option>
                          <option value="Aile Yanı Ev İzni">Aile Yanı Ev İzni</option>
                          <option value="Sağlık / Hastane İzni">Sağlık / Hastane İzni</option>
                          <option value="Çarşı / Kurs İzni">Çarşı / Kurs İzni</option>
                        </select>
                      </div>
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">Başlangıç Tarihi</label>
                        <input
                          type="date"
                          required
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="w-full p-2.5 border rounded-xl"
                        />
                      </div>
                      <div>
                        <label className="font-bold text-slate-600 block mb-1">Dönüş Tarihi</label>
                        <input
                          type="date"
                          required
                          value={endDate}
                          onChange={(e) => setEndDate(e.target.value)}
                          className="w-full p-2.5 border rounded-xl"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="font-bold text-slate-600 block mb-1">Açıklama / Adres</label>
                        <input
                          type="text"
                          required
                          placeholder="İzin süresince bulunacağı adres veya açıklama..."
                          value={leaveNote}
                          onChange={(e) => setLeaveNote(e.target.value)}
                          className="w-full p-2.5 border rounded-xl"
                        />
                      </div>
                      <div className="md:col-span-2 flex justify-end">
                        <button
                          type="submit"
                          disabled={loading}
                          className="bg-[#006bb6] hover:bg-[#005694] text-white px-6 py-2.5 rounded-xl font-bold shadow transition"
                        >
                          {loading ? 'Kaydediliyor...' : '✅ İzin Talebini Onayla'}
                        </button>
                      </div>
                    </form>
                  </div>

                  <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
                    <h3 className="text-base font-extrabold text-slate-900 mb-3">
                      📅 {activeStudent.name} - Geçmiş İzinleri ({activeStudentLeaves.length})
                    </h3>
                    {activeStudentLeaves.length === 0 ? (
                      <p className="text-xs text-slate-400 italic">Henüz izin kaydı bulunmamaktadır.</p>
                    ) : (
                      <div className="space-y-2 text-xs">
                        {activeStudentLeaves.map((lv) => (
                          <div key={lv.id} className="p-3 border rounded-xl bg-slate-50 flex justify-between items-center">
                            <div>
                              <span className="font-bold text-[#006bb6]">{lv.tip}</span>
                              <p className="text-slate-600 mt-0.5">{lv.aciklama}</p>
                            </div>
                            <div className="text-right font-semibold text-slate-500">
                              {lv.baslangic} → {lv.bitis}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="border-t border-slate-200 bg-white px-6 py-3 text-[11px] text-slate-400">
        <div className="max-w-6xl mx-auto flex justify-between">
          <span>© 2026 Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Pansiyonu</span>
          <span>Neon Bulut Veritabanı • KVKK Uyumlu</span>
        </div>
      </footer>
    </div>
  );
}
'''

# =========================================================================
# 4. MODERN BELLETMEN YOKLAMA VE NÖBET MODÜLÜ (app/belletmen/page.tsx)
# =========================================================================
BELLETMEN_PAGE_TSX = r'''"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import SblLogo from '../components/SblLogo';

export default function BelletmenPage() {
  const [store, setStore] = useState<any>(null);
  const [loggedBelletmen, setLoggedBelletmen] = useState<any>(null);
  const [allowedGender, setAllowedGender] = useState<'erkek' | 'kiz'>('erkek');

  // Giriş Formu
  const [selectedId, setSelectedId] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [infoMsg, setInfoMsg] = useState('');

  // Yoklama Filtreleri
  const [selectedKat, setSelectedKat] = useState<number | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState<'yoklama' | 'defter' | 'izinler'>('yoklama');
  const [saving, setSaving] = useState(false);

  // Nöbet Defteri Formu
  const [dutyLogForm, setDutyLogForm] = useState({
    tarih: new Date().toISOString().split('T')[0],
    seans: 'Gece Yat Yoklaması (22:00)',
    erkekBelletmen1: '',
    erkekBelletmen2: '',
    kizBelletmen1: '',
    kizBelletmen2: '',
    notlar: ''
  });

  const loadData = async (genderFilter?: 'erkek' | 'kiz') => {
    const g = genderFilter || allowedGender;
    const url = loggedBelletmen
      ? `/api/pansiyon?cinsiyet=${g}&t=${Date.now()}`
      : `/api/pansiyon?t=${Date.now()}`;
    const res = await fetch(url, { cache: 'no-store' });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      if (!selectedId && data.store?.belletmenler?.length > 0) {
        setSelectedId(data.store.belletmenler[0].id);
      }
    }
  };

  useEffect(() => {
    const saved = sessionStorage.getItem('pansiyon_belletmen_session');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setLoggedBelletmen(parsed.belletmen);
        setAllowedGender(parsed.allowedGender);
        loadData(parsed.allowedGender);
        return;
      } catch {}
    }
    loadData();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'belletmen_login', id: selectedId, password })
    });
    const data = await res.json();
    if (data.success) {
      setLoggedBelletmen(data.belletmen);
      setAllowedGender(data.allowedGender);
      sessionStorage.setItem('pansiyon_belletmen_session', JSON.stringify({
        belletmen: data.belletmen,
        allowedGender: data.allowedGender
      }));
      loadData(data.allowedGender);
    } else {
      setErrorMsg(data.message || 'Hatalı şifre!');
    }
  };

  const handleForgotPassword = async () => {
    if (!selectedId) return;
    setErrorMsg('');
    setInfoMsg('');
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'log_forgot_password', id: selectedId })
    });
    const data = await res.json();
    if (data.success && data.belletmen) {
      const msg = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın ${data.belletmen.name},\nBelletmen Yoklama Ekranı Giriş Şifreniz: *${data.belletmen.password}*`;
      let sent = false;
      if (data.tunnelUrl) {
        try {
          const r = await fetch(`${data.tunnelUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: data.belletmen.phone, code: data.belletmen.password, customMessage: msg })
          });
          if (r.ok) sent = true;
        } catch {}
      }
      if (sent) setInfoMsg('Şifreniz kayıtlı WhatsApp numaranıza gönderildi.');
      else setErrorMsg('WhatsApp sunucusu kapalı olduğu için gönderilemedi.');
    }
  };

  const handleStatusChange = async (studentId: string, newStatus: 'var' | 'yok' | 'izinli') => {
    if (!store?.students) return;
    const updatedStudents = store.students.map((s: any) =>
      s.id === studentId ? { ...s, status: newStatus } : s
    );
    setStore({ ...store, students: updatedStudents });
    setSaving(true);
    await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'update_attendance', students: updatedStudents })
    });
    setSaving(false);
  };

  const sendAbsenceWhatsApp = async (student: any, parentType: 'anne' | 'baba') => {
    const targetPhone = parentType === 'anne' ? student.anneTel : student.babaTel;
    const parentName = parentType === 'anne' ? student.anneAdi : student.babaAdi;
    if (!targetPhone) {
      alert('Bu velinin telefon numarası sistemde kayıtlı değil!');
      return;
    }
    const text = `*Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Pansiyonu*\n\nSayın ${parentName || 'Velimiz'},\nÖğrencimiz *${student.name}* (Oda ${student.oda}), ${new Date().toLocaleDateString('tr-TR')} tarihli pansiyon yoklamasında *YOK* olarak işaretlenmiştir.\n\nBilgilerinize sunar, acil durumda nöbetçi belletmen öğretmenimizle iletişime geçmenizi rica ederiz.`;

    let sent = false;
    if (store?.tunnelUrl) {
      try {
        const r = await fetch(`${store.tunnelUrl}/send-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: targetPhone, code: 'YOKLAMA', customMessage: text })
        });
        if (r.ok) sent = true;
      } catch {}
    }
    if (sent) {
      alert(`✅ ${student.name} için ${parentType.toUpperCase()} numarasına (${targetPhone}) WhatsApp devamsızlık bildirimi gönderildi!`);
    } else {
      alert('WhatsApp Botu kapalı! Doğrudan WhatsApp Web penceresi açılıyor...');
      const clean = String(targetPhone).replace(/\D/g, '').slice(-10);
      window.open(`https://wa.me/90${clean}?text=${encodeURIComponent(text)}`, '_blank');
    }
  };

  const handleSaveDutyLog = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_duty_log', ...dutyLogForm })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setDutyLogForm({ ...dutyLogForm, notlar: '' });
      alert('Resmî nöbet tutanağı kaydedildi!');
    }
  };

  if (!loggedBelletmen) {
    return (
      <div className="min-h-screen bg-[#f4f8fc] flex flex-col justify-between">
        <header className="bg-white border-b px-6 py-3 flex justify-between items-center">
          <SblLogo size="sm" />
          <Link href="/" className="text-xs font-bold text-[#006bb6] hover:underline">
            ← Ana Sayfaya Dön
          </Link>
        </header>
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="bg-white p-8 rounded-3xl shadow-xl border max-w-md w-full">
            <div className="flex justify-center mb-4">
              <SblLogo size="md" showText={false} />
            </div>
            <h1 className="text-xl font-extrabold text-center text-slate-900">Nöbetçi Belletmen Girişi</h1>
            <p className="text-xs text-center text-slate-500 mb-6">
              Kız ve Erkek pansiyonu yoklama ekranları KVKK gereği izole edilmiştir.
            </p>
            {errorMsg && <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold rounded-xl text-center">{errorMsg}</div>}
            {infoMsg && <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold rounded-xl text-center">{infoMsg}</div>}
            <form onSubmit={handleLogin} className="space-y-4">
              <select
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
                className="w-full p-3.5 border rounded-xl font-bold text-sm"
              >
                {(store?.belletmenler || []).map((b: any) => (
                  <option key={b.id} value={b.id}>
                    {b.cinsiyet === 'kadin' ? '👩 ' : '👨 '} {b.name} ({b.brans})
                  </option>
                ))}
              </select>
              <input
                type="password"
                required
                placeholder="Şifreniz"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3.5 border rounded-xl text-center text-lg font-bold"
              />
              <button type="submit" className="w-full bg-[#006bb6] hover:bg-[#005694] text-white py-3.5 rounded-xl font-bold text-sm shadow">
                Yoklama Ekranına Gir
              </button>
              <button
                type="button"
                onClick={handleForgotPassword}
                className="w-full text-xs text-[#006bb6] font-semibold hover:underline py-1"
              >
                📲 Şifremi Unuttum (WhatsApp Gönder)
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  const allStudents = (store?.students || []).filter((s: any) => s.cinsiyet === allowedGender);
  const filteredStudents = allStudents.filter((s: any) => {
    const katMatch = selectedKat === 'all' || Number(s.kat) === Number(selectedKat);
    const searchMatch =
      !searchTerm ||
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(s.oda).toLowerCase().includes(searchTerm.toLowerCase());
    return katMatch && searchMatch;
  });

  const varCount = allStudents.filter((s: any) => s.status === 'var').length;
  const yokCount = allStudents.filter((s: any) => s.status === 'yok').length;
  const izinCount = allStudents.filter((s: any) => s.status === 'izinli').length;

  return (
    <div className="min-h-screen bg-[#f4f8fc] text-slate-800">
      <header className="bg-white border-b sticky top-0 z-20 px-4 md:px-8 py-3">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-3">
          <div className="flex items-center gap-3">
            <SblLogo size="sm" showText={false} />
            <div>
              <span className="text-xs font-extrabold uppercase text-[#006bb6]">
                {allowedGender === 'kiz' ? '👩 KIZ PANSİYONU' : '👨 ERKEK PANSİYONU'} NÖBET EKRANI
              </span>
              <h1 className="text-base font-black text-slate-900">{loggedBelletmen.name}</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {saving && <span className="text-xs font-bold text-amber-600 animate-pulse">💾 Kaydediliyor...</span>}
            <button
              onClick={() => loadData(allowedGender)}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-2 rounded-xl text-xs font-bold"
            >
              🔄 Listeyi Yenile
            </button>
            <button
              onClick={() => { sessionStorage.removeItem('pansiyon_belletmen_session'); setLoggedBelletmen(null); }}
              className="bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-2 rounded-xl text-xs font-bold"
            >
              Çıkış
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4 md:p-6 space-y-6">
        {/* ÖZET İSTATİSTİK KARTLARI */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-2xl border shadow-sm">
            <span className="text-xs text-slate-400 font-bold">Toplam Öğrenci</span>
            <p className="text-2xl font-black text-slate-900">{allStudents.length}</p>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-2xl">
            <span className="text-xs text-emerald-700 font-bold">🟢 Yurtta (Var)</span>
            <p className="text-2xl font-black text-emerald-900">{varCount}</p>
          </div>
          <div className="bg-rose-50 border border-rose-200 p-4 rounded-2xl">
            <span className="text-xs text-rose-700 font-bold">🔴 Yoklamada Yok</span>
            <p className="text-2xl font-black text-rose-900">{yokCount}</p>
          </div>
          <div className="bg-amber-50 border border-amber-200 p-4 rounded-2xl">
            <span className="text-xs text-amber-700 font-bold">🟡 Evci / İzinli</span>
            <p className="text-2xl font-black text-amber-900">{izinCount}</p>
          </div>
        </div>

        {/* MODÜL SEKMELERİ */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setActiveTab('yoklama')}
            className={`px-5 py-2.5 rounded-xl font-bold text-xs transition ${
              activeTab === 'yoklama' ? 'bg-[#006bb6] text-white shadow' : 'bg-white border text-slate-600'
            }`}
          >
            📋 Kat & Oda Yoklaması ({allStudents.length})
          </button>
          <button
            onClick={() => setActiveTab('defter')}
            className={`px-5 py-2.5 rounded-xl font-bold text-xs transition ${
              activeTab === 'defter' ? 'bg-[#006bb6] text-white shadow' : 'bg-white border text-slate-600'
            }`}
          >
            📖 Pansiyon Nöbet Defteri ({store?.dutyLogs?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('izinler')}
            className={`px-5 py-2.5 rounded-xl font-bold text-xs transition ${
              activeTab === 'izinler' ? 'bg-[#006bb6] text-white shadow' : 'bg-white border text-slate-600'
            }`}
          >
            🟡 İzinli Öğrenci Listesi ({store?.leaves?.length || 0})
          </button>
        </div>

        {activeTab === 'yoklama' && (
          <div className="space-y-4">
            {/* KAT FİLTRESİ VE ARAMA */}
            <div className="bg-white p-4 rounded-2xl border shadow-sm flex flex-wrap justify-between items-center gap-3">
              <div className="flex flex-wrap gap-1.5">
                {(['all', 1, 2, 3, 4] as const).map((k) => (
                  <button
                    key={String(k)}
                    onClick={() => setSelectedKat(k)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-bold transition ${
                      selectedKat === k ? 'bg-[#006bb6] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {k === 'all' ? 'Tüm Katlar' : `${k}. Kat`}
                  </button>
                ))}
              </div>
              <input
                type="text"
                placeholder="🔍 Öğrenci adı veya oda ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="p-2.5 border rounded-xl text-xs w-full sm:w-64"
              />
            </div>

            {/* ÖĞRENCİ YOKLAMA KARTLARI */}
            {filteredStudents.length === 0 ? (
              <div className="bg-white p-10 rounded-2xl border text-center text-slate-400 text-sm">
                Bu filtrede kayıtlı öğrenci bulunmamaktadır.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filteredStudents.map((st: any) => (
                  <div
                    key={st.id}
                    className={`bg-white rounded-2xl border p-4 shadow-sm transition ${
                      st.status === 'yok' ? 'border-rose-400 ring-2 ring-rose-100' : 'border-slate-200'
                    }`}
                  >
                    <div className="flex justify-between items-start gap-2">
                      <div>
                        <span className="text-[11px] font-bold bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full">
                          {st.kat}. Kat • Oda {st.oda}
                        </span>
                        <h3 className="text-base font-extrabold text-slate-900 mt-1">{st.name}</h3>
                      </div>
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleStatusChange(st.id, 'var')}
                          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                            st.status === 'var'
                              ? 'bg-emerald-600 text-white shadow'
                              : 'bg-slate-100 text-slate-600 hover:bg-emerald-50'
                          }`}
                        >
                          Var
                        </button>
                        <button
                          onClick={() => handleStatusChange(st.id, 'yok')}
                          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                            st.status === 'yok'
                              ? 'bg-rose-600 text-white shadow'
                              : 'bg-slate-100 text-slate-600 hover:bg-rose-50'
                          }`}
                        >
                          Yok
                        </button>
                        <button
                          onClick={() => handleStatusChange(st.id, 'izinli')}
                          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
                            st.status === 'izinli'
                              ? 'bg-amber-500 text-white shadow'
                              : 'bg-slate-100 text-slate-600 hover:bg-amber-50'
                          }`}
                        >
                          İzinli
                        </button>
                      </div>
                    </div>

                    {/* YOK SEÇİLDİĞİNDE AÇILAN WHATSAPP VELİ BİLDİRİM ÇUBUĞU */}
                    {st.status === 'yok' && (
                      <div className="mt-3 pt-3 border-t border-rose-100 bg-rose-50/60 p-2.5 rounded-xl flex flex-wrap justify-between items-center gap-2">
                        <span className="text-[11px] font-bold text-rose-800">
                          🚨 Veliye WhatsApp Devamsızlık Mesajı:
                        </span>
                        <div className="flex gap-1.5">
                          <button
                            onClick={() => sendAbsenceWhatsApp(st, 'anne')}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold"
                          >
                            📲 Anneye Gönder ({st.anneTel || 'Yok'})
                          </button>
                          <button
                            onClick={() => sendAbsenceWhatsApp(st, 'baba')}
                            className="bg-[#006bb6] hover:bg-[#005694] text-white px-2.5 py-1 rounded-lg text-[11px] font-bold"
                          >
                            📲 Babaya Gönder ({st.babaTel || 'Yok'})
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'defter' && (
          <div className="bg-white p-6 rounded-2xl border shadow-sm space-y-4">
            <h2 className="text-base font-extrabold text-slate-900">📖 Resmî Pansiyon Nöbet Defteri Tutanağı Ekle</h2>
            <form onSubmit={handleSaveDutyLog} className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
              <input type="date" value={dutyLogForm.tarih} onChange={(e) => setDutyLogForm({ ...dutyLogForm, tarih: e.target.value })} className="p-2.5 border rounded-xl" />
              <select value={dutyLogForm.seans} onChange={(e) => setDutyLogForm({ ...dutyLogForm, seans: e.target.value })} className="p-2.5 border rounded-xl font-bold md:col-span-3">
                <option value="1. Etüt Yoklaması (19:30)">1. Etüt Yoklaması (19:30)</option>
                <option value="2. Etüt Yoklaması (20:30)">2. Etüt Yoklaması (20:30)</option>
                <option value="Gece Yat Yoklaması (22:00)">Gece Yat Yoklaması (22:00)</option>
              </select>
              <input placeholder="Erkek Belletmen 1 Adı" value={dutyLogForm.erkekBelletmen1} onChange={(e) => setDutyLogForm({ ...dutyLogForm, erkekBelletmen1: e.target.value })} className="p-2.5 border rounded-xl" />
              <input placeholder="Erkek Belletmen 2 Adı" value={dutyLogForm.erkekBelletmen2} onChange={(e) => setDutyLogForm({ ...dutyLogForm, erkekBelletmen2: e.target.value })} className="p-2.5 border rounded-xl" />
              <input placeholder="Kız Belletmen 1 Adı" value={dutyLogForm.kizBelletmen1} onChange={(e) => setDutyLogForm({ ...dutyLogForm, kizBelletmen1: e.target.value })} className="p-2.5 border rounded-xl" />
              <input placeholder="Kız Belletmen 2 Adı" value={dutyLogForm.kizBelletmen2} onChange={(e) => setDutyLogForm({ ...dutyLogForm, kizBelletmen2: e.target.value })} className="p-2.5 border rounded-xl" />
              <textarea rows={3} placeholder="Nöbet vukuat ve yoklama notları..." value={dutyLogForm.notlar} onChange={(e) => setDutyLogForm({ ...dutyLogForm, notlar: e.target.value })} className="md:col-span-4 p-2.5 border rounded-xl" />
              <div className="md:col-span-4 flex justify-end">
                <button type="submit" className="bg-[#006bb6] text-white px-6 py-2.5 rounded-xl font-bold">
                  Tutanağı Kaydet
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'izinler' && (
          <div className="bg-white p-6 rounded-2xl border shadow-sm space-y-3">
            <h2 className="text-base font-extrabold text-slate-900">🟡 Veli Onaylı İzinli Öğrenciler</h2>
            {(store?.leaves || []).length === 0 ? (
              <p className="text-xs text-slate-400 italic">Kayıtlı izin bulunmamaktadır.</p>
            ) : (
              (store?.leaves || []).map((lv: any) => (
                <div key={lv.id} className="p-3 border rounded-xl bg-amber-50/40 flex justify-between items-center text-xs">
                  <div>
                    <strong className="text-slate-900">{lv.studentName} (Oda {lv.oda})</strong>
                    <span className="ml-2 bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">{lv.tip}</span>
                    <p className="text-slate-600 mt-1">{lv.aciklama}</p>
                  </div>
                  <div className="text-right font-bold text-slate-600">
                    {lv.baslangic} → {lv.bitis}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
'''

# =========================================================================
# 5. TAM KAPSAMLI YÖNETİCİ PANELİ (app/admin/page.tsx)
#    - SBL Logolu, Nöbet & Nöbet Defteri İsim Düzenlemeli, Otomatik Numarasız!
# =========================================================================
ADMIN_PAGE_TSX = r'''"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import SblLogo from '../components/SblLogo';

export default function AdminPage() {
  const [store, setStore] = useState<any>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState<'ogrenciler' | 'belletmenler' | 'nobet' | 'defter' | 'loglar'>('ogrenciler');
  const [loading, setLoading] = useState(false);

  // Öğrenci Formu (Varsayılan telefonlar tamamen BOŞ!)
  const [stForm, setStForm] = useState({
    name: '', cinsiyet: 'erkek', kat: '1', oda: '101',
    anneAdi: '', anneTel: '', babaAdi: '', babaTel: ''
  });
  const [bulkText, setBulkText] = useState('');

  // Belletmen Formu
  const [belForm, setBelForm] = useState({
    name: '', cinsiyet: 'erkek', brans: '', phone: '', password: '1234'
  });

  // Aylık Nöbet Formu + Düzenleme Modu
  const [dutyForm, setDutyForm] = useState({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' });
  const [isEditingDuty, setIsEditingDuty] = useState(false);

  // Nöbet Defteri (Tutanak) Düzenleme Modu
  const [editingLog, setEditingLog] = useState<any>(null);

  const fetchStore = async () => {
    try {
      const res = await fetch('/api/pansiyon?t=' + Date.now(), { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setStore(data.store);
      }
    } catch (error) {
      console.error('Veri çekme hatası:', error);
    }
  };

  useEffect(() => {
    if (sessionStorage.getItem('pansiyon_admin_logged') === 'true') {
      setIsLoggedIn(true);
    }
  }, []);

  useEffect(() => {
    if (isLoggedIn) fetchStore();
  }, [isLoggedIn]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'admin_login', username: 'admin', password })
      });
      const data = await res.json();
      if (data.success) {
        sessionStorage.setItem('pansiyon_admin_logged', 'true');
        setIsLoggedIn(true);
        setStore(data.store);
      } else {
        alert(data.message || 'Hatalı şifre!');
      }
    } catch {
      alert('Giriş yapılamadı.');
    }
    setLoading(false);
  };

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_student', ...stForm })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setStForm({ name: '', cinsiyet: 'erkek', kat: '1', oda: '101', anneAdi: '', anneTel: '', babaAdi: '', babaTel: '' });
    }
    setLoading(false);
  };

  // Excel'den Kopyala-Yapıştır ile Toplu Öğrenci Yükleme (Numara boşsa boş kalır!)
  const handleBulkPasteImport = async () => {
    if (!bulkText.trim()) return;
    const lines = bulkText.trim().split('\n');
    const rows = lines.map((line) => {
      const parts = line.split(/\t|;|,/);
      return {
        name: (parts[0] || '').trim(),
        cinsiyet: (parts[1] || 'Erkek').trim(),
        kat: (parts[2] || '1').trim(),
        oda: (parts[3] || '101').trim(),
        anneAdi: (parts[4] || '').trim(),
        anneTel: (parts[5] || '').trim(),
        babaAdi: (parts[6] || '').trim(),
        babaTel: (parts[7] || '').trim()
      };
    }).filter((r) => r.name.length > 1);

    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setBulkText('');
      alert(data.message);
    }
    setLoading(false);
  };

  const handleClearAllStudents = async () => {
    if (!confirm('Tüm öğrenci listesini ve eski test numaralarını sıfırlamak istediğinize emin misiniz?')) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'clear_all_students' })
    });
    const data = await res.json();
    if (data.success) setStore(data.store);
  };

  const handleDeleteStudent = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_student', id })
    });
    const data = await res.json();
    if (data.success) setStore(data.store);
  };

  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_belletmen', ...belForm })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setBelForm({ name: '', cinsiyet: 'erkek', brans: '', phone: '', password: '1234' });
    }
    setLoading(false);
  };

  const handleDeleteBelletmen = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_belletmen', id })
    });
    const data = await res.json();
    if (data.success) setStore(data.store);
  };

  const handleDutySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_or_update_monthly_duty', ...dutyForm })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setDutyForm({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' });
      setIsEditingDuty(false);
    }
    setLoading(false);
  };

  const handleUpdateDutyLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingLog) return;
    setLoading(true);
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'update_duty_log', ...editingLog })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      setEditingLog(null);
      alert('Nöbet defterindeki belletmen isimleri güncellendi!');
    }
    setLoading(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f0f6ff] p-4">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-3xl shadow-xl border w-full max-w-md text-center">
          <div className="flex justify-center mb-4">
            <SblLogo size="lg" showText={false} />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900">SBL Pansiyon İdare Paneli</h2>
          <p className="text-xs text-slate-500 mt-1 mb-6">Öğrenci, Belletmen ve Nöbet Defteri Yönetimi</p>
          <input
            type="password"
            placeholder="Yönetici Şifresi"
            className="w-full p-3.5 border rounded-xl mb-4 text-center text-lg font-bold focus:outline-none focus:ring-2 focus:ring-[#006bb6]"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit" disabled={loading} className="w-full bg-[#006bb6] text-white p-3.5 rounded-xl font-bold hover:bg-[#005694] transition">
            {loading ? 'Giriş Yapılıyor...' : 'Yönetim Paneline Gir'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f8fc] text-slate-800">
      <header className="bg-white border-b sticky top-0 z-20 px-4 md:px-8 py-3">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-between items-center gap-3">
          <SblLogo size="sm" />
          <div className="flex gap-2">
            <Link href="/" className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3.5 py-2 rounded-xl text-xs font-bold">
              🏠 Ana Sayfa / Veli
            </Link>
            <Link href="/belletmen" className="bg-[#006bb6] hover:bg-[#005694] text-white px-3.5 py-2 rounded-xl text-xs font-bold">
              👨‍🏫 Belletmen Ekranı
            </Link>
            <button
              onClick={() => { sessionStorage.removeItem('pansiyon_admin_logged'); setIsLoggedIn(false); }}
              className="bg-rose-600 text-white px-3.5 py-2 rounded-xl text-xs font-bold"
            >
              Çıkış
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4 md:p-6 space-y-6">
        <div className="flex gap-2 overflow-x-auto pb-1">
          {[
            { id: 'ogrenciler', label: `👨‍🎓 Öğrenciler (${store?.students?.length || 0})` },
            { id: 'belletmenler', label: `👨‍🏫 Belletmenler (${store?.belletmenler?.length || 0})` },
            { id: 'nobet', label: `📅 Aylık Nöbet Çizelgesi (${store?.aylikNobetler?.length || 0})` },
            { id: 'defter', label: `📖 Pansiyon Nöbet Defteri (${store?.dutyLogs?.length || 0})` },
            { id: 'loglar', label: `📋 Denetim Günlüğü` }
          ].map((t: any) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-5 py-2.5 rounded-xl font-bold text-xs transition whitespace-nowrap ${
                activeTab === t.id ? 'bg-[#006bb6] text-white shadow' : 'bg-white text-slate-600 border hover:bg-slate-50'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* 1) ÖĞRENCİLER SEKMESİ */}
        {activeTab === 'ogrenciler' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border space-y-4">
              <div className="flex flex-wrap justify-between items-center gap-2">
                <div>
                  <h2 className="text-base font-extrabold text-slate-900">➕ Yeni Öğrenci Ekle</h2>
                  <p className="text-xs text-slate-500">Veli numarası boş bırakılırsa sistem artık otomatik numara atamaz, boş kaydeder.</p>
                </div>
                <button
                  type="button"
                  onClick={handleClearAllStudents}
                  className="bg-rose-100 hover:bg-rose-200 text-rose-700 px-3.5 py-2 rounded-xl text-xs font-bold"
                >
                  🗑️ Eski Test Öğrencilerini Sıfırla
                </button>
              </div>

              <form onSubmit={handleAddStudent} className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                <input required placeholder="Öğrenci Adı Soyadı" className="p-2.5 border rounded-xl" value={stForm.name} onChange={(e) => setStForm({ ...stForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-xl font-bold" value={stForm.cinsiyet} onChange={(e) => setStForm({ ...stForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Pansiyonu</option>
                  <option value="kiz">👩 Kız Pansiyonu</option>
                </select>
                <input required placeholder="Kat (1-4)" type="number" className="p-2.5 border rounded-xl" value={stForm.kat} onChange={(e) => setStForm({ ...stForm, kat: e.target.value })} />
                <input required placeholder="Oda No (Örn: 101)" className="p-2.5 border rounded-xl" value={stForm.oda} onChange={(e) => setStForm({ ...stForm, oda: e.target.value })} />
                <input placeholder="Anne Adı (İsteğe Bağlı)" className="p-2.5 border rounded-xl" value={stForm.anneAdi} onChange={(e) => setStForm({ ...stForm, anneAdi: e.target.value })} />
                <input placeholder="Anne Tel (Boş bırakılabilir)" className="p-2.5 border rounded-xl" value={stForm.anneTel} onChange={(e) => setStForm({ ...stForm, anneTel: e.target.value })} />
                <input placeholder="Baba Adı (İsteğe Bağlı)" className="p-2.5 border rounded-xl" value={stForm.babaAdi} onChange={(e) => setStForm({ ...stForm, babaAdi: e.target.value })} />
                <input placeholder="Baba Tel (Boş bırakılabilir)" className="p-2.5 border rounded-xl" value={stForm.babaTel} onChange={(e) => setStForm({ ...stForm, babaTel: e.target.value })} />
                <div className="md:col-span-4 flex justify-end">
                  <button type="submit" className="bg-[#006bb6] hover:bg-[#005694] text-white px-6 py-2.5 rounded-xl font-bold">
                    Öğrenciyi Kaydet
                  </button>
                </div>
              </form>

              {/* EXCEL KOPYALA YAPIŞTIR ALANI */}
              <div className="pt-4 border-t">
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  📥 Excel'den Toplu Yapıştır (Ad Soyad | Cinsiyet | Kat | Oda | Anne Adı | Anne Tel | Baba Adı | Baba Tel)
                </label>
                <textarea
                  rows={3}
                  placeholder="Excel tablonuzdaki satırları kopyalayıp buraya yapıştırın..."
                  value={bulkText}
                  onChange={(e) => setBulkText(e.target.value)}
                  className="w-full p-2.5 border rounded-xl text-xs font-mono"
                />
                <div className="flex justify-end mt-2">
                  <button
                    type="button"
                    onClick={handleBulkPasteImport}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-xl text-xs font-bold"
                  >
                    📥 Yapıştırılan Listeyi Buluta Aktar
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="p-3">Ad Soyad</th>
                    <th className="p-3">Pansiyon</th>
                    <th className="p-3">Kat / Oda</th>
                    <th className="p-3">Anne (Tel)</th>
                    <th className="p-3">Baba (Tel)</th>
                    <th className="p-3">Durum</th>
                    <th className="p-3 text-center">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  {(store?.students || []).map((s: any) => (
                    <tr key={s.id} className="border-t hover:bg-slate-50">
                      <td className="p-3 font-bold">{s.name}</td>
                      <td className="p-3">{s.cinsiyet === 'kiz' ? '👩 Kız' : '👨 Erkek'}</td>
                      <td className="p-3">{s.kat}. Kat / {s.oda}</td>
                      <td className="p-3">{s.anneAdi || '-'} ({s.anneTel || 'Numara Yok'})</td>
                      <td className="p-3">{s.babaAdi || '-'} ({s.babaTel || 'Numara Yok'})</td>
                      <td className="p-3 font-bold">{s.status.toUpperCase()}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteStudent(s.id)} className="bg-rose-500 text-white px-3 py-1 rounded-lg font-bold">
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 2) BELLETMENLER SEKMESİ */}
        {activeTab === 'belletmenler' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border">
              <h2 className="text-base font-extrabold mb-4">➕ Yeni Belletmen Öğretmen Ekle</h2>
              <form onSubmit={handleAddBelletmen} className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
                <input required placeholder="Ad Soyad" className="p-2.5 border rounded-xl" value={belForm.name} onChange={(e) => setBelForm({ ...belForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-xl font-bold" value={belForm.cinsiyet} onChange={(e) => setBelForm({ ...belForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Belletmen</option>
                  <option value="kadin">👩 Kadın Belletmen</option>
                </select>
                <input required placeholder="Branş" className="p-2.5 border rounded-xl" value={belForm.brans} onChange={(e) => setBelForm({ ...belForm, brans: e.target.value })} />
                <input placeholder="Telefon (İsteğe Bağlı)" className="p-2.5 border rounded-xl" value={belForm.phone} onChange={(e) => setBelForm({ ...belForm, phone: e.target.value })} />
                <input required placeholder="Şifre" className="p-2.5 border rounded-xl" value={belForm.password} onChange={(e) => setBelForm({ ...belForm, password: e.target.value })} />
                <div className="md:col-span-5 flex justify-end">
                  <button type="submit" className="bg-[#006bb6] text-white px-6 py-2.5 rounded-xl font-bold">
                    Belletmeni Kaydet
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="p-3">Ad Soyad</th>
                    <th className="p-3">Görev Bloğu</th>
                    <th className="p-3">Branş</th>
                    <th className="p-3">Telefon</th>
                    <th className="p-3">Şifre</th>
                    <th className="p-3 text-center">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  {(store?.belletmenler || []).map((b: any) => (
                    <tr key={b.id} className="border-t">
                      <td className="p-3 font-bold">{b.name}</td>
                      <td className="p-3">{b.cinsiyet === 'kadin' ? '👩 Kız Pansiyonu' : '👨 Erkek Pansiyonu'}</td>
                      <td className="p-3">{b.brans}</td>
                      <td className="p-3">{b.phone || '-'}</td>
                      <td className="p-3 font-mono">{b.password}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteBelletmen(b.id)} className="bg-rose-500 text-white px-3 py-1 rounded-lg font-bold">
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 3) AYLIK NÖBET ÇİZELGESİ (İSİM DÜZENLEME MODU) */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            <div className={`p-6 rounded-2xl shadow-sm border ${isEditingDuty ? 'bg-amber-50 border-amber-300' : 'bg-white'}`}>
              <h2 className="text-base font-extrabold mb-4">
                {isEditingDuty ? `✏️ ${dutyForm.tarih} Günü Nöbetçi Belletmen İsimlerini Düzenle` : '➕ Nöbet Günü Ekle / Güncelle'}
              </h2>
              <form onSubmit={handleDutySubmit} className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
                <input type="date" required className="p-2.5 border rounded-xl" value={dutyForm.tarih} onChange={(e) => setDutyForm({ ...dutyForm, tarih: e.target.value })} />
                <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-xl" value={dutyForm.erkek1} onChange={(e) => setDutyForm({ ...dutyForm, erkek1: e.target.value })} />
                <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-xl" value={dutyForm.erkek2} onChange={(e) => setDutyForm({ ...dutyForm, erkek2: e.target.value })} />
                <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-xl" value={dutyForm.kadin1} onChange={(e) => setDutyForm({ ...dutyForm, kadin1: e.target.value })} />
                <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-xl" value={dutyForm.kadin2} onChange={(e) => setDutyForm({ ...dutyForm, kadin2: e.target.value })} />
                <div className="md:col-span-5 flex justify-end gap-2">
                  {isEditingDuty && (
                    <button type="button" onClick={() => { setIsEditingDuty(false); setDutyForm({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' }); }} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                  )}
                  <button type="submit" className="bg-[#006bb6] text-white px-6 py-2 rounded-xl font-bold">
                    {isEditingDuty ? '💾 İsimleri Güncelle' : 'Kaydet'}
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="p-3">Tarih</th>
                    <th className="p-3">Erkek 1</th>
                    <th className="p-3">Erkek 2</th>
                    <th className="p-3">Kız 1</th>
                    <th className="p-3">Kız 2</th>
                    <th className="p-3 text-center">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  {(store?.aylikNobetler || []).map((d: any) => (
                    <tr key={d.tarih} className="border-t">
                      <td className="p-3 font-bold">{d.tarih}</td>
                      <td className="p-3">{d.erkek1}</td>
                      <td className="p-3">{d.erkek2}</td>
                      <td className="p-3">{d.kadin1}</td>
                      <td className="p-3">{d.kadin2}</td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => { setDutyForm(d); setIsEditingDuty(true); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                          className="bg-amber-500 text-white px-3 py-1 rounded-lg font-bold"
                        >
                          ✏️ İsimleri Düzenle
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 4) PANSİYON NÖBET DEFTERİ (BELLETMEN İSİMLERİNİ DÜZENLEME) */}
        {activeTab === 'defter' && (
          <div className="space-y-6">
            {editingLog && (
              <div className="bg-amber-50 border border-amber-300 p-6 rounded-2xl shadow-sm">
                <h2 className="text-base font-extrabold mb-3">
                  ✏️ Pansiyon Nöbet Defteri Belletmen İsimlerini Düzenle ({editingLog.tarih})
                </h2>
                <form onSubmit={handleUpdateDutyLog} className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                  <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-xl bg-white" value={editingLog.erkekBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen1: e.target.value })} />
                  <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-xl bg-white" value={editingLog.erkekBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen2: e.target.value })} />
                  <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-xl bg-white" value={editingLog.kizBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen1: e.target.value })} />
                  <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-xl bg-white" value={editingLog.kizBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen2: e.target.value })} />
                  <textarea rows={3} placeholder="Nöbet Notları" className="md:col-span-4 p-2.5 border rounded-xl bg-white" value={editingLog.notlar || ''} onChange={(e) => setEditingLog({ ...editingLog, notlar: e.target.value })} />
                  <div className="md:col-span-4 flex justify-end gap-2">
                    <button type="button" onClick={() => setEditingLog(null)} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                    <button type="submit" className="bg-amber-600 text-white px-6 py-2 rounded-xl font-bold">
                      💾 Nöbet Defterini Güncelle
                    </button>
                  </div>
                </form>
              </div>
            )}

            <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
              <h2 className="text-base font-extrabold">📖 Kayıtlı Pansiyon Nöbet Defteri Tutanakları</h2>
              {(store?.dutyLogs || []).length === 0 ? (
                <p className="text-xs text-slate-400 italic">Henüz nöbet defteri tutanağı girilmemiş.</p>
              ) : (
                (store?.dutyLogs || []).map((log: any) => (
                  <div key={log.id} className="p-4 border rounded-xl bg-slate-50 space-y-2 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-extrabold text-[#006bb6]">📅 {log.tarih} — {log.seans}</span>
                      <button
                        onClick={() => setEditingLog(log)}
                        className="bg-amber-500 hover:bg-amber-600 text-white px-3 py-1 rounded-lg font-bold"
                      >
                        ✏️ Belletmen İsimlerini Düzenle
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 bg-white p-3 rounded-lg border">
                      <div><strong>👨 Erkek Pansiyonu Nöbetçileri:</strong> {log.erkekBelletmen1 || '-'}, {log.erkekBelletmen2 || '-'}</div>
                      <div><strong>👩 Kız Pansiyonu Nöbetçileri:</strong> {log.kizBelletmen1 || '-'}, {log.kizBelletmen2 || '-'}</div>
                    </div>
                    <p className="text-slate-700"><strong>Notlar:</strong> {log.notlar}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* 5) DENETİM GÜNLÜĞÜ */}
        {activeTab === 'loglar' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6">
            <h2 className="text-base font-extrabold mb-4">📋 Sistem Denetim Günlüğü</h2>
            <div className="space-y-2 text-xs">
              {(store?.auditLogs || []).map((l: any) => (
                <div key={l.id} className="p-2.5 border rounded-lg flex justify-between">
                  <div><strong>{l.kullanici}</strong> — {l.islem}: {l.detay}</div>
                  <span className="text-slate-400">{l.tarihSaat}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
'''

def main():
    print("================================================================")
    print("   SBL KURUMSAL LOGO & TÜM MODÜLLERİN MODERN ARAYÜZ KURULUMU")
    print("================================================================")

    db_url = get_saved_db_url()
    if not db_url:
        db_url = input("Lütfen Neon DATABASE_URL adresinizi girin: ").strip().strip('"').strip("'")

    write_file("app/api/pansiyon/route.ts", API_ROUTE_TS.replace("__USER_DATABASE_URL__", db_url))
    write_file("app/components/SblLogo.tsx", SBL_LOGO_COMPONENT_TSX)
    write_file("app/page.tsx", HOME_PAGE_TSX)
    write_file("app/belletmen/page.tsx", BELLETMEN_PAGE_TSX)
    write_file("app/admin/page.tsx", ADMIN_PAGE_TSX)

    print("\n🚀 Next.js derleniyor ve Vercel'e gönderiliyor...")
    if subprocess.run("npm run build", shell=True).returncode != 0:
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    subprocess.run("git add app/api/pansiyon/route.ts app/components/SblLogo.tsx app/page.tsx app/belletmen/page.tsx app/admin/page.tsx", shell=True)
    subprocess.run('git commit -m "SBL Mavi Lale logosu entegre edildi, tum modullerin arayuzu yenilendi ve otomatik numara atama kaldirildi" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    print("\n================================================================")
    print("🎉 SBL MODERN ARAYÜZ VE LOGO GÜNCELLEMESİ TAMAMLANDI!")
    print("👉 Ana sayfa: https://pansiyon-yurt-sistemi.vercel.app")
    print("================================================================")

if __name__ == "__main__":
    main()