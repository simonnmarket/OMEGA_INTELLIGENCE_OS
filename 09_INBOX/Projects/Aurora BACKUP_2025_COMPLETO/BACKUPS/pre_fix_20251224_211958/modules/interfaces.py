"""
🔌 Interfaces Padrão NCNT
Formato padrão de transmissão para todos os módulos
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json
import hashlib
import uuid
from abc import ABC, abstractmethod


class NCNTTransmission:
    """
    📦 Formato Padrão de Transmissão NCNT
    Todas as comunicações entre módulos usam este formato
    """
    
    def __init__(
        self,
        transmission_id: Optional[str] = None,
        source_module: str = "",
        target_module: str = "",
        module_type: str = "",
        timestamp: Optional[datetime] = None,
        payload: Dict[str, Any] = None,
        checksum: Optional[str] = None
    ):
        self.transmission_id = transmission_id or f"TX_{uuid.uuid4().hex[:12]}"
        self.source_module = source_module
        self.target_module = target_module
        self.module_type = module_type
        self.timestamp = timestamp or datetime.now()
        self.payload = payload or {}
        self.checksum = checksum or self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calcular checksum SHA-256 para integridade"""
        data_str = json.dumps({
            "source": self.source_module,
            "target": self.target_module,
            "type": self.module_type,
            "payload": self.payload
        }, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def validate(self) -> bool:
        """Validar integridade da transmissão"""
        expected_checksum = self._calculate_checksum()
        return self.checksum == expected_checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "transmission_id": self.transmission_id,
            "source_module": self.source_module,
            "target_module": self.target_module,
            "module_type": self.module_type,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "checksum": self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NCNTTransmission":
        """Criar a partir de dicionário"""
        timestamp = datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"]
        return cls(
            transmission_id=data.get("transmission_id"),
            source_module=data.get("source_module", ""),
            target_module=data.get("target_module", ""),
            module_type=data.get("module_type", ""),
            timestamp=timestamp,
            payload=data.get("payload", {}),
            checksum=data.get("checksum")
        )


class NCNTModuleInterface(ABC):
    """
    🔌 Interface Padrão para Todos os Módulos NCNT
    Todos os módulos devem implementar esta interface
    """
    
    def __init__(self, module_name: str, module_type: str):
        self.module_name = module_name
        self.module_type = module_type
        self.status = "INACTIVE"
        self.config = {}
        self.connector_id = f"CONN_{module_type.upper()}_{module_name.upper()}"
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializar módulo com configuração"""
        pass
    
    @abstractmethod
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissão recebida"""
        pass
    
    async def shutdown(self) -> bool:
        """Encerrar módulo de forma segura"""
        self.status = "SHUTDOWN"
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status do módulo"""
        return {
            "module_name": self.module_name,
            "module_type": self.module_type,
            "status": self.status,
            "connector_id": self.connector_id
        }


class NCNTStandardConnector(NCNTModuleInterface):
    """
    🔌 Conector Padrão NCNT
    Implementação base para todos os módulos
    """
    
    def __init__(self, module_name: str, module_type: str):
        super().__init__(module_name, module_type)
        self.standard_config = {
            "input_format": "NCNTTransmission",
            "output_format": "NCNTTransmission",
            "validation_required": True,
            "ack_required": True,
            "timeout_seconds": 30
        }
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializar conector com configuração padrão"""
        self.config = {**self.standard_config, **config}
        self.status = "ACTIVE"
        return True
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissão no formato padrão"""
        
        # Validação padrão
        if self.config.get("validation_required", True):
            if not transmission.validate():
                return self._create_error_response("Transmissão inválida", transmission)
        
        # Roteamento padrão
        if transmission.target_module == self.module_name:
            # Processar no módulo específico
            result = await self._process_module_specific(transmission.payload)
            
            # Resposta padrão
            return NCNTTransmission(
                transmission_id=f"RESP_{uuid.uuid4().hex[:12]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                timestamp=datetime.now(),
                payload=result,
                checksum=None  # Será calculado automaticamente
            )
        
        return None
    
    async def _process_module_specific(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processamento específico do módulo (deve ser sobrescrito)"""
        return {"status": "processed", "payload": payload}
    
    def _create_error_response(self, error_message: str, original_transmission: NCNTTransmission) -> NCNTTransmission:
        """Criar resposta de erro padrão"""
        return NCNTTransmission(
            transmission_id=f"ERR_{uuid.uuid4().hex[:12]}",
            source_module=self.module_name,
            target_module=original_transmission.source_module,
            module_type=self.module_type,
            timestamp=datetime.now(),
            payload={
                "error": error_message,
                "original_transmission_id": original_transmission.transmission_id,
                "status": "ERROR"
            },
            checksum=None
        )

