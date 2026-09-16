from fastapi import APIRouter, Depends

from app.api.dependencies import get_alert_service
from app.schemas.alert import AlertItemSchema
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get(
    "",
    response_model=list[AlertItemSchema],
    summary="Get recent alerts",
    description=(
        "Alerts are generated only from real detected state changes: a symbol's first "
        "signal (new-signal), a meaningful confidence move on an existing signal "
        "(confidence-up/confidence-down), a risk-tier or sentiment-tier shift, or a "
        "completed backtest run (backtest-complete). Nothing here is randomly generated."
    ),
)
async def get_alerts(service: AlertService = Depends(get_alert_service)) -> list[AlertItemSchema]:
    return await service.list_alerts()
