"""
AirfareX India — Amadeus Self-Service Live Flight Provider Adapter
Integrates with Amadeus Flight Offers Search API (v2) and Locations API.
Gracefully disabled when AMADEUS_CLIENT_ID / AMADEUS_CLIENT_SECRET are not configured.
Strictly protects credentials and access tokens — never logs secrets or exposes them to clients.
"""

import os
import httpx
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from backend.services.flight_providers.base import (
    BaseFlightProvider,
    FlightSearchParams,
    NormalizedFlight,
    NormalizedSearchResponse,
    FlightSegment
)

logger = logging.getLogger("airfarex.amadeus")

class AmadeusFlightProvider(BaseFlightProvider):
    """Amadeus Self-Service API Provider Adapter for live flight searches."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        hostname: Optional[str] = None
    ):
        self._custom_client_id = client_id
        self._custom_client_secret = client_secret
        self._custom_hostname = hostname
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    @property
    def client_id(self) -> str:
        if self._custom_client_id is not None:
            return self._custom_client_id.strip()
        return os.environ.get("AMADEUS_CLIENT_ID", "").strip()

    @client_id.setter
    def client_id(self, val: str):
        self._custom_client_id = val

    @property
    def client_secret(self) -> str:
        if self._custom_client_secret is not None:
            return self._custom_client_secret.strip()
        return os.environ.get("AMADEUS_CLIENT_SECRET", "").strip()

    @client_secret.setter
    def client_secret(self, val: str):
        self._custom_client_secret = val

    @property
    def base_url(self) -> str:
        custom_url = os.environ.get("AMADEUS_BASE_URL", "").strip().rstrip("/")
        if custom_url:
            return custom_url
        hostname = (self._custom_hostname or os.environ.get("AMADEUS_HOSTNAME", "test")).lower().strip()
        if hostname in ["production", "prod", "api"]:
            return "https://api.amadeus.com"
        return "https://test.api.amadeus.com"

    def get_hostname(self) -> str:
        """Returns 'production' or 'test' environment indicator."""
        url = self.base_url
        if "test.api.amadeus.com" in url:
            return "test"
        if "api.amadeus.com" in url:
            return "production"
        return (self._custom_hostname or os.environ.get("AMADEUS_HOSTNAME", "test")).lower().strip()

    def get_name(self) -> str:
        return "AmadeusFlightProvider"

    def is_configured(self) -> bool:
        """Returns True only when valid non-placeholder Amadeus credentials exist."""
        cid = self.client_id
        sec = self.client_secret
        if not cid or not sec:
            return False
        # Disallow default placeholders
        forbidden = ["your_amadeus", "replace_with", "placeholder", "dummy", "api_key", "api_secret"]
        if any(f in cid.lower() for f in forbidden) or any(f in sec.lower() for f in forbidden):
            return False
        return True

    async def get_access_token(self) -> Optional[str]:
        """Public accessor for fetching/refreshing OAuth2 token."""
        return await self._get_access_token()

    async def _get_access_token(self) -> Optional[str]:
        """Fetches or refreshes OAuth2 token securely without logging secrets."""
        if not self.is_configured():
            return None

        # Check existing cached token validity (with 60s safety buffer)
        now_utc = datetime.now(timezone.utc)
        if self._access_token and self._token_expires_at and now_utc < self._token_expires_at:
            return self._access_token

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    f"{self.base_url}/v1/security/oauth2/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    self._access_token = data.get("access_token")
                    expires_in = data.get("expires_in", 1799)
                    self._token_expires_at = now_utc + timedelta(seconds=expires_in - 60)
                    return self._access_token
                else:
                    logger.warning(f"Amadeus OAuth2 token authentication returned HTTP {res.status_code}")
        except Exception as e:
            logger.warning(f"Amadeus OAuth2 token request connection error: {type(e).__name__}")
        return None

    def _extract_iata_code(self, val: str) -> str:
        """Extracts 3-letter IATA code from airport/city strings like 'Delhi (DEL)'."""
        clean = (val or "").strip().upper()
        if "(" in clean and ")" in clean:
            start = clean.find("(") + 1
            end = clean.find(")")
            code = clean[start:end].strip()
            if len(code) == 3:
                return code
        parts = clean.split()
        for p in parts:
            p_clean = p.replace("(", "").replace(")", "").replace(",", "")
            if len(p_clean) == 3 and p_clean.isalpha():
                return p_clean
        return clean[:3] if len(clean) >= 3 else "DEL"

    def _parse_iso_duration(self, iso_dur: str) -> int:
        """Parses ISO 8601 duration e.g. PT2H15M into total minutes."""
        if not iso_dur:
            return 120
        clean = iso_dur.replace("PT", "")
        hours = 0
        mins = 0
        if "H" in clean:
            h_part, clean = clean.split("H")
            try:
                hours = int(h_part)
            except ValueError:
                hours = 2
        if "M" in clean:
            m_part = clean.replace("M", "")
            if m_part:
                try:
                    mins = int(m_part)
                except ValueError:
                    mins = 15
        return hours * 60 + mins

    async def search_flights(self, params: FlightSearchParams) -> NormalizedSearchResponse:
        """Executes Amadeus Flight Offers Search and normalizes response."""
        if not self.is_configured():
            raise RuntimeError("AmadeusFlightProvider is not configured with active API credentials.")

        token = await self._get_access_token()
        if not token:
            raise RuntimeError("Amadeus authentication failed: Unable to obtain OAuth2 access token.")

        orig_iata = self._extract_iata_code(params.origin)
        dest_iata = self._extract_iata_code(params.destination)
        dep_date = params.date or (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")

        query_params: Dict[str, Any] = {
            "originLocationCode": orig_iata,
            "destinationLocationCode": dest_iata,
            "departureDate": dep_date,
            "adults": max(1, params.adults or 1),
            "travelClass": params.cabin.upper() if params.cabin else "ECONOMY",
            "currencyCode": "INR",
            "max": 20
        }

        if params.return_date:
            query_params["returnDate"] = params.return_date

        if params.direct_only or (params.stops and params.stops.lower() == "nonstop"):
            query_params["nonStop"] = "true"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(
                    f"{self.base_url}/v2/shopping/flight-offers",
                    headers={"Authorization": f"Bearer {token}"},
                    params=query_params
                )
                if res.status_code != 200:
                    logger.warning(f"Amadeus Flight Offers Search returned status {res.status_code}")
                    raise RuntimeError(f"Amadeus Flight Offers Search failed with status {res.status_code}")
                
                raw_data = res.json()
        except Exception as e:
            if not isinstance(e, RuntimeError):
                logger.warning(f"Amadeus search connection error: {type(e).__name__}")
                raise RuntimeError(f"Amadeus search connection failed: {type(e).__name__}")
            raise

        return self._normalize_offers(raw_data, params)

    def _normalize_offers(self, raw_data: Dict[str, Any], params: FlightSearchParams) -> NormalizedSearchResponse:
        """Normalizes raw Amadeus v2 flight-offers payload into AirfareX NormalizedSearchResponse."""
        orig_iata = self._extract_iata_code(params.origin)
        dest_iata = self._extract_iata_code(params.destination)

        # Airline & aircraft dictionaries
        dictionaries = raw_data.get("dictionaries", {})
        carrier_dict = dictionaries.get("carriers", {})
        aircraft_dict = dictionaries.get("aircraft", {})

        airline_name_map = {
            "6E": "IndiGo",
            "AI": "Air India",
            "QP": "Akasa Air",
            "SG": "SpiceJet",
            "IX": "Air India Express",
            "S5": "Star Air",
            "UK": "Vistara (Historical)",
            "I5": "AirAsia India (AIX Connect)",
            "9I": "Alliance Air"
        }
        # Merge carrier dict from Amadeus
        for c_code, c_name in carrier_dict.items():
            if c_code == "UK":
                airline_name_map["UK"] = "Vistara (Historical)"
            elif c_code not in airline_name_map:
                airline_name_map[c_code] = c_name

        normalized_flights: List[NormalizedFlight] = []
        data_offers = raw_data.get("data", [])
        now_utc_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        for idx, offer in enumerate(data_offers):
            itineraries = offer.get("itineraries", [])
            if not itineraries:
                continue
            
            outbound = itineraries[0]
            segments_raw = outbound.get("segments", [])
            if not segments_raw:
                continue

            # Multi-segment extraction
            parsed_segments: List[FlightSegment] = []
            for s_idx, seg in enumerate(segments_raw):
                dep_info = seg.get("departure", {})
                arr_info = seg.get("arrival", {})
                carrier = seg.get("carrierCode", "6E")
                carrier_name = airline_name_map.get(carrier, carrier)
                fl_num = f"{carrier} {seg.get('number', '101')}"
                dur_m = self._parse_iso_duration(seg.get("duration", "PT2H0M"))
                ac_code = seg.get("aircraft", {}).get("code", "")
                ac_name = aircraft_dict.get(ac_code, "Airbus A320neo") if ac_code else "Airbus A320neo"
                
                # Calculate layover to next segment
                layover = 0
                if s_idx < len(segments_raw) - 1:
                    next_seg_dep = segments_raw[s_idx + 1].get("departure", {}).get("at")
                    curr_seg_arr = arr_info.get("at")
                    if next_seg_dep and curr_seg_arr:
                        try:
                            t_arr = datetime.fromisoformat(curr_seg_arr.replace("Z", ""))
                            t_next = datetime.fromisoformat(next_seg_dep.replace("Z", ""))
                            layover = max(0, int((t_next - t_arr).total_seconds() // 60))
                        except Exception:
                            layover = 45

                parsed_segments.append(FlightSegment(
                    segment_id=f"SEG-AMD-{idx + 1}-{s_idx + 1}",
                    flight_no=fl_num,
                    airline=carrier_name,
                    airline_code=carrier,
                    origin=dep_info.get("iataCode", orig_iata),
                    origin_code=dep_info.get("iataCode", orig_iata),
                    destination=arr_info.get("iataCode", dest_iata),
                    destination_code=arr_info.get("iataCode", dest_iata),
                    dep_time=dep_info.get("at", "2026-09-06T06:00:00").split("T")[-1][:5],
                    arr_time=arr_info.get("at", "2026-09-06T08:15:00").split("T")[-1][:5],
                    duration=f"{dur_m // 60}h {dur_m % 60}m",
                    duration_mins=dur_m,
                    layover_mins=layover,
                    terminal_dep=dep_info.get("terminal", "T2"),
                    terminal_arr=arr_info.get("terminal", "T1"),
                    aircraft=ac_name
                ))

            first_seg = parsed_segments[0]
            last_seg = parsed_segments[-1]
            total_dur_m = self._parse_iso_duration(outbound.get("duration", "PT2H15M"))
            stops_count = len(parsed_segments) - 1
            stops_label = "Nonstop" if stops_count == 0 else (f"{stops_count} stop" if stops_count == 1 else f"{stops_count} stops")

            price_obj = offer.get("price", {})
            try:
                total_fare = round(float(price_obj.get("total", 4500)))
                base_fare = round(float(price_obj.get("base", total_fare * 0.82)))
            except (ValueError, TypeError):
                total_fare = 4500
                base_fare = 3800
            taxes = max(0, total_fare - base_fare)

            # Baggage extraction
            checked_bag = "15 KG"
            traveler_pricings = offer.get("travelerPricings", [])
            if traveler_pricings:
                fare_details = traveler_pricings[0].get("fareDetailsBySegment", [])
                if fare_details:
                    inc_bags = fare_details[0].get("includedCheckedBags", {})
                    if inc_bags:
                        if "weight" in inc_bags:
                            checked_bag = f"{inc_bags['weight']} {inc_bags.get('weightUnit', 'KG')}"
                        elif "quantity" in inc_bags:
                            checked_bag = f"{inc_bags['quantity']} piece(s) (15 KG)"

            main_carrier = first_seg.airline_code
            main_airline = airline_name_map.get(main_carrier, main_carrier)

            normalized_flights.append(NormalizedFlight(
                id=idx + 1,
                airline=main_airline,
                airline_code=main_carrier,
                flight_no=first_seg.flight_no if stops_count == 0 else f"{first_seg.flight_no} / {last_seg.flight_no}",
                origin=first_seg.origin,
                origin_code=first_seg.origin_code,
                destination=last_seg.destination,
                destination_code=last_seg.destination_code,
                dep_time=first_seg.dep_time,
                arr_time=last_seg.arr_time,
                duration=f"{total_dur_m // 60}h {total_dur_m % 60}m",
                duration_mins=total_dur_m,
                stops=stops_label,
                stop_count=stops_count,
                segments=parsed_segments,
                base_fare=base_fare,
                taxes=taxes,
                total_fare=total_fare,
                currency=price_obj.get("currency", "INR"),
                checked_baggage=checked_bag,
                bag_fee=0,
                emissions_kg=135,
                fare_score=92,
                tag="LIVE FARE",
                status="On time",
                terminal=first_seg.terminal_dep or "T2",
                gate="G4",
                aircraft=first_seg.aircraft or "Airbus A320neo",
                provider=self.get_name(),
                data_source="LIVE",
                provider_attribution="Flight data source: Amadeus (Self-Service API)",
                search_timestamp=now_utc_str,
                retrieved_at_human="Updated just now",
                deeplink=None
            ))

        best_fare = min([f.total_fare for f in normalized_flights]) if normalized_flights else None

        return NormalizedSearchResponse(
            total=len(normalized_flights),
            origin=params.origin,
            destination=params.destination,
            date=params.date,
            cabin=params.cabin,
            best_fare=best_fare,
            provider=self.get_name(),
            data_source="LIVE",
            provider_attribution="Flight data source: Amadeus (Self-Service API)",
            search_timestamp=now_utc_str,
            retrieved_at_human="Updated just now",
            cached=False,
            flights=normalized_flights
        )

    async def autocomplete_airports(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Queries Amadeus Locations API for real airport autocomplete if configured."""
        if not self.is_configured() or not query or len(query.strip()) < 2:
            return []

        token = await self._get_access_token()
        if not token:
            return []

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.get(
                    f"{self.base_url}/v1/reference-data/locations",
                    headers={"Authorization": f"Bearer {token}"},
                    params={
                        "subType": "AIRPORT,CITY",
                        "keyword": query.strip().upper(),
                        "countryCode": "IN",
                        "page[limit]": limit
                    }
                )
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    results = []
                    for item in data:
                        iata = item.get("iataCode")
                        if not iata:
                            continue
                        name = item.get("name", "")
                        city = item.get("address", {}).get("cityName", "")
                        state = item.get("address", {}).get("stateCode", "")
                        results.append({
                            "iata_code": iata,
                            "icao_code": None,
                            "name": name,
                            "city": city or name,
                            "state": state,
                            "country": "India",
                            "display_label": f"{city or name} ({iata}) — {name}",
                            "short_label": f"{city or name} ({iata})"
                        })
                    return results
        except Exception as e:
            logger.debug(f"Amadeus location autocomplete fallback: {e}")
        return []
