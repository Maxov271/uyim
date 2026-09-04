# Uyim.uz — Mobil ilova (Bosqich 2)

**Holat:** Backend (`../backend`) va frontend (`../frontend`) ishlaydi va production-ready API
bilan ulangan. Bu hujjat React Native/Expo mobil ilova uchun to'liq reja va boshlang'ich
skeleton (`../mobile`) — CLAUDE_CODE_PROMPT.md §8 asosida.

## Nega hozir emas, keyingi bosqichda

Backend API allaqachon mobil-tayyor (JWT auth, barcha CRUD/qidiruv/filtr endpointlari, geo,
ipoteka, Telegram, to'lov) — mobil ilova qo'shimcha backend ishi talab qilmaydi, faqat frontend
(React Native) ishi. Buni alohida bosqichda qilish to'g'ri, chunki: (1) real qurilma/simulyator
bu muhitda yo'q — yozilgan kodni ishga tushirib sinab bo'lmaydi; (2) Expo/React Native loyihasi
alohida repo tsikli (EAS build, App Store/Play Console hisoblari, push-sertifikatlar) talab
qiladi. Shuning uchun bu yerda: to'liq texnik reja + ishlaydigan API-client va dizayn-token
skeleton (`../mobile`) — keyingi sessiya to'g'ridan-to'g'ri ekranlarni yoza boshlashi mumkin.

## Texnologiya

| Qatlam | Tanlov | Izoh |
|---|---|---|
| Framework | **Expo (React Native) + TypeScript** | bitta kod bazasi — iOS + Android |
| Navigatsiya | **Expo Router** (file-based) | 5 ta tab: Asosiy, Xarita, Sevimli, Ipoteka, Kabinet |
| Server state | **TanStack Query** | keshlash, retry, offline-aware refetch — `/api/bootstrap` va `/api/listings` uchun mos |
| Local state | **Zustand** | fav/compare/tema — `AsyncStorage`ga yozib turadi (frontendning `localStorage` o'rnini bosadi) |
| Xarita | **react-native-maps** (OSM/Carto tiles, kalitsiz) | `frontend`dagi Leaflet bilan bir xil tile serverlar |
| Formalar | **react-hook-form + zod** | `add-listing` 6-qadamli sehrgar uchun |
| Auth saqlash | **expo-secure-store** | JWT access/refresh tokenlar (localStorage emas) |
| Push | **expo-notifications** (FCM/APNs) | saqlangan qidiruv + yangi lid push'lari — backend allaqachon buni Telegram orqali qiladi, mobil uchun xuddi shu event'larga push kanali qo'shiladi |
| Kamera/fayl | **expo-image-picker** | e'lon fotolarini `POST /api/listings/:id/photos`ga yuklash |

## Backend bilan bog'lanish — o'zgarishsiz

Mobil ilova **xuddi shu Django API**dan foydalanadi (`../backend`), boshqa hech narsa
qo'shilmaydi:

- Auth: `POST /api/auth/otp/request` → `/verify` → JWT (frontenddagi bilan bir xil oqim)
- Katalog: to'g'ridan-to'g'ri `GET /api/listings?...` (filtr/sahifalash bilan) — frontenddan
  farqli o'laroq, mobil ilova **bootstrap emas**, haqiqiy paginatsiyalangan endpointdan
  foydalanadi (ekranlar boshidanoq async-ga mo'ljallangan, frontenddagi kabi "hammasi bitta
  massivda" cheklovi yo'q)
- Qolgan hammasi (`/api/geo/*`, `/api/banks`, `/api/mortgage/*`, `/api/favorites`,
  `/api/saved-searches`, `/api/listings/:id/{boost,lead,photos}`, `/api/me`) — bir xil

`mobile/src/api/client.ts` shu kontraktga mos yozilgan (frontenddagi `api.js`ning TypeScript +
async/await versiyasi, sync XHR kerak emas — RN'da hammasi boshidanoq async).

## Dizayn tizimi

`frontend/assets/css/app.css`dagi barcha token (rang, radius, shrift) `mobile/src/theme/tokens.ts`
ga ko'chirildi — light/dark ikkalasi ham. Komponent kutubxonasi yo'q (NativeWind yoki
Tamagui keyinroq qo'shilishi mumkin) — boshlang'ich bosqichda oddiy `StyleSheet` + shared
`<Card>`, `<Button>`, `<Badge>`, `<PropertyCard>` primitives yetarli, chunki dizayn allaqachon
frontendda pishirilgan (bir xil komponentlarni RN'da qayta yaratish kifoya).

## Ekran xaritasi (§8 jadvali)

| Tab | Ekran | Frontend ekvivalenti |
|---|---|---|
| Asosiy | Qidiruv, tezkor filtr chiplari, TOP karusel, tuman statistikasi | `index.html` |
| Xarita | To'liq ekran xarita, narxli pinlar, klaster, radius (bosib ushlab turish), pastdan chiqadigan kartochka | `search.html` (xarita rejimi) |
| Sevimli | Sevimlilar + taqqoslash (gorizontal skroll) + saqlangan qidiruvlar | `dashboard-buyer.html`, `compare.html` |
| Ipoteka | Kalkulyator, bank tanlash, ariza | `calculator.html` |
| Kabinet | Profil, e'lonlarim, analitika, boost, sozlamalar | `dashboard-agent.html`, `auth.html` |

Qo'shimcha ekranlar (tab tashqarisida, stack navigatsiya bilan): `listing/[id]` (e'lon
sahifasi), `add-listing` (6 qadamli sehrgar), `new-buildings`, `auth` (OTP oqimi).

Modal/sheet'lar: filtrlar (bottom sheet — `@gorhom/bottom-sheet`), aloqa (call/Telegram/chat),
foto galereya (`react-native-image-viewing`), 360° tur (WebView + pannellum.js, frontend bilan
bir xil).

## Native imkoniyatlar

- `tel:` qo'ng'iroq → `Linking.openURL('tel:...')`
- Telegram deep link → `Linking.openURL('tg://resolve?domain=uyim_bot')`, fallback `https://t.me/uyim_bot`
- Push → `expo-notifications` + backend `telegram_id` o'rniga/qo'shimcha `push_token` maydoni
  (User modeliga qo'shiladi — kichik backend qo'shimchasi, 1 maydon + 1 endpoint)
- Geolokatsiya ("Menga yaqin") → `expo-location`, `GET /api/listings?lat=&lng=&radius=`ga uzatiladi
- Kamera → `expo-image-picker` → `POST /api/listings/:id/photos` (backend allaqachon tayyor)
- Biometrik kirish → `expo-local-authentication` (JWT refresh tokenni qulflash uchun)

iOS — pastki tab bar + sheet'lar; Android — Material bottom nav + FAB "E'lon joylash". Hit-target
≥ 44pt. Tungi rejim — `useColorScheme()` + `tokens.ts`dagi dark palette, majburiy qo'llab-quvvatlash.

## Loyiha tuzilishi (skeleton, `../mobile`)

```
mobile/
  app.json                 Expo config
  package.json
  tsconfig.json
  src/
    theme/tokens.ts         app.css'dan ko'chirilgan ranglar/radius/shrift (light+dark)
    api/client.ts           to'liq API client (auth, listings, favorites, mortgage, boost, …)
    api/types.ts            backend serializerlariga mos TypeScript interfeyslar
    store/useAppStore.ts     Zustand: auth token, fav/compare, tema
    screens/                 bo'sh placeholder ekranlar — navigatsiya keyingi sessiyada ulanadi
```

`npx create-expo-app` bilan to'liq loyiha keyingi sessiyada shu skeletonni asos qilib olib
davom ettirilishi kerak (bu yerda faqat kodning framework-agnostik qismlari — tokens, api
client, types — tayyorlangan, chunki ular Expo CLI generatsiyasiga bog'liq emas va Node.js
bilan to'g'ridan-to'g'ri yozilishi/tekshirilishi mumkin edi).

## Relizga chiqish (Bosqich 3 bilan mos)

1. `eas build` — iOS (App Store Connect) + Android (Play Console) profillari.
2. Push sertifikatlar: APNs key + FCM server key.
3. Deep link domenlari: `uyim.uz` universal links (iOS) / App Links (Android) — veb va mobil
   bitta URL sxemasini ulashishi uchun (`https://uyim.uz/listing/123` ilovada ham ochiladi).
4. Store listing: ekran skrinshotlari, tavsif (uz-Latn asosiy, ru/en Bosqich 3da).
