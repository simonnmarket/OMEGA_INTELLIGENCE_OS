"""
OMEGA Intelligence OS - Base Agent Architecture
Defines the abstract base class for all trading and analytical agents in the ecosystem.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseOmegaAgent(ABC):
    def __init__(self, name: str, layer: int, specialization: str):
        self.name = name
        self.layer = layer
        self.specialization = specialization
        self.status = "INITIALIZED"
        self.metrics: Dict[str, Any] = {}

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core processing logic of the agent. Must be implemented by subclasses.
        Accepts state/market data and returns decisions/analysis.
        """
        pass

    def get_status(self) -> str:
        return self.status

    def set_status(self, new_status: str):
        self.status = new_status
        
    def info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "layer": self.layer,
            "specialization": self.specialization,
            "status": self.status
        }
