import logging
from sqlite3 import OperationalError
from typing import Literal

from sqlalchemy import insert
from sqlalchemy.orm import Session

from models.call import Call
from models.campaign import Campaign
from models.contact import Contact


class DataImporterRepository:
    
    def __init__(self, db: Session):
        self.__db = db
    
    def insert(self, data: list[dict], table: Literal['campaings', 'contacts', 'calls']):
        stmt = None
        if table == 'campaings':
            stmt = insert(Campaign)
        elif table == 'contacts':
            stmt = insert(Contact)
        elif table == 'calls':
            stmt = insert(Call)
        try:
            self.__db.execute(stmt, data)
            self.__db.commit()
            logging.info(f"insert into {table}: {len(data)} rows")
        except OperationalError as e:
            self.__db.rollback()
            logging.error(f"Error connect DB: {e}")
        except Exception as e:
            self.__db.rollback()
            logging.error(f"Error proccess lote: {e}")
        finally:
            self.__db.expunge_all()