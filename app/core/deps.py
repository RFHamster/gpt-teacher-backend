from app.core.config import settings
from collections.abc import Generator
from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session
from typing import Annotated


engine = create_engine(str(settings.sqlalchemy_db_uri))


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
