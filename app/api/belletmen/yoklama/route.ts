import { NextResponse } from 'next/server';

declare global {
  var __pansiyonYoklamaDB: any[] | undefined;
}

if (!globalThis.__pansiyonYoklamaDB) {
  globalThis.__pansiyonYoklamaDB = [
    { id: '1', adSoyad: 'Ahmet Yılmaz', sinif: '10-A', odaNo: '201', veliTelefon: '05416571469', durum: 'burada' },
    { id: '2', adSoyad: 'Mehmet Demir', sinif: '11-B', odaNo: '201', veliTelefon: '05410000002', durum: 'izinli', izinDetay: 'Hafta Sonu Evci İzni' },
    { id: '3', adSoyad: 'Can Kaya', sinif: '9-C', odaNo: '202', veliTelefon: '05410000003', durum: 'burada' },
    { id: '4', adSoyad: 'Burak Şahin', sinif: '12-A', odaNo: '203', veliTelefon: '05410000004', durum: 'yok' },
    { id: '5', adSoyad: 'Emre Çelik', sinif: '10-B', odaNo: '204', veliTelefon: '05410000005', durum: 'revir', izinDetay: 'Baş Ağrısı / Revirde' },
  ];
}

export async function GET() {
  return NextResponse.json({ success: true, data: globalThis.__pansiyonYoklamaDB });
}

export async function POST(request: Request) {
  try {
    const { seans, records } = await request.json();
    if (Array.isArray(records)) {
      globalThis.__pansiyonYoklamaDB = records;
    }
    return NextResponse.json({
      success: true,
      message: `${seans === 'etut' ? '19:15 Etüt' : '23:00 Yat'} yoklaması başarıyla kaydedildi.`,
      updatedCount: records?.length || 0
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}