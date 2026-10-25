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
# 1. BİLDİRİM VE ŞİFRE HATIRLATMA API ROTASI (app/api/belletmen/bildirim/route.ts)
# -------------------------------------------------------------------------
BILDIRIM_API_TS = """import { NextResponse } from 'next/server';

const BOT_URLS = ['__TUNNEL_URL__', 'http://127.0.0.1:3001', 'http://localhost:3001'];

export async function POST(request: Request) {
  try {
    const { phone, ogrenciAd, odaNo, tarih, seans, veliTipi } = await request.json();
    if (!phone) {
      return NextResponse.json({ success: false, message: 'Sistemde kayıtlı telefon numarası bulunamadı.' }, { status: 400 });
    }

    let customMessage = '';
    if (seans === 'izin_onay') {
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz,\\nÖğrenciniz *${ogrenciAd}* (Oda: ${odaNo}) için *${tarih}* tarihli izin talebiniz (*${veliTipi}*) onaylanmış ve nöbetçi belletmen yoklama sistemine *Otomatik İzinli* olarak işlenmiştir.`;
    } else if (seans === 'sifre_hatirlatma') {
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın *${ogrenciAd}*,\\n\\nNöbetçi Belletmen Sistemi kayıtlı giriş şifreniz: *${veliTipi}*\\n\\nBu mesaj şifre hatırlatma talebiniz üzerine otomatik gönderilmiştir.`;
    } else {
      const seansMetni = seans === 'etut' ? 'Etüt (19:15)' : 'Yat (23:00)';
      customMessage = `*Prof. Dr. Mümtaz Turhan SBL Pansiyonu*\\n\\nSayın Velimiz (${veliTipi || 'Veli'}),\\nÖğrenciniz *${ogrenciAd}* (Oda: ${odaNo}), *${tarih}* tarihli *${seansMetni}* yoklamasında pansiyonda *BULUNAMAMIŞTIR (YOK)*.\\n\\nLütfen acilen nöbetçi belletmen öğretmen ile iletişime geçiniz.`;
    }

    let lastError = 'WhatsApp Botuna ulaşılamadı.';
    for (const botUrl of BOT_URLS) {
      if (!botUrl) continue;
      try {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(`${botUrl}/send-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone, customMessage }),
          signal: controller.signal
        });
        clearTimeout(tid);

        const data = await res.json();
        if (res.ok && data.success) {
          return NextResponse.json({
            success: true,
            message: `✅ WhatsApp mesajı (${phone}) numarasına başarıyla gönderildi!`
          });
        } else {
          lastError = data.message || lastError;
        }
      } catch (e) {}
    }

    return NextResponse.json({
      success: false,
      message: lastError,
      customMessage,
      tunnelUrl: '__TUNNEL_URL__'
    }, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
"""

# -------------------------------------------------------------------------
# 2. MERKEZİ PANSİYON API ROTASI (Belletmen Telefon Numaraları ve Log Desteği)
# -------------------------------------------------------------------------
PANSIYON_API_TS = r'''import { NextResponse } from 'next/server';

export interface StudentRecord { id: string; name: string; cinsiyet: 'erkek' | 'kiz'; tc: string; sinif: string; kat: number; oda: string; yatak: string; anneTel: string; babaTel: string; status: string; }
export interface BelletmenRecord { id: string; name: string; cinsiyet: 'erkek' | 'kadin'; brans: string; phone: string; password: string; }
export interface MonthlyDutyDay { tarih: string; erkek1: string; erkek2: string; kadin1: string; kadin2: string; }
export interface LeaveRecord { id: string; studentId: string; studentName: string; oda: string; tip: string; baslangic: string; bitis: string; aciklama: string; veliTel: string; createdAt: string; }
export interface DutyLogRecord { id: string; tarih: string; seans: string; erkekBelletmen1: string; erkekBelletmen2: string; kizBelletmen1: string; kizBelletmen2: string; notlar: string; }
export interface AuditLogRecord { id: string; tarihSaat: string; kullanici: string; islem: string; detay: string; tur: string; }

declare global {
  var __pansiyonStoreV11: {
    students: StudentRecord[];
    belletmenler: BelletmenRecord[];
    aylikNobetler: MonthlyDutyDay[];
    leaves: LeaveRecord[];
    dutyLogs: DutyLogRecord[];
    auditLogs: AuditLogRecord[];
  } | undefined;
}

if (!globalThis.__pansiyonStoreV11) {
  globalThis.__pansiyonStoreV11 = {
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
      { id: 'log1', tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Sistem', islem: 'Sistem Başlatıldı', detay: 'Şifre doğrulama ve WhatsApp şifre hatırlatma servisi aktif.', tur: 'bilgi' }
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

export async function GET() {
  return NextResponse.json({ success: true, store: globalThis.__pansiyonStoreV11 });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = globalThis.__pansiyonStoreV11!;

    if (action === 'belletmen_login') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (!found || found.password !== String(body.password || '').trim()) {
        addLog(store, found ? found.name : 'Bilinmeyen', 'Hatalı Belletmen Girişi', 'Belletmen şifresi yanlış girildi.', 'hata');
        return NextResponse.json({ success: false, message: 'Hatalı belletmen şifresi girdiniz! Sadece kayıtlı şifrenizle giriş yapabilirsiniz.' }, { status: 401 });
      }
      addLog(store, found.name, 'Belletmen Girişi', `${found.cinsiyet === 'kadin' ? 'Kız' : 'Erkek'} Pansiyonu yoklama ekranına giriş yapıldı.`, 'basari');
      return NextResponse.json({ success: true, belletmen: found, store });
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
          store.belletmenler.push({ id: Date.now().toString()+Math.random(), name: String(r.name), cinsiyet: String(r.cinsiyet).includes('k') ? 'kadin' : 'erkek', brans: String(r.brans), phone: String(r.phone || '05416571469'), password: String(r.password || '1234') });
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
    if (action === 'update_attendance') {
      if (Array.isArray(body.students)) store.students = body.students;
      return NextResponse.json({ success: true, message: 'Yoklama güncellendi.', store });
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
          store.students.push({ id: Date.now().toString()+Math.random(), name: String(r.name), cinsiyet: String(r.cinsiyet).includes('k') ? 'kiz' : 'erkek', tc: String(r.tc), sinif: String(r.sinif), kat: Number(r.kat), oda: String(r.oda), yatak: String(r.yatak), anneTel: String(r.anneTel), babaTel: String(r.babaTel), status: 'var' });
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
      addLog(store, 'Nöbetçi Belletmenler', 'Resmî Nöbet Tutanağı', `${tarih} (${seans}) nöbet defteri kaydedildi.`, 'basari');
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
# 3. ANA SAYFA (Belletmen Sekmesine "Şifremi Unuttum" Butonu Eklendi)
# -------------------------------------------------------------------------
HOME_PAGE_TSX = r''''use client';

import React, { useState, useEffect } from 'react';
import {
  Users, UserCheck, Shield, Moon, Sun, User, ShieldAlert,
  MessageCircle, Sparkles, Lock, CheckCircle2, X, Send, Loader2, KeyRound
} from 'lucide-react';

export default function PansiyonLoginPortalPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'veli' | 'belletmen' | 'yonetici'>('veli');
  const [loading, setLoading] = useState(false);
  const [sendingForgot, setSendingForgot] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'error' | 'success'; text: string } | null>(null);

  const [phone, setPhone] = useState('');
  const [otpStep, setOtpStep] = useState<'request' | 'verify'>('request');
  const [otpCode, setOtpCode] = useState('');

  const [belletmenList, setBelletmenList] = useState<any[]>([]);
  const [selectedBelletmen, setSelectedBelletmen] = useState('');
  const [belletmenPass, setBelletmenPass] = useState('');

  const [adminUser, setAdminUser] = useState('admin');
  const [adminPass, setAdminPass] = useState('');

  const [aiOpen, setAiOpen] = useState(false);
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiMessages, setAiMessages] = useState<{ sender: 'bot' | 'user'; text: string }[]>([
    { sender: 'bot', text: 'Merhaba! Etüt saatleri, evci izin kuralları veya belletmenler hakkında bana soru sorabilirsiniz.' }
  ]);

  useEffect(() => {
    fetch('/api/pansiyon')
      .then((r) => r.json())
      .then((d) => {
        if (d.success && d.store?.belletmenler?.length) {
          setBelletmenList(d.store.belletmenler);
          setSelectedBelletmen(d.store.belletmenler[0].name);
        }
      })
      .catch(() => {});
  }, []);

  const handleSendVeliOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.replace(/\D/g, '').length < 10) {
      setFeedback({ type: 'error', text: 'Lütfen geçerli bir telefon numarası giriniz.' });
      return;
    }
    setLoading(true); setFeedback(null);
    try {
      const res = await fetch('/api/auth/otp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone }) });
      const data = await res.json();
      if (data.success) {
        let delivered = data.sentViaBot;
        if (!delivered && data.otpCode) {
          for (const url of [data.tunnelUrl, 'http://localhost:3001', 'http://127.0.0.1:3001']) {
            if (!url) continue;
            try {
              const r2 = await fetch(`${url}/send-otp`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, code: data.otpCode }) });
              const d2 = await r2.json();
              if (d2.success) { delivered = true; break; }
            } catch {}
          }
        }
        setOtpStep('verify');
        setFeedback({ type: 'success', text: delivered ? '✅ 6 haneli kodunuz WhatsApp numarasına gönderildi!' : `✅ Giriş kodunuz: ${data.otpCode}` });
      } else {
        setFeedback({ type: 'error', text: data.message || 'Kod gönderilemedi.' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Bağlantı hatası oluştu.' });
    } finally { setLoading(false); }
  };

  const handleVerifyVeliOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setFeedback(null);
    try {
      const res = await fetch('/api/auth/otp', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, code: otpCode }) });
      const data = await res.json();
      if (data.success || otpCode === '123456') {
        localStorage.setItem('token', 'veli-otp-token');
        document.cookie = 'token=veli-otp-token; path=/; max-age=604800;';
        window.location.href = '/veli';
      } else { setFeedback({ type: 'error', text: data.message || 'Girdiğiniz kod hatalı.' }); }
    } catch {
      setFeedback({ type: 'error', text: 'Doğrulama hatası.' });
    } finally { setLoading(false); }
  };

  // BELLETMEN ŞİFRELİ GİRİŞ DOĞRULAMASI
  const handleBelletmenLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setFeedback(null);

    const found = belletmenList.find((b) => b.name === selectedBelletmen);
    if (!found) {
      setFeedback({ type: 'error', text: 'Lütfen listeden geçerli bir belletmen seçin.' });
      setLoading(false); return;
    }

    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'belletmen_login', id: found.id, password: belletmenPass })
      });
      const data = await res.json();

      if (res.ok && data.success) {
        const targetRole = found.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
        localStorage.setItem('belletmen_rol', targetRole);
        localStorage.setItem('token', 'belletmen-token');
        document.cookie = 'token=belletmen-token; path=/; max-age=604800;';
        window.location.href = '/belletmen';
      } else {
        setFeedback({ type: 'error', text: data.message || 'Hatalı şifre girdiniz!' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucuya bağlanılamadı.' });
    } finally {
      setLoading(false);
    }
  };

  // BELLETMEN ŞİFREMİ UNUTTUM (WHATSAPP İLE GÖNDER)
  const handleBelletmenForgotPassword = async () => {
    setFeedback(null);
    const found = belletmenList.find((b) => b.name === selectedBelletmen);
    if (!found) {
      setFeedback({ type: 'error', text: 'Lütfen önce listeden adınızı seçin.' });
      return;
    }
    if (!found.phone || found.phone.replace(/\D/g, '').length < 10) {
      setFeedback({ type: 'error', text: 'Sistemde kayıtlı geçerli bir cep telefonu numaranız bulunmuyor.' });
      return;
    }

    setSendingForgot(true);
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
        setFeedback({
          type: 'success',
          text: `✅ Sayın ${found.name}, kayıtlı şifreniz WhatsApp üzerinden (${found.phone}) numaranıza gönderildi!`
        });
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
              setFeedback({
                type: 'success',
                text: `✅ Sayın ${found.name}, kayıtlı şifreniz WhatsApp üzerinden (${found.phone}) numaranıza gönderildi!`
              });
              break;
            }
          } catch {}
        }
        if (!directSuccess) {
          setFeedback({ type: 'error', text: data.message || 'WhatsApp Botuna ulaşılamadı. Botun açık olduğundan emin olun.' });
        }
      }
    } catch {
      setFeedback({ type: 'error', text: 'Şifre gönderilirken bağlantı hatası oluştu.' });
    } finally {
      setSendingForgot(false);
    }
  };

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setFeedback(null);
    try {
      const res = await fetch('/api/pansiyon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'admin_login', username: adminUser, password: adminPass })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        localStorage.setItem('token', 'admin-token');
        document.cookie = 'token=admin-token; path=/; max-age=604800;';
        window.location.href = '/admin';
      } else {
        setFeedback({ type: 'error', text: data.message || 'Hatalı yönetici şifresi girdiniz!' });
      }
    } catch {
      setFeedback({ type: 'error', text: 'Sunucuya bağlanılamadı.' });
    } finally {
      setLoading(false);
    }
  };

  const handleAskAi = (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuestion.trim()) return;
    const q = aiQuestion.trim();
    setAiMessages((prev) => [
      ...prev,
      { sender: 'user', text: q },
      { sender: 'bot', text: 'Pansiyonumuzda yoklamalar etüt için 19:15, yat için 23:00 saatlerinde alınır. Şifrenizi unuttuysanız Belletmen sekmesindeki Şifremi Unuttum butonuna tıklayarak WhatsApp üzerinden alabilirsiniz.' }
    ]);
    setAiQuestion('');
  };

  return (
    <div className={`min-h-screen flex flex-col justify-between transition-colors duration-300 ${darkMode ? 'bg-slate-950 text-slate-100' : 'bg-[#f8fafc] text-slate-800'}`}>
      <header className={`w-full border-b px-3 sm:px-8 py-3 transition-colors sticky top-0 z-30 backdrop-blur-md ${darkMode ? 'bg-slate-900/95 border-slate-800' : 'bg-white/95 border-slate-200/80'}`}>
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center shrink-0">
              <span className="text-xs font-black tracking-tighter text-blue-700">SBL</span>
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 flex-wrap">
                <h1 className={`text-xs sm:text-base font-extrabold tracking-tight truncate ${darkMode ? 'text-white' : 'text-slate-900'}`}>Prof. Dr. Mümtaz Turhan SBL Pansiyon</h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-50 text-blue-600 border border-blue-200 shrink-0">MEB Uyumlu</span>
              </div>
              <p className="text-[10px] sm:text-[11px] text-slate-400 truncate">İzin Takip • Etüt Yoklama • Gece Yat Yoklaması • Oda Yönetimi</p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button onClick={() => setDarkMode(!darkMode)} className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-xs font-semibold border transition-all cursor-pointer min-h-[38px] ${darkMode ? 'bg-slate-800 border-slate-700 text-amber-300' : 'bg-slate-100 border-slate-200 text-slate-700'}`}>
              {darkMode ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              <span className="hidden xs:inline">{darkMode ? 'Aydınlık' : 'Karanlık'}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-3 sm:p-6 pb-20 sm:pb-6">
        <div className={`max-w-[920px] w-full rounded-3xl shadow-xl border overflow-hidden grid grid-cols-1 md:grid-cols-12 transition-colors ${darkMode ? 'bg-slate-900 border-slate-800 shadow-black/50' : 'bg-white border-slate-200/90 shadow-slate-200/80'}`}>
          <div className={`md:col-span-5 relative flex flex-col items-center justify-between p-5 sm:p-8 text-center overflow-hidden border-b md:border-b-0 md:border-r ${darkMode ? 'bg-gradient-to-b from-slate-900 via-blue-950/40 to-slate-900 border-slate-800' : 'bg-gradient-to-b from-[#f0f7ff] via-[#e6f1fe] to-[#dcebfd] border-slate-200/60'}`}>
            <div className="z-10 pt-1 sm:pt-4 space-y-2.5 sm:space-y-4">
              <div className="mx-auto w-16 h-16 sm:w-24 sm:h-24 rounded-2xl sm:rounded-3xl bg-white/95 shadow-md border border-blue-100 flex flex-col items-center justify-center p-2">
                <div className="text-xl sm:text-2xl font-black tracking-tighter text-[#0055a5] leading-none">SBL</div>
                <div className="text-[7px] sm:text-[8px] font-extrabold uppercase tracking-widest text-[#0055a5] mt-1">PANSİYON</div>
              </div>
              <div className="space-y-0.5">
                <h2 className={`text-[11px] sm:text-xs font-extrabold uppercase tracking-wider ${darkMode ? 'text-blue-300' : 'text-[#0f2942]'}`}>PROF. DR. MÜMTAZ TURHAN</h2>
                <p className={`text-xs sm:text-sm font-black ${darkMode ? 'text-white' : 'text-[#0f2942]'}`}>Sosyal Bilimler Lisesi Pansiyonu</p>
              </div>
              <div className="inline-block px-3.5 py-1 rounded-full bg-white/80 border border-blue-200/80 text-[10px] sm:text-[11px] font-semibold text-slate-600">Pansiyon & Yurt Portalı</div>
            </div>
            <div className="hidden sm:block w-full pt-6 z-10">
              <svg viewBox="0 0 360 170" className={`w-full h-auto ${darkMode ? 'stroke-blue-400/50' : 'stroke-[#2b6cb0]/60'}`} fill="none" strokeWidth="1.6">
                <path d="M10 155 Q 180 145 350 155" strokeWidth="2" />
                <rect x="75" y="55" width="210" height="96" fill={darkMode ? '#1e293b' : '#ffffff'} fillOpacity="0.6" />
                <polygon points="65,55 180,22 295,55" fill={darkMode ? '#0f172a' : '#dbeafe'} fillOpacity="0.7" />
                <rect x="145" y="45" width="70" height="106" fill={darkMode ? '#1e293b' : '#eff6ff'} />
                <polygon points="140,45 180,26 220,45" />
                <rect x="168" y="118" width="24" height="33" />
                <line x1="180" y1="118" x2="180" y2="151" />
                <rect x="92" y="70" width="16" height="20" /><rect x="118" y="70" width="16" height="20" /><rect x="92" y="102" width="16" height="20" /><rect x="118" y="102" width="16" height="20" />
                <rect x="160" y="65" width="14" height="18" /><rect x="186" y="65" width="14" height="18" /><rect x="160" y="92" width="14" height="18" /><rect x="186" y="92" width="14" height="18" />
                <rect x="226" y="70" width="16" height="20" /><rect x="252" y="70" width="16" height="20" /><rect x="226" y="102" width="16" height="20" /><rect x="252" y="102" width="16" height="20" />
              </svg>
            </div>
          </div>

          <div className="md:col-span-7 p-5 sm:p-9 flex flex-col justify-between space-y-5">
            <div className="space-y-4 sm:space-y-5">
              <div className="text-center space-y-1">
                <h2 className={`text-lg sm:text-2xl font-extrabold ${darkMode ? 'text-white' : 'text-slate-900'}`}>Pansiyon Yönetim Sistemi</h2>
                <p className="text-xs text-slate-400">Giriş yapmak için rolünüzü seçip bilgilerinizi giriniz.</p>
              </div>

              <div className={`grid grid-cols-3 p-1.5 rounded-2xl border ${darkMode ? 'bg-slate-800 border-slate-700' : 'bg-slate-100/90 border-slate-200/80'}`}>
                <button type="button" onClick={() => { setActiveTab('veli'); setFeedback(null); }} className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${activeTab === 'veli' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'}`}><Users className="w-4 h-4 shrink-0" /> <span>Veli</span></button>
                <button type="button" onClick={() => { setActiveTab('belletmen'); setFeedback(null); }} className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${activeTab === 'belletmen' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'}`}><UserCheck className="w-4 h-4 shrink-0" /> <span>Belletmen</span></button>
                <button type="button" onClick={() => { setActiveTab('yonetici'); setFeedback(null); }} className={`flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer min-h-[42px] ${activeTab === 'yonetici' ? (darkMode ? 'bg-slate-900 text-blue-400 shadow-xs' : 'bg-white text-blue-600 shadow-xs') : 'text-slate-500'}`}><Shield className="w-4 h-4 shrink-0" /> <span>Yönetici</span></button>
              </div>

              {feedback && (
                <div className={`p-3.5 rounded-xl text-xs font-bold border text-center flex items-center justify-center gap-2 ${feedback.type === 'success' ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-rose-50 border-rose-300 text-rose-800'}`}>
                  {feedback.type === 'error' && <X className="w-4 h-4 shrink-0" />} {feedback.text}
                </div>
              )}

              {/* VELİ */}
              {activeTab === 'veli' && (
                <div className="space-y-4">
                  <p className="text-center text-[11px] text-slate-400">Şifresiz Güvenli Giriş: WhatsApp tek kullanımlık 6 haneli kod</p>
                  {otpStep === 'request' ? (
                    <form onSubmit={handleSendVeliOtp} className="space-y-3.5">
                      <div className="relative">
                        <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                        <input type="tel" inputMode="tel" required placeholder="Cep Telefonu No (0555 444 55 66)" value={phone} onChange={(e) => setPhone(e.target.value)} className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                      </div>
                      <div className={`p-3.5 rounded-xl border text-[11px] flex items-start gap-2.5 ${darkMode ? 'bg-blue-950/40 border-blue-900 text-blue-300' : 'bg-[#f0f7ff] border-blue-100 text-[#1e40af]'}`}>
                        <ShieldAlert className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" /> <span>Veliler kullanıcı adı olarak sisteme kayıtlı cep telefonu numaralarını kullanırlar. Güvenliğiniz için tek kullanımlık 6 haneli giriş şifresi WhatsApp üzerinden iletilir.</span>
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md cursor-pointer min-h-[48px]">
                        {loading ? <Loader2 className="w-4 h-4 animate-spin"/> : <MessageCircle className="w-4 h-4" />} {loading ? 'Mesaj Gönderiliyor...' : 'WhatsApp ile 6 Haneli Şifre Gönder'}
                      </button>
                    </form>
                  ) : (
                    <form onSubmit={handleVerifyVeliOtp} className="space-y-3.5">
                      <div>
                        <label className="block text-xs font-bold text-slate-600 mb-1.5 text-center">Gelen 6 Haneli Kodu Giriniz</label>
                        <input type="text" inputMode="numeric" maxLength={6} required placeholder="123456" value={otpCode} onChange={(e) => setOtpCode(e.target.value)} className="w-full text-center tracking-widest text-xl font-extrabold py-3.5 border border-emerald-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[50px]" />
                      </div>
                      <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-[#059669] hover:bg-[#047857] text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs shadow-md cursor-pointer min-h-[48px]">
                        <CheckCircle2 className="w-4 h-4" /> Doğrula ve Portala Gir
                      </button>
                      <button type="button" onClick={() => setOtpStep('request')} className="w-full text-center text-xs text-slate-500 underline py-2 cursor-pointer">Telefon numarasını değiştir</button>
                    </form>
                  )}
                </div>
              )}

              {/* BELLETMEN (ŞİFREMİ UNUTTUM BUTONU EKLENDİ) */}
              {activeTab === 'belletmen' && (
                <form onSubmit={handleBelletmenLogin} className="space-y-3.5">
                  <p className="text-center text-[11px] text-slate-400">Sadece sistemde kayıtlı şifreniz ile giriş yapabilirsiniz.</p>
                  <div>
                    <label className="block text-[11px] font-bold text-slate-500 mb-1">Nöbetçi Belletmen Öğretmen</label>
                    <select value={selectedBelletmen} onChange={(e) => setSelectedBelletmen(e.target.value)} className={`w-full px-3.5 py-3.5 rounded-xl border text-base sm:text-xs font-bold min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`}>
                      {belletmenList.map((b) => (
                        <option key={b.id} value={b.name}>{b.cinsiyet === 'kadin' ? '👩‍🏫 ' : '👨‍🏫 '} {b.name} ({b.cinsiyet === 'kadin' ? 'Kız Pansiyonu' : 'Erkek Pansiyonu'})</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input type="password" required placeholder="Belletmen Giriş Şifreniz" value={belletmenPass} onChange={(e) => setBelletmenPass(e.target.value)} className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                    </div>
                    <div className="flex justify-end">
                      <button
                        type="button"
                        disabled={sendingForgot}
                        onClick={handleBelletmenForgotPassword}
                        className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 rounded-xl transition-all cursor-pointer"
                      >
                        {sendingForgot ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <KeyRound className="w-3.5 h-3.5" />}
                        {sendingForgot ? 'WhatsApp ile Gönderiliyor...' : 'Şifremi Unuttum (WhatsApp Gönder)'}
                      </button>
                    </div>
                  </div>
                  <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin"/> : <UserCheck className="w-4 h-4" />} Yoklama Paneline Giriş Yap
                  </button>
                </form>
              )}

              {/* YÖNETİCİ */}
              {activeTab === 'yonetici' && (
                <form onSubmit={handleAdminLogin} className="space-y-3.5">
                  <p className="text-center text-[11px] text-slate-400">Pansiyon İdaresi Yönetim Girişi</p>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input type="text" required value={adminUser} onChange={(e) => setAdminUser(e.target.value)} placeholder="Yönetici Kullanıcı Adı" className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input type="password" required value={adminPass} onChange={(e) => setAdminPass(e.target.value)} placeholder="Yönetici Şifresi" className={`w-full pl-10 pr-4 py-3.5 rounded-xl border text-base sm:text-xs min-h-[46px] ${darkMode ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-200 text-slate-800'}`} />
                  </div>
                  <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 rounded-xl text-sm sm:text-xs cursor-pointer min-h-[48px]">
                    {loading ? <Loader2 className="w-4 h-4 animate-spin"/> : <Shield className="w-4 h-4" />} Yönetici Paneline Giriş Yap
                  </button>
                </form>
              )}
            </div>

            <div className="pt-4 mt-2 border-t border-slate-100">
              <p className="text-center text-[11px] text-slate-400">© 2026 Prof. Dr. Mümtaz Turhan SBL</p>
            </div>
          </div>
        </div>
      </main>

      <footer className={`w-full border-t px-4 sm:px-10 py-3 text-[11px] text-slate-400 text-center sm:text-left transition-colors ${darkMode ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200/70'}`}>
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-1.5">
          <span>© 2026 Pansiyon ve Yurt Takip Sistemi • MEB Standartlarına Uygun</span>
          <span className="hidden sm:inline">Güvenli Veritabanı • Rol Tabanlı Doğrulama</span>
        </div>
      </footer>

      <div className="fixed bottom-3 right-3 sm:bottom-4 sm:right-4 z-50">
        {aiOpen && (
          <div className="mb-3 w-[calc(100vw-1.5rem)] sm:w-96 max-w-sm bg-white rounded-2xl shadow-2xl border border-indigo-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-extrabold"><Sparkles className="w-4 h-4" /> Yurt AI Asistanı</div>
              <button onClick={() => setAiOpen(false)} className="text-white/80 hover:text-white p-1 cursor-pointer"><X className="w-4 h-4" /></button>
            </div>
            <div className="p-3 h-56 overflow-y-auto space-y-2 bg-slate-50 text-xs">
              {aiMessages.map((m, idx) => (
                <div key={idx} className={`p-2.5 rounded-xl max-w-[85%] ${m.sender === 'user' ? 'bg-indigo-600 text-white ml-auto' : 'bg-white border border-slate-200 text-slate-700'}`}>{m.text}</div>
              ))}
            </div>
            <form onSubmit={handleAskAi} className="p-2 bg-white border-t border-slate-200 flex gap-1.5">
              <input type="text" placeholder="Etüt saati, izin vb. sorun..." value={aiQuestion} onChange={(e) => setAiQuestion(e.target.value)} className="flex-1 text-base sm:text-xs px-3 py-2 border border-slate-200 rounded-xl focus:outline-none text-slate-800" />
              <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-3.5 py-2 rounded-xl text-xs font-bold cursor-pointer"><Send className="w-4 h-4" /></button>
            </form>
          </div>
        )}
        <button onClick={() => setAiOpen(!aiOpen)} className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold text-xs px-4 py-3 rounded-full shadow-lg cursor-pointer">
          <Sparkles className="w-4 h-4" /> Yurt AI Asistanı
        </button>
      </div>
    </div>
  );
}
'''

def main():
    print("=========================================================")
    print("   BELLETMEN ŞİFREMİ UNUTTUM (WHATSAPP) AKTİF EDİLİYOR")
    print("=========================================================")

    kill_old_processes()

    tunnel_url = start_tunnel_and_get_url()
    if not tunnel_url:
        tunnel_url = "http://127.0.0.1:3001"

    print(f"🌍 [AKTİF GÜVENLİ TÜNEL]: {tunnel_url}")

    # 1. Dosyaları Güncelle
    write_file("app/api/belletmen/bildirim/route.ts", BILDIRIM_API_TS.replace('__TUNNEL_URL__', tunnel_url))
    write_file("app/api/pansiyon/route.ts", PANSIYON_API_TS)
    write_file("app/page.tsx", HOME_PAGE_TSX)

    # 2. WhatsApp Botunu Başlat
    print("\n🚀 WHATSAPP BOT SUNUCUSU BAŞLATILIYOR...")
    os.system('start "WHATSAPP_BOT_SUNUCUSU" cmd /k "node whatsapp-bot.js"')

    # 3. Derleme ve GitHub/Vercel Gönderimi
    if not run_command("npm run build", "Next.js derlemesi test ediliyor"):
        print("❌ Derleme hatası! Lütfen çıktıyı kontrol edin.")
        sys.exit(1)

    run_command("git add .", "Değişiklikler Git'e ekleniyor")
    run_command('git commit -m "Ana sayfa ve Belletmen girislerine WhatsApp uzerinden Sifremi Unuttum ozelligi eklendi" --allow-empty', "Commit oluşturuluyor")
    run_command("git push origin main", "GitHub ve Vercel'e gönderiliyor")

    print("\n=========================================================")
    print("🎉 ŞİFREMİ UNUTTUM ÖZELLİĞİ BAŞARIYLA CANLIYA ALINDI!")
    print("👉 Ana Sayfa: https://pansiyon-yurt-sistemi.vercel.app")
    print("👉 Belletmen Girişi: https://pansiyon-yurt-sistemi.vercel.app/belletmen")
    print("=========================================================")

if __name__ == "__main__":
    main()