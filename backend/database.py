import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "airfarex.db"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Flights table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airline TEXT NOT NULL,
        flight_no TEXT NOT NULL,
        origin TEXT NOT NULL,
        origin_code TEXT NOT NULL,
        destination TEXT NOT NULL,
        destination_code TEXT NOT NULL,
        dep_time TEXT NOT NULL,
        arr_time TEXT NOT NULL,
        duration TEXT NOT NULL,
        duration_mins INTEGER NOT NULL,
        stops TEXT NOT NULL,
        base_fare INTEGER NOT NULL,
        taxes INTEGER NOT NULL,
        total_fare INTEGER NOT NULL,
        bag_fee INTEGER NOT NULL,
        emissions_kg INTEGER NOT NULL,
        fare_score INTEGER NOT NULL,
        tag TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'On time',
        terminal TEXT DEFAULT 'T1',
        gate TEXT DEFAULT 'G1'
    )
    """)

    # Monitored routes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_code TEXT UNIQUE NOT NULL,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        index_value REAL NOT NULL,
        change_30d REAL NOT NULL,
        avg_fare INTEGER NOT NULL,
        volatility_score INTEGER NOT NULL,
        status TEXT NOT NULL
    )
    """)

    # Price alerts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT DEFAULT 'guest',
        route TEXT NOT NULL,
        current_fare TEXT NOT NULL,
        target_condition TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Index history table (for 30D, 90D, 1Y charts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS index_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period TEXT NOT NULL,
        label TEXT NOT NULL,
        value REAL NOT NULL,
        is_projected INTEGER DEFAULT 0
    )
    """)

    # Elasticity points table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elasticity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_code TEXT NOT NULL,
        advance_window TEXT NOT NULL,
        fare INTEGER NOT NULL,
        sensitivity TEXT NOT NULL
    )
    """)

    # Refunds tracking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS refunds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT DEFAULT 'guest',
        pnr TEXT UNIQUE NOT NULL,
        passenger_name TEXT NOT NULL,
        airline TEXT NOT NULL,
        flight_no TEXT NOT NULL,
        sector TEXT NOT NULL,
        total_fare INTEGER NOT NULL,
        cancellation_fee INTEGER NOT NULL,
        refund_amount INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        arn_number TEXT NOT NULL,
        status TEXT NOT NULL, -- 'Credited', 'Processing', 'Approved', 'Initiated'
        stage INTEGER NOT NULL, -- 1 to 5
        cancellation_date TEXT NOT NULL,
        expected_credit_date TEXT NOT NULL
    )
    """)

    # Production-ready Bookings table (Phase 5: Full End-to-End Booking Model)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE NOT NULL,
        booking_reference TEXT UNIQUE,
        user_id TEXT DEFAULT 'guest',
        booking_type TEXT NOT NULL DEFAULT 'flight', -- 'flight' or 'package'
        package_id TEXT,
        flight_no TEXT,
        airline TEXT,
        sector TEXT,
        origin_code TEXT,
        destination_code TEXT,
        provider TEXT DEFAULT 'MockDevelopmentProvider',
        data_source TEXT DEFAULT 'DEVELOPMENT',
        traveler_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        travel_date TEXT NOT NULL,
        pax_count INTEGER NOT NULL DEFAULT 1,
        base_fare INTEGER DEFAULT 0,
        taxes INTEGER DEFAULT 0,
        fees INTEGER DEFAULT 0,
        amount INTEGER NOT NULL, -- Trusted server-computed total amount in INR
        currency TEXT NOT NULL DEFAULT 'INR',
        payment_status TEXT NOT NULL DEFAULT 'PAYMENT_PENDING',
        booking_status TEXT NOT NULL DEFAULT 'PENDING_PAYMENT',
        payment_order_id TEXT,
        payment_id TEXT,
        seat_number TEXT,
        pnr TEXT,
        voucher_id TEXT,
        pricing_breakdown TEXT, -- JSON string of trusted cost decomposition
        idempotency_key TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )
    """)

    # Production-ready Payments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id TEXT UNIQUE,
        order_id TEXT UNIQUE NOT NULL,
        booking_id TEXT NOT NULL,
        amount INTEGER NOT NULL, -- Amount in paise
        currency TEXT NOT NULL DEFAULT 'INR',
        status TEXT NOT NULL DEFAULT 'CREATED', -- 'CREATED', 'AUTHORIZED', 'CAPTURED', 'FAILED'
        method TEXT,
        signature TEXT,
        error_code TEXT,
        error_description TEXT,
        idempotency_key TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Master Catalog: Airports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS airports (
        iata_code TEXT PRIMARY KEY,
        icao_code TEXT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        country TEXT NOT NULL DEFAULT 'India',
        is_active INTEGER DEFAULT 1
    )
    """)

    # Master Catalog: Airlines
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS airlines (
        iata_code TEXT PRIMARY KEY,
        icao_code TEXT,
        name TEXT NOT NULL,
        callsign TEXT,
        country TEXT NOT NULL DEFAULT 'India',
        is_active INTEGER DEFAULT 1
    )
    """)

    # Booking passengers table (Phase 5: Multi-passenger support)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booking_passengers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT NOT NULL,
        title TEXT DEFAULT 'Mr',
        first_name TEXT,
        last_name TEXT,
        full_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        passenger_type TEXT DEFAULT 'ADULT',
        seat_number TEXT,
        gender TEXT,
        age INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
    )
    """)

    # Customer Travel Profiles (Mapped to Supabase Auth UUID or guest)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        gstin TEXT,
        company_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # User Saved Flights Watchlist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        flight_no TEXT NOT NULL,
        origin_code TEXT NOT NULL,
        destination_code TEXT NOT NULL,
        travel_date TEXT,
        observed_fare INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Flight Provider Search Cache (Phase 4)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flight_search_cache (
        cache_key TEXT PRIMARY KEY,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_date TEXT,
        return_date TEXT,
        cabin_class TEXT NOT NULL DEFAULT 'Economy',
        adults INTEGER NOT NULL DEFAULT 1,
        provider TEXT NOT NULL,
        data_source TEXT NOT NULL,
        results_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL
    )
    """)

    # User Travel Preferences (Phase 7: Personalized AI Recommendations)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id TEXT PRIMARY KEY,
        priority TEXT DEFAULT 'best_value', -- 'best_value', 'lowest_price', 'fastest', 'nonstop'
        time_preference TEXT DEFAULT 'any', -- 'any', 'morning', 'afternoon', 'evening'
        preferred_airline TEXT,
        max_stops TEXT DEFAULT 'Any',
        flexible_dates INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Safe dynamic column migrations for existing SQLite instances
    migration_columns = {
        "bookings": [
            ("booking_reference", "TEXT"),
            ("user_id", "TEXT DEFAULT 'guest'"),
            ("provider", "TEXT DEFAULT 'MockDevelopmentProvider'"),
            ("data_source", "TEXT DEFAULT 'DEVELOPMENT'"),
            ("origin_code", "TEXT"),
            ("destination_code", "TEXT"),
            ("base_fare", "INTEGER DEFAULT 0"),
            ("taxes", "INTEGER DEFAULT 0"),
            ("fees", "INTEGER DEFAULT 0"),
            ("idempotency_key", "TEXT"),
            ("expires_at", "TIMESTAMP")
        ],
        "booking_passengers": [
            ("title", "TEXT DEFAULT 'Mr'"),
            ("first_name", "TEXT"),
            ("last_name", "TEXT")
        ],
        "alerts": [
            ("user_id", "TEXT DEFAULT 'guest'")
        ],
        "refunds": [
            ("user_id", "TEXT DEFAULT 'guest'")
        ]
    }

    for tbl, cols in migration_columns.items():
        try:
            cursor.execute(f"PRAGMA table_info({tbl})")
            existing = [c[1] for c in cursor.fetchall()]
            for col_name, col_type in cols:
                if col_name not in existing:
                    cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass

    # Fast lookup indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_id ON bookings(booking_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_ref ON bookings(booking_reference)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_pnr ON bookings(pnr)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_order ON bookings(payment_order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_idemp ON bookings(idempotency_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_id ON payments(payment_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_passengers_bid ON booking_passengers(booking_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_saved_flights_user ON saved_flights(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_lookup ON flight_search_cache(origin, destination, departure_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON flight_search_cache(expires_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_airports_lookup ON airports(iata_code, city, name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_flights_sector ON flights(origin_code, destination_code)")

    conn.commit()
    conn.close()
