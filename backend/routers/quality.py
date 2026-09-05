from fastapi import APIRouter
from backend.models import QualityReportResponse

router = APIRouter(prefix="/quality", tags=["Data Quality"])

@router.get("", response_model=QualityReportResponse)
def get_quality_report():
    return QualityReportResponse(
        quotes_collected=125420,
        valid_quotes=117842,
        duplicates_removed=4120,
        outliers_flagged=1613,
        airline_direct_health_pct=96.4,
        ota_health_pct=93.1,
        price_consistency_pct=91.8,
        mape_30d_pct=4.8,
        correlation_dgca=0.93,
        missing_data_pct=2.1,
        anomaly_rate_pct=1.3,
        freshness_sla_pct=98.6,
        overall_confidence_pct=94.2
    )
