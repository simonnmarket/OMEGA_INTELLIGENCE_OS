# -*- coding: utf-8 -*-
"""
================================================================================
DIRETIVA NUMEIA v4.1 - MISSÃO 2: GOLD MACRO INFLECTION
================================================================================

HIPÓTESE PRÉ-REGISTRADA:
"Estratégia de Long em Ouro quando a média móvel de 90 dias da Taxa de Juros
Real (10Y Treasury - Breakeven Inflation) está abaixo de 0% possui edge
explorável no período 2018-2023."

PERÍODO: 2018-01-01 a 2023-12-31 (IMUTÁVEL)
CAPITAL: EUR 30,000
CUSTOS: 5 bps por transação
TICKER GOLD: GLD (SPDR Gold Shares ETF)
TICKER MACRO: DGS10 (10Y Treasury), T10YIE (10Y Breakeven Inflation) - FRED

LÓGICA:
  Real_Rate = DGS10 - T10YIE
  MA_Real_Rate = MA(Real_Rate, 90 dias)
  
  LONG Gold: quando MA_Real_Rate < 0.0%
  CASH:      quando MA_Real_Rate >= 0.0%

CRITÉRIOS DE SUCESSO:
  - Sharpe Ratio > 0.50
  - p-value < 0.05 (binomial test para Win Rate)
  - Max Drawdown < 20%
  - Performance positiva em 2/3 regimes

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
from scipy.stats import binomtest

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Adicionar path para importar RobustYFinance
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from Core.Backtesting.yfinance_robust import RobustYFinance

# Importar FRED API
try:
    from fredapi import Fred
except ImportError:
    logging.error("fredapi não instalado. Execute: pip install fredapi")
    sys.exit(1)


class GoldMacroInflectionStrategy:
    """
    Estratégia Gold Macro Inflection baseada em Juros Reais.
    
    Operação:
    1. Calcular Taxa de Juros Real = DGS10 - T10YIE
    2. Calcular MA(90 dias) da Taxa de Juros Real
    3. LONG Gold quando MA_Real_Rate < 0%
    4. CASH quando MA_Real_Rate >= 0%
    5. Aplicar custos de transação (5 bps) em cada mudança de posição
    """
    
    def __init__(self, config):
        self.ticker_gold = config['TICKER']
        self.ticker_nominal = config['TICKER_JUROS_NOMINAL']
        self.ticker_inflacao = config['TICKER_INFLACAO']
        self.ma_period = config['PERIODO_MEDIA_JUROS_REAL']
        self.threshold = config['LIMIAR_JUROS_REAL']
        self.capital_inicial = config['CAPITAL_INICIAL_EUR']
        self.transaction_cost_bps = config['CUSTO_TRANSACAO_BPS']
        self.data_inicio = config['DATA_INICIO']
        self.data_fim = config['DATA_FIM']
        self.fred_api_key = config['FRED_API_KEY']
        
        self.data_gold = None
        self.data_macro = None
        self.data_merged = None
        self.results = {}
        self.trades = []
        
        logging.info(f"[MISSÃO 2] Inicializado: {self.ticker_gold}")
        logging.info(f"[MISSÃO 2] Macro: {self.ticker_nominal}, {self.ticker_inflacao}")
        logging.info(f"[MISSÃO 2] Período MA: {self.ma_period} dias")
        logging.info(f"[MISSÃO 2] Threshold: {self.threshold}%")
        logging.info(f"[MISSÃO 2] Período: {self.data_inicio} a {self.data_fim}")
    
    def fetch_gold_data(self):
        """Coletar dados históricos do GLD."""
        logging.info(f"[MISSÃO 2] Coletando dados para {self.ticker_gold}...")
        
        try:
            robust_yf = RobustYFinance(max_retries=5, backoff_factor=2.0, delay_between_requests=1.5)
            self.data_gold = robust_yf.download(
                ticker=self.ticker_gold,
                start=self.data_inicio,
                end=self.data_fim,
                progress=False
            )
            
            if self.data_gold.empty:
                raise ValueError(f"Dados vazios para {self.ticker_gold}")
            
            # Handle MultiIndex columns
            if isinstance(self.data_gold.columns, pd.MultiIndex):
                self.data_gold.columns = self.data_gold.columns.get_level_values(0)
            
            logging.info(f"[MISSÃO 2] ✅ GLD: {len(self.data_gold)} dias coletados")
            return True
            
        except Exception as e:
            logging.error(f"[MISSÃO 2] ❌ Erro ao coletar dados GLD: {e}")
            return False
    
    def fetch_macro_data(self):
        """Coletar dados macro (DGS10, T10YIE) do FRED."""
        logging.info(f"[MISSÃO 2] Coletando dados macro do FRED...")
        
        try:
            fred = Fred(api_key=self.fred_api_key)
            
            # DGS10: 10-Year Treasury Constant Maturity Rate
            dgs10 = fred.get_series(self.ticker_nominal, observation_start=self.data_inicio, observation_end=self.data_fim)
            logging.info(f"[MISSÃO 2] ✅ DGS10: {len(dgs10)} pontos coletados")
            
            # T10YIE: 10-Year Breakeven Inflation Rate
            t10yie = fred.get_series(self.ticker_inflacao, observation_start=self.data_inicio, observation_end=self.data_fim)
            logging.info(f"[MISSÃO 2] ✅ T10YIE: {len(t10yie)} pontos coletados")
            
            # Combinar em DataFrame
            self.data_macro = pd.DataFrame({
                'DGS10': dgs10,
                'T10YIE': t10yie
            })
            
            # Forward fill para dias sem dados (finais de semana/feriados)
            self.data_macro = self.data_macro.fillna(method='ffill')
            
            logging.info(f"[MISSÃO 2] ✅ Dados macro combinados: {len(self.data_macro)} dias")
            return True
            
        except Exception as e:
            logging.error(f"[MISSÃO 2] ❌ Erro ao coletar dados FRED: {e}")
            return False
    
    def merge_and_calculate(self):
        """Merge dados de Gold + Macro e calcular Real Rates + Sinais."""
        logging.info("[MISSÃO 2] Merging dados e calculando sinais...")
        
        try:
            # Merge Gold e Macro por data
            self.data_merged = pd.merge(
                self.data_gold[['Close']].rename(columns={'Close': 'Gold_Close'}),
                self.data_macro,
                left_index=True,
                right_index=True,
                how='inner'
            )
            
            logging.info(f"[MISSÃO 2] Dados alinhados: {len(self.data_merged)} dias")
            
            # Calcular Real Rate
            self.data_merged['Real_Rate'] = self.data_merged['DGS10'] - self.data_merged['T10YIE']
            
            # Calcular MA(Real Rate)
            self.data_merged['MA_Real_Rate'] = self.data_merged['Real_Rate'].rolling(
                window=self.ma_period,
                min_periods=self.ma_period
            ).mean()
            
            # Gerar Sinais
            self.data_merged['Signal'] = 'CASH'
            self.data_merged.loc[self.data_merged['MA_Real_Rate'] < self.threshold, 'Signal'] = 'LONG'
            
            # Detectar mudanças de posição (para custos de transação)
            self.data_merged['Position_Change'] = self.data_merged['Signal'] != self.data_merged['Signal'].shift(1)
            
            # Remover NaN do início (devido a MA)
            self.data_merged = self.data_merged.dropna()
            
            logging.info(f"[MISSÃO 2] ✅ Sinais calculados: {len(self.data_merged)} dias válidos")
            
            # Log de estatísticas dos sinais
            num_long = (self.data_merged['Signal'] == 'LONG').sum()
            num_cash = (self.data_merged['Signal'] == 'CASH').sum()
            num_changes = self.data_merged['Position_Change'].sum()
            
            logging.info(f"[MISSÃO 2] Dias LONG: {num_long} ({num_long/len(self.data_merged)*100:.1f}%)")
            logging.info(f"[MISSÃO 2] Dias CASH: {num_cash} ({num_cash/len(self.data_merged)*100:.1f}%)")
            logging.info(f"[MISSÃO 2] Mudanças de posição: {num_changes}")
            
            return True
            
        except Exception as e:
            logging.error(f"[MISSÃO 2] ❌ Erro ao processar dados: {e}")
            return False
    
    def execute_backtest(self):
        """Executar backtest da estratégia Gold Macro."""
        
        if self.data_merged is None or self.data_merged.empty:
            logging.error("[MISSÃO 2] Dados não disponíveis. Execute merge_and_calculate() primeiro.")
            return False
        
        logging.info("[MISSÃO 2] Executando backtest Gold Macro...")
        
        capital = self.capital_inicial
        position = 'CASH'
        shares = 0.0
        equity_curve = []
        self.trades = []
        
        for i, (date, row) in enumerate(self.data_merged.iterrows()):
            
            # Detectar mudança de posição
            if row['Position_Change']:
                # Se estava LONG, vender
                if position == 'LONG' and shares > 0:
                    sell_price = row['Gold_Close']
                    capital = shares * sell_price
                    cost = capital * (self.transaction_cost_bps / 10000)
                    capital -= cost
                    
                    self.trades.append({
                        'date': date,
                        'action': 'SELL',
                        'price': sell_price,
                        'shares': shares,
                        'cost': cost,
                        'capital': capital
                    })
                    
                    shares = 0.0
                
                # Se novo sinal é LONG, comprar
                if row['Signal'] == 'LONG':
                    buy_price = row['Gold_Close']
                    cost = capital * (self.transaction_cost_bps / 10000)
                    capital -= cost
                    shares = capital / buy_price
                    
                    self.trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': buy_price,
                        'shares': shares,
                        'cost': cost,
                        'capital': capital
                    })
                
                position = row['Signal']
            
            # Atualizar capital baseado em posição atual
            if position == 'LONG' and shares > 0:
                current_value = shares * row['Gold_Close']
                equity_curve.append(current_value)
            else:
                equity_curve.append(capital)
        
        # Se terminou LONG, fechar posição
        if position == 'LONG' and shares > 0:
            final_price = self.data_merged['Gold_Close'].iloc[-1]
            capital = shares * final_price
            cost = capital * (self.transaction_cost_bps / 10000)
            capital -= cost
            
            self.trades.append({
                'date': self.data_merged.index[-1],
                'action': 'SELL_FINAL',
                'price': final_price,
                'shares': shares,
                'cost': cost,
                'capital': capital
            })
        
        # Criar DataFrame de equity
        equity_df = pd.DataFrame({
            'Equity': equity_curve
        }, index=self.data_merged.index)
        
        # Calcular métricas
        self.results = self.calculate_metrics(equity_df, capital)
        
        logging.info("[MISSÃO 2] ✅ Backtest concluído")
        logging.info(f"[MISSÃO 2] Retorno Total: {self.results['retorno_total_pct']:.2f}%")
        logging.info(f"[MISSÃO 2] Sharpe Ratio: {self.results['sharpe_ratio']:.3f}")
        logging.info(f"[MISSÃO 2] Max Drawdown: {self.results['max_drawdown_pct']:.2f}%")
        logging.info(f"[MISSÃO 2] Num Trades: {self.results['num_trades']}")
        logging.info(f"[MISSÃO 2] Win Rate: {self.results['win_rate']*100:.2f}%")
        logging.info(f"[MISSÃO 2] p-value: {self.results['p_value']:.4f}")
        
        return True
    
    def calculate_metrics(self, equity_df, capital_final):
        """Calcular métricas de performance."""
        
        # Retorno total
        retorno_total = (capital_final - self.capital_inicial) / self.capital_inicial
        
        # Retornos diários
        daily_returns = equity_df['Equity'].pct_change().dropna()
        
        # Sharpe Ratio (anualizado, assumindo risk-free = 2%)
        risk_free_rate = 0.02
        retornos_excesso = daily_returns - (risk_free_rate / 252)
        
        if retornos_excesso.std() == 0:
            sharpe = 0.0
        else:
            sharpe = np.sqrt(252) * retornos_excesso.mean() / retornos_excesso.std()
        
        # Max Drawdown
        pico = equity_df['Equity'].expanding(min_periods=1).max()
        drawdown = (equity_df['Equity'] - pico) / pico
        max_dd = drawdown.min()
        
        # Retorno anualizado
        num_anos = len(equity_df) / 252
        retorno_anualizado = (1 + retorno_total) ** (1 / num_anos) - 1
        
        # Volatilidade anualizada
        volatilidade = daily_returns.std() * np.sqrt(252)
        
        # Análise de Trades
        num_trades = len([t for t in self.trades if t['action'] in ['BUY', 'SELL', 'SELL_FINAL']])
        
        # Calcular P&L de cada par buy-sell
        buy_trades = [t for t in self.trades if t['action'] == 'BUY']
        sell_trades = [t for t in self.trades if t['action'] in ['SELL', 'SELL_FINAL']]
        
        winning_trades = 0
        losing_trades = 0
        
        for buy, sell in zip(buy_trades, sell_trades):
            pnl = (sell['price'] - buy['price']) / buy['price']
            if pnl > 0.001:  # > 0.1% para evitar empate
                winning_trades += 1
            elif pnl < -0.001:
                losing_trades += 1
        
        total_pairs = winning_trades + losing_trades
        win_rate = winning_trades / total_pairs if total_pairs > 0 else 0.5
        
        # Binomial Test
        if total_pairs > 0:
            p_value = binomtest(winning_trades, total_pairs, 0.5, alternative='greater').pvalue
        else:
            p_value = 1.0
        
        return {
            'retorno_total_pct': retorno_total * 100,
            'retorno_anualizado_pct': retorno_anualizado * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_dd * 100,
            'volatilidade_anualizada_pct': volatilidade * 100,
            'capital_final_eur': capital_final,
            'num_dias': len(equity_df),
            'num_trades': num_trades,
            'num_trade_pairs': total_pairs,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'p_value': p_value
        }
    
    def get_results(self):
        """Retornar resultados do backtest."""
        return self.results


def main():
    """Função principal para executar MISSÃO 2."""
    
    # Carregar API Key do FRED
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    with open(config_path, 'r') as f:
        config_file = json.load(f)
    
    # Configuração (IMUTÁVEL - PRÉ-REGISTRADA)
    CONFIG = {
        'TICKER': 'GLD',
        'TICKER_JUROS_NOMINAL': 'DGS10',
        'TICKER_INFLACAO': 'T10YIE',
        'PERIODO_MEDIA_JUROS_REAL': 90,
        'LIMIAR_JUROS_REAL': 0.0,
        'DATA_INICIO': '2018-01-01',
        'DATA_FIM': '2023-12-31',
        'CAPITAL_INICIAL_EUR': 30000.0,
        'CUSTO_TRANSACAO_BPS': 5.0,
        'FRED_API_KEY': config_file['FRED_API_KEY']
    }
    
    logging.info("="*80)
    logging.info("DIRETIVA NUMEIA v4.1 - MISSÃO 2: GOLD MACRO INFLECTION")
    logging.info("="*80)
    
    # Instanciar estratégia
    strategy = GoldMacroInflectionStrategy(CONFIG)
    
    # Coletar dados Gold
    if not strategy.fetch_gold_data():
        logging.error("[MISSÃO 2] FALHA na coleta de dados Gold. Abortando.")
        return None
    
    # Coletar dados Macro
    if not strategy.fetch_macro_data():
        logging.error("[MISSÃO 2] FALHA na coleta de dados Macro. Abortando.")
        return None
    
    # Merge e calcular sinais
    if not strategy.merge_and_calculate():
        logging.error("[MISSÃO 2] FALHA no processamento de dados. Abortando.")
        return None
    
    # Executar backtest
    if not strategy.execute_backtest():
        logging.error("[MISSÃO 2] FALHA na execução do backtest. Abortando.")
        return None
    
    # Retornar resultados
    results = strategy.get_results()
    
    logging.info("="*80)
    logging.info("MISSÃO 2 CONCLUÍDA COM SUCESSO")
    logging.info("="*80)
    
    return {
        'status': 'OK',
        'resultados': results,
        'config': CONFIG
    }


if __name__ == '__main__':
    resultado = main()
    if resultado:
        print("\n[MISSÃO 2] RESULTADOS:")
        print(json.dumps(resultado['resultados'], indent=2, ensure_ascii=False))

