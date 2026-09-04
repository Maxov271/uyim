/* Uyim.uz — umumiy UI qatlami: chrome, holat (localStorage), formatlash, kartochka, xarita */

window.Uyim = (() => {
  const D = window.UyimData;
  const LS = {
    theme:'uyim.theme', lang:'uyim.lang', fav:'uyim.fav', cmp:'uyim.compare',
    saved:'uyim.savedSearches', role:'uyim.role'
  };

  /* ---------------- holat ---------------- */
  const read = (k, def) => { try { return JSON.parse(localStorage.getItem(k)) ?? def; } catch { return def; } };
  const write = (k, v) => localStorage.setItem(k, JSON.stringify(v));

  const state = {
    fav: read(LS.fav, []),
    compare: read(LS.cmp, []),
    role: read(LS.role, 'buyer')
  };

  /* Favorites/compare stay in localStorage for instant, offline-safe UI (unchanged from the
     mock build) — when signed in, the same action is also mirrored to the backend in the
     background so it survives across devices. A failed sync never blocks the local toggle.
     Ids are coerced to strings throughout: real listing ids from the API are numbers, but a
     `data-fav="${l.id}"` DOM attribute always reads back as a string, so without this a
     listing could end up stored twice (once as 1, once as "1") depending on which code path
     favorited it. */
  const syncApi = window.UyimAPI;
  const bgSync = (fn) => { if (syncApi && syncApi.isAuthed()) fn().catch(() => {}); };

  const isFav = id => state.fav.includes(String(id));
  const toggleFav = id => {
    id = String(id);
    const on = isFav(id);
    state.fav = on ? state.fav.filter(x => x !== id) : [...state.fav, id];
    write(LS.fav, state.fav);
    toast(on ? "Saqlanganlardan olindi" : "Sevimlilarga saqlandi");
    document.dispatchEvent(new CustomEvent('uyim:fav', { detail:{ id, on:!on } }));
    bgSync(() => on ? syncApi.removeFavorite(id) : syncApi.addFavorite(id));
    return !on;
  };
  const inCompare = id => state.compare.includes(String(id));
  const toggleCompare = id => {
    id = String(id);
    const wasIn = inCompare(id);
    if (wasIn) { state.compare = state.compare.filter(x => x !== id); }
    else if (state.compare.length >= 4) { toast("Taqqoslashga eng ko'pi 4 ta mulk"); return false; }
    else { state.compare = [...state.compare, id]; }
    write(LS.cmp, state.compare);
    toast(inCompare(id) ? `Taqqoslashga qo'shildi · ${state.compare.length}` : "Taqqoslashdan olindi");
    document.dispatchEvent(new CustomEvent('uyim:compare'));
    bgSync(() => wasIn ? syncApi.removeCompare(id) : syncApi.addCompare(id));
    return inCompare(id);
  };

  /* ---------------- formatlash ---------------- */
  const nf = new Intl.NumberFormat('ru-RU');
  const usd = n => '$' + nf.format(Math.round(n)).replace(/\u00A0/g, ' ');
  const uzs = n => {
    const s = n * D.RATE_UZS;
    return s >= 1e9 ? (s / 1e9).toFixed(2).replace('.', ',') + ' mlrd so\'m'
                    : Math.round(s / 1e6) + ' mln so\'m';
  };
  const priceLabel = l => l.deal === 'rent' ? usd(l.price) + '/oy'
                        : l.deal === 'daily' ? usd(l.price) + '/kun' : usd(l.price);
  const ppm = l => l.area ? usd(l.price / l.area) + '/m²' : '—';
  const pinLabel = l => l.deal === 'sale' || l.deal === 'new' || l.deal === 'commercial' || l.deal === 'land'
    ? '$' + Math.round(l.price / 1000) + 'k' : usd(l.price);
  const titleOf = l => l.rooms
    ? `${l.rooms} xonali ${l.type.toLowerCase()} · ${l.area} m²`
    : `${l.type} · ${l.area} m²`;
  const placeOf = l => {
    const d = D.DISTRICTS.find(x => x.id === l.district);
    return `${d ? d.name : ''}, ${l.mahalla} mahallasi`;
  };
  const dealLabel = id => (D.DEAL_TYPES.find(d => d.id === id) || {}).label || '';

  /* ---------------- ipoteka ---------------- */
  function mortgage({ price, downPct, years, rate }) {
    const down = price * downPct / 100;
    const loan = price - down;
    const i = rate / 100 / 12, n = years * 12;
    const monthly = i === 0 ? loan / n : loan * i / (1 - Math.pow(1 + i, -n));
    const total = monthly * n;
    return { down, loan, monthly, total, interest: total - loan, incomeNeeded: monthly / 0.5 };
  }

  /* ---------------- chrome ---------------- */
  const NAV = [
    { href:'search.html?deal=sale',  label:"Sotib olish", key:'sale' },
    { href:'search.html?deal=rent',  label:"Ijaraga",     key:'rent' },
    { href:'search.html?deal=daily', label:"Kunlik ijara",key:'daily' },
    { href:'new-buildings.html',     label:"Yangi binolar", key:'new' },
    { href:'calculator.html',        label:"Ipoteka",     key:'calc' },
    { href:'compare.html',           label:"Taqqoslash",  key:'compare' }
  ];

  function header(active) {
    return `
<header class="hdr">
  <div class="hdr-in">
    <a class="brand" href="index.html">
      <span class="brand-mark"><i class="ph-fill ph-house-line"></i></span>
      Uyim<span class="brand-dot">.</span>uz
    </a>
    <nav class="nav">
      ${NAV.map(n => `<a href="${n.href}"${n.key === active ? ' aria-current="page"' : ''}>${n.label}</a>`).join('')}
    </nav>
    <div class="hdr-tools">
      <div class="lang" role="group" aria-label="Til">
        ${['uz','ru','en'].map(l => `<button data-lang="${l}">${l.toUpperCase()}</button>`).join('')}
      </div>
      <button class="btn btn-icon" data-theme-toggle title="Tungi rejim"><i class="ph ph-moon-stars"></i></button>
      <a class="btn btn-icon" href="dashboard-buyer.html" title="Kabinet"><i class="ph ph-user"></i></a>
      <a class="btn btn-outline btn-sm" href="auth.html">Kirish</a>
      <a class="btn btn-cta btn-sm" href="add-listing.html"><i class="ph ph-plus-circle"></i>E'lon joylash</a>
    </div>
  </div>
</header>`;
  }

  function footer() {
    const col = (h, items) => `<div><h4>${h}</h4><ul>${items.map(i => `<li><a href="${i[1]}">${i[0]}</a></li>`).join('')}</ul></div>`;
    return `
<footer class="ftr">
  <div class="ftr-in">
    <div class="stack" style="gap:14px">
      <a class="brand" href="index.html"><span class="brand-mark"><i class="ph-fill ph-house-line"></i></span>Uyim<span class="brand-dot">.</span>uz</a>
      <p class="tiny muted" style="max-width:34ch">O'zbekiston uchun ko'chmas mulk platformasi — mahalla darajasidagi qidiruv, mahalliy banklar ipotekasi va Telegram integratsiyasi.</p>
      <div class="store">
        <a href="#"><i class="ph ph-apple-logo"></i>App Store</a>
        <a href="#"><i class="ph ph-google-play-logo"></i>Google Play</a>
      </div>
    </div>
    ${col("Qidiruv", [["Kvartiralar","search.html?deal=sale"],["Yangi binolar","new-buildings.html"],["Ijaraga","search.html?deal=rent"],["Kunlik ijara","search.html?deal=daily"],["Tijorat","search.html?deal=commercial"]])}
    ${col("Xizmatlar", [["Ipoteka kalkulyatori","calculator.html"],["Taqqoslash","compare.html"],["E'lon joylash","add-listing.html"],["Agentlar uchun","dashboard-agent.html"]])}
    ${col("Kompaniya", [["Biz haqimizda","#"],["Ishonch va xavfsizlik","#"],["Foydalanish shartlari","#"],["Aloqa","#"]])}
    <div>
      <h4>Telegram</h4>
      <p class="tiny muted" style="margin-bottom:12px">Bot orqali yangi e'lonlar to'g'ridan-to'g'ri sizga keladi.</p>
      <a class="btn btn-tg btn-sm btn-block" href="#"><i class="ph-fill ph-telegram-logo"></i>@uyim_bot</a>
    </div>
  </div>
  <div class="ftr-bottom">
    <span>© 2026 Uyim.uz · Barcha huquqlar himoyalangan</span>
    <span>Toshkent · +998 71 200 00 00</span>
  </div>
</footer>`;
  }

  function mobileNav(active) {
    const item = (href, icon, label, key) =>
      `<a href="${href}"${key === active ? ' aria-current="page"' : ''}><i class="ph${key === active ? '-fill' : ''} ${icon}"></i>${label}</a>`;
    return `
<nav class="mnav"><div class="mnav-in wrap" style="padding:0 8px">
  ${item('index.html','ph-house-line',"Asosiy",'home')}
  ${item('search.html','ph-map-trifold',"Xarita",'search')}
  <a class="fab" href="add-listing.html" aria-label="E'lon joylash"><i class="ph ph-plus"></i></a>
  ${item('dashboard-buyer.html','ph-heart',"Sevimli",'fav')}
  ${item('dashboard-agent.html','ph-user-circle',"Kabinet",'me')}
</div></nav>`;
  }

  /* ---------------- kartochka ---------------- */
  function badges(l) {
    const out = [];
    if (l.top) out.push(`<span class="badge badge-top"><i class="ph-fill ph-crown-simple"></i>TOP</span>`);
    if (l.hot) out.push(`<span class="badge badge-hot"><i class="ph-fill ph-fire"></i>HOT</span>`);
    if (l.isNew) out.push(`<span class="badge badge-new">YANGI BINO</span>`);
    return out.join('');
  }
  function trustBadges(l) {
    const a = D.AGENTS.find(x => x.id === l.agent) || {};
    const out = [];
    if (l.verified && a.type === 'agency') out.push(`<span class="badge badge-agency"><i class="ph-fill ph-seal-check"></i>ISHONCHLI AGENTLIK</span>`);
    else if (l.verified) out.push(`<span class="badge badge-verified"><i class="ph-fill ph-seal-check"></i>TASDIQLANGAN EGASI</span>`);
    if (l.tg) out.push(`<span class="badge badge-tg"><i class="ph-fill ph-telegram-logo"></i>KANALDA</span>`);
    return out.join('');
  }

  function propertyCard(l, opts = {}) {
    const m = l.mortgage ? mortgage({ price:l.price, downPct:15, years:15, rate:17 }) : null;
    return `
<article class="pcard" data-id="${l.id}" tabindex="0">
  <div class="pcard-media">
    <i class="ph-duotone ph-image"></i>
    <div class="pcard-badges">${badges(l)}</div>
    <button class="pcard-fav" data-fav="${l.id}" aria-pressed="${isFav(l.id)}" aria-label="Sevimlilarga">
      <i class="ph${isFav(l.id) ? '-fill' : ''} ph-heart"></i>
    </button>
    <span class="pcard-count"><i class="ph ph-image"></i> ${l.photos}</span>
  </div>
  <div class="pcard-body">
    <div class="pcard-price">
      <b class="num">${priceLabel(l)}</b>
      <span>${l.deal === 'sale' || l.deal === 'new' ? ppm(l) : dealLabel(l.deal)}</span>
    </div>
    <div class="pcard-title">${titleOf(l)}${l.floors ? ` · ${l.floor}/${l.floors} qavat` : ''}</div>
    <div class="pcard-place"><i class="ph ph-map-pin"></i>${placeOf(l)}${l.metro ? ` · ${l.metro} ${l.metroMin} daq` : ''}</div>
    ${m ? `<div class="pcard-place" style="color:var(--emerald);font-weight:700"><i class="ph ph-calculator"></i>Ipoteka ${usd(m.monthly)}/oy</div>` : ''}
    <div class="pcard-specs">${trustBadges(l)}</div>
    <div class="pcard-foot">
      <span class="caption">${l.created}</span>
      <div class="pcard-actions">
        <button class="btn btn-icon btn-sm" data-compare="${l.id}" title="Taqqoslash"><i class="ph ph-scales"></i></button>
        <button class="btn btn-primary btn-sm" data-contact="${l.id}"><i class="ph-fill ph-phone"></i>Aloqa</button>
      </div>
    </div>
  </div>
</article>`;
  }

  /* ---------------- aloqa modali ---------------- */
  function contactModal(l) {
    const a = D.AGENTS.find(x => x.id === l.agent) || D.AGENTS[0];
    const el = document.createElement('div');
    el.className = 'scrim';
    el.innerHTML = `
<div class="modal" role="dialog" aria-modal="true" aria-label="Aloqa">
  <div class="agent">
    <div class="ava"><i class="ph-duotone ph-user"></i></div>
    <div class="stack" style="gap:3px;flex:1">
      <b style="font-size:15px">${a.name}</b>
      <span class="tiny" style="color:var(--emerald);font-weight:700">
        <i class="ph-fill ph-seal-check"></i> ${a.type === 'agency' ? `Ishonchli agentlik · ${a.listings} e'lon` : 'Tasdiqlangan egasi'}
      </span>
    </div>
    <button class="btn btn-icon" data-close><i class="ph ph-x"></i></button>
  </div>
  <a class="btn btn-primary btn-lg btn-block" href="tel:${a.phone.replace(/\s/g,'')}"><i class="ph-fill ph-phone"></i>${a.phone}</a>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:9px">
    <a class="btn btn-tg" href="https://t.me/uyim_bot" target="_blank" rel="noopener"><i class="ph-fill ph-telegram-logo"></i>Telegram</a>
    <button class="btn btn-outline" data-chat><i class="ph ph-chat-circle-dots"></i>Ilova chati</button>
  </div>
  <div class="note"><i class="ph-duotone ph-shield-check"></i>
    Oldindan to'lov qilmang. Kelishuvni notariusda rasmiylashtiring — Uyim vositachini tekshiradi.</div>
  <div class="tgnote"><i class="ph-fill ph-telegram-logo"></i>
    Bu e'lon <b>@${l.district}_uylar</b> kanalida ham chiqqan</div>
</div>`;
    el.addEventListener('click', e => {
      if (e.target === el || e.target.closest('[data-close]')) el.remove();
      if (e.target.closest('.btn-primary[href^="tel:"]')) syncApi?.sendLead(l.id, 'call').catch(() => {});
      if (e.target.closest('.btn-tg')) syncApi?.sendLead(l.id, 'telegram').catch(() => {});
      if (e.target.closest('[data-chat]')) { el.remove(); toast("Ilova ichida chat ochildi"); syncApi?.sendLead(l.id, 'chat').catch(() => {}); }
    });
    document.body.appendChild(el);
  }

  /* ---------------- toast ---------------- */
  let toastEl;
  function toast(msg, icon = 'ph-check-circle') {
    toastEl?.remove();
    toastEl = document.createElement('div');
    toastEl.className = 'toast';
    toastEl.innerHTML = `<i class="ph-fill ${icon}"></i>${msg}`;
    document.body.appendChild(toastEl);
    setTimeout(() => toastEl?.remove(), 2600);
  }

  /* ---------------- tema / til ---------------- */
  function applyTheme(t) {
    document.documentElement.dataset.theme = t;
    write(LS.theme, t);
    document.querySelectorAll('[data-theme-toggle] i').forEach(i => {
      i.className = t === 'dark' ? 'ph-fill ph-sun' : 'ph ph-moon-stars';
    });
    document.dispatchEvent(new CustomEvent('uyim:theme', { detail:{ theme:t } }));
  }
  function initTheme() {
    const saved = read(LS.theme, null);
    applyTheme(saved || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  }
  function applyLang(l) {
    write(LS.lang, l);
    document.documentElement.lang = l;
    document.querySelectorAll('[data-lang]').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === l));
    // to'liq lug'at backend/i18n bosqichida ulanadi — chrome darajasida almashtiriladi
    document.querySelectorAll('[data-i18n]').forEach(n => {
      const dict = I18N[l]; const k = n.dataset.i18n;
      if (dict && dict[k]) n.textContent = dict[k];
    });
  }
  const I18N = {
    uz:{ search:"Qidirish", buy:"Sotib olish", rent:"Ijaraga", login:"Kirish", post:"E'lon joylash" },
    ru:{ search:"Поиск", buy:"Купить", rent:"Аренда", login:"Войти", post:"Разместить" },
    en:{ search:"Search", buy:"Buy", rent:"Rent", login:"Sign in", post:"Post a listing" }
  };

  /* ---------------- xarita (Leaflet, kalitsiz OSM) ---------------- */
  function initMap(node, { center = [41.2995,69.2401], zoom = 12 } = {}) {
    if (!window.L) return null;
    const map = L.map(node, { zoomControl:false, attributionControl:false }).setView(center, zoom);
    const url = document.documentElement.dataset.theme === 'dark'
      ? 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
    let layer = L.tileLayer(url, { maxZoom:19 }).addTo(map);
    L.control.zoom({ position:'bottomright' }).addTo(map);
    document.addEventListener('uyim:theme', e => {
      layer.remove();
      layer = L.tileLayer(e.detail.theme === 'dark'
        ? 'https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        : 'https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { maxZoom:19 }).addTo(map);
    });
    return map;
  }
  const priceMarker = l => L.marker([l.lat, l.lng], {
    icon: L.divIcon({ className:'', html:`<span class="pin${l.verified ? ' is-verified' : ''}" data-pin="${l.id}">${pinLabel(l)}</span>`, iconSize:null })
  });

  /* ---------------- sahifa yuklash ---------------- */
  function mount({ active, mobile } = {}) {
    initTheme();
    document.body.insertAdjacentHTML('afterbegin', header(active));
    document.body.insertAdjacentHTML('beforeend', footer() + mobileNav(mobile));
    applyLang(read(LS.lang, 'uz'));
    document.addEventListener('click', e => {
      const t = e.target;
      if (t.closest('[data-theme-toggle]')) applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
      const lg = t.closest('[data-lang]'); if (lg) applyLang(lg.dataset.lang);
      const fav = t.closest('[data-fav]');
      if (fav) {
        e.stopPropagation();
        const on = toggleFav(fav.dataset.fav);
        fav.setAttribute('aria-pressed', on);
        fav.querySelector('i').className = `ph${on ? '-fill' : ''} ph-heart`;
      }
      const cmp = t.closest('[data-compare]'); if (cmp) { e.stopPropagation(); toggleCompare(cmp.dataset.compare); }
      const c = t.closest('[data-contact]');
      if (c) { e.stopPropagation(); const l = byId(c.dataset.contact); if (l) contactModal(l); }
      const card = t.closest('.pcard[data-id]');
      if (card && !t.closest('button')) location.href = `listing.html?id=${card.dataset.id}`;
    });
  }

  const qs = k => new URLSearchParams(location.search).get(k);
  // Listing ids come back from the API as numbers; URL query params are always strings —
  // compare loosely so `listing.html?id=2` still resolves against a real numeric l.id.
  const byId = id => D.LISTINGS.find(l => String(l.id) === String(id));

  return { mount, state, isFav, toggleFav, inCompare, toggleCompare, usd, uzs, nf, priceLabel, ppm,
           pinLabel, titleOf, placeOf, dealLabel, badges, trustBadges, propertyCard, contactModal,
           mortgage, toast, initMap, priceMarker, qs, byId, applyTheme, applyLang, I18N };
})();
