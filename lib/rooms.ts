// lib/rooms.ts
export const EXCLUDED_ROOMS = [107, 207, 307]; // Depo ve idari alanlar

export const HOSTEL_FLOORS = [
  {
    floor: 1,
    name: "1. Kat (Erkek Pansiyonu)",
    rooms: Array.from({ length: 15 }, (_, i) => 101 + i).filter(r => !EXCLUDED_ROOMS.includes(r))
  },
  {
    floor: 2,
    name: "2. Kat",
    rooms: Array.from({ length: 15 }, (_, i) => 201 + i).filter(r => !EXCLUDED_ROOMS.includes(r))
  },
  {
    floor: 3,
    name: "3. Kat",
    rooms: Array.from({ length: 15 }, (_, i) => 301 + i).filter(r => !EXCLUDED_ROOMS.includes(r))
  }
];