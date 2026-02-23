"""
AURORA CORE TIER-0 - Main Entry Point
Production-ready trading system
"""

import os
import sys
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("HEALTH_CHECK_PORT", "8081"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logger.info(f"Starting Aurora Core Tier-0 on {host}:{port}")
    logger.info(f"Demo mode: {os.getenv('DEMO_MODE', 'false')}")
    logger.info(f"Log level: {log_level}")
    
    # Run uvicorn
    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
        reload=reload
    )


if __name__ == "__main__":
    main()

