from typing import Literal

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from configuration.platforms import Platforms
from service.call_service import CallService


call_router = APIRouter()

@call_router.get('/descargar/')
async def descargar(input_start: str, input_end: str, tag: str, plataforma: Literal['BBVA_COBRANZA', 'BBVA_RETARGETING'], segmento: str = Query(default=None), max_records: int = 5):
    call_service = CallService(platform=Platforms[plataforma])
    response = await call_service.download(input_start, input_end, tag, segmento, max_records)
    headers = { 'Content-Disposition': 'attacment; filename="grabaciones.zip"'}
    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )