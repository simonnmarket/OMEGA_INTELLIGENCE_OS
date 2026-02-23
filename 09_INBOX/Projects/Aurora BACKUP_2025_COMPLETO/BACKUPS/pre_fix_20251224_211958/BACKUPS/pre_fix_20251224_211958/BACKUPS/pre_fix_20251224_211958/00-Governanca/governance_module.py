#!/usr/bin/env python3
"""
GovernanceModule - Módulo NCNT
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

class GovernanceModule(NCNTBaseModule):
    """📜 MÓDULO DE GOVERNANÇA - Nível 00"""
    
    def __init__(self):
        super().__init__("governance_core", ModuleType.GOVERNANCE)
        self.charter = self._create_default_charter()
        self.decision_committee = []
        self.decision_log = []
        self.review_cycles = []
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar comitê
        self.decision_committee = config.get("committee", [
            {"role": "tech_lead", "name": "Sistema Aurora", "weight": 1.0},
            {"role": "risk_officer", "name": "Risk Manager", "weight": 1.0},
            {"role": "compliance", "name": "Compliance Officer", "weight": 1.0}
        ])
        
        self.status = "ACTIVE"
        return True
    
    def _create_default_charter(self) -> Dict:
        """Criar charter padrão Goldman Sachs"""
        return {
            "project_name": "NCNT System - Goldman Sachs Structure",
            "objective": "Sistema de trading modular bank-like com governança institucional",
            "scope": {
                "included": ["Forex", "Metals", "Crypto", "Indices"],
                "excluded": ["Options", "Futures", "High-Frequency (<1ms)"]
            },
            "sla": {
                "uptime": "99.9%",
                "latency": "<50ms",
                "recovery_time": "<5 minutes"
            },
            "raci_matrix": {
                "architecture": {"responsible": "Tech Lead", "accountable": "CTO"},
                "risk_management": {"responsible": "Risk Officer", "accountable": "CRO"},
                "compliance": {"responsible": "Compliance Officer", "accountable": "CCO"}
            },
            "capital_allocation": {
                "initial_capital": 3500.00,
                "risk_per_trade": 0.01,
                "max_drawdown": 0.15
            }
        }
    
    async def register_decision(self, decision_type: str, description: str, 
                               data: Dict, approved_by: List[str]) -> Dict:
        """Registrar decisão no log de governança"""
        decision = {
            "decision_id": f"DEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": decision_type,
            "description": description,
            "data": data,
            "approved_by": approved_by,
            "timestamp": datetime.now().isoformat(),
            "status": "APPROVED"
        }
        
        self.decision_log.append(decision)
        self.update_metric("decisions_registered", len(self.decision_log))
        
        return decision
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões de governança"""
        if transmission.module_type != ModuleType.GOVERNANCE:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "request_approval":
            # Processar solicitação de aprovação
            approval_result = await self._process_approval_request(transmission.payload)
            
            return NCNTTransmission(
                transmission_id=f"GOV_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=approval_result
            )
        
        return None
    
    async def _process_approval_request(self, request_data: Dict) -> Dict:
        """Processar solicitação de aprovação"""
        # Lógica de aprovação baseada em comitê
        requires_vote = request_data.get("requires_vote", False)
        
        if requires_vote:
            # Votação do comitê
            votes = []
            for member in self.decision_committee:
                # Simular votação (na prática seria via UI/API)
                vote = {
                    "member": member["role"],
                    "vote": "APPROVE",  # Simulado
                    "timestamp": datetime.now().isoformat()
                }
                votes.append(vote)
            
            # Registrar decisão
            decision = await self.register_decision(
                decision_type="committee_vote",
                description=f"Aprovação de {request_data.get('item_type')}",
                data=request_data,
                approved_by=[m["role"] for m in self.decision_committee]
            )
            
            return {
                "status": "APPROVED",
                "decision_id": decision["decision_id"],
                "votes": votes,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Aprovação automática para itens de baixo risco
            return {
                "status": "AUTO_APPROVED",
                "reason": "Low risk item - auto-approved",
                "timestamp": datetime.now().isoformat()
            }

# ============================================================================
# 💰 01-DEPARTAMENTOS: TREASURY & CAPITAL
# ============================================================================

@dataclass
class CapitalAllocation:
    """Estrutura de alocação de capital"""
    allocation_id: str
    strategy_id: str
    asset_class: AssetClass
    allocated_amount: Decimal
    allocated_at: datetime
    current_value: Decimal
    roi_percentage: Decimal
    status: str  # ACTIVE, PAUSED, CLOSED
    
    def to_dict(self) -> Dict:
        return {
            "allocation_id": self.allocation_id,
            "strategy_id": self.strategy_id,
            "asset_class": self.asset_class.value,
            "allocated_amount": float(self.allocated_amount),
            "allocated_at": self.allocated_at.isoformat(),
            "current_value": float(self.current_value),
            "roi_percentage": float(self.roi_percentage),
            "status": self.status
        }
