#!/usr/bin/env python3
"""
🏦 DATABASE CONNECTION - NCNT Tier-0
Gerenciamento de conexão PostgreSQL
"""

import json
import os
from pathlib import Path
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Caminho do arquivo de configuração
CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    """Carregar configuração do banco de dados"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        # Configuração padrão para desenvolvimento
        return {
            "database": {
                "engine": "postgresql",
                "host": "localhost",
                "port": 5432,
                "name": "ncnt_production",
                "user": "ncnt_app",
                "password": "GoldmanSachs_Tier0_2024",
                "pool_size": 10,
                "max_overflow": 20,
                "echo": False
            }
        }


def get_database_url() -> str:
    """Construir URL de conexão do banco de dados"""
    config = load_config()
    db_config = config["database"]
    
    return (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    )


# Engine global
_engine: Optional[any] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine():
    """Obter engine SQLAlchemy (singleton)"""
    global _engine
    if _engine is None:
        config = load_config()
        db_config = config["database"]
        
        _engine = create_engine(
            get_database_url(),
            pool_size=db_config.get("pool_size", 10),
            max_overflow=db_config.get("max_overflow", 20),
            echo=db_config.get("echo", False),
            pool_pre_ping=True
        )
    return _engine


def get_session() -> Session:
    """Obter sessão do banco de dados"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal()


def check_db_connection() -> bool:
    """Verificar conexão com banco de dados"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def close_connection():
    """Fechar conexão com banco de dados"""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
        _engine = None
    _SessionLocal = None

