"""
🔄 Barramento de Mensagens NCNT
Sistema de comunicação assíncrona entre módulos
"""

import asyncio
from typing import Dict, List, Callable, Optional
from datetime import datetime
import json
from modules.interfaces import NCNTTransmission


class NCNTMessageBus:
    """
    🔄 Message Bus Central
    Gerencia todas as comunicações entre módulos
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.message_history: List[NCNTTransmission] = []
        self.max_history = 1000
    
    async def start(self):
        """Iniciar message bus"""
        self.running = True
        asyncio.create_task(self._message_processor())
    
    async def stop(self):
        """Parar message bus"""
        self.running = False
    
    def subscribe(self, module_name: str, callback: Callable):
        """Inscrever módulo para receber mensagens"""
        if module_name not in self.subscribers:
            self.subscribers[module_name] = []
        self.subscribers[module_name].append(callback)
    
    def unsubscribe(self, module_name: str, callback: Callable):
        """Desinscrever módulo"""
        if module_name in self.subscribers:
            if callback in self.subscribers[module_name]:
                self.subscribers[module_name].remove(callback)
    
    async def publish(self, transmission: NCNTTransmission) -> bool:
        """Publicar transmissão no bus"""
        try:
            # Adicionar ao histórico
            self.message_history.append(transmission)
            if len(self.message_history) > self.max_history:
                self.message_history.pop(0)
            
            # Adicionar à fila
            await self.message_queue.put(transmission)
            return True
        except Exception as e:
            print(f"Erro ao publicar mensagem: {e}")
            return False
    
    async def _message_processor(self):
        """Processador de mensagens (roda em background)"""
        while self.running:
            try:
                # Aguardar mensagem com timeout
                transmission = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                # Distribuir para subscribers
                await self._distribute_message(transmission)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Erro no processador de mensagens: {e}")
    
    async def _distribute_message(self, transmission: NCNTTransmission):
        """Distribuir mensagem para subscribers"""
        target = transmission.target_module
        
        # Broadcast se target vazio
        if not target:
            for module_name, callbacks in self.subscribers.items():
                for callback in callbacks:
                    try:
                        await callback(transmission)
                    except Exception as e:
                        print(f"Erro ao entregar mensagem para {module_name}: {e}")
        else:
            # Enviar apenas para target específico
            if target in self.subscribers:
                for callback in self.subscribers[target]:
                    try:
                        await callback(transmission)
                    except Exception as e:
                        print(f"Erro ao entregar mensagem para {target}: {e}")
    
    def get_stats(self) -> Dict:
        """Obter estatísticas do message bus"""
        return {
            "subscribers_count": sum(len(callbacks) for callbacks in self.subscribers.values()),
            "queue_size": self.message_queue.qsize(),
            "history_size": len(self.message_history),
            "running": self.running
        }

