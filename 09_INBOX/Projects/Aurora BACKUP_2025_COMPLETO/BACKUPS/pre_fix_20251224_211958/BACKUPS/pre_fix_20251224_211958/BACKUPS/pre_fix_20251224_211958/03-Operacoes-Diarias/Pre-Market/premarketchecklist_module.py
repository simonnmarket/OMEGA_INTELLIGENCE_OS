#!/usr/bin/env python3
"""
PreMarketChecklistModule - Módulo NCNT
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

class PreMarketChecklistModule(NCNTBaseModule):
    """🕒 CHECKLIST PRÉ-MERCADO - Validação Automatizada"""
    
    def __init__(self):
        super().__init__("pre_market_checklist", ModuleType.OPERATION)
        self.checklist_items = self._initialize_checklist()
        self.check_results = {}
        self.daily_reports = {}
        
    def _initialize_checklist(self) -> List[Dict]:
        """Inicializar itens do checklist"""
        return [
            {
                "id": "data_feeds",
                "name": "Data Feeds Connectivity",
                "description": "Verify all market data feeds are connected",
                "critical": True,
                "auto_check": True,
                "threshold": 1.0,  # 100% must pass
                "check_type": "connectivity"
            },
            {
                "id": "risk_limits",
                "name": "Risk Limits Validation",
                "description": "Verify risk limits are loaded and active",
                "critical": True,
                "auto_check": True,
                "threshold": 1.0,
                "check_type": "configuration"
            },
            {
                "id": "system_health",
                "name": "System Health Status",
                "description": "Check overall system health and resources",
                "critical": True,
                "auto_check": True,
                "threshold": 0.9,  # 90% must be healthy
                "check_type": "health"
            },
            {
                "id": "capital_availability",
                "name": "Capital Availability",
                "description": "Verify sufficient capital for trading",
                "critical": True,
                "auto_check": True,
                "threshold": 1.0,
                "check_type": "financial"
            },
            {
                "id": "compliance_rules",
                "name": "Compliance Rules Loaded",
                "description": "Ensure compliance rules are active",
                "critical": True,
                "auto_check": True,
                "threshold": 1.0,
                "check_type": "compliance"
            },
            {
                "id": "backup_systems",
                "name": "Backup Systems Online",
                "description": "Verify backup and failover systems",
                "critical": False,
                "auto_check": True,
                "threshold": 0.8,
                "check_type": "redundancy"
            },
            {
                "id": "monitoring_dashboard",
                "name": "Monitoring Dashboard Active",
                "description": "Check real-time monitoring",
                "critical": False,
                "auto_check": True,
                "threshold": 1.0,
                "check_type": "monitoring"
            },
            {
                "id": "news_sources",
                "name": "News & Event Sources",
                "description": "Verify news and economic calendar feeds",
                "critical": False,
                "auto_check": True,
                "threshold": 0.7,
                "check_type": "information"
            },
            {
                "id": "api_connections",
                "name": "API Connections",
                "description": "Check external API connections",
                "critical": True,
                "auto_check": True,
                "threshold": 1.0,
                "check_type": "connectivity"
            },
            {
                "id": "manual_review",
                "name": "Manual Systems Review",
                "description": "Requires manual verification",
                "critical": True,
                "auto_check": False,
                "check_type": "manual"
            }
        ]
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar schedule
        self.check_schedule = config.get("check_schedule", {
            "pre_market": "06:00 UTC",
            "intraday": ["12:00 UTC", "18:00 UTC"],
            "post_market": "22:00 UTC"
        })
        
        # Configurar alertas
        self.alert_config = config.get("alert_config", {
            "email_on_failure": True,
            "slack_on_critical": True,
            "auto_retry_failed": True,
            "retry_attempts": 3
        })
        
        self.status = "ACTIVE"
        return True
    
    async def run_checklist(self, check_type: str = "pre_market") -> Dict:
        """Executar checklist completo"""
        checklist_id = f"CHECK_{check_type.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        checklist_run = {
            "checklist_id": checklist_id,
            "type": check_type,
            "started_at": datetime.now().isoformat(),
            "status": "RUNNING",
            "items": [],
            "summary": {
                "total_items": 0,
                "passed_items": 0,
                "failed_items": 0,
                "critical_failures": 0,
                "manual_required": 0
            }
        }
        
        print(f"🕒 Running {check_type} checklist: {checklist_id}")
        
        # Executar cada item
        for item in self.checklist_items:
            item_result = await self._run_checklist_item(item, check_type)
            checklist_run["items"].append(item_result)
            
            # Atualizar sumário
            checklist_run["summary"]["total_items"] += 1
            
            if item_result["status"] == "PASSED":
                checklist_run["summary"]["passed_items"] += 1
            elif item_result["status"] == "FAILED":
                checklist_run["summary"]["failed_items"] += 1
                if item["critical"]:
                    checklist_run["summary"]["critical_failures"] += 1
            
            if not item["auto_check"]:
                checklist_run["summary"]["manual_required"] += 1
        
        # Determinar status geral
        if checklist_run["summary"]["critical_failures"] > 0:
            checklist_run["status"] = "CRITICAL_FAILURE"
            checklist_run["system_ready"] = False
        elif checklist_run["summary"]["failed_items"] > 0:
            checklist_run["status"] = "WARNING"
            checklist_run["system_ready"] = True
        else:
            checklist_run["status"] = "SUCCESS"
            checklist_run["system_ready"] = True
        
        checklist_run["completed_at"] = datetime.now().isoformat()
        checklist_run["duration_seconds"] = (
            datetime.fromisoformat(checklist_run["completed_at"]) - 
            datetime.fromisoformat(checklist_run["started_at"])
        ).total_seconds()
        
        # Armazenar resultados
        self.check_results[checklist_id] = checklist_run
        self.daily_reports[datetime.now().strftime("%Y-%m-%d")] = checklist_run
        
        # Enviar notificações se necessário
        if checklist_run["status"] != "SUCCESS":
            await self._send_checklist_alerts(checklist_run)
        
        return checklist_run
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões do checklist"""
        if transmission.module_type != ModuleType.OPERATION:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "run_checklist":
            # Executar checklist
            check_type = transmission.payload.get("check_type", "pre_market")
            results = await self.run_checklist(check_type)
            
            return NCNTTransmission(
                transmission_id=f"CHECK_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=results
            )
        
        elif action == "get_checklist_status":
            # Obter status do checklist
            checklist_id = transmission.payload.get("checklist_id")
            status = await self.get_checklist_status(checklist_id)
            
            return NCNTTransmission(
                transmission_id=f"CHECK_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=status
            )
        
        return None
    
    # ========== MÉTODOS DE EXECUÇÃO ==========
    
    async def _run_checklist_item(self, item: Dict, check_type: str) -> Dict:
        """Executar item individual do checklist"""
        item_start = datetime.now()
        
        result = {
            "item_id": item["id"],
            "name": item["name"],
            "description": item["description"],
            "critical": item["critical"],
            "started_at": item_start.isoformat(),
            "status": "PENDING",
            "details": {}
        }
        
        try:
            if item["auto_check"]:
                # Executar verificação automática
                check_result = await self._execute_auto_check(item, check_type)
                result.update(check_result)
            else:
                # Marcar como requerendo verificação manual
                result["status"] = "MANUAL_REQUIRED"
                result["output"] = "Requires manual verification"
                result["details"] = {"manual_check": True}
            
        except Exception as e:
            result["status"] = "FAILED"
            result["output"] = f"Check failed with error: {str(e)}"
            result["error"] = str(e)
        
        # Calcular duração
        item_end = datetime.now()
        result["completed_at"] = item_end.isoformat()
        result["duration_seconds"] = (item_end - item_start).total_seconds()
        
        return result
    
    async def _execute_auto_check(self, item: Dict, check_type: str) -> Dict:
        """Executar verificação automática"""
        check_type = item["check_type"]
        
        # Simular diferentes tipos de verificação
        import random
        
        if check_type == "connectivity":
            # Verificação de conectividade
            success_rate = random.uniform(0.8, 1.0)
            passed = success_rate >= item["threshold"]
            
            return {
                "status": "PASSED" if passed else "FAILED",
                "output": f"Connectivity check: {success_rate:.1%} success rate",
                "details": {
                    "success_rate": success_rate,
                    "threshold": item["threshold"],
                    "endpoints_tested": random.randint(5, 15),
                    "average_latency": random.uniform(10, 50)
                }
            }
        
        elif check_type == "configuration":
            # Verificação de configuração
            configs_checked = random.randint(10, 30)
            configs_valid = random.randint(int(configs_checked * 0.9), configs_checked)
            success_rate = configs_valid / configs_checked
            passed = success_rate >= item["threshold"]
            
            return {
                "status": "PASSED" if passed else "FAILED",
                "output": f"Configuration check: {configs_valid}/{configs_checked} valid",
                "details": {
                    "configs_checked": configs_checked,
                    "configs_valid": configs_valid,
                    "success_rate": success_rate,
                    "threshold": item["threshold"]
                }
            }
        
        elif check_type == "health":
            # Verificação de saúde
            components = ["database", "api", "cache", "queue", "storage"]
            healthy_components = random.sample(components, random.randint(3, len(components)))
            success_rate = len(healthy_components) / len(components)
            passed = success_rate >= item["threshold"]
            
            return {
                "status": "PASSED" if passed else "FAILED",
                "output": f"Health check: {len(healthy_components)}/{len(components)} components healthy",
                "details": {
                    "components": components,
                    "healthy_components": healthy_components,
                    "success_rate": success_rate,
                    "threshold": item["threshold"]
                }
            }
        
        elif check_type == "financial":
            # Verificação financeira
            capital_available = random.uniform(5000, 15000)
            required_capital = 10000
            success_rate = capital_available / required_capital
            passed = success_rate >= item["threshold"]
            
            return {
                "status": "PASSED" if passed else "FAILED",
                "output": f"Capital check: ${capital_available:.2f} available",
                "details": {
                    "capital_available": capital_available,
                    "required_capital": required_capital,
                    "success_rate": success_rate,
                    "threshold": item["threshold"]
                }
            }
        
        else:
            # Verificação genérica
            success = random.random() >= 0.1  # 90% success rate
            
            return {
                "status": "PASSED" if success else "FAILED",
                "output": f"{check_type} check {'passed' if success else 'failed'}",
                "details": {"simulated": True, "check_type": check_type}
            }
    
    # ========== MÉTODOS DE NOTIFICAÇÃO ==========
    
    async def _send_checklist_alerts(self, checklist_run: Dict):
        """Enviar alertas de checklist"""
        if checklist_run["status"] == "CRITICAL_FAILURE":
            print(f"🚨 CRITICAL: Checklist {checklist_run['checklist_id']} failed with critical items!")
            print(f"   System NOT ready for trading")
        elif checklist_run["status"] == "WARNING":
            print(f"⚠️ WARNING: Checklist {checklist_run['checklist_id']} has warnings")
            print(f"   System ready but needs attention")
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def get_checklist_status(self, checklist_id: str) -> Dict:
        """Obter status do checklist"""
        if checklist_id not in self.check_results:
            return {"error": f"Checklist {checklist_id} not found", "status": "UNKNOWN"}
        
        checklist = self.check_results[checklist_id]
        
        return {
            "checklist_id": checklist_id,
            "type": checklist["type"],
            "status": checklist["status"],
            "system_ready": checklist["system_ready"],
            "started_at": checklist["started_at"],
            "completed_at": checklist["completed_at"],
            "duration_seconds": checklist["duration_seconds"],
            "summary": checklist["summary"],
            "critical_items": [
                item for item in checklist["items"] 
                if item["critical"] and item["status"] != "PASSED"
            ]
        }

# ============================================================================
# 📤 03-OPERAÇÕES DIÁRIAS: EXECUTION WINDOW
# ============================================================================
