import { NextResponse } from 'next/server';

export interface StudentRecord {
  id: string;
  name: string;
  cinsiyet: 'erkek' | 'kiz';
  kat: number;
  oda: string;
  anneAdi: string;
  anneTel: string;
  babaAdi: string;
  babaTel: string;
  status: string;
}

export interface BelletmenRecord { id: string; name: string; cinsiyet: 'erkek' | 'kadin'; brans: string; phone: string; password: string; }
export interface MonthlyDutyDay { tarih: string; erkek1: string; erkek2: string; kadin1: string; kadin2: string; }
export interface LeaveRecord { id: string; studentId: string; studentName: string; oda: string; tip: string; baslangic: string; bitis: string; aciklama: string; veliTel: string; createdAt: string; }
export interface DutyLogRecord { id: string; tarih: string; seans: string; erkekBelletmen1: string; erkekBelletmen2: string; kizBelletmen1: string; kizBelletmen2: string; notlar: string; }
export interface AuditLogRecord { id: string; tarihSaat: string; kullanici: string; islem: string; detay: string; tur: string; }

declare global {
  var __pansiyonStoreV13: {
    students: StudentRecord[];
    belletmenler: BelletmenRecord[];
    aylikNobetler: MonthlyDutyDay[];
    leaves: LeaveRecord[];
    dutyLogs: DutyLogRecord[];
    auditLogs: AuditLogRecord[];
  } | undefined;
}

if (!globalThis.__pansiyonStoreV13) {
  globalThis.__pansiyonStoreV13 = {
    students: [
      { id: '1', name: 'Ahmet Yılmaz', cinsiyet: 'erkek', kat: 1, oda: '101', anneAdi: 'Ayşe Yılmaz', anneTel: '05416571469', babaAdi: 'Ali Yılmaz', babaTel: '05416571469', status: 'izinli' },
      { id: '2', name: 'Mehmet Demir', cinsiyet: 'erkek', kat: 1, oda: '101', anneAdi: 'Fatma Demir', anneTel: '05416571469', babaAdi: 'Mustafa Demir', babaTel: '05416571469', status: 'izinli' },
      { id: '3', name: 'Canberk Öztürk', cinsiyet: 'erkek', kat: 1, oda: '102', anneAdi: 'Zeynep Öztürk', anneTel: '05416571469', babaAdi: 'Hasan Öztürk', babaTel: '05556667788', status: 'yok' },
      { id: '4', name: 'Burak Kaya', cinsiyet: 'erkek', kat: 2, oda: '201', anneAdi: 'Elif Kaya', anneTel: '05416571469', babaAdi: 'Hüseyin Kaya', babaTel: '05416571469', status: 'var' },
      { id: '5', name: 'Zeynep Aydın', cinsiyet: 'kiz', kat: 1, oda: 'K-101', anneAdi: 'Hatice Aydın', anneTel: '05416571469', babaAdi: 'İbrahim Aydın', babaTel: '05416571469', status: 'var' },
      { id: '6', name: 'Elif Yılmaz', cinsiyet: 'kiz', kat: 1, oda: 'K-101', anneAdi: 'Merve Yılmaz', anneTel: '05416571469', babaAdi: 'Kemal Yılmaz', babaTel: '05416571469', status: 'izinli' },
      { id: '7', name: 'Selin Şahin', cinsiyet: 'kiz', kat: 2, oda: 'K-201', anneAdi: 'Gül Şahin', anneTel: '05416571469', babaAdi: 'Ömer Şahin', babaTel: '05416571469', status: 'yok' },
      { id: '8', name: 'Merve Çelik', cinsiyet: 'kiz', kat: 2, oda: 'K-201', anneAdi: 'Yasemin Çelik', anneTel: '05416571469', babaAdi: 'Serkan Çelik', babaTel: '05416571469', status: 'var' },
    ],
    belletmenler: [
      { id: 'b1', name: 'Cüneyt DEMİR', cinsiyet: 'erkek', brans: 'Bilişim Teknolojileri', phone: '05416571469', password: '1234' },
      { id: 'b2', name: 'Ali BEY', cinsiyet: 'erkek', brans: 'Matematik', phone: '05416571469', password: '1234' },
      { id: 'b3', name: 'Furkan DEMİR', cinsiyet: 'erkek', brans: 'Tarih', phone: '05416571469', password: '1234' },
      { id: 'b4', name: 'Hasan ÇELİK', cinsiyet: 'erkek', brans: 'Fizik', phone: '05416571469', password: '1234' },
      { id: 'b5', name: 'Ayşenur KAYA', cinsiyet: 'kadin', brans: 'Edebiyat', phone: '05416571469', password: '1234' },
      { id: 'b6', name: 'Fatma YILMAZ', cinsiyet: 'kadin', brans: 'İngilizce', phone: '05416571469', password: '1234' },
      { id: 'b7', name: 'Zeynep ŞAHİN', cinsiyet: 'kadin', brans: 'Kimya', phone: '05416571469', password: '1234' },
      { id: 'b8', name: 'Merve AYDIN', cinsiyet: 'kadin', brans: 'Biyoloji', phone: '05416571469', password: '1234' },
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
      { id: 'log1', tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Sistem', islem: 'Şablon Güncellendi', detay: 'Öğrenci Excel şablonuna Anne Adı ve Baba Adı eklendi.', tur: 'bilgi' }
    ],
  };
}

const addLog = (store: any, kullanici: string, islem: string, detay: string, tur: string) => {
  store.auditLogs.unshift({
    id: Date.now().toString() + Math.random().toString(36).substring(2, 7),
    tarihSaat: new Date().toLocaleString('tr-TR'),
    kullanici, islem, detay, tur
  });
  if (store.auditLogs.length > 100) store.auditLogs.pop();
};

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const cinsiyetFilter = searchParams.get('cinsiyet');
  const store = globalThis.__pansiyonStoreV13!;

  if (cinsiyetFilter === 'erkek' || cinsiyetFilter === 'kiz') {
    const filteredStudents = store.students.filter((s) => s.cinsiyet === cinsiyetFilter);
    const allowedIds = new Set(filteredStudents.map((s) => s.id));
    const filteredLeaves = store.leaves.filter((l) => allowedIds.has(l.studentId));

    return NextResponse.json({
      success: true,
      store: {
        ...store,
        students: filteredStudents,
        leaves: filteredLeaves,
      }
    });
  }

  return NextResponse.json({ success: true, store });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action } = body;
    const store = globalThis.__pansiyonStoreV13!;

    if (action === 'belletmen_login') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (!found || found.password !== String(body.password || '').trim()) {
        addLog(store, found ? found.name : 'Bilinmeyen', 'Hatalı Belletmen Girişi', 'Belletmen şifresi yanlış girildi.', 'hata');
        return NextResponse.json({ success: false, message: 'Hatalı belletmen şifresi girdiniz!' }, { status: 401 });
      }
      const targetStudentGender = found.cinsiyet === 'kadin' ? 'kiz' : 'erkek';
      addLog(store, found.name, 'Belletmen Girişi', `${targetStudentGender === 'kiz' ? 'Kız' : 'Erkek'} Pansiyonu yoklama ekranına giriş yapıldı.`, 'basari');
      return NextResponse.json({ success: true, belletmen: found, allowedGender: targetStudentGender });
    }

    if (action === 'log_forgot_password') {
      const found = store.belletmenler.find((b) => b.id === body.id || b.name === body.name);
      if (found) {
        addLog(store, found.name, 'Şifre Hatırlatma Talebi', `Kayıtlı şifre WhatsApp (${found.phone}) üzerinden gönderildi.`, 'uyari');
      }
      return NextResponse.json({ success: true });
    }

    if (action === 'admin_login') {
      if (body.username === 'admin' && String(body.password).trim() === '123456') {
        addLog(store, 'Yönetici (Admin)', 'Yönetim Paneli Girişi', 'Sisteme yetkili idareci girişi yapıldı.', 'basari');
        return NextResponse.json({ success: true, message: 'Giriş başarılı.', store });
      }
      addLog(store, 'Bilinmeyen (Admin)', 'Hatalı Yönetici Girişi', 'Yönetici şifresi hatalı girildi.', 'hata');
      return NextResponse.json({ success: false, message: 'Hatalı yönetici kullanıcı adı veya şifresi!' }, { status: 401 });
    }

    if (action === 'update_attendance') {
      if (Array.isArray(body.students)) {
        const updatedMap = new Map(body.students.map((s: StudentRecord) => [s.id, s]));
        store.students = store.students.map((existing) =>
          updatedMap.has(existing.id) ? (updatedMap.get(existing.id) as StudentRecord) : existing
        );
      }
      return NextResponse.json({ success: true, message: 'Yoklama güncellendi.' });
    }

    if (action === 'add_belletmen') {
      store.belletmenler.push({ id: Date.now().toString(), name: String(body.name).trim(), cinsiyet: body.cinsiyet === 'kadin' ? 'kadin' : 'erkek', brans: String(body.brans || 'Öğretmen').trim(), phone: String(body.phone || '05416571469').trim(), password: String(body.password || '1234').trim() });
      addLog(store, 'Yönetici', 'Belletmen Eklendi', `${body.name} eklendi.`, 'basari');
      return NextResponse.json({ success: true, message: 'Belletmen eklendi.', store });
    }
    if (action === 'bulk_add_belletmen') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = String(r.cinsiyet || 'erkek').toLowerCase();
          store.belletmenler.push({ id: Date.now().toString()+Math.random(), name: String(r.name), cinsiyet: rawCins.includes('k') || rawCins.includes('bayan') ? 'kadin' : 'erkek', brans: String(r.brans), phone: String(r.phone || '05416571469'), password: String(r.password || '1234') });
          added++;
        }
      }
      addLog(store, 'Yönetici', 'Toplu Belletmen Yükleme', `${added} belletmen aktarıldı.`, 'basari');
      return NextResponse.json({ success: true, message: `${added} belletmen eklendi.`, store });
    }
    if (action === 'update_belletmen_password') {
      const target = store.belletmenler.find((b) => b.id === body.id);
      if (target) {
        target.password = String(body.newPassword).trim();
        addLog(store, 'Yönetici', 'Şifre Değişikliği', `${target.name} şifresi güncellendi.`, 'uyari');
        return NextResponse.json({ success: true, message: 'Şifre güncellendi.', store });
      }
      return NextResponse.json({ success: false, message: 'Bulunamadı.' }, { status: 404 });
    }
    if (action === 'delete_belletmen') {
      store.belletmenler = store.belletmenler.filter((b) => b.id !== body.id);
      addLog(store, 'Yönetici', 'Silme', `Belletmen silindi.`, 'uyari');
      return NextResponse.json({ success: true, message: 'Silindi.', store });
    }
    if (action === 'add_or_update_monthly_duty') {
      const { tarih, erkek1, erkek2, kadin1, kadin2 } = body;
      const idx = store.aylikNobetler.findIndex((d) => d.tarih === tarih);
      const item: MonthlyDutyDay = { tarih, erkek1, erkek2, kadin1, kadin2 };
      if (idx > -1) store.aylikNobetler[idx] = item;
      else { store.aylikNobetler.push(item); store.aylikNobetler.sort((a, b) => a.tarih.localeCompare(b.tarih)); }
      return NextResponse.json({ success: true, message: `${tarih} günü nöbetçileri kaydedildi.`, store });
    }
    if (action === 'auto_generate_month_duty') {
      const yearMonth = String(body.yearMonth);
      const [yStr, mStr] = yearMonth.split('-');
      const days = new Date(Number(yStr), Number(mStr), 0).getDate();
      const erkekler = store.belletmenler.filter((b) => b.cinsiyet === 'erkek');
      const kadinlar = store.belletmenler.filter((b) => b.cinsiyet === 'kadin');
      store.aylikNobetler = store.aylikNobetler.filter((d) => !d.tarih.startsWith(yearMonth));
      for (let d = 1; d <= days; d++) {
        const dateKey = `${yearMonth}-${d < 10 ? '0'+d : d}`;
        store.aylikNobetler.push({
          tarih: dateKey,
          erkek1: erkekler.length > 0 ? erkekler[(d * 2 - 2) % erkekler.length].name : 'Erkek 1',
          erkek2: erkekler.length > 1 ? erkekler[(d * 2 - 1) % erkekler.length].name : 'Erkek 2',
          kadin1: kadinlar.length > 0 ? kadinlar[(d * 2 - 2) % kadinlar.length].name : 'Kadın 1',
          kadin2: kadinlar.length > 1 ? kadinlar[(d * 2 - 1) % kadinlar.length].name : 'Kadın 2',
        });
      }
      addLog(store, 'Yönetici', 'Otomatik Nöbet', `${yearMonth} nöbetleri atandı.`, 'bilgi');
      return NextResponse.json({ success: true, message: 'Nöbetler oluşturuldu!', store });
    }
    if (action === 'bulk_monthly_duty') {
      let count = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.tarih) continue;
          store.aylikNobetler.push({ tarih: String(r.tarih), erkek1: String(r.erkek1), erkek2: String(r.erkek2), kadin1: String(r.kadin1), kadin2: String(r.kadin2) });
          count++;
        }
      }
      return NextResponse.json({ success: true, message: `${count} gün eklendi.`, store });
    }
    if (action === 'delete_monthly_duty') {
      store.aylikNobetler = store.aylikNobetler.filter((d) => d.tarih !== body.tarih);
      return NextResponse.json({ success: true, message: 'Nöbet silindi.', store });
    }
    if (action === 'add_leave') {
      const { studentId, tip, baslangic, bitis, aciklama, veliTel } = body;
      const st = store.students.find((s) => s.id === studentId) || store.students[0];
      store.leaves.unshift({ id: Date.now().toString(), studentId: st.id, studentName: st.name, oda: st.oda, tip: tip || 'Evci İzni', baslangic, bitis, aciklama: aciklama || 'Veli talebi', veliTel: veliTel || st.anneTel, createdAt: new Date().toISOString().split('T')[0] });
      st.status = 'izinli';
      addLog(store, `Veli (${veliTel || st.anneTel})`, 'Veli İzin Talebi', `${st.name} için izin onaylandı.`, 'basari');
      return NextResponse.json({ success: true, message: 'İzin talebi onaylandı.', store });
    }

    // YENİ ÖĞRENCİ EKLEME (TC, Sınıf, Yatak Kaldırıldı -> Anne Adı ve Baba Adı Eklendi)
    if (action === 'add_student') {
      store.students.push({
        id: Date.now().toString(),
        name: String(body.name || '').trim(),
        cinsiyet: body.cinsiyet === 'kiz' ? 'kiz' : 'erkek',
        kat: Number(body.kat || 1),
        oda: String(body.oda || '101').trim(),
        anneAdi: String(body.anneAdi || 'Anne').trim(),
        anneTel: String(body.anneTel || '05416571469').trim(),
        babaAdi: String(body.babaAdi || 'Baba').trim(),
        babaTel: String(body.babaTel || '05416571469').trim(),
        status: 'var'
      });
      addLog(store, 'Yönetici', 'Öğrenci Eklendi', `${body.name} (Oda: ${body.oda}) eklendi.`, 'basari');
      return NextResponse.json({ success: true, message: `${body.name} eklendi.`, store });
    }

    if (action === 'bulk_import') {
      let added = 0;
      if (Array.isArray(body.rows)) {
        for (const r of body.rows) {
          if (!r.name) continue;
          const rawCins = String(r.cinsiyet || 'erkek').toLowerCase();
          store.students.push({
            id: (Date.now() + Math.random()).toString(),
            name: String(r.name).trim(),
            cinsiyet: rawCins.includes('k') || rawCins.includes('bayan') ? 'kiz' : 'erkek',
            kat: Number(r.kat) || 1,
            oda: String(r.oda || '101').trim(),
            anneAdi: String(r.anneAdi || 'Anne').trim(),
            anneTel: String(r.anneTel || '05416571469').trim(),
            babaAdi: String(r.babaAdi || 'Baba').trim(),
            babaTel: String(r.babaTel || '05416571469').trim(),
            status: 'var'
          });
          added++;
        }
      }
      addLog(store, 'Yönetici', 'Toplu Öğrenci Yükleme', `${added} öğrenci Excel şablonundan aktarıldı.`, 'basari');
      return NextResponse.json({ success: true, message: `${added} öğrenci başarıyla eklendi.`, store });
    }

    if (action === 'delete_student') {
      store.students = store.students.filter((s) => s.id !== body.id);
      addLog(store, 'Yönetici', 'Öğrenci Silindi', `Öğrenci kaydı silindi.`, 'uyari');
      return NextResponse.json({ success: true, message: 'Öğrenci silindi.', store });
    }
    if (action === 'add_duty_log') {
      const { tarih, seans, erkekBelletmen1, erkekBelletmen2, kizBelletmen1, kizBelletmen2, notlar } = body;
      store.dutyLogs.unshift({ id: Date.now().toString(), tarih: String(tarih || ''), seans: String(seans || ''), erkekBelletmen1: String(erkekBelletmen1 || ''), erkekBelletmen2: String(erkekBelletmen2 || ''), kizBelletmen1: String(kizBelletmen1 || ''), kizBelletmen2: String(kizBelletmen2 || ''), notlar: String(notlar || '') });
      addLog(store, 'Nöbetçi Belletmen', 'Resmî Nöbet Tutanağı', `${tarih} (${seans}) nöbet defteri kaydedildi.`, 'basari');
      return NextResponse.json({ success: true, message: 'Nöbet defteri kaydedildi.', store });
    }
    if (action === 'clear_audit_logs') {
      store.auditLogs = [{ id: Date.now().toString(), tarihSaat: new Date().toLocaleString('tr-TR'), kullanici: 'Yönetici', islem: 'Günlük Temizlendi', detay: 'Denetim günlüğü yönetici tarafından sıfırlandı.', tur: 'uyari' }];
      return NextResponse.json({ success: true, message: 'Denetim günlüğü temizlendi.', store });
    }

    return NextResponse.json({ success: false, message: 'Bilinmeyen işlem.' }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ success: false, message: err.message }, { status: 500 });
  }
}