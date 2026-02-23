# -*- coding: utf-8 -*-
"""
================================================================================
BACKTEST CIENTÍFICO - MOMENTUM SCANNER v6.0
================================================================================

OBJETIVO: Validar estratégia Momentum Scanner antes de deploy
PERÍODO: 2022-2024 (2 anos - período recente e relevante)
PROTOCOLO: ASC-AQ - Experimento de Refutação

HIPÓTESE:
"Ativos com momentum positivo (3M, 6M) tendem a continuar subindo no curto prazo"

CRITÉRIOS DE APROVAÇÃO:
✅ Sharpe Ratio > 0.3
✅ Win Rate > 50%
✅ Max Drawdown < 30%
✅ Expectancy > 0

CRITÉRIOS DE REFUTAÇÃO:
❌ Sharpe < 0.3 → DESCARTAR estratégia
❌ Win Rate < 40% → DESCARTAR
❌ Max DD > 40% → DESCARTAR

================================================================================
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Setup paths
current_dir = Path(__file__).parent
core_dir = current_dir.parent
strategies_dir = core_dir / 'Strategies' / 'Tactical'

sys.path.insert(0, str(core_dir))
sys.path.insert(0, str(strategies_dir))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

from MomentumScanner_Aggressive import MomentumScannerAggressive

class MomentumBacktest:
    """
    Backtest rigoroso da estratégia Momentum Scanner.
    """
    
    def __init__(self, start_date='2022-01-01', end_date='2024-11-01'):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = 10000.0
        self.current_capital = self.initial_capital
        
        # Portfolio
        self.positions = {}  # {symbol: {'entry': price, 'sl': price, 'tp': price, 'size': lots}}
        self.trades = []
        
        # Universo de teste (representativo)
        self.universe = [
            'SPY', 'QQQ', 'IWM',  # US Indices ETFs
            'GLD', 'SLV', 'USO',  # Commodities
            'EFA', 'EEM',  # International
            'TLT', 'HYG',  # Bonds
            'XLF', 'XLE', 'XLK', 'XLV', 'XLI',  # Sectors
        ]
        
        logging.info("="*80)
        logging.info("BACKTEST MOMENTUM SCANNER v6.0")
        logging.info("="*80)
        logging.info(f"Período: {start_date} → {end_date}")
        logging.info(f"Capital Inicial: ${self.initial_capital:,.2f}")
        logging.info(f"Universo: {len(self.universe)} ativos")
        logging.info("="*80)
    
    def fetch_data(self):
        """Baixar dados históricos para todo o universo."""
        logging.info("\n📊 Baixando dados históricos...")
        
        data_dict = {}
        
        for symbol in self.universe:
            try:
                data = yf.download(
                    symbol,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False
                )
                
                if not data.empty:
                    data_dict[symbol] = data
                    logging.info(f"  ✅ {symbol}: {len(data)} dias")
                else:
                    logging.warning(f"  ⚠️ {symbol}: Sem dados")
                    
            except Exception as e:
                logging.warning(f"  ❌ {symbol}: {e}")
        
        logging.info(f"\n✅ Total: {len(data_dict)} ativos com dados")
        return data_dict
    
    def run_backtest(self, data_dict):
        """Executar backtest dia a dia."""
        logging.info("\n🔬 Iniciando backtest...")
        
        # Criar scanner
        scanner = MomentumScannerAggressive(self.universe)
        
        # Pegar todas as datas (usar SPY como referência)
        dates = data_dict['SPY'].index if 'SPY' in data_dict else list(data_dict.values())[0].index
        
        # Rebalance a cada 5 dias (semanal)
        rebalance_interval = 5
        days_since_rebalance = 0
        
        equity_curve = []
        
        for i, current_date in enumerate(dates):
            # Skip primeiros 126 dias (precisamos de 6 meses de histórico)
            if i < 126:
                equity_curve.append(self.current_capital)
                continue
            
            # 1. Atualizar posições existentes (check SL/TP)
            self._update_positions(data_dict, current_date)
            
            # 2. Rebalancear portfolio
            days_since_rebalance += 1
            
            if days_since_rebalance >= rebalance_interval:
                # Fechar todas as posições antigas
                self._close_all_positions(data_dict, current_date)
                
                # Criar subset de dados até current_date
                data_subset = self._create_data_subset(data_dict, current_date)
                
                # Gerar novos sinais
                momentum_df = scanner.scan_universe(data_subset)
                
                if not momentum_df.empty:
                    signals = scanner.generate_signals(momentum_df)
                    
                    # Abrir novas posições
                    self._open_positions(signals, data_dict, current_date)
                
                days_since_rebalance = 0
            
            # 3. Calcular equity atual
            equity = self._calculate_equity(data_dict, current_date)
            equity_curve.append(equity)
            
            # Log progresso a cada 50 dias
            if i % 50 == 0:
                logging.info(f"  Dia {i}/{len(dates)}: Equity = ${equity:,.2f} | Posições: {len(self.positions)}")
        
        # Fechar posições finais
        self._close_all_positions(data_dict, dates[-1])
        
        return equity_curve, dates
    
    def _create_data_subset(self, data_dict, current_date):
        """Criar subset de dados até current_date (evitar look-ahead bias)."""
        subset = {}
        for symbol, data in data_dict.items():
            subset[symbol] = data[data.index <= current_date]
        return subset
    
    def _open_positions(self, signals, data_dict, current_date):
        """Abrir posições baseadas nos sinais."""
        risk_per_trade = 0.02  # 2% por trade
        
        for signal in signals:
            symbol = signal['symbol']
            
            if symbol not in data_dict:
                continue
            
            # Pegar preço atual (close do dia)
            try:
                current_price = float(data_dict[symbol].loc[current_date, 'Close'])
            except:
                continue
            
            # Calcular posição size baseado no risco
            stop_loss = float(signal['stop_loss'])
            sl_distance = abs(current_price - stop_loss)
            
            if sl_distance == 0 or np.isnan(sl_distance):
                continue
            
            risk_amount = self.current_capital * risk_per_trade
            position_size = risk_amount / sl_distance
            position_value = position_size * current_price
            
            # Limitar posição a 10% do capital
            max_position = self.current_capital * 0.10
            if position_value > max_position:
                position_size = max_position / current_price
                position_value = position_size * current_price
            
            # Verificar se temos capital
            if position_value > self.current_capital:
                continue
            
            # Abrir posição
            self.positions[symbol] = {
                'entry': current_price,
                'sl': signal['stop_loss'],
                'tp': signal['take_profit'],
                'size': position_size,
                'entry_date': current_date,
                'action': signal['action']
            }
            
            self.current_capital -= position_value
    
    def _update_positions(self, data_dict, current_date):
        """Atualizar posições (verificar SL/TP)."""
        closed_symbols = []
        
        for symbol, pos in self.positions.items():
            if symbol not in data_dict:
                continue
            
            try:
                current_price = data_dict[symbol].loc[current_date, 'Close']
            except:
                continue
            
            # Check SL/TP (assumindo BUY)
            if pos['action'] == 'BUY':
                if current_price <= pos['sl']:
                    # Stop Loss hit
                    self._close_position(symbol, current_price, current_date, 'SL')
                    closed_symbols.append(symbol)
                elif current_price >= pos['tp']:
                    # Take Profit hit
                    self._close_position(symbol, current_price, current_date, 'TP')
                    closed_symbols.append(symbol)
            else:  # SELL
                if current_price >= pos['sl']:
                    self._close_position(symbol, current_price, current_date, 'SL')
                    closed_symbols.append(symbol)
                elif current_price <= pos['tp']:
                    self._close_position(symbol, current_price, current_date, 'TP')
                    closed_symbols.append(symbol)
        
        # Remover posições fechadas
        for symbol in closed_symbols:
            del self.positions[symbol]
    
    def _close_position(self, symbol, exit_price, exit_date, reason):
        """Fechar uma posição."""
        pos = self.positions[symbol]
        
        if pos['action'] == 'BUY':
            pnl = (exit_price - pos['entry']) * pos['size']
        else:  # SELL
            pnl = (pos['entry'] - exit_price) * pos['size']
        
        # Retornar capital + PnL
        position_value = exit_price * pos['size']
        self.current_capital += position_value
        
        # Registrar trade
        self.trades.append({
            'symbol': symbol,
            'entry_date': pos['entry_date'],
            'exit_date': exit_date,
            'entry_price': pos['entry'],
            'exit_price': exit_price,
            'size': pos['size'],
            'pnl': pnl,
            'pnl_pct': (pnl / (pos['entry'] * pos['size'])) * 100,
            'reason': reason,
            'action': pos['action']
        })
    
    def _close_all_positions(self, data_dict, current_date):
        """Fechar todas as posições (rebalance)."""
        symbols_to_close = list(self.positions.keys())
        
        for symbol in symbols_to_close:
            if symbol not in data_dict:
                continue
            
            try:
                current_price = data_dict[symbol].loc[current_date, 'Close']
                self._close_position(symbol, current_price, current_date, 'REBALANCE')
            except:
                pass
        
        self.positions = {}
    
    def _calculate_equity(self, data_dict, current_date):
        """Calcular equity total (capital + valor das posições)."""
        equity = self.current_capital
        
        for symbol, pos in self.positions.items():
            if symbol not in data_dict:
                continue
            
            try:
                current_price = data_dict[symbol].loc[current_date, 'Close']
                position_value = current_price * pos['size']
                equity += position_value
            except:
                pass
        
        return equity
    
    def calculate_metrics(self, equity_curve, dates):
        """Calcular métricas de performance."""
        logging.info("\n" + "="*80)
        logging.info("📊 CALCULANDO MÉTRICAS DE PERFORMANCE")
        logging.info("="*80)
        
        # Equity final
        final_equity = equity_curve[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital * 100
        
        # Returns diários
        equity_series = pd.Series(equity_curve, index=dates)
        daily_returns = equity_series.pct_change().dropna()
        
        # Sharpe Ratio (252 dias de trading)
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        else:
            sharpe = 0.0
        
        # Max Drawdown
        cumulative = (1 + daily_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Trade stats
        trades_df = pd.DataFrame(self.trades)
        
        if len(trades_df) > 0:
            wins = trades_df[trades_df['pnl'] > 0]
            losses = trades_df[trades_df['pnl'] <= 0]
            
            win_rate = len(wins) / len(trades_df) * 100
            avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
            avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0
            
            # Expectancy
            expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)
            
            # Profit Factor
            total_wins = wins['pnl'].sum() if len(wins) > 0 else 0
            total_losses = abs(losses['pnl'].sum()) if len(losses) > 0 else 1
            profit_factor = total_wins / total_losses if total_losses != 0 else 0
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            expectancy = 0
            profit_factor = 0
        
        # Print resultados
        logging.info(f"\n💰 RETORNOS:")
        logging.info(f"   Capital Inicial: ${self.initial_capital:,.2f}")
        logging.info(f"   Capital Final:   ${final_equity:,.2f}")
        logging.info(f"   Retorno Total:   {total_return:+.2f}%")
        
        logging.info(f"\n📈 MÉTRICAS DE RISCO:")
        logging.info(f"   Sharpe Ratio:    {sharpe:.3f}")
        logging.info(f"   Max Drawdown:    {max_drawdown:.2f}%")
        
        logging.info(f"\n📊 ESTATÍSTICAS DE TRADES:")
        logging.info(f"   Total Trades:    {len(trades_df)}")
        logging.info(f"   Win Rate:        {win_rate:.1f}%")
        logging.info(f"   Avg Win:         ${avg_win:,.2f}")
        logging.info(f"   Avg Loss:        ${avg_loss:,.2f}")
        logging.info(f"   Expectancy:      ${expectancy:,.2f}")
        logging.info(f"   Profit Factor:   {profit_factor:.2f}")
        
        # DECISÃO FINAL
        logging.info("\n" + "="*80)
        logging.info("🎯 DECISÃO FINAL (PROTOCOLO ASC-AQ)")
        logging.info("="*80)
        
        approved = True
        reasons = []
        
        if sharpe < 0.3:
            approved = False
            reasons.append(f"❌ Sharpe ({sharpe:.3f}) < 0.3")
        else:
            reasons.append(f"✅ Sharpe ({sharpe:.3f}) ≥ 0.3")
        
        if win_rate < 50:
            approved = False
            reasons.append(f"❌ Win Rate ({win_rate:.1f}%) < 50%")
        else:
            reasons.append(f"✅ Win Rate ({win_rate:.1f}%) ≥ 50%")
        
        if abs(max_drawdown) > 30:
            approved = False
            reasons.append(f"❌ Max DD ({abs(max_drawdown):.1f}%) > 30%")
        else:
            reasons.append(f"✅ Max DD ({abs(max_drawdown):.1f}%) ≤ 30%")
        
        if expectancy <= 0:
            approved = False
            reasons.append(f"❌ Expectancy (${expectancy:.2f}) ≤ 0")
        else:
            reasons.append(f"✅ Expectancy (${expectancy:.2f}) > 0")
        
        for reason in reasons:
            logging.info(f"   {reason}")
        
        logging.info("")
        if approved:
            logging.info("🎉 ESTRATÉGIA APROVADA! DEPLOY EM DEMO AUTORIZADO")
        else:
            logging.info("🚫 ESTRATÉGIA REFUTADA! ENVIAR PARA CEMITÉRIO DE HIPÓTESES")
        
        logging.info("="*80)
        
        return {
            'total_return': total_return,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'expectancy': expectancy,
            'profit_factor': profit_factor,
            'total_trades': len(trades_df),
            'approved': approved
        }


def main():
    """Executar backtest completo."""
    
    logging.info("")
    logging.info("╔═══════════════════════════════════════════════════════════════╗")
    logging.info("║                                                               ║")
    logging.info("║     BACKTEST CIENTÍFICO - MOMENTUM SCANNER v6.0               ║")
    logging.info("║     Protocolo ASC-AQ: Experimento de Refutação               ║")
    logging.info("║                                                               ║")
    logging.info("╚═══════════════════════════════════════════════════════════════╝")
    logging.info("")
    
    # Criar backtest
    bt = MomentumBacktest(start_date='2022-01-01', end_date='2024-11-01')
    
    # Baixar dados
    data_dict = bt.fetch_data()
    
    if len(data_dict) == 0:
        logging.error("❌ Nenhum dado disponível. Abortando backtest.")
        return
    
    # Executar backtest
    equity_curve, dates = bt.run_backtest(data_dict)
    
    # Calcular métricas
    metrics = bt.calculate_metrics(equity_curve, dates)
    
    # Salvar resultado
    result_file = Path(__file__).parent / f"BACKTEST_MOMENTUM_RESULT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    import json
    with open(result_file, 'w') as f:
        json.dump({
            'backtest_date': datetime.now().isoformat(),
            'period': f"{bt.start_date} → {bt.end_date}",
            'metrics': metrics,
            'trades': bt.trades
        }, f, indent=2, default=str)
    
    logging.info(f"\n💾 Resultado salvo em: {result_file}")
    
    return metrics


if __name__ == '__main__':
    metrics = main()

