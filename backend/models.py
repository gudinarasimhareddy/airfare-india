from pydantic import BaseModel, Field
from typing import List, Optional

class FlightItem(BaseModel):
    id: int
    airline: str
    flight_no: str
    origin: str
    origin_code: str
    destination: str
    destination_code: str
    dep_time: str
    arr_time: str
    duration: str
    duration_mins: int
    stops: str
    base_fare: int
    taxes: int
    total_fare: int
    bag_fee: int
    emissions_kg: int
    fare_score: int
    tag: str
    status: str
    terminal: Optional[str] = "T1"
    gate: Optional[str] = "G1"

class SearchResponse(BaseModel):
    total: int
    origin: str
    destination: str
    best_fare: Optional[int] = None
    flights: List[FlightItem]

class RouteItem(BaseModel):
    id: int
    route_code: str
    origin: str
    destination: str
    index_value: float
    change_30d: float
    avg_fare: int
    volatility_score: int
    status: str

class AlertCreateRequest(BaseModel):
    route: str = Field(..., example="HYD → DEL")
    current_fare: str = Field(..., example="₹5,240")
    target_condition: str = Field(..., example="Drop below ₹5,000")

class AlertItem(BaseModel):
    id: int
    route: str
    current_fare: str
    target_condition: str
    created_at: str
    is_active: bool

class FlightStatusResponse(BaseModel):
    flight_no: str
    airline: str
    origin: str
    destination: str
    dep_time: str
    arr_time: str
    status: str
    terminal: str
    gate: str
    aircraft: str = "Airbus A320neo"

class CPISimulationRequest(BaseModel):
    headline_cpi_weight: float = Field(0.012, description="Airfare weight in overall CPI (e.g. 1.2%)")
    transport_weight: float = Field(0.086, description="Transport basket weight (e.g. 8.6%)")
    current_apix_inflation: float = Field(7.4, description="Observed airfare inflation (%)")

class CPISimulationResponse(BaseModel):
    apix_inflation: float
    cpi_headline_impact_pct: float
    cpi_headline_impact_basis_points: float
    transport_basket_impact_pct: float
    methodology: str

class QualityReportResponse(BaseModel):
    quotes_collected: int
    valid_quotes: int
    duplicates_removed: int
    outliers_flagged: int
    airline_direct_health_pct: float
    ota_health_pct: float
    price_consistency_pct: float
    mape_30d_pct: float
    correlation_dgca: float
    missing_data_pct: float
    anomaly_rate_pct: float
    freshness_sla_pct: float
    overall_confidence_pct: float
