from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from config.depends import get_report_service
from config.platforms import Platforms
from service.report_service import ReportService


router = APIRouter(prefix="/report", tags=["Reporteria"])

@router.get("/contacts")
async def get_report_contacts(input_start: str, input_end: str,
                    segmento: Literal['SPC_', 'DESPACHO_'] = Query(default=None),
                    product: str = Query(default=None),
                    report_service: ReportService = Depends(get_report_service)):
    response = await report_service.get_report_cantacts(input_start, input_end, segmento, product)
    headers = { 'Content-Disposition': 'attacment; filename="report_contacts.zip"'}
    
    if response is None:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron llamadas o contactos en el rango seleccionado."
        )

    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )
    
@router.get("/contacts/api")
async def get_report_contacts(input_start: str, input_end: str,
                    segmento: Literal['SPC_', 'DESPACHO_', 'WELCOME_', 'SERVICE_', 'RTG_'] = Query(default=None),
                    report_service: ReportService = Depends(get_report_service),
                    product: str = Query(default=None)):
    response = await report_service.get_report_cantacts_api(input_start, input_end, segmento, product)
    headers = { 'Content-Disposition': 'attacment; filename="report_contacts.zip"'}
    
    if response is None:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron llamadas o contactos en el rango seleccionado."
        )

    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )
    
@router.get("/calls")
async def get_report_calls(input_start: str, input_end: str,
                    segmento: Literal['SPC_', 'DESPACHO_', 'WELCOME_', 'SERVICE_', 'RTG_'] = Query(default=None),
                    report_service: ReportService = Depends(get_report_service),
                    product: str = Query(default=None)):
    response = await report_service.get_report_calls(input_start, input_end, segmento, product)
    headers = { 'Content-Disposition': 'attacment; filename="report_calls.zip"'}
    if response is None:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron llamadas."
        )

    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )