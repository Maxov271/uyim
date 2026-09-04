# Uyim.uz — Backend

Django + Django REST Framework backend for [Uyim.uz](../frontend), O'zbekiston ko'chmas mulk
platformasi. Implements the full API contract from [`CLAUDE_CODE_PROMPT.md`](../CLAUDE_CODE_PROMPT.md).

## Stack

| Qatlam | Tanlov |
|---|---|
| Framework | Django 5 + Django REST Framework |
| Auth | Telefon + SMS OTP → JWT (SimpleJWT), + Telegram Login Widget |
| DB | PostgreSQL (prod) / SQLite (zero-setup dev fallback) |
| Geo | Plain lat/lng + Haversine (no PostGIS/GDAL dependency — see note below) |
| Fon vazifalar | Celery + Redis (dev: `CELERY_TASK_ALWAYS_EAGER=True`, no broker needed) |
| SMS | Eskiz.uz (falls back to console/debug OTP when unconfigured) |
| Telegram | Raw Bot API calls (`apps/telegrambot`) — auto-publish, push, /start phone-link, Telegram-delivered OTP login |
| To'lov | Payme (JSON-RPC merchant API) + Click (Prepare/Complete) |
| Fayl | Local `MEDIA_ROOT` in dev; point `django-storages` at S3/MinIO for prod |

**Why not PostGIS?** GDAL/GEOS system libraries aren't guaranteed on every host this runs on.
Radius search and clustering are implemented with plain `lat`/`lng` floats + Haversine in
`apps/core/geo_utils.py` — correct and portable, just without a spatial index. If the
catalogue grows into the millions, swap in `django.contrib.gis` (the model fields are a
drop-in replacement) without changing the API contract.

## Loyiha tuzilishi

```
backend/
  config/                  settings, urls, celery.py
  apps/
    core/                  humanize (uz relative time), exceptions ({code,message_uz,message_ru}),
                           throttling, permissions, geo_utils, currency (CBU sync)
    accounts/               User (phone-based), OTP, JWT, Telegram Login
    geo/                    City → District → Mahalla
    agencies/               Agency profiles + unified agent serialization (agency OR owner)
    listings/               Listing, ListingPhoto, PriceHistory + filtering/sort/cluster
    favorites/              Favorite, Compare, SavedSearch
    leads/                  Lead (call/chat/telegram), ChatThread/ChatMessage (data model ready;
                           no chat UI in the frontend yet, so no chat REST/WS surface built)
    mortgage/               Bank, MortgageApplication, calculator (same formula as the frontend)
    telegrambot/            TelegramChannel/TelegramPost, bot client, webhook, auto-publish tasks
    payments/               BoostOrder, Payme + Click gateways
    developers/             Developer, Project (new buildings)
    bootstrap/               GET /api/bootstrap — aggregate read matching window.UyimData 1:1
```

## Ishga tushirish (local dev)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # SQLite by default — no DB setup needed
python manage.py migrate
python manage.py seed_demo      # loads the same catalogue as the old data.js mock
python manage.py createsuperuser --phone +998900000000
python manage.py runserver
```

API: `http://localhost:8000/api/...` · Admin (moderator panel): `http://localhost:8000/admin/`

Then serve the frontend separately and point it at this API (see [../frontend/README.md](../frontend/README.md)):

```bash
cd ../frontend && python3 -m http.server 8080
```

### Docker (Postgres + Redis + Celery, closer to prod)

```bash
cd backend
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_demo
docker compose exec web python manage.py createsuperuser --phone +998900000000
```

## API kontrakti

Full endpoint list, data model and business rules: see
[`../CLAUDE_CODE_PROMPT.md`](../CLAUDE_CODE_PROMPT.md) §4–7 — this backend implements it as-is,
plus a few pragmatic additions:

- `GET /api/bootstrap` — one aggregate read the frontend's `data.js` fetches once (see
  "How the frontend connects" below) instead of the ~8 separate calls the individual
  `/api/geo/cities`, `/api/listings`, `/api/banks`, … endpoints would otherwise need for an
  initial page load. Those individual REST endpoints still exist and are fully functional —
  they're what the future mobile app (and a more granular frontend refactor) should use.
- `POST /api/listings/:id/photos` (multipart) / `DELETE /api/listings/:id/photos/:photo_id` —
  photo upload wasn't in the original contract's endpoint list but is obviously required for
  real listing CRUD.
- `POST /api/payments/payme/webhook`, `POST /api/payments/click/{prepare,complete}` — payment
  provider callbacks (see Payments below).
- `POST /api/telegram/webhook/<secret>` — Telegram Bot API webhook receiver.

All error responses use the required shape: `{code, message_uz, message_ru}`.

### OTP login via Telegram (no SMS)

`POST /api/auth/otp/request {phone, channel: "telegram"}` returns a
`telegram_deep_link` (`https://t.me/<bot>?start=<token>`) instead of sending an SMS. When the
user opens it and presses **Start**, the bot webhook (`apps/telegrambot/views.py`) looks up
the token, delivers the same 4-digit code as a chat message, and records that chat's
`telegram_id`. `POST /api/auth/otp/verify` is unchanged — same code, same endpoint — and
additionally links `telegram_id`/`telegram_username` onto the account the moment it verifies,
so the account is bot-notifiable (saved searches, new leads) without a separate linking step.
Requires `TELEGRAM_BOT_USERNAME` set (the token itself doesn't need a live bot to *generate* —
only to *deliver*, so requesting a link works even before `TELEGRAM_BOT_TOKEN` is configured;
delivery obviously needs a real, webhook-registered bot). Verified end-to-end locally by
posting a synthetic Telegram update straight at the webhook endpoint and confirming the
account came out linked — see git history for the test script if useful as a reference.

## How the frontend connects

The static frontend (`../frontend`) was built fully client-side with all data preloaded
synchronously into `window.UyimData` before any page script runs — there's no async/await
anywhere in the original 10 pages. Rather than rewrite all of them to an async-boot pattern,
`frontend/assets/js/data.js` now does **one synchronous XHR call to `/api/bootstrap`** and
assigns the (identically-shaped) response to `window.UyimData`. Every page's rendering code —
`ui.js`, `index.html`'s hero search, `search.html`'s filters, etc. — needed **zero changes**.

This means `/api/bootstrap` currently returns the *entire* active listings catalogue (not
paginated) so the frontend's existing client-side filtering keeps working unchanged. That's
correct for a demo-scale catalogue (tens to low hundreds of listings) but won't scale
indefinitely. The real, paginated, filterable `GET /api/listings?...` endpoint already exists
and is what a future iteration of `search.html` (or the mobile app) should call directly
instead of filtering the full in-memory array — swapping that in is a frontend-only follow-up,
no backend changes needed.

Actions (not just reads) go through `frontend/assets/js/api.js` (`window.UyimAPI`), which the
pages now call directly for: OTP login (`auth.html`), creating a listing (`add-listing.html`),
mortgage calc/apply, sending leads on contact-modal clicks, and background-syncing
favorites/compare when signed in (they still live in `localStorage` first, for instant/offline
UI — the backend call just mirrors it so it survives across devices).

## Seed data

`python manage.py seed_demo` recreates the exact same cities, districts, mahallas, banks,
agents/agencies and 14 listings that used to be hardcoded in `data.js`, so switching from the
mock to the real API produces an identical-looking catalogue out of the box. Safe to re-run
(upserts by natural keys).

## Testing what was built

Every endpoint below was exercised against a live `runserver` + SQLite during development:
OTP request/verify → JWT, `/api/me`, `/api/bootstrap`, `/api/geo/*`, `/api/listings` (list with
filters, create, detail w/ similar+agent_profile), `/api/favorites`, `/api/listings/:id/lead`,
`/api/listings/:id/boost` (permission check), `/api/banks`, `/api/mortgage/calc`, Django admin
login. Telegram/Payme/Click integrations are structurally correct against their documented
protocols but untested against live credentials (none exist in this environment) — see
`.env.example` for what to configure before going live.

## Bosqichlar (matches CLAUDE_CODE_PROMPT.md §9)

- **Bosqich 1 (MVP) — done here:** OTP auth, geo catalog, listing CRUD + moderation (Django
  admin), search/filter, map data (bbox + clustering), listing detail, favorites, mortgage
  calculator, Telegram bot (auto-publish + saved-search push + new-lead alerts + /start
  phone-link).
- **Bosqich 2 — scaffolded, needs real credentials/hardening to go live:** compare, saved
  searches (done), agent analytics (done), boost + Payme/Click payment (protocol-correct,
  untested live), chat data model (present, no REST/WS surface — frontend has no chat UI yet),
  new-buildings module (done).
- **Bosqich 3 — not started (as scoped in the brief):** AI natural-language search, price
  prediction, 360° tours, perceptual-hash duplicate detection, ru/en localization, and the
  mobile app — see [`../docs/MOBILE_APP_PLAN.md`](../docs/MOBILE_APP_PLAN.md) for that.

## Rate limits (§10)

`60/min` search, `3/10min` OTP request, `10/hour` lead submission — enforced via DRF throttling
(`apps/core/throttling.py`).
