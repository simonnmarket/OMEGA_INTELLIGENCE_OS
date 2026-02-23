"""
Connectors module for AURORA v6.0 MVP - TIER-0 Integrated
"""

from .mt5_connector_tier0 import Tier0MT5Connector

# Backward compatibility
MT5Connector = Tier0MT5Connector

__all__ = ["Tier0MT5Connector", "MT5Connector"]

