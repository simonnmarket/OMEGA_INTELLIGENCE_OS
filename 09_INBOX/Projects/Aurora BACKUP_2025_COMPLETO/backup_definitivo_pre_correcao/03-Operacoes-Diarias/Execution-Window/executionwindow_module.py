#!/usr/bin/env python3
"""
ExecutionWindowModule - Módulo NCNT
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

class ExecutionWindowModule(NCNTBaseModule):
    """📤 JANELA DE EXECUÇÃO - Controle de Horários e Throttling"""
    
    def __init__(self):
        super().__init__("execution_window", ModuleType.OPERATION)
        self.market_schedules = self._initialize_market_schedules()
        self.throttling_rules = self._initialize_throttling_rules()
        self.execution_logs = {}
        self.window_status = {}
        
    def _initialize_market_schedules(self) -> Dict:
        """Inicializar horários de mercado"""
        return {
            "forex": {
                "name": "Forex Market",
                "open": "00:00",
                "close": "23:59",
                "timezone": "UTC",
                "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "holidays": ["2024-01-01", "2024-12-25"],
                "session_breaks": []
            },
            "us_equities": {
                "name": "US Equities",
                "open": "14:30",
                "close": "21:00",
                "timezone": "UTC",
                "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "holidays": ["2024-01-01", "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27", "2024-06-19", "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25"],
                "session_breaks": []  # No breaks for US equities
            },
            "crypto": {
                "name": "Cryptocurrency",
                "open": "00:00",
                "close": "23:59",
                "timezone": "UTC",
                "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "holidays": [],
                "session_breaks": []
            },
            "metals": {
                "name": "Metals Trading",
                "open": "01:00",
                "close": "22:00",
                "timezone": "UTC",
                "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "holidays": ["2024-01-01", "2024-12-25"],
                "session_breaks": [
                    {"start": "17:00", "end": "18:00", "reason": "Daily maintenance"}
                ]
            }
        }
    
    def _initialize_throttling_rules(self) -> Dict:
        """Inicializar regras de throttling"""
        return {
            "rate_limits": {
                "max_orders_per_second": 10,
                "max_trades_per_minute": 60,
                "max_volume_per_hour": 1000000,
                "max_position_changes_per_day": 1000
            },
            "cooldown_periods": {
                "after_error": 5,  # seconds
                "after_rate_limit": 60,  # seconds
                "after_system_issue": 300  # seconds
            },
            "dynamic_adjustments": {
                "high_volatility_multiplier": 0.5,
                "low_liquidity_multiplier": 0.3,
                "news_event_multiplier": 0.2
            }
        }
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar ajustes dinâmicos
        self.dynamic_settings = config.get("dynamic_settings", {
            "auto_adjust_for_volatility": True,
            "auto_adjust_for_liquidity": True,
            "pause_during_news": True,
            "circuit_breaker_enabled": True
        })
        
        # Configurar logging
        self.logging_config = config.get("logging_config", {
            "log_all_executions": True,
            "log_throttling_events": True,
            "log_window_changes": True,
            "retention_days": 90
        })
        
        self.status = "ACTIVE"
        return True
    
    async def check_market_status(self, asset_class: str) -> Dict:
        """Verificar status do mercado para uma classe de ativos"""
        if asset_class not in self.market_schedules:
            return {"error": f"Asset class {asset_class} not found", "status": "UNKNOWN"}
        
        schedule = self.market_schedules[asset_class]
        now = datetime.now()
        
        # Verificar se é dia de trading
        current_day = now.strftime("%A")
        if current_day not in schedule["trading_days"]:
            return {
                "asset_class": asset_class,
                "status": "CLOSED",
                "reason": f"{current_day} is not a trading day",
                "next_open": self._get_next_trading_day(asset_class),
                "timestamp": now.isoformat()
            }
        
        # Verificar feriados
        current_date = now.strftime("%Y-%m-%d")
        if current_date in schedule["holidays"]:
            return {
                "asset_class": asset_class,
                "status": "CLOSED",
                "reason": "Market holiday",
                "next_open": self._get_next_trading_day(asset_class),
                "timestamp": now.isoformat()
            }
        
        # Verificar horário
        current_time = now.strftime("%H:%M")
        open_time = schedule["open"]
        close_time = schedule["close"]
        
        # Verificar pausas de sessão
        for session_break in schedule.get("session_breaks", []):
            break_start = session_break["start"]
            break_end = session_break["end"]
            
            if break_start <= current_time <= break_end:
                return {
                    "asset_class": asset_class,
                    "status": "BREAK",
                    "reason": session_break.get("reason", "Session break"),
                    "break_ends": break_end,
                    "timestamp": now.isoformat()
                }
        
        if open_time <= current_time <= close_time:
            status = "OPEN"
        elif current_time < open_time:
            status = "PRE_OPEN"
        else:
            status = "POST_CLOSE"
        
        return {
            "asset_class": asset_class,
            "status": status,
            "open_time": open_time,
            "close_time": close_time,
            "timezone": schedule["timezone"],
            "current_time": current_time,
            "timestamp": now.isoformat(),
            "next_status_change": self._get_next_status_change(asset_class, status)
        }
    
    async def check_throttling_limits(self, order_request: Dict) -> Dict:
        """Verificar limites de throttling para uma ordem"""
        asset_class = order_request.get("asset_class", "forex")
        order_size = order_request.get("size", 0)
        order_type = order_request.get("type", "market")
        
        # Verificar status do mercado primeiro
        market_status = await self.check_market_status(asset_class)
        if market_status.get("status") != "OPEN":
            return {
                "allowed": False,
                "reason": f"Market is {market_status.get('status')}",
                "details": market_status,
                "timestamp": datetime.now().isoformat()
            }
        
        # Verificar limites de taxa
        rate_checks = await self._check_rate_limits(asset_class, order_type)
        if not rate_checks["allowed"]:
            return rate_checks
        
        # Verificar limites de volume
        volume_checks = await self._check_volume_limits(asset_class, order_size)
        if not volume_checks["allowed"]:
            return volume_checks
        
        # Aplicar ajustes dinâmicos
        dynamic_adjustments = await self._apply_dynamic_adjustments(asset_class, order_request)
        if not dynamic_adjustments["allowed"]:
            return dynamic_adjustments
        
        # Todas as verificações passaram
        return {
            "allowed": True,
            "reason": "All checks passed",
            "details": {
                "rate_limits": rate_checks["details"],
                "volume_limits": volume_checks["details"],
                "dynamic_adjustments": dynamic_adjustments["details"]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões da janela de execução"""
        if transmission.module_type != ModuleType.OPERATION:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "check_market_status":
            # Verificar status do mercado
            asset_class = transmission.payload.get("asset_class", "forex")
            market_status = await self.check_market_status(asset_class)
            
            return NCNTTransmission(
                transmission_id=f"WINDOW_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=market_status
            )
        
        elif action == "check_throttling":
            # Verificar throttling
            order_request = transmission.payload.get("order_request", {})
            throttling_check = await self.check_throttling_limits(order_request)
            
            return NCNTTransmission(
                transmission_id=f"WINDOW_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=throttling_check
            )
        
        elif action == "get_execution_window":
            # Obter janela de execução atual
            asset_class = transmission.payload.get("asset_class", "all")
            window_info = await self.get_execution_window_info(asset_class)
            
            return NCNTTransmission(
                transmission_id=f"WINDOW_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=window_info
            )
        
        return None
    
    # ========== MÉTODOS DE VERIFICAÇÃO ==========
    
    async def _check_rate_limits(self, asset_class: str, order_type: str) -> Dict:
        """Verificar limites de taxa"""
        # Simular contagem de ordens
        import random
        
        orders_this_second = random.randint(0, 15)
        orders_this_minute = random.randint(0, 70)
        
        limits = self.throttling_rules["rate_limits"]
        
        checks = [
            {
                "check": "orders_per_second",
                "limit": limits["max_orders_per_second"],
                "current": orders_this_second,
                "passed": orders_this_second <= limits["max_orders_per_second"]
            },
            {
                "check": "trades_per_minute",
                "limit": limits["max_trades_per_minute"],
                "current": orders_this_minute,
                "passed": orders_this_minute <= limits["max_trades_per_minute"]
            }
        ]
        
        all_passed = all(c["passed"] for c in checks)
        
        return {
            "allowed": all_passed,
            "reason": "Rate limits OK" if all_passed else "Rate limit exceeded",
            "details": {"checks": checks},
            "cooldown_required": not all_passed
        }
    
    async def _check_volume_limits(self, asset_class: str, order_size: float) -> Dict:
        """Verificar limites de volume"""
        # Simular volume acumulado
        import random
        
        volume_this_hour = random.uniform(0, 1500000)
        
        limits = self.throttling_rules["rate_limits"]
        
        checks = [
            {
                "check": "volume_per_hour",
                "limit": limits["max_volume_per_hour"],
                "current": volume_this_hour,
                "passed": volume_this_hour + order_size <= limits["max_volume_per_hour"]
            }
        ]
        
        all_passed = all(c["passed"] for c in checks)
        
        return {
            "allowed": all_passed,
            "reason": "Volume limits OK" if all_passed else "Volume limit exceeded",
            "details": {"checks": checks},
            "cooldown_required": not all_passed
        }
    
    async def _apply_dynamic_adjustments(self, asset_class: str, order_request: Dict) -> Dict:
        """Aplicar ajustes dinâmicos"""
        adjustments = []
        
        # Verificar volatilidade
        if self.dynamic_settings["auto_adjust_for_volatility"]:
            volatility_check = await self._check_volatility(asset_class)
            adjustments.append(volatility_check)
        
        # Verificar liquidez
        if self.dynamic_settings["auto_adjust_for_liquidity"]:
            liquidity_check = await self._check_liquidity(asset_class)
            adjustments.append(liquidity_check)
        
        # Verificar eventos de notícias
        if self.dynamic_settings["pause_during_news"]:
            news_check = await self._check_news_events(asset_class)
            adjustments.append(news_check)
        
        # Verificar circuit breakers
        if self.dynamic_settings["circuit_breaker_enabled"]:
            circuit_check = await self._check_circuit_breakers(asset_class)
            adjustments.append(circuit_check)
        
        # Determinar se permitido
        all_allowed = all(a.get("allowed", True) for a in adjustments)
        
        return {
            "allowed": all_allowed,
            "reason": "Dynamic adjustments OK" if all_allowed else "Dynamic adjustment required",
            "details": {"adjustments": adjustments},
            "cooldown_required": not all_allowed
        }
    
    async def _check_volatility(self, asset_class: str) -> Dict:
        """Verificar volatilidade"""
        # Simulação
        import random
        
        volatility_level = random.uniform(0.5, 3.0)  # Volatilidade anualizada
        threshold = 2.0
        
        if volatility_level > threshold:
            multiplier = self.throttling_rules["dynamic_adjustments"]["high_volatility_multiplier"]
            
            return {
                "adjustment": "high_volatility",
                "allowed": False,
                "volatility_level": volatility_level,
                "threshold": threshold,
                "multiplier": multiplier,
                "recommendation": f"Reduce order size by {1-multiplier:.0%}"
            }
        
        return {
            "adjustment": "volatility_ok",
            "allowed": True,
            "volatility_level": volatility_level,
            "threshold": threshold
        }
    
    async def _check_liquidity(self, asset_class: str) -> Dict:
        """Verificar liquidez"""
        # Simulação
        import random
        
        liquidity_score = random.uniform(0.3, 1.0)
        threshold = 0.5
        
        if liquidity_score < threshold:
            multiplier = self.throttling_rules["dynamic_adjustments"]["low_liquidity_multiplier"]
            
            return {
                "adjustment": "low_liquidity",
                "allowed": False,
                "liquidity_score": liquidity_score,
                "threshold": threshold,
                "multiplier": multiplier,
                "recommendation": f"Reduce order size by {1-multiplier:.0%}"
            }
        
        return {
            "adjustment": "liquidity_ok",
            "allowed": True,
            "liquidity_score": liquidity_score,
            "threshold": threshold
        }
    
    async def _check_news_events(self, asset_class: str) -> Dict:
        """Verificar eventos de notícias"""
        # Simulação
        import random
        
        # 10% chance de evento de notícias
        has_news_event = random.random() < 0.1
        
        if has_news_event:
            multiplier = self.throttling_rules["dynamic_adjustments"]["news_event_multiplier"]
            
            return {
                "adjustment": "news_event",
                "allowed": False,
                "has_news": True,
                "multiplier": multiplier,
                "recommendation": "Pause trading during news event"
            }
        
        return {
            "adjustment": "no_news",
            "allowed": True,
            "has_news": False
        }
    
    async def _check_circuit_breakers(self, asset_class: str) -> Dict:
        """Verificar circuit breakers"""
        # Simulação
        import random
        
        # 5% chance de circuit breaker ativado
        circuit_breaker_active = random.random() < 0.05
        
        if circuit_breaker_active:
            return {
                "adjustment": "circuit_breaker",
                "allowed": False,
                "active": True,
                "recommendation": "Trading halted by circuit breaker"
            }
        
        return {
            "adjustment": "circuit_breaker_ok",
            "allowed": True,
            "active": False
        }
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _get_next_trading_day(self, asset_class: str) -> str:
        """Obter próximo dia de trading"""
        schedule = self.market_schedules[asset_class]
        now = datetime.now()
        
        # Encontrar próximo dia de trading
        for i in range(1, 8):  # Próximos 7 dias
            next_day = now + timedelta(days=i)
            if next_day.strftime("%A") in schedule["trading_days"]:
                next_date_str = next_day.strftime("%Y-%m-%d")
                if next_date_str not in schedule["holidays"]:
                    return next_date_str
        
        return "Unknown"
    
    def _get_next_status_change(self, asset_class: str, current_status: str) -> Dict:
        """Obter próxima mudança de status"""
        schedule = self.market_schedules[asset_class]
        now = datetime.now()
        
        if current_status == "PRE_OPEN":
            next_change = schedule["open"]
            change_type = "OPENING"
        elif current_status == "OPEN":
            # Verificar se há pausa antes do fechamento
            next_break = None
            for session_break in schedule.get("session_breaks", []):
                if session_break["start"] > now.strftime("%H:%M"):
                    next_break = session_break
                    break
            
            if next_break:
                next_change = next_break["start"]
                change_type = "BREAK_START"
            else:
                next_change = schedule["close"]
                change_type = "CLOSING"
        elif current_status == "BREAK":
            # Encontrar fim da pausa
            current_time = now.strftime("%H:%M")
            for session_break in schedule.get("session_breaks", []):
                if session_break["start"] <= current_time <= session_break["end"]:
                    next_change = session_break["end"]
                    change_type = "BREAK_END"
                    break
            else:
                next_change = schedule["close"]
                change_type = "CLOSING"
        else:  # POST_CLOSE
            next_change = self._get_next_trading_day(asset_class) + " " + schedule["open"]
            change_type = "NEXT_OPENING"
        
        return {
            "time": next_change,
            "type": change_type,
            "timezone": schedule["timezone"]
        }
    
    async def get_execution_window_info(self, asset_class: str = "all") -> Dict:
        """Obter informações da janela de execução"""
        if asset_class == "all":
            statuses = {}
            for ac in self.market_schedules.keys():
                statuses[ac] = await self.check_market_status(ac)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "asset_classes": statuses,
                "summary": {
                    "open_markets": sum(1 for s in statuses.values() if s.get("status") == "OPEN"),
                    "total_markets": len(statuses),
                    "any_restrictions": any(
                        s.get("status") != "OPEN" for s in statuses.values()
                    )
                }
            }
        else:
            market_status = await self.check_market_status(asset_class)
            throttling_info = self.throttling_rules["rate_limits"]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "asset_class": asset_class,
                "market_status": market_status,
                "throttling_limits": throttling_info,
                "dynamic_settings": self.dynamic_settings
            }

# ============================================================================
# 📊 03-OPERAÇÕES DIÁRIAS: REAL-TIME DASHBOARD
# ============================================================================
