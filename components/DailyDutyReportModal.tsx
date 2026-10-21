// components/DailyDutyReportModal.tsx
import React from 'react';
import { Printer, X } from 'lucide-react';

interface ReportProps {
  isOpen: boolean;
  onClose: () => void;
  dutyData: {
    date: string;
    belletmenName: string;
    totalStudents: number;
    presentCount: number;
    absentCount: number;
    leaveCount: number;
    infirmaryList: string[];
    incidentNotes: string;
  };
}

export default function DailyDutyReportModal({ isOpen, onClose, dutyData }: ReportProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full p-6 shadow-2xl print:shadow-none">
        <div className="flex justify-between items-center pb-4 border-b print:hidden">
          <h3 className="text-xl font-bold text-gray-800">MEB Resmî Nöbet Defteri ve Tutanak</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-full"><X className="w-6 h-6" /></button>
        </div>

        <div className="mt-4 space-y-4 print:text-black">
          <div className="text-center pb-2 border-b-2 border-gray-800">
            <h4 className="font-bold text-lg">T.C. MİLLÎ EĞİTİM BAKANLIĞI</h4>
            <p className="text-sm font-semibold">Pansiyon Günlük Nöbet ve Yoklama Raporu</p>
            <p className="text-xs text-gray-500">Tarih: {dutyData.date}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="font-semibold">Nöbetçi Belletmen:</span> {dutyData.belletmenName}</div>
            <div><span className="font-semibold">Toplam Öğrenci:</span> {dutyData.totalStudents}</div>
            <div><span className="font-semibold">Derse/Etüde Katılan:</span> {dutyData.presentCount}</div>
            <div><span className="font-semibold">Mazeretsiz Devamsız:</span> {dutyData.absentCount}</div>
            <div><span className="font-semibold">İzinli Öğrenci:</span> {dutyData.leaveCount}</div>
          </div>

          <div className="border-t pt-2">
            <h5 className="font-semibold text-sm mb-1">Revir Kayıtları:</h5>
            <ul className="list-disc list-inside text-xs text-gray-700">
              {dutyData.infirmaryList.length > 0 ? dutyData.infirmaryList.map((item, idx) => <li key={idx}>{item}</li>) : <li>Revire giden öğrenci bulunmamaktadır.</li>}
            </ul>
          </div>

          <div className="border-t pt-2">
            <h5 className="font-semibold text-sm mb-1">Vukuat ve Önemli Notlar:</h5>
            <p className="text-xs bg-gray-50 p-2 rounded border min-h-[50px]">{dutyData.incidentNotes || "Herhangi bir olay yaşanmamıştır."}</p>
          </div>

          <div className="grid grid-cols-2 pt-8 text-center text-sm">
            <div>
              <p className="font-semibold">Nöbetçi Belletmen Öğretmen</p>
              <p className="mt-12 border-t w-48 mx-auto pt-1">İmza</p>
            </div>
            <div>
              <p className="font-semibold">Pansiyondan Sorumlu Müdür Yardımcısı</p>
              <p className="mt-12 border-t w-48 mx-auto pt-1">Onay / İmza</p>
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3 print:hidden">
          <button onClick={() => window.print()} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Printer className="w-4 h-4" /> Yazdır / PDF Kaydet
          </button>
        </div>
      </div>
    </div>
  );
}