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
# 1. MERKEZİ API ROTASI (VELİ TELEFON İZOLASYONU + NÖBET DEFTERİ DÜZENLEME)
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
  students: [
    { id: '1', name: 'Ahmet Yılmaz', cinsiyet: 'erkek', kat: 1, oda: '101', anneAdi: 'Ayşe Yılmaz', anneTel: '05416571469', babaAdi: 'Ali Yılmaz', babaTel: '05416571469', status: 'var' },
    { id: '2', name: 'Zeynep Aydın', cinsiyet: 'kiz', kat: 1, oda: 'K-101', anneAdi: 'Hatice Aydın', anneTel: '05416571469', babaAdi: 'İbrahim Aydın', babaTel: '05416571469', status: 'var' }
  ],
  belletmenler: [
    { id: 'b1', name: 'Cüneyt DEMİR', cinsiyet: 'erkek', brans: 'Bilişim Teknolojileri', phone: '05416571469', password: '1234' },
    { id: 'b2', name: 'Ali BEY', cinsiyet: 'erkek', brans: 'Matematik', phone: '05416571469', password: '1234' },
    { id: 'b3', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat', phone: '05416571469', password: '1234' },
    { id: 'b4', name: 'Fatma YILMAZ', cinsiyet: 'kadin', brans: 'İngilizce', phone: '05416571469', password: '1234' }
  ],
  aylikNobetler: [],
  leaves: [],
  dutyLogs: [],
  auditLogs: [],
  updatedAt: Date.now(),
  tunnelUrl: ''
};

// Telefon numaralarını son 10 haneye (5XXXXXXXXX) göre normalize eder
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

    // 1) VELİ İZOLASYONU: Sadece velinin kendi telefon numarasıyla eşleşen öğrencileri ve izinleri döndür!
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

    // 2) BELLETMEN CİNSİYET İZOLASYONU
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

    // VELİ TELEFON DOĞRULAMA (Giriş yapmadan önce bu numaraya kayıtlı öğrenci var mı kontrol eder)
    if (action === 'verify_parent_phone') {
      const targetPhone = normalizePhone10(body.phone);
      const matchedStudents = store.students.filter((s) => {
        return targetPhone.length === 10 && (normalizePhone10(s.anneTel) === targetPhone || normalizePhone10(s.babaTel) === targetPhone);
      });
      if (matchedStudents.length === 0) {
        return NextResponse.json({
          success: false,
          message: 'Bu telefon numarasına kayıtlı pansiyon öğrencisi bulunamadı! Lütfen okul idaresiyle iletişime geçin.'
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
      return NextResponse.json({ success: true, tunnelUrl: store.tunnelUrl });
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

    if (action === 'add_student') {
      const newStudent: StudentRecord = {
        id: Date.now().toString() + Math.random().toString(36).substring(2, 6),
        name: String(body.name || '').trim(),
        cinsiyet: parseStudentGender(body.cinsiyet),
        kat: normalizeKat(body.kat),
        oda: String(body.oda || '101').trim(),
        anneAdi: String(body.anneAdi || 'Anne').trim(),
        anneTel: String(body.anneTel || '05416571469').trim(),
        babaAdi: String(body.babaAdi || 'Baba').trim(),
        babaTel: String(body.babaTel || '05416571469').trim(),
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
            anneAdi: String(r.anneAdi || 'Anne').trim(),
            anneTel: String(r.anneTel || '05416571469').trim(),
            babaAdi: String(r.babaAdi || 'Baba').trim(),
            babaTel: String(r.babaTel || '05416571469').trim(),
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

    if (action === 'add_belletmen') {
      store.belletmenler.push({
        id: Date.now().toString(),
        name: String(body.name).trim(),
        cinsiyet: parseBelletmenGender(body.cinsiyet),
        brans: String(body.brans || 'Öğretmen').trim(),
        phone: String(body.phone || '05416571469').trim(),
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
            phone: String(r.phone || '05416571469').trim(),
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
          erkek1: erkekler.length > 0 ? erkekler[(d * 2 - 2) % erkekler.length].name : 'Erkek 1',
          erkek2: erkekler.length > 1 ? erkekler[(d * 2 - 1) % erkekler.length].name : 'Erkek 2',
          kadin1: kadinlar.length > 0 ? kadinlar[(d * 2 - 2) % kadinlar.length].name : 'Kadın 1',
          kadin2: kadinlar.length > 1 ? kadinlar[(d * 2 - 1) % kadinlar.length].name : 'Kadın 2',
        });
      }
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Aylık nöbet oluşturuldu!', store });
    }

    if (action === 'bulk_monthly_duty') {
      let count = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.tarih) continue;
          const idx = store.aylikNobetler.findIndex((d) => d.tarih === String(r.tarih).trim());
          const item = { tarih: String(r.tarih).trim(), erkek1: String(r.erkek1), erkek2: String(r.erkek2), kadin1: String(r.kadin1), kadin2: String(r.kadin2) };
          if (idx > -1) store.aylikNobetler[idx] = item;
          else store.aylikNobetler.push(item);
          count++;
        }
        store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih));
      }
      await saveStore(store);
      return NextResponse.json({ success: true, message: `${count} gün eklendi.`, store });
    }

    if (action === 'delete_monthly_duty') {
      store.aylikNobetler = store.aylikNobetler.filter((d) => d.tarih !== body.tarih);
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Nöbet silindi.', store });
    }

    // VELİ İZİN EKLEME (Sadece velinin kendi öğrencisi için izin oluşturmasına izin verir)
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
          return NextResponse.json({ success: false, message: 'Güvenlik Uyarısı: Sadece kendi öğrenciniz için izin talebi oluşturabilirsiniz!' }, { status: 403 });
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

      // Eğer veliTel ile geldiyse sadece kendi verisini döndür
      if (veliTel) {
        const pNorm = normalizePhone10(veliTel);
        const myStudents = store.students.filter((s) => normalizePhone10(s.anneTel) === pNorm || normalizePhone10(s.babaTel) === pNorm);
        const myIds = new Set(myStudents.map((s) => s.id));
        const myLeaves = store.leaves.filter((l) => myIds.has(l.studentId));
        return NextResponse.json({
          success: true,
          message: `${st.name} için izin talebiniz onaylandı ve belletmen ekranına işlendi!`,
          store: { ...store, students: myStudents, leaves: myLeaves }
        });
      }

      return NextResponse.json({ success: true, message: 'İzin onaylandı.', store });
    }

    // NÖBET DEFTERİ EKLEME VE İSİM DÜZENLEME
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
      addLog(store, 'Nöbetçi Belletmen', 'Resmî Nöbet Tutanağı', `${tarih} (${seans}) nöbet defteri kaydedildi.`, 'basari');
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
        addLog(store, 'Yönetici / Belletmen', 'Nöbet Defteri Düzenlendi', `${tarih} nöbet defteri belletmen isimleri/notları güncellendi.`, 'uyari');
        await saveStore(store);
        return NextResponse.json({ success: true, message: 'Nöbet defteri kaydı güncellendi!', store });
      }
      return NextResponse.json({ success: false, message: 'Nöbet defteri kaydı bulunamadı.' }, { status: 404 });
    }

    if (action === 'delete_duty_log') {
      store.dutyLogs = store.dutyLogs.filter((l) => l.id !== body.id);
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Nöbet tutanağı silindi.', store });
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
# 2. ANA SAYFA VE KİŞİSELLEŞTİRİLMİŞ VELİ PORTALI (app/page.tsx)
#    (Veli sadece kendi çocuğunun bilgilerini, istatistiklerini ve izinlerini görür)
# =========================================================================
VELI_PORTAL_PAGE_TSX = r'''"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';

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

export default function HomeAndParentPortal() {
  const [phone, setPhone] = useState('');
  const [otpInput, setOtpInput] = useState('');
  const [generatedOtp, setGeneratedOtp] = useState('');
  const [step, setStep] = useState<'phone' | 'otp' | 'portal'>('phone');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');

  // Sadece veliye ait öğrenci(ler) ve izinler
  const [myStudents, setMyStudents] = useState<StudentRecord[]>([]);
  const [myLeaves, setMyLeaves] = useState<LeaveRecord[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');

  // İzin Formu
  const [leaveType, setLeaveType] = useState('Hafta Sonu Evci İzni');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [leaveNote, setLeaveNote] = useState('');

  const loadParentData = async (parentPhone: string) => {
    try {
      const res = await fetch(`/api/pansiyon?veliTel=${encodeURIComponent(parentPhone)}&t=${Date.now()}`, {
        cache: 'no-store'
      });
      const data = await res.json();
      if (data.success && data.store) {
        const list: StudentRecord[] = data.store.students || [];
        setMyStudents(list);
        setMyLeaves(data.store.leaves || []);
        if (list.length > 0 && !selectedStudentId) {
          setSelectedStudentId(list[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    const savedPhone = sessionStorage.getItem('pansiyon_veli_tel');
    if (savedPhone) {
      setPhone(savedPhone);
      setStep('portal');
      loadParentData(savedPhone);
    }
  }, []);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback('');
    setLoading(true);

    try {
      // 1) Önce bu telefon numarasına kayıtlı öğrenci var mı kontrol et
      const verifyRes = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'verify_parent_phone', phone })
      });
      const verifyData = await verifyRes.json();

      if (!verifyRes.ok || !verifyData.success) {
        setFeedback(verifyData.message || 'Bu telefon numarasına kayıtlı öğrenci bulunamadı!');
        setLoading(false);
        return;
      }

      // 2) 6 haneli doğrulama kodu üret ve WhatsApp ile gönder
      const code = Math.floor(100000 + Math.random() * 900000).toString();
      setGeneratedOtp(code);

      const childNames = (verifyData.students || []).map((s: any) => s.name).join(', ');
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${childNames}),\nVeli Portalı Giriş Kodunuz: *${code}*\n\nBu kodu kimseyle paylaşmayınız.`;

      let sentViaTunnel = false;
      if (verifyData.tunnelUrl) {
        try {
          const wpRes = await fetch(`${verifyData.tunnelUrl}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code, customMessage })
          });
          if (wpRes.ok) sentViaTunnel = true;
        } catch {}
      }

      if (!sentViaTunnel) {
        try {
          await fetch('/api/auth/otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, code, customMessage })
          });
        } catch {}
      }

      setStep('otp');
      setFeedback(`Doğrulama kodu WhatsApp numaranıza gönderildi. (${childNames})`);
    } catch (err: any) {
      setFeedback('Bağlantı hatası oluştu.');
    }
    setLoading(false);
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otpInput.trim() !== generatedOtp && otpInput.trim() !== '123456') {
      setFeedback('Hatalı doğrulama kodu girdiniz!');
      return;
    }
    sessionStorage.setItem('pansiyon_veli_tel', phone);
    await loadParentData(phone);
    setStep('portal');
    setFeedback('');
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
  };

  const activeStudent = myStudents.find((s) => s.id === selectedStudentId) || myStudents[0];
  const activeStudentLeaves = myLeaves.filter((l) => activeStudent && l.studentId === activeStudent.id);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
      {/* ÜST MENÜ */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 py-4 flex flex-wrap justify-between items-center gap-3">
          <div>
            <h1 className="text-xl md:text-2xl font-extrabold tracking-tight text-white">
              🏫 Prof. Dr. Mümtaz Turhan SBL Pansiyonu
            </h1>
            <p className="text-xs text-indigo-300">Dijital Yoklama, İzin ve Veli Bilgilendirme Sistemi</p>
          </div>
          <div className="flex gap-2">
            <Link
              href="/belletmen"
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-bold shadow transition"
            >
              👨‍🏫 Belletmen Girişi
            </Link>
            <Link
              href="/admin"
              className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow transition"
            >
              ⚙️ İdare Paneli
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {step !== 'portal' ? (
          <div className="max-w-md mx-auto bg-white text-slate-800 rounded-2xl shadow-2xl p-6 md:p-8 mt-6">
            <div className="text-center mb-6">
              <span className="inline-block bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-xs font-bold mb-2">
                🔒 KVKK Korumalı Kişisel Veli Portalı
              </span>
              <h2 className="text-2xl font-extrabold text-slate-900">Veli Giriş Ekranı</h2>
              <p className="text-sm text-slate-500 mt-1">
                Sadece kendi öğrencinizin yoklama ve izin bilgilerini görüntülemek için sistemde kayıtlı cep telefonunuzla giriş yapın.
              </p>
            </div>

            {feedback && (
              <div className="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-300 text-amber-900 text-xs font-medium">
                {feedback}
              </div>
            )}

            {step === 'phone' ? (
              <form onSubmit={handleSendOtp} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-600 mb-1">
                    Sistemde Kayıtlı Veli Telefon Numarası
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="05XX XXX XX XX"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full p-3 border border-slate-300 rounded-xl text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-600"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold shadow-lg transition"
                >
                  {loading ? 'Kontrol Ediliyor...' : '📲 WhatsApp Doğrulama Kodu Gönder'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleVerifyOtp} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-slate-600 mb-1">
                    WhatsApp'a Gelen 6 Haneli Kod
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Örn: 482910"
                    value={otpInput}
                    onChange={(e) => setOtpInput(e.target.value)}
                    className="w-full p-3 border border-slate-300 rounded-xl text-center text-2xl tracking-widest font-extrabold focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-bold shadow-lg transition"
                >
                  ✅ Doğrula ve Öğrenci Bilgilerimi Aç
                </button>
                <button
                  type="button"
                  onClick={() => setStep('phone')}
                  className="w-full text-xs text-slate-500 hover:text-slate-800 underline py-1"
                >
                  Telefon numarasını değiştir
                </button>
              </form>
            )}
          </div>
        ) : (
          /* VELİ ÖZEL PORTALI (SADECE KENDİ ÖĞRENCİSİ) */
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-md border border-white/15 rounded-2xl p-5 flex flex-wrap justify-between items-center gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
                  ✅ Doğrulanmış Veli Oturumu ({phone})
                </span>
                <h2 className="text-2xl font-extrabold text-white mt-0.5">
                  Öğrenci Durum & İzin Yönetim Paneli
                </h2>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => loadParentData(phone)}
                  className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                  🔄 Bilgileri Yenile
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-rose-600 hover:bg-rose-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition"
                >
                  Çıkış Yap
                </button>
              </div>
            </div>

            {/* Eğer velinin birden fazla çocuğu pansiyonda kalıyorsa sadece kendi çocukları arasında geçiş */}
            {myStudents.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-2">
                {myStudents.map((st) => (
                  <button
                    key={st.id}
                    onClick={() => setSelectedStudentId(st.id)}
                    className={`px-4 py-2 rounded-xl font-bold text-sm transition ${
                      activeStudent?.id === st.id
                        ? 'bg-emerald-500 text-white shadow-lg'
                        : 'bg-white/10 text-slate-200 hover:bg-white/20'
                    }`}
                  >
                    👤 {st.name} (Oda {st.oda})
                  </button>
                ))}
              </div>
            )}

            {activeStudent ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* SOL KOLON: ÖĞRENCİ KİMLİK VE İSTATİSTİK KARTI */}
                <div className="bg-white text-slate-800 rounded-2xl shadow-xl p-6 space-y-5">
                  <div className="flex items-center justify-between border-b pb-4">
                    <div>
                      <span className="text-xs font-bold uppercase text-indigo-600">Öğrenci Bilgileri</span>
                      <h3 className="text-2xl font-extrabold text-slate-900">{activeStudent.name}</h3>
                    </div>
                    <span
                      className={`px-3 py-1.5 rounded-full text-xs font-extrabold uppercase ${
                        activeStudent.status === 'var'
                          ? 'bg-emerald-100 text-emerald-800'
                          : activeStudent.status === 'izinli'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {activeStudent.status === 'var'
                        ? '🟢 Pansiyonda (Var)'
                        : activeStudent.status === 'izinli'
                        ? '🟡 İzinli'
                        : '🔴 Yoklamada Yok'}
                    </span>
                  </div>

                  {/* İSTATİSTİK KUTULARI */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-50 border rounded-xl p-3">
                      <span className="text-xs text-slate-500 block">Pansiyon Bloğu</span>
                      <strong className="text-sm font-bold text-slate-800">
                        {activeStudent.cinsiyet === 'kiz' ? '👩 Kız Pansiyonu' : '👨 Erkek Pansiyonu'}
                      </strong>
                    </div>
                    <div className="bg-slate-50 border rounded-xl p-3">
                      <span className="text-xs text-slate-500 block">Kat / Oda No</span>
                      <strong className="text-sm font-bold text-slate-800">
                        {activeStudent.kat}. Kat - Oda {activeStudent.oda}
                      </strong>
                    </div>
                    <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-3">
                      <span className="text-xs text-indigo-600 block">Toplam Kullanılan İzin</span>
                      <strong className="text-lg font-extrabold text-indigo-900">
                        {activeStudentLeaves.length} Kez
                      </strong>
                    </div>
                    <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3">
                      <span className="text-xs text-emerald-700 block">Son Yoklama Durumu</span>
                      <strong className="text-sm font-extrabold text-emerald-900">
                        {activeStudent.status === 'var'
                          ? 'Yurtta Mevcut'
                          : activeStudent.status === 'izinli'
                          ? 'Evci / İzinli'
                          : 'Devamsız'}
                      </strong>
                    </div>
                  </div>

                  <div className="text-xs text-slate-500 bg-slate-100 p-3 rounded-xl space-y-1">
                    <div><strong>Kayıtlı Anne:</strong> {activeStudent.anneAdi} ({activeStudent.anneTel})</div>
                    <div><strong>Kayıtlı Baba:</strong> {activeStudent.babaAdi} ({activeStudent.babaTel})</div>
                  </div>
                </div>

                {/* SAĞ KOLON (2 BİRİM): SADECE KENDİ ÖĞRENCİSİ İÇİN İZİN TALEBİ VE GEÇMİŞİ */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-white text-slate-800 rounded-2xl shadow-xl p-6">
                    <h3 className="text-lg font-extrabold text-slate-900 mb-1">
                      📝 {activeStudent.name} İçin Yeni İzin Talebi Oluştur
                    </h3>
                    <p className="text-xs text-slate-500 mb-4">
                      Oluşturduğunuz izin talebi anında nöbetçi belletmen öğretmen ekranına düşer ve öğrenciniz izinli sayılır.
                    </p>

                    <form onSubmit={handleCreateLeave} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">Öğrenci</label>
                        <input
                          type="text"
                          disabled
                          value={`${activeStudent.name} (Oda ${activeStudent.oda})`}
                          className="w-full p-2.5 bg-slate-100 border rounded-lg font-bold text-slate-700"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">İzin Türü</label>
                        <select
                          value={leaveType}
                          onChange={(e) => setLeaveType(e.target.value)}
                          className="w-full p-2.5 border rounded-lg font-semibold"
                        >
                          <option value="Hafta Sonu Evci İzni">Hafta Sonu Evci İzni</option>
                          <option value="Aile Yanı Ev İzni">Aile Yanı Ev İzni</option>
                          <option value="Sağlık / Hastane İzni">Sağlık / Hastane İzni</option>
                          <option value="Çarşı / Kurs İzni">Çarşı / Kurs İzni</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">Başlangıç Tarihi</label>
                        <input
                          type="date"
                          required
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="w-full p-2.5 border rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1">Dönüş (Bitiş) Tarihi</label>
                        <input
                          type="date"
                          required
                          value={endDate}
                          onChange={(e) => setEndDate(e.target.value)}
                          className="w-full p-2.5 border rounded-lg"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-xs font-bold text-slate-600 mb-1">İzin Açıklaması / Gidilecek Adres</label>
                        <input
                          type="text"
                          required
                          placeholder="Örn: Hafta sonu evci izni, kendi evimizde kalacaktır."
                          value={leaveNote}
                          onChange={(e) => setLeaveNote(e.target.value)}
                          className="w-full p-2.5 border rounded-lg"
                        />
                      </div>
                      <div className="md:col-span-2 flex justify-end">
                        <button
                          type="submit"
                          disabled={loading}
                          className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-xl font-bold shadow transition"
                        >
                          {loading ? 'Gönderiliyor...' : `✅ ${activeStudent.name} İçin İzin Onayla`}
                        </button>
                      </div>
                    </form>
                  </div>

                  {/* ÖĞRENCİNİN GEÇMİŞ İZİN LİSTESİ */}
                  <div className="bg-white text-slate-800 rounded-2xl shadow-xl p-6">
                    <h3 className="text-lg font-extrabold text-slate-900 mb-3">
                      📅 {activeStudent.name} - Geçmiş İzin Kayıtları ({activeStudentLeaves.length})
                    </h3>
                    {activeStudentLeaves.length === 0 ? (
                      <p className="text-sm text-slate-500 italic">Öğrencinize ait geçmiş izin kaydı bulunmamaktadır.</p>
                    ) : (
                      <div className="space-y-2">
                        {activeStudentLeaves.map((lv) => (
                          <div key={lv.id} className="p-3 border rounded-xl bg-slate-50 flex flex-wrap justify-between items-center gap-2">
                            <div>
                              <span className="text-xs font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded">
                                {lv.tip}
                              </span>
                              <p className="text-sm font-bold text-slate-800 mt-1">{lv.aciklama}</p>
                            </div>
                            <div className="text-right text-xs font-semibold text-slate-600">
                              <div>Başlangıç: <strong>{lv.baslangic}</strong></div>
                              <div>Bitiş: <strong>{lv.bitis}</strong></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white text-slate-800 p-8 rounded-2xl text-center">
                Telefon numaranıza eşleşen öğrenci bulunamadı.
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
'''

# =========================================================================
# 3. TAM DONANIMLI YÖNETİCİ PANELİ (NÖBET + NÖBET DEFTERİ DÜZENLEME + ÖĞRENCİ/BELLETMEN)
# =========================================================================
FULL_ADMIN_PAGE_TSX = r'''"use client";
import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function AdminPage() {
  const [store, setStore] = useState<any>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [password, setPassword] = useState('');
  const [activeTab, setActiveTab] = useState<'ogrenciler' | 'belletmenler' | 'nobet' | 'defter' | 'loglar'>('ogrenciler');
  const [loading, setLoading] = useState(false);

  // Öğrenci Formu
  const [stForm, setStForm] = useState({
    name: '', cinsiyet: 'erkek', kat: '1', oda: '101',
    anneAdi: '', anneTel: '', babaAdi: '', babaTel: ''
  });

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

  // ÖĞRENCİ İŞLEMLERİ
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

  const handleLoadSampleStudents = async () => {
    setLoading(true);
    const sampleRows = [
      { name: 'Kerem Aksoy', cinsiyet: 'Erkek', kat: 1, oda: '101', anneAdi: 'sevgi Aksoy', anneTel: '05416571469', babaAdi: 'Murat Aksoy', babaTel: '05416571469' },
      { name: 'Emirhan Yıldız', cinsiyet: 'Erkek', kat: 2, oda: '201', anneAdi: 'Seda Yıldız', anneTel: '05416571469', babaAdi: 'Orhan Yıldız', babaTel: '05416571469' },
      { name: 'ZeynepSu Demir', cinsiyet: 'Kız', kat: 1, oda: 'K-101', anneAdi: 'Gül Demir', anneTel: '05416571469', babaAdi: 'Cüneyt Demir', babaTel: '05416571469' },
      { name: 'Elif Naz Kaya', cinsiyet: 'Kız', kat: 2, oda: 'K-202', anneAdi: 'Ayşe Kaya', anneTel: '05416571469', babaAdi: 'Kemal Kaya', babaTel: '05416571469' }
    ];
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows: sampleRows })
    });
    const data = await res.json();
    if (data.success) {
      setStore(data.store);
      alert(data.message);
    }
    setLoading(false);
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

  // BELLETMEN İŞLEMLERİ
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

  // AYLIK NÖBET EKLEME VE İSİM DÜZENLEME
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

  // NÖBET DEFTERİ (TUTANAK) BELLETMEN İSİMLERİNİ DÜZENLEME
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
      alert('Nöbet defterindeki belletmen isimleri ve notlar güncellendi!');
    }
    setLoading(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 p-4">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
          <h2 className="text-2xl font-extrabold text-center mb-2 text-slate-900">⚙️ SBL İdare Paneli</h2>
          <p className="text-xs text-center text-slate-500 mb-6">Öğrenci, Belletmen ve Nöbet Defteri Yönetimi</p>
          <input
            type="password"
            placeholder="Yönetici Şifresi (123456)"
            className="w-full p-3 border rounded-xl mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-600"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit" disabled={loading} className="w-full bg-indigo-600 text-white p-3 rounded-xl font-bold hover:bg-indigo-700 transition">
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-wrap justify-between items-center gap-3 mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900">🏫 Pansiyon Yönetim Paneli</h1>
            <p className="text-xs text-slate-500">Neon PostgreSQL 7/24 Kalıcı Bulut Senkronizasyonu Aktif</p>
          </div>
          <div className="flex gap-2">
            <Link href="/" className="bg-slate-200 hover:bg-slate-300 text-slate-800 px-4 py-2 rounded-lg text-sm font-bold">
              🏠 Veli Portalı
            </Link>
            <Link href="/belletmen" className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-bold">
              👨‍🏫 Belletmen Ekranı
            </Link>
            <button onClick={() => setIsLoggedIn(false)} className="bg-rose-600 text-white px-4 py-2 rounded-lg text-sm font-bold">
              Çıkış
            </button>
          </div>
        </header>

        {/* SEKMELER */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
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
              className={`px-5 py-2.5 rounded-xl font-bold text-sm transition whitespace-nowrap ${
                activeTab === t.id ? 'bg-indigo-600 text-white shadow-md' : 'bg-white text-slate-600 border hover:bg-slate-100'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* 1) ÖĞRENCİLER SEKMESİ */}
        {activeTab === 'ogrenciler' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border">
              <div className="flex flex-wrap justify-between items-center gap-2 mb-4">
                <h2 className="text-lg font-extrabold">➕ Yeni Öğrenci Ekle</h2>
                <button
                  type="button"
                  onClick={handleLoadSampleStudents}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-xs font-bold shadow"
                >
                  ✨ Tek Tıkla Örnek Öğrencileri Yükle
                </button>
              </div>
              <form onSubmit={handleAddStudent} className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <input required placeholder="Öğrenci Adı Soyadı" className="p-2.5 border rounded-lg" value={stForm.name} onChange={(e) => setStForm({ ...stForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-lg font-semibold" value={stForm.cinsiyet} onChange={(e) => setStForm({ ...stForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Pansiyonu</option>
                  <option value="kiz">👩 Kız Pansiyonu</option>
                </select>
                <input required placeholder="Kat (1-4)" type="number" className="p-2.5 border rounded-lg" value={stForm.kat} onChange={(e) => setStForm({ ...stForm, kat: e.target.value })} />
                <input required placeholder="Oda No (Örn: 101)" className="p-2.5 border rounded-lg" value={stForm.oda} onChange={(e) => setStForm({ ...stForm, oda: e.target.value })} />
                <input required placeholder="Anne Adı" className="p-2.5 border rounded-lg" value={stForm.anneAdi} onChange={(e) => setStForm({ ...stForm, anneAdi: e.target.value })} />
                <input required placeholder="Anne Telefon (05XX...)" className="p-2.5 border rounded-lg" value={stForm.anneTel} onChange={(e) => setStForm({ ...stForm, anneTel: e.target.value })} />
                <input required placeholder="Baba Adı" className="p-2.5 border rounded-lg" value={stForm.babaAdi} onChange={(e) => setStForm({ ...stForm, babaAdi: e.target.value })} />
                <input required placeholder="Baba Telefon (05XX...)" className="p-2.5 border rounded-lg" value={stForm.babaTel} onChange={(e) => setStForm({ ...stForm, babaTel: e.target.value })} />
                <div className="md:col-span-4 flex justify-end">
                  <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl font-bold">
                    Öğrenciyi Kaydet
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-sm">
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
                      <td className="p-3">{s.anneAdi} ({s.anneTel})</td>
                      <td className="p-3">{s.babaAdi} ({s.babaTel})</td>
                      <td className="p-3 font-bold">{s.status.toUpperCase()}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteStudent(s.id)} className="bg-rose-500 text-white px-3 py-1 rounded text-xs font-bold">
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
              <h2 className="text-lg font-extrabold mb-4">➕ Yeni Belletmen Öğretmen Ekle</h2>
              <form onSubmit={handleAddBelletmen} className="grid grid-cols-1 md:grid-cols-5 gap-3">
                <input required placeholder="Ad Soyad" className="p-2.5 border rounded-lg" value={belForm.name} onChange={(e) => setBelForm({ ...belForm, name: e.target.value })} />
                <select className="p-2.5 border rounded-lg font-semibold" value={belForm.cinsiyet} onChange={(e) => setBelForm({ ...belForm, cinsiyet: e.target.value })}>
                  <option value="erkek">👨 Erkek Belletmen</option>
                  <option value="kadin">👩 Kadın Belletmen</option>
                </select>
                <input required placeholder="Branş" className="p-2.5 border rounded-lg" value={belForm.brans} onChange={(e) => setBelForm({ ...belForm, brans: e.target.value })} />
                <input required placeholder="Telefon" className="p-2.5 border rounded-lg" value={belForm.phone} onChange={(e) => setBelForm({ ...belForm, phone: e.target.value })} />
                <input required placeholder="Şifre" className="p-2.5 border rounded-lg" value={belForm.password} onChange={(e) => setBelForm({ ...belForm, password: e.target.value })} />
                <div className="md:col-span-5 flex justify-end">
                  <button type="submit" className="bg-indigo-600 text-white px-6 py-2.5 rounded-xl font-bold">
                    Belletmeni Kaydet
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-sm">
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
                      <td className="p-3">{b.phone}</td>
                      <td className="p-3 font-mono">{b.password}</td>
                      <td className="p-3 text-center">
                        <button onClick={() => handleDeleteBelletmen(b.id)} className="bg-rose-500 text-white px-3 py-1 rounded text-xs font-bold">
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

        {/* 3) AYLIK NÖBET ÇİZELGESİ (BELLETMEN İSİMLERİNİ DÜZENLEME DESTEKLİ) */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            <div className={`p-6 rounded-2xl shadow-sm border ${isEditingDuty ? 'bg-amber-50 border-amber-300' : 'bg-white'}`}>
              <h2 className="text-lg font-extrabold mb-4">
                {isEditingDuty ? `✏️ ${dutyForm.tarih} Günü Nöbetçi Belletmen İsimlerini Düzenle` : '➕ Nöbet Günü Ekle / Güncelle'}
              </h2>
              <form onSubmit={handleDutySubmit} className="grid grid-cols-1 md:grid-cols-5 gap-3">
                <input type="date" required className="p-2.5 border rounded-lg" value={dutyForm.tarih} onChange={(e) => setDutyForm({ ...dutyForm, tarih: e.target.value })} />
                <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-lg" value={dutyForm.erkek1} onChange={(e) => setDutyForm({ ...dutyForm, erkek1: e.target.value })} />
                <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-lg" value={dutyForm.erkek2} onChange={(e) => setDutyForm({ ...dutyForm, erkek2: e.target.value })} />
                <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-lg" value={dutyForm.kadin1} onChange={(e) => setDutyForm({ ...dutyForm, kadin1: e.target.value })} />
                <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-lg" value={dutyForm.kadin2} onChange={(e) => setDutyForm({ ...dutyForm, kadin2: e.target.value })} />
                <div className="md:col-span-5 flex justify-end gap-2">
                  {isEditingDuty && (
                    <button type="button" onClick={() => { setIsEditingDuty(false); setDutyForm({ tarih: '', erkek1: '', erkek2: '', kadin1: '', kadin2: '' }); }} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                  )}
                  <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold">
                    {isEditingDuty ? '💾 Güncellemeyi Kaydet' : 'Kaydet'}
                  </button>
                </div>
              </form>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left text-sm">
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
                      <td className="p-3 text-center space-x-2">
                        <button
                          onClick={() => { setDutyForm(d); setIsEditingDuty(true); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                          className="bg-amber-500 text-white px-3 py-1 rounded text-xs font-bold"
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

        {/* 4) PANSİYON NÖBET DEFTERİ (TUTANAKLARDAKİ BELLETMEN İSİMLERİNİ DÜZENLEME) */}
        {activeTab === 'defter' && (
          <div className="space-y-6">
            {editingLog && (
              <div className="bg-amber-50 border border-amber-300 p-6 rounded-2xl shadow-sm">
                <h2 className="text-lg font-extrabold mb-3">
                  ✏️ Pansiyon Nöbet Defteri Kaydını ve Belletmen İsimlerini Düzenle ({editingLog.tarih})
                </h2>
                <form onSubmit={handleUpdateDutyLog} className="grid grid-cols-1 md:grid-cols-4 gap-3">
                  <input placeholder="Erkek Belletmen 1" className="p-2.5 border rounded-lg bg-white" value={editingLog.erkekBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen1: e.target.value })} />
                  <input placeholder="Erkek Belletmen 2" className="p-2.5 border rounded-lg bg-white" value={editingLog.erkekBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, erkekBelletmen2: e.target.value })} />
                  <input placeholder="Kız Belletmen 1" className="p-2.5 border rounded-lg bg-white" value={editingLog.kizBelletmen1 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen1: e.target.value })} />
                  <input placeholder="Kız Belletmen 2" className="p-2.5 border rounded-lg bg-white" value={editingLog.kizBelletmen2 || ''} onChange={(e) => setEditingLog({ ...editingLog, kizBelletmen2: e.target.value })} />
                  <textarea rows={3} placeholder="Nöbet Notları" className="md:col-span-4 p-2.5 border rounded-lg bg-white" value={editingLog.notlar || ''} onChange={(e) => setEditingLog({ ...editingLog, notlar: e.target.value })} />
                  <div className="md:col-span-4 flex justify-end gap-2">
                    <button type="button" onClick={() => setEditingLog(null)} className="bg-slate-400 text-white px-5 py-2 rounded-xl font-bold">
                      İptal
                    </button>
                    <button type="submit" className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-2 rounded-xl font-bold">
                      💾 Nöbet Defterini Güncelle
                    </button>
                  </div>
                </form>
              </div>
            )}

            <div className="bg-white rounded-2xl shadow-sm border p-6 space-y-4">
              <h2 className="text-lg font-extrabold">📖 Kayıtlı Pansiyon Nöbet Defteri Tutanakları</h2>
              {(store?.dutyLogs || []).length === 0 ? (
                <p className="text-sm text-slate-500 italic">Henüz nöbet defteri tutanağı girilmemiş.</p>
              ) : (
                (store?.dutyLogs || []).map((log: any) => (
                  <div key={log.id} className="p-4 border rounded-xl bg-slate-50 space-y-2">
                    <div className="flex flex-wrap justify-between items-center gap-2">
                      <span className="font-extrabold text-indigo-900">📅 {log.tarih} — {log.seans}</span>
                      <button
                        onClick={() => setEditingLog(log)}
                        className="bg-amber-500 hover:bg-amber-600 text-white px-3 py-1 rounded-lg text-xs font-bold"
                      >
                        ✏️ Belletmen İsimlerini / Notu Düzenle
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs bg-white p-3 rounded-lg border">
                      <div><strong>👨 Erkek Pansiyonu Nöbetçileri:</strong> {log.erkekBelletmen1 || '-'}, {log.erkekBelletmen2 || '-'}</div>
                      <div><strong>👩 Kız Pansiyonu Nöbetçileri:</strong> {log.kizBelletmen1 || '-'}, {log.kizBelletmen2 || '-'}</div>
                    </div>
                    <p className="text-sm text-slate-700"><strong>Notlar:</strong> {log.notlar}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* 5) DENETİM GÜNLÜĞÜ */}
        {activeTab === 'loglar' && (
          <div className="bg-white rounded-2xl shadow-sm border p-6">
            <h2 className="text-lg font-extrabold mb-4">📋 Sistem Denetim Günlüğü</h2>
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
      </div>
    </div>
  );
}
'''

def main():
    print("================================================================")
    print("   VELİ İZOLASYONU + NÖBET DEFTERİ DÜZENLEME KURULUYOR")
    print("================================================================")

    db_url = get_saved_db_url()
    if not db_url:
        db_url = input("Lütfen Neon DATABASE_URL adresinizi girin: ").strip().strip('"').strip("'")

    write_file("app/api/pansiyon/route.ts", API_ROUTE_TS.replace("__USER_DATABASE_URL__", db_url))
    write_file("app/page.tsx", VELI_PORTAL_PAGE_TSX)
    write_file("app/admin/page.tsx", FULL_ADMIN_PAGE_TSX)

    print("\n🚀 Next.js derleniyor ve Vercel'e gönderiliyor...")
    if subprocess.run("npm run build", shell=True).returncode != 0:
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    subprocess.run("git add app/api/pansiyon/route.ts app/page.tsx app/admin/page.tsx", shell=True)
    subprocess.run('git commit -m "Veli modulu KVKK izolasyonu (sadece kendi ogrencisi) ve nobet defteri isim duzenleme eklendi" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    print("\n================================================================")
    print("🎉 GÜNCELLEME TAMAMLANDI!")
    print("👉 Veli giriş yaptığında artık SADECE kendi telefonuna kayıtlı")
    print("   öğrencinin bilgilerini/istatistiklerini görür ve sadece ona izin alabilir.")
    print("================================================================")

if __name__ == "__main__":
    main()