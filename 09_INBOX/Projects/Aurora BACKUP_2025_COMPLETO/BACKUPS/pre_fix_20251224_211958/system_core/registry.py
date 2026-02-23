"""
📋 Registro de Módulos NCNT
Gerencia registro e descoberta de módulos
"""

from typing import Dict, List, Optional
from datetime import datetime
from modules.interfaces import NCNTModuleInterface


class NCNTRegistry:
    """
    📋 Registry Central
    Mantém registro de todos os módulos ativos
    """
    
    def __init__(self):
        self.modules: Dict[str, NCNTModuleInterface] = {}
        self.module_metadata: Dict[str, Dict] = {}
    
    def register(self, module: NCNTModuleInterface, metadata: Optional[Dict] = None) -> bool:
        """Registrar novo módulo"""
        try:
            module_id = module.connector_id
            
            if module_id in self.modules:
                return False  # Já registrado
            
            self.modules[module_id] = module
            self.module_metadata[module_id] = {
                "module_name": module.module_name,
                "module_type": module.module_type,
                "registered_at": datetime.now().isoformat(),
                "status": module.status,
                **(metadata or {})
            }
            return True
        except Exception as e:
            print(f"Erro ao registrar módulo: {e}")
            return False
    
    def unregister(self, module_id: str) -> bool:
        """Desregistrar módulo"""
        try:
            if module_id in self.modules:
                del self.modules[module_id]
            if module_id in self.module_metadata:
                del self.module_metadata[module_id]
            return True
        except Exception as e:
            print(f"Erro ao desregistrar módulo: {e}")
            return False
    
    def get_module(self, module_id: str) -> Optional[NCNTModuleInterface]:
        """Obter módulo por ID"""
        return self.modules.get(module_id)
    
    def get_module_by_name(self, module_name: str) -> Optional[NCNTModuleInterface]:
        """Obter módulo por nome"""
        for module in self.modules.values():
            if module.module_name == module_name:
                return module
        return None
    
    def list_modules(self, module_type: Optional[str] = None) -> List[Dict]:
        """Listar todos os módulos (opcionalmente filtrado por tipo)"""
        modules_list = []
        for module_id, module in self.modules.items():
            if module_type is None or module.module_type == module_type:
                modules_list.append({
                    "module_id": module_id,
                    "module_name": module.module_name,
                    "module_type": module.module_type,
                    "status": module.status,
                    "metadata": self.module_metadata.get(module_id, {})
                })
        return modules_list
    
    def get_stats(self) -> Dict:
        """Obter estatísticas do registry"""
        type_counts = {}
        for module in self.modules.values():
            type_counts[module.module_type] = type_counts.get(module.module_type, 0) + 1
        
        return {
            "total_modules": len(self.modules),
            "modules_by_type": type_counts,
            "active_modules": sum(1 for m in self.modules.values() if m.status == "ACTIVE")
        }

