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

    print("🚀 Mobil Senkronizasyon ve WhatsApp için Cloudflare HTTPS tüneli açılıyor...")
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

# =========================================================================
# 1. API ROTASI (TypeScript "null" hataları giderildi)
# =========================================================================
PANSIYON_API_TS = r'''import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

const TUNNEL_HUB_URLS = ['__TUNNEL_URL__', 'http://127.0.0.1:3001', 'http://localhost:3001'];

export interface StudentRecord {
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

const DB_FILE = path.join('/tmp', 'pansiyon_store_v15.json');

const DEFAULT_STORE: StoreData = {
  students: [
    { id: '1', name: 'Ahmet Yılmaz', cinsiyet: 'erkek', kat: 1, oda: '101', anneAdi: 'Ayşe Yılmaz', anneTel: '05416571469', babaAdi: 'Ali Yılmaz', babaTel: '05416571469', status: 'izinli' },
    { id: '5', name: 'Zeynep Aydın', cinsiyet: 'kiz', kat: 1, oda: 'K-101', anneAdi: 'Hatice Aydın', anneTel: '05416571469', babaAdi: 'İbrahim Aydın', babaTel: '05416571469', status: 'var' },
  ],
  belletmenler: [
    { id: 'b1', name: 'Cüneyt DEMİR', cinsiyet: 'erkek', brans: 'Bilişim Teknolojileri', phone: '05416571469', password: '1234' },
    { id: 'b5', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat', phone: '05416571469', password: '1234' },
  ],
  aylikNobetler: [],
  leaves: [],
  dutyLogs: [],
  auditLogs: [
    { id: 'log1', tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Sistem', islem: 'Mobil Senkronizasyon Köprüsü', detay: 'Derleme hataları giderildi.', tur: 'bilgi' }
  ],
  updatedAt: 1000,
  tunnelUrl: '__TUNNEL_URL__'
};

declare global {
  var __pansiyonStoreV15: StoreData | undefined;
}

// 1) Hem yerel bellekten hem de 7/24 açık Cloudflare Tünel Hub'ından en güncel veriyi çek
async function loadStoreAsync(): Promise<StoreData> {
  let localStore: StoreData | null = globalThis.__pansiyonStoreV15 || null;

  if (!localStore) {
    try {
      if (fs.existsSync(DB_FILE)) {
        localStore = JSON.parse(fs.readFileSync(DB_FILE, 'utf-8')) as StoreData;
      }
    } catch {}
  }

  // Cloudflare Tünelindeki 7/24 açık ana bilgisayardan kontrol et
  for (const hubUrl of TUNNEL_HUB_URLS) {
    if (!hubUrl || hubUrl.includes('__TUNNEL')) continue;
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), 2500);
      const res = await fetch(`${hubUrl}/store?t=${Date.now()}`, {
        cache: 'no-store',
        signal: controller.signal
      });
      clearTimeout(tid);
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.store && Array.isArray(data.store.students)) {
          if (!localStore || (data.store.updatedAt || 0) >= (localStore.updatedAt || 0)) {
            localStore = data.store as StoreData;
            globalThis.__pansiyonStoreV15 = localStore;
          }
          break;
        }
      }
    } catch {}
  }

  // TS18047 hatasını önlemek için Type Casting ile boşsa varsayılanı ata
  if (!localStore) {
    localStore = JSON.parse(JSON.stringify(DEFAULT_STORE)) as StoreData;
    globalThis.__pansiyonStoreV15 = localStore;
  }

  const safeStore: StoreData = localStore;
  safeStore.tunnelUrl = '__TUNNEL_URL__';
  return safeStore;
}

// 2) Değişikliği hem Vercel belleğine hem de 7/24 açık Cloudflare Tünel Hub'ına kaydet
async function saveStoreAsync(store: StoreData) {
  store.updatedAt = Date.now();
  store.tunnelUrl = '__TUNNEL_URL__';
  globalThis.__pansiyonStoreV15 = store;

  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(store), 'utf-8');
  } catch {}

  for (const hubUrl of TUNNEL_HUB_URLS) {
    if (!hubUrl || hubUrl.includes('__TUNNEL')) continue;
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), 2500);
      const res = await fetch(`${hubUrl}/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ store }),
        signal: controller.signal
      });
      clearTimeout(tid);
      if (res.ok) break;
    } catch {}
  }
}

function normalizeGender(val: any): 'erkek' | 'kiz' {
  const s = String(val || 'erkek').trim().toLowerCase();
  if (s.includes('k') || s.includes('bayan')) return 'kiz';
  return 'erkek';
}

function normalizeKat(val: any): number {
  const match = String(val || '1').match(/\d+/);
  return match ? parseInt(match[0], 10) : 1;
}

const addLog = (store: StoreData, kullanici: string, islem: string, detay: string, tur: string) => {
  store.auditLogs.unshift({
    id: Date.now().toString() + Math.random().toString(36).substring(2, 7),
    tarihSaat: new Date().toLocaleString('tr-TR'),
    kullanici, islem, detay, tur
  });
  if (store.auditLogs.length > 100) store.auditLogs.pop();
};

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const cinsiyetFilter = searchParams.get('cinsiyet');
  const store = await loadStoreAsync();

  const headers = {
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
  };

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
    }, { headers });
  }

  return NextResponse.json({ success: true, store }, { headers });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = await loadStoreAsync();

    // Doğrudan Senkronizasyon Aksiyonu
    if (action === 'sync_full_store' && body.store) {
      await saveStoreAsync(body.store);
      return NextResponse.json({ success: true, store: body.store });
    }

    if (action === 'belletmen_login') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (!found || found.password !== String(body.password || '').trim()) {
        addLog(store, found ? found.name : 'Bilinmeyen', 'Hatalı Belletmen Girişi', 'Belletmen şifresi yanlış girildi.', 'hata');
        await saveStoreAsync(store);
        return NextResponse.json({ success: false, message: 'Hatalı belletmen şifresi girdiniz!' }, { status: 401 });
      }
      const targetStudentGender = found.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
      addLog(store, found.name, 'Belletmen Girişi', `${targetStudentGender === 'kiz' ? 'Kız' : 'Erkek'} Pansiyonu yoklama ekranına giriş yapıldı.`, 'basari');
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, belletmen: found, allowedGender: targetStudentGender, store });
    }

    if (action === 'log_forgot_password') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (found) {
        addLog(store, found.name, 'Şifre Hatırlatma Talebi', `Kayıtlı şifre WhatsApp (${found.phone}) üzerinden gönderildi.`, 'uyari');
        await saveStoreAsync(store);
      }
      return NextResponse.json({ success: true });
    }

    if (action === 'admin_login') {
      if (body.username === 'admin' && String(body.password).trim() === '123456') {
        addLog(store, 'Yönetici (Admin)', 'Yönetim Paneli Girişi', 'Sisteme yetkili idareci girişi yapıldı.', 'basari');
        await saveStoreAsync(store);
        return NextResponse.json({ success: true, message: 'Giriş başarılı.', store });
      }
      addLog(store, 'Bilinmeyen (Admin)', 'Hatalı Yönetici Girişi', 'Yönetici şifresi hatalı girildi.', 'hata');
      await saveStoreAsync(store);
      return NextResponse.json({ success: false, message: 'Hatalı yönetici kullanıcı adı veya şifresi!' }, { status: 401 });
    }

    if (action === 'update_attendance') {
      if (Array.isArray(body.students)) {
        const updatedMap = new Map(body.students.map((s: StudentRecord) => [s.id, s]));
        store.students = store.students.map((existing) =>
          updatedMap.has(existing.id) ? (updatedMap.get(existing.id) as StudentRecord) : existing
        );
        await saveStoreAsync(store);
      }
      return NextResponse.json({ success: true, message: 'Yoklama güncellendi.', store });
    }

    if (action === 'add_belletmen') {
      store.belletmenler.push({
        id: Date.now().toString(),
        name: String(body.name).trim(),
        cinsiyet: body.cinsiyet === 'kadin' ? 'kadin' : 'erkek',
        brans: String(body.brans || 'Öğretmen').trim(),
        phone: String(body.phone || '05416571469').trim(),
        password: String(body.password || '1234').trim()
      });
      addLog(store, 'Yönetici', 'Belletmen Eklendi', `${body.name} eklendi.`, 'basari');
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: 'Belletmen eklendi ve mobil cihazlarla eşitlendi.', store });
    }

    if (action === 'bulk_add_belletmen') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = String(r.cinsiyet || 'erkek').toLowerCase();
          store.belletmenler.push({
            id: (Date.now() + Math.random()).toString(),
            name: String(r.name).trim(),
            cinsiyet: rawCins.includes('k') || rawCins.includes('bayan') ? 'kadin' : 'erkek',
            brans: String(r.brans || 'Öğretmen').trim(),
            phone: String(r.phone || '05416571469').trim(),
            password: String(r.password || '1234').trim()
          });
          added++;
        }
      }
      addLog(store, 'Yönetici', 'Toplu Belletmen Yükleme', `${added} belletmen aktarıldı.`, 'basari');
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: `${added} belletmen yüklendi.`, store });
    }

    if (action === 'update_belletmen_password') {
      const target = store.belletmenler.find((b) => b.id === body.id);
      if (target) {
        target.password = String(body.newPassword).trim();
        addLog(store, 'Yönetici', 'Şifre Değişikliği', `${target.name} şifresi güncellendi.`, 'uyari');
        await saveStoreAsync(store);
        return NextResponse.json({ success: true, message: 'Şifre güncellendi.', store });
      }
      return NextResponse.json({ success: false, message: 'Bulunamadı.' }, { status: 404 });
    }

    if (action === 'delete_belletmen') {
      store.belletmenler = store.belletmenler.filter((b) => b.id !== body.id);
      addLog(store, 'Yönetici', 'Silme', `Belletmen silindi.`, 'uyari');
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: 'Silindi.', store });
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
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: 'Nöbetler oluşturuldu!', store });
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
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: `${count} gün eklendi.`, store });
    }

    if (action === 'add_student') {
      const newStudent: StudentRecord = {
        id: Date.now().toString() + Math.random().toString(36).substring(2, 6),
        name: String(body.name || '').trim(),
        cinsiyet: normalizeGender(body.cinsiyet),
        kat: normalizeKat(body.kat),
        oda: String(body.oda || '101').trim(),
        anneAdi: String(body.anneAdi || 'Anne').trim(),
        anneTel: String(body.anneTel || '05416571469').trim(),
        babaAdi: String(body.babaAdi || 'Baba').trim(),
        babaTel: String(body.babaTel || '05416571469').trim(),
        status: 'var'
      };
      store.students.push(newStudent);
      addLog(store, 'Yönetici', 'Öğrenci Eklendi', `${newStudent.name} eklendi.`, 'basari');
      await saveStoreAsync(store);
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
            cinsiyet: normalizeGender(r.cinsiyet),
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
      addLog(store, 'Yönetici', 'Toplu Öğrenci Yükleme', `${added} öğrenci Excel listesinden yüklendi.`, 'basari');
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: `${added} öğrenci başarıyla yüklendi!`, store });
    }

    if (action === 'delete_student') {
      store.students = store.students.filter((s) => s.id !== body.id);
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: 'Öğrenci silindi.', store });
    }

    if (action === 'delete_monthly_duty') {
      store.aylikNobetler = store.aylikNobetler.filter((d) => d.tarih !== body.tarih);
      await saveStoreAsync(store);
      return NextResponse.json({ success: true, message: 'Nöbet silindi.', store });
    }

    return NextResponse.json({ success: false, message: 'Bilinmeyen işlem.' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
'''

def main():
    print("=========================================================")
    print("   HATA GİDERİCİ VE WHATSAPP BOT PAKETLERİ YÜKLENİYOR")
    print("=========================================================")

    kill_old_processes()

    # 1. Eksik NPM paketlerini yükle (Node Module hatası için)
    run_command("npm install express cors whatsapp-web.js qrcode-terminal", "WhatsApp Botu için gereken NPM paketleri kuruluyor")

    # 2. Hatalı TS dosyasını güncelle
    write_file("app/api/pansiyon/route.ts", PANSIYON_API_TS)

    # 3. Cloudflare Tüneli Aç
    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"
    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 4. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 5. Derleme (TypeScript hataları onarıldı) ve Vercel'e gönderme
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "TS18047 TypeScript tipleri onarildi ve WhatsApp bot modul hatalari giderildi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 TÜM HATALAR GİDERİLDİ VE SİSTEM BAŞARIYLA DERLENDİ!")
    print("👉 Yönetici Paneli: https://pansiyon-yurt-sistemi.vercel.app/admin")
    print("=========================================================")

if __name__ == "__main__":
    main()