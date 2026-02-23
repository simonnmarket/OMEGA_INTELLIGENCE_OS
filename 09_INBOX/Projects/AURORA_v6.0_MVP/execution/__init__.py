"""
Execution module for AURORA v6.0 MVP - TIER-0 Integrated
"""

from .safe_execution_tier0 import Tier0ExecutionEngine

# Backward compatibility
ExecutionEngine = Tier0ExecutionEngine

__all__ = ["Tier0ExecutionEngine", "ExecutionEngine"]

