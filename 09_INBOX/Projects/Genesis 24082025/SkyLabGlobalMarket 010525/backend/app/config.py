import os
from typing import Optional, List
from pydantic import BaseSettings, PostgresDsn, validator
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    # Configurações da Aplicação
    APP_NAME: str = "SkyLab Global Market"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    TESTING: bool = False
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Configurações de Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Configurações do Banco de Dados
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "skylab_market")
    
    # URL do Banco de Dados
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )
    
    # Configurações do MetaTrader 5
    MT5_SERVER: str = os.getenv("MT5_SERVER", "localhost")
    MT5_LOGIN: int = int(os.getenv("MT5_LOGIN", "0"))
    MT5_PASSWORD: str = os.getenv("MT5_PASSWORD", "")
    MT5_PORT: int = int(os.getenv("MT5_PORT", "443"))
    
    # Configurações de CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Configurações de Rate Limiting
    RATE_LIMIT: int = 100
    RATE_LIMIT_WINDOW: int = 60  # segundos
    
    # Configurações de Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurações de Cache
    CACHE_TTL: int = 300  # 5 minutos
    CACHE_MAX_SIZE: int = 1000
    
    # Configurações de Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_TLS: bool = True
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@skylabmarket.com")
    
    # Configurações de Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Instância das configurações
settings = Settings()

# Configurações de Desenvolvimento
class DevelopmentConfig(Settings):
    DEBUG = True
    TESTING = False

# Configurações de Teste
class TestingConfig(Settings):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"

# Configurações de Produção
class ProductionConfig(Settings):
    DEBUG = False
    TESTING = False

# Configuração baseada no ambiente
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

# Função para obter a configuração atual
def get_config():
    env = os.getenv("FLASK_ENV", "default")
    return config[env] 