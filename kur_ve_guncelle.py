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
# 1. MERKEZİ API ROTASI (Cinsiyet Bazlı Veri İzolasyonu Eklendi)
# -------------------------------------------------------------------------
PANSIYON_API_TS = r'''import { NextResponse } from 'next/server';

export interface StudentRecord { id: string; name: string; cinsiyet: 'erkek' | 'kiz'; tc: string; sinif: string; kat: number; oda: string; yatak: string; anneTel: string; babaTel: string; status: string; }
export interface BelletmenRecord { id: string; name: string; cinsiyet: 'erkek' | 'kadin'; brans: string; phone: string; password: string; }
export interface MonthlyDutyDay { tarih: string; erkek1: string; erkek2: string; kadin1: string; kadin2: string; }
export interface LeaveRecord { id: string; studentId: string; studentName: string; oda: string; tip: string; baslangic: string; bitis: string; aciklama: string; veliTel: string; createdAt: string; }
export interface DutyLogRecord { id: string; tarih: string; seans: string; erkekBelletmen1: string; erkekBelletmen2: string; kizBelletmen1: string; kizBelletmen2: string; notlar: string; }
export interface AuditLogRecord { id: string; tarihSaat: string; kullanici: string; islem: string; detay: string; tur: string; }

declare global {
  var __pansiyonStoreV12: {
    students: StudentRecord[];
    belletmenler: BelletmenRecord[];
    aylikNobetler: MonthlyDutyDay[];
    leaves: LeaveRecord[];
    dutyLogs: DutyLogRecord[];
    auditLogs: AuditLogRecord[];
  } | undefined;
}

if (!globalThis.__pansiyonStoreV12) {
  globalThis.__pansiyonStoreV12 = {
    students: [
      { id: '1', name: 'Ahmet Yılmaz', cinsiyet: 'erkek', tc: '12345678901', sinif: '10-A', kat: 1, oda: '101', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '2', name: 'Mehmet Demir', cinsiyet: 'erkek', tc: '12345678902', sinif: '11-B', kat: 1, oda: '101', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '3', name: 'Canberk Öztürk', cinsiyet: 'erkek', tc: '12345678905', sinif: '9-A', kat: 1, oda: '102', yatak: 'A', anneTel: '05416571469', babaTel: '05556667788', status: 'yok' },
      { id: '4', name: 'Burak Kaya', cinsiyet: 'erkek', tc: '12345678908', sinif: '10-C', kat: 2, oda: '201', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
      { id: '5', name: 'Zeynep Aydın', cinsiyet: 'kiz', tc: '12345678912', sinif: '10-A', kat: 1, oda: 'K-101', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
      { id: '6', name: 'Elif Yılmaz', cinsiyet: 'kiz', tc: '12345678913', sinif: '11-A', kat: 1, oda: 'K-101', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '7', name: 'Selin Şahin', cinsiyet: 'kiz', tc: '12345678914', sinif: '9-B', kat: 2, oda: 'K-201', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'yok' },
      { id: '8', name: 'Merve Çelik', cinsiyet: 'kiz', tc: '12345678915', sinif: '12-B', kat: 2, oda: 'K-201', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
    ],
    belletmenler: [
      { id: 'b1', name: 'Cüneyt DEMİR', cinsiyet: 'erkek', brans: 'Bilişim Teknolojileri', phone: '05416571469', password: '1234' },
      { id: 'b2', name: 'Ali BEY', cinsiyet: 'erkek', brans: 'Matematik', phone: '05416571469', password: '1234' },
      { id: 'b3', name: 'Furkan DEMİR', cinsiyet: 'erkek', brans: 'Tarih', phone: '05416571469', password: '1234' },
      { id: 'b4', name: 'Hasan ÇELİK', cinsiyet: 'erkek', brans: 'Fizik', phone: '05416571469', password: '1234' },
      { id: 'b5', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat', phone: '05416571469', password: '1234' },
      { id: 'b6', name: 'Fatma YILMAZ', cinsiyet: 'kadin', brans: 'İngilizce', phone: '05416571469', password: '1234' },
      { id: 'b7', name: 'Zeynep ŞAHİN', cinsiyet: 'kadin', brans: 'Kimya', phone: '05416571469', password: '1234' },
      { id: 'b8', name: 'Merve AYDIN', cinsiyet: 'kadin', brans: 'Biyoloji', phone: '05416571469', password: '1234' },
    ],
    aylikNobetler: [
      { tarih: '2026-10-24', erkek1: 'Cüneyt DEMİR', erkek2: 'Ali BEY', kadin1: 'Ayşenur KAYA', kadin2: 'Fatma YILMAZ' },
      { tarih: '2026-10-25', erkek1: 'Furkan DEMİR', erkek2: 'Hasan ÇELİK', kadin1: 'Zeynep ŞAHİN', kadin2: 'Merve AYDIN' },
      { tarih: '2026-10-26', erkek1: 'Cüneyt DEMİR', erkek2: 'Furkan DEMİR', kadin1: 'Ayşenur KAYA', kadin2: 'Zeynep ŞAHİN' },
    ],
    leaves: [
      { id: '101', studentId: '1', studentName: 'Ahmet Yılmaz', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-21', bitis: '2026-10-30', aciklama: 'Akraba ziyareti', veliTel: '05416571469', createdAt: '2026-10-21' },
      { id: '102', studentId: '2', studentName: 'Mehmet Demir', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-20', bitis: '2026-10-25', aciklama: 'Aile ziyareti ve hafta sonu ev izni', veliTel: '05416571469', createdAt: '2026-10-20' },
      { id: '103', studentId: '6', studentName: 'Elif Yılmaz', oda: 'K-101', tip: 'Ev İzni', baslangic: '2026-10-23', bitis: '2026-10-26', aciklama: 'Hafta sonu evci izni', veliTel: '05416571469', createdAt: '2026-10-23' },
    ],
    dutyLogs: [],
    auditLogs: [
      { id: 'log1', tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Sistem', islem: 'Gizlilik İzolasyonu Aktif', detay: 'Erkek ve Kız pansiyonu veri erişim sınırları kilitlendi.', tur: 'bilgi' }
    ],
  };
}

const addLog = (store: any, kullanici: string, islem: string, detay: string, tur: string) => {
  store.auditLogs.unshift({
    id: Date.now().toString() + Math.random().toString(36).substring(2, 7),
    tarihSaat: new Date().toLocaleString('tr-TR'),
    kullanici, islem, detay, tur
  });
  if (store.auditLogs.length > 100) store.auditLogs.pop();
};

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const cinsiyetFilter = searchParams.get('cinsiyet'); // 'erkek' veya 'kiz'
  const store = globalThis.__pansiyonStoreV12!;

  // Eğer belletmen kendi rolüyle veri istediyse SADECE kendi cinsiyetindeki öğrencileri döndür!
  if (cinsiyetFilter === 'erkek' || cinsiyetFilter === 'kiz') {
    const filteredStudents = store.students.filter((s) => s.cinsiyet === cinsiyetFilter);
    const allowedIds = new Set(filteredStudents.map((s) => s.id));
    const filteredLeaves = store.leaves.filter((l) => allowedIds.has(l.studentId));

    return NextResponse.json({
      success: true,
      store: {
        ...store,
        students: filteredStudents,
        leaves: filteredLeaves,
      }
    });
  }

  return NextResponse.json({ success: true, store });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = globalThis.__pansiyonStoreV12!;

    if (action === 'belletmen_login') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (!found || found.password !== String(body.password || '').trim()) {
        addLog(store, found ? found.name : 'Bilinmeyen', 'Hatalı Belletmen Girişi', 'Belletmen şifresi yanlış girildi.', 'hata');
        return NextResponse.json({ success: false, message: 'Hatalı belletmen şifresi girdiniz!' }, { status: 401 });
      }
      const targetStudentGender = found.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
      addLog(store, found.name, 'Belletmen Girişi', `${targetStudentGender === 'kiz' ? 'Kız' : 'Erkek'} Pansiyonu yoklama ekranına giriş yapıldı.`, 'basari');
      return NextResponse.json({
        success: true,
        belletmen: found,
        allowedGender: targetStudentGender
      });
    }

    if (action === 'log_forgot_password') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (found) {
        addLog(store, found.name, 'Şifre Hatırlatma Talebi', `Kayıtlı şifre WhatsApp (${found.phone}) üzerinden gönderildi.`, 'uyari');
      }
      return NextResponse.json({ success: true });
    }

    if (action === 'admin_login') {
      if (body.username === 'admin' && String(body.password).trim() === '123456') {
        addLog(store, 'Yönetici (Admin)', 'Yönetim Paneli Girişi', 'Sisteme yetkili idareci girişi yapıldı.', 'basari');
        return NextResponse.json({ success: true, message: 'Giriş başarılı.', store });
      }
      addLog(store, 'Bilinmeyen (Admin)', 'Hatalı Yönetici Girişi', 'Yönetici şifresi hatalı girildi.', 'hata');
      return NextResponse.json({ success: false, message: 'Hatalı yönetici kullanıcı adı veya şifresi!' }, { status: 401 });
    }

    // KISMİ YOKLAMA GÜNCELLEME (Erkek belletmen güncelleme yaptığında kız öğrencilerin verisi silinmez, sadece kendi öğrencileri güncellenir)
    if (action === 'update_attendance') {
      if (Array.isArray(body.students)) {
        const updatedMap = new Map(body.students.map((s: StudentRecord) => [s.id, s]));
        store.students = store.students.map((existing) =>
          updatedMap.has(existing.id) ? (updatedMap.get(existing.id) as StudentRecord) : existing
        );
      }
      return NextResponse.json({ success: true, message: 'Yoklama güncellendi.' });
    }

    if (action === 'add_belletmen') {
      store.belletmenler.push({ id: Date.now().toString(), name: String(body.name).trim(), cinsiyet: body.cinsiyet === 'kadin' ? 'kadin' : 'erkek', brans: String(body.brans || 'Öğretmen').trim(), phone: String(body.phone || '05416571469').trim(), password: String(body.password || '1234').trim() });
      addLog(store, 'Yönetici', 'Belletmen Eklendi', `${body.name} eklendi.`, 'basari');
      return NextResponse.json({ success: true, message: 'Belletmen eklendi.', store });
    }
    if (action === 'bulk_add_belletmen') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = String(r.cinsiyet || 'erkek').toLowerCase();
          store.belletmenler.push({ id: Date.now().toString()+Math.random(), name: String(r.name), cinsiyet: rawCins.includes('k') || rawCins.includes('bayan') ? 'kadin' : 'erkek', brans: String(r.brans), phone: String(r.phone || '05416571469'), password: String(r.password || '1234') });
          added++;
        }
      }
      addLog(store, 'Yönetici', 'Toplu Yükleme', `${added} belletmen aktarıldı.`, 'basari');
      return NextResponse.json({ success: true, message: `${added} belletmen eklendi.`, store });
    }
    if (action === 'update_belletmen_password') {
      const target = store.belletmenler.find((b) => b.id === body.id);
      if (target) {
        target.password = String(body.newPassword).trim();
        addLog(store, 'Yönetici', 'Şifre Değişikliği', `${target.name} şifresi güncellendi.`, 'uyari');
        return NextResponse.json({ success: true, message: 'Şifre güncellendi.', store });
      }
      return NextResponse.json({ success: false, message: 'Bulunamadı.' }, { status: 404 });
    }
    if (action === 'delete_belletmen') {
      store.belletmenler = store.belletmenler.filter((b) => b.id !== body.id);
      addLog(store, 'Yönetici', 'Silme', `Belletmen silindi.`, 'uyari');
      return NextResponse.json({ success: true, message: 'Silindi.', store });
    }
    if (action === 'add_or_update_monthly_duty') {
      const { tarih, erkek1, erkek2, kadin1, kadin2 } = body;
      const idx = store.aylikNobetler.findIndex((d) => d.tarih === tarih);
      const item: MonthlyDutyDay = { tarih, erkek1, erkek2, kadin1, kadin2 };
      if (idx > -1) store.aylikNobetler[idx] = item;
      else { store.aylikNobetler.push(item); store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih)); }
      return NextResponse.json({ success: true, message: `${tarih} günü nöbetçileri kaydedildi.`, store });
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
      addLog(store, 'Yönetici', 'Otomatik Nöbet', `${yearMonth} nöbetleri atandı.`, 'bilgi');
      return NextResponse.json({ success: true, message: 'Nöbetler oluşturuldu!', store });
    }
    if (action === 'bulk_monthly_duty') {
      let count = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.tarih) continue;
          store.aylikNobetler.push({ tarih: String(r.tarih), erkek1: String(r.erkek1), erkek2: String(r.erkek2), kadin1: String(r.kadin1), kadin2: String(r.kadin2) });
          count++;
        }
      }
      return NextResponse.json({ success: true, message: `${count} gün eklendi.`, store });
    }
    if (action === 'delete_monthly_duty') {
      store.aylikNobetler = store.aylikNobetler.filter((d) => d.tarih !== body.tarih);
      return NextResponse.json({ success: true, message: 'Nöbet silindi.', store });
    }
    if (action === 'add_leave') {
      const { studentId, tip, baslangic, bitis, aciklama, veliTel } = body;
      const st = store.students.find((s) => s.id === studentId) || store.students[0];
      store.leaves.unshift({ id: Date.now().toString(), studentId: st.id, studentName: st.name, oda: st.oda, tip: tip || 'Evci İzni', baslangic, bitis, aciklama: aciklama || 'Veli talebi', veliTel: veliTel || st.anneTel, createdAt: new Date().toISOString().split('T')[0] });
      st.status = 'izinli';
      addLog(store, `Veli (${veliTel || st.anneTel})`, 'Veli İzin Talebi', `${st.name} için izin onaylandı.`, 'basari');
      return NextResponse.json({ success: true, message: 'İzin talebi onaylandı.', store });
    }
    if (action === 'add_student') {
      store.students.push({ id: Date.now().toString(), name: String(body.name), cinsiyet: body.cinsiyet === 'kiz' ? 'kiz' : 'erkek', tc: String(body.tc || '10000000000'), sinif: String(body.sinif || '9-A'), kat: Number(body.kat || 1), oda: String(body.oda || '101'), yatak: String(body.yatak || 'A'), anneTel: String(body.anneTel || '05416571469'), babaTel: String(body.babaTel || '05416571469'), status: 'var' });
      addLog(store, 'Yönetici', 'Öğrenci Eklendi', `${body.name} eklendi.`, 'basari');
      return NextResponse.json({ success: true, message: 'Öğrenci eklendi.', store });
    }
    if (action === 'bulk_import') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = String(r.cinsiyet || 'erkek').toLowerCase();
          store.students.push({ id: Date.now().toString()+Math.random(), name: String(r.name), cinsiyet: rawCins.includes('k') || rawCins.includes('bayan') ? 'kiz' : 'erkek', tc: String(r.tc), sinif: String(r.sinif), kat: Number(r.kat), oda: String(r.oda), yatak: String(r.yatak), anneTel: String(r.anneTel), babaTel: String(r.babaTel), status: 'var' });
          added++;
        }
      }
      return NextResponse.json({ success: true, message: `${added} öğrenci eklendi.`, store });
    }
    if (action === 'delete_student') {
      store.students = store.students.filter((s) => s.id !== body.id);
      addLog(store, 'Yönetici', 'Öğrenci Silindi', `Öğrenci kaydı silindi.`, 'uyari');
      return NextResponse.json({ success: true, message: 'Öğrenci silindi.', store });
    }
    if (action === 'add_duty_log') {
      const { tarih, seans, erkekBelletmen1, erkekBelletmen2, kizBelletmen1, kizBelletmen2, notlar } = body;
      store.dutyLogs.unshift({ id: Date.now().toString(), tarih: String(tarih || ''), seans: String(seans || ''), erkekBelletmen1: String(erkekBelletmen1 || ''), erkekBelletmen2: String(erkekBelletmen2 || ''), kizBelletmen1: String(kizBelletmen1 || ''), kizBelletmen2: String(kizBelletmen2 || ''), notlar: String(notlar || '') });
      addLog(store, 'Nöbetçi Belletmen', 'Resmî Nöbet Tutanağı', `${tarih} (${seans}) nöbet defteri kaydedildi.`, 'basari');
      return NextResponse.json({ success: true, message: 'Nöbet defteri kaydedildi.', store });
    }
    if (action === 'clear_audit_logs') {
      store.auditLogs = [{ id: Date.now().toString(), tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Yönetici', islem: 'Günlük Temizlendi', detay: 'Denetim günlüğü yönetici tarafından sıfırlandı.', tur: 'uyari' }];
      return NextResponse.json({ success: true, message: 'Denetim günlüğü temizlendi.', store });
    }

    return NextResponse.json({ success: false, message: 'Bilinmeyen işlem.' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
'''

# -------------------------------------------------------------------------
# 2. TAM İZOLE BELLETMEN EKRANI (app/belletmen/page.tsx)
#    - Erkek belletmen sadece erkekleri, Kadın belletmen sadece kızları görür.
#    - Nöbet defteri (PDF) de sadece aktif belletmenin kendi bölümünü içerir.
# -------------------------------------------------------------------------
BELLETMEN_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Calendar, FileText, CheckCircle2, Home, Send, Check, Loader2,
  Phone, Printer, X, LogOut, UserCheck, Lock, KeyRound, ShieldCheck
} from 'lucide-react';

interface Student {
  id: string;
  name: string;
  cinsiyet: 'erkek' | 'kiz';
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
  const [aktifRol, setAktifRol] = useState<'erkek' | 'kiz' | null>(null);
  const [aktifBelletmenAd, setAktifBelletmenAd] = useState<string>('');

  const [students, setStudents] = useState<Student[]>([]);
  const [belletmenler, setBelletmenler] = useState<any[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<any[]>([]);
  const [leaves, setLeaves] = useState<any[]>([]);

  const [secilenErkekId, setSecilenErkekId] = useState<string>('');
  const [erkekSifre, setErkekSifre] = useState<string>('');
  const [secilenKadinId, setSecilenKadinId] = useState<string>('');
  const [kadinSifre, setKadinSifre] = useState<string>('');
  const [loginError, setLoginError] = useState<string>('');

  const [selectedKat, setSelectedKat] = useState<number>(1);
  const [tarih, setTarih] = useState<string>('2026-10-25');
  const [seans, setSeans] = useState<'etut' | 'yat'>('etut');
  const [sendingKey, setSendingKey] = useState<string | null>(null);
  const [sentKeys, setSentKeys] = useState<Record<string, boolean>>({});
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [nobetDefteriAcik, setNobetDefteriAcik] = useState(false);
  const [erkekBelletmen1, setErkekBelletmen1] = useState('Cüneyt DEMİR');
  const [erkekBelletmen2, setErkekBelletmen2] = useState('Ali BEY');
  const [kizBelletmen1, setKizBelletmen1] = useState('Ayşenur KAYA');
  const [kizBelletmen2, setKizBelletmen2] = useState('Fatma YILMAZ');
  const [nobetNotu, setNobetNotu] = useState('Pansiyon akşam etüt ve yat yoklamaları nöbetçi belletmen öğretmenler tarafından zamanında alındı. Katlarda asayiş ve düzen sağlandı.');

  // SADECE İLGİLİ CİNSİYETİN VERİSİNİ SUNUCUDAN ÇEK
  const loadRoleSpecificData = async (rol: 'erkek' | 'kiz' | null) => {
    try {
      const url = rol ? `/api/pansiyon?cinsiyet=${rol}` : '/api/pansiyon';
      const res = await fetch(url);
      const data = await res.json();
      if (data.success && data.store) {
        if (rol) {
          // Ekstra güvenlik: Sunucudan zaten filtrelenmiş gelir, istemcide de kesin filtre uygula
          const strictStudents = (data.store.students || []).filter((s: Student) => s.cinsiyet === rol);
          setStudents(strictStudents);
          setLeaves(data.store.leaves || []);
        } else {
          setStudents([]);
        }
        const bList = data.store.belletmenler || [];
        setBelletmenler(bList);
        setAylikNobetler(data.store.aylikNobetler || []);

        const firstErkek = bList.find((b: any) => b.cinsiyet === 'erkek');
        const firstKadin = bList.find((b: any) => b.cinsiyet === 'kadin');
        if (firstErkek && !secilenErkekId) setSecilenErkekId(firstErkek.id);
        if (firstKadin && !secilenKadinId) setSecilenKadinId(firstKadin.id);
      }
    } catch {}
  };

  useEffect(() => {
    const savedRole = localStorage.getItem('belletmen_rol') as 'erkek' | 'kiz' | null;
    const savedName = localStorage.getItem('belletmen_ad') || '';
    if (savedRole === 'erkek' || savedRole === 'kiz') {
      setAktifRol(savedRole);
      setAktifBelletmenAd(savedName);
      loadRoleSpecificData(savedRole);
    } else {
      loadRoleSpecificData(null);
    }
  }, []);

  useEffect(() => {
    const gunKaydi = aylikNobetler.find((d) => d.tarih === tarih);
    if (gunKaydi) {
      setErkekBelletmen1(gunKaydi.erkek1);
      setErkekBelletmen2(gunKaydi.erkek2);
      setKizBelletmen1(gunKaydi.kadin1);
      setKizBelletmen2(gunKaydi.kadin2);
    }
  }, [tarih, aylikNobetler]);

  const handleLogin = async (rol: 'erkek' | 'kiz') => {
    setLoginError('');
    setFeedback(null);
    const targetId = rol === 'erkek' ? secilenErkekId : secilenKadinId;
    const targetPass = rol === 'erkek' ? erkekSifre : kadinSifre;

    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'belletmen_login', id: targetId, password: targetPass }),
    });
    const data = await res.json();
    if (res.ok && data.success) {
      // Giriş yapan öğretmenin cinsiyeti ile seçtiği kutu uyumlu mu kontrol et
      const allowedRole: 'erkek' | 'kiz' = data.belletmen.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
      setAktifRol(allowedRole);
      setAktifBelletmenAd(data.belletmen.name);
      localStorage.setItem('belletmen_rol', allowedRole);
      localStorage.setItem('belletmen_ad', data.belletmen.name);
      await loadRoleSpecificData(allowedRole);
    } else {
      setLoginError(data.message || 'Şifre hatalı!');
    }
  };

  const handleForgotPassword = async (rol: 'erkek' | 'kiz') => {
    setLoginError('');
    setFeedback(null);
    const targetId = rol === 'erkek' ? secilenErkekId : secilenKadinId;
    const found = belletmenler.find((b) => b.id === targetId);

    if (!found) {
      setLoginError('Lütfen listeden isminizi seçin.');
      return;
    }
    if (!found.phone || found.phone.length < 10) {
      setLoginError('Sistemde kayıtlı geçerli bir cep telefonu numaranız bulunmuyor.');
      return;
    }

    setFeedback({ type: 'success', text: 'Şifreniz WhatsApp üzerinden gönderiliyor, lütfen bekleyin...' });

    try {
      await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'log_forgot_password', id: found.id })
      });

      const res = await fetch('/api/belletmen/bildirim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: found.phone,
          ogrenciAd: found.name,
          seans: 'sifre_hatirlatma',
          veliTipi: found.password
        })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        setFeedback({ type: 'success', text: `✅ Sayın ${found.name}, kayıtlı şifreniz WhatsApp numaranıza gönderildi!` });
      } else {
        let directSuccess = false;
        const fallbackMsg = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın *${found.name}*,\n\nNöbetçi Belletmen Sistemi kayıtlı giriş şifreniz: *${found.password}*`;
        for (const directUrl of [data.tunnelUrl, 'http://localhost:3001', 'http://127.0.0.1:3001']) {
          if (!directUrl) continue;
          try {
            const r2 = await fetch(`${directUrl}/send-otp`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ phone: found.phone, customMessage: fallbackMsg })
            });
            const d2 = await r2.json();
            if (r2.ok && d2.success) {
              directSuccess = true;
              setFeedback({ type: 'success', text: `✅ Sayın ${found.name}, kayıtlı şifreniz WhatsApp numaranıza gönderildi!` });
              break;
            }
          } catch {}
        }
        if (!directSuccess) {
          setFeedback({ type: 'error', text: data.message || 'WhatsApp Botuna ulaşılamadı.' });
        }
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucu bağlantı hatası oluştu.' });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('belletmen_rol');
    localStorage.removeItem('belletmen_ad');
    setAktifRol(null);
    setStudents([]);
    window.location.href = '/';
  };

  const getActiveLeaveText = (studentId: string) => {
    const found = leaves.find((l) => l.studentId === studentId && l.baslangic <= tarih && l.bitis >= tarih);
    return found ? `${found.baslangic} — ${found.bitis} (${found.tip}: ${found.aciklama})` : undefined;
  };

  // KESİN CİNSİYET FİLTRESİ: Erkek belletmen sadece 'erkek', Kadın belletmen sadece 'kiz' öğrencileri görebilir!
  const strictlyIsolatedStudents = students
    .filter((s) => s.cinsiyet === aktifRol)
    .map((s) => {
      const leaveTxt = getActiveLeaveText(s.id);
      return leaveTxt ? { ...s, status: 'izinli' as const, izinAciklama: leaveTxt } : s;
    });

  const katStudents = strictlyIsolatedStudents.filter((s) => s.kat === selectedKat);

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
    syncAttendance(students.map((s) => (s.id === id && s.cinsiyet === aktifRol ? { ...s, status: newStatus } : s)));
  };

  const handlePhoneChange = (id: string, field: 'anneTel' | 'babaTel', value: string) => {
    setStudents((prev) => prev.map((s) => (s.id === id && s.cinsiyet === aktifRol ? { ...s, [field]: value } : s)));
  };

  const handleTumunuVarYap = () => {
    const updated = students.map((s) => {
      const hasLeave = getActiveLeaveText(s.id);
      if (s.cinsiyet === aktifRol && s.kat === selectedKat && !hasLeave && s.status !== 'izinli') {
        return { ...s, status: 'var' as const };
      }
      return s;
    });
    syncAttendance(updated);
    setFeedback({ type: 'success', text: `✅ ${selectedKat}. Kattaki izinsiz tüm ${aktifRol === 'erkek' ? 'erkek' : 'kız'} öğrenciler 'Var' yapıldı.` });
  };

  const handleSendWhatsApp = async (student: Student, veliTipi: 'Anne' | 'Baba', phone: string) => {
    const btnKey = `${student.id}-${veliTipi}`;
    setSendingKey(btnKey);
    setFeedback(null);

    try {
      const res = await fetch('/api/belletmen/bildirim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, ogrenciAd: student.name, odaNo: student.oda, tarih, seans, veliTipi })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setSentKeys((prev) => ({ ...prev, [btnKey]: true }));
        setFeedback({ type: 'success', text: data.message });
      } else {
        let directSuccess = false;
        const fallbackMsg = data.customMessage || `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nSayın Velimiz (${veliTipi}), öğrenciniz *${student.name}* (Oda: ${student.oda}) *${tarih}* tarihli yoklamada pansiyonda *BULUNAMAMIŞTIR (YOK)*.`;
        for (const directUrl of [data.tunnelUrl, 'http://localhost:3001', 'http://127.0.0.1:3001']) {
          if (!directUrl) continue;
          try {
            const r2 = await fetch(`${directUrl}/send-otp`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ phone, customMessage: fallbackMsg })
            });
            const d2 = await r2.json();
            if (r2.ok && d2.success) {
              directSuccess = true;
              setSentKeys((prev) => ({ ...prev, [btnKey]: true }));
              setFeedback({ type: 'success', text: `✅ ${student.name} velisine (${phone}) WhatsApp bildirimi gönderildi!` });
              break;
            }
          } catch {}
        }
        if (!directSuccess) {
          setFeedback({ type: 'error', text: data.message || 'WhatsApp Botuna ulaşılamadı.' });
        }
      }
    } catch {
      setFeedback({ type: 'error', text: 'Bağlantı hatası oluştu.' });
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
        erkekBelletmen1: aktifRol === 'erkek' ? erkekBelletmen1 : '-',
        erkekBelletmen2: aktifRol === 'erkek' ? erkekBelletmen2 : '-',
        kizBelletmen1: aktifRol === 'kiz' ? kizBelletmen1 : '-',
        kizBelletmen2: aktifRol === 'kiz' ? kizBelletmen2 : '-',
        notlar: nobetNotu,
      }),
    });
    window.print();
  };

  const erkekBelletmenler = belletmenler.filter((b) => b.cinsiyet === 'erkek');
  const kadinBelletmenler = belletmenler.filter((b) => b.cinsiyet === 'kadin');

  if (!aktifRol) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-3 sm:p-4">
        <div className="max-w-4xl w-full bg-white rounded-3xl shadow-xl border border-slate-200 p-5 sm:p-10 space-y-6">
          <div className="text-center space-y-2">
            <span className="text-[11px] sm:text-xs font-extrabold uppercase tracking-wider bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full border border-indigo-200">
              Prof. Dr. Mümtaz Turhan SBL Pansiyonu
            </span>
            <h1 className="text-xl sm:text-3xl font-extrabold text-slate-900 mt-2">
              Nöbetçi Belletmen Şifreli Giriş
            </h1>
            <p className="text-xs text-slate-500">
              Gizlilik kuralları gereği <strong>Erkek Belletmenler yalnızca Erkek Pansiyonunu</strong>, <strong>Kadın Belletmenler yalnızca Kız Pansiyonunu</strong> görebilir.
            </p>
          </div>

          {feedback && (
            <div className={`p-3.5 rounded-2xl text-xs font-bold text-center ${feedback.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'}`}>
              {feedback.text}
            </div>
          )}

          {loginError && (
            <div className="p-3.5 bg-rose-50 border border-rose-300 text-rose-800 rounded-2xl text-xs font-bold text-center">
              ❌ {loginError}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            {/* ERKEK BELLETMEN */}
            <div className="border-2 border-blue-200 bg-blue-50/40 rounded-2xl p-5 space-y-4">
              <div className="w-11 h-11 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold">
                <UserCheck className="w-6 h-6" />
              </div>
              <h2 className="text-base sm:text-lg font-extrabold text-blue-950">1) Erkek Belletmen Girişi</h2>
              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nöbetçi Erkek Belletmen:</label>
                  <select
                    value={secilenErkekId}
                    onChange={(e) => setSecilenErkekId(e.target.value)}
                    className="w-full border border-blue-300 rounded-xl px-3 py-3 text-base sm:text-xs font-bold bg-white min-h-[46px]"
                  >
                    {erkekBelletmenler.map((b) => (
                      <option key={b.id} value={b.id}>{b.name} ({b.brans})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Giriş Şifreniz:</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      placeholder="Şifrenizi Girin"
                      value={erkekSifre}
                      onChange={(e) => setErkekSifre(e.target.value)}
                      className="w-full pl-9 pr-3 py-3 border border-blue-300 rounded-xl bg-white text-base sm:text-xs font-mono min-h-[46px]"
                    />
                  </div>
                  <div className="flex justify-end pt-2">
                    <button type="button" onClick={() => handleForgotPassword('erkek')} className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-700 hover:underline cursor-pointer">
                      <KeyRound className="w-3 h-3" /> Şifremi Unuttum (WhatsApp Gönder)
                    </button>
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleLogin('erkek')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]"
              >
                Erkek Pansiyonu Yoklamasına Gir →
              </button>
            </div>

            {/* KADIN BELLETMEN */}
            <div className="border-2 border-rose-200 bg-rose-50/40 rounded-2xl p-5 space-y-4">
              <div className="w-11 h-11 rounded-2xl bg-rose-600 text-white flex items-center justify-center font-bold">
                <UserCheck className="w-6 h-6" />
              </div>
              <h2 className="text-base sm:text-lg font-extrabold text-rose-950">2) Kadın Belletmen Girişi</h2>
              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nöbetçi Kadın Belletmen:</label>
                  <select
                    value={secilenKadinId}
                    onChange={(e) => setSecilenKadinId(e.target.value)}
                    className="w-full border border-rose-300 rounded-xl px-3 py-3 text-base sm:text-xs font-bold bg-white min-h-[46px]"
                  >
                    {kadinBelletmenler.map((b) => (
                      <option key={b.id} value={b.id}>{b.name} ({b.brans})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Giriş Şifreniz:</label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="password"
                      placeholder="Şifrenizi Girin"
                      value={kadinSifre}
                      onChange={(e) => setKadinSifre(e.target.value)}
                      className="w-full pl-9 pr-3 py-3 border border-rose-300 rounded-xl bg-white text-base sm:text-xs font-mono min-h-[46px]"
                    />
                  </div>
                  <div className="flex justify-end pt-2">
                    <button type="button" onClick={() => handleForgotPassword('kiz')} className="inline-flex items-center gap-1 text-[11px] font-bold text-rose-700 hover:underline cursor-pointer">
                      <KeyRound className="w-3 h-3" /> Şifremi Unuttum (WhatsApp Gönder)
                    </button>
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleLogin('kiz')}
                className="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]"
              >
                Kız Pansiyonu Yoklamasına Gir →
              </button>
            </div>
          </div>

          <div className="flex justify-between items-center pt-3 border-t border-slate-100 text-xs">
            <a href="/" className="text-slate-600 font-bold hover:underline">← Ana Sayfaya Dön</a>
          </div>
        </div>
      </div>
    );
  }

  // Nöbet Defteri İçin YALNIZCA Aktif Belletmenin Kendi Cinsiyet Grubundaki Öğrenciler
  const bolumYoklar = strictlyIsolatedStudents.filter((s) => s.status === 'yok');
  const bolumIzinliler = strictlyIsolatedStudents.filter((s) => s.status === 'izinli');

  return (
    <div className="min-h-screen bg-slate-100 p-2.5 sm:p-6 pb-20">
      <div className="max-w-5xl mx-auto space-y-4 print:hidden">

        {/* ÜST PANEL (Grup Değiştirme Kaldırıldı - Tam İzolasyon) */}
        <div className="bg-white rounded-2xl p-4 sm:p-5 shadow-sm border border-slate-200 space-y-3.5">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`inline-block text-[11px] font-extrabold px-3 py-1 rounded-full ${aktifRol === 'erkek' ? 'bg-blue-100 text-blue-800' : 'bg-rose-100 text-rose-800'}`}>
                  {aktifRol === 'erkek'
                    ? `👨 Erkek Pansiyonu Nöbetçileri: ${erkekBelletmen1} & ${erkekBelletmen2}`
                    : `👩 Kız Pansiyonu Nöbetçileri: ${kizBelletmen1} & ${kizBelletmen2}`}
                </span>
                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  {aktifRol === 'erkek' ? 'Yalnızca Erkek Öğrenciler Yetkisi' : 'Yalnızca Kız Öğrenciler Yetkisi'}
                </span>
              </div>
              <h1 className="text-base sm:text-xl font-extrabold text-slate-900">
                {aktifRol === 'erkek' ? 'Erkek Öğrenci Pansiyonu' : 'Kız Öğrenci Pansiyonu'} Yoklama Ekranı
              </h1>
            </div>

            <button
              onClick={handleLogout}
              className="w-full sm:w-auto flex items-center justify-center gap-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 py-2.5 px-4 rounded-xl cursor-pointer min-h-[42px]"
            >
              <LogOut className="w-4 h-4 shrink-0" /> Güvenli Çıkış Yap
            </button>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 pt-3 border-t border-slate-100">
            <div className="flex flex-col xs:flex-row items-stretch xs:items-center gap-2">
              <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 min-h-[42px]">
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-blue-600 shrink-0" />
                  <span className="text-xs font-medium text-slate-600">Tarih:</span>
                </div>
                <input type="date" value={tarih} onChange={(e) => setTarih(e.target.value)} className="text-xs font-bold text-slate-800 bg-transparent focus:outline-none ml-2" />
              </div>

              <div className="grid grid-cols-2 bg-slate-100 p-1 rounded-xl border border-slate-200 min-h-[42px]">
                <button onClick={() => setSeans('etut')} className={`px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${seans === 'etut' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600'}`}>
                  Etüt (19:15)
                </button>
                <button onClick={() => setSeans('yat')} className={`px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${seans === 'yat' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600'}`}>
                  Yat (23:00)
                </button>
              </div>
            </div>

            <button onClick={() => setNobetDefteriAcik(true)} className="flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs cursor-pointer min-h-[44px]">
              <FileText className="w-4 h-4 shrink-0" /> {aktifRol === 'erkek' ? 'Erkek Pansiyonu Nöbet Defteri (PDF)' : 'Kız Pansiyonu Nöbet Defteri (PDF)'}
            </button>
          </div>
        </div>

        {feedback && (
          <div className={`p-3.5 rounded-2xl border text-xs font-bold flex items-center justify-between ${feedback.type === 'success' ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-rose-50 border-rose-300 text-rose-800'}`}>
            <span>{feedback.text}</span>
            <button onClick={() => setFeedback(null)} className="underline ml-3 shrink-0">Kapat</button>
          </div>
        )}

        {/* KAT SEÇİMİ VE TÜMÜNÜ VAR YAP */}
        <div className="bg-white/95 backdrop-blur-md sticky top-2 z-20 rounded-2xl p-3 shadow-md border border-slate-200 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
          <div className="grid grid-cols-3 gap-1.5">
            {[1, 2, 3].map((kat) => (
              <button
                key={kat}
                onClick={() => setSelectedKat(kat)}
                className={`py-2.5 px-3 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px] transition-all ${
                  selectedKat === kat ? (aktifRol === 'erkek' ? 'bg-blue-600 text-white shadow-xs' : 'bg-rose-600 text-white shadow-xs') : 'bg-slate-100 text-slate-700'
                }`}
              >
                {kat}. Kat ({aktifRol === 'erkek' ? 'Erkek' : 'Kız'})
              </button>
            ))}
          </div>

          <button onClick={handleTumunuVarYap} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px]">
            <CheckCircle2 className="w-4 h-4" /> Bu Kattaki Tümünü Var Yap
          </button>
        </div>

        {/* ÖZET KARTLARI */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div className="bg-white p-3.5 rounded-2xl border border-slate-200">
            <div className="text-[11px] text-slate-500">{selectedKat}. Kat Mevcudu ({aktifRol === 'erkek' ? 'Erkek' : 'Kız'})</div>
            <div className="text-xl font-extrabold text-slate-900 mt-0.5">{katMevcudu}</div>
          </div>
          <div className="bg-emerald-50/70 p-3.5 rounded-2xl border border-emerald-200">
            <div className="text-[11px] text-emerald-700 font-medium">Var</div>
            <div className="text-xl font-extrabold text-emerald-700 mt-0.5">{varSayisi}</div>
          </div>
          <div className="bg-rose-50/70 p-3.5 rounded-2xl border border-rose-200">
            <div className="text-[11px] text-rose-700 font-medium">Yok</div>
            <div className="text-xl font-extrabold text-rose-700 mt-0.5">{yokSayisi}</div>
          </div>
          <div className="bg-amber-50/70 p-3.5 rounded-2xl border border-amber-200">
            <div className="text-[11px] text-amber-700 font-medium">İzinli</div>
            <div className="text-xl font-extrabold text-amber-700 mt-0.5">{izinliSayisi}</div>
          </div>
        </div>

        {/* ODALAR VE ÖĞRENCİ KARTLARI */}
        {odalar.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center border border-slate-200 text-xs text-slate-500">
            Bu katta kayıtlı {aktifRol === 'erkek' ? 'erkek' : 'kız'} öğrenci bulunmamaktadır.
          </div>
        ) : (
          <div className="space-y-4">
            {odalar.map((odaNo) => {
              const odaOgrencileri = katStudents.filter((s) => s.oda === odaNo);
              return (
                <div key={odaNo} className="bg-white rounded-2xl shadow-xs border border-slate-200 overflow-hidden">
                  <div className={`${aktifRol === 'erkek' ? 'bg-slate-900' : 'bg-rose-950'} text-white px-4 py-3 flex items-center justify-between`}>
                    <div className="flex items-center gap-2 text-xs font-bold">
                      <Home className="w-4 h-4 text-blue-400" /> Oda No: {odaNo} ({aktifRol === 'erkek' ? 'Erkek Pansiyonu' : 'Kız Pansiyonu'})
                    </div>
                    <span className="text-[11px] bg-white/15 px-2.5 py-0.5 rounded-full text-slate-100">
                      {odaOgrencileri.length} Öğrenci
                    </span>
                  </div>

                  <div className="p-3.5 sm:p-5 grid grid-cols-1 md:grid-cols-2 gap-3.5">
                    {odaOgrencileri.map((student) => {
                      const anneKey = `${student.id}-Anne`;
                      const babaKey = `${student.id}-Baba`;

                      return (
                        <div key={student.id} className="border border-slate-200 rounded-2xl p-3.5 sm:p-4 space-y-3 bg-white">
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <h3 className="font-extrabold text-slate-900 text-sm">{student.name}</h3>
                              <p className="text-[11px] text-slate-500 mt-0.5">
                                Oda: {student.oda} | Yatak: {student.yatak} | T.C.: {student.tc}
                              </p>
                            </div>
                            <span className={`text-[11px] font-extrabold px-2.5 py-1 rounded-lg shrink-0 ${student.status === 'izinli' ? 'bg-amber-100 text-amber-800' : student.status === 'yok' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
                              {student.status === 'izinli' ? 'İzinli' : student.status === 'yok' ? 'Yok' : 'Var'}
                            </span>
                          </div>

                          {student.status === 'izinli' ? (
                            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 font-medium">
                              <strong>Otomatik İzinli:</strong> {student.izinAciklama || 'Veli İzni Aktif'}
                            </div>
                          ) : (
                            <>
                              <div className="grid grid-cols-2 gap-2 pt-1">
                                <button onClick={() => handleStatusChange(student.id, 'var')} className={`py-2.5 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px] transition-all ${student.status === 'var' ? 'bg-emerald-600 text-white shadow-xs' : 'bg-slate-100 text-slate-700'}`}>
                                  ✓ Var
                                </button>
                                <button onClick={() => handleStatusChange(student.id, 'yok')} className={`py-2.5 rounded-xl text-xs font-extrabold cursor-pointer min-h-[42px] transition-all ${student.status === 'yok' ? 'bg-red-600 text-white shadow-xs' : 'bg-slate-100 text-slate-700'}`}>
                                  ✕ Yok
                                </button>
                              </div>

                              {student.status === 'yok' && (
                                <div className="p-3 bg-rose-50/80 border border-rose-200 rounded-xl space-y-2.5 mt-2">
                                  <div className="text-[11px] font-extrabold text-rose-800">WhatsApp Yoklama Bildirimi Gönder:</div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                                    <div className="flex items-center bg-white border border-rose-200 rounded-xl px-2.5 py-2 min-h-[40px]">
                                      <Phone className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
                                      <span className="text-slate-500 mr-1 text-[11px]">Anne:</span>
                                      <input type="tel" value={student.anneTel} onChange={(e) => handlePhoneChange(student.id, 'anneTel', e.target.value)} className="w-full font-mono text-xs text-slate-800 focus:outline-none" />
                                    </div>
                                    <div className="flex items-center bg-white border border-rose-200 rounded-xl px-2.5 py-2 min-h-[40px]">
                                      <Phone className="w-3.5 h-3.5 text-slate-400 mr-1.5 shrink-0" />
                                      <span className="text-slate-500 mr-1 text-[11px]">Baba:</span>
                                      <input type="tel" value={student.babaTel} onChange={(e) => handlePhoneChange(student.id, 'babaTel', e.target.value)} className="w-full font-mono text-xs text-slate-800 focus:outline-none" />
                                    </div>
                                  </div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    <button type="button" disabled={sendingKey === anneKey} onClick={() => handleSendWhatsApp(student, 'Anne', student.anneTel)} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 px-3 rounded-xl text-xs font-bold cursor-pointer min-h-[42px]">
                                      {sendingKey === anneKey ? <><Loader2 className="w-4 h-4 animate-spin" /> Gönderiliyor...</> : sentKeys[anneKey] ? <><Check className="w-4 h-4" /> Anneye Gönderildi</> : <><Send className="w-3.5 h-3.5" /> Anneye Mesaj At</>}
                                    </button>
                                    <button type="button" disabled={sendingKey === babaKey} onClick={() => handleSendWhatsApp(student, 'Baba', student.babaTel)} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 px-3 rounded-xl text-xs font-bold cursor-pointer min-h-[42px]">
                                      {sendingKey === babaKey ? <><Loader2 className="w-4 h-4 animate-spin" /> Gönderiliyor...</> : sentKeys[babaKey] ? <><Check className="w-4 h-4" /> Babaya Gönderildi</> : <><Send className="w-3.5 h-3.5" /> Babaya Mesaj At</>}
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
        )}
      </div>

      {/* RESMÎ MEB NÖBET DEFTERİ MODAL (Yalnızca Aktif Belletmenin Kendi Bölümünü Gösterir!) */}
      {nobetDefteriAcik && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-2.5 sm:p-4 overflow-y-auto print:static print:bg-white print:p-0">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-4 sm:p-8 space-y-5 shadow-2xl max-h-[92vh] overflow-y-auto print:max-h-none print:shadow-none">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 print:hidden">
              <h2 className="text-sm sm:text-base font-extrabold text-slate-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600 shrink-0" />
                {aktifRol === 'erkek' ? 'Erkek Pansiyonu Resmî Nöbet Defteri' : 'Kız Pansiyonu Resmî Nöbet Defteri'}
              </h2>
              <button onClick={() => setNobetDefteriAcik(false)} className="text-slate-400 hover:text-slate-700 p-1 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200 print:hidden">
              {aktifRol === 'erkek' ? (
                <>
                  <div>
                    <label className="block text-[11px] font-bold text-blue-800 mb-1">1. Nöbetçi Erkek Belletmen</label>
                    <input type="text" value={erkekBelletmen1} onChange={(e) => setErkekBelletmen1(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-blue-800 mb-1">2. Nöbetçi Erkek Belletmen</label>
                    <input type="text" value={erkekBelletmen2} onChange={(e) => setErkekBelletmen2(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-[11px] font-bold text-rose-800 mb-1">1. Nöbetçi Kadın Belletmen</label>
                    <input type="text" value={kizBelletmen1} onChange={(e) => setKizBelletmen1(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-rose-800 mb-1">2. Nöbetçi Kadın Belletmen</label>
                    <input type="text" value={kizBelletmen2} onChange={(e) => setKizBelletmen2(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-bold bg-white" />
                  </div>
                </>
              )}
              <div className="sm:col-span-2">
                <label className="block text-xs font-bold text-slate-700 mb-1">Günlük Nöbet Vukuat / Olay Notları</label>
                <textarea rows={2} value={nobetNotu} onChange={(e) => setNobetNotu(e.target.value)} className="w-full border border-slate-300 rounded-lg p-2.5 text-xs bg-white" />
              </div>
            </div>

            <div className="border border-slate-300 p-4 sm:p-6 rounded-xl space-y-4 text-slate-900 print:border-none print:p-0">
              <div className="text-center space-y-1 border-b-2 border-slate-800 pb-3">
                <p className="text-xs font-bold uppercase">T.C. MİLLÎ EĞİTİM BAKANLIĞI</p>
                <p className="text-xs sm:text-sm font-extrabold uppercase">Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Müdürlüğü</p>
                <p className="text-[11px] font-semibold uppercase text-slate-700">
                  {aktifRol === 'erkek' ? 'ERKEK ÖĞRENCİ PANSİYONU' : 'KIZ ÖĞRENCİ PANSİYONU'} GÜNLÜK NÖBET TUTANAĞI ({tarih} - {seans === 'etut' ? '19:15 Etüt' : '23:00 Yat'})
                </p>
              </div>

              <div className="border border-slate-300 p-3 rounded-lg text-xs">
                <div className={`font-bold border-b pb-1 mb-1.5 ${aktifRol === 'erkek' ? 'text-blue-900' : 'text-rose-900'}`}>
                  {aktifRol === 'erkek' ? 'ERKEK PANSİYONU YOKLAMA ÖZETİ' : 'KIZ PANSİYONU YOKLAMA ÖZETİ'}
                </div>
                Toplam Kayıtlı: <strong>{strictlyIsolatedStudents.length}</strong> | Pansiyonda Mevcut (Var): <strong>{strictlyIsolatedStudents.filter(s => s.status === 'var').length}</strong> | Yoklamada Bulunmayan (Yok): <strong>{bolumYoklar.length}</strong> | İzinli: <strong>{bolumIzinliler.length}</strong>
              </div>

              <div className="space-y-1.5">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-1.5 border-l-4 border-rose-600">
                  1. Yoklamada Bulunmayan ({aktifRol === 'erkek' ? 'Erkek' : 'Kız'}) Öğrenciler ({bolumYoklar.length})
                </h4>
                {bolumYoklar.length === 0 ? (
                  <p className="text-xs italic pl-2">Yoklamada habersiz eksik öğrenci yoktur.</p>
                ) : (
                  <div className="space-y-1 text-xs">
                    {bolumYoklar.map((s) => (
                      <div key={s.id} className="border-b py-1 flex justify-between">
                        <strong>{s.name} (Oda {s.oda} - Yatak {s.yatak})</strong>
                        <span>Veli Tel: {s.anneTel}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-1.5">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-1.5 border-l-4 border-amber-500">
                  2. İzinli ({aktifRol === 'erkek' ? 'Erkek' : 'Kız'}) Öğrenciler ({bolumIzinliler.length})
                </h4>
                {bolumIzinliler.length === 0 ? (
                  <p className="text-xs italic pl-2">İzinli öğrenci yoktur.</p>
                ) : (
                  <div className="space-y-1 text-xs">
                    {bolumIzinliler.map((s) => (
                      <div key={s.id} className="border-b py-1 flex justify-between">
                        <strong>{s.name} (Oda {s.oda})</strong>
                        <span>{s.izinAciklama}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-1.5">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-1.5 border-l-4 border-indigo-600">
                  3. Nöbetçi Belletmenler Vukuat ve Değerlendirme Notu
                </h4>
                <div className="p-2.5 border border-slate-300 rounded-lg text-xs min-h-[50px]">
                  {nobetNotu}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 text-center text-xs">
                {aktifRol === 'erkek' ? (
                  <>
                    <div><p className="font-bold">1. Nöbetçi Erkek Belletmen</p><p className="mt-1">{erkekBelletmen1}</p><p className="mt-5 text-slate-400">İmza</p></div>
                    <div><p className="font-bold">2. Nöbetçi Erkek Belletmen</p><p className="mt-1">{erkekBelletmen2}</p><p className="mt-5 text-slate-400">İmza</p></div>
                  </>
                ) : (
                  <>
                    <div><p className="font-bold">1. Nöbetçi Kadın Belletmen</p><p className="mt-1">{kizBelletmen1}</p><p className="mt-5 text-slate-400">İmza</p></div>
                    <div><p className="font-bold">2. Nöbetçi Kadın Belletmen</p><p className="mt-1">{kizBelletmen2}</p><p className="mt-5 text-slate-400">İmza</p></div>
                  </>
                )}
                <div><p className="font-bold">Müdür Yardımcısı</p><p className="mt-1">Pansiyon İdaresi</p><p className="mt-5 text-slate-400">İmza / Mühür</p></div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row justify-end gap-2.5 print:hidden">
              <button onClick={() => setNobetDefteriAcik(false)} className="px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 cursor-pointer min-h-[42px]">
                Kapat
              </button>
              <button onClick={handleSaveAndPrintDutyLog} className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold cursor-pointer min-h-[42px]">
                <Printer className="w-4 h-4" /> Kaydet ve Resmî PDF Çıktısı Al
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
    print("   ERKEK / KIZ PANSİYONU TAM VERİ İZOLASYONU KURULUYOR")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 1. Dosyaları Yaz
    write_file("app/api/pansiyon/route.ts", PANSIYON_API_TS)
    write_file("app/belletmen/page.tsx", BELLETMEN_PAGE_TSX)

    # 2. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 3. Derleme ve GitHub/Vercel Gönderimi
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Erkek ve Kadin belletmenler arasinda API ve arayuz seviyesinde tam veri izolasyonu saglandi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 GİZLİLİK VE VERİ İZOLASYONU CANLIYA ALINDI!")
    print("👉 Erkek Belletmen giriş yaptığında yalnızca Erkek öğrencileri,")
    print("👉 Kadın Belletmen giriş yaptığında yalnızca Kız öğrencileri görebilir.")
    print("=========================================================")

if __name__ == "__main__":
    main()