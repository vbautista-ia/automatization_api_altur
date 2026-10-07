import sys
import os
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
# -----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from config.database import SessionLocal
from repository.data_importer_repository import DataImporterRepository
from service.data_importer_service import DataImporterService

async def main():
    logging.info('Start cronjob: download data Altur')
    
    db_session = SessionLocal()
    
    try:
        repository = DataImporterRepository(db_session)
        service = DataImporterService(repository)
        
        await service.download_data()
        
        logging.info("Download data finished")
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        db_session.close()
        logging.info("Close connection cronjob")

if __name__ == "__main__":
    asyncio.run(main())