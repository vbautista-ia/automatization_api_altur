import json
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config.enviroments import get_env


USER_DB = get_env("USER_DB")
PASS_DB = get_env("PASS_DB")
HOST_DB = get_env("HOST_DB")
PORT_DB = get_env("PORT_DB")
NAME_DB = get_env("NAME_DB")

DB_URL = f"postgresql://{USER_DB}:{PASS_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"

def json_custom_serializer(obj):
    return json.dumps(obj, ensure_ascii=False)

engine = create_engine(
    url=DB_URL,
    json_serializer=json_custom_serializer,
    pool_pre_ping=True
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

depend_db = Annotated[Session, Depends(get_db)]