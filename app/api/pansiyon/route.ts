import { NextResponse } from 'next/server';

export interface StudentRecord {
  id: string;
  name: string;
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
  belletmenAd: string;
  notlar: string;
  toplam: number;
  varSayisi: number;
  yokSayisi: number;
  izinliSayisi: number;
}

declare global {
  var __pansiyonStore: {
    students: StudentRecord[];
    leaves: LeaveRecord[];
    dutyLogs: DutyLogRecord[];
    nobetciler: { gun: string; belletmen: string; kat: string }[];
  } | undefined;
}

if (!globalThis.__pansiyonStore) {
  globalThis.__pansiyonStore = {
    students: [
      { id: '1', name: 'Ahmet Yılmaz', tc: '12345678901', sinif: '10-A', kat: 1, oda: '101', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '2', name: 'Mehmet Demir', tc: '12345678902', sinif: '11-B', kat: 1, oda: '101', yatak: 'B', anneTel: '05416571469', babaTel: '05416571469', status: 'izinli' },
      { id: '3', name: 'Canberk Öztürk', tc: '12345678905', sinif: '9-A', kat: 1, oda: '102', yatak: 'A', anneTel: '05416571469', babaTel: '05556667788', status: 'yok' },
      { id: '4', name: 'Burak Kaya', tc: '12345678908', sinif: '10-C', kat: 2, oda: '201', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
      { id: '5', name: 'Emre Çelik', tc: '12345678909', sinif: '12-A', kat: 3, oda: '301', yatak: 'A', anneTel: '05416571469', babaTel: '05416571469', status: 'var' },
    ],
    leaves: [
      { id: '101', studentId: '1', studentName: 'Ahmet Yılmaz', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-21', bitis: '2026-10-30', aciklama: 'Akraba ziyareti', veliTel: '05416571469', createdAt: '2026-10-21' },
      { id: '102', studentId: '2', studentName: 'Mehmet Demir', oda: '101', tip: 'Ev İzni', baslangic: '2026-10-20', bitis: '2026-10-25', aciklama: 'Aile ziyareti ve hafta sonu ev izni', veliTel: '05416571469', createdAt: '2026-10-20' },
    ],
    dutyLogs: [
      { id: '1', tarih: '2026-10-24', seans: 'Etüt (19:15)', belletmenAd: 'Cüneyt DEMİR', notlar: 'Etüt yoklaması zamanında alındı. Oda 102 Canberk Öztürk yoklamada bulunmadı, velisine bilgi verildi.', toplam: 5, varSayisi: 2, yokSayisi: 1, izinliSayisi: 2 }
    ],
    nobetciler: [
      { gun: 'Pazartesi', belletmen: 'Cüneyt DEMİR', kat: 'Tüm Katlar' },
      { gun: 'Salı', belletmen: 'Ali KAYA', kat: '1. ve 2. Kat' },
      { gun: 'Çarşamba', belletmen: 'Mehmet YILMAZ', kat: '3. Kat' },
      { gun: 'Perşembe', belletmen: 'Cüneyt DEMİR', kat: 'Tüm Katlar' },
      { gun: 'Cuma', belletmen: 'Hasan DEMİR', kat: 'Hafta Sonu Nöbeti' },
    ]
  };
}

export async function GET() {
  return NextResponse.json({
    success: true,
    store: globalThis.__pansiyonStore
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = globalThis.__pansiyonStore!;

    if (action === 'add_leave') {
      const { studentId, tip, baslangic, bitis, aciklama, veliTel } = body;
      const st = store.students.find((s) => s.id === studentId) || store.students[0];
      const newLeave: LeaveRecord = {
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
      };
      store.leaves.unshift(newLeave);
      st.status = 'izinli';
      return NextResponse.json({ success: true, message: 'İzin talebi onaylandı ve belletmen ekranına otomatik işlendi.', store });
    }

    if (action === 'update_attendance') {
      const { students } = body;
      if (Array.isArray(students)) {
        store.students = students;
      }
      return NextResponse.json({ success: true, message: 'Yoklama kayıtları güncellendi.', store });
    }

    if (action === 'add_student') {
      const { name, tc, sinif, kat, oda, yatak, anneTel, babaTel } = body;
      const newStudent: StudentRecord = {
        id: Date.now().toString(),
        name,
        tc: tc || '10000000000',
        sinif: sinif || '9-A',
        kat: Number(kat) || 1,
        oda: oda || '101',
        yatak: yatak || 'A',
        anneTel: anneTel || '05416571469',
        babaTel: babaTel || '05416571469',
        status: 'var',
      };
      store.students.push(newStudent);
      return NextResponse.json({ success: true, message: `${name} pansiyon listesine eklendi.`, store });
    }

    if (action === 'bulk_import') {
      const { rows } = body;
      let added = 0;
      if (Array.isArray(rows)) {
        for (const r of rows) {
          if (!r.name) continue;
          store.students.push({
            id: (Date.now() + Math.random()).toString(),
            name: r.name.trim(),
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
      return NextResponse.json({ success: true, message: `${added} öğrenci başarıyla toplu olarak yüklendi.`, store });
    }

    if (action === 'delete_student') {
      store.students = store.students.filter((s) => s.id !== body.id);
      return NextResponse.json({ success: true, message: 'Öğrenci kaydı silindi.', store });
    }

    if (action === 'add_duty_log') {
      const { tarih, seans, belletmenAd, notlar } = body;
      const newLog: DutyLogRecord = {
        id: Date.now().toString(),
        tarih,
        seans,
        belletmenAd: belletmenAd || 'Nöbetçi Belletmen',
        notlar,
        toplam: store.students.length,
        varSayisi: store.students.filter((s) => s.status === 'var').length,
        yokSayisi: store.students.filter((s) => s.status === 'yok').length,
        izinliSayisi: store.students.filter((s) => s.status === 'izinli').length,
      };
      store.dutyLogs.unshift(newLog);
      return NextResponse.json({ success: true, message: 'Resmî nöbet defteri kaydı oluşturuldu.', store });
    }

    return NextResponse.json({ success: false, message: 'Geçersiz işlem.' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}