from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/offers", tags=["Offers & Discounts"])

OFFERS_DATABASE = [
    {
        "code": "AIRX500",
        "title": "AirfareX Launch Special",
        "badge": "POPULAR",
        "category": "promo",
        "type": "flat",
        "value": 500,
        "min_fare": 3000,
        "applies_to": "total_fare",
        "description": "Flat ₹500 off on all domestic flight bookings across any airline.",
        "baggage_perk": None,
        "expiry": "2026-12-31",
        "terms": "Valid once per user on all domestic sectors. No minimum lead time."
    },
    {
        "code": "STUDENT10",
        "title": "DGCA Student Concession",
        "badge": "STUDENT SPECIAL",
        "category": "concession",
        "type": "percent",
        "value": 10,
        "min_fare": 2500,
        "applies_to": "base_fare",
        "description": "10% off base fare + 10kg FREE extra check-in baggage allowance (Total 25kg).",
        "baggage_perk": "+10kg Extra Baggage Included",
        "expiry": "2026-12-31",
        "terms": "Valid for bona fide students aged 12-26 with valid Student ID card presented at check-in."
    },
    {
        "code": "SENIOR50",
        "title": "Senior Citizen Concession",
        "badge": "50% OFF BASE",
        "category": "concession",
        "type": "percent",
        "value": 50,
        "min_fare": 2000,
        "applies_to": "base_fare",
        "description": "Up to 50% discount on base fare for Indian senior citizens aged 60 and above.",
        "baggage_perk": "Standard 15kg + Priority Boarding",
        "expiry": "2026-12-31",
        "terms": "Requires Indian citizenship and age 60+ with photo ID proof (Aadhaar / Voter ID)."
    },
    {
        "code": "ARMEDFORCES",
        "title": "Veer Jawan Concession",
        "badge": "DEFENCE SPECIAL",
        "category": "concession",
        "type": "percent",
        "value": 50,
        "min_fare": 2000,
        "applies_to": "base_fare",
        "description": "50% discount on base fare for serving & retired Indian Armed Forces personnel & dependents.",
        "baggage_perk": "Free 20kg Check-in Baggage",
        "expiry": "2026-12-31",
        "terms": "Valid official Armed Forces / Paramilitary service ID required at security check-in."
    },
    {
        "code": "HDFCFLY",
        "title": "HDFC Bank Weekend Escape",
        "badge": "BANK OFFER",
        "category": "bank",
        "type": "flat",
        "value": 1200,
        "min_fare": 5000,
        "applies_to": "total_fare",
        "description": "Instant ₹1,200 discount on HDFC Bank Credit & Debit Cards on bookings above ₹5,000.",
        "baggage_perk": None,
        "expiry": "2026-10-31",
        "terms": "Valid on payments made via HDFC Bank credit or debit cards. Not applicable on corporate cards."
    },
    {
        "code": "ICICISKY",
        "title": "ICICI Bank Travel Supercharge",
        "badge": "15% SAVINGS",
        "category": "bank",
        "type": "percent_capped",
        "value": 15,
        "cap": 1500,
        "min_fare": 4000,
        "applies_to": "total_fare",
        "description": "15% instant discount up to ₹1,500 with ICICI Bank NetBanking & Credit Cards.",
        "baggage_perk": None,
        "expiry": "2026-11-15",
        "terms": "Valid every Thursday to Sunday on all domestic airline bookings."
    },
    {
        "code": "SBIWINGS",
        "title": "SBI Card Domestic Flight Savings",
        "badge": "₹800 FLAT",
        "category": "bank",
        "type": "flat",
        "value": 800,
        "min_fare": 4500,
        "applies_to": "total_fare",
        "description": "Flat ₹800 instant discount on SBI Credit Cards for domestic sectors.",
        "baggage_perk": None,
        "expiry": "2026-12-31",
        "terms": "Minimum transaction value ₹4,500. Valid on SBI contactless & chip cards."
    },
    {
        "code": "EARLYBIRD",
        "title": "T+30 Advance Booking Advantage",
        "badge": "EARLY BIRD",
        "category": "promo",
        "type": "flat",
        "value": 1500,
        "min_fare": 6000,
        "applies_to": "total_fare",
        "description": "₹1,500 off on flights booked 30 or more days ahead of departure date.",
        "baggage_perk": "Free Seat Selection Voucher",
        "expiry": "2026-12-31",
        "terms": "Applicable for travel dates at least 30 days after booking date."
    }
]

class ValidateOfferRequest(BaseModel):
    code: str
    base_fare: int
    total_fare: int
    airline: Optional[str] = None

class ValidateOfferResponse(BaseModel):
    valid: bool
    code: str
    title: str
    category: str
    discount_amount: int
    original_total: int
    new_total_fare: int
    baggage_perk: Optional[str] = None
    message: str

@router.get("/list")
def list_offers(category: Optional[str] = None):
    """Retrieve all active offers, bank discounts, and concessions."""
    if category:
        filtered = [o for o in OFFERS_DATABASE if o["category"] == category]
        return {"total": len(filtered), "offers": filtered}
    return {"total": len(OFFERS_DATABASE), "offers": OFFERS_DATABASE}

@router.post("/validate", response_model=ValidateOfferResponse)
def validate_offer(req: ValidateOfferRequest):
    """Validate a promo code and compute exact instant discount."""
    code_upper = req.code.strip().upper()
    offer = next((o for o in OFFERS_DATABASE if o["code"] == code_upper), None)

    if not offer:
        raise HTTPException(
            status_code=400,
            detail=f"Promo code '{code_upper}' is invalid or has expired."
        )

    if req.total_fare < offer["min_fare"]:
        raise HTTPException(
            status_code=400,
            detail=f"Code '{code_upper}' requires a minimum fare of ₹{offer['min_fare']:,}. Current fare is ₹{req.total_fare:,}."
        )

    # Calculate discount amount
    discount = 0
    if offer["type"] == "flat":
        discount = offer["value"]
    elif offer["type"] == "percent":
        target = req.base_fare if offer["applies_to"] == "base_fare" else req.total_fare
        discount = int(target * (offer["value"] / 100.0))
    elif offer["type"] == "percent_capped":
        target = req.base_fare if offer["applies_to"] == "base_fare" else req.total_fare
        calculated = int(target * (offer["value"] / 100.0))
        discount = min(calculated, offer.get("cap", calculated))

    # Discount cannot exceed total fare - min ₹500 taxes
    max_discount = max(0, req.total_fare - 500)
    discount = min(discount, max_discount)
    new_total = max(500, req.total_fare - discount)

    return ValidateOfferResponse(
        valid=True,
        code=offer["code"],
        title=offer["title"],
        category=offer["category"],
        discount_amount=discount,
        original_total=req.total_fare,
        new_total_fare=new_total,
        baggage_perk=offer.get("baggage_perk"),
        message=f"Coupon applied! You saved ₹{discount:,} instantly."
    )
