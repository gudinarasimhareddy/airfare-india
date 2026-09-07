-- ==============================================================================
-- AirfareX India — Complete Supabase PostgreSQL Schema & Real Data Foundation
-- Project: https://thtwkhhccxmkkgwtoleb.supabase.co
--
-- This script configures:
-- 1. Extensions (uuid-ossp, pgcrypto)
-- 2. Master Catalog Tables (airports, airlines, flights, flight_prices, routes)
-- 3. Curated Travel Products (tourist_packages, package_items)
-- 4. Customer & Transaction Tables (profiles, bookings, booking_passengers, payments, refunds)
-- 5. Personalization & Watchlist Tables (saved_flights, price_alerts)
-- 6. Production Row Level Security (RLS) policies
-- 7. High-Performance Query Indexes
-- 8. Verified Development Seed Fixtures (Airports, Airlines, Routes, Packages)
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- 1. MASTER CATALOG: AIRPORTS
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.airports (
    iata_code VARCHAR(3) PRIMARY KEY,
    icao_code VARCHAR(4),
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 2. MASTER CATALOG: AIRLINES
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.airlines (
    iata_code VARCHAR(3) PRIMARY KEY,
    icao_code VARCHAR(4),
    name TEXT NOT NULL,
    callsign TEXT,
    country TEXT NOT NULL DEFAULT 'India',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 3. CUSTOMER PROFILES (Mapped to auth.users or guest IDs)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    gstin VARCHAR(20),
    company_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 4. FLIGHT DEFINITIONS (Static Schedule / Route Specs)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.flights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flight_no VARCHAR(20) NOT NULL,
    airline_code VARCHAR(3) NOT NULL REFERENCES public.airlines(iata_code) ON DELETE RESTRICT,
    airline_name TEXT NOT NULL,
    origin_code VARCHAR(3) NOT NULL REFERENCES public.airports(iata_code) ON DELETE RESTRICT,
    origin_city TEXT NOT NULL,
    destination_code VARCHAR(3) NOT NULL REFERENCES public.airports(iata_code) ON DELETE RESTRICT,
    destination_city TEXT NOT NULL,
    dep_time VARCHAR(10) NOT NULL,
    arr_time VARCHAR(10) NOT NULL,
    duration TEXT NOT NULL,
    duration_mins INTEGER NOT NULL DEFAULT 120,
    stops VARCHAR(20) NOT NULL DEFAULT 'Nonstop',
    aircraft TEXT NOT NULL DEFAULT 'Airbus A320neo',
    terminal VARCHAR(10) DEFAULT 'T2',
    gate VARCHAR(10) DEFAULT 'G1',
    status VARCHAR(30) NOT NULL DEFAULT 'On time',
    provider TEXT NOT NULL DEFAULT 'Direct Carrier Schedule',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 5. FLIGHT PRICES (Separated for Time-Varying Fares)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.flight_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flight_id UUID NOT NULL REFERENCES public.flights(id) ON DELETE CASCADE,
    cabin_class VARCHAR(30) NOT NULL DEFAULT 'Economy',
    base_fare INTEGER NOT NULL CHECK (base_fare >= 0),
    taxes INTEGER NOT NULL CHECK (taxes >= 0),
    total_fare INTEGER NOT NULL CHECK (total_fare > 0),
    bag_fee INTEGER NOT NULL DEFAULT 0 CHECK (bag_fee >= 0),
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    fare_score INTEGER NOT NULL DEFAULT 90 CHECK (fare_score BETWEEN 1 AND 100),
    emissions_kg INTEGER NOT NULL DEFAULT 130,
    tag TEXT DEFAULT 'Standard Fare',
    seats_available INTEGER DEFAULT 40,
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 6. MONITORED ROUTE INTELLIGENCE & TOPOLOGY
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.routes (
    id BIGSERIAL PRIMARY KEY,
    route_code VARCHAR(10) UNIQUE NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    origin_code VARCHAR(3) REFERENCES public.airports(iata_code),
    destination_code VARCHAR(3) REFERENCES public.airports(iata_code),
    index_value NUMERIC(6, 2) NOT NULL,
    change_30d NUMERIC(5, 2) NOT NULL,
    avg_fare INTEGER NOT NULL,
    volatility_score INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 7. TOURIST PACKAGES & HOLIDAY PLANS
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.tourist_packages (
    id VARCHAR(60) PRIMARY KEY,
    destination VARCHAR(3) NOT NULL REFERENCES public.airports(iata_code),
    city_name TEXT NOT NULL,
    package_title TEXT NOT NULL,
    tagline TEXT,
    duration TEXT NOT NULL,
    hero_image TEXT,
    price_without_offers INTEGER NOT NULL CHECK (price_without_offers > 0),
    price_with_offers INTEGER NOT NULL CHECK (price_with_offers > 0),
    savings INTEGER NOT NULL DEFAULT 0,
    discount_pct INTEGER NOT NULL DEFAULT 0,
    applied_promo TEXT,
    flight_info JSONB,
    hotel_info JSONB,
    inclusions JSONB,
    exclusions JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.package_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id VARCHAR(60) NOT NULL REFERENCES public.tourist_packages(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL,
    day_label VARCHAR(30) NOT NULL,
    title TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 8. BOOKINGS & PASSENGERS (Phase 5: Full Booking Architecture)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id VARCHAR(60) UNIQUE NOT NULL,
    booking_reference VARCHAR(20) UNIQUE,
    user_id UUID REFERENCES public.profiles(id),
    booking_type VARCHAR(20) NOT NULL DEFAULT 'flight' CHECK (booking_type IN ('flight', 'package')),
    pnr VARCHAR(20) UNIQUE,
    eticket_number VARCHAR(30) UNIQUE,
    voucher_id VARCHAR(30),
    airline TEXT,
    flight_no TEXT,
    sector TEXT,
    origin_code VARCHAR(3) REFERENCES public.airports(iata_code),
    destination_code VARCHAR(3) REFERENCES public.airports(iata_code),
    provider TEXT DEFAULT 'MockDevelopmentProvider',
    data_source TEXT DEFAULT 'DEVELOPMENT' CHECK (data_source IN ('DEVELOPMENT', 'CACHE', 'LIVE')),
    package_id VARCHAR(60) REFERENCES public.tourist_packages(id),
    traveler_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    travel_date DATE NOT NULL,
    pax_count INTEGER NOT NULL DEFAULT 1 CHECK (pax_count >= 1),
    seat_number VARCHAR(10),
    gate VARCHAR(10),
    terminal VARCHAR(10),
    base_fare INTEGER NOT NULL DEFAULT 0,
    taxes INTEGER NOT NULL DEFAULT 0,
    fees INTEGER NOT NULL DEFAULT 0,
    total_amount INTEGER NOT NULL CHECK (total_amount > 0),
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    booking_status VARCHAR(30) NOT NULL DEFAULT 'PENDING_PAYMENT' CHECK (booking_status IN ('DRAFT', 'PENDING_PAYMENT', 'PAYMENT_PROCESSING', 'CONFIRMED', 'CANCELLED', 'FAILED', 'EXPIRED')),
    payment_status VARCHAR(30) NOT NULL DEFAULT 'PAYMENT_PENDING' CHECK (payment_status IN ('PENDING', 'PAYMENT_PENDING', 'AUTHORIZED', 'PAYMENT_VERIFIED', 'PAID', 'FAILED', 'PAYMENT_FAILED', 'REFUNDED')),
    payment_order_id VARCHAR(60),
    payment_id VARCHAR(60),
    payment_method VARCHAR(30) DEFAULT 'UPI',
    utr_reference TEXT,
    gstin VARCHAR(20),
    company_name TEXT,
    invoice_number VARCHAR(30),
    pricing_breakdown JSONB,
    idempotency_key VARCHAR(100) UNIQUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.booking_passengers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id VARCHAR(60) NOT NULL REFERENCES public.bookings(booking_id) ON DELETE CASCADE,
    title VARCHAR(10) DEFAULT 'Mr',
    first_name TEXT,
    last_name TEXT,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    passenger_type VARCHAR(20) NOT NULL DEFAULT 'ADULT' CHECK (passenger_type IN ('ADULT', 'CHILD', 'INFANT')),
    seat_number VARCHAR(10),
    gender VARCHAR(20),
    age INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 9. PAYMENT LEDGER
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(60) UNIQUE NOT NULL,
    booking_id VARCHAR(60) NOT NULL REFERENCES public.bookings(booking_id) ON DELETE CASCADE,
    payment_id VARCHAR(60),
    provider VARCHAR(30) NOT NULL DEFAULT 'razorpay',
    amount INTEGER NOT NULL CHECK (amount > 0),
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    status VARCHAR(30) NOT NULL DEFAULT 'CREATED' CHECK (status IN ('CREATED', 'AUTHORIZED', 'CAPTURED', 'FAILED')),
    method VARCHAR(30),
    signature TEXT,
    error_code TEXT,
    error_description TEXT,
    idempotency_key VARCHAR(100) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 10. REFUNDS TRACKER
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pnr VARCHAR(20) UNIQUE NOT NULL,
    booking_id VARCHAR(60),
    passenger_name TEXT NOT NULL,
    airline TEXT NOT NULL,
    flight_no TEXT NOT NULL,
    sector TEXT NOT NULL,
    total_fare INTEGER NOT NULL CHECK (total_fare >= 0),
    cancellation_fee INTEGER NOT NULL DEFAULT 0 CHECK (cancellation_fee >= 0),
    refund_amount INTEGER NOT NULL CHECK (refund_amount >= 0),
    payment_method TEXT NOT NULL DEFAULT 'UPI',
    arn_number VARCHAR(60) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'REQUESTED' CHECK (status IN ('REQUESTED', 'Approved', 'Processing', 'Credited', 'COMPLETED', 'FAILED', 'Initiated')),
    stage INTEGER NOT NULL DEFAULT 1 CHECK (stage BETWEEN 1 AND 5),
    cancellation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_credit_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- 11. PERSONALIZATION: SAVED FLIGHTS & PRICE ALERTS
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.saved_flights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id),
    flight_no VARCHAR(20) NOT NULL,
    origin_code VARCHAR(3) NOT NULL REFERENCES public.airports(iata_code),
    destination_code VARCHAR(3) NOT NULL REFERENCES public.airports(iata_code),
    travel_date DATE,
    observed_fare INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id),
    route TEXT NOT NULL,
    origin_code VARCHAR(3),
    destination_code VARCHAR(3),
    current_fare TEXT NOT NULL,
    target_condition TEXT NOT NULL,
    email TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_checked TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ==============================================================================
-- PERFORMANCE INDEXES
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_flights_route ON public.flights (origin_code, destination_code);
CREATE INDEX IF NOT EXISTS idx_flights_airline ON public.flights (airline_code);
CREATE INDEX IF NOT EXISTS idx_flight_prices_flight ON public.flight_prices (flight_id);
CREATE INDEX IF NOT EXISTS idx_bookings_bid ON public.bookings (booking_id);
CREATE INDEX IF NOT EXISTS idx_bookings_pnr ON public.bookings (pnr);
CREATE INDEX IF NOT EXISTS idx_bookings_order ON public.bookings (payment_order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON public.payments (order_id);
CREATE INDEX IF NOT EXISTS idx_payments_bid ON public.payments (booking_id);
CREATE INDEX IF NOT EXISTS idx_refunds_pnr ON public.refunds (pnr);
CREATE INDEX IF NOT EXISTS idx_package_items_pkg ON public.package_items (package_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user ON public.price_alerts (user_id);

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================
ALTER TABLE public.airports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.airlines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flight_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.routes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tourist_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.package_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.booking_passengers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_flights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.price_alerts ENABLE ROW LEVEL SECURITY;

-- Catalog Discovery Policies (Public Read)
CREATE POLICY "Allow public read on airports" ON public.airports FOR SELECT USING (true);
CREATE POLICY "Allow public read on airlines" ON public.airlines FOR SELECT USING (true);
CREATE POLICY "Allow public read on flights" ON public.flights FOR SELECT USING (true);
CREATE POLICY "Allow public read on flight_prices" ON public.flight_prices FOR SELECT USING (true);
CREATE POLICY "Allow public read on routes" ON public.routes FOR SELECT USING (true);
CREATE POLICY "Allow public read on tourist_packages" ON public.tourist_packages FOR SELECT USING (true);
CREATE POLICY "Allow public read on package_items" ON public.package_items FOR SELECT USING (true);

-- Backend Service Role Full Access Policies (Strict Server-Side Operation)
CREATE POLICY "Service role full access on airports" ON public.airports FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on airlines" ON public.airlines FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on flights" ON public.flights FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on flight_prices" ON public.flight_prices FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on routes" ON public.routes FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on tourist_packages" ON public.tourist_packages FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on package_items" ON public.package_items FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on profiles" ON public.profiles FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on bookings" ON public.bookings FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on booking_passengers" ON public.booking_passengers FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on payments" ON public.payments FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on refunds" ON public.refunds FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on saved_flights" ON public.saved_flights FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access on price_alerts" ON public.price_alerts FOR ALL TO service_role USING (true) WITH CHECK (true);

-- User-Level Row Level Security (RLS) Isolation Policies
-- Profiles: users manage only their own profile
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT TO authenticated USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE TO authenticated USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT TO authenticated WITH CHECK (auth.uid() = id);

-- Bookings & Passengers: users can only query their own bookings
CREATE POLICY "Users can view own bookings" ON public.bookings FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can view own booking passengers" ON public.booking_passengers FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM public.bookings b WHERE b.booking_id = booking_passengers.booking_id AND b.user_id = auth.uid()));

-- Saved Flights Watchlist: strict per-user isolation
CREATE POLICY "Users can view own saved flights" ON public.saved_flights FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own saved flights" ON public.saved_flights FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own saved flights" ON public.saved_flights FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Price Alerts: strict per-user isolation
CREATE POLICY "Users can view own price alerts" ON public.price_alerts FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own price alerts" ON public.price_alerts FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own price alerts" ON public.price_alerts FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Refunds: users view only their own claims
CREATE POLICY "Users can view own refunds" ON public.refunds FOR SELECT TO authenticated USING (auth.uid() = user_id OR user_id IS NULL);

-- ==============================================================================
-- DEVELOPMENT SEED FIXTURES
-- Explicitly designated for development/testing environments.
-- ==============================================================================

-- 1. Major Indian Airports
INSERT INTO public.airports (iata_code, icao_code, name, city, state, country)
VALUES
    ('DEL', 'VIDP', 'Indira Gandhi International Airport', 'Delhi', 'Delhi', 'India'),
    ('BOM', 'VABB', 'Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'Maharashtra', 'India'),
    ('BLR', 'VOBL', 'Kempegowda International Airport', 'Bengaluru', 'Karnataka', 'India'),
    ('HYD', 'VOHS', 'Rajiv Gandhi International Airport', 'Hyderabad', 'Telangana', 'India'),
    ('MAA', 'VOMM', 'Chennai International Airport', 'Chennai', 'Tamil Nadu', 'India'),
    ('CCU', 'VECC', 'Netaji Subhash Chandra Bose International Airport', 'Kolkata', 'West Bengal', 'India'),
    ('GOI', 'VOGO', 'Dabolim Airport', 'Goa', 'Goa', 'India'),
    ('COK', 'VOCI', 'Cochin International Airport', 'Kochi', 'Kerala', 'India'),
    ('PNQ', 'VAPO', 'Pune International Airport', 'Pune', 'Maharashtra', 'India'),
    ('AMD', 'VAAH', 'Sardar Vallabhbhai Patel International Airport', 'Ahmedabad', 'Gujarat', 'India')
ON CONFLICT (iata_code) DO UPDATE
SET name = EXCLUDED.name, city = EXCLUDED.city, state = EXCLUDED.state;

-- 2. Major Indian Domestic Carriers
INSERT INTO public.airlines (iata_code, icao_code, name, callsign, country, is_active)
VALUES
    ('6E', 'IGO', 'IndiGo', 'IFLY', 'India', true),
    ('AI', 'AIC', 'Air India', 'AIRINDIA', 'India', true),
    ('QP', 'AKJ', 'Akasa Air', 'AKASA AIR', 'India', true),
    ('SG', 'SEJ', 'SpiceJet', 'SPICEJET', 'India', true),
    ('IX', 'AXB', 'Air India Express', 'EXPRESS INDIA', 'India', true),
    ('S5', 'SDG', 'Star Air', 'HISTAR', 'India', true),
    ('UK', 'VTI', 'Vistara (Historical / Merged into Air India)', 'VISTARA', 'India', false)
ON CONFLICT (iata_code) DO UPDATE
SET name = EXCLUDED.name, callsign = EXCLUDED.callsign, is_active = EXCLUDED.is_active;

-- 3. Monitored Sector Routes
INSERT INTO public.routes (route_code, origin, destination, origin_code, destination_code, index_value, change_30d, avg_fare, volatility_score, status)
VALUES
    ('DEL-BOM', 'Delhi (DEL)', 'Mumbai (BOM)', 'DEL', 'BOM', 114.2, 3.4, 5240, 68, 'High Traffic'),
    ('BOM-BLR', 'Mumbai (BOM)', 'Bengaluru (BLR)', 'BOM', 'BLR', 108.5, -1.2, 4120, 52, 'Stable'),
    ('DEL-BLR', 'Delhi (DEL)', 'Bengaluru (BLR)', 'DEL', 'BLR', 119.8, 5.8, 6450, 74, 'Surging'),
    ('HYD-DEL', 'Hyderabad (HYD)', 'Delhi (DEL)', 'HYD', 'DEL', 106.3, 1.1, 4890, 48, 'Moderate'),
    ('BOM-GOI', 'Mumbai (BOM)', 'Goa (GOI)', 'BOM', 'GOI', 128.4, 12.6, 5600, 89, 'High Volatility'),
    ('MAA-DEL', 'Chennai (MAA)', 'Delhi (DEL)', 'MAA', 'DEL', 111.0, 2.3, 5380, 59, 'Normal'),
    ('CCU-DEL', 'Kolkata (CCU)', 'Delhi (DEL)', 'CCU', 'DEL', 115.7, 4.0, 5720, 63, 'Normal'),
    ('BLR-HYD', 'Bengaluru (BLR)', 'Hyderabad (HYD)', 'BLR', 'HYD', 98.4, -3.1, 3200, 38, 'Low Fare')
ON CONFLICT (route_code) DO UPDATE
SET index_value = EXCLUDED.index_value, avg_fare = EXCLUDED.avg_fare, status = EXCLUDED.status;

-- 4. Initial Development Seed Refunds
INSERT INTO public.refunds (
    pnr, passenger_name, airline, flight_no, sector, total_fare,
    cancellation_fee, refund_amount, payment_method, arn_number, status, stage, cancellation_date, expected_credit_date
)
VALUES
    ('AIRX789', 'Rahul Sharma', 'IndiGo', '6E 203', 'HYD ➔ DEL', 5240, 999, 4241, 'UPI / Google Pay', 'UPI/428901239842', 'Credited', 4, '2026-08-28', '2026-08-31'),
    ('6E9021', 'Priya Patel', 'IndiGo', '6E 214', 'DEL ➔ BOM', 4820, 1200, 3620, 'HDFC Credit Card', 'ARN890213894102', 'Processing', 3, '2026-09-02', '2026-09-07'),
    ('AI3481', 'Ananya Reddy', 'Air India', 'AI 541', 'HYD ➔ DEL', 5780, 800, 4980, 'Net Banking (SBI)', 'ARN112938472910', 'Approved', 2, '2026-09-03', '2026-09-09')
ON CONFLICT (pnr) DO NOTHING;
