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
    print(f"✅ [GÜNCELLENDİ] {filepath}")

def kill_old_processes():
    print("🧹 Eski Node.js ve Tünel işlemleri temizleniyor...")
    subprocess.run("taskkill /F /IM node.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, capture_output=True)
    time.sleep(1)

def ensure_cloudflared():
    exe_name = "cloudflared.exe"
    if not os.path.exists(exe_name):
        print("🌐 cloudflared.exe indiriliyor...")
        urllib.request.urlretrieve(
            "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe",
            exe_name
        )
    return exe_name

def start_tunnel():
    exe_name = ensure_cloudflared()
    log_file = "tunnel.log"
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except:
            pass

    print("🚀 WhatsApp Bildirim Tüneli Açılıyor...")
    os.system(f'start "WHATSAPP_TUNELI" /MIN cmd /c "{exe_name} tunnel --url http://127.0.0.1:3001 > {log_file} 2>&1"')

    for _ in range(25):
        time.sleep(1)
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", f.read())
                if match:
                    return match.group(0)
    return None

# =========================================================================
# 1. NEON POSTGRESQL DESTEKLİ MERKEZİ API ROTASI (app/api/pansiyon/route.ts)
# =========================================================================
NEON_API_ROUTE = r'''import { NextResponse } from 'next/server';
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
  auditLogs: [
    { id: 'init1', tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Sistem', islem: 'Neon PostgreSQL Aktif', detay: '7/24 Kalıcı Bulut Veritabanı devreye alındı.', tur: 'basari' }
  ],
  updatedAt: Date.now(),
  tunnelUrl: ''
};

// NEON VERİTABANINDAN OKU (Tablo yoksa otomatik kurar)
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

// NEON VERİTABANINA KALICI YAZ
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
    const store = await getStore();

    const headers = {
      'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    };

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

    // WhatsApp Botu açıldığında güncel Cloudflare Tünel URL'sini Neon DB'ye kaydeder
    if (action === 'update_tunnel_url') {
      store.tunnelUrl = String(body.tunnelUrl || '').trim();
      await saveStore(store);
      return NextResponse.json({ success: true, tunnelUrl: store.tunnelUrl });
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
      return NextResponse.json({ success: true, message: `${newStudent.name} kalıcı bulut veritabanına eklendi!`, store });
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
      addLog(store, 'Yönetici', 'Toplu Öğrenci Yükleme', `${added} öğrenci Neon PostgreSQL veritabanına kaydedildi.`, 'basari');
      await saveStore(store);
      return NextResponse.json({ success: true, message: `${added} öğrenci kalıcı olarak kaydedildi ve tüm mobil cihazlarla senkronize edildi!`, store });
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
      return NextResponse.json({ success: true, message: `${added} belletmen kalıcı olarak eklendi!`, store });
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
      const st = store.students.find((s) => s.id === studentId) || store.students[0];
      store.leaves.unshift({ id: Date.now().toString(), studentId: st.id, studentName: st.name, oda: st.oda, tip: tip || 'Evci İzni', baslangic, bitis, aciklama: aciklama || 'Veli talebi', veliTel: veliTel || st.anneTel, createdAt: new Date().toISOString().split('T')[0] });
      st.status = 'izinli';
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'İzin onaylandı.', store });
    }

    if (action === 'add_duty_log') {
      const { tarih, seans, erkekBelletmen1, erkekBelletmen2, kizBelletmen1, kizBelletmen2, notlar } = body;
      store.dutyLogs.unshift({ id: Date.now().toString(), tarih: String(tarih || ''), seans: String(seans || ''), erkekBelletmen1: String(erkekBelletmen1 || ''), erkekBelletmen2: String(erkekBelletmen2 || ''), kizBelletmen1: String(kizBelletmen1 || ''), kizBelletmen2: String(kizBelletmen2 || ''), notlar: String(notlar || '') });
      await saveStore(store);
      return NextResponse.json({ success: true, message: 'Nöbet defteri kaydedildi.', store });
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
# 2. WHATSAPP BOTU (Açıldığında Tünel Adresini Otomatik Neon DB'ye Bildirir)
# =========================================================================
WHATSAPP_BOT_JS = r"""const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(cors({ origin: '*', methods: ['GET', 'POST', 'PUT', 'OPTIONS'] }));
app.use(express.json({ limit: '15mb' }));

async function syncTunnelToNeon() {
    try {
        if (!fs.existsSync('tunnel.log')) return;
        const log = fs.readFileSync('tunnel.log', 'utf-8');
        const match = log.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
        if (match) {
            const tunnelUrl = match[0];
            await fetch('https://pansiyon-yurt-sistemi.vercel.app/api/pansiyon', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'update_tunnel_url', tunnelUrl })
            });
            console.log('☁️ [NEON DB] WhatsApp Tünel Adresi Buluta İşlendi:', tunnelUrl);
        }
    } catch (e) {}
}

const chromePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
];
let targetExecutable = null;
for (const p of chromePaths) { if (fs.existsSync(p)) { targetExecutable = p; break; } }

let isReady = false;
const client = new Client({
    authStrategy: new LocalAuth({ dataPath: './.wwebjs_auth' }),
    puppeteer: { headless: false, executablePath: targetExecutable, args: ['--no-sandbox', '--disable-setuid-sandbox'] }
});

client.on('qr', (qr) => {
    console.log('\n📱 LÜTFEN WHATSAPP QR KODUNU OKUTUN:\n');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    console.log('\n✅ [BAŞARILI] WhatsApp Bildirim Sunucusu Hazır!');
    syncTunnelToNeon();
    setInterval(syncTunnelToNeon, 60000);
});

app.post('/send-otp', async (req, res) => {
    const { phone, code, customMessage } = req.body;
    if (!isReady) return res.status(503).json({ success: false, message: 'WhatsApp hazır değil.' });
    try {
        let cleaned = String(phone || '').replace(/\D/g, '');
        if (cleaned.length === 10) cleaned = '90' + cleaned;
        if (cleaned.length === 11 && cleaned.startsWith('0')) cleaned = '90' + cleaned.substring(1);
        const numberDetails = await client.getNumberId(cleaned);
        const targetChatId = numberDetails ? numberDetails._serialized : `${cleaned}@c.us`;
        const text = customMessage ? customMessage : `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\n\nGiriş Kodunuz: *${code}*`;
        await client.sendMessage(targetChatId, text);
        console.log(`📩 [WHATSAPP GÖNDERİLDİ] -> ${cleaned}`);
        return res.json({ success: true, message: 'Mesaj iletildi.' });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
});

app.listen(3001, '0.0.0.0', () => {
    console.log('🌐 WhatsApp Sunucusu (Port 3001) çalışıyor.');
    syncTunnelToNeon();
    client.initialize();
});
"""

def clean_old_tunnel_fetches(filepath):
    """Önceki geçici tünel/localStorage yamalarını temizler, doğrudan Neon API'den okumasını sağlar."""
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # Belletmen sayfasındaki eski tünel önceliğini kaldır, doğrudan /api/pansiyon (Neon) kullansın
    code = re.sub(
        r"// tunnel_mobile_fallback:.*?const data = await res\.json\(\);\n\s*\}",
        "const res = await fetch(url, { cache: 'no-store' });\n      const data = await res.json();",
        code,
        flags=re.DOTALL
    )
    write_file(filepath, code)

def main():
    print("================================================================")
    print("   PROFESYONEL NEON POSTGRESQL + MOBİL SENKRONİZASYON KURULUMU")
    print("================================================================")

    db_url = ""
    if os.path.exists(".env.local"):
        with open(".env.local", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("DATABASE_URL="):
                    db_url = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

    if not db_url:
        print("\n📌 Lütfen Neon PostgreSQL bağlantı adresinizi (postgresql://...) yapıştırıp Enter'a basın:")
        db_url = input("DATABASE_URL: ").strip().strip('"').strip("'")

    if not db_url.startswith("postgres"):
        print("❌ Geçersiz PostgreSQL bağlantı adresi! 'postgresql://' ile başlamalıdır.")
        sys.exit(1)

    kill_old_processes()

    # 1. .env.local dosyasına kaydet
    write_file(".env.local", f'DATABASE_URL="{db_url}"\n')

    # 2. @neondatabase/serverless paketini kur
    print("\n📦 @neondatabase/serverless paketi yükleniyor...")
    subprocess.run("npm install @neondatabase/serverless", shell=True)

    # 3. API ve WhatsApp Bot dosyalarını güncelle
    write_file("app/api/pansiyon/route.ts", NEON_API_ROUTE.replace("__USER_DATABASE_URL__", db_url))
    write_file("whatsapp-bot.js", WHATSAPP_BOT_JS)
    clean_old_tunnel_fetches("app/belletmen/page.tsx")

    # 4. Derle ve GitHub/Vercel'e gönder
    print("\n🚀 Next.js derleniyor ve Vercel'e gönderiliyor...")
    if subprocess.run("npm run build", shell=True).returncode != 0:
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    subprocess.run("git add app/api/pansiyon/route.ts app/belletmen/page.tsx package.json", shell=True)
    subprocess.run('git commit -m "Kalici Neon PostgreSQL bulut veritabani mimarisine gecildi" --allow-empty', shell=True)
    subprocess.run("git push origin main", shell=True)

    # 5. WhatsApp tünelini ve botu başlat
    start_tunnel()
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    print("\n================================================================")
    print("🎉 PROFESYONEL NEON POSTGRESQL SİSTEMİ CANLIYA ALINDI!")
    print("👉 Artık bilgisayarınızı kapatsanız bile verileriniz ASLA silinmez.")
    print("👉 İdare panelinden eklenen her öğrenci saniyesinde mobilde görünür.")
    print("================================================================")

if __name__ == "__main__":
    main()