"""
🎼 Orquestrador Principal NCNT
Coordena todos os módulos e operações do sistema
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from .message_bus import NCNTMessageBus
from .registry import NCNTRegistry
from modules.interfaces import NCNTModuleInterface, NCNTTransmission


class NCNTOrchestrator:
    """
    🎼 Orquestrador Principal
    Gerencia ciclo de vida e comunicação entre módulos
    """
    
    def __init__(self):
        self.message_bus = NCNTMessageBus()
        self.registry = NCNTRegistry()
        self.running = False
        self.start_time: Optional[datetime] = None
    
    async def start(self):
        """Iniciar orquestrador e sistema"""
        print("🚀 Iniciando AURORA NCNT System...")
        
        self.running = True
        self.start_time = datetime.now()
        
        # Iniciar message bus
        await self.message_bus.start()
        print("✅ Message Bus iniciado")
        
        print("✅ Sistema AURORA NCNT iniciado com sucesso!")
    
    async def stop(self):
        """Parar orquestrador e sistema"""
        print("🛑 Parando AURORA NCNT System...")
        
        # Parar message bus
        await self.message_bus.stop()
        
        # Desregistrar todos os módulos
        for module_id in list(self.registry.modules.keys()):
            module = self.registry.get_module(module_id)
            if module:
                await module.shutdown()
            self.registry.unregister(module_id)
        
        self.running = False
        print("✅ Sistema AURORA NCNT parado")
    
    def register_module(self, module: NCNTModuleInterface, metadata: Optional[Dict] = None) -> bool:
        """Registrar novo módulo no sistema"""
        success = self.registry.register(module, metadata)
        
        if success:
            # Inscrever módulo no message bus
            async def message_handler(transmission: NCNTTransmission):
                response = await module.process_transmission(transmission)
                if response:
                    await self.message_bus.publish(response)
            
            self.message_bus.subscribe(module.module_name, message_handler)
            print(f"✅ Módulo registrado: {module.module_name} ({module.connector_id})")
        
        return success
    
    def unregister_module(self, module_id: str) -> bool:
        """Desregistrar módulo do sistema"""
        module = self.registry.get_module(module_id)
        if module:
            # Desinscrever do message bus
            # (implementar callback tracking se necessário)
            pass
        
        return self.registry.unregister(module_id)
    
    async def send_transmission(
        self,
        source_module: str,
        target_module: str,
        module_type: str,
        payload: Dict
    ) -> bool:
        """Enviar transmissão entre módulos"""
        transmission = NCNTTransmission(
            source_module=source_module,
            target_module=target_module,
            module_type=module_type,
            payload=payload
        )
        
        return await self.message_bus.publish(transmission)
    
    def get_system_status(self) -> Dict:
        """Obter status completo do sistema"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "system": "AURORA NCNT",
            "version": "1.0.0",
            "running": self.running,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "registry_stats": self.registry.get_stats(),
            "message_bus_stats": self.message_bus.get_stats()
        }
    
    def list_all_modules(self) -> List[Dict]:
        """Listar todos os módulos registrados"""
        return self.registry.list_modules()

