import { NextResponse } from 'next/server';
import { loadFallbackData, saveFallbackData } from '@/lib/db';

export async function GET() {
  const attendance = loadFallbackData('attendance.json');
  return NextResponse.json({ success: true, attendance });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { floor, records, sessionType } = body; // records: { roomNo: status }

    const newRecord = {
      id: Date.now(),
      floor,
      sessionType: sessionType || 'Etüt',
      records,
      createdAt: new Date().toISOString()
    };

    const attendanceList = loadFallbackData('attendance.json');
    attendanceList.unshift(newRecord);
    saveFallbackData('attendance.json', attendanceList);

    return NextResponse.json({ success: true, record: newRecord });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}
