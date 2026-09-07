"""
AirfareX India — Natural Language Flight Query Interpreter
Parses conversational traveler queries into structured, validated search parameters.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from backend.services.ai.base import NLSearchParams

# Comprehensive Indian domestic city / airport mapping
AIRPORT_MAP = {
    "delhi": "DEL", "del": "DEL", "new delhi": "DEL", "igi": "DEL", "दिल्ली": "DEL", "ఢిల్లీ": "DEL", "டெல்லி": "DEL",
    "mumbai": "BOM", "bom": "BOM", "bombay": "BOM", "csmia": "BOM", "मुंबई": "BOM", "ముంబై": "BOM", "மும்பை": "BOM",
    "bengaluru": "BLR", "bangalore": "BLR", "blr": "BLR", "kempegowda": "BLR", "बेंगलुरु": "BLR", "బెంగళూరు": "BLR", "பெங்களூரு": "BLR",
    "hyderabad": "HYD", "hyd": "HYD", "rgia": "HYD", "हैदराबाद": "HYD", "హైదరాబాద్": "HYD", "ஹைதராபாத்": "HYD",
    "goa": "GOI", "goi": "GOI", "mopa": "GOI", "dabolim": "GOI", "gox": "GOI", "गोवा": "GOI", "గోవా": "GOI",
    "kolkata": "CCU", "ccu": "CCU", "calcutta": "CCU", "कोलकाता": "CCU", "కోల్‌కతా": "CCU", "கொல்கத்தா": "CCU",
    "chennai": "MAA", "maa": "MAA", "madras": "MAA", "चेन्नई": "MAA", "చెన్నై": "MAA", "சென்னை": "MAA",
    "pune": "PNQ", "pnq": "PNQ", "पुणे": "PNQ", "పుణే": "PNQ",
    "jaipur": "JAI", "jai": "JAI", "जयपुर": "JAI", "జైపూర్": "JAI",
    "ahmedabad": "AMD", "amd": "AMD", "अहमदाबाद": "AMD",
    "kochi": "COK", "cok": "COK", "cochin": "COK", "कोच्चि": "COK",
    "guwahati": "GAU", "gau": "GAU", "गुवाहाटी": "GAU",
    "lucknow": "LKO", "lko": "LKO", "लखनऊ": "LKO",
    "varanasi": "VNS", "vns": "VNS", "वाराणसी": "VNS",
    "srinagar": "SXR", "sxr": "SXR", "श्रीनगर": "SXR",
    "chandigarh": "IXC", "ixc": "IXC", "चंडीगढ़": "IXC"
}

AIRLINE_NAMES = {
    "indigo": "IndiGo", "6e": "IndiGo",
    "air india": "Air India", "ai": "Air India",
    "akasa": "Akasa Air", "qp": "Akasa Air",
    "spicejet": "SpiceJet", "sg": "SpiceJet",
    "air india express": "Air India Express", "express": "Air India Express", "ix": "Air India Express",
    "star air": "Star Air", "s5": "Star Air",
    "vistara": "Air India", "uk": "Air India"
}

MONTHS_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

WEEKDAYS_MAP = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6
}

class NLSearchInterpreter:
    """Parses natural-language queries into structured, verified search parameters."""

    @classmethod
    def parse_query(cls, query: str) -> NLSearchParams:
        text = query.strip()
        text_lower = text.lower()

        # Sanitize potential prompt injection markers
        clean_text = re.sub(r'[\<\>\{\}\[\];`]', ' ', text_lower)

        # 1. Sector Extraction (Origin & Destination)
        origin, destination = cls._extract_sector(clean_text)

        # 2. Date Extraction
        target_date = cls._extract_date(clean_text)

        # 3. Max Price Extraction
        max_price = cls._extract_max_price(clean_text)

        # 4. Stops Filter Extraction
        stops = "Any"
        if any(w in clean_text for w in ["nonstop", "non-stop", "direct", "0 stop", "no stop", "without stop"]):
            stops = "Nonstop"
        elif any(w in clean_text for w in ["1 stop", "one stop", "single stop"]):
            stops = "1 stop"

        # 5. Cabin Class
        cabin = "Economy"
        if any(w in clean_text for w in ["business", "business class", "biz"]):
            cabin = "Business"

        # 6. Time of Day
        time_of_day = "Any time"
        if any(w in clean_text for w in ["morning", "early morning", "am flight", "sunrise"]):
            time_of_day = "Morning"
        elif any(w in clean_text for w in ["afternoon", "midday", "noon"]):
            time_of_day = "Afternoon"
        elif any(w in clean_text for w in ["evening", "night", "late night", "pm flight", "sunset"]):
            time_of_day = "Evening"

        # 7. Airline Filter
        airline = "All airlines"
        for key, full_name in AIRLINE_NAMES.items():
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, clean_text):
                airline = full_name
                break

        # 8. User Preference
        pref = "best_value"
        if any(w in clean_text for w in ["cheapest", "lowest price", "cheap", "budget", "lowest fare", "least expensive"]):
            pref = "lowest_price"
        elif any(w in clean_text for w in ["fastest", "quickest", "shortest", "time than price", "care more about time", "least time"]):
            pref = "fastest"
        elif stops == "Nonstop":
            pref = "nonstop"

        # 9. Clarification Check
        clarification_needed = False
        clarification_msg = None

        if not origin and not destination:
            clarification_needed = True
            clarification_msg = "Please specify your departure and destination cities (e.g., 'Flights from Delhi to Mumbai')."
        elif not origin:
            clarification_needed = True
            clarification_msg = f"Which city are you departing from to reach {destination}?"
        elif not destination:
            clarification_needed = True
            clarification_msg = f"Where would you like to fly to from {origin}?"
        elif origin == destination:
            clarification_needed = True
            clarification_msg = "Origin and destination cannot be the same city. Please provide distinct cities."

        return NLSearchParams(
            origin=origin,
            destination=destination,
            date=target_date,
            max_price=max_price,
            stops=stops,
            cabin=cabin,
            time_of_day=time_of_day,
            airline=airline,
            preference=pref,
            confidence=95 if (origin and destination and not clarification_needed) else 60,
            clarification_needed=clarification_needed,
            clarification_message=clarification_msg,
            raw_query=query
        )

    @classmethod
    def _extract_sector(cls, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extracts origin and destination using positional markers and city lookup."""
        # Pattern 1: from X to Y
        from_to_match = re.search(r'\b(?:from|origin|leaving)\s+([a-zA-Z\s]+?)\s+(?:to|destination|reaching)\s+([a-zA-Z\s]+?)(?:\s+(?:on|under|tomorrow|today|next|under|with|for|\d)|$)', text)
        if from_to_match:
            from_str = from_to_match.group(1).strip()
            to_str = from_to_match.group(2).strip()
            orig = cls._match_airport(from_str)
            dest = cls._match_airport(to_str)
            if orig and dest:
                return orig, dest

        # Pattern 2: X to Y (e.g. "Delhi to Mumbai", "DEL to BOM", "DEL-BOM", "DEL -> BOM")
        dash_match = re.search(r'\b([a-zA-Z\s]+?)\s*(?:->|-->|to|-|➔)\s*([a-zA-Z\s]+?)(?:\s+(?:on|under|tomorrow|today|next|under|for|\d)|$)', text)
        if dash_match:
            from_str = dash_match.group(1).strip()
            to_str = dash_match.group(2).strip()
            orig = cls._match_airport(from_str)
            dest = cls._match_airport(to_str)
            if orig and dest:
                return orig, dest

        # Pattern 3: Sequential detection of known cities
        found_airports = []
        for word, code in AIRPORT_MAP.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text):
                # find start index
                idx = text.find(word)
                if code not in [c[1] for c in found_airports]:
                    found_airports.append((idx, code))

        found_airports.sort(key=lambda x: x[0])
        if len(found_airports) >= 2:
            return found_airports[0][1], found_airports[1][1]
        elif len(found_airports) == 1:
            # If query mentions "flights to Goa", dest is GOI
            if "to " in text:
                return None, found_airports[0][1]
            return found_airports[0][1], None

        return None, None

    @classmethod
    def _match_airport(cls, term: str) -> Optional[str]:
        term = term.strip().lower()
        if term in AIRPORT_MAP:
            return AIRPORT_MAP[term]
        for key, code in AIRPORT_MAP.items():
            if key in term:
                return code
        return None

    @classmethod
    def _extract_date(cls, text: str) -> Optional[str]:
        now = datetime.now()

        # Relative keywords
        if "tomorrow" in text:
            return (now + timedelta(days=1)).strftime("%Y-%m-%d")
        if "day after tomorrow" in text:
            return (now + timedelta(days=2)).strftime("%Y-%m-%d")
        if "today" in text or "tonight" in text:
            return now.strftime("%Y-%m-%d")

        # "next monday", "this friday"
        for w_name, w_idx in WEEKDAYS_MAP.items():
            if f"next {w_name}" in text or f"this {w_name}" in text or f"on {w_name}" in text or f"coming {w_name}" in text:
                cur_w = now.weekday()
                days_ahead = (w_idx - cur_w) % 7
                if days_ahead == 0 or f"next {w_name}" in text:
                    days_ahead += 7
                return (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        # Specific dates: "15 September", "Sep 15", "15th Oct"
        date_pattern = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([a-zA-Z]+)(?:\s+(\d{4}))?\b', text)
        if date_pattern:
            day = int(date_pattern.group(1))
            month_str = date_pattern.group(2).lower()
            year = int(date_pattern.group(3)) if date_pattern.group(3) else now.year
            if month_str in MONTHS_MAP:
                month = MONTHS_MAP[month_str]
                try:
                    target_dt = datetime(year, month, day)
                    if target_dt < now:
                        target_dt = datetime(year + 1, month, day)
                    return target_dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # ISO format: 2026-09-15
        iso_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
        if iso_match:
            try:
                target_dt = datetime.strptime(iso_match.group(1), "%Y-%m-%d")
                if target_dt >= now - timedelta(days=1):
                    return iso_match.group(1)
            except ValueError:
                pass

        # Default to 7 days ahead
        return (now + timedelta(days=7)).strftime("%Y-%m-%d")

    @classmethod
    def _extract_max_price(cls, text: str) -> Optional[int]:
        # Matches: "under ₹6000", "< 5000", "below 6k", "under 6,000", "max price 7500"
        price_patterns = [
            r'(?:under|below|less than|within|max|budget of|under\s*₹|₹|<|<=)\s*₹?\s*(\d{1,2}(?:,\d{3})+|\d+)\s*(?:k|thousand)?\b',
            r'\b(\d+)\s*k\b'
        ]

        for p in price_patterns:
            m = re.search(p, text)
            if m:
                val_str = m.group(1).replace(",", "")
                val = int(val_str)
                # If followed by 'k' or matched k pattern
                if "k" in m.group(0).lower() and val < 100:
                    val = val * 1000
                if 500 <= val <= 200000:
                    return val
        return None
