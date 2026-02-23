#!/usr/bin/env python3
"""
Script para iniciar o servidor AURORA CORE TIER-0
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set environment variables for demo mode
os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("VAULT_ADDR", "http://localhost:8200")
os.environ.setdefault("VAULT_TOKEN", "demo-token")
os.environ.setdefault("REDIS_NODES", "localhost:6379")
os.environ.setdefault("HEALTH_CHECK_PORT", "8081")
os.environ.setdefault("LOG_LEVEL", "INFO")


def main():
    """Start the server"""
    print("🚀 Starting AURORA CORE TIER-0 Server...")
    print(f"   Mode: {'DEMO' if os.getenv('DEMO_MODE') == 'true' else 'PRODUCTION'}")
    print(f"   Port: {os.getenv('HEALTH_CHECK_PORT')}")
    print()
    
    from main import main as run_server
    run_server()


if __name__ == "__main__":
    main()

