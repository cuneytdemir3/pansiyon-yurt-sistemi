// app/belletmen/page.tsx
'use client';

import React, { useState } from 'react';
import { CheckCircle, Send, FileText, Home, Printer, X, LogOut } from 'lucide-react';

interface Student {
  id: string;
  name: string;
  tc: string;
  floor: number;
  room: number;
  bed: string;
  status: 'Var' | 'Yok' | 'İzinli';
  motherPhone: string;
  fatherPhone: string;
}

const EXCLUDED_ROOMS = [107, 207, 307];

export default function BelletmenPage() {
  const [selectedFloor, setSelectedFloor] = useState<number>(1);
  const [selectedSession, setSelectedSession] = useState<'etut' | 'yat'>('etut');
  const [isReportModalOpen, setIsReportModalOpen] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [incidentNotes, setIncidentNotes] = useState<string>(
    'Katta herhangi bir disiplin veya asayiş sorunu yaşanmamıştır. Yoklama zamanında tamamlanmıştır.'
  );

  const handleLogout = () => {
    document.cookie = 'token=; Max-Age=0; path=/;';
    localStorage.removeItem('token');
    sessionStorage.clear();
    window.location.href = '/';
  };

  const getRoomsForFloor = (floor: number) => {
    const start = floor * 100 + 1;
    const end = floor * 100 + 15;
    return Array.from({ length: end - start + 1 }, (_, i) => start + i).filter(
      (room) => !EXCLUDED_ROOMS.includes(room)
    );
  };

  const [students, setStudents] = useState<Student[]>([
    { id: '1', name: 'Ahmet Yılmaz', tc: '12345678901', floor: 1, room: 101, bed: 'A', status: 'Var', motherPhone: '05551112233', fatherPhone: '05551112244' },
    { id: '2', name: 'Mehmet Demir', tc: '12345678902', floor: 1, room: 101, bed: 'B', status: 'İzinli', motherPhone: '05552223333', fatherPhone: '05552223344' },
    { id: '3', name: 'Canberk Öztürk', tc: '12345678905', floor: 1, room: 102, bed: 'A', status: 'Var', motherPhone: '05556667777', fatherPhone: '05556667788' },
    { id: '4', name: 'Mustafa Şahin', tc: '12345678906', floor: 2, room: 201, bed: 'A', status: 'Yok', motherPhone: '05557778888', fatherPhone: '05557778899' },
    { id: '5', name: 'Emre Kaya', tc: '12345678907', floor: 3, room: 301, bed: 'A', status: 'Var', motherPhone: '05558889900', fatherPhone: '05558889911' },
  ]);

  const handleStatusChange = (studentId: string, newStatus: 'Var' | 'Yok') => {
    setStudents((prev) =>
      prev.map((s) => {
        if (s.id === studentId && s.status !== 'İzinli') {
          return { ...s, status: newStatus };
        }
        return s;
      })
    );
  };

  const handleMarkAllPresent = () => {
    setStudents((prev) =>
      prev.map((s) => {
        if (s.floor !== selectedFloor) return s;
        return {
          ...s,
          status: s.status === 'İzinli' ? 'İzinli' : 'Var',
        };
      })
    );
    setSuccessMessage(`${selectedFloor}. kattaki tüm öğrenciler (izinliler hariç) "Var" olarak işaretlendi.`);
    setTimeout(() => setSuccessMessage(''), 4000);
  };

  const handleWhatsAppAlert = (student: Student, parentType: 'Anne' | 'Baba', phone: string) => {
    const sessionTitle =
      selectedSession === 'etut' ? 'Akşam Etüt Yoklaması (19:15)' : 'Gece Yat Yoklaması (23:00)';

    const message =
      `Sayın Veli (${parentType}),\n\n` +
      `Öğrencimiz: *${student.name}*\n` +
      `Oda Numarası: *${student.room}*\n` +
      `Yoklama: *${sessionTitle}*\n\n` +
      `Yukarıda belirtilen yoklamada öğrencimiz mazeretsiz olarak *YOK* yazılmıştır. Bilgilerinize sunar, gereğini rica ederiz.\n\n` +
      `*Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi İdaresi*`;

    const cleanPhone = phone.replace(/\D/g, '');
    const formattedPhone = cleanPhone.startsWith('0') ? `9${cleanPhone}` : `90${cleanPhone}`;
    const url = `https://wa.me/${formattedPhone}?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank');
  };

  const currentFloorRooms = getRoomsForFloor(selectedFloor);
  const floorStudents = students.filter((s) => s.floor === selectedFloor);

  const totalCount = floorStudents.length;
  const presentCount = floorStudents.filter((s) => s.status === 'Var').length;
  const absentCount = floorStudents.filter((s) => s.status === 'Yok').length;
  const leaveCount = floorStudents.filter((s) => s.status === 'İzinli').length;

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto space-y-5 bg-gray-50 min-h-screen">
      {/* Üst Başlık ve Çıkış Butonu */}
      <div className="flex flex-col gap-4 bg-white p-4 md:p-6 rounded-2xl shadow-sm border border-gray-100">
        <div className="flex flex-wrap justify-between items-center gap-3 border-b border-gray-100 pb-4">
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-gray-800">Nöbetçi Belletmen Yoklama Paneli</h1>
            <p className="text-xs md:text-sm text-gray-500">
              Etüt (19:15) ve Yat Yoklaması (23:00) • 107, 207 ve 307 nolu depo odaları hariç tutulmuştur
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition-all shadow-sm"
          >
            <LogOut className="w-4 h-4" /> Çıkış Yap
          </button>
        </div>

        <div className="flex flex-wrap justify-between items-center gap-2">
          <div className="flex bg-gray-100 p-1 rounded-xl w-full sm:w-auto">
            <button
              onClick={() => setSelectedSession('etut')}
              className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                selectedSession === 'etut' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
              }`}
            >
              Etüt Yoklaması (19:15)
            </button>
            <button
              onClick={() => setSelectedSession('yat')}
              className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                selectedSession === 'yat' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-600'
              }`}
            >
              Yat Yoklaması (23:00)
            </button>
          </div>

          <button
            onClick={() => setIsReportModalOpen(true)}
            className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-xl text-xs md:text-sm font-medium shadow-sm transition-all w-full sm:w-auto"
          >
            <FileText className="w-4 h-4" /> Resmî Nöbet Defteri
          </button>
        </div>
      </div>

      {successMessage && (
        <div className="flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 p-3 rounded-xl text-xs md:text-sm">
          <CheckCircle className="w-5 h-5 shrink-0" /> {successMessage}
        </div>
      )}

      {/* Kat Seçimi ve Tümünü Var Yap */}
      <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
        <div className="flex gap-2">
          {[1, 2, 3].map((floor) => (
            <button
              key={floor}
              onClick={() => setSelectedFloor(floor)}
              className={`flex-1 sm:flex-none px-5 py-2.5 rounded-xl font-medium text-xs md:text-sm transition-all ${
                selectedFloor === floor
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {floor}. Kat
            </button>
          ))}
        </div>
        <button
          onClick={handleMarkAllPresent}
          className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl text-xs md:text-sm font-medium shadow-sm transition-all"
        >
          <CheckCircle className="w-4 h-4" /> Tümünü Var Yap
        </button>
      </div>

      {/* Kat Özeti */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs text-gray-500">Kat Mevcudu</p>
          <p className="text-xl font-bold text-gray-800">{totalCount}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-xl border border-green-100 shadow-sm">
          <p className="text-xs text-green-600">Var</p>
          <p className="text-xl font-bold text-green-700">{presentCount}</p>
        </div>
        <div className="bg-red-50 p-4 rounded-xl border border-red-100 shadow-sm">
          <p className="text-xs text-red-600">Yok</p>
          <p className="text-xl font-bold text-red-700">{absentCount}</p>
        </div>
        <div className="bg-amber-50 p-4 rounded-xl border border-amber-100 shadow-sm">
          <p className="text-xs text-amber-600">Veli İzinli (Otomatik)</p>
          <p className="text-xl font-bold text-amber-700">{leaveCount}</p>
        </div>
      </div>

      {/* Odalar ve Öğrenciler */}
      <div className="space-y-4">
        {currentFloorRooms.map((roomNum) => {
          const roomStudents = floorStudents.filter((s) => s.room === roomNum);
          if (roomStudents.length === 0) return null;

          return (
            <div key={roomNum} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="bg-gray-900 text-white px-4 md:px-6 py-3 flex justify-between items-center">
                <div className="flex items-center gap-2 font-semibold text-sm md:text-base">
                  <Home className="w-4 h-4 text-blue-400" />
                  Oda No: {roomNum}
                </div>
                <span className="text-xs bg-gray-800 text-gray-300 px-2.5 py-0.5 rounded-full">
                  {roomStudents.length} Öğrenci
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-4 md:p-6 bg-gray-50/50">
                {roomStudents.map((student) => (
                  <div
                    key={student.id}
                    className="bg-white p-4 rounded-xl border border-gray-200/80 shadow-sm flex flex-col justify-between gap-3"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="font-semibold text-gray-900 text-sm md:text-base">{student.name}</span>
                        <p className="text-xs text-gray-500 mt-0.5">
                          Oda: {student.room} | Yatak: {student.bed} | T.C.: {student.tc}
                        </p>
                      </div>
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
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

                    <div className="flex flex-col gap-2 pt-3 border-t border-gray-100">
                      {student.status === 'İzinli' ? (
                        <span className="text-xs text-amber-700 bg-amber-50 px-3 py-1.5 rounded-lg font-medium">
                          Veli izin talebi gönderdiği için öğrenci otomatik İzinli sayılmıştır.
                        </span>
                      ) : (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleStatusChange(student.id, 'Var')}