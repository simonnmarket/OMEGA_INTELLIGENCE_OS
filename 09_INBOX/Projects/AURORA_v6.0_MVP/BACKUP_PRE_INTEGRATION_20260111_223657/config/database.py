"""
Database Config - AURORA v6.0 MVP
Configurações de banco de dados e armazenamento
"""

import os

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_CONFIG = {
    # Experience Buffer (SQLite)
    "experience_buffer": os.path.join(BASE_DIR, "data", "experience_buffer", "trades.db"),
    
    # Modelos treinados
    "models_path": os.path.join(BASE_DIR, "data", "models"),
    
    # Backups
    "backups_path": os.path.join(BASE_DIR, "data", "backups"),
    
    # Logs
    "logs_path": os.path.join(BASE_DIR, "logs"),
    
    # Cache temporário
    "cache_path": os.path.join(BASE_DIR, "data", "cache"),
}


def ensure_directories():
    """Cria todos os diretórios necessários"""
    for key, path in DATABASE_CONFIG.items():
        if key.endswith("_path"):
            os.makedirs(path, exist_ok=True)
        else:
            # Para arquivos, criar diretório pai
            os.makedirs(os.path.dirname(path), exist_ok=True)


def get_db_path(name: str) -> str:
    """Retorna caminho do banco/diretório pelo nome"""
    return DATABASE_CONFIG.get(name, "")


# Auto-criar diretórios ao importar
ensure_directories()

