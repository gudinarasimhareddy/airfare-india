"""
AirfareX India — Flight Search Service
Coordinates multi-provider dispatch, TTL caching (15 mins), fallback resilience,
and flight result normalization with explicit data source labeling (LIVE / CACHE / DEVELOPMENT).
Strictly protects API credentials and ensures honest data labeling.
"""

import json
import hashlib
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

from backend.database import get_db_connection
from backend.services.flight_providers.base import (
    BaseFlightProvider,
    FlightSearchParams,
    NormalizedFlight,
    NormalizedSearchResponse
)
from backend.services.flight_providers.mock_provider import MockDevelopmentProvider
from backend.services.flight_providers.amadeus_provider import AmadeusFlightProvider

CACHE_TTL_MINUTES = 15
logger = logging.getLogger("airfarex.flight_search")

class FlightSearchService:
    """Core flight search coordinator and caching engine."""

    def __init__(self):
        self.mock_provider = MockDevelopmentProvider()
        self.amadeus_provider = AmadeusFlightProvider()

    def _generate_cache_key(self, params: FlightSearchParams) -> str:
        """Generates a deterministic MD5 hash for a given set of flight search parameters."""
        raw_key = (
            f"{params.origin.strip().upper()}|"
            f"{params.destination.strip().upper()}|"
            f"{params.date or 'any'}|"
            f"{params.return_date or 'none'}|"
            f"{params.cabin.strip().lower()}|"
            f"{params.stops.strip().lower()}|"
            f"{params.airline.strip().lower()}|"
            f"{params.max_price or 0}|"
            f"{params.baggage.strip().lower()}|"
            f"{params.time_of_day.strip().lower()}|"
            f"{params.direct_only}|"
            f"{params.sort_by.strip().lower()}|"
            f"{params.adults}"
        )
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def _get_cached_search(self, cache_key: str) -> Optional[NormalizedSearchResponse]:
        """Looks up valid unexpired search results in the SQLite cache."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                SELECT results_json, provider, data_source, created_at, expires_at 
                FROM flight_search_cache
                WHERE cache_key = ? AND expires_at > ?
                LIMIT 1
            """, (cache_key, now_iso))

            row = cursor.fetchone()
            conn.close()

            if row:
                data = json.loads(row["results_json"])
                try:
                    exp_dt = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    remaining = max(0, int((exp_dt - datetime.now(timezone.utc)).total_seconds()))
                except Exception:
                    remaining = CACHE_TTL_MINUTES * 60

                mins_left = max(1, round(remaining / 60))
                data["cached"] = True
                data["data_source"] = "CACHE"
                data["cache_ttl_remaining_secs"] = remaining
                data["retrieved_at_human"] = f"Cached (refreshes in {mins_left}m)"
                
                for f in data.get("flights", []):
                    f["data_source"] = "CACHE"
                    f["retrieved_at_human"] = f"Cached (refreshes in {mins_left}m)"

                return NormalizedSearchResponse(**data)
        except Exception as e:
            logger.debug(f"Cache lookup warning: {e}")
        return None

    def _save_to_cache(self, cache_key: str, params: FlightSearchParams, resp: NormalizedSearchResponse):
        """Stores search results in SQLite flight_search_cache table with 15-min TTL."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=CACHE_TTL_MINUTES)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            exp_str = expires_at.strftime("%Y-%m-%d %H:%M:%S")

            results_json = resp.model_dump_json() if hasattr(resp, "model_dump_json") else resp.json()

            cursor.execute("""
                INSERT OR REPLACE INTO flight_search_cache (
                    cache_key, origin, destination, departure_date, return_date,
                    cabin_class, adults, provider, data_source, results_json,
                    created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key,
                params.origin,
                params.destination,
                params.date,
                params.return_date,
                params.cabin,
                params.adults,
                resp.provider,
                resp.data_source,
                results_json,
                now_str,
                exp_str
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Cache save warning: {e}")

    def clear_cache(self) -> int:
        """Clears all cached flight searches."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM flight_search_cache")
            count = cursor.rowcount
            conn.commit()
            conn.close()
            return count
        except Exception:
            return 0

    def get_provider_status(self) -> Dict[str, Any]:
        """
        Returns active provider status, cache health, and data source mode.
        Ensures credentials and secrets are NEVER returned.
        """
        amadeus_ready = self.amadeus_provider.is_configured()
        active = "AmadeusFlightProvider" if amadeus_ready else "MockDevelopmentProvider"
        source = "LIVE" if amadeus_ready else "DEVELOPMENT"
        flight_provider_name = "Amadeus" if amadeus_ready else "MockDevelopmentProvider"
        hostname = self.amadeus_provider.get_hostname()

        return {
            "active_provider": active,
            "flight_provider": flight_provider_name,
            "data_source_mode": source,
            "configured": amadeus_ready,
            "environment": hostname,
            "amadeus_configured": amadeus_ready,
            "amadeus_environment": hostname,
            "amadeus_readiness": "CONFIGURED" if amadeus_ready else "UNCONFIGURED_CREDENTIALS_REQUIRED",
            "live_enabled": amadeus_ready,
            "cache_enabled": True,
            "cache_ttl_seconds": CACHE_TTL_MINUTES * 60,
            "supported_providers": [
                "MockDevelopmentProvider",
                "AmadeusFlightProvider"
            ],
            "booking_provider": {
                "configured": False,
                "ticketing_enabled": False,
                "provider_name": "None (Development Booking)",
                "notice": "Development booking mode — airline ticket issuance requires authorized GDS/NDC connection."
            },
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    async def search_flights(self, params: FlightSearchParams, bypass_cache: bool = False) -> NormalizedSearchResponse:
        """
        Executes flight search:
        1. Checks 15-minute TTL cache (returns data_source='CACHE' on hit)
        2. Dispatches to active provider (Amadeus if configured, else MockDevelopmentProvider)
        3. Labels fresh results as 'LIVE' or 'DEVELOPMENT'
        4. Saves fresh results to cache
        """
        cache_key = self._generate_cache_key(params)

        # 1. Check Cache
        if not bypass_cache:
            cached_resp = self._get_cached_search(cache_key)
            if cached_resp:
                return cached_resp

        # 2. Cache Miss: Dispatch to Active Provider
        if self.amadeus_provider.is_configured():
            try:
                live_resp = await self.amadeus_provider.search_flights(params)
                self._save_to_cache(cache_key, params, live_resp)
                return live_resp
            except Exception as e:
                logger.warning(f"Amadeus live provider query failed: {e}")
                env = os.environ.get("ENVIRONMENT", "development").lower()
                if env == "production":
                    # In production without fallback, try stale cache or return honest error
                    raise RuntimeError("Live flight data is temporarily unavailable.")
                # In development mode, allow fallback to development catalog
                logger.info("Falling back to development provider in non-production mode")

        # Fallback to Mock Development Provider
        mock_resp = await self.mock_provider.search_flights(params)
        self._save_to_cache(cache_key, params, mock_resp)
        return mock_resp

# Global singleton instance
flight_search_service = FlightSearchService()
