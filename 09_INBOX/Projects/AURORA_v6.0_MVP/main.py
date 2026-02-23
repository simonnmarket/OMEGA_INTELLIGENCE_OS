"""
AURORA v6.0 MVP - TIER-0 Integrated
Main Entry Point

Sistema integrado combinando:
- TIER-0 Core (orchestrator, health, auth, circuit breakers)
- v6.0 MVP (strategies, learning, specialized agents)
"""

import os
import sys
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for AURORA v6.0 MVP - TIER-0 Integrated"""
    
    # Set default environment variables
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("VAULT_ADDR", "http://localhost:8200")
    os.environ.setdefault("VAULT_TOKEN", "demo-token")
    os.environ.setdefault("REDIS_NODES", "localhost:6379")
    os.environ.setdefault("HEALTH_CHECK_PORT", "8081")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("HEALTH_CHECK_PORT", "8081"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logger.info("=" * 60)
    logger.info("AURORA v6.0 MVP - TIER-0 INTEGRATED")
    logger.info("=" * 60)
    logger.info(f"Starting on {host}:{port}")
    logger.info(f"Demo mode: {os.getenv('DEMO_MODE', 'false')}")
    logger.info(f"Log level: {log_level}")
    logger.info("Compliance: NIST SP 800-53, ISO 27001, SEC 15c3-5, MiFID II")
    logger.info("=" * 60)
    
    # Run uvicorn with integrated app
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
        reload=reload
    )


if __name__ == "__main__":
    main()
