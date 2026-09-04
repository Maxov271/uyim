/* Uyim.uz — real data layer. Was a hardcoded mock; now a thin synchronous bootstrap fetch
   against the Django/DRF backend (see /backend and backend/apps/bootstrap/views.py).
   window.UyimData keeps EXACTLY the same shape the mock produced (CITIES, DISTRICTS,
   DEAL_TYPES, PROP_TYPES, BANKS, DEVELOPERS, AGENTS, LISTINGS, SAVED_SEARCHES,
   DISTRICT_STATS, NOTIFICATIONS, RATE_UZS) so every page's rendering code — ui.js,
   index.html, search.html, listing.html, … — needed zero changes.
   Requires assets/js/api.js to be loaded first. */

window.UyimData = (() => {
  const FALLBACK = {
    CITIES: [], DISTRICTS: [], DEAL_TYPES: [], PROP_TYPES: [], BANKS: [], DEVELOPERS: [],
    AGENTS: [], LISTINGS: [], SAVED_SEARCHES: [], DISTRICT_STATS: [], NOTIFICATIONS: [],
    RATE_UZS: 12700,
  };

  const data = window.UyimAPI ? window.UyimAPI.fetchBootstrapSync() : null;

  if (!data) {
    console.error(
      '[Uyim] Backend bilan bog\'lanib bo\'lmadi — bo\'sh ma\'lumot bilan davom etilmoqda. ' +
      'Django serveri ishga tushirilganini tekshiring: python manage.py runserver'
    );
    return FALLBACK;
  }

  return data;
})();
