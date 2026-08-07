
from typing import Literal

from fastapi import APIRouter, Query

from configuration.platforms import Platforms
from service.report_service import ReportService


router = APIRouter(prefix="/report", tags=["Reporteria"])

@router.get("/calls")
async def get_report_calls(input_start: str, input_end: str,
                    plataforma: Literal['BBVA_COBRANZA', 'BBVA_RETARGETING'],
                    segmento: Literal['SPC_', 'DESPACHO_', 'WELCOME_', 'SERVICE_', 'RTG_'] = Query(default=None),
                    product: str = Query(default=None)):
    call_service = ReportService(platform=Platforms[plataforma])
    await call_service.get_report_calls(input_start, input_end, segmento, product)
