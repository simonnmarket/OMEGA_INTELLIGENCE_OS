#!/usr/bin/env python3
"""
SOPsModule - Módulo NCNT
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

class SOPsModule(NCNTBaseModule):
    """📑 PROCEDIMENTOS OPERACIONAIS PADRÃO (SOPs)"""
    
    def __init__(self):
        super().__init__("sops_management", ModuleType.DOCUMENTATION)
        self.sops = self._initialize_sops()
        self.procedures = {}
        self.templates = {}
        
    def _initialize_sops(self) -> Dict:
        """Inicializar SOPs padrão"""
        return {
            "trading_operations": {
                "title": "Trading Operations Procedures",
                "version": "1.0",
                "category": "operations",
                "owner": "Trading Desk",
                "status": "active",
                "sections": [
                    "Pre-Market Preparation",
                    "Market Monitoring",
                    "Trade Execution",
                    "Post-Trade Processing",
                    "End of Day Procedures"
                ]
            },
            "risk_management": {
                "title": "Risk Management Procedures",
                "version": "1.0",
                "category": "risk",
                "owner": "Risk Department",
                "status": "active",
                "sections": [
                    "Risk Limit Setting",
                    "Real-Time Monitoring",
                    "Breach Response",
                    "Reporting",
                    "Procedure Updates"
                ]
            },
            "compliance_procedures": {
                "title": "Compliance Procedures",
                "version": "1.0",
                "category": "compliance",
                "owner": "Compliance Department",
                "status": "active",
                "sections": [
                    "Regulatory Monitoring",
                    "Transaction Reporting",
                    "Record Keeping",
                    "Audit Preparation",
                    "Training"
                ]
            },
            "incident_response": {
                "title": "Incident Response Procedures",
                "version": "1.0",
                "category": "operations",
                "owner": "IT Department",
                "status": "active",
                "sections": [
                    "Incident Classification",
                    "Response Activation",
                    "Communication Protocol",
                    "Resolution Process",
                    "Post-Mortem"
                ]
            }
        }
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar gerenciamento de versões
        self.version_control = config.get("version_control", {
            "auto_versioning": True,
            "require_approval": True,
            "retention_policy": "keep_all",
            "audit_trail": True
        })
        
        # Configurar templates
        self.templates = config.get("templates", {
            "procedure_template": {
                "sections": ["Purpose", "Scope", "Responsibilities", "Procedure", "References"],
                "required_fields": ["title", "owner", "category", "version"]
            },
            "checklist_template": {
                "sections": ["Preparation", "Execution", "Verification", "Documentation"],
                "required_fields": ["title", "items", "frequency"]
            }
        })
        
        self.status = "ACTIVE"
        return True
    
    async def create_procedure(self, procedure_data: Dict) -> Dict:
        """Criar novo procedimento"""
        procedure_id = f"SOP_{uuid.uuid4().hex[:8]}"
        
        # Validar dados do procedimento
        validation_result = await self._validate_procedure_data(procedure_data)
        if not validation_result["valid"]:
            return {
                "procedure_id": procedure_id,
                "status": "REJECTED",
                "errors": validation_result["errors"],
                "timestamp": datetime.now().isoformat()
            }
        
        procedure = {
            "procedure_id": procedure_id,
            "title": procedure_data.get("title"),
            "category": procedure_data.get("category"),
            "version": "1.0",
            "status": "DRAFT",
            "created_by": procedure_data.get("created_by", "system"),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "owner": procedure_data.get("owner"),
            "description": procedure_data.get("description", ""),
            "sections": procedure_data.get("sections", []),
            "steps": procedure_data.get("steps", []),
            "references": procedure_data.get("references", []),
            "approval_history": [],
            "review_history": []
        }
        
        self.procedures[procedure_id] = procedure
        
        return {
            "procedure_id": procedure_id,
            "status": "CREATED",
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões de SOPs"""
        if transmission.module_type != ModuleType.DOCUMENTATION:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "create_procedure":
            # Criar procedimento
            procedure_data = transmission.payload.get("procedure_data", {})
            creation_result = await self.create_procedure(procedure_data)
            
            return NCNTTransmission(
                transmission_id=f"SOPS_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=creation_result
            )
        
        elif action == "get_procedure":
            # Obter procedimento
            procedure_id = transmission.payload.get("procedure_id")
            procedure = await self.get_procedure(procedure_id)
            
            return NCNTTransmission(
                transmission_id=f"SOPS_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=procedure
            )
        
        return None
    
    # ========== MÉTODOS DE VALIDAÇÃO ==========
    
    async def _validate_procedure_data(self, procedure_data: Dict) -> Dict:
        """Validar dados do procedimento"""
        errors = []
        
        required_fields = ["title", "category", "owner"]
        for field in required_fields:
            if field not in procedure_data:
                errors.append(f"Missing required field: {field}")
        
        # Validar categoria
        valid_categories = ["operations", "risk", "compliance", "it", "finance", "hr"]
        if procedure_data.get("category") not in valid_categories:
            errors.append(f"Invalid category. Must be one of: {valid_categories}")
        
        # Validar seções
        if "sections" in procedure_data and not isinstance(procedure_data["sections"], list):
            errors.append("Sections must be a list")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def get_procedure(self, procedure_id: str) -> Dict:
        """Obter procedimento específico"""
        if procedure_id not in self.procedures:
            return {"error": f"Procedure {procedure_id} not found", "status": "NOT_FOUND"}
        
        procedure = self.procedures[procedure_id]
        
        return {
            "procedure_id": procedure_id,
            "title": procedure["title"],
            "category": procedure["category"],
            "version": procedure["version"],
            "status": procedure["status"],
            "owner": procedure["owner"],
            "created_at": procedure["created_at"],
            "last_updated": procedure["last_updated"],
            "sections": procedure["sections"],
            "steps": procedure["steps"],
            "references": procedure["references"]
        }

# ============================================================================
# ✅ 06-MONITORAMENTO: FEEDBACK LOOP
# ============================================================================
