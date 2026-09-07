"""
Base Flight Provider Interface and Data Normalization Models
Provides a provider-agnostic abstraction for Indian domestic flight search,
multi-segment flight representations, and standardized flight result envelopes.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any

class FlightSegment(BaseModel):
    segment_id: str = Field(..., description="Unique segment identifier, e.g. SEG-1")
    flight_no: str = Field(..., description="Flight carrier number, e.g. 6E 214")
    airline: str = Field(..., description="Marketing airline name, e.g. IndiGo")
    airline_code: str = Field(..., description="2-letter IATA airline code, e.g. 6E")
    origin: str = Field(..., description="Departure city/airport name, e.g. Delhi")
    origin_code: str = Field(..., description="3-letter IATA origin airport code, e.g. DEL")
    destination: str = Field(..., description="Arrival city/airport name, e.g. Mumbai")
    destination_code: str = Field(..., description="3-letter IATA destination airport code, e.g. BOM")
    dep_time: str = Field(..., description="Local departure time HH:MM")
    arr_time: str = Field(..., description="Local arrival time HH:MM")
    duration: str = Field(..., description="Segment duration, e.g. 2h 15m")
    duration_mins: int = Field(..., description="Segment duration in minutes")
    layover_mins: Optional[int] = Field(0, description="Layover minutes before next segment")
    terminal_dep: Optional[str] = Field("T2", description="Departure terminal")
    terminal_arr: Optional[str] = Field("T1", description="Arrival terminal")
    aircraft: Optional[str] = Field("Airbus A320neo", description="Operating aircraft model")

class FlightSearchParams(BaseModel):
    origin: str
    destination: str
    date: Optional[str] = None
    return_date: Optional[str] = None
    cabin: str = "Economy"
    stops: str = "Any"  # 'Any', 'Nonstop', '1 stop'
    airline: str = "All airlines"
    max_price: Optional[int] = None
    baggage: str = "Any"
    time_of_day: str = "Any time"
    direct_only: bool = False
    sort_by: str = "score"  # 'score', 'price', 'duration', 'emissions'
    adults: int = 1

class NormalizedFlight(BaseModel):
    id: int
    airline: str
    airline_code: str
    flight_no: str
    origin: str
    origin_code: str
    destination: str
    destination_code: str
    dep_time: str
    arr_time: str
    duration: str
    duration_mins: int
    stops: str  # 'Nonstop', '1 stop', '2 stops'
    stop_count: int = 0
    segments: List[FlightSegment] = Field(default_factory=list)
    base_fare: int
    taxes: int
    taxes_and_fees: Optional[int] = None
    total_fare: int
    currency: str = "INR"
    checked_baggage: Optional[str] = "15 KG (1 piece)"
    bag_fee: int = 0
    emissions_kg: int = 135
    fare_score: int = 90
    tag: str = "BEST VALUE"
    status: str = "On time"
    terminal: Optional[str] = "T2"
    gate: Optional[str] = "G4"
    aircraft: Optional[str] = "Airbus A320neo"
    provider: str = "MockDevelopmentProvider"
    data_source: str = "DEVELOPMENT"  # 'DEVELOPMENT', 'CACHE', 'LIVE'
    provider_attribution: Optional[str] = "Flight data source: MockDevelopmentProvider (Development Catalog)"
    search_timestamp: Optional[str] = None
    retrieved_at_human: Optional[str] = "Updated just now"
    deeplink: Optional[str] = None

    @model_validator(mode="after")
    def populate_defaults(self):
        if self.taxes_and_fees is None:
            self.taxes_and_fees = self.taxes
        return self

class NormalizedSearchResponse(BaseModel):
    total: int
    origin: str
    destination: str
    date: Optional[str] = None
    cabin: str = "Economy"
    best_fare: Optional[int] = None
    provider: str = "MockDevelopmentProvider"
    data_source: str = "DEVELOPMENT"  # 'DEVELOPMENT', 'CACHE', 'LIVE'
    provider_attribution: Optional[str] = "Flight data source: MockDevelopmentProvider (Development Catalog)"
    search_timestamp: Optional[str] = None
    retrieved_at_human: Optional[str] = "Updated just now"
    cached: bool = False
    cache_ttl_remaining_secs: Optional[int] = None
    flights: List[NormalizedFlight] = Field(default_factory=list)

class BaseFlightProvider(ABC):
    """Abstract base class for all flight search providers."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the human-readable identifier of the provider."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if API credentials / dependencies are configured and ready."""
        pass

    @abstractmethod
    async def search_flights(self, params: FlightSearchParams) -> NormalizedSearchResponse:
        """Execute flight search and return normalized results."""
        pass

class BaseBookingProvider(ABC):
    """
    Abstract base class for airline/GDS/NDC booking and ticketing providers.
    Prepared for future live GDS / NDC ticketing provider credentials.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Return the human-readable identifier of the booking provider."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if ticketing API credentials are configured and active."""
        pass

    @abstractmethod
    async def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute booking reservation and ticketing."""
        pass

    @abstractmethod
    async def cancel_booking(self, booking_ref: str) -> Dict[str, Any]:
        """Execute booking cancellation and refund claim with carrier."""
        pass
