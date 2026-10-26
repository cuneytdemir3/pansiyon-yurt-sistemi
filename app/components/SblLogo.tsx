"use client";
import React from 'react';

interface SblLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
}

export default function SblLogo({ size = 'md', showText = true, className = '' }: SblLogoProps) {
  const iconSizes = {
    sm: 'w-9 h-9',
    md: 'w-12 h-12',
    lg: 'w-20 h-20',
    xl: 'w-28 h-28'
  };

  return (
    <div className={`inline-flex items-center gap-3 select-none ${className}`}>
      {/* SBL Mavi Lale ve Yaprak Vektörü (#006bb6) */}
      <div className={`${iconSizes[size]} relative flex-shrink-0 flex items-center justify-center`}>
        <svg viewBox="0 0 220 240" className="w-full h-full drop-shadow-sm" fill="none" xmlns="http://www.w3.org/2000/svg">
          {/* Sol Lale Taç Yaprağı */}
          <path
            d="M66 15 C64 65, 62 110, 102 128 C118 96, 108 48, 66 15 Z"
            fill="#006bb6"
          />
          {/* Sağ Lale Taç Yaprağı */}
          <path
            d="M156 15 C115 48, 105 96, 114 128 C154 112, 160 68, 156 15 Z"
            fill="#006bb6"
          />
          {/* Alt Sol Kıvrımlı Yaprak */}
          <path
            d="M12 88 C28 134, 65 132, 92 178 C98 134, 64 95, 12 88 Z"
            fill="#006bb6"
          />
          {/* Minimalist SBL Tipografi İmzası */}
          <text
            x="104"
            y="188"
            fill="#006bb6"
            fontFamily="Impact, Arial Black, sans-serif"
            fontWeight="900"
            fontSize="58"
            letterSpacing="1"
          >
            SBL
          </text>
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col leading-tight text-left">
          <span className="text-[11px] font-extrabold tracking-wide text-[#006bb6] uppercase">
            Prof. Dr. Mümtaz Turhan
          </span>
          <span className="text-base md:text-lg font-black tracking-tight text-slate-900">
            SOSYAL BİLİMLER LİSESİ
          </span>
          <span className="text-[10px] font-semibold text-slate-500">
            Pansiyon & Yurt Yönetim Portalı
          </span>
        </div>
      )}
    </div>
  );
}