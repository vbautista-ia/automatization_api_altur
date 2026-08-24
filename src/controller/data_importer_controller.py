from fastapi import APIRouter, Depends
from starlette import status

from config.depends import get_data_importer_service
from service.data_importer_service import DataImporterService

data_router = APIRouter(prefix='/data', tags=['Data'])

@data_router.post(path='', status_code=status.HTTP_200_OK)
async def download_data(service: DataImporterService = Depends(get_data_importer_service)):
    await service.download_data()