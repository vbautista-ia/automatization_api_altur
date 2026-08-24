from fastapi import Depends
from sqlalchemy.orm import Session

from config.database import get_db
from repository.data_importer_repository import DataImporterRepository
from service.data_importer_service import DataImporterService

def get_data_importer_repository(db: Session = Depends(get_db)) -> DataImporterRepository:
    return DataImporterRepository(db)

def get_data_importer_service(repository: DataImporterRepository = Depends(get_data_importer_repository)) -> DataImporterService:
    return DataImporterService(repository)