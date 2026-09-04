/* Uyim.uz — real API client for the Django/DRF backend (see /backend).
   Load this BEFORE data.js. It exposes:
     - window.UyimAPI.fetchBootstrapSync() — used once by data.js to build window.UyimData
     - window.UyimAPI.* — everything the pages call for real actions (auth, create listing,
       favorites/compare sync, leads, mortgage, boost …)

   Override the backend location by setting `window.UYIM_API_BASE` in an inline <script>
   BEFORE this file loads, e.g. <script>window.UYIM_API_BASE='https://api.uyim.uz/api'</script>.
   Default assumes `python manage.py runserver` on the standard local port. */

window.UyimAPI = (() => {
  const API_BASE = window.UYIM_API_BASE || 'http://localhost:8000/api';
  const LS = { access: 'uyim.token', refresh: 'uyim.refresh' };

  const getAccess = () => localStorage.getItem(LS.access);
  const getRefresh = () => localStorage.getItem(LS.refresh);
  const setTokens = (access, refresh) => {
    if (access) localStorage.setItem(LS.access, access);
    if (refresh) localStorage.setItem(LS.refresh, refresh);
  };
  const clearTokens = () => { localStorage.removeItem(LS.access); localStorage.removeItem(LS.refresh); };
  const isAuthed = () => !!getAccess();

  /* ---------------- synchronous bootstrap fetch ----------------
     Every frontend page currently does: <script src="data.js"></script> then immediately,
     synchronously, reads window.UyimData in the very next inline <script> — there is no
     async/await anywhere in the existing 10 pages. Rather than rewrite all of them to an
     async-boot pattern, data.js uses this synchronous XHR once at load time so
     window.UyimData is fully populated before any other script on the page runs — the exact
     same contract the old mock data.js provided. This is a deliberate, documented bridge;
     the natural next step (see backend/README.md) is to move the frontend to an async boot
     or have Django render the bootstrap JSON server-side. */
  function fetchBootstrapSync() {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `${API_BASE}/bootstrap`, false); // false = synchronous
    if (getAccess()) xhr.setRequestHeader('Authorization', `Bearer ${getAccess()}`);
    try {
      xhr.send(null);
    } catch (e) {
      console.error('[Uyim] backend bilan bog\'lanib bo\'lmadi:', e);
      return null;
    }
    if (xhr.status >= 200 && xhr.status < 300) {
      try { return JSON.parse(xhr.responseText); } catch (e) { console.error('[Uyim] bootstrap JSON xato', e); return null; }
    }
    console.error('[Uyim] /bootstrap HTTP', xhr.status);
    return null;
  }

  /* ---------------- async request helper ---------------- */
  async function request(method, path, { body, auth = false, retry = true } = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth && getAccess()) headers.Authorization = `Bearer ${getAccess()}`;

    const resp = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (resp.status === 401 && auth && retry && getRefresh()) {
      const refreshed = await refreshAccessToken();
      if (refreshed) return request(method, path, { body, auth, retry: false });
    }

    if (resp.status === 204) return null;
    const data = await resp.json().catch(() => null);
    if (!resp.ok) {
      const err = new Error((data && (data.message_uz || data.detail)) || `HTTP ${resp.status}`);
      err.status = resp.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  async function refreshAccessToken() {
    try {
      const resp = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: getRefresh() }),
      });
      if (!resp.ok) { clearTokens(); return false; }
      const data = await resp.json();
      setTokens(data.access, null);
      return true;
    } catch {
      return false;
    }
  }

  /* ---------------- domain calls ---------------- */
  const otpRequest = (phone, channel = 'sms') =>
    request('POST', '/auth/otp/request', { body: { phone, channel } });
  const otpVerify = (phone, code, role) =>
    request('POST', '/auth/otp/verify', { body: { phone, code, role } }).then((d) => {
      setTokens(d.access, d.refresh);
      return d;
    });
  const logout = () => clearTokens();

  const me = () => request('GET', '/me', { auth: true });
  const updateMe = (patch) => request('PATCH', '/me', { body: patch, auth: true });

  const createListing = (payload) => request('POST', '/listings', { body: payload, auth: true });
  const uploadListingPhotos = async (id, files) => {
    const form = new FormData();
    [...files].forEach((f) => form.append('images', f));
    const resp = await fetch(`${API_BASE}/listings/${id}/photos`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getAccess()}` },
      body: form,
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  };
  const updateListing = (id, patch) => request('PATCH', `/listings/${id}`, { body: patch, auth: true });
  const deleteListing = (id) => request('DELETE', `/listings/${id}`, { auth: true });
  const boostListing = (id, pkg, provider = 'payme') =>
    request('POST', `/listings/${id}/boost`, { body: { package: pkg, provider }, auth: true });
  const sendLead = (id, channel) => request('POST', `/listings/${id}/lead`, { body: { channel } });

  const addFavorite = (listingId) => request('POST', '/favorites', { body: { listing: listingId }, auth: true });
  const removeFavorite = (listingId) => request('DELETE', `/favorites/${listingId}`, { auth: true });
  const addCompare = (listingId) => request('POST', '/compare', { body: { listing: listingId }, auth: true });
  const removeCompare = (listingId) => request('DELETE', `/compare/${listingId}`, { auth: true });

  const savedSearches = () => request('GET', '/saved-searches', { auth: true });
  const createSavedSearch = (payload) => request('POST', '/saved-searches', { body: payload, auth: true });
  const updateSavedSearch = (id, patch) => request('PATCH', `/saved-searches/${id}`, { body: patch, auth: true });
  const deleteSavedSearch = (id) => request('DELETE', `/saved-searches/${id}`, { auth: true });

  const mortgageCalc = (payload) => request('POST', '/mortgage/calc', { body: payload });
  const mortgageApply = (payload) => request('POST', '/mortgage/apply', { body: payload, auth: true });

  const geoSuggest = (q) => request('GET', `/geo/suggest?q=${encodeURIComponent(q)}`);

  return {
    API_BASE, isAuthed, setTokens, clearTokens, getAccess,
    fetchBootstrapSync,
    otpRequest, otpVerify, logout, me, updateMe,
    createListing, uploadListingPhotos, updateListing, deleteListing, boostListing, sendLead,
    addFavorite, removeFavorite, addCompare, removeCompare,
    savedSearches, createSavedSearch, updateSavedSearch, deleteSavedSearch,
    mortgageCalc, mortgageApply, geoSuggest,
  };
})();
