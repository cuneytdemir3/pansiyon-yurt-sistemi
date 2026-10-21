'use client';

import React from 'react';
import { Shield, Users, Phone, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-8 text-center">
        <div className="space-y-3">
          <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900">T.C. Millî Eğitim Bakanlığı</h1>
          <h2 className="text-xl md:text-2xl font-bold text-blue-600">Pansiyon ve Yurt Takip Sistemi</h2>
          <p className="text-sm md:text-base text-gray-600 max-w-xl mx-auto">Veli, belletmen ve yönetim platformu.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
          <Link href="/veli/login" className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:border-emerald-500 transition-all flex flex-col justify-between group text-left">
            <div className="space-y-3">
              <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center font-bold group-hover:bg-emerald-600 group-hover:text-white transition-all">
                <Phone className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Öğrenci Velisi Girişi</h3>
              <p className="text-xs text-gray-500">WhatsApp üzerinden tek kullanımlık kod ile şifresiz giriş ve izin yönetimi.</p>
            </div>
            <div className="mt-6 flex items-center gap-2 text-sm font-semibold text-emerald-600">
              Veli Portalı <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          <Link href="/belletmen" className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:border-blue-500 transition-all flex flex-col justify-between group text-left">
            <div className="space-y-3">
              <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center font-bold group-hover:bg-blue-600 group-hover:text-white transition-all">
                <Users className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Nöbetçi Belletmen</h3>
              <p className="text-xs text-gray-500">Etüt ve yat yoklamaları, WhatsApp veli bildirim köprüsü.</p>
            </div>
            <div className="mt-6 flex items-center gap-2 text-sm font-semibold text-blue-600">
              Yoklama Paneli <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>

          <Link href="/yonetici" className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:border-indigo-500 transition-all flex flex-col justify-between group text-left">
            <div className="space-y-3">
              <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center font-bold group-hover:bg-indigo-600 group-hover:text-white transition-all">
                <Shield className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Pansiyon Yöneticisi</h3>
              <p className="text-xs text-gray-500">Öğrenci kütüğü, oda yerleşimleri ve denetim günlüğü.</p>
            </div>
            <div className="mt-6 flex items-center gap-2 text-sm font-semibold text-indigo-600">
              Yönetici Paneli <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}