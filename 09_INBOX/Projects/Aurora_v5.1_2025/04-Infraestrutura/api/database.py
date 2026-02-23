"""
MÓDULO DE BANCO DE DADOS AURORA API v5.0
Implementação completa SQLAlchemy com connection pooling
"""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from sqlalchemy import create_engine, MetaData, inspect, Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

# Configuração do banco
DATABASE_URL = "sqlite:///./aurora_trading.db"
POOL_SIZE = 10
MAX_OVERFLOW = 20
POOL_TIMEOUT = 30

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

ScopedSession = scoped_session(SessionFactory)
Base = declarative_base()
Base.metadata = MetaData()

# Model Mixin para timestamps
class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

def get_db() -> Generator[Session, None, None]:
    """Dependency injection para FastAPI."""
    db = ScopedSession()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        ScopedSession.remove()

@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager para uso fora do FastAPI."""
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        ScopedSession.remove()

def init_database() -> None:
    """Inicializa o banco de dados."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database inicializado com sucesso")
        
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Conexão com database validada")
        
    except OperationalError as e:
        logger.error(f"❌ Falha ao conectar com database: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao inicializar database: {str(e)}")
        raise

def get_database_status() -> dict:
    """Retorna status de saúde do database."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            return {
                "status": "healthy",
                "database_type": engine.url.drivername,
                "tables_count": len(tables),
                "tables": tables[:10],
                "connection_pool": {
                    "checked_out": engine.pool.checkedout(),
                    "connections": engine.pool.status()
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Inicialização automática
if __name__ != "__main__":
    try:
        init_database()
    except Exception as e:
        logger.warning(f"Atenção: Database não inicializado automaticamente: {str(e)}")

__all__ = [
    "Base", "engine", "SessionFactory", "ScopedSession",
    "get_db", "db_session", "init_database", "get_database_status",
    "TimestampMixin"
]