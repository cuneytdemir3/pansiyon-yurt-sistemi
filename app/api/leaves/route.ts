import { NextResponse } from 'next/server';
import { loadFallbackData, saveFallbackData } from '@/lib/db';

export async function GET() {
  const leaves = loadFallbackData('leaves.json');
  return NextResponse.json({ success: true, leaves });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { studentName, leaveType, startDate, endDate, transport, reason } = body;

    const newLeave = {
      id: Date.now(),
      studentName: studentName || 'Öğrenci',
      leaveType: leaveType || 'Ev İzni',
      startDate,
      endDate,
      transport,
      reason,
      status: 'Onaylandı', // MEB kuralı: İzin anında otomatik onaylanır
      createdAt: new Date().toISOString()
    };

    const leaves = loadFallbackData('leaves.json');
    leaves.unshift(newLeave);
    saveFallbackData('leaves.json', leaves);

    return NextResponse.json({ success: true, leave: newLeave });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
