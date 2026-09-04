/**
 * Design tokens ported 1:1 from frontend/assets/css/app.css (:root and html[data-theme="dark"])
 * so the mobile app renders as the same visual system as the web frontend.
 */

export const radius = { sm: 10, lg: 16, pill: 999 };

export const font = {
  family: 'PlusJakartaSans', // load via expo-font: Plus Jakarta Sans 400/500/600/700/800
};

export const light = {
  navy: '#16324F', navy600: '#1B4067', navy700: '#0F2439',
  emerald: '#0F7A5C', emerald600: '#0C6A50', emeraldTint: '#E6F4EF',
  gold: '#C9822B', gold600: '#B0701F', goldTint: '#FBF1E2',
  blue: '#2F80ED', blueTint: '#E8F1FE',
  telegram: '#229ED9', telegramTint: '#E6F4FB',
  hot: '#D8503F', hotTint: '#FCEBE8',
  bg: '#F4F6F8', surface: '#FFFFFF', surface2: '#EDF1F5',
  ink: '#22282E', sub: '#6B7280', faint: '#9AA4B0',
  line: '#D9DEE3', lineSoft: '#E7EBEF',
  placeholder: '#E3E8ED',
};

export const dark = {
  ...light,
  bg: '#0F1720', surface: '#172231', surface2: '#1E2B3C',
  ink: '#E7ECF2', sub: '#94A3B8', faint: '#6F8098',
  line: '#253244', lineSoft: '#1F2C3D',
  navy: '#2A5C8A', navy600: '#356FA3', navy700: '#1D4363',
  emerald: '#17A97F', emeraldTint: '#12302A',
  gold: '#E0A050', goldTint: '#2E2418',
  blue: '#5A9CF5', blueTint: '#17273D',
  telegramTint: '#12293A', hotTint: '#33201D',
  placeholder: '#1E2B3C',
};

export type Theme = typeof light;
export const getTheme = (scheme: 'light' | 'dark' | null | undefined): Theme =>
  scheme === 'dark' ? dark : light;
