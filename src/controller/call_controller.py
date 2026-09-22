from typing import Literal

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import StreamingResponse

from config.platforms import Platforms
from service.call_service import CallService


call_router = APIRouter(prefix='/call', tags=['Llamadas'])

@call_router.get('/download/')
async def descargar(input_start: str, input_end: str, tag: str,
                    plataforma: Literal['BBVA_COBRANZA', 'BBVA_RETARGETING'],
                    segmento: Literal['SPC_', 'DESPACHO_', 'WELCOME_', 'SERVICE_', 'RTG_'] = Query(default=None),
                    max_records: int = 5,
                    product: str = Query(default=None)):
    call_service = CallService(platform=Platforms[plataforma])
    response = await call_service.download(input_start, input_end, tag, segmento, max_records, product)
    headers = { 'Content-Disposition': 'attachment; filename="grabaciones.zip"'}
    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )
    
@call_router.post('/download/by/id/')
async def download_by_id(plataforma: Literal['BBVA_COBRANZA', 'BBVA_RETARGETING'], 
                         calls: list[str]):
    call_service = CallService(platform=Platforms[plataforma])
    response = await call_service.download_calls_by_id(calls)
    if not response:
        raise HTTPException(
                    status_code=404, 
                    detail="No se encontraron llamadas"
                )

    headers = { 'Content-Disposition': 'attachment; filename="grabaciones.zip"'}
    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )