# MEMORY_ID: TASK_CORE_SETUP
# TIMESTAMP: 2025-11-09T21:26:30+01:00
# AUTHOR: Cursor_Omega

"""
Camada de persistência unificada (SQLAlchemy).
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine  # type: ignore
from sqlalchemy.orm import Session, declarative_base, sessionmaker  # type: ignore

from Core.Config import ConfigManager
from Core.Logger import get_logger

logger = get_logger("prometheus.database")

Base = declarative_base()
_engine = None
_SessionLocal: Optional[sessionmaker] = None


class DataPoint(Base):
    __tablename__ = "datapoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment = Column(String, nullable=False)
    metal = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_engine(connection_string: Optional[str] = None):
    global _engine, _SessionLocal

    if _engine is not None:
        return _engine

    if connection_string is None:
        config = ConfigManager.get_instance()
        connection_string = config.get("database", "connection_string", default="sqlite:///finance.db")

    logger.info("Inicializando engine SQLAlchemy (%s)", connection_string)
    _engine = create_engine(connection_string, future=True)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(_engine)
    return _engine


def get_engine():
    if _engine is None:
        return init_engine()
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        init_engine()
    assert _SessionLocal is not None
    return _SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Erro durante operação de banco de dados. Realizando rollback.")
        raise
    finally:
        session.close()

