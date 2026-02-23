#!/usr/bin/env python3
"""
StrategyModule - Módulo NCNT
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

class StrategyModule(NCNTBaseModule):
    """📈 MÓDULO DE ESTRATÉGIA - Template para todas estratégias"""
    
    STRATEGY_TYPE = "base"
    ASSET_CLASS = AssetClass.FOREX
    
    def __init__(self, strategy_name: str):
        super().__init__(strategy_name, ModuleType.STRATEGY)
        self.parameters = {}
        self.market_data_buffer = []
        self.signal_history = []
        self.performance_metrics = {
            "total_signals": 0,
            "profitable_signals": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0
        }
        
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar parâmetros da estratégia
        self.parameters = config.get("parameters", {})
        
        # Configurar buffers
        buffer_size = config.get("buffer_size", 1000)
        self.market_data_buffer = []
        
        self.status = "ACTIVE"
        return True
    
    @abstractmethod
    async def analyze(self, market_data: Dict) -> Dict:
        """Análise de mercado - IMPLEMENTAR NAS SUBCLASSES"""
        pass
    
    @abstractmethod
    async def generate_signal(self, analysis: Dict) -> Optional[Dict]:
        """Gerar sinal de trading - IMPLEMENTAR NAS SUBCLASSES"""
        pass
    
    async def process_market_data(self, market_data: Dict) -> Optional[Dict]:
        """Processar dados de mercado e gerar sinal"""
        try:
            # 1. Adicionar ao buffer
            self.market_data_buffer.append(market_data)
            if len(self.market_data_buffer) > 1000:
                self.market_data_buffer.pop(0)
            
            # 2. Análise
            analysis = await self.analyze(market_data)
            if not analysis:
                return None
            
            # 3. Gerar sinal
            raw_signal = await self.generate_signal(analysis)
            if not raw_signal:
                return None
            
            # 4. Formatar sinal no padrão NCNT
            formatted_signal = self._format_signal(raw_signal, market_data)
            
            # 5. Atualizar histórico
            self.signal_history.append(formatted_signal)
            
            # 6. Atualizar métricas
            self._update_performance_metrics(formatted_signal)
            
            return formatted_signal
            
        except Exception as e:
            self._log_error(f"Error processing market data: {e}")
            return None
    
    def _format_signal(self, raw_signal: Dict, market_data: Dict) -> Dict:
        """Formatar sinal no padrão NCNT"""
        signal_id = f"SIG_{self.module_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "signal_id": signal_id,
            "strategy_id": self.module_id,
            "strategy_name": self.module_name,
            "strategy_type": self.STRATEGY_TYPE,
            "timestamp": datetime.now().isoformat(),
            "action": raw_signal.get("action"),  # BUY, SELL, HOLD
            "symbol": raw_signal.get("symbol", market_data.get("symbol", "EURUSD")),
            "price": raw_signal.get("price", market_data.get("price", 0.0)),
            "size": raw_signal.get("size", 0.01),
            "confidence": raw_signal.get("confidence", 0.5),
            "stop_loss": raw_signal.get("stop_loss"),
            "take_profit": raw_signal.get("take_profit"),
            "timeframe": raw_signal.get("timeframe", "M1"),
            "reasoning": raw_signal.get("reasoning", ""),
            "market_conditions": {
                "volatility": market_data.get("volatility", 0.0),
                "volume": market_data.get("volume", 0.0),
                "trend": market_data.get("trend", "neutral")
            }
        }
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões para estratégias"""
        if transmission.module_type != ModuleType.STRATEGY:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "process_market_data":
            # Processar dados de mercado
            market_data = transmission.payload.get("market_data", {})
            signal = await self.process_market_data(market_data)
            
            response_payload = {
                "strategy_id": self.module_id,
                "signal": signal,
                "timestamp": datetime.now().isoformat()
            }
            
            return NCNTTransmission(
                transmission_id=f"STRAT_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=response_payload
            )
        
        elif action == "get_performance_report":
            # Retornar relatório de performance
            report = await self.get_performance_report()
            
            return NCNTTransmission(
                transmission_id=f"STRAT_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=report
            )
        
        return None
    
    async def get_performance_report(self) -> Dict:
        """Gerar relatório de performance"""
        return {
            "report_id": f"PERF_REPORT_{self.module_id}_{datetime.now().strftime('%Y%m%d')}",
            "strategy_id": self.module_id,
            "strategy_name": self.module_name,
            "strategy_type": self.STRATEGY_TYPE,
            "status": self.status,
            "parameters": self.parameters,
            "performance_metrics": self.performance_metrics,
            "total_signals": len(self.signal_history),
            "last_signal": self.signal_history[-1] if self.signal_history else None,
            "market_data_buffer_size": len(self.market_data_buffer),
            "timestamp": datetime.now().isoformat()
        }
    
    # ========== MÉTODOS INTERNOS ==========
    
    def _update_performance_metrics(self, signal: Dict):
        """Atualizar métricas de performance"""
        self.performance_metrics["total_signals"] += 1
        
        # Em produção, calcularia P&L real
        if signal.get("action") in ["BUY", "SELL"]:
            # Simular resultado
            import random
            is_profitable = random.random() > 0.4  # 60% win rate
            
            if is_profitable:
                self.performance_metrics["profitable_signals"] += 1
                self.performance_metrics["total_pnl"] += 10.0  # Simulado
            else:
                self.performance_metrics["total_pnl"] -= 5.0  # Simulado
            
            # Calcular win rate
            if self.performance_metrics["total_signals"] > 0:
                self.performance_metrics["win_rate"] = (
                    self.performance_metrics["profitable_signals"] / 
                    self.performance_metrics["total_signals"]
                )
    
    def _log_error(self, error_message: str):
        """Log de erro"""
        error_entry = {
            "strategy_id": self.module_id,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
        self.update_metric("errors", error_entry)

# ============================================================================
# 🛡️ 01-DEPARTAMENTOS: RISK & CONTROLS
# ============================================================================
