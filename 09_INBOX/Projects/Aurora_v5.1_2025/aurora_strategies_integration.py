#!/usr/bin/env python3
"""
AURORA STRATEGIES INTEGRATION - Integração das 3 Estratégias no Teste 24h
Ativa AlphaMomentum, MeanReversion e BreakoutDetection para operação em CRYPTO
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
import pandas as pd
import numpy as np
import yfinance as yf
import asyncio

# Adicionar caminho do projeto
project_root = Path(__file__).parent
strategies_path = project_root / "01-Departamentos" / "Execution-Trading" / "strategies"
infra_path = project_root / "04-Infraestrutura"

# Importar estratégias dinamicamente
import importlib.util

# Importar executor MT5
try:
    sys.path.insert(0, str(infra_path))
    from mt5_executor import MT5Executor
    MT5_AVAILABLE = True
except ImportError as e:
    MT5_AVAILABLE = False
    logging.warning(f"⚠️  MT5 Executor não disponível: {str(e)}")

logger = logging.getLogger("AURORA_STRATEGIES")

class AuroraStrategiesManager:
    """Gerenciador das 3 estratégias Aurora para operação em CRYPTO"""
    
    def __init__(self, mt5_enabled: bool = True, mt5_login: Optional[int] = None, 
                 mt5_password: Optional[str] = None, mt5_server: Optional[str] = None):
        self.strategies = {}
        self.strategy_results = {}
        self.initialized = False
        self.mt5_enabled = mt5_enabled and MT5_AVAILABLE
        self.mt5_executor = None
        
        # Inicializar MT5 se habilitado
        if self.mt5_enabled:
            try:
                self.mt5_executor = MT5Executor(
                    login=mt5_login,
                    password=mt5_password,
                    server=mt5_server
                )
                if self.mt5_executor.connected:
                    logger.info("✅ MT5 Executor conectado e pronto para executar ordens")
                else:
                    logger.warning("⚠️  MT5 Executor inicializado mas não conectado - tentará reconectar quando necessário")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar MT5 Executor: {str(e)}")
                self.mt5_enabled = False
                self.mt5_executor = None
        
        logger.info("🎯 Gerenciador de Estratégias Aurora inicializado")
    
    def initialize_strategies(self) -> bool:
        """Inicializa as 3 estratégias do sistema"""
        try:
            # 1. Alpha Momentum Strategy
            spec_alpha = importlib.util.spec_from_file_location(
                "alpha_momentum",
                strategies_path / "alpha_momentum.py"
            )
            alpha_module = importlib.util.module_from_spec(spec_alpha)
            spec_alpha.loader.exec_module(alpha_module)
            self.strategies["ALPHA_MOMENTUM_v1"] = alpha_module.AlphaMomentumStrategy()
            
            # 2. Mean Reversion Strategy
            spec_mean = importlib.util.spec_from_file_location(
                "mean_reversion",
                strategies_path / "mean_reversion.py"
            )
            mean_module = importlib.util.module_from_spec(spec_mean)
            spec_mean.loader.exec_module(mean_module)
            self.strategies["MEAN_REVERSION_v1"] = mean_module.MeanReversionStrategy()
            
            # 3. Breakout Detection Strategy
            spec_breakout = importlib.util.spec_from_file_location(
                "breakout_detection",
                strategies_path / "breakout_detection.py"
            )
            breakout_module = importlib.util.module_from_spec(spec_breakout)
            spec_breakout.loader.exec_module(breakout_module)
            self.strategies["BREAKOUT_DETECTION_v1"] = breakout_module.BreakoutDetectionStrategy()
            
            self.initialized = True
            logger.info(f"✅ {len(self.strategies)} estratégias inicializadas:")
            for strategy_id in self.strategies.keys():
                logger.info(f"   • {strategy_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar estratégias: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_yfinance_to_market_data(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Converte dados yfinance para formato market_data das estratégias"""
        if len(data) == 0:
            return {}
        
        try:
            # Pegar últimos dados (última linha)
            latest = data.iloc[-1]
            
            # Converter colunas para listas (garantir que são Series, não DataFrame)
            def safe_to_list(series_or_df, max_items=100):
                """Converte Series ou DataFrame para lista de forma segura"""
                if isinstance(series_or_df, pd.DataFrame):
                    # Se for DataFrame, pegar primeira coluna
                    series_or_df = series_or_df.iloc[:, 0]
                # Garantir que é Series
                if isinstance(series_or_df, pd.Series):
                    return series_or_df.tolist()[-max_items:]
                else:
                    # Se não for Series nem DataFrame, tentar converter
                    return list(series_or_df)[-max_items:] if hasattr(series_or_df, '__iter__') else []
            
            # Preparar histórico para análise
            market_data = {
                "symbol": symbol,
                "timestamp": latest.name if hasattr(latest.name, 'isoformat') else datetime.now(),
                "close": safe_to_list(data['Close'], 100),  # Últimos 100 pontos
                "high": safe_to_list(data['High'], 100),
                "low": safe_to_list(data['Low'], 100),
                "volume": safe_to_list(data['Volume'], 100),
                "open": safe_to_list(data['Open'], 100) if 'Open' in data.columns else safe_to_list(data['Close'], 100)
            }
            
            return market_data
        except Exception as e:
            logger.error(f"❌ Erro ao converter dados de {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
    async def analyze_with_all_strategies(self, symbol: str, period: str = "1d", interval: str = "15m") -> Dict[str, Any]:
        """Analisa símbolo com todas as 3 estratégias"""
        if not self.initialized:
            logger.error("❌ Estratégias não inicializadas")
            return {}
        
        try:
            # Coletar dados
            logger.info(f"📊 Coletando dados para {symbol}...")
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            
            if len(data) < 20:
                logger.warning(f"⚠️  {symbol}: Dados insuficientes ({len(data)} pontos)")
                return {"symbol": symbol, "error": "Dados insuficientes"}
            
            # Converter para formato das estratégias
            market_data = self.convert_yfinance_to_market_data(data, symbol)
            
            if not market_data:
                return {"symbol": symbol, "error": "Falha na conversão de dados"}
            
            # Analisar com cada estratégia
            results = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "strategies": {}
            }
            
            for strategy_id, strategy in self.strategies.items():
                try:
                    # Gerar sinais
                    signals = strategy.analyze(market_data)
                    
                    # Executar sinais no MT5 se habilitado
                    mt5_executions = []
                    if self.mt5_enabled and self.mt5_executor and signals:
                        for signal in signals:
                            # Filtrar apenas sinais BUY/SELL (ignorar HOLD)
                            if signal.action.upper() in ["BUY", "SELL"]:
                                try:
                                    execution_result = self.mt5_executor.execute_order(signal)
                                    mt5_executions.append(execution_result)
                                    
                                    if execution_result.get("success"):
                                        logger.info(f"   📤 {strategy_id}: Ordem executada no MT5 - Ticket: {execution_result.get('ticket')}")
                                    else:
                                        logger.warning(f"   ⚠️  {strategy_id}: Falha ao executar ordem no MT5 - {execution_result.get('error')}")
                                except Exception as e:
                                    logger.error(f"   ❌ {strategy_id}: Erro ao executar ordem no MT5 - {str(e)}")
                                    mt5_executions.append({"success": False, "error": str(e)})
                    
                    # Calcular métricas
                    risk_metrics = strategy.calculate_risk_metrics() if hasattr(strategy, 'calculate_risk_metrics') else {}
                    
                    results["strategies"][strategy_id] = {
                        "signals_generated": len(signals),
                        "signals": [
                            {
                                "action": sig.action,
                                "quantity": float(sig.quantity),
                                "price": float(sig.price),
                                "confidence": sig.confidence,
                                "timestamp": sig.timestamp.isoformat() if hasattr(sig.timestamp, 'isoformat') else str(sig.timestamp)
                            }
                            for sig in signals[:5]  # Limitar a 5 sinais
                        ],
                        "mt5_executions": mt5_executions if self.mt5_enabled else [],
                        "mt5_enabled": self.mt5_enabled,
                        "risk_metrics": risk_metrics,
                        "strategy_info": strategy.get_strategy_info()
                    }
                    
                    logger.info(f"   ✅ {strategy_id}: {len(signals)} sinais gerados" + 
                               (f", {len([e for e in mt5_executions if e.get('success')])} ordens executadas no MT5" if mt5_executions else ""))
                    
                except Exception as e:
                    logger.error(f"   ❌ {strategy_id}: Erro na análise - {str(e)}")
                    results["strategies"][strategy_id] = {
                        "error": str(e),
                        "signals_generated": 0
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"💥 Erro ao analisar {symbol}: {str(e)}")
            return {"symbol": symbol, "error": str(e)}
    
    async def run_24h_test_cycle(self, crypto_pairs: List[str], interval_minutes: int = 5) -> Dict[str, Any]:
        """Executa um ciclo de teste de 24h com todas as estratégias"""
        if not self.initialized:
            if not self.initialize_strategies():
                return {"error": "Falha ao inicializar estratégias"}
        
        logger.info("🚀 INICIANDO CICLO DE TESTE 24H COM ESTRATÉGIAS")
        logger.info(f"📊 Pares crypto: {', '.join(crypto_pairs)}")
        logger.info(f"⏱️  Intervalo: {interval_minutes} minutos")
        
        cycle_results = {
            "start_time": datetime.now().isoformat(),
            "crypto_pairs": crypto_pairs,
            "strategies_active": list(self.strategies.keys()),
            "cycles": [],
            "summary": {
                "total_cycles": 0,
                "successful_cycles": 0,
                "total_signals": 0,
                "signals_by_strategy": {sid: 0 for sid in self.strategies.keys()}
            }
        }
        
        # Executar análise para cada par
        for symbol in crypto_pairs:
            try:
                result = await self.analyze_with_all_strategies(
                    symbol=symbol,
                    period="1d",
                    interval="15m"
                )
                
                cycle_results["cycles"].append(result)
                cycle_results["summary"]["total_cycles"] += 1
                
                if "error" not in result:
                    cycle_results["summary"]["successful_cycles"] += 1
                    
                    # Contar sinais por estratégia
                    for strategy_id, strategy_data in result.get("strategies", {}).items():
                        signals_count = strategy_data.get("signals_generated", 0)
                        cycle_results["summary"]["total_signals"] += signals_count
                        cycle_results["summary"]["signals_by_strategy"][strategy_id] += signals_count
                
            except Exception as e:
                logger.error(f"💥 Erro no ciclo para {symbol}: {str(e)}")
                cycle_results["cycles"].append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        cycle_results["end_time"] = datetime.now().isoformat()
        
        logger.info("📊 RESUMO DO CICLO:")
        logger.info(f"   • Ciclos executados: {cycle_results['summary']['total_cycles']}")
        logger.info(f"   • Ciclos bem-sucedidos: {cycle_results['summary']['successful_cycles']}")
        logger.info(f"   • Total de sinais: {cycle_results['summary']['total_signals']}")
        for strategy_id, count in cycle_results['summary']['signals_by_strategy'].items():
            logger.info(f"   • {strategy_id}: {count} sinais")
        
        return cycle_results
    
    def get_strategies_status(self) -> Dict[str, Any]:
        """Retorna status de todas as estratégias"""
        status = {
            "initialized": self.initialized,
            "strategies_count": len(self.strategies),
            "strategies": {
                strategy_id: strategy.get_strategy_info()
                for strategy_id, strategy in self.strategies.items()
            },
            "mt5_enabled": self.mt5_enabled,
            "mt5_connected": self.mt5_executor.connected if self.mt5_executor else False
        }
        
        # Adicionar estatísticas MT5 se disponível
        if self.mt5_executor:
            status["mt5_statistics"] = self.mt5_executor.get_statistics()
        
        return status

