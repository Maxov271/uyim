# CLAUDE CODE PROMPT — Uyim.uz backend + mobil ilova

> Bu faylni Claude Code'ga kontekst sifatida bering. Frontend allaqachon tayyor (`frontend/`), uni **qayta yozmang** — API bilan ulang va mobil ilovani shu dizayn tizimida quring.

---

## 1. Loyiha haqida

**Uyim.uz** — O'zbekiston bozori uchun ko'chmas mulk platformasi (OLX Ko'chmas mulk / Uybor.uz / Zillow raqobatchilari o'rnini egallaydi, lekin toza PropTech UX bilan).
Foydalanuvchilar: xaridor/ijarachi, uy egasi, agentlik, quruvchi (developer), moderator.
Tillar: **uz-Latn (asosiy)**, ru, en. Valyuta: **USD** (so'm ekvivalenti bilan, kurs 12 700).

Repozitoriyda hozir:

```
frontend/           # tayyor statik frontend — 10 ekran, build yo'q
  assets/css/app.css
  assets/js/data.js # ← MOCK. Buni API klient bilan almashtirasiz
  assets/js/ui.js   # window.Uyim helperlari
  *.html
```

---

## 2. Vazifa

1. **Backend** — REST (yoki GraphQL) API + admin/moderatsiya.
2. **Frontendni ulash** — `data.js` o'rniga real API.
3. **Telegram bot + avto-nashr xizmati**.
4. **Mobil ilova** (React Native / Expo, iOS + Android) — frontenddagi dizayn tizimini 1:1 takrorlaydi.

---

## 3. Texnologiya tavsiyasi

| Qatlam | Tanlov | Sabab |
|---|---|---|
| API | **NestJS + TypeScript** (yoki FastAPI) | modul tuzilma, DTO validatsiya |
| DB | **PostgreSQL + PostGIS** | radius/geo qidiruv shart |
| Qidiruv | **Meilisearch** yoki Postgres GIN + trigram | mahalla nomlari uchun fuzzy |
| Kesh/navbat | Redis + BullMQ | Telegram nashr, moderatsiya, narx tarixi |
| Fayl | S3-mos (MinIO) + imgproxy | foto/360° tur |
| Auth | Telefon + SMS OTP (Eskiz.uz / Play Mobile), Telegram Login, OneID | |
| To'lov | **Payme, Click, Uzum Bank** | reklama paketlari |
| Mobil | **React Native (Expo) + TypeScript** | bitta kod bazasi |
| Xarita | Leaflet (web) / react-native-maps (mobil), OSM tiles | kalitsiz start |

---

## 4. Ma'lumotlar modeli (minimal)

```
User        id, phone, name, role(buyer|owner|agency|developer|moderator), city,
            telegram_id, verified_phone, created_at
Agency      id, user_id, name, logo, inn, license_doc, verified, years, rating, listings_count
Listing     id, owner_id, agency_id, deal(sale|new|rent|daily|commercial|land),
            type, price_usd, price_uzs, negotiable, mortgage_allowed, swap_allowed,
            rooms, area, floor, floors, year, condition, city_id, district_id, mahalla_id,
            lat, lng, address_hidden, title, description, features[](jsonb),
            status(draft|moderation|active|archived|rejected), verified_owner, cadastre_doc,
            top_until, hot_until, views, calls, tg_leads, created_at, published_at
ListingPhoto id, listing_id, url, order, is_cover
PriceHistory id, listing_id, price_usd, changed_at
Geo         City → District → Mahalla (MFY)   // hammasi lat/lng + polygon (PostGIS)
Favorite    user_id, listing_id
Compare     user_id, listing_id
SavedSearch id, user_id, query(jsonb), notify_push, notify_telegram, last_run_at
Lead        id, listing_id, user_id, channel(call|chat|telegram), created_at
ChatThread / ChatMessage
Bank        id, name, rate, min_down_pct, max_term_years, note, active
MortgageApplication id, user_id, listing_id, bank_id, price, down_pct, years, status
TelegramChannel id, username, district_id, active
BoostOrder  id, listing_id, package(top|hot|tg_push|banner), price_uzs, payment_id, status
```

**Muhim:** `frontend/assets/js/data.js` dagi obyektlar aynan shu maydonlarni ishlatadi (`l.deal`, `l.rooms`, `l.district`, `l.mahalla`, `l.verified`, `l.top`, `l.hot`, `l.tg`, `l.mortgage`, `l.priceHistory`…). API javobini shu shaklga moslang — frontend hech qanday o'zgarishsiz ishlaydi.

---

## 5. API kontrakti (asosiy endpointlar)

```
GET  /api/geo/cities                       → [{id,name,center:[lat,lng],zoom}]
GET  /api/geo/districts?city=tashkent      → [{id,name,center,ppm,mahallas:[...]}]
GET  /api/geo/suggest?q=qator              → shahar/tuman/mahalla aralash autocomplete

GET  /api/listings?deal=&district=&mahalla=&price_min=&price_max=&rooms=1,2,3
     &area_min=&floor_min=&type=&condition=&verified=&mortgage=&tg=
     &lat=&lng=&radius=1500&sort=new|cheap|rich|pop&page=&limit=
     → {items:[Listing], total, bbox, clusters:[{lat,lng,count}]}
GET  /api/listings/:id                     → Listing + agent + priceHistory + poi + similar
POST /api/listings                         → e'lon joylash (moderationga)
PATCH/DELETE /api/listings/:id

POST /api/listings/:id/boost               → {package} → to'lov linki (Payme/Click)
POST /api/listings/:id/lead                → {channel} — qo'ng'iroq/chat/telegram analitikasi

GET/POST/DELETE /api/favorites             GET/POST/DELETE /api/compare
GET/POST/PATCH  /api/saved-searches        (+ notify_telegram)

GET  /api/banks                            → [{id,name,rate,minDown,maxTerm,note}]
POST /api/mortgage/calc                    → {monthly,down,loan,interest,total,incomeNeeded}
POST /api/mortgage/apply

POST /api/auth/otp/request  {phone}
POST /api/auth/otp/verify   {phone,code}   → JWT (access+refresh)
POST /api/auth/telegram     (Login Widget)
GET  /api/me                               PATCH /api/me

GET  /api/agents/:id                       GET /api/agency/:id/analytics
GET  /api/developers  GET /api/projects    (yangi binolar)
```

Ipoteka formulasi (frontend bilan bir xil bo'lishi shart):
`monthly = loan * i / (1 - (1+i)^-n)`, `i = rate/100/12`, `n = years*12`, `loan = price*(1-down/100)`.

---

## 6. Telegram integratsiyasi (platformaning asosiy farqi)

1. **@uyim_bot**
   - `/start` — telefon raqamini so'rash → hisobga bog'lash.
   - Saqlangan qidiruv bo'yicha yangi e'lon chiqsa — darhol push (rasm + narx + "Ochish" tugmasi, deep link).
   - Inline qidiruv: bot ichida tuman/narx tanlab natija olish.
   - Agent uchun: yangi lid kelganda xabar.
2. **Avto-nashr** — e'lon `active` bo'lgan zahoti tuman kanaliga (`@chilonzor_uylar` va h.k.) post: 1-foto, narx, xonalar/m²/qavat, mahalla, ishonch belgisi, e'longa link. BullMQ navbati, rate-limit, post_id saqlanadi (narx o'zgarsa — post tahrirlanadi, sotilsa — ✅ belgisi).
3. `TelegramChannel` jadvali orqali agentlik o'z kanallarini ulaydi.

---

## 7. Moderatsiya va ishonch

- Har bir e'lon `moderation` holatida boshlanadi. Moderator paneli: foto sifati, dublikat aniqlash (perceptual hash), narx anomaliyasi, telefon qora ro'yxati.
- **Tasdiqlangan egasi** — kadastr hujjati + telefon tasdiqlangan.
- **Ishonchli agentlik** — guvohnoma/STIR tekshirilgan, ≥6 oy faoliyat, shikoyat darajasi past.
- Dublikat e'lonlar birlashtiriladi (bir mulk — bir kartochka, bir nechta agent).

---

## 8. Mobil ilova (React Native / Expo)

Ekranlar frontenddagi bilan bir xil axborot arxitekturasida:

| Tab | Ekran |
|---|---|
| Asosiy | Qidiruv, tezkor filtr chiplari, TOP karusel, tuman statistikasi |
| Xarita | To'liq ekran xarita, narxli pinlar, klaster, radius (bosib ushlab turish), pastdan chiqadigan kartochka |
| Sevimli | Sevimlilar + taqqoslash (gorizontal skroll ustunlar) + saqlangan qidiruvlar |
| Ipoteka | Kalkulyator, bank tanlash, ariza |
| Kabinet | Profil, e'lonlarim, analitika, boost, sozlamalar |

Modal/sheet'lar: filtrlar (bottom sheet), aloqa (qo'ng'iroq / Telegram / chat), foto galereya, 360° tur.
Native: `tel:` qo'ng'iroq, Telegram deep link (`tg://resolve?domain=uyim_bot`), push (FCM/APNs), geolokatsiya ("Menga yaqin"), kameradan foto yuklash, biometrik kirish.
iOS — pastdagi tab bar + sheet'lar; Android — Material bottom nav + FAB "E'lon joylash". Hit-target ≥ 44pt. Tungi rejim majburiy.

**Dizayn tokenlarini `frontend/assets/css/app.css` dan ko'chiring** (navy `#16324F`, emerald `#0F7A5C`, gold `#C9822B`, radius 10/16, Plus Jakarta Sans) va `theme.ts` qiling.

---

## 9. Bosqichlar

1. **MVP (4–6 hafta):** auth (OTP), geo katalog, e'lon CRUD + moderatsiya, qidiruv/filtr, xarita, e'lon sahifasi, sevimlilar, ipoteka kalkulyator, Telegram bot (push + avto-nashr).
2. **Faza 2:** saqlangan qidiruvlar, taqqoslash, agent analitikasi, boost + to'lov (Payme/Click), chat, yangi binolar moduli.
3. **Faza 3:** AI qidiruv (tabiiy tilda → filtr), narx bashorati, 360° tur, dublikat aniqlash, ru/en lokalizatsiya, mobil ilova relizi.

---

## 10. Qat'iy talablar

- Frontend fayllari **ko'rinishi o'zgarmasin** — faqat `data.js` API klientga almashtiriladi.
- Barcha matn uz-Latn; API xatolari ham uz-Latn (`{code, message_uz, message_ru}`).
- Narx USD saqlanadi, ko'rsatishda so'm ekvivalenti (kurs kunlik yangilanadi — CBU API).
- Aniq manzil ommaviy API'da qaytmasin — faqat taxminiy nuqta (±150 m) va mahalla.
- Rate-limit: qidiruv 60/min, OTP 3/10min, lead 10/soat.
- Analitika hodisalari: `search`, `filter_apply`, `map_radius`, `listing_view`, `call_click`, `tg_click`, `chat_open`, `mortgage_calc`, `listing_publish`, `boost_purchase`.
