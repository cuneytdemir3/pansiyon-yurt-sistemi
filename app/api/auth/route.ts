import { NextResponse } from 'next/server';
import { loadFallbackData } from '@/lib/db';
import { signToken, cleanMobileInput } from '@/lib/auth';

export async function POST(request: Request) {
  try {
    const { role, identity, password } = await request.json();
    const cleanId = cleanMobileInput(identity);

    if (role === 'yonetici' || role === 'belletmen') {
      const teachers = loadFallbackData('teachers.json');
      const teacher = teachers.find((t: any) => 
        cleanMobileInput(t['Kullanıcı Adı'] || '') === cleanId ||
        cleanMobileInput(t['TC Kimlik No'] || '') === cleanId ||
        cleanMobileInput(t['Adı Soyadı'] || '') === cleanId
      );

      if (teacher) {
        const token = await signToken({ role, name: teacher['Adı Soyadı'], id: teacher['TC Kimlik No'] });
        const res = NextResponse.json({ success: true, user: teacher['Adı Soyadı'] });
        res.cookies.set('token', token, { httpOnly: true, secure: process.env.NODE_ENV === 'production', maxAge: 60 * 60 * 24 * 7 });
        return res;
      }
    } else if (role === 'veli') {
      const maleStudents = loadFallbackData('male_students.json');
      const femaleStudents = loadFallbackData('female_students.json');
      const allStudents = [...maleStudents, ...femaleStudents];

      const student = allStudents.find((s: any) =>
        cleanMobileInput(s['Anne Telefon'] || '') === cleanId ||
        cleanMobileInput(s['Baba Telefon'] || '') === cleanId ||
        cleanMobileInput(s['Öğrenci Telefon'] || '') === cleanId ||
        cleanMobileInput(s['Adı Soyadı'] || '') === cleanId
      );

      if (student || cleanId) {
        const token = await signToken({ role, student: student ? student['Adı Soyadı'] : 'Veli' });
        const res = NextResponse.json({ success: true, student: student ? student['Adı Soyadı'] : 'Veli' });
        res.cookies.set('token', token, { httpOnly: true, secure: process.env.NODE_ENV === 'production', maxAge: 60 * 60 * 24 * 7 });
        return res;
      }
    }

    return NextResponse.json({ success: false, message: 'Geçersiz kullanıcı adı veya şifre.' }, { status: 401 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}