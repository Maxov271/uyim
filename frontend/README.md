# Uyim.uz — Frontend

O'zbekiston ko'chmas mulk platformasi. Statik HTML/CSS/JS (build talab qilmaydi), endi
**real Django API bilan ulangan** — qarang: [`../backend`](../backend). Mobil ilova rejasi:
[`../docs/MOBILE_APP_PLAN.md`](../docs/MOBILE_APP_PLAN.md).

## Ishga tushirish

Avval backend kerak (u yo'q bo'lsa sahifalar bo'sh ma'lumot bilan ochiladi — konsolda xato
ko'rinadi):

```bash
cd ../backend && source .venv/bin/activate && python manage.py runserver   # http://localhost:8000
```

Keyin frontendni alohida serverda:

```bash
cd frontend
python3 -m http.server 8080      # yoki: npx serve .
# http://localhost:8080
```

Backend boshqa manzilda bo'lsa, `assets/js/api.js` yuklanishidan oldin o'zgartiring:
`<script>window.UYIM_API_BASE = 'https://api.uyim.uz/api';</script>`.

Hech qanday npm/build kerak emas. Tashqi CDN: Google Fonts (Plus Jakarta Sans), Phosphor Icons, Leaflet + MarkerCluster (OpenStreetMap/Carto — API kalit talab qilmaydi).

## Sahifalar

| Fayl | Ekran | Asosiy funksiyalar |
|---|---|---|
| `index.html` | Bosh sahifa | Bitim turi tablari, mahalla darajasidagi autocomplete, tezkor filtrlar, AI qidiruv (beta), TOP karusel, tuman narx statistikasi, quruvchilar, bank/Telegram banner |
| `search.html` | Qidiruv + xarita | Split-screen, Leaflet klaster, narxli pinlar, radius qidiruv, kartochka↔pin sinxroni, 12+ filtr, saralash, ro'yxat/xarita rejimi, qidiruvni saqlash |
| `listing.html` | E'lon sahifasi | Galereya + 360°, ishonch belgilari, xususiyatlar jadvali, narx tarixi grafigi, infratuzilma, sticky aloqa paneli (qo'ng'iroq / Telegram / chat), ipoteka bloki, o'xshash e'lonlar |
| `calculator.html` | Ipoteka / nasiya | 6 bank shartlari, bitta bank yoki barchasini solishtirish, donut taqsimot, yillik amortizatsiya, ariza yuborish |
| `dashboard-buyer.html` | Xaridor kabineti | Sevimlilar, saqlangan qidiruvlar (Telegram xabarnoma), taqqoslash jadvali, uchrashuvlar, ipoteka byudjeti |
| `dashboard-agent.html` | Agent kabineti | KPI, e'lonlar jadvali + holatlar, ko'tarish (boost), ko'rishlar grafigi, lidlar manbasi donut, Telegram avto-nashr, reklama paketlari |
| `add-listing.html` | E'lon joylash | 6 qadamli sehrgar, xaritada nuqta tanlash, foto yuklash, kadastr, AI tavsif, narx, reklama paketi, jonli ko'rinish |
| `compare.html` | Taqqoslash | 4 tagacha obyekt, 15 ko'rsatkich, eng yaxshi qiymat ajratiladi, "faqat farqlar" rejimi |
| `new-buildings.html` | Yangi binolar | Loyihalar, qurilish bosqichi, quruvchi nasiyasi, 3D tur |
| `auth.html` | Kirish | Telefon → SMS OTP → profil; Telegram va OneID variantlari; xaridor/agent rollari |

## Tuzilma

```
frontend/
  assets/css/app.css     # design tokens + barcha komponentlar (yagona stylesheet)
  assets/js/data.js      # mock ma'lumotlar — backendga o'tishda shu shakl saqlanadi
  assets/js/ui.js        # window.Uyim: chrome, holat, formatlash, kartochka, xarita, ipoteka
  *.html                 # 10 ta ekran
```

## Design system

**Ranglar** — navy `#16324F` (asosiy), emerald `#0F7A5C` (ishonch), gold `#C9822B` (CTA), fon `#F4F6F8`, matn `#22282E`. Tungi rejim `html[data-theme="dark"]` orqali, barcha token'lar qayta aniqlanadi.
**Shrift** — Plus Jakarta Sans 400/500/600/700/800. **Radius** 10/16px. **Grid** 1320px, 4/8px shkala.
**Ikonalar** — Phosphor (regular / fill / duotone).

## Holat (localStorage)

`uyim.theme`, `uyim.lang`, `uyim.fav`, `uyim.compare`, `uyim.savedSearches`, `uyim.role`.

## Backendga ulanish (amalga oshirildi)

`assets/js/api.js` — Django API klienti (`window.UyimAPI`). `assets/js/data.js` endi mock emas —
sahifa yuklanishida `/api/bootstrap`ga bitta sinxron so'rov yuborib, natijani o'sha eski
`window.UyimData` shaklida (`CITIES, DISTRICTS, LISTINGS, BANKS, AGENTS …`) qaytaradi, shuning
uchun qolgan barcha sahifa kodi **o'zgarishsiz** ishlayveradi. Amallar (OTP kirish, e'lon
joylash, ipoteka, lid yuborish, sevimlilar sinxroni) `UyimAPI` orqali to'g'ridan-to'g'ri real
backendga boradi. Texnik tafsilotlar va bu yondashuvning nima uchun tanlanganligi —
[`../backend/README.md`](../backend/README.md#how-the-frontend-connects).
