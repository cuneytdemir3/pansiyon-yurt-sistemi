// components/YoneticiModule.tsx
'use client';

import React, { useState } from 'react';
import { Users, Shield, Search, Bed, Phone, Home, FileSpreadsheet, CheckCircle, Activity, Lock, Globe } from 'lucide-react';
import * as XLSX from 'xlsx';

interface Student {
  id: string;
  name: string;
  tc: string;
  gender: 'Erkek' | 'Kız';
  room: number;
  bed: string;
  status: 'Yurtta' | 'İzinli' | 'Etütte' | 'Revirde';
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

export default function YoneticiModule() {
  const [activeTab, setActiveTab] = useState<'erkek' | 'kiz' | 'belletmens' | 'security'>('erkek');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');

  const [students] = useState<Student[]>([
    { id: '1', name: 'Ahmet Yılmaz', tc: '12345678901', gender: 'Erkek', room: 101, bed: 'A', status: 'Yurtta', parentPhone: '05551112233' },
    { id: '2', name: 'Mehmet Demir', tc: '12345678902', gender: 'Erkek', room: 101, bed: 'B', status: 'İzinli', parentPhone: '05552223344' },
    { id: '3', name: 'Canberk Öztürk', tc: '12345678905', gender: 'Erkek', room: 102, bed: 'A', status: 'Etütte', parentPhone: '05556667788' },
    { id: '4', name: 'Ayşe Kaya', tc: '12345678903', gender: 'Kız', room: 201, bed: 'A', status: 'Etütte', parentPhone: '05553334455' },
    { id: '5', name: 'Zeynep Çelik', tc: '12345678904', gender: 'Kız', room: 201, bed: 'B', status: 'Yurtta', parentPhone: '05554445566' },
  ]);

  const [belletmens, setBelletmens] = useState<Belletmen[]>([
    { id: '1', name: 'Ali Çelik (Matematik)', phone: '05324445566', dutyDays: ['Pazartesi', 'Perşembe'] },
    { id: '2', name: 'Fatma Şahin (Türk Dili)', phone: '05335556677', dutyDays: ['Salı', 'Cuma'] },
  ]);

  const [auditLogs] = useState<AuditLog[]>([
    { id: '1', user: 'Ali Çelik', role: 'Belletmen', action: 'Akşam etüt yoklaması alındı', ip: '192.168.1.45', timestamp: '11.10.2026 - 19:18' },
    { id: '2', user: 'Ahmet Yılmaz (Veli)', role: 'Veli', action: 'Ev izni talebi oluşturuldu ve onaylandı', ip: '88.235.12.5', timestamp: '11.10.2026 - 17:42' },
  ]);

  const handleExcelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const bstr = evt.target?.result;
        const workbook = XLSX.read(bstr, { type: 'binary' });
        const wsname = workbook.SheetNames[0];
        const ws = workbook.Sheets[wsname];
        const data = XLSX.utils.sheet_to_json<any>(ws);

        const newBelletmens: Belletmen[] = data.map((row, index) => ({
          id: `excel-${Date.now()}-${index}`,
          name: row['Ad Soyad'] || row['Adı Soyadı'] || 'İsimsiz',
          phone: row['Telefon'] || row['Tel'] || 'Belirtilmemiş',
          dutyDays: row['Nöbet Günleri'] ? row['Nöbet Günleri'].split(',').map((d: string) => d.trim()) : ['Pazartesi']
        }));

        setBelletmens(prev => [...prev, ...newBelletmens]);
        setUploadSuccess(`Başarıyla ${newBelletmens.length} belletmen eklendi!`);
        setTimeout(() => setUploadSuccess(''), 5000);
      } catch (error) {
        alert('Excel okunurken hata oluştu.');
      }
    };
    reader.readAsBinaryString(file);
  };

  const filteredStudents = students.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
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

  const filteredBelletmens = belletmens.filter(b => 
    b.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    b.phone.includes(searchTerm)
  );

  const filteredLogs = auditLogs.filter(l => 
    l.user.toLowerCase().includes(searchTerm.toLowerCase()) || 
    l.action.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto space-y-4 md:space-y-6 bg-gray-50 min-h-screen">
      {/* Üst Başlık ve Sekmeler (Mobilde alt alta, masaüstünde yan yana) */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 bg-white p-4 md:p-6 rounded-2xl shadow-sm border border-gray-100">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-gray-800">Yönetici Paneli</h1>
          <p className="text-xs md:text-sm text-gray-500">Pansiyon kütüğü, oda yerleşimleri ve güvenlik denetimleri.</p>
        </div>
        <div className="grid grid-cols-2 sm:flex flex-wrap bg-gray-100 p-1 rounded-xl gap-1 w-full lg:w-auto">
          <button 
            onClick={() => setActiveTab('erkek')}
            className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg font-medium text-xs md:text-sm transition-all ${activeTab === 'erkek' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
          >
            <Users className="w-4 h-4" /> Erkek ({students.filter(s => s.gender === 'Erkek').length})
          </button>
          <button 
            onClick={() => setActiveTab('kiz')}
            className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg font-medium text-xs md:text-sm transition-all ${activeTab === 'kiz' ? 'bg-white text-pink-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
          >
            <Users className="w-4 h-4" /> Kız ({students.filter(s => s.gender === 'Kız').length})
          </button>
          <button 
            onClick={() => setActiveTab('belletmens')}
            className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg font-medium text-xs md:text-sm transition-all ${activeTab === 'belletmens' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
          >
            <Shield className="w-4 h-4" /> Belletmen ({belletmens.length})
          </button>
          <button 
            onClick={() => setActiveTab('security')}
            className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg font-medium text-xs md:text-sm transition-all ${activeTab === 'security' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
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

      {/* Arama ve Excel Butonu */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4 md:w-5 md:h-5" />
          <input 
            type="text"
            placeholder="Arama yapın..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 md:py-3 bg-white border border-gray-200 rounded-xl text-xs md:text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
        </div>

        {activeTab === 'belletmens' && (
          <label className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 md:py-3 rounded-xl font-medium text-xs md:text-sm cursor-pointer shadow-sm transition-all w-full sm:w-auto whitespace-nowrap">
            <FileSpreadsheet className="w-4 h-4 md:w-5 md:h-5" /> Excel ile Belletmen Yükle
            <input type="file" accept=".xlsx, .xls" onChange={handleExcelUpload} className="hidden" />
          </label>
        )}
      </div>

      {/* İçerik Alanı */}
      {activeTab === 'security' ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-4 md:p-6 bg-gray-900 text-white flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
            <div className="flex items-center gap-2 font-semibold text-sm md:text-base">
              <Lock className="w-5 h-5 text-red-400 shrink-0" />
              Sistem Denetim ve Güvenlik Günlüğü
            </div>
            <span className="text-xs bg-gray-800 text-gray-300 px-3 py-1 rounded-full">
              {auditLogs.length} Kayıt
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[600px]">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase">
                  <th className="py-3 px-4 md:px-6">Kullanıcı</th>
                  <th className="py-3 px-4 md:px-6">Rol</th>
                  <th className="py-3 px-4 md:px-6">İşlem</th>
                  <th className="py-3 px-4 md:px-6">IP Adresi</th>
                  <th className="py-3 px-4 md:px-6">Zaman</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-xs md:text-sm">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50/50">
                    <td className="py-3 px-4 md:px-6 font-medium text-gray-900">{log.user}</td>
                    <td className="py-3 px-4 md:px-6"><span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{log.role}</span></td>
                    <td className="py-3 px-4 md:px-6 text-gray-700">{log.action}</td>
                    <td className="py-3 px-4 md:px-6 text-gray-500 font-mono text-xs">{log.ip}</td>
                    <td className="py-3 px-4 md:px-6 text-gray-500 text-xs">{log.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : activeTab === 'belletmens' ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[500px]">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase">
                  <th className="py-3 px-4 md:px-6">Belletmen Öğretmen</th>
                  <th className="py-3 px-4 md:px-6">Telefon</th>
                  <th className="py-3 px-4 md:px-6">Nöbet Günleri</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 text-xs md:text-sm">
                {filteredBelletmens.map((belletmen) => (
                  <tr key={belletmen.id} className="hover:bg-gray-50/50">
                    <td className="py-3 px-4 md:px-6 font-medium text-gray-900">{belletmen.name}</td>
                    <td className="py-3 px-4 md:px-6 text-gray-600">{belletmen.phone}</td>
                    <td className="py-3 px-4 md:px-6">
                      <div className="flex flex-wrap gap-1">
                        {belletmen.dutyDays.map((d, i) => (
                          <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">{d}</span>
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
        <div className="space-y-4 md:space-y-6">
          {Object.keys(groupedByRoom).length > 0 ? (
            Object.entries(groupedByRoom).map(([roomNo, roomStudents]) => (
              <div key={roomNo} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="bg-gray-900 text-white px-4 md:px-6 py-3 flex justify-between items-center">
                  <div className="flex items-center gap-2 font-semibold text-sm md:text-base">
                    <Home className="w-4 h-4 md:w-5 md:h-5 text-blue-400" />
                    Oda No: {roomNo}
                  </div>
                  <span className="text-xs bg-gray-800 text-gray-300 px-2.5 py-0.5 rounded-full">
                    {roomStudents.length} Öğrenci
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4 p-4 md:p-6 bg-gray-50/50">
                  {roomStudents.map((student) => (
                    <div key={student.id} className="bg-white p-3.5 md:p-4 rounded-xl border border-gray-200/80 shadow-sm flex flex-col justify-between">
                      <div>
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-semibold text-gray-900 text-sm">{student.name}</span>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] md:text-xs font-medium ${
                            student.status === 'Yurtta' ? 'bg-green-50 text-green-700' :
                            student.status === 'İzinli' ? 'bg-amber-50 text-amber-700' : 'bg-blue-50 text-blue-700'
                          }`}>
                            {student.status}
                          </span>
                        </div>
                        <p className="text-[11px] md:text-xs text-gray-500 mb-1">T.C.: {student.tc}</p>
                        <p className="text-[11px] md:text-xs text-gray-500 flex items-center gap-1">
                          <Bed className="w-3 h-3 text-gray-400" /> Yatak: {student.bed}
                        </p>
                      </div>
                      <div className="mt-3 pt-2.5 border-t border-gray-100 text-[11px] md:text-xs text-gray-600">
                        <span className="flex items-center gap-1">
                          <Phone className="w-3 h-3 text-gray-400" /> {student.parentPhone}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="bg-white rounded-2xl p-8 md:p-12 text-center text-gray-400 shadow-sm border border-gray-100 text-sm">
              Bu kategoride kayıtlı öğrenci bulunamadı.
            </div>
          )}
        </div>
      )}
    </div>
  );
}