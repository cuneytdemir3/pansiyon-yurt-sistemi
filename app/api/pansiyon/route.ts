import { NextResponse } from 'next/server';

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