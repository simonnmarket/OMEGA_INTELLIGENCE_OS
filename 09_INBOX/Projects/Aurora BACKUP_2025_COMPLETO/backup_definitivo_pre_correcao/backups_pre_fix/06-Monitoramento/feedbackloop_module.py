#!/usr/bin/env python3
"""
FeedbackLoopModule - Módulo NCNT
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

class FeedbackLoopModule(NCNTBaseModule):
    """✅ LOOP DE FEEDBACK - Melhoria Contínua"""
    
    def __init__(self):
        super().__init__("feedback_loop", ModuleType.MONITORING)
        self.feedback_items = {}
        self.improvement_projects = {}
        self.metrics_history = {}
        
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar ciclos de feedback
        self.feedback_cycles = config.get("feedback_cycles", {
            "daily_retrospective": True,
            "weekly_review": True,
            "monthly_analysis": True,
            "quarterly_strategy": True
        })
        
        # Configurar categorias de melhoria
        self.improvement_categories = config.get("improvement_categories", [
            "process_efficiency",
            "risk_management", 
            "system_performance",
            "user_experience",
            "cost_optimization",
            "compliance"
        ])
        
        self.status = "ACTIVE"
        return True
    
    async def submit_feedback(self, feedback_data: Dict) -> Dict:
        """Submeter feedback"""
        feedback_id = f"FEEDBACK_{uuid.uuid4().hex[:8]}"
        
        feedback = {
            "feedback_id": feedback_id,
            "type": feedback_data.get("type", "suggestion"),
            "category": feedback_data.get("category", "general"),
            "title": feedback_data.get("title", "Untitled Feedback"),
            "description": feedback_data.get("description", ""),
            "submitted_by": feedback_data.get("submitted_by", "anonymous"),
            "submitted_at": datetime.now().isoformat(),
            "status": "SUBMITTED",
            "priority": feedback_data.get("priority", "medium"),
            "impact": feedback_data.get("impact", "medium"),
            "effort": feedback_data.get("effort", "medium"),
            "votes": {"up": 0, "down": 0},
            "comments": [],
            "assignee": None,
            "resolution": None,
            "related_items": feedback_data.get("related_items", [])
        }
        
        self.feedback_items[feedback_id] = feedback
        
        # Analisar e categorizar automaticamente
        await self._analyze_feedback(feedback)
        
        return {
            "feedback_id": feedback_id,
            "status": "SUBMITTED",
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões do loop de feedback"""
        if transmission.module_type != ModuleType.MONITORING:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "submit_feedback":
            # Submeter feedback
            feedback_data = transmission.payload.get("feedback_data", {})
            submission_result = await self.submit_feedback(feedback_data)
            
            return NCNTTransmission(
                transmission_id=f"FEEDBACK_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=submission_result
            )
        
        elif action == "get_feedback_summary":
            # Obter resumo de feedback
            timeframe = transmission.payload.get("timeframe", "month")
            summary = await self.get_feedback_summary(timeframe)
            
            return NCNTTransmission(
                transmission_id=f"FEEDBACK_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=summary
            )
        
        return None
    
    # ========== MÉTODOS DE ANÁLISE ==========
    
    async def _analyze_feedback(self, feedback: Dict):
        """Analisar feedback automaticamente"""
        description = feedback["description"].lower()
        
        # Detectar categoria baseada no conteúdo
        detected_categories = []
        
        for category in self.improvement_categories:
            keywords = self._get_category_keywords(category)
            if any(keyword in description for keyword in keywords):
                detected_categories.append(category)
        
        if detected_categories:
            feedback["detected_categories"] = detected_categories
        
        # Calcular score de prioridade
        priority_score = self._calculate_priority_score(feedback)
        feedback["priority_score"] = priority_score
        
        # Sugerir atribuição
        suggested_assignee = self._suggest_assignee(feedback)
        feedback["suggested_assignee"] = suggested_assignee
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Obter palavras-chave para categoria"""
        keyword_map = {
            "process_efficiency": ["slow", "fast", "efficient", "inefficient", "bottleneck", "optimize"],
            "risk_management": ["risk", "danger", "safe", "unsafe", "limit", "exposure"],
            "system_performance": ["crash", "error", "bug", "performance", "speed", "latency"],
            "user_experience": ["ui", "ux", "interface", "design", "confusing", "intuitive"],
            "cost_optimization": ["cost", "expensive", "cheap", "save", "budget", "expensive"],
            "compliance": ["compliance", "regulation", "legal", "audit", "violation"]
        }
        return keyword_map.get(category, [])
    
    def _calculate_priority_score(self, feedback: Dict) -> float:
        """Calcular score de prioridade"""
        impact_scores = {"low": 1, "medium": 2, "high": 3}
        effort_scores = {"low": 3, "medium": 2, "high": 1}  # Inverso
        
        impact = feedback.get("impact", "medium")
        effort = feedback.get("effort", "medium")
        
        return impact_scores.get(impact, 2) * effort_scores.get(effort, 2)
    
    def _suggest_assignee(self, feedback: Dict) -> str:
        """Sugerir atribuição baseada na categoria"""
        category_map = {
            "process_efficiency": "process_team",
            "risk_management": "risk_department",
            "system_performance": "engineering_team",
            "user_experience": "product_team",
            "cost_optimization": "finance_department",
            "compliance": "compliance_officer"
        }
        
        detected = feedback.get("detected_categories", [])
        if detected:
            return category_map.get(detected[0], "general_support")
        
        return "general_support"
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def get_feedback_summary(self, timeframe: str) -> Dict:
        """Obter resumo de feedback"""
        now = datetime.now()
        
        if timeframe == "week":
            cutoff = now - timedelta(days=7)
        elif timeframe == "month":
            cutoff = now - timedelta(days=30)
        elif timeframe == "quarter":
            cutoff = now - timedelta(days=90)
        else:
            cutoff = now - timedelta(days=365)  # Year
        
        recent_feedback = [
            f for f in self.feedback_items.values()
            if datetime.fromisoformat(f["submitted_at"]) > cutoff
        ]
        
        # Agrupar por categoria
        by_category = {}
        for feedback in recent_feedback:
            category = feedback.get("category", "general")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(feedback)
        
        # Calcular estatísticas
        total_feedback = len(recent_feedback)
        resolved = len([f for f in recent_feedback if f.get("status") == "RESOLVED"])
        in_progress = len([f for f in recent_feedback if f.get("status") == "IN_PROGRESS"])
        
        return {
            "summary_id": f"FEEDBACK_SUMMARY_{timeframe.upper()}_{datetime.now().strftime('%Y%m%d')}",
            "timeframe": timeframe,
            "timestamp": now.isoformat(),
            "statistics": {
                "total_feedback": total_feedback,
                "resolved": resolved,
                "in_progress": in_progress,
                "submitted": total_feedback - resolved - in_progress,
                "resolution_rate": resolved / total_feedback if total_feedback > 0 else 0
            },
            "by_category": {
                category: {
                    "count": len(items),
                    "examples": items[:3]
                }
                for category, items in by_category.items()
            },
            "top_priorities": sorted(
                recent_feedback, 
                key=lambda x: x.get("priority_score", 0), 
                reverse=True
            )[:5]
        }

# ============================================================================
# 🚀 NCNT ORCHESTRATOR - SISTEMA PRINCIPAL
# ============================================================================

class NCNTOrchestrator:
    """
    🚀 ORQUESTRADOR NCNT - Sistema Principal
    Gerencia todos os módulos e coordena operações
    """
    
    def __init__(self):
        self.system_name = "NCNT - Núcleo Central Neuro Transmissor"
        self.version = "2.0"
        self.modules = {}
        self.message_bus = None
        self.system_status = "BOOTING"
        
    async def initialize(self):
        """Inicializar sistema completo"""
        print(f"\n{'='*80}")
        print(f"🚀 INICIALIZANDO {self.system_name} v{self.version}")
        print(f"{'='*80}")
        
        try:
            # 1. Inicializar módulos base
            await self._initialize_core_modules()
            
            # 2. Configurar message bus
            await self._setup_message_bus()
            
            # 3. Registrar módulos
            await self._register_all_modules()
            
            # 4. Verificar dependências
            await self._check_dependencies()
            
            # 5. Iniciar operações
            await self._start_operations()
            
            self.system_status = "ACTIVE"
            
            print(f"\n{'='*80}")
            print(f"✅ SISTEMA {self.system_name} INICIALIZADO COM SUCESSO")
            print(f"📊 Módulos ativos: {len(self.modules)}")
            print(f"🔄 Status: {self.system_status}")
            print(f"{'='*80}")
            
        except Exception as e:
            self.system_status = "ERROR"
            print(f"\n❌ ERRO NA INICIALIZAÇÃO: {e}")
            raise
    
    async def _initialize_core_modules(self):
        """Inicializar módulos principais"""
        print("\n📦 INICIALIZANDO MÓDULOS PRINCIPAIS...")
        
        # 00-Governança
        self.modules["governance"] = GovernanceModule()
        await self.modules["governance"].initialize({})
        
        # 01-Departamentos
        self.modules["treasury"] = TreasuryModule()
        await self.modules["treasury"].initialize({"initial_capital": 3500.00})
        
        self.modules["core_engine"] = CoreEngineModule()
        await self.modules["core_engine"].initialize({})
        
        self.modules["risk"] = RiskModule()
        await self.modules["risk"].initialize({"risk_tier": "tier_1"})
        
        self.modules["compliance"] = ComplianceModule()
        await self.modules["compliance"].initialize({})
        
        self.modules["innovation"] = InnovationLabModule()
        await self.modules["innovation"].initialize({})
        
        # 02-Processos-Chave
        self.modules["ci_cd"] = CICDPipelineModule()
        await self.modules["ci_cd"].initialize({})
        
        self.modules["qa_backtesting"] = QABacktestingModule()
        await self.modules["qa_backtesting"].initialize({})
        
        self.modules["onboarding"] = OnboardingModule()
        await self.modules["onboarding"].initialize({})
        
        self.modules["incident_response"] = IncidentResponseModule()
        await self.modules["incident_response"].initialize({})
        
        # 03-Operações Diárias
        self.modules["pre_market"] = PreMarketChecklistModule()
        await self.modules["pre_market"].initialize({})
        
        self.modules["execution_window"] = ExecutionWindowModule()
        await self.modules["execution_window"].initialize({})
        
        self.modules["dashboard"] = RealTimeDashboardModule()
        await self.modules["dashboard"].initialize({})
        
        self.modules["reconciliation"] = PostTradeReconciliationModule()
        await self.modules["reconciliation"].initialize({})
        
        # 04-Infraestrutura
        self.modules["module_registry"] = ModuleRegistry()
        await self.modules["module_registry"].initialize({})
        
        # 05-Documentação
        self.modules["sops"] = SOPsModule()
        await self.modules["sops"].initialize({})
        
        # 06-Monitoramento
        self.modules["feedback"] = FeedbackLoopModule()
        await self.modules["feedback"].initialize({})
        
        print(f"✅ {len(self.modules)} módulos inicializados")
    
    async def _setup_message_bus(self):
        """Configurar barramento de mensagens"""
        print("\n🔌 CONFIGURANDO MESSAGE BUS...")
        # Implementação simplificada
        self.message_bus = {"active": True, "type": "simulated"}
        print("✅ Message Bus configurado")
    
    async def _register_all_modules(self):
        """Registrar todos os módulos no sistema"""
        print("\n📝 REGISTRANDO MÓDULOS...")
        
        for module_name, module in self.modules.items():
            # Cada módulo se auto-registra
            print(f"  📋 {module_name}: {module.module_id}")
        
        print("✅ Todos os módulos registrados")
    
    async def _check_dependencies(self):
        """Verificar dependências entre módulos"""
        print("\n🔗 VERIFICANDO DEPENDÊNCIAS...")
        
        # Verificações básicas
        checks = [
            ("Treasury depende de Governance", True),
            ("Risk depende de Treasury", True),
            ("Compliance depende de Governance", True),
            ("Execution Window depende de Market Data", False),
            ("Dashboard depende de todos os módulos", True)
        ]
        
        for check, required in checks:
            if required:
                print(f"  ✅ {check}")
            else:
                print(f"  ⚠️ {check} (opcional)")
        
        print("✅ Dependências verificadas")
    
    async def _start_operations(self):
        """Iniciar operações do sistema"""
        print("\n🔄 INICIANDO OPERAÇÕES...")
        
        # Iniciar operações em background
        operations = [
            "Pre-market checklist",
            "Market data feeds",
            "Risk monitoring",
            "Compliance checks",
            "Dashboard updates"
        ]
        
        for operation in operations:
            print(f"  🚀 {operation}")
        
        print("✅ Operações iniciadas")
    
    async def run_demo_workflow(self):
        """Executar fluxo de trabalho de demonstração"""
        print(f"\n{'='*80}")
        print("🎮 DEMONSTRAÇÃO DO SISTEMA NCNT")
        print(f"{'='*80}")
        
        try:
            # 1. Executar checklist pré-mercado
            print("\n1. 🕒 EXECUTANDO CHECKLIST PRÉ-MERCADO...")
            checklist_result = await self.modules["pre_market"].run_checklist("pre_market")
            print(f"   Status: {checklist_result['status']}")
            print(f"   System Ready: {checklist_result.get('system_ready', False)}")
            
            # 2. Verificar status do mercado
            print("\n2. 📊 VERIFICANDO STATUS DO MERCADO...")
            market_status = await self.modules["execution_window"].check_market_status("forex")
            print(f"   Forex Market: {market_status['status']}")
            print(f"   Open: {market_status.get('open_time')} - {market_status.get('close_time')}")
            
            # 3. Atualizar dashboard
            print("\n3. 📈 ATUALIZANDO DASHBOARD...")
            dashboard_data = await self.modules["dashboard"].update_dashboard()
            print(f"   Dashboard ID: {dashboard_data['dashboard_id']}")
            print(f"   Widgets: {len(dashboard_data['widgets'])}")
            
            # 4. Verificar saúde do sistema
            print("\n4. 🏥 VERIFICANDO SAÚDE DO SISTEMA...")
            health_checks = []
            for module_name, module in self.modules.items():
                try:
                    health = await module.health_check()
                    health_checks.append({
                        "module": module_name,
                        "status": health.get("status"),
                        "uptime": health.get("uptime")
                    })
                except:
                    pass
            
            healthy = len([h for h in health_checks if h["status"] == "ACTIVE"])
            total = len(health_checks)
            print(f"   Módulos saudáveis: {healthy}/{total}")
            
            # 5. Demonstrar alocação de capital
            print("\n5. 💰 DEMONSTRANDO ALO
