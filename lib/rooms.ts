// Oda ve Kat Mimari Tanımları (MEB Pansiyon Standartları)
// 107, 207, 307 nolu odalar depo ve idari alan olduğu için sistemden hariç tutulmuştur.

export const EXCLUDED_ROOMS = [107, 207, 307];

export interface RoomInfo {
  roomNumber: number;
  floor: number;
  capacity: number;
  block: string;
}

export function getRoomsForFloor(floor: number): number[] {
  const rooms: number[] = [];
  const start = floor * 100 + 1;
  const end = floor * 100 + 15;
  for (let i = start; i <= end; i++) {
    if (!EXCLUDED_ROOMS.includes(i)) {
      rooms.push(i);
    }
  }
  return rooms;
}

export function getAllValidRooms(): { floor: number; room: number }[] {
  const all: { floor: number; room: number }[] = [];
  [1, 2, 3].forEach(floor => {
    getRoomsForFloor(floor).forEach(room => {
      all.push({ floor, room });
    });
  });
  return all;
}