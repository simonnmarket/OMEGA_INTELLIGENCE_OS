# GoldModule_Numeia_v3_0.py
"""
MODULO GOLD PARA NUMEIA TRADING SYSTEM v3.0
FASE 3 - INTEGRACAO COMPLETA
DATA: 01-11-2025 21:10 CET
APROVACAO: CONSELHO (DISTINCAO MAXIMA)

FUNCIONALIDADE:
- Interface padrao do modulo Gold para o NumeiaTradingSystem
- Gerenciamento de risco consolidado
- Integracao com 5 engines Numeia
- Retorno padrao: Lista de TradingSignalPerfeito

COMPLIANCE: PROTOCOLO BLINDADO 100%
CAPITAL APROVADO: €75,000 (7.5% do total)
ESTRATEGIAS: 1 (Gold Macro Inflection)
"""

import sys
from pathlib import Path

# Adicionar pasta Strategies/Gold ao path
gold_path = Path(__file__).parent.parent / 'Strategies' / 'Gold'
sys.path.insert(0, str(gold_path))

from decimal import Decimal
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Import adapter Gold
from GoldStrategyAdapter_Numeia import GoldStrategyAdapter, TradingSignalPerfeito

class GoldModule:
    """
    Modulo Gold para NumeiaTradingSystem v3.0
    
    Interface padrao: analyze() -> List[TradingSignalPerfeito]
    """
    
    def __init__(self,
                 allocated_capital: Decimal = Decimal('75000'),
                 max_positions: int = 2,
                 max_daily_trades: int = 5):
        """
        Initialize Gold Module
        
        Args:
            allocated_capital: Capital alocado (aprovado: €75k)
            max_positions: Maximo de posicoes simultaneas
            max_daily_trades: Maximo de trades por dia
        """
        self.allocated_capital = allocated_capital
        self.max_positions = max_positions
        self.max_daily_trades = max_daily_trades
        
        # Inicializar adapter
        self.adapter = GoldStrategyAdapter(allocated_capital=allocated_capital)
        
        # Controles de risco
        self.current_positions = 0
        self.daily_trades = 0
        self.last_trade_date = None
        
        # Estatisticas
        self.total_signals_generated = 0
        self.total_signals_filtered = 0
        
        logging.info(f"[GoldModule] Inicializado")
        logging.info(f"  -> Capital: €{self.allocated_capital}")
        logging.info(f"  -> Max Positions: {self.max_positions}")
        logging.info(f"  -> Max Daily Trades: {self.max_daily_trades}")
        logging.info(f"  -> Estrategias ativas: 1 (Gold Macro Inflection)")
    
    def analyze(self,
                hale_engine,
                rossi_engine,
                tanaka_engine,
                leblanc_engine,
                market_masters_engine,
                use_real_data: bool = True) -> List[TradingSignalPerfeito]:
        """
        Interface padrao para NumeiaTradingSystem
        
        Analisa mercado de ouro e retorna sinais formatados
        
        Args:
            hale_engine: Engine Hale (Intentionality)
            rossi_engine: Engine Rossi (Kelly)
            tanaka_engine: Engine Tanaka (Kalman)
            leblanc_engine: Engine Leblanc (ZKP)
            market_masters_engine: Engine MarketMasters (Validation)
            use_real_data: Se True, usa yfinance + FRED API
        
        Returns:
            Lista de TradingSignalPerfeito
        """
        
        # Reset contador diario se novo dia
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
        
        # Gerar sinais via adapter
        signals = self.adapter.generate_all_gold_signals(
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
                logging.warning(f"[GoldModule] Limite de posicoes atingido: {self.current_positions}/{self.max_positions}")
                self.total_signals_filtered += 1
                continue
            
            # Filtro 2: Limite de trades diarios
            if self.daily_trades >= self.max_daily_trades:
                logging.warning(f"[GoldModule] Limite de trades diarios atingido: {self.daily_trades}/{self.max_daily_trades}")
                self.total_signals_filtered += 1
                continue
            
            # Filtro 3: Validacao MarketMasters
            if not signal.market_masters_validation:
                logging.warning(f"[GoldModule] Sinal falhou validacao MarketMasters")
                self.total_signals_filtered += 1
                continue
            
            # Filtro 4: Confidence minima
            if signal.confidence < 0.10:
                logging.warning(f"[GoldModule] Confidence muito baixa: {signal.confidence:.2f} < 0.10")
                self.total_signals_filtered += 1
                continue
            
            # Sinal aprovado
            filtered_signals.append(signal)
            
            # Atualizar contadores (simulado - em producao atualizar apos execucao)
            if signal.action in ['BUY', 'SELL']:
                self.daily_trades += 1
        
        logging.info(f"[GoldModule] Sinais gerados: {len(signals)} | Aprovados: {len(filtered_signals)} | Filtrados: {len(signals) - len(filtered_signals)}")
        
        return filtered_signals
    
    def get_module_status(self) -> Dict:
        """
        Retorna status atual do modulo
        
        Returns:
            Dicionario com metricas do modulo
        """
        return {
            'module': 'Gold',
            'version': '3.0',
            'allocated_capital': float(self.allocated_capital),
            'strategies': 1,
            'strategy_names': ['Gold Macro Inflection'],
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
            True se modulo esta OK
        """
        try:
            logging.info("[GoldModule] Iniciando validacao...")
            
            # Teste 1: Adapter inicializado
            assert self.adapter is not None, "Adapter nao inicializado"
            logging.info("  [OK] Adapter Gold inicializado")
            
            # Teste 2: Capital correto
            assert self.allocated_capital == Decimal('75000'), f"Capital incorreto: {self.allocated_capital}"
            logging.info(f"  [OK] Capital alocado: €{self.allocated_capital}")
            
            # Teste 3: Limites configurados
            assert self.max_positions > 0, "Max positions invalido"
            assert self.max_daily_trades > 0, "Max daily trades invalido"
            logging.info(f"  [OK] Limites: Positions={self.max_positions}, DailyTrades={self.max_daily_trades}")
            
            # Teste 4: Validar adapter
            adapter_ok = self.adapter.validate_adapter()
            assert adapter_ok, "Falha na validacao do adapter"
            logging.info("  [OK] Adapter validado com sucesso")
            
            logging.info("[GoldModule] Validacao completa - SUCESSO")
            return True
        
        except Exception as e:
            logging.error(f"[GoldModule] Falha na validacao: {e}")
            return False


# Teste standalone
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("VALIDACAO - GOLD MODULE NUMEIA v3.0")
    print("="*80 + "\n")
    
    # Criar modulo
    gold_module = GoldModule(
        allocated_capital=Decimal('75000'),
        max_positions=2,
        max_daily_trades=5
    )
    
    # Validar
    if gold_module.validate_module():
        print("\n[SUCCESS] Gold Module validado com sucesso!")
        
        # Mostrar status
        status = gold_module.get_module_status()
        print("\nSTATUS DO MODULO:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    else:
        print("\n[FAILED] Falha na validacao do modulo")

