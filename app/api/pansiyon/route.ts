import { NextResponse } from 'next/server';
import { neon } from '@neondatabase/serverless';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

const FALLBACK_DB_URL = 'postgresql://neondb_owner:npg_P3YBw2DvSdqI@ep-long-brook-b7pfqguz-pooler.c-13.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require';

function getSql() {
  const url = process.env.DATABASE_URL || FALLBACK_DB_URL;
  if (!url || url.includes('postgresql://neondb_owner:npg_P3YBw2DvSdqI@ep-long-brook-b7pfqguz-pooler.c-13.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')) {
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

export interface AttendanceHistoryRecord {
  id: string;
  studentId: string;
  studentName: string;
  oda: string;
  tarih: string;
  saat: string;
  seans: string;
  status: 'var' | 'yok' | 'izinli';
  belletmenName: string;
}

export interface StoreData {
  students: StudentRecord[];
  belletmenler: BelletmenRecord[];
  aylikNobetler: MonthlyDutyDay[];
  leaves: LeaveRecord[];
  dutyLogs: DutyLogRecord[];
  auditLogs: AuditLogRecord[];
  attendanceHistory: AttendanceHistoryRecord[];
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
  attendanceHistory: [],
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
  const store = rows[0].data as StoreData;
  if (!store.attendanceHistory) store.attendanceHistory = [];
  return store;
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

    // VELİ İZOLASYONU: Sadece velinin kendi öğrencisini, kendi izinlerini ve kendi etüt/yat yoklama geçmişini döndürür
    if (veliTelFilter) {
      const targetPhone = normalizePhone10(veliTelFilter);
      const myStudents = (store.students || []).filter((s) => {
        const anneP = normalizePhone10(s.anneTel);
        const babaP = normalizePhone10(s.babaTel);
        return targetPhone.length === 10 && (anneP === targetPhone || babaP === targetPhone);
      });
      const myStudentIds = new Set(myStudents.map((s) => s.id));
      const myLeaves = (store.leaves || []).filter((l) => myStudentIds.has(l.studentId));
      const myAttendanceHistory = (store.attendanceHistory || []).filter((h) => myStudentIds.has(h.studentId));

      return NextResponse.json({
        success: true,
        store: {
          students: myStudents,
          leaves: myLeaves,
          attendanceHistory: myAttendanceHistory,
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
      const filteredHistory = (store.attendanceHistory || []).filter((h) => allowedIds.has(h.studentId));
      return NextResponse.json({
        success: true,
        store: { ...store, students: filteredStudents, leaves: filteredLeaves, attendanceHistory: filteredHistory }
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
    if (!store.attendanceHistory) store.attendanceHistory = [];

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

    // ANLIK YOKLAMA DEĞİŞİMİ + ETÜT/YAT YOKLAMA GEÇMİŞİNE KAYIT
    if (action === 'update_attendance') {
      const tarih = body.tarih || new Date().toISOString().split('T')[0];
      const seans = body.seans || 'Gece Yat Yoklaması (22:00)';
      const belletmenName = body.belletmenName || 'Nöbetçi Belletmen';
      const saat = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });

      if (Array.isArray(body.students)) {
        const updatedMap = new Map(body.students.map((s: StudentRecord) => [s.id, s]));
        store.students = store.students.map((existing) =>
          updatedMap.has(existing.id) ? (updatedMap.get(existing.id) as StudentRecord) : existing
        );
      }

      // Tek bir öğrenci tıklandıysa veya toplu seans kaydedildiyse geçmişe (attendanceHistory) işle
      const recordsToArchive: StudentRecord[] = body.changedStudent
        ? [body.changedStudent]
        : (body.archiveAll && Array.isArray(body.students) ? body.students : []);

      for (const st of recordsToArchive) {
        if (!st || !st.id) continue;
        const existingIdx = store.attendanceHistory.findIndex(
          (h) => h.studentId === st.id && h.tarih === tarih && h.seans === seans
        );
        const item: AttendanceHistoryRecord = {
          id: existingIdx > -1 ? store.attendanceHistory[existingIdx].id : (Date.now() + Math.random()).toString(),
          studentId: st.id,
          studentName: st.name,
          oda: st.oda,
          tarih,
          saat,
          seans,
          status: st.status,
          belletmenName
        };
        if (existingIdx > -1) {
          store.attendanceHistory[existingIdx] = item;
        } else {
          store.attendanceHistory.unshift(item);
        }
      }

      if (store.attendanceHistory.length > 3000) {
        store.attendanceHistory = store.attendanceHistory.slice(0, 3000);
      }

      if (body.archiveAll) {
        addLog(store, belletmenName, 'Yoklama Arşivlendi', `${tarih} - ${seans} yoklaması veli portalı geçmişine işlendi.`, 'basari');
      }

      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Yoklama ve geçmiş kaydı güncellendi.', store });
    }

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
      store.attendanceHistory = store.attendanceHistory.filter((h) => h.studentId !== body.id);
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Öğrenci silindi.', store });
    }

    if (action === 'clear_all_students') {
      store.students = [];
      store.leaves = [];
      store.attendanceHistory = [];
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
        const myAttendanceHistory = store.attendanceHistory.filter((h) => myIds.has(h.studentId));
        return NextResponse.json({
          success: true,
          message: `${st.name} için izin talebiniz onaylandı!`,
          store: { ...store, students: myStudents, leaves: myLeaves, attendanceHistory: myAttendanceHistory }
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