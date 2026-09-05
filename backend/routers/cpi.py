from fastapi import APIRouter
from backend.models import CPISimulationRequest, CPISimulationResponse

router = APIRouter(prefix="/cpi-simulation", tags=["CPI Augmentation Lab"])

@router.get("", response_model=CPISimulationResponse)
def get_default_cpi_simulation():
    return calculate_impact(CPISimulationRequest())

@router.post("", response_model=CPISimulationResponse)
def simulate_cpi_impact(payload: CPISimulationRequest):
    return calculate_impact(payload)

def calculate_impact(req: CPISimulationRequest) -> CPISimulationResponse:
    # Impact on Headline CPI: Airfare Inflation * Weight
    headline_impact = round(req.current_apix_inflation * req.headline_cpi_weight, 4)
    headline_bps = round(headline_impact * 100, 2)
    
    # Impact within the Transport Sub-Basket
    transport_ratio = (req.headline_cpi_weight / req.transport_weight) if req.transport_weight > 0 else 0
    transport_impact = round(req.current_apix_inflation * transport_ratio, 3)

    return CPISimulationResponse(
        apix_inflation=req.current_apix_inflation,
        cpi_headline_impact_pct=headline_impact,
        cpi_headline_impact_basis_points=headline_bps,
        transport_basket_impact_pct=transport_impact,
        methodology="Laspeyres-equivalent high-frequency weighted price index simulation using DGCA sector basket weighting."
    )
