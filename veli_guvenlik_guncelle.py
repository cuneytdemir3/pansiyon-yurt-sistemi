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
# 1. API ROTASI (Varsayılan hayalet öğrenciler kaldırıldı + Sıkı Veli Kontrolü)
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

// Varsayılan öğrenci listesi BOŞ bırakıldı (Hayalet öğrenci numarası eşleşmesini önlemek için)
const DEFAULT_STORE: StoreData = {
  students: [],
  belletmenler: [
    { id: 'b1', name: 'Cüneyt DEMİR', cinsiyet: 'erkek', brans: 'Bilişim Teknolojileri', phone: '05416571469', password: '1234' },
    { id: 'b2', name: 'Ali BEY', cinsiyet: 'erkek', brans: 'Matematik', phone: '05416571469', password: '1234' },
    { id: 'b3', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat', phone: '05416571469', password: '1234' }
  ],
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

    // VELİ NUMARA KONTROLÜ: Kayıtlı öğrenci yoksa kesin olarak reddeder
    if (action === 'verify_parent_phone') {
      const targetPhone = normalizePhone10(body.phone);
      if (targetPhone.length < 10) {
        return NextResponse.json({
          success: false,
          message: 'Lütfen geçerli bir 10 veya 11 haneli cep telefonu numarası giriniz.'
        }, { status: 400 });
      }

      const matchedStudents = store.students.filter((s) => {
        return normalizePhone10(s.anneTel) === targetPhone || normalizePhone10(s.babaTel) === targetPhone;
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
        anneTel: String(body.anneTel || '').trim(),
        babaAdi: String(body.babaAdi || 'Baba').trim(),
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
            anneAdi: String(r.anneAdi || 'Anne').trim(),
            anneTel: String(r.anneTel || '').trim(),
            babaAdi: String(r.babaAdi || 'Baba').trim(),
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
# 2. ANA GİRİŞ VE VELİ PORTALI (app/page.tsx)
#    - Şifre ASLA ekranda gösterilmez, sadece WhatsApp'a gider.
#    - Kayıtlı öğrenci yoksa "Adınıza kayıtlı öğrenci gözükmemektedir" der.
# =========================================================================
PORTAL_PAGE_TSX = r'''"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

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

  // Sadece Veliye Ait Öğrenciler ve İzinler
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
    setErrorMsg('');
    setInfoMsg('');
    setLoading(true);

    try {
      // 1) Önce veritabanında bu numaraya kayıtlı öğrenci var mı kontrol et
      const verifyRes = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'verify_parent_phone', phone })
      });
      const verifyData = await verifyRes.json();

      // Öğrenci yoksa ŞİFRE ÜRETME ve direkt hata mesajını göster!
      if (!verifyRes.ok || !verifyData.success) {
        setErrorMsg(verifyData.message || 'Adınıza kayıtlı öğrenci gözükmemektedir');
        setLoading(false);
        return;
      }

      // 2) Öğrenci varsa 6 haneli gizli şifre üret (EKRANDA ASLA GÖSTERİLMEZ!)
      const secretCode = Math.floor(100000 + Math.random() * 900000).toString();
      setGeneratedOtp(secretCode);

      const childNames = (verifyData.students || []).map((s: any) => s.name).join(', ');
      const customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${childNames}),\nVeli Portalı Giriş Şifreniz: *${secretCode}*\n\n_Güvenliğiniz için bu kodu kimseyle paylaşmayınız._`;

      let sentSuccess = false;

      // Önce aktif Cloudflare tünelinden WhatsApp botuna gönder
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

      // Yerel bilgisayar üzerinden test ediliyorsa localhost:3001 dene
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
      // Ekranda şifre KESİNLİKLE yazmaz, sadece WhatsApp'a gönderildiği bilgisi verilir
      setInfoMsg('Tek kullanımlık 6 haneli giriş şifreniz cep telefonunuzdaki WhatsApp uygulamasına gönderilmiştir.');
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
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex flex-col justify-between">
      {/* ÜST BAŞLIK ÇUBUĞU */}
      <header className="bg-white border-b border-slate-200 px-6 py-3.5">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center font-extrabold text-blue-700 text-xs">
              SBL
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 text-sm md:text-base">
                  Prof. Dr. Mümtaz Turhan SBL Pansiyon
                </span>
                <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full text-[11px] font-semibold">
                  MEB Uyumlu
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                İzin Takip • Etüt Yoklama • Gece Yat Yoklaması • Oda Yönetimi
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* ANA İÇERİK */}
      <main className="flex-1 flex items-center justify-center p-4 md:p-8">
        {step !== 'portal' ? (
          /* GİRİŞ KARTI (Ekran görüntüsündeki kurumsal tasarım) */
          <div className="bg-white rounded-3xl shadow-xl border border-slate-100 max-w-4xl w-full grid grid-cols-1 md:grid-cols-12 overflow-hidden">
            {/* SOL PANEL */}
            <div className="md:col-span-5 bg-gradient-to-b from-[#eef4ff] to-[#e0ebff] p-8 flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-white rounded-2xl shadow-md flex flex-col items-center justify-center mb-5 border border-blue-100">
                <span className="text-xl font-black text-blue-700 leading-none">SBL</span>
                <span className="text-[9px] font-bold text-blue-500 tracking-wider mt-1">PANSİYON</span>
              </div>
              <h2 className="font-extrabold text-slate-800 text-base">
                PROF. DR. MÜMTAZ TURHAN
              </h2>
              <p className="font-bold text-slate-700 text-sm mb-4">
                Sosyal Bilimler Lisesi Pansiyonu
              </p>
              <span className="bg-white/80 text-slate-600 text-xs font-semibold px-4 py-1.5 rounded-full shadow-sm border border-blue-100">
                Pansiyon & Yurt Portalı
              </span>
            </div>

            {/* SAĞ PANEL */}
            <div className="md:col-span-7 p-8 md:p-10 flex flex-col justify-center">
              <div className="text-center mb-6">
                <h1 className="text-2xl font-extrabold text-slate-900">Pansiyon Yönetim Sistemi</h1>
                <p className="text-xs text-slate-500 mt-1">
                  Giriş yapmak için rolünüzü seçip bilgilerinizi giriniz.
                </p>
              </div>

              {/* ROL SEKMELERİ */}
              <div className="grid grid-cols-3 bg-slate-100 p-1.5 rounded-2xl mb-6 text-xs font-bold">
                <button
                  type="button"
                  onClick={() => { setRoleTab('veli'); setErrorMsg(''); }}
                  className={`py-2.5 rounded-xl transition ${
                    roleTab === 'veli' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  👥 Veli
                </button>
                <button
                  type="button"
                  onClick={() => router.push('/belletmen')}
                  className="py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition"
                >
                  👨‍🏫 Belletmen
                </button>
                <button
                  type="button"
                  onClick={() => router.push('/admin')}
                  className="py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition"
                >
                  🛡️ Yönetici
                </button>
              </div>

              {/* HATA MESAJI KUTUSU ("Adınıza kayıtlı öğrenci gözükmemektedir") */}
              {errorMsg && (
                <div className="mb-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold text-center">
                  ⚠️ {errorMsg}
                </div>
              )}

              {/* BİLGİ MESAJI KUTUSU (ŞİFRE İÇERMEZ, SADECE WHATSAPP BİLGİSİ VERİR) */}
              {infoMsg && (
                <div className="mb-4 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold text-center">
                  📲 {infoMsg}
                </div>
              )}

              {step === 'phone' ? (
                <form onSubmit={handleSendOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">
                      Kayıtlı Veli Cep Telefonu Numaranız
                    </label>
                    <input
                      type="tel"
                      required
                      placeholder="05XX XXX XX XX"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full p-3.5 border border-slate-300 rounded-xl text-center text-lg font-bold tracking-wider focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl font-bold text-sm shadow-md transition"
                  >
                    {loading ? 'Öğrenci Kaydı Kontrol Ediliyor...' : '📲 WhatsApp İle Giriş Kodu Gönder'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <p className="text-[11px] text-slate-500 text-center">
                    Şifresiz Güvenli Giriş: WhatsApp mesajınıza gelen 6 haneli kodu giriniz
                  </p>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1.5 text-center">
                      Gelen 6 Haneli Kodu Giriniz
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
                    ✅ Doğrula ve Portala Gir
                  </button>
                  <button
                    type="button"
                    onClick={() => { setStep('phone'); setInfoMsg(''); setErrorMsg(''); setOtpInput(''); }}
                    className="w-full text-xs text-slate-500 hover:text-slate-800 underline py-1"
                  >
                    Telefon numarasını değiştir
                  </button>
                </form>
              )}

              <div className="mt-8 pt-4 border-t border-slate-100 text-center text-[11px] text-slate-400">
                © 2026 Prof. Dr. Mümtaz Turhan SBL
              </div>
            </div>
          </div>
        ) : (
          /* VELİ ÖZEL PORTALI (SADECE KENDİ ÖĞRENCİSİ GÖRÜNÜR) */
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
                        ? 'bg-blue-600 text-white shadow'
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
                {/* ÖĞRENCİ BİLGİ VE İSTATİSTİK KARTI */}
                <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-4">
                  <div className="flex items-center justify-between border-b pb-3">
                    <div>
                      <span className="text-[11px] font-bold uppercase text-blue-600">Öğrenciniz</span>
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
                      <span className="text-blue-600 block">Toplam Kullanılan İzin Sayısı</span>
                      <strong className="text-base font-extrabold text-blue-900">
                        {activeStudentLeaves.length} İzin Kaydı
                      </strong>
                    </div>
                  </div>
                </div>

                {/* SADECE KENDİ ÖĞRENCİSİNE İZİN ALMA FORMU */}
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
                          className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-xl font-bold shadow transition"
                        >
                          {loading ? 'Kaydediliyor...' : '✅ İzin Talebini Onayla'}
                        </button>
                      </div>
                    </form>
                  </div>

                  {/* GEÇMİŞ İZİNLER */}
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
                              <span className="font-bold text-blue-700">{lv.tip}</span>
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

      {/* ALT BİLGİ */}
      <footer className="border-t border-slate-200 bg-white px-6 py-3 text-[11px] text-slate-400">
        <div className="max-w-6xl mx-auto flex justify-between">
          <span>© 2026 Pansiyon ve Yurt Takip Sistemi • MEB Standartlarına Uygun</span>
          <span>Güvenli Veritabanı • Rol Tabanlı Doğrulama</span>
        </div>
      </footer>
    </div>
  );
}
'''

def main():
    print("================================================================")
    print("   VELİ GİRİŞ GÜVENLİĞİ (GİZLİ WHATSAPP KODU & NUMARA KONTROLÜ)")
    print("================================================================")

    db_url = get_saved_db_url()
    if not db_url:
        db_url = input("Lütfen Neon DATABASE_URL adresinizi girin: ").strip().strip('"').strip("'")

    write_file("app/api/pansiyon/route.ts", API_ROUTE_TS.replace("__USER_DATABASE_URL__", db_url))
    write_file("app/page.tsx", PORTAL_PAGE_TSX)

    print("\n🚀 Next.js derleniyor ve Vercel ana adresine gönderiliyor...")
    if subprocess.run("npm run build", shell=True).returncode != 0:
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    subprocess.run("git add app/api/pansiyon/route.ts app/page.tsx", shell=True)
    subprocess.run('git commit -m "Veli girisinde ekranda sifre gosterimi kaldirildi ve kayitsiz numara uyarisi eklendi" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    print("\n================================================================")
    print("🎉 GÜNCELLEME TAMAMLANDI!")
    print("⚠️ ÖNEMLİ: Lütfen eski '-k1o9l8hv3-' uzantılı adresi kapatıp")
    print("   doğrudan ana adresinizden giriş yapın:")
    print("👉 https://pansiyon-yurt-sistemi.vercel.app")
    print("================================================================")

if __name__ == "__main__":
    main()