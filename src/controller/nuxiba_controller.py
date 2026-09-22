from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, model_validator

from config.depends import get_nuxiba_service
from service.nuxiba_service import NuxibaService


class TranscriptionFilter(BaseModel):
    campaign: Literal['SPC_', 'DESPACHO_'] = Field(default=None, description="Filtrar por nombre de campaña")
    start: Optional[datetime] = Field(default=None, description="Fecha inicio YYYY-MM-DD HH:MM:SS")
    end: Optional[datetime] = Field(default=None, description="Fecha fin YYYY-MM-DD HH:MM:SS")
    min_duration: int = Field(default=0, ge=0, description="Duración mínima en segundos")
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'TranscriptionFilter':
        if bool(self.start) != bool(self.end):
            raise ValueError("Debes proporcionar tanto 'start' como 'end' para filtrar por fecha.")
        
        if self.start and self.end:
            if self.start > self.end:
                raise ValueError("La fecha de inicio (start) no puede ser mayor a la fecha de fin (end).")
        return self

router = APIRouter(prefix='/nuxiba', tags=['Nuxiba'])

@router.get('/transcript')
async def get_transcript(nuxbia_service: NuxibaService = Depends(get_nuxiba_service),
                         params: TranscriptionFilter = Depends(TranscriptionFilter)):
    
    response = nuxbia_service.get_transcriptions(**params.model_dump())

    if response is None:
        raise HTTPException(
            status_code=204, 
            detail="No se encontraron llamadas o contactos en el rango seleccionado."
        )
        
    headers = { 'Content-Disposition': 'attachment; filename="transcripciones.zip"' }
    
    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )