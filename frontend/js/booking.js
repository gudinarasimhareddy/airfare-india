/**
 * AirfareX India — Booking & Checkout Controller
 * Manages Flight Review, Google Flights 30D Trends, DGCA Fee Decomposition,
 * Indian GST (5% CGST+SGST), Promo Validation, Dynamic UPI Gateway & E-Ticket
 */

let bookingState = {
  flight: null,
  taxBreakdown: null,
  addons: {
    digiyatra: false,
    insurance: false,
    baggage: false
  },
  addonPrices: {
    digiyatra: 99,
    insurance: 199,
    baggage: 1350
  },
  couponCode: 'AIRX500',
  discountAmount: 500,
  paymentMethod: 'upi',
  upiApp: 'Google Pay',
  upiId: 'rajesh@okhdfcbank',
  gender: 'Male',
  qrSecondsLeft: 599,
  qrTimerInterval: null,
  confirmedBooking: null
};

// =========================================================
// INITIALIZATION
// =========================================================
document.addEventListener('DOMContentLoaded', async () => {
  initBookingTheme();
  loadSelectedFlight();
  startQrTimer();
  await fetchTaxesAndFees();
  await fetchGoogleFlightsIntelligence();
});

function initBookingTheme() {
  const savedTheme = localStorage.getItem('airfarex_theme') || 'aurora';
  document.documentElement.setAttribute('data-theme', savedTheme);
  const btn = document.getElementById('themeToggleBtn');
  if (btn) btn.innerHTML = savedTheme === 'light' ? '☀️' : '🌙';
}

function toggleBookingTheme() {
  const cur = document.documentElement.getAttribute('data-theme') || 'aurora';
  const next = cur === 'light' ? 'aurora' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('airfarex_theme', next);
  const btn = document.getElementById('themeToggleBtn');
  if (btn) btn.innerHTML = next === 'light' ? '☀️' : '🌙';
}

function showToast(msg, isSuccess = true) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const t = document.createElement('div');
  t.className = 'toast-message';
  t.innerHTML = `<span>${isSuccess ? '✓' : 'ℹ'}</span><span>${msg}</span>`;
  container.appendChild(t);

  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateY(10px)';
    t.style.transition = 'all 0.3s ease';
    setTimeout(() => t.remove(), 300);
  }, 2800);
}

// =========================================================
// LOAD FLIGHT DATA
// =========================================================
function loadSelectedFlight() {
  let stored = null;
  try {
    const raw = sessionStorage.getItem('airfarex_booking_flight');
    if (raw) stored = JSON.parse(raw);
  } catch (e) {
    console.warn('Failed to parse flight from sessionStorage:', e);
  }

  // Fallback realistic flight if opened directly
  bookingState.flight = stored || {
    airline: 'IndiGo',
    flight_no: '6E-205',
    origin_code: 'HYD',
    origin_city: 'Hyderabad',
    destination_code: 'DEL',
    destination_city: 'Delhi (IGI)',
    total_fare: 5420,
    base_fare: 4120,
    dep_time: '07:15',
    arr_time: '09:30',
    duration: '2h 15m',
    stops: 'Nonstop',
    aircraft: 'Airbus A320neo',
    cabin: 'Economy',
    terminal: 'T2',
    gate: 'G12',
    seat_pitch: '30"',
    baggage: '15kg Check-in + 7kg Cabin',
    travel_date: new Date(Date.now() + 86400000 * 3).toISOString().slice(0, 10)
  };

  const f = bookingState.flight;

  // Render to DOM
  document.getElementById('bAirlineName') && (document.getElementById('bAirlineName').textContent = f.airline);
  document.getElementById('bFlightNo') && (document.getElementById('bFlightNo').textContent = f.flight_no);
  document.getElementById('bAircraft') && (document.getElementById('bAircraft').textContent = f.aircraft);
  document.getElementById('bCabinBadge') && (document.getElementById('bCabinBadge').textContent = `${f.cabin} Class`);
  document.getElementById('bTravelDate') && (document.getElementById('bTravelDate').textContent = `Travel: ${f.travel_date}`);

  document.getElementById('bDepTime') && (document.getElementById('bDepTime').textContent = f.dep_time);
  document.getElementById('bOriginCode') && (document.getElementById('bOriginCode').textContent = f.origin_code);
  document.getElementById('bOriginCity') && (document.getElementById('bOriginCity').textContent = f.origin_city);

  document.getElementById('bArrTime') && (document.getElementById('bArrTime').textContent = f.arr_time);
  document.getElementById('bDestCode') && (document.getElementById('bDestCode').textContent = f.destination_code);
  document.getElementById('bDestCity') && (document.getElementById('bDestCity').textContent = f.destination_city);

  document.getElementById('bDuration') && (document.getElementById('bDuration').textContent = f.duration);
  document.getElementById('bStops') && (document.getElementById('bStops').textContent = f.stops);

  document.getElementById('bTerminalTag') && (document.getElementById('bTerminalTag').textContent = `📍 Terminal: ${f.terminal}`);
  document.getElementById('bGateTag') && (document.getElementById('bGateTag').textContent = `🚪 Gate: ${f.gate}`);
  document.getElementById('bBaggageTag') && (document.getElementById('bBaggageTag').textContent = `🧳 ${f.baggage}`);
  document.getElementById('bSeatPitchTag') && (document.getElementById('bSeatPitchTag').textContent = `💺 ${f.seat_pitch} Legroom`);
}

// =========================================================
// GOOGLE FLIGHTS 30-DAY INTELLIGENCE
// =========================================================
async function fetchGoogleFlightsIntelligence() {
  const f = bookingState.flight;
  if (!f) return;

  try {
    const data = await window.api.getGoogleFlightsHistory30d(f.origin_code, f.destination_code);
    
    if (data && data.price_insights) {
      const ins = data.price_insights;
      const descEl = document.getElementById('googleInsightDesc');
      const pillEl = document.getElementById('googleInsightPill');
      const verdictEl = document.getElementById('googleInsightVerdict');

      if (descEl) {
        descEl.textContent = `Google Flights 30-Day Benchmark: Typical ${ins.typical_range}. Lowest 30-day observed: ₹${ins.lowest_price_recorded.toLocaleString('en-IN')}.`;
      }

      if (verdictEl) {
        verdictEl.textContent = ins.verdict;
      }

      if (pillEl) {
        pillEl.className = `google-insight-pill ${ins.level || 'low'}`;
      }
    }
  } catch (err) {
    console.warn('Google Flights intelligence call failed:', err);
  }
}

// =========================================================
// TAX & FEE BREAKDOWN CONTROLLER
// =========================================================
async function fetchTaxesAndFees() {
  const f = bookingState.flight;
  const baseEstimate = f.base_fare || Math.round(f.total_fare * 0.76);

  try {
    const taxData = await window.api.getTaxBreakdown(baseEstimate, f.cabin);
    bookingState.taxBreakdown = taxData;
  } catch (err) {
    console.warn('Fallback to local tax calculation:', err);
    // DGCA statutory formulas fallback
    const yq = 450;
    const udf = 380;
    const asf = 236; // DGCA statutory ₹236
    const taxable = baseEstimate + yq;
    const cgst = Math.round(taxable * 0.025);
    const sgst = Math.round(taxable * 0.025);
    const totalGst = cgst + sgst;
    
    bookingState.taxBreakdown = {
      base_fare: baseEstimate,
      fuel_surcharge_yq: yq,
      user_development_fee_udf: udf,
      aviation_security_fee_asf: asf,
      central_gst_cgst_2_5_pct: cgst,
      state_gst_sgst_2_5_pct: sgst,
      total_gst_5_pct: totalGst,
      card_convenience_fee: 350,
      upi_convenience_fee: 0
    };
  }

  recalculateTotalPayable();
}

function recalculateTotalPayable() {
  const tb = bookingState.taxBreakdown;
  if (!tb) return;

  // Addons sum
  let addonsSum = 0;
  if (bookingState.addons.digiyatra) addonsSum += bookingState.addonPrices.digiyatra;
  if (bookingState.addons.insurance) addonsSum += bookingState.addonPrices.insurance;
  if (bookingState.addons.baggage) addonsSum += bookingState.addonPrices.baggage;

  // Convenience Fee
  const convFee = bookingState.paymentMethod === 'card' ? 350 : 0;

  // Subtotal
  const subtotal = tb.base_fare + tb.fuel_surcharge_yq + tb.user_development_fee_udf + tb.aviation_security_fee_asf + tb.total_gst_5_pct + addonsSum + convFee;
  
  // Apply discount
  const finalTotal = Math.max(subtotal - bookingState.discountAmount, 500);

  // Render Table
  document.getElementById('feeBaseFare') && (document.getElementById('feeBaseFare').textContent = `₹${tb.base_fare.toLocaleString('en-IN')}`);
  document.getElementById('feeYq') && (document.getElementById('feeYq').textContent = `₹${tb.fuel_surcharge_yq.toLocaleString('en-IN')}`);
  document.getElementById('feeUdf') && (document.getElementById('feeUdf').textContent = `₹${tb.user_development_fee_udf.toLocaleString('en-IN')}`);
  document.getElementById('feeAsf') && (document.getElementById('feeAsf').textContent = `₹${tb.aviation_security_fee_asf.toLocaleString('en-IN')}`);
  document.getElementById('feeCgst') && (document.getElementById('feeCgst').textContent = `₹${tb.central_gst_cgst_2_5_pct.toLocaleString('en-IN')}`);
  document.getElementById('feeSgst') && (document.getElementById('feeSgst').textContent = `₹${tb.state_gst_sgst_2_5_pct.toLocaleString('en-IN')}`);
  document.getElementById('feeTotalGst') && (document.getElementById('feeTotalGst').textContent = `₹${tb.total_gst_5_pct.toLocaleString('en-IN')}`);

  // Addons row
  const addonsRow = document.getElementById('feeAddonsRow');
  const addonsVal = document.getElementById('feeAddonsVal');
  if (addonsRow && addonsVal) {
    if (addonsSum > 0) {
      addonsRow.style.display = 'table-row';
      addonsVal.textContent = `+₹${addonsSum.toLocaleString('en-IN')}`;
    } else {
      addonsRow.style.display = 'none';
    }
  }

  // Discount row
  const discRow = document.getElementById('feeDiscountRow');
  const discVal = document.getElementById('feeDiscountVal');
  if (discRow && discVal) {
    if (bookingState.discountAmount > 0) {
      discRow.style.display = 'table-row';
      discVal.textContent = `-₹${bookingState.discountAmount.toLocaleString('en-IN')}`;
    } else {
      discRow.style.display = 'none';
    }
  }

  // Convenience Fee Display
  const convCell = document.getElementById('feeConvenience');
  if (convCell) {
    if (bookingState.paymentMethod === 'card') {
      convCell.innerHTML = `<span style="color:var(--text-main); font-weight:800;">₹350</span>`;
    } else {
      convCell.innerHTML = `
        <span style="text-decoration:line-through; font-size:11.5px; color:var(--text-subtle);">₹350</span>
        <span style="color:var(--brand-mint); font-weight:800; margin-left:4px;">₹0 (Waived)</span>
      `;
    }
  }

  // Total
  const totalDisplay = `₹${finalTotal.toLocaleString('en-IN')}`;
  document.getElementById('feeTotalPayable') && (document.getElementById('feeTotalPayable').textContent = totalDisplay);
  document.getElementById('btnPayAmount') && (document.getElementById('btnPayAmount').textContent = totalDisplay);
  document.getElementById('upiRequestAmount') && (document.getElementById('upiRequestAmount').textContent = totalDisplay);

  bookingState.finalTotal = finalTotal;
}

// =========================================================
// ADD-ONS TOGGLER
// =========================================================
function toggleAddon(type, price) {
  const chk = document.getElementById(type === 'digiyatra' ? 'checkDigiYatra' : (type === 'insurance' ? 'checkInsurance' : 'checkBaggage'));
  const card = document.getElementById(type === 'digiyatra' ? 'addonDigiYatra' : (type === 'insurance' ? 'addonInsurance' : 'addonBaggage'));

  const nextState = !bookingState.addons[type];
  bookingState.addons[type] = nextState;

  if (chk) chk.checked = nextState;
  if (card) card.classList.toggle('selected', nextState);

  showToast(nextState ? `Added ${type.toUpperCase()} to your booking` : `Removed ${type.toUpperCase()}`);
  recalculateTotalPayable();
}

// =========================================================
// PROMO CODE COUPON SYSTEM
// =========================================================
function applyBookingCoupon() {
  const inp = document.getElementById('couponInput');
  const code = inp ? inp.value.trim().toUpperCase() : '';

  if (!code) {
    showToast('Please enter a coupon code', false);
    return;
  }

  const badge = document.getElementById('appliedPromoBadge');

  if (code === 'AIRX500') {
    bookingState.couponCode = code;
    bookingState.discountAmount = 500;
    if (badge) {
      badge.style.display = 'flex';
      badge.innerHTML = `<span>🏷️ <b>AIRX500</b> Applied (₹500 Instant Discount)</span><span style="cursor:pointer; font-weight:800;" onclick="removeBookingCoupon()">✕</span>`;
    }
    showToast('🎉 Code AIRX500 applied! Saved ₹500');
  } else if (code === 'UPIFIRST') {
    bookingState.couponCode = code;
    bookingState.discountAmount = 300;
    if (badge) {
      badge.style.display = 'flex';
      badge.innerHTML = `<span>🏷️ <b>UPIFIRST</b> Applied (₹300 Extra Savings)</span><span style="cursor:pointer; font-weight:800;" onclick="removeBookingCoupon()">✕</span>`;
    }
    showToast('🎉 Code UPIFIRST applied! Saved ₹300');
  } else if (code === 'FESTIVE1000') {
    bookingState.couponCode = code;
    bookingState.discountAmount = 1000;
    if (badge) {
      badge.style.display = 'flex';
      badge.innerHTML = `<span>🏷️ <b>FESTIVE1000</b> Applied (₹1,000 Mega Discount)</span><span style="cursor:pointer; font-weight:800;" onclick="removeBookingCoupon()">✕</span>`;
    }
    showToast('🎉 Code FESTIVE1000 applied! Saved ₹1,000');
  } else if (code === 'STUDENT') {
    bookingState.couponCode = code;
    bookingState.discountAmount = 600;
    if (badge) {
      badge.style.display = 'flex';
      badge.innerHTML = `<span>🏷️ <b>STUDENT</b> Applied (₹600 Concession + 10kg Extra Bag)</span><span style="cursor:pointer; font-weight:800;" onclick="removeBookingCoupon()">✕</span>`;
    }
    showToast('🎉 Student concession applied! Saved ₹600');
  } else {
    showToast(`Invalid coupon code: "${code}". Try AIRX500 or UPIFIRST`, false);
    return;
  }

  recalculateTotalPayable();
}

function removeBookingCoupon() {
  bookingState.couponCode = '';
  bookingState.discountAmount = 0;
  const badge = document.getElementById('appliedPromoBadge');
  if (badge) badge.style.display = 'none';
  showToast('Promo coupon removed');
  recalculateTotalPayable();
}

// =========================================================
// GST DETAILS ACCORDION
// =========================================================
function toggleGstFields() {
  const box = document.getElementById('gstFieldsBox');
  const chk = document.getElementById('gstCheckbox');
  const icon = document.getElementById('gstToggleIcon');

  if (!box) return;
  const isVisible = box.style.display === 'block';
  box.style.display = isVisible ? 'none' : 'block';
  if (chk) chk.checked = !isVisible;
  if (icon) icon.textContent = !isVisible ? '▲' : '▼';
}

function selectGender(el) {
  document.querySelectorAll('.radio-pill-btn').forEach(b => b.classList.remove('active'));
  if (el) {
    el.classList.add('active');
    bookingState.gender = el.getAttribute('data-gender') || 'Male';
  }
}

// =========================================================
// PAYMENT METHODS & UPI CONTROLLER
// =========================================================
function switchPaymentTab(tab) {
  bookingState.paymentMethod = tab;

  // Buttons
  document.getElementById('tabBtnUpi')?.classList.toggle('active', tab === 'upi');
  document.getElementById('tabBtnCard')?.classList.toggle('active', tab === 'card');
  document.getElementById('tabBtnNb')?.classList.toggle('active', tab === 'netbanking');

  // Contents
  document.getElementById('tabContentUpi') && (document.getElementById('tabContentUpi').style.display = tab === 'upi' ? 'block' : 'none');
  document.getElementById('tabContentCard') && (document.getElementById('tabContentCard').style.display = tab === 'card' ? 'block' : 'none');
  document.getElementById('tabContentNb') && (document.getElementById('tabContentNb').style.display = tab === 'netbanking' ? 'block' : 'none');

  if (tab === 'upi') {
    showToast('Switched to UPI (₹0 Convenience Fee Waived)');
  } else if (tab === 'card') {
    showToast('Standard card processing fee applies', false);
  }

  recalculateTotalPayable();
}

function selectUpiApp(appName) {
  bookingState.upiApp = appName;
  document.querySelectorAll('.upi-app-chip').forEach(c => {
    c.classList.toggle('active', c.textContent.includes(appName));
  });
  showToast(`Selected UPI Provider: ${appName}`);
}

function verifyVpa() {
  const inp = document.getElementById('upiIdInput');
  const vpa = inp ? inp.value.trim() : '';
  const badge = document.getElementById('vpaStatusBadge');

  if (!vpa || !vpa.includes('@')) {
    if (badge) {
      badge.style.display = 'block';
      badge.style.color = 'var(--brand-rose)';
      badge.textContent = '✕ Invalid UPI ID format. Example: user@oksbi';
    }
    showToast('Please enter a valid UPI ID (e.g. mobile@paytm)', false);
    return;
  }

  bookingState.upiId = vpa;
  if (badge) {
    badge.style.display = 'block';
    badge.style.color = 'var(--brand-mint)';
    badge.textContent = `✓ Verified: ${vpa.split('@')[0].toUpperCase()} · NPCI Active`;
  }
  showToast(`UPI ID ${vpa} successfully verified!`);
}

function startQrTimer() {
  bookingState.qrTimerInterval = setInterval(() => {
    bookingState.qrSecondsLeft--;
    if (bookingState.qrSecondsLeft <= 0) {
      bookingState.qrSecondsLeft = 600; // auto refresh
    }

    const m = Math.floor(bookingState.qrSecondsLeft / 60);
    const s = bookingState.qrSecondsLeft % 60;
    const countEl = document.getElementById('qrTimerCount');
    if (countEl) {
      countEl.textContent = `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
    }
  }, 1000);
}

// =========================================================
// CHECKOUT & PAYMENT GATEWAY CONTROLLER
// =========================================================
function submitBookingCheckout() {
  const firstName = document.getElementById('paxFirstName')?.value.trim();
  const lastName = document.getElementById('paxLastName')?.value.trim();
  const email = document.getElementById('paxEmail')?.value.trim();
  const phone = document.getElementById('paxPhone')?.value.trim();

  if (!firstName || !lastName || !email || !phone) {
    showToast('Please fill all mandatory passenger contact details', false);
    document.getElementById('paxFirstName')?.focus();
    return;
  }

  // Validate Card details if Card tab is chosen
  if (bookingState.paymentMethod === 'card') {
    const cardInputs = document.querySelectorAll('#tabContentCard input');
    const cardNum = cardInputs[0]?.value.trim();
    if (!cardNum || cardNum.length < 12) {
      showToast('Please enter a valid 16-digit card number', false);
      cardInputs[0]?.focus();
      return;
    }
  }

  // Open the interactive payment gateway authorization modal
  openPaymentGatewayModal();
}

function openPaymentGatewayModal() {
  const backdrop = document.getElementById('paymentModalBackdrop');
  const amountEl = document.getElementById('pgModalAmount');
  const titleEl = document.getElementById('pgModalTitle');
  const upiSection = document.getElementById('pgModalUpiSection');
  const cardSection = document.getElementById('pgModalCardSection');
  const processingState = document.getElementById('pgProcessingState');
  const actionButtons = document.getElementById('pgActionButtons');

  if (processingState) processingState.style.display = 'none';
  if (actionButtons) actionButtons.style.display = 'flex';

  const total = (bookingState.finalTotal || 4914).toLocaleString('en-IN');
  if (amountEl) amountEl.textContent = `₹${total}`;

  if (bookingState.paymentMethod === 'card') {
    if (titleEl) titleEl.textContent = '3D-Secure Bank Gateway';
    if (upiSection) upiSection.style.display = 'none';
    if (cardSection) cardSection.style.display = 'block';
  } else {
    if (titleEl) titleEl.textContent = `NPCI UPI · ${bookingState.upiApp}`;
    if (upiSection) upiSection.style.display = 'block';
    if (cardSection) cardSection.style.display = 'none';
    const appDisplay = document.getElementById('pgUpiAppDisplay');
    const vpaDisplay = document.getElementById('pgUpiVpaDisplay');
    if (appDisplay) appDisplay.textContent = bookingState.upiApp;
    if (vpaDisplay) vpaDisplay.textContent = bookingState.upiId || 'user@okhdfcbank';
  }

  if (backdrop) backdrop.classList.add('open');
  showToast('Connecting to secure payment switch...', true);
}

function cancelPaymentAuthorization() {
  const backdrop = document.getElementById('paymentModalBackdrop');
  if (backdrop) backdrop.classList.remove('open');
  authorizePaymentFailure('Transaction cancelled by user in payment gateway dialog');
}

async function authorizePaymentSuccess() {
  const processingState = document.getElementById('pgProcessingState');
  const actionButtons = document.getElementById('pgActionButtons');
  const processText = document.getElementById('pgProcessText');

  if (actionButtons) actionButtons.style.display = 'none';
  if (processingState) processingState.style.display = 'block';
  if (processText) processText.textContent = 'Authenticating PIN with issuing bank...';

  // Step 2 simulated latency
  setTimeout(() => {
    if (processText) processText.textContent = 'NPCI Debit Confirmed. Generating DGCA Ticket...';
  }, 600);

  const payload = buildCheckoutPayload({
    payment_status: 'COMPLETED',
    payment_verified: true
  });

  try {
    const res = await window.api.checkoutFlight(payload);
    setTimeout(() => {
      const backdrop = document.getElementById('paymentModalBackdrop');
      if (backdrop) backdrop.classList.remove('open');

      if (res && res.status === 'CONFIRMED' && res.seat_allocated) {
        bookingState.confirmedBooking = res;
        renderConfirmedTicket(res);
        showToast(`🎉 Payment Confirmed! Seat ${res.seat_number} allocated.`);
      } else {
        renderPaymentFailed(res || { failure_reason: 'Payment status could not be verified by bank switch.' });
      }
    }, 1200);

  } catch (err) {
    console.error('Checkout error:', err);
    setTimeout(() => {
      const backdrop = document.getElementById('paymentModalBackdrop');
      if (backdrop) backdrop.classList.remove('open');
      renderPaymentFailed({
        failure_reason: 'Network timeout during bank settlement. Transaction aborted.'
      });
    }, 1000);
  }
}

async function authorizePaymentFailure(reason) {
  const processingState = document.getElementById('pgProcessingState');
  const actionButtons = document.getElementById('pgActionButtons');
  const processText = document.getElementById('pgProcessText');

  if (actionButtons) actionButtons.style.display = 'none';
  if (processingState) processingState.style.display = 'block';
  if (processText) processText.textContent = 'Simulating payment decline from banking network...';

  const failReason = reason || 'Bank authorization declined (NPCI Error U16: Authentication failed / insufficient funds)';

  const payload = buildCheckoutPayload({
    payment_status: 'FAILED',
    payment_verified: false,
    failure_reason: failReason
  });

  try {
    const res = await window.api.checkoutFlight(payload);
    setTimeout(() => {
      const backdrop = document.getElementById('paymentModalBackdrop');
      if (backdrop) backdrop.classList.remove('open');
      renderPaymentFailed(res);
    }, 800);
  } catch (err) {
    setTimeout(() => {
      const backdrop = document.getElementById('paymentModalBackdrop');
      if (backdrop) backdrop.classList.remove('open');
      renderPaymentFailed({ failure_reason: failReason });
    }, 800);
  }
}

function buildCheckoutPayload(extraFields = {}) {
  const firstName = document.getElementById('paxFirstName')?.value.trim() || 'Rajesh';
  const lastName = document.getElementById('paxLastName')?.value.trim() || 'Sharma';
  const title = document.getElementById('paxTitle')?.value || 'Mr';
  const email = document.getElementById('paxEmail')?.value.trim() || 'rajesh.sharma@example.com';
  const phone = document.getElementById('paxPhone')?.value.trim() || '9876543210';
  const meal = document.getElementById('paxMeal')?.value || 'Indian Vegetarian Thali';
  const gstin = document.getElementById('gstNumber')?.value.trim() || null;
  const company = document.getElementById('gstCompanyName')?.value.trim() || null;

  const f = bookingState.flight;
  const tb = bookingState.taxBreakdown;

  return {
    flight_no: f.flight_no,
    airline: f.airline,
    origin_code: f.origin_code,
    destination_code: f.destination_code,
    passenger_name: `${title}. ${firstName} ${lastName}`,
    email: email,
    phone: phone,
    gender: bookingState.gender,
    age: parseInt(document.getElementById('paxAge')?.value) || 29,
    meal_preference: meal,
    gstin: gstin,
    company_name: company,
    base_price: tb?.base_fare || 4120,
    payment_method: bookingState.paymentMethod,
    upi_vpa: bookingState.paymentMethod === 'upi' ? bookingState.upiId : null,
    promo_code: bookingState.couponCode || null,
    ...extraFields
  };
}

// =========================================================
// RENDER CONFIRMED E-TICKET & ALLOCATED SEATS
// =========================================================
function renderConfirmedTicket(data) {
  // Update Stepper to Completed
  document.getElementById('step1Indicator')?.classList.add('completed');
  document.getElementById('stepDiv1')?.classList.add('active');
  document.getElementById('step2Indicator')?.classList.add('completed');
  document.getElementById('stepDiv2')?.classList.add('active');
  document.getElementById('step3Indicator')?.classList.add('active');

  // STRICT VIEW TOGGLING: Hide form and failure view, Show ONLY confirmation view
  const formSection = document.getElementById('checkoutFormSection');
  const failureView = document.getElementById('paymentFailedView');
  const successView = document.getElementById('ticketSuccessView');

  if (formSection) formSection.style.display = 'none';
  if (failureView) failureView.style.display = 'none';
  if (successView) successView.style.display = 'block';

  // Highlight Booked Seat
  const seatBanner = document.getElementById('confSeatBanner');
  if (seatBanner) {
    const isWindow = data.seat_number.endsWith('A') || data.seat_number.endsWith('F');
    seatBanner.textContent = `Seat ${data.seat_number} (${isWindow ? 'Window' : 'Aisle'} · Forward Cabin)`;
  }

  // Payment Method
  const pmEl = document.getElementById('confPaymentMethod');
  if (pmEl) pmEl.textContent = data.payment_method === 'UPI' ? `UPI (${bookingState.upiApp || 'NPCI'})` : data.payment_method;

  // Fill in Ticket details
  document.getElementById('confSentEmail') && (document.getElementById('confSentEmail').textContent = data.email);
  document.getElementById('confSentPhone') && (document.getElementById('confSentPhone').textContent = `+91 ${data.phone}`);
  document.getElementById('confAirlineHeader') && (document.getElementById('confAirlineHeader').textContent = data.airline);
  document.getElementById('confEticketNo') && (document.getElementById('confEticketNo').textContent = data.eticket_number);
  document.getElementById('confPnr') && (document.getElementById('confPnr').textContent = data.pnr);
  document.getElementById('confUtr') && (document.getElementById('confUtr').textContent = data.utr_reference);

  document.getElementById('confPaxName') && (document.getElementById('confPaxName').textContent = data.passenger_name.toUpperCase());
  document.getElementById('confFlightDetails') && (document.getElementById('confFlightDetails').textContent = `${data.flight_no} (${bookingState.flight?.aircraft || 'A320neo'})`);
  document.getElementById('confSeatNo') && (document.getElementById('confSeatNo').textContent = `${data.seat_number} (${data.seat_number.endsWith('A') || data.seat_number.endsWith('F') ? 'Window' : 'Aisle'})`);
  document.getElementById('confGateTerminal') && (document.getElementById('confGateTerminal').textContent = `Gate ${data.gate} · ${data.terminal}`);

  document.getElementById('confOrigin') && (document.getElementById('confOrigin').textContent = `${data.origin_code} (${bookingState.flight?.origin_city || 'Origin'})`);
  document.getElementById('confDest') && (document.getElementById('confDest').textContent = `${data.destination_code} (${bookingState.flight?.destination_city || 'Destination'})`);
  document.getElementById('confDepTime') && (document.getElementById('confDepTime').textContent = `${bookingState.flight?.dep_time || '07:15 AM'} · ${data.travel_date}`);
  document.getElementById('confBaggage') && (document.getElementById('confBaggage').textContent = bookingState.flight?.baggage || '15kg Check-in + 7kg Cabin');

  // Barcode
  const cleanName = data.passenger_name.replace(/[^a-zA-Z]/g, '').slice(0, 10).toUpperCase();
  document.getElementById('confBarcodeText') && (document.getElementById('confBarcodeText').textContent = `M1${cleanName} ${data.flight_no.replace('-', '')} ${data.origin_code}${data.destination_code} ETKT${data.eticket_number.replace(/-/g, '')}`);

  // Tax Invoice Section
  const inv = data.tax_invoice;
  if (inv) {
    document.getElementById('confInvoiceNo') && (document.getElementById('confInvoiceNo').textContent = inv.invoice_number);
    document.getElementById('confAirlineGstin') && (document.getElementById('confAirlineGstin').textContent = inv.airline_gstin);
    document.getElementById('confRecipient') && (document.getElementById('confRecipient').textContent = `${data.passenger_name} ${data.gstin ? `(GSTIN: ${data.gstin})` : ''}`);
    document.getElementById('confTaxableVal') && (document.getElementById('confTaxableVal').textContent = `₹${inv.taxable_value.toLocaleString('en-IN')}`);
    document.getElementById('confGstVal') && (document.getElementById('confGstVal').textContent = `₹${inv.gst_amount.toLocaleString('en-IN')} (5% SAC 9964)`);
    document.getElementById('confTotalPaid') && (document.getElementById('confTotalPaid').textContent = `₹${inv.total_amount.toLocaleString('en-IN')}`);
  }

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =========================================================
// RENDER PAYMENT FAILED VIEW (NO SEATS ALLOCATED)
// =========================================================
function renderPaymentFailed(errData) {
  // Reset Stepper (Payment Step Failed)
  document.getElementById('step3Indicator')?.classList.remove('active');
  document.getElementById('stepDiv2')?.classList.remove('active');

  // STRICT VIEW TOGGLING: Hide form, Hide confirmed view, Show Failure view
  const formSection = document.getElementById('checkoutFormSection');
  const successView = document.getElementById('ticketSuccessView');
  const failureView = document.getElementById('paymentFailedView');

  if (formSection) formSection.style.display = 'none';
  if (successView) successView.style.display = 'none';
  if (failureView) failureView.style.display = 'block';

  // Fill in failure information
  const txnIdEl = document.getElementById('failTxnId');
  const amountEl = document.getElementById('failAmount');
  const methodEl = document.getElementById('failMethod');
  const reasonEl = document.getElementById('failReason');

  if (txnIdEl) txnIdEl.textContent = errData.transaction_id || `TXN-FAIL-${Math.floor(100000 + Math.random() * 900000)}`;
  if (amountEl) amountEl.textContent = `₹${(bookingState.finalTotal || 4914).toLocaleString('en-IN')}`;
  if (methodEl) methodEl.textContent = bookingState.paymentMethod === 'card' ? 'Credit / Debit Card' : `UPI (${bookingState.upiApp})`;
  if (reasonEl) reasonEl.textContent = errData.failure_reason || errData.error_message || 'Payment authorization declined by issuing bank (Error: U16)';

  window.scrollTo({ top: 0, behavior: 'smooth' });
  showToast('❌ Payment authorization declined. Seats not allocated.', false);
}

function retryBookingPayment() {
  const formSection = document.getElementById('checkoutFormSection');
  const failureView = document.getElementById('paymentFailedView');
  const successView = document.getElementById('ticketSuccessView');

  if (failureView) failureView.style.display = 'none';
  if (successView) successView.style.display = 'none';
  if (formSection) formSection.style.display = 'grid';

  const payCard = document.getElementById('paymentSectionCard');
  if (payCard) {
    payCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  showToast('Ready to retry payment. Enter PIN or authorize on your device.');
}

function changePaymentMethod() {
  retryBookingPayment();
  const tabs = document.querySelector('.payment-tabs-header');
  if (tabs) {
    tabs.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// Download Invoice JSON/Summary
function downloadInvoiceSummary() {
  const data = bookingState.confirmedBooking;
  if (!data) return;

  const content = JSON.stringify(data, null, 2);
  const blob = new Blob([content], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `AirfareX_Tax_Invoice_${data.pnr}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('Tax Invoice JSON downloaded successfully!');
}

// Expose globals for HTML inline events
window.toggleBookingTheme = toggleBookingTheme;
window.toggleAddon = toggleAddon;
window.applyBookingCoupon = applyBookingCoupon;
window.removeBookingCoupon = removeBookingCoupon;
window.toggleGstFields = toggleGstFields;
window.selectGender = selectGender;
window.switchPaymentTab = switchPaymentTab;
window.selectUpiApp = selectUpiApp;
window.verifyVpa = verifyVpa;
window.submitBookingCheckout = submitBookingCheckout;
window.openPaymentGatewayModal = openPaymentGatewayModal;
window.cancelPaymentAuthorization = cancelPaymentAuthorization;
window.authorizePaymentSuccess = authorizePaymentSuccess;
window.authorizePaymentFailure = authorizePaymentFailure;
window.renderConfirmedTicket = renderConfirmedTicket;
window.renderPaymentFailed = renderPaymentFailed;
window.retryBookingPayment = retryBookingPayment;
window.changePaymentMethod = changePaymentMethod;
window.downloadInvoiceSummary = downloadInvoiceSummary;

