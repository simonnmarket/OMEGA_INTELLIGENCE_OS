# FuturesModule_Numeia_v3_0.py
"""
MODULO FUTURES PARA NUMEIA TRADING SYSTEM v3.0
FASE 3 - INTEGRACAO COMPLETA
DATA: 01-11-2025 22:20 CET
APROVACAO: CONSELHO (ROTA 2 - SYNTHETIC FUTURES)

FUNCIONALIDADE:
- Interface padrao do modulo Futures para o NumeiaTradingSystem
- Gerenciamento de risco consolidado
- Integracao com 5 engines Numeia
- Retorno padrao: Lista de TradingSignalPerfeito

INOVACAO: Primeira implementacao usando Futuros Sinteticos (Cost-of-Carry)
COMPLIANCE: PROTOCOLO BLINDADO 100%
CAPITAL APROVADO: €75,000
ESTRATEGIAS: 2 (Calendar Spread + Term Structure)
"""

import sys
from pathlib import Path

# Adicionar pasta Strategies/Futures ao path
futures_path = Path(__file__).parent.parent / 'Strategies' / 'Futures'
sys.path.insert(0, str(futures_path))

from decimal import Decimal
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Import adapter Futures
from FuturesStrategyAdapter_Numeia import FuturesStrategyAdapter, TradingSignalPerfeito


class FuturesModule:
    """
    Modulo Futures para NumeiaTradingSystem v3.0
    
    Interface padrao: analyze() -> List[TradingSignalPerfeito]
    
    INOVACAO: Utiliza Futuros Sinteticos via Cost-of-Carry Model
    """
    
    def __init__(self,
                 allocated_capital: Decimal = Decimal('75000'),
                 max_positions: int = 3,
                 max_daily_trades: int = 8):
        """
        Initialize Futures Module
        
        Args:
            allocated_capital: Capital alocado (aprovado: €75k)
            max_positions: Maximo de posicoes simultaneas
            max_daily_trades: Maximo de trades por dia
        """
        self.allocated_capital = allocated_capital
        self.max_positions = max_positions
        self.max_daily_trades = max_daily_trades
        
        # Inicializar adapter
        self.adapter = FuturesStrategyAdapter(allocated_capital=allocated_capital)
        
        # Controles de risco
        self.current_positions = 0
        self.daily_trades = 0
        self.last_trade_date = None
        
        # Estatisticas
        self.total_signals_generated = 0
        self.total_signals_filtered = 0
        
        logging.info(f"[FuturesModule] Inicializado")
        logging.info(f"  -> Capital: €{self.allocated_capital}")
        logging.info(f"  -> Max Positions: {self.max_positions}")
        logging.info(f"  -> Max Daily Trades: {self.max_daily_trades}")
        logging.info(f"  -> Estrategias: 2 (Calendar Spread + Term Structure)")
        logging.info(f"  -> Metodo: Synthetic Futures (Cost-of-Carry)")
    
    def analyze(self,
                hale_engine,
                rossi_engine,
                tanaka_engine,
                leblanc_engine,
                market_masters_engine,
                use_real_data: bool = True) -> List[TradingSignalPerfeito]:
        """
        Interface padrao para NumeiaTradingSystem
        
        Analisa mercado de futuros e retorna sinais formatados
        
        Args:
            hale_engine: Engine Hale
            rossi_engine: Engine Rossi
            tanaka_engine: Engine Tanaka
            leblanc_engine: Engine Leblanc
            market_masters_engine: Engine MarketMasters
            use_real_data: Se True, usa yfinance + FRED
        
        Returns:
            Lista de TradingSignalPerfeito
        """
        
        # Reset contador diario
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
        
        # Gerar sinais via adapter
        signals = self.adapter.generate_all_futures_signals(
            hale_engine=hale_engine,
            rossi_engine=rossi_engine,
            tanaka_engine=tanaka_engine,
            leblanc_engine=leblanc_engine,
            market_masters_engine=market_masters_engine,
            use_real_data=use_real_data
        )
        
        self.total_signals_generated += len(signals)
        
        # Aplicar filtros de risco
        filtered_signals = []
        
        for signal in signals:
            # Filtro 1: Limite de posicoes
            if self.current_positions >= self.max_positions:
                logging.warning(f"[FuturesModule] Limite de posicoes: {self.current_positions}/{self.max_positions}")
                self.total_signals_filtered += 1
                continue
            
            # Filtro 2: Limite de trades diarios
            if self.daily_trades >= self.max_daily_trades:
                logging.warning(f"[FuturesModule] Limite de trades diarios: {self.daily_trades}/{self.max_daily_trades}")
                self.total_signals_filtered += 1
                continue
            
            # Filtro 3: Validacao MarketMasters
            if not signal.market_masters_validation:
                logging.warning(f"[FuturesModule] Sinal falhou validacao MarketMasters")
                self.total_signals_filtered += 1
                continue
            
            # Filtro 4: Confidence minima
            if signal.confidence < 0.15:
                logging.warning(f"[FuturesModule] Confidence baixa: {signal.confidence:.2f} < 0.15")
                self.total_signals_filtered += 1
                continue
            
            # Sinal aprovado
            filtered_signals.append(signal)
            
            # Atualizar contadores
            if signal.action in ['BUY', 'SELL', 'BUY_SPREAD', 'SELL_SPREAD']:
                self.daily_trades += 1
        
        logging.info(f"[FuturesModule] Gerados: {len(signals)} | Aprovados: {len(filtered_signals)} | Filtrados: {len(signals) - len(filtered_signals)}")
        
        return filtered_signals
    
    def get_module_status(self) -> Dict:
        """
        Retorna status do modulo
        
        Returns:
            Dict com metricas
        """
        return {
            'module': 'Futures',
            'version': '3.0',
            'method': 'Synthetic (Cost-of-Carry)',
            'allocated_capital': float(self.allocated_capital),
            'strategies': 2,
            'strategy_names': ['Calendar Spread', 'Term Structure Arbitrage'],
            'max_positions': self.max_positions,
            'current_positions': self.current_positions,
            'max_daily_trades': self.max_daily_trades,
            'daily_trades': self.daily_trades,
            'total_signals_generated': self.total_signals_generated,
            'total_signals_filtered': self.total_signals_filtered,
            'filter_rate': (self.total_signals_filtered / self.total_signals_generated * 100)
                          if self.total_signals_generated > 0 else 0.0
        }
    
    def validate_module(self) -> bool:
        """
        Valida integridade do modulo
        
        Returns:
            True se OK
        """
        try:
            logging.info("[FuturesModule] Iniciando validacao...")
            
            # Teste 1: Adapter
            assert self.adapter is not None, "Adapter nao inicializado"
            logging.info("  [OK] Adapter inicializado")
            
            # Teste 2: Capital
            assert self.allocated_capital == Decimal('75000'), f"Capital incorreto"
            logging.info(f"  [OK] Capital: €{self.allocated_capital}")
            
            # Teste 3: Limites
            assert self.max_positions > 0 and self.max_daily_trades > 0, "Limites invalidos"
            logging.info(f"  [OK] Limites: Pos={self.max_positions}, Trades={self.max_daily_trades}")
            
            # Teste 4: Validar adapter
            adapter_ok = self.adapter.validate_adapter()
            assert adapter_ok, "Falha no adapter"
            logging.info("  [OK] Adapter validado")
            
            logging.info("[FuturesModule] Validacao - SUCESSO")
            return True
        
        except Exception as e:
            logging.error(f"[FuturesModule] Falha: {e}")
            return False


# Teste standalone
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("VALIDACAO - FUTURES MODULE NUMEIA v3.0")
    print("="*80 + "\n")
    
    futures_module = FuturesModule(
        allocated_capital=Decimal('75000'),
        max_positions=3,
        max_daily_trades=8
    )
    
    if futures_module.validate_module():
        print("\n[SUCCESS] Futures Module validado!")
        
        status = futures_module.get_module_status()
        print("\nSTATUS DO MODULO:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    else:
        print("\n[FAILED] Falha na validacao")

