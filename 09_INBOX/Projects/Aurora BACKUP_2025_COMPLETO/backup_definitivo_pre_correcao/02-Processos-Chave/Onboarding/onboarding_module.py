#!/usr/bin/env python3
"""
OnboardingModule - Módulo NCNT
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

class OnboardingModule(NCNTBaseModule):
    """📥 PROCESSO DE ONBOARDING - Novos dados, estratégias, contrapartes"""
    
    def __init__(self):
        super().__init__("onboarding_core", ModuleType.PROCESS)
        self.onboarding_pipelines = {
            "data": self._create_data_onboarding_pipeline(),
            "strategy": self._create_strategy_onboarding_pipeline(),
            "counterparty": self._create_counterparty_onboarding_pipeline()
        }
        self.onboarding_requests = {}
        self.approval_workflows = {}
        
    def _create_data_onboarding_pipeline(self) -> Dict:
        """Criar pipeline para onboarding de dados"""
        return {
            "stages": [
                {"name": "data_validation", "description": "Validar formato e integridade"},
                {"name": "source_verification", "description": "Verificar fonte dos dados"},
                {"name": "quality_assessment", "description": "Avaliar qualidade dos dados"},
                {"name": "integration_testing", "description": "Testar integração com sistema"},
                {"name": "approval_request", "description": "Solicitar aprovação"},
                {"name": "production_deployment", "description": "Implementar em produção"}
            ],
            "estimated_duration_days": 7,
            "required_approvals": ["data_engineer", "compliance_officer"]
        }
    
    def _create_strategy_onboarding_pipeline(self) -> Dict:
        """Criar pipeline para onboarding de estratégias"""
        return {
            "stages": [
                {"name": "strategy_review", "description": "Revisar lógica da estratégia"},
                {"name": "backtesting", "description": "Executar backtests completos"},
                {"name": "risk_assessment", "description": "Avaliar riscos da estratégia"},
                {"name": "compliance_check", "description": "Verificar conformidade"},
                {"name": "paper_trading", "description": "Testar em ambiente simulado"},
                {"name": "committee_approval", "description": "Aprovação do comitê"},
                {"name": "production_activation", "description": "Ativar em produção"}
            ],
            "estimated_duration_days": 30,
            "required_approvals": ["risk_officer", "compliance_officer", "trading_committee"]
        }
    
    def _create_counterparty_onboarding_pipeline(self) -> Dict:
        """Criar pipeline para onboarding de contrapartes"""
        return {
            "stages": [
                {"name": "kyc_check", "description": "Verificação Know Your Customer"},
                {"name": "aml_screening", "description": "Triagem Anti-Money Laundering"},
                {"name": "credit_check", "description": "Avaliação de crédito"},
                {"name": "legal_documentation", "description": "Documentação legal"},
                {"name": "risk_assessment", "description": "Avaliação de risco"},
                {"name": "compliance_approval", "description": "Aprovação de compliance"},
                {"name": "account_setup", "description": "Configuração da conta"}
            ],
            "estimated_duration_days": 14,
            "required_approvals": ["compliance_officer", "risk_officer", "legal_department"]
        }
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar workflows de aprovação
        self.approval_workflows = config.get("approval_workflows", {
            "auto_approve_low_risk": True,
            "require_multiple_approvers": True,
            "escalation_time_hours": 24,
            "audit_trail_required": True
        })
        
        self.status = "ACTIVE"
        return True
    
    async def onboard_data_source(self, data_source_config: Dict) -> Dict:
        """Onboard de nova fonte de dados"""
        onboarding_id = f"ONBOARD_DATA_{uuid.uuid4().hex[:8]}"
        
        onboarding_request = {
            "onboarding_id": onboarding_id,
            "type": "data",
            "source_name": data_source_config.get("name"),
            "source_type": data_source_config.get("type", "api"),
            "submitted_by": data_source_config.get("submitted_by", "system"),
            "submitted_at": datetime.now().isoformat(),
            "status": "SUBMITTED",
            "current_stage": "data_validation",
            "stages": [],
            "config": data_source_config
        }
        
        self.onboarding_requests[onboarding_id] = onboarding_request
        
        # Iniciar pipeline
        asyncio.create_task(self._execute_onboarding_pipeline(onboarding_request))
        
        return onboarding_request
    
    async def onboard_strategy(self, strategy_config: Dict, developer: str) -> Dict:
        """Onboard de nova estratégia"""
        onboarding_id = f"ONBOARD_STRAT_{uuid.uuid4().hex[:8]}"
        
        # Validar formato da estratégia
        validation_result = await self._validate_strategy_format(strategy_config)
        if not validation_result["valid"]:
            return {
                "onboarding_id": onboarding_id,
                "status": "REJECTED",
                "reason": "Invalid strategy format",
                "validation_errors": validation_result["errors"]
            }
        
        onboarding_request = {
            "onboarding_id": onboarding_id,
            "type": "strategy",
            "strategy_name": strategy_config.get("name"),
            "strategy_type": strategy_config.get("type", "alpha"),
            "developer": developer,
            "submitted_at": datetime.now().isoformat(),
            "status": "SUBMITTED",
            "current_stage": "strategy_review",
            "stages": [],
            "config": strategy_config,
            "validation_result": validation_result
        }
        
        self.onboarding_requests[onboarding_id] = onboarding_request
        
        # Iniciar pipeline
        asyncio.create_task(self._execute_onboarding_pipeline(onboarding_request))
        
        return onboarding_request
    
    async def onboard_counterparty(self, counterparty_data: Dict) -> Dict:
        """Onboard de nova contraparte"""
        onboarding_id = f"ONBOARD_CPTY_{uuid.uuid4().hex[:8]}"
        
        # Verificar dados básicos
        required_fields = ["name", "type", "country", "contact_email"]
        missing_fields = [field for field in required_fields if field not in counterparty_data]
        
        if missing_fields:
            return {
                "onboarding_id": onboarding_id,
                "status": "REJECTED",
                "reason": f"Missing required fields: {missing_fields}"
            }
        
        onboarding_request = {
            "onboarding_id": onboarding_id,
            "type": "counterparty",
            "counterparty_name": counterparty_data.get("name"),
            "counterparty_type": counterparty_data.get("type"),
            "submitted_at": datetime.now().isoformat(),
            "status": "SUBMITTED",
            "current_stage": "kyc_check",
            "stages": [],
            "data": counterparty_data
        }
        
        self.onboarding_requests[onboarding_id] = onboarding_request
        
        # Iniciar pipeline
        asyncio.create_task(self._execute_onboarding_pipeline(onboarding_request))
        
        return onboarding_request
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões de onboarding"""
        if transmission.module_type != ModuleType.PROCESS:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "onboard_data":
            # Onboard de dados
            data_config = transmission.payload.get("data_config", {})
            onboarding_result = await self.onboard_data_source(data_config)
            
            return NCNTTransmission(
                transmission_id=f"ONBOARD_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=onboarding_result
            )
        
        elif action == "onboard_strategy":
            # Onboard de estratégia
            strategy_config = transmission.payload.get("strategy_config", {})
            developer = transmission.payload.get("developer", "unknown")
            
            onboarding_result = await self.onboard_strategy(strategy_config, developer)
            
            return NCNTTransmission(
                transmission_id=f"ONBOARD_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=onboarding_result
            )
        
        elif action == "onboard_counterparty":
            # Onboard de contraparte
            counterparty_data = transmission.payload.get("counterparty_data", {})
            onboarding_result = await self.onboard_counterparty(counterparty_data)
            
            return NCNTTransmission(
                transmission_id=f"ONBOARD_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=onboarding_result
            )
        
        elif action == "get_onboarding_status":
            # Obter status de onboarding
            onboarding_id = transmission.payload.get("onboarding_id")
            status = await self.get_onboarding_status(onboarding_id)
            
            return NCNTTransmission(
                transmission_id=f"ONBOARD_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=status
            )
        
        return None
    
    # ========== MÉTODOS DE EXECUÇÃO ==========
    
    async def _execute_onboarding_pipeline(self, onboarding_request: Dict):
        """Executar pipeline de onboarding"""
        pipeline_type = onboarding_request["type"]
        pipeline = self.onboarding_pipelines[pipeline_type]
        
        print(f"🚀 Starting {pipeline_type} onboarding: {onboarding_request.get('onboarding_id')}")
        
        try:
            for stage in pipeline["stages"]:
                stage_name = stage["name"]
                
                # Atualizar estágio atual
                onboarding_request["current_stage"] = stage_name
                
                # Executar estágio
                stage_result = await self._execute_onboarding_stage(
                    stage_name, onboarding_request
                )
                
                # Registrar resultado
                onboarding_request["stages"].append({
                    "stage": stage_name,
                    "started_at": stage_result.get("started_at"),
                    "completed_at": stage_result.get("completed_at"),
                    "success": stage_result.get("success", False),
                    "output": stage_result.get("output", ""),
                    "details": stage_result.get("details", {})
                })
                
                # Se estágio falhar, parar pipeline
                if not stage_result.get("success", False):
                    onboarding_request["status"] = "FAILED"
                    onboarding_request["failed_stage"] = stage_name
                    onboarding_request["failure_reason"] = stage_result.get("error", "Unknown error")
                    break
            
            # Se todos os estágios passaram
            if onboarding_request["status"] != "FAILED":
                onboarding_request["status"] = "COMPLETED"
                onboarding_request["completed_at"] = datetime.now().isoformat()
                
                print(f"✅ Onboarding completed: {onboarding_request['onboarding_id']}")
                
        except Exception as e:
            onboarding_request["status"] = "FAILED"
            onboarding_request["error"] = str(e)
            print(f"❌ Onboarding failed: {onboarding_request['onboarding_id']} - {e}")
        
        # Atualizar request
        self.onboarding_requests[onboarding_request["onboarding_id"]] = onboarding_request
    
    async def _execute_onboarding_stage(self, stage_name: str, onboarding_request: Dict) -> Dict:
        """Executar estágio específico do onboarding"""
        stage_start = datetime.now()
        
        result = {
            "stage": stage_name,
            "started_at": stage_start.isoformat(),
            "success": False,
            "output": "",
            "details": {}
        }
        
        try:
            # Executar baseado no tipo de estágio
            if stage_name == "data_validation":
                result = await self._execute_data_validation(onboarding_request)
            elif stage_name == "strategy_review":
                result = await self._execute_strategy_review(onboarding_request)
            elif stage_name == "kyc_check":
                result = await self._execute_kyc_check(onboarding_request)
            elif "approval" in stage_name:
                result = await self._execute_approval_stage(stage_name, onboarding_request)
            elif "test" in stage_name:
                result = await self._execute_testing_stage(stage_name, onboarding_request)
            else:
                # Estágio genérico
                result = await self._execute_generic_stage(stage_name, onboarding_request)
            
        except Exception as e:
            result["success"] = False
            result["output"] = f"Stage failed with error: {str(e)}"
            result["error"] = str(e)
        
        # Calcular duração
        stage_end = datetime.now()
        result["completed_at"] = stage_end.isoformat()
        result["duration_seconds"] = (stage_end - stage_start).total_seconds()
        
        return result
    
    async def _execute_data_validation(self, onboarding_request: Dict) -> Dict:
        """Executar validação de dados"""
        data_config = onboarding_request.get("config", {})
        
        # Verificações básicas
        checks = [
            {"check": "data_format", "passed": "format" in data_config},
            {"check": "update_frequency", "passed": "frequency" in data_config},
            {"check": "authentication", "passed": "auth" in data_config},
            {"check": "rate_limits", "passed": "rate_limits" in data_config}
        ]
        
        all_passed = all(c["passed"] for c in checks)
        
        return {
            "success": all_passed,
            "output": f"Data validation {'passed' if all_passed else 'failed'}",
            "details": {"checks": checks},
            "requires_manual_review": not all_passed
        }
    
    async def _execute_strategy_review(self, onboarding_request: Dict) -> Dict:
        """Executar revisão de estratégia"""
        strategy_config = onboarding_request.get("config", {})
        
        # Verificações de estratégia
        issues = []
        
        if "entry_logic" not in strategy_config:
            issues.append("Missing entry logic")
        if "exit_logic" not in strategy_config:
            issues.append("Missing exit logic")
        if "risk_management" not in strategy_config:
            issues.append("Missing risk management")
        
        # Verificar complexidade
        logic_complexity = len(str(strategy_config.get("entry_logic", ""))) + len(str(strategy_config.get("exit_logic", "")))
        if logic_complexity > 10000:
            issues.append("Strategy logic too complex")
        
        return {
            "success": len(issues) == 0,
            "output": f"Strategy review found {len(issues)} issues",
            "details": {"issues": issues, "logic_complexity": logic_complexity},
            "requires_manual_review": len(issues) > 0
        }
    
    async def _execute_kyc_check(self, onboarding_request: Dict) -> Dict:
        """Executar verificação KYC"""
        counterparty_data = onboarding_request.get("data", {})
        
        # Verificações KYC básicas
        checks = [
            {"check": "name_provided", "passed": bool(counterparty_data.get("name"))},
            {"check": "country_provided", "passed": bool(counterparty_data.get("country"))},
            {"check": "email_valid", "passed": "@" in counterparty_data.get("contact_email", "")},
            {"check": "tax_id_provided", "passed": bool(counterparty_data.get("tax_id", ""))}
        ]
        
        all_passed = all(c["passed"] for c in checks)
        
        # Lista de países restritos
        restricted_countries = ["IR", "KP", "SY", "CU", "RU"]
        country = counterparty_data.get("country", "").upper()
        
        if country in restricted_countries:
            return {
                "success": False,
                "output": f"Country {country} is restricted",
                "details": {"country_restricted": True, "country": country},
                "requires_manual_review": True
            }
        
        return {
            "success": all_passed,
            "output": f"KYC check {'passed' if all_passed else 'failed'}",
            "details": {"checks": checks},
            "requires_manual_review": not all_passed
        }
    
    async def _execute_approval_stage(self, stage_name: str, onboarding_request: Dict) -> Dict:
        """Executar estágio de aprovação"""
        # Simular processo de aprovação
        import random
        
        # Chance de aprovação baseada no tipo
        approval_chance = 0.9  # 90% chance
        
        if onboarding_request["type"] == "strategy":
            approval_chance = 0.8  # 80% para estratégias
        
        approved = random.random() < approval_chance
        
        if approved:
            approvers = random.sample(["risk_officer", "compliance_officer", "tech_lead"], k=2)
            
            return {
                "success": True,
                "output": f"Stage {stage_name} approved by {', '.join(approvers)}",
                "details": {"approvers": approvers, "approval_time": random.uniform(1, 24)},
                "requires_manual_review": False
            }
        else:
            reasons = ["Insufficient documentation", "Risk too high", "Compliance concerns"]
            
            return {
                "success": False,
                "output": f"Stage {stage_name} rejected: {random.choice(reasons)}",
                "details": {"rejection_reason": random.choice(reasons)},
                "requires_manual_review": True
            }
    
    async def _execute_testing_stage(self, stage_name: str, onboarding_request: Dict) -> Dict:
        """Executar estágio de teste"""
        # Simular testes
        import random
        
        test_types = {
            "integration_testing": {"tests": 25, "pass_rate": 0.95},
            "paper_trading": {"days": 30, "success_rate": 0.85}
        }
        
        test_config = test_types.get(stage_name, {"tests": 10, "pass_rate": 0.90})
        
        if "pass_rate" in test_config:
            passed = random.random() < test_config["pass_rate"]
        else:
            passed = random.random() < test_config["success_rate"]
        
        return {
            "success": passed,
            "output": f"Testing stage {stage_name} {'passed' if passed else 'failed'}",
            "details": test_config,
            "requires_manual_review": not passed
        }
    
    async def _execute_generic_stage(self, stage_name: str, onboarding_request: Dict) -> Dict:
        """Executar estágio genérico"""
        # Simular execução
        import random
        import time
        
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simular processamento
        
        passed = random.random() > 0.1  # 90% success rate
        
        return {
            "success": passed,
            "output": f"Stage {stage_name} {'completed successfully' if passed else 'failed'}",
            "details": {"simulated": True},
            "requires_manual_review": not passed
        }
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def _validate_strategy_format(self, strategy_config: Dict) -> Dict:
        """Validar formato da estratégia"""
        errors = []
        
        required_fields = ["name", "type", "entry_logic", "exit_logic"]
        for field in required_fields:
            if field not in strategy_config:
                errors.append(f"Missing required field: {field}")
        
        # Validar tipo
        valid_types = ["alpha", "execution", "arbitrage", "market_making"]
        if strategy_config.get("type") not in valid_types:
            errors.append(f"Invalid strategy type. Must be one of: {valid_types}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_onboarding_status(self, onboarding_id: str) -> Dict:
        """Obter status de onboarding específico"""
        if onboarding_id not in self.onboarding_requests:
            return {"error": f"Onboarding request {onboarding_id} not found", "status": "UNKNOWN"}
        
        request = self.onboarding_requests[onboarding_id]
        
        # Calcular progresso
        pipeline = self.onboarding_pipelines[request["type"]]
        total_stages = len(pipeline["stages"])
        completed_stages = len(request["stages"])
        
        if total_stages > 0:
            progress_percentage = (completed_stages / total_stages) * 100
        else:
            progress_percentage = 0.0
        
        return {
            "onboarding_id": onboarding_id,
            "type": request["type"],
            "status": request["status"],
            "current_stage": request["current_stage"],
            "progress_percentage": progress_percentage,
            "stages_completed": completed_stages,
            "total_stages": total_stages,
            "submitted_at": request["submitted_at"],
            "completed_at": request.get("completed_at"),
            "stages": request["stages"]
        }

# ============================================================================
# 🚨 02-PROCESSOS-CHAVE: INCIDENT RESPONSE PROTOCOL
# ============================================================================
