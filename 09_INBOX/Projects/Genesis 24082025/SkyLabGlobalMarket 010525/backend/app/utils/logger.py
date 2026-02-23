import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from ..config import settings

def setup_logger(
    name: str,
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configura um logger com formatação e handlers apropriados.
    """
    # Cria o logger
    logger = logging.getLogger(name)
    
    # Define o nível de log
    logger.setLevel(level or settings.LOG_LEVEL)
    
    # Remove handlers existentes
    logger.handlers = []
    
    # Formatação do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo, se especificado
    if log_file:
        # Cria o diretório de logs se não existir
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Configura o handler de arquivo com rotação
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_request_logger() -> logging.Logger:
    """
    Retorna um logger específico para requisições HTTP.
    """
    return setup_logger(
        "request",
        log_file=str(Path(settings.LOG_DIR) / "requests.log")
    )

def get_error_logger() -> logging.Logger:
    """
    Retorna um logger específico para erros.
    """
    return setup_logger(
        "error",
        log_file=str(Path(settings.LOG_DIR) / "errors.log")
    )

def get_security_logger() -> logging.Logger:
    """
    Retorna um logger específico para eventos de segurança.
    """
    return setup_logger(
        "security",
        log_file=str(Path(settings.LOG_DIR) / "security.log")
    )

def get_performance_logger() -> logging.Logger:
    """
    Retorna um logger específico para métricas de performance.
    """
    return setup_logger(
        "performance",
        log_file=str(Path(settings.LOG_DIR) / "performance.log")
    )

# Loggers globais
request_logger = get_request_logger()
error_logger = get_error_logger()
security_logger = get_security_logger()
performance_logger = get_performance_logger()

def log_request(request_id: str, method: str, path: str, status: int, duration: float) -> None:
    """
    Registra informações de uma requisição HTTP.
    """
    request_logger.info(
        f"Request {request_id}: {method} {path} - Status: {status} - Duration: {duration:.2f}s"
    )

def log_error(error_type: str, message: str, traceback: Optional[str] = None) -> None:
    """
    Registra um erro.
    """
    if traceback:
        error_logger.error(f"{error_type}: {message}\n{traceback}")
    else:
        error_logger.error(f"{error_type}: {message}")

def log_security_event(event_type: str, user_id: Optional[int] = None, details: Optional[str] = None) -> None:
    """
    Registra um evento de segurança.
    """
    message = f"Security Event: {event_type}"
    if user_id:
        message += f" - User: {user_id}"
    if details:
        message += f" - Details: {details}"
    security_logger.warning(message)

def log_performance_metric(metric_name: str, value: float, tags: Optional[dict] = None) -> None:
    """
    Registra uma métrica de performance.
    """
    message = f"Performance Metric: {metric_name} = {value}"
    if tags:
        message += f" - Tags: {tags}"
    performance_logger.info(message) 