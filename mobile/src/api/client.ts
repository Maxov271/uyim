/**
 * API client for the Uyim.uz Django backend (../../backend) — same REST contract as
 * frontend/assets/js/api.js, rewritten as async/await TypeScript for React Native (no need
 * for the frontend's synchronous-XHR bootstrap trick; RN screens are async from the start).
 * Tokens are stored in expo-secure-store rather than localStorage.
 */
import * as SecureStore from 'expo-secure-store';

import type { Bank, City, District, Listing, ListingsResponse, Me, MortgageCalcResult } from './types';

const API_BASE = process.env.EXPO_PUBLIC_API_BASE ?? 'http://localhost:8000/api';

const KEYS = { access: 'uyim.token', refresh: 'uyim.refresh' } as const;

async function getAccess() { return SecureStore.getItemAsync(KEYS.access); }
async function getRefresh() { return SecureStore.getItemAsync(KEYS.refresh); }
async function setTokens(access?: string, refresh?: string) {
  if (access) await SecureStore.setItemAsync(KEYS.access, access);
  if (refresh) await SecureStore.setItemAsync(KEYS.refresh, refresh);
}
export async function clearTokens() {
  await SecureStore.deleteItemAsync(KEYS.access);
  await SecureStore.deleteItemAsync(KEYS.refresh);
}
export async function isAuthed() { return !!(await getAccess()); }

class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request<T>(
  method: string,
  path: string,
  opts: { body?: unknown; auth?: boolean; retry?: boolean; formData?: FormData } = {}
): Promise<T> {
  const { body, auth = false, retry = true, formData } = opts;
  const headers: Record<string, string> = {};
  if (!formData) headers['Content-Type'] = 'application/json';
  if (auth) {
    const token = await getAccess();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const resp = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: formData ?? (body !== undefined ? JSON.stringify(body) : undefined),
  });

  if (resp.status === 401 && auth && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return request<T>(method, path, { ...opts, retry: false });
  }

  if (resp.status === 204) return null as T;
  const data = await resp.json().catch(() => null);
  if (!resp.ok) {
    const message = (data && (data.message_uz ?? data.detail)) ?? `HTTP ${resp.status}`;
    throw new ApiError(message, resp.status, data);
  }
  return data as T;
}

async function refreshAccessToken(): Promise<boolean> {
  const refresh = await getRefresh();
  if (!refresh) return false;
  try {
    const resp = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!resp.ok) { await clearTokens(); return false; }
    const data = await resp.json();
    await setTokens(data.access);
    return true;
  } catch {
    return false;
  }
}

export const api = {
  otpRequest: (phone: string) => request<{ phone: string; ttl: number; debug_code?: string }>(
    'POST', '/auth/otp/request', { body: { phone } }
  ),
  otpVerify: async (phone: string, code: string, role?: string) => {
    const res = await request<{ access: string; refresh: string; is_new: boolean; user: Me }>(
      'POST', '/auth/otp/verify', { body: { phone, code, role } }
    );
    await setTokens(res.access, res.refresh);
    return res;
  },
  logout: clearTokens,

  me: () => request<Me>('GET', '/me', { auth: true }),
  updateMe: (patch: Partial<Me>) => request<Me>('PATCH', '/me', { body: patch, auth: true }),

  cities: () => request<City[]>('GET', '/geo/cities'),
  districts: (city?: string) => request<District[]>('GET', `/geo/districts${city ? `?city=${city}` : ''}`),

  listings: (params: Record<string, string | number | undefined>) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined) as [string, string][]
    ).toString();
    return request<ListingsResponse>('GET', `/listings?${qs}`);
  },
  listing: (id: number) => request<Listing>('GET', `/listings/${id}`),
  createListing: (payload: Partial<Listing> & Record<string, unknown>) =>
    request<Listing>('POST', '/listings', { body: payload, auth: true }),
  uploadListingPhotos: async (id: number, uris: string[]) => {
    const form = new FormData();
    uris.forEach((uri, i) => {
      // @ts-expect-error React Native FormData accepts { uri, name, type } file objects.
      form.append('images', { uri, name: `photo-${i}.jpg`, type: 'image/jpeg' });
    });
    return request('POST', `/listings/${id}/photos`, { formData: form, auth: true });
  },
  boostListing: (id: number, pkg: string, provider = 'payme') =>
    request('POST', `/listings/${id}/boost`, { body: { package: pkg, provider }, auth: true }),
  sendLead: (id: number, channel: 'call' | 'chat' | 'telegram') =>
    request('POST', `/listings/${id}/lead`, { body: { channel } }),

  addFavorite: (listingId: number) => request('POST', '/favorites', { body: { listing: listingId }, auth: true }),
  removeFavorite: (listingId: number) => request('DELETE', `/favorites/${listingId}`, { auth: true }),
  favorites: () => request<Listing[]>('GET', '/favorites', { auth: true }),

  banks: () => request<Bank[]>('GET', '/banks'),
  mortgageCalc: (payload: { price: number; downPct: number; years: number; rate: number }) =>
    request<MortgageCalcResult>('POST', '/mortgage/calc', { body: payload }),
};
