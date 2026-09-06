from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any

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

# =========================================================
# PAYMENT & BOOKING STATE MACHINE SCHEMAS
# =========================================================

class CreatePaymentOrderRequest(BaseModel):
    booking_type: str = Field("flight", description="'flight' or 'package'")
    package_id: Optional[str] = None
    flight_no: Optional[str] = None
    origin_code: Optional[str] = None
    destination_code: Optional[str] = None
    cabin: Optional[str] = "Economy"
    payment_method: Optional[str] = "upi"
    traveler_name: Optional[str] = "Valued Guest"
    email: Optional[str] = "guest@example.com"
    phone: Optional[str] = "+919876543210"
    travel_date: Optional[str] = None
    pax_count: int = Field(1, ge=1, le=9)
    promo_code: Optional[str] = None
    seat_choice: Optional[str] = None
    addons: Optional[Union[List[str], Dict[str, Any]]] = None
    gstin: Optional[str] = None
    company_name: Optional[str] = None
    meal_preference: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None

class PriceBreakdownItem(BaseModel):
    item_title: str
    base_price: int
    hotel_price: int = 0
    transfers_price: int = 0
    taxes_and_fees: int
    service_fee: int = 0
    discount: int = 0
    promo_applied: Optional[str] = None
    final_payable_amount: int
    currency: str = "INR"
    fuel_surcharge_yq: int = 0
    user_development_fee_udf: int = 0
    aviation_security_fee_asf: int = 0
    cgst: int = 0
    sgst: int = 0
    total_gst: int = 0
    addons_amount: int = 0
    convenience_fee: int = 0

class PaymentOrderResponse(BaseModel):
    order_id: str
    booking_id: str
    amount_paise: int
    amount_inr: int
    currency: str = "INR"
    key_id: str
    is_sandbox: bool
    package_title: Optional[str] = None
    traveler_name: str
    email: str
    phone: str
    pricing: PriceBreakdownItem

class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str
    booking_id: str

class PaymentVerificationResponse(BaseModel):
    status: str  # 'CONFIRMED', 'FAILED', 'RECONCILIATION_REQUIRED'
    booking_id: str
    payment_id: str
    order_id: str
    amount_inr: int
    pnr: Optional[str] = None
    eticket_number: Optional[str] = None
    voucher_id: Optional[str] = None
    traveler_name: str
    email: str
    flight_details: Optional[str] = None
    hotel_details: Optional[str] = None
    travel_date: str
    seat_number: Optional[str] = None
    booking_type: Optional[str] = "flight"
    invoice_number: Optional[str] = None
    message: str


