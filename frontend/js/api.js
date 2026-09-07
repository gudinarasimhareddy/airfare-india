/**
 * AirfareX India — Unified API Client
 * Seamlessly interfaces with FastAPI backend (/api/v1) with robust error handling
 */

class AirfarexAPI {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl || (window.AIRFAREX_CONFIG && window.AIRFAREX_CONFIG.API_BASE_URL) || '';
  }

  async _fetch(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    // Automatically attach Bearer token if user is authenticated
    if (!headers['Authorization'] && window.auth && typeof window.auth.getToken === 'function') {
      const token = window.auth.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    try {
      const response = await fetch(url, {
        headers,
        ...options
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const msg = errorData?.detail || errorData?.message || `HTTP ${response.status}: ${response.statusText}`;
        const err = new Error(msg);
        err.status = response.status;
        err.data = errorData;
        throw err;
      }
      return await response.json();
    } catch (err) {
      console.warn(`[API] Request to ${endpoint} failed:`, err.message || err);
      throw err;
    }
  }

  // Flight Explorer
  async searchFlights(params = {}) {
    const query = new URLSearchParams();
    if (params.from_city) query.set('from_city', params.from_city);
    if (params.to_city) query.set('to_city', params.to_city);
    if (params.date) query.set('date', params.date);
    if (params.return_date) query.set('return_date', params.return_date);
    if (params.cabin) query.set('cabin', params.cabin);
    if (params.stops && params.stops !== 'Any') query.set('stops', params.stops);
    if (params.airline && params.airline !== 'All airlines') query.set('airline', params.airline);
    if (params.max_price) query.set('max_price', params.max_price);
    if (params.baggage && params.baggage !== 'Any') query.set('baggage', params.baggage);
    if (params.time_of_day && params.time_of_day !== 'Any time') query.set('time_of_day', params.time_of_day);
    if (params.direct_only) query.set('direct_only', 'true');
    if (params.sort_by) query.set('sort_by', params.sort_by);
    if (params.adults) query.set('adults', params.adults);
    if (params.bypass_cache) query.set('bypass_cache', 'true');

    return this._fetch(`/api/v1/flights/search?${query.toString()}`);
  }

  async getProviderStatus() {
    return this._fetch('/api/v1/flights/provider-status');
  }

  async autocompleteAirports(query = '', limit = 10) {
    return this._fetch(`/api/v1/flights/airports/autocomplete?q=${encodeURIComponent(query)}&limit=${limit}`);
  }

  async listAirports(query = null, limit = null) {
    let url = '/api/v1/flights/airports';
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (limit) params.set('limit', limit);
    const qs = params.toString();
    return this._fetch(qs ? `${url}?${qs}` : url);
  }

  async listAirlines() {
    return this._fetch('/api/v1/flights/airlines');
  }

  async getFlightStatus(flightNo) {
    const encoded = encodeURIComponent(flightNo.trim());
    return this._fetch(`/api/v1/flights/status/${encoded}`);
  }

  // Route Intelligence
  async getRoutes() {
    return this._fetch('/api/v1/routes');
  }

  async getRouteElasticity(origin = 'DEL', destination = 'BOM') {
    return this._fetch(`/api/v1/routes/${origin}/${destination}/elasticity`);
  }

  // APIx Index & Trends
  async getApixOverview() {
    return this._fetch('/api/v1/apix/overview');
  }

  async getApixTrend(period = '30D') {
    return this._fetch(`/api/v1/apix/trend?period=${encodeURIComponent(period)}`);
  }

  // Price Alerts (CRUD)
  async getAlerts() {
    return this._fetch('/api/v1/alerts');
  }

  async createAlert(route, currentFare, targetCondition) {
    return this._fetch('/api/v1/alerts', {
      method: 'POST',
      body: JSON.stringify({
        route,
        current_fare: currentFare,
        target_condition: targetCondition
      })
    });
  }

  async deleteAlert(alertId) {
    return this._fetch(`/api/v1/alerts/${alertId}`, {
      method: 'DELETE'
    });
  }

  // Data Quality
  async getQualityReport() {
    return this._fetch('/api/v1/quality');
  }

  // CPI Simulation
  async simulateCpi(payload) {
    return this._fetch('/api/v1/cpi-simulation', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Refund Tracking
  async trackRefund(pnr) {
    const encoded = encodeURIComponent(pnr.trim().toUpperCase());
    return this._fetch(`/api/v1/refunds/track/${encoded}`);
  }

  async listRefunds() {
    return this._fetch('/api/v1/refunds');
  }

  async submitRefundClaim(data) {
    return this._fetch('/api/v1/refunds/claim', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  // Price Prediction Engine
  async predictPrice(origin = 'HYD', destination = 'DEL', departDate = null) {
    const query = new URLSearchParams({ origin, destination });
    if (departDate) query.set('depart_date', departDate);
    return this._fetch(`/api/v1/predict/price?${query.toString()}`);
  }

  // Offers & Discounts
  async listOffers(category = null) {
    const url = category ? `/api/v1/offers/list?category=${encodeURIComponent(category)}` : '/api/v1/offers/list';
    return this._fetch(url);
  }

  async validateOffer(payload) {
    return this._fetch('/api/v1/offers/validate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Airline Comparison
  async compareSector(origin = 'DEL', destination = 'BOM') {
    const query = new URLSearchParams({ origin, destination });
    return this._fetch(`/api/v1/comparison/sector?${query.toString()}`);
  }

  // Monthly Cheapest Fares Calendar
  async getMonthlyCalendar(origin = 'DEL', destination = 'BOM', month = null) {
    const query = new URLSearchParams({ origin, destination });
    if (month) query.set('month', month);
    return this._fetch(`/api/v1/monthly-fares/calendar?${query.toString()}`);
  }

  // Travel Guide & Passenger Charter
  async getTravelDestinations() {
    return this._fetch('/api/v1/travel-guide/destinations');
  }

  async getDestinationDetail(code) {
    return this._fetch(`/api/v1/travel-guide/destination/${encodeURIComponent(code)}`);
  }

  async getGuidelines() {
    return this._fetch('/api/v1/travel-guide/guidelines');
  }

  // Tourist Plans & Packages
  async getTouristPlans(destination = null) {
    const url = destination ? `/api/v1/tourist-plans?destination=${encodeURIComponent(destination)}` : '/api/v1/tourist-plans';
    return this._fetch(url);
  }

  async bookTouristPlan(payload) {
    return this._fetch('/api/v1/tourist-plans/book', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // AI Aviation Assistant (Legacy & Enhanced)
  async chatWithAssistant(message, language = 'en', context = {}) {
    return this._fetch('/api/v1/ai/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ message, language, context })
    });
  }

  // Phase 7: AI Intelligence Layer Methods
  async getAiStatus() {
    return this._fetch('/api/v1/ai/status');
  }

  async interpretSearch(query) {
    return this._fetch('/api/v1/ai/interpret-search', {
      method: 'POST',
      body: JSON.stringify({ query })
    });
  }

  async recommendFlightsAi(flights, userPreferences = null, searchParams = null) {
    return this._fetch('/api/v1/ai/recommend', {
      method: 'POST',
      body: JSON.stringify({
        flights,
        user_preferences: userPreferences,
        search_params: searchParams
      })
    });
  }

  async compareFlightsAi(flightA, flightB, userPreferences = null) {
    return this._fetch('/api/v1/ai/compare', {
      method: 'POST',
      body: JSON.stringify({
        flight_a: flightA,
        flight_b: flightB,
        user_preferences: userPreferences
      })
    });
  }

  async getFlightInsights(flightNo, origin = null, destination = null, departDate = null) {
    const query = new URLSearchParams();
    if (origin) query.set('origin', origin);
    if (destination) query.set('destination', destination);
    if (departDate) query.set('depart_date', departDate);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this._fetch(`/api/v1/ai/flight-insights/${encodeURIComponent(flightNo)}${qs}`);
  }

  async getAiPreferences() {
    return this._fetch('/api/v1/ai/preferences');
  }

  async saveAiPreferences(payload) {
    return this._fetch('/api/v1/ai/preferences', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async chatWithCopilot(message, searchContext = null, availableFlights = null, selectedFlight = null, userPreferences = null, language = 'en') {
    return this._fetch('/api/v1/ai/copilot', {
      method: 'POST',
      body: JSON.stringify({
        message,
        search_context: searchContext,
        available_flights: availableFlights,
        selected_flight: selectedFlight,
        user_preferences: userPreferences,
        language
      })
    });
  }

  // Google Flights 30-Day Historical Data & Price Insights
  async getGoogleFlightsHistory30d(origin = 'DEL', destination = 'BOM') {
    const query = new URLSearchParams({ origin, destination });
    return this._fetch(`/api/v1/google-flights/history-30d?${query.toString()}`);
  }

  // MoCA / DGCA Tax & Fee Decomposition (Base, UDF, ASF, YQ, 5% GST)
  async getTaxBreakdown(basePrice = 4500, cabin = 'Economy') {
    const query = new URLSearchParams({ base_price: basePrice, cabin });
    return this._fetch(`/api/v1/google-flights/tax-breakdown?${query.toString()}`);
  }

  // Secure Checkout, PNR & Boarding Pass Generator
  async checkoutFlight(payload) {
    return this._fetch('/api/v1/google-flights/checkout', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Supabase Cloud Database Connector (Read-only status)
  async getSupabaseStatus() {
    return this._fetch('/api/v1/supabase/status');
  }

  // Authoritative Server-Side Price Calculation
  async calculatePaymentPrice(payload) {
    return this._fetch('/api/v1/payments/calculate-price', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Payment State Machine: Order Creation
  async createPaymentOrder(payload) {
    return this._fetch('/api/v1/payments/create-order', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Payment State Machine: Signature Verification
  async verifyPayment(payload) {
    return this._fetch('/api/v1/payments/verify', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Sandbox Mode Authorize / Decline Simulator
  async sandboxAuthorize(payload) {
    return this._fetch('/api/v1/payments/sandbox-authorize', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Real-time Payment & Booking Order Status
  async getPaymentStatus(orderId) {
    return this._fetch(`/api/v1/payments/status/${encodeURIComponent(orderId)}`);
  }

  // Customer Trips & Bookings
  async getMyTrips() {
    return this._fetch('/api/v1/trips/my-trips');
  }

  async getBookingDetails(bookingId) {
    return this._fetch(`/api/v1/trips/booking/${encodeURIComponent(bookingId)}`);
  }

  // Saved Flights Watchlist
  async getSavedFlights() {
    return this._fetch('/api/v1/saved-flights');
  }

  async saveFlight(flightData) {
    return this._fetch('/api/v1/saved-flights', {
      method: 'POST',
      body: JSON.stringify(flightData)
    });
  }

  async deleteSavedFlight(savedId) {
    return this._fetch(`/api/v1/saved-flights/${savedId}`, {
      method: 'DELETE'
    });
  }

  // User Profile
  async getAuthProfile() {
    return this._fetch('/api/v1/auth/me');
  }

  async updateAuthProfile(profileData) {
    return this._fetch('/api/v1/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  }

  // Phase 5: Core Booking Engine API
  async createBooking(bookingPayload) {
    return this._fetch('/api/v1/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingPayload)
    });
  }

  async getBooking(bookingIdOrRef) {
    return this._fetch(`/api/v1/bookings/${encodeURIComponent(bookingIdOrRef)}`);
  }

  async cancelBooking(bookingIdOrRef) {
    return this._fetch(`/api/v1/bookings/${encodeURIComponent(bookingIdOrRef)}/cancel`, {
      method: 'POST'
    });
  }

  // Phase 6: System Health & Provider Readiness
  async getHealth() {
    return this._fetch('/api/v1/health');
  }
}

window.api = new AirfarexAPI();


