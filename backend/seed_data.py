from backend.database import get_db_connection

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if flights table already has data
    cursor.execute("SELECT COUNT(*) FROM flights")
    if cursor.fetchone()[0] == 0:
        flights_data = [
            # HYD -> DEL
            ("IndiGo", "6E 203", "Hyderabad", "HYD", "Delhi", "DEL", "06:15", "08:25", "2h 10m", 130, "Nonstop", 4340, 900, 5240, 1200, 82, 94, "Best value", "On time", "T2", "14A"),
            ("Air India", "AI 541", "Hyderabad", "HYD", "Delhi", "DEL", "08:10", "10:35", "2h 25m", 145, "Nonstop", 4880, 900, 5780, 0, 95, 91, "Bag included", "On time", "T3", "22B"),
            ("Akasa Air", "QP 1412", "Hyderabad", "HYD", "Delhi", "DEL", "11:20", "13:40", "2h 20m", 140, "Nonstop", 4080, 900, 4980, 1500, 78, 92, "Low fare", "On time", "T1", "04"),
            ("SpiceJet", "SG 401", "Hyderabad", "HYD", "Delhi", "DEL", "15:30", "18:55", "3h 25m", 205, "1 stop", 3720, 900, 4620, 1400, 112, 78, "Cheapest", "Delayed 15m", "T2", "09"),
            ("IndiGo", "6E 507", "Hyderabad", "HYD", "Delhi", "DEL", "18:05", "20:20", "2h 15m", 135, "Nonstop", 5200, 900, 6100, 0, 88, 89, "Flexible", "On time", "T2", "16"),
            ("Air India Express", "IX 992", "Hyderabad", "HYD", "Delhi", "DEL", "21:40", "23:55", "2h 15m", 135, "Nonstop", 4200, 850, 5050, 1100, 80, 90, "Late night saver", "On time", "T1", "02C"),

            # DEL -> BOM
            ("IndiGo", "6E 214", "Delhi", "DEL", "Mumbai", "BOM", "06:10", "08:20", "2h 10m", 130, "Nonstop", 4020, 800, 4820, 1200, 118, 93, "Popular departure", "On time", "T2", "11"),
            ("Air India", "AI 864", "Delhi", "DEL", "Mumbai", "BOM", "09:05", "11:20", "2h 15m", 135, "Nonstop", 4450, 800, 5250, 0, 126, 92, "Bag included", "On time", "T3", "34A"),
            ("Akasa Air", "QP 1320", "Delhi", "DEL", "Mumbai", "BOM", "13:35", "15:45", "2h 10m", 130, "Nonstop", 3590, 800, 4390, 1500, 115, 95, "Lowest fare", "On time", "T1", "06"),
            ("SpiceJet", "SG 8172", "Delhi", "DEL", "Mumbai", "BOM", "17:20", "19:40", "2h 20m", 140, "Nonstop", 3820, 800, 4620, 1400, 131, 84, "Evening choice", "On time", "T2", "15"),
            ("IndiGo", "6E 602", "Delhi", "DEL", "Mumbai", "BOM", "20:30", "23:00", "2h 30m", 150, "1 stop", 3180, 800, 3980, 1400, 154, 77, "Red-eye discount", "On time", "T2", "08"),
            ("Air India", "AI 678", "Delhi", "DEL", "Mumbai", "BOM", "19:00", "21:15", "2h 15m", 135, "Nonstop", 5440, 800, 6240, 0, 124, 88, "Business favorite", "On time", "T3", "28"),

            # DEL -> BLR
            ("IndiGo", "6E 2131", "Delhi", "DEL", "Bengaluru", "BLR", "07:00", "09:45", "2h 45m", 165, "Nonstop", 5050, 1000, 6050, 1200, 132, 90, "Early express", "On time", "T2", "19"),
            ("Air India", "AI 506", "Delhi", "DEL", "Bengaluru", "BLR", "10:15", "13:05", "2h 50m", 170, "Nonstop", 5400, 1000, 6400, 0, 140, 89, "Complimentary meal", "On time", "T3", "31"),
            ("Akasa Air", "QP 1502", "Delhi", "DEL", "Bengaluru", "BLR", "14:40", "17:25", "2h 45m", 165, "Nonstop", 4800, 1000, 5800, 1400, 128, 93, "Great value", "On time", "T1", "07"),

            # BLR -> HYD
            ("IndiGo", "6E 448", "Bengaluru", "BLR", "Hyderabad", "HYD", "07:30", "08:40", "1h 10m", 70, "Nonstop", 3150, 700, 3850, 1200, 54, 96, "High frequency", "On time", "T1", "05"),
            ("Air India", "AI 512", "Bengaluru", "BLR", "Hyderabad", "HYD", "12:15", "13:30", "1h 15m", 75, "Nonstop", 3500, 700, 4200, 0, 60, 92, "Bag included", "On time", "T2", "12"),
            ("SpiceJet", "SG 1084", "Bengaluru", "BLR", "Hyderabad", "HYD", "18:40", "19:55", "1h 15m", 75, "Nonstop", 2850, 700, 3550, 1300, 58, 88, "Budget pick", "Delayed 20m", "T1", "03"),

            # MAA -> DEL
            ("IndiGo", "6E 611", "Chennai", "MAA", "Delhi", "DEL", "06:40", "09:30", "2h 50m", 170, "Nonstop", 5780, 1000, 6780, 1200, 145, 87, "Fastest link", "On time", "T1", "17"),
            ("Air India", "AI 440", "Chennai", "MAA", "Delhi", "DEL", "14:20", "17:15", "2h 55m", 175, "Nonstop", 6100, 1000, 7100, 0, 150, 85, "Bag included", "On time", "T4", "26"),

            # BOM -> GOI
            ("IndiGo", "6E 534", "Mumbai", "BOM", "Goa", "GOI", "10:30", "11:45", "1h 15m", 75, "Nonstop", 2980, 650, 3630, 1200, 50, 94, "Vacation special", "On time", "T2", "14"),
            ("Akasa Air", "QP 1205", "Mumbai", "BOM", "Goa", "GOI", "16:10", "17:20", "1h 10m", 70, "Nonstop", 2750, 650, 3400, 1300, 48, 97, "Best seller", "On time", "T1", "08"),

            # CCU -> DEL
            ("IndiGo", "6E 824", "Kolkata", "CCU", "Delhi", "DEL", "08:50", "11:15", "2h 25m", 145, "Nonstop", 4950, 950, 5900, 1200, 122, 91, "Daily direct", "On time", "T2", "21"),
            ("Air India", "AI 701", "Kolkata", "CCU", "Delhi", "DEL", "16:30", "18:50", "2h 20m", 140, "Nonstop", 5350, 950, 6300, 0, 125, 89, "Bag included", "On time", "T2", "25")
        ]
        cursor.executemany("""
            INSERT INTO flights (
                airline, flight_no, origin, origin_code, destination, destination_code,
                dep_time, arr_time, duration, duration_mins, stops, base_fare, taxes,
                total_fare, bag_fee, emissions_kg, fare_score, tag, status, terminal, gate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, flights_data)

    # Routes table
    cursor.execute("SELECT COUNT(*) FROM routes")
    if cursor.fetchone()[0] == 0:
        routes_data = [
            ("DEL-BOM", "Delhi (DEL)", "Mumbai (BOM)", 132.4, 14.2, 6240, 82, "High"),
            ("DEL-BLR", "Delhi (DEL)", "Bengaluru (BLR)", 127.8, 9.8, 6050, 71, "Watch"),
            ("BLR-HYD", "Bengaluru (BLR)", "Hyderabad (HYD)", 124.3, -1.2, 3850, 44, "Stable"),
            ("HYD-DEL", "Hyderabad (HYD)", "Delhi (DEL)", 128.6, 6.8, 5240, 65, "Watch"),
            ("MAA-DEL", "Chennai (MAA)", "Delhi (DEL)", 135.7, 16.1, 6780, 88, "High"),
            ("CCU-DEL", "Kolkata (CCU)", "Delhi (DEL)", 129.2, 8.4, 5900, 68, "Watch"),
            ("BOM-GOI", "Mumbai (BOM)", "Goa (GOI)", 119.5, -3.4, 3400, 52, "Stable"),
            ("PNQ-DEL", "Pune (PNQ)", "Delhi (DEL)", 131.0, 11.5, 5650, 74, "High")
        ]
        cursor.executemany("""
            INSERT INTO routes (route_code, origin, destination, index_value, change_30d, avg_fare, volatility_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, routes_data)

    # Alerts table
    cursor.execute("SELECT COUNT(*) FROM alerts")
    if cursor.fetchone()[0] == 0:
        alerts_data = [
            ("HYD → DEL", "₹5,240", "Drop below ₹5,000", 1),
            ("DEL → BOM", "₹6,240", "Any price change", 1),
            ("BLR → HYD", "₹3,850", "Drop below ₹3,500", 1)
        ]
        cursor.executemany("""
            INSERT INTO alerts (route, current_fare, target_condition, is_active)
            VALUES (?, ?, ?, ?)
        """, alerts_data)

    # Historical Index data
    cursor.execute("SELECT COUNT(*) FROM index_history")
    if cursor.fetchone()[0] == 0:
        index_data = [
            ("30D", "W1", 121.2, 0),
            ("30D", "W2", 122.8, 0),
            ("30D", "W3", 125.1, 0),
            ("30D", "W4", 124.6, 0),
            ("30D", "W5", 127.3, 0),
            ("30D", "W6", 128.0, 0),
            ("30D", "W7", 128.6, 0),
            ("90D", "M-2", 116.4, 0),
            ("90D", "M-1.5", 119.8, 0),
            ("90D", "M-1", 122.5, 0),
            ("90D", "M-0.5", 125.7, 0),
            ("90D", "Current", 128.6, 0),
            ("1Y", "Q1 '25", 108.2, 0),
            ("1Y", "Q2 '25", 112.5, 0),
            ("1Y", "Q3 '25", 118.9, 0),
            ("1Y", "Q4 '25", 123.4, 0),
            ("1Y", "Q1 '26", 128.6, 0)
        ]
        cursor.executemany("""
            INSERT INTO index_history (period, label, value, is_projected)
            VALUES (?, ?, ?, ?)
        """, index_data)

    # Elasticity points
    cursor.execute("SELECT COUNT(*) FROM elasticity")
    if cursor.fetchone()[0] == 0:
        elasticity_data = [
            ("DEL-BOM", "T+1", 8400, "HIGH"),
            ("DEL-BOM", "T+7", 6900, "MODERATE"),
            ("DEL-BOM", "T+15", 5800, "BALANCED"),
            ("DEL-BOM", "T+30", 4900, "OPTIMAL"),
            ("DEL-BOM", "T+45", 4600, "LOW")
        ]
        cursor.executemany("""
            INSERT INTO elasticity (route_code, advance_window, fare, sensitivity)
            VALUES (?, ?, ?, ?)
        """, elasticity_data)

    # Refunds seed data
    cursor.execute("SELECT COUNT(*) FROM refunds")
    if cursor.fetchone()[0] == 0:
        refunds_data = [
            ("AIRX789", "Rahul Sharma", "IndiGo", "6E 203", "HYD ➔ DEL", 5240, 999, 4241, "UPI / Google Pay", "UPI/428901239842", "Credited", 4, "2026-08-28", "2026-08-31"),
            ("6E9021", "Priya Patel", "IndiGo", "6E 214", "DEL ➔ BOM", 4820, 1200, 3620, "HDFC Credit Card", "ARN890213894102", "Processing", 3, "2026-09-02", "2026-09-07"),
            ("AI3481", "Ananya Reddy", "Air India", "AI 541", "HYD ➔ DEL", 5780, 800, 4980, "Net Banking (SBI)", "ARN112938472910", "Approved", 2, "2026-09-03", "2026-09-09"),
            ("QP1502", "Vikram Singh", "Akasa Air", "QP 1502", "DEL ➔ BLR", 5800, 1500, 4300, "ICICI Debit Card", "PENDING-GATEWAY", "Initiated", 1, "2026-09-04", "2026-09-11")
        ]
        cursor.executemany("""
            INSERT INTO refunds (
                pnr, passenger_name, airline, flight_no, sector, total_fare,
                cancellation_fee, refund_amount, payment_method, arn_number,
                status, stage, cancellation_date, expected_credit_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, refunds_data)

    conn.commit()
    conn.close()
