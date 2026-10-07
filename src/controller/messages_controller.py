
from typing import Literal

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from config.platforms import Platforms
from service.messages_service import MessagesService


messages_router = APIRouter(prefix='/messages', tags=['Mensajes'])

@messages_router.get('')
async def get_transcriptions(input_start: str, input_end: str,
                    segmento: Literal['SPC_', 'DESPACHO_'] = Query(default=None),
                    product: str = Query(default=None)):
    messages_service = MessagesService(platform=Platforms.BBVA_COBRANZA)
    response = await messages_service.get_transcriptions(input_start, input_end, segmento, product)
    headers = { 'Content-Disposition': 'attachment; filename="transcripciones.zip"'}
    return StreamingResponse(
                response,
                media_type='application/x-zip-compressed',
                headers=headers
            )