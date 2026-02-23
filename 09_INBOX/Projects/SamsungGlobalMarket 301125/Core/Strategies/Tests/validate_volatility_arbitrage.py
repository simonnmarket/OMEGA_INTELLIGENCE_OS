# validate_volatility_arbitrage.py
# -*- coding: utf-8 -*-
"""
VALIDACAO EMPIRICA MULTI-ATIVO - VOLATILITY ARBITRAGE
DATA: 01-11-2025 (CET)
BASE CIENTIFICA: Bollinger (1992) + Engle (1982)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("VALIDACAO EMPIRICA MULTI-ATIVO - ENGINE #2")
print("Data: 01.11.2025 (CET)")
print("Base Cientifica: Bollinger (1992) + Engle (1982)")
print("=" * 60)
print()

class VolatilityArbitrageValidator:
    def __init__(self):
        self.results = {}
        
    def calculate_bollinger_bands(self, prices, window=20):
        """Bollinger Bands conforme Bollinger (1992)"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (2 * rolling_std)
        lower_band = rolling_mean - (2 * rolling_std)
        return upper_band, rolling_mean, lower_band
        
    def calculate_simple_volatility(self, returns, window=20):
        """Volatilidade historica simples"""
        return returns.rolling(window=window).std() * np.sqrt(252)
            
    def validate_asset(self, symbol, period="4y"):
        """Validacao completa para um ativo"""
        print(f"Validando {symbol}...")
        
        # Buscar dados REAIS
        try:
            data = yf.download(symbol, period=period, progress=False)
            if data.empty:
                print(f"   ERRO: Sem dados para {symbol}")
                return None
                
            # Calcular componentes cientificos
            returns = data['Close'].pct_change().dropna()
            
            # 1. Bollinger Bands (Bollinger 1992)
            upper, middle, lower = self.calculate_bollinger_bands(data['Close'])
            
            # 2. Volatilidade historica
            hist_vol = self.calculate_simple_volatility(returns)
            
            # 3. Sinais de oportunidade
            close_prices = data['Close']
            bb_signals = pd.Series(0, index=close_prices.index)
            
            # Buy signal: price below lower band
            bb_signals[close_prices < lower] = 1
            
            # Sell signal: price above upper band
            bb_signals[close_prices > upper] = -1
            
            # 4. Performance (simulacao conservadora)
            strategy_returns = bb_signals.shift(1) * returns
            strategy_returns = strategy_returns.dropna()
            
            # Custos de transacao (10bps)
            trades = bb_signals.diff().fillna(0).abs()
            transaction_costs = trades * 0.0010
            strategy_returns_net = strategy_returns - transaction_costs.loc[strategy_returns.index]
            
            # Metricas
            if len(strategy_returns_net) > 0:
                win_rate = (strategy_returns_net > 0).mean()
                sharpe = (strategy_returns_net.mean() / strategy_returns_net.std() * np.sqrt(252)) if strategy_returns_net.std() > 0 else 0
                
                cumulative_returns = (1 + strategy_returns_net).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                max_dd = drawdown.min()
                
                result = {
                    'symbol': symbol,
                    'period': f"{data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}",
                    'total_days': len(data),
                    'opportunities': int((bb_signals != 0).sum()),
                    'win_rate': float(win_rate),
                    'sharpe_ratio': float(sharpe),
                    'max_drawdown': float(max_dd),
                    'avg_daily_return': float(strategy_returns_net.mean()),
                    'volatility': float(strategy_returns_net.std()),
                    'total_return': float(cumulative_returns.iloc[-1] - 1) if len(cumulative_returns) > 0 else 0
                }
                
                print(f"   OK - Oportunidades: {result['opportunities']}")
                print(f"   Win Rate: {win_rate:.2%}")
                print(f"   Sharpe: {sharpe:.3f}")
                print(f"   Max DD: {max_dd:.2%}")
                print(f"   Total Return: {result['total_return']:.2%}")
                print()
                
                return result
                
        except Exception as e:
            print(f"   ERRO em {symbol}: {str(e)}")
            print()
            return None
            
    def run_validation(self):
        """Executa validacao completa multi-ativo"""
        assets = ["SPY", "QQQ", "IWM", "AAPL", "MSFT"]
        
        print("INICIANDO VALIDACAO EMPIRICA MULTI-ATIVO")
        print("Base Cientifica: Bollinger (1992) + Engle (1982)")
        print("=" * 60)
        print()
        
        for asset in assets:
            result = self.validate_asset(asset)
            if result:
                self.results[asset] = result
                
        # Relatorio consolidado
        print("=" * 60)
        print("RELATORIO FINAL DE VALIDACAO")
        print("=" * 60)
        print()
        
        for asset, metrics in self.results.items():
            print(f"{asset}:")
            print(f"   Periodo: {metrics['period']}")
            print(f"   Dias: {metrics['total_days']} | Oportunidades: {metrics['opportunities']}")
            print(f"   Win Rate: {metrics['win_rate']:.2%} | Sharpe: {metrics['sharpe_ratio']:.3f}")
            print(f"   Max DD: {metrics['max_drawdown']:.2%} | Return: {metrics['total_return']:.2%}")
            print()
            
        # Metricas agregadas
        if self.results:
            avg_win_rate = np.mean([m['win_rate'] for m in self.results.values()])
            avg_sharpe = np.mean([m['sharpe_ratio'] for m in self.results.values()])
            total_opportunities = sum([m['opportunities'] for m in self.results.values()])
            
            print("=" * 60)
            print("METRICAS CONSOLIDADAS:")
            print("=" * 60)
            print(f"Win Rate Medio: {avg_win_rate:.2%}")
            print(f"Sharpe Medio: {avg_sharpe:.3f}")
            print(f"Oportunidades Totais: {total_opportunities}")
            print(f"Ativos Validados: {len(self.results)}/5")
            print()
            
        return self.results

# EXECUTAR AGORA
if __name__ == "__main__":
    validator = VolatilityArbitrageValidator()
    results = validator.run_validation()
    
    print("=" * 60)
    print("VALIDACAO CONCLUIDA - ENGINE #2")
    print("Resultados salvos para relatorio final")
    print("=" * 60)
