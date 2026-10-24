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
# 1. MERKEZİ PANSİYON API ROTASI (Belletmen Şifre & Aylık Nöbet Destekli)
# -------------------------------------------------------------------------
PANSIYON_API_TS = r'''import { NextResponse } from 'next/server';

export interface StudentRecord {
  id: string;
  name: string;
  cinsiyet: 'erkek' | 'kiz';
  tc: string;
  sinif: string;
  kat: number;
  oda: string;
  yatak: string;
  anneTel: string;
  babaTel: string;
  status: 'var' | 'yok' | 'izinli';
}

export interface BelletmenRecord {
  id: string;
  name: string;
  cinsiyet: 'erkek' | 'kadin';
  brans: string;
  phone: string;
  password: string;
}

export interface MonthlyDutyDay {
  tarih: string; // YYYY-MM-DD
  erkek1: string;
  erkek2: string;
  kadin1: string;
  kadin2: string;
}

export interface LeaveRecord {
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

export interface DutyLogRecord {
  id: string;
  tarih: string;
  seans: string;
  erkekBelletmen1: string;
  erkekBelletmen2: string;
  kizBelletmen1: string;
  kizBelletmen2: string;
  notlar: string;
}

declare global {
  var __pansiyonStoreV5: {
    students: StudentRecord[];
    belletmenler: BelletmenRecord[];
    aylikNobetler: MonthlyDutyDay[];
    leaves: LeaveRecord[];
    dutyLogs: DutyLogRecord[];
  } | undefined;
}

if (!globalThis.__pansiyonStoreV5) {
  globalThis.__pansiyonStoreV5 = {
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
      { id: 'b2', name: 'Ali BEY', cinsiyet: 'erkek', brans: 'Matematik', phone: '05410000001', password: '1234' },
      { id: 'b3', name: 'Furkan DEMİR', cinsiyet: 'erkek', brans: 'Tarih', phone: '05410000002', password: '1234' },
      { id: 'b4', name: 'Hasan ÇELİK', cinsiyet: 'erkek', brans: 'Fizik', phone: '05410000003', password: '1234' },
      { id: 'b5', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat', phone: '05410000004', password: '1234' },
      { id: 'b6', name: 'Fatma YILMAZ', cinsiyet: 'kadin', brans: 'İngilizce', phone: '05410000005', password: '1234' },
      { id: 'b7', name: 'Zeynep ŞAHİN', cinsiyet: 'kadin', brans: 'Kimya', phone: '05410000006', password: '1234' },
      { id: 'b8', name: 'Merve AYDIN', cinsiyet: 'kadin', brans: 'Biyoloji', phone: '05410000007', password: '1234' },
    ],
    aylikNobetler: [
      { tarih: '2026-10-24', erkek1: 'Cüneyt DEMİR', erkek2: 'Ali BEY', kadin1: 'Ayşenur KAYA', kadin2: 'Fatma YILMAZ' },
      { tarih: '2026-10-25', erkek1: 'Furkan DEMİR', erkek2: 'Hasan ÇELİK', kadin1: 'Zeynep ŞAHİN', kadin2: 'Merve AYDIN' },
      { tarih: '2026-10-26', erkek1: 'Cüneyt DEMİR', erkek2: 'Furkan DEMİR', kadin1: 'Ayşenur KAYA', kadin2: 'Zeynep ŞAHİN' },
      { tarih: '2026-10-27', erkek1: 'Ali BEY', erkek2: 'Hasan ÇELİK', kadin1: 'Fatma YILMAZ', kadin2: 'Merve AYDIN' },
      { tarih: '2026-10-28', erkek1: 'Cüneyt DEMİR', erkek2: 'Ali BEY', kadin1: 'Ayşenur KAYA', kadin2: 'Fatma YILMAZ' },
    ],
    leaves: [
      { id: '101', studentId: '1', studentName: 'Ahmet Yılmaz', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-21', bitis: '2026-10-30', aciklama: 'Akraba ziyareti', veliTel: '05416571469', createdAt: '2026-10-21' },
      { id: '102', studentId: '2', studentName: 'Mehmet Demir', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-20', bitis: '2026-10-25', aciklama: 'Aile ziyareti ve hafta sonu ev izni', veliTel: '05416571469', createdAt: '2026-10-20' },
      { id: '103', studentId: '6', studentName: 'Elif Yılmaz', oda: 'K-101', tip: 'Ev İzni', baslangic: '2026-10-23', bitis: '2026-10-26', aciklama: 'Hafta sonu evci izni', veliTel: '05416571469', createdAt: '2026-10-23' },
    ],
    dutyLogs: [
      {
        id: '1',
        tarih: '2026-10-24',
        seans: 'Etüt (19:15)',
        erkekBelletmen1: 'Cüneyt DEMİR',
        erkekBelletmen2: 'Ali BEY',
        kizBelletmen1: 'Ayşenur KAYA',
        kizBelletmen2: 'Fatma YILMAZ',
        notlar: 'Erkek ve Kız pansiyonu etüt ve yat yoklamaları 4 nöbetçi belletmen tarafından zamanında alındı.'
      }
    ],
  };
}

export async function GET() {
  return NextResponse.json({ success: true, store: globalThis.__pansiyonStoreV5 });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = globalThis.__pansiyonStoreV5!;

    // --- BELLETMEN İŞLEMLERİ ---
    if (action === 'add_belletmen') {
      const { name, cinsiyet, brans, phone, password } = body;
      store.belletmenler.push({
        id: Date.now().toString(),
        name: name.trim(),
        cinsiyet: cinsiyet === 'kadin' ? 'kadin' : 'erkek',
        brans: (brans || 'Öğretmen').trim(),
        phone: (phone || '05410000000').trim(),
        password: (password || '1234').trim(),
      });
      return NextResponse.json({ success: true, message: `${name} belletmen listesine eklendi.`, store });
    }

    if (action === 'bulk_add_belletmen') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = (r.cinsiyet || 'erkek').toString().toLowerCase();
          const cins: 'erkek' | 'kadin' = (rawCins.includes('k') || rawCins.includes('kadın') || rawCins.includes('kadin') || rawCins.includes('bayan')) ? 'kadin' : 'erkek';
          store.belletmenler.push({
            id: (Date.now() + Math.random()).toString(),
            name: r.name.trim(),
            cinsiyet: cins,
            brans: (r.brans || 'Öğretmen').trim(),
            phone: (r.phone || '05410000000').trim(),
            password: (r.password || '1234').trim(),
          });
          added++;
        }
      }
      return NextResponse.json({ success: true, message: `${added} belletmen Excel/CSV listesinden başarıyla eklendi.`, store });
    }

    if (action === 'update_belletmen_password') {
      const { id, newPassword } = body;
      const target = store.belletmenler.find((b) => b.id === id);
      if (target) {
        target.password = newPassword.trim();
        return NextResponse.json({ success: true, message: `${target.name} isimli belletmenin şifresi güncellendi.`, store });
      }
      return NextResponse.json({ success: false, message: 'Belletmen bulunamadı.' }, { status: 404 });
    }

    if (action === 'delete_belletmen') {
      store.belletmenler = store.belletmenler.filter((b) => b.id !== body.id);
      return NextResponse.json({ success: true, message: 'Belletmen kaydı silindi.', store });
    }

    if (action === 'belletmen_login') {
      const { id, password } = body;
      const found = store.belletmenler.find((b) => b.id === id);
      if (!found || found.password !== (password || '').trim()) {
        return NextResponse.json({ success: false, message: 'Hatalı belletmen şifresi! Lütfen şifrenizi kontrol edin.' }, { status: 401 });
      }
      return NextResponse.json({ success: true, belletmen: found, store });
    }

    // --- AYLIK NÖBET LİSTESİ İŞLEMLERİ ---
    if (action === 'add_or_update_monthly_duty') {
      const { tarih, erkek1, erkek2, kadin1, kadin2 } = body;
      const existingIdx = store.aylikNobetler.findIndex((d) => d.tarih === tarih);
      const newEntry: MonthlyDutyDay = { tarih, erkek1, erkek2, kadin1, kadin2 };
      if (existingIdx > -1) {
        store.aylikNobetler[existingIdx] = newEntry;
      } else {
        store.aylikNobetler.push(newEntry);
        store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih));
      }
      return NextResponse.json({ success: true, message: `${tarih} günü nöbetçileri güncellendi.`, store });
    }

    if (action === 'bulk_monthly_duty') {
      let count = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.tarih) continue;
          const existingIdx = store.aylikNobetler.findIndex((d) => d.tarih === r.tarih.trim());
          const item: MonthlyDutyDay = {
            tarih: r.tarih.trim(),
            erkek1: (r.erkek1 || '-').trim(),
            erkek2: (r.erkek2 || '-').trim(),
            kadin1: (r.kadin1 || '-').trim(),
            kadin2: (r.kadin2 || '-').trim(),
          };
          if (existingIdx > -1) {
            store.aylikNobetler[existingIdx] = item;
          } else {
            store.aylikNobetler.push(item);
          }
          count++;
        }
        store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih));
      }
      return NextResponse.json({ success: true, message: `${count} günlük aylık nöbet çizelgesi başarıyla kaydedildi.`, store });
    }

    if (action === 'auto_generate_month_duty') {
      const { yearMonth } = body; // Örn: "2026-10" veya "2026-11"
      const [yStr, mStr] = (yearMonth || '2026-10').split('-');
      const year = Number(yStr) || 2026;
      const month = Number(mStr) || 10;
      const daysInMonth = new Date(year, month, 0).getDate();

      const erkekler = store.belletmenler.filter((b) => b.cinsiyet === 'erkek');
      const kadinlar = store.belletmenler.filter((b) => b.cinsiyet === 'kadin');

      // O aya ait eski kayıtları temizle
      store.aylikNobetler = store.aylikNobetler.filter((d) => !d.tarih.startsWith(yearMonth));

      for (let d = 1; d <= daysInMonth; d++) {
        const dayStr = d < 10 ? `0${d}` : `${d}`;
        const dateKey = `${yearMonth}-${dayStr}`;
        const e1 = erkekler.length > 0 ? erkekler[(d * 2 - 2) % erkekler.length].name : 'Erkek Belletmen 1';
        const e2 = erkekler.length > 1 ? erkekler[(d * 2 - 1) % erkekler.length].name : e1;
        const k1 = kadinlar.length > 0 ? kadinlar[(d * 2 - 2) % kadinlar.length].name : 'Kadın Belletmen 1';
        const k2 = kadinlar.length > 1 ? kadinlar[(d * 2 - 1) % kadinlar.length].name : k1;

        store.aylikNobetler.push({
          tarih: dateKey,
          erkek1: e1,
          erkek2: e2,
          kadin1: k1,
          kadin2: k2,
        });
      }
      store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih));
      return NextResponse.json({ success: true, message: `${yearMonth} ayı için ${daysInMonth} günlük (2 Erkek + 2 Kadın) nöbet listesi otomatik oluşturuldu!`, store });
    }

    if (action === 'delete_monthly_duty') {
      store.aylikNobetler = store.aylikNobetler.filter((d) => d.tarih !== body.tarih);
      return NextResponse.json({ success: true, message: 'Nöbet günü silindi.', store });
    }

    // --- ÖĞRENCİ VE İZİN İŞLEMLERİ ---
    if (action === 'add_leave') {
      const { studentId, tip, baslangic, bitis, aciklama, veliTel } = body;
      const st = store.students.find((s) => s.id === studentId) || store.students[0];
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
        createdAt: new Date().toISOString().split('T')[0],
      });
      st.status = 'izinli';
      return NextResponse.json({ success: true, message: 'İzin talebi onaylandı.', store });
    }

    if (action === 'update_attendance') {
      if (Array.isArray(body.students)) {
        store.students = body.students;
      }
      return NextResponse.json({ success: true, message: 'Yoklama güncellendi.', store });
    }

    if (action === 'add_student') {
      const { name, cinsiyet, tc, sinif, kat, oda, yatak, anneTel, babaTel } = body;
      store.students.push({
        id: Date.now().toString(),
        name,
        cinsiyet: cinsiyet === 'kiz' ? 'kiz' : 'erkek',
        tc: tc || '10000000000',
        sinif: sinif || '9-A',
        kat: Number(kat) || 1,
        oda: oda || '101',
        yatak: yatak || 'A',
        anneTel: anneTel || '05416571469',
        babaTel: babaTel || '05416571469',
        status: 'var',
      });
      return NextResponse.json({ success: true, message: `${name} eklendi.`, store });
    }

    if (action === 'bulk_import') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = (r.cinsiyet || 'erkek').toString().toLowerCase();
          const cins: 'erkek' | 'kiz' = rawCins.includes('k') ? 'kiz' : 'erkek';
          store.students.push({
            id: (Date.now() + Math.random()).toString(),
            name: r.name.trim(),
            cinsiyet: cins,
            tc: (r.tc || '10000000000').trim(),
            sinif: (r.sinif || '9-A').trim(),
            kat: Number(r.kat) || 1,
            oda: (r.oda || '101').trim(),
            yatak: (r.yatak || 'A').trim(),
            anneTel: (r.anneTel || '05416571469').trim(),
            babaTel: (r.babaTel || '05416571469').trim(),
            status: 'var',
          });
          added++;
        }
      }
      return NextResponse.json({ success: true, message: `${added} öğrenci yüklendi.`, store });
    }

    if (action === 'delete_student') {
      store.students = store.students.filter((s) => s.id !== body.id);
      return NextResponse.json({ success: true, message: 'Öğrenci silindi.', store });
    }

    if (action === 'add_duty_log') {
      const { tarih, seans, erkekBelletmen1, erkekBelletmen2, kizBelletmen1, kizBelletmen2, notlar } = body;
      store.dutyLogs.unshift({
        id: Date.now().toString(),
        tarih,
        seans,
        erkekBelletmen1: erkekBelletmen1 || '1. Erkek Belletmen',
        erkekBelletmen2: erkekBelletmen2 || '2. Erkek Belletmen',
        kizBelletmen1: kizBelletmen1 || '1. Kadın Belletmen',
        kizBelletmen2: kizBelletmen2 || '2. Kadın Belletmen',
        notlar,
      });
      return NextResponse.json({ success: true, message: '4 Belletmenli nöbet defteri kaydedildi.', store });
    }

    return NextResponse.json({ success: false, message: 'Geçersiz işlem.' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
'''

# -------------------------------------------------------------------------
# 2. YÖNETİCİ PANELİ (/admin - Belletmen Şifre, Excel Ekleme ve Aylık Nöbet)
# -------------------------------------------------------------------------
ADMIN_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Users, Upload, Plus, Trash2, Shield, FileSpreadsheet, LogOut,
  KeyRound, Eye, EyeOff, Calendar, UserCheck, Wand2, Save
} from 'lucide-react';

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'belletmen' | 'nobet' | 'ogrenci'>('belletmen');

  const [students, setStudents] = useState<any[]>([]);
  const [belletmenler, setBelletmenler] = useState<any[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<any[]>([]);
  const [msg, setMsg] = useState('');

  // --- 1) TEKİL BELLETMEN EKLEME STATE ---
  const [bName, setBName] = useState('');
  const [bCinsiyet, setBCinsiyet] = useState<'erkek' | 'kadin'>('erkek');
  const [bBrans, setBBrans] = useState('');
  const [bPhone, setBPhone] = useState('0541');
  const [bPassword, setBPassword] = useState('1234');

  // --- EXCEL / CSV İLE TOPLU BELLETMEN EKLEME STATE ---
  const [belletmenCsv, setBelletmenCsv] = useState(
    'Serhat AKAN, erkek, Matematik, 05411112233, 1453\nElif DEMİR, kadin, Türk Dili ve Edebiyatı, 05412223344, 2026'
  );

  // --- ŞİFRE GÖRME VE DEĞİŞTİRME STATE ---
  const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({});
  const [editingPasswordId, setEditingPasswordId] = useState<string | null>(null);
  const [newPasswordVal, setNewPasswordVal] = useState('');

  // --- 2) AYLIK NÖBET LİSTESİ STATE ---
  const [nobetAySecim, setNobetAySecim] = useState('2026-10');
  const [nTarih, setNTarih] = useState('2026-10-29');
  const [nErkek1, setNErkek1] = useState('Cüneyt DEMİR');
  const [nErkek2, setNErkek2] = useState('Ali BEY');
  const [nKadin1, setNKadin1] = useState('Ayşenur KAYA');
  const [nKadin2, setNKadin2] = useState('Fatma YILMAZ');

  const [nobetCsv, setNobetCsv] = useState(
    '2026-10-29, Cüneyt DEMİR, Ali BEY, Ayşenur KAYA, Fatma YILMAZ\n2026-10-30, Furkan DEMİR, Hasan ÇELİK, Zeynep ŞAHİN, Merve AYDIN\n2026-10-31, Cüneyt DEMİR, Furkan DEMİR, Ayşenur KAYA, Merve AYDIN'
  );

  // --- 3) ÖĞRENCİ EKLEME STATE ---
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
    'Ali Veli, erkek, 12345678910, 9-B, 1, 103, A, 05416571469, 05416571469\nAyşe Fatma, kiz, 12345678911, 10-A, 1, K-102, B, 05416571469, 05416571469'
  );

  const syncFromStore = (store: any) => {
    setStudents(store.students || []);
    setBelletmenler(store.belletmenler || []);
    setAylikNobetler(store.aylikNobetler || []);
  };

  const fetchAll = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        syncFromStore(data.store);
      }
    } catch {}
  };

  useEffect(() => {
    fetchAll();
  }, []);

  // --- BELLETMEN FONKSİYONLARI ---
  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_belletmen',
        name: bName,
        cinsiyet: bCinsiyet,
        brans: bBrans,
        phone: bPhone,
        password: bPassword,
      }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setBName('');
      setBBrans('');
      setMsg(data.message);
    }
  };

  const handleBulkAddBelletmen = async () => {
    const lines = belletmenCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const parts = line.split(',').map((p) => p.trim());
      return {
        name: parts[0],
        cinsiyet: parts[1] || 'erkek',
        brans: parts[2] || 'Öğretmen',
        phone: parts[3] || '05410000000',
        password: parts[4] || '1234',
      };
    });

    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_add_belletmen', rows }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleUpdatePassword = async (id: string) => {
    if (!newPasswordVal.trim()) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'update_belletmen_password', id, newPassword: newPasswordVal }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setEditingPasswordId(null);
      setNewPasswordVal('');
      setMsg(data.message);
    }
  };

  const handleDeleteBelletmen = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_belletmen', id }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  // --- AYLIK NÖBET FONKSİYONLARI ---
  const handleAddSingleDutyDay = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_or_update_monthly_duty',
        tarih: nTarih,
        erkek1: nErkek1,
        erkek2: nErkek2,
        kadin1: nKadin1,
        kadin2: nKadin2,
      }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleBulkMonthlyDuty = async () => {
    const lines = nobetCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return {
        tarih: p[0],
        erkek1: p[1] || '-',
        erkek2: p[2] || '-',
        kadin1: p[3] || '-',
        kadin2: p[4] || '-',
      };
    });
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_monthly_duty', rows }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleAutoGenerateMonth = async () => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'auto_generate_month_duty', yearMonth: nobetAySecim }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleDeleteDutyDay = async (tarih: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_monthly_duty', tarih }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  // --- ÖĞRENCİ FONKSİYONLARI ---
  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_student',
        name: sName,
        cinsiyet: sCinsiyet,
        tc: sTc,
        sinif: sSinif,
        kat: sKat,
        oda: sOda,
        yatak: sYatak,
        anneTel: sAnneTel,
        babaTel: sBabaTel,
      }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setSName('');
      setSTc('');
      setMsg(data.message);
    }
  };

  const handleBulkImportStudents = async () => {
    const lines = studentCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const parts = line.split(',').map((p) => p.trim());
      return {
        name: parts[0],
        cinsiyet: parts[1] || 'erkek',
        tc: parts[2] || '10000000000',
        sinif: parts[3] || '9-A',
        kat: Number(parts[4]) || 1,
        oda: parts[5] || '101',
        yatak: parts[6] || 'A',
        anneTel: parts[7] || '05416571469',
        babaTel: parts[8] || '05416571469',
      };
    });

    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'bulk_import', rows }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const handleDeleteStudent = async (id: string) => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'delete_student', id }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
  };

  const erkekBelletmenList = belletmenler.filter((b) => b.cinsiyet === 'erkek');
  const kadinBelletmenList = belletmenler.filter((b) => b.cinsiyet === 'kadin');

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-6xl mx-auto space-y-6">

        {/* ÜST BAŞLIK */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg md:text-xl font-extrabold text-slate-900">Pansiyon İdare & Yönetici Paneli</h1>
              <p className="text-xs text-slate-500">
                Belletmen Şifre & Excel Yönetimi • Aylık Nöbet Listesi • Öğrenci & Oda Yönetimi
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <a href="/belletmen" className="text-xs font-bold text-blue-700 bg-blue-50 px-3 py-2 rounded-xl border border-blue-200">
              Belletmen Ekranı
            </a>
            <a href="/veli" className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200">
              Veli Portalı
            </a>
            <a href="/" className="flex items-center gap-1 text-xs font-bold text-white bg-rose-600 px-3 py-2 rounded-xl">
              <LogOut className="w-3.5 h-3.5" /> Çıkış
            </a>
          </div>
        </div>

        {/* SEKME MENÜSÜ */}
        <div className="bg-white rounded-2xl p-2 border border-slate-200 shadow-xs flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTab('belletmen')}
            className={`flex-1 min-w-[200px] flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'belletmen' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <KeyRound className="w-4 h-4" /> 1. Belletmen & Şifre Yönetimi ({belletmenler.length})
          </button>
          <button
            onClick={() => setActiveTab('nobet')}
            className={`flex-1 min-w-[200px] flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'nobet' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Calendar className="w-4 h-4" /> 2. Aylık Nöbet Listesi ({aylikNobetler.length} Gün)
          </button>
          <button
            onClick={() => setActiveTab('ogrenci')}
            className={`flex-1 min-w-[200px] flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'ogrenci' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Users className="w-4 h-4" /> 3. Öğrenci & Oda Yönetimi ({students.length})
          </button>
        </div>

        {msg && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold flex justify-between items-center">
            <span>✅ {msg}</span>
            <button onClick={() => setMsg('')} className="underline ml-4">Kapat</button>
          </div>
        )}

        {/* ======================================================================= */}
        {/* SEKME 1: BELLETMEN EKLEME (TEKİL & EXCEL) VE ŞİFRE GÖRME / DEĞİŞTİRME */}
        {/* ======================================================================= */}
        {activeTab === 'belletmen' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tekil Belletmen Ekleme */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Belletmen Öğretmen Ekle
                </h2>
                <form onSubmit={handleAddBelletmen} className="grid grid-cols-2 gap-3 text-xs">
                  <input
                    type="text"
                    required
                    placeholder="Ad Soyad (Örn: Cüneyt DEMİR)"
                    value={bName}
                    onChange={(e) => setBName(e.target.value)}
                    className="border border-slate-200 rounded-xl px-3 py-2.5 font-semibold"
                  />
                  <select
                    value={bCinsiyet}
                    onChange={(e) => setBCinsiyet(e.target.value as 'erkek' | 'kadin')}
                    className="border border-slate-200 rounded-xl px-3 py-2.5 font-bold bg-white"
                  >
                    <option value="erkek">👨 Erkek Belletmen</option>
                    <option value="kadin">👩 Kadın Belletmen</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Branş (Örn: Bilişim / Matematik)"
                    value={bBrans}
                    onChange={(e) => setBBrans(e.target.value)}
                    className="border border-slate-200 rounded-xl px-3 py-2.5"
                  />
                  <input
                    type="text"
                    placeholder="Telefon (0541...)"
                    value={bPhone}
                    onChange={(e) => setBPhone(e.target.value)}
                    className="border border-slate-200 rounded-xl px-3 py-2.5 font-mono"
                  />
                  <div className="col-span-2">
                    <label className="block text-[11px] font-bold text-slate-600 mb-1">Belletmen Giriş Şifresi:</label>
                    <input
                      type="text"
                      required
                      placeholder="Giriş Şifresi Belirleyin (Örn: 1234)"
                      value={bPassword}
                      onChange={(e) => setBPassword(e.target.value)}
                      className="w-full border border-indigo-200 bg-indigo-50/40 rounded-xl px-3 py-2.5 font-mono font-bold text-indigo-950"
                    />
                  </div>
                  <button
                    type="submit"
                    className="col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-bold cursor-pointer"
                  >
                    Belletmeni Sisteme Kaydet
                  </button>
                </form>
              </div>

              {/* Excel / CSV ile Toplu Belletmen Ekleme */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Excel / CSV ile Toplu Belletmen Ekleme
                </h2>
                <p className="text-[11px] text-slate-500">
                  Her satıra 1 öğretmen gelecek şekilde Excel’den yapıştırın:<br />
                  Format: <code>Ad Soyad, erkek/kadin, Branş, Telefon, Şifre</code>
                </p>
                <textarea
                  rows={4}
                  value={belletmenCsv}
                  onChange={(e) => setBelletmenCsv(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50"
                />
                <button
                  onClick={handleBulkAddBelletmen}
                  className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer"
                >
                  <Upload className="w-4 h-4" /> Excel Belletmen Listesini Toplu Yükle
                </button>
              </div>
            </div>

            {/* Belletmen Listesi + Şifre Görme ve Değiştirme Tablosu */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-indigo-600" /> Kayıtlı Belletmen Öğretmenler & Şifre Yönetimi ({belletmenler.length})
                </h2>
                <span className="text-[11px] text-slate-500">
                  👁️ Göz ikonuna tıklayarak şifreyi görebilir veya <strong>Şifre Değiştir</strong> ile yeni şifre atayabilirsiniz.
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-100 text-slate-700 text-left">
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Görev Grubu</th>
                      <th className="p-2.5">Branş</th>
                      <th className="p-2.5">Telefon</th>
                      <th className="p-2.5">Giriş Şifresi (Gör / Değiştir)</th>
                      <th className="p-2.5 text-right">İşlem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {belletmenler.map((b) => {
                      const isShown = !!visiblePasswords[b.id];
                      const isEditing = editingPasswordId === b.id;

                      return (
                        <tr key={b.id} className="hover:bg-slate-50">
                          <td className="p-2.5 font-extrabold text-slate-900">{b.name}</td>
                          <td className="p-2.5">
                            <span
                              className={`px-2.5 py-0.5 rounded-md font-bold text-[11px] ${
                                b.cinsiyet === 'kadin' ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {b.cinsiyet === 'kadin' ? '👩 Kadın Belletmen' : '👨 Erkek Belletmen'}
                            </span>
                          </td>
                          <td className="p-2.5 text-slate-600">{b.brans}</td>
                          <td className="p-2.5 font-mono">{b.phone}</td>
                          <td className="p-2.5">
                            {isEditing ? (
                              <div className="flex items-center gap-1.5">
                                <input
                                  type="text"
                                  value={newPasswordVal}
                                  onChange={(e) => setNewPasswordVal(e.target.value)}
                                  placeholder="Yeni şifre..."
                                  className="border border-indigo-300 rounded-lg px-2 py-1 text-xs font-mono w-28 bg-white"
                                />
                                <button
                                  onClick={() => handleUpdatePassword(b.id)}
                                  className="bg-emerald-600 text-white px-2.5 py-1 rounded-lg font-bold text-[11px] cursor-pointer"
                                >
                                  Kaydet
                                </button>
                                <button
                                  onClick={() => setEditingPasswordId(null)}
                                  className="text-slate-500 underline text-[11px] cursor-pointer"
                                >
                                  İptal
                                </button>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2">
                                <span className="font-mono font-bold bg-slate-100 px-2.5 py-1 rounded-lg text-slate-800">
                                  {isShown ? b.password : '••••••'}
                                </span>
                                <button
                                  type="button"
                                  onClick={() =>
                                    setVisiblePasswords((prev) => ({ ...prev, [b.id]: !prev[b.id] }))
                                  }
                                  className="p-1 text-slate-500 hover:text-indigo-600 cursor-pointer"
                                  title={isShown ? 'Şifreyi Gizle' : 'Şifreyi Gör'}
                                >
                                  {isShown ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    setEditingPasswordId(b.id);
                                    setNewPasswordVal(b.password);
                                  }}
                                  className="text-[11px] font-bold text-indigo-600 hover:underline cursor-pointer"
                                >
                                  Şifre Değiştir
                                </button>
                              </div>
                            )}
                          </td>
                          <td className="p-2.5 text-right">
                            <button
                              onClick={() => handleDeleteBelletmen(b.id)}
                              className="text-rose-600 hover:text-rose-800 p-1 cursor-pointer"
                            >
                              <Trash2 className="w-4 h-4 inline" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================================= */}
        {/* SEKME 2: AYLIK NÖBET LİSTESİ EKLEME (OTOMATİK, EXCEL VE TEKİL GÜN)       */}
        {/* ======================================================================= */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            {/* Otomatik Ay Dağıtıcı Bar */}
            <div className="bg-indigo-950 text-white rounded-2xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="space-y-1">
                <h2 className="text-sm font-extrabold flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-amber-400" /> Kayıtlı Belletmenlerden Otomatik Aylık Nöbet Çizelgesi Oluştur
                </h2>
                <p className="text-xs text-indigo-200">
                  Seçtiğiniz ayın tüm günleri için (1’inden 30/31’ine kadar) her güne 2 Erkek + 2 Kadın belletmeni sırayla otomatik atar.
                </p>
              </div>
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <input
                  type="month"
                  value={nobetAySecim}
                  onChange={(e) => setNobetAySecim(e.target.value)}
                  className="bg-white text-slate-900 font-bold text-xs px-3 py-2.5 rounded-xl"
                />
                <button
                  onClick={handleAutoGenerateMonth}
                  className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs px-4 py-2.5 rounded-xl cursor-pointer whitespace-nowrap"
                >
                  Tüm Ayı Otomatik Doldur
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tekil Gün Nöbeti Ekle / Güncelle */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-blue-600" /> Günlük Nöbetçi Ata / Güncelle (2 Erkek + 2 Kadın)
                </h3>
                <form onSubmit={handleAddSingleDutyDay} className="grid grid-cols-2 gap-3 text-xs">
                  <div className="col-span-2">
                    <label className="block text-[11px] font-bold text-slate-600 mb-1">Nöbet Tarihi:</label>
                    <input
                      type="date"
                      required
                      value={nTarih}
                      onChange={(e) => setNTarih(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-3 py-2 font-bold"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-blue-700 mb-1">1. Erkek Belletmen:</label>
                    <select
                      value={nErkek1}
                      onChange={(e) => setNErkek1(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {erkekBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-blue-700 mb-1">2. Erkek Belletmen:</label>
                    <select
                      value={nErkek2}
                      onChange={(e) => setNErkek2(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {erkekBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-rose-700 mb-1">1. Kadın Belletmen:</label>
                    <select
                      value={nKadin1}
                      onChange={(e) => setNKadin1(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {kadinBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold text-rose-700 mb-1">2. Kadın Belletmen:</label>
                    <select
                      value={nKadin2}
                      onChange={(e) => setNKadin2(e.target.value)}
                      className="w-full border border-slate-200 rounded-xl px-2.5 py-2 bg-white font-semibold"
                    >
                      {kadinBelletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.name}</option>
                      ))}
                    </select>
                  </div>

                  <button
                    type="submit"
                    className="col-span-2 flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl font-bold cursor-pointer"
                  >
                    <Save className="w-4 h-4" /> Seçili Günün Nöbetçilerini Kaydet
                  </button>
                </form>
              </div>

              {/* Excel / CSV ile Aylık Toplu Nöbet Listesi Yükleme */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Excel ile Aylık Nöbet Listesi Toplu Yükleme
                </h3>
                <p className="text-[11px] text-slate-500">
                  Format: <code>YYYY-AA-GG, 1.Erkek, 2.Erkek, 1.Kadın, 2.Kadın</code>
                </p>
                <textarea
                  rows={5}
                  value={nobetCsv}
                  onChange={(e) => setNobetCsv(e.target.value)}
                  className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50"
                />
                <button
                  onClick={handleBulkMonthlyDuty}
                  className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer"
                >
                  <Upload className="w-4 h-4" /> Aylık Nöbet Listesini Sisteme Aktar
                </button>
              </div>
            </div>

            {/* Aylık Nöbet Çizelgesi Tablosu */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900">
                Aktif Aylık Nöbet Çizelgesi ({aylikNobetler.length} Gün Kayıtlı)
              </h3>
              <div className="overflow-x-auto max-h-[480px]">
                <table className="w-full text-xs border-collapse">
                  <thead className="sticky top-0 bg-slate-100 text-slate-700 text-left">
                    <tr>
                      <th className="p-2.5">Tarih</th>
                      <th className="p-2.5 text-blue-800">1. Erkek Belletmen</th>
                      <th className="p-2.5 text-blue-800">2. Erkek Belletmen</th>
                      <th className="p-2.5 text-rose-800">1. Kadın Belletmen</th>
                      <th className="p-2.5 text-rose-800">2. Kadın Belletmen</th>
                      <th className="p-2.5 text-right">İşlem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {aylikNobetler.map((d) => (
                      <tr key={d.tarih} className="hover:bg-slate-50">
                        <td className="p-2.5 font-extrabold text-slate-900 font-mono">{d.tarih}</td>
                        <td className="p-2.5 font-semibold text-blue-700">👨 {d.erkek1}</td>
                        <td className="p-2.5 font-semibold text-blue-700">👨 {d.erkek2}</td>
                        <td className="p-2.5 font-semibold text-rose-700">👩 {d.kadin1}</td>
                        <td className="p-2.5 font-semibold text-rose-700">👩 {d.kadin2}</td>
                        <td className="p-2.5 text-right">
                          <button
                            onClick={() => handleDeleteDutyDay(d.tarih)}
                            className="text-rose-600 hover:text-rose-800 p-1 cursor-pointer"
                          >
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================================= */}
        {/* SEKME 3: ÖĞRENCİ EKLEME (TEKİL & EXCEL) VE ODA LİSTESİ                  */}
        {/* ======================================================================= */}
        {activeTab === 'ogrenci' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Yeni Öğrenci & Oda Kaydı
                </h2>
                <form onSubmit={handleAddStudent} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={sName} onChange={(e) => setSName(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <select value={sCinsiyet} onChange={(e) => setSCinsiyet(e.target.value as 'erkek' | 'kiz')} className="border border-slate-200 rounded-xl px-3 py-2 font-bold bg-white">
                    <option value="erkek">Erkek Pansiyonu</option>
                    <option value="kiz">Kız Pansiyonu</option>
                  </select>
                  <input type="text" placeholder="T.C. Kimlik No" value={sTc} onChange={(e) => setSTc(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Sınıf (Örn: 10-A)" value={sSinif} onChange={(e) => setSSinif(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <select value={sKat} onChange={(e) => setSKat(Number(e.target.value))} className="border border-slate-200 rounded-xl px-3 py-2 bg-white">
                    <option value={1}>1. Kat</option>
                    <option value={2}>2. Kat</option>
                    <option value={3}>3. Kat</option>
                  </select>
                  <input type="text" placeholder="Oda No (Örn: 102 / K-101)" value={sOda} onChange={(e) => setSOda(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Anne WhatsApp Tel" value={sAnneTel} onChange={(e) => setSAnneTel(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Baba WhatsApp Tel" value={sBabaTel} onChange={(e) => setSBabaTel(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2" />
                  <button type="submit" className="col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    Öğrenciyi Pansiyona Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> e-Okul / Excel Toplu Öğrenci Yükleme
                </h2>
                <p className="text-[11px] text-slate-500">
                  Format: <code>Ad Soyad, erkek/kiz, TC, Sınıf, Kat, Oda, Yatak, AnneTel, BabaTel</code>
                </p>
                <textarea rows={4} value={studentCsv} onChange={(e) => setStudentCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkImportStudents} className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4" /> Öğrenci Listesini Toplu Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Users className="w-4 h-4 text-blue-600" /> Kayıtlı Öğrenciler ({students.length})
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-100 text-slate-700 text-left">
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Bölüm</th>
                      <th className="p-2.5">Kat / Oda / Yatak</th>
                      <th className="p-2.5">Anne Tel</th>
                      <th className="p-2.5">Durum</th>
                      <th className="p-2.5 text-right">İşlem</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {students.map((s) => (
                      <tr key={s.id} className="hover:bg-slate-50">
                        <td className="p-2.5 font-bold text-slate-900">{s.name}</td>
                        <td className="p-2.5">
                          <span className={`px-2 py-0.5 rounded-md font-bold text-[11px] ${s.cinsiyet === 'kiz' ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'}`}>
                            {s.cinsiyet === 'kiz' ? 'Kız' : 'Erkek'}
                          </span>
                        </td>
                        <td className="p-2.5 font-semibold">{s.kat}. Kat — Oda {s.oda} ({s.yatak})</td>
                        <td className="p-2.5 font-mono">{s.anneTel}</td>
                        <td className="p-2.5 font-bold">{s.status.toUpperCase()}</td>
                        <td className="p-2.5 text-right">
                          <button onClick={() => handleDeleteStudent(s.id)} className="text-rose-600 hover:text-rose-800 p-1 cursor-pointer">
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
'''

# -------------------------------------------------------------------------
# 3. BELLETMEN EKRANI (/belletmen - Şifreli Giriş & Aylık Nöbet Entegreli)
# -------------------------------------------------------------------------
BELLETMEN_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Calendar, FileText, CheckCircle2, Home, Send, Check, Loader2,
  Phone, Printer, X, LogOut, UserCheck, Lock, RefreshCw
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

  // Giriş Form State
  const [secilenErkekId, setSecilenErkekId] = useState<string>('');
  const [erkekSifre, setErkekSifre] = useState<string>('');
  const [secilenKadinId, setSecilenKadinId] = useState<string>('');
  const [kadinSifre, setKadinSifre] = useState<string>('');
  const [loginError, setLoginError] = useState<string>('');

  const [selectedKat, setSelectedKat] = useState<number>(1);
  const [tarih, setTarih] = useState<string>('2026-10-24');
  const [seans, setSeans] = useState<'etut' | 'yat'>('etut');
  const [sendingKey, setSendingKey] = useState<string | null>(null);
  const [sentKeys, setSentKeys] = useState<Record<string, boolean>>({});
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [nobetDefteriAcik, setNobetDefteriAcik] = useState(false);
  const [erkekBelletmen1, setErkekBelletmen1] = useState('Cüneyt DEMİR');
  const [erkekBelletmen2, setErkekBelletmen2] = useState('Ali BEY');
  const [kizBelletmen1, setKizBelletmen1] = useState('Ayşenur KAYA');
  const [kizBelletmen2, setKizBelletmen2] = useState('Fatma YILMAZ');
  const [nobetNotu, setNobetNotu] = useState('Erkek ve Kız pansiyonu akşam etüt ve yat yoklamaları nöbetçi belletmen öğretmenler tarafından zamanında alındı.');

  const loadData = async () => {
    try {
      const res = await fetch('/api/pansiyon');
      const data = await res.json();
      if (data.success && data.store) {
        setStudents(data.store.students || []);
        setLeaves(data.store.leaves || []);
        const bList = data.store.belletmenler || [];
        setBelletmenler(bList);
        setAylikNobetler(data.store.aylikNobetler || []);

        const firstErkek = bList.find((b: any) => b.cinsiyet === 'erkek');
        const firstKadin = bList.find((b: any) => b.cinsiyet === 'kadin');
        if (firstErkek) setSecilenErkekId(firstErkek.id);
        if (firstKadin) setSecilenKadinId(firstKadin.id);
      }
    } catch {}
  };

  useEffect(() => {
    loadData();
  }, []);

  // Seçili tarihe göre aylık nöbet listesinden o günün 4 nöbetçisini otomatik getir
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
    const targetId = rol === 'erkek' ? secilenErkekId : secilenKadinId;
    const targetPass = rol === 'erkek' ? erkekSifre : kadinSifre;

    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'belletmen_login', id: targetId, password: targetPass }),
    });
    const data = await res.json();
    if (res.ok && data.success) {
      setAktifRol(rol);
      setAktifBelletmenAd(data.belletmen.name);
    } else {
      setLoginError(data.message || 'Şifre hatalı!');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setAktifRol(null);
    setErkekSifre('');
    setKadinSifre('');
    window.location.href = '/';
  };

  const getActiveLeaveText = (studentId: string) => {
    const found = leaves.find((l) => l.studentId === studentId && l.baslangic <= tarih && l.bitis >= tarih);
    return found ? `${found.baslangic} — ${found.bitis} (${found.tip}: ${found.aciklama})` : undefined;
  };

  const enrichedStudents = students.map((s) => {
    const leaveTxt = getActiveLeaveText(s.id);
    return leaveTxt ? { ...s, status: 'izinli' as const, izinAciklama: leaveTxt } : s;
  });

  const roleFilteredStudents = enrichedStudents.filter((s) => s.cinsiyet === aktifRol);
  const katStudents = roleFilteredStudents.filter((s) => s.kat === selectedKat);

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
    syncAttendance(students.map((s) => (s.id === id ? { ...s, status: newStatus } : s)));
  };

  const handlePhoneChange = (id: string, field: 'anneTel' | 'babaTel', value: string) => {
    setStudents((prev) => prev.map((s) => (s.id === id ? { ...s, [field]: value } : s)));
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
    setFeedback({ type: 'success', text: `✅ ${selectedKat}. Kattaki izinsiz tüm öğrenciler 'Var' yapıldı.` });
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
        setFeedback({ type: 'error', text: data.message || 'Mesaj iletilemedi.' });
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
        erkekBelletmen1,
        erkekBelletmen2,
        kizBelletmen1,
        kizBelletmen2,
        notlar: nobetNotu,
      }),
    });
    window.print();
  };

  const erkekBelletmenler = belletmenler.filter((b) => b.cinsiyet === 'erkek');
  const kadinBelletmenler = belletmenler.filter((b) => b.cinsiyet === 'kadin');

  if (!aktifRol) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full bg-white rounded-3xl shadow-xl border border-slate-200 p-6 md:p-10 space-y-6">
          <div className="text-center space-y-2">
            <span className="text-xs font-extrabold uppercase tracking-wider bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full border border-indigo-200">
              Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Pansiyonu
            </span>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 mt-2">
              Nöbetçi Belletmen Şifreli Giriş Ekranı
            </h1>
            <p className="text-xs text-slate-500">
              Erkek Belletmenler sadece <strong>Erkek Öğrencileri</strong>, Kadın Belletmenler sadece <strong>Kız Öğrencileri</strong> görüp yoklama alabilir. (Varsayılan Test Şifresi: <strong>1234</strong>)
            </p>
          </div>

          {loginError && (
            <div className="p-3.5 bg-rose-50 border border-rose-300 text-rose-800 rounded-2xl text-xs font-bold text-center">
              ❌ {loginError}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* ERKEK BELLETMEN ŞİFRELİ GİRİŞ */}
            <div className="border-2 border-blue-200 bg-blue-50/40 rounded-2xl p-6 space-y-4">
              <div className="w-11 h-11 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold">
                <UserCheck className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-extrabold text-blue-950">1) Erkek Belletmen Girişi</h2>
              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nöbetçi Erkek Belletmen Seçin:</label>
                  <select
                    value={secilenErkekId}
                    onChange={(e) => setSecilenErkekId(e.target.value)}
                    className="w-full border border-blue-300 rounded-xl px-3 py-2.5 font-bold bg-white"
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
                      placeholder="Şifreniz (Varsayılan: 1234)"
                      value={erkekSifre}
                      onChange={(e) => setErkekSifre(e.target.value)}
                      className="w-full pl-9 pr-3 py-2.5 border border-blue-300 rounded-xl bg-white font-mono"
                    />
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleLogin('erkek')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl text-xs cursor-pointer"
              >
                Erkek Pansiyonu Yoklamasına Giriş Yap →
              </button>
            </div>

            {/* KADIN BELLETMEN ŞİFRELİ GİRİŞ */}
            <div className="border-2 border-rose-200 bg-rose-50/40 rounded-2xl p-6 space-y-4">
              <div className="w-11 h-11 rounded-2xl bg-rose-600 text-white flex items-center justify-center font-bold">
                <UserCheck className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-extrabold text-rose-950">2) Kadın Belletmen Girişi</h2>
              <div className="space-y-3 text-xs">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nöbetçi Kadın Belletmen Seçin:</label>
                  <select
                    value={secilenKadinId}
                    onChange={(e) => setSecilenKadinId(e.target.value)}
                    className="w-full border border-rose-300 rounded-xl px-3 py-2.5 font-bold bg-white"
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
                      placeholder="Şifreniz (Varsayılan: 1234)"
                      value={kadinSifre}
                      onChange={(e) => setKadinSifre(e.target.value)}
                      className="w-full pl-9 pr-3 py-2.5 border border-rose-300 rounded-xl bg-white font-mono"
                    />
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleLogin('kiz')}
                className="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-3 rounded-xl text-xs cursor-pointer"
              >
                Kız Pansiyonu Yoklamasına Giriş Yap →
              </button>
            </div>
          </div>

          <div className="flex justify-between items-center pt-2 border-t border-slate-100 text-xs">
            <a href="/veli" className="text-emerald-700 font-bold hover:underline">← Veli İzin Portalı</a>
            <a href="/admin" className="text-indigo-700 font-bold hover:underline">Yönetici Paneli (Şifre & Aylık Nöbet Yönetimi) →</a>
          </div>
        </div>
      </div>
    );
  }

  const erkekOgrenciler = enrichedStudents.filter((s) => s.cinsiyet === 'erkek');
  const kizOgrenciler = enrichedStudents.filter((s) => s.cinsiyet === 'kiz');
  const tumYoklar = enrichedStudents.filter((s) => s.status === 'yok');
  const tumIzinliler = enrichedStudents.filter((s) => s.status === 'izinli');

  return (
    <div className="min-h-screen bg-slate-100 p-4 md:p-6">
      <div className="max-w-5xl mx-auto space-y-5 print:hidden">

        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <span className={`text-xs font-extrabold px-3 py-1 rounded-full ${aktifRol === 'erkek' ? 'bg-blue-100 text-blue-800' : 'bg-rose-100 text-rose-800'}`}>
                {aktifRol === 'erkek'
                  ? `👨 Aktif Erkek Belletmen: ${aktifBelletmenAd} (Günlük Nöbetçiler: ${erkekBelletmen1} & ${erkekBelletmen2})`
                  : `👩 Aktif Kadın Belletmen: ${aktifBelletmenAd} (Günlük Nöbetçiler: ${kizBelletmen1} & ${kizBelletmen2})`}
              </span>
              <h1 className="text-lg md:text-xl font-bold text-slate-800 mt-1.5">
                {aktifRol === 'erkek' ? 'Erkek Öğrenci Pansiyonu' : 'Kız Öğrenci Pansiyonu'} Yoklama Ekranı
              </h1>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button onClick={() => setAktifRol(null)} className="flex items-center gap-1 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-xl cursor-pointer">
                <RefreshCw className="w-3.5 h-3.5" /> Belletmen Değiştir
              </button>
              <a href="/admin" className="text-xs font-bold text-indigo-700 bg-indigo-50 px-3 py-2 rounded-xl border border-indigo-200">
                Yönetici Paneli
              </a>
              <button onClick={handleLogout} className="flex items-center gap-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 px-4 py-2 rounded-xl cursor-pointer">
                <LogOut className="w-4 h-4" /> Çıkış Yap
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5">
                <Calendar className="w-4 h-4 text-blue-600" />
                <span className="text-xs font-medium text-slate-600">Yoklama Tarihi:</span>
                <input type="date" value={tarih} onChange={(e) => setTarih(e.target.value)} className="text-xs font-bold text-slate-800 bg-transparent focus:outline-none" />
              </div>

              <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200">
                <button onClick={() => setSeans('etut')} className={`px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${seans === 'etut' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'}`}>
                  Etüt (19:15)
                </button>
                <button onClick={() => setSeans('yat')} className={`px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${seans === 'yat' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600'}`}>
                  Yat (23:00)
                </button>
              </div>
            </div>

            <button onClick={() => setNobetDefteriAcik(true)} className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-sm cursor-pointer">
              <FileText className="w-4 h-4" /> Resmî Nöbet Defteri (2 Erkek + 2 Kadın Belletmen)
            </button>
          </div>
        </div>

        {feedback && (
          <div className={`p-4 rounded-2xl border text-xs font-bold flex items-center justify-between ${feedback.type === 'success' ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-rose-50 border-rose-300 text-rose-800'}`}>
            <span>{feedback.text}</span>
            <button onClick={() => setFeedback(null)} className="underline ml-4">Kapat</button>
          </div>
        )}

        <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {[1, 2, 3].map((kat) => (
              <button
                key={kat}
                onClick={() => setSelectedKat(kat)}
                className={`px-4 py-2 rounded-xl text-xs font-bold cursor-pointer ${
                  selectedKat === kat ? (aktifRol === 'erkek' ? 'bg-blue-600 text-white' : 'bg-rose-600 text-white') : 'bg-slate-100 text-slate-700'
                }`}
              >
                {kat}. Kat ({aktifRol === 'erkek' ? 'Erkek' : 'Kız'})
              </button>
            ))}
          </div>

          <button onClick={handleTumunuVarYap} className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-xs font-bold cursor-pointer">
            <CheckCircle2 className="w-4 h-4" /> Tümünü Var Yap
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white p-4 rounded-2xl border border-slate-200">
            <div className="text-xs text-slate-500">Kat Mevcudu</div>
            <div className="text-xl font-extrabold text-slate-900 mt-1">{katMevcudu}</div>
          </div>
          <div className="bg-emerald-50/70 p-4 rounded-2xl border border-emerald-200">
            <div className="text-xs text-emerald-700 font-medium">Var</div>
            <div className="text-xl font-extrabold text-emerald-700 mt-1">{varSayisi}</div>
          </div>
          <div className="bg-rose-50/70 p-4 rounded-2xl border border-rose-200">
            <div className="text-xs text-rose-700 font-medium">Yok</div>
            <div className="text-xl font-extrabold text-rose-700 mt-1">{yokSayisi}</div>
          </div>
          <div className="bg-amber-50/70 p-4 rounded-2xl border border-amber-200">
            <div className="text-xs text-amber-700 font-medium">Veli İzinli (Otomatik)</div>
            <div className="text-xl font-extrabold text-amber-700 mt-1">{izinliSayisi}</div>
          </div>
        </div>

        {odalar.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 text-center border border-slate-200 text-xs text-slate-500">
            Bu katta kayıtlı {aktifRol === 'erkek' ? 'erkek' : 'kız'} öğrenci bulunmamaktadır.
          </div>
        ) : (
          <div className="space-y-5">
            {odalar.map((odaNo) => {
              const odaOgrencileri = katStudents.filter((s) => s.oda === odaNo);
              return (
                <div key={odaNo} className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                  <div className={`${aktifRol === 'erkek' ? 'bg-slate-900' : 'bg-rose-950'} text-white px-5 py-3 flex items-center justify-between`}>
                    <div className="flex items-center gap-2 text-xs font-bold">
                      <Home className="w-4 h-4 text-blue-400" /> Oda No: {odaNo}
                    </div>
                    <span className="text-[11px] bg-white/10 px-2.5 py-0.5 rounded-full text-slate-200">
                      {odaOgrencileri.length} Öğrenci
                    </span>
                  </div>

                  <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                    {odaOgrencileri.map((student) => {
                      const anneKey = `${student.id}-Anne`;
                      const babaKey = `${student.id}-Baba`;

                      return (
                        <div key={student.id} className="border border-slate-200 rounded-xl p-4 space-y-3 bg-white">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className="font-bold text-slate-900 text-sm">{student.name}</h3>
                              <p className="text-[11px] text-slate-500 mt-0.5">
                                Oda: {student.oda} | Yatak: {student.yatak} | T.C.: {student.tc}
                              </p>
                            </div>
                            <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-md ${student.status === 'izinli' ? 'bg-amber-100 text-amber-800' : student.status === 'yok' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'}`}>
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
                                <button onClick={() => handleStatusChange(student.id, 'var')} className={`px-4 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${student.status === 'var' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-700'}`}>
                                  Var
                                </button>
                                <button onClick={() => handleStatusChange(student.id, 'yok')} className={`px-4 py-1.5 rounded-lg text-xs font-bold cursor-pointer ${student.status === 'yok' ? 'bg-red-600 text-white' : 'bg-slate-100 text-slate-700'}`}>
                                  Yok
                                </button>
                              </div>

                              {student.status === 'yok' && (
                                <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-xl space-y-2.5 mt-2">
                                  <div className="text-[11px] font-bold text-rose-800">WhatsApp Yoklama Bildirimi Gönder:</div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                                    <div className="flex items-center bg-white border border-rose-200 rounded-lg px-2 py-1">
                                      <Phone className="w-3 h-3 text-slate-400 mr-1" />
                                      <span className="text-slate-500 mr-1">Anne:</span>
                                      <input type="text" value={student.anneTel} onChange={(e) => handlePhoneChange(student.id, 'anneTel', e.target.value)} className="w-full font-mono text-slate-800 focus:outline-none" />
                                    </div>
                                    <div className="flex items-center bg-white border border-rose-200 rounded-lg px-2 py-1">
                                      <Phone className="w-3 h-3 text-slate-400 mr-1" />
                                      <span className="text-slate-500 mr-1">Baba:</span>
                                      <input type="text" value={student.babaTel} onChange={(e) => handlePhoneChange(student.id, 'babaTel', e.target.value)} className="w-full font-mono text-slate-800 focus:outline-none" />
                                    </div>
                                  </div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    <button type="button" disabled={sendingKey === anneKey} onClick={() => handleSendWhatsApp(student, 'Anne', student.anneTel)} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white py-2 px-3 rounded-lg text-[11px] font-bold cursor-pointer">
                                      {sendingKey === anneKey ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Gönderiliyor...</> : sentKeys[anneKey] ? <><Check className="w-3.5 h-3.5" /> Anneye Gönderildi</> : <><Send className="w-3.5 h-3.5" /> Anneye Mesaj At</>}
                                    </button>
                                    <button type="button" disabled={sendingKey === babaKey} onClick={() => handleSendWhatsApp(student, 'Baba', student.babaTel)} className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white py-2 px-3 rounded-lg text-[11px] font-bold cursor-pointer">
                                      {sendingKey === babaKey ? <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Gönderiliyor...</> : sentKeys[babaKey] ? <><Check className="w-3.5 h-3.5" /> Babaya Gönderildi</> : <><Send className="w-3.5 h-3.5" /> Babaya Mesaj At</>}
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

      {/* RESMÎ MEB 4 BELLETMENLİ (2 ERKEK + 2 KADIN) NÖBET DEFTERİ MODAL */}
      {nobetDefteriAcik && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto print:static print:bg-white print:p-0">
          <div className="bg-white rounded-2xl max-w-4xl w-full p-6 md:p-8 space-y-6 shadow-2xl print:shadow-none">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-4 print:hidden">
              <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600" /> Resmî MEB Nöbet Defteri (2 Erkek + 2 Kadın Belletmen)
              </h2>
              <button onClick={() => setNobetDefteriAcik(false)} className="text-slate-400 hover:text-slate-700">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200 print:hidden">
              <div>
                <label className="block text-[11px] font-bold text-blue-800 mb-1">1. Erkek Belletmen</label>
                <input type="text" value={erkekBelletmen1} onChange={(e) => setErkekBelletmen1(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-bold bg-white" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-blue-800 mb-1">2. Erkek Belletmen</label>
                <input type="text" value={erkekBelletmen2} onChange={(e) => setErkekBelletmen2(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-bold bg-white" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-rose-800 mb-1">1. Kadın Belletmen</label>
                <input type="text" value={kizBelletmen1} onChange={(e) => setKizBelletmen1(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-bold bg-white" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-rose-800 mb-1">2. Kadın Belletmen</label>
                <input type="text" value={kizBelletmen2} onChange={(e) => setKizBelletmen2(e.target.value)} className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-bold bg-white" />
              </div>
              <div className="sm:col-span-2 md:col-span-4">
                <label className="block text-xs font-bold text-slate-700 mb-1">Günlük Nöbet Vukuat / Olay Notları</label>
                <textarea rows={2} value={nobetNotu} onChange={(e) => setNobetNotu(e.target.value)} className="w-full border border-slate-300 rounded-lg p-2.5 text-xs bg-white" />
              </div>
            </div>

            <div className="border border-slate-300 p-6 rounded-xl space-y-5 text-slate-900 print:border-none print:p-0">
              <div className="text-center space-y-1 border-b-2 border-slate-800 pb-4">
                <p className="text-xs font-bold uppercase">T.C. MİLLÎ EĞİTİM BAKANLIĞI</p>
                <p className="text-sm font-extrabold uppercase">Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Müdürlüğü</p>
                <p className="text-xs font-semibold uppercase text-slate-700">Erkek ve Kız Öğrenci Pansiyonu Günlük Nöbet Tutanağı ({tarih} - {seans === 'etut' ? '19:15 Etüt' : '23:00 Yat'})</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="border border-slate-300 p-3 rounded-lg space-y-1">
                  <div className="font-bold text-blue-900 border-b pb-1">ERKEK PANSİYONU YOKLAMA ÖZETİ</div>
                  <div>Toplam: <strong>{erkekOgrenciler.length}</strong> | Var: <strong>{erkekOgrenciler.filter(s => s.status === 'var').length}</strong> | Yok: <strong>{erkekOgrenciler.filter(s => s.status === 'yok').length}</strong> | İzinli: <strong>{erkekOgrenciler.filter(s => s.status === 'izinli').length}</strong></div>
                </div>
                <div className="border border-slate-300 p-3 rounded-lg space-y-1">
                  <div className="font-bold text-rose-900 border-b pb-1">KIZ PANSİYONU YOKLAMA ÖZETİ</div>
                  <div>Toplam: <strong>{kizOgrenciler.length}</strong> | Var: <strong>{kizOgrenciler.filter(s => s.status === 'var').length}</strong> | Yok: <strong>{kizOgrenciler.filter(s => s.status === 'yok').length}</strong> | İzinli: <strong>{kizOgrenciler.filter(s => s.status === 'izinli').length}</strong></div>
                </div>
              </div>

              <div className="space-y-1.5">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-1.5 border-l-4 border-rose-600">
                  1. Yoklamada Bulunmayan (Yok) Öğrenciler ({tumYoklar.length})
                </h4>
                {tumYoklar.length === 0 ? (
                  <p className="text-xs italic pl-2">Yoklamada habersiz eksik öğrenci yoktur.</p>
                ) : (
                  <table className="w-full text-xs border-collapse border border-slate-300">
                    <thead>
                      <tr className="bg-slate-100">
                        <th className="border border-slate-300 p-1 text-left">Ad Soyad</th>
                        <th className="border border-slate-300 p-1 text-left">Bölüm / Oda</th>
                        <th className="border border-slate-300 p-1 text-left">Veli Tel</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tumYoklar.map((s) => (
                        <tr key={s.id}>
                          <td className="border border-slate-300 p-1 font-bold">{s.name}</td>
                          <td className="border border-slate-300 p-1">{s.cinsiyet === 'erkek' ? 'Erkek' : 'Kız'} - Oda {s.oda}</td>
                          <td className="border border-slate-300 p-1">{s.anneTel}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              <div className="space-y-1.5">
                <h4 className="text-xs font-bold uppercase bg-slate-100 p-1.5 border-l-4 border-indigo-600">
                  2. Nöbetçi Belletmenler Günlük Vukuat ve Değerlendirme Notu
                </h4>
                <div className="p-2.5 border border-slate-300 rounded-lg text-xs min-h-[55px]">
                  {nobetNotu}
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 pt-6 text-center text-[11px]">
                <div>
                  <p className="font-bold">1. Erkek Belletmen</p>
                  <p className="mt-1 text-slate-800">{erkekBelletmen1}</p>
                  <p className="mt-5 text-slate-400">İmza</p>
                </div>
                <div>
                  <p className="font-bold">2. Erkek Belletmen</p>
                  <p className="mt-1 text-slate-800">{erkekBelletmen2}</p>
                  <p className="mt-5 text-slate-400">İmza</p>
                </div>
                <div>
                  <p className="font-bold">1. Kadın Belletmen</p>
                  <p className="mt-1 text-slate-800">{kizBelletmen1}</p>
                  <p className="mt-5 text-slate-400">İmza</p>
                </div>
                <div>
                  <p className="font-bold">2. Kadın Belletmen</p>
                  <p className="mt-1 text-slate-800">{kizBelletmen2}</p>
                  <p className="mt-5 text-slate-400">İmza</p>
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <p className="font-bold">Müdür Yardımcısı</p>
                  <p className="mt-1 text-slate-800">Pansiyon İdaresi</p>
                  <p className="mt-5 text-slate-400">İmza / Mühür</p>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 print:hidden">
              <button onClick={() => setNobetDefteriAcik(false)} className="px-4 py-2 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 cursor-pointer">
                Kapat
              </button>
              <button onClick={handleSaveAndPrintDutyLog} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl text-xs font-bold cursor-pointer">
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
    print("   ADMİN BELLETMEN ŞİFRE & AYLIK NÖBET SİSTEMİ KURULUYOR")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    write_file("app/api/pansiyon/route.ts", PANSIYON_API_TS)
    write_file("app/admin/page.tsx", ADMIN_PAGE_TSX)
    write_file("app/belletmen/page.tsx", BELLETMEN_PAGE_TSX)

    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Admin paneline Excel ile belletmen ekleme, sifre gorme/degistirme ve aylik nobet cizelgesi eklendi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 YÖNETİCİ PANELİ TÜM YENİ FONKSİYONLARLA CANLIYA ALINDI!")
    print("👉 Yönetici Paneli : https://pansiyon-yurt-sistemi.vercel.app/admin")
    print("👉 Belletmen Girişi: https://pansiyon-yurt-sistemi.vercel.app/belletmen")
    print("=========================================================")

if __name__ == "__main__":
    main()