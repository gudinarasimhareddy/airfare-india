/**
 * AirfareX India — Centralized Master Demo Dataset & Scoring Engine
 * 
 * Provides 26+ realistic Indian domestic flights across major routes and airlines
 * with a transparent, weighted scoring engine, dynamic filtering, sorting,
 * recommendations, and dashboard analytics.
 */

(function () {
  'use strict';

  // Master Raw Flight Inventory (26+ Flights across top Indian routes)
  const RAW_DEMO_FLIGHTS = [
    // =========================================================================
    // 1. HYDERABAD (HYD) ➔ DELHI (DEL)
    // =========================================================================
    {
      flightId: 'FL-6E-502',
      airline: 'IndiGo',
      flightNumber: '6E 502',
      logo: 'indigo',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '07:15',
      arrivalTime: '09:30',
      duration: '2h 15m',
      durationMinutes: 135,
      stops: 'Nonstop',
      aircraft: 'Airbus A321neo',
      cabinClass: 'Economy',
      availableSeats: 14,
      basePrice: 3850,
      taxes: 850,
      totalPrice: 4700,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 94,
      priceScore: 92,
      reliabilityScore: 95,
      punctualityScore: 94,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '12B',
      seat_pitch: '30"',
      emissions_kg: 122,
      recommendation: 'Best Overall'
    },
    {
      flightId: 'FL-AI-542',
      airline: 'Air India',
      flightNumber: 'AI 542',
      logo: 'airindia',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '10:30',
      arrivalTime: '12:50',
      duration: '2h 20m',
      durationMinutes: 140,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 8,
      basePrice: 4300,
      taxes: 850,
      totalPrice: 5150,
      currency: 'INR',
      baggage: '7kg Cabin + 25kg Check-in + Free Hot Meal',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,000 fee thereafter',
      delayProbability: 'Low (7%)',
      onTimePercentage: 91,
      priceScore: 86,
      reliabilityScore: 92,
      punctualityScore: 91,
      comfortScore: 95,
      status: 'On Time',
      terminal: 'T3',
      gate: '24',
      seat_pitch: '32"',
      emissions_kg: 128,
      recommendation: 'Most Comfortable'
    },
    {
      flightId: 'FL-QP-1412',
      airline: 'Akasa Air',
      flightNumber: 'QP 1412',
      logo: 'akasa',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '14:20',
      arrivalTime: '16:40',
      duration: '2h 20m',
      durationMinutes: 140,
      stops: 'Nonstop',
      aircraft: 'Boeing 737 MAX 8',
      cabinClass: 'Economy',
      availableSeats: 19,
      basePrice: 3440,
      taxes: 850,
      totalPrice: 4290,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Low (5%)',
      onTimePercentage: 93,
      priceScore: 98,
      reliabilityScore: 92,
      punctualityScore: 93,
      comfortScore: 89,
      status: 'On Time',
      terminal: 'T1',
      gate: '06',
      seat_pitch: '31"',
      emissions_kg: 115,
      recommendation: 'Lowest Price'
    },
    {
      flightId: 'FL-SG-8192',
      airline: 'SpiceJet',
      flightNumber: 'SG 8192',
      logo: 'spicejet',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '19:45',
      arrivalTime: '22:10',
      duration: '2h 25m',
      durationMinutes: 145,
      stops: 'Nonstop',
      aircraft: 'Boeing 737-800',
      cabinClass: 'Economy',
      availableSeats: 6,
      basePrice: 3600,
      taxes: 850,
      totalPrice: 4450,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Moderate (14%)',
      onTimePercentage: 84,
      priceScore: 94,
      reliabilityScore: 82,
      punctualityScore: 84,
      comfortScore: 80,
      status: 'Scheduled',
      terminal: 'T2',
      gate: '15',
      seat_pitch: '29"',
      emissions_kg: 138,
      recommendation: 'Late Evening Saver'
    },

    // =========================================================================
    // 2. DELHI (DEL) ➔ HYDERABAD (HYD)
    // =========================================================================
    {
      flightId: 'FL-6E-503',
      airline: 'IndiGo',
      flightNumber: '6E 503',
      logo: 'indigo',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'HYD',
      destinationCity: 'Hyderabad',
      departureTime: '06:30',
      arrivalTime: '08:45',
      duration: '2h 15m',
      durationMinutes: 135,
      stops: 'Nonstop',
      aircraft: 'Airbus A321neo',
      cabinClass: 'Economy',
      availableSeats: 12,
      basePrice: 3900,
      taxes: 850,
      totalPrice: 4750,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (3%)',
      onTimePercentage: 96,
      priceScore: 91,
      reliabilityScore: 96,
      punctualityScore: 96,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '14',
      seat_pitch: '30"',
      emissions_kg: 122,
      recommendation: 'Most Reliable'
    },
    {
      flightId: 'FL-AI-543',
      airline: 'Air India',
      flightNumber: 'AI 543',
      logo: 'airindia',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'HYD',
      destinationCity: 'Hyderabad',
      departureTime: '17:15',
      arrivalTime: '19:35',
      duration: '2h 20m',
      durationMinutes: 140,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 10,
      basePrice: 4400,
      taxes: 850,
      totalPrice: 5250,
      currency: 'INR',
      baggage: '7kg Cabin + 25kg Check-in + Free Hot Meal',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,000 fee thereafter',
      delayProbability: 'Low (6%)',
      onTimePercentage: 92,
      priceScore: 85,
      reliabilityScore: 93,
      punctualityScore: 92,
      comfortScore: 95,
      status: 'On Time',
      terminal: 'T3',
      gate: '28',
      seat_pitch: '32"',
      emissions_kg: 128,
      recommendation: 'Full Service Choice'
    },

    // =========================================================================
    // 3. HYDERABAD (HYD) ➔ MUMBAI (BOM)
    // =========================================================================
    {
      flightId: 'FL-6E-344',
      airline: 'IndiGo',
      flightNumber: '6E 344',
      logo: 'indigo',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'BOM',
      destinationCity: 'Mumbai',
      departureTime: '06:00',
      arrivalTime: '07:25',
      duration: '1h 25m',
      durationMinutes: 85,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 22,
      basePrice: 2890,
      taxes: 750,
      totalPrice: 3640,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 95,
      priceScore: 96,
      reliabilityScore: 95,
      punctualityScore: 95,
      comfortScore: 87,
      status: 'On Time',
      terminal: 'T2',
      gate: '08',
      seat_pitch: '30"',
      emissions_kg: 88,
      recommendation: 'Best Value'
    },
    {
      flightId: 'FL-AI-620',
      airline: 'Air India',
      flightNumber: 'AI 620',
      logo: 'airindia',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'BOM',
      destinationCity: 'Mumbai',
      departureTime: '13:10',
      arrivalTime: '14:35',
      duration: '1h 25m',
      durationMinutes: 85,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 15,
      basePrice: 3250,
      taxes: 750,
      totalPrice: 4000,
      currency: 'INR',
      baggage: '7kg Cabin + 25kg Check-in + Snack',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,000 fee thereafter',
      delayProbability: 'Low (6%)',
      onTimePercentage: 91,
      priceScore: 90,
      reliabilityScore: 93,
      punctualityScore: 91,
      comfortScore: 94,
      status: 'On Time',
      terminal: 'T3',
      gate: '21',
      seat_pitch: '32"',
      emissions_kg: 92,
      recommendation: 'Most Comfortable'
    },

    // =========================================================================
    // 4. HYDERABAD (HYD) ➔ BENGALURU (BLR)
    // =========================================================================
    {
      flightId: 'FL-6E-421',
      airline: 'IndiGo',
      flightNumber: '6E 421',
      logo: 'indigo',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'BLR',
      destinationCity: 'Bengaluru',
      departureTime: '08:10',
      arrivalTime: '09:20',
      duration: '1h 10m',
      durationMinutes: 70,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 18,
      basePrice: 2450,
      taxes: 700,
      totalPrice: 3150,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Very Low (3%)',
      onTimePercentage: 96,
      priceScore: 97,
      reliabilityScore: 96,
      punctualityScore: 96,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '04',
      seat_pitch: '30"',
      emissions_kg: 72,
      recommendation: 'Fastest & Best Value'
    },
    {
      flightId: 'FL-IX-712',
      airline: 'Air India Express',
      flightNumber: 'IX 712',
      logo: 'aiexpress',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'BLR',
      destinationCity: 'Bengaluru',
      departureTime: '16:30',
      arrivalTime: '17:45',
      duration: '1h 15m',
      durationMinutes: 75,
      stops: 'Nonstop',
      aircraft: 'Boeing 737 MAX 8',
      cabinClass: 'Economy',
      availableSeats: 25,
      basePrice: 2250,
      taxes: 700,
      totalPrice: 2950,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Low (6%)',
      onTimePercentage: 92,
      priceScore: 99,
      reliabilityScore: 91,
      punctualityScore: 92,
      comfortScore: 87,
      status: 'On Time',
      terminal: 'T1',
      gate: '02',
      seat_pitch: '30"',
      emissions_kg: 70,
      recommendation: 'Lowest Price'
    },

    // =========================================================================
    // 5. BENGALURU (BLR) ➔ DELHI (DEL)
    // =========================================================================
    {
      flightId: 'FL-6E-2131',
      airline: 'IndiGo',
      flightNumber: '6E 2131',
      logo: 'indigo',
      origin: 'BLR',
      originCity: 'Bengaluru',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '07:00',
      arrivalTime: '09:45',
      duration: '2h 45m',
      durationMinutes: 165,
      stops: 'Nonstop',
      aircraft: 'Airbus A321neo',
      cabinClass: 'Economy',
      availableSeats: 16,
      basePrice: 4850,
      taxes: 950,
      totalPrice: 5800,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 94,
      priceScore: 90,
      reliabilityScore: 95,
      punctualityScore: 94,
      comfortScore: 89,
      status: 'On Time',
      terminal: 'T1',
      gate: '18',
      seat_pitch: '30"',
      emissions_kg: 132,
      recommendation: 'Best Overall'
    },
    {
      flightId: 'FL-AI-506',
      airline: 'Air India',
      flightNumber: 'AI 506',
      logo: 'airindia',
      origin: 'BLR',
      originCity: 'Bengaluru',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '10:15',
      arrivalTime: '13:05',
      duration: '2h 50m',
      durationMinutes: 170,
      stops: 'Nonstop',
      aircraft: 'Airbus A350-900',
      cabinClass: 'Economy',
      availableSeats: 28,
      basePrice: 5200,
      taxes: 950,
      totalPrice: 6150,
      currency: 'INR',
      baggage: '7kg Cabin + 25kg Check-in + Free Hot Meal + HD IFE',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,000 fee thereafter',
      delayProbability: 'Low (5%)',
      onTimePercentage: 93,
      priceScore: 85,
      reliabilityScore: 94,
      punctualityScore: 93,
      comfortScore: 98,
      status: 'On Time',
      terminal: 'T2',
      gate: '31',
      seat_pitch: '33"',
      emissions_kg: 125,
      recommendation: 'Flagship Experience'
    },
    {
      flightId: 'FL-QP-1502',
      airline: 'Akasa Air',
      flightNumber: 'QP 1502',
      logo: 'akasa',
      origin: 'BLR',
      originCity: 'Bengaluru',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '14:40',
      arrivalTime: '17:25',
      duration: '2h 45m',
      durationMinutes: 165,
      stops: 'Nonstop',
      aircraft: 'Boeing 737 MAX 8',
      cabinClass: 'Economy',
      availableSeats: 20,
      basePrice: 4450,
      taxes: 950,
      totalPrice: 5400,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Low (5%)',
      onTimePercentage: 93,
      priceScore: 94,
      reliabilityScore: 93,
      punctualityScore: 93,
      comfortScore: 90,
      status: 'On Time',
      terminal: 'T1',
      gate: '07',
      seat_pitch: '31"',
      emissions_kg: 124,
      recommendation: 'Lowest Price'
    },

    // =========================================================
    // 6. MUMBAI (BOM) ➔ DELHI (DEL)
    // =========================================================
    {
      flightId: 'FL-6E-214',
      airline: 'IndiGo',
      flightNumber: '6E 214',
      logo: 'indigo',
      origin: 'BOM',
      originCity: 'Mumbai',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '06:10',
      arrivalTime: '08:20',
      duration: '2h 10m',
      durationMinutes: 130,
      stops: 'Nonstop',
      aircraft: 'Airbus A321neo',
      cabinClass: 'Economy',
      availableSeats: 11,
      basePrice: 3950,
      taxes: 800,
      totalPrice: 4750,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 95,
      priceScore: 91,
      reliabilityScore: 96,
      punctualityScore: 95,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '11',
      seat_pitch: '30"',
      emissions_kg: 118,
      recommendation: 'Popular Business Shuttle'
    },
    {
      flightId: 'FL-AI-864',
      airline: 'Air India',
      flightNumber: 'AI 864',
      logo: 'airindia',
      origin: 'BOM',
      originCity: 'Mumbai',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '09:05',
      arrivalTime: '11:20',
      duration: '2h 15m',
      durationMinutes: 135,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 9,
      basePrice: 4350,
      taxes: 800,
      totalPrice: 5150,
      currency: 'INR',
      baggage: '7kg Cabin + 25kg Check-in + Complimentary Meal',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,000 fee thereafter',
      delayProbability: 'Low (6%)',
      onTimePercentage: 92,
      priceScore: 86,
      reliabilityScore: 93,
      punctualityScore: 92,
      comfortScore: 95,
      status: 'On Time',
      terminal: 'T2',
      gate: '34A',
      seat_pitch: '32"',
      emissions_kg: 126,
      recommendation: 'Most Comfortable'
    },
    {
      flightId: 'FL-QP-1320',
      airline: 'Akasa Air',
      flightNumber: 'QP 1320',
      logo: 'akasa',
      origin: 'BOM',
      originCity: 'Mumbai',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '13:35',
      arrivalTime: '15:45',
      duration: '2h 10m',
      durationMinutes: 130,
      stops: 'Nonstop',
      aircraft: 'Boeing 737 MAX 8',
      cabinClass: 'Economy',
      availableSeats: 17,
      basePrice: 3490,
      taxes: 800,
      totalPrice: 4290,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Low (5%)',
      onTimePercentage: 94,
      priceScore: 97,
      reliabilityScore: 93,
      punctualityScore: 94,
      comfortScore: 89,
      status: 'On Time',
      terminal: 'T1',
      gate: '06',
      seat_pitch: '31"',
      emissions_kg: 114,
      recommendation: 'Lowest Price'
    },

    // =========================================================
    // 7. DELHI (DEL) ➔ MUMBAI (BOM)
    // =========================================================
    {
      flightId: 'FL-6E-215',
      airline: 'IndiGo',
      flightNumber: '6E 215',
      logo: 'indigo',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'BOM',
      destinationCity: 'Mumbai',
      departureTime: '08:00',
      arrivalTime: '10:10',
      duration: '2h 10m',
      durationMinutes: 130,
      stops: 'Nonstop',
      aircraft: 'Airbus A321neo',
      cabinClass: 'Economy',
      availableSeats: 15,
      basePrice: 4050,
      taxes: 800,
      totalPrice: 4850,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 95,
      priceScore: 90,
      reliabilityScore: 96,
      punctualityScore: 95,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '10',
      seat_pitch: '30"',
      emissions_kg: 118,
      recommendation: 'Best Overall'
    },
    {
      flightId: 'FL-SG-8172',
      airline: 'SpiceJet',
      flightNumber: 'SG 8172',
      logo: 'spicejet',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'BOM',
      destinationCity: 'Mumbai',
      departureTime: '17:20',
      arrivalTime: '19:40',
      duration: '2h 20m',
      durationMinutes: 140,
      stops: 'Nonstop',
      aircraft: 'Boeing 737-800',
      cabinClass: 'Economy',
      availableSeats: 7,
      basePrice: 3750,
      taxes: 800,
      totalPrice: 4550,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Moderate (12%)',
      onTimePercentage: 86,
      priceScore: 93,
      reliabilityScore: 84,
      punctualityScore: 86,
      comfortScore: 81,
      status: 'Scheduled',
      terminal: 'T2',
      gate: '15',
      seat_pitch: '29"',
      emissions_kg: 131,
      recommendation: 'Evening Saver'
    },
    {
      flightId: 'FL-IX-192',
      airline: 'Air India Express',
      flightNumber: 'IX 192',
      logo: 'aiexpress',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'BOM',
      destinationCity: 'Mumbai',
      departureTime: '22:15',
      arrivalTime: '00:30',
      duration: '2h 15m',
      durationMinutes: 135,
      stops: 'Nonstop',
      aircraft: 'Boeing 737 MAX 8',
      cabinClass: 'Economy',
      availableSeats: 21,
      basePrice: 3450,
      taxes: 800,
      totalPrice: 4250,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Low (6%)',
      onTimePercentage: 92,
      priceScore: 98,
      reliabilityScore: 91,
      punctualityScore: 92,
      comfortScore: 87,
      status: 'On Time',
      terminal: 'T1',
      gate: '03',
      seat_pitch: '30"',
      emissions_kg: 114,
      recommendation: 'Late Night Saver'
    },

    // =========================================================
    // 8. CHENNAI (MAA) ➔ HYDERABAD (HYD)
    // =========================================================
    {
      flightId: 'FL-6E-718',
      airline: 'IndiGo',
      flightNumber: '6E 718',
      logo: 'indigo',
      origin: 'MAA',
      originCity: 'Chennai',
      destination: 'HYD',
      destinationCity: 'Hyderabad',
      departureTime: '06:45',
      arrivalTime: '07:55',
      duration: '1h 10m',
      durationMinutes: 70,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 19,
      basePrice: 2350,
      taxes: 680,
      totalPrice: 3030,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Very Low (3%)',
      onTimePercentage: 96,
      priceScore: 98,
      reliabilityScore: 96,
      punctualityScore: 96,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T1',
      gate: '05',
      seat_pitch: '30"',
      emissions_kg: 68,
      recommendation: 'Best Overall & Lowest Price'
    },
    {
      flightId: 'FL-AI-572',
      airline: 'Air India',
      flightNumber: 'AI 572',
      logo: 'airindia',
      origin: 'MAA',
      originCity: 'Chennai',
      destination: 'HYD',
      destinationCity: 'Hyderabad',
      departureTime: '15:20',
      arrivalTime: '16:35',
      duration: '1h 15m',
      durationMinutes: 75,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 14,
      basePrice: 2800,
      taxes: 680,
      totalPrice: 3480,
      currency: 'INR',
      baggage: '7kg Cabin + 25kg Check-in + Snack',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,000 fee thereafter',
      delayProbability: 'Low (5%)',
      onTimePercentage: 93,
      priceScore: 92,
      reliabilityScore: 94,
      punctualityScore: 93,
      comfortScore: 95,
      status: 'On Time',
      terminal: 'T1',
      gate: '12',
      seat_pitch: '32"',
      emissions_kg: 72,
      recommendation: 'Most Comfortable'
    },

    // =========================================================
    // 9. HYDERABAD (HYD) ➔ CHENNAI (MAA)
    // =========================================================
    {
      flightId: 'FL-6E-719',
      airline: 'IndiGo',
      flightNumber: '6E 719',
      logo: 'indigo',
      origin: 'HYD',
      originCity: 'Hyderabad',
      destination: 'MAA',
      destinationCity: 'Chennai',
      departureTime: '08:35',
      arrivalTime: '09:45',
      duration: '1h 10m',
      durationMinutes: 70,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 23,
      basePrice: 2390,
      taxes: 680,
      totalPrice: 3070,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 95,
      priceScore: 97,
      reliabilityScore: 95,
      punctualityScore: 95,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '07',
      seat_pitch: '30"',
      emissions_kg: 68,
      recommendation: 'Best Value'
    },

    // =========================================================
    // 10. KOLKATA (CCU) ➔ DELHI (DEL)
    // =========================================================
    {
      flightId: 'FL-6E-825',
      airline: 'IndiGo',
      flightNumber: '6E 825',
      logo: 'indigo',
      origin: 'CCU',
      originCity: 'Kolkata',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '07:45',
      arrivalTime: '10:00',
      duration: '2h 15m',
      durationMinutes: 135,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 15,
      basePrice: 4450,
      taxes: 900,
      totalPrice: 5350,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 94,
      priceScore: 91,
      reliabilityScore: 95,
      punctualityScore: 94,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '20',
      seat_pitch: '30"',
      emissions_kg: 120,
      recommendation: 'Best Overall'
    },
    {
      flightId: 'FL-AI-702',
      airline: 'Air India',
      flightNumber: 'AI 702',
      logo: 'airindia',
      origin: 'CCU',
      originCity: 'Kolkata',
      destination: 'DEL',
      destinationCity: 'Delhi',
      departureTime: '17:15',
      arrivalTime: '19:35',
      duration: '2h 20m',
      durationMinutes: 140,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 11,
      basePrice: 4850,
      taxes: 900,
      totalPrice: 5750,
      currency: 'INR',
      baggage: '7kg Cabin + 25kg Check-in + Complimentary Meal',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,000 fee thereafter',
      delayProbability: 'Low (6%)',
      onTimePercentage: 91,
      priceScore: 86,
      reliabilityScore: 93,
      punctualityScore: 91,
      comfortScore: 95,
      status: 'On Time',
      terminal: 'T3',
      gate: '27',
      seat_pitch: '32"',
      emissions_kg: 125,
      recommendation: 'Most Comfortable'
    },

    // =========================================================
    // 11. DELHI (DEL) ➔ GOA (GOI) & PUNE (PNQ)
    // =========================================================
    {
      flightId: 'FL-6E-331',
      airline: 'IndiGo',
      flightNumber: '6E 331',
      logo: 'indigo',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'GOI',
      destinationCity: 'Goa',
      departureTime: '09:20',
      arrivalTime: '11:55',
      duration: '2h 35m',
      durationMinutes: 155,
      stops: 'Nonstop',
      aircraft: 'Airbus A321neo',
      cabinClass: 'Economy',
      availableSeats: 14,
      basePrice: 4600,
      taxes: 850,
      totalPrice: 5450,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 95,
      priceScore: 92,
      reliabilityScore: 96,
      punctualityScore: 95,
      comfortScore: 89,
      status: 'On Time',
      terminal: 'T2',
      gate: '14',
      seat_pitch: '30"',
      emissions_kg: 130,
      recommendation: 'Beach Holiday Direct'
    },
    {
      flightId: 'FL-QP-1420',
      airline: 'Akasa Air',
      flightNumber: 'QP 1420',
      logo: 'akasa',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'GOI',
      destinationCity: 'Goa',
      departureTime: '14:05',
      arrivalTime: '16:40',
      duration: '2h 35m',
      durationMinutes: 155,
      stops: 'Nonstop',
      aircraft: 'Boeing 737 MAX 8',
      cabinClass: 'Economy',
      availableSeats: 18,
      basePrice: 4250,
      taxes: 850,
      totalPrice: 5100,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,200 fee thereafter',
      delayProbability: 'Low (5%)',
      onTimePercentage: 94,
      priceScore: 96,
      reliabilityScore: 93,
      punctualityScore: 94,
      comfortScore: 90,
      status: 'On Time',
      terminal: 'T1',
      gate: '05',
      seat_pitch: '31"',
      emissions_kg: 125,
      recommendation: 'Lowest Price to Goa'
    },
    {
      flightId: 'FL-6E-261',
      airline: 'IndiGo',
      flightNumber: '6E 261',
      logo: 'indigo',
      origin: 'DEL',
      originCity: 'Delhi',
      destination: 'PNQ',
      destinationCity: 'Pune',
      departureTime: '06:40',
      arrivalTime: '08:45',
      duration: '2h 05m',
      durationMinutes: 125,
      stops: 'Nonstop',
      aircraft: 'Airbus A320neo',
      cabinClass: 'Economy',
      availableSeats: 16,
      basePrice: 3800,
      taxes: 800,
      totalPrice: 4600,
      currency: 'INR',
      baggage: '7kg Cabin + 15kg Check-in',
      bag_fee: 0,
      cancellationPolicy: 'DGCA CAR Sec 3: Free within 24h, ₹2,500 fee thereafter',
      delayProbability: 'Very Low (4%)',
      onTimePercentage: 95,
      priceScore: 93,
      reliabilityScore: 95,
      punctualityScore: 95,
      comfortScore: 88,
      status: 'On Time',
      terminal: 'T2',
      gate: '09',
      seat_pitch: '30"',
      emissions_kg: 112,
      recommendation: 'Early Pune Shuttle'
    }
  ];

  // =========================================================================
  // SCORING ENGINE (Requirement 2 & 3)
  // Transparent Weighted Calculation:
  // Overall = Price * 30% + Reliability * 25% + Punctuality * 25% + Comfort * 20%
  // =========================================================================
  function calculateFlightScores(flight) {
    const pScore = Math.max(0, Math.min(100, Math.round(flight.priceScore || 90)));
    const rScore = Math.max(0, Math.min(100, Math.round(flight.reliabilityScore || 90)));
    const punctScore = Math.max(0, Math.min(100, Math.round(flight.punctualityScore || flight.onTimePercentage || 90)));
    const cScore = Math.max(0, Math.min(100, Math.round(flight.comfortScore || 85)));

    // Weighted Formula
    const overall = Math.round(
      (pScore * 0.30) +
      (rScore * 0.25) +
      (punctScore * 0.25) +
      (cScore * 0.20)
    );

    let rating = 'Average';
    if (overall >= 90) rating = 'Excellent';
    else if (overall >= 80) rating = 'Very Good';
    else if (overall >= 70) rating = 'Good';

    // Detailed Plain-English Reason
    let reason = `Scored ${overall}/100 based on competitive fare (${pScore}/100), ${flight.onTimePercentage || punctScore}% on-time rate (${punctScore}/100), high fleet reliability (${rScore}/100), and ${flight.seat_pitch || '30"'} seat pitch comfort (${cScore}/100).`;

    return {
      priceScore: pScore,
      reliabilityScore: rScore,
      punctualityScore: punctScore,
      comfortScore: cScore,
      overallScore: overall,
      scoreRating: rating,
      scoreReason: reason
    };
  }

  // Pre-process and normalize all demo flights with score metrics & compatibility aliases
  const PROCESSED_DEMO_FLIGHTS = RAW_DEMO_FLIGHTS.map((f, index) => {
    const scores = calculateFlightScores(f);

    // Provide both camelCase & snake_case aliases so existing codebase remains 100% compatible
    return {
      ...f,
      flight_id: f.flightId,
      flight_no: f.flightNumber,
      origin_code: f.origin,
      origin_city: f.originCity,
      destination_code: f.destination,
      destination_city: f.destinationCity,
      dep_time: f.departureTime,
      arr_time: f.arrivalTime,
      base_fare: f.basePrice,
      total_fare: f.totalPrice,
      taxes_fees: f.taxes,
      otp: f.onTimePercentage,
      data_source: 'DEMO',
      seat_pitch_inch: parseInt(f.seat_pitch) || 30,
      cabin: f.cabinClass,
      bag_fee: f.bag_fee || 0,
      // Attached Scores
      ...scores,
      scores: {
        price_score: scores.priceScore,
        reliability_score: scores.reliabilityScore,
        punctuality_score: scores.punctualityScore,
        comfort_score: scores.comfortScore,
        overall_score: scores.overallScore,
        rating: scores.scoreRating,
        reason: scores.scoreReason
      },
      fare_score: scores.overallScore
    };
  });

  // =========================================================================
  // HELPER: EXTRACT AIRPORT CODE
  // =========================================================================
  function extractAirportCode(str) {
    if (!str) return 'HYD';
    const match = str.match(/\(([A-Z]{3})\)/);
    if (match) return match[1];
    const cleaned = str.trim().toUpperCase();
    if (cleaned.length === 3) return cleaned;
    if (cleaned.includes('HYD') || cleaned.includes('HYDERABAD')) return 'HYD';
    if (cleaned.includes('DEL') || cleaned.includes('DELHI')) return 'DEL';
    if (cleaned.includes('BOM') || cleaned.includes('MUMBAI')) return 'BOM';
    if (cleaned.includes('BLR') || cleaned.includes('BENGALURU') || cleaned.includes('BANGALORE')) return 'BLR';
    if (cleaned.includes('MAA') || cleaned.includes('CHENNAI')) return 'MAA';
    if (cleaned.includes('CCU') || cleaned.includes('KOLKATA')) return 'CCU';
    if (cleaned.includes('GOI') || cleaned.includes('GOA')) return 'GOI';
    if (cleaned.includes('PNQ') || cleaned.includes('PUNE')) return 'PNQ';
    if (cleaned.includes('JAI') || cleaned.includes('JAIPUR')) return 'JAI';
    return cleaned.slice(0, 3);
  }

  // =========================================================================
  // FILTERING ENGINE (Requirement 4 & 6)
  // =========================================================================
  function filterDemoFlights(params = {}) {
    let list = [...PROCESSED_DEMO_FLIGHTS];

    const origCode = params.from_city ? extractAirportCode(params.from_city) : null;
    const destCode = params.to_city ? extractAirportCode(params.to_city) : null;

    // Filter by Origin & Destination
    if (origCode && origCode !== 'ANY') {
      list = list.filter(f => f.origin === origCode || f.originCity.toUpperCase() === origCode);
    }
    if (destCode && destCode !== 'ANY') {
      list = list.filter(f => f.destination === destCode || f.destinationCity.toUpperCase() === destCode);
    }

    // Filter by Stops
    if (params.stops && params.stops !== 'Any') {
      if (params.stops.toLowerCase().includes('nonstop') || params.stops.toLowerCase().includes('direct')) {
        list = list.filter(f => f.stops.toLowerCase() === 'nonstop' || f.stops.toLowerCase() === 'direct');
      } else if (params.stops.toLowerCase().includes('1 stop')) {
        list = list.filter(f => f.stops.toLowerCase().includes('1'));
      }
    }

    // Direct only toggle
    if (params.direct_only) {
      list = list.filter(f => f.stops.toLowerCase() === 'nonstop' || f.stops.toLowerCase() === 'direct');
    }

    // Filter by Airline
    if (params.airline && params.airline !== 'All airlines' && params.airline !== 'All' && params.airline !== 'Any') {
      list = list.filter(f => f.airline.toLowerCase() === params.airline.toLowerCase());
    }

    // Filter by Max Price
    if (params.max_price && !isNaN(params.max_price)) {
      const maxP = Number(params.max_price);
      if (maxP > 0) {
        list = list.filter(f => f.totalPrice <= maxP);
      }
    }

    // Filter by Time of Day
    if (params.time_of_day && params.time_of_day !== 'Any time' && params.time_of_day !== 'Any') {
      const tod = params.time_of_day.toLowerCase();
      list = list.filter(f => {
        const hour = parseInt(f.departureTime.split(':')[0], 10);
        if (tod.includes('morning') || tod.includes('06:00') || tod.includes('early')) return hour >= 6 && hour < 12;
        if (tod.includes('afternoon') || tod.includes('12:00')) return hour >= 12 && hour < 18;
        if (tod.includes('evening') || tod.includes('18:00')) return hour >= 18 && hour < 24;
        if (tod.includes('night') || tod.includes('00:00')) return hour >= 0 && hour < 6;
        return true;
      });
    }

    // Filter by Minimum Score
    if (params.min_score && !isNaN(params.min_score)) {
      const minS = Number(params.min_score);
      if (minS > 0) {
        list = list.filter(f => f.overallScore >= minS);
      }
    }

    // Filter by Cabin Class
    if (params.cabin && params.cabin !== 'Any' && !params.cabin.toLowerCase().includes('all')) {
      const cab = params.cabin.toLowerCase();
      list = list.filter(f => f.cabinClass.toLowerCase().includes(cab) || cab.includes(f.cabinClass.toLowerCase()));
    }

    // Apply Sorting
    list = sortDemoFlights(list, params.sort_by || 'score');

    return list;
  }

  // =========================================================================
  // SORTING ENGINE (Requirement 5)
  // =========================================================================
  function sortDemoFlights(flights, sortBy = 'score') {
    const list = [...flights];
    const mode = (sortBy || 'score').toLowerCase();

    switch (mode) {
      case 'price_asc':
      case 'lowest_price':
      case 'price':
        list.sort((a, b) => a.totalPrice - b.totalPrice);
        break;

      case 'highest_score':
      case 'score':
      case 'recommended':
      case 'rec':
        list.sort((a, b) => b.overallScore - a.overallScore || a.totalPrice - b.totalPrice);
        break;

      case 'duration_asc':
      case 'shortest_duration':
      case 'fastest':
      case 'duration':
        list.sort((a, b) => a.durationMinutes - b.durationMinutes || a.totalPrice - b.totalPrice);
        break;

      case 'dep_asc':
      case 'earliest_departure':
      case 'earliest':
      case 'time':
        list.sort((a, b) => a.departureTime.localeCompare(b.departureTime));
        break;

      case 'reliability':
      case 'most_reliable':
      case 'punctuality':
        list.sort((a, b) => (b.reliabilityScore + b.punctualityScore) - (a.reliabilityScore + a.punctualityScore));
        break;

      default:
        list.sort((a, b) => b.overallScore - a.overallScore);
        break;
    }

    return list;
  }

  // =========================================================================
  // DYNAMIC RECOMMENDATIONS GENERATOR (Requirement 10)
  // Generates 4 recommendations from the active flight list
  // =========================================================================
  function getDemoRecommendations(flightList) {
    if (!flightList || flightList.length === 0) return null;

    // 1. Best Overall: Highest overallScore
    const bestOverall = [...flightList].sort((a, b) => b.overallScore - a.overallScore || a.totalPrice - b.totalPrice)[0];

    // 2. Best Price: Lowest totalPrice
    const bestPrice = [...flightList].sort((a, b) => a.totalPrice - b.totalPrice)[0];

    // 3. Most Reliable: Highest reliability + punctuality score
    const mostReliable = [...flightList].sort((a, b) => (b.reliabilityScore + b.punctualityScore) - (a.reliabilityScore + a.punctualityScore))[0];

    // 4. Fastest: Shortest duration
    const fastest = [...flightList].sort((a, b) => a.durationMinutes - b.durationMinutes || a.totalPrice - b.totalPrice)[0];

    return {
      airfarex_pick: bestOverall,
      best_value: bestOverall,
      cheapest: bestPrice,
      fastest: fastest,
      most_reliable: mostReliable,
      scored_flights: flightList.map(f => ({
        flight_no: f.flightNumber,
        badge: f.flightNumber === bestOverall?.flightNumber ? 'BEST OVERALL' :
               (f.flightNumber === bestPrice?.flightNumber ? 'LOWEST PRICE' :
               (f.flightNumber === fastest?.flightNumber ? 'FASTEST' :
               (f.flightNumber === mostReliable?.flightNumber ? 'MOST RELIABLE' : 'VERIFIED VALUE'))),
        scores: f.scores
      }))
    };
  }

  // =========================================================================
  // DASHBOARD & ANALYTICS METRICS GENERATOR (Requirement 9)
  // Dynamic statistics calculated directly from the demo flight dataset
  // =========================================================================
  function getDemoDashboardStats(flights = PROCESSED_DEMO_FLIGHTS) {
    const list = flights && flights.length > 0 ? flights : PROCESSED_DEMO_FLIGHTS;
    const totalFlights = list.length;
    
    const totalPriceSum = list.reduce((sum, f) => sum + f.totalPrice, 0);
    const avgPrice = Math.round(totalPriceSum / totalFlights);

    const totalScoreSum = list.reduce((sum, f) => sum + f.overallScore, 0);
    const avgScore = Math.round(totalScoreSum / totalFlights);

    const totalOtpSum = list.reduce((sum, f) => sum + f.onTimePercentage, 0);
    const avgOtp = Math.round(totalOtpSum / totalFlights);

    const lowestPriceFlight = [...list].sort((a, b) => a.totalPrice - b.totalPrice)[0];
    const bestRatedFlight = [...list].sort((a, b) => b.overallScore - a.overallScore)[0];

    // Airline Distribution
    const airlineCounts = {};
    list.forEach(f => {
      airlineCounts[f.airline] = (airlineCounts[f.airline] || 0) + 1;
    });

    // Sector Fares
    const sectorStats = {};
    list.forEach(f => {
      const key = `${f.origin} ➔ ${f.destination}`;
      if (!sectorStats[key]) {
        sectorStats[key] = { count: 0, minPrice: f.totalPrice, maxPrice: f.totalPrice, sumPrice: 0 };
      }
      sectorStats[key].count += 1;
      sectorStats[key].sumPrice += f.totalPrice;
      if (f.totalPrice < sectorStats[key].minPrice) sectorStats[key].minPrice = f.totalPrice;
      if (f.totalPrice > sectorStats[key].maxPrice) sectorStats[key].maxPrice = f.totalPrice;
    });

    return {
      totalFlights,
      avgPrice,
      avgScore,
      avgOtp,
      lowestPrice: lowestPriceFlight.totalPrice,
      lowestPriceFlight,
      bestRatedScore: bestRatedFlight.overallScore,
      bestRatedFlight,
      airlineCounts,
      sectorStats
    };
  }

  // =========================================================================
  // SINGLE FLIGHT LOOKUP
  // =========================================================================
  function getDemoFlightByNumber(flightNo) {
    if (!flightNo) return null;
    const cleanNo = flightNo.replace(/\s+/g, '').toUpperCase();
    return PROCESSED_DEMO_FLIGHTS.find(f => 
      f.flightNumber.replace(/\s+/g, '').toUpperCase() === cleanNo ||
      f.flightId.replace(/\s+/g, '').toUpperCase() === cleanNo ||
      f.flightNumber.toUpperCase() === flightNo.trim().toUpperCase()
    ) || PROCESSED_DEMO_FLIGHTS[0];
  }

  // =========================================================================
  // EXPOSE GLOBAL DEMO DATA INTERFACE
  // =========================================================================
  window.AirfarexDemoData = {
    getAllFlights: () => [...PROCESSED_DEMO_FLIGHTS],
    getRawFlights: () => [...RAW_DEMO_FLIGHTS],
    filterFlights: filterDemoFlights,
    sortFlights: sortDemoFlights,
    calculateScores: calculateFlightScores,
    getRecommendations: getDemoRecommendations,
    getDashboardStats: getDemoDashboardStats,
    getFlightByNumber: getDemoFlightByNumber,
    extractAirportCode: extractAirportCode
  };

  // Backwards compatibility alias
  window.DEMO_FLIGHTS = PROCESSED_DEMO_FLIGHTS;

  console.log(`[AirfareX Demo] Loaded ${PROCESSED_DEMO_FLIGHTS.length} master demo flights with dynamic score engine.`);
})();
