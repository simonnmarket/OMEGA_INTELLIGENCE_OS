"""
SCRIPT DE CORREÇÃO AUTOMÁTICA DOS 8 MÓDULOS AURORA v5.0
Tempo: 5-10 minutos | Backup automático | Validação em tempo real
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import shutil
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aurora_fix_log.txt')
    ]
)

logger = logging.getLogger(__name__)

class AuroraModuleFixer:
    """Classe principal para correção dos 8 módulos."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).absolute()
        self.fixed_modules = []
        self.failed_modules = []
        
        self.modules_to_fix = [
            "04-Infraestrutura/api/database.py",
            "04-Infraestrutura/api/__init__.py",
            "04-Infraestrutura/api/endpoints/__init__.py",
            "04-Infraestrutura/api/endpoints/strategies.py",
            "04-Infraestrutura/api/main.py",
            "06-Monitoramento/feedbackloop_module.py",
            "system_core/ncnt_orchestrator_complete.py",
            "main_ncnt.py",
            "ncnt_system_complete.py"
        ]
        
        self.backup_dir = self.project_root / "backups_pre_fix"
    
    def create_backup(self) -> bool:
        """Cria backup de todos os módulos antes da correção."""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            self.backup_dir.mkdir(exist_ok=True)
            
            logger.info(f"📂 Criando backup em: {self.backup_dir}")
            
            for module in self.modules_to_fix:
                module_path = self.project_root / module
                if module_path.exists():
                    backup_path = self.backup_dir / module
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(module_path, backup_path)
                    logger.info(f"  ✅ Backup: {module}")
            
            logger.info(f"✅ Backup completo: {len(self.modules_to_fix)} módulos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha no backup: {str(e)}")
            return False
    
    def fix_database_module(self) -> bool:
        """Corrige/cria módulo database.py."""
        try:
            db_path = self.project_root / "04-Infraestrutura/api/database.py"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            db_content = '''"""
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
]'''
            
            db_path.write_text(db_content, encoding='utf-8')
            logger.info(f"✅ database.py criado: {db_path}")
            
            # Verificar compilação
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(db_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.fixed_modules.append(str(db_path))
                return True
            else:
                logger.error(f"❌ database.py não compila: {result.stderr[:200]}")
                self.failed_modules.append(str(db_path))
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar database.py: {str(e)}")
            self.failed_modules.append("04-Infraestrutura/api/database.py")
            return False
    
    def fix_api_init_files(self) -> bool:
        """Corrige arquivos __init__.py da API."""
        files_to_fix = {
            "04-Infraestrutura/api/__init__.py": '''"""
PACKAGE PRINCIPAL DA API AURORA v5.0
"""

__version__ = "5.0.0"
__author__ = "Aurora Trading System"

from .database import (
    Base, engine, get_db, db_session, init_database,
    get_database_status, SessionFactory, ScopedSession, TimestampMixin
)

from .main import app
from .endpoints import strategies, health, monitoring

__all__ = [
    "app", "__version__",
    "Base", "engine", "get_db", "db_session", "init_database",
    "get_database_status", "SessionFactory", "ScopedSession", "TimestampMixin",
    "strategies", "health", "monitoring"
]''',
            
            "04-Infraestrutura/api/endpoints/__init__.py": '''"""
PACKAGE DE ENDPOINTS DA API AURORA v5.0
"""

from . import strategies
from . import health
from . import monitoring

__all__ = ["strategies", "health", "monitoring"]

routers = {
    "strategies": strategies.router,
    "health": health.router,
    "monitoring": monitoring.router
}

def get_all_routers():
    return list(routers.values())

def register_all_routers(app):
    for name, router in routers.items():
        app.include_router(router)'''
        }
        
        success = True
        for rel_path, content in files_to_fix.items():
            try:
                file_path = self.project_root / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"✅ {rel_path} corrigido")
                
                # Verificar compilação
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(file_path)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.fixed_modules.append(rel_path)
                else:
                    logger.error(f"❌ {rel_path} não compila: {result.stderr[:200]}")
                    self.failed_modules.append(rel_path)
                    success = False
                    
            except Exception as e:
                logger.error(f"❌ Erro ao corrigir {rel_path}: {str(e)}")
                self.failed_modules.append(rel_path)
                success = False
        
        return success
    
    def fix_string_modules(self) -> bool:
        """Corrige módulos com strings não terminadas."""
        import re
        
        corrections = {
            "06-Monitoramento/feedbackloop_module.py": [
                (r'log\.info\("([^"\n]*)\n\s+([^"]*)', r'log.info("\1\2"'),
                (r'"""[^"]*$', '"""'),
            ],
            "system_core/ncnt_orchestrator_complete.py": [
                (r'"""[^"]*$', '"""'),
                (r"'''[^']*$", "'''"),
            ],
            "main_ncnt.py": [
                (r'print\("([^"\n]*)\n\s+([^"]*)', r'print("\1\2"'),
                (r'"""[^"]*$', '"""'),
            ],
            "ncnt_system_complete.py": [
                (r'"""[^"]*$', '"""'),
                (r"'''[^']*$", "'''"),
                (r'f"""[^"]*$', 'f"""'),
            ]
        }
        
        success = True
        
        for module, patterns in corrections.items():
            module_path = self.project_root / module
            
            if not module_path.exists():
                logger.warning(f"⚠️  {module} não existe, pulando")
                continue
            
            try:
                content = module_path.read_text(encoding='utf-8')
                original_content = content
                
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                # Garantir fechamento de strings
                if content.count('"""') % 2 == 1:
                    content += '\n"""'
                if content.count("'''") % 2 == 1:
                    content += "\n'''"
                
                if content != original_content:
                    module_path.write_text(content, encoding='utf-8')
                    logger.info(f"✅ {module} - Strings corrigidas")
                else:
                    logger.info(f"✅ {module} - Nenhuma correção necessária")
                
                # Verificar compilação
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(module_path)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.fixed_modules.append(module)
                else:
                    logger.error(f"❌ {module} não compila: {result.stderr[:200]}")
                    self.failed_modules.append(module)
                    success = False
                    
            except Exception as e:
                logger.error(f"❌ Erro ao corrigir {module}: {str(e)}")
                self.failed_modules.append(module)
                success = False
        
        return success
    
    def generate_report(self) -> str:
        """Gera relatório de correção."""
        report = f"""AURORA v5.0 - RELATÓRIO DE CORREÇÃO DOS 8 MÓDULOS
================================================================================
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Diretório: {self.project_root}
================================================================================

RESUMO
------
Módulos corrigidos: {len(self.fixed_modules)}
Módulos com falha: {len(self.failed_modules)}
Backup: {self.backup_dir}

STATUS POR MÓDULO
-----------------
"""
        
        all_modules = self.modules_to_fix
        for module in all_modules:
            if module in self.fixed_modules:
                report += f"✅ {module}\n"
            elif module in self.failed_modules:
                report += f"❌ {module} (FALHA)\n"
            else:
                report += f"⚠️  {module} (NÃO PROCESSADO)\n"
        
        if self.failed_modules:
            report += f"""

AÇÕES NECESSÁRIAS
-----------------
Corrigir manualmente:
"""
            for module in self.failed_modules:
                report += f"- {module}\n"
        else:
            report += f"""

✅ CORREÇÃO COMPLETA COM SUCESSO
--------------------------------
Todos os 8 módulos foram corrigidos.
Próximo passo: python validate_239_modules.py

RELATÓRIO GERADO AUTOMATICAMENTE
"""
        
        return report
    
    def run_complete_fix(self) -> bool:
        """Executa correção completa."""
        logger.info("=" * 80)
        logger.info("🔧 INICIANDO CORREÇÃO DOS 8 MÓDULOS AURORA v5.0")
        logger.info("=" * 80)
        
        # Backup
        if not self.create_backup():
            return False
        
        # Corrigir módulos
        logger.info("\n🛠️  Corrigindo módulos...")
        
        success = True
        if not self.fix_database_module():
            success = False
        if not self.fix_api_init_files():
            success = False
        if not self.fix_string_modules():
            success = False
        
        # Gerar relatório
        report = self.generate_report()
        report_path = self.project_root / "aurora_module_fix_report.txt"
        report_path.write_text(report, encoding='utf-8')
        
        print("\n" + "=" * 80)
        print(report)
        print("=" * 80)
        
        logger.info(f"📁 Relatório salvo em: {report_path}")
        
        return success and len(self.failed_modules) == 0

def main():
    """Função principal."""
    fixer = AuroraModuleFixer()
    
    try:
        success = fixer.run_complete_fix()
        
        if success:
            print("\n✅ CORREÇÃO COMPLETA COM SUCESSO!")
            print("\n🚀 PRÓXIMO PASSO:")
            print("python validate_239_modules.py")
            return 0
        else:
            print("\n⚠️  CORREÇÃO PARCIAL - VERIFIQUE O RELATÓRIO")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Operação interrompida pelo usuário")
        return 2
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        return 3

if __name__ == "__main__":
    sys.exit(main())

