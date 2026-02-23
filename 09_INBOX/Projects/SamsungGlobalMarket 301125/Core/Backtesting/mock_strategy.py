# -*- coding: utf-8 -*-
"""
MOCK STRATEGY - VALIDAÇÃO DO FRAMEWORK DE BACKTESTING
DIRETIVA: F1-T4 - Validação com Dados Simples
DATA: 02-11-2025 22:00 CET

OBJETIVO:
- Validar framework de backtesting com sinais previsíveis
- Isolar problemas do framework vs problemas de estratégia
- Permitir cálculo manual de métricas esperadas

FUNCIONALIDADE:
- Sinais absurdamente simples e previsíveis
- SPY: BUY primeiro dia de cada mês, SELL 15 dias depois
- BTC-USD: SELL quando queda > 5% em 1 dia
- Permite validação manual dos resultados
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class MockStrategy:
    """
    Estratégia mock para validação do framework
    
    REGRAS SIMPLES:
    1. SPY: Monthly rotation (BUY dia 1, SELL dia 15)
    2. BTC-USD: Sell on 5% drop
    3. Previsível e testável manualmente
    """
    
    def __init__(self, strategy_type: str = 'monthly_rotation'):
        """
        Initialize Mock Strategy
        
        Args:
            strategy_type: 'monthly_rotation' ou 'drop_sell'
        """
        self.strategy_type = strategy_type
        self.last_trade_month = None
        self.position_open = False
        self.entry_price = None
        
        logger.info(f"[MockStrategy] Tipo: {strategy_type}")
    
    def generate_signal(self, 
                       symbol: str,
                       current_date: datetime,
                       current_price: float,
                       price_history: pd.Series = None) -> Optional[Dict]:
        """
        Gera sinal mock baseado em regras simples
        
        Args:
            symbol: Símbolo do ativo
            current_date: Data atual
            current_price: Preço atual
            price_history: Série de preços históricos
            
        Returns:
            Dict com sinal ou None
        """
        
        if self.strategy_type == 'monthly_rotation':
            return self._monthly_rotation_signal(symbol, current_date, current_price)
        
        elif self.strategy_type == 'drop_sell':
            return self._drop_sell_signal(symbol, current_date, current_price, price_history)
        
        return None
    
    def _monthly_rotation_signal(self, symbol: str, current_date: datetime, 
                                 current_price: float) -> Optional[Dict]:
        """
        REGRA: BUY no dia 1 de cada mês, SELL no dia 15
        
        Exemplo:
        - 2021-01-01: BUY SPY @ 370
        - 2021-01-15: SELL SPY @ 380
        - 2021-02-01: BUY SPY @ 385
        - ...
        
        Resultado esperado: ~12 trades por ano = 36 trades em 3 anos
        """
        current_month = current_date.month
        current_day = current_date.day
        
        # BUY no primeiro dia útil do mês
        if current_day == 1 and not self.position_open:
            self.position_open = True
            self.entry_price = current_price
            self.last_trade_month = current_month
            
            return {
                'action': 'BUY',
                'symbol': symbol,
                'price': current_price,
                'confidence': 1.0,  # Mock tem 100% confidence
                'stop_loss': current_price * 0.95,  # -5%
                'take_profit': current_price * 1.05,  # +5%
                'reason': f'Monthly rotation: BUY dia 1 de {current_month}'
            }
        
        # SELL no dia 15
        elif current_day >= 15 and self.position_open and current_month == self.last_trade_month:
            self.position_open = False
            
            # Calcular P&L esperado
            expected_pnl = ((current_price - self.entry_price) / self.entry_price) * 100
            
            return {
                'action': 'SELL',
                'symbol': symbol,
                'price': current_price,
                'confidence': 1.0,
                'expected_pnl': expected_pnl,
                'reason': f'Monthly rotation: SELL dia 15 de {current_month}'
            }
        
        return None
    
    def _drop_sell_signal(self, symbol: str, current_date: datetime,
                         current_price: float, price_history: pd.Series) -> Optional[Dict]:
        """
        REGRA: SELL quando preço cai > 5% em 1 dia
        
        Exemplo:
        - 2021-05-19: BTC cai de 43k para 36k (-16%)
        - SINAL: SELL (short)
        - Stop: 36k * 1.03 = 37k
        - Target: 36k * 0.95 = 34.2k
        
        Resultado esperado: ~10-15 trades em 3 anos (eventos raros)
        """
        if price_history is None or len(price_history) < 2:
            return None
        
        # Calcular mudança de 1 dia
        yesterday_price = price_history.iloc[-2]
        today_price = current_price
        
        daily_change = (today_price - yesterday_price) / yesterday_price
        
        # Se queda > 5% e não há posição aberta
        if daily_change < -0.05 and not self.position_open:
            self.position_open = True
            self.entry_price = current_price
            
            return {
                'action': 'SELL',  # SHORT
                'symbol': symbol,
                'price': current_price,
                'confidence': 1.0,
                'stop_loss': current_price * 1.03,  # +3% (stop para short)
                'take_profit': current_price * 0.95,  # -5% (target para short)
                'reason': f'Drop > 5%: {daily_change*100:.1f}%'
            }
        
        # Fechar se atingir target de -5% adicional
        elif self.position_open and daily_change < -0.05:
            self.position_open = False
            
            expected_pnl = ((self.entry_price - current_price) / self.entry_price) * 100
            
            return {
                'action': 'CLOSE',
                'symbol': symbol,
                'price': current_price,
                'confidence': 1.0,
                'expected_pnl': expected_pnl,
                'reason': 'Target atingido'
            }
        
        return None
    
    def reset(self):
        """Reset do estado da estratégia"""
        self.position_open = False
        self.entry_price = None
        self.last_trade_month = None

# =====================================================
# CALCULADORA DE MÉTRICAS ESPERADAS (Para Validação Manual)
# =====================================================

class MockStrategyValidator:
    """
    Valida resultados do backtest contra valores esperados
    """
    
    @staticmethod
    def calculate_expected_metrics_monthly_rotation(years: int = 3) -> Dict:
        """
        Calcula métricas esperadas para monthly rotation
        
        Args:
            years: Número de anos de backtest
            
        Returns:
            Dict com métricas esperadas
        """
        # Monthly rotation: 12 trades por ano
        expected_trades = 12 * years
        
        # Assumindo SPY sobe ~10% ao ano
        # Cada trade captura ~2 semanas de movimento
        # Expectativa: +0.5% por trade em média
        
        expected_metrics = {
            'total_trades': expected_trades,
            'win_rate': 0.60,  # 60% dos trades lucrativos
            'avg_return_per_trade': 0.005,  # 0.5% por trade
            'total_return': expected_trades * 0.005,  # ~18% em 3 anos
            'max_drawdown': 0.10,  # Esperado < 10%
            'sharpe_ratio': 0.8  # Sharpe moderado
        }
        
        logger.info("[Validator] Métricas esperadas (Monthly Rotation):")
        logger.info(f"  Trades: {expected_metrics['total_trades']}")
        logger.info(f"  Win rate: {expected_metrics['win_rate']*100:.0f}%")
        logger.info(f"  Retorno total: {expected_metrics['total_return']*100:.1f}%")
        
        return expected_metrics
    
    @staticmethod
    def validate_results(actual_metrics: Dict, expected_metrics: Dict) -> bool:
        """
        Valida se resultados estão próximos do esperado
        
        Args:
            actual_metrics: Métricas do backtest
            expected_metrics: Métricas esperadas
            
        Returns:
            bool: True se validação passou
        """
        tolerance = 0.20  # 20% de tolerância
        
        checks = []
        
        # Check 1: Número de trades
        trades_ok = abs(actual_metrics['total_trades'] - expected_metrics['total_trades']) <= 5
        checks.append(trades_ok)
        logger.info(f"  Trades: {'OK' if trades_ok else 'FALHOU'} "
                   f"(esperado: {expected_metrics['total_trades']}, "
                   f"atual: {actual_metrics['total_trades']})")
        
        # Check 2: Retorno total
        expected_return = expected_metrics['total_return']
        actual_return = actual_metrics.get('total_return', 0)
        return_ok = abs(actual_return - expected_return) <= abs(expected_return * tolerance)
        checks.append(return_ok)
        logger.info(f"  Retorno: {'OK' if return_ok else 'FALHOU'} "
                   f"(esperado: {expected_return*100:.1f}%, "
                   f"atual: {actual_return*100:.1f}%)")
        
        all_ok = all(checks)
        
        if all_ok:
            logger.info("[Validator] VALIDAÇÃO PASSOU ✅")
        else:
            logger.warning("[Validator] VALIDAÇÃO FALHOU ⚠️")
        
        return all_ok

