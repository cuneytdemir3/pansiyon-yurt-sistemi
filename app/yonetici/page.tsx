// app/yonetici/page.tsx
'use client';

import React, { useState } from 'react';
import { Users, Shield, Search, Bed, Phone, Home, FileSpreadsheet, CheckCircle, Activity, Lock, Globe, LogOut } from 'lucide-react';
import * as XLSX from 'xlsx';

interface Student {
  id: string;
  name: string;
  tc: string;
  gender: 'Erkek' | 'Kız';
  room: number;
  bed: string;
  status: 'Var' | 'Yok' | 'İzinli';
  parentPhone: string;
}

interface Belletmen {
  id: string;
  name: string;
  phone: string;
  dutyDays: string[];
}

interface AuditLog {
  id: string;
  user: string;
  role: string;
  action: string;
  ip: string;
  timestamp: string;
}

export default function YoneticiPage() {
  const [activeTab, setActiveTab] = useState<'erkek' | 'kiz' | 'belletmens' | 'security'>('erkek');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');

  const handleLogout = () => {
    document.cookie = 'token=; Max-Age=0; path=/;';
    localStorage.removeItem('token');
    sessionStorage.clear();
    window.location.href = '/';
  };

  const [students, setStudents] = useState<Student[]>([
    { id: '1', name: 'Ahmet Yılmaz', tc: '12345678901', gender: 'Erkek', room: 101, bed: 'A', status: 'Var', parentPhone: '05551112233' },
    { id: '2', name: 'Mehmet Demir', tc: '12345678902', gender: 'Erkek', room: 101, bed: 'B', status: 'İzinli', parentPhone: '05552223344' },
    { id: '3', name: 'Canberk Öztürk', tc: '12345678905', gender: 'Erkek', room: 102, bed: 'A', status: 'Var', parentPhone: '05556667788' },
    { id: '4', name: 'Ayşe Kaya', tc: '12345678903', gender: 'Kız', room: 201, bed: 'A', status: 'Var', parentPhone: '05553334455' },
    { id: '5', name: 'Zeynep Çelik', tc: '12345678904', gender: 'Kız', room: 201, bed: 'B', status: 'İzinli', parentPhone: '05554445566' },
  ]);

  const [belletmens, setBelletmens] = useState<Belletmen[]>([
    { id: '1', name: 'Ali Çelik (Matematik Öğretmeni)', phone: '05324445566', dutyDays: ['Pazartesi', 'Perşembe'] },
    { id: '2', name: 'Fatma Şahin (Türk Dili ve Edebiyatı)', phone: '05335556677', dutyDays: ['Salı', 'Cuma'] },
  ]);

  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([
    { id: '1', user: 'Ali Çelik', role: 'Belletmen', action: '1. Kat akşam etüt yoklaması alındı (19:15)', ip: '192.168.1.45', timestamp: '21.10.2026 - 19:18' },
    { id: '2', user: 'Mehmet Demir Velisi', role: 'Veli', action: 'Ev izni gönderildi — Öğrenci otomatik İzinli sayıldı', ip: '88.235.12.5', timestamp: '21.10.2026 - 17:42' },
    { id: '3', user: 'Pansiyon İdaresi', role: 'Yönetici', action: 'Excel ile belletmen ve öğrenci listesi güncellendi', ip: '192.168.1.10', timestamp: '21.10.2026 - 14:10' },
  ]);

  const handleTeacherExcelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const bstr = evt.target?.result;
        const workbook = XLSX.read(bstr, { type: 'binary' });
        const wsname = workbook.SheetNames[0];
        const ws = workbook.Sheets[wsname];
        const data = XLSX.utils.sheet_to_json<Record<string, string>>(ws);

        const newBelletmens: Belletmen[] = data.map((row, index) => ({
          id: `excel-t-${Date.now()}-${index}`,
          name: row['Ad Soyad'] || row['Adı Soyadı'] || row['İsim'] || 'Öğretmen',
          phone: row['Telefon'] || row['Tel'] || row['GSM'] || 'Belirtilmemiş',
          dutyDays: row['Nöbet Günleri'] ? String(row['Nöbet Günleri']).split(',').map((d) => d.trim()) : ['Pazartesi'],
        }));

        setBelletmens((prev) => [...prev, ...newBelletmens]);
        setAuditLogs((prev) => [
          {
            id: `log-${Date.now()}`,
            user: 'Pansiyon Yöneticisi',
            role: 'Yönetici',
            action: `Excel ile ${newBelletmens.length} belletmen öğretmen yüklendi`,
            ip: '192.168.1.1',
            timestamp: new Date().toLocaleString('tr-TR'),
          },
          ...prev,
        ]);
        setUploadSuccess(`Başarıyla ${newBelletmens.length} öğretmen sisteme eklendi!`);
        setTimeout(() => setUploadSuccess(''), 5000);
      } catch {
        alert('Excel dosyası okunurken bir hata oluştu.');
      }
    };
    reader.readAsBinaryString(file);
  };

  const handleStudentExcelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const bstr = evt.target?.result;
        const workbook = XLSX.read(bstr, { type: 'binary' });
        const wsname = workbook.SheetNames[0];
        const ws = workbook.Sheets[wsname];
        const data = XLSX.utils.sheet_to_json<Record<string, string | number>>(ws);

        const newStudents: Student[] = data.map((row, index) => ({
          id: `excel-s-${Date.now()}-${index}`,
          name: String(row['Ad Soyad'] || row['Adı Soyadı'] || 'Öğrenci'),
          tc: String(row['TC'] || row['T.C.'] || '00000000000'),
          gender: activeTab === 'kiz' ? 'Kız' : 'Erkek',
          room: Number(row['Oda'] || row['Oda No'] || 101),
          bed: String(row['Yatak'] || 'A'),
          status: 'Var',
          parentPhone: String(row['Veli Telefon'] || row['Telefon'] || '05550000000'),
        }));

        setStudents((prev) => [...prev, ...newStudents]);
        setUploadSuccess(`Başarıyla ${newStudents.length} öğrenci odalarına yerleştirildi!`);
        setTimeout(() => setUploadSuccess(''), 5000);
      } catch {
        alert('Öğrenci Excel dosyası okunurken bir hata oluştu.');
      }
    };
    reader.readAsBinaryString(file);
  };

  const filteredStudents = students.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.tc.includes(searchTerm) ||
      s.room.toString().includes(searchTerm);
    if (activeTab === 'erkek') return s.gender === 'Erkek' && matchesSearch;
    if (activeTab === 'kiz') return s.gender === 'Kız' && matchesSearch;
    return false;
  });

  const groupedByRoom = filteredStudents.reduce((acc, student) => {
    if (!acc[student.room]) acc[student.room] = [];
    acc[student.room].push(student);
    return acc;
  }, {} as Record<number, Student[]>);

  const filteredBelletmens = belletmens.filter(
    (b) => b.name.toLowerCase().includes(searchTerm.toLowerCase()) || b.phone.includes(searchTerm)
  );

  const filteredLogs = auditLogs.filter(
    (l) =>
      l.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.action.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto space-y-5 bg-gray-50 min-h-screen">
      {/* Üst Başlık, Sekmeler ve Çıkış Butonu */}
      <div className="flex flex-col gap-4 bg-white p-4 md:p-6 rounded-2xl shadow-sm border border-gray-100">
        <div className="flex flex-wrap justify-between items-center gap-3 border-b border-gray-100 pb-4">
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-gray-800">Pansiyon Yöneticisi Paneli</h1>
            <p className="text-xs md:text-sm text-gray-500">
              Erkek/Kız Oda Yerleşimleri, Belletmen Kadrosu ve Güvenlik Denetim Günlüğü
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition-all shadow-sm"
          >
            <LogOut className="w-4 h-4" /> Çıkış Yap
          </button>
        </div>

        <div className="grid grid-cols-2 sm:flex flex-wrap bg-gray-100 p-1 rounded-xl gap-1 w-full">
          <button
            onClick={() => setActiveTab('erkek')}
            className={`flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg font-medium text-xs md:text-sm transition-all flex-1 ${
              activeTab === 'erkek' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
            }`}
          >
            <Users className="w-4 h-4" /> Erkek Öğrenciler ({students.filter((s) => s.gender === 'Erkek').length})
          </button>
          <button
            onClick={() => setActiveTab('kiz')}
            className={`flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg font-medium text-xs md:text-sm transition-all flex-1 ${
              activeTab === 'kiz' ? 'bg-white text-pink-600 shadow-sm' : 'text-gray-600'
            }`}
          >
            <Users className="w-4 h-4" /> Kız Öğrenciler ({students.filter((s) => s.gender === 'Kız').length})
          </button>
          <button
            onClick={() => setActiveTab('belletmens')}
            className={`flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg font-medium text-xs md:text-sm transition-all flex-1 ${
              activeTab === 'belletmens' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-600'
            }`}
          >
            <Shield className="w-4 h-4" /> Belletmenler ({belletmens.length})
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg font-medium text-xs md:text-sm transition-all flex-1 ${
              activeTab === 'security' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-600'
            }`}
          >
            <Activity className="w-4 h-4" /> Güvenlik
          </button>
        </div>
      </div>

      {uploadSuccess && (
        <div className="flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 p-3 rounded-xl text-xs md:text-sm">
          <CheckCircle className="w-5 h-5 shrink-0" /> {uploadSuccess}
        </div>
      )}

      {/* Arama ve Excel Yükleme Çubuğu */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="İsim, T.C., oda numarası veya işlem ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
        </div>

        {activeTab === 'belletmens' && (
          <label className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-medium text-xs md:text-sm cursor-pointer shadow-sm transition-all w-full sm:w-auto whitespace-nowrap">
            <FileSpreadsheet className="w-4 h-4" /> Excel ile Öğretmen Yükle
            <input type="file" accept=".xlsx, .xls" onChange={handleTeacherExcelUpload} className="hidden" />
          </label>
        )}

        {(activeTab === 'erkek' || activeTab === 'kiz') && (
          <label className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium text-xs md:text-sm cursor-pointer shadow-sm transition-all w-full sm:w-auto whitespace-nowrap">
            <FileSpreadsheet className="w-4 h-4" /> Excel ile Öğrenci Yükle
            <input type="file" accept=".xlsx, .xls" onChange={handleStudentExcelUpload} className="hidden" />
          </label>
        )}
      </div>

      {/* Sekme İçerikleri */}
      {activeTab === 'security' ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-4 bg-gray-900 text-white flex justify-between items-center">
            <div className="flex items-center gap-2 font-semibold text-sm">
              <Lock className="w-4 h-4 text-red-400" />
              Güvenlik ve Sistem Denetim Günlüğü (Kim Ne Değişiklik Yaptı)
            </div>
            <span className="text-xs bg-gray-800 text-gray-300 px-2.5 py-0.5 rounded-full">
              {auditLogs.length} Kayıt
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[550px]">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase">
                  <th className="py-3 px-4">Kullanıcı</th>
                  <th className="py-3 px-4">Rol</th>
                  <th className="py-3 px-4">Yapılan Değişiklik</th>
                  <th className="py-3 px-4">IP Adresi</th>
                  <th className="py-3 px-4">Tarih / Saat</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-xs md:text-sm">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50/50">
                    <td className="py-3 px-4 font-semibold text-gray-900">{log.user}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{log.role}</span>
                    </td>
                    <td className="py-3 px-4 text-gray-700">{log.action}</td>
                    <td className="py-3 px-4 text-gray-500 font-mono text-xs flex items-center gap-1">
                      <Globe className="w-3.5 h-3.5 text-gray-400" /> {log.ip}
                    </td>
                    <td className="py-3 px-4 text-gray-500 text-xs">{log.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : activeTab === 'belletmens' ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[450px]">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase">
                  <th className="py-3 px-4">Belletmen Öğretmen Adı</th>
                  <th className="py-3 px-4">Telefon</th>
                  <th className="py-3 px-4">Nöbet Günleri</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-xs md:text-sm">
                {filteredBelletmens.map((belletmen) => (
                  <tr key={belletmen.id} className="hover:bg-gray-50/50">
                    <td className="py-3 px-4 font-medium text-gray-900">{belletmen.name}</td>
                    <td className="py-3 px-4 text-gray-600">{belletmen.phone}</td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {belletmen.dutyDays.map((d, i) => (
                          <span key={i} className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs font-medium">
                            {d}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {Object.keys(groupedByRoom).length > 0 ? (
            Object.entries(groupedByRoom).map(([roomNo, roomStudents]) => (
              <div key={roomNo} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="bg-gray-900 text-white px-4 md:px-6 py-3 flex justify-between items-center">
                  <div className="flex items-center gap-2 font-semibold text-sm md:text-base">
                    <Home className="w-4 h-4 text-blue-400" />
                    Oda No: {roomNo} ({activeTab === 'erkek' ? 'Erkek Pansiyonu' : 'Kız Pansiyonu'})
                  </div>
                  <span className="text-xs bg-gray-800 text-gray-300 px-2.5 py-0.5 rounded-full">
                    {roomStudents.length} Öğrenci
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 p-4 bg-gray-50/50">
                  {roomStudents.map((student) => (
                    <div
                      key={student.id}
                      className="bg-white p-3.5 rounded-xl border border-gray-200/80 shadow-sm flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex justify-between items-start mb-1.5">
                          <span className="font-semibold text-gray-900 text-sm">{student.name}</span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                              student.status === 'Var'
                                ? 'bg-green-50 text-green-700'
                                : student.status === 'Yok'
                                ? 'bg-red-50 text-red-700'
                                : 'bg-amber-50 text-amber-700'
                            }`}
                          >
                            {student.status}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500">T.C.: {student.tc}</p>
                        <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                          <Bed className="w-3.5 h-3.5 text-gray-400" /> Yatak: {student.bed}
                        </p>
                      </div>
                      <div className="mt-3 pt-2 border-t border-gray-100 text-xs text-gray-600 flex items-center gap-1">
                        <Phone className="w-3.5 h-3.5 text-gray-400" /> Veli: {student.parentPhone}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="bg-white rounded-2xl p-8 text-center text-gray-400 shadow-sm border border-gray-100 text-sm">
              Bu kategoride kayıtlı öğrenci bulunamadı.
            </div>
          )}
        </div>
      )}
    </div>
  );
}