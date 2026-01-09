from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine

from app.db.models import Base
from app.db.repo import DB
from app.dependencies.config import Config

DB_ENGINE: Engine | None = None


def create_db_engine(config: Config) -> Engine:
    engine = create_engine(config.db_url, echo=True)
    Base.metadata.create_all(engine)
    return engine


def get_db_engine(config: Config) -> Engine:
    global DB_ENGINE
    if DB_ENGINE is None:
        DB_ENGINE = create_db_engine(config)
    return DB_ENGINE


def get_db(config: Config) -> DB:
    engine = get_db_engine(config)
    return DB(engine)


DBDependency = Annotated[DB, Depends(get_db)]
