from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from .config import settings

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração do engine do SQLAlchemy
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Criação da sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager para gerenciar sessões do banco de dados.
    Garante que a sessão seja fechada corretamente após o uso.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro na sessão do banco de dados: {str(e)}")
        raise
    finally:
        db.close()

def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {str(e)}")
        raise

def get_db_session() -> Session:
    """
    Retorna uma nova sessão do banco de dados.
    """
    return SessionLocal()

def close_db_session(db: Session) -> None:
    """
    Fecha uma sessão do banco de dados.
    """
    try:
        db.close()
    except Exception as e:
        logger.error(f"Erro ao fechar sessão do banco de dados: {str(e)}")
        raise

def check_db_connection() -> bool:
    """
    Verifica se a conexão com o banco de dados está funcionando.
    """
    try:
        with get_db() as db:
            db.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Erro ao verificar conexão com o banco de dados: {str(e)}")
        return False

def get_db_stats() -> dict:
    """
    Retorna estatísticas do banco de dados.
    """
    try:
        with get_db() as db:
            # Número de conexões ativas
            active_connections = db.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            ).scalar()
            
            # Tamanho do banco de dados
            db_size = db.execute(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            ).scalar()
            
            # Número de tabelas
            table_count = db.execute(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
            ).scalar()
            
            return {
                "active_connections": active_connections,
                "database_size": db_size,
                "table_count": table_count
            }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do banco de dados: {str(e)}")
        return {}

# Funções de utilidade para transações
def begin_transaction(db: Session) -> None:
    """
    Inicia uma transação.
    """
    db.begin()

def commit_transaction(db: Session) -> None:
    """
    Commita uma transação.
    """
    db.commit()

def rollback_transaction(db: Session) -> None:
    """
    Faz rollback de uma transação.
    """
    db.rollback()

# Funções de utilidade para queries
def execute_query(db: Session, query: str, params: dict = None) -> list:
    """
    Executa uma query SQL e retorna os resultados.
    """
    try:
        result = db.execute(query, params or {})
        return [dict(row) for row in result]
    except Exception as e:
        logger.error(f"Erro ao executar query: {str(e)}")
        raise

def execute_scalar(db: Session, query: str, params: dict = None) -> any:
    """
    Executa uma query SQL e retorna um único valor.
    """
    try:
        return db.execute(query, params or {}).scalar()
    except Exception as e:
        logger.error(f"Erro ao executar query scalar: {str(e)}")
        raise

# Funções de utilidade para migrações
def get_current_migration_version() -> str:
    """
    Retorna a versão atual da migração.
    """
    try:
        with get_db() as db:
            return execute_scalar(
                db,
                "SELECT version_num FROM alembic_version"
            )
    except Exception as e:
        logger.error(f"Erro ao obter versão da migração: {str(e)}")
        return None

def check_migrations() -> bool:
    """
    Verifica se há migrações pendentes.
    """
    try:
        with get_db() as db:
            # Verifica se a tabela alembic_version existe
            table_exists = execute_scalar(
                db,
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                )
                """
            )
            
            if not table_exists:
                return True
            
            # Verifica se há migrações pendentes
            pending_migrations = execute_scalar(
                db,
                """
                SELECT EXISTS (
                    SELECT 1 
                    FROM alembic_version 
                    WHERE version_num != (
                        SELECT version_num 
                        FROM alembic_version 
                        ORDER BY version_num DESC 
                        LIMIT 1
                    )
                )
                """
            )
            
            return pending_migrations
    except Exception as e:
        logger.error(f"Erro ao verificar migrações: {str(e)}")
        return False

# Importação dos modelos
from .models.user import User
from .models.portfolio import Portfolio
from .models.trade import Trade
from .models.risk_metrics import RiskMetrics

# Função para dropar todas as tabelas (usar com cuidado!)
def drop_db():
    Base.metadata.drop_all(bind=engine)

# Função para resetar o banco de dados (usar com cuidado!)
def reset_db():
    drop_db()
    init_db() 