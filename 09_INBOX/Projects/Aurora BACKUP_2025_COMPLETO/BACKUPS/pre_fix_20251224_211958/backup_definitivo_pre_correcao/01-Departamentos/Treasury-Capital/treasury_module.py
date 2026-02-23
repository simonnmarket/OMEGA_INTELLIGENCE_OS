#!/usr/bin/env python3
"""
TreasuryModule - Módulo NCNT
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

class TreasuryModule(NCNTBaseModule):
    """💰 MÓDULO DE TESOURARIA - Goldman Sachs Capital Management"""
    
    def __init__(self):
        super().__init__("treasury_core", ModuleType.TREASURY)
        self.capital_pool = Decimal('0.0')
        self.allocations: Dict[str, CapitalAllocation] = {}
        self.reserves: Dict[str, Decimal] = {}
        self.roi_history: Dict[str, List[Decimal]] = {}
        self.rebalance_schedule = {}
        
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar capital inicial
        initial_capital = Decimal(str(config.get("initial_capital", 3500.00)))
        self.capital_pool = initial_capital
        
        # Configurar reservas
        reserve_percentage = Decimal(str(config.get("reserve_percentage", 0.10)))
        self.reserves["operational"] = initial_capital * reserve_percentage
        self.capital_pool -= self.reserves["operational"]
        
        # Configurar schedule de rebalanceamento
        self.rebalance_schedule = config.get("rebalance_schedule", {
            "frequency": "daily",
            "time": "00:00 UTC",
            "threshold": 0.05  # 5% de desvio
        })
        
        self.status = "ACTIVE"
        self.update_metric("capital_pool", float(self.capital_pool))
        
        return True
    
    async def allocate_capital(self, strategy_id: str, amount: Decimal, 
                              asset_class: AssetClass, purpose: str) -> Optional[CapitalAllocation]:
        """Alocar capital para estratégia"""
        if amount <= self.capital_pool:
            self.capital_pool -= amount
            
            allocation = CapitalAllocation(
                allocation_id=f"ALLOC_{uuid.uuid4().hex[:8]}",
                strategy_id=strategy_id,
                asset_class=asset_class,
                allocated_amount=amount,
                allocated_at=datetime.now(),
                current_value=amount,
                roi_percentage=Decimal('0.0'),
                status="ACTIVE"
            )
            
            self.allocations[allocation.allocation_id] = allocation
            self.update_metric("active_allocations", len(self.allocations))
            self.update_metric("capital_pool", float(self.capital_pool))
            
            # Log de alocação
            await self._log_allocation(allocation, purpose)
            
            return allocation
        
        return None
    
    async def update_allocation_value(self, allocation_id: str, new_value: Decimal):
        """Atualizar valor atual da alocação"""
        if allocation_id in self.allocations:
            allocation = self.allocations[allocation_id]
            old_value = allocation.current_value
            allocation.current_value = new_value
            
            # Calcular ROI
            if allocation.allocated_amount > 0:
                allocation.roi_percentage = ((new_value - allocation.allocated_amount) / 
                                            allocation.allocated_amount) * Decimal('100')
            
            # Atualizar histórico
            if allocation.strategy_id not in self.roi_history:
                self.roi_history[allocation.strategy_id] = []
            self.roi_history[allocation.strategy_id].append(allocation.roi_percentage)
            
            self.update_metric(f"roi_{allocation.strategy_id}", float(allocation.roi_percentage))
    
    async def rebalance_allocations(self) -> Dict[str, Any]:
        """Rebalancear alocações automaticamente"""
        rebalance_report = {
            "rebalance_id": f"REBAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "changes": [],
            "reasoning": []
        }
        
        total_allocated = sum(a.allocated_amount for a in self.allocations.values())
        if total_allocated == 0:
            return rebalance_report
        
        # Calcular desvios
        for allocation in self.allocations.values():
            target_percentage = self._get_target_percentage(allocation.strategy_id)
            if not target_percentage:
                continue
                
            current_percentage = (allocation.current_value / total_allocated) * Decimal('100')
            deviation = current_percentage - target_percentage
            
            if abs(deviation) > Decimal(str(self.rebalance_schedule.get("threshold", 0.05))):
                # Necessário rebalancear
                adjustment = (target_percentage - current_percentage) / Decimal('100') * total_allocated
                
                change = {
                    "allocation_id": allocation.allocation_id,
                    "strategy_id": allocation.strategy_id,
                    "current_percentage": float(current_percentage),
                    "target_percentage": float(target_percentage),
                    "deviation": float(deviation),
                    "adjustment": float(adjustment)
                }
                
                rebalance_report["changes"].append(change)
                
                # Aplicar ajuste
                if adjustment > 0:
                    # Adicionar capital
                    if adjustment <= self.capital_pool:
                        await self._add_to_allocation(allocation.allocation_id, adjustment)
                    else:
                        rebalance_report["reasoning"].append(f"Insufficient capital for {allocation.strategy_id}")
                else:
                    # Remover capital
                    await self._remove_from_allocation(allocation.allocation_id, abs(adjustment))
        
        return rebalance_report
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões de tesouraria"""
        if transmission.module_type != ModuleType.TREASURY:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "allocate_capital":
            # Alocar capital
            strategy_id = transmission.payload.get("strategy_id")
            amount = Decimal(str(transmission.payload.get("amount", 0)))
            asset_class = AssetClass(transmission.payload.get("asset_class", "forex"))
            purpose = transmission.payload.get("purpose", "trading")
            
            allocation = await self.allocate_capital(strategy_id, amount, asset_class, purpose)
            
            response_payload = {
                "status": "ALLOCATED" if allocation else "FAILED",
                "allocation": allocation.to_dict() if allocation else None,
                "remaining_capital": float(self.capital_pool)
            }
            
            return NCNTTransmission(
                transmission_id=f"TREAS_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=response_payload
            )
        
        elif action == "get_capital_status":
            # Retornar status do capital
            response_payload = await self.get_capital_status_report()
            
            return NCNTTransmission(
                transmission_id=f"TREAS_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=response_payload
            )
        
        return None
    
    async def get_capital_status_report(self) -> Dict:
        """Gerar relatório completo de status do capital"""
        total_allocated = sum(a.allocated_amount for a in self.allocations.values())
        total_current = sum(a.current_value for a in self.allocations.values())
        total_roi = ((total_current - total_allocated) / total_allocated * Decimal('100')) if total_allocated > 0 else Decimal('0')
        
        return {
            "report_id": f"CAPITAL_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "capital_pool": float(self.capital_pool),
            "total_allocated": float(total_allocated),
            "total_current_value": float(total_current),
            "total_roi_percentage": float(total_roi),
            "active_allocations": len([a for a in self.allocations.values() if a.status == "ACTIVE"]),
            "reserves": {k: float(v) for k, v in self.reserves.items()},
            "allocations": [a.to_dict() for a in self.allocations.values()],
            "rebalance_schedule": self.rebalance_schedule
        }
    
    # ========== MÉTODOS INTERNOS ==========
    
    def _get_target_percentage(self, strategy_id: str) -> Optional[Decimal]:
        """Obter porcentagem alvo para estratégia"""
        # Na prática, viria de configuração
        target_map = {
            "STRAT_ALPHA_01": Decimal('0.30'),  # 30%
            "STRAT_MEAN_REVERSION": Decimal('0.25'),  # 25%
            "STRAT_BREAKOUT": Decimal('0.20'),  # 20%
            "STRAT_TREND": Decimal('0.15'),  # 15%
            "STRAT_ARBITRAGE": Decimal('0.10'),  # 10%
        }
        return target_map.get(strategy_id)
    
    async def _add_to_allocation(self, allocation_id: str, amount: Decimal):
        """Adicionar capital à alocação"""
        if amount <= self.capital_pool:
            allocation = self.allocations[allocation_id]
            allocation.allocated_amount += amount
            allocation.current_value += amount
            self.capital_pool -= amount
    
    async def _remove_from_allocation(self, allocation_id: str, amount: Decimal):
        """Remover capital da alocação"""
        allocation = self.allocations[allocation_id]
        if amount <= allocation.current_value:
            allocation.allocated_amount -= amount
            allocation.current_value -= amount
            self.capital_pool += amount
    
    async def _log_allocation(self, allocation: CapitalAllocation, purpose: str):
        """Registrar log de alocação"""
        log_entry = {
            "event": "CAPITAL_ALLOCATION",
            "allocation_id": allocation.allocation_id,
            "strategy_id": allocation.strategy_id,
            "amount": float(allocation.allocated_amount),
            "asset_class": allocation.asset_class.value,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat(),
            "remaining_capital": float(self.capital_pool)
        }
        
        # Em produção, salvaria em banco de dados
        self.update_metric("allocation_logs", log_entry)

# ============================================================================
# ⚙️ 01-DEPARTAMENTOS: ENGINEERING & INFRASTRUCTURE
# ============================================================================
