"""
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
        app.include_router(router)