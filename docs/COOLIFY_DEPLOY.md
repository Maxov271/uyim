# Uyim.uz backendini Coolify'ga joylash

Domen: **uyim.server.umarovgroup.uz** · Repo: `Maxov271/uyim` · Papka: `backend/`

Bu qo'llanma ikki xil yo'l bilan: **A) Coolify UI orqali** (tavsiya etiladi, oddiyroq) yoki
**B) Coolify API orqali** (skript bilan, token kerak).

---

## 0. Oldindan tayyorlab qo'yish

`SECRET_KEY`ni terminalda generatsiya qiling (buni hech qayerga, hatto shu faylga ham
yozmang — faqat Coolify'ning Environment Variables maydoniga qo'ying):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## A) Coolify UI orqali (tavsiya etiladi)

### 1. Ma'lumotlar bazasi va Redis

Coolify'da avval ikkita **Managed Service** yarating (Project ichida → **+ New → Database**):

- **PostgreSQL 16** — nomi: `uyim-db`
- **Redis 7** — nomi: `uyim-redis`

Yaratilgach, ularning ulanish satrlarini (connection string) nusxalab oling — pastda kerak
bo'ladi.

### 2. Application yaratish

**+ New Resource → Application → Public/Private Git Repository**

| Maydon | Qiymat |
|---|---|
| Repository | `https://github.com/Maxov271/uyim` |
| Branch | `main` (yoki hozircha `claude/optimistic-ramanujan-yf3340`, keyin main'ga merge qilinadi) |
| Build Pack | **Dockerfile** |
| Base Directory | `backend` |
| Dockerfile Location | `backend/Dockerfile` |
| Port | `8000` |

### 3. Domain

Application → **Domains** → qo'shing: `uyim.server.umarovgroup.uz`
(Coolify avtomatik Let's Encrypt SSL sertifikat oladi — DNS shu serverga to'g'ri
yo'naltirilgan bo'lishi kerak: A-record → server IP).

### 4. Environment Variables

Application → **Environment Variables** — quyidagilarni qo'shing:

```
DEBUG=False
SECRET_KEY=<0-qadamda generatsiya qilingan qiymat>
ALLOWED_HOSTS=uyim.server.umarovgroup.uz
CORS_ALLOWED_ORIGINS=https://uyim.server.umarovgroup.uz

DATABASE_URL=<uyim-db xizmatining connection string'i, Coolify beradi>
REDIS_URL=<uyim-redis xizmatining connection string'i>
CELERY_TASK_ALWAYS_EAGER=False

USD_UZS_RATE=12700
OTP_DEBUG_STATIC_CODE=

# Quyidagilar bo'sh qoldirilsa ham ishlайdi (funksiya o'chirilgan holda) —
# tayyor bo'lganda to'ldirasiz:
ESKIZ_EMAIL=
ESKIZ_PASSWORD=
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_SECRET=<tasodifiy uzun matn>
PAYME_MERCHANT_ID=
PAYME_SECRET_KEY=
CLICK_SERVICE_ID=
CLICK_MERCHANT_ID=
CLICK_SECRET_KEY=
```

**Muhim:** `DEBUG=False` bo'lganda `OTP_DEBUG_STATIC_CODE` va `debug_code` javobda
qaytmaydi — SMS haqiqatan yuborilishi uchun `ESKIZ_EMAIL`/`ESKIZ_PASSWORD` to'ldirilishi kerak,
aks holda OTP kodi faqat server logida ko'rinadi (`docker logs`).

### 5. Deploy

**Deploy** tugmasini bosing. Birinchi build ~2-3 daqiqa oladi.

### 6. Migratsiya va admin yaratish

Deploy tugagach, Application → **Terminal** (yoki Coolify'ning "Execute Command" oynasi)dan:

```bash
python manage.py migrate
python manage.py seed_demo               # demo katalogni yuklaydi (ixtiyoriy)
python manage.py createsuperuser --phone +998901234567
```

### 7. Frontendni shu backendga ulash

`frontend/assets/js/api.js` yuklanishidan oldin (har bir HTML sahifada, `<script src="assets/js/api.js">`dan oldin):

```html
<script>window.UYIM_API_BASE = 'https://uyim.server.umarovgroup.uz/api';</script>
```

Frontendni qayerda joylashtirsangiz ham (Coolify'da alohida static-site sifatida, yoki
boshqa hosting), shu bitta qatorni qo'shish yetarli.

### 8. Telegram webhook (bot tayyor bo'lgach)

```bash
python manage.py set_telegram_webhook https://uyim.server.umarovgroup.uz
```

---

## B) Coolify API orqali (skript bilan)

Coolify → **Keys & Tokens → API tokens**dan token yarating, so'ng:

```bash
export COOLIFY_URL="https://server.umarovgroup.uz"
export COOLIFY_TOKEN="<token>"

# 1. Loyihadagi mavjud server/project UUID'larini ko'rish
curl -sS "$COOLIFY_URL/api/v1/servers" -H "Authorization: Bearer $COOLIFY_TOKEN" | python3 -m json.tool
curl -sS "$COOLIFY_URL/api/v1/projects" -H "Authorization: Bearer $COOLIFY_TOKEN" | python3 -m json.tool

# 2. Application yaratish (server_uuid, project_uuid, environment_name'ni 1-qadamdan oling)
curl -sS -X POST "$COOLIFY_URL/api/v1/applications/public" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "<PROJECT_UUID>",
    "server_uuid": "<SERVER_UUID>",
    "environment_name": "production",
    "git_repository": "https://github.com/Maxov271/uyim",
    "git_branch": "main",
    "build_pack": "dockerfile",
    "base_directory": "backend",
    "dockerfile_location": "backend/Dockerfile",
    "ports_exposes": "8000",
    "domains": "https://uyim.server.umarovgroup.uz",
    "name": "uyim-backend"
  }'
```

Javobda qaytgan `uuid`ni saqlab qoling — keyin shu orqali environment variable qo'shish,
deploy qilish (`POST /api/v1/applications/{uuid}/deploy`) va h.k. mumkin. To'liq API
hujjati: `$COOLIFY_URL/api/documentation` (o'zingizning Coolify instansiyangizda ochiladi).

---

## Tekshirish

```bash
curl https://uyim.server.umarovgroup.uz/api/bootstrap
```

Bo'sh emas, `CITIES`/`LISTINGS` bilan to'la JSON qaytsa — deploy muvaffaqiyatli.
