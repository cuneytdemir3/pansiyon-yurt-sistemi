// app/veli/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Bed, Calendar, CheckCircle, Clock, FileCheck, Home, LogOut, MapPin, Send, Truck, User } from 'lucide-react';

interface StudentOption {
  id: string;
  name: string;
  room: number;
  floor: number;
  bed: string;
}

interface LeaveRecord {
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
}

const STUDENTS: StudentOption[] = [
  { id: '1', name: 'Ahmet Yılmaz', floor: 1, room: 101, bed: 'A' },
  { id: '2', name: 'Mehmet Demir', floor: 1, room: 101, bed: 'B' },
  { id: '3', name: 'Canberk Öztürk', floor: 1, room: 102, bed: 'A' },
  { id: '4', name: 'Mustafa Şahin', floor: 2, room: 201, bed: 'A' },
  { id: '5', name: 'Emre Kaya', floor: 3, room: 301, bed: 'A' },
];

export default function VeliPage() {
  const todayStr = new Date().toISOString().split('T')[0];

  const [selectedStudentId, setSelectedStudentId] = useState<string>('1');
  const [leaveType, setLeaveType] = useState<'Ev İzni' | 'Etüt İzni'>('Ev İzni');
  const [startDate, setStartDate] = useState<string>(todayStr);
  const [endDate, setEndDate] = useState<string>(todayStr);
  const [transport, setTransport] = useState<string>('Veli teslim alacak');
  const [address, setAddress] = useState<string>('');
  const [reason, setReason] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [successMsg, setSuccessMsg] = useState<string>('');
  const [leaves, setLeaves] = useState<LeaveRecord[]>([]);

  const selectedStudent = STUDENTS.find((s) => s.id === selectedStudentId) || STUDENTS[0];

  // Mevcut izinleri yükle
  useEffect(() => {
    const loadLeaves = async () => {
      try {
        const res = await fetch('/api/leaves');
        const data = await res.json();
        const serverLeaves: LeaveRecord[] = data.leaves || [];
        const localRaw = localStorage.getItem('pansiyon_leaves');
        const localLeaves: LeaveRecord[] = localRaw ? JSON.parse(localRaw) : [];

        const mergedMap = new Map<string, LeaveRecord>();
        [...localLeaves, ...serverLeaves].forEach((item) => mergedMap.set(item.id, item));
        const merged = Array.from(mergedMap.values());
        setLeaves(merged);
        localStorage.setItem('pansiyon_leaves', JSON.stringify(merged));
      } catch {
        const localRaw = localStorage.getItem('pansiyon_leaves');
        if (localRaw) setLeaves(JSON.parse(localRaw));
      }
    };
    loadLeaves();
  }, []);

  const handleLogout = () => {
    document.cookie = 'token=; Max-Age=0; path=/;';
    localStorage.removeItem('token');
    sessionStorage.clear();
    window.location.href = '/';
  };

  // Gerekli tüm alanlar dolduruldu mu kontrolü
  const isFormValid =
    Boolean(startDate) &&
    Boolean(endDate) &&
    endDate >= startDate &&
    address.trim().length >= 3 &&
    reason.trim().length >= 3;

  // Öğrencinin bugün tarihli aktif bir izni var mı kontrolü
  const isStudentCurrentlyOnLeave = leaves.some(
    (l) => l.studentId === selectedStudent.id && todayStr >= l.startDate && todayStr <= l.endDate
  );

  const handleLeaveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid || isSubmitting) return;

    setIsSubmitting(true);

    const newLeave: LeaveRecord = {
      id: `leave-${Date.now()}`,
      studentId: selectedStudent.id,
      studentName: selectedStudent.name,
      leaveType,
      startDate,
      endDate,
      transport,
      address: address.trim(),
      reason: reason.trim(),
      status: 'onaylandi',
    };

    try {
      await fetch('/api/leaves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newLeave),
      });
    } catch {
      // Çevrimdışı durumda yerel kayıt ile devam et
    }

    const updatedLeaves = [newLeave, ...leaves];
    setLeaves(updatedLeaves);
    localStorage.setItem('pansiyon_leaves', JSON.stringify(updatedLeaves));

    setSuccessMsg(
      `${selectedStudent.name} için ${startDate} ile ${endDate} tarihleri arasındaki ${leaveType} talebiniz otomatik olarak onaylandı. Öğrenciniz bu tarihler arasında tüm yoklamalarda otomatik "İzinli" sayılacaktır.`
    );
    setAddress('');
    setReason('');
    setIsSubmitting(false);
    setTimeout(() => setSuccessMsg(''), 8000);
  };

  const studentLeaves = leaves.filter((l) => l.studentId === selectedStudent.id);

  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto space-y-6 bg-gray-50 min-h-screen">
      {/* Üst Başlık ve Çıkış Butonu */}
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white p-4 md:p-6 rounded-2xl shadow-sm border border-gray-100">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-gray-800">Öğrenci Velisi Portalı</h1>
          <p className="text-xs md:text-sm text-gray-500">
            Prof. Dr. Mümtaz Turhan Sosyal Bilimler Lisesi Pansiyonu • Anlık Durum ve İzin Yönetimi
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 px-4 py-2 rounded-xl text-xs md:text-sm font-semibold transition-all shadow-sm"
        >
          <LogOut className="w-4 h-4" /> Çıkış Yap
        </button>
      </div>

      {successMsg && (
        <div className="flex items-center gap-2 bg-green-50 border border-green-200 text-green-800 p-4 rounded-xl text-xs md:text-sm font-medium shadow-sm">
          <CheckCircle className="w-5 h-5 text-green-600 shrink-0" /> {successMsg}
        </div>
      )}

      {/* Öğrenci Seçimi ve Anlık Durum Kartı */}
      <div className="bg-white p-5 md:p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="space-y-2 w-full sm:w-auto">
          <label className="text-xs font-semibold text-blue-600 uppercase tracking-wider flex items-center gap-1">
            <User className="w-3.5 h-3.5" /> Öğrenci Seçimi
          </label>
          <select
            value={selectedStudentId}
            onChange={(e) => setSelectedStudentId(e.target.value)}
            className="w-full sm:w-72 p-2.5 border border-gray-200 rounded-xl font-bold text-gray-900 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {STUDENTS.map((st) => (
              <option key={st.id} value={st.id}>
                {st.name} (Oda {st.room})
              </option>
            ))}
          </select>
          <div className="flex flex-wrap items-center gap-3 text-xs md:text-sm text-gray-600 pt-1">
            <span className="flex items-center gap-1">
              <Home className="w-4 h-4 text-gray-400" /> {selectedStudent.floor}. Kat - Oda {selectedStudent.room}
            </span>
            <span className="flex items-center gap-1">
              <Bed className="w-4 h-4 text-gray-400" /> Yatak: {selectedStudent.bed}
            </span>
          </div>
        </div>

        <div className="flex flex-col items-start sm:items-end">
          <span className="text-xs text-gray-500 mb-1">Bugünkü Yoklama Durumu ({todayStr})</span>
          <span
            className={`px-4 py-1.5 rounded-full text-xs md:text-sm font-bold ${
              isStudentCurrentlyOnLeave ? 'bg-amber-100 text-amber-800' : 'bg-green-100 text-green-800'
            }`}
          >
            {isStudentCurrentlyOnLeave ? 'İzinli (Otomatik Onaylı)' : 'Yurtta (Var)'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* İzin Bildirim Formu */}
        <div className="bg-white p-5 md:p-6 rounded-2xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-100">
            <FileCheck className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-gray-800 text-base">İzin Bildirimi (Anında Otomatik Onay)</h3>
          </div>

          <form onSubmit={handleLeaveSubmit} className="space-y-4 text-xs md:text-sm">
            <div>
              <label className="block font-semibold text-gray-700 mb-1">İzin Türü</label>
              <div className="grid grid-cols-2 gap-2">
                {(['Ev İzni', 'Etüt İzni'] as const).map((type) => (
                  <button
                    type="button"
                    key={type}
                    onClick={() => setLeaveType(type)}
                    className={`py-2.5 rounded-xl font-semibold border transition-all ${
                      leaveType === type
                        ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                        : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">İzin Başlangıç Tarihi *</label>
                <input
                  type="date"
                  required
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full p-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block font-semibold text-gray-700 mb-1">İzin Bitiş Tarihi *</label>
                <input
                  type="date"
                  required
                  min={startDate}
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full p-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Ulaşım Biçimi *</label>
              <div className="relative">
                <Truck className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <select
                  value={transport}
                  onChange={(e) => setTransport(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Veli teslim alacak">Veli teslim alacak</option>
                  <option value="Kendi imkanlarıyla / Toplu taşıma">Kendi imkanlarıyla / Toplu taşıma</option>
                  <option value="Şehirlerarası Otobüs">Şehirlerarası Otobüs</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">İzinde Bulunacağı Adres *</label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  required
                  placeholder="İl / İlçe / Mahalle (En az 3 karakter)..."
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Mazeret / Açıklama *</label>
              <textarea
                rows={2}
                required
                placeholder="Hafta sonu ev izni, doktor randevusu vb. (En az 3 karakter)..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full p-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={!isFormValid || isSubmitting}
              className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold transition-all ${
                isFormValid
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-md cursor-pointer'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
              {isFormValid
                ? 'İzni Gönder ve Otomatik Onayla'
                : 'Lütfen Tüm Zorunlu Alanları Doldurun'}
            </button>
          </form>
        </div>

        {/* Aktif İzinler ve Yoklama Geçmişi */}
        <div className="bg-white p-5 md:p-6 rounded-2xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-100">
            <Clock className="w-5 h-5 text-indigo-600" />
            <h3 className="font-bold text-gray-800 text-base">Onaylı İzinler ve Yoklama Geçmişi</h3>
          </div>

          <div className="space-y-3">
            {studentLeaves.length > 0 ? (
              studentLeaves.map((item) => (
                <div
                  key={item.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-xl bg-amber-50/70 border border-amber-200 gap-2"
                >
                  <div>
                    <p className="font-bold text-gray-900 text-xs md:text-sm">
                      {item.leaveType} • {item.reason}
                    </p>
                    <p className="text-xs text-gray-600 flex items-center gap-1 mt-1">
                      <Calendar className="w-3.5 h-3.5 text-amber-600" />
                      Tarih Aralığı: <strong>{item.startDate}</strong> — <strong>{item.endDate}</strong>
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      Ulaşım: {item.transport} | Adres: {item.address}
                    </p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 self-start sm:self-center whitespace-nowrap">
                    İzinli (Onaylandı)
                  </span>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-gray-50 border border-gray-100 text-xs text-gray-500 text-center">
                Bu öğrenci için kayıtlı izin talebi bulunmamaktadır.
              </div>
            )}

            <div className="flex items-center justify-between p-3.5 rounded-xl bg-gray-50 border border-gray-100">
              <div>
                <p className="font-semibold text-gray-800 text-xs md:text-sm">Akşam Etüt Yoklaması (19:15)</p>
                <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                  <Calendar className="w-3.5 h-3.5" /> {todayStr}
                </p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  isStudentCurrentlyOnLeave ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                }`}
              >
                {isStudentCurrentlyOnLeave ? 'İzinli' : 'Var'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}