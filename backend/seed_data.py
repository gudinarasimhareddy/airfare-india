from backend.database import get_db_connection

def seed_database():
    """
    AirfareX India — Centralized Deterministic Demo Dataset Seeder.
    Populates all core business models with realistic, consistent, repeatable development data.
    Safe to execute multiple times (idempotent via INSERT OR REPLACE).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # =========================================================================
    # 1. Master Catalog: 20 Major Indian Airports
    # =========================================================================
    airports_data = [
        ("DEL", "VIDP", "Indira Gandhi International Airport", "Delhi", "Delhi", "India", 1),
        ("BOM", "VABB", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "Maharashtra", "India", 1),
        ("BLR", "VOBL", "Kempegowda International Airport", "Bengaluru", "Karnataka", "India", 1),
        ("HYD", "VOHS", "Rajiv Gandhi International Airport", "Hyderabad", "Telangana", "India", 1),
        ("MAA", "VOMM", "Chennai International Airport", "Chennai", "Tamil Nadu", "India", 1),
        ("CCU", "VECC", "Netaji Subhash Chandra Bose International Airport", "Kolkata", "West Bengal", "India", 1),
        ("GOI", "VOGO", "Dabolim Airport", "Goa", "Goa", "India", 1),
        ("PNQ", "VAPO", "Pune International Airport", "Pune", "Maharashtra", "India", 1),
        ("AMD", "VAAH", "Sardar Vallabhbhai Patel International Airport", "Ahmedabad", "Gujarat", "India", 1),
        ("COK", "VOCI", "Cochin International Airport", "Kochi", "Kerala", "India", 1),
        ("JAI", "VIJP", "Jaipur International Airport", "Jaipur", "Rajasthan", "India", 1),
        ("LKO", "VILK", "Chaudhary Charan Singh International Airport", "Lucknow", "Uttar Pradesh", "India", 1),
        ("GAU", "VEGT", "Lokpriya Gopinath Bordoloi International Airport", "Guwahati", "Assam", "India", 1),
        ("BBI", "VEBS", "Biju Patnaik International Airport", "Bhubaneswar", "Odisha", "India", 1),
        ("IXC", "VICG", "Shaheed Bhagat Singh International Airport", "Chandigarh", "Chandigarh", "India", 1),
        ("IXM", "VOMD", "Madurai Airport", "Madurai", "Tamil Nadu", "India", 1),
        ("TRV", "VOTV", "Trivandrum International Airport", "Thiruvananthapuram", "Kerala", "India", 1),
        ("PAT", "VEPT", "Jay Prakash Narayan Airport", "Patna", "Bihar", "India", 1),
        ("SXR", "VISR", "Sheikh ul-Alam International Airport", "Srinagar", "Jammu & Kashmir", "India", 1),
        ("IXZ", "VOPB", "Veer Savarkar International Airport", "Port Blair", "Andaman & Nicobar", "India", 1)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO airports (iata_code, icao_code, name, city, state, country, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, airports_data)

    # =========================================================================
    # 2. Master Catalog: 10 Indian Airlines (Active + Historical Vistara)
    # =========================================================================
    airlines_data = [
        ("6E", "IGO", "IndiGo", "IFLY", "India", 1),
        ("AI", "AIC", "Air India", "AIRINDIA", "India", 1),
        ("IX", "AXB", "Air India Express", "EXPRESS INDIA", "India", 1),
        ("QP", "AKJ", "Akasa Air", "AKASA AIR", "India", 1),
        ("SG", "SEJ", "SpiceJet", "SPICEJET", "India", 1),
        ("S5", "SDG", "Star Air", "HISTAR", "India", 1),
        ("9I", "LLR", "Alliance Air", "ALLIED", "India", 1),
        ("IC", "GOA", "Fly91", "GOA AIR", "India", 1),
        ("I7", "IOA", "IndiaOne Air", "INDIAONE", "India", 1),
        ("UK", "VTI", "Vistara (Historical / Merged into Air India)", "VISTARA", "India", 0)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO airlines (iata_code, icao_code, name, callsign, country, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, airlines_data)

    # =========================================================================
    # 3. Master Flight Inventory: 40+ Demo Flights Across 20 Domestic Routes
    # =========================================================================
    cursor.execute("DELETE FROM flights")
    flights_data = [
        # Sector 1: DEL -> BOM (Strongest inventory: 7 flights across day & airlines)
        ("IndiGo", "6E 214", "Delhi", "DEL", "Mumbai", "BOM", "06:10", "08:20", "2h 10m", 130, "Nonstop", 4020, 800, 4820, 1200, 118, 93, "Popular departure", "On time", "T2", "11"),
        ("Air India", "AI 864", "Delhi", "DEL", "Mumbai", "BOM", "09:05", "11:20", "2h 15m", 135, "Nonstop", 4450, 800, 5250, 0, 126, 92, "Bag included", "On time", "T3", "34A"),
        ("Akasa Air", "QP 1320", "Delhi", "DEL", "Mumbai", "BOM", "13:35", "15:45", "2h 10m", 130, "Nonstop", 3590, 800, 4390, 1500, 115, 95, "Lowest fare", "On time", "T1", "06"),
        ("SpiceJet", "SG 8172", "Delhi", "DEL", "Mumbai", "BOM", "17:20", "19:40", "2h 20m", 140, "Nonstop", 3820, 800, 4620, 1400, 131, 84, "Evening choice", "On time", "T2", "15"),
        ("Air India", "AI 678", "Delhi", "DEL", "Mumbai", "BOM", "19:00", "21:15", "2h 15m", 135, "Nonstop", 5440, 800, 6240, 0, 124, 88, "Business favorite", "On time", "T3", "28"),
        ("IndiGo", "6E 602", "Delhi", "DEL", "Mumbai", "BOM", "20:30", "23:00", "2h 30m", 150, "1 stop", 3180, 800, 3980, 1400, 154, 77, "Red-eye discount", "On time", "T2", "08"),
        ("Air India Express", "IX 192", "Delhi", "DEL", "Mumbai", "BOM", "22:15", "00:30", "2h 15m", 135, "Nonstop", 3650, 800, 4450, 1100, 114, 91, "Late saver", "On time", "T1", "03"),

        # Sector 2: DEL -> BLR
        ("IndiGo", "6E 2131", "Delhi", "DEL", "Bengaluru", "BLR", "07:00", "09:45", "2h 45m", 165, "Nonstop", 5050, 1000, 6050, 1200, 132, 90, "Early express", "On time", "T2", "19"),
        ("Air India", "AI 506", "Delhi", "DEL", "Bengaluru", "BLR", "10:15", "13:05", "2h 50m", 170, "Nonstop", 5400, 1000, 6400, 0, 140, 89, "Complimentary meal", "On time", "T3", "31"),
        ("Akasa Air", "QP 1502", "Delhi", "DEL", "Bengaluru", "BLR", "14:40", "17:25", "2h 45m", 165, "Nonstop", 4800, 1000, 5800, 1400, 128, 93, "Great value", "On time", "T1", "07"),

        # Sector 3: DEL -> HYD
        ("IndiGo", "6E 502", "Delhi", "DEL", "Hyderabad", "HYD", "07:15", "09:30", "2h 15m", 135, "Nonstop", 4250, 850, 5100, 1200, 85, 92, "Direct Morning", "On time", "T2", "12"),
        ("Air India", "AI 542", "Delhi", "DEL", "Hyderabad", "HYD", "16:40", "19:00", "2h 20m", 140, "Nonstop", 4600, 850, 5450, 0, 90, 90, "Bag included", "On time", "T3", "24"),

        # Sector 4: DEL -> MAA
        ("IndiGo", "6E 612", "Delhi", "DEL", "Chennai", "MAA", "08:30", "11:15", "2h 45m", 165, "Nonstop", 5650, 950, 6600, 1200, 142, 88, "Morning Direct", "On time", "T2", "18"),
        ("Air India", "AI 441", "Delhi", "DEL", "Chennai", "MAA", "15:10", "18:00", "2h 50m", 170, "Nonstop", 6050, 950, 7000, 0, 148, 86, "Full Service", "On time", "T3", "29"),
        ("Akasa Air", "QP 1701", "Delhi", "DEL", "Chennai", "MAA", "11:00", "14:45", "3h 45m", 225, "1 stop", 4800, 950, 5750, 1300, 155, 84, "1 Stop Saver", "On time", "T1", "04"),

        # Sector 5: DEL -> GOI
        ("IndiGo", "6E 331", "Delhi", "DEL", "Goa", "GOI", "09:20", "11:55", "2h 35m", 155, "Nonstop", 4950, 850, 5800, 1200, 130, 94, "Beach Express", "On time", "T2", "14"),
        ("Akasa Air", "QP 1420", "Delhi", "DEL", "Goa", "GOI", "14:05", "16:40", "2h 35m", 155, "Nonstop", 4700, 850, 5550, 1300, 125, 96, "Holiday Special", "On time", "T1", "05"),

        # Sector 6: DEL -> CCU
        ("IndiGo", "6E 825", "Delhi", "DEL", "Kolkata", "CCU", "07:45", "10:00", "2h 15m", 135, "Nonstop", 4850, 900, 5750, 1200, 120, 91, "City of Joy Link", "On time", "T2", "20"),
        ("Air India", "AI 702", "Delhi", "DEL", "Kolkata", "CCU", "17:15", "19:35", "2h 20m", 140, "Nonstop", 5250, 900, 6150, 0, 125, 89, "Complimentary Meal", "On time", "T3", "27"),

        # Sector 7: BOM -> DEL
        ("IndiGo", "6E 215", "Mumbai", "BOM", "Delhi", "DEL", "07:00", "09:10", "2h 10m", 130, "Nonstop", 4120, 800, 4920, 1200, 118, 93, "Early Mumbai Shuttle", "On time", "T2", "10"),
        ("Air India", "AI 865", "Mumbai", "BOM", "Delhi", "DEL", "18:30", "20:45", "2h 15m", 135, "Nonstop", 4550, 800, 5350, 0, 126, 91, "Evening Shuttle", "On time", "T2", "33"),

        # Sector 8: BOM -> BLR
        ("IndiGo", "6E 341", "Mumbai", "BOM", "Bengaluru", "BLR", "08:15", "10:00", "1h 45m", 105, "Nonstop", 3250, 700, 3950, 1200, 80, 95, "Business Route", "On time", "T2", "12"),
        ("Akasa Air", "QP 1105", "Mumbai", "BOM", "Bengaluru", "BLR", "16:20", "18:05", "1h 45m", 105, "Nonstop", 2980, 700, 3680, 1300, 78, 97, "Low Fare Direct", "On time", "T1", "08"),
        ("Air India", "AI 639", "Mumbai", "BOM", "Bengaluru", "BLR", "11:30", "13:20", "1h 50m", 110, "Nonstop", 3600, 700, 4300, 0, 84, 91, "Mid-day Service", "On time", "T2", "25"),
        ("SpiceJet", "SG 382", "Mumbai", "BOM", "Bengaluru", "BLR", "14:10", "16:00", "1h 50m", 110, "Nonstop", 2890, 700, 3590, 1300, 82, 92, "Budget Saver", "On time", "T1", "03"),
        ("Air India Express", "IX 284", "Mumbai", "BOM", "Bengaluru", "BLR", "20:45", "22:30", "1h 45m", 105, "Nonstop", 2950, 700, 3650, 1100, 79, 96, "Late Express", "On time", "T1", "06"),

        # Sector 9: BOM -> HYD
        ("IndiGo", "6E 521", "Mumbai", "BOM", "Hyderabad", "HYD", "09:00", "10:25", "1h 25m", 85, "Nonstop", 2850, 650, 3500, 1200, 62, 94, "High Frequency", "On time", "T2", "09"),
        ("Air India Express", "IX 412", "Mumbai", "BOM", "Hyderabad", "HYD", "15:45", "17:10", "1h 25m", 85, "Nonstop", 2700, 650, 3350, 1100, 60, 96, "Saver Rate", "On time", "T1", "02"),

        # Sector 10: BOM -> GOI
        ("IndiGo", "6E 534", "Mumbai", "BOM", "Goa", "GOI", "10:30", "11:45", "1h 15m", 75, "Nonstop", 2980, 650, 3630, 1200, 50, 94, "Vacation special", "On time", "T2", "14"),
        ("Akasa Air", "QP 1205", "Mumbai", "BOM", "Goa", "GOI", "16:10", "17:20", "1h 10m", 70, "Nonstop", 2750, 650, 3400, 1300, 48, 97, "Best seller", "On time", "T1", "08"),

        # Sector 11: BLR -> DEL
        ("IndiGo", "6E 2132", "Bengaluru", "BLR", "Delhi", "DEL", "06:30", "09:15", "2h 45m", 165, "Nonstop", 4950, 1000, 5950, 1200, 132, 91, "Morning Prime", "On time", "T1", "16"),
        ("Air India", "AI 507", "Bengaluru", "BLR", "Delhi", "DEL", "17:40", "20:30", "2h 50m", 170, "Nonstop", 5350, 1000, 6350, 0, 140, 89, "Meal Included", "On time", "T2", "30"),

        # Sector 12: BLR -> BOM
        ("IndiGo", "6E 342", "Bengaluru", "BLR", "Mumbai", "BOM", "07:20", "09:05", "1h 45m", 105, "Nonstop", 3200, 700, 3900, 1200, 80, 95, "Fast Direct", "On time", "T1", "11"),
        ("Akasa Air", "QP 1106", "Bengaluru", "BLR", "Mumbai", "BOM", "19:00", "20:45", "1h 45m", 105, "Nonstop", 2950, 700, 3650, 1300, 78, 97, "Night Link", "On time", "T1", "06"),

        # Sector 13: BLR -> HYD
        ("IndiGo", "6E 448", "Bengaluru", "BLR", "Hyderabad", "HYD", "07:30", "08:40", "1h 10m", 70, "Nonstop", 3150, 700, 3850, 1200, 54, 96, "High frequency", "On time", "T1", "05"),
        ("Air India", "AI 512", "Bengaluru", "BLR", "Hyderabad", "HYD", "12:15", "13:30", "1h 15m", 75, "Nonstop", 3500, 700, 4200, 0, 60, 92, "Bag included", "On time", "T2", "12"),
        ("SpiceJet", "SG 1084", "Bengaluru", "BLR", "Hyderabad", "HYD", "18:40", "19:55", "1h 15m", 75, "Nonstop", 2850, 700, 3550, 1300, 58, 88, "Budget pick", "Delayed 20m", "T1", "03"),

        # Sector 14: BLR -> MAA
        ("IndiGo", "6E 471", "Bengaluru", "BLR", "Chennai", "MAA", "08:00", "09:00", "1h 00m", 60, "Nonstop", 2400, 600, 3000, 1200, 45, 96, "South Shuttle", "On time", "T1", "04"),
        ("Air India Express", "IX 611", "Bengaluru", "BLR", "Chennai", "MAA", "16:30", "17:35", "1h 05m", 65, "Nonstop", 2250, 600, 2850, 1100, 44, 98, "Quick Hopper", "On time", "T1", "02"),

        # Sector 15: HYD -> DEL
        ("IndiGo", "6E 203", "Hyderabad", "HYD", "Delhi", "DEL", "06:15", "08:25", "2h 10m", 130, "Nonstop", 4340, 900, 5240, 1200, 82, 94, "Best value", "On time", "T2", "14A"),
        ("Air India", "AI 541", "Hyderabad", "HYD", "Delhi", "DEL", "08:10", "10:35", "2h 25m", 145, "Nonstop", 4880, 900, 5780, 0, 95, 91, "Bag included", "On time", "T3", "22B"),
        ("Akasa Air", "QP 1412", "Hyderabad", "HYD", "Delhi", "DEL", "11:20", "13:40", "2h 20m", 140, "Nonstop", 4080, 900, 4980, 1500, 78, 92, "Low fare", "On time", "T1", "04"),
        ("SpiceJet", "SG 401", "Hyderabad", "HYD", "Delhi", "DEL", "15:30", "18:55", "3h 25m", 205, "1 stop", 3720, 900, 4620, 1400, 112, 78, "Cheapest", "Delayed 15m", "T2", "09"),
        ("Air India Express", "IX 992", "Hyderabad", "HYD", "Delhi", "DEL", "21:40", "23:55", "2h 15m", 135, "Nonstop", 4200, 850, 5050, 1100, 80, 90, "Late night saver", "On time", "T1", "02C"),

        # Sector 16: HYD -> BOM
        ("IndiGo", "6E 522", "Hyderabad", "HYD", "Mumbai", "BOM", "07:30", "08:55", "1h 25m", 85, "Nonstop", 2890, 650, 3540, 1200, 62, 95, "Morning Hop", "On time", "T2", "11"),
        ("Air India", "AI 618", "Hyderabad", "HYD", "Mumbai", "BOM", "18:15", "19:45", "1h 30m", 90, "Nonstop", 3300, 650, 3950, 0, 65, 92, "Full Service", "On time", "T2", "21"),

        # Sector 17: HYD -> BLR
        ("IndiGo", "6E 449", "Hyderabad", "HYD", "Bengaluru", "BLR", "09:15", "10:25", "1h 10m", 70, "Nonstop", 3100, 700, 3800, 1200, 54, 96, "Direct Commuter", "On time", "T2", "08"),
        ("Akasa Air", "QP 1352", "Hyderabad", "HYD", "Bengaluru", "BLR", "17:00", "18:10", "1h 10m", 70, "Nonstop", 2850, 700, 3550, 1300, 52, 97, "Eco Link", "On time", "T1", "05"),

        # Sector 18: MAA -> DEL
        ("IndiGo", "6E 611", "Chennai", "MAA", "Delhi", "DEL", "06:40", "09:30", "2h 50m", 170, "Nonstop", 5780, 1000, 6780, 1200, 145, 87, "Fastest link", "On time", "T1", "17"),
        ("Air India", "AI 440", "Chennai", "MAA", "Delhi", "DEL", "14:20", "17:15", "2h 55m", 175, "Nonstop", 6100, 1000, 7100, 0, 150, 85, "Bag included", "On time", "T4", "26"),

        # Sector 19: MAA -> BLR
        ("IndiGo", "6E 472", "Chennai", "MAA", "Bengaluru", "BLR", "09:40", "10:40", "1h 00m", 60, "Nonstop", 2350, 600, 2950, 1200, 45, 96, "South Hopper", "On time", "T1", "07"),
        ("Akasa Air", "QP 1280", "Chennai", "MAA", "Bengaluru", "BLR", "18:20", "19:25", "1h 05m", 65, "Nonstop", 2190, 600, 2790, 1300, 43, 98, "Value Hop", "On time", "T1", "03"),

        # Sector 20: CCU -> DEL
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

    # =========================================================================
    # 4. Route Intelligence Catalog: 12 Key Domestic Sectors
    # =========================================================================
    cursor.execute("DELETE FROM routes")
    routes_data = [
        ("DEL-BOM", "Delhi (DEL)", "Mumbai (BOM)", 132.4, 14.2, 4820, 82, "High Demand"),
        ("DEL-BLR", "Delhi (DEL)", "Bengaluru (BLR)", 127.8, 9.8, 6050, 71, "Watch"),
        ("DEL-HYD", "Delhi (DEL)", "Hyderabad (HYD)", 125.1, 5.4, 5100, 60, "Stable"),
        ("DEL-MAA", "Delhi (DEL)", "Chennai (MAA)", 135.7, 16.1, 6600, 88, "High Demand"),
        ("DEL-GOI", "Delhi (DEL)", "Goa (GOI)", 130.2, 12.0, 5800, 78, "Surge Window"),
        ("DEL-CCU", "Delhi (DEL)", "Kolkata (CCU)", 129.2, 8.4, 5750, 68, "Watch"),
        ("BOM-DEL", "Mumbai (BOM)", "Delhi (DEL)", 131.8, 13.5, 4920, 80, "High Demand"),
        ("BOM-BLR", "Mumbai (BOM)", "Bengaluru (BLR)", 122.4, -2.1, 3680, 48, "Stable"),
        ("BOM-HYD", "Mumbai (BOM)", "Hyderabad (HYD)", 120.9, -1.5, 3350, 42, "Optimal"),
        ("BOM-GOI", "Mumbai (BOM)", "Goa (GOI)", 119.5, -3.4, 3400, 52, "Stable"),
        ("BLR-HYD", "Bengaluru (BLR)", "Hyderabad (HYD)", 124.3, -1.2, 3850, 44, "Stable"),
        ("PNQ-DEL", "Pune (PNQ)", "Delhi (DEL)", 131.0, 11.5, 5650, 74, "High Demand")
    ]
    cursor.executemany("""
        INSERT INTO routes (route_code, origin, destination, index_value, change_30d, avg_fare, volatility_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, routes_data)

    # =========================================================================
    # 5. Price Alerts: 10 Realistic Alert Watchers
    # =========================================================================
    cursor.execute("DELETE FROM alerts")
    alerts_data = [
        ("guest", "DEL → BOM", "₹4,820", "Drop below ₹4,200", 1),
        ("guest", "DEL → BLR", "₹6,050", "Drop below ₹5,500", 1),
        ("guest", "HYD → DEL", "₹5,240", "Drop below ₹4,800", 1),
        ("guest", "BLR → HYD", "₹3,850", "Drop below ₹3,200", 1),
        ("guest", "BOM → GOI", "₹3,400", "Drop below ₹3,000", 1),
        ("guest", "DEL → GOI", "₹5,800", "Drop below ₹5,000", 1),
        ("guest", "MAA → DEL", "₹6,780", "Any price change", 1),
        ("guest", "CCU → DEL", "₹5,900", "Drop below ₹5,200", 1),
        ("guest", "BOM → BLR", "₹3,680", "Drop below ₹3,200", 1),
        ("guest", "BLR → MAA", "₹2,850", "Drop below ₹2,500", 1)
    ]
    cursor.executemany("""
        INSERT INTO alerts (user_id, route, current_fare, target_condition, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, alerts_data)

    # =========================================================================
    # 6. Historical Index Data (20+ Points across 30D, 90D, 1Y)
    # =========================================================================
    cursor.execute("DELETE FROM index_history")
    index_data = [
        ("30D", "Day -30", 121.2, 0),
        ("30D", "Day -25", 122.8, 0),
        ("30D", "Day -20", 125.1, 0),
        ("30D", "Day -15", 124.6, 0),
        ("30D", "Day -10", 127.3, 0),
        ("30D", "Day -5", 128.0, 0),
        ("30D", "Current", 128.6, 0),
        ("90D", "Month -3", 114.2, 0),
        ("90D", "Month -2.5", 116.4, 0),
        ("90D", "Month -2", 119.8, 0),
        ("90D", "Month -1.5", 122.5, 0),
        ("90D", "Month -1", 125.7, 0),
        ("90D", "Current", 128.6, 0),
        ("1Y", "Q1 '25", 108.2, 0),
        ("1Y", "Q2 '25", 112.5, 0),
        ("1Y", "Q3 '25", 118.9, 0),
        ("1Y", "Q4 '25", 123.4, 0),
        ("1Y", "Q1 '26", 128.6, 0),
        ("1Y", "Q2 '26 (Proj)", 131.2, 1),
        ("1Y", "Q3 '26 (Proj)", 134.5, 1)
    ]
    cursor.executemany("""
        INSERT INTO index_history (period, label, value, is_projected)
        VALUES (?, ?, ?, ?)
    """, index_data)

    # =========================================================================
    # 7. Elasticity Points (Advance Purchase Windows)
    # =========================================================================
    cursor.execute("DELETE FROM elasticity")
    elasticity_data = [
        ("DEL-BOM", "T+1", 8400, "HIGH"),
        ("DEL-BOM", "T+7", 6900, "MODERATE"),
        ("DEL-BOM", "T+15", 5800, "BALANCED"),
        ("DEL-BOM", "T+30", 4390, "OPTIMAL"),
        ("DEL-BOM", "T+45", 3980, "LOW"),
        ("DEL-BLR", "T+1", 9200, "HIGH"),
        ("DEL-BLR", "T+7", 7800, "MODERATE"),
        ("DEL-BLR", "T+15", 6400, "BALANCED"),
        ("DEL-BLR", "T+30", 5800, "OPTIMAL"),
        ("DEL-BLR", "T+45", 5200, "LOW")
    ]
    cursor.executemany("""
        INSERT INTO elasticity (route_code, advance_window, fare, sensitivity)
        VALUES (?, ?, ?, ?)
    """, elasticity_data)

    # =========================================================================
    # 8. Refunds Seed Data: 10 Realistic Demo Refund Claims
    # =========================================================================
    cursor.execute("DELETE FROM refunds")
    refunds_data = [
        ("guest", "AIRX789", "Rahul Sharma", "IndiGo", "6E 203", "HYD ➔ DEL", 5240, 999, 4241, "UPI / Google Pay", "UPI/428901239842", "Credited", 5, "2026-08-28", "2026-08-31"),
        ("guest", "6E9021", "Priya Patel", "IndiGo", "6E 214", "DEL ➔ BOM", 4820, 1200, 3620, "HDFC Credit Card", "ARN890213894102", "Processing", 4, "2026-09-02", "2026-09-07"),
        ("guest", "AI3481", "Ananya Reddy", "Air India", "AI 541", "HYD ➔ DEL", 5780, 800, 4980, "Net Banking (SBI)", "ARN112938472910", "Approved", 3, "2026-09-03", "2026-09-09"),
        ("guest", "QP1502", "Vikram Singh", "Akasa Air", "QP 1502", "DEL ➔ BLR", 5800, 1500, 4300, "ICICI Debit Card", "PENDING-GATEWAY", "Initiated", 1, "2026-09-04", "2026-09-11"),
        ("guest", "DEMO-REF-005", "Demo Passenger 05", "SpiceJet", "SG 8172", "DEL ➔ BOM", 4620, 1400, 3220, "Axis Bank Credit Card", "ARN445892019283", "Approved", 3, "2026-09-01", "2026-09-06"),
        ("guest", "DEMO-REF-006", "Demo Passenger 06", "Air India Express", "IX 992", "HYD ➔ DEL", 5050, 1100, 3950, "Paytm UPI", "UPI/889201948201", "Credited", 5, "2026-08-25", "2026-08-29"),
        ("guest", "DEMO-REF-007", "Demo Passenger 07", "IndiGo", "6E 534", "BOM ➔ GOI", 3630, 850, 2780, "Kotak Debit Card", "ARN772819039182", "Processing", 4, "2026-09-03", "2026-09-08"),
        ("guest", "DEMO-REF-008", "Demo Passenger 08", "Air India", "AI 864", "DEL ➔ BOM", 5250, 0, 5250, "Refund Voucher", "VOUCHER-AI-991", "Credited", 5, "2026-08-20", "2026-08-21"),
        ("guest", "DEMO-REF-009", "Demo Passenger 09", "Akasa Air", "QP 1205", "BOM ➔ GOI", 3400, 1300, 2100, "PhonePe UPI", "UPI/991029384756", "Initiated", 2, "2026-09-05", "2026-09-12"),
        ("guest", "DEMO-REF-010", "Demo Passenger 10", "SpiceJet", "SG 401", "HYD ➔ DEL", 4620, 4620, 0, "No-Show Non-Refundable", "NON-REF-SG-401", "Rejected", 1, "2026-08-15", "2026-08-16")
    ]
    cursor.executemany("""
        INSERT INTO refunds (
            user_id, pnr, passenger_name, airline, flight_no, sector, total_fare,
            cancellation_fee, refund_amount, payment_method, arn_number,
            status, stage, cancellation_date, expected_credit_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, refunds_data)

    # =========================================================================
    # 9. Saved Flights Watchlist: 10 Realistic Demo Tracked Flights
    # =========================================================================
    cursor.execute("DELETE FROM saved_flights")
    saved_data = [
        ("guest", "6E 214", "DEL", "BOM", "2026-09-15", 4820),
        ("guest", "AI 864", "DEL", "BOM", "2026-09-15", 5250),
        ("guest", "QP 1320", "DEL", "BOM", "2026-09-15", 4390),
        ("guest", "6E 2131", "DEL", "BLR", "2026-09-18", 6050),
        ("guest", "QP 1502", "DEL", "BLR", "2026-09-18", 5800),
        ("guest", "6E 203", "HYD", "DEL", "2026-09-20", 5240),
        ("guest", "AI 541", "HYD", "DEL", "2026-09-20", 5780),
        ("guest", "6E 534", "BOM", "GOI", "2026-09-25", 3630),
        ("guest", "6E 448", "BLR", "HYD", "2026-09-22", 3850),
        ("guest", "6E 611", "MAA", "DEL", "2026-09-28", 6780)
    ]
    cursor.executemany("""
        INSERT INTO saved_flights (user_id, flight_no, origin_code, destination_code, travel_date, observed_fare)
        VALUES (?, ?, ?, ?, ?, ?)
    """, saved_data)

    # =========================================================================
    # 10. Demo Bookings / My Trips: 10 Safe Development Bookings
    # =========================================================================
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM booking_passengers")
    
    bookings_data = [
        (
            "DEMO-BOOK-101", "DEMO-AIRX-101", "guest", "flight", None, "6E 214", "IndiGo", "DEL ➔ BOM", "DEL", "BOM",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 01", "demo1@airfarex.dev", "+919876543201",
            "2026-09-15", 1, 4020, 800, 0, 4820, "INR", "PAID", "CONFIRMED", "order_demo_101", "pay_demo_101", "12A", "DEMO-PNR-01"
        ),
        (
            "DEMO-BOOK-102", "DEMO-AIRX-102", "guest", "flight", None, "AI 864", "Air India", "DEL ➔ BOM", "DEL", "BOM",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 02", "demo2@airfarex.dev", "+919876543202",
            "2026-09-16", 1, 4450, 800, 0, 5250, "INR", "PAID", "CONFIRMED", "order_demo_102", "pay_demo_102", "14F", "DEMO-PNR-02"
        ),
        (
            "DEMO-BOOK-103", "DEMO-AIRX-103", "guest", "flight", None, "QP 1502", "Akasa Air", "DEL ➔ BLR", "DEL", "BLR",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 03", "demo3@airfarex.dev", "+919876543203",
            "2026-09-18", 2, 9600, 2000, 0, 11600, "INR", "PAID", "CONFIRMED", "order_demo_103", "pay_demo_103", "6B, 6C", "DEMO-PNR-03"
        ),
        (
            "DEMO-BOOK-104", "DEMO-AIRX-104", "guest", "flight", None, "6E 203", "IndiGo", "HYD ➔ DEL", "HYD", "DEL",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 04", "demo4@airfarex.dev", "+919876543204",
            "2026-09-20", 1, 4340, 900, 0, 5240, "INR", "PAYMENT_PENDING", "PENDING_PAYMENT", "order_demo_104", None, None, "DEMO-PNR-04"
        ),
        (
            "DEMO-BOOK-105", "DEMO-AIRX-105", "guest", "flight", None, "6E 534", "IndiGo", "BOM ➔ GOI", "BOM", "GOI",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 05", "demo5@airfarex.dev", "+919876543205",
            "2026-09-25", 1, 2980, 650, 0, 3630, "INR", "PAID", "CONFIRMED", "order_demo_105", "pay_demo_105", "8D", "DEMO-PNR-05"
        ),
        (
            "DEMO-BOOK-106", "DEMO-AIRX-106", "guest", "flight", None, "SG 8172", "SpiceJet", "DEL ➔ BOM", "DEL", "BOM",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 06", "demo6@airfarex.dev", "+919876543206",
            "2026-08-10", 1, 3820, 800, 0, 4620, "INR", "PAID", "CONFIRMED", "order_demo_106", "pay_demo_106", "18A", "DEMO-PNR-06"
        ),
        (
            "DEMO-BOOK-107", "DEMO-AIRX-107", "guest", "package", "tour-goa-3d", None, None, "DEL ➔ GOI", "DEL", "GOI",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 07", "demo7@airfarex.dev", "+919876543207",
            "2026-10-02", 2, 21998, 0, 0, 21998, "INR", "PAID", "CONFIRMED", "order_demo_107", "pay_demo_107", None, "DEMO-PKG-07"
        ),
        (
            "DEMO-BOOK-108", "DEMO-AIRX-108", "guest", "flight", None, "6E 448", "IndiGo", "BLR ➔ HYD", "BLR", "HYD",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 08", "demo8@airfarex.dev", "+919876543208",
            "2026-09-22", 1, 3150, 700, 0, 3850, "INR", "PAID", "CONFIRMED", "order_demo_108", "pay_demo_108", "3F", "DEMO-PNR-08"
        ),
        (
            "DEMO-BOOK-109", "DEMO-AIRX-109", "guest", "flight", None, "AI 440", "Air India", "MAA ➔ DEL", "MAA", "DEL",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 09", "demo9@airfarex.dev", "+919876543209",
            "2026-09-28", 1, 6100, 1000, 0, 7100, "INR", "REFUNDED", "CANCELLED", "order_demo_109", "pay_demo_109", "22C", "DEMO-PNR-09"
        ),
        (
            "DEMO-BOOK-110", "DEMO-AIRX-110", "guest", "flight", None, "IX 992", "Air India Express", "HYD ➔ DEL", "HYD", "DEL",
            "MockDevelopmentProvider", "DEVELOPMENT", "Demo Passenger 10", "demo10@airfarex.dev", "+919876543210",
            "2026-09-30", 1, 4200, 850, 0, 5050, "INR", "PAID", "CONFIRMED", "order_demo_110", "pay_demo_110", "5A", "DEMO-PNR-10"
        )
    ]
    cursor.executemany("""
        INSERT INTO bookings (
            booking_id, booking_reference, user_id, booking_type, package_id, flight_no, airline,
            sector, origin_code, destination_code, provider, data_source, traveler_name,
            email, phone, travel_date, pax_count, base_fare, taxes, fees, amount, currency,
            payment_status, booking_status, payment_order_id, payment_id, seat_number, pnr
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, bookings_data)

    # 11. Booking Passengers: 12 Itemized Fictional Demo Passengers
    passengers_data = [
        ("DEMO-BOOK-101", "Mr", "Demo", "Passenger 01", "Demo Passenger 01", "demo1@airfarex.dev", "+919876543201", "ADULT", "12A", "Male", 29),
        ("DEMO-BOOK-102", "Ms", "Demo", "Passenger 02", "Demo Passenger 02", "demo2@airfarex.dev", "+919876543202", "ADULT", "14F", "Female", 27),
        ("DEMO-BOOK-103", "Mr", "Demo", "Passenger 03", "Demo Passenger 03", "demo3@airfarex.dev", "+919876543203", "ADULT", "6B", "Male", 34),
        ("DEMO-BOOK-103", "Mrs", "Demo", "Passenger 03B", "Demo Passenger 03B", "demo3b@airfarex.dev", "+919876543203", "ADULT", "6C", "Female", 31),
        ("DEMO-BOOK-104", "Dr", "Demo", "Passenger 04", "Demo Passenger 04", "demo4@airfarex.dev", "+919876543204", "ADULT", "15C", "Male", 45),
        ("DEMO-BOOK-105", "Mr", "Demo", "Passenger 05", "Demo Passenger 05", "demo5@airfarex.dev", "+919876543205", "ADULT", "8D", "Male", 26),
        ("DEMO-BOOK-106", "Ms", "Demo", "Passenger 06", "Demo Passenger 06", "demo6@airfarex.dev", "+919876543206", "ADULT", "18A", "Female", 24),
        ("DEMO-BOOK-107", "Mr", "Demo", "Passenger 07", "Demo Passenger 07", "demo7@airfarex.dev", "+919876543207", "ADULT", "1A", "Male", 38),
        ("DEMO-BOOK-107", "Mrs", "Demo", "Passenger 07B", "Demo Passenger 07B", "demo7b@airfarex.dev", "+919876543207", "ADULT", "1B", "Female", 35),
        ("DEMO-BOOK-108", "Mr", "Demo", "Passenger 08", "Demo Passenger 08", "demo8@airfarex.dev", "+919876543208", "ADULT", "3F", "Male", 30),
        ("DEMO-BOOK-109", "Ms", "Demo", "Passenger 09", "Demo Passenger 09", "demo9@airfarex.dev", "+919876543209", "ADULT", "22C", "Female", 52),
        ("DEMO-BOOK-110", "Mr", "Demo", "Passenger 10", "Demo Passenger 10", "demo10@airfarex.dev", "+919876543210", "ADULT", "5A", "Male", 28)
    ]
    cursor.executemany("""
        INSERT INTO booking_passengers (
            booking_id, title, first_name, last_name, full_name, email, phone, passenger_type, seat_number, gender, age
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, passengers_data)

    conn.commit()
    conn.close()
