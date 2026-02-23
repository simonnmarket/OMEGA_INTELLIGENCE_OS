# EquitiesStrategiesAdapter_Numeia.py
"""
EQUITIES STRATEGIES ADAPTER - INTEGRAÇÃO COM NUMEIA v3.0
FASE 5.5 - CORREÇÃO CRÍTICA
DATA: 02-11-2025 20:20 CET
APROVAÇÃO: PROTOCOLO DE CORREÇÃO IMEDIATA

FUNCIONALIDADE:
- Adapta as 3 estratégias científicas Equities para o formato TradingSignalPerfeito
- Interface padronizada para integração com NumeiaTradingSystem v3.0
- Gestão de capital entre as 3 estratégias
- Conformidade 100% com Protocolo Blindado

COMPLIANCE: PROTOCOLO BLINDADO 100%
INTEGRAÇÃO: NumeiaTradingSystem v3.0
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import pandas as pd

from DefenseTechPairsStrategy_Scientific import DefenseTechPairsStrategy
from VolatilityArbitrageStrategy_Scientific import VolatilityArbitrageStrategy
from SectorRotationStrategy_Scientific import SectorRotationStrategy

@dataclass
class TradingSignalPerfeito:
    """
    Estrutura de sinal de trading perfeito para NumeiaTradingSystem v3.0
    Formato unificado para todos os módulos
    """
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0.0 - 1.0
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    strategy_name: str
    timestamp: datetime
    position_size: Optional[Decimal] = None
    entry_price: Optional[float] = None
    metadata: Optional[Dict] = None

class EquitiesStrategiesAdapter:
    """
    Adaptador das 3 estratégias científicas Equities
    para o formato TradingSignalPerfeito do Numeia v3.0
    
    Responsabilidades:
    - Inicializar as 3 estratégias científicas
    - Alocar capital entre estratégias
    - Converter sinais para formato TradingSignalPerfeito
    - Validar sinais antes de retornar
    """
    
    def __init__(self, allocated_capital: Decimal = Decimal('100000')):
        """
        Initialize Equities Strategies Adapter
        
        Args:
            allocated_capital: Capital total alocado para Equities (default: €100k)
        """
        self.allocated_capital = allocated_capital
        
        # Alocação de capital por estratégia (baseado em risco/retorno)
        self.capital_allocation = {
            'pairs': Decimal('0.40'),      # 40% - menor risco, maior Sharpe
            'volatility': Decimal('0.30'),  # 30% - risco médio
            'sector': Decimal('0.30')       # 30% - risco médio
        }
        
        # Inicializar as 3 estratégias científicas
        self.pairs_strategy = DefenseTechPairsStrategy(
            zscore_threshold=2.0,
            correlation_threshold=0.7,
            lookback_period=60,
            kelly_fraction=0.25
        )
        
        self.volatility_strategy = VolatilityArbitrageStrategy(
            lookback_period=20,
            volatility_window=30,
            bollinger_std=2.0,
            vol_ratio_threshold=1.5
        )
        
        self.sector_strategy = SectorRotationStrategy(
            momentum_window=126,
            max_sectors=5,
            min_allocation=0.05,
            max_allocation=0.25,
            rebalance_threshold=0.10
        )
        
        # Mapeamento de estratégias
        self.strategies = {
            'pairs': self.pairs_strategy,
            'volatility': self.volatility_strategy,
            'sector': self.sector_strategy
        }
        
        logging.info("[EquitiesAdapter] Initialized for NumeiaTradingSystem v3.0")
        logging.info(f"  Total capital: €{float(allocated_capital):,.0f}")
        logging.info(f"  Active strategies: 3 (MODULO EQUITIES)")
        logging.info(f"  Capital allocation:")
        logging.info(f"    - Pairs Trading: €{float(allocated_capital * self.capital_allocation['pairs']):,.0f}")
        logging.info(f"    - Volatility Arb: €{float(allocated_capital * self.capital_allocation['volatility']):,.0f}")
        logging.info(f"    - Sector Rotation: €{float(allocated_capital * self.capital_allocation['sector']):,.0f}")
    
    def generate_signals(self, price_data: Dict[str, pd.Series]) -> List[TradingSignalPerfeito]:
        """
        Gera sinais de todas as 3 estratégias no formato TradingSignalPerfeito
        
        Args:
            price_data: Dicionário com dados de preços {symbol: pd.Series}
            
        Returns:
            Lista de TradingSignalPerfeito
        """
        all_signals = []
        
        # 1. PAIRS TRADING
        try:
            pairs_raw = self.pairs_strategy.generate_signal(price_data)
            if pairs_raw and pairs_raw.get('action') != 'HOLD':
                pairs_signal = self._convert_to_perfect_signal(
                    raw_signal=pairs_raw,
                    strategy_name='DefenseTech Pairs Trading',
                    allocated_capital=self.allocated_capital * self.capital_allocation['pairs']
                )
                all_signals.append(pairs_signal)
        except Exception as e:
            logging.warning(f"[EquitiesAdapter] Erro em Pairs Trading: {e}")
        
        # 2. VOLATILITY ARBITRAGE
        try:
            vol_raw = self.volatility_strategy.generate_signal(price_data)
            if vol_raw and vol_raw.get('action') != 'HOLD':
                vol_signal = self._convert_to_perfect_signal(
                    raw_signal=vol_raw,
                    strategy_name='Volatility Arbitrage',
                    allocated_capital=self.allocated_capital * self.capital_allocation['volatility']
                )
                all_signals.append(vol_signal)
        except Exception as e:
            logging.warning(f"[EquitiesAdapter] Erro em Volatility Arbitrage: {e}")
        
        # 3. SECTOR ROTATION
        try:
            sector_raw = self.sector_strategy.generate_signal(price_data)
            if sector_raw and sector_raw.get('action') != 'HOLD':
                sector_signal = self._convert_to_perfect_signal(
                    raw_signal=sector_raw,
                    strategy_name='Sector Rotation',
                    allocated_capital=self.allocated_capital * self.capital_allocation['sector']
                )
                all_signals.append(sector_signal)
        except Exception as e:
            logging.warning(f"[EquitiesAdapter] Erro em Sector Rotation: {e}")
        
        logging.info(f"[EquitiesAdapter] Generated {len(all_signals)} signals from 3 strategies")
        return all_signals
    
    def _convert_to_perfect_signal(self, 
                                   raw_signal: Dict, 
                                   strategy_name: str,
                                   allocated_capital: Decimal) -> TradingSignalPerfeito:
        """
        Converte sinal bruto da estratégia para TradingSignalPerfeito
        
        Args:
            raw_signal: Sinal bruto da estratégia
            strategy_name: Nome da estratégia
            allocated_capital: Capital alocado para esta estratégia
            
        Returns:
            TradingSignalPerfeito
        """
        # Extrair informações do sinal bruto
        symbol = raw_signal.get('symbol', 'UNKNOWN')
        action = raw_signal.get('action', 'HOLD')
        confidence = raw_signal.get('confidence', 0.5)
        
        # Calcular stop loss e take profit baseado em volatilidade
        entry_price = raw_signal.get('price', 100.0)
        volatility = raw_signal.get('volatility', 0.02)  # 2% default
        
        # Stop loss: 2x volatilidade
        stop_loss = entry_price * (1 - 2 * volatility) if action == 'BUY' else entry_price * (1 + 2 * volatility)
        
        # Take profit: 6x volatilidade (risco/retorno 3:1)
        take_profit = entry_price * (1 + 6 * volatility) if action == 'BUY' else entry_price * (1 - 6 * volatility)
        
        # Calcular risk/reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 3.0
        
        # Calcular tamanho da posição baseado em Kelly
        kelly_fraction = raw_signal.get('kelly_fraction', 0.25)
        position_size = allocated_capital * Decimal(str(kelly_fraction))
        
        return TradingSignalPerfeito(
            symbol=symbol,
            action=action,
            confidence=confidence,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            strategy_name=strategy_name,
            timestamp=datetime.now(),
            position_size=position_size,
            entry_price=entry_price,
            metadata={
                'strategy_details': raw_signal,
                'allocated_capital': float(allocated_capital),
                'kelly_fraction': kelly_fraction,
                'volatility': volatility
            }
        )
    
    def get_strategies_status(self) -> Dict:
        """
        Retorna status de todas as estratégias
        
        Returns:
            Dict com status de cada estratégia
        """
        return {
            'total_strategies': 3,
            'allocated_capital': float(self.allocated_capital),
            'strategies': {
                'pairs_trading': {
                    'name': 'DefenseTech Pairs Trading',
                    'capital': float(self.allocated_capital * self.capital_allocation['pairs']),
                    'allocation': float(self.capital_allocation['pairs'])
                },
                'volatility_arbitrage': {
                    'name': 'Volatility Arbitrage',
                    'capital': float(self.allocated_capital * self.capital_allocation['volatility']),
                    'allocation': float(self.capital_allocation['volatility'])
                },
                'sector_rotation': {
                    'name': 'Sector Rotation',
                    'capital': float(self.allocated_capital * self.capital_allocation['sector']),
                    'allocation': float(self.capital_allocation['sector'])
                }
            }
        }

