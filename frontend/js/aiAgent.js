/**
 * AirfareX India — Central Agentic AI Travel Advisor & Live Voice Engine
 * Phase 8 & 8.5 Implementation
 * 
 * Features:
 * 1. ONE Central Agent: window.AirfareXAgent
 * 2. 3 Demo Customer Profiles (Budget, Comfort, Time-Critical) with 10+ Historical Bookings
 * 3. History Analysis Engine: computes behavioral weights, average fare, airline affinity
 * 4. Priority Override Resolver: Current natural language intent ALWAYS overrides history
 * 5. Dual Scoring: AirfareX General Score (0-100) vs Personal Match Score (0-100)
 * 6. Explicit 19-Tool Registry on AirfareXAgent.tools returning structured data
 * 7. Multi-Turn Conversational Memory (maintains route context, draft bookings, preference trail)
 * 8. Live Voice AI Assistant: Browser-native SpeechRecognition & SpeechSynthesis with Interruption
 * 9. Privacy Controls: ON/OFF toggle, Reset preferences, User-provided Accessibility needs
 * 10. Zero external API requirement for local demo mode
 */

(function() {
  'use strict';

  // =========================================================================
  // 1. DEMO CUSTOMER PROFILES & 10+ HISTORICAL BOOKINGS PER CUSTOMER
  // =========================================================================

  const DEMO_CUSTOMER_PROFILES = {
    budget: {
      customerId: "DEMO-1001",
      name: "Rajesh Sharma",
      tag: "Budget Traveler",
      persona: "Budget Traveler",
      avatar: "💼",
      bio: "Frequent domestic traveler who prioritizes low fares, non-stop morning flights, and budget carriers.",
      preferences: {
        priority: "cheapest",
        preferredAirlines: ["IndiGo", "Akasa Air", "Air India Express"],
        preferredCabin: "Economy",
        preferredDeparture: "morning",
        maxTypicalBudget: 6500,
        preferredStops: 0,
        priceImportance: 0.60,
        reliabilityImportance: 0.20,
        comfortImportance: 0.10,
        speedImportance: 0.10,
        durationImportance: 0.10,
        punctualityImportance: 0.20,
        useHistory: true,
        wheelchairAssistance: false,
        extraLegroom: false,
        specialMeal: false,
        aisleSeat: false
      },
      accessibilityNeeds: {
        enabled: false,
        wheelchairAssistance: false,
        reducedWalking: false,
        airportAssistance: false,
        preferFewerConnections: true,
        preferShorterTravelTime: false
      },
      useHistory: true,
      history: [
        { id: "TRIP-101", sector: "HYD ➔ DEL", origin: "HYD", destination: "DEL", airline: "IndiGo", flightNo: "6E 203", fare: 5240, stops: "Nonstop", time: "morning", depTime: "06:15", cabin: "Economy", rating: 5, date: "2026-06-12" },
        { id: "TRIP-102", sector: "HYD ➔ BOM", origin: "HYD", destination: "BOM", airline: "IndiGo", flightNo: "6E 522", fare: 3540, stops: "Nonstop", time: "morning", depTime: "07:30", cabin: "Economy", rating: 4, date: "2026-06-28" },
        { id: "TRIP-103", sector: "DEL ➔ BOM", origin: "DEL", destination: "BOM", airline: "Akasa Air", flightNo: "QP 1320", fare: 4390, stops: "Nonstop", time: "afternoon", depTime: "13:35", cabin: "Economy", rating: 5, date: "2026-07-05" },
        { id: "TRIP-104", sector: "HYD ➔ BLR", origin: "HYD", destination: "BLR", airline: "IndiGo", flightNo: "6E 449", fare: 3800, stops: "Nonstop", time: "morning", depTime: "09:15", cabin: "Economy", rating: 4, date: "2026-07-19" },
        { id: "TRIP-105", sector: "BOM ➔ HYD", origin: "BOM", destination: "HYD", airline: "Air India Express", flightNo: "IX 412", fare: 3350, stops: "Nonstop", time: "afternoon", depTime: "15:45", cabin: "Economy", rating: 4, date: "2026-08-02" },
        { id: "TRIP-106", sector: "BLR ➔ DEL", origin: "BLR", destination: "DEL", airline: "IndiGo", flightNo: "6E 2132", fare: 5950, stops: "Nonstop", time: "morning", depTime: "06:30", cabin: "Economy", rating: 5, date: "2026-08-14" },
        { id: "TRIP-107", sector: "HYD ➔ DEL", origin: "HYD", destination: "DEL", airline: "Akasa Air", flightNo: "QP 1412", fare: 4980, stops: "Nonstop", time: "morning", depTime: "11:20", cabin: "Economy", rating: 5, date: "2026-08-25" },
        { id: "TRIP-108", sector: "MAA ➔ HYD", origin: "MAA", destination: "HYD", airline: "IndiGo", flightNo: "6E 471", fare: 3000, stops: "Nonstop", time: "morning", depTime: "08:00", cabin: "Economy", rating: 4, date: "2026-09-01" },
        { id: "TRIP-109", sector: "BOM ➔ BLR", origin: "BOM", destination: "BLR", airline: "Akasa Air", flightNo: "QP 1105", fare: 3680, stops: "Nonstop", time: "afternoon", depTime: "16:20", cabin: "Economy", rating: 5, date: "2026-09-03" },
        { id: "TRIP-110", sector: "DEL ➔ CCU", origin: "DEL", destination: "CCU", airline: "IndiGo", flightNo: "6E 825", fare: 5750, stops: "Nonstop", time: "morning", depTime: "07:45", cabin: "Economy", rating: 4, date: "2026-09-05" }
      ]
    },

    comfort: {
      customerId: "DEMO-1002",
      name: "Priya Patel",
      tag: "Comfort Traveler",
      persona: "Comfort Traveler",
      avatar: "🛋️",
      bio: "Leisure & corporate executive traveler who values extra legroom, full-service amenities, and seamless connections.",
      preferences: {
        priority: "comfort",
        preferredAirlines: ["Air India", "IndiGo"],
        preferredCabin: "Economy / Premium",
        preferredDeparture: "afternoon",
        maxTypicalBudget: 12000,
        preferredStops: 0,
        priceImportance: 0.10,
        comfortImportance: 0.60,
        reliabilityImportance: 0.20,
        speedImportance: 0.10,
        durationImportance: 0.10,
        punctualityImportance: 0.20,
        useHistory: true,
        wheelchairAssistance: false,
        extraLegroom: true,
        specialMeal: true,
        aisleSeat: true
      },
      accessibilityNeeds: {
        enabled: true,
        wheelchairAssistance: false,
        reducedWalking: true,
        airportAssistance: true,
        preferFewerConnections: true,
        preferShorterTravelTime: false
      },
      useHistory: true,
      history: [
        { id: "TRIP-201", sector: "HYD ➔ DEL", origin: "HYD", destination: "DEL", airline: "Air India", flightNo: "AI 541", fare: 5780, stops: "Nonstop", time: "morning", depTime: "08:10", cabin: "Economy", rating: 5, date: "2026-06-15" },
        { id: "TRIP-202", sector: "DEL ➔ BOM", origin: "DEL", destination: "BOM", airline: "Air India", flightNo: "AI 864", fare: 5250, stops: "Nonstop", time: "morning", depTime: "09:05", cabin: "Economy", rating: 5, date: "2026-07-02" },
        { id: "TRIP-203", sector: "BOM ➔ BLR", origin: "BOM", destination: "BLR", airline: "Air India", flightNo: "AI 639", fare: 4300, stops: "Nonstop", time: "morning", depTime: "11:30", cabin: "Economy", rating: 4, date: "2026-07-18" },
        { id: "TRIP-204", sector: "DEL ➔ MAA", origin: "DEL", destination: "MAA", airline: "Air India", flightNo: "AI 441", fare: 7000, stops: "Nonstop", time: "afternoon", depTime: "15:10", cabin: "Economy", rating: 5, date: "2026-08-01" },
        { id: "TRIP-205", sector: "DEL ➔ BOM", origin: "DEL", destination: "BOM", airline: "Air India", flightNo: "AI 678", fare: 6240, stops: "Nonstop", time: "evening", depTime: "19:00", cabin: "Economy", rating: 5, date: "2026-08-11" },
        { id: "TRIP-206", sector: "BLR ➔ HYD", origin: "BLR", destination: "HYD", airline: "Air India", flightNo: "AI 512", fare: 4200, stops: "Nonstop", time: "afternoon", depTime: "12:15", cabin: "Economy", rating: 4, date: "2026-08-20" },
        { id: "TRIP-207", sector: "DEL ➔ BLR", origin: "DEL", destination: "BLR", airline: "Air India", flightNo: "AI 506", fare: 6400, stops: "Nonstop", time: "morning", depTime: "10:15", cabin: "Economy", rating: 5, date: "2026-08-29" },
        { id: "TRIP-208", sector: "HYD ➔ BOM", origin: "HYD", destination: "BOM", airline: "Air India", flightNo: "AI 618", fare: 3950, stops: "Nonstop", time: "evening", depTime: "18:15", cabin: "Economy", rating: 4, date: "2026-09-02" },
        { id: "TRIP-209", sector: "DEL ➔ CCU", origin: "DEL", destination: "CCU", airline: "Air India", flightNo: "AI 702", fare: 6150, stops: "Nonstop", time: "evening", depTime: "17:15", cabin: "Economy", rating: 5, date: "2026-09-04" },
        { id: "TRIP-210", sector: "CCU ➔ DEL", origin: "CCU", destination: "DEL", airline: "Air India", flightNo: "AI 701", fare: 6300, stops: "Nonstop", time: "afternoon", depTime: "16:30", cabin: "Economy", rating: 5, date: "2026-09-06" }
      ]
    },

    time_critical: {
      customerId: "DEMO-1003",
      name: "Vikram Reddy",
      tag: "Time-Critical Business Traveler",
      persona: "Time-Critical",
      avatar: "⚡",
      bio: "High-frequency business executive where on-time arrival, rapid security transit, and zero delays are paramount.",
      preferences: {
        priority: "fastest",
        preferredAirlines: ["IndiGo", "Akasa Air", "Air India"],
        preferredCabin: "Economy / Business",
        preferredDeparture: "early_morning",
        maxTypicalBudget: 15000,
        preferredStops: 0,
        priceImportance: 0.10,
        comfortImportance: 0.10,
        reliabilityImportance: 0.30,
        speedImportance: 0.50,
        durationImportance: 0.50,
        punctualityImportance: 0.30,
        useHistory: true,
        wheelchairAssistance: false,
        extraLegroom: true,
        specialMeal: false,
        aisleSeat: true
      },
      accessibilityNeeds: {
        enabled: false,
        wheelchairAssistance: false,
        reducedWalking: false,
        airportAssistance: false,
        preferFewerConnections: true,
        preferShorterTravelTime: true
      },
      useHistory: true,
      history: [
        { id: "TRIP-301", sector: "HYD ➔ DEL", origin: "HYD", destination: "DEL", airline: "IndiGo", flightNo: "6E 203", fare: 5240, stops: "Nonstop", time: "morning", depTime: "06:15", cabin: "Economy", rating: 5, date: "2026-06-10" },
        { id: "TRIP-302", sector: "BOM ➔ DEL", origin: "BOM", destination: "DEL", airline: "IndiGo", flightNo: "6E 215", fare: 4920, stops: "Nonstop", time: "morning", depTime: "07:00", cabin: "Economy", rating: 5, date: "2026-06-22" },
        { id: "TRIP-303", sector: "BLR ➔ DEL", origin: "BLR", destination: "DEL", airline: "IndiGo", flightNo: "6E 2132", fare: 5950, stops: "Nonstop", time: "morning", depTime: "06:30", cabin: "Economy", rating: 5, date: "2026-07-08" },
        { id: "TRIP-304", sector: "DEL ➔ BOM", origin: "DEL", destination: "BOM", airline: "IndiGo", flightNo: "6E 214", fare: 4820, stops: "Nonstop", time: "morning", depTime: "06:10", cabin: "Economy", rating: 5, date: "2026-07-25" },
        { id: "TRIP-305", sector: "HYD ➔ BOM", origin: "HYD", destination: "BOM", airline: "IndiGo", flightNo: "6E 344", fare: 3540, stops: "Nonstop", time: "morning", depTime: "06:00", cabin: "Economy", rating: 5, date: "2026-08-05" },
        { id: "TRIP-306", sector: "MAA ➔ DEL", origin: "MAA", destination: "DEL", airline: "IndiGo", flightNo: "6E 611", fare: 6780, stops: "Nonstop", time: "morning", depTime: "06:40", cabin: "Economy", rating: 4, date: "2026-08-16" },
        { id: "TRIP-307", sector: "DEL ➔ BLR", origin: "DEL", destination: "BLR", airline: "IndiGo", flightNo: "6E 2131", fare: 6050, stops: "Nonstop", time: "morning", depTime: "07:00", cabin: "Economy", rating: 5, date: "2026-08-28" },
        { id: "TRIP-308", sector: "BOM ➔ BLR", origin: "BOM", destination: "BLR", airline: "Akasa Air", flightNo: "QP 1105", fare: 3680, stops: "Nonstop", time: "afternoon", depTime: "16:20", cabin: "Economy", rating: 5, date: "2026-09-01" },
        { id: "TRIP-309", sector: "HYD ➔ DEL", origin: "HYD", destination: "DEL", airline: "Akasa Air", flightNo: "QP 1412", fare: 4980, stops: "Nonstop", time: "morning", depTime: "11:20", cabin: "Economy", rating: 5, date: "2026-09-04" },
        { id: "TRIP-310", sector: "DEL ➔ GOI", origin: "DEL", destination: "GOI", airline: "IndiGo", flightNo: "6E 331", fare: 5800, stops: "Nonstop", time: "morning", depTime: "09:20", cabin: "Economy", rating: 5, date: "2026-09-06" }
      ]
    }
  };

  // =========================================================
  // 2. SESSION STATE & LIVE METRICS
  // =========================================================

  let activeProfileKey = 'budget';
  let currentProfile = JSON.parse(JSON.stringify(DEMO_CUSTOMER_PROFILES.budget));

  const sessionMemory = {
    currentRoute: { origin: 'HYD', destination: 'DEL' },
    currentDate: null,
    currentCandidates: [],
    currentPreferenceWeights: { ...currentProfile.preferences },
    historicalPreferenceProfile: null,
    currentRecommendation: null,
    selectedFlight: null,
    bookingDraft: null,
    confirmedBooking: null,
    historyUsageEnabled: true,
    lastTurnType: 'INIT',
    conversationHistory: []
  };

  const aiSessionMetrics = {
    searches: 132,
    recommendations: 94,
    personalizedRecommendations: 51,
    historyBasedRecommendations: 38,
    comparisons: 59,
    demoBookings: 34,
    preferenceChanges: 22,
    bestMatchSelections: 31,
    avgPersonalMatch: 92
  };

  // =========================================================
  // 3. HISTORY ANALYSIS ENGINE (analyzeTravelHistory)
  // =========================================================

  function analyzeTravelHistory(history) {
    const list = history || currentProfile.history || [];
    if (list.length === 0) {
      return {
        preferredAirline: "IndiGo",
        averageFare: 5000,
        typicalBudget: 7500,
        preferredDeparture: "morning",
        preferredStops: 0,
        priceSensitivity: 0.75,
        comfortSensitivity: 0.60,
        reliabilitySensitivity: 0.80,
        speedSensitivity: 0.70,
        nonStopRatio: 1.0,
        totalTrips: 0
      };
    }

    const airlineCounts = {};
    let totalFare = 0;
    let nonStopCount = 0;
    const timeOfDayCounts = { morning: 0, afternoon: 0, evening: 0, night: 0 };

    list.forEach(t => {
      airlineCounts[t.airline] = (airlineCounts[t.airline] || 0) + 1;
      totalFare += t.fare || 0;
      if (t.stops === 'Nonstop' || t.stops === '0' || t.stops === 0) nonStopCount++;
      if (t.time) timeOfDayCounts[t.time] = (timeOfDayCounts[t.time] || 0) + 1;
    });

    const preferredAirline = Object.keys(airlineCounts).reduce((a, b) => airlineCounts[a] > airlineCounts[b] ? a : b, 'IndiGo');
    const preferredDeparture = Object.keys(timeOfDayCounts).reduce((a, b) => timeOfDayCounts[a] > timeOfDayCounts[b] ? a : b, 'morning');
    const averageFare = Math.round(totalFare / list.length);
    const nonStopRatio = nonStopCount / list.length;

    const priceSensitivity = averageFare < 5000 ? 0.90 : (averageFare < 7000 ? 0.75 : 0.40);
    const comfortSensitivity = preferredAirline === 'Air India' ? 0.90 : 0.55;
    const reliabilitySensitivity = nonStopRatio > 0.8 ? 0.88 : 0.70;
    const speedSensitivity = nonStopRatio > 0.8 ? 0.85 : 0.65;

    return {
      preferredAirline,
      averageFare,
      typicalBudget: Math.round(averageFare * 1.25),
      preferredDeparture,
      preferredStops: nonStopRatio >= 0.8 ? 0 : 1,
      priceSensitivity,
      comfortSensitivity,
      reliabilitySensitivity,
      speedSensitivity,
      nonStopRatio,
      totalTrips: list.length
    };
  }

  sessionMemory.historicalPreferenceProfile = analyzeTravelHistory(currentProfile.history);

  // =========================================================
  // 4. PERSONAL MATCH SCORING FORMULA (Step 8 & 9)
  // =========================================================

  /**
   * Personal Match = 
   *   Price Fit * priceWeight 
   * + Comfort Fit * comfortWeight 
   * + Reliability Fit * reliabilityWeight 
   * + Punctuality Fit * punctualityWeight 
   * + Convenience Fit * convenienceWeight
   * Normalized to 0–100.
   */
  function calculatePersonalMatch(flight, customWeights = null) {
    if (!flight) return 85;

    const weights = customWeights || sessionMemory.currentPreferenceWeights || currentProfile.preferences;
    const hist = (sessionMemory.historyUsageEnabled && currentProfile.preferences.useHistory !== false)
      ? sessionMemory.historicalPreferenceProfile 
      : null;

    const pScore = flight.priceScore || 90;
    const rScore = flight.reliabilityScore || 92;
    const punctScore = flight.punctualityScore || flight.onTimePercentage || 94;
    const cScore = flight.comfortScore || 85;
    const fare = flight.totalPrice || flight.total_fare || 5000;
    const stops = flight.stops || 'Nonstop';
    const isNonstop = stops === 'Nonstop' || stops === '0';
    const airline = flight.airline || 'IndiGo';
    const depTime = flight.departureTime || flight.dep_time || '08:00';
    const depHour = parseInt(depTime.split(':')[0]) || 8;

    // 1. Price Fit (0–100)
    let priceFit = pScore;
    const budgetLimit = weights.maxTypicalBudget || (hist ? hist.typicalBudget : 8000);
    if (fare <= budgetLimit) {
      priceFit = Math.min(100, priceFit + 8);
    } else {
      const overBudgetPenalty = Math.min(35, Math.round(((fare - budgetLimit) / budgetLimit) * 50));
      priceFit = Math.max(20, priceFit - overBudgetPenalty);
    }

    // 2. Comfort Fit (0–100)
    let comfortFit = cScore;
    if (airline === 'Air India' || (flight.seat_pitch && parseInt(flight.seat_pitch) >= 31)) {
      comfortFit = Math.min(100, comfortFit + 6);
    }
    if (weights.extraLegroom) comfortFit = Math.min(100, comfortFit + 4);

    // 3. Reliability Fit (0–100)
    let reliabilityFit = rScore;

    // 4. Punctuality Fit (0–100)
    let punctualityFit = punctScore;

    // 5. Convenience Fit (0–100)
    let convenienceFit = 85;
    if (isNonstop) convenienceFit += 10;
    else convenienceFit -= 18;

    // Departure time alignment
    const prefTime = (weights.preferredDeparture || (hist ? hist.preferredDeparture : 'any')).toLowerCase();
    if (prefTime.includes('morning') || prefTime === 'early_morning') {
      if (depHour >= 5 && depHour <= 11) convenienceFit += 6;
      else convenienceFit -= 8;
    } else if (prefTime.includes('afternoon')) {
      if (depHour >= 12 && depHour <= 17) convenienceFit += 6;
    } else if (prefTime.includes('evening')) {
      if (depHour >= 17 && depHour <= 22) convenienceFit += 6;
    }

    // Airline Affinity from history
    if (hist && sessionMemory.historyUsageEnabled) {
      if (airline === hist.preferredAirline) convenienceFit += 6;
      if (currentProfile.preferences.preferredAirlines && currentProfile.preferences.preferredAirlines.includes(airline)) {
        convenienceFit += 4;
      }
    }

    // Accessibility / assistance convenience fit (Step 19)
    const access = currentProfile.accessibilityNeeds || {};
    if (access.enabled || weights.wheelchairAssistance || weights.reducedWalking) {
      if (isNonstop) convenienceFit += 8;
      if (access.preferShorterTravelTime && isNonstop) convenienceFit += 4;
    }

    convenienceFit = Math.max(30, Math.min(100, convenienceFit));

    // Determine Normalized Weights
    const wPrice = weights.priceImportance !== undefined ? weights.priceImportance : 0.35;
    const wComfort = weights.comfortImportance !== undefined ? weights.comfortImportance : 0.25;
    const wRel = weights.reliabilityImportance !== undefined ? weights.reliabilityImportance : 0.20;
    const wPunct = weights.punctualityImportance !== undefined ? weights.punctualityImportance : 0.10;
    const wConv = (weights.speedImportance || weights.durationImportance || 0.10);

    const totalWeight = (wPrice + wComfort + wRel + wPunct + wConv) || 1.0;
    const nwPrice = wPrice / totalWeight;
    const nwComfort = wComfort / totalWeight;
    const nwRel = wRel / totalWeight;
    const nwPunct = wPunct / totalWeight;
    const nwConv = wConv / totalWeight;

    const rawMatch = (priceFit * nwPrice) 
                   + (comfortFit * nwComfort) 
                   + (reliabilityFit * nwRel) 
                   + (punctualityFit * nwPunct) 
                   + (convenienceFit * nwConv);

    return Math.max(50, Math.min(99, Math.round(rawMatch)));
  }

  // Alias for compatibility
  const calculatePersonalizedMatch = calculatePersonalMatch;

  // =========================================================
  // 5. EXPLICIT 19-TOOL REGISTRY (Step 10)
  // =========================================================

  const AgentTools = {
    // 1. searchFlights
    searchFlights: Object.assign(
      function(params = {}) {
        aiSessionMetrics.searches++;
        const orig = params.origin || sessionMemory.currentRoute.origin || 'HYD';
        const dest = params.destination || sessionMemory.currentRoute.destination || 'DEL';
        sessionMemory.currentRoute = { origin: orig, destination: dest };

        let flights = [];
        if (window.AirfarexDemoData && typeof window.AirfarexDemoData.filterFlights === 'function') {
          flights = window.AirfarexDemoData.filterFlights({
            from_city: orig,
            to_city: dest,
            stops: params.stops || 'Any',
            airline: params.airline || 'All airlines',
            max_price: params.maxPrice,
            cabin: params.cabinClass || 'Economy'
          });
        }

        flights = flights.map(f => {
          const matchScore = calculatePersonalMatch(f);
          return {
            ...f,
            personalMatchScore: matchScore,
            personal_match: matchScore
          };
        });

        sessionMemory.currentCandidates = flights;

        if (typeof window.renderFlightCards === 'function' && flights.length > 0) {
          const bestFare = Math.min(...flights.map(f => f.totalPrice || f.total_fare));
          window.renderFlightCards(flights, bestFare, { data_source: 'DEMO' });
        }

        return flights;
      },
      { description: "Search flights matching route, price, airline, and date constraints with personal scoring.", parameters: ["origin", "destination", "maxPrice", "stops", "airline", "cabinClass"] }
    ),

    // 2. filterFlights
    filterFlights: Object.assign(
      function(filters = {}) {
        let list = [...sessionMemory.currentCandidates];
        if (list.length === 0) list = AgentTools.searchFlights();

        if (filters.maxPrice) {
          list = list.filter(f => (f.totalPrice || f.total_fare) <= filters.maxPrice);
        }
        if (filters.stops !== undefined && filters.stops !== 'Any') {
          const isNonStop = filters.stops === 'Nonstop' || filters.stops === 0 || filters.stops === '0';
          list = list.filter(f => isNonStop ? (f.stops === 'Nonstop' || f.stops === '0') : f.stops !== 'Nonstop');
        }
        if (filters.airline && filters.airline !== 'All airlines') {
          list = list.filter(f => f.airline.toLowerCase().includes(filters.airline.toLowerCase()));
        }
        if (filters.timeOfDay && filters.timeOfDay !== 'Any time') {
          const tod = filters.timeOfDay.toLowerCase();
          list = list.filter(f => {
            const hour = parseInt((f.departureTime || '08:00').split(':')[0]) || 8;
            if (tod.includes('morning')) return hour >= 5 && hour < 12;
            if (tod.includes('afternoon')) return hour >= 12 && hour < 17;
            if (tod.includes('evening') || tod.includes('night')) return hour >= 17;
            return true;
          });
        }

        sessionMemory.currentCandidates = list;
        return list;
      },
      { description: "Filter candidate flights by price range, airline, departure time, and stops.", parameters: ["maxPrice", "stops", "airline", "timeOfDay"] }
    ),

    // 3. sortFlights
    sortFlights: Object.assign(
      function(mode = 'match') {
        let list = [...sessionMemory.currentCandidates];
        if (mode === 'match' || mode === 'best_for_me') {
          list.sort((a, b) => (b.personalMatchScore || 85) - (a.personalMatchScore || 85));
        } else if (mode === 'score' || mode === 'best_overall') {
          list.sort((a, b) => (b.overallScore || 85) - (a.overallScore || 85));
        } else if (mode === 'price' || mode === 'cheapest') {
          list.sort((a, b) => (a.totalPrice || a.total_fare) - (b.totalPrice || b.total_fare));
        } else if (mode === 'fastest' || mode === 'duration') {
          list.sort((a, b) => (a.durationMinutes || 120) - (b.durationMinutes || 120));
        } else if (mode === 'comfort') {
          list.sort((a, b) => (b.comfortScore || 85) - (a.comfortScore || 85));
        } else if (mode === 'reliability') {
          list.sort((a, b) => (b.reliabilityScore || 90) - (a.reliabilityScore || 90));
        }
        sessionMemory.currentCandidates = list;
        return list;
      },
      { description: "Sort candidate flights by personal match, general score, fare, duration, or reliability.", parameters: ["mode"] }
    ),

    // 4. getFlightDetails
    getFlightDetails: Object.assign(
      function(flightIdOrNumber) {
        const list = sessionMemory.currentCandidates.length > 0 
          ? sessionMemory.currentCandidates 
          : (window.AirfarexDemoData ? window.AirfarexDemoData.getAllFlights() : []);
        
        const f = list.find(item => 
          (item.flightNumber && item.flightNumber.toLowerCase() === String(flightIdOrNumber).toLowerCase()) ||
          (item.flight_no && item.flight_no.toLowerCase() === String(flightIdOrNumber).toLowerCase()) ||
          item.flightId === flightIdOrNumber
        ) || list[0] || null;

        if (!f) return { error: `Flight ${flightIdOrNumber} not found.` };

        return {
          flightId: f.flightId,
          airline: f.airline,
          flightNumber: f.flightNumber || f.flight_no,
          origin: f.origin,
          destination: f.destination,
          departureTime: f.departureTime,
          arrivalTime: f.arrivalTime,
          duration: f.duration,
          stops: f.stops,
          aircraft: f.aircraft || 'Airbus A320neo',
          cabinClass: f.cabinClass || 'Economy',
          totalPrice: f.totalPrice || f.total_fare,
          basePrice: f.basePrice || f.base_fare,
          taxes: f.taxes || 850,
          airfarexScore: f.overallScore || 90,
          personalMatchScore: f.personalMatchScore || calculatePersonalMatch(f),
          breakdown: {
            priceScore: f.priceScore || 90,
            reliabilityScore: f.reliabilityScore || 92,
            punctualityScore: f.punctualityScore || f.onTimePercentage || 94,
            comfortScore: f.comfortScore || 85
          },
          baggage: f.baggage || "15kg Check-in + 7kg Cabin",
          cancellation: f.cancellationPolicy || "Refundable with ₹2,500 fee"
        };
      },
      { description: "Retrieve full details, score decomposition, baggage, and cancellation policy for a flight.", parameters: ["flightIdOrNumber"] }
    ),

    // 5. calculateFlightScore
    calculateFlightScore: Object.assign(
      function(flight) {
        if (!flight) return { overallScore: 90, priceScore: 90, reliabilityScore: 92, punctualityScore: 94, comfortScore: 85 };
        const priceScore = flight.priceScore || 90;
        const reliabilityScore = flight.reliabilityScore || 92;
        const punctualityScore = flight.punctualityScore || flight.onTimePercentage || 94;
        const comfortScore = flight.comfortScore || 85;
        const overallScore = flight.overallScore || Math.round((priceScore * 0.35) + (reliabilityScore * 0.25) + (punctualityScore * 0.25) + (comfortScore * 0.15));
        return {
          flightNumber: flight.flightNumber || flight.flight_no,
          airline: flight.airline,
          overallScore,
          priceScore,
          reliabilityScore,
          punctualityScore,
          comfortScore
        };
      },
      { description: "Calculate general objective AirfareX quality score (0-100) based on industry benchmarks.", parameters: ["flight"] }
    ),

    // 6. explainScore
    explainScore: Object.assign(
      function(flight, alternativeFlight = null) {
        const chosenFlight = flight || sessionMemory.selectedFlight || sessionMemory.currentRecommendation || AgentTools.getBestForCustomer();
        if (!chosenFlight) return { error: "No flight specified to explain." };

        const hist = sessionMemory.historicalPreferenceProfile;
        const weights = sessionMemory.currentPreferenceWeights;
        const isHistoryUsed = sessionMemory.historyUsageEnabled;

        const fNo = chosenFlight.flightNumber || chosenFlight.flight_no;
        const airline = chosenFlight.airline;
        const fare = chosenFlight.totalPrice || chosenFlight.total_fare;
        const matchScore = chosenFlight.personalMatchScore || calculatePersonalMatch(chosenFlight);
        const genScore = chosenFlight.overallScore || 90;

        let reasons = [];

        if (weights.priceImportance >= 0.50) {
          reasons.push(`Competitive fare of ₹${Number(fare).toLocaleString('en-IN')} matches your budget priority.`);
        }
        if (weights.comfortImportance >= 0.40) {
          reasons.push(`Superior cabin comfort on ${chosenFlight.aircraft || 'fleet'} with ${chosenFlight.seat_pitch || '30"'} legroom.`);
        }
        if (weights.speedImportance >= 0.40 || weights.reliabilityImportance >= 0.40) {
          reasons.push(`Direct flight duration of ${chosenFlight.duration} with ${chosenFlight.punctualityScore || chosenFlight.onTimePercentage || 94}% DGCA on-time rating.`);
        }

        if (isHistoryUsed && hist) {
          if (chosenFlight.airline === hist.preferredAirline) {
            reasons.push(`Matches your frequent airline choice (${hist.preferredAirline} across ${hist.totalTrips} past demo trips).`);
          }
          if (chosenFlight.stops === 'Nonstop' && hist.nonStopRatio >= 0.8) {
            reasons.push(`Maintains your preference for nonstop routes.`);
          }
        }

        let diffVerdict = "";
        if (alternativeFlight && alternativeFlight.flightNumber !== chosenFlight.flightNumber) {
          const altNo = alternativeFlight.flightNumber || alternativeFlight.flight_no;
          const altGen = alternativeFlight.overallScore || 90;
          const altMatch = alternativeFlight.personalMatchScore || calculatePersonalMatch(alternativeFlight);

          if (altGen > genScore) {
            diffVerdict = `Flight ${alternativeFlight.airline} ${altNo} has a higher general score (${altGen}/100), but ${airline} ${fNo} is a superior personal match (${matchScore}/100 vs ${altMatch}/100) for your needs.`;
          }
        }

        return {
          flightNumber: fNo,
          airline: airline,
          personalMatchScore: matchScore,
          airfarexScore: genScore,
          reasons: reasons,
          diffVerdict: diffVerdict
        };
      },
      { description: "Generate explainable AI reasoning for why a flight is recommended for this customer.", parameters: ["flight", "alternativeFlight"] }
    ),

    // 7. getRecommendations
    getRecommendations: Object.assign(
      function(flightsList = null) {
        aiSessionMetrics.recommendations++;
        aiSessionMetrics.personalizedRecommendations++;
        if (sessionMemory.historyUsageEnabled) aiSessionMetrics.historyBasedRecommendations++;

        const list = flightsList || sessionMemory.currentCandidates;
        if (!list || list.length === 0) {
          const fresh = AgentTools.searchFlights();
          if (!fresh || fresh.length === 0) return null;
          return AgentTools.getRecommendations(fresh);
        }

        const bestForMe = AgentTools.getBestForCustomer(list);
        const bestOverall = AgentTools.getBestOverallFlight(list);
        const cheapest = AgentTools.getCheapestFlight(list);
        const fastest = AgentTools.getFastestFlight(list);
        const mostReliable = AgentTools.getMostReliableFlight(list);

        const explanation = AgentTools.explainScore(bestForMe, bestOverall);

        sessionMemory.currentRecommendation = bestForMe;
        sessionMemory.selectedFlight = bestForMe;

        return {
          bestForCustomer: bestForMe,
          bestForMe: bestForMe,
          bestOverall: bestOverall,
          cheapest: cheapest,
          fastest: fastest,
          mostReliable: mostReliable,
          explanation: explanation
        };
      },
      { description: "Get complete multi-factor recommendations (Best For You, Best Overall, Cheapest, Fastest, Most Reliable).", parameters: ["flightsList"] }
    ),

    // 8. getCheapestFlight
    getCheapestFlight: Object.assign(
      function(flightsList = null) {
        const list = flightsList || sessionMemory.currentCandidates;
        if (!list || list.length === 0) return null;
        return [...list].sort((a, b) => (a.totalPrice || a.total_fare) - (b.totalPrice || b.total_fare))[0];
      },
      { description: "Find the flight with the lowest total fare.", parameters: ["flightsList"] }
    ),

    // 9. getFastestFlight
    getFastestFlight: Object.assign(
      function(flightsList = null) {
        const list = flightsList || sessionMemory.currentCandidates;
        if (!list || list.length === 0) return null;
        return [...list].sort((a, b) => (a.durationMinutes || 120) - (b.durationMinutes || 120))[0];
      },
      { description: "Find the flight with the shortest sector travel duration.", parameters: ["flightsList"] }
    ),

    // 10. getMostReliableFlight
    getMostReliableFlight: Object.assign(
      function(flightsList = null) {
        const list = flightsList || sessionMemory.currentCandidates;
        if (!list || list.length === 0) return null;
        return [...list].sort((a, b) => ((b.reliabilityScore || 90) + (b.punctualityScore || 90)) - ((a.reliabilityScore || 90) + (a.punctualityScore || 90)))[0];
      },
      { description: "Find the flight with the highest on-time punctuality and operational reliability rating.", parameters: ["flightsList"] }
    ),

    // 11. getBestOverallFlight
    getBestOverallFlight: Object.assign(
      function(flightsList = null) {
        const list = flightsList || sessionMemory.currentCandidates;
        if (!list || list.length === 0) return null;
        return [...list].sort((a, b) => (b.overallScore || 85) - (a.overallScore || 85))[0];
      },
      { description: "Find the flight with the highest objective AirfareX quality score across all metrics.", parameters: ["flightsList"] }
    ),

    // 12. getBestForCustomer
    getBestForCustomer: Object.assign(
      function(flightsList = null) {
        aiSessionMetrics.bestMatchSelections++;
        const list = flightsList || sessionMemory.currentCandidates;
        if (!list || list.length === 0) {
          const fresh = AgentTools.searchFlights();
          if (!fresh || fresh.length === 0) return null;
          return [...fresh].sort((a, b) => (b.personalMatchScore || 85) - (a.personalMatchScore || 85))[0];
        }
        return [...list].sort((a, b) => (b.personalMatchScore || 85) - (a.personalMatchScore || 85))[0];
      },
      { description: "Find the flight that achieves the highest Personal Match Score specifically for this passenger.", parameters: ["flightsList"] }
    ),

    // 13. compareFlights
    compareFlights: Object.assign(
      function(flightIdentifiers = []) {
        aiSessionMetrics.comparisons++;
        let flightsToCompare = [];
        const list = sessionMemory.currentCandidates.length > 0 
          ? sessionMemory.currentCandidates 
          : (window.AirfarexDemoData ? window.AirfarexDemoData.getAllFlights() : []);

        if (flightIdentifiers && flightIdentifiers.length > 0) {
          flightIdentifiers.forEach(id => {
            const match = list.find(f => 
              (f.flightNumber && f.flightNumber.toLowerCase() === String(id).toLowerCase()) ||
              (f.flight_no && f.flight_no.toLowerCase() === String(id).toLowerCase()) ||
              f.flightId === id
            );
            if (match) flightsToCompare.push(match);
          });
        }

        if (flightsToCompare.length < 2) {
          flightsToCompare = list.slice(0, 3);
        }

        return flightsToCompare.map(f => ({
          flightNo: f.flightNumber || f.flight_no,
          airline: f.airline,
          price: f.totalPrice || f.total_fare,
          duration: f.duration,
          stops: f.stops,
          aircraft: f.aircraft,
          seatPitch: f.seat_pitch || '30"',
          airfarexScore: f.overallScore || 90,
          personalMatch: f.personalMatchScore || calculatePersonalMatch(f),
          priceScore: f.priceScore || 90,
          reliabilityScore: f.reliabilityScore || 92,
          punctualityScore: f.punctualityScore || f.onTimePercentage || 94,
          comfortScore: f.comfortScore || 85
        }));
      },
      { description: "Generate a side-by-side comparison matrix for two or more candidate flights.", parameters: ["flightIdentifiers"] }
    ),

    // 14. getCustomerProfile
    getCustomerProfile: Object.assign(
      function() {
        return {
          customerId: currentProfile.customerId,
          name: currentProfile.name,
          tag: currentProfile.tag,
          persona: currentProfile.persona,
          bio: currentProfile.bio,
          preferences: { ...currentProfile.preferences },
          accessibilityNeeds: { ...currentProfile.accessibilityNeeds },
          useHistory: sessionMemory.historyUsageEnabled,
          activeWeights: { ...sessionMemory.currentPreferenceWeights }
        };
      },
      { description: "Get the active customer profile, preferences, and accessibility settings.", parameters: [] }
    ),

    // 15. getTravelHistory
    getTravelHistory: Object.assign(
      function() {
        return [...currentProfile.history];
      },
      { description: "Retrieve the customer's 10+ past domestic demo bookings and sector choices.", parameters: [] }
    ),

    // 16. analyzeTravelHistory
    analyzeTravelHistory: Object.assign(
      function(hist = null) {
        return analyzeTravelHistory(hist || currentProfile.history);
      },
      { description: "Compute behavioral preferences, average spend, and airline affinity from history.", parameters: ["history"] }
    ),

    // 17. calculatePersonalMatch
    calculatePersonalMatch: Object.assign(
      function(flight, weights = null) {
        return calculatePersonalMatch(flight, weights);
      },
      { description: "Calculate personalized match score (0-100) using the multi-factor formula.", parameters: ["flight", "weights"] }
    ),

    // 18. createDemoBooking
    createDemoBooking: Object.assign(
      function(flightNo = null, customPax = null) {
        let flight = null;
        if (flightNo) {
          flight = sessionMemory.currentCandidates.find(f => (f.flightNumber || f.flight_no) === flightNo)
            || (window.AirfarexDemoData ? window.AirfarexDemoData.getFlightByNumber(flightNo) : null);
        }
        if (!flight) {
          flight = sessionMemory.selectedFlight || sessionMemory.currentRecommendation || AgentTools.getBestForCustomer();
        }

        if (!flight) return { error: "No flight available to book." };

        const travelerName = customPax?.name || currentProfile.name;
        const refCode = `TRV-AI-${Math.floor(100000 + Math.random() * 900000)}`;
        const fNo = flight.flightNumber || flight.flight_no || '6E 203';
        const fare = flight.totalPrice || flight.total_fare || 5240;

        sessionMemory.bookingDraft = {
          bookingRef: refCode,
          bookingReference: refCode,
          flightNo: fNo,
          flightNumber: fNo,
          airline: flight.airline,
          origin: flight.origin || sessionMemory.currentRoute.origin || 'HYD',
          destination: flight.destination || sessionMemory.currentRoute.destination || 'DEL',
          fare: fare,
          totalPrice: fare,
          travelerName: travelerName,
          passengerName: travelerName,
          travelDate: sessionMemory.currentDate || new Date(Date.now() + 86400000 * 3).toISOString().slice(0, 10),
          status: "DRAFT_PENDING_CONFIRMATION",
          allocatedSeat: `${Math.floor(4 + Math.random() * 20)}${['A', 'C', 'D', 'F'][Math.floor(Math.random() * 4)]}`,
          flight: flight
        };

        return sessionMemory.bookingDraft;
      },
      { description: "Prepare a demo booking draft for a selected flight in cryptographic sandbox.", parameters: ["flightNo", "customPax"] }
    ),

    // 19. confirmDemoBooking
    confirmDemoBooking: Object.assign(
      function() {
        if (!sessionMemory.bookingDraft) {
          AgentTools.createDemoBooking();
        }

        aiSessionMetrics.demoBookings++;
        sessionMemory.bookingDraft.status = "CONFIRMED";
        sessionMemory.bookingDraft.pnr = `PNR${Math.floor(100000 + Math.random() * 900000)}`;
        sessionMemory.bookingDraft.confirmedAt = new Date().toISOString();
        sessionMemory.confirmedBooking = { ...sessionMemory.bookingDraft };

        return sessionMemory.bookingDraft;
      },
      { description: "Confirm and issue the active demo booking draft with sandbox PNR and e-ticket voucher.", parameters: [] }
    )
  };

  // Helper Aliases
  AgentTools.getBestFlightForMe = AgentTools.getBestForCustomer;
  AgentTools.getPersonalizedRecommendation = AgentTools.getRecommendations;
  AgentTools.calculatePersonalizedMatch = AgentTools.calculatePersonalMatch;
  AgentTools.explainPersonalizedRecommendation = AgentTools.explainScore;

  // =========================================================
  // 6. NATURAL LANGUAGE INTENT & CONSTRAINT PARSER
  // =========================================================

  function parseUserQuery(query) {
    const q = (query || '').toLowerCase().trim();

    const intent = {
      action: 'GENERAL_CHAT',
      origin: null,
      destination: null,
      budget: null,
      stops: null,
      timeOfDay: null,
      airline: null,
      priorityOverride: null,
      referencedFlightNo: null,
      compareCount: null,
      isBooking: false,
      isConfirm: false,
      isCancel: false,
      isStartOver: false
    };

    // 1. Reset / Start Over
    if (q === 'start over' || q === 'reset' || q === 'clear' || q.includes('start again')) {
      intent.isStartOver = true;
      intent.action = 'START_OVER';
      return intent;
    }

    // 2. Cancellation
    if (q === 'cancel' || q.includes('cancel booking') || q.includes('never mind')) {
      intent.isCancel = true;
      intent.action = 'CANCEL';
      return intent;
    }

    // 3. Confirmations
    if (q === 'yes' || q === 'confirm' || q === 'yes book' || q === 'yes, book' || q === 'proceed' || q.includes('confirm booking') || q.includes('issue ticket')) {
      intent.isConfirm = true;
      intent.action = 'CONFIRM_BOOKING';
      return intent;
    }

    // 4. Booking request ("Book it", "Book the first one", "Book this flight")
    if (q === 'book it' || q === 'book' || q.includes('book the first') || q.includes('book this') || q.includes('reserve ticket') || q.includes('book flight')) {
      intent.isBooking = true;
      intent.action = 'INITIATE_BOOKING';
      return intent;
    }

    // 5. Sector matching (e.g. Hyderabad to Delhi, HYD to BOM, etc.)
    const sectorMatch = q.match(/(?:from\s+)?(hyderabad|delhi|mumbai|bengaluru|bangalore|chennai|kolkata|goa|pune|jaipur|hyd|del|bom|blr|maa|ccu|goi|pnq|jai)\s+(?:to|➔|->|--)\s+(hyderabad|delhi|mumbai|bengaluru|bangalore|chennai|kolkata|goa|pune|jaipur|hyd|del|bom|blr|maa|ccu|goi|pnq|jai)/i);
    if (sectorMatch) {
      intent.origin = mapCityToCode(sectorMatch[1]);
      intent.destination = mapCityToCode(sectorMatch[2]);
      intent.action = 'SEARCH';
    } else {
      const matchTo = q.match(/(?:to|in)\s+(hyderabad|delhi|mumbai|bengaluru|bangalore|chennai|kolkata|goa|pune|jaipur|hyd|del|bom|blr|maa|ccu|goi|pnq|jai)/i);
      if (matchTo) {
        intent.destination = mapCityToCode(matchTo[1]);
        intent.action = 'SEARCH';
      }
    }

    // 6. Budget constraint
    const budgetMatch = q.match(/(?:under|below|less than|max|within|budget of)\s*(?:₹|rs\.?|inr)?\s*([0-9,]+)/i);
    if (budgetMatch) {
      intent.budget = parseInt(budgetMatch[1].replace(/,/g, ''));
    }

    // 7. Stops constraint
    if (q.includes('no stop') || q.includes('nonstop') || q.includes('non-stop') || q.includes('direct only') || q.includes('zero stops') || q.includes("don't want stops") || q.includes('no stops')) {
      intent.stops = 'Nonstop';
    } else if (q.includes('1 stop') || q.includes('one stop') || q.includes('with stop')) {
      intent.stops = '1 stop';
    }

    // 8. Time of day
    if (q.includes('morning') || q.includes('early morning')) intent.timeOfDay = 'morning';
    else if (q.includes('afternoon')) intent.timeOfDay = 'afternoon';
    else if (q.includes('evening') || q.includes('night') || q.includes('red-eye')) intent.timeOfDay = 'evening';

    // 9. Airline
    if (q.includes('indigo')) intent.airline = 'IndiGo';
    else if (q.includes('air india express') || q.includes('ai express')) intent.airline = 'Air India Express';
    else if (q.includes('air india')) intent.airline = 'Air India';
    else if (q.includes('akasa')) intent.airline = 'Akasa Air';
    else if (q.includes('spicejet')) intent.airline = 'SpiceJet';

    // 10. Natural Language Priority Overrides (Step 6 & 7)
    if (q.includes('comfort is more important') || q.includes('comfort matters more') || q.includes('comfort more important') || q.includes('prioritize comfort') || q.includes('most comfortable') || q.includes('maximum comfort') || q.includes('dont care about price') || q.includes("don't care about price") || q.includes('price does not matter') || q.includes("price doesn't matter") || q.includes('pay more for comfort') || q.includes('find more comfortable') || q.includes('find something more comfortable')) {
      intent.priorityOverride = 'comfort';
    } else if (q.includes('price is most important') || q.includes('cheapest') || q.includes('lowest price') || q.includes('budget flight') || q.includes('find cheaper') || q.includes('find something cheaper') || q.includes('i want the cheapest')) {
      intent.priorityOverride = 'cheapest';
    } else if (q.includes('fastest') || q.includes('shortest') || q.includes('least time') || q.includes('quickest') || q.includes('i want the fastest')) {
      intent.priorityOverride = 'fastest';
    } else if (q.includes('reliable') || q.includes('on time') || q.includes('punctual') || q.includes('no delays') || q.includes('need something reliable') || q.includes('i need something reliable')) {
      intent.priorityOverride = 'reliability';
    } else if (q.includes('best value') || q.includes('best balance') || q.includes('balanced')) {
      intent.priorityOverride = 'best_value';
    } else if (q.includes('best overall') || q.includes('best flight overall')) {
      intent.priorityOverride = 'best_overall';
    }

    // 11. Intent Categorization
    if (intent.priorityOverride && (q.includes('what do you recommend now') || q.includes('recommend now') || q.includes('what is best now'))) {
      intent.action = 'RECOMMEND_FOR_ME';
    } else if (q.includes('compare') || q.includes('comparison') || q.includes('versus') || q.includes(' vs ')) {
      intent.action = 'COMPARE';
      const numMatch = q.match(/top\s*(\d+)/i) || q.match(/compare\s*(\d+)/i) || (q.includes('two') ? [, 2] : (q.includes('three') ? [, 3] : null));
      intent.compareCount = numMatch ? parseInt(numMatch[1]) : 2;
    } else if (q.includes('why did you choose') || q.includes('why did you change') || q.includes('why this flight') || q.includes('why is this') || q === 'why' || q === 'why?' || q.includes('explain score')) {
      intent.action = 'EXPLAIN';
    } else if (q.includes('best for me') || q.includes('which one is best for me') || q.includes('what is best for me') || q.includes('what do you recommend') || q.includes('recommend for me') || q.includes('suits me')) {
      intent.action = 'RECOMMEND_FOR_ME';
    } else if (q.includes('best overall') || q.includes('highest score') || q.includes('top rated')) {
      intent.action = 'RECOMMEND_BEST_OVERALL';
    } else if (q.includes('which is cheapest') || q.includes('find me the cheapest') || q.includes('show cheapest') || q.includes('cheapest flight')) {
      intent.action = 'FIND_CHEAPEST';
    } else if (q.includes('which is fastest') || q.includes('find fastest') || q.includes('fastest flight')) {
      intent.action = 'FIND_FASTEST';
    } else if (q.includes('which is most reliable') || q.includes('most reliable flight') || q.includes('highest reliability')) {
      intent.action = 'FIND_RELIABLE';
    } else if (q.includes('ignore my history') || q.includes('turn off personalization') || q.includes('without history')) {
      intent.action = 'IGNORE_HISTORY';
    } else if (q.includes('use my history') || q.includes('turn on personalization') || q.includes('with history')) {
      intent.action = 'USE_HISTORY';
    }

    return intent;
  }

  function mapCityToCode(str) {
    if (!str) return 'DEL';
    const s = str.toLowerCase().trim();
    if (s.includes('hyd') || s.includes('hyderabad')) return 'HYD';
    if (s.includes('del') || s.includes('delhi')) return 'DEL';
    if (s.includes('bom') || s.includes('mumbai')) return 'BOM';
    if (s.includes('blr') || s.includes('bengaluru') || s.includes('bangalore')) return 'BLR';
    if (s.includes('maa') || s.includes('chennai')) return 'MAA';
    if (s.includes('ccu') || s.includes('kolkata')) return 'CCU';
    if (s.includes('goi') || s.includes('goa')) return 'GOI';
    if (s.includes('pnq') || s.includes('pune')) return 'PNQ';
    if (s.includes('jai') || s.includes('jaipur')) return 'JAI';
    return s.toUpperCase().slice(0, 3);
  }

  // =========================================================
  // 7. AGENTIC ORCHESTRATION PIPELINE (processUserRequest)
  // =========================================================

  async function processUserRequest(userText, onStatusUpdate = null) {
    const updateStatus = (text) => {
      if (typeof onStatusUpdate === 'function') {
        onStatusUpdate(typeof text === 'object' ? text : { message: text, step: text });
      }
    };

    updateStatus('🧠 Understanding user intent & route context...');
    await new Promise(r => setTimeout(r, 180));

    const parsed = parseUserQuery(userText);

    // Apply Natural Language Priority Override if present (Step 6 & 7)
    if (parsed.priorityOverride) {
      updateStatus('👤 Adjusting real-time preference weights...');
      if (parsed.priorityOverride === 'comfort') {
        sessionMemory.currentPreferenceWeights.comfortImportance = 0.95;
        sessionMemory.currentPreferenceWeights.priceImportance = 0.10;
        sessionMemory.currentPreferenceWeights.priority = 'comfort';
      } else if (parsed.priorityOverride === 'cheapest') {
        sessionMemory.currentPreferenceWeights.priceImportance = 0.95;
        sessionMemory.currentPreferenceWeights.comfortImportance = 0.10;
        sessionMemory.currentPreferenceWeights.priority = 'cheapest';
      } else if (parsed.priorityOverride === 'fastest') {
        sessionMemory.currentPreferenceWeights.speedImportance = 0.95;
        sessionMemory.currentPreferenceWeights.priority = 'fastest';
      } else if (parsed.priorityOverride === 'reliability') {
        sessionMemory.currentPreferenceWeights.reliabilityImportance = 0.95;
        sessionMemory.currentPreferenceWeights.priority = 'reliability';
      }
      aiSessionMetrics.preferenceChanges++;
      await new Promise(r => setTimeout(r, 150));
    }

    // 1. Reset / Start Over
    if (parsed.isStartOver) {
      sessionMemory.bookingDraft = null;
      sessionMemory.confirmedBooking = null;
      sessionMemory.currentPreferenceWeights = { ...currentProfile.preferences };
      updateStatus('✓ Reset session memory');
      return {
        reply: `Session context reset. How can I help you with your flights today?`,
        actionType: 'RESET_SESSION'
      };
    }

    // 2. Cancellation
    if (parsed.isCancel) {
      sessionMemory.bookingDraft = null;
      updateStatus('✓ Action cancelled');
      return {
        reply: `Understood, I've cancelled the current action. Let me know what you'd like to do next.`,
        actionType: 'CANCELLED'
      };
    }

    // 3. History Toggle Actions
    if (parsed.action === 'IGNORE_HISTORY') {
      sessionMemory.historyUsageEnabled = false;
      currentProfile.preferences.useHistory = false;
      updateStatus('✓ Personalization history paused');
      return {
        reply: `**Personalization History Paused.**\n\nI will now evaluate flights using **only your explicit search constraints** and objective AirfareX criteria. Past demo booking patterns are currently ignored.`,
        actionType: 'HISTORY_TOGGLED'
      };
    }

    if (parsed.action === 'USE_HISTORY') {
      sessionMemory.historyUsageEnabled = true;
      currentProfile.preferences.useHistory = true;
      updateStatus('✓ Personalization history activated');
      return {
        reply: `**Personalization History Activated.**\n\nI am now analyzing past booking habits from **${currentProfile.name} (${currentProfile.history.length} demo trips)** to calculate your **Personal Match Scores**.`,
        actionType: 'HISTORY_TOGGLED'
      };
    }

    // 4. Search / Route Change Intent
    if (parsed.action === 'SEARCH' || parsed.origin || parsed.destination) {
      updateStatus('🔎 Searching verified domestic flights...');
      await new Promise(r => setTimeout(r, 200));

      const flights = AgentTools.searchFlights({
        origin: parsed.origin || sessionMemory.currentRoute.origin,
        destination: parsed.destination || sessionMemory.currentRoute.destination,
        maxPrice: parsed.budget,
        stops: parsed.stops,
        timeOfDay: parsed.timeOfDay,
        airline: parsed.airline
      });

      updateStatus('⭐ Calculating AirfareX and Personal Match scores...');
      await new Promise(r => setTimeout(r, 180));

      updateStatus('🎯 Finding the best match for you...');
      const rec = AgentTools.getRecommendations(flights);
      await new Promise(r => setTimeout(r, 120));

      updateStatus('✓ Recommendation ready');

      const orig = sessionMemory.currentRoute.origin;
      const dest = sessionMemory.currentRoute.destination;
      const best = rec.bestForMe;

      if (!best) {
        return {
          reply: `I couldn't find any flights matching all constraints for **${orig} ➔ ${dest}**.\n\nWould you like to relax budget limits or allow connecting stops?`,
          actionType: 'EMPTY_RESULTS'
        };
      }

      const replyHtml = formatFlightRecommendationMarkdown(rec, orig, dest);
      return {
        reply: replyHtml,
        answer: replyHtml,
        recommendedFlight: best,
        alternativeFlight: rec.bestOverall,
        recommendations: rec,
        matchResult: { matchScore: best.personalMatchScore || 96 },
        actionType: 'FLIGHT_RECOMMENDATION',
        steps: [
          { tool: 'searchFlights', step: 'Search Flights', detail: `Found ${flights.length} flights for ${orig} ➔ ${dest}` },
          { tool: 'calculatePersonalMatch', step: 'Calculate Personal Match', detail: `Evaluated flights against ${currentProfile.name}'s profile` },
          { tool: 'getBestForCustomer', step: 'Select Recommendation', detail: `Recommended ${best.airline} ${best.flightNumber || best.flight_no}` }
        ]
      };
    }

    // 5. Explain Score / Change Intent
    if (parsed.action === 'EXPLAIN') {
      updateStatus('⭐ Analyzing score decomposition...');
      await new Promise(r => setTimeout(r, 180));
      updateStatus('✓ Explanation ready');

      const activeFlight = sessionMemory.selectedFlight || sessionMemory.currentRecommendation || AgentTools.getBestForCustomer();
      const altFlight = AgentTools.getBestOverallFlight();
      const exp = AgentTools.explainScore(activeFlight, altFlight);

      const reply = `### 💡 Score & Decision Breakdown for ${exp.airline} ${exp.flightNumber}\n\n` +
        `• **AirfareX Objective Quality:** \`${exp.airfarexScore}/100\`\n` +
        `• **Your Personal Match Score:** \`${exp.personalMatchScore}/100\`\n\n` +
        `**Key Alignment Factors:**\n` +
        exp.reasons.map(r => `• ${r}`).join('\n') +
        (exp.diffVerdict ? `\n\n> 💡 *${exp.diffVerdict}*` : '');

      return {
        reply: reply,
        answer: reply,
        flight: activeFlight,
        recommendedFlight: activeFlight,
        explanation: exp,
        actionType: 'EXPLANATION'
      };
    }

    // 6. Personalized Recommendation ("What is best for me?" / priority override)
    if (parsed.action === 'RECOMMEND_FOR_ME' || parsed.priorityOverride) {
      updateStatus('⭐ Evaluating personal match against candidate flights...');
      await new Promise(r => setTimeout(r, 180));

      const rec = AgentTools.getRecommendations();
      const best = rec.bestForMe;
      const alt = rec.bestOverall;

      updateStatus('✓ Personalized match calculated');

      const exp = AgentTools.explainScore(best, alt);
      const reply = `### 🎯 Best Match for ${currentProfile.name} (${currentProfile.tag})\n\n` +
        `I recommend **${best.airline} ${best.flightNumber || best.flight_no}** (${best.origin} ➔ ${best.destination}):\n\n` +
        `• **Fare:** ₹${(best.totalPrice || best.total_fare).toLocaleString('en-IN')}\n` +
        `• **Schedule:** ${best.departureTime} – ${best.arrivalTime} (${best.duration}, ${best.stops})\n` +
        `• **Personal Match:** \`${exp.personalMatchScore}/100\` ⭐\n` +
        `• **AirfareX Score:** \`${exp.airfarexScore}/100\`\n\n` +
        `**Why it matches your profile:**\n` +
        exp.reasons.map(r => `• ${r}`).join('\n') +
        (exp.diffVerdict ? `\n\n> 💡 *${exp.diffVerdict}*` : '');

      return {
        reply: reply,
        answer: reply,
        flight: best,
        recommendedFlight: best,
        alternativeFlight: alt,
        recommendations: rec,
        matchResult: { matchScore: exp.personalMatchScore },
        actionType: 'PERSONALIZED_MATCH'
      };
    }

    // 7. Best Overall ("Which is best overall?")
    if (parsed.action === 'RECOMMEND_BEST_OVERALL') {
      updateStatus('⭐ Finding highest general AirfareX score...');
      const best = AgentTools.getBestOverallFlight();
      updateStatus('✓ Best overall identified');

      if (!best) return { reply: "Please search for a route first (e.g. 'Flights from Hyderabad to Delhi')." };

      sessionMemory.selectedFlight = best;

      const reply = `### 👑 Highest Rated Flight (AirfareX Benchmark)\n\n` +
        `**${best.airline} ${best.flightNumber || best.flight_no}** achieves the highest general score across all carriers:\n\n` +
        `• **AirfareX Score:** \`${best.overallScore || 92}/100\` (Price: ${best.priceScore}/100, Reliability: ${best.reliabilityScore}/100, Punctuality: ${best.punctualityScore}/100, Comfort: ${best.comfortScore}/100)\n` +
        `• **Fare:** ₹${(best.totalPrice || best.total_fare).toLocaleString('en-IN')}\n` +
        `• **Schedule:** ${best.departureTime} ➔ ${best.arrivalTime} (${best.duration}, ${best.stops})\n` +
        `• **Personal Match:** \`${calculatePersonalMatch(best)}/100\` for ${currentProfile.name}`;

      return {
        reply: reply,
        answer: reply,
        flight: best,
        recommendedFlight: best,
        actionType: 'BEST_OVERALL'
      };
    }

    // 8. Find Cheapest
    if (parsed.action === 'FIND_CHEAPEST') {
      updateStatus('💸 Identifying lowest price option...');
      const cheapest = AgentTools.getCheapestFlight();
      updateStatus('✓ Lowest price found');

      if (!cheapest) return { reply: "Please specify an origin and destination (e.g. 'Cheapest flight to Mumbai')." };

      sessionMemory.selectedFlight = cheapest;

      const reply = `### 💸 Lowest Fare Option\n\n` +
        `**${cheapest.airline} ${cheapest.flightNumber || cheapest.flight_no}** is the most economical flight available:\n\n` +
        `• **Total Fare:** **₹${(cheapest.totalPrice || cheapest.total_fare).toLocaleString('en-IN')}**\n` +
        `• **Schedule:** ${cheapest.departureTime} – ${cheapest.arrivalTime} (${cheapest.duration}, ${cheapest.stops})\n` +
        `• **AirfareX Score:** \`${cheapest.overallScore || 85}/100\` · **Personal Match:** \`${calculatePersonalMatch(cheapest)}/100\``;

      return {
        reply: reply,
        answer: reply,
        flight: cheapest,
        recommendedFlight: cheapest,
        actionType: 'CHEAPEST'
      };
    }

    // 9. Find Fastest
    if (parsed.action === 'FIND_FASTEST') {
      updateStatus('⚡ Calculating shortest travel times...');
      const fastest = AgentTools.getFastestFlight();
      updateStatus('✓ Fastest flight identified');

      if (!fastest) return { reply: "Please specify a flight sector first." };

      sessionMemory.selectedFlight = fastest;

      const reply = `### ⚡ Fastest Sector Flight\n\n` +
        `**${fastest.airline} ${fastest.flightNumber || fastest.flight_no}** offers the shortest flight duration:\n\n` +
        `• **Duration:** **${fastest.duration}** (${fastest.stops})\n` +
        `• **Schedule:** ${fastest.departureTime} – ${fastest.arrivalTime}\n` +
        `• **Total Fare:** ₹${(fastest.totalPrice || fastest.total_fare).toLocaleString('en-IN')}\n` +
        `• **Punctuality Rating:** ${fastest.punctualityScore || fastest.onTimePercentage || 94}% on-time`;

      return {
        reply: reply,
        answer: reply,
        flight: fastest,
        recommendedFlight: fastest,
        actionType: 'FASTEST'
      };
    }

    // 10. Find Most Reliable
    if (parsed.action === 'FIND_RELIABLE') {
      updateStatus('🛡️ Checking DGCA on-time records...');
      const reliable = AgentTools.getMostReliableFlight();
      updateStatus('✓ Punctuality leader selected');

      if (!reliable) return { reply: "Please search for a route first." };

      sessionMemory.selectedFlight = reliable;

      const reply = `### 🛡️ Punctuality & Reliability Leader\n\n` +
        `**${reliable.airline} ${reliable.flightNumber || reliable.flight_no}** ranks highest for operational consistency:\n\n` +
        `• **Historical On-Time Rate:** **${reliable.punctualityScore || reliable.onTimePercentage || 96}%**\n` +
        `• **Fleet Reliability Score:** \`${reliable.reliabilityScore || 95}/100\`\n` +
        `• **Schedule:** ${reliable.departureTime} – ${reliable.arrivalTime} (${reliable.duration})\n` +
        `• **Fare:** ₹${(reliable.totalPrice || reliable.total_fare).toLocaleString('en-IN')}`;

      return {
        reply: reply,
        answer: reply,
        flight: reliable,
        recommendedFlight: reliable,
        actionType: 'RELIABLE'
      };
    }

    // 11. Compare Flights Intent
    if (parsed.action === 'COMPARE') {
      updateStatus('📊 Generating side-by-side comparison matrix...');
      const count = parsed.compareCount || 2;
      const compRows = AgentTools.compareFlights().slice(0, count);
      updateStatus('✓ Comparison ready');

      const tableMd = formatComparisonTableMarkdown(compRows);
      return {
        reply: tableMd,
        answer: tableMd,
        actionType: 'COMPARISON',
        comparisonRows: compRows
      };
    }

    // 12. Initiate Booking ("Book it")
    if (parsed.action === 'INITIATE_BOOKING') {
      updateStatus('✈️ Preparing demo booking draft...');
      const draft = AgentTools.createDemoBooking();
      updateStatus('✓ Booking draft ready for confirmation');

      const reply = `### 📋 Confirm Demo Flight Booking\n\n` +
        `I have prepared an assisted booking for **${draft.travelerName}**:\n\n` +
        `• **Flight:** **${draft.airline} ${draft.flightNo}**\n` +
        `• **Sector:** ${draft.origin} ➔ ${draft.destination} · 📅 ${draft.travelDate}\n` +
        `• **Total Payable:** **₹${Number(draft.fare).toLocaleString('en-IN')}** (Demo Sandbox)\n` +
        `• **Allocated Seat:** **Seat ${draft.allocatedSeat}**\n\n` +
        `Shall I confirm this booking? Say **"Yes"** or click Confirm.`;

      return {
        reply: reply,
        answer: reply,
        actionType: 'BOOKING_PROMPT',
        bookingDraft: draft
      };
    }

    // 13. Confirm Booking ("Yes")
    if (parsed.action === 'CONFIRM_BOOKING') {
      updateStatus('🔒 Authorizing demo booking in cryptographic sandbox...');
      await new Promise(r => setTimeout(r, 250));

      const confirmed = AgentTools.confirmDemoBooking();
      updateStatus('🎉 Ticket issued!');

      const reply = `### 🎉 Demo Booking Confirmed!\n\n` +
        `Your demo booking is confirmed with reference **\`${confirmed.bookingRef}\`**.\n\n` +
        `• **Passenger:** **${confirmed.travelerName}**\n` +
        `• **PNR:** **\`${confirmed.pnr}\`**\n` +
        `• **Flight:** **${confirmed.airline} ${confirmed.flightNo}** (${confirmed.origin} ➔ ${confirmed.destination})\n` +
        `• **Allocated Seat:** **${confirmed.allocatedSeat}**\n` +
        `• **Total Paid:** **₹${Number(confirmed.fare).toLocaleString('en-IN')}**\n\n` +
        `*Your demo booking is ready for confirmation.*`;

      return {
        reply: reply,
        answer: reply,
        actionType: 'BOOKING_CONFIRMED',
        booking: {
          bookingReference: confirmed.bookingRef,
          passengerName: confirmed.travelerName,
          flight: confirmed.flight || {
            airline: confirmed.airline,
            flightNumber: confirmed.flightNo,
            origin: confirmed.origin,
            destination: confirmed.destination,
            totalPrice: confirmed.fare
          }
        },
        confirmedBooking: confirmed
      };
    }

    // 14. Default Travel Planning Fallback
    updateStatus('💡 Evaluating journey options...');
    const defRec = AgentTools.getRecommendations();
    updateStatus('✓ Ready');

    if (defRec && defRec.bestForMe) {
      const b = defRec.bestForMe;
      return {
        reply: `Namaste! As your **Personal Travel Advisor** for **${currentProfile.name}**, I'm monitoring **${sessionMemory.currentRoute.origin} ➔ ${sessionMemory.currentRoute.destination}**.\n\n` +
          `Your highest match right now is **${b.airline} ${b.flightNumber || b.flight_no}** with a **${b.personalMatchScore || 94}/100 Personal Match** (₹${(b.totalPrice || b.total_fare).toLocaleString('en-IN')}).\n\n` +
          `Try asking:\n` +
          `• *"Why is this flight best for me?"*\n` +
          `• *"Compare the top 2 flights"*\n` +
          `• *"This time comfort is more important than price"*\n` +
          `• *"Book it"*`,
        answer: `Namaste! How can I help you customize your flight today?`,
        actionType: 'GENERAL_ASSIST'
      };
    }

    return {
      reply: `I can help you search, compare, and personalize flights across all major Indian airlines. Try asking:\n• *"Find flights from Hyderabad to Delhi"* \n• *"Which is cheapest?"* \n• *"What's best for me?"*`,
      answer: `I can help you search, compare, and personalize flights across all major Indian airlines.`,
      actionType: 'HELP'
    };
  }

  // =========================================================
  // 8. MARKDOWN FORMATTERS
  // =========================================================

  function formatFlightRecommendationMarkdown(rec, orig, dest) {
    const best = rec.bestForMe;
    const exp = rec.explanation;

    return `### ✈️ Recommended for ${currentProfile.name}: **${best.airline} ${best.flightNumber || best.flight_no}**\n\n` +
      `**Sector:** ${orig} ➔ ${dest} · **${best.departureTime} – ${best.arrivalTime}** (${best.duration}, ${best.stops})\n\n` +
      `• **Total Price:** **₹${(best.totalPrice || best.total_fare).toLocaleString('en-IN')}**\n` +
      `• **🎯 Your Personal Match:** \`${exp.personalMatchScore}/100\` *(Personalized fit)*\n` +
      `• **⭐ AirfareX General Score:** \`${exp.airfarexScore}/100\` *(Aviation benchmark)*\n\n` +
      `**Decision Factors:**\n` +
      exp.reasons.map(r => `• ${r}`).join('\n') +
      (exp.diffVerdict ? `\n\n> 💡 *${exp.diffVerdict}*` : '');
  }

  function formatComparisonTableMarkdown(rows) {
    let header = `### ⚖️ Side-by-Side Comparison Matrix\n\n` +
      `| Carrier & Flight | Fare | Duration | Stops | AirfareX | Match Score | Key Highlight |\n` +
      `| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n`;

    const body = rows.map((r, i) => {
      const isWinner = i === 0 || r.personalMatch >= 92;
      return `| **${r.airline} ${r.flightNo}** | ₹${Number(r.price).toLocaleString('en-IN')} | ${r.duration} | ${r.stops} | \`${r.airfarexScore}/100\` | **\`${r.personalMatch}/100\`** | ${isWinner ? '👑 Best Match' : (r.priceScore >= 92 ? '💸 Lowest Fare' : '⭐ Solid Choice')} |`;
    }).join('\n');

    const footer = `\n\n> 💡 *Recommendation: **${rows[0].airline} ${rows[0].flightNo}** achieves the highest match under your current preferences.*`;
    return header + body + footer;
  }

  // =========================================================
  // 9. PROFILE SWITCHER & CONTROLLER
  // =========================================================

  function setActiveProfile(profileIdOrKey) {
    let key = 'budget';
    if (profileIdOrKey === 'DEMO-1001' || profileIdOrKey === 'budget') key = 'budget';
    else if (profileIdOrKey === 'DEMO-1002' || profileIdOrKey === 'comfort') key = 'comfort';
    else if (profileIdOrKey === 'DEMO-1003' || profileIdOrKey === 'time_critical') key = 'time_critical';
    else if (DEMO_CUSTOMER_PROFILES[profileIdOrKey]) key = profileIdOrKey;

    activeProfileKey = key;
    currentProfile = JSON.parse(JSON.stringify(DEMO_CUSTOMER_PROFILES[key]));
    sessionMemory.currentPreferenceWeights = { ...currentProfile.preferences };
    sessionMemory.historicalPreferenceProfile = analyzeTravelHistory(currentProfile.history);

    if (sessionMemory.currentCandidates.length > 0) {
      sessionMemory.currentCandidates = sessionMemory.currentCandidates.map(f => ({
        ...f,
        personalMatchScore: calculatePersonalMatch(f),
        personal_match: calculatePersonalMatch(f)
      }));
    }

    console.log(`[AirfareX Agent] Active profile switched to: ${currentProfile.name} (${currentProfile.tag})`);
    return { ...currentProfile };
  }

  const switchProfile = setActiveProfile;

  // =========================================================
  // 10. LIVE BROWSER-NATIVE VOICE AI SYSTEM (Step 12–18)
  // =========================================================

  let recognitionInstance = null;
  let isListening = false;
  let isMuted = false;
  let currentVoiceState = '🎙️ Ready';
  let voiceStateListeners = [];
  let voiceTranscriptListeners = [];

  const SpeechRecognitionClass = typeof window !== 'undefined' ? (window.SpeechRecognition || window.webkitSpeechRecognition || null) : null;
  const isSpeechSupported = !!SpeechRecognitionClass;
  const isSynthesisSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  function setVoiceState(stateName) {
    currentVoiceState = stateName;
    voiceStateListeners.forEach(cb => {
      try { cb(stateName); } catch (e) { console.error(e); }
    });
  }

  function initSpeechRecognition() {
    if (!SpeechRecognitionClass) return null;
    if (recognitionInstance) return recognitionInstance;

    try {
      const rec = new SpeechRecognitionClass();
      rec.continuous = false;
      rec.interimResults = true;
      rec.lang = 'en-IN';

      rec.onstart = () => {
        isListening = true;
        setVoiceState('🔴 Listening...');
      };

      rec.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }

        voiceTranscriptListeners.forEach(cb => {
          try { cb(transcript, event.results[event.results.length - 1].isFinal); } catch (e) {}
        });

        if (event.results[0].isFinal) {
          handleVoiceInput(transcript);
        }
      };

      rec.onerror = (event) => {
        console.warn('[AirfareX Voice] Recognition error:', event.error);
        isListening = false;
        setVoiceState('🎙️ Ready');
      };

      rec.onend = () => {
        isListening = false;
        if (currentVoiceState === '🔴 Listening...') {
          setVoiceState('🎙️ Ready');
        }
      };

      recognitionInstance = rec;
      return rec;
    } catch (err) {
      console.warn('[AirfareX Voice] Init error:', err);
      return null;
    }
  }

  async function handleVoiceInput(transcript) {
    if (!transcript || !transcript.trim()) {
      setVoiceState('🎙️ Ready');
      return;
    }

    // Step 17: Voice interruption — stop previous speech synthesis immediately
    stopSpeaking();

    setVoiceState('🧠 Understanding...');
    await new Promise(r => setTimeout(r, 120));

    setVoiceState('🔎 Searching...');
    const result = await processUserRequest(transcript, (step) => {
      const msg = typeof step === 'object' ? (step.message || step.step) : step;
      if (msg.includes('AirfareX') || msg.includes('Personal Match')) setVoiceState('📊 Analyzing...');
    });

    setVoiceState('💬 Responding...');

    // Extract clean plain text for TTS
    let spokenText = (result.answer || result.reply || '')
      .replace(/###/g, '')
      .replace(/##/g, '')
      .replace(/\*\*/g, '')
      .replace(/`/g, '')
      .replace(/>/g, '')
      .replace(/•/g, '')
      .replace(/<[^>]*>/g, '')
      .replace(/\n+/g, '. ')
      .trim();

    // Summarize for natural conversational voice if too long
    if (result.actionType === 'SEARCH' || result.actionType === 'FLIGHT_RECOMMENDATION') {
      const f = result.recommendedFlight;
      spokenText = `I found flights for ${sessionMemory.currentRoute.origin} to ${sessionMemory.currentRoute.destination}. I recommend ${f.airline} flight ${f.flightNumber || f.flight_no} at ₹${Number(f.totalPrice || f.total_fare).toLocaleString('en-IN')}, with a ${f.personalMatchScore || 96}% Personal Match.`;
    } else if (result.actionType === 'BOOKING_PROMPT') {
      spokenText = `I can prepare the demo booking for that flight. Shall I continue?`;
    } else if (result.actionType === 'BOOKING_CONFIRMED') {
      spokenText = `Your demo booking is ready for confirmation. Ticket confirmed with reference ${result.confirmedBooking?.bookingRef || 'TRV-AI'}.`;
    }

    speakResponse(spokenText, () => {
      setVoiceState('✓ Ready');
    });

    // Notify app UI if listener present
    if (typeof window.onAiVoiceResponse === 'function') {
      window.onAiVoiceResponse(result, transcript, spokenText);
    }
  }

  function startVoiceListening() {
    // Interruption check
    stopSpeaking();

    const rec = initSpeechRecognition();
    if (!rec) {
      setVoiceState('🎙️ Ready');
      return false;
    }

    try {
      rec.start();
      return true;
    } catch (err) {
      console.warn('[AirfareX Voice] Start failed:', err);
      return false;
    }
  }

  function stopVoiceListening() {
    if (recognitionInstance && isListening) {
      try { recognitionInstance.stop(); } catch (e) {}
    }
    isListening = false;
    setVoiceState('🎙️ Ready');
  }

  function speakResponse(text, onEnd = null) {
    if (!isSynthesisSupported || isMuted || !text) {
      if (typeof onEnd === 'function') onEnd();
      return;
    }

    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.lang = 'en-IN';

      utterance.onend = () => {
        if (typeof onEnd === 'function') onEnd();
      };
      utterance.onerror = () => {
        if (typeof onEnd === 'function') onEnd();
      };

      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('[AirfareX Voice] Speech synthesis error:', e);
      if (typeof onEnd === 'function') onEnd();
    }
  }

  function stopSpeaking() {
    if (isSynthesisSupported) {
      try { window.speechSynthesis.cancel(); } catch (e) {}
    }
  }

  // =========================================================
  // 11. CENTRAL AGENT INSTANCE (window.AirfareXAgent)
  // =========================================================

  window.AirfareXAgent = {
    // Step 3 Core Methods
    processUserRequest: processUserRequest,
    getState: () => ({
      activeProfileKey: activeProfileKey,
      activeProfile: { ...currentProfile },
      currentProfile: { ...currentProfile },
      sessionMemory: { ...sessionMemory },
      sessionMetrics: { ...aiSessionMetrics },
      isListening: isListening,
      isMuted: isMuted,
      voiceState: currentVoiceState,
      voiceSupported: isSpeechSupported
    }),
    resetSession: () => {
      sessionMemory.currentCandidates = [];
      sessionMemory.selectedFlight = null;
      sessionMemory.bookingDraft = null;
      sessionMemory.confirmedBooking = null;
      sessionMemory.currentPreferenceWeights = { ...currentProfile.preferences };
      sessionMemory.historyUsageEnabled = true;
      sessionMemory.conversationHistory = [];
      return { success: true, message: "Session memory reset." };
    },
    executeTool: (toolName, args = null) => {
      if (typeof AgentTools[toolName] === 'function') {
        try {
          return AgentTools[toolName](args);
        } catch (err) {
          return { error: `Failed to execute tool '${toolName}': ${err.message}` };
        }
      }
      return { error: `Tool '${toolName}' is not registered in AirfareXAgent.tools.` };
    },
    getCustomerProfile: AgentTools.getCustomerProfile,
    analyzeTravelHistory: analyzeTravelHistory,
    calculatePersonalMatch: calculatePersonalMatch,
    calculatePersonalizedMatch: calculatePersonalMatch,

    // Step 10 Tool Registry
    tools: AgentTools,

    // Profile & Preferences
    setActiveProfile: setActiveProfile,
    switchProfile: switchProfile,
    get activeProfile() {
      return currentProfile;
    },
    getActiveProfile: () => ({ ...currentProfile, key: activeProfileKey }),
    getAllProfiles: () => DEMO_CUSTOMER_PROFILES,
    get profiles() {
      return DEMO_CUSTOMER_PROFILES;
    },
    getSessionMetrics: () => ({ ...aiSessionMetrics }),
    getSessionMemory: () => ({ ...sessionMemory }),
    parseQuery: parseUserQuery,

    // Step 12-18 Voice APIs
    startVoiceListening: startVoiceListening,
    stopVoiceListening: stopVoiceListening,
    speakResponse: speakResponse,
    stopSpeaking: stopSpeaking,
    isVoiceSupported: () => isSpeechSupported,
    getVoiceState: () => currentVoiceState,
    setVoiceMuted: (muted) => { isMuted = !!muted; },
    isVoiceMuted: () => isMuted,
    onVoiceStateChange: (cb) => { if (typeof cb === 'function') voiceStateListeners.push(cb); },
    onVoiceTranscript: (cb) => { if (typeof cb === 'function') voiceTranscriptListeners.push(cb); }
  };

  console.log('[AirfareX AI Agent] Central Agentic AI Travel Advisor & Live Voice Engine initialized.');
})();
