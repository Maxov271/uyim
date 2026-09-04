/**
 * Local app state — favorites/compare ids and theme preference, mirroring what
 * frontend/assets/js/ui.js keeps in localStorage. Persisted via AsyncStorage so it survives
 * app restarts; add `@react-native-async-storage/async-storage` and `zustand/middleware`'s
 * `persist` when wiring this into the real Expo project.
 */
import { create } from 'zustand';

interface AppState {
  favoriteIds: string[];
  compareIds: string[];
  theme: 'light' | 'dark' | 'system';
  toggleFavorite: (id: string) => void;
  toggleCompare: (id: string) => void;
  setTheme: (t: AppState['theme']) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  favoriteIds: [],
  compareIds: [],
  theme: 'system',
  toggleFavorite: (id) => {
    const has = get().favoriteIds.includes(id);
    set({ favoriteIds: has ? get().favoriteIds.filter((x) => x !== id) : [...get().favoriteIds, id] });
  },
  toggleCompare: (id) => {
    const { compareIds } = get();
    if (compareIds.includes(id)) {
      set({ compareIds: compareIds.filter((x) => x !== id) });
    } else if (compareIds.length < 4) {
      set({ compareIds: [...compareIds, id] });
    }
  },
  setTheme: (theme) => set({ theme }),
}));
