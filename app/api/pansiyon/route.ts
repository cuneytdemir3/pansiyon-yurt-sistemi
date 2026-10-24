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
  var __pansiyonStoreV4: {
    students: StudentRecord[];
    leaves: LeaveRecord[];
    dutyLogs: DutyLogRecord[];
    nobetciler: {
      gun: string;
      erkek1: string;
      erkek2: string;
      kadin1: string;
      kadin2: string;
    }[];
  } | undefined;
}

if (!globalThis.__pansiyonStoreV4) {
  globalThis.__pansiyonStoreV4 = {
    students: [
      // Erkek Öğrenciler
      { id: '1', name: 'Ahmet Yılmaz', cinsiyet: 'erkek', tc: '12345678901', sinif: '10-A', kat: 1, oda: '101', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '2', name: 'Mehmet Demir', cinsiyet: 'erkek', tc: '12345678902', sinif: '11-B', kat: 1, oda: '101', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '3', name: 'Canberk Öztürk', cinsiyet: 'erkek', tc: '12345678905', sinif: '9-A', kat: 1, oda: '102', yatak: 'A', anneTel: '05416571469', babaTel: '05556667788', status: 'yok' },
      { id: '4', name: 'Burak Kaya', cinsiyet: 'erkek', tc: '12345678908', sinif: '10-C', kat: 2, oda: '201', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
      // Kız Öğrenciler
      { id: '5', name: 'Zeynep Aydın', cinsiyet: 'kiz', tc: '12345678912', sinif: '10-A', kat: 1, oda: 'K-101', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
      { id: '6', name: 'Elif Yılmaz', cinsiyet: 'kiz', tc: '12345678913', sinif: '11-A', kat: 1, oda: 'K-101', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '7', name: 'Selin Şahin', cinsiyet: 'kiz', tc: '12345678914', sinif: '9-B', kat: 2, oda: 'K-201', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'yok' },
      { id: '8', name: 'Merve Çelik', cinsiyet: 'kiz', tc: '12345678915', sinif: '12-B', kat: 2, oda: 'K-201', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
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
    nobetciler: [
      { gun: 'Pazartesi', erkek1: 'Cüneyt DEMİR', erkek2: 'Ali BEY', kadin1: 'Ayşenur KAYA', kadin2: 'Fatma YILMAZ' },
      { gun: 'Salı', erkek1: 'Furkan DEMİR', erkek2: 'Hasan ÇELİK', kadin1: 'Zeynep ŞAHİN', kadin2: 'Merve AYDIN' },
      { gun: 'Çarşamba', erkek1: 'Cüneyt DEMİR', erkek2: 'Furkan DEMİR', kadin1: 'Ayşenur KAYA', kadin2: 'Zeynep ŞAHİN' },
      { gun: 'Perşembe', erkek1: 'Ali BEY', erkek2: 'Hasan ÇELİK', kadin1: 'Fatma YILMAZ', kadin2: 'Merve AYDIN' },
      { gun: 'Cuma', erkek1: 'Cüneyt DEMİR', erkek2: 'Ali BEY', kadin1: 'Ayşenur KAYA', kadin2: 'Fatma YILMAZ' },
      { gun: 'Cumartesi', erkek1: 'Furkan DEMİR', erkek2: 'Hasan ÇELİK', kadin1: 'Zeynep ŞAHİN', kadin2: 'Merve AYDIN' },
      { gun: 'Pazar', erkek1: 'Cüneyt DEMİR', erkek2: 'Furkan DEMİR', kadin1: 'Ayşenur KAYA', kadin2: 'Merve AYDIN' },
    ]
  };
}

export async function GET() {
  return NextResponse.json({ success: true, store: globalThis.__pansiyonStoreV4 });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = globalThis.__pansiyonStoreV4!;

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