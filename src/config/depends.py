from fastapi import Depends
from sqlalchemy.orm import Session

from config.database import get_db
from repository.data_importer_repository import DataImporterRepository
from repository.report_repository import ReportRepository
from service.data_importer_service import DataImporterService
from service.report_service import ReportService

def get_data_importer_repository(db: Session = Depends(get_db)) -> DataImporterRepository:
    return DataImporterRepository(db)

def get_data_importer_service(repository: DataImporterRepository = Depends(get_data_importer_repository)) -> DataImporterService:
    return DataImporterService(repository)


def get_report_repository(db: Session = Depends(get_db)) -> ReportRepository:
    return ReportRepository(db)

def get_report_service(repository: ReportRepository = Depends(get_report_repository)) -> ReportService:
    return ReportService(repository)