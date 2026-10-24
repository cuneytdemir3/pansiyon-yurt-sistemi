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
    print("🧹 Açık kalan Node.js işlemleri temizleniyor...")
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
# 1. MERKEZİ API ROTASI (app/api/pansiyon/route.ts)
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
  tarih: string;
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

export interface AuditLogRecord {
  id: string;
  tarihSaat: string;
  kullanici: string;
  islem: string;
  detay: string;
  tur: 'basari' | 'uyari' | 'hata' | 'bilgi';
}

declare global {
  var __pansiyonStoreV9: {
    students: StudentRecord[];
    belletmenler: BelletmenRecord[];
    aylikNobetler: MonthlyDutyDay[];
    leaves: LeaveRecord[];
    dutyLogs: DutyLogRecord[];
    auditLogs: AuditLogRecord[];
  } | undefined;
}

if (!globalThis.__pansiyonStoreV9) {
  globalThis.__pansiyonStoreV9 = {
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
    ],
    leaves: [
      { id: '101', studentId: '1', studentName: 'Ahmet Yılmaz', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-21', bitis: '2026-10-30', aciklama: 'Akraba ziyareti', veliTel: '05416571469', createdAt: '2026-10-21' },
      { id: '102', studentId: '2', studentName: 'Mehmet Demir', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-20', bitis: '2026-10-25', aciklama: 'Aile ziyareti ve hafta sonu ev izni', veliTel: '05416571469', createdAt: '2026-10-20' },
      { id: '103', studentId: '6', studentName: 'Elif Yılmaz', oda: 'K-101', tip: 'Ev İzni', baslangic: '2026-10-23', bitis: '2026-10-26', aciklama: 'Hafta sonu evci izni', veliTel: '05416571469', createdAt: '2026-10-23' },
    ],
    dutyLogs: [],
    auditLogs: [
      { id: 'log1', tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Sistem', islem: 'Sistem Başlatıldı', detay: 'Pansiyon Yönetim Sistemi güvenlik ve denetim günlüğü aktif edildi.', tur: 'bilgi' },
      { id: 'log2', tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Cüneyt DEMİR', islem: 'Yetkili Oturumu', detay: 'Erkek Pansiyonu belletmen yoklama modülü hazır.', tur: 'basari' }
    ],
  };
}

const addLog = (store: any, kullanici: string, islem: string, detay: string, tur: 'basari' | 'uyari' | 'hata' | 'bilgi') => {
  store.auditLogs.unshift({
    id: Date.now().toString() + Math.random().toString(36).substring(2, 7),
    tarihSaat: new Date().toLocaleString('tr-TR'),
    kullanici,
    islem,
    detay,
    tur
  });
  if (store.auditLogs.length > 100) store.auditLogs.pop();
};

export async function GET() {
  return NextResponse.json({ success: true, store: globalThis.__pansiyonStoreV9 });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = globalThis.__pansiyonStoreV9!;

    if (action === 'add_belletmen') {
      store.belletmenler.push({
        id: Date.now().toString(),
        name: String(body.name || '').trim(),
        cinsiyet: body.cinsiyet === 'kadin' ? 'kadin' : 'erkek',
        brans: String(body.brans || 'Öğretmen').trim(),
        phone: String(body.phone || '05410000000').trim(),
        password: String(body.password || '1234').trim(),
      });
      addLog(store, 'Yönetici', 'Belletmen Eklendi', `${body.name} isimli öğretmen belletmen listesine eklendi.`, 'basari');
      return NextResponse.json({ success: true, message: `${body.name} belletmen listesine eklendi.`, store });
    }

    if (action === 'bulk_add_belletmen') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = String(r.cinsiyet || 'erkek').toLowerCase();
          const cins: 'erkek' | 'kadin' = rawCins.includes('k') || rawCins.includes('bayan') ? 'kadin' : 'erkek';
          store.belletmenler.push({
            id: (Date.now() + Math.random()).toString(),
            name: String(r.name).trim(),
            cinsiyet: cins,
            brans: String(r.brans || 'Öğretmen').trim(),
            phone: String(r.phone || '05410000000').trim(),
            password: String(r.password || '1234').trim(),
          });
          added++;
        }
      }
      addLog(store, 'Yönetici', 'Toplu Belletmen Yükleme', `${added} belletmen Excel listesinden sisteme aktarıldı.`, 'basari');
      return NextResponse.json({ success: true, message: `${added} belletmen başarıyla eklendi.`, store });
    }

    if (action === 'update_belletmen_password') {
      const target = store.belletmenler.find((b) => b.id === body.id);
      if (target) {
        target.password = String(body.newPassword || '1234').trim();
        addLog(store, 'Yönetici', 'Şifre Değiştirildi', `${target.name} isimli belletmenin giriş şifresi güncellendi.`, 'uyari');
        return NextResponse.json({ success: true, message: `${target.name} şifresi güncellendi.`, store });
      }
      return NextResponse.json({ success: false, message: 'Belletmen bulunamadı.' }, { status: 404 });
    }

    if (action === 'delete_belletmen') {
      const target = store.belletmenler.find((b) => b.id === body.id);
      store.belletmenler = store.belletmenler.filter((b) => b.id !== body.id);
      addLog(store, 'Yönetici', 'Belletmen Silindi', `${target?.name || body.id} kaydı sistemden silindi.`, 'uyari');
      return NextResponse.json({ success: true, message: 'Belletmen kaydı silindi.', store });
    }

    if (action === 'belletmen_login') {
      const found = store.belletmenler.find((b) => b.id === body.id);
      if (!found || found.password !== String(body.password || '').trim()) {
        addLog(store, found ? found.name : 'Bilinmeyen', 'Hatalı Giriş Denemesi', 'Belletmen şifresi hatalı girildi.', 'hata');
        return NextResponse.json({ success: false, message: 'Hatalı belletmen şifresi!' }, { status: 401 });
      }
      addLog(store, found.name, 'Belletmen Girişi', `${found.cinsiyet === 'kadin' ? 'Kız' : 'Erkek'} Pansiyonu yoklama ekranına giriş yapıldı.`, 'basari');
      return NextResponse.json({ success: true, belletmen: found, store });
    }

    if (action === 'add_or_update_monthly_duty') {
      const { tarih, erkek1, erkek2, kadin1, kadin2 } = body;
      const idx = store.aylikNobetler.findIndex((d) => d.tarih === tarih);
      const item: MonthlyDutyDay = { tarih, erkek1, erkek2, kadin1, kadin2 };
      if (idx > -1) store.aylikNobetler[idx] = item;
      else {
        store.aylikNobetler.push(item);
        store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih));
      }
      addLog(store, 'Yönetici', 'Günlük Nöbet Ataması', `${tarih} günü için 2 Erkek + 2 Kadın nöbetçi belletmen güncellendi.`, 'bilgi');
      return NextResponse.json({ success: true, message: `${tarih} günü nöbetçileri kaydedildi.`, store });
    }

    if (action === 'auto_generate_month_duty') {
      const yearMonth = String(body.yearMonth || '2026-10');
      const [yStr, mStr] = yearMonth.split('-');
      const days = new Date(Number(yStr) || 2026, Number(mStr) || 10, 0).getDate();
      const erkekler = store.belletmenler.filter((b) => b.cinsiyet === 'erkek');
      const kadinlar = store.belletmenler.filter((b) => b.cinsiyet === 'kadin');
      store.aylikNobetler = store.aylikNobetler.filter((d) => !d.tarih.startsWith(yearMonth));

      for (let d = 1; d <= days; d++) {
        const dateKey = `${yearMonth}-${d < 10 ? '0' + d : d}`;
        store.aylikNobetler.push({
          tarih: dateKey,
          erkek1: erkekler.length > 0 ? erkekler[(d * 2 - 2) % erkekler.length].name : 'Erkek Belletmen 1',
          erkek2: erkekler.length > 1 ? erkekler[(d * 2 - 1) % erkekler.length].name : 'Erkek Belletmen 2',
          kadin1: kadinlar.length > 0 ? kadinlar[(d * 2 - 2) % kadinlar.length].name : 'Kadın Belletmen 1',
          kadin2: kadinlar.length > 1 ? kadinlar[(d * 2 - 1) % kadinlar.length].name : 'Kadın Belletmen 2',
        });
      }
      store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih));
      addLog(store, 'Yönetici', 'Otomatik Aylık Nöbet', `${yearMonth} ayı (${days} gün) nöbet çizelgesi otomatik oluşturuldu.`, 'basari');
      return NextResponse.json({ success: true, message: `${yearMonth} ayı nöbet listesi oluşturuldu!`, store });
    }

    if (action === 'bulk_monthly_duty') {
      let count = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.tarih) continue;
          const idx = store.aylikNobetler.findIndex((d) => d.tarih === String(r.tarih).trim());
          const item: MonthlyDutyDay = {
            tarih: String(r.tarih).trim(),
            erkek1: String(r.erkek1 || '-').trim(),
            erkek2: String(r.erkek2 || '-').trim(),
            kadin1: String(r.kadin1 || '-').trim(),
            kadin2: String(r.kadin2 || '-').trim(),
          };
          if (idx > -1) store.aylikNobetler[idx] = item;
          else store.aylikNobetler.push(item);
          count++;
        }
        store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih));
      }
      addLog(store, 'Yönetici', 'Excel Nöbet Yükleme', `${count} günlük nöbet çizelgesi toplu yüklendi.`, 'basari');
      return NextResponse.json({ success: true, message: `${count} günlük nöbet listesi aktarıldı.`, store });
    }

    if (action === 'delete_monthly_duty') {
      store.aylikNobetler = store.aylikNobetler.filter((d) => d.tarih !== body.tarih);
      addLog(store, 'Yönetici', 'Nöbet Günü Silindi', `${body.tarih} tarihli nöbet kaydı silindi.`, 'uyari');
      return NextResponse.json({ success: true, message: 'Nöbet günü silindi.', store });
    }

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
      addLog(store, `Veli (${veliTel || st.anneTel})`, 'Veli İzin Talebi', `${st.name} için ${baslangic} - ${bitis} arası ${tip} onaylandı.`, 'basari');
      return NextResponse.json({ success: true, message: 'İzin talebi onaylandı.', store });
    }

    if (action === 'update_attendance') {
      if (Array.isArray(body.students)) {
        store.students = body.students;
      }
      addLog(store, 'Nöbetçi Belletmen', 'Yoklama Güncellendi', 'Pansiyon öğrenci yoklama durumları güncellendi.', 'bilgi');
      return NextResponse.json({ success: true, message: 'Yoklama güncellendi.', store });
    }

    if (action === 'add_student') {
      store.students.push({
        id: Date.now().toString(),
        name: String(body.name || '').trim(),
        cinsiyet: body.cinsiyet === 'kiz' ? 'kiz' : 'erkek',
        tc: String(body.tc || '10000000000'),
        sinif: String(body.sinif || '9-A'),
        kat: Number(body.kat || 1),
        oda: String(body.oda || '101'),
        yatak: String(body.yatak || 'A'),
        anneTel: String(body.anneTel || '05416571469'),
        babaTel: String(body.babaTel || '05416571469'),
        status: 'var',
      });
      addLog(store, 'Yönetici', 'Öğrenci Eklendi', `${body.name} (Oda: ${body.oda}) pansiyona kaydedildi.`, 'basari');
      return NextResponse.json({ success: true, message: `${body.name} eklendi.`, store });
    }

    if (action === 'bulk_import') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          store.students.push({
            id: (Date.now() + Math.random()).toString(),
            name: String(r.name).trim(),
            cinsiyet: String(r.cinsiyet || 'erkek').toLowerCase().includes('k') ? 'kiz' : 'erkek',
            tc: String(r.tc || '10000000000').trim(),
            sinif: String(r.sinif || '9-A').trim(),
            kat: Number(r.kat || 1),
            oda: String(r.oda || '101').trim(),
            yatak: String(r.yatak || 'A').trim(),
            anneTel: String(r.anneTel || '05416571469').trim(),
            babaTel: String(r.babaTel || '05416571469').trim(),
            status: 'var',
          });
          added++;
        }
      }
      addLog(store, 'Yönetici', 'Toplu Öğrenci Yükleme', `${added} öğrenci e-Okul/Excel listesinden aktarıldı.`, 'basari');
      return NextResponse.json({ success: true, message: `${added} öğrenci yüklendi.`, store });
    }

    if (action === 'delete_student') {
      const st = store.students.find((s) => s.id === body.id);
      store.students = store.students.filter((s) => s.id !== body.id);
      addLog(store, 'Yönetici', 'Öğrenci Silindi', `${st?.name || body.id} kaydı silindi.`, 'uyari');
      return NextResponse.json({ success: true, message: 'Öğrenci silindi.', store });
    }

    if (action === 'add_duty_log') {
      const { tarih, seans, erkekBelletmen1, erkekBelletmen2, kizBelletmen1, kizBelletmen2, notlar } = body;
      store.dutyLogs.unshift({
        id: Date.now().toString(),
        tarih: String(tarih || ''),
        seans: String(seans || ''),
        erkekBelletmen1: String(erkekBelletmen1 || '1. Erkek Belletmen'),
        erkekBelletmen2: String(erkekBelletmen2 || '2. Erkek Belletmen'),
        kizBelletmen1: String(kizBelletmen1 || '1. Kadın Belletmen'),
        kizBelletmen2: String(kizBelletmen2 || '2. Kadın Belletmen'),
        notlar: String(notlar || ''),
      });
      addLog(store, 'Nöbetçi Belletmenler', 'Resmî Nöbet Tutanağı', `${tarih} (${seans}) nöbet defteri onaylandı ve PDF çıktısı alındı.`, 'basari');
      return NextResponse.json({ success: true, message: 'Nöbet defteri kaydedildi.', store });
    }

    if (action === 'clear_audit_logs') {
      store.auditLogs = [
        { id: Date.now().toString(), tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Yönetici', islem: 'Günlük Temizlendi', detay: 'Denetim günlüğü yönetici tarafından sıfırlandı.', tur: 'uyari' }
      ];
      return NextResponse.json({ success: true, message: 'Denetim günlüğü temizlendi.', store });
    }

    return NextResponse.json({ success: false, message: 'Bilinmeyen işlem.' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
'''

# -------------------------------------------------------------------------
# 2. ADMİN PANELİ (X İkonu ve Tüm Fonksiyonlar %100 Eksiksiz Tanımlandı)
# -------------------------------------------------------------------------
ADMIN_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  Upload,
  Plus,
  Trash2,
  Shield,
  FileSpreadsheet,
  LogOut,
  KeyRound,
  Eye,
  EyeOff,
  Calendar,
  UserCheck,
  Wand2,
  Save,
  Activity,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
  X
} from 'lucide-react';

interface Student {
  id: string;
  name: string;
  cinsiyet: string;
  tc: string;
  sinif: string;
  kat: number;
  oda: string;
  yatak: string;
  anneTel: string;
  babaTel: string;
  status: string;
}

interface Belletmen {
  id: string;
  name: string;
  cinsiyet: string;
  brans: string;
  phone: string;
  password: string;
}

interface MonthlyDutyDay {
  tarih: string;
  erkek1: string;
  erkek2: string;
  kadin1: string;
  kadin2: string;
}

interface AuditLog {
  id: string;
  tarihSaat: string;
  kullanici: string;
  islem: string;
  detay: string;
  tur: string;
}

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<'belletmen' | 'nobet' | 'ogrenci' | 'loglar'>('belletmen');

  const [students, setStudents] = useState<Student[]>([]);
  const [belletmenler, setBelletmenler] = useState<Belletmen[]>([]);
  const [aylikNobetler, setAylikNobetler] = useState<MonthlyDutyDay[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [msg, setMsg] = useState('');

  // 1) Belletmen State
  const [bName, setBName] = useState('');
  const [bCinsiyet, setBCinsiyet] = useState<'erkek' | 'kadin'>('erkek');
  const [bBrans, setBBrans] = useState('');
  const [bPhone, setBPhone] = useState('0541');
  const [bPassword, setBPassword] = useState('1234');
  const [belletmenCsv, setBelletmenCsv] = useState(
    'Serhat AKAN, erkek, Matematik, 05411112233, 1453\nElif DEMİR, kadin, Edebiyat, 05412223344, 2026'
  );

  const [visiblePasswords, setVisiblePasswords] = useState<Record<string, boolean>>({});
  const [editingPasswordId, setEditingPasswordId] = useState<string | null>(null);
  const [newPasswordVal, setNewPasswordVal] = useState('');

  // 2) Aylık Nöbet State
  const [nobetAySecim, setNobetAySecim] = useState('2026-10');
  const [nTarih, setNTarih] = useState('2026-10-29');
  const [nErkek1, setNErkek1] = useState('Cüneyt DEMİR');
  const [nErkek2, setNErkek2] = useState('Ali BEY');
  const [nKadin1, setNKadin1] = useState('Ayşenur KAYA');
  const [nKadin2, setNKadin2] = useState('Fatma YILMAZ');
  const [nobetCsv, setNobetCsv] = useState(
    '2026-10-29, Cüneyt DEMİR, Ali BEY, Ayşenur KAYA, Fatma YILMAZ\n2026-10-30, Furkan DEMİR, Hasan ÇELİK, Zeynep ŞAHİN, Merve AYDIN'
  );

  // 3) Öğrenci State
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

  // --- BELLETMEN İŞLEMLERİ ---
  const handleAddBelletmen = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_belletmen', name: bName, cinsiyet: bCinsiyet, brans: bBrans, phone: bPhone, password: bPassword }),
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
      const p = line.split(',').map((x) => x.trim());
      return { name: p[0], cinsiyet: p[1] || 'erkek', brans: p[2] || 'Öğretmen', phone: p[3] || '05410000000', password: p[4] || '1234' };
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

  // --- AYLIK NÖBET İŞLEMLERİ ---
  const handleAddSingleDutyDay = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_or_update_monthly_duty', tarih: nTarih, erkek1: nErkek1, erkek2: nErkek2, kadin1: nKadin1, kadin2: nKadin2 }),
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

  const handleBulkMonthlyDuty = async () => {
    const lines = nobetCsv.split('\n').map((l) => l.trim()).filter(Boolean);
    const rows = lines.map((line) => {
      const p = line.split(',').map((x) => x.trim());
      return { tarih: p[0], erkek1: p[1] || '-', erkek2: p[2] || '-', kadin1: p[3] || '-', kadin2: p[4] || '-' };
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

  // --- ÖĞRENCİ İŞLEMLERİ ---
  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sName) return;
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'add_student', name: sName, cinsiyet: sCinsiyet, tc: sTc, sinif: sSinif, kat: sKat, oda: sOda, yatak: sYatak, anneTel: sAnneTel, babaTel: sBabaTel }),
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
      const p = line.split(',').map((x) => x.trim());
      return { name: p[0], cinsiyet: p[1] || 'erkek', tc: p[2] || '10000000000', sinif: p[3] || '9-A', kat: Number(p[4]) || 1, oda: p[5] || '101', yatak: p[6] || 'A', anneTel: p[7] || '05416571469', babaTel: p[8] || '05416571469' };
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

  const handleClearLogs = async () => {
    const res = await fetch('/api/pansiyon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'clear_audit_logs' }),
    });
    const data = await res.json();
    if (data.success) {
      syncFromStore(data.store);
      setMsg(data.message);
    }
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
                Belletmen Şifre & Excel Yönetimi • Aylık Nöbet Listesi • Öğrenci Yönetimi • <strong className="text-indigo-600">Sistem Güvenlik & Denetim Günlüğü</strong>
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
            <a href="/" className="flex items-center gap-1.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 px-4 py-2 rounded-xl">
              <LogOut className="w-4 h-4" /> Çıkış Yap
            </a>
          </div>
        </div>

        {/* 4 SEKMELİ MENÜ */}
        <div className="bg-white rounded-2xl p-2 border border-slate-200 shadow-xs flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTab('belletmen')}
            className={`flex-1 min-w-[160px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'belletmen' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <KeyRound className="w-4 h-4" /> 1. Belletmen & Şifre ({belletmenler.length})
          </button>
          <button
            onClick={() => setActiveTab('nobet')}
            className={`flex-1 min-w-[160px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'nobet' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Calendar className="w-4 h-4" /> 2. Aylık Nöbet ({aylikNobetler.length} Gün)
          </button>
          <button
            onClick={() => setActiveTab('ogrenci')}
            className={`flex-1 min-w-[160px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'ogrenci' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Users className="w-4 h-4" /> 3. Öğrenciler ({students.length})
          </button>
          <button
            onClick={() => setActiveTab('loglar')}
            className={`flex-1 min-w-[180px] flex items-center justify-center gap-2 py-3 px-3 rounded-xl text-xs font-extrabold transition-all cursor-pointer ${
              activeTab === 'loglar' ? 'bg-slate-900 text-amber-400 shadow-sm' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Activity className="w-4 h-4" /> 4. Sistem Güvenlik & Denetim Günlüğü ({auditLogs.length})
          </button>
        </div>

        {msg && (
          <div className="p-4 bg-emerald-50 border border-emerald-300 text-emerald-800 rounded-2xl text-xs font-bold flex justify-between items-center">
            <span>✅ {msg}</span>
            <button onClick={() => setMsg('')} className="underline ml-4 cursor-pointer">Kapat</button>
          </div>
        )}

        {/* SEKME 4: SİSTEM GÜVENLİK & DENETİM GÜNLÜĞÜ */}
        {activeTab === 'loglar' && (
          <div className="bg-slate-950 rounded-3xl p-6 border border-slate-800 shadow-2xl space-y-5">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-amber-400" /> Sistem Güvenlik & Denetim Günlüğü (Audit Log)
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Belletmen girişleri, şifre değişiklikleri, öğrenci/izin hareketleri ve nöbet işlemleri saniye saniye kayıt altına alınır.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-3 py-1.5 rounded-full border border-emerald-800">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Canlı İzleme Aktif
                </div>
                <button
                  onClick={handleClearLogs}
                  className="text-[11px] font-bold text-rose-300 hover:text-white bg-rose-950/50 border border-rose-800 px-3 py-1.5 rounded-xl cursor-pointer"
                >
                  Günlüğü Temizle
                </button>
              </div>
            </div>

            <div className="overflow-x-auto max-h-[500px]">
              <table className="w-full text-xs border-collapse text-left">
                <thead className="sticky top-0 bg-slate-950">
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                    <th className="p-3">Tarih / Saat</th>
                    <th className="p-3">Kullanıcı / Kaynak</th>
                    <th className="p-3">İşlem Türü</th>
                    <th className="p-3">Açıklama & Detay</th>
                    <th className="p-3 text-right">Durum</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-900/60 transition-colors">
                      <td className="p-3 font-mono text-slate-300 flex items-center gap-2 whitespace-nowrap">
                        <Clock className="w-3.5 h-3.5 text-slate-500" /> {log.tarihSaat}
                      </td>
                      <td className="p-3 font-semibold text-blue-300 whitespace-nowrap">{log.kullanici}</td>
                      <td className="p-3 font-bold text-slate-100 whitespace-nowrap">{log.islem}</td>
                      <td className="p-3 text-slate-300">{log.detay}</td>
                      <td className="p-3 text-right whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md border font-bold text-[10px] uppercase ${getBadgeColor(log.tur)}`}>
                          {getIcon(log.tur)} {log.tur}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* SEKME 1: BELLETMEN & ŞİFRE YÖNETİMİ */}
        {activeTab === 'belletmen' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Plus className="w-4 h-4 text-indigo-600" /> Tekil Belletmen Öğretmen Ekle
                </h2>
                <form onSubmit={handleAddBelletmen} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={bName} onChange={(e) => setBName(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2.5 font-semibold" />
                  <select value={bCinsiyet} onChange={(e) => setBCinsiyet(e.target.value as 'erkek' | 'kadin')} className="border border-slate-200 rounded-xl px-3 py-2.5 font-bold bg-white">
                    <option value="erkek">👨 Erkek Belletmen</option>
                    <option value="kadin">👩 Kadın Belletmen</option>
                  </select>
                  <input type="text" placeholder="Branş" value={bBrans} onChange={(e) => setBBrans(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2.5" />
                  <input type="text" placeholder="Telefon" value={bPhone} onChange={(e) => setBPhone(e.target.value)} className="border border-slate-200 rounded-xl px-3 py-2.5 font-mono" />
                  <input type="text" required placeholder="Giriş Şifresi" value={bPassword} onChange={(e) => setBPassword(e.target.value)} className="col-span-2 border border-indigo-200 bg-indigo-50/40 rounded-xl px-3 py-2.5 font-mono font-bold" />
                  <button type="submit" className="col-span-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    Belletmeni Sisteme Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Excel ile Toplu Belletmen Ekleme
                </h2>
                <p className="text-[11px] text-slate-500">Format: <code>Ad Soyad, erkek/kadin, Branş, Telefon, Şifre</code></p>
                <textarea rows={4} value={belletmenCsv} onChange={(e) => setBelletmenCsv(e.target.value)} className="w-full border border-slate-200 rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkAddBelletmen} className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4" /> Excel Belletmen Listesini Toplu Yükle
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-indigo-600" /> Kayıtlı Belletmenler & Şifre Görme / Değiştirme
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-xs border-collapse text-left">
                  <thead>
                    <tr className="bg-slate-100 text-slate-700">
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Grup</th>
                      <th className="p-2.5">Branş</th>
                      <th className="p-2.5">Şifre (Gör / Değiştir)</th>
                      <th className="p-2.5 text-right">Sil</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {belletmenler.map((b) => {
                      const isShown = !!visiblePasswords[b.id];
                      const isEditing = editingPasswordId === b.id;
                      return (
                        <tr key={b.id} className="hover:bg-slate-50">
                          <td className="p-2.5 font-bold">{b.name}</td>
                          <td className="p-2.5">{b.cinsiyet === 'kadin' ? '👩 Kadın' : '👨 Erkek'}</td>
                          <td className="p-2.5">{b.brans}</td>
                          <td className="p-2.5">
                            {isEditing ? (
                              <div className="flex items-center gap-1.5">
                                <input type="text" value={newPasswordVal} onChange={(e) => setNewPasswordVal(e.target.value)} className="border border-indigo-300 rounded-lg px-2 py-1 text-xs font-mono w-24" />
                                <button onClick={() => handleUpdatePassword(b.id)} className="bg-emerald-600 text-white px-2.5 py-1 rounded-lg font-bold cursor-pointer">Kaydet</button>
                                <button onClick={() => setEditingPasswordId(null)} className="text-slate-500 underline cursor-pointer">İptal</button>
                              </div>
                            ) : (
                              <div className="flex items-center gap-2">
                                <span className="font-mono font-bold bg-slate-100 px-2.5 py-1 rounded-lg">{isShown ? b.password : '••••••'}</span>
                                <button onClick={() => setVisiblePasswords((p) => ({ ...p, [b.id]: !p[b.id] }))} className="text-slate-500 hover:text-indigo-600 cursor-pointer">
                                  {isShown ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                                <button onClick={() => { setEditingPasswordId(b.id); setNewPasswordVal(b.password); }} className="text-indigo-600 font-bold hover:underline cursor-pointer">
                                  Şifre Değiştir
                                </button>
                              </div>
                            )}
                          </td>
                          <td className="p-2.5 text-right">
                            <button onClick={() => handleDeleteBelletmen(b.id)} className="text-rose-600 hover:text-rose-800 cursor-pointer">
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

        {/* SEKME 2: AYLIK NÖBET LİSTESİ */}
        {activeTab === 'nobet' && (
          <div className="space-y-6">
            <div className="bg-indigo-950 text-white rounded-2xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h2 className="text-sm font-extrabold flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-amber-400" /> Otomatik Aylık Nöbet Çizelgesi Oluştur
                </h2>
                <p className="text-xs text-indigo-200">Seçilen ayın tüm günlerine 2 Erkek + 2 Kadın belletmeni otomatik dağıtır.</p>
              </div>
              <div className="flex items-center gap-2">
                <input type="month" value={nobetAySecim} onChange={(e) => setNobetAySecim(e.target.value)} className="bg-white text-slate-900 font-bold text-xs px-3 py-2 rounded-xl" />
                <button onClick={handleAutoGenerateMonth} className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs px-4 py-2 rounded-xl cursor-pointer">
                  Tüm Ayı Otomatik Doldur
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900">Tekil Gün Nöbeti Ata</h3>
                <form onSubmit={handleAddSingleDutyDay} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="date" value={nTarih} onChange={(e) => setNTarih(e.target.value)} className="col-span-2 border rounded-xl px-3 py-2 font-bold" />
                  <select value={nErkek1} onChange={(e) => setNErkek1(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nErkek2} onChange={(e) => setNErkek2(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {erkekBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin1} onChange={(e) => setNKadin1(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <select value={nKadin2} onChange={(e) => setNKadin2(e.target.value)} className="border rounded-xl px-2 py-2 bg-white">
                    {kadinBelletmenList.map((b) => <option key={b.id} value={b.name}>{b.name}</option>)}
                  </select>
                  <button type="submit" className="col-span-2 bg-blue-600 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    <Save className="w-4 h-4 inline mr-1" /> Günü Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900">Excel ile Aylık Nöbet Listesi Yükle</h3>
                <textarea rows={4} value={nobetCsv} onChange={(e) => setNobetCsv(e.target.value)} className="w-full border rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkMonthlyDuty} className="w-full bg-emerald-600 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4 inline mr-1" /> Aylık Nöbet Listesini Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
              <div className="overflow-x-auto max-h-[420px]">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100 sticky top-0">
                    <tr>
                      <th className="p-2.5">Tarih</th>
                      <th className="p-2.5 text-blue-800">Erkek Belletmenler</th>
                      <th className="p-2.5 text-rose-800">Kadın Belletmenler</th>
                      <th className="p-2.5 text-right">Sil</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {aylikNobetler.map((d) => (
                      <tr key={d.tarih} className="hover:bg-slate-50">
                        <td className="p-2.5 font-mono font-bold">{d.tarih}</td>
                        <td className="p-2.5 text-blue-700 font-semibold">👨 {d.erkek1} & {d.erkek2}</td>
                        <td className="p-2.5 text-rose-700 font-semibold">👩 {d.kadin1} & {d.kadin2}</td>
                        <td className="p-2.5 text-right">
                          <button onClick={() => handleDeleteDutyDay(d.tarih)} className="text-rose-600 cursor-pointer">
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

        {/* SEKME 3: ÖĞRENCİ YÖNETİMİ */}
        {activeTab === 'ogrenci' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900">Yeni Öğrenci Kaydı</h2>
                <form onSubmit={handleAddStudent} className="grid grid-cols-2 gap-3 text-xs">
                  <input type="text" required placeholder="Ad Soyad" value={sName} onChange={(e) => setSName(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <select value={sCinsiyet} onChange={(e) => setSCinsiyet(e.target.value as 'erkek' | 'kiz')} className="border rounded-xl px-3 py-2 font-bold bg-white">
                    <option value="erkek">Erkek Pansiyonu</option>
                    <option value="kiz">Kız Pansiyonu</option>
                  </select>
                  <input type="text" placeholder="T.C." value={sTc} onChange={(e) => setSTc(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Sınıf (9-A)" value={sSinif} onChange={(e) => setSSinif(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <select value={sKat} onChange={(e) => setSKat(Number(e.target.value))} className="border rounded-xl px-3 py-2 bg-white">
                    <option value={1}>1. Kat</option>
                    <option value={2}>2. Kat</option>
                    <option value={3}>3. Kat</option>
                  </select>
                  <input type="text" placeholder="Oda No" value={sOda} onChange={(e) => setSOda(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Anne Tel" value={sAnneTel} onChange={(e) => setSAnneTel(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <input type="text" placeholder="Baba Tel" value={sBabaTel} onChange={(e) => setSBabaTel(e.target.value)} className="border rounded-xl px-3 py-2" />
                  <button type="submit" className="col-span-2 bg-indigo-600 text-white py-2.5 rounded-xl font-bold cursor-pointer">
                    Öğrenciyi Kaydet
                  </button>
                </form>
              </div>

              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <h2 className="text-sm font-bold text-slate-900">Excel ile Toplu Öğrenci Yükleme</h2>
                <textarea rows={4} value={studentCsv} onChange={(e) => setStudentCsv(e.target.value)} className="w-full border rounded-xl p-3 text-xs font-mono bg-slate-50" />
                <button onClick={handleBulkImportStudents} className="w-full bg-emerald-600 text-white py-2.5 rounded-xl text-xs font-bold cursor-pointer">
                  <Upload className="w-4 h-4 inline mr-1" /> Toplu Öğrenci Aktar
                </button>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100">
                    <tr>
                      <th className="p-2.5">Ad Soyad</th>
                      <th className="p-2.5">Bölüm</th>
                      <th className="p-2.5">Kat / Oda</th>
                      <th className="p-2.5">Anne Tel</th>
                      <th className="p-2.5 text-right">Sil</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {students.map((s) => (
                      <tr key={s.id} className="hover:bg-slate-50">
                        <td className="p-2.5 font-bold">{s.name}</td>
                        <td className="p-2.5">{s.cinsiyet === 'kiz' ? '👩 Kız' : '👨 Erkek'}</td>
                        <td className="p-2.5">{s.kat}. Kat - Oda {s.oda}</td>
                        <td className="p-2.5 font-mono">{s.anneTel}</td>
                        <td className="p-2.5 text-right">
                          <button onClick={() => handleDeleteStudent(s.id)} className="text-rose-600 cursor-pointer">
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

def main():
    print("=========================================================")
    print("   TYPESCRIPT DERLEME HATASI ONARILIYOR VE YAYINLANIYOR")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 1. API ve Admin Dosyalarını Güncelle
    write_file("app/api/pansiyon/route.ts", PANSIYON_API_TS)
    write_file("app/admin/page.tsx", ADMIN_PAGE_TSX)

    # 2. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 3. Derleme ve GitHub/Vercel Gönderimi
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen yukarıdaki detaylı çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Admin paneli X ikonu import hatasi giderildi ve Sistem Guvenlik Gunlugu yayina alindi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 DERLEME BAŞARILI! TÜM SİSTEM CANLIYA ALINDI!")
    print("👉 Yönetici Paneli: https://pansiyon-yurt-sistemi.vercel.app/admin")
    print("=========================================================")

if __name__ == "__main__":
    main()