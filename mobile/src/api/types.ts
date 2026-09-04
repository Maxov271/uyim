/** Mirrors backend/apps/listings/serializers.py ListingCardSerializer output exactly. */
export interface Listing {
  id: number;
  deal: 'sale' | 'new' | 'rent' | 'daily' | 'commercial' | 'land';
  type: string;
  price: number;
  rooms: number;
  area: number;
  floor: number;
  floors: number;
  district: string;
  mahalla: string;
  city: string;
  lat: number;
  lng: number;
  photos: number | { id: number; url: string; order: number; is_cover: boolean }[];
  year: number | null;
  condition: string;
  agent: string;
  verified: boolean;
  top: boolean;
  hot: boolean;
  isNew: boolean;
  tg: boolean;
  metro: string;
  metroMin: number | null;
  mortgage: boolean;
  created: string;
  views: number;
  priceHistory: { m: string; v: number }[];
  features: string[];
  desc: string;
}

export interface City { id: string; name: string; center: [number, number]; zoom: number }
export interface District {
  id: string; city: string; name: string; center: [number, number]; ppm: number; mahallas: string[];
}
export interface Bank { id: string; name: string; rate: number; minDown: number; maxTerm: number; note: string }
export interface Agent {
  id: string; name: string; type: 'agency' | 'owner'; verified: boolean; years: number;
  listings: number; rating: number; phone: string; tg: string;
}

export interface MortgageCalcResult {
  down: number; loan: number; monthly: number; total: number; interest: number; incomeNeeded: number;
}

export interface Me {
  id: number; phone: string; name: string; role: string; city: string | null;
  telegram_id: number | null; verified_phone: boolean; notify_telegram: boolean; notify_push: boolean;
}

export interface ListingsResponse {
  items: Listing[]; total: number; page: number; limit: number;
  bbox: { south: number; west: number; north: number; east: number } | null;
  clusters: { lat: number; lng: number; count: number }[];
}
