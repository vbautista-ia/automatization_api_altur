from typing import Annotated

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config.enviroments import get_env


DB_URL = get_env('DB_URL')

engine = create_engine(
    url=DB_URL,
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

depend_db = Annotated[Session, get_db]