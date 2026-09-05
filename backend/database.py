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

    conn.commit()
    conn.close()
