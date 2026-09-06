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
        stage INTEGER NOT NULL, -- 1 to 4
        cancellation_date TEXT NOT NULL,
        expected_credit_date TEXT NOT NULL
    )
    """)

    # Production-ready Bookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE NOT NULL,
        user_id TEXT DEFAULT 'guest',
        booking_type TEXT NOT NULL DEFAULT 'flight', -- 'flight' or 'package'
        package_id TEXT,
        flight_no TEXT,
        airline TEXT,
        sector TEXT,
        traveler_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        travel_date TEXT NOT NULL,
        pax_count INTEGER NOT NULL DEFAULT 1,
        amount INTEGER NOT NULL, -- Trusted server-computed total amount in INR
        currency TEXT NOT NULL DEFAULT 'INR',
        payment_status TEXT NOT NULL DEFAULT 'PAYMENT_PENDING',
        booking_status TEXT NOT NULL DEFAULT 'DRAFT',
        payment_order_id TEXT,
        payment_id TEXT,
        seat_number TEXT,
        pnr TEXT,
        voucher_id TEXT,
        pricing_breakdown TEXT, -- JSON string of trusted cost decomposition
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    # Fast lookup indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_id ON bookings(booking_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_pnr ON bookings(pnr)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_order ON bookings(payment_order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_id ON payments(payment_id)")

    conn.commit()
    conn.close()

