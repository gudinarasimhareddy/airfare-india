-- =========================================================
-- AirfareX India — Supabase PostgreSQL Schema Migration
-- Project: https://thtwkhhccxmkkgwtoleb.supabase.co
-- Run this script in the Supabase SQL Editor (Dashboard > SQL Editor)
-- =========================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. FLIGHTS TABLE
CREATE TABLE IF NOT EXISTS public.flights (
    id BIGSERIAL PRIMARY KEY,
    airline TEXT NOT NULL,
    flight_no TEXT NOT NULL,
    origin TEXT NOT NULL,
    origin_code VARCHAR(3) NOT NULL,
    destination TEXT NOT NULL,
    destination_code VARCHAR(3) NOT NULL,
    dep_time TEXT NOT NULL,
    arr_time TEXT NOT NULL,
    duration TEXT NOT NULL,
    duration_mins INTEGER NOT NULL DEFAULT 120,
    stops TEXT NOT NULL DEFAULT 'Nonstop',
    base_fare INTEGER NOT NULL,
    taxes INTEGER NOT NULL,
    total_fare INTEGER NOT NULL,
    bag_fee INTEGER NOT NULL DEFAULT 0,
    emissions_kg INTEGER NOT NULL DEFAULT 130,
    fare_score INTEGER NOT NULL DEFAULT 90,
    tag TEXT NOT NULL DEFAULT 'Standard Fare',
    status TEXT NOT NULL DEFAULT 'On time',
    terminal TEXT DEFAULT 'T2',
    gate TEXT DEFAULT 'G1',
    aircraft TEXT DEFAULT 'Airbus A320neo',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. MONITORED ROUTES TABLE
CREATE TABLE IF NOT EXISTS public.routes (
    id BIGSERIAL PRIMARY KEY,
    route_code VARCHAR(10) UNIQUE NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    index_value NUMERIC(6, 2) NOT NULL,
    change_30d NUMERIC(5, 2) NOT NULL,
    avg_fare INTEGER NOT NULL,
    volatility_score INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. PRICE ALERTS TABLE
CREATE TABLE IF NOT EXISTS public.alerts (
    id BIGSERIAL PRIMARY KEY,
    route TEXT NOT NULL,
    current_fare TEXT NOT NULL,
    target_condition TEXT NOT NULL,
    email TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. CONFIRMED BOOKINGS & E-TICKETS TABLE
CREATE TABLE IF NOT EXISTS public.bookings (
    id BIGSERIAL PRIMARY KEY,
    pnr VARCHAR(20) UNIQUE NOT NULL,
    eticket_number VARCHAR(30) UNIQUE NOT NULL,
    airline TEXT NOT NULL,
    flight_no TEXT NOT NULL,
    origin_code VARCHAR(3) NOT NULL,
    destination_code VARCHAR(3) NOT NULL,
    travel_date DATE NOT NULL,
    passenger_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    gate VARCHAR(10),
    terminal VARCHAR(10),
    base_fare INTEGER NOT NULL,
    total_fare INTEGER NOT NULL,
    payment_method VARCHAR(20) NOT NULL DEFAULT 'UPI',
    utr_reference TEXT,
    gstin VARCHAR(20),
    company_name TEXT,
    sac_code VARCHAR(10) DEFAULT '9964',
    invoice_number VARCHAR(30),
    gst_amount INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. REFUND TRACKER TABLE
CREATE TABLE IF NOT EXISTS public.refunds (
    id BIGSERIAL PRIMARY KEY,
    pnr VARCHAR(20) UNIQUE NOT NULL,
    passenger_name TEXT NOT NULL,
    airline TEXT NOT NULL,
    flight_no TEXT NOT NULL,
    sector TEXT NOT NULL,
    total_fare INTEGER NOT NULL,
    cancellation_fee INTEGER NOT NULL,
    refund_amount INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    arn_number TEXT NOT NULL,
    status TEXT NOT NULL,
    stage INTEGER NOT NULL DEFAULT 1,
    cancellation_date TEXT NOT NULL,
    expected_credit_date TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. PAYMENTS AUDIT TABLE
CREATE TABLE IF NOT EXISTS public.payments (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(60) UNIQUE NOT NULL,
    booking_id VARCHAR(60) NOT NULL,
    payment_id VARCHAR(60),
    amount INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    status VARCHAR(30) NOT NULL DEFAULT 'CREATED',
    signature TEXT,
    error_code TEXT,
    error_description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. TOURIST PLANS TABLE
CREATE TABLE IF NOT EXISTS public.tourist_plans (
    id TEXT PRIMARY KEY,
    destination TEXT NOT NULL,
    title TEXT NOT NULL,
    tagline TEXT,
    duration TEXT NOT NULL,
    image_url TEXT,
    flight_carrier TEXT NOT NULL,
    flight_sector TEXT NOT NULL,
    flight_baggage TEXT,
    hotel_name TEXT NOT NULL,
    hotel_rating NUMERIC(2, 1),
    hotel_room_type TEXT,
    price_without_offers INTEGER NOT NULL,
    price_with_offers INTEGER NOT NULL,
    savings INTEGER NOT NULL,
    discount_pct INTEGER NOT NULL,
    applied_promo TEXT,
    itinerary_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security (RLS) Configuration
ALTER TABLE public.flights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.routes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tourist_plans ENABLE ROW LEVEL SECURITY;

-- 1. Catalog Read Policies (Publicly readable for search & exploration)
CREATE POLICY "Allow public read access to flights" ON public.flights FOR SELECT USING (true);
CREATE POLICY "Allow public read access to routes" ON public.routes FOR SELECT USING (true);
CREATE POLICY "Allow public read access to tourist_plans" ON public.tourist_plans FOR SELECT USING (true);

-- 2. Secure RLS for Sensitive Customer Data (Bookings, Payments, Refunds)
-- Prevent public unauthorized reading and arbitrary tampering.
-- Inserts & Updates are strictly restricted to the authenticated backend service_role.
CREATE POLICY "Service role full access on bookings" ON public.bookings 
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on payments" ON public.payments 
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on refunds" ON public.refunds 
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access on alerts" ON public.alerts 
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Allow public read access to specific booking only when querying by matching PNR
CREATE POLICY "Allow individual PNR lookup on bookings" ON public.bookings
    FOR SELECT TO anon, authenticated
    USING (pnr = current_setting('request.jwt.claim.pnr', true));

-- Allow public read access to individual refund status by matching PNR
CREATE POLICY "Allow individual PNR lookup on refunds" ON public.refunds
    FOR SELECT TO anon, authenticated
    USING (pnr = current_setting('request.jwt.claim.pnr', true));

-- Seed initial flight sectors
INSERT INTO public.routes (route_code, origin, destination, index_value, change_30d, avg_fare, volatility_score, status)
VALUES
    ('DEL-BOM', 'Delhi (DEL)', 'Mumbai (BOM)', 114.2, 3.4, 5240, 68, 'High Traffic'),
    ('BOM-BLR', 'Mumbai (BOM)', 'Bengaluru (BLR)', 108.5, -1.2, 4120, 52, 'Stable'),
    ('DEL-BLR', 'Delhi (DEL)', 'Bengaluru (BLR)', 119.8, 5.8, 6450, 74, 'Surging'),
    ('HYD-DEL', 'Hyderabad (HYD)', 'Delhi (DEL)', 106.3, 1.1, 4890, 48, 'Moderate'),
    ('BOM-GOI', 'Mumbai (BOM)', 'Goa (GOI)', 128.4, 12.6, 5600, 89, 'High Volatility'),
    ('MAA-DEL', 'Chennai (MAA)', 'Delhi (DEL)', 111.0, 2.3, 5380, 59, 'Normal'),
    ('CCU-DEL', 'Kolkata (CCU)', 'Delhi (DEL)', 115.7, 4.0, 5720, 63, 'Normal'),
    ('BLR-HYD', 'Bengaluru (BLR)', 'Hyderabad (HYD)', 98.4, -3.1, 3200, 38, 'Low Fare')
ON CONFLICT (route_code) DO NOTHING;
