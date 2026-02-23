"""
FastAPI app principal com todos os endpoints Tier-0
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Global instances
_orchestrator = None
_health_monitor = None
_auth_middleware = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifecycle manager para a aplicação"""
    global _orchestrator, _health_monitor, _auth_middleware
    
    logger.info("Starting Aurora Core Tier-0")
    
    try:
        # Initialize components
        from src.utils.vault_client import Tier0VaultClient
        from src.utils.redlock_manager import RedlockManager
        from src.health.tier0_health import Tier0HealthMonitor
        from src.auth.tier0_auth import Tier0AuthMiddleware
        from src.core.async_orchestrator import AsyncOrchestrator
        from src.api.tier0_endpoints import set_orchestrator, set_auth_middleware
        
        # Initialize Vault client
        vault_client = Tier0VaultClient(
            vault_addr=os.getenv("VAULT_ADDR", "http://localhost:8200"),
            vault_token=os.getenv("VAULT_TOKEN", "demo-token")
        )
        
        # Initialize Redlock
        redis_nodes = os.getenv("REDIS_NODES", "localhost:6379").split(",")
        redlock = RedlockManager(redis_nodes)
        
        # Initialize health monitor
        _health_monitor = Tier0HealthMonitor(vault_client, redlock)
        
        # Initialize auth middleware
        _auth_middleware = Tier0AuthMiddleware(vault_client, redlock)
        set_auth_middleware(_auth_middleware)
        
        # Initialize orchestrator
        _orchestrator = AsyncOrchestrator(vault_client, redlock)
        await _orchestrator.initialize()
        set_orchestrator(_orchestrator)
        
        # Start orchestrator workers in background
        orchestrator_task = asyncio.create_task(_orchestrator.run())
        
        logger.info("Aurora Core Tier-0 started successfully")
        
        yield
        
        # Shutdown
        logger.info("Shutting down Aurora Core Tier-0")
        orchestrator_task.cancel()
        try:
            await orchestrator_task
        except asyncio.CancelledError:
            pass
        
        await _orchestrator.shutdown()
        logger.info("Aurora Core Tier-0 shutdown complete")
        
    except Exception as e:
        logger.error(f"Failed to start Aurora Core: {e}")
        raise


# Create FastAPI app
app = FastAPI(
    title="Aurora Core Tier-0 API",
    description="Trading system core with institutional-grade security and compliance",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Include routers
from src.api.tier0_endpoints import router as api_router
app.include_router(api_router)


# Health endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Aurora Core Tier-0",
        "version": "2.0.0",
        "status": "operational",
        "compliance": ["NIST SP 800-53", "ISO 27001", "SEC 15c3-5", "MiFID II"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check completo"""
    global _health_monitor
    
    if not _health_monitor:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "overall": "CRITICAL"}
        )
    
    matrix = await _health_monitor.check_comprehensive()
    
    return {
        "status": "healthy" if matrix.overall.value >= 2 else "unhealthy",
        "overall": matrix.overall.name,
        "components": {
            name: {
                "level": comp.level.name,
                "latency_ms": comp.latency_ms,
                "status": comp.details.get("status", "unknown")
            }
            for name, comp in matrix.components.items()
        },
        "recommendations": matrix.recommendations,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/live")
async def liveness():
    """Liveness probe - rápido"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/ready")
async def readiness():
    """Readiness probe - verifica dependências"""
    global _health_monitor, _orchestrator
    
    if not _health_monitor or not _orchestrator:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "components_not_initialized"}
        )
    
    if not _orchestrator.is_initialized():
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "orchestrator_not_initialized"}
        )
    
    matrix = await _health_monitor.check_comprehensive()
    
    if matrix.overall.value >= 2:  # STABLE or better
        return {
            "status": "ready",
            "level": matrix.overall.name,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return JSONResponse(
        status_code=503,
        content={
            "status": "not_ready",
            "level": matrix.overall.name,
            "recommendations": matrix.recommendations
        }
    )


@app.get("/health/detailed")
async def health_detailed():
    """Health check detalhado com métricas do sistema"""
    global _health_monitor
    
    if not _health_monitor:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"}
        )
    
    matrix = await _health_monitor.check_comprehensive()
    
    # Métricas do sistema
    try:
        import psutil
        system_info = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        }
    except ImportError:
        system_info = {"note": "psutil not available"}
    
    return {
        "health_matrix": {
            "overall": matrix.overall.name,
            "components": {
                name: comp.model_dump()
                for name, comp in matrix.components.items()
            }
        },
        "system": system_info,
        "environment": {
            "demo_mode": os.getenv("DEMO_MODE", "false"),
            "vault_addr": os.getenv("VAULT_ADDR", "not_set"),
            "redis_nodes": len(os.getenv("REDIS_NODES", "").split(","))
        },
        "audit_trail_count": len(matrix.audit_trail),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def metrics():
    """Endpoint para Prometheus metrics"""
    global _orchestrator, _health_monitor
    
    metrics_output = []
    
    # Health metrics
    if _health_monitor:
        matrix = await _health_monitor.check_comprehensive()
        metrics_output.append(f'aurora_health_level{{overall="true"}} {matrix.overall.value}')
        
        for name, comp in matrix.components.items():
            metrics_output.append(f'aurora_component_health{{component="{name}"}} {comp.level.value}')
            metrics_output.append(f'aurora_component_latency_ms{{component="{name}"}} {comp.latency_ms}')
    
    # Circuit breaker metrics
    if _orchestrator:
        for name, cb in _orchestrator.circuit_breakers.items():
            state = await cb.get_state()
            state_value = 1 if state["state"].value == "OPEN" else 0
            metrics_output.append(f'circuit_breaker_state{{component="{name}",state="OPEN"}} {state_value}')
            metrics_output.append(f'circuit_breaker_failures{{component="{name}"}} {state["failure_count"]}')
    
    return "\n".join(metrics_output)

