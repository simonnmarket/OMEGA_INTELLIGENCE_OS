# -*- coding: utf-8 -*-
"""
================================================================================
ESTRATÉGIA #1: MOMENTUM SCANNER MULTI-ASSET (AGRESSIVA)
================================================================================

FILOSOFIA: "Agressão ao Mercado - Testar TUDO"
OBJETIVO: Capturar momentum nos 120+ ativos Hantec
TIMEFRAME: Swing (2-7 dias)
RISCO: Alto (é demo, podemos testar limites)
PROTOCOLO: Experimento de Refutação Rápida

HIPÓTESE:
"Ativos com momentum positivo (3M, 6M) tendem a continuar subindo no curto prazo"

CRITÉRIOS DE REFUTAÇÃO:
- Sharpe < 0.3 em backtest → DESCARTAR
- Win Rate < 50% → DESCARTAR
- Max DD > 30% → DESCARTAR

SE PASSAR: Deploy em demo IMEDIATO
SE FALHAR: Cemitério de Hipóteses

================================================================================
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

class MomentumScannerAggressive:
    """
    Scanner de momentum agressivo para múltiplos ativos.
    
    LÓGICA:
    1. Calcular momentum 3M e 6M para todos os ativos
    2. Ranquear ativos por momentum
    3. Long nos top 10
    4. SL: -3%, TP: +8%
    5. Hold: Até SL/TP ou novo scan (diário)
    """
    
    def __init__(self, universo_ativos):
        self.universo = universo_ativos
        self.lookback_3m = 63  # ~3 meses trading days
        self.lookback_6m = 126
        self.top_n = 10
        self.stop_loss = 0.03  # -3%
        self.take_profit = 0.08  # +8%
        
        logging.info("="*80)
        logging.info("MOMENTUM SCANNER AGRESSIVO")
        logging.info(f"Universo: {len(self.universo)} ativos")
        logging.info(f"Top N: {self.top_n}")
        logging.info(f"SL: -{self.stop_loss*100}% | TP: +{self.take_profit*100}%")
        logging.info("="*80)
    
    def calculate_momentum(self, prices):
        """Calcular momentum 3M e 6M."""
        if len(prices) < self.lookback_6m:
            return None, None
        
        # Momentum = (Preço atual - Preço passado) / Preço passado
        mom_3m = (prices.iloc[-1] - prices.iloc[-self.lookback_3m]) / prices.iloc[-self.lookback_3m]
        mom_6m = (prices.iloc[-1] - prices.iloc[-self.lookback_6m]) / prices.iloc[-self.lookback_6m]
        
        return mom_3m, mom_6m
    
    def scan_universe(self, data_dict):
        """
        Scannear todos os ativos e ranquear por momentum.
        
        data_dict: {symbol: DataFrame com 'Close'}
        """
        momentum_scores = []
        
        for symbol, data in data_dict.items():
            if data is None or data.empty:
                continue
            
            mom_3m, mom_6m = self.calculate_momentum(data['Close'])
            
            if mom_3m is None or mom_6m is None:
                continue
            
            # Score composto: 60% peso em 3M, 40% em 6M
            score = float(0.6 * mom_3m + 0.4 * mom_6m)
            
            momentum_scores.append({
                'symbol': str(symbol),
                'momentum_3m': float(mom_3m),
                'momentum_6m': float(mom_6m),
                'score': score,
                'price': float(data['Close'].iloc[-1])
            })
        
        # Ranquear por score
        if len(momentum_scores) == 0:
            return pd.DataFrame()
        
        # Criar DataFrame sem índices problemáticos
        momentum_df = pd.DataFrame(momentum_scores)
        
        # Sort usando numpy para evitar erro de pandas
        scores_array = momentum_df['score'].values
        sorted_indices = np.argsort(scores_array)[::-1]  # Descendente
        momentum_df = momentum_df.iloc[sorted_indices].reset_index(drop=True)
        
        return momentum_df
    
    def generate_signals(self, momentum_df):
        """Gerar sinais para os top N ativos."""
        
        top_assets = momentum_df.head(self.top_n)
        
        signals = []
        
        for idx, row in top_assets.iterrows():
            signal = {
                'symbol': row['symbol'],
                'action': 'BUY',
                'entry_price': row['price'],
                'stop_loss': row['price'] * (1 - self.stop_loss),
                'take_profit': row['price'] * (1 + self.take_profit),
                'momentum_3m': row['momentum_3m'],
                'momentum_6m': row['momentum_6m'],
                'score': row['score'],
                'confidence': min(abs(row['score']) * 2, 0.95),
                'reason': f"Momentum 3M: {row['momentum_3m']*100:.1f}%, 6M: {row['momentum_6m']*100:.1f}%"
            }
            
            signals.append(signal)
        
        return signals


def test_momentum_strategy():
    """Teste rápido da estratégia."""
    
    # Universo de teste (amostra dos 120+ Hantec)
    test_universe = [
        'SPY', 'QQQ', 'GLD', 'SLV',  # ETFs
        'AAPL', 'MSFT', 'NVDA', 'TSLA',  # Tech
        'JPM', 'BAC', 'GS',  # Financials
        'XOM', 'CVX'  # Energy
    ]
    
    logging.info("\n[TEST] Baixando dados de teste...")
    
    # Baixar dados (6 meses)
    data_dict = {}
    for symbol in test_universe:
        try:
            data = yf.download(symbol, period='6mo', progress=False)
            if not data.empty:
                data_dict[symbol] = data
                logging.info(f"  ✅ {symbol}: {len(data)} dias")
        except:
            logging.warning(f"  ❌ {symbol}: Falhou")
    
    # Criar scanner
    scanner = MomentumScannerAggressive(test_universe)
    
    # Scannear
    logging.info("\n[SCAN] Calculando momentum...")
    momentum_df = scanner.scan_universe(data_dict)
    
    # Mostrar ranking
    logging.info("\n[RANKING] Top 10 por Momentum:")
    logging.info(momentum_df.head(10).to_string())
    
    # Gerar sinais
    signals = scanner.generate_signals(momentum_df)
    
    logging.info(f"\n[SIGNALS] {len(signals)} sinais gerados:")
    for sig in signals:
        logging.info(f"  {sig['symbol']}: {sig['action']} @ {sig['entry_price']:.2f}")
        logging.info(f"    SL: {sig['stop_loss']:.2f} | TP: {sig['take_profit']:.2f}")
        logging.info(f"    Momentum: {sig['momentum_3m']*100:.1f}%")
    
    return signals


if __name__ == '__main__':
    logging.info("="*80)
    logging.info("TESTE - MOMENTUM SCANNER AGRESSIVO")
    logging.info("Protocolo: Experimento de Refutação Rápida")
    logging.info("="*80)
    
    signals = test_momentum_strategy()
    
    logging.info("\n" + "="*80)
    logging.info(f"RESULTADO: {len(signals)} sinais prontos para deploy")
    logging.info("PRÓXIMO: Backtest 2018-2023 → SE Sharpe > 0.3 → DEPLOY DEMO")
    logging.info("="*80)

