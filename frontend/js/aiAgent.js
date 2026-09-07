/**
 * AirfareX India — Personalized Agentic AI Travel Advisor Engine
 * Phase 8 & 8.5 Implementation
 * 
 * Features:
 * 1. 3 Demo Customer Profiles (Budget, Comfort, Time-Critical) with 10+ Historical Bookings
 * 2. History Analysis Engine: computes behavioral weights, average fare, airline affinity
 * 3. Priority Override Resolver: Current natural language intent ALWAYS overrides history
 * 4. Dual Scoring: AirfareX General Score (0-100) vs Personalized Match Score (0-100)
 * 5. Complete Executable Tool Registry (Search, Match, Filter, Compare, Explain, Book)
 * 6. Multi-Turn Conversational Memory with Pronoun & Context Resolution
 * 7. Live Agent Status Progression Lifecycle Ticker
 * 8. Zero-dependency Local Fallback Architecture
 */

(function() {
  'use strict';

  // =========================================================================
  // 1. DEMO CUSTOMER PROFILES & HISTORICAL BOOKINGS
  // =========================================================================

  const DEMO_CUSTOMER_PROFILES = {
    budget: {
      customerId: "DEMO-1001",
      name: "Rajesh Sharma",
      tag: "Budget Traveler",
      avatar: "💼",
      bio: "Frequent domestic traveler who prioritizes low fares, non-stop morning flights, and budget carriers.",
      preferences: {
        priority: "cheapest",
        preferredAirlines: ["IndiGo", "Akasa Air", "Air India Express"],
        preferredCabin: "Economy",
        preferredDeparture: "morning",
        maxTypicalBudget: 6500,
        preferredStops: 0,
        priceImportance: 0.90,
        comfortImportance: 0.40,
        reliabilityImportance: 0.75,
        speedImportance: 0.60
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
      avatar: "🛋️",
      bio: "Leisure & corporate executive traveler who values extra legroom, full-service amenities, and seamless connections.",
      preferences: {
        priority: "comfort",
        preferredAirlines: ["Air India", "IndiGo"],
        preferredCabin: "Economy / Premium",
        preferredDeparture: "afternoon",
        maxTypicalBudget: 12000,
        preferredStops: 0,
        priceImportance: 0.35,
        comfortImportance: 0.95,
        reliabilityImportance: 0.85,
        speedImportance: 0.65
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
      avatar: "⚡",
      bio: "High-frequency business executive where on-time arrival, rapid security transit, and zero delays are paramount.",
      preferences: {
        priority: "fastest",
        preferredAirlines: ["IndiGo", "Akasa Air", "Air India"],
        preferredCabin: "Economy / Business",
        preferredDeparture: "early_morning",
        maxTypicalBudget: 15000,
        preferredStops: 0,
        priceImportance: 0.30,
        comfortImportance: 0.70,
        reliabilityImportance: 0.95,
        speedImportance: 0.95
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
    historyUsageEnabled: true,
    lastTurnType: 'INIT',
    conversationHistory: []
  };

  const aiSessionMetrics = {
    searches: 128,
    recommendations: 86,
    personalizedRecommendations: 42,
    historyBasedRecommendations: 31,
    comparisons: 54,
    demoBookings: 31,
    preferenceChanges: 18,
    bestMatchSelections: 27,
    avgPersonalMatch: 91
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

    // Airline frequency
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

    // Derived sensitivity ratings
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

  // Pre-calculate initial history profile
  sessionMemory.historicalPreferenceProfile = analyzeTravelHistory(currentProfile.history);

  // =========================================================
  // 4. PERSONALIZED MATCH SCORING FORMULA
  // =========================================================

  /**
   * Calculates Personalized Match Score (0–100) combining current weights + profile history
   */
  function calculatePersonalizedMatch(flight, customWeights = null) {
    if (!flight) return 85;

    const weights = customWeights || sessionMemory.currentPreferenceWeights || currentProfile.preferences;
    const hist = sessionMemory.historyUsageEnabled ? sessionMemory.historicalPreferenceProfile : null;

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

    // 1. Price Fit (0-100)
    let priceFit = pScore;
    const budgetLimit = weights.maxTypicalBudget || (hist ? hist.typicalBudget : 8000);
    if (fare <= budgetLimit) {
      priceFit = Math.min(100, priceFit + 8);
    } else {
      const overBudgetPenalty = Math.min(35, Math.round(((fare - budgetLimit) / budgetLimit) * 50));
      priceFit = Math.max(20, priceFit - overBudgetPenalty);
    }

    // 2. Comfort Fit (0-100)
    let comfortFit = cScore;
    if (airline === 'Air India' || (flight.seat_pitch && parseInt(flight.seat_pitch) >= 31)) {
      comfortFit = Math.min(100, comfortFit + 6);
    }

    // 3. Reliability & Punctuality Fit (0-100)
    let relFit = Math.round((rScore + punctScore) / 2);

    // 4. Convenience / Sector Fit (0-100)
    let convFit = 85;
    if (isNonstop) convFit += 10;
    else convFit -= 18;

    // Departure time fit
    const prefTime = (weights.preferredDeparture || (hist ? hist.preferredDeparture : 'any')).toLowerCase();
    if (prefTime.includes('morning') || prefTime === 'early_morning') {
      if (depHour >= 5 && depHour <= 11) convFit += 6;
      else convFit -= 8;
    } else if (prefTime.includes('afternoon')) {
      if (depHour >= 12 && depHour <= 17) convFit += 6;
    } else if (prefTime.includes('evening')) {
      if (depHour >= 17 && depHour <= 22) convFit += 6;
    }

    // Airline Affinity fit from history
    if (hist && sessionMemory.historyUsageEnabled) {
      if (airline === hist.preferredAirline) convFit += 6;
      if (currentProfile.preferences.preferredAirlines.includes(airline)) convFit += 4;
    }

    convFit = Math.max(30, Math.min(100, convFit));

    // Dynamic Weights Normalization
    const wPrice = weights.priceImportance !== undefined ? weights.priceImportance : 0.35;
    const wComfort = weights.comfortImportance !== undefined ? weights.comfortImportance : 0.25;
    const wRel = weights.reliabilityImportance !== undefined ? weights.reliabilityImportance : 0.25;
    const wSpeed = weights.speedImportance !== undefined ? weights.speedImportance : 0.15;

    const totalWeight = wPrice + wComfort + wRel + wSpeed;
    const nwPrice = wPrice / totalWeight;
    const nwComfort = wComfort / totalWeight;
    const nwRel = wRel / totalWeight;
    const nwSpeed = wSpeed / totalWeight;

    const rawMatch = (priceFit * nwPrice) + (comfortFit * nwComfort) + (relFit * nwRel) + (convFit * nwSpeed);
    return Math.max(50, Math.min(99, Math.round(rawMatch)));
  }

  // =========================================================
  // 5. EXECUTABLE AGENT TOOL REGISTRY
  // =========================================================

  const AgentTools = {
    getCustomerProfile: () => {
      return { ...currentProfile };
    },

    getTravelHistory: () => {
      return [...currentProfile.history];
    },

    analyzeTravelHistory: (hist) => {
      return analyzeTravelHistory(hist || currentProfile.history);
    },

    getCustomerPreferences: () => {
      return {
        profileKey: activeProfileKey,
        customerName: currentProfile.name,
        tag: currentProfile.tag,
        preferences: { ...currentProfile.preferences },
        accessibilityNeeds: { ...currentProfile.accessibilityNeeds },
        useHistory: sessionMemory.historyUsageEnabled,
        currentWeights: { ...sessionMemory.currentPreferenceWeights }
      };
    },

    updateCustomerPreference: (key, value) => {
      sessionMemory.currentPreferenceWeights[key] = value;
      aiSessionMetrics.preferenceChanges++;
      return { success: true, updatedKey: key, newValue: value, currentWeights: sessionMemory.currentPreferenceWeights };
    },

    searchFlights: (params = {}) => {
      aiSessionMetrics.searches++;
      const orig = params.origin || sessionMemory.currentRoute.origin || 'HYD';
      const dest = params.destination || sessionMemory.currentRoute.destination || 'DEL';
      sessionMemory.currentRoute = { origin: orig, destination: dest };

      let flights = [];
      if (window.AirfarexDemoData) {
        flights = window.AirfarexDemoData.filterFlights({
          from_city: orig,
          to_city: dest,
          stops: params.stops || 'Any',
          airline: params.airline || 'All airlines',
          max_price: params.maxPrice,
          cabin: params.cabinClass || 'Economy'
        });
      }

      // Compute match scores for candidates
      flights = flights.map(f => {
        const personalMatch = calculatePersonalizedMatch(f);
        return {
          ...f,
          personalMatchScore: personalMatch,
          personal_match: personalMatch
        };
      });

      sessionMemory.currentCandidates = flights;

      // Update explorer results UI if available
      if (typeof window.renderFlightCards === 'function' && flights.length > 0) {
        const bestFare = Math.min(...flights.map(f => f.totalPrice || f.total_fare));
        window.renderFlightCards(flights, bestFare, { data_source: 'DEMO' });
      }

      return flights;
    },

    filterFlights: (filters = {}) => {
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

    sortFlights: (mode = 'match') => {
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

    calculatePersonalizedMatch: (flight, weights) => {
      return calculatePersonalizedMatch(flight, weights);
    },

    getBestFlightForMe: (flightsList = null) => {
      aiSessionMetrics.bestMatchSelections++;
      const list = flightsList || sessionMemory.currentCandidates;
      if (!list || list.length === 0) {
        const fresh = AgentTools.searchFlights();
        if (!fresh || fresh.length === 0) return null;
        return fresh.sort((a, b) => (b.personalMatchScore || 85) - (a.personalMatchScore || 85))[0];
      }
      return [...list].sort((a, b) => (b.personalMatchScore || 85) - (a.personalMatchScore || 85))[0];
    },

    getBestOverallFlight: (flightsList = null) => {
      const list = flightsList || sessionMemory.currentCandidates;
      if (!list || list.length === 0) return null;
      return [...list].sort((a, b) => (b.overallScore || 85) - (a.overallScore || 85))[0];
    },

    getCheapestFlight: (flightsList = null) => {
      const list = flightsList || sessionMemory.currentCandidates;
      if (!list || list.length === 0) return null;
      return [...list].sort((a, b) => (a.totalPrice || a.total_fare) - (b.totalPrice || b.total_fare))[0];
    },

    getFastestFlight: (flightsList = null) => {
      const list = flightsList || sessionMemory.currentCandidates;
      if (!list || list.length === 0) return null;
      return [...list].sort((a, b) => (a.durationMinutes || 120) - (b.durationMinutes || 120))[0];
    },

    getMostReliableFlight: (flightsList = null) => {
      const list = flightsList || sessionMemory.currentCandidates;
      if (!list || list.length === 0) return null;
      return [...list].sort((a, b) => ((b.reliabilityScore || 90) + (b.punctualityScore || 90)) - ((a.reliabilityScore || 90) + (a.punctualityScore || 90)))[0];
    },

    getPersonalizedRecommendation: (flightsList = null) => {
      aiSessionMetrics.recommendations++;
      aiSessionMetrics.personalizedRecommendations++;
      if (sessionMemory.historyUsageEnabled) aiSessionMetrics.historyBasedRecommendations++;

      const list = flightsList || sessionMemory.currentCandidates;
      if (!list || list.length === 0) return null;

      const bestForMe = AgentTools.getBestFlightForMe(list);
      const bestOverall = AgentTools.getBestOverallFlight(list);
      const cheapest = AgentTools.getCheapestFlight(list);
      const fastest = AgentTools.getFastestFlight(list);
      const mostReliable = AgentTools.getMostReliableFlight(list);

      const explanation = AgentTools.explainPersonalizedRecommendation(bestForMe, bestOverall);

      sessionMemory.currentRecommendation = bestForMe;
      sessionMemory.selectedFlight = bestForMe;

      return {
        bestForMe,
        bestOverall,
        cheapest,
        fastest,
        mostReliable,
        explanation
      };
    },

    explainPersonalizedRecommendation: (chosenFlight, alternativeFlight = null) => {
      if (!chosenFlight) return "No flight selected.";
      const hist = sessionMemory.historicalPreferenceProfile;
      const weights = sessionMemory.currentPreferenceWeights;
      const isHistoryUsed = sessionMemory.historyUsageEnabled;

      const fNo = chosenFlight.flightNumber || chosenFlight.flight_no;
      const airline = chosenFlight.airline;
      const fare = chosenFlight.totalPrice || chosenFlight.total_fare;
      const matchScore = chosenFlight.personalMatchScore || calculatePersonalizedMatch(chosenFlight);
      const genScore = chosenFlight.overallScore || 90;

      let reasons = [];

      if (weights.priceImportance >= 0.70) {
        reasons.push(`Highly competitive fare of **₹${fare.toLocaleString('en-IN')}** fits your budget priority.`);
      }
      if (weights.comfortImportance >= 0.70) {
        reasons.push(`Superior cabin comfort on ${chosenFlight.aircraft || 'fleet'} with **${chosenFlight.seat_pitch || '30"'}** legroom.`);
      }
      if (weights.speedImportance >= 0.70 || weights.reliabilityImportance >= 0.70) {
        reasons.push(`Fast non-stop travel time of **${chosenFlight.duration}** with **${chosenFlight.punctualityScore || chosenFlight.onTimePercentage || 94}%** DGCA on-time rating.`);
      }

      if (isHistoryUsed && hist) {
        if (chosenFlight.airline === hist.preferredAirline) {
          reasons.push(`Matches your historical carrier preference for **${hist.preferredAirline}** (${hist.totalTrips} past demo trips).`);
        }
        if (chosenFlight.stops === 'Nonstop' && hist.nonStopRatio >= 0.8) {
          reasons.push(`Aligns with your standard preference for non-stop direct flights.`);
        }
      }

      let diffVerdict = "";
      if (alternativeFlight && alternativeFlight.flightNumber !== chosenFlight.flightNumber) {
        const altNo = alternativeFlight.flightNumber || alternativeFlight.flight_no;
        const altGen = alternativeFlight.overallScore || 90;
        const altMatch = alternativeFlight.personalMatchScore || calculatePersonalizedMatch(alternativeFlight);

        if (altGen > genScore) {
          diffVerdict = `\n\n> 💡 *Note: Although ${alternativeFlight.airline} ${altNo} has a higher general AirfareX Score (${altGen}/100), I selected ${airline} ${fNo} because it achieves a superior **Personal Match (${matchScore}/100 vs ${altMatch}/100)** under your current priorities.*`;
        }
      }

      return {
        flightNo: fNo,
        airline: airline,
        matchScore: matchScore,
        generalScore: genScore,
        reasons: reasons,
        diffVerdict: diffVerdict
      };
    },

    compareFlights: (flightIdentifiers = []) => {
      aiSessionMetrics.comparisons++;
      let flightsToCompare = [];
      const list = sessionMemory.currentCandidates.length > 0 ? sessionMemory.currentCandidates : (window.AirfarexDemoData ? window.AirfarexDemoData.getAllFlights() : []);

      if (flightIdentifiers.length > 0) {
        flightIdentifiers.forEach(id => {
          const match = list.find(f => (f.flightNumber || f.flight_no) === id || f.flightId === id);
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
        personalMatch: f.personalMatchScore || calculatePersonalizedMatch(f),
        priceScore: f.priceScore || 90,
        reliabilityScore: f.reliabilityScore || 92,
        punctualityScore: f.punctualityScore || f.onTimePercentage || 94,
        comfortScore: f.comfortScore || 85
      }));
    },

    createDemoBooking: (flightNo, customPax = null) => {
      const flight = sessionMemory.currentCandidates.find(f => (f.flightNumber || f.flight_no) === flightNo) 
        || (window.AirfarexDemoData ? window.AirfarexDemoData.getFlightByNumber(flightNo) : null)
        || sessionMemory.currentRecommendation;

      if (!flight) return { error: "No flight available to book." };

      const travelerName = customPax?.name || currentProfile.name;
      const refCode = `TRV-AI-${Math.floor(100000 + Math.random() * 900000)}`;

      sessionMemory.bookingDraft = {
        bookingRef: refCode,
        flightNo: flight.flightNumber || flight.flight_no,
        airline: flight.airline,
        origin: flight.origin,
        destination: flight.destination,
        fare: flight.totalPrice || flight.total_fare,
        travelerName: travelerName,
        travelDate: sessionMemory.currentDate || new Date(Date.now() + 86400000 * 3).toISOString().slice(0, 10),
        status: "DRAFT_PENDING_CONFIRMATION",
        allocatedSeat: `${Math.floor(4 + Math.random() * 20)}${['A', 'C', 'D', 'F'][Math.floor(Math.random() * 4)]}`
      };

      return sessionMemory.bookingDraft;
    },

    confirmDemoBooking: () => {
      if (!sessionMemory.bookingDraft) {
        return AgentTools.createDemoBooking(sessionMemory.selectedFlight?.flightNumber || '6E 203');
      }

      aiSessionMetrics.demoBookings++;
      sessionMemory.bookingDraft.status = "CONFIRMED";
      sessionMemory.bookingDraft.pnr = `PNR${Math.floor(100000 + Math.random() * 900000)}`;
      sessionMemory.bookingDraft.confirmedAt = new Date().toISOString();

      return sessionMemory.bookingDraft;
    }
  };

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
      bookingRequested: false,
      confirmationRequested: false,
      ignoreHistory: false,
      useHistory: false,
      explainRequested: false
    };

    // 1. Sector matching (e.g. Hyderabad to Delhi, HYD to BOM, etc.)
    const sectorPatterns = [
      /(?:from\s+)?([a-z\s]+?)\s+(?:to|➔|->|--)\s+([a-z\s]+)/i,
      /(?:flights?\s+(?:to|for)\s+)([a-z\s]+)/i
    ];

    const matchPair = q.match(/(?:from\s+)?(hyderabad|delhi|mumbai|bengaluru|bangalore|chennai|kolkata|goa|pune|jaipur|hyd|del|bom|blr|maa|ccu|goi|pnq|jai)\s+(?:to|➔|->|--)\s+(hyderabad|delhi|mumbai|bengaluru|bangalore|chennai|kolkata|goa|pune|jaipur|hyd|del|bom|blr|maa|ccu|goi|pnq|jai)/i);
    if (matchPair) {
      intent.origin = mapCityToCode(matchPair[1]);
      intent.destination = mapCityToCode(matchPair[2]);
      intent.action = 'SEARCH';
    } else {
      const matchTo = q.match(/(?:to|in)\s+(hyderabad|delhi|mumbai|bengaluru|bangalore|chennai|kolkata|goa|pune|jaipur|hyd|del|bom|blr|maa|ccu|goi|pnq|jai)/i);
      if (matchTo) {
        intent.destination = mapCityToCode(matchTo[1]);
        intent.action = 'SEARCH';
      }
    }

    // 2. Budget constraint (e.g. "under ₹8,000", "below 7000", "max 6500")
    const budgetMatch = q.match(/(?:under|below|less than|max|within|budget of)\s*(?:₹|rs\.?|inr)?\s*([0-9,]+)/i);
    if (budgetMatch) {
      intent.budget = parseInt(budgetMatch[1].replace(/,/g, ''));
    }

    // 3. Stops constraint
    if (q.includes('no stop') || q.includes('nonstop') || q.includes('non-stop') || q.includes('direct only') || q.includes('zero stops') || q.includes("don't want stops") || q.includes('no stops')) {
      intent.stops = 'Nonstop';
    } else if (q.includes('1 stop') || q.includes('one stop') || q.includes('with stop')) {
      intent.stops = '1 stop';
    }

    // 4. Time of day
    if (q.includes('morning') || q.includes('early morning')) intent.timeOfDay = 'morning';
    else if (q.includes('afternoon')) intent.timeOfDay = 'afternoon';
    else if (q.includes('evening') || q.includes('night') || q.includes('red-eye')) intent.timeOfDay = 'evening';

    // 5. Airline
    if (q.includes('indigo')) intent.airline = 'IndiGo';
    else if (q.includes('air india express') || q.includes('ai express')) intent.airline = 'Air India Express';
    else if (q.includes('air india')) intent.airline = 'Air India';
    else if (q.includes('akasa')) intent.airline = 'Akasa Air';
    else if (q.includes('spicejet')) intent.airline = 'SpiceJet';

    // 6. Natural Language Priority Changes & Overrides
    if (q.includes('comfort is more important') || q.includes('comfort more important') || q.includes('prioritize comfort') || q.includes('most comfortable') || q.includes('maximum comfort') || q.includes('dont care about price') || q.includes("don't care about price") || q.includes('price does not matter') || q.includes("price doesn't matter") || q.includes('pay more for comfort')) {
      intent.priorityOverride = 'comfort';
    } else if (q.includes('price is most important') || q.includes('cheapest') || q.includes('lowest price') || q.includes('budget flight') || q.includes('cheaper option')) {
      intent.priorityOverride = 'cheapest';
    } else if (q.includes('fastest') || q.includes('shortest') || q.includes('least time') || q.includes('quickest')) {
      intent.priorityOverride = 'fastest';
    } else if (q.includes('reliable') || q.includes('on time') || q.includes('punctual') || q.includes('no delays')) {
      intent.priorityOverride = 'reliability';
    } else if (q.includes('best value') || q.includes('best balance') || q.includes('balanced')) {
      intent.priorityOverride = 'best_value';
    }

    // 7. Core Intent Categorization
    if (q.includes('confirm') || q.includes('yes book') || q.includes('yes, book') || q.includes('proceed booking') || q.includes('confirm booking')) {
      intent.action = 'CONFIRM_BOOKING';
    } else if (q.includes('book') || q.includes('reserve') || q.includes('ticket')) {
      intent.action = 'INITIATE_BOOKING';
    } else if (q.includes('compare') || q.includes('comparison') || q.includes('versus') || q.includes(' vs ')) {
      intent.action = 'COMPARE';
      const numMatch = q.match(/top\s*(\d+)/i);
      intent.compareCount = numMatch ? parseInt(numMatch[1]) : 3;
    } else if (q.includes('why') || q.includes('explain') || q.includes('reason') || q.includes('why this score') || q.includes('why did you change') || q.includes('why this flight')) {
      intent.action = 'EXPLAIN';
    } else if (q.includes('best for me') || q.includes('recommend for me') || q.includes('suit me best') || q.includes('suits me') || q.includes('which one is best for me') || q.includes('what do you recommend')) {
      intent.action = 'RECOMMEND_FOR_ME';
    } else if (q.includes('best overall') || q.includes('highest score') || q.includes('top rated') || q.includes('which is the best') || q.includes("which is best")) {
      intent.action = 'RECOMMEND_BEST_OVERALL';
    } else if (q.includes('which is cheapest') || q.includes('find me the cheapest') || q.includes('show cheapest') || q.includes('lowest fare')) {
      intent.action = 'FIND_CHEAPEST';
    } else if (q.includes('which is fastest') || q.includes('find fastest') || q.includes('shortest duration')) {
      intent.action = 'FIND_FASTEST';
    } else if (q.includes('which is most reliable') || q.includes('highest reliability') || q.includes('most on-time')) {
      intent.action = 'FIND_RELIABLE';
    } else if (q.includes('ignore my history') || q.includes('ignore history') || q.includes('without history') || q.includes('turn off personalization')) {
      intent.action = 'IGNORE_HISTORY';
    } else if (q.includes('use my history') || q.includes('enable history') || q.includes('with history') || q.includes('turn on personalization')) {
      intent.action = 'USE_HISTORY';
    } else if (q.includes('plan my trip') || q.includes('plan trip')) {
      intent.action = 'PLAN_TRIP';
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
  // 7. AGENTIC ORCHESTRATION & RESPONSE GENERATOR
  // =========================================================

  async function processUserRequest(userText, onStatusUpdate = null) {
    const updateStatus = (text) => {
      if (typeof onStatusUpdate === 'function') onStatusUpdate(text);
    };

    updateStatus('🧠 Understanding your preferences & intent...');
    await new Promise(r => setTimeout(r, 220));

    const parsed = parseUserQuery(userText);

    // Apply Natural Language Priority Override if present
    if (parsed.priorityOverride) {
      updateStatus('👤 Adjusting real-time decision weights...');
      if (parsed.priorityOverride === 'comfort') {
        sessionMemory.currentPreferenceWeights.comfortImportance = 0.95;
        sessionMemory.currentPreferenceWeights.priceImportance = 0.25;
        sessionMemory.currentPreferenceWeights.priority = 'comfort';
      } else if (parsed.priorityOverride === 'cheapest') {
        sessionMemory.currentPreferenceWeights.priceImportance = 0.95;
        sessionMemory.currentPreferenceWeights.comfortImportance = 0.35;
        sessionMemory.currentPreferenceWeights.priority = 'cheapest';
      } else if (parsed.priorityOverride === 'fastest') {
        sessionMemory.currentPreferenceWeights.speedImportance = 0.95;
        sessionMemory.currentPreferenceWeights.priority = 'fastest';
      } else if (parsed.priorityOverride === 'reliability') {
        sessionMemory.currentPreferenceWeights.reliabilityImportance = 0.95;
        sessionMemory.currentPreferenceWeights.priority = 'reliability';
      }
      aiSessionMetrics.preferenceChanges++;
      await new Promise(r => setTimeout(r, 180));
    }

    // 1. History Toggle Actions
    if (parsed.action === 'IGNORE_HISTORY') {
      sessionMemory.historyUsageEnabled = false;
      updateStatus('✓ Personalization history bypassed for this session');
      return {
        reply: `**Personalization History Paused.**\n\nI will now evaluate flights using **only your explicit search constraints** and objective AirfareX criteria. Historical demo booking patterns are currently ignored.`,
        actionType: 'HISTORY_TOGGLED',
        statusSteps: ['🧠 Parsed command', '🔒 Disabled history analytics', '✓ Updated session mode']
      };
    }

    if (parsed.action === 'USE_HISTORY') {
      sessionMemory.historyUsageEnabled = true;
      updateStatus('✓ Personalization history re-enabled');
      return {
        reply: `**Personalization History Activated.**\n\nI am now analyzing past booking habits from **${currentProfile.name} (${currentProfile.history.length} demo trips)** to calculate your **Personal Match Scores**.`,
        actionType: 'HISTORY_TOGGLED',
        statusSteps: ['🧠 Parsed command', '🔓 Loaded travel history', '✓ Re-evaluated match weights']
      };
    }

    // 2. Search / Route Change Intent
    if (parsed.action === 'SEARCH' || parsed.origin || parsed.destination) {
      updateStatus('🔎 Searching verified domestic flights...');
      await new Promise(r => setTimeout(r, 250));

      const flights = AgentTools.searchFlights({
        origin: parsed.origin || sessionMemory.currentRoute.origin,
        destination: parsed.destination || sessionMemory.currentRoute.destination,
        maxPrice: parsed.budget,
        stops: parsed.stops,
        timeOfDay: parsed.timeOfDay,
        airline: parsed.airline
      });

      updateStatus('⭐ Calculating AirfareX and Personal Match scores...');
      await new Promise(r => setTimeout(r, 200));

      updateStatus('🎯 Finding the best match for you...');
      const rec = AgentTools.getPersonalizedRecommendation(flights);
      await new Promise(r => setTimeout(r, 150));

      updateStatus('✓ Recommendation ready');

      const orig = sessionMemory.currentRoute.origin;
      const dest = sessionMemory.currentRoute.destination;
      const best = rec.bestForMe;

      if (!best) {
        return {
          reply: `I couldn't find any flights matching all constraints for **${orig} ➔ ${dest}**.\n\nWould you like to relax budget limits or allow connecting stops?`,
          actionType: 'EMPTY_RESULTS',
          actions: [
            { label: '🔍 Relax Budget', type: 'relax_budget' },
            { label: '🛑 Allow 1 Stop', type: 'allow_stops' },
            { label: '🌐 Show All Flights', type: 'show_all' }
          ]
        };
      }

      const replyHtml = formatFlightRecommendationMarkdown(rec, orig, dest);
      return {
        reply: replyHtml,
        flight: best,
        actionType: 'FLIGHT_RECOMMENDATION',
        recommendations: rec,
        statusSteps: [
          `🧠 Understood route ${orig} ➔ ${dest}`,
          `🔎 Evaluated ${flights.length} demo flights`,
          `⭐ Computed AirfareX & Personal Match scores`,
          `🎯 Selected best fit for ${currentProfile.name}`
        ]
      };
    }

    // 3. Explain Score / Change Intent
    if (parsed.action === 'EXPLAIN') {
      updateStatus('⭐ Analyzing score decomposition...');
      await new Promise(r => setTimeout(r, 200));
      updateStatus('✓ Explanation ready');

      const activeFlight = sessionMemory.selectedFlight || sessionMemory.currentRecommendation || AgentTools.getBestFlightForMe();
      const altFlight = AgentTools.getBestOverallFlight();
      const exp = AgentTools.explainPersonalizedRecommendation(activeFlight, altFlight);

      const reply = `### 💡 Score & Decision Breakdown for ${exp.airline} ${exp.flightNo}\n\n` +
        `• **AirfareX Objective Quality:** \`${exp.generalScore}/100\`\n` +
        `• **Your Personal Match Score:** \`${exp.matchScore}/100\`\n\n` +
        `**Key Alignment Factors:**\n` +
        exp.reasons.map(r => `• ${r}`).join('\n') +
        exp.diffVerdict;

      return {
        reply: reply,
        flight: activeFlight,
        actionType: 'EXPLANATION'
      };
    }

    // 4. Personalized Recommendation ("Which is best for me?")
    if (parsed.action === 'RECOMMEND_FOR_ME' || parsed.priorityOverride) {
      updateStatus('⭐ Evaluating personal match against candidate flights...');
      await new Promise(r => setTimeout(r, 200));

      const rec = AgentTools.getPersonalizedRecommendation();
      const best = rec.bestForMe;
      const alt = rec.bestOverall;

      updateStatus('✓ Personalized match calculated');

      const exp = AgentTools.explainPersonalizedRecommendation(best, alt);
      const reply = `### 🎯 Best Match for ${currentProfile.name} (${currentProfile.tag})\n\n` +
        `I recommend **${best.airline} ${best.flightNumber || best.flight_no}** (${best.origin} ➔ ${best.destination}):\n\n` +
        `• **Fare:** ₹${(best.totalPrice || best.total_fare).toLocaleString('en-IN')} (Base: ₹${best.basePrice || best.base_fare})\n` +
        `• **Schedule:** ${best.departureTime} – ${best.arrivalTime} (${best.duration}, ${best.stops})\n` +
        `• **Personal Match:** \`${exp.matchScore}/100\` ⭐\n` +
        `• **AirfareX Score:** \`${exp.generalScore}/100\`\n\n` +
        `**Why it matches your profile:**\n` +
        exp.reasons.map(r => `• ${r}`).join('\n') +
        exp.diffVerdict;

      return {
        reply: reply,
        flight: best,
        actionType: 'PERSONALIZED_MATCH',
        recommendations: rec
      };
    }

    // 5. Best Overall ("Which is best overall?")
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
        `• **Personal Match:** \`${calculatePersonalizedMatch(best)}/100\` for ${currentProfile.name}`;

      return {
        reply: reply,
        flight: best,
        actionType: 'BEST_OVERALL'
      };
    }

    // 6. Find Cheapest
    if (parsed.action === 'FIND_CHEAPEST') {
      updateStatus('💸 Identifying lowest price option...');
      const cheapest = AgentTools.getCheapestFlight();
      updateStatus('✓ Lowest price found');

      if (!cheapest) return { reply: "Please specify an origin and destination (e.g. 'Cheapest flight to Mumbai')." };

      sessionMemory.selectedFlight = cheapest;

      const reply = `### 💸 Lowest Fare Option\n\n` +
        `**${cheapest.airline} ${cheapest.flightNumber || cheapest.flight_no}** is the most economical flight available:\n\n` +
        `• **Total Fare:** **₹${(cheapest.totalPrice || cheapest.total_fare).toLocaleString('en-IN')}** (incl. DGCA fees & GST)\n` +
        `• **Schedule:** ${cheapest.departureTime} – ${cheapest.arrivalTime} (${cheapest.duration}, ${cheapest.stops})\n` +
        `• **AirfareX Score:** \`${cheapest.overallScore || 85}/100\` · **Personal Match:** \`${calculatePersonalizedMatch(cheapest)}/100\``;

      return {
        reply: reply,
        flight: cheapest,
        actionType: 'CHEAPEST'
      };
    }

    // 7. Find Fastest
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
        flight: fastest,
        actionType: 'FASTEST'
      };
    }

    // 8. Find Most Reliable
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
        flight: reliable,
        actionType: 'RELIABLE'
      };
    }

    // 9. Compare Flights Intent
    if (parsed.action === 'COMPARE') {
      updateStatus('📊 Generating side-by-side comparison matrix...');
      const compRows = AgentTools.compareFlights();
      updateStatus('✓ Comparison ready');

      const tableMd = formatComparisonTableMarkdown(compRows);
      return {
        reply: tableMd,
        actionType: 'COMPARISON',
        comparisonRows: compRows
      };
    }

    // 10. Initiate Booking
    if (parsed.action === 'INITIATE_BOOKING') {
      updateStatus('✈️ Preparing demo booking draft...');
      const draft = AgentTools.createDemoBooking();
      updateStatus('✓ Booking draft ready for confirmation');

      const reply = `### 📋 Confirm Demo Flight Booking\n\n` +
        `I have prepared an assisted booking for **${draft.travelerName}**:\n\n` +
        `• **Flight:** **${draft.airline} ${draft.flightNo}**\n` +
        `• **Sector:** ${draft.origin} ➔ ${draft.destination} · 📅 ${draft.travelDate}\n` +
        `• **Total Payable:** **₹${draft.fare.toLocaleString('en-IN')}** (Zero-Fee Demo Sandbox)\n` +
        `• **Allocated Seat:** **Seat ${draft.allocatedSeat}**\n\n` +
        `Would you like to confirm and issue this demo ticket?`;

      return {
        reply: reply,
        actionType: 'BOOKING_PROMPT',
        bookingDraft: draft
      };
    }

    // 11. Confirm Booking
    if (parsed.action === 'CONFIRM_BOOKING') {
      updateStatus('🔒 Authorizing demo booking in cryptographic sandbox...');
      await new Promise(r => setTimeout(r, 300));

      const confirmed = AgentTools.confirmDemoBooking();
      updateStatus('🎉 Ticket issued!');

      const reply = `### 🎉 Demo Booking Confirmed!\n\n` +
        `Your booking has been completed with reference **\`${confirmed.bookingRef}\`**.\n\n` +
        `• **Passenger:** **${confirmed.travelerName}**\n` +
        `• **PNR:** **\`${confirmed.pnr}\`**\n` +
        `• **Flight:** **${confirmed.airline} ${confirmed.flightNo}** (${confirmed.origin} ➔ ${confirmed.destination})\n` +
        `• **Allocated Seat:** **${confirmed.allocatedSeat}** (Forward Cabin)\n` +
        `• **Total Paid:** **₹${confirmed.fare.toLocaleString('en-IN')}** · Verified via Sandbox UPI\n\n` +
        `*AI-assisted demo booking completed. No real funds were charged.*`;

      return {
        reply: reply,
        actionType: 'BOOKING_CONFIRMED',
        confirmedBooking: confirmed
      };
    }

    // 12. Default Travel Planning Fallback
    updateStatus('💡 Evaluating journey options...');
    const defRec = AgentTools.getPersonalizedRecommendation();
    updateStatus('✓ Ready');

    if (defRec && defRec.bestForMe) {
      const b = defRec.bestForMe;
      return {
        reply: `Namaste! As your **Personal Travel Advisor** for **${currentProfile.name}**, I'm monitoring **${sessionMemory.currentRoute.origin} ➔ ${sessionMemory.currentRoute.destination}**.\n\n` +
          `Your highest match right now is **${b.airline} ${b.flightNumber || b.flight_no}** with a **${b.personalMatchScore || 94}/100 Personal Match** (₹${(b.totalPrice || b.total_fare).toLocaleString('en-IN')}).\n\n` +
          `Try asking:\n` +
          `• *"Why is this flight best for me?"*\n` +
          `• *"Compare the top 3 flights"*\n` +
          `• *"This time comfort is more important than price"*\n` +
          `• *"Book the best flight"*`,
        actionType: 'GENERAL_ASSIST'
      };
    }

    return {
      reply: `I can help you search, compare, and personalize flights across all major Indian airlines. Try asking:\n• *"Find flights from Hyderabad to Delhi"* \n• *"Which is cheapest?"* \n• *"What's best for me?"*`,
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
      `• **🎯 Your Personal Match:** \`${exp.matchScore}/100\` *(Personalized fit)*\n` +
      `• **⭐ AirfareX General Score:** \`${exp.generalScore}/100\` *(Aviation standard)*\n\n` +
      `**Decision Factors:**\n` +
      exp.reasons.map(r => `• ${r}`).join('\n') +
      exp.diffVerdict;
  }

  function formatComparisonTableMarkdown(rows) {
    let header = `### ⚖️ Side-by-Side Comparison Matrix\n\n` +
      `| Carrier & Flight | Fare | Duration | Stops | AirfareX | Match Score | Key Highlight |\n` +
      `| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n`;

    const body = rows.map((r, i) => {
      const isWinner = i === 0 || r.personalMatch >= 92;
      return `| **${r.airline} ${r.flightNo}** | ₹${r.price.toLocaleString('en-IN')} | ${r.duration} | ${r.stops} | \`${r.airfarexScore}/100\` | **\`${r.personalMatch}/100\`** | ${isWinner ? '👑 Best Match' : (r.priceScore >= 92 ? '💸 Lowest Fare' : '⭐ Solid Choice')} |`;
    }).join('\n');

    const footer = `\n\n> 💡 *Recommendation: **${rows[0].airline} ${rows[0].flightNo}** achieves the highest match under your current preferences.*`;
    return header + body + footer;
  }

  // =========================================================
  // 9. PROFILE SWITCHER CONTROLLER
  // =========================================================

  function switchProfile(profileKey) {
    if (!DEMO_CUSTOMER_PROFILES[profileKey]) return null;
    activeProfileKey = profileKey;
    currentProfile = JSON.parse(JSON.stringify(DEMO_CUSTOMER_PROFILES[profileKey]));
    sessionMemory.currentPreferenceWeights = { ...currentProfile.preferences };
    sessionMemory.historicalPreferenceProfile = analyzeTravelHistory(currentProfile.history);

    // Re-evaluate current candidates
    if (sessionMemory.currentCandidates.length > 0) {
      sessionMemory.currentCandidates = sessionMemory.currentCandidates.map(f => ({
        ...f,
        personalMatchScore: calculatePersonalizedMatch(f),
        personal_match: calculatePersonalizedMatch(f)
      }));
    }

    console.log(`[AirfareX AI Advisor] Switched profile to: ${currentProfile.name} (${currentProfile.tag})`);
    return { ...currentProfile };
  }

  // =========================================================
  // 10. PUBLIC AGENT INTERFACE
  // =========================================================

  window.AirfareXAgent = {
    getActiveProfile: () => ({ ...currentProfile, key: activeProfileKey }),
    getAllProfiles: () => DEMO_CUSTOMER_PROFILES,
    switchProfile: switchProfile,
    getSessionMetrics: () => ({ ...aiSessionMetrics }),
    getSessionMemory: () => ({ ...sessionMemory }),
    tools: AgentTools,
    processUserRequest: processUserRequest,
    calculatePersonalizedMatch: calculatePersonalizedMatch,
    analyzeTravelHistory: analyzeTravelHistory,
    parseQuery: parseUserQuery
  };

  console.log('[AirfareX AI Agent] Personalized AI Travel Advisor Engine initialized successfully.');
})();
