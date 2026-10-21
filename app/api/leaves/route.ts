// app/api/leaves/route.ts
import { NextResponse } from 'next/server';

export interface LeaveItem {
  id: string;
  studentId: string;
  studentName: string;
  leaveType: string;
  startDate: string;
  endDate: string;
  transport: string;
  address: string;
  reason: string;
  status: 'onaylandi';
  createdAt: string;
}

declare global {
  // eslint-disable-next-line no-var
  var __pansiyonLeaves: LeaveItem[] | undefined;
}

if (!globalThis.__pansiyonLeaves) {
  globalThis.__pansiyonLeaves = [
    {
      id: 'default-leave-1',
      studentId: '2',
      studentName: 'Mehmet Demir',
      leaveType: 'Ev İzni',
      startDate: '2026-10-20',
      endDate: '2026-10-25',
      transport: 'Veli teslim alacak',
      address: 'İstanbul / Bahçelievler',
      reason: 'Aile ziyareti ve hafta sonu ev izni',
      status: 'onaylandi',
      createdAt: new Date().toISOString(),
    },
  ];
}

export async function GET() {
  return NextResponse.json({
    success: true,
    leaves: globalThis.__pansiyonLeaves || [],
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { studentId, studentName, leaveType, startDate, endDate, transport, address, reason } = body;

    if (!studentId || !startDate || !endDate || !address || !reason) {
      return NextResponse.json(
        { success: false, message: 'Lütfen tüm zorunlu izin alanlarını doldurun.' },
        { status: 400 }
      );
    }

    const newLeave: LeaveItem = {
      id: `leave-${Date.now()}`,
      studentId: String(studentId),
      studentName: studentName || 'Öğrenci',
      leaveType: leaveType || 'Ev İzni',
      startDate,
      endDate,
      transport: transport || 'Veli teslim alacak',
      address,
      reason,
      status: 'onaylandi',
      createdAt: new Date().toISOString(),
    };

    globalThis.__pansiyonLeaves = [newLeave, ...(globalThis.__pansiyonLeaves || [])];

    return NextResponse.json({
      success: true,
      message: 'İzin talebi otomatik olarak onaylandı.',
      leave: newLeave,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Bilinmeyen hata';
    return NextResponse.json({ success: false, message }, { status: 500 });
  }
}