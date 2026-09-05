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
  theme: localStorage.getItem('airfarex_theme') || 'aurora',
  flights: [],
  routes: [],
  alerts: [],
  touristPlans: [],
  selectedPackage: null,
  overview: null,
  cpiSimulation: null,
  predictionData: null,
  currentRefund: null
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

// Navigation between views
function showTab(tabId, el) {
  const sections = ['home', 'explorer', 'comparison', 'monthly-fares', 'offers', 'tourist-plans', 'prediction', 'refunds', 'routes', 'index', 'quality', 'saved'];
  sections.forEach(id => {
    const sec = document.getElementById(id);
    if (sec) sec.classList.toggle('hidden', id !== tabId);
  });

  document.querySelectorAll('.main-nav .nav-link').forEach(link => {
    link.classList.remove('active');
  });
  if (el) el.classList.add('active');

  state.currentTab = tabId;

  // Trigger contextual data loads
  if (tabId === 'explorer') loadFlights();
  if (tabId === 'comparison') loadSectorComparison();
  if (tabId === 'monthly-fares') loadMonthlyCalendar();
  if (tabId === 'offers') loadOffers();
  if (tabId === 'tourist-plans') loadTouristPlans();
  if (tabId === 'prediction') runPricePrediction();
  if (tabId === 'refunds') trackRefundStatus('AIRX789');
  if (tabId === 'routes') loadRoutes();
  if (tabId === 'index') loadIndexData();
  if (tabId === 'quality') loadQualityData();
  if (tabId === 'saved') loadAlerts();

  window.scrollTo({ top: 0, behavior: 'smooth' });
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
}

// Load National Overview Metrics
async function loadOverview() {
  try {
    const data = await window.api.getApixOverview();
    state.overview = data;

    const elApix = document.getElementById('kpiApix');
    if (elApix) elApix.textContent = data.national_apix.toFixed(1);

    const elAvgFare = document.getElementById('kpiAvgFare');
    if (elAvgFare) elAvgFare.textContent = `₹${data.average_domestic_fare.toLocaleString('en-IN')}`;

    const elQuotes = document.getElementById('kpiQuotes');
    if (elQuotes) elQuotes.textContent = data.quotes_processed;

    const elConfidence = document.getElementById('kpiConfidence');
    if (elConfidence) elConfidence.textContent = `${data.data_confidence_pct}%`;
  } catch (err) {
    console.error('Failed to load overview:', err);
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

// Flight Search
async function triggerSearch() {
  const fromCity = document.getElementById('fromCity').value;
  const toCity = document.getElementById('toCity').value;

  const statusBox = document.getElementById('searchResultBox');
  if (statusBox) {
    statusBox.classList.remove('hidden');
    statusBox.innerHTML = `Searching real flights for <b>${fromCity} → ${toCity}</b>...`;
  }

  const explorerNav = document.querySelector('.main-nav a[data-tab="explorer"]');
  showTab('explorer', explorerNav);

  const expFrom = document.getElementById('fFrom');
  const expTo = document.getElementById('fTo');
  if (expFrom) expFrom.value = fromCity;
  if (expTo) expTo.value = toCity;

  await loadFlights();
}

// Load Flights with Filters & Sorting
async function loadFlights() {
  const resultsContainer = document.getElementById('flightResults');
  if (resultsContainer) {
    resultsContainer.innerHTML = '<div class="empty-box">Searching domestic airline schedules & live quotes...</div>';
  }

  const fromCity = document.getElementById('fFrom')?.value || document.getElementById('fromCity')?.value || 'HYD';
  const toCity = document.getElementById('fTo')?.value || document.getElementById('toCity')?.value || 'DEL';
  const stops = document.getElementById('fStops')?.value || 'Any';
  const airline = document.getElementById('fAir')?.value || 'All airlines';
  const maxPriceVal = document.getElementById('fPrice')?.value || 'Any';
  const baggage = document.getElementById('fBag')?.value || 'Any';
  const timeOfDay = document.getElementById('fTime')?.value || 'Any time';
  const directOnly = document.getElementById('directToggle')?.checked || false;

  const params = {
    from_city: fromCity,
    to_city: toCity,
    stops: stops,
    airline: airline,
    baggage: baggage,
    time_of_day: timeOfDay,
    direct_only: directOnly,
    sort_by: state.sortMode
  };

  if (maxPriceVal !== 'Any') {
    params.max_price = parseInt(maxPriceVal.replace(/[^0-9]/g, ''));
  }

  try {
    const data = await window.api.searchFlights(params);
    state.flights = data.flights;
    renderFlightCards(data.flights, data.best_fare);
  } catch (err) {
    if (resultsContainer) {
      resultsContainer.innerHTML = `<div class="empty-box">Error loading flights. Please verify API server status.</div>`;
    }
  }
}

// Render Flight Result Cards
function renderFlightCards(flights, bestFare) {
  const container = document.getElementById('flightResults');
  if (!container) return;

  if (!flights || !flights.length) {
    container.innerHTML = `
      <div class="card empty-box" style="margin-top:14px;">
        <h3>No flights match your filter criteria</h3>
        <p style="margin-top:6px; font-size:13px;">Try widening your price range, choosing "Any" stops, or selecting "All airlines".</p>
      </div>
    `;
    return;
  }

  const withBag = document.getElementById('bagsToggle')?.checked || false;

  container.innerHTML = flights.map(f => {
    const finalFare = withBag ? (f.total_fare + f.bag_fee) : f.total_fare;
    const isBest = bestFare && f.total_fare === bestFare;
    const airlineClass = `airline-${f.airline.toLowerCase().replace(/\s+/g, '-')}`;

    const bagSubText = withBag 
      ? window.i18n?.t('card_incl_bag', 'incl. 15kg checked bag') 
      : window.i18n?.t('card_base_taxes', 'base fare + taxes');
    const selectBtnText = 'Select Fare ✈';
    const trackBtnText = window.i18n?.t('card_track', '🔔 Track');
    const liveStatusText = window.i18n?.t('card_live_status', 'Live Status →');
    const termText = window.i18n?.t('card_terminal', 'Terminal');
    const gateText = window.i18n?.t('card_gate', 'Gate');
    const scoreText = window.i18n?.t('card_score', 'Score');
    const bagTagText = f.bag_fee === 0 
      ? window.i18n?.t('card_bag_incl', '✓ 1 checked bag included') 
      : (window.i18n?.t('card_bag_extra', 'Checked bag: +₹') + f.bag_fee);
    const taxesTagText = window.i18n?.t('card_taxes_incl', 'Taxes included');

    return `
      <div class="flight-card ${airlineClass}">
        <div class="flight-row-main">
          <div class="flight-airline">
            <div class="airline-name">
              ${f.airline}
              <span class="flight-no-tag">${f.flight_no}</span>
            </div>
            <div>
              <span class="badge ${isBest ? 'green' : 'blue'}">${f.tag || 'Standard Fare'}</span>
            </div>
          </div>

          <div class="flight-schedule">
            <div class="flight-time-box">
              <span class="flight-time">${f.dep_time}</span>
              <span class="flight-city">${f.origin_code}</span>
            </div>
            <div class="flight-duration-track">
              <span class="flight-duration">${f.duration}</span>
              <div class="flight-track-line"></div>
              <span class="flight-stop-label ${f.stops !== 'Nonstop' ? 'has-stops' : ''}">${f.stops}</span>
            </div>
            <div class="flight-time-box" style="text-align: right;">
              <span class="flight-time">${f.arr_time}</span>
              <span class="flight-city">${f.destination_code}</span>
            </div>
          </div>

          <div class="flight-intelligence-box">
            <div class="score-badge-wrap">
              <span class="small" style="font-size:11px; color:var(--text-muted); font-weight:700;">${scoreText}</span>
              <span class="score-value">${f.fare_score}/100</span>
            </div>
            <div class="co2-pill">
              <span>🌱 ${f.emissions_kg} kg CO₂e</span>
            </div>
          </div>

          <div class="flight-pricing-box">
            <div class="flight-price">₹${finalFare.toLocaleString('en-IN')}</div>
            <div class="price-type-sub">${bagSubText}</div>
          </div>

          <div class="flight-actions">
            <button class="btn sm" onclick="selectFlight('${f.airline}', '${f.flight_no}', ${finalFare}, '${f.destination_code}', '${f.destination}')">${selectBtnText}</button>
            <button class="btn sm light" onclick="quickAlert('${f.origin_code} → ${f.destination_code}', ${finalFare})">${trackBtnText}</button>
          </div>
        </div>

        <div class="flight-tags-row">
          <span class="flight-pill-tag">${termText} ${f.terminal || 'T2'}</span>
          <span class="flight-pill-tag">${gateText} ${f.gate || 'G1'}</span>
          <span class="flight-pill-tag">${bagTagText}</span>
          <span class="flight-pill-tag">${taxesTagText}</span>
          <span class="flight-pill-tag accent clickable" onclick="checkStatusForFlight('${f.flight_no}')">${liveStatusText}</span>
        </div>
      </div>
    `;
  }).join('');
}

// Sorting handler
function setSort(mode) {
  state.sortMode = mode;
  document.querySelectorAll('.result-toolbar .btn').forEach(b => b.classList.remove('dark'));
  const activeBtn = document.getElementById(`sortBtn_${mode}`);
  if (activeBtn) activeBtn.classList.add('dark');
  loadFlights();
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
  try {
    const alerts = await window.api.getAlerts();
    state.alerts = alerts;
    const container = document.getElementById('alertsListContainer');
    if (!container) return;

    if (!alerts.length) {
      container.innerHTML = '<div class="empty-box">No price alerts active. Search flights and click "Track" or create one above!</div>';
      return;
    }

    container.innerHTML = alerts.map(a => `
      <div class="route-row">
        <div>
          <b>${a.route}</b>
          <div class="metric-sub">Current: ${a.current_fare} · Trigger: ${a.target_condition}</div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge green">Tracking</span>
          <button class="btn sm gray" onclick="deleteAlert(${a.id})">✕</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Failed to load alerts:', err);
  }
}

async function quickAlert(route, fare) {
  try {
    await window.api.createAlert(route, `₹${fare.toLocaleString('en-IN')}`, 'Notify on 8% fare drop');
    showToast(`Price alert activated for ${route}!`);
    await loadAlerts();
  } catch (err) {
    showToast('Failed to save alert', false);
  }
}

async function handleCreateAlertForm() {
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

  // Look up flight object in current state if available
  const existing = state.flights?.find(f => f.flight_no === flightNo);

  const bookingData = {
    airline: airline || existing?.airline || 'IndiGo',
    flight_no: flightNo || existing?.flight_no || '6E-205',
    origin_code: existing?.origin_code || fromCode || 'HYD',
    origin_city: existing?.origin_city || (fromVal.includes('(') ? fromVal.split('(')[0].trim() : fromVal) || 'Hyderabad',
    destination_code: existing?.destination_code || targetDestCode || 'DEL',
    destination_city: existing?.destination_city || (toVal.includes('(') ? toVal.split('(')[0].trim() : toVal) || 'Delhi',
    total_fare: price || existing?.total_fare || 5420,
    base_fare: existing?.base_fare || Math.round((price || 5420) * 0.76),
    dep_time: existing?.dep_time || '07:15',
    arr_time: existing?.arr_time || '09:30',
    duration: existing?.duration || '2h 15m',
    stops: existing?.stops || 'Nonstop',
    aircraft: existing?.aircraft || 'Airbus A320neo',
    cabin: existing?.cabin || 'Economy',
    terminal: existing?.terminal || 'T2',
    gate: existing?.gate || 'G12',
    seat_pitch: existing?.seat_pitch || '30"',
    baggage: existing?.baggage || '15kg Check-in + 7kg Cabin',
    emissions_kg: existing?.emissions_kg || 135,
    fare_score: existing?.fare_score || 94,
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
    const res = await window.api.chatWithAssistant(text, lang, { currentTab: state.currentTab });
    
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

    // 2. Format markdown response content
    let formattedReply = res.reply
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

        <!-- Book Complete Package Button -->
        <div style="padding: 0 18px 18px;">
          <button class="tourist-book-btn" onclick="openPackageBookingModal('${p.id}')">
            Book Vacation Package ➔
          </button>
        </div>
      </div>
    `;
  }).join('');
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
  const amountEl = document.getElementById('pkgPayableAmount');
  const dateInput = document.getElementById('pkgTravelDate');

  if (detailsBox) {
    detailsBox.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
        <div>
          <h3 style="margin:0 0 4px; font-size:16px; color:var(--brand-cyan);">${plan.title}</h3>
          <span class="metric-sub">${plan.destination} · ${plan.duration}</span>
        </div>
        <span class="badge green">Offer Applied</span>
      </div>
      <div style="font-size:12px; color:var(--text-main); margin-bottom:6px;">
        ✈️ <b>Flight:</b> ${plan.flight.carrier} (${plan.flight.sector})
      </div>
      <div style="font-size:12px; color:var(--text-main); margin-bottom:10px;">
        🏨 <b>Hotel:</b> ${plan.hotel.name} (${plan.hotel.room_type})
      </div>
      <div style="display:flex; justify-content:space-between; font-size:12px; border-top:1px solid rgba(255,255,255,0.08); padding-top:8px;">
        <span style="color:var(--text-muted);">Standard Rack Rate:</span>
        <span style="text-decoration:line-through; color:var(--text-muted);">₹${plan.pricing.price_without_offers.toLocaleString('en-IN')}</span>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--brand-mint); margin-top:4px;">
        <span>Promo Discount (${plan.pricing.applied_promo}):</span>
        <b>-₹${plan.pricing.savings.toLocaleString('en-IN')}</b>
      </div>
    `;
  }

  if (amountEl) {
    amountEl.textContent = `₹${plan.pricing.price_with_offers.toLocaleString('en-IN')}`;
  }

  if (dateInput && !dateInput.value) {
    dateInput.value = new Date(Date.now() + 86400000 * 14).toISOString().slice(0, 10);
  }

  openModal('bookPackageModal');
}

async function confirmPackageBooking() {
  if (!state.selectedPackage) return;

  const name = document.getElementById('pkgTravelerName')?.value || 'Guest Traveler';
  const contact = document.getElementById('pkgTravelerContact')?.value || 'guest@example.com';
  const travelDate = document.getElementById('pkgTravelDate')?.value || new Date().toISOString().slice(0, 10);

  const payload = {
    plan_id: state.selectedPackage.id,
    traveler_name: name,
    contact: contact,
    travel_date: travelDate,
    pax_count: 1
  };

  try {
    const res = await window.api.bookTouristPlan(payload);
    closeModal('bookPackageModal');
    showToast(`🎉 Vacation Package Booked! Confirmation Reference: ${res.booking_reference}`);
    
    alert(`🎉 Booking Confirmed!\n\nPackage: ${res.plan_title}\nTraveler: ${res.traveler_name}\nTravel Date: ${res.travel_date}\nFlight: ${res.flight_details}\nHotel: ${res.hotel_details}\nTotal Paid: ₹${res.amount_paid.toLocaleString('en-IN')}\nReference: ${res.booking_reference}\n\nYour e-tickets and hotel confirmation voucher have been sent to ${contact}.`);
  } catch (err) {
    console.error('Failed to book package:', err);
    showToast('Failed to complete booking. Please retry.', false);
  }
}

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
// SUPABASE CLOUD DATABASE CONTROLLER
// =========================================================
function openSupabaseModal() {
  openModal('supabaseModal');
  checkSupabaseConnectionLive();
}

async function checkSupabaseConnectionLive() {
  const badge = document.getElementById('supaStatusBadge');
  const msg = document.getElementById('supaStatusMsg');

  if (badge) {
    badge.className = 'badge amber';
    badge.textContent = 'Checking...';
  }
  if (msg) {
    msg.textContent = 'Pinging Supabase PostgREST API (https://thtwkhhccxmkkgwtoleb.supabase.co)...';
  }

  try {
    const res = await window.api.getSupabaseStatus();
    if (badge) {
      if (res.connected) {
        badge.className = 'badge green';
        badge.textContent = 'Connected (Authenticated)';
      } else if (res.status_code === 401) {
        badge.className = 'badge amber';
        badge.textContent = 'Online (Awaiting API Key)';
      } else {
        badge.className = 'badge red';
        badge.textContent = 'Disconnected';
      }
    }
    if (msg) {
      msg.innerHTML = `<b>${res.message}</b><br><span style="font-size:11px; color:var(--text-muted);">Endpoint: ${res.project_url} · Project ID: ${res.project_id}</span>`;
    }
  } catch (err) {
    if (badge) {
      badge.className = 'badge red';
      badge.textContent = 'Offline';
    }
    if (msg) {
      msg.textContent = `Error connecting to Supabase: ${err.message}`;
    }
  }
}

async function saveSupabaseKey() {
  const keyInput = document.getElementById('supaKeyInput');
  const key = keyInput ? keyInput.value.trim() : '';

  if (!key) {
    showToast('Please enter your Supabase Anon or Service Role key', false);
    return;
  }

  try {
    const res = await window.api.updateSupabaseConfig(key);
    showToast(res.message);
    checkSupabaseConnectionLive();
  } catch (err) {
    showToast(`Failed to update key: ${err.message}`, false);
  }
}

window.openSupabaseModal = openSupabaseModal;
window.checkSupabaseConnectionLive = checkSupabaseConnectionLive;
window.saveSupabaseKey = saveSupabaseKey;

