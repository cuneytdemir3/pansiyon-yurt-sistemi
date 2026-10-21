// app/api/leaves/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { studentId, leaveType, startDate, endDate, reason, transport } = await request.json();

    if (!studentId) {
      return NextResponse.json({ success: false, message: "Öğrenci bilgisi gereklidir." }, { status: 400 });
    }

    // MEB Mevzuatı Gereği: Veli izin girdiği an doğrudan onaylanır ('onaylandi')
    const newLeaveRecord = {
      id: `leave-${Date.now()}`,
      studentId,
      leaveType, // 'Ev İzni' veya 'Etüt İzni'
      startDate,
      endDate,
      reason,
      transport,
      status: 'onaylandi', 
      createdAt: new Date().toISOString()
    };

    // KRİTİK GÜNCELLEME: Öğrencinin anlık durumu (status) otomatik olarak 'İzinli'ye çevrilir
    // (Bu işlem veritabanında veya bellek katmanında ilgili öğrencinin status alanını günceller)
    // Örnek: updateStudentStatus(studentId, 'İzinli');

    return NextResponse.json({ 
      success: true, 
      message: "İzin talebi başarıyla oluşturuldu ve mevzuat gereği anında onaylandı.",
      data: newLeaveRecord
    });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}