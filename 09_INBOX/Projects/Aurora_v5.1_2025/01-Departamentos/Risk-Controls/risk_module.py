#!/usr/bin/env python3
"""
RiskModule - Módulo NCNT
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

class RiskModule(NCNTBaseModule):
    """🛡️ MÓDULO DE RISCO - Goldman Sachs Risk Framework"""
    
    def __init__(self):
        super().__init__("risk_core", ModuleType.RISK)
        self.risk_limits = self._initialize_risk_limits()
        self.exposure_tracking = {}
        self.var_model = HistoricalVaR()
        self.stress_test_engine = StressTestEngine()
        self.circuit_breakers = self._initialize_circuit_breakers()
        self.risk_metrics_history = []
        
    def _initialize_risk_limits(self) -> Dict:
        """Inicializar limites de risco Goldman Sachs Style"""
        return {
            "tier_0": {  # Missão crítica
                "max_daily_loss": 0.05,      # 5%
                "max_position_size": 0.10,   # 10% do capital
                "max_drawdown": 0.15,        # 15%
                "max_exposure": 0.50,        # 50% do capital
                "var_confidence": 0.99,
                "stress_scenarios": 1000000,
                "real_time_monitoring": True,
                "auto_breakers": True
            },
            "tier_1": {  # Produção
                "max_daily_loss": 0.10,
                "max_position_size": 0.20,
                "max_drawdown": 0.25,
                "max_exposure": 0.75,
                "var_confidence": 0.95,
                "stress_scenarios": 100000,
                "real_time_monitoring": True,
                "auto_breakers": True
            },
            "tier_2": {  # Desenvolvimento
                "max_daily_loss": 0.25,
                "max_position_size": 0.50,
                "max_drawdown": 0.40,
                "max_exposure": 1.00,
                "var_confidence": 0.90,
                "stress_scenarios": 10000,
                "real_time_monitoring": False,
                "auto_breakers": False
            }
        }
    
    def _initialize_circuit_breakers(self) -> Dict:
        """Inicializar circuit breakers"""
        return {
            "max_drawdown_breaker": {
                "threshold": 0.15,
                "action": "STOP_ALL_TRADING",
                "cooldown_minutes": 60,
                "auto_reset": True
            },
            "daily_loss_breaker": {
                "threshold": 0.10,
                "action": "REDUCE_POSITIONS_50",
                "cooldown_minutes": 30,
                "auto_reset": True
            },
            "volatility_breaker": {
                "threshold": 3.0,  # Volatilidade histórica * 3
                "action": "PAUSE_NEW_TRADES",
                "cooldown_minutes": 15,
                "auto_reset": True
            },
            "concentration_breaker": {
                "threshold": 0.30,  # 30% em um ativo
                "action": "FORCE_DIVERSIFICATION",
                "cooldown_minutes": 0,
                "auto_reset": False
            }
        }
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar tier de risco
        self.risk_tier = config.get("risk_tier", "tier_1")
        self.current_limits = self.risk_limits[self.risk_tier]
        
        # Inicializar modelos
        await self.var_model.initialize(config.get("var_config", {}))
        await self.stress_test_engine.initialize(config.get("stress_test_config", {}))
        
        self.status = "ACTIVE"
        return True
    
    async def calculate_position_risk(self, position: Dict) -> Dict:
        """Calcular risco de posição individual"""
        risk_metrics = {
            "position_id": position.get("id"),
            "symbol": position.get("symbol"),
            "size": position.get("size", 0),
            "entry_price": position.get("entry_price", 0),
            "current_price": position.get("current_price", 0),
            "exposure": position.get("exposure", 0),
            
            # Métricas de risco
            "absolute_risk": self._calculate_absolute_risk(position),
            "var_95": await self.var_model.calculate(position, confidence=0.95),
            "var_99": await self.var_model.calculate(position, confidence=0.99),
            "expected_shortfall": await self._calculate_expected_shortfall(position),
            
            # Sensibilidade
            "delta": position.get("delta", 0) if position.get("option") else 1.0,
            "gamma": position.get("gamma", 0) if position.get("option") else 0,
            "vega": position.get("vega", 0) if position.get("option") else 0,
            "theta": position.get("theta", 0) if position.get("option") else 0,
            
            # Limites
            "limit_utilization": self._calculate_limit_utilization(position),
            "breach_risk": self._check_limit_breaches(position),
            
            "calculated_at": datetime.now().isoformat()
        }
        
        # Atualizar tracking de exposição
        self._update_exposure_tracking(risk_metrics)
        
        return risk_metrics
    
    async def calculate_portfolio_risk(self, portfolio: List[Dict]) -> Dict:
        """Calcular risco agregado do portfólio"""
        portfolio_metrics = {
            "portfolio_id": f"PORT_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "total_positions": len(portfolio),
            "total_exposure": sum(p.get("exposure", 0) for p in portfolio),
            "net_exposure": self._calculate_net_exposure(portfolio),
            "gross_exposure": self._calculate_gross_exposure(portfolio),
            "diversification_score": self._calculate_diversification_score(portfolio),
            
            # VAR do portfólio
            "portfolio_var_95": await self.calculate_portfolio_var(portfolio, 0.95),
            "portfolio_var_99": await self.calculate_portfolio_var(portfolio, 0.99),
            
            # Stress Testing
            "stress_test_results": await self.run_stress_tests(portfolio),
            
            # Concentração
            "concentration_metrics": self._calculate_concentration_metrics(portfolio),
            
            # Liquidez
            "liquidity_metrics": self._calculate_liquidity_metrics(portfolio),
            
            # Sensibilidade agregada
            "portfolio_greeks": self._calculate_portfolio_greeks(portfolio),
            
            "timestamp": datetime.now().isoformat()
        }
        
        # Verificar circuit breakers
        portfolio_metrics["circuit_breaker_status"] = await self.check_circuit_breakers(portfolio_metrics)
        
        # Armazenar no histórico
        self.risk_metrics_history.append(portfolio_metrics)
        
        return portfolio_metrics
    
    async def check_circuit_breakers(self, metrics: Dict) -> Dict:
        """Verificar e acionar circuit breakers"""
        triggers = []
        actions = []
        
        current_drawdown = metrics.get("current_drawdown", 0)
        daily_loss = metrics.get("daily_loss", 0)
        max_position_concentration = metrics.get("max_position_concentration", 0)
        
        # Verificar cada breaker
        for breaker_name, config in self.circuit_breakers.items():
            triggered = False
            action_needed = None
            
            if breaker_name == "max_drawdown_breaker":
                if current_drawdown > config["threshold"]:
                    triggered = True
                    action_needed = config["action"]
                    
            elif breaker_name == "daily_loss_breaker":
                if daily_loss > config["threshold"]:
                    triggered = True
                    action_needed = config["action"]
                    
            elif breaker_name == "concentration_breaker":
                if max_position_concentration > config["threshold"]:
                    triggered = True
                    action_needed = config["action"]
            
            if triggered:
                triggers.append({
                    "breaker": breaker_name,
                    "threshold": config["threshold"],
                    "actual": current_drawdown if "drawdown" in breaker_name else 
                              daily_loss if "loss" in breaker_name else 
                              max_position_concentration,
                    "action": action_needed,
                    "timestamp": datetime.now().isoformat()
                })
                
                actions.append(action_needed)
        
        # Executar ações se necessário
        executed_actions = []
        for action in set(actions):  # Remover duplicados
            if await self._execute_breaker_action(action):
                executed_actions.append(action)
        
        return {
            "triggers": triggers,
            "executed_actions": executed_actions,
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões de risco"""
        if transmission.module_type != ModuleType.RISK:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "calculate_position_risk":
            # Calcular risco de posição
            position = transmission.payload.get("position", {})
            risk_metrics = await self.calculate_position_risk(position)
            
            return NCNTTransmission(
                transmission_id=f"RISK_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload={
                    "risk_metrics": risk_metrics,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        elif action == "calculate_portfolio_risk":
            # Calcular risco de portfólio
            portfolio = transmission.payload.get("portfolio", [])
            portfolio_risk = await self.calculate_portfolio_risk(portfolio)
            
            return NCNTTransmission(
                transmission_id=f"RISK_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=portfolio_risk
            )
        
        elif action == "check_breakers":
            # Verificar circuit breakers
            metrics = transmission.payload.get("metrics", {})
            breaker_status = await self.check_circuit_breakers(metrics)
            
            return NCNTTransmission(
                transmission_id=f"RISK_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=breaker_status
            )
        
        return None
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _calculate_absolute_risk(self, position: Dict) -> float:
        """Calcular risco absoluto"""
        size = abs(position.get("size", 0))
        entry_price = position.get("entry_price", 0)
        current_price = position.get("current_price", 0)
        
        if entry_price == 0:
            return 0.0
            
        pnl_percentage = (current_price - entry_price) / entry_price
        exposure = size * entry_price
        
        return abs(exposure * pnl_percentage)
    
    async def _calculate_expected_shortfall(self, position: Dict) -> float:
        """Calcular Expected Shortfall (CVaR)"""
        # Implementação simplificada
        var_99 = await self.var_model.calculate(position, confidence=0.99)
        return var_99 * 1.5  # ES é tipicamente maior que VaR
    
    def _calculate_limit_utilization(self, position: Dict) -> Dict:
        """Calcular utilização de limites"""
        exposure = position.get("exposure", 0)
        position_size = abs(position.get("size", 0))
        
        return {
            "exposure_limit": exposure / (self.current_limits["max_exposure"] * 10000),
            "position_size_limit": position_size / self.current_limits["max_position_size"],
            "daily_loss_limit": 0.0,  # Seria calculado com P&L real
            "drawdown_limit": 0.0     # Seria calculado com drawdown real
        }
    
    def _check_limit_breaches(self, position: Dict) -> List[str]:
        """Verificar violações de limite"""
        breaches = []
        utilization = self._calculate_limit_utilization(position)
        
        if utilization["exposure_limit"] > 1.0:
            breaches.append("EXPOSURE_LIMIT_BREACH")
        if utilization["position_size_limit"] > 1.0:
            breaches.append("POSITION_SIZE_LIMIT_BREACH")
        
        return breaches
    
    def _update_exposure_tracking(self, risk_metrics: Dict):
        """Atualizar tracking de exposição"""
        symbol = risk_metrics.get("symbol")
        if not symbol:
            return
            
        if symbol not in self.exposure_tracking:
            self.exposure_tracking[symbol] = {
                "total_exposure": 0.0,
                "position_count": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        self.exposure_tracking[symbol]["total_exposure"] += risk_metrics.get("exposure", 0)
        self.exposure_tracking[symbol]["position_count"] += 1
        self.exposure_tracking[symbol]["last_updated"] = datetime.now().isoformat()
    
    def _calculate_net_exposure(self, portfolio: List[Dict]) -> float:
        """Calcular exposição líquida"""
        long_exposure = sum(p.get("exposure", 0) for p in portfolio if p.get("side") == "BUY")
        short_exposure = sum(p.get("exposure", 0) for p in portfolio if p.get("side") == "SELL")
        return long_exposure - short_exposure
    
    def _calculate_gross_exposure(self, portfolio: List[Dict]) -> float:
        """Calcular exposição bruta"""
        return sum(abs(p.get("exposure", 0)) for p in portfolio)
    
    def _calculate_diversification_score(self, portfolio: List[Dict]) -> float:
        """Calcular score de diversificação (0-1)"""
        if not portfolio:
            return 1.0
            
        # Contar ativos únicos
        unique_symbols = len(set(p.get("symbol") for p in portfolio))
        total_positions = len(portfolio)
        
        # Ponderar por exposição
        exposure_by_symbol = {}
        for position in portfolio:
            symbol = position.get("symbol", "UNKNOWN")
            exposure = abs(position.get("exposure", 0))
            exposure_by_symbol[symbol] = exposure_by_symbol.get(symbol, 0) + exposure
        
        # Calcular índice de Herfindahl-Hirschman (HHI)
        total_exposure = sum(exposure_by_symbol.values())
        if total_exposure == 0:
            return 1.0
            
        hhi = sum((exp / total_exposure) ** 2 for exp in exposure_by_symbol.values())
        
        # Converter HHI para score (0-1)
        # HHI varia de 1/n (perfeitamente diversificado) a 1 (monopólio)
        min_hhi = 1 / len(exposure_by_symbol) if exposure_by_symbol else 0
        score = 1 - (hhi - min_hhi) / (1 - min_hhi) if 1 - min_hhi > 0 else 1.0
        
        return max(0.0, min(1.0, score))
    
    async def calculate_portfolio_var(self, portfolio: List[Dict], confidence: float) -> float:
        """Calcular VAR do portfólio"""
        # Implementação simplificada
        total_exposure = sum(abs(p.get("exposure", 0)) for p in portfolio)
        
        if confidence == 0.95:
            return total_exposure * 0.05  # 5% VAR
        elif confidence == 0.99:
            return total_exposure * 0.10  # 10% VAR
        else:
            return total_exposure * 0.03  # 3% VAR padrão
    
    async def run_stress_tests(self, portfolio: List[Dict]) -> Dict:
        """Executar testes de stress"""
        scenarios = [
            {"name": "2008_Financial_Crisis", "shock": -0.50},
            {"name": "2020_COVID_Crash", "shock": -0.35},
            {"name": "Flash_Crash", "shock": -0.20},
            {"name": "Interest_Rate_Shock", "shock": 0.05},
            {"name": "Currency_Crisis", "shock": -0.25}
        ]
        
        results = {}
        total_exposure = sum(abs(p.get("exposure", 0)) for p in portfolio)
        
        for scenario in scenarios:
            scenario_loss = total_exposure * scenario["shock"]
            results[scenario["name"]] = {
                "shock_percentage": scenario["shock"],
                "estimated_loss": abs(scenario_loss),
                "survival_capital_required": abs(scenario_loss) * 1.5,
                "timestamp": datetime.now().isoformat()
            }
        
        return results
    
    def _calculate_concentration_metrics(self, portfolio: List[Dict]) -> Dict:
        """Calcular métricas de concentração"""
        if not portfolio:
            return {}
        
        exposure_by_symbol = {}
        for position in portfolio:
            symbol = position.get("symbol", "UNKNOWN")
            exposure = abs(position.get("exposure", 0))
            exposure_by_symbol[symbol] = exposure_by_symbol.get(symbol, 0) + exposure
        
        total_exposure = sum(exposure_by_symbol.values())
        
        if total_exposure == 0:
            return {}
        
        # Encontrar maior concentração
        max_symbol = max(exposure_by_symbol.items(), key=lambda x: x[1])
        max_concentration = max_symbol[1] / total_exposure
        
        # Top 3 concentrações
        top_symbols = sorted(exposure_by_symbol.items(), key=lambda x: x[1], reverse=True)[:3]
        top_concentrations = {symbol: exp/total_exposure for symbol, exp in top_symbols}
        
        return {
            "max_concentration": max_concentration,
            "max_concentration_symbol": max_symbol[0],
            "top_concentrations": top_concentrations,
            "symbol_count": len(exposure_by_symbol),
            "hhi_index": sum((exp/total_exposure)**2 for exp in exposure_by_symbol.values())
        }
    
    def _calculate_liquidity_metrics(self, portfolio: List[Dict]) -> Dict:
        """Calcular métricas de liquidez"""
        # Implementação simplificada
        liquidity_scores = {
            "EURUSD": 0.95,
            "GBPUSD": 0.90,
            "USDJPY": 0.92,
            "XAUUSD": 0.85,
            "BTCUSD": 0.75,
            "ETHUSD": 0.70
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for position in portfolio:
            symbol = position.get("symbol", "")
            exposure = abs(position.get("exposure", 0))
            score = liquidity_scores.get(symbol, 0.50)
            
            weighted_score += score * exposure
            total_weight += exposure
        
        avg_liquidity = weighted_score / total_weight if total_weight > 0 else 0.50
        
        return {
            "average_liquidity_score": avg_liquidity,
            "estimated_slippage": (1 - avg_liquidity) * 0.001,  # 0.1% slippage para baixa liquidez
            "exit_time_seconds": (1 - avg_liquidity) * 60,  # Tempo estimado para saída
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_portfolio_greeks(self, portfolio: List[Dict]) -> Dict:
        """Calcular gregos agregados do portfólio"""
        greeks = {
            "delta": 0.0,
            "gamma": 0.0,
            "vega": 0.0,
            "theta": 0.0,
            "rho": 0.0
        }
        
        for position in portfolio:
            if position.get("option"):
                greeks["delta"] += position.get("delta", 0)
                greeks["gamma"] += position.get("gamma", 0)
                greeks["vega"] += position.get("vega", 0)
                greeks["theta"] += position.get("theta", 0)
                greeks["rho"] += position.get("rho", 0)
            else:
                # Para posições à vista, delta é 1 para comprado, -1 para vendido
                side_multiplier = 1 if position.get("side") == "BUY" else -1
                greeks["delta"] += side_multiplier
        
        return greeks
    
    async def _execute_breaker_action(self, action: str) -> bool:
        """Executar ação do circuit breaker"""
        action_map = {
            "STOP_ALL_TRADING": self._stop_all_trading,
            "REDUCE_POSITIONS_50": self._reduce_positions_50,
            "PAUSE_NEW_TRADES": self._pause_new_trades,
            "FORCE_DIVERSIFICATION": self._force_diversification
        }
        
        if action in action_map:
            return await action_map[action]()
        
        return False
    
    async def _stop_all_trading(self) -> bool:
        """Parar todas as negociações"""
        # Em produção, enviaria comando para todos os módulos de execução
        print("🔴 STOP_ALL_TRADING: Todas as negociações foram interrompidas")
        self.update_metric("breaker_actions", "STOP_ALL_TRADING")
        return True
    
    async def _reduce_positions_50(self) -> bool:
        """Reduzir posições em 50%"""
        # Em produção, calcularia quais posições reduzir
        print("🟡 REDUCE_POSITIONS_50: Reduzindo posições em 50%")
        self.update_metric("breaker_actions", "REDUCE_POSITIONS_50")
        return True
    
    async def _pause_new_trades(self) -> bool:
        """Pausar novas negociações"""
        print("🟠 PAUSE_NEW_TRADES: Novas negociações pausadas")
        self.update_metric("breaker_actions", "PAUSE_NEW_TRADES")
        return True
    
    async def _force_diversification(self) -> bool:
        """Forçar diversificação"""
        print("🔵 FORCE_DIVERSIFICATION: Forçando diversificação do portfólio")
        self.update_metric("breaker_actions", "FORCE_DIVERSIFICATION")
        return True

# ============================================================================
# 📜 01-DEPARTAMENTOS: COMPLIANCE & AUDIT
# ============================================================================
