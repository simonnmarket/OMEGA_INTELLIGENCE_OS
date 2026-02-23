from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.last_activity = datetime.utcnow()
        self.config: Dict[str, Any] = {}
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent and its resources."""
        pass
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming data and return results."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up resources and shut down the agent."""
        pass
    
    def update_status(self, status: str) -> None:
        """Update the agent's status."""
        self.status = status
        self.last_activity = datetime.utcnow()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "last_activity": self.last_activity.isoformat(),
            "config": self.config
        }
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update the agent's configuration."""
        self.config.update(config)
    
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data before processing."""
        return True
    
    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle errors during processing."""
        return {
            "error": str(error),
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        } 