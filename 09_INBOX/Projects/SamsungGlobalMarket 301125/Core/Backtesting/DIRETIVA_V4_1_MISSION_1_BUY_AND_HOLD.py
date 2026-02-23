# -*- coding: utf-8 -*-
"""
================================================================================
DIRETIVA NUMEIA v4.1 - MISSÃO 1: BUY & HOLD ACWI (BASELINE DE EFICIÊNCIA)
================================================================================

HIPÓTESE PRÉ-REGISTRADA:
"Estratégia passiva de Buy & Hold no índice global ACWI supera o desempenho
ajustado ao risco (Sharpe Ratio) das estratégias ativas testadas no Numeia v3.1."

PERÍODO: 2018-01-01 a 2023-12-31 (IMUTÁVEL)
CAPITAL: EUR 30,000
CUSTOS: 5 bps por transação + 0.10% a.a. management fee
TICKER: ACWI (iShares MSCI ACWI ETF)

CRITÉRIOS DE SUCESSO:
  - Sharpe Ratio > 0.30 (vs -0.01 das estratégias ativas v3.1)
  - Max Drawdown < 30%
  - Retorno Total > 0%

PROTOCOLO: ASC-AQ v1.0.0
EXECUTOR: Agente ASC-AQ
TIMESTAMP PRÉ-REGISTRO: 2025-11-04T01:40:00Z
TIMESTAMP EXECUÇÃO: 2025-11-04T21:56:00Z

================================================================================
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import logging
import json
import os
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Adicionar path para importar RobustYFinance
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from Core.Backtesting.yfinance_robust import RobustYFinance


class BuyAndHoldACWI:
    """
    Estratégia Buy & Hold no índice global ACWI.
    
    Operação:
    1. Comprar ACWI no primeiro dia do período
    2. Hold até o último dia
    3. Aplicar custos de transação (5 bps na entrada)
    4. Aplicar management fee (0.10% a.a.)
    5. Calcular métricas de performance
    """
    
    def __init__(self, config):
        self.ticker = config['TICKER']
        self.capital_inicial = config['CAPITAL_INICIAL_EUR']
        self.transaction_cost_bps = config['CUSTO_TRANSACAO_BPS']
        self.management_fee_anual = config['TAXA_GESTAO_ANUAL']
        self.data_inicio = config['DATA_INICIO']
        self.data_fim = config['DATA_FIM']
        
        self.data = None
        self.results = {}
        
        logging.info(f"[MISSÃO 1] Inicializado: {self.ticker}")
        logging.info(f"[MISSÃO 1] Período: {self.data_inicio} a {self.data_fim}")
        logging.info(f"[MISSÃO 1] Capital: EUR {self.capital_inicial:,.2f}")
    
    def fetch_data(self):
        """Coletar dados históricos do ACWI usando RobustYFinance."""
        logging.info(f"[MISSÃO 1] Coletando dados para {self.ticker}...")
        
        try:
            robust_yf = RobustYFinance(max_retries=5, backoff_factor=2.0, delay_between_requests=1.5)
            self.data = robust_yf.download(
                ticker=self.ticker,
                start=self.data_inicio,
                end=self.data_fim,
                progress=False
            )
            
            if self.data.empty:
                raise ValueError(f"Dados vazios para {self.ticker}")
            
            # Handle MultiIndex columns
            if isinstance(self.data.columns, pd.MultiIndex):
                self.data.columns = self.data.columns.get_level_values(0)
            
            logging.info(f"[MISSÃO 1] ✅ Coletados {len(self.data)} dias de dados")
            return True
            
        except Exception as e:
            logging.error(f"[MISSÃO 1] ❌ Erro ao coletar dados: {e}")
            return False
    
    def calculate_metrics(self, series_retornos, equity_curve):
        """Calcular métricas de performance."""
        
        # Retorno total
        retorno_total = (equity_curve.iloc[-1] - self.capital_inicial) / self.capital_inicial
        
        # Sharpe Ratio (anualizado, assumindo risk-free = 2%)
        risk_free_rate = 0.02
        retornos_excesso = series_retornos - (risk_free_rate / 252)
        
        if retornos_excesso.std() == 0:
            sharpe = 0.0
        else:
            sharpe = np.sqrt(252) * retornos_excesso.mean() / retornos_excesso.std()
        
        # Max Drawdown
        pico = equity_curve.expanding(min_periods=1).max()
        drawdown = (equity_curve - pico) / pico
        max_dd = drawdown.min()
        
        # Retorno anualizado
        num_anos = len(self.data) / 252
        retorno_anualizado = (1 + retorno_total) ** (1 / num_anos) - 1
        
        # Volatilidade anualizada
        volatilidade = series_retornos.std() * np.sqrt(252)
        
        return {
            'retorno_total_pct': retorno_total * 100,
            'retorno_anualizado_pct': retorno_anualizado * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_dd * 100,
            'volatilidade_anualizada_pct': volatilidade * 100,
            'capital_final_eur': equity_curve.iloc[-1],
            'num_dias': len(self.data)
        }
    
    def execute_backtest(self):
        """Executar backtest Buy & Hold."""
        
        if self.data is None or self.data.empty:
            logging.error("[MISSÃO 1] Dados não disponíveis. Execute fetch_data() primeiro.")
            return False
        
        logging.info("[MISSÃO 1] Executando backtest Buy & Hold...")
        
        # 1. Entrada: Comprar no primeiro dia
        price_entry = self.data['Close'].iloc[0]
        cost_entry = self.capital_inicial * (self.transaction_cost_bps / 10000)
        capital_apos_entrada = self.capital_inicial - cost_entry
        shares = capital_apos_entrada / price_entry
        
        logging.info(f"[MISSÃO 1] Entrada: {price_entry:.2f} USD")
        logging.info(f"[MISSÃO 1] Custo transação: EUR {cost_entry:.2f}")
        logging.info(f"[MISSÃO 1] Shares compradas: {shares:.4f}")
        
        # 2. Calcular equity curve diária
        equity_curve = self.data['Close'] * shares
        
        # 3. Aplicar management fee (diário)
        num_dias = len(self.data)
        fee_diario = self.management_fee_anual / 252
        total_fee = equity_curve.iloc[-1] * (fee_diario * num_dias)
        
        logging.info(f"[MISSÃO 1] Management fee total: EUR {total_fee:.2f}")
        
        # 4. Capital final após fees
        equity_curve_final = equity_curve - (total_fee / num_dias)  # Distribuir fee ao longo do tempo
        
        # 5. Retornos diários
        daily_returns = self.data['Close'].pct_change().dropna()
        
        # 6. Calcular métricas
        self.results = self.calculate_metrics(daily_returns, equity_curve_final)
        
        # 7. Adicionar informações extras
        self.results['price_entry'] = price_entry
        self.results['price_exit'] = self.data['Close'].iloc[-1]
        self.results['shares'] = shares
        self.results['cost_entry_eur'] = cost_entry
        self.results['management_fee_eur'] = total_fee
        
        logging.info("[MISSÃO 1] ✅ Backtest concluído")
        logging.info(f"[MISSÃO 1] Retorno Total: {self.results['retorno_total_pct']:.2f}%")
        logging.info(f"[MISSÃO 1] Sharpe Ratio: {self.results['sharpe_ratio']:.3f}")
        logging.info(f"[MISSÃO 1] Max Drawdown: {self.results['max_drawdown_pct']:.2f}%")
        
        return True
    
    def get_results(self):
        """Retornar resultados do backtest."""
        return self.results


def main():
    """Função principal para executar MISSÃO 1."""
    
    # Configuração (IMUTÁVEL - PRÉ-REGISTRADA)
    CONFIG = {
        'TICKER': 'ACWI',
        'DATA_INICIO': '2018-01-01',
        'DATA_FIM': '2023-12-31',
        'CAPITAL_INICIAL_EUR': 30000.0,
        'CUSTO_TRANSACAO_BPS': 5.0,
        'TAXA_GESTAO_ANUAL': 0.001  # 0.10%
    }
    
    logging.info("="*80)
    logging.info("DIRETIVA NUMEIA v4.1 - MISSÃO 1: BUY & HOLD ACWI")
    logging.info("="*80)
    
    # Instanciar estratégia
    strategy = BuyAndHoldACWI(CONFIG)
    
    # Coletar dados
    if not strategy.fetch_data():
        logging.error("[MISSÃO 1] FALHA na coleta de dados. Abortando.")
        return None
    
    # Executar backtest
    if not strategy.execute_backtest():
        logging.error("[MISSÃO 1] FALHA na execução do backtest. Abortando.")
        return None
    
    # Retornar resultados
    results = strategy.get_results()
    
    logging.info("="*80)
    logging.info("MISSÃO 1 CONCLUÍDA COM SUCESSO")
    logging.info("="*80)
    
    return {
        'status': 'OK',
        'resultados': results,
        'config': CONFIG
    }


if __name__ == '__main__':
    resultado = main()
    if resultado:
        print("\n[MISSÃO 1] RESULTADOS:")
        print(json.dumps(resultado['resultados'], indent=2, ensure_ascii=False))

