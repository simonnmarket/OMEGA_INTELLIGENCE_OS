#!/usr/bin/env python3
"""
ModuleRegistry - Módulo NCNT
Extraído do sistema completo NCNT v2.0
"""

import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.ncnt_base import (
    ModuleType,
    AssetClass,
    TransmissionPriority,
    NCNTTransmission,
    NCNTBaseModule
)
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
import hashlib
import uuid
from pathlib import Path
import logging
import asyncio
from abc import ABC, abstractmethod
import pickle
import csv
from decimal import Decimal

class ModuleRegistry(NCNTBaseModule):
    """📦 REGISTRO DE MÓDULOS - Gerenciamento de Módulos NCNT"""
    
    def __init__(self):
        super().__init__("module_registry", ModuleType.INFRASTRUCTURE)
        self.modules = {}
        self.dependencies = {}
        self.version_history = {}
        self.health_status = {}
        
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar registro
        self.registry_config = config.get("registry_config", {
            "auto_discovery": True,
            "health_check_interval": 60,
            "dependency_resolution": True,
            "version_validation": True
        })
        
        self.status = "ACTIVE"
        return True
    
    async def register_module(self, module_info: Dict) -> Dict:
        """Registrar novo módulo"""
        module_id = module_info.get("module_id")
        
        if not module_id:
            return {"error": "Module ID required", "status": "REJECTED"}
        
        if module_id in self.modules:
            return {"error": f"Module {module_id} already registered", "status": "DUPLICATE"}
        
        # Validar informações do módulo
        validation_result = await self._validate_module_info(module_info)
        if not validation_result["valid"]:
            return {
                "error": f"Module validation failed: {validation_result['errors']}",
                "status": "INVALID"
            }
        
        # Registrar módulo
        module_record = {
            "module_id": module_id,
            "module_name": module_info.get("module_name"),
            "module_type": module_info.get("module_type"),
            "version": module_info.get("version", "1.0.0"),
            "status": "REGISTERED",
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "endpoint": module_info.get("endpoint"),
            "capabilities": module_info.get("capabilities", []),
            "dependencies": module_info.get("dependencies", []),
            "config": module_info.get("config", {}),
            "metadata": module_info.get("metadata", {})
        }
        
        self.modules[module_id] = module_record
        
        # Registrar dependências
        for dep in module_record["dependencies"]:
            if dep not in self.dependencies:
                self.dependencies[dep] = []
            self.dependencies[dep].append(module_id)
        
        # Iniciar monitoramento de saúde
        asyncio.create_task(self._monitor_module_health(module_id))
        
        return {
            "status": "REGISTERED",
            "module_id": module_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões do registro de módulos"""
        if transmission.module_type != ModuleType.INFRASTRUCTURE:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "register_module":
            # Registrar módulo
            module_info = transmission.payload.get("module_info", {})
            registration_result = await self.register_module(module_info)
            
            return NCNTTransmission(
                transmission_id=f"REGISTRY_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=registration_result
            )
        
        elif action == "discover_modules":
            # Descobrir módulos
            module_type = transmission.payload.get("module_type")
            modules = await self.discover_modules(module_type)
            
            return NCNTTransmission(
                transmission_id=f"REGISTRY_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=modules
            )
        
        return None
    
    # ========== MÉTODOS DE VALIDAÇÃO ==========
    
    async def _validate_module_info(self, module_info: Dict) -> Dict:
        """Validar informações do módulo"""
        errors = []
        
        required_fields = ["module_id", "module_name", "module_type"]
        for field in required_fields:
            if field not in module_info:
                errors.append(f"Missing required field: {field}")
        
        # Validar tipo de módulo
        valid_types = [mt.value for mt in ModuleType]
        if module_info.get("module_type") not in valid_types:
            errors.append(f"Invalid module type. Must be one of: {valid_types}")
        
        # Validar versão
        version = module_info.get("version", "1.0.0")
        if not self._is_valid_version(version):
            errors.append(f"Invalid version format: {version}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    def _is_valid_version(self, version: str) -> bool:
        """Verificar se versão é válida"""
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
    
    # ========== MÉTODOS DE DESCOBERTA ==========
    
    async def discover_modules(self, module_type: Optional[str] = None) -> Dict:
        """Descobrir módulos registrados"""
        if module_type:
            filtered_modules = {
                mid: module for mid, module in self.modules.items()
                if module["module_type"] == module_type
            }
        else:
            filtered_modules = self.modules
        
        # Agrupar por tipo
        modules_by_type = {}
        for module in filtered_modules.values():
            mtype = module["module_type"]
            if mtype not in modules_by_type:
                modules_by_type[mtype] = []
            modules_by_type[mtype].append(module)
        
        return {
            "discovery_id": f"DISCOVERY_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "total_modules": len(filtered_modules),
            "modules_by_type": modules_by_type,
            "health_summary": await self._get_health_summary(filtered_modules)
        }
    
    async def _get_health_summary(self, modules: Dict) -> Dict:
        """Obter resumo de saúde dos módulos"""
        status_counts = {
            "HEALTHY": 0,
            "UNHEALTHY": 0,
            "UNKNOWN": 0
        }
        
        for module_id in modules.keys():
            health = self.health_status.get(module_id, "UNKNOWN")
            status_counts[health] += 1
        
        return status_counts
    
    # ========== MÉTODOS DE MONITORAMENTO ==========
    
    async def _monitor_module_health(self, module_id: str):
        """Monitorar saúde do módulo"""
        while True:
            if module_id not in self.modules:
                break
            
            module = self.modules[module_id]
            endpoint = module.get("endpoint")
            
            if endpoint:
                health_status = await self._check_module_health(endpoint)
                self.health_status[module_id] = health_status
                
                # Atualizar último heartbeat
                self.modules[module_id]["last_heartbeat"] = datetime.now().isoformat()
            
            # Aguardar próximo check
            await asyncio.sleep(self.registry_config["health_check_interval"])
    
    async def _check_module_health(self, endpoint: str) -> str:
        """Verificar saúde do módulo"""
        # Implementação simplificada
        import random
        
        # Simular verificação de saúde
        success_rate = 0.95  # 95% success rate
        
        if random.random() < success_rate:
            return "HEALTHY"
        else:
            return "UNHEALTHY"

# ============================================================================
# 📑 05-DOCUMENTAÇÃO: STANDARD OPERATING PROCEDURES
# ============================================================================
