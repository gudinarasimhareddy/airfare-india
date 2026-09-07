"""
AirfareX India — Master Airport Autocomplete Service
Provides fast autocomplete indexing and search for all major Indian domestic airports,
with optional live Amadeus location lookup when configured.
"""

from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.supabase_client import get_airports_from_supabase

class AirportService:
    """Airport search and autocomplete indexing service."""

    async def autocomplete(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Searches airports by IATA code, city, or airport name with relevance sorting:
        1. Exact IATA match
        2. City prefix match
        3. Name / state substring match
        4. Optional Amadeus live location integration when configured
        """
        clean_q = (query or "").strip().upper()
        if not clean_q:
            return await self.list_all(limit=limit)

        # Optional live Amadeus autocomplete if active
        try:
            from backend.services.flight_search_service import flight_search_service
            if flight_search_service.amadeus_provider.is_configured():
                amadeus_results = await flight_search_service.amadeus_provider.autocomplete_airports(clean_q, limit=limit)
                if amadeus_results:
                    return amadeus_results[:limit]
        except Exception:
            pass

        # Try fetching from Supabase or fallback to SQLite
        supa_airports = await get_airports_from_supabase()
        airports_list: List[Dict[str, Any]] = []

        if supa_airports:
            airports_list = supa_airports
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT iata_code, icao_code, name, city, state, country FROM airports")
                rows = cursor.fetchall()
                airports_list = [dict(r) for r in rows]
                conn.close()
            except Exception:
                airports_list = []

        # Ranking logic
        exact_matches = []
        prefix_matches = []
        other_matches = []

        for ap in airports_list:
            iata = ap.get("iata_code", "").upper()
            city = ap.get("city", "").upper()
            name = ap.get("name", "").upper()
            state = ap.get("state", "").upper()

            item = {
                "iata_code": ap.get("iata_code"),
                "icao_code": ap.get("icao_code"),
                "name": ap.get("name"),
                "city": ap.get("city"),
                "state": ap.get("state"),
                "country": ap.get("country", "India"),
                "display_label": f"{ap.get('city')} ({ap.get('iata_code')}) - {ap.get('name')}",
                "short_label": f"{ap.get('city')} ({ap.get('iata_code')})"
            }

            if iata == clean_q:
                exact_matches.append(item)
            elif city.startswith(clean_q) or iata.startswith(clean_q):
                prefix_matches.append(item)
            elif clean_q in city or clean_q in name or clean_q in state or clean_q in iata:
                other_matches.append(item)

        results = exact_matches + prefix_matches + other_matches
        return results[:limit]

    async def list_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns all monitored Indian domestic airports."""
        supa_airports = await get_airports_from_supabase()
        if supa_airports:
            return supa_airports[:limit] if limit else supa_airports

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT iata_code, icao_code, name, city, state, country FROM airports ORDER BY city ASC")
        rows = cursor.fetchall()
        conn.close()
        res = [dict(r) for r in rows]
        for item in res:
            item["display_label"] = f"{item.get('city')} ({item.get('iata_code')}) - {item.get('name')}"
            item["short_label"] = f"{item.get('city')} ({item.get('iata_code')})"
        return res[:limit] if limit else res

airport_service = AirportService()
