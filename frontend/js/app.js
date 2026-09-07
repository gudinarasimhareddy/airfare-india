/**
 * AirfareX India — Main Application Controller
 * Handles Instant Multi-Airline Comparison, Tourist Packages, Tabs, Search,
 * Filtering, API Sync, Modals, Charts, Theme Toggling, Language Localization,
 * Smart Price Prediction, and DGCA Refund Tracking
 */

let state = {
  currentTab: 'home',
  sortMode: 'score',
  activeTrendPeriod: '30D',
  theme: localStorage.getItem('airfarex_theme') || 'light',
  flights: [],
  routes: [],
  alerts: [],
  touristPlans: [],
  selectedPackage: null,
  overview: null,
  cpiSimulation: null,
  predictionData: null,
  currentRefund: null,
  aiRecommendations: null,
  userPreferences: null,
  selectedComparisonFlights: [],
  selectedFlight: null
};

// =========================================================
// INSTANT MULTI-AIRLINE COMPARISON UPON PLACE SELECTION
// =========================================================
function extractAirportCode(str) {
  if (!str) return 'DEL';
  const match = str.match(/\(([A-Z]{3})\)/);
  if (match) return match[1];
  const cleaned = str.trim().toUpperCase();
  if (cleaned.length === 3) return cleaned;
  if (cleaned.includes('HYD') || cleaned.includes('HYDERABAD')) return 'HYD';
  if (cleaned.includes('DEL') || cleaned.includes('DELHI')) return 'DEL';
  if (cleaned.includes('BOM') || cleaned.includes('MUMBAI')) return 'BOM';
  if (cleaned.includes('BLR') || cleaned.includes('BENGALURU') || cleaned.includes('BANGALORE')) return 'BLR';
  if (cleaned.includes('GOI') || cleaned.includes('GOA')) return 'GOI';
  if (cleaned.includes('CCU') || cleaned.includes('KOLKATA')) return 'CCU';
  if (cleaned.includes('MAA') || cleaned.includes('CHENNAI')) return 'MAA';
  if (cleaned.includes('PNQ') || cleaned.includes('PUNE')) return 'PNQ';
  if (cleaned.includes('JAI') || cleaned.includes('JAIPUR')) return 'JAI';
  return 'DEL';
}

function handleHomePlaceChange() {
  const fromVal = document.getElementById('fromCity')?.value || 'HYD';
  const toVal = document.getElementById('toCity')?.value || 'DEL';
  const orig = extractAirportCode(fromVal);
  const dest = extractAirportCode(toVal);

  if (orig && dest && orig !== dest) {
    renderInstantSectorComparison('home', orig, dest);
  }
}

function updateExplorerComparison() {
  const fromVal = document.getElementById('fFrom')?.value || 'HYD';
  const toVal = document.getElementById('fTo')?.value || 'DEL';
  const orig = extractAirportCode(fromVal);
  const dest = extractAirportCode(toVal);

  if (orig && dest && orig !== dest) {
    renderInstantSectorComparison('explorer', orig, dest);
  }
}

function selectDestinationSector(orig, dest, label) {
  const fromInput = document.getElementById('fromCity');
  const toInput = document.getElementById('toCity');
  if (fromInput) fromInput.value = `${orig} (${orig})`;
  if (toInput) toInput.value = label || `${dest} (${dest})`;

  showToast(`Selected Sector ${orig} ➔ ${dest}`);
  renderInstantSectorComparison('home', orig, dest);

  const compCard = document.getElementById('homeComparisonCard');
  if (compCard) {
    compCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

async function renderInstantSectorComparison(target, orig, dest) {
  const badge = document.getElementById('instantCompRouteBadge');
  if (badge) {
    badge.textContent = `✈ ${orig} ➔ ${dest} · Instant Comparison`;
  }

  const expLabel = document.getElementById('expCompSectorLabel');
  if (expLabel) {
    expLabel.textContent = `${orig} ➔ ${dest} Multi-Airline Benchmark`;
  }

  // Also sync the comparison tab selects
  const compOrig = document.getElementById('compOriginSelect');
  const compDest = document.getElementById('compDestSelect');
  if (compOrig && compOrig.value !== orig) compOrig.value = orig;
  if (compDest && compDest.value !== dest) compDest.value = dest;

  const tableBody = document.getElementById('homeComparisonTableBody');
  const winnersGrid = document.getElementById('homeCompWinnersGrid');

  if (tableBody) {
    tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:24px; color:var(--text-muted);">Comparing real-time fares for ${orig} ➔ ${dest}...</td></tr>`;
  }

  try {
    const data = await window.api.compareSector(orig, dest);
    
    // Render Winner Cards on Home
    if (winnersGrid && data.highlights) {
      const h = data.highlights;
      winnersGrid.innerHTML = `
        <div class="comp-winner-card green">
          <div class="metric-title">💸 Lowest Fare Champion</div>
          <div class="metric good">₹${h.cheapest.fare.toLocaleString('en-IN')}</div>
          <div class="metric-sub">${h.cheapest.airline} · Best Value</div>
        </div>
        <div class="comp-winner-card cyan">
          <div class="metric-title">⏱️ Punctuality Leader (OTP)</div>
          <div class="metric">${h.most_punctual.otp}</div>
          <div class="metric-sub">${h.most_punctual.airline} · On-Time Arrival</div>
        </div>
        <div class="comp-winner-card gold">
          <div class="metric-title">💺 Best Comfort & Free Meals</div>
          <div class="metric" style="font-size:18px;">${h.most_comfortable.pitch}</div>
          <div class="metric-sub">${h.most_comfortable.airline}</div>
        </div>
        <div class="comp-winner-card purple">
          <div class="metric-title">🌿 Lowest Carbon Footprint</div>
          <div class="metric" style="font-size:18px;">${h.most_eco_friendly.emissions}</div>
          <div class="metric-sub">${h.most_eco_friendly.airline} · Modern Fleet</div>
        </div>
      `;
    }

    // Render Table Rows on Home
    if (tableBody && data.airlines) {
      tableBody.innerHTML = data.airlines.map(al => `
        <tr>
          <td>
            <div class="airline-badge-cell">
              <span class="airline-dot" style="background:${al.color};"></span>
              <b>${al.airline}</b>
            </div>
            <div style="font-size:10.5px; color:var(--text-subtle); margin-top:2px;">${al.badge}</div>
          </td>
          <td>
            <b style="font-size:15px; font-family:'JetBrains Mono',monospace; color:var(--brand-mint);">₹${al.total_fare.toLocaleString('en-IN')}</b>
            <div style="font-size:11px; color:var(--text-muted);">Base ₹${al.base_fare.toLocaleString('en-IN')}</div>
          </td>
          <td><span style="font-size:12.5px;">${al.cabin_baggage}</span></td>
          <td><b style="color:var(--brand-cyan);">${al.checked_baggage}</b></td>
          <td>${al.seat_pitch_inch}" Legroom</td>
          <td><span class="badge ${al.otp_percentage >= 85 ? 'green' : 'amber'}">${al.otp_percentage}%</span></td>
          <td style="font-size:12px;">${al.meals_policy}</td>
          <td style="font-family:'JetBrains Mono',monospace;">₹${al.cancellation_fee.toLocaleString('en-IN')}</td>
          <td>
            <button class="btn sm" onclick="selectFlight('${al.airline}', '${al.iata} 101', ${al.total_fare}, '${dest}', '${dest}')" style="padding:4px 10px; font-size:11px;">
              Select Fare ✈
            </button>
          </td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load instant comparison:', err);
    if (tableBody) {
      tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:20px; color:var(--text-muted);">Comparison available in the Compare Airlines tab.</td></tr>`;
    }
  }
}

// Multi-Theme Switching Functionality
function setThemeMode(theme) {
  state.theme = theme;
  applyTheme(theme);
}

function toggleTheme() {
  const nextTheme = state.theme === 'light' ? 'aurora' : 'light';
  setThemeMode(nextTheme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('airfarex_theme', theme);
  const sel = document.getElementById('themeSelector');
  if (sel) sel.value = theme;
  const btn = document.getElementById('themeToggleBtn');
  if (btn) {
    btn.innerHTML = theme === 'light' ? '☀️' : '🌙';
  }
}

// Toast notification helper
function showToast(message, isSuccess = true) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast-message';
  toast.innerHTML = `<span>${isSuccess ? '✓' : 'ℹ'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2600);
}

// Destination Quick Search
function searchDestination(code, fullName) {
  const toCityInput = document.getElementById('toCity');
  const fToInput = document.getElementById('fTo');
  if (toCityInput) toCityInput.value = fullName;
  if (fToInput) fToInput.value = code;

  showToast(`Searching lowest fares to ${fullName}...`);
  const explorerNav = document.querySelector('.main-nav a[data-tab="explorer"]');
  showTab('explorer', explorerNav);
  loadFlights();
}

// Admin Portal Subtab Switcher
function switchAdminPortalTab(subId, btn) {
  const subtabs = ['routes', 'index', 'quality'];
  subtabs.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('hidden', id !== subId);
  });
  document.querySelectorAll('.admin-subtab-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  if (subId === 'routes') loadRoutes();
  if (subId === 'index') loadIndexData();
  if (subId === 'quality') loadQualityData();
}

// Navigation between customer & admin views
function showTab(tabId, el, updateUrl = true) {
  let targetTab = tabId;
  let adminSubtab = null;
  if (['routes', 'index', 'quality'].includes(tabId)) {
    targetTab = 'admin';
    adminSubtab = tabId;
  }

  const sections = ['home', 'explorer', 'comparison', 'monthly-fares', 'offers', 'tourist-plans', 'trips', 'prediction', 'refunds', 'admin', 'saved'];
  sections.forEach(id => {
    const sec = document.getElementById(id);
    if (sec) sec.classList.toggle('hidden', id !== targetTab);
  });

  // Clear active state on all nav elements
  document.querySelectorAll('.main-nav .nav-link, .nav-dropdown .dropdown-link, .mobile-drawer-link').forEach(link => {
    link.classList.remove('active');
  });

  // Set active on matching link and its parent dropdown container if any
  const activeNav = el || document.querySelector(`.main-nav a[data-tab="${targetTab}"], .main-nav .dropdown-link[data-tab="${targetTab}"]`);
  if (activeNav) {
    activeNav.classList.add('active');
    const parentNavItem = activeNav.closest('.nav-item');
    if (parentNavItem) {
      const parentBtn = parentNavItem.querySelector('.nav-link');
      if (parentBtn) parentBtn.classList.add('active');
    }
  }

  // Update mobile drawer active states as well
  const mobileLink = document.querySelector(`.mobile-drawer-link[data-tab="${targetTab}"]`);
  if (mobileLink) mobileLink.classList.add('active');

  state.currentTab = targetTab;

  // Sync URL query state without full page reload
  if (updateUrl && typeof window !== 'undefined' && window.history && window.history.pushState) {
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('tab', targetTab);
      if (targetTab === 'explorer') {
        const fromVal = document.getElementById('fFrom')?.value || document.getElementById('fromCity')?.value;
        const toVal = document.getElementById('fTo')?.value || document.getElementById('toCity')?.value;
        const dateVal = document.getElementById('departDate')?.value;
        if (fromVal) url.searchParams.set('from', extractAirportCode(fromVal));
        if (toVal) url.searchParams.set('to', extractAirportCode(toVal));
        if (dateVal) url.searchParams.set('date', dateVal);
      }
      window.history.pushState({ tab: targetTab }, '', url.toString());
    } catch (e) {
      // Ignore URL history errors in embedded contexts
    }
  }

  // Handle Admin portal subtab
  if (targetTab === 'admin') {
    const sub = adminSubtab || 'routes';
    const subBtn = document.getElementById(`adminBtn${sub.charAt(0).toUpperCase() + sub.slice(1)}`);
    if (subBtn && typeof switchAdminPortalTab === 'function') {
      switchAdminPortalTab(sub, subBtn);
    }
  }

  // Trigger contextual data loads
  if (targetTab === 'explorer') loadFlights();
  if (targetTab === 'comparison') loadSectorComparison();
  if (targetTab === 'monthly-fares') loadMonthlyCalendar();
  if (targetTab === 'offers') loadOffers();
  if (targetTab === 'tourist-plans') loadTouristPlans();
  if (targetTab === 'trips') loadMyTrips();
  if (targetTab === 'prediction') runPricePrediction();
  if (targetTab === 'refunds') trackRefundStatus('AIRX789');
  if (targetTab === 'saved') loadAlerts();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Mobile Drawer Navigation Toggle
function toggleMobileMenu() {
  const drawer = document.getElementById('mobileDrawer');
  const backdrop = document.getElementById('mobileDrawerBackdrop');
  if (drawer && backdrop) {
    const isOpen = drawer.classList.toggle('open');
    backdrop.classList.toggle('open', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  }
}
window.toggleMobileMenu = toggleMobileMenu;

// Switch directly to an Admin subtab (e.g. routes) from any menu
function showAdminSubtab(subId) {
  showTab(subId);
}
window.showAdminSubtab = showAdminSubtab;

// Customer Trip Type Selector
let currentTripType = 'oneway';
function setTripType(type) {
  currentTripType = type;
  const tabOneWay = document.getElementById('tabOneWay');
  const tabRoundTrip = document.getElementById('tabRoundTrip');
  const returnWrap = document.getElementById('returnDateFieldWrap');
  const returnDate = document.getElementById('returnDate');

  if (type === 'roundtrip') {
    if (tabOneWay) tabOneWay.classList.remove('active');
    if (tabRoundTrip) tabRoundTrip.classList.add('active');
    if (returnWrap) returnWrap.style.opacity = '1';
    if (returnDate && !returnDate.value) {
      const depVal = document.getElementById('departDate')?.value;
      const baseDate = depVal ? new Date(depVal) : new Date();
      returnDate.value = new Date(baseDate.getTime() + 86400000 * 4).toISOString().slice(0, 10);
    }
    showToast('Round Trip selected. Return date added.');
  } else {
    if (tabOneWay) tabOneWay.classList.add('active');
    if (tabRoundTrip) tabRoundTrip.classList.remove('active');
    if (returnWrap) returnWrap.style.opacity = '0.5';
    showToast('One Way flight selected.');
  }
}

function enableRoundTrip() {
  setTripType('roundtrip');
}

// Airport Origin / Destination Swap
function swapOriginDest() {
  const from = document.getElementById('fromCity');
  const to = document.getElementById('toCity');
  if (from && to) {
    const tmp = from.value;
    from.value = to.value;
    to.value = tmp;
  }
  const fFrom = document.getElementById('fFrom');
  const fTo = document.getElementById('fTo');
  if (fFrom && fTo) {
    const tmp = fFrom.value;
    fFrom.value = fTo.value;
    fTo.value = tmp;
  }
  handleHomePlaceChange();
  const fromLabel = from ? from.value : (fFrom ? fFrom.value : 'Origin');
  const toLabel = to ? to.value : (fTo ? fTo.value : 'Destination');
  showToast(`Swapped: ${fromLabel} ➔ ${toLabel}`);
}

// AI Recommendation Category Filter & Recommendations (Issue #3 & #7)
const aiRecommendationsData = {
  all: {
    airline: 'IndiGo',
    flight_no: '6E-2341',
    fare: 5240,
    destCode: 'BLR',
    destCity: 'Bengaluru',
    title: 'IndiGo 6E 2341 · 06:30 DEL ➔ 09:10 BLR',
    reasons: [
      '<b>₹1,840 cheaper</b> than 7-day average route fare',
      '<b>Non-stop direct</b> flight (2h 40m total duration)',
      '<b>Optimal morning</b> departure slot',
      '<b>94% on-time</b> historical DGCA performance'
    ]
  },
  cheapest: {
    airline: 'Akasa Air',
    flight_no: 'QP-1382',
    fare: 4390,
    destCode: 'BLR',
    destCity: 'Bengaluru',
    title: 'Akasa Air QP 1382 · 11:45 DEL ➔ 14:30 BLR',
    reasons: [
      '<b>₹2,690 cheaper</b> — lowest fare observed this week',
      '<b>Non-stop direct</b> flight (2h 45m)',
      '<b>USB charging & extra legroom</b> at every seat',
      '<b>Zero change fees</b> if booked 7+ days in advance'
    ]
  },
  fastest: {
    airline: 'Air India',
    flight_no: 'AI-804',
    fare: 5850,
    destCode: 'BLR',
    destCity: 'Bengaluru',
    title: 'Air India AI 804 · 18:15 DEL ➔ 20:45 BLR',
    reasons: [
      '<b>Fastest sector time</b> (2h 30m non-stop direct)',
      '<b>Terminal 3 departure</b> with DigiYatra express lanes',
      '<b>Complimentary hot meal & beverages</b> included',
      '<b>25kg checked baggage</b> allowance included'
    ]
  },
  family: {
    airline: 'Air India Express',
    flight_no: 'IX-1422',
    fare: 4980,
    destCode: 'BLR',
    destCity: 'Bengaluru',
    title: 'AI Express IX 1422 · 08:30 DEL ➔ 11:20 BLR',
    reasons: [
      '<b>Best family departure time</b> (no late-night arrival)',
      '<b>Adjacent family seats</b> auto-allocated with zero fee',
      '<b>Warm snack box</b> included for all passengers',
      '<b>20kg baggage</b> allowance for easier packing'
    ]
  }
};

function filterByAiCategory(cat, btn) {
  document.querySelectorAll('.ai-compare-chip').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const rec = aiRecommendationsData[cat] || aiRecommendationsData.all;
  const titleEl = document.getElementById('aiPickFlightTitle');
  const fareEl = document.getElementById('aiPickFare');
  const reasonsEl = document.querySelector('.ai-reasons-grid');

  if (titleEl) titleEl.textContent = rec.title;
  if (fareEl) fareEl.textContent = `₹${rec.fare.toLocaleString('en-IN')}`;
  if (reasonsEl && rec.reasons) {
    reasonsEl.innerHTML = rec.reasons.map(r => `
      <div class="ai-reason-item">
        <span class="check-icon">✓</span>
        <div>${r}</div>
      </div>
    `).join('');
  }

  const ctaBtn = document.querySelector('#aiHeroPickCard button.btn.green');
  if (ctaBtn) {
    ctaBtn.onclick = () => selectFlight(rec.airline, rec.flight_no, rec.fare, rec.destCode, rec.destCity);
  }
}

// Initial Data Bootstrapper
async function initApp() {
  // Apply saved theme
  applyTheme(state.theme);

  // Apply saved language
  if (window.i18n) {
    const lang = localStorage.getItem('airfarex_lang') || 'en';
    window.i18n.setLanguage(lang);
  }

  // Immediately load instant place comparison on Home
  handleHomePlaceChange();

  // Set default dates (today + 7 days)
  const defaultDate = new Date(Date.now() + 86400000 * 7).toISOString().slice(0, 10);
  const dateInput = document.getElementById('departDate');
  if (dateInput) dateInput.value = defaultDate;

  const predDate = document.getElementById('predDate');
  if (predDate) predDate.value = defaultDate;

  const statusDate = document.getElementById('statusDate');
  if (statusDate) statusDate.value = new Date().toISOString().slice(0, 10);

  // Load overview metrics and trend chart
  await loadOverview();
  await loadTrendChart('30D');

  // Render initial network map
  Charts.renderNetworkMap('routeNetworkMap');

  // Load initial alerts count
  await loadAlerts();

  // Load AI user preferences
  await loadUserPreferences();
}

// Load National Overview Metrics
async function loadOverview() {
  try {
    const data = await window.api.getApixOverview();
    state.overview = data;

    const elApix = document.getElementById('kpiApix');
    if (elApix) elApix.textContent = data.national_apix ? data.national_apix.toFixed(1) : '131.8';

    const elAvgFare = document.getElementById('kpiAvgFare');
    if (elAvgFare) elAvgFare.textContent = `₹${(data.average_domestic_fare || 4850).toLocaleString('en-IN')}`;

    const elQuotes = document.getElementById('kpiQuotes');
    if (elQuotes) elQuotes.textContent = data.quotes_processed || '48,290';

    const elConfidence = document.getElementById('kpiConfidence');
    if (elConfidence) elConfidence.textContent = `${data.data_confidence_pct || 98.4}%`;
  } catch (err) {
    console.debug('Using demo dataset dashboard stats fallback:', err);
    if (window.AirfarexDemoData) {
      const stats = window.AirfarexDemoData.getDashboardStats();
      const elApix = document.getElementById('kpiApix');
      if (elApix) elApix.textContent = '132.4';

      const elAvgFare = document.getElementById('kpiAvgFare');
      if (elAvgFare) elAvgFare.textContent = `₹${stats.avgPrice.toLocaleString('en-IN')}`;

      const elQuotes = document.getElementById('kpiQuotes');
      if (elQuotes) elQuotes.textContent = `${stats.totalFlights * 1850}+`;

      const elConfidence = document.getElementById('kpiConfidence');
      if (elConfidence) elConfidence.textContent = '99.2%';
    }
  }
}

// Load Trend Chart for 30D, 90D, 1Y
async function loadTrendChart(period = '30D') {
  state.activeTrendPeriod = period;
  document.querySelectorAll('.tab-btn[data-trend]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.trend === period);
  });

  try {
    const res = await window.api.getApixTrend(period);
    Charts.renderTrendBars('trendChartBars', res.points);
  } catch (err) {
    console.error('Failed to load trend chart:', err);
  }
}

// =========================================================
// HOMEPAGE FEATURED FLIGHT DISCOVERY & INTELLIGENCE
// =========================================================

async function loadHomepageFeaturedFlights(orig = 'DEL', dest = 'BOM') {
  const container = document.getElementById('homeFlightResults');
  if (container) {
    container.innerHTML = `
      <div class="skeleton-card">
        <div class="skeleton-shimmer"></div>
        <div class="skeleton-line lg" style="width:32%;"></div>
        <div class="skeleton-line md" style="width:65%;"></div>
        <div class="skeleton-line sm" style="width:40%;"></div>
      </div>
      <div class="skeleton-card">
        <div class="skeleton-shimmer"></div>
        <div class="skeleton-line lg" style="width:28%;"></div>
        <div class="skeleton-line md" style="width:58%;"></div>
        <div class="skeleton-line sm" style="width:45%;"></div>
      </div>
    `;
  }

  const routeBadge = document.getElementById('homeFeaturedRouteBadge');
  if (routeBadge) routeBadge.textContent = `✈ ${orig} ➔ ${dest} · Today's Flight Deals`;

  const compBadge = document.getElementById('instantCompRouteBadge');
  if (compBadge) compBadge.textContent = `✈ ${orig} ➔ ${dest} · Instant Comparison`;

  try {
    let flights = [];
    let bestFare = 0;
    let envelope = null;
    let aiRec = null;

    // First try demo data provider if loaded
    if (window.AirfarexDemoData) {
      flights = window.AirfarexDemoData.filterFlights({ from_city: orig, to_city: dest });
      if (flights.length > 0) {
        bestFare = Math.min(...flights.map(f => f.totalPrice || f.total_fare));
        envelope = { data_source: 'DEMO', provider: 'AirfareX Master Demo Dataset', cached: false };
        aiRec = window.AirfarexDemoData.getRecommendations(flights);
      }
    }

    // Try backend if demo dataset did not match or for live sync
    if (!flights || flights.length === 0) {
      try {
        const searchParams = { from_city: orig, to_city: dest };
        const data = await window.api.searchFlights(searchParams);
        if (data && data.flights && data.flights.length > 0) {
          flights = data.flights;
          bestFare = data.best_fare || Math.min(...flights.map(f => f.total_fare));
          envelope = data;
        }
      } catch (apiErr) {
        console.warn('Backend search fallback to demo data:', apiErr);
      }
    }

    // If still empty, fall back to master list
    if (!flights || flights.length === 0) {
      flights = window.AirfarexDemoData ? window.AirfarexDemoData.getAllFlights().slice(0, 6) : [];
      bestFare = flights.length > 0 ? Math.min(...flights.map(f => f.totalPrice)) : 4290;
      envelope = { data_source: 'DEMO', provider: 'AirfareX Master Dataset' };
      aiRec = window.AirfarexDemoData ? window.AirfarexDemoData.getRecommendations(flights) : null;
    }

    // Update data source badge
    const srcBadge = document.getElementById('homeFeaturedDataSourceBadge');
    if (srcBadge) {
      srcBadge.className = 'data-source-pill badge-live';
      srcBadge.textContent = 'DEMO ACTIVE (26+ Flights)';
      srcBadge.style.cssText = 'background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3);';
    }

    const subtitle = document.getElementById('homeFeaturedSubtitle');
    if (subtitle) {
      subtitle.textContent = `Showing ${flights.length} verified demo flights for ${orig} ➔ ${dest} · Best Fare: ₹${bestFare.toLocaleString('en-IN')} · Deterministic Scoring & DGCA Breakdown`;
    }

    // Render recommendations and cards
    renderHomeAiRecommendationsSummary(aiRec);
    renderHomeFlightCards(flights, bestFare, envelope, aiRec);

    // Fetch and render Price Intelligence
    try {
      const predData = await window.api.predictPrice(orig, dest);
      renderHomePriceIntelligence(predData, orig, dest);
    } catch (pErr) {
      console.debug('Price prediction fallback:', pErr);
    }

    // Also update comparison matrix for this sector
    renderInstantSectorComparison('home', orig, dest);

  } catch (err) {
    console.error('Failed to load homepage featured flights:', err);
    if (container) {
      container.innerHTML = `
        <div class="friendly-error-card">
          <div class="friendly-error-icon">📡</div>
          <h3 class="friendly-error-title">Unable to Fetch Flight Deals</h3>
          <p class="friendly-error-desc">Could not retrieve development schedules for ${orig} ➔ ${dest}.</p>
          <button class="btn primary sm" onclick="loadHomepageFeaturedFlights('${orig}', '${dest}')">Retry</button>
        </div>
      `;
    }
  }
}

// Render AI 4-Card Summary Bar on Homepage
function renderHomeAiRecommendationsSummary(rec) {
  const banner = document.getElementById('homeAiSummaryGrid');
  if (!banner || !rec) {
    if (banner) banner.innerHTML = '';
    return;
  }

  const pick = rec.airfarex_pick;
  const bestVal = rec.best_value;
  const cheapest = rec.cheapest;
  const fastest = rec.fastest;

  if (!pick && !cheapest && !fastest) {
    banner.innerHTML = '';
    return;
  }

  banner.innerHTML = `
    <!-- 1. AirfareX Pick / Best Overall -->
    ${pick ? `
      <div class="ai-rec-card card-pick" onclick="openFlightDetailsModal('${pick.flightNumber || pick.flight_no}')" title="Click to view full flight details & score breakdown" style="cursor:pointer;">
        <div class="ai-rec-card-tag">👑 Best Overall</div>
        <div class="ai-rec-flight-title">${pick.airline} · ${pick.flightNumber || pick.flight_no}</div>
        <div class="ai-rec-flight-sub">${pick.duration} · ${pick.stops}</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(pick.totalPrice || pick.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill">⭐ ${pick.overallScore || pick.scores?.overall_score || 92}/100</span>
        </div>
      </div>
    ` : ''}

    <!-- 2. Best Value -->
    ${bestVal ? `
      <div class="ai-rec-card card-best-value" onclick="openFlightDetailsModal('${bestVal.flightNumber || bestVal.flight_no}')" title="Click to view full flight details & score breakdown" style="cursor:pointer;">
        <div class="ai-rec-card-tag">💎 Best Value</div>
        <div class="ai-rec-flight-title">${bestVal.airline} · ${bestVal.flightNumber || bestVal.flight_no}</div>
        <div class="ai-rec-flight-sub">${bestVal.duration} · ${bestVal.stops}</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(bestVal.totalPrice || bestVal.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill" style="background:rgba(16,185,129,0.15); color:#34d399;">⭐ ${bestVal.overallScore || 90}/100</span>
        </div>
      </div>
    ` : ''}

    <!-- 3. Lowest Price -->
    ${cheapest ? `
      <div class="ai-rec-card card-cheapest" onclick="openFlightDetailsModal('${cheapest.flightNumber || cheapest.flight_no}')" title="Click to view full flight details & score breakdown" style="cursor:pointer;">
        <div class="ai-rec-card-tag">💸 Lowest Price</div>
        <div class="ai-rec-flight-title">${cheapest.airline} · ${cheapest.flightNumber || cheapest.flight_no}</div>
        <div class="ai-rec-flight-sub">${cheapest.duration} · ${cheapest.stops}</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(cheapest.totalPrice || cheapest.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill" style="background:rgba(14,165,233,0.15); color:#38bdf8;">Base ₹${(cheapest.basePrice || cheapest.base_fare || (cheapest.totalPrice - 800)).toLocaleString('en-IN')}</span>
        </div>
      </div>
    ` : ''}

    <!-- 4. Fastest Travel -->
    ${fastest ? `
      <div class="ai-rec-card card-fastest" onclick="openFlightDetailsModal('${fastest.flightNumber || fastest.flight_no}')" title="Click to view full flight details & score breakdown" style="cursor:pointer;">
        <div class="ai-rec-card-tag">⚡ Fastest Travel</div>
        <div class="ai-rec-flight-title">${fastest.airline} · ${fastest.flightNumber || fastest.flight_no}</div>
        <div class="ai-rec-flight-sub">${fastest.duration} · Non-stop</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(fastest.totalPrice || fastest.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill" style="background:rgba(245,158,11,0.15); color:#fbbf24;">${fastest.duration}</span>
        </div>
      </div>
    ` : ''}
  `;
}

// Render Polished Flight Result Cards on Homepage
function renderHomeFlightCards(flights, bestFare, searchEnvelope = null, aiRec = null) {
  const container = document.getElementById('homeFlightResults');
  if (!container) return;

  if (!flights || !flights.length) {
    container.innerHTML = `
      <div class="friendly-empty-card">
        <div class="friendly-empty-icon">✈️</div>
        <h3 class="friendly-empty-title">No Flights Available for this Exact Sector</h3>
        <p class="friendly-empty-desc">Explore one of our high-frequency demo sectors with comprehensive pricing & scores:</p>
        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin:14px 0;">
          <button class="btn sm light" onclick="selectDemoRoute('HYD', 'DEL')">⚡ Hyderabad ➔ Delhi</button>
          <button class="btn sm light" onclick="selectDemoRoute('HYD', 'BOM')">⚡ Hyderabad ➔ Mumbai</button>
          <button class="btn sm light" onclick="selectDemoRoute('BLR', 'DEL')">⚡ Bengaluru ➔ Delhi</button>
          <button class="btn sm light" onclick="selectDemoRoute('BOM', 'DEL')">⚡ Mumbai ➔ Delhi</button>
          <button class="btn sm green" onclick="exploreDemoFlights()">🌐 View All 20+ Demo Flights</button>
        </div>
        <button class="btn primary sm" onclick="loadHomepageFeaturedFlights('HYD', 'DEL')">Reset to HYD ➔ DEL</button>
      </div>
    `;
    return;
  }

  const cardsHtml = flights.map((f, idx) => {
    const flightNo = f.flightNumber || f.flight_no || `6E-${idx+200}`;
    const airline = f.airline || 'IndiGo';
    const airlineClass = `airline-${airline.toLowerCase().replace(/\s+/g, '-')}`;
    const totFare = f.totalPrice || f.total_fare || 4500;
    const baseFare = f.basePrice || f.base_fare || Math.round(totFare * 0.8);
    const taxes = f.taxes || f.taxes_fees || (totFare - baseFare);
    const depTime = f.departureTime || f.dep_time || '07:15';
    const arrTime = f.arrivalTime || f.arr_time || '09:30';
    const origCode = f.origin || f.origin_code || 'HYD';
    const destCode = f.destination || f.destination_code || 'DEL';
    const duration = f.duration || '2h 15m';
    const stops = f.stops || 'Nonstop';

    // Scoring metrics
    const overallScore = f.overallScore || f.fare_score || 92;
    const scoreRating = f.scoreRating || (overallScore >= 90 ? 'Excellent' : (overallScore >= 80 ? 'Very Good' : 'Good'));
    const ratingClass = overallScore >= 90 ? 'excellent' : (overallScore >= 80 ? 'very-good' : (overallScore >= 70 ? 'good' : 'average'));
    const priceScore = f.priceScore || 92;
    const relScore = f.reliabilityScore || 95;
    const punctScore = f.punctualityScore || f.onTimePercentage || 94;
    const comfScore = f.comfortScore || 88;

    // Smart Badge
    let badgeText = f.recommendation || (totFare <= (bestFare || 4500) ? 'Lowest Price' : (stops === 'Nonstop' ? 'Best Value' : 'Standard'));
    let badgeClass = 'best-value';
    if (badgeText.toLowerCase().includes('overall') || badgeText.toLowerCase().includes('pick')) badgeClass = 'airfarex-pick';
    else if (badgeText.toLowerCase().includes('lowest') || badgeText.toLowerCase().includes('price') || badgeText.toLowerCase().includes('cheapest')) badgeClass = 'cheapest';
    else if (badgeText.toLowerCase().includes('fastest') || badgeText.toLowerCase().includes('quick')) badgeClass = 'fastest';

    const initials = airline.split(' ').map(w => w[0]).join('').slice(0, 3).toUpperCase();

    return `
      <div class="flight-card ${airlineClass}" id="homeFlightCard_${flightNo.replace(/\s+/g, '_')}" style="margin-bottom:14px;">
        <div class="flight-row-main">
          <!-- Airline Brand & Initials/Flight No -->
          <div class="flight-airline">
            <div class="airline-name">
              <span class="airline-avatar" style="display:inline-flex; align-items:center; justify-content:center; width:32px; height:32px; border-radius:8px; background:var(--brand-blue-light, rgba(2,132,199,0.15)); color:var(--brand-blue, #0284c7); font-weight:800; font-size:12px;">${initials}</span>
              <div>
                <b style="font-size:15px; color:var(--text-main);">${airline}</b>
                <span class="flight-no-tag" style="margin-left:4px;">${flightNo}</span>
              </div>
            </div>
            <div style="display:flex; align-items:center; gap:6px; margin-top:6px; flex-wrap:wrap;">
              <span class="smart-badge ${badgeClass}" style="font-size:10px; font-weight:800; padding:3px 8px; border-radius:4px; text-transform:uppercase;">${badgeText}</span>
              <span class="score-badge-indicator ${ratingClass}" title="Composite Weighted Score">⭐ ${overallScore}/100 — ${scoreRating}</span>
            </div>
          </div>

          <!-- Schedule Times & Route -->
          <div class="flight-schedule">
            <div class="flight-time-col">
              <span class="flight-time">${depTime}</span>
              <span class="flight-airport-code">${origCode}</span>
            </div>

            <div class="flight-duration-col">
              <span class="duration-text">${duration}</span>
              <div class="route-line-wrap">
                <div class="route-line"></div>
                <div class="route-plane-icon">✈</div>
              </div>
              <span class="stops-text ${stops === 'Nonstop' ? 'nonstop' : ''}">${stops}</span>
            </div>

            <div class="flight-time-col">
              <span class="flight-time">${arrTime}</span>
              <span class="flight-airport-code">${destCode}</span>
            </div>
          </div>

          <!-- Fare Breakdown & Total -->
          <div class="flight-fare-col">
            <div class="flight-fare">₹${totFare.toLocaleString('en-IN')}</div>
            <div class="flight-fare-sub" style="font-size:11px; color:var(--text-muted);">
              Base: ₹${baseFare.toLocaleString('en-IN')} + Taxes: ₹${taxes.toLocaleString('en-IN')}
            </div>
            <div style="font-size:10.5px; color:var(--brand-mint, #10b981); font-weight:600;">✓ All Taxes & Fees Included</div>
          </div>

          <!-- Actions: Book Now, View Details, Compare, Why -->
          <div class="flight-actions-col" style="display:flex; flex-direction:column; gap:6px; align-items:flex-end;">
            <button class="btn green sm" onclick="selectFlight('${airline}', '${flightNo}', ${totFare}, '${destCode}', '${destCode}')" style="min-width:120px; font-weight:700; padding:8px 14px;">Book Now ➔</button>
            <div style="display:flex; gap:4px;">
              <button class="btn sm light" onclick="openFlightDetailsModal('${flightNo}')" title="View Full Details & Score Breakdown" style="padding:4px 8px; font-size:11.5px;">📋 Details</button>
              <button class="btn sm light" onclick="quickAddToComparison('${flightNo}')" title="Compare this flight" style="padding:4px 8px; font-size:11.5px;">⚖️ Compare</button>
              <button class="btn sm light" onclick="openWhyThisFlightModal('${flightNo}')" title="Why this score?" style="padding:4px 8px; font-size:11.5px;">💡 Why?</button>
            </div>
          </div>
        </div>

        <!-- Requirement 3: Sub-scores strip -->
        <div class="flight-subscores-strip">
          <span class="subscore-item price">💸 Price Score: <b>${priceScore}/100</b></span>
          <span style="color:rgba(255,255,255,0.15);">·</span>
          <span class="subscore-item reliability">🛡️ Reliability: <b>${relScore}/100</b></span>
          <span style="color:rgba(255,255,255,0.15);">·</span>
          <span class="subscore-item punctuality">⏱️ Punctuality: <b>${punctScore}/100</b></span>
          <span style="color:rgba(255,255,255,0.15);">·</span>
          <span class="subscore-item comfort">💺 Comfort: <b>${comfScore}/100</b></span>
          <span style="margin-left:auto; font-size:11px; color:var(--text-muted);">🧳 ${f.baggage || '7kg Cabin + 15kg Checked'}</span>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = cardsHtml;
}

// 1-Click Explore All 20+ Demo Flights
function exploreDemoFlights() {
  showTab('explorer', document.querySelector('.main-nav a[data-tab=\'explorer\']'));
  const fFrom = document.getElementById('fFrom');
  const fTo = document.getElementById('fTo');
  if (fFrom) fFrom.value = '';
  if (fTo) fTo.value = '';
  resetFlightFilters();
  showToast('Loaded all 26+ master demo flights with complete score rankings.');
}

// 1-Click Select Demo Route
function selectDemoRoute(orig, dest) {
  const fFrom = document.getElementById('fFrom');
  const fTo = document.getElementById('fTo');
  const fromCity = document.getElementById('fromCity');
  const toCity = document.getElementById('toCity');

  if (fFrom) fFrom.value = orig;
  if (fTo) fTo.value = dest;
  if (fromCity) fromCity.value = `${orig} (${orig})`;
  if (toCity) toCity.value = `${dest} (${dest})`;

  showTab('explorer', document.querySelector('.main-nav a[data-tab=\'explorer\']'));
  loadFlights();
  showToast(`Filtering demo flights for ${orig} ➔ ${dest}`);
}

// Render Price Intelligence on Homepage
function renderHomePriceIntelligence(predData, orig, dest) {
  if (!predData) return;

  const sectorBadge = document.getElementById('homePriceSectorBadge');
  if (sectorBadge) sectorBadge.textContent = `${orig} ➔ ${dest} Sector`;

  const signalBadge = document.getElementById('homePriceSignalBadge');
  if (signalBadge) {
    if (predData.recommendation === 'BUY_NOW') {
      signalBadge.className = 'badge green';
      signalBadge.textContent = '● BUY NOW RECOMMENDED';
    } else {
      signalBadge.className = 'badge orange';
      signalBadge.textContent = '● WAIT FOR PRICE DROP';
    }
  }

  const confBadge = document.getElementById('homePriceConfBadge');
  if (confBadge) confBadge.textContent = `${predData.confidence_pct || 89}% Confidence`;

  const currentFareEl = document.getElementById('homePriceCurrentFare');
  if (currentFareEl) currentFareEl.textContent = `₹${(predData.current_fare || 3980).toLocaleString('en-IN')}`;

  const deltaText = document.getElementById('homePriceDeltaText');
  if (deltaText) {
    const delta = Math.abs(predData.expected_delta_inr || 1250);
    deltaText.textContent = `Potential Savings: ₹${delta.toLocaleString('en-IN')} ${predData.recommendation === 'BUY_NOW' ? 'before surge' : 'if you wait'}`;
  }

  const signalDesc = document.getElementById('homePriceSignalDesc');
  if (signalDesc && predData.recommendation_desc) {
    signalDesc.textContent = predData.recommendation_desc;
  }

  const optimalWin = document.getElementById('homePriceOptimalWindow');
  if (optimalWin && predData.optimal_booking_window) {
    optimalWin.textContent = `Optimal Booking Window: ${predData.optimal_booking_window}.`;
  }

  const driversList = document.getElementById('homePriceDriversList');
  if (driversList && predData.price_drivers && predData.price_drivers.length) {
    driversList.innerHTML = predData.price_drivers.slice(0, 3).map(driver => `
      <div style="font-size:12px; color:var(--text-secondary); display:flex; align-items:flex-start; gap:6px;">
        <span style="color:var(--brand-blue);">•</span> ${driver}
      </div>
    `).join('');
  }
}

// Send conversational prompt directly into AI Copilot
function sendPromptToAi(promptText) {
  const windowEl = document.getElementById('aiChatWindow');
  if (windowEl && windowEl.classList.contains('hidden')) {
    toggleAiAssistant();
  }
  handleSendAiMessage(promptText);
}

// Quick Add Flight to Comparison Matrix
function quickAddToComparison(flightNo) {
  const flight = (state.flights || []).find(f => (f.flightNumber || f.flight_no) === flightNo);
  if (!flight) {
    showToast(`Flight ${flightNo} selected for comparison.`);
    showTab('comparison');
    return;
  }
  if (!state.selectedComparisonFlights.some(f => (f.flightNumber || f.flight_no) === flightNo)) {
    state.selectedComparisonFlights.push(flight);
  }
  showToast(`Added ${flightNo} to comparison matrix.`);
  showTab('comparison');
}

// Dual Search Trigger: Updates Home results if on Home, otherwise opens Explorer
async function triggerHomeOrExplorerSearch() {
  const fromVal = document.getElementById('fromCity')?.value || 'DEL';
  const toVal = document.getElementById('toCity')?.value || 'BOM';
  const orig = extractAirportCode(fromVal);
  const dest = extractAirportCode(toVal);

  const fFrom = document.getElementById('fFrom');
  const fTo = document.getElementById('fTo');
  if (fFrom) fFrom.value = orig;
  if (fTo) fTo.value = dest;

  if (state.currentTab === 'home') {
    showToast(`Searching flights for ${orig} ➔ ${dest}...`);
    await loadHomepageFeaturedFlights(orig, dest);
    const featuredSec = document.getElementById('homeFeaturedSection');
    if (featuredSec) {
      featuredSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  } else {
    await triggerSearch();
  }
}

// Flight Search (Explorer tab)
async function triggerSearch() {
  const fromCity = document.getElementById('fromCity')?.value || 'DEL';
  const toCity = document.getElementById('toCity')?.value || 'BOM';
  const orig = extractAirportCode(fromCity);
  const dest = extractAirportCode(toCity);

  const fFrom = document.getElementById('fFrom');
  const fTo = document.getElementById('fTo');
  if (fFrom) fFrom.value = orig;
  if (fTo) fTo.value = dest;

  const statusBox = document.getElementById('searchResultBox');
  if (statusBox) {
    statusBox.classList.remove('hidden');
    statusBox.innerHTML = `Searching flights for <b>${orig} → ${dest}</b>...`;
  }

  const explorerNav = document.querySelector('.main-nav a[data-tab="explorer"]');
  showTab('explorer', explorerNav);
  await loadFlights();
}

// =========================================================
// PHASE 7 & 8: NATURAL LANGUAGE FLIGHT SEARCH & AI REASONING
// =========================================================

async function executeNlSearch(inputId = 'heroNlSearchInput') {
  const inputEl = document.getElementById(inputId);
  if (!inputEl) return;
  const query = inputEl.value.trim();
  if (!query) {
    showToast('Please enter a flight query (e.g., Delhi to Mumbai tomorrow under ₹6,000)', false);
    return;
  }

  showToast('Interpreting natural language search with AirfareX AI...');

  try {
    const res = await window.api.interpretSearch(query);

    if (res.clarification_needed && res.clarification_message) {
      showToast(res.clarification_message, false);
      return;
    }

    // Populate search inputs
    if (res.origin) {
      const fFrom = document.getElementById('fFrom');
      const fromCity = document.getElementById('fromCity');
      if (fFrom) fFrom.value = res.origin;
      if (fromCity) fromCity.value = `${res.origin} (${res.origin})`;
    }
    if (res.destination) {
      const fTo = document.getElementById('fTo');
      const toCity = document.getElementById('toCity');
      if (fTo) fTo.value = res.destination;
      if (toCity) toCity.value = `${res.destination} (${res.destination})`;
    }
    if (res.date) {
      const depDate = document.getElementById('departDate');
      if (depDate) depDate.value = res.date;
    }
    if (res.stops && res.stops !== 'Any') {
      const fStops = document.getElementById('fStops');
      if (fStops) fStops.value = res.stops;
    }
    if (res.airline && res.airline !== 'All airlines') {
      const fAir = document.getElementById('fAir');
      if (fAir) fAir.value = res.airline;
    }
    if (res.preference) {
      if (res.preference === 'lowest_price') setSort('price');
      else if (res.preference === 'fastest') setSort('duration');
      else setSort('score');
    }

    // Switch to explorer tab and trigger search
    const explorerNav = document.querySelector('.main-nav a[data-tab="explorer"]');
    showTab('explorer', explorerNav);

    showToast(`AI matched: ${res.origin || 'Origin'} ➔ ${res.destination || 'Dest'} (${res.stops || 'Any stops'}, ${res.preference || 'Best Value'})`);
    await loadFlights();
  } catch (err) {
    console.error('NL Search interpretation failed:', err);
    showToast('Could not interpret query. Please use standard search inputs.', false);
  }
}

function setNlQuery(query, inputId = 'heroNlSearchInput') {
  const inputEl = document.getElementById(inputId);
  if (inputEl) {
    inputEl.value = query;
    executeNlSearch(inputId);
  }
}

// Reset Flight Filters
function resetFlightFilters() {
  const fStops = document.getElementById('fStops');
  const fAir = document.getElementById('fAir');
  const fPrice = document.getElementById('fPrice');
  const fTime = document.getElementById('fTime');
  const fMinScore = document.getElementById('fMinScore');
  const fCabin = document.getElementById('fCabin');
  const directToggle = document.getElementById('directToggle');
  const bagsToggle = document.getElementById('bagsToggle');

  if (fStops) fStops.value = 'Any';
  if (fAir) fAir.value = 'All airlines';
  if (fPrice) fPrice.value = 'Any';
  if (fTime) fTime.value = 'Any time';
  if (fMinScore) fMinScore.value = '0';
  if (fCabin) fCabin.value = 'Any';
  if (directToggle) directToggle.checked = false;
  if (bagsToggle) bagsToggle.checked = false;

  loadFlights();
}

// Load Flights in Explorer with AI Scoring & Badge Integration
async function loadFlights() {
  const resultsContainer = document.getElementById('flightResults');
  if (resultsContainer) {
    resultsContainer.innerHTML = `
      <div class="skeleton-card">
        <div class="skeleton-shimmer"></div>
        <div class="skeleton-line lg" style="width:32%;"></div>
        <div class="skeleton-line md" style="width:65%;"></div>
        <div class="skeleton-line sm" style="width:40%;"></div>
      </div>
      <div class="skeleton-card">
        <div class="skeleton-shimmer"></div>
        <div class="skeleton-line lg" style="width:28%;"></div>
        <div class="skeleton-line md" style="width:58%;"></div>
        <div class="skeleton-line sm" style="width:45%;"></div>
      </div>
    `;
  }

  const fromCity = document.getElementById('fFrom')?.value || document.getElementById('fromCity')?.value || '';
  const toCity = document.getElementById('fTo')?.value || document.getElementById('toCity')?.value || '';
  const orig = fromCity.trim() ? extractAirportCode(fromCity) : '';
  const dest = toCity.trim() ? extractAirportCode(toCity) : '';
  const stops = document.getElementById('fStops')?.value || 'Any';
  const airline = document.getElementById('fAir')?.value || 'All airlines';
  const maxPriceVal = document.getElementById('fPrice')?.value || 'Any';
  const timeOfDay = document.getElementById('fTime')?.value || 'Any time';
  const minScoreVal = document.getElementById('fMinScore')?.value || '0';
  const cabinVal = document.getElementById('fCabin')?.value || 'Any';
  const directOnly = document.getElementById('directToggle')?.checked || false;

  const params = {
    from_city: orig,
    to_city: dest,
    stops: stops,
    airline: airline,
    time_of_day: timeOfDay,
    min_score: parseInt(minScoreVal) || 0,
    cabin: cabinVal,
    direct_only: directOnly,
    sort_by: state.sortMode || 'score'
  };

  if (maxPriceVal !== 'Any') {
    params.max_price = parseInt(maxPriceVal.replace(/[^0-9]/g, ''));
  }

  try {
    let flights = [];
    let bestFare = 0;
    let envelope = { data_source: 'DEMO', provider: 'AirfareX Centralized Master Dataset' };

    // Query demo dataset directly
    if (window.AirfarexDemoData) {
      flights = window.AirfarexDemoData.filterFlights(params);
      if (flights.length > 0) {
        bestFare = Math.min(...flights.map(f => f.totalPrice || f.total_fare));
      }
    }

    // If empty and user searched an unlisted route, try backend API
    if (flights.length === 0 && orig && dest) {
      try {
        const data = await window.api.searchFlights(params);
        if (data && data.flights && data.flights.length > 0) {
          flights = data.flights;
          bestFare = data.best_fare || Math.min(...flights.map(f => f.total_fare));
          envelope = data;
        }
      } catch (apiErr) {
        console.warn('API fetch fallback:', apiErr);
      }
    }

    state.flights = flights;

    // Phase 7: Compute recommendations
    const rec = window.AirfarexDemoData ? window.AirfarexDemoData.getRecommendations(flights) : null;
    state.aiRecommendations = rec;
    renderAiRecommendationsSummary(rec);

    renderFlightCards(flights, bestFare, envelope);
  } catch (err) {
    console.error('Failed to load flights:', err);
    if (resultsContainer) {
      resultsContainer.innerHTML = `
        <div class="friendly-error-card">
          <div class="friendly-error-icon">📡</div>
          <h3 class="friendly-error-title">Unable to Fetch Flight Data</h3>
          <p class="friendly-error-desc">We could not retrieve flight schedules for ${orig} ➔ ${dest}.</p>
          <button class="btn primary sm" onclick="loadFlights()">Retry Search</button>
        </div>
      `;
    }
  }
}

// Render AI 4-Card Summary Bar (Cheapest / Fastest / Best Value / AirfareX Pick) in Explorer
function renderAiRecommendationsSummary(rec) {
  const banner = document.getElementById('aiRecSummaryGrid');
  if (!banner || !rec) {
    if (banner) banner.classList.add('hidden');
    return;
  }

  const pick = rec.airfarex_pick;
  const bestVal = rec.best_value;
  const cheapest = rec.cheapest;
  const fastest = rec.fastest;

  if (!pick && !cheapest && !fastest) {
    banner.classList.add('hidden');
    return;
  }

  banner.classList.remove('hidden');
  banner.innerHTML = `
    <!-- 1. Best Overall / AirfareX Pick -->
    ${pick ? `
      <div class="ai-rec-card card-pick" onclick="openFlightDetailsModal('${pick.flightNumber || pick.flight_no}')" title="Click to view AI score reasoning" style="cursor:pointer;">
        <div class="ai-rec-card-tag">👑 Best Overall</div>
        <div class="ai-rec-flight-title">${pick.airline} · ${pick.flightNumber || pick.flight_no}</div>
        <div class="ai-rec-flight-sub">${pick.duration} · ${pick.stops}</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(pick.totalPrice || pick.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill">⭐ ${pick.overallScore || 92}/100</span>
        </div>
      </div>
    ` : ''}

    <!-- 2. Best Value -->
    ${bestVal ? `
      <div class="ai-rec-card card-best-value" onclick="openFlightDetailsModal('${bestVal.flightNumber || bestVal.flight_no}')" title="Click to view AI score reasoning" style="cursor:pointer;">
        <div class="ai-rec-card-tag">💎 Best Value</div>
        <div class="ai-rec-flight-title">${bestVal.airline} · ${bestVal.flightNumber || bestVal.flight_no}</div>
        <div class="ai-rec-flight-sub">${bestVal.duration} · ${bestVal.stops}</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(bestVal.totalPrice || bestVal.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill" style="background:rgba(16,185,129,0.15); color:#34d399;">⭐ ${bestVal.overallScore || 90}/100</span>
        </div>
      </div>
    ` : ''}

    <!-- 3. Lowest Price -->
    ${cheapest ? `
      <div class="ai-rec-card card-cheapest" onclick="openFlightDetailsModal('${cheapest.flightNumber || cheapest.flight_no}')" title="Click to view AI score reasoning" style="cursor:pointer;">
        <div class="ai-rec-card-tag">💸 Lowest Price</div>
        <div class="ai-rec-flight-title">${cheapest.airline} · ${cheapest.flightNumber || cheapest.flight_no}</div>
        <div class="ai-rec-flight-sub">${cheapest.duration} · ${cheapest.stops}</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(cheapest.totalPrice || cheapest.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill" style="background:rgba(14,165,233,0.15); color:#38bdf8;">Base Fare</span>
        </div>
      </div>
    ` : ''}

    <!-- 4. Fastest Travel -->
    ${fastest ? `
      <div class="ai-rec-card card-fastest" onclick="openFlightDetailsModal('${fastest.flightNumber || fastest.flight_no}')" title="Click to view AI score reasoning" style="cursor:pointer;">
        <div class="ai-rec-card-tag">⚡ Fastest Travel</div>
        <div class="ai-rec-flight-title">${fastest.airline} · ${fastest.flightNumber || fastest.flight_no}</div>
        <div class="ai-rec-flight-sub">${fastest.duration} · Non-stop</div>
        <div class="ai-rec-price-row">
          <span class="ai-rec-price">₹${(fastest.totalPrice || fastest.total_fare).toLocaleString('en-IN')}</span>
          <span class="ai-rec-score-pill" style="background:rgba(245,158,11,0.15); color:#fbbf24;">${fastest.duration}</span>
        </div>
      </div>
    ` : ''}
  `;
}

// Render Flight Cards in Explorer with Full Score UI, Sub-scores & Actions
function renderFlightCards(flights, bestFare, searchEnvelope = null) {
  const container = document.getElementById('flightResults');
  if (!container) return;

  if (!flights || !flights.length) {
    container.innerHTML = `
      <div class="friendly-empty-card" style="margin-top:20px; text-align:center; padding:36px; background:var(--bg-card); border:1px solid var(--border-color); border-radius:var(--radius-md);">
        <div class="friendly-empty-icon" style="font-size:36px; margin-bottom:12px;">✈️</div>
        <h3 class="friendly-empty-title" style="margin:0 0 8px; font-size:18px;">No Flights Match Your Selected Criteria</h3>
        <p class="friendly-empty-desc" style="color:var(--text-muted); max-width:520px; margin:0 auto 16px;">
          Try selecting "Any" stops, broadening your price limit, or explore one of our verified master demo routes:
        </p>
        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-bottom:18px;">
          <button class="btn sm light" onclick="selectDemoRoute('HYD', 'DEL')">⚡ Hyderabad ➔ Delhi</button>
          <button class="btn sm light" onclick="selectDemoRoute('HYD', 'BOM')">⚡ Hyderabad ➔ Mumbai</button>
          <button class="btn sm light" onclick="selectDemoRoute('BLR', 'DEL')">⚡ Bengaluru ➔ Delhi</button>
          <button class="btn sm light" onclick="selectDemoRoute('BOM', 'DEL')">⚡ Mumbai ➔ Delhi</button>
          <button class="btn sm green" onclick="exploreDemoFlights()">🌐 View All 20+ Demo Flights</button>
        </div>
        <button class="btn primary sm" onclick="resetFlightFilters()">Reset Filters & Show All</button>
      </div>
    `;
    return;
  }

  const withBag = document.getElementById('bagsToggle')?.checked || false;

  // Header banner showing count and best fare
  let metaHeaderHtml = `
    <div class="search-provider-banner" style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.03); border:1px solid var(--border-color); padding:10px 16px; border-radius:10px; margin-bottom:14px; font-size:12px; flex-wrap:wrap; gap:8px;">
      <div style="display:flex; align-items:center; gap:8px;">
        <span style="color:var(--text-muted);">Data Source:</span>
        <span class="data-source-pill badge-live" style="font-weight:700; padding:3px 8px; border-radius:6px; font-size:11px; text-transform:uppercase; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3);">● DEMO DATASET</span>
        <span style="color:var(--text-muted);">Provider: <b>AirfareX Aviation Engine</b></span>
      </div>
      <div style="color:var(--text-muted);">
        <b>${flights.length}</b> flight${flights.length === 1 ? '' : 's'} found · Best Fare: <b style="color:var(--brand-mint);">₹${(bestFare || 4290).toLocaleString('en-IN')}</b>
      </div>
    </div>
  `;

  const cardsHtml = flights.map((f, idx) => {
    const flightNo = f.flightNumber || f.flight_no || `6E-${idx+200}`;
    const airline = f.airline || 'IndiGo';
    const airlineClass = `airline-${airline.toLowerCase().replace(/\s+/g, '-')}`;
    const safeFlightId = flightNo.replace(/[^a-zA-Z0-9]/g, '_');
    const totFare = f.totalPrice || f.total_fare || 4500;
    const finalFare = withBag ? (totFare + (f.bag_fee || 0)) : totFare;
    const baseFare = f.basePrice || f.base_fare || Math.round(totFare * 0.8);
    const taxes = f.taxes || f.taxes_fees || (totFare - baseFare);
    const depTime = f.departureTime || f.dep_time || '07:15';
    const arrTime = f.arrivalTime || f.arr_time || '09:30';
    const origCode = f.origin || f.origin_code || 'HYD';
    const destCode = f.destination || f.destination_code || 'DEL';
    const duration = f.duration || '2h 15m';
    const stops = f.stops || 'Nonstop';

    // Scoring metrics
    const overallScore = f.overallScore || f.fare_score || 92;
    const scoreRating = f.scoreRating || (overallScore >= 90 ? 'Excellent' : (overallScore >= 80 ? 'Very Good' : 'Good'));
    const ratingClass = overallScore >= 90 ? 'excellent' : (overallScore >= 80 ? 'very-good' : (overallScore >= 70 ? 'good' : 'average'));
    const priceScore = f.priceScore || 92;
    const relScore = f.reliabilityScore || 95;
    const punctScore = f.punctualityScore || f.onTimePercentage || 94;
    const comfScore = f.comfortScore || 88;

    // Badges
    let badgeText = f.recommendation || (totFare <= (bestFare || 4500) ? 'Lowest Price' : (stops === 'Nonstop' ? 'Best Value' : 'Verified'));
    let badgeClass = 'best-value';
    if (badgeText.toLowerCase().includes('overall') || badgeText.toLowerCase().includes('pick')) badgeClass = 'airfarex-pick';
    else if (badgeText.toLowerCase().includes('lowest') || badgeText.toLowerCase().includes('price') || badgeText.toLowerCase().includes('cheapest')) badgeClass = 'cheapest';
    else if (badgeText.toLowerCase().includes('fastest') || badgeText.toLowerCase().includes('quick')) badgeClass = 'fastest';
    else if (badgeText.toLowerCase().includes('reliable')) badgeClass = 'airfarex-pick';

    const bagSubText = withBag ? 'incl. 15kg checked bag' : 'Taxes & fees included';
    const bagTagText = f.baggage || (f.bag_fee === 0 ? '🧳 7kg Cabin + 15kg Checked bag' : `🧳 Checked bag: +₹${f.bag_fee}`);
    const isCompared = state.selectedComparisonFlights.some(cf => (cf.flightNumber || cf.flight_no) === flightNo);

    return `
      <div class="flight-card ${airlineClass}" id="flightCard_${safeFlightId}" style="margin-bottom:14px;">
        <div class="flight-row-main">
          <!-- Airline & Flight No -->
          <div class="flight-airline">
            <div class="airline-name">
              <b style="font-size:16px; color:var(--text-main);">${airline}</b>
              <span class="flight-no-tag">${flightNo}</span>
            </div>
            <div class="smart-badge-row" style="display:flex; align-items:center; gap:6px; margin-top:6px; flex-wrap:wrap;">
              <span class="smart-badge ${badgeClass}">${badgeText}</span>
              <span class="score-badge-indicator ${ratingClass}" title="Calculated Composite Score">⭐ ${overallScore}/100 — ${scoreRating}</span>
            </div>
          </div>

          <!-- Schedule & Track -->
          <div class="flight-schedule">
            <div class="flight-time-box">
              <span class="flight-time">${depTime}</span>
              <span class="flight-city">${origCode}</span>
            </div>
            <div class="flight-duration-track">
              <span class="flight-duration">${duration}</span>
              <div class="flight-track-line"></div>
              <span class="flight-stop-label ${stops !== 'Nonstop' ? 'has-stops' : ''}">${stops}</span>
            </div>
            <div class="flight-time-box" style="text-align: right;">
              <span class="flight-time">${arrTime}</span>
              <span class="flight-city">${destCode}</span>
            </div>
          </div>

          <!-- Pricing -->
          <div class="flight-pricing-box">
            <div class="flight-price">₹${finalFare.toLocaleString('en-IN')}</div>
            <div class="price-type-sub">${bagSubText}</div>
          </div>

          <!-- Action Buttons -->
          <div class="flight-actions" style="display:flex; flex-direction:column; gap:6px;">
            <button class="btn-select-flight" onclick="selectFlight('${airline}', '${flightNo}', ${finalFare}, '${destCode}', '${f.destinationCity || destCode}')">Book Now ➔</button>
            <div style="display:flex; gap:6px;">
              <button class="btn-view-details" onclick="openFlightDetailsModal('${flightNo}')" title="View Full Details & 5-Bar Score Breakdown">📋 Details</button>
              <button class="btn-why-flight" onclick="openWhyThisFlightModal('${flightNo}')" title="Explain why this flight is recommended">💡 Why?</button>
            </div>
          </div>
        </div>

        <!-- Requirement 3: Sub-scores strip -->
        <div class="flight-subscores-strip">
          <span class="subscore-item price">💸 Price: <b>${priceScore}/100</b></span>
          <span style="color:rgba(255,255,255,0.15);">·</span>
          <span class="subscore-item reliability">🛡️ Reliability: <b>${relScore}/100</b></span>
          <span style="color:rgba(255,255,255,0.15);">·</span>
          <span class="subscore-item punctuality">⏱️ Punctuality: <b>${punctScore}/100</b></span>
          <span style="color:rgba(255,255,255,0.15);">·</span>
          <span class="subscore-item comfort">💺 Comfort: <b>${comfScore}/100</b></span>
          <span style="margin-left:auto; font-size:11px; color:var(--text-muted);">${f.aircraft || 'Airbus A320neo'}</span>
        </div>

        <!-- Meta Tags & Compare Toggle -->
        <div class="flight-tags-row" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-top:8px;">
          <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
            <span class="flight-pill-tag">📍 Terminal ${f.terminal || 'T2'}</span>
            <span class="flight-pill-tag">${bagTagText}</span>
            <span class="flight-pill-tag">✓ Refundable (DGCA Rules)</span>
            <span class="flight-pill-tag">💺 ${f.seat_pitch || '30"'} Seat Pitch</span>
            <span class="flight-pill-tag accent clickable" onclick="checkStatusForFlight('${flightNo}')">Live Status →</span>
            <button class="flight-pill-tag clickable" onclick="quickAlert('${origCode} ➔ ${destCode}', ${finalFare})" title="Track Price Alerts" style="border:none; cursor:pointer;">🔔 Track</button>
          </div>

          <!-- Compare Checkbox -->
          <label class="flight-compare-toggle" title="Select to compare up to 2 flights side-by-side" style="display:inline-flex; align-items:center; gap:5px; cursor:pointer; font-size:12px; font-weight:700;">
            <input type="checkbox" onchange="toggleFlightComparisonSelect('${flightNo}', this)" ${isCompared ? 'checked' : ''}>
            <span>⚖️ Compare</span>
          </label>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = metaHeaderHtml + cardsHtml;
}

// =========================================================
// PHASE 7: FLIGHT DETAILS & SCORE BREAKDOWN MODAL HANDLER
// =========================================================

function openFlightDetailsModal(flightNo) {
  const modal = document.getElementById('flightDetailsModal');
  if (!modal) return;

  const flight = window.AirfarexDemoData ? window.AirfarexDemoData.getFlightByNumber(flightNo) : (state.flights || []).find(f => (f.flightNumber || f.flight_no) === flightNo);
  if (!flight) return;

  const airline = flight.airline || 'IndiGo';
  const fNo = flight.flightNumber || flight.flight_no || flightNo;
  const origCode = flight.origin || flight.origin_code || 'HYD';
  const destCode = flight.destination || flight.destination_code || 'DEL';
  const origCity = flight.originCity || flight.origin_city || origCode;
  const destCity = flight.destinationCity || flight.destination_city || destCode;
  const depTime = flight.departureTime || flight.dep_time || '07:15';
  const arrTime = flight.arrivalTime || flight.arr_time || '09:30';
  const duration = flight.duration || '2h 15m';
  const stops = flight.stops || 'Nonstop';
  const totFare = flight.totalPrice || flight.total_fare || 4700;
  const baseFare = flight.basePrice || flight.base_fare || Math.round(totFare * 0.82);
  const taxes = flight.taxes || flight.taxes_fees || (totFare - baseFare);

  // Scores
  const pScore = flight.priceScore || 92;
  const rScore = flight.reliabilityScore || 95;
  const punctScore = flight.punctualityScore || flight.onTimePercentage || 94;
  const cScore = flight.comfortScore || 88;
  const overall = flight.overallScore || Math.round(pScore*0.3 + rScore*0.25 + punctScore*0.25 + cScore*0.2);
  const rating = flight.scoreRating || (overall >= 90 ? 'Excellent' : (overall >= 80 ? 'Very Good' : 'Good'));
  const ratingClass = overall >= 90 ? 'excellent' : (overall >= 80 ? 'very-good' : (overall >= 70 ? 'good' : 'average'));

  // Header Elements
  const titleEl = document.getElementById('fDetFlightTitle');
  const badgeEl = document.getElementById('fDetBadge');
  const scoreBadgeEl = document.getElementById('fDetScoreBadge');
  const sectorEl = document.getElementById('fDetSector');
  const aircraftEl = document.getElementById('fDetAircraft');
  const totalFareEl = document.getElementById('fDetTotalFare');

  if (titleEl) titleEl.textContent = `${airline} ${fNo}`;
  if (badgeEl) badgeEl.textContent = flight.recommendation || 'BEST VALUE';
  if (scoreBadgeEl) {
    scoreBadgeEl.className = `score-badge-indicator ${ratingClass}`;
    scoreBadgeEl.textContent = `⭐ ${overall}/100 — ${rating}`;
  }
  if (sectorEl) sectorEl.textContent = `${origCode} ➔ ${destCode}`;
  if (aircraftEl) aircraftEl.textContent = `${flight.aircraft || 'Airbus A320neo'} · ${flight.cabinClass || 'Economy Standard'}`;
  if (totalFareEl) totalFareEl.textContent = `₹${totFare.toLocaleString('en-IN')}`;

  // Schedule Elements
  document.getElementById('fDetDepTime') && (document.getElementById('fDetDepTime').textContent = depTime);
  document.getElementById('fDetArrTime') && (document.getElementById('fDetArrTime').textContent = arrTime);
  document.getElementById('fDetOriginCode') && (document.getElementById('fDetOriginCode').textContent = origCode);
  document.getElementById('fDetDestCode') && (document.getElementById('fDetDestCode').textContent = destCode);
  document.getElementById('fDetOriginCity') && (document.getElementById('fDetOriginCity').textContent = origCity);
  document.getElementById('fDetDestCity') && (document.getElementById('fDetDestCity').textContent = destCity);
  document.getElementById('fDetDuration') && (document.getElementById('fDetDuration').textContent = duration);
  document.getElementById('fDetStops') && (document.getElementById('fDetStops').textContent = stops);
  document.getElementById('fDetTerminalDep') && (document.getElementById('fDetTerminalDep').textContent = `📍 Terminal ${flight.terminal || 'T2'} · Gate ${flight.gate || '12'}`);
  document.getElementById('fDetTerminalArr') && (document.getElementById('fDetTerminalArr').textContent = `📍 Terminal ${flight.terminal || 'T2'}`);

  // Score Progress Bars
  setScoreBar('fDetBarPrice', 'fDetBarValPrice', pScore);
  setScoreBar('fDetBarReliability', 'fDetBarValReliability', rScore);
  setScoreBar('fDetBarPunctuality', 'fDetBarValPunctuality', punctScore);
  setScoreBar('fDetBarComfort', 'fDetBarValComfort', cScore);
  setScoreBar('fDetBarOverall', 'fDetBarValOverall', overall);

  const reasonEl = document.getElementById('fDetScoreReason');
  if (reasonEl) {
    reasonEl.textContent = flight.scoreReason || `Scored ${overall}/100 based on competitive fare (${pScore}/100), ${punctScore}% on-time rate (${punctScore}/100), high fleet reliability (${rScore}/100), and ${flight.seat_pitch || '30"'} seat pitch comfort (${cScore}/100).`;
  }

  // DGCA Taxes
  const udfFee = Math.round(taxes * 0.55);
  const fuelFee = Math.round(taxes * 0.32);
  const gstFee = taxes - udfFee - fuelFee;
  document.getElementById('fDetBaseFare') && (document.getElementById('fDetBaseFare').textContent = `₹${baseFare.toLocaleString('en-IN')}`);
  document.getElementById('fDetUdfFee') && (document.getElementById('fDetUdfFee').textContent = `₹${udfFee.toLocaleString('en-IN')}`);
  document.getElementById('fDetFuelFee') && (document.getElementById('fDetFuelFee').textContent = `₹${fuelFee.toLocaleString('en-IN')}`);
  document.getElementById('fDetGstFee') && (document.getElementById('fDetGstFee').textContent = `₹${gstFee.toLocaleString('en-IN')}`);
  document.getElementById('fDetFinalTotal') && (document.getElementById('fDetFinalTotal').textContent = `₹${totFare.toLocaleString('en-IN')}`);
  document.getElementById('fDetBtnFare') && (document.getElementById('fDetBtnFare').textContent = totFare.toLocaleString('en-IN'));

  // Baggage & Policy
  document.getElementById('fDetBaggage') && (document.getElementById('fDetBaggage').textContent = flight.baggage || '7kg Cabin + 15kg Check-in included');
  document.getElementById('fDetPolicy') && (document.getElementById('fDetPolicy').textContent = flight.cancellationPolicy || 'DGCA CAR Sec 3: Free cancellation within 24h of booking');

  // Book Button Handler
  const bookBtn = document.getElementById('fDetBookBtn');
  if (bookBtn) {
    bookBtn.onclick = () => {
      closeModal('flightDetailsModal');
      selectFlight(airline, fNo, totFare, destCode, destCity);
    };
  }

  openModal('flightDetailsModal');
}

// =========================================================
// PHASE 7: EXPLAINABLE "WHY THIS FLIGHT?" MODAL HANDLER
// =========================================================

async function openWhyThisFlightModal(flightNo) {
  const modal = document.getElementById('whyFlightModal');
  if (!modal) return;

  const fromCity = document.getElementById('fFrom')?.value || 'HYD';
  const toCity = document.getElementById('fTo')?.value || 'DEL';
  const depDate = document.getElementById('departDate')?.value || null;

  try {
    const flight = window.AirfarexDemoData ? window.AirfarexDemoData.getFlightByNumber(flightNo) : null;
    const titleEl = document.getElementById('whyModalFlightTitle');
    const badgeEl = document.getElementById('whyModalBadge');
    const sectorEl = document.getElementById('whyModalSector');
    const schedEl = document.getElementById('whyModalSchedule');
    const fareEl = document.getElementById('whyModalFare');
    const scoreEl = document.getElementById('whyModalOverallScore');

    if (flight) {
      if (titleEl) titleEl.textContent = `${flight.airline} ${flight.flightNumber || flight.flight_no}`;
      if (sectorEl) sectorEl.textContent = `${flight.origin} ➔ ${flight.destination}`;
      if (schedEl) schedEl.textContent = `${flight.departureTime} – ${flight.arrivalTime} · ${flight.duration} · ${flight.stops}`;
      if (fareEl) fareEl.textContent = `₹${(flight.totalPrice || flight.total_fare).toLocaleString('en-IN')}`;
      if (scoreEl) scoreEl.textContent = flight.overallScore || 92;

      if (badgeEl) {
        badgeEl.textContent = flight.recommendation || 'BEST VALUE';
        badgeEl.className = 'smart-badge airfarex-pick';
      }

      setScoreBar('scoreBarPrice', 'scoreValPrice', flight.priceScore || 92);
      setScoreBar('scoreBarDur', 'scoreValDur', flight.punctualityScore || 94);
      setScoreBar('scoreBarStops', 'scoreValStops', flight.reliabilityScore || 95);
      setScoreBar('scoreBarConv', 'scoreValConv', flight.comfortScore || 88);
      setScoreBar('scoreBarValue', 'scoreValValue', flight.overallScore || 92);

      const reasonsBox = document.getElementById('whyModalReasonsList');
      if (reasonsBox) {
        reasonsBox.innerHTML = `
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="color:var(--brand-mint); font-weight:800;">✓</span>
            <span>${flight.scoreReason || 'Statutory on-time flight with competitive fare.'}</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="color:var(--brand-mint); font-weight:800;">✓</span>
            <span>Baggage: ${flight.baggage || '7kg Cabin + 15kg Checked bag included'}</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="color:var(--brand-mint); font-weight:800;">✓</span>
            <span>Seat Comfort: ${flight.seat_pitch || '30"'} Legroom on ${flight.aircraft || 'modern fleet'}</span>
          </div>
        `;
      }

      openModal('whyFlightModal');
    }
  } catch (err) {
    console.error('Failed to load flight insights:', err);
    showToast('Could not load AI flight breakdown', false);
  }
}

function setScoreBar(barId, valId, val) {
  const bar = document.getElementById(barId);
  const vEl = document.getElementById(valId);
  if (bar) bar.style.width = `${Math.min(100, Math.max(10, val))}%`;
  if (vEl) vEl.textContent = val;
}

// =========================================================
// PHASE 7: SIDE-BY-SIDE FLIGHT COMPARISON CONTROLLER
// =========================================================

function toggleFlightComparisonSelect(flightNo, checkbox) {
  const targetFlight = window.AirfarexDemoData ? window.AirfarexDemoData.getFlightByNumber(flightNo) : (state.flights || []).find(f => (f.flightNumber || f.flight_no) === flightNo);
  if (!targetFlight) return;

  const fIdentifier = targetFlight.flightNumber || targetFlight.flight_no;

  if (checkbox.checked) {
    if (state.selectedComparisonFlights.length >= 2) {
      showToast('Comparing 2 selected flights side-by-side.', false);
      state.selectedComparisonFlights.shift();
    }
    state.selectedComparisonFlights.push(targetFlight);
  } else {
    state.selectedComparisonFlights = state.selectedComparisonFlights.filter(f => (f.flightNumber || f.flight_no) !== fIdentifier);
  }

  updateComparisonFloatingBar();
}

function updateComparisonFloatingBar() {
  const bar = document.getElementById('comparisonFloatingBar');
  const countEl = document.getElementById('compFloatingCount');
  if (!bar) return;

  const count = state.selectedComparisonFlights.length;
  if (count > 0) {
    bar.classList.remove('hidden');
    if (countEl) countEl.textContent = `${count} flight${count === 1 ? '' : 's'} selected for comparison`;
  } else {
    bar.classList.add('hidden');
  }
}

function clearFlightComparisonSelection() {
  state.selectedComparisonFlights = [];
  document.querySelectorAll('.flight-compare-toggle input').forEach(cb => cb.checked = false);
  updateComparisonFloatingBar();
}

async function launchSelectedFlightComparison() {
  if (state.selectedComparisonFlights.length < 2) {
    showToast('Please select 2 flights from the list to compare side-by-side', false);
    return;
  }

  const flightA = state.selectedComparisonFlights[0];
  const flightB = state.selectedComparisonFlights[1];

  // Populate Comparison Modal
  const secEl = document.getElementById('compModalSectorTitle');
  if (secEl) secEl.textContent = `${flightA.origin || flightA.origin_code || 'HYD'} ➔ ${flightA.destination || flightA.destination_code || 'DEL'}`;

  // Flight A
  const nameA = document.getElementById('compFlightAName');
  const fareA = document.getElementById('compFareA');
  const durA = document.getElementById('compDurA');
  const stopsA = document.getElementById('compStopsA');
  const depA = document.getElementById('compDepA');
  const arrA = document.getElementById('compArrA');
  const scoreA = document.getElementById('compScoreA');
  const btnA = document.getElementById('compSelectBtnA');

  const fareNumA = flightA.totalPrice || flightA.total_fare || 4500;
  const scoreNumA = flightA.overallScore || 92;
  if (nameA) nameA.textContent = `${flightA.airline} ${flightA.flightNumber || flightA.flight_no}`;
  if (fareA) fareA.textContent = `₹${fareNumA.toLocaleString('en-IN')}`;
  if (durA) durA.textContent = flightA.duration;
  if (stopsA) stopsA.textContent = flightA.stops;
  if (depA) depA.textContent = flightA.departureTime || flightA.dep_time;
  if (arrA) arrA.textContent = flightA.arrivalTime || flightA.arr_time;
  if (scoreA) scoreA.textContent = `${scoreNumA}/100`;
  if (btnA) btnA.onclick = () => { selectFlight(flightA.airline, flightA.flightNumber || flightA.flight_no, fareNumA, flightA.destination || 'DEL', flightA.destinationCity || 'Delhi'); closeModal('flightComparisonModal'); };

  // Flight B
  const nameB = document.getElementById('compFlightBName');
  const fareB = document.getElementById('compFareB');
  const durB = document.getElementById('compDurB');
  const stopsB = document.getElementById('compStopsB');
  const depB = document.getElementById('compDepB');
  const arrB = document.getElementById('compArrB');
  const scoreB = document.getElementById('compScoreB');
  const btnB = document.getElementById('compSelectBtnB');

  const fareNumB = flightB.totalPrice || flightB.total_fare || 4800;
  const scoreNumB = flightB.overallScore || 88;
  if (nameB) nameB.textContent = `${flightB.airline} ${flightB.flightNumber || flightB.flight_no}`;
  if (fareB) fareB.textContent = `₹${fareNumB.toLocaleString('en-IN')}`;
  if (durB) durB.textContent = flightB.duration;
  if (stopsB) stopsB.textContent = flightB.stops;
  if (depB) depB.textContent = flightB.departureTime || flightB.dep_time;
  if (arrB) arrB.textContent = flightB.arrivalTime || flightB.arr_time;
  if (scoreB) scoreB.textContent = `${scoreNumB}/100`;
  if (btnB) btnB.onclick = () => { selectFlight(flightB.airline, flightB.flightNumber || flightB.flight_no, fareNumB, flightB.destination || 'DEL', flightB.destinationCity || 'Delhi'); closeModal('flightComparisonModal'); };

  // Narrative & Verdict
  const narrEl = document.getElementById('compModalNarrative');
  const verdEl = document.getElementById('compModalVerdict');
  const pointsList = document.getElementById('compModalPointsList');

  const isCheaperA = fareNumA <= fareNumB;
  const priceDiff = Math.abs(fareNumA - fareNumB);

  if (narrEl) {
    narrEl.textContent = isCheaperA 
      ? `Flight A (${flightA.airline}) saves ₹${priceDiff.toLocaleString('en-IN')} with a composite score of ${scoreNumA}/100.` 
      : `Flight B (${flightB.airline}) saves ₹${priceDiff.toLocaleString('en-IN')} with a composite score of ${scoreNumB}/100.`;
  }
  if (verdEl) {
    verdEl.textContent = scoreNumA >= scoreNumB 
      ? `Recommendation: Choose ${flightA.airline} for superior overall value score.` 
      : `Recommendation: Choose ${flightB.airline} for superior overall value score.`;
  }

  if (pointsList) {
    pointsList.innerHTML = `
      <li><b>Price Delta:</b> ₹${priceDiff.toLocaleString('en-IN')} difference</li>
      <li><b>Punctuality:</b> ${flightA.airline} (${flightA.punctualityScore || flightA.onTimePercentage || 94}%) vs ${flightB.airline} (${flightB.punctualityScore || flightB.onTimePercentage || 91}%)</li>
      <li><b>Aircraft:</b> ${flightA.aircraft || 'A320neo'} vs ${flightB.aircraft || 'B737 MAX'}</li>
      <li><b>Legroom / Comfort:</b> ${flightA.seat_pitch || '30"'} vs ${flightB.seat_pitch || '31"'}</li>
    `;
  }

  openModal('flightComparisonModal');
}

// =========================================================
// PHASE 7: USER SCORING PREFERENCES (PERSONALIZATION)
// =========================================================

async function loadUserPreferences() {
  try {
    const prefs = await window.api.getAiPreferences();
    state.userPreferences = prefs;

    const pPrio = document.getElementById('prefPriority');
    const pTime = document.getElementById('prefTime');
    const pAir = document.getElementById('prefAirline');
    const pFlex = document.getElementById('prefFlexDates');

    if (pPrio && prefs.priority) pPrio.value = prefs.priority;
    if (pTime && prefs.time_preference) pTime.value = prefs.time_preference;
    if (pAir && prefs.preferred_airline) pAir.value = prefs.preferred_airline;
    if (pFlex && prefs.flexible_dates) pFlex.checked = prefs.flexible_dates;
  } catch (err) {
    console.info('Preferences loaded with guest defaults.');
  }
}

async function handleSavePreferences(event) {
  event.preventDefault();
  const priority = document.getElementById('prefPriority')?.value || 'best_value';
  const timePref = document.getElementById('prefTime')?.value || 'any';
  const prefAir = document.getElementById('prefAirline')?.value || null;
  const flexDates = document.getElementById('prefFlexDates')?.checked || false;

  const payload = {
    priority,
    time_preference: timePref,
    preferred_airline: prefAir || null,
    max_stops: priority === 'nonstop' ? 'Nonstop' : 'Any',
    flexible_dates: flexDates
  };

  try {
    await window.api.saveAiPreferences(payload);
    state.userPreferences = payload;
    closeModal('userPreferencesModal');
    showToast('AI travel preferences updated! Re-evaluating flight rankings...');
    await loadFlights();
  } catch (err) {
    // If guest / unauthenticated, store in local state
    state.userPreferences = payload;
    closeModal('userPreferencesModal');
    showToast('Preferences applied for current session.');
    await loadFlights();
  }
}

window.toggleFlightDetails = function(flightId) {
  const el = document.getElementById('details_' + flightId);
  if (el) {
    el.classList.toggle('hidden');
  }
};

function setSort(mode) {
  state.sortMode = mode;
  document.querySelectorAll('.result-toolbar .btn').forEach(b => {
    b.classList.remove('dark');
    b.classList.add('gray');
  });
  const activeBtn = document.getElementById(`sortBtn_${mode}`);
  if (activeBtn) {
    activeBtn.classList.remove('gray');
    activeBtn.classList.add('dark');
  }

  if (state.flights && state.flights.length > 0 && window.AirfarexDemoData) {
    state.flights = window.AirfarexDemoData.sortFlights(state.flights, mode);
    const bestFare = Math.min(...state.flights.map(f => f.totalPrice || f.total_fare || 4500));
    renderFlightCards(state.flights, bestFare, { data_source: 'DEMO' });
  } else {
    loadFlights();
  }
}

// =========================================================
// SMART AIRFARE PRICE PREDICTION HANDLER
// =========================================================
async function runPricePrediction() {
  const from = document.getElementById('predFrom')?.value || 'HYD';
  const to = document.getElementById('predTo')?.value || 'DEL';
  const date = document.getElementById('predDate')?.value || null;

  try {
    const res = await window.api.predictPrice(from, to, date);
    state.predictionData = res;

    // Update Hero Recommendation Card
    const heroCard = document.getElementById('predHeroCard');
    const signalBadge = document.getElementById('predSignalBadge');
    const confBadge = document.getElementById('predConfidenceBadge');
    const titleText = document.getElementById('predTitleText');
    const descText = document.getElementById('predDescText');
    const fareVal = document.getElementById('predCurrentFare');

    if (heroCard && signalBadge) {
      if (res.recommendation === 'BUY_NOW') {
        heroCard.className = 'pred-card-hero buy-now';
        signalBadge.className = 'pred-signal-pill green';
        signalBadge.textContent = '● ' + window.i18n?.t('pred_buy_now', 'BUY NOW RECOMMENDED');
        titleText.textContent = window.i18n?.t('pred_surge_imminent', res.recommendation_title);
      } else {
        heroCard.className = 'pred-card-hero wait';
        signalBadge.className = 'pred-signal-pill amber';
        signalBadge.textContent = '● ' + window.i18n?.t('pred_wait', 'WAIT FOR DROP');
        titleText.textContent = window.i18n?.t('pred_drop_likely', res.recommendation_title);
      }

      confBadge.textContent = `${res.confidence_pct}% ` + window.i18n?.t('pred_conf_score', 'Confidence Score');
      descText.textContent = res.recommendation_desc;
      fareVal.textContent = `₹${res.current_fare.toLocaleString('en-IN')}`;
    }

    // Render 14-Day Prediction Chart
    const chart = document.getElementById('predForecastChart');
    if (chart && res.forecast_14d) {
      const fares = res.forecast_14d.map(p => p.predicted_fare);
      const minF = Math.min(...fares) * 0.95;
      const maxF = Math.max(...fares) * 1.05;
      const range = maxF - minF || 1;

      // Update Expected Price Range
      const rangeEl = document.getElementById('predExpectedRange');
      if (rangeEl && fares.length) {
        const minActual = Math.round(Math.min(...fares));
        const maxActual = Math.round(Math.max(...fares));
        rangeEl.textContent = `Expected range: ₹${minActual.toLocaleString('en-IN')} – ₹${maxActual.toLocaleString('en-IN')}`;
      }

      chart.innerHTML = res.forecast_14d.map(pt => {
        const heightPct = Math.round(((pt.predicted_fare - minF) / range) * 80) + 20;
        const isLowest = pt.predicted_fare === Math.min(...fares);
        return `
          <div class="pred-chart-bar-wrap" title="${pt.day} (${pt.date}): ₹${pt.predicted_fare}">
            <span style="font-size:10px; font-weight:700; color:var(--text-muted);">₹${Math.round(pt.predicted_fare/100)*100}</span>
            <div class="pred-bar ${isLowest ? 'lowest' : ''}" style="height: ${heightPct}%;"></div>
            <span style="font-size:10px; font-weight:600; color:var(--text-subtle);">${pt.date}</span>
          </div>
        `;
      }).join('');
    }

    // Lowest date text
    const lowestDateEl = document.getElementById('predLowestDate');
    if (lowestDateEl) lowestDateEl.textContent = res.predicted_lowest_date;

    // Price Drivers
    const driversList = document.getElementById('predDriversList');
    if (driversList && res.price_drivers) {
      driversList.innerHTML = res.price_drivers.map(d => `
        <div style="display:flex; align-items:flex-start; gap:8px; font-size:13px; color:var(--text-muted);">
          <span style="color:var(--brand-blue); font-weight:900;">✔</span>
          <span>${d}</span>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to run price prediction:', err);
  }
}

// =========================================================
// REFUND TRACKING & CLAIMS HANDLER
// =========================================================
async function trackRefundStatus(overridePnr = null) {
  const pnrInput = document.getElementById('refundPnrInput');
  const pnr = overridePnr || (pnrInput ? pnrInput.value.trim() : 'AIRX789');

  if (!pnr) {
    showToast('Please enter a PNR or ticket number', false);
    return;
  }

  try {
    const res = await window.api.trackRefund(pnr);
    state.currentRefund = res;

    // Update Titles
    document.getElementById('refPassengerTitle') && (document.getElementById('refPassengerTitle').textContent = `PNR: ${res.pnr} · ${res.passenger_name}`);
    document.getElementById('refFlightSector') && (document.getElementById('refFlightSector').textContent = `${res.airline} (${res.flight_no}) · ${res.sector}`);
    
    const badge = document.getElementById('refStatusBadge');
    if (badge) {
      badge.textContent = res.stage >= 4 ? window.i18n?.t('ref_step4', res.status) : res.status;
      badge.className = `badge ${res.stage >= 4 ? 'green' : res.stage >= 2 ? 'blue' : 'amber'}`;
    }

    // Render 4-Stage Stepper
    const stepper = document.getElementById('refundStepperContainer');
    if (stepper && res.timeline) {
      stepper.innerHTML = res.timeline.map(step => {
        let cls = '';
        if (step.completed) cls = 'completed';
        else if (step.current) cls = 'active';

        const stepTitle = window.i18n?.t(`ref_step${step.step}`, step.title);
        const stepDesc = window.i18n?.t(`ref_step${step.step}_desc`, step.desc);

        return `
          <div class="refund-step-item ${cls}">
            <div class="refund-step-circle">${step.completed ? '✓' : step.step}</div>
            <div class="refund-step-title">${stepTitle}</div>
            <div class="refund-step-desc">${stepDesc}</div>
          </div>
        `;
      }).join('');
    }

    // Update Decomposition
    document.getElementById('refOriginalFare') && (document.getElementById('refOriginalFare').textContent = `₹${res.total_fare.toLocaleString('en-IN')}`);
    document.getElementById('refCancelFee') && (document.getElementById('refCancelFee').textContent = `-₹${res.cancellation_fee.toLocaleString('en-IN')}`);
    document.getElementById('refNetRefund') && (document.getElementById('refNetRefund').textContent = `₹${res.refund_amount.toLocaleString('en-IN')}`);
    document.getElementById('refArnNumber') && (document.getElementById('refArnNumber').textContent = res.arn_number);

    showToast(`Refund tracking updated for PNR: ${res.pnr}`);
  } catch (err) {
    showToast('Error tracking refund for this PNR', false);
  }
}

async function submitNewRefundClaim() {
  const pnr = document.getElementById('claimPnr')?.value;
  const name = document.getElementById('claimName')?.value;
  const airline = document.getElementById('claimAirline')?.value;
  const sector = document.getElementById('claimSector')?.value;
  const fare = parseInt(document.getElementById('claimFare')?.value || 5000);

  if (!pnr || !name) {
    alert('Please enter PNR and passenger name');
    return;
  }

  try {
    const res = await window.api.submitRefundClaim({
      pnr,
      passenger_name: name,
      airline,
      flight_no: sector.split('·')[1]?.trim() || '6E 203',
      sector: sector.split('·')[0]?.trim() || 'HYD ➔ DEL',
      total_fare: fare,
      payment_method: 'UPI / Original Card'
    });

    closeModal('claimRefundModal');
    showToast(`Cancellation refund claim submitted for PNR: ${res.pnr}!`);
    trackRefundStatus(res.pnr);
  } catch (err) {
    showToast('Failed to submit refund claim', false);
  }
}

// Route Intelligence view
async function loadRoutes() {
  try {
    const routes = await window.api.getRoutes();
    state.routes = routes;

    const tbody = document.getElementById('routesTableBody');
    if (tbody) {
      tbody.innerHTML = routes.map(r => {
        const isUp = r.change_30d > 0;
        return `
          <tr>
            <td><b>${r.origin} → ${r.destination}</b></td>
            <td><span class="badge blue">${r.index_value.toFixed(1)}</span></td>
            <td class="${isUp ? 'risk' : 'good'}">${isUp ? '+' : ''}${r.change_30d}%</td>
            <td><b>₹${r.avg_fare.toLocaleString('en-IN')}</b></td>
            <td>${r.volatility_score}/100</td>
            <td><span class="badge ${r.status === 'High' ? 'red' : r.status === 'Watch' ? 'amber' : 'green'}">${r.status}</span></td>
            <td><button class="btn sm light" onclick="viewRouteElasticity('${r.route_code}')">${window.i18n?.t('btn_curve', 'Curve')}</button></td>
          </tr>
        `;
      }).join('');
    }

    await viewRouteElasticity('DEL-BOM');
  } catch (err) {
    console.error('Failed to load routes:', err);
  }
}

// View Elasticity Curve for specific route
async function viewRouteElasticity(routeCode) {
  const parts = routeCode.split('-');
  const origin = parts[0] || 'DEL';
  const dest = parts[1] || 'BOM';

  try {
    const data = await window.api.getRouteElasticity(origin, dest);
    const container = document.getElementById('elasticityCurveBox');
    if (!container) return;

    container.innerHTML = `
      <div style="margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
        <div><b>${data.route}</b> <span class="badge green">${data.sensitivity_level}</span></div>
        <span class="metric-sub">${data.description}</span>
      </div>
      ${data.points.map(pt => `
        <div class="route-row">
          <span style="font-weight:700; width:60px;">${pt.window}</span>
          <div style="flex:1; margin:0 14px;">
            <div class="progress-bar-wrap" style="margin:0;">
              <div class="progress-bar-fill" style="width: ${(pt.fare / 9000) * 100}%;"></div>
            </div>
          </div>
          <b style="font-size:14px;">${pt.formatted_fare}</b>
        </div>
      `).join('')}
    `;
  } catch (err) {
    console.error('Failed to load elasticity:', err);
  }
}

// APIx Index Section
async function loadIndexData() {
  try {
    const data = await window.api.getApixOverview();
    
    const basketContainer = document.getElementById('advanceBasketContainer');
    if (basketContainer && data.booking_basket) {
      basketContainer.innerHTML = data.booking_basket.map(b => `
        <div class="route-row">
          <b>${b.window}</b>
          <span>₹${b.fare.toLocaleString('en-IN')}</span>
        </div>
        <div class="progress-bar-wrap">
          <div class="progress-bar-fill" style="width: ${b.weight_pct}%;"></div>
        </div>
      `).join('');
    }

    const decompContainer = document.getElementById('fareDecompositionBody');
    if (decompContainer && data.fare_decomposition) {
      decompContainer.innerHTML = data.fare_decomposition.map(d => `
        <tr>
          <td><b>${d.component}</b></td>
          <td>${d.share_pct}%</td>
          <td><b>₹${d.example_inr.toLocaleString('en-IN')}</b></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load index data:', err);
  }
}

// Data Quality Center
async function loadQualityData() {
  try {
    const q = await window.api.getQualityReport();
    
    document.getElementById('qQuotes')?.textContent !== undefined && (document.getElementById('qQuotes').textContent = q.quotes_collected.toLocaleString('en-IN'));
    document.getElementById('qValid')?.textContent !== undefined && (document.getElementById('qValid').textContent = q.valid_quotes.toLocaleString('en-IN'));
    document.getElementById('qDups')?.textContent !== undefined && (document.getElementById('qDups').textContent = q.duplicates_removed.toLocaleString('en-IN'));
    document.getElementById('qOutliers')?.textContent !== undefined && (document.getElementById('qOutliers').textContent = q.outliers_flagged.toLocaleString('en-IN'));
  } catch (err) {
    console.error('Failed to load quality data:', err);
  }
}

// Saved & Alerts CRUD
async function loadAlerts() {
  const container = document.getElementById('alertsListContainer');
  if (!container) return;

  if (window.auth && !window.auth.isAuthenticated()) {
    container.innerHTML = `
      <div class="card empty-box" style="margin-top:14px; text-align:center; padding:44px 20px;">
        <span style="font-size:36px; display:block; margin-bottom:10px;">🔒</span>
        <h3 style="margin-bottom:6px; font-size:17px;">Sign In to View & Manage Saved Alerts</h3>
        <p style="font-size:13px; color:var(--text-muted); max-width:440px; margin:0 auto 16px;">
          Create persistent sector monitors, track historical fare fluctuations, and receive verified price drop notices.
        </p>
        <button class="btn primary sm" onclick="openAuthModal('login')">Sign In / Register</button>
      </div>
    `;
    return;
  }

  try {
    const alerts = await window.api.getAlerts();
    state.alerts = alerts;

    if (!alerts.length) {
      container.innerHTML = `
        <div class="card empty-box" style="margin-top:14px; text-align:center; padding:44px 20px;">
          <span style="font-size:36px; display:block; margin-bottom:10px;">🔔</span>
          <h3 style="margin-bottom:6px; font-size:17px;">You haven't saved any flights yet</h3>
          <p style="font-size:13px; color:var(--text-muted); max-width:440px; margin:0 auto 16px;">
            When you search for flights, tap the <b>Track</b> icon to follow fare changes and receive real-time price drop alerts.
          </p>
          <button class="btn sm" onclick="showTab('home')">Search Flights Now</button>
        </div>
      `;
      return;
    }

    container.innerHTML = alerts.map(a => {
      const parts = a.route.split(/→|➔/).map(s => s.trim());
      const fromCode = parts[0] || 'HYD';
      const toCode = parts[1] || 'DEL';
      return `
        <div class="saved-route-card">
          <div class="saved-route-info">
            <div class="saved-route-title">✈️ ${a.route}</div>
            <div class="saved-route-meta">Condition: ${a.target_condition} · Active 24x7 Fare Monitor</div>
          </div>
          <div style="display:flex; align-items:center; gap:16px;">
            <div style="text-align:right;">
              <div style="font-size:10.5px; color:var(--text-muted); font-weight:700; text-transform:uppercase; letter-spacing:0.3px;">Current Fare</div>
              <div style="font-size:18px; font-weight:800; color:var(--text-main); font-family:'JetBrains Mono', monospace;">${a.current_fare}</div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <button class="btn sm" onclick="searchSavedRoute('${fromCode}', '${toCode}')">View Flights</button>
              <button class="btn sm light" onclick="deleteAlert(${a.id})" title="Remove Alert">✕</button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Failed to load alerts:', err);
  }
}

function searchSavedRoute(fromCode, toCode) {
  const fromCity = document.getElementById('fromCity');
  const toCity = document.getElementById('toCity');
  if (fromCity) fromCity.value = fromCode;
  if (toCity) toCity.value = toCode;
  showTab('home');
  triggerSearch();
}
window.searchSavedRoute = searchSavedRoute;

async function quickAlert(route, fare) {
  if (window.auth && !window.auth.isAuthenticated()) {
    showToast('Please sign in to save price alerts', false);
    openAuthModal('login');
    return;
  }
  try {
    await window.api.createAlert(route, `₹${fare.toLocaleString('en-IN')}`, 'Notify on 8% fare drop');
    showToast(`Price alert activated for ${route}!`);
    await loadAlerts();
  } catch (err) {
    showToast('Failed to save alert', false);
  }
}

async function handleCreateAlertForm() {
  if (window.auth && !window.auth.isAuthenticated()) {
    closeModal('createAlertModal');
    showToast('Please sign in to create alerts', false);
    openAuthModal('login');
    return;
  }
  const route = document.getElementById('alertRouteInput').value;
  const target = document.getElementById('alertTargetInput').value;
  const fare = document.getElementById('alertFareInput').value || '₹5,500';

  if (!route || !target) {
    alert('Please enter route and target condition.');
    return;
  }

  try {
    await window.api.createAlert(route, fare, target);
    closeModal('createAlertModal');
    showToast(`Alert created for ${route}`);
    await loadAlerts();
  } catch (err) {
    showToast('Failed to create alert', false);
  }
}

async function deleteAlert(id) {
  try {
    await window.api.deleteAlert(id);
    showToast('Alert removed');
    await loadAlerts();
  } catch (err) {
    showToast('Error removing alert', false);
  }
}

// Flight Status Checker
async function checkFlightStatus() {
  const flightInput = document.getElementById('flightNoInput');
  const flightNo = flightInput ? flightInput.value.trim() : '6E 203';
  const out = document.getElementById('flightStatusOutput');

  if (!flightNo) {
    if (out) out.innerHTML = '<div class="empty-box">Please enter a flight number (e.g. 6E 203, AI 541, QP 1412).</div>';
    return;
  }

  try {
    const res = await window.api.getFlightStatus(flightNo);
    if (!out) return;

    out.innerHTML = `
      <div class="card" style="margin-top:12px; border-left: 4px solid var(--brand-mint);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <div>
            <h3 style="margin:0; font-size:18px;">${res.airline} · <b>${res.flight_no}</b></h3>
            <span class="metric-sub">${res.aircraft}</span>
          </div>
          <span class="badge ${res.status.includes('Delayed') ? 'amber' : 'green'}">${res.status}</span>
        </div>
        <div class="grid-3" style="margin: 12px 0;">
          <div>
            <div class="metric-title">Origin</div>
            <b>${res.origin}</b>
            <div class="metric-sub">Dep: ${res.dep_time}</div>
          </div>
          <div>
            <div class="metric-title">Destination</div>
            <b>${res.destination}</b>
            <div class="metric-sub">Arr: ${res.arr_time}</div>
          </div>
          <div>
            <div class="metric-title">Terminal & Gate</div>
            <b>${res.terminal} · Gate ${res.gate}</b>
            <div class="metric-sub">Baggage Belt: 04</div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    if (out) out.innerHTML = `<div class="empty-box">Unable to fetch status for ${flightNo}.</div>`;
  }
}

function checkStatusForFlight(no) {
  showTab('saved', document.querySelector('.main-nav a[data-tab="saved"]'));
  const inp = document.getElementById('flightNoInput');
  if (inp) inp.value = no;
  checkFlightStatus();
}

// Flight selection handler — navigates to dedicated Booking & Checkout page
function selectFlight(airline, flightNo, price, destCode = 'DEL', destName = 'Delhi') {
  const fromVal = document.getElementById('fromCity')?.value || document.getElementById('fFrom')?.value || 'HYD';
  const toVal = destName || document.getElementById('toCity')?.value || document.getElementById('fTo')?.value || 'DEL';
  const fromCode = extractAirportCode(fromVal);
  const targetDestCode = destCode || extractAirportCode(toVal);

  // Look up flight object in current state or demo dataset
  const existing = state.flights?.find(f => (f.flightNumber || f.flight_no) === flightNo) 
    || (window.AirfarexDemoData ? window.AirfarexDemoData.getFlightByNumber(flightNo) : null);

  const cleanAirline = airline || existing?.airline || 'IndiGo';
  const cleanFlightNo = flightNo || existing?.flightNumber || existing?.flight_no || '6E 203';
  const cleanOrig = existing?.origin || existing?.origin_code || fromCode || 'HYD';
  const cleanDest = existing?.destination || existing?.destination_code || targetDestCode || 'DEL';
  const cleanOrigCity = existing?.originCity || existing?.origin_city || (fromVal.includes('(') ? fromVal.split('(')[0].trim() : fromVal) || 'Hyderabad';
  const cleanDestCity = existing?.destinationCity || existing?.destination_city || (toVal.includes('(') ? toVal.split('(')[0].trim() : toVal) || 'Delhi';
  const cleanFare = price || existing?.totalPrice || existing?.total_fare || 5240;
  const cleanBase = existing?.basePrice || existing?.base_fare || Math.round(cleanFare * 0.8);
  const cleanTaxes = existing?.taxes || existing?.taxes_fees || (cleanFare - cleanBase);

  const bookingData = {
    airline: cleanAirline,
    flight_no: cleanFlightNo,
    origin_code: cleanOrig,
    origin_city: cleanOrigCity,
    destination_code: cleanDest,
    destination_city: cleanDestCity,
    total_fare: cleanFare,
    base_fare: cleanBase,
    taxes: cleanTaxes,
    dep_time: existing?.departureTime || existing?.dep_time || '07:15',
    arr_time: existing?.arrivalTime || existing?.arr_time || '09:30',
    duration: existing?.duration || '2h 15m',
    stops: existing?.stops || 'Nonstop',
    aircraft: existing?.aircraft || 'Airbus A320neo',
    cabin: existing?.cabinClass || existing?.cabin || 'Economy',
    terminal: existing?.terminal || 'T2',
    gate: existing?.gate || 'G12',
    seat_pitch: existing?.seat_pitch || '30"',
    baggage: existing?.baggage || '15kg Check-in + 7kg Cabin',
    emissions_kg: existing?.emissions_kg || 135,
    fare_score: existing?.overallScore || existing?.fare_score || 94,
    travel_date: document.getElementById('flyDate')?.value || document.getElementById('departDate')?.value || new Date(Date.now() + 86400000 * 3).toISOString().slice(0, 10)
  };

  try {
    sessionStorage.setItem('airfarex_booking_flight', JSON.stringify(bookingData));
  } catch (e) {
    console.warn('Session storage write error:', e);
  }

  showToast(`Proceeding to Fare Details & Booking for ${bookingData.airline} ${bookingData.flight_no}...`);
  setTimeout(() => {
    window.location.href = '/booking.html';
  }, 250);
}


// Quick action chips
function flexDates() {
  showToast('📅 Showing lowest fares around your travel window (Tuesday: ₹4,620)');
  showTab('explorer', document.querySelector('.main-nav a[data-tab="explorer"]'));
}

function everywhere() {
  showToast('🌍 Exploring all top sectors from your origin airport');
  showTab('routes', document.querySelector('.main-nav a[data-tab="routes"]'));
}

function nearbyAirports() {
  showToast('📍 Nearby regional alternatives included (HYD / PNQ / JAI)');
  showTab('explorer', document.querySelector('.main-nav a[data-tab="explorer"]'));
}

// City select from map
window.selectCity = function(code, name) {
  showToast(`Selected hub: ${name} (${code})`);
  const fromInp = document.getElementById('fromCity');
  if (fromInp) fromInp.value = `${name} (${code})`;
  handleHomePlaceChange();
  showTab('home', document.querySelector('.main-nav a[data-tab="home"]'));
};

// Modal handlers
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('open');
  if (modalId === 'cpiModal') updateCpiSimulation();
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('open');
}

// CPI Simulation
async function updateCpiSimulation() {
  const headlineWeight = parseFloat(document.getElementById('cpiWeightSlider')?.value || 1.2) / 100;
  const transportWeight = parseFloat(document.getElementById('transportWeightSlider')?.value || 8.6) / 100;
  const inflation = parseFloat(document.getElementById('inflationSlider')?.value || 7.4);

  document.getElementById('cpiWeightVal') && (document.getElementById('cpiWeightVal').textContent = `${(headlineWeight * 100).toFixed(1)}%`);
  document.getElementById('transportWeightVal') && (document.getElementById('transportWeightVal').textContent = `${(transportWeight * 100).toFixed(1)}%`);
  document.getElementById('inflationVal') && (document.getElementById('inflationVal').textContent = `+${inflation.toFixed(1)}%`);

  try {
    const res = await window.api.simulateCpi({
      headline_cpi_weight: headlineWeight,
      transport_weight: transportWeight,
      current_apix_inflation: inflation
    });

    document.getElementById('cpiImpactPp') && (document.getElementById('cpiImpactPp').textContent = `+${res.cpi_headline_impact_pct.toFixed(3)} pp`);
    document.getElementById('cpiImpactBps') && (document.getElementById('cpiImpactBps').textContent = `${res.cpi_headline_impact_basis_points} bps`);
    document.getElementById('cpiTransportImpact') && (document.getElementById('cpiTransportImpact').textContent = `+${res.transport_basket_impact_pct}%`);
  } catch (err) {
    console.error('CPI simulation failed:', err);
  }
}

// Research API Console Tester
async function testApiEndpoint(endpoint) {
  const out = document.getElementById('apiJsonOutput');
  if (!out) return;

  out.textContent = `Executing GET ${endpoint}...`;

  try {
    let res;
    if (endpoint.includes('/predict/price')) {
      res = await window.api.predictPrice('HYD', 'DEL');
    } else if (endpoint.includes('/refunds/track')) {
      res = await window.api.trackRefund('AIRX789');
    } else if (endpoint.includes('/overview')) {
      res = await window.api.getApixOverview();
    } else if (endpoint.includes('/elasticity')) {
      res = await window.api.getRouteElasticity('HYD', 'DEL');
    } else if (endpoint.includes('/quality')) {
      res = await window.api.getQualityReport();
    } else if (endpoint.includes('/routes')) {
      res = await window.api.getRoutes();
    } else {
      res = await window.api.searchFlights({ from_city: 'HYD', to_city: 'DEL' });
    }

    out.textContent = JSON.stringify(res, null, 2);
  } catch (err) {
    out.textContent = JSON.stringify({ error: err.message, status: "failed" }, null, 2);
  }
}

function copyApiResponse() {
  const text = document.getElementById('apiJsonOutput')?.textContent;
  if (text) {
    navigator.clipboard?.writeText(text);
    showToast('API JSON response copied to clipboard!');
  }
}

// Export CSV
function exportRouteData() {
  window.location.href = '/api/v1/routes/export/csv';
  showToast('Downloading AirfareX Route Intelligence CSV...');
}

// =========================================================
// AI AVIATION ASSISTANT (AIRFAREX AI COPILOT)
// =========================================================
let aiChatHistory = [];

function toggleAiAssistant() {
  const windowEl = document.getElementById('aiChatWindow');
  if (!windowEl) return;
  const isHidden = windowEl.classList.toggle('hidden');
  if (!isHidden) {
    const inputEl = document.getElementById('aiInputField');
    if (inputEl) inputEl.focus();
    const chatBody = document.getElementById('aiChatBody');
    if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
  }
}

function clearAiChat() {
  aiChatHistory = [];
  const chatBody = document.getElementById('aiChatBody');
  if (!chatBody) return;
  const welcomeText = window.i18n?.t('ai_welcome_msg', 'Namaste! I am your AirfareX AI Copilot.');
  chatBody.innerHTML = `
    <div class="ai-msg assistant" id="aiWelcomeBubble">
      <div>${welcomeText}</div>
    </div>
  `;
}

function sendAiQuickPrompt(btn) {
  const prompt = btn.textContent.trim().replace(/^[^\w\s\u0900-\u0DFF]+/, '').trim();
  handleSendAiMessage(prompt);
}

function handleAiInputKey(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    handleSendAiMessage();
  }
}

async function handleSendAiMessage(customText = null) {
  const inputEl = document.getElementById('aiInputField');
  const text = customText || (inputEl ? inputEl.value.trim() : '');
  if (!text) return;

  if (inputEl) inputEl.value = '';

  const chatBody = document.getElementById('aiChatBody');
  if (!chatBody) return;

  // Append user message bubble
  const userMsgEl = document.createElement('div');
  userMsgEl.className = 'ai-msg user';
  userMsgEl.textContent = text;
  chatBody.appendChild(userMsgEl);

  // Append typing indicator
  const typingEl = document.createElement('div');
  typingEl.className = 'ai-typing-indicator';
  typingEl.id = 'aiTypingIndicator';
  typingEl.innerHTML = `
    <div class="ai-typing-dot"></div>
    <div class="ai-typing-dot"></div>
    <div class="ai-typing-dot"></div>
  `;
  chatBody.appendChild(typingEl);
  chatBody.scrollTop = chatBody.scrollHeight;

  try {
    const lang = window.i18n?.currentLang || 'en';
    
    // Build rich context for the Travel Copilot
    const searchContext = {
      currentTab: state.currentTab,
      origin: document.getElementById('fFrom')?.value || document.getElementById('fromCity')?.value || 'DEL',
      destination: document.getElementById('fTo')?.value || document.getElementById('toCity')?.value || 'BOM',
      date: document.getElementById('departDate')?.value || null
    };
    const availableFlights = (state.flights || []).slice(0, 8);
    const selectedFlight = state.selectedFlight;

    let res;
    try {
      res = await window.api.chatWithCopilot(
        text,
        searchContext,
        availableFlights,
        selectedFlight,
        state.userPreferences,
        lang
      );
    } catch (copilotErr) {
      // Graceful legacy fallback
      res = await window.api.chatWithAssistant(text, lang, { currentTab: state.currentTab });
    }
    
    // Remove typing indicator
    const curTyping = document.getElementById('aiTypingIndicator');
    if (curTyping) curTyping.remove();

    // Render markdown-like response
    const assistantMsgEl = document.createElement('div');
    assistantMsgEl.className = 'ai-msg assistant';

    // 1. If Agentic Execution Trace is present, render expandable reasoning accordion
    if (res.execution_trace && res.execution_trace.length) {
      const traceBox = document.createElement('div');
      traceBox.className = 'agent-trace-box';
      traceBox.innerHTML = `
        <div class="agent-trace-header" onclick="this.nextElementSibling.classList.toggle('hidden')">
          <span>🧠 Agentic Execution Trace (${res.execution_trace.length} autonomous steps)</span>
          <span style="font-size:10px; opacity:0.8;">[Toggle ▼]</span>
        </div>
        <div class="agent-trace-steps">
          ${res.execution_trace.map(step => `
            <div class="agent-step-item">
              <span class="trace-pill ${step.step_type}">${step.step_type}</span>
              <div>
                <strong style="color:var(--text-main);">${step.title}:</strong>
                <span style="color:var(--text-muted); margin-left:4px;">${step.detail}</span>
              </div>
            </div>
          `).join('')}
        </div>
      `;
      assistantMsgEl.appendChild(traceBox);
    }

    // 2. Format markdown response content (handles both answer and reply)
    const rawText = res.answer || res.reply || "I am ready to help you plan your journey.";
    let formattedReply = rawText
      .replace(/^### (.*$)/gim, '<h3 style="margin:4px 0 8px; color:var(--brand-cyan); font-size:15px;">$1</h3>')
      .replace(/^## (.*$)/gim, '<h3 style="margin:4px 0 8px; color:var(--brand-cyan); font-size:15px;">$1</h3>')
      .replace(/^#### (.*$)/gim, '<h4 style="margin:6px 0 4px; color:var(--brand-blue); font-size:13px;">$1</h4>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code style="background:rgba(0,0,0,0.4); padding:2px 6px; border-radius:4px; color:var(--brand-cyan); font-size:12px; font-weight:700;">$1</code>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');

    const replyDiv = document.createElement('div');
    replyDiv.innerHTML = formattedReply;
    assistantMsgEl.appendChild(replyDiv);

    // Attribution footer in bubble
    const attrDiv = document.createElement('div');
    attrDiv.style.cssText = 'margin-top:8px; font-size:10px; color:var(--text-muted); border-top:1px solid rgba(255,255,255,0.06); padding-top:4px; display:flex; justify-content:space-between;';
    attrDiv.innerHTML = `
      <span>⚡ Powered by AirfareX Intelligence</span>
      <span>Provider: ${res.provider || 'RULE_BASED'}</span>
    `;
    assistantMsgEl.appendChild(attrDiv);

    // 3. Render interactive action buttons
    if (res.action) {
      const actionsWrap = document.createElement('div');
      actionsWrap.className = 'ai-inline-actions';
      
      if (res.action.type === 'open_tab') {
        const btn = document.createElement('button');
        btn.className = 'ai-action-chip';
        const tabNames = {
          'comparison': '⚖️ Open Airline Comparison',
          'monthly-fares': '📅 Open Low-Fare Calendar',
          'offers': '🏷️ View Discount Coupons',
          'guide': '🧭 Open Travel Guide'
        };
        btn.innerHTML = tabNames[res.action.tab] || `Open ${res.action.tab}`;
        btn.onclick = () => {
          showTab(res.action.tab, document.querySelector(`.main-nav a[data-tab="${res.action.tab}"]`));
          if (res.action.tab === 'guide' && res.action.city) {
            showCityDetail(res.action.city);
          }
          toggleAiAssistant();
        };
        actionsWrap.appendChild(btn);
      } else if (res.action.type === 'track_refund' && res.action.pnr) {
        const btn = document.createElement('button');
        btn.className = 'ai-action-chip';
        btn.innerHTML = `🔍 View Refund for PNR ${res.action.pnr}`;
        btn.onclick = () => {
          showTab('refunds', document.querySelector('.main-nav a[data-tab="refunds"]'));
          trackRefundStatus(res.action.pnr);
          toggleAiAssistant();
        };
        actionsWrap.appendChild(btn);
      } else if (res.action.type === 'populate_search') {
        const btn = document.createElement('button');
        btn.className = 'ai-action-chip';
        btn.innerHTML = `✈️ View ${res.action.origin} ➔ ${res.action.destination} Flights (₹${res.action.fare?.toLocaleString('en-IN')})`;
        btn.onclick = () => {
          const fFrom = document.getElementById('fFrom');
          const fTo = document.getElementById('fTo');
          if (fFrom) fFrom.value = res.action.origin;
          if (fTo) fTo.value = res.action.destination;
          showTab('explorer', document.querySelector('.main-nav a[data-tab="explorer"]'));
          loadFlights();
          toggleAiAssistant();
        };
        actionsWrap.appendChild(btn);
      } else if (res.action.type === 'show_prediction') {
        const btn = document.createElement('button');
        btn.className = 'ai-action-chip';
        btn.innerHTML = `🔮 Open ${res.action.origin} ➔ ${res.action.destination} Forecast`;
        btn.onclick = () => {
          const pFrom = document.getElementById('predFrom');
          const pTo = document.getElementById('predTo');
          if (pFrom) pFrom.value = res.action.origin;
          if (pTo) pTo.value = res.action.destination;
          showTab('prediction', document.querySelector('.main-nav a[data-tab="prediction"]'));
          runPricePrediction();
          toggleAiAssistant();
        };
        actionsWrap.appendChild(btn);
      }
      
      assistantMsgEl.appendChild(actionsWrap);
    }

    chatBody.appendChild(assistantMsgEl);

    // Update suggestions chips if returned
    if (res.suggestions && res.suggestions.length) {
      const chipsContainer = document.getElementById('aiQuickChips');
      if (chipsContainer) {
        chipsContainer.innerHTML = res.suggestions.map(s => `
          <button class="ai-suggest-btn" onclick="sendAiQuickPrompt(this)">${s}</button>
        `).join('');
      }
    }

    chatBody.scrollTop = chatBody.scrollHeight;
  } catch (err) {
    const curTyping = document.getElementById('aiTypingIndicator');
    if (curTyping) curTyping.remove();

    const errEl = document.createElement('div');
    errEl.className = 'ai-msg assistant';
    errEl.innerHTML = `<p style="color:var(--brand-amber);">Sorry, I encountered an issue retrieving real-time data. Please try again or check your query.</p>`;
    chatBody.appendChild(errEl);
    chatBody.scrollTop = chatBody.scrollHeight;
  }
}

// =========================================================
// MULTI-AIRLINE SECTOR COMPARISON CONTROLLER
// =========================================================
async function loadSectorComparison() {
  const orig = document.getElementById('compOriginSelect')?.value || 'DEL';
  const dest = document.getElementById('compDestSelect')?.value || 'BOM';

  if (orig === dest) {
    showToast('Origin and destination cannot be identical', false);
    return;
  }

  const tableBody = document.getElementById('comparisonTableBody');
  if (tableBody) {
    tableBody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:30px; color:var(--text-muted);">Analyzing multi-carrier network quotes for ${orig} ➔ ${dest}...</td></tr>`;
  }

  try {
    const data = await window.api.compareSector(orig, dest);
    
    // 1. Update Winner Highlight Cards
    const h = data.highlights;
    if (h) {
      document.getElementById('winCheapestFare') && (document.getElementById('winCheapestFare').textContent = `₹${h.cheapest.fare.toLocaleString('en-IN')}`);
      document.getElementById('winCheapestAirline') && (document.getElementById('winCheapestAirline').textContent = `${h.cheapest.airline} · Economy Value`);
      
      document.getElementById('winOtpVal') && (document.getElementById('winOtpVal').textContent = h.most_punctual.otp);
      document.getElementById('winOtpAirline') && (document.getElementById('winOtpAirline').textContent = `${h.most_punctual.airline} · Punctuality Leader`);
      
      document.getElementById('winComfortPitch') && (document.getElementById('winComfortPitch').textContent = h.most_comfortable.pitch);
      document.getElementById('winComfortAirline') && (document.getElementById('winComfortAirline').textContent = `${h.most_comfortable.airline}`);
      
      document.getElementById('winEcoCo2') && (document.getElementById('winEcoCo2').textContent = h.most_eco_friendly.emissions);
      document.getElementById('winEcoAirline') && (document.getElementById('winEcoAirline').textContent = `${h.most_eco_friendly.airline} · Eco Leader`);
    }

    // 2. Render Table Rows
    if (tableBody && data.airlines) {
      tableBody.innerHTML = data.airlines.map(al => `
        <tr>
          <td>
            <div class="airline-badge-cell">
              <span class="airline-dot" style="background:${al.color};"></span>
              <span>${al.airline}</span>
            </div>
            <div style="font-size:10.5px; color:var(--text-subtle); margin-top:2px;">${al.badge}</div>
          </td>
          <td>
            <b style="font-size:15px; font-family:'JetBrains Mono',monospace; color:var(--text-main);">₹${al.total_fare.toLocaleString('en-IN')}</b>
            <div style="font-size:11px; color:var(--text-muted);">Base ₹${al.base_fare.toLocaleString('en-IN')}</div>
          </td>
          <td><span style="font-size:12.5px;">${al.cabin_baggage}</span></td>
          <td><b style="color:var(--brand-cyan);">${al.checked_baggage}</b></td>
          <td>${al.seat_pitch_inch}" Legroom</td>
          <td><span class="badge ${al.otp_percentage >= 85 ? 'green' : 'amber'}">${al.otp_percentage}%</span></td>
          <td style="font-size:12px;">${al.meals_policy}</td>
          <td style="font-family:'JetBrains Mono',monospace;">₹${al.cancellation_fee.toLocaleString('en-IN')}</td>
          <td style="font-size:11.5px; color:var(--text-muted);">${al.fleet}</td>
          <td>
            <button class="btn sm" onclick="selectFlight('${al.airline}', '${al.iata} 101', ${al.total_fare}, '${dest}', '${dest}')" style="padding:4px 10px; font-size:11px;">
              Select Fare ✈
            </button>
          </td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load comparison:', err);
    if (tableBody) {
      tableBody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:24px; color:var(--brand-rose);">Failed to load comparison data. Please try again.</td></tr>`;
    }
  }
}

// =========================================================
// MONTHLY LOW-FARE CALENDAR MATRIX CONTROLLER
// =========================================================
async function loadMonthlyCalendar() {
  const orig = document.getElementById('calOriginSelect')?.value || 'DEL';
  const dest = document.getElementById('calDestSelect')?.value || 'BOM';

  if (orig === dest) {
    showToast('Origin and destination cannot be identical', false);
    return;
  }

  const gridBody = document.getElementById('calendarGridBody');
  if (gridBody) {
    gridBody.innerHTML = `<div style="grid-column: span 7; text-align:center; padding:30px; color:var(--text-muted);">Generating 30-day low-fare elasticity matrix for ${orig} ➔ ${dest}...</div>`;
  }

  try {
    const data = await window.api.getMonthlyCalendar(orig, dest);

    // 1. Update Ribbon Metrics
    document.getElementById('calCheapestVal') && (document.getElementById('calCheapestVal').textContent = `₹${data.cheapest_fare.toLocaleString('en-IN')}`);
    document.getElementById('calCheapestDaySub') && (document.getElementById('calCheapestDaySub').textContent = `${data.cheapest_weekday}, ${data.cheapest_day} · ${data.cheapest_airline}`);
    document.getElementById('calAvgVal') && (document.getElementById('calAvgVal').textContent = `₹${data.average_fare.toLocaleString('en-IN')}`);
    document.getElementById('calSurgeVal') && (document.getElementById('calSurgeVal').textContent = `₹${data.highest_fare.toLocaleString('en-IN')}`);
    document.getElementById('calSavingsVal') && (document.getElementById('calSavingsVal').textContent = `Save ₹${data.max_potential_savings.toLocaleString('en-IN')}`);
    document.getElementById('calInsightText') && (document.getElementById('calInsightText').textContent = data.insight);

    // 2. Render 7-Column Day Tiles
    if (gridBody && data.days) {
      gridBody.innerHTML = data.days.map(d => `
        <div class="cal-day-tile ${d.category}" onclick="selectCalendarDay('${orig}', '${dest}', '${d.date}', ${d.fare}, '${d.airline}')">
          <div class="cal-tile-top">
            <span class="cal-day-num">${d.day} <small style="font-weight:400; color:var(--text-subtle);">${d.weekday}</small></span>
            <span class="cal-badge ${d.category}">${d.badge}</span>
          </div>
          <div class="cal-tile-fare">₹${d.fare.toLocaleString('en-IN')}</div>
          <div class="cal-tile-airline">${d.airline}</div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load monthly calendar:', err);
    if (gridBody) {
      gridBody.innerHTML = `<div style="grid-column: span 7; text-align:center; padding:24px; color:var(--brand-rose);">Failed to load calendar fares.</div>`;
    }
  }
}

function selectCalendarDay(orig, dest, dateIso, fare, airline) {
  showToast(`Loaded ${dateIso}: ${airline} (₹${fare.toLocaleString('en-IN')})`);
  const fFrom = document.getElementById('fFrom');
  const fTo = document.getElementById('fTo');
  const dDate = document.getElementById('departDate');
  if (fFrom) fFrom.value = orig;
  if (fTo) fTo.value = dest;
  if (dDate) dDate.value = dateIso;

  showTab('explorer', document.querySelector('.main-nav a[data-tab="explorer"]'));
  loadFlights();
}

// =========================================================
// OFFERS & PROMO CODES HUB CONTROLLER
// =========================================================
let cachedOffers = [];

async function loadOffers(category = null) {
  const container = document.getElementById('offersGridContainer');
  if (container) {
    container.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding:30px; color:var(--text-muted);">Fetching active airline coupons and statutory concessions...</div>`;
  }

  try {
    const data = await window.api.listOffers(category);
    cachedOffers = data.offers || [];

    if (container) {
      container.innerHTML = cachedOffers.map(o => `
        <div class="offer-promo-card">
          <div>
            <span class="offer-badge-pill">${o.badge}</span>
            <h3 style="margin:0 0 6px; font-size:16px; color:var(--text-main);">${o.title}</h3>
            <p style="font-size:12.5px; color:var(--text-muted); line-height:1.4;">${o.description}</p>
            ${o.baggage_perk ? `<div style="margin-top:8px; font-size:11.5px; font-weight:700; color:var(--brand-mint);">🧳 ${o.baggage_perk}</div>` : ''}
          </div>

          <div>
            <div class="offer-code-bar">
              <span class="offer-code-text">${o.code}</span>
              <button class="copy-offer-btn" onclick="copyOfferCode('${o.code}')">Copy Code</button>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; color:var(--text-subtle);">
              <span>Min fare: ₹${o.min_fare.toLocaleString('en-IN')}</span>
              <span style="color:var(--brand-blue); cursor:pointer; font-weight:700;" onclick="applyOfferToSearch('${o.code}')">Use on Flight ➔</span>
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load offers:', err);
    if (container) {
      container.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding:24px; color:var(--brand-rose);">Failed to load offers.</div>`;
    }
  }
}

function filterOffers(category, btn) {
  document.querySelectorAll('.offer-filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  loadOffers(category === 'all' ? null : category);
}

function copyOfferCode(code) {
  navigator.clipboard?.writeText(code);
  showToast(`Promo code '${code}' copied to clipboard!`);
}

function applyOfferToSearch(code) {
  const calcCode = document.getElementById('calcPromoCodeInput');
  if (calcCode) calcCode.value = code;
  copyOfferCode(code);
  handleCalculateDiscount();
  const el = document.getElementById('calcDiscountResult');
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function handleCalculateDiscount() {
  const fare = parseInt(document.getElementById('calcFareInput')?.value) || 5500;
  const baseFare = parseInt(document.getElementById('calcBaseFareInput')?.value) || 4400;
  const code = document.getElementById('calcPromoCodeInput')?.value.trim() || 'AIRX500';
  const resultBox = document.getElementById('calcDiscountResult');

  if (!resultBox) return;
  resultBox.style.display = 'block';
  resultBox.innerHTML = '<span style="color:var(--brand-cyan);">Calculating instant discount...</span>';

  try {
    const res = await window.api.validateOffer({
      code,
      base_fare: baseFare,
      total_fare: fare
    });

    resultBox.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
          <div style="font-weight:800; color:var(--brand-mint); font-size:15px;">✓ ${res.message}</div>
          <div style="font-size:12px; color:var(--text-muted); margin-top:3px;">Coupon: <b>${res.code}</b> (${res.title}) ${res.baggage_perk ? `· ${res.baggage_perk}` : ''}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:12px; color:var(--text-subtle); text-decoration:line-through;">Original: ₹${res.original_total.toLocaleString('en-IN')}</div>
          <div style="font-size:20px; font-weight:800; color:var(--brand-cyan); font-family:'JetBrains Mono',monospace;">Net Payable: ₹${res.new_total_fare.toLocaleString('en-IN')}</div>
        </div>
      </div>
    `;
    showToast(`Saved ₹${res.discount_amount.toLocaleString('en-IN')} with code ${res.code}!`);
  } catch (err) {
    resultBox.innerHTML = `
      <div style="color:var(--brand-rose); font-weight:700;">✕ ${err.message || 'Invalid promo code or minimum fare requirement not met.'}</div>
    `;
  }
}

// =========================================================
// TOURIST PACKAGES & SIDE-BY-SIDE PRICING CONTROLLER
// =========================================================
let currentTouristDestination = 'all';

async function loadTouristPlans(destination = null) {
  const container = document.getElementById('touristPlansContainer');
  if (!container) return;

  container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">Finding best vacation packages and side-by-side pricing...</div>`;

  try {
    const data = await window.api.getTouristPlans(destination === 'all' ? null : destination);
    state.touristPlans = data.plans || [];
    renderTouristCards(state.touristPlans);
  } catch (err) {
    console.error('Failed to load tourist plans:', err);
    container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--brand-rose);">Failed to load packages. Please check API server.</div>`;
  }
}

function filterTouristPlans(dest, btn) {
  currentTouristDestination = dest;
  document.querySelectorAll('.tourist-pill-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  loadTouristPlans(dest === 'all' ? null : dest);
}

function renderTouristCards(plans) {
  const container = document.getElementById('touristPlansContainer');
  if (!container) return;

  if (!plans || !plans.length) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 50px 20px; background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
        <h3 style="margin-bottom: 8px;">No packages found for ${currentTouristDestination}</h3>
        <p style="color: var(--text-muted);">Try selecting "All Destinations" to explore other curated holiday packages.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = plans.map(p => {
    const regularPrice = p.pricing.price_without_offers;
    const offerPrice = p.pricing.price_with_offers;
    const savings = p.pricing.savings;
    const discountPct = p.pricing.discount_pct;
    const promoCode = p.pricing.applied_promo;

    return `
      <div class="tourist-card" id="card-${p.id}">
        <div>
          <!-- Card Media Banner -->
          <div class="tourist-card-media">
            <img src="${p.image_url}" alt="${p.title}" class="tourist-card-img" onerror="this.src='/assets/images/hero_aviation.jpg'">
            <span class="tourist-duration-pill">⏱️ ${p.duration}</span>
            <span class="tourist-dest-pill">📍 ${p.destination}</span>
          </div>

          <!-- Card Header & Description -->
          <div style="padding: 16px 18px 8px;">
            <h3 style="font-size: 17px; font-weight: 800; margin-bottom: 4px; color: var(--text-main);">${p.title}</h3>
            <p style="font-size: 12.5px; color: var(--text-muted); line-height: 1.4; margin-bottom: 12px;">${p.tagline}</p>

            <!-- Flight Included Details -->
            <div class="bundle-component-item">
              <div class="bundle-icon">✈️</div>
              <div class="bundle-info">
                <div class="bundle-title">Flight Included: <b>${p.flight.carrier}</b></div>
                <div class="bundle-sub">${p.flight.sector} · ${p.flight.baggage}</div>
              </div>
            </div>

            <!-- Hotel Included Details -->
            <div class="bundle-component-item">
              <div class="bundle-icon">🏨</div>
              <div class="bundle-info">
                <div class="bundle-title">4-Star Hotel: <b>${p.hotel.name}</b></div>
                <div class="bundle-sub">★ ${p.hotel.rating} Rating · ${p.hotel.room_type}</div>
              </div>
            </div>

            <!-- Side-by-Side Pricing Box (Requested Feature) -->
            <div class="side-by-side-pricing-box">
              <div class="pricing-columns-wrapper">
                <div class="price-col regular">
                  <span class="price-col-label">Without Offers</span>
                  <span class="price-col-val regular">₹${regularPrice.toLocaleString('en-IN')}</span>
                  <span style="font-size: 9.5px; color: var(--text-subtle); margin-top: 2px;">Standard Rack Rate</span>
                </div>
                <div class="price-col offer">
                  <span class="price-col-label">With AirfareX Offers ✨</span>
                  <span class="price-col-val offer">₹${offerPrice.toLocaleString('en-IN')}</span>
                  <span style="font-size: 9.5px; color: var(--brand-cyan); margin-top: 2px;">All Taxes & Perks Included</span>
                </div>
              </div>

              <div class="pricing-savings-bar">
                <span class="savings-badge-pill">🏷️ Save ₹${savings.toLocaleString('en-IN')} (${discountPct}% OFF)</span>
                <span class="promo-applied-label">Code: ${promoCode}</span>
              </div>
            </div>

            <!-- Embedded Day-by-Day Itinerary Accordion -->
            <button class="itinerary-accordion-toggle" onclick="toggleItinerary('${p.id}')">
              <span>🗺️ Day-by-Day Sightseeing Schedule</span>
              <span id="itinIcon-${p.id}">▼</span>
            </button>
            <div id="itinBox-${p.id}" class="itinerary-steps-box" style="display: none;">
              ${p.itinerary.map(day => `
                <div class="itinerary-day-bullet">
                  <b style="color: var(--brand-cyan);">${day.day}: ${day.title}</b>
                  <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
                    ${day.activities.slice(0, 2).join(' · ')}
                  </div>
                </div>
              `).join('')}
              <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 10.5px; color: var(--brand-mint);">
                ✓ Return Airport Transfers & Sightseeing Guide Included
              </div>
            </div>
          </div>
        </div>

        <!-- Package Action Buttons: View Details & Instant Book -->
        <div style="padding: 0 18px 18px; display: grid; grid-template-columns: 1fr 1.2fr; gap: 10px;">
          <button type="button" class="btn light sm" onclick="openPackageDetailsModal('${p.id}')" style="font-weight:700; border-radius:var(--radius-sm); font-size:12.5px; padding:10px 0; justify-content:center;">
            View Details
          </button>
          <button type="button" class="tourist-book-btn" onclick="openPackageBookingModal('${p.id}')" style="margin-top:0;">
            Book Package ➔
          </button>
        </div>
      </div>
    `;
  }).join('');
}

let currentDetailPackageId = null;

function openPackageDetailsModal(planId) {
  const plan = state.touristPlans?.find(p => p.id === planId);
  if (!plan) return;

  currentDetailPackageId = planId;
  const modal = document.getElementById('packageDetailsModal');
  if (!modal) return;

  const imgEl = document.getElementById('pkgDetailImg');
  const durationEl = document.getElementById('pkgDetailDuration');
  const destEl = document.getElementById('pkgDetailDest');
  const titleEl = document.getElementById('pkgDetailTitle');
  const taglineEl = document.getElementById('pkgDetailTagline');
  const carrierEl = document.getElementById('pkgDetailCarrier');
  const hotelEl = document.getElementById('pkgDetailHotel');
  const itinList = document.getElementById('pkgDetailItineraryList');
  const offerPriceEl = document.getElementById('pkgDetailOfferPrice');
  const regularPriceEl = document.getElementById('pkgDetailRegularPrice');
  const savingsPill = document.getElementById('pkgDetailSavingsPill');

  if (imgEl) imgEl.src = plan.image_url || '/assets/images/hero_aviation.jpg';
  if (durationEl) durationEl.textContent = `⏱️ ${plan.duration}`;
  if (destEl) destEl.textContent = `📍 ${plan.destination}`;
  if (titleEl) titleEl.textContent = plan.title;
  if (taglineEl) taglineEl.textContent = plan.tagline;
  if (carrierEl) carrierEl.textContent = `${plan.flight.carrier} (${plan.flight.sector})`;
  if (hotelEl) hotelEl.textContent = `${plan.hotel.name} (★ ${plan.hotel.rating})`;
  if (offerPriceEl) offerPriceEl.textContent = `₹${plan.pricing.price_with_offers.toLocaleString('en-IN')}`;
  if (regularPriceEl) regularPriceEl.textContent = `₹${plan.pricing.price_without_offers.toLocaleString('en-IN')}`;
  if (savingsPill) savingsPill.textContent = `Save ₹${plan.pricing.savings.toLocaleString('en-IN')}`;

  if (itinList && plan.itinerary) {
    itinList.innerHTML = plan.itinerary.map(day => `
      <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:8px; padding:12px 14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <b style="color:var(--brand-cyan); font-size:13px;">${day.day}: ${day.title}</b>
          <span class="badge blue" style="font-size:10px;">Day Activity</span>
        </div>
        <div style="font-size:12px; color:var(--text-muted); line-height:1.5;">
          ${day.activities.join(' · ')}
        </div>
      </div>
    `).join('');
  }

  modal.classList.add('active');
}

function bookCurrentDetailPackage() {
  closeModal('packageDetailsModal');
  if (currentDetailPackageId) {
    openPackageBookingModal(currentDetailPackageId);
  }
}

function toggleItinerary(planId) {
  const box = document.getElementById(`itinBox-${planId}`);
  const icon = document.getElementById(`itinIcon-${planId}`);
  if (!box) return;

  const isHidden = box.style.display === 'none';
  box.style.display = isHidden ? 'block' : 'none';
  if (icon) icon.textContent = isHidden ? '▲' : '▼';
}

function openPackageBookingModal(planId) {
  const plan = state.touristPlans?.find(p => p.id === planId);
  if (!plan) return;

  state.selectedPackage = plan;
  const detailsBox = document.getElementById('packageBookingDetails');
  const dateInput = document.getElementById('pkgTravelDate');

  if (detailsBox) {
    detailsBox.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
        <div>
          <h3 style="margin:0 0 4px; font-size:16px; color:var(--brand-cyan);">${plan.title}</h3>
          <span class="metric-sub">${plan.destination} · ${plan.duration}</span>
        </div>
        <span class="badge green">Direct Booking Active</span>
      </div>
      <div style="font-size:12px; color:var(--text-main); margin-bottom:6px;">
        ✈️ <b>Flight:</b> ${plan.flight.carrier} (${plan.flight.sector})
      </div>
      <div style="font-size:12px; color:var(--text-main); margin-bottom:10px;">
        🏨 <b>Hotel:</b> ${plan.hotel.name} (${plan.hotel.room_type})
      </div>
      <div style="font-size:11.5px; color:var(--text-muted); border-top:1px solid rgba(255,255,255,0.06); padding-top:6px;">
        ✨ <b>Inclusions:</b> ${(plan.inclusions || []).join(' · ')}
      </div>
    `;
  }

  if (dateInput && !dateInput.value) {
    dateInput.value = new Date(Date.now() + 86400000 * 14).toISOString().slice(0, 10);
  }

  onPackagePaxOrPromoChanged();
  openModal('bookPackageModal');
}

async function onPackagePaxOrPromoChanged() {
  if (!state.selectedPackage) return;
  const plan = state.selectedPackage;

  const paxEl = document.getElementById('pkgPaxCount');
  const promoEl = document.getElementById('pkgPromoInput');
  const pax = parseInt(paxEl ? paxEl.value : '1', 10) || 1;
  const promoCode = promoEl ? promoEl.value.trim().toUpperCase() : '';

  try {
    // Authoritative Server-Side Price Calculation
    const quote = await window.api.calculatePaymentPrice({
      booking_type: 'package',
      package_id: plan.id,
      pax_count: pax,
      promo_code: promoCode
    });

    state.currentPackageQuote = quote;

    const baseEl = document.getElementById('pkgBreakdownBase');
    const offerEl = document.getElementById('pkgBreakdownOffer');
    const promoRow = document.getElementById('pkgBreakdownPromoRow');
    const promoEl2 = document.getElementById('pkgBreakdownPromo');
    const payableEl = document.getElementById('pkgPayableAmount');
    const btnText = document.getElementById('btnProceedText');

    const baseUnit = plan.pricing.price_without_offers || 0;
    const totalBase = baseUnit * pax;
    const packageDiscount = (plan.pricing.savings || 0) * pax;
    const extraPromoDiscount = Math.max(0, quote.discount - packageDiscount);

    if (baseEl) baseEl.textContent = `₹${totalBase.toLocaleString('en-IN')}`;
    if (offerEl) offerEl.textContent = `-₹${packageDiscount.toLocaleString('en-IN')}`;

    if (promoRow && promoEl2) {
      if (extraPromoDiscount > 0) {
        promoRow.style.display = 'flex';
        promoEl2.textContent = `-₹${extraPromoDiscount.toLocaleString('en-IN')} (${quote.promo_applied})`;
      } else {
        promoRow.style.display = 'none';
      }
    }

    if (payableEl) payableEl.textContent = `₹${quote.final_payable_amount.toLocaleString('en-IN')}`;
    if (btnText) btnText.textContent = `Proceed to Payment (₹${quote.final_payable_amount.toLocaleString('en-IN')})`;

    const btn = document.getElementById('btnProceedPackagePayment');
    if (btn) btn.disabled = false;

  } catch (err) {
    console.warn('Failed to calculate server quote:', err);
    state.currentPackageQuote = null;
    const btn = document.getElementById('btnProceedPackagePayment');
    if (btn) btn.disabled = true;
    const btnText = document.getElementById('btnProceedText');
    if (btnText) btnText.textContent = 'Fare Calculation Unavailable';
    const payableEl = document.getElementById('pkgPayableAmount');
    if (payableEl) payableEl.textContent = 'Unable to calculate the latest fare. Please try again.';
  }
}

async function initiatePackagePayment() {
  if (!state.selectedPackage) return;
  if (!state.currentPackageQuote) {
    showToast('Unable to calculate the latest fare. Please try again.', false);
    return;
  }
  const plan = state.selectedPackage;

  const travelerName = document.getElementById('pkgTravelerName')?.value?.trim();
  const travelerEmail = document.getElementById('pkgTravelerEmail')?.value?.trim();
  const travelerPhone = document.getElementById('pkgTravelerPhone')?.value?.trim();
  const travelDate = document.getElementById('pkgTravelDate')?.value;
  const pax = parseInt(document.getElementById('pkgPaxCount')?.value || '1', 10) || 1;
  const promo = document.getElementById('pkgPromoInput')?.value?.trim();

  if (!travelerName || !travelerEmail || !travelerPhone || !travelDate) {
    showToast('Please fill all mandatory traveler contact & date fields', false);
    return;
  }

  const btn = document.getElementById('btnProceedPackagePayment');
  const btnText = document.getElementById('btnProceedText');
  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = 'Creating Payment Order...';

  try {
    const orderPayload = {
      booking_type: 'package',
      package_id: plan.id,
      traveler_name: travelerName,
      email: travelerEmail,
      phone: travelerPhone,
      travel_date: travelDate,
      pax_count: pax,
      promo_code: promo || null
    };

    const orderRes = await window.api.createPaymentOrder(orderPayload);
    state.activePaymentOrder = orderRes;

    closeModal('bookPackageModal');

    if (orderRes.is_sandbox) {
      // Open Cryptographic Sandbox Gateway
      const sbxOrderId = document.getElementById('sbxOrderId');
      const sbxAmount = document.getElementById('sbxAmount');
      const sbxTraveler = document.getElementById('sbxTraveler');
      const sbxProcessing = document.getElementById('sbxProcessing');
      const sbxActions = document.getElementById('sbxActionButtons');

      if (sbxOrderId) sbxOrderId.textContent = orderRes.order_id;
      if (sbxAmount) sbxAmount.textContent = `₹${orderRes.amount_inr.toLocaleString('en-IN')}`;
      if (sbxTraveler) sbxTraveler.textContent = `${travelerName} (${pax} Pax)`;
      if (sbxProcessing) sbxProcessing.style.display = 'none';
      if (sbxActions) sbxActions.style.display = 'flex';

      openModal('sandboxPaymentModal');
    } else {
      // Official Razorpay Gateway
      launchRazorpayCheckout(orderRes);
    }

  } catch (err) {
    console.error('Failed to initiate payment order:', err);
    showToast(err.message || 'Payment initiation failed. Please retry.', false);
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = 'Proceed to Payment';
  }
}

function launchRazorpayCheckout(order) {
  if (typeof Razorpay === 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => openRazorpayModal(order);
    script.onerror = () => {
      showToast('Could not load Razorpay SDK. Please check internet connection.', false);
    };
    document.body.appendChild(script);
  } else {
    openRazorpayModal(order);
  }
}

function openRazorpayModal(order) {
  const options = {
    key: order.key_id,
    amount: order.amount_paise,
    currency: order.currency || 'INR',
    name: 'AirfareX India',
    description: order.package_title || 'Holiday Package Booking',
    order_id: order.order_id,
    prefill: {
      name: order.traveler_name,
      email: order.email,
      contact: order.phone
    },
    theme: {
      color: '#0ea5e9'
    },
    handler: async function (response) {
      try {
        showToast('Verifying payment signature with banking gateway...');
        const verifyRes = await window.api.verifyPayment({
          booking_id: order.booking_id,
          order_id: response.razorpay_order_id,
          payment_id: response.razorpay_payment_id,
          signature: response.razorpay_signature
        });
        showConfirmedPackageVoucher(verifyRes);
      } catch (err) {
        showPaymentFailureView(order.order_id, order.amount_inr, err.message || 'Signature verification failed.');
      }
    },
    modal: {
      ondismiss: function () {
        showPaymentFailureView(order.order_id, order.amount_inr, 'Payment was cancelled or closed by user.');
      }
    }
  };

  const rzp = new Razorpay(options);
  rzp.on('payment.failed', function (resp) {
    showPaymentFailureView(order.order_id, order.amount_inr, resp.error.description || 'Payment declined by bank.');
  });
  rzp.open();
}

async function executeSandboxPayment(action) {
  const order = state.activePaymentOrder;
  if (!order) return;

  const sbxProcessing = document.getElementById('sbxProcessing');
  const sbxActions = document.getElementById('sbxActionButtons');
  const sbxText = document.getElementById('sbxProcessText');

  if (sbxActions) sbxActions.style.display = 'none';
  if (sbxProcessing) sbxProcessing.style.display = 'block';

  if (action === 'AUTHORIZE') {
    if (sbxText) sbxText.textContent = 'Contacting Banking Switch & Validating HMAC Signature...';
  } else {
    if (sbxText) sbxText.textContent = 'Simulating Payment Decline from Banking Switch...';
  }

  try {
    const res = await window.api.sandboxAuthorize({
      order_id: order.order_id,
      booking_id: order.booking_id,
      action: action,
      failure_reason: action === 'DECLINE' ? 'User cancelled or declined authorization' : null
    });

    setTimeout(() => {
      closeModal('sandboxPaymentModal');
      if (res && res.status === 'CONFIRMED') {
        showConfirmedPackageVoucher(res);
      } else {
        showPaymentFailureView(order.order_id, order.amount_inr, res.message || 'Payment authorization declined.');
      }
    }, 800);

  } catch (err) {
    setTimeout(() => {
      closeModal('sandboxPaymentModal');
      showPaymentFailureView(order.order_id, order.amount_inr, err.message || 'Authorization rejected.');
    }, 700);
  }
}

function showConfirmedPackageVoucher(res) {
  document.getElementById('pkgConfPnr') && (document.getElementById('pkgConfPnr').textContent = res.pnr || res.booking_id);
  document.getElementById('pkgConfHotelVoucher') && (document.getElementById('pkgConfHotelVoucher').textContent = res.voucher_id || 'HTL-84920');
  document.getElementById('pkgConfTitle') && (document.getElementById('pkgConfTitle').textContent = res.package_title || state.selectedPackage?.title || 'Tour Package');
  document.getElementById('pkgConfTraveler') && (document.getElementById('pkgConfTraveler').textContent = res.traveler_name || 'Guest Traveler');
  document.getElementById('pkgConfDatePax') && (document.getElementById('pkgConfDatePax').textContent = `${res.travel_date || ''} · Verified Booking`);
  document.getElementById('pkgConfSeat') && (document.getElementById('pkgConfSeat').textContent = `Seat ${res.seat_number || '14A'} (Confirmed)`);
  document.getElementById('pkgConfPayId') && (document.getElementById('pkgConfPayId').textContent = res.payment_id || 'PGW-SUCCESS');
  document.getElementById('pkgConfAmount') && (document.getElementById('pkgConfAmount').textContent = `₹${(res.amount_inr || 0).toLocaleString('en-IN')}`);

  openModal('packageConfirmedModal');
  showToast(`🎉 Booking Confirmed! Official PNR: ${res.pnr || res.booking_id}`);
}

function showPaymentFailureView(orderId, amount, reason) {
  document.getElementById('pkgFailOrderId') && (document.getElementById('pkgFailOrderId').textContent = orderId || 'order_unknown');
  document.getElementById('pkgFailAmount') && (document.getElementById('pkgFailAmount').textContent = `₹${(amount || 0).toLocaleString('en-IN')}`);
  document.getElementById('pkgFailReason') && (document.getElementById('pkgFailReason').textContent = reason || 'Payment authorization declined by issuing bank');

  openModal('packageFailedModal');
  showToast('Payment declined: No seats or hotel rooms booked.', false);
}

window.openPackageBookingModal = openPackageBookingModal;
window.onPackagePaxOrPromoChanged = onPackagePaxOrPromoChanged;
window.initiatePackagePayment = initiatePackagePayment;
window.executeSandboxPayment = executeSandboxPayment;
window.showConfirmedPackageVoucher = showConfirmedPackageVoucher;
window.showPaymentFailureView = showPaymentFailureView;

// Event Listeners on DOMContentLoaded
window.addEventListener('DOMContentLoaded', () => {
  initApp();

  // Listen for languageChanged event to automatically re-render active sections
  window.addEventListener('languageChanged', (e) => {
    const lang = e.detail?.lang || 'en';
    window.i18n?.translatePage();
    
    // Re-render currently active tab
    if (state.currentTab === 'explorer') {
      renderFlights(state.flights);
    } else if (state.currentTab === 'prediction') {
      runPricePrediction();
    } else if (state.currentTab === 'refunds') {
      trackRefundStatus(state.currentRefund?.pnr || 'AIRX789');
    } else if (state.currentTab === 'routes') {
      loadRoutes();
    }

    // Refresh AI Assistant welcome bubble if no conversation has started yet
    const welcomeBubble = document.getElementById('aiWelcomeBubble');
    if (welcomeBubble && document.querySelectorAll('.ai-msg').length <= 1) {
      welcomeBubble.innerHTML = window.i18n?.t('ai_welcome_msg');
    }

    showToast(`Language switched to ${lang.toUpperCase()} successfully!`);
  });

  // Close modals on backdrop click
  window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop')) {
      e.target.classList.remove('open');
    }
  });

  // ESC key closes modals & AI Assistant
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop.open').forEach(m => m.classList.remove('open'));
      const aiWindow = document.getElementById('aiChatWindow');
      if (aiWindow && !aiWindow.classList.contains('hidden')) {
        aiWindow.classList.add('hidden');
      }
    }
  });
});

// =========================================================
// SYSTEM & SUPABASE STATUS (READ-ONLY)
// =========================================================
async function checkSupabaseConnectionLive() {
  try {
    const res = await window.api.getSupabaseStatus();
    return res;
  } catch (err) {
    console.warn('[Supabase Status]', err.message);
    return { connected: false, message: err.message };
  }
}

window.checkSupabaseConnectionLive = checkSupabaseConnectionLive;

// =========================================================
// CUSTOMER TRIPS & BOOKINGS (MY TRIPS)
// =========================================================
state.myTrips = [];
state.tripFilter = 'All';

async function loadMyTrips() {
  const container = document.getElementById('myTripsListContainer');
  if (!container) return;

  if (!window.auth || !window.auth.isAuthenticated()) {
    container.innerHTML = `
      <div class="card empty-box" style="margin-top:14px; text-align:center; padding:50px 20px;">
        <span style="font-size:42px; display:block; margin-bottom:12px;">🔒</span>
        <h3 style="margin-bottom:6px; font-size:18px;">Sign In to View Your Bookings</h3>
        <p style="font-size:13px; color:var(--text-muted); max-width:440px; margin:0 auto 18px;">
          Access your confirmed e-tickets, boarding passes, flight vouchers, and real-time trip status.
        </p>
        <button class="btn primary" onclick="openAuthModal('login')">Sign In / Create Account</button>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div style="text-align:center; padding:40px; color:var(--text-muted);">
      <div class="loading-spinner" style="margin:0 auto 10px;"></div>
      <span>Loading your bookings...</span>
    </div>
  `;

  try {
    const trips = await window.api.getMyTrips();
    state.myTrips = trips || [];
    renderTripsList();
  } catch (err) {
    container.innerHTML = `
      <div class="card" style="padding:24px; text-align:center; color:var(--brand-rose);">
        <p>Could not load bookings: ${err.message || 'Network error'}</p>
        <button class="btn sm light" onclick="loadMyTrips()">Retry</button>
      </div>
    `;
  }
}

function renderTripsList() {
  const container = document.getElementById('myTripsListContainer');
  if (!container) return;

  const filtered = state.myTrips.filter(t => {
    if (state.tripFilter === 'All') return true;
    return t.trip_category === state.tripFilter;
  });

  if (!filtered.length) {
    container.innerHTML = `
      <div class="card empty-box" style="margin-top:14px; text-align:center; padding:50px 20px;">
        <span style="font-size:42px; display:block; margin-bottom:12px;">✈️</span>
        <h3 style="margin-bottom:6px; font-size:18px;">No ${state.tripFilter !== 'All' ? state.tripFilter.toLowerCase() : ''} bookings found</h3>
        <p style="font-size:13px; color:var(--text-muted); max-width:440px; margin:0 auto 18px;">
          When you book flight tickets or holiday packages on AirfareX, your confirmed itineraries and e-tickets will be stored securely here.
        </p>
        <button class="btn primary sm" onclick="showTab('explorer')">Explore Flights & Deals</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(t => {
    const statusBadgeClass = t.payment_status === 'PAYMENT_VERIFIED' || t.booking_status === 'BOOKING_CONFIRMED' || t.booking_status === 'CONFIRMED'
      ? 'green'
      : (t.booking_status === 'CANCELLED' || t.payment_status === 'FAILED' ? 'rose' : 'amber');

    const catBadge = t.trip_category === 'Upcoming' ? 'blue' : (t.trip_category === 'Completed' ? 'gray' : 'rose');

    const passengerNames = t.passengers && t.passengers.length
      ? t.passengers.map(p => p.full_name).join(', ')
      : t.traveler_name;

    const bRef = t.booking_reference || t.booking_id.slice(-8).toUpperCase();
    const isCancellable = ['PENDING_PAYMENT', 'CONFIRMED', 'BOOKING_CONFIRMED', 'DRAFT'].includes(t.booking_status);

    return `
      <div class="card" style="margin-bottom:16px; padding:20px; border-radius:var(--radius-lg); border:1px solid var(--border-color); background:var(--bg-surface); box-shadow:var(--shadow-sm);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px; margin-bottom:14px; border-bottom:1px solid var(--border-color); padding-bottom:12px;">
          <div>
            <span class="badge ${catBadge}" style="font-weight:700; margin-right:8px;">${t.trip_category.toUpperCase()}</span>
            <span style="font-family:'JetBrains Mono', monospace; font-size:14px; font-weight:800; color:var(--brand-cyan);">Ref: ${bRef}</span>
            <span style="font-size:11px; color:var(--text-muted); margin-left:8px;">(${t.booking_id})</span>
            ${t.pnr ? `<span style="margin-left:10px; font-size:12.5px; color:var(--text-muted);">PNR: <b style="color:var(--text-main);">${t.pnr}</b></span>` : ''}
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="data-source-pill" style="font-size:10px; padding:2px 6px; border-radius:4px; font-weight:700; background:rgba(245,158,11,0.15); color:#fbbf24; border:1px solid rgba(245,158,11,0.3);">[${t.data_source || 'DEVELOPMENT'}]</span>
            <span class="badge ${statusBadgeClass}" style="font-weight:700;">${t.booking_status}</span>
          </div>
        </div>

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin-bottom:14px;">
          <div>
            <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase; font-weight:700; letter-spacing:0.3px;">Sector / Flight</div>
            <div style="font-size:16px; font-weight:800; color:var(--text-main); margin-top:2px;">
              ${t.sector || 'Domestic Flight'}
            </div>
            <div style="font-size:12.5px; color:var(--text-muted);">
              ${t.airline ? `${t.airline} · ` : ''}<b>${t.flight_no || 'Scheduled'}</b>
            </div>
          </div>

          <div>
            <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase; font-weight:700; letter-spacing:0.3px;">Travel Date</div>
            <div style="font-size:15px; font-weight:700; color:var(--text-main); margin-top:2px;">
              📅 ${t.travel_date}
            </div>
            ${t.seat_number ? `<div style="font-size:12px; color:var(--text-muted);">Seat: <b style="color:var(--brand-cyan);">${t.seat_number}</b></div>` : ''}
          </div>

          <div>
            <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase; font-weight:700; letter-spacing:0.3px;">Travelers (${t.pax_count})</div>
            <div style="font-size:13.5px; font-weight:600; color:var(--text-main); margin-top:2px;">
              👤 ${passengerNames}
            </div>
          </div>

          <div style="text-align:right;">
            <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase; font-weight:700; letter-spacing:0.3px;">Total Amount</div>
            <div style="font-size:18px; font-weight:800; color:var(--text-main); font-family:'JetBrains Mono', monospace; margin-top:2px;">
              ₹${t.amount.toLocaleString('en-IN')}
            </div>
            <div style="font-size:11px; color:var(--text-muted);">${t.payment_status}</div>
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed var(--border-color); padding-top:12px; flex-wrap:wrap; gap:8px;">
          <div style="font-size:11.5px; color:var(--text-muted);">
            Booked on ${t.created_at ? t.created_at.split('T')[0] : 'Recent'} · <span style="color:#fbbf24;">${t.development_notice || 'Development booking'}</span>
          </div>
          <div style="display:flex; gap:8px;">
            <button class="btn sm light" onclick="viewTripDetailsModal('${t.booking_id}')">View Details</button>
            ${isCancellable ? `<button class="btn sm light" onclick="cancelTripBookingPrompt('${t.booking_id}')" style="color:var(--brand-rose); border-color:rgba(244,63,94,0.3);">Cancel Booking</button>` : ''}
            ${t.pnr ? `<button class="btn sm light" onclick="trackRefundDirect('${t.pnr}')">Refund Status</button>` : ''}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function filterTrips(category, btn) {
  state.tripFilter = category;
  document.querySelectorAll('#trips .tab-btn').forEach(b => {
    b.style.background = 'var(--bg-surface)';
    b.style.color = 'var(--text-main)';
  });
  if (btn) {
    btn.style.background = 'var(--brand-navy, #0f2447)';
    btn.style.color = '#fff';
  }
  renderTripsList();
}

function trackRefundDirect(pnr) {
  showTab('refunds');
  trackRefundStatus(pnr);
}

async function viewTripDetailsModal(bookingId) {
  try {
    showToast('Fetching booking details...');
    const b = await window.api.getBooking(bookingId);
    if (!b) return;

    const modalId = 'tripDetailsModal';
    let modal = document.getElementById(modalId);
    if (!modal) {
      modal = document.createElement('div');
      modal.id = modalId;
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    const paxList = b.passengers && b.passengers.length
      ? b.passengers.map((p, idx) => `
          <div style="padding:8px 12px; background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:6px; margin-bottom:6px; font-size:12px; display:flex; justify-content:space-between;">
            <div><b>${idx+1}. ${p.title || 'Mr'}. ${p.first_name || ''} ${p.last_name || p.full_name || ''}</b> (${p.passenger_type || 'ADULT'})</div>
            <div>${p.seat_number ? `Seat: <b style="color:var(--brand-cyan);">${p.seat_number}</b>` : ''} · ${p.gender || 'Male'}</div>
          </div>
        `).join('')
      : `<div style="font-size:12px; color:var(--text-muted);">${b.contact?.name || 'Valued Passenger'}</div>`;

    const pr = b.pricing || {};

    modal.innerHTML = `
      <div class="modal-card" style="max-width:560px; width:90%; max-height:90vh; overflow-y:auto; padding:24px; border-radius:var(--radius-lg); background:var(--bg-card); border:1px solid var(--border-color);">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color); padding-bottom:12px; margin-bottom:16px;">
          <div>
            <h3 style="margin:0; font-size:18px; color:var(--text-main);">Booking Reference: <span style="color:var(--brand-cyan); font-family:'JetBrains Mono',monospace;">${b.booking_reference || b.booking_id}</span></h3>
            <div style="font-size:11px; color:var(--text-muted);">ID: ${b.booking_id}</div>
          </div>
          <button class="btn sm light" onclick="document.getElementById('${modalId}').classList.remove('open')" style="font-size:16px; padding:2px 8px;">✕</button>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:12.5px; margin-bottom:16px;">
          <div>
            <span style="color:var(--text-muted);">Status:</span> <b class="badge ${b.booking_status === 'CONFIRMED' || b.booking_status === 'BOOKING_CONFIRMED' ? 'green' : 'amber'}">${b.booking_status}</b>
          </div>
          <div>
            <span style="color:var(--text-muted);">Payment:</span> <b>${b.payment_status}</b>
          </div>
          <div>
            <span style="color:var(--text-muted);">Sector:</span> <b>${b.sector || 'Domestic Route'}</b>
          </div>
          <div>
            <span style="color:var(--text-muted);">Travel Date:</span> <b>${b.travel_date}</b>
          </div>
          <div>
            <span style="color:var(--text-muted);">Airline:</span> <b>${b.airline || 'IndiGo'} (${b.flight_no || '6E-205'})</b>
          </div>
          <div>
            <span style="color:var(--text-muted);">PNR:</span> <b style="color:var(--brand-cyan);">${b.pnr || 'Pending allocation'}</b>
          </div>
        </div>

        <div style="margin-bottom:16px;">
          <h4 style="font-size:13px; text-transform:uppercase; color:var(--text-muted); margin-bottom:8px;">Itemized Passengers (${b.passenger_count || 1})</h4>
          ${paxList}
        </div>

        <div style="margin-bottom:16px; padding:12px; background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; font-size:12px;">
          <h4 style="font-size:12px; text-transform:uppercase; color:var(--text-muted); margin-bottom:8px;">Authoritative Fare Breakdown</h4>
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;"><span>Base Fare:</span> <span>₹${(pr.base_price || 0).toLocaleString('en-IN')}</span></div>
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;"><span>Taxes & Fees (UDF, ASF, 5% GST):</span> <span>₹${(pr.taxes_and_fees || 0).toLocaleString('en-IN')}</span></div>
          ${pr.discount ? `<div style="display:flex; justify-content:space-between; margin-bottom:4px; color:var(--brand-mint);"><span>Discount Applied:</span> <span>-₹${pr.discount.toLocaleString('en-IN')}</span></div>` : ''}
          <div style="display:flex; justify-content:space-between; font-weight:800; font-size:14px; border-top:1px dashed var(--border-color); padding-top:6px; margin-top:6px;"><span>Total Paid:</span> <span style="color:var(--brand-cyan);">₹${(pr.final_payable_amount || b.amount || 0).toLocaleString('en-IN')}</span></div>
        </div>

        <div style="padding:10px 12px; background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.25); border-radius:8px; font-size:11px; color:#fbbf24; text-align:center; margin-bottom:16px;">
          ℹ️ ${b.development_notice || 'Development booking — airline ticket issuance is not connected in this environment.'}
        </div>

        <div style="display:flex; justify-content:flex-end; gap:8px;">
          <button class="btn sm light" onclick="document.getElementById('${modalId}').classList.remove('open')">Close</button>
        </div>
      </div>
    `;

    modal.classList.add('open');
  } catch (err) {
    showToast(`Could not load booking details: ${err.message || err}`, false);
  }
}

async function cancelTripBookingPrompt(bookingId) {
  if (!confirm(`Are you sure you want to cancel booking ${bookingId}? DGCA statutory refund rules will be applied.`)) {
    return;
  }

  try {
    showToast('Processing booking cancellation with DGCA refund engine...');
    const res = await window.api.cancelBooking(bookingId);
    showToast(`✓ Booking cancelled. Refund of ₹${res.refund_amount.toLocaleString('en-IN')} initiated (ARN: ${res.refund_arn || 'N/A'}).`);
    await loadMyTrips();
  } catch (err) {
    showToast(`Cancellation failed: ${err.message || (typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail))}`, false);
  }
}

window.loadMyTrips = loadMyTrips;
window.filterTrips = filterTrips;
window.trackRefundDirect = trackRefundDirect;
window.viewTripDetailsModal = viewTripDetailsModal;
window.cancelTripBookingPrompt = cancelTripBookingPrompt;

// =========================================================
// AUTH MODAL & FORM CONTROLLERS
// =========================================================
function openAuthModal(tab = 'login') {
  const modal = document.getElementById('authModal');
  if (modal) {
    modal.classList.add('open');
    switchAuthTab(tab);
    clearAuthAlert();
  }
}

function closeAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) modal.classList.remove('open');
  clearAuthAlert();
}

function switchAuthTab(tab) {
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const forgotForm = document.getElementById('forgotForm');
  const btnLogin = document.getElementById('authTabBtnLogin');
  const btnSignup = document.getElementById('authTabBtnSignup');
  const heading = document.getElementById('authModalHeading');
  const subheading = document.getElementById('authModalSubheading');
  const switcher = document.getElementById('authTabSwitcher');

  clearAuthAlert();

  if (tab === 'login') {
    if (loginForm) loginForm.style.display = 'block';
    if (signupForm) signupForm.style.display = 'none';
    if (forgotForm) forgotForm.style.display = 'none';
    if (switcher) switcher.style.display = 'flex';
    if (btnLogin) {
      btnLogin.style.background = 'var(--bg-surface)';
      btnLogin.style.color = 'var(--text-main)';
    }
    if (btnSignup) {
      btnSignup.style.background = 'transparent';
      btnSignup.style.color = 'var(--text-muted)';
    }
    if (heading) heading.textContent = 'Welcome to AirfareX';
    if (subheading) subheading.textContent = 'Sign in to manage your bookings, alerts and saved routes.';
  } else if (tab === 'signup') {
    if (loginForm) loginForm.style.display = 'none';
    if (signupForm) signupForm.style.display = 'block';
    if (forgotForm) forgotForm.style.display = 'none';
    if (switcher) switcher.style.display = 'flex';
    if (btnSignup) {
      btnSignup.style.background = 'var(--bg-surface)';
      btnSignup.style.color = 'var(--text-main)';
    }
    if (btnLogin) {
      btnLogin.style.background = 'transparent';
      btnLogin.style.color = 'var(--text-muted)';
    }
    if (heading) heading.textContent = 'Create Traveler Account';
    if (subheading) subheading.textContent = 'Join AirfareX to save favorite routes, track prices, and manage trips.';
  } else if (tab === 'forgot') {
    if (loginForm) loginForm.style.display = 'none';
    if (signupForm) signupForm.style.display = 'none';
    if (forgotForm) forgotForm.style.display = 'block';
    if (switcher) switcher.style.display = 'none';
    if (heading) heading.textContent = 'Reset Your Password';
    if (subheading) subheading.textContent = 'We will send a password reset link to your registered email.';
  }
}

function showAuthAlert(msg, isSuccess = false) {
  const box = document.getElementById('authAlertBox');
  if (box) {
    box.style.display = 'block';
    box.style.background = isSuccess ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)';
    box.style.border = isSuccess ? '1px solid #10b981' : '1px solid #ef4444';
    box.style.color = isSuccess ? '#059669' : '#dc2626';
    box.textContent = msg;
  }
}

function clearAuthAlert() {
  const box = document.getElementById('authAlertBox');
  if (box) box.style.display = 'none';
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail')?.value;
  const pass = document.getElementById('loginPassword')?.value;
  const btn = document.getElementById('loginSubmitBtn');

  if (!email || !pass) {
    showAuthAlert('Please fill in both email and password.');
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Signing in...';
  }

  try {
    await window.auth.signIn(email, pass);
    closeAuthModal();
    showToast(`Welcome back, ${window.auth.getUserDisplayName()}!`);
    if (state.currentTab === 'trips') loadMyTrips();
    if (state.currentTab === 'saved') loadAlerts();
  } catch (err) {
    showAuthAlert(err.message || 'Login failed. Please verify credentials.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Sign In';
    }
  }
}

async function handleSignupSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('signupFullName')?.value;
  const email = document.getElementById('signupEmail')?.value;
  const phone = document.getElementById('signupPhone')?.value;
  const pass = document.getElementById('signupPassword')?.value;
  const confirm = document.getElementById('signupConfirmPassword')?.value;
  const btn = document.getElementById('signupSubmitBtn');

  if (pass !== confirm) {
    showAuthAlert('Passwords do not match. Please re-enter.');
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Creating account...';
  }

  try {
    const res = await window.auth.signUp(name, email, pass, confirm, phone);
    if (res.session) {
      closeAuthModal();
      showToast(`Account created! Welcome, ${name}!`);
      if (state.currentTab === 'trips') loadMyTrips();
    } else {
      showAuthAlert(res.message || 'Account created! Please check your email to verify your address.', true);
    }
  } catch (err) {
    showAuthAlert(err.message || 'Registration failed.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Create Account';
    }
  }
}

async function handleForgotSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('forgotEmail')?.value;
  const btn = document.getElementById('forgotSubmitBtn');

  if (!email) {
    showAuthAlert('Please enter your registered email address.');
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Sending link...';
  }

  try {
    const res = await window.auth.resetPassword(email);
    showAuthAlert(res.message || 'Password reset link sent! Check your inbox.', true);
  } catch (err) {
    showAuthAlert(err.message || 'Could not send reset link.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Send Reset Link';
    }
  }
}

window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthTab = switchAuthTab;
window.handleLoginSubmit = handleLoginSubmit;
window.handleSignupSubmit = handleSignupSubmit;
window.handleForgotSubmit = handleForgotSubmit;

// Register auth state listener to refresh tabs upon login/logout
if (window.auth) {
  window.auth.onAuthStateChange((user) => {
    if (state.currentTab === 'trips') loadMyTrips();
    if (state.currentTab === 'saved') loadAlerts();
  });
}

// Master Airport Datalist Autocomplete Initializer
async function initAirportDatalists() {
  try {
    if (window.api && typeof window.api.listAirports === 'function') {
      const airports = await window.api.listAirports();
      if (airports && airports.length) {
        const originList = document.getElementById('originAirports');
        const destList = document.getElementById('destAirports');
        const optionsHtml = airports.map(a => `<option value="${a.city} (${a.iata_code})">${a.name}</option>`).join('');
        if (originList) originList.innerHTML = optionsHtml;
        if (destList) destList.innerHTML = optionsHtml;
      }
    }
  } catch (err) {
    console.debug('[Airports] Datalist fallback active');
  }
}

// URL Query State Synchronization & Navigation Restoration
function initUrlState() {
  if (typeof window === 'undefined' || !window.location) return;
  try {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab');
    const from = params.get('from');
    const to = params.get('to');
    const date = params.get('date');

    if (from) {
      const fFrom = document.getElementById('fFrom');
      const fromCity = document.getElementById('fromCity');
      if (fFrom) fFrom.value = from;
      if (fromCity) fromCity.value = `${from} (${from})`;
    }
    if (to) {
      const fTo = document.getElementById('fTo');
      const toCity = document.getElementById('toCity');
      if (fTo) fTo.value = to;
      if (toCity) toCity.value = `${to} (${to})`;
    }
    if (date) {
      const depDate = document.getElementById('departDate');
      if (depDate) depDate.value = date;
    }

    if (tab) {
      const tabLink = document.querySelector(`.main-nav a[data-tab="${tab}"]`);
      showTab(tab, tabLink, false);
    }
  } catch (e) {
    console.debug('URL state initialization skipped');
  }
}

// Popstate listener for browser Back/Forward navigation
if (typeof window !== 'undefined') {
  window.addEventListener('popstate', (e) => {
    if (e.state && e.state.tab) {
      showTab(e.state.tab, null, false);
    } else {
      initUrlState();
    }
  });
}

// Initialize on DOM Ready
function onAppReady() {
  initAirportDatalists();
  initUrlState();
  
  // Phase 9: Restore Homepage Featured Discovery (Safe DEL -> BOM demo)
  if (!state.currentTab || state.currentTab === 'home') {
    loadHomepageFeaturedFlights('DEL', 'BOM');
  }
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onAppReady);
  } else {
    onAppReady();
  }
}

// Global window bindings for Phase 8 & 9 UX
window.showTab = showTab;
window.triggerSearch = triggerSearch;
window.triggerHomeOrExplorerSearch = triggerHomeOrExplorerSearch;
window.loadHomepageFeaturedFlights = loadHomepageFeaturedFlights;
window.sendPromptToAi = sendPromptToAi;
window.quickAddToComparison = quickAddToComparison;
window.swapOriginDest = swapOriginDest;
window.resetFlightFilters = resetFlightFilters;
window.executeNlSearch = executeNlSearch;
window.setNlQuery = setNlQuery;
window.toggleAiAssistant = toggleAiAssistant;
window.toggleAiCopilotDrawer = toggleAiAssistant;




