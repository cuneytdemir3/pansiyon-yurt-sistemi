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