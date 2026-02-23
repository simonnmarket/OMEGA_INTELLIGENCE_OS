# -*- coding: utf-8 -*-
"""
NUMEIA TRADING SYSTEM v3.1 - BACKTESTING ENGINE
DIRETIVA: F1-T4-FRAMEWORK-BACKTESTING
DATA: 02-11-2025 21:50 CET
EMISSOR: CEO Numeia System
EXECUTOR: Agente Cursor Omega

FUNCIONALIDADE:
- Motor de backtesting robusto e reutilizável
- Simulação de operação do SystemOrchestrator em dados históricos
- Cálculo de métricas de performance (Sharpe, Drawdown, Win Rate)
- Incorporação de custos de transação realistas
- Geração automatizada de relatórios

COMPLIANCE: PROTOCOLO BLINDADO 100%
PERÍODO: 01-01-2021 a 31-12-2023 (3 anos)
FONTE DE DADOS: yfinance (exclusivamente)
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from dataclasses import dataclass, field
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =====================================================
# ESTRUTURAS DE DADOS
# =====================================================

@dataclass
class BacktestTrade:
    """Estrutura para um trade no backtest"""
    timestamp: datetime
    symbol: str
    action: str  # 'BUY', 'SELL', 'CLOSE'
    price: float
    size: Decimal
    strategy: str
    module: str
    pnl: float = 0.0  # P&L líquido do trade (para CLOSE)
    
@dataclass
class BacktestPosition:
    """Estrutura para uma posição aberta no backtest"""
    symbol: str
    action: str  # 'LONG', 'SHORT'
    entry_price: float
    entry_time: datetime
    size: Decimal
    stop_loss: float
    take_profit: float
    strategy: str
    module: str
    current_pnl: float = 0.0
    
@dataclass
class PerformanceMetrics:
    """Métricas de performance de uma estratégia ou portfólio"""
    name: str
    total_return: float = 0.0
    annualized_return: float = 0.0
    annualized_volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    equity_curve: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)

# =====================================================
# BACKTESTING ENGINE
# =====================================================

class Backtester:
    """
    Motor de backtesting para NumeiaTradingSystem v3.1
    
    Responsabilidades:
    - Carregar dados históricos (yfinance)
    - Simular geração de sinais das estratégias
    - Executar trades virtuais
    - Calcular P&L com custos de transação
    - Computar métricas de performance
    - Gerar equity curves
    """
    
    def __init__(self, 
                 start_date: str = '2021-01-01',
                 end_date: str = '2023-12-31',
                 initial_capital: Decimal = Decimal('500000'),
                 transaction_cost_bps: float = 10.0):
        """
        Initialize Backtester
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            initial_capital: Capital inicial (default: EUR 500,000)
            transaction_cost_bps: Custo de transação em basis points (default: 10 bps = 0.10%)
        """
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.transaction_cost_bps = transaction_cost_bps / 10000  # Converter para decimal
        
        # Tracking
        self.trades_history: List[BacktestTrade] = []
        self.positions: Dict[str, BacktestPosition] = {}
        self.equity_curve: List[float] = []
        self.equity_timestamps: List[datetime] = []
        self.daily_returns: List[float] = []
        
        # Performance por estratégia
        self.strategy_performance: Dict[str, PerformanceMetrics] = {}
        
        # Dados de mercado
        self.market_data: Dict[str, pd.DataFrame] = {}
        
        logger.info(f"[Backtester] Inicializado")
        logger.info(f"  Período: {start_date} a {end_date}")
        logger.info(f"  Capital inicial: EUR {float(initial_capital):,.0f}")
        logger.info(f"  Custo de transação: {transaction_cost_bps} bps")
    
    def load_market_data(self, symbols: List[str]) -> bool:
        """
        Carregar dados históricos do yfinance
        
        Args:
            symbols: Lista de símbolos (e.g., ['BTC-USD', 'AAPL', 'EURUSD=X'])
            
        Returns:
            bool: True se dados carregados com sucesso
        """
        logger.info(f"[Backtester] Carregando dados para {len(symbols)} símbolos...")
        
        for symbol in symbols:
            try:
                # Adicionar buffer de 1 ano antes para cálculos (lookback)
                buffer_start = self.start_date - timedelta(days=365)
                
                data = yf.download(
                    symbol, 
                    start=buffer_start, 
                    end=self.end_date,
                    progress=False
                )
                
                if data.empty:
                    logger.warning(f"  AVISO: Sem dados para {symbol}")
                    continue
                
                self.market_data[symbol] = data
                logger.info(f"  OK {symbol}: {len(data)} candles")
                
            except Exception as e:
                logger.error(f"  ERRO ao carregar {symbol}: {e}")
        
        logger.info(f"[Backtester] {len(self.market_data)}/{len(symbols)} símbolos carregados")
        return len(self.market_data) > 0
    
    def execute_trade(self, 
                     timestamp: datetime,
                     symbol: str,
                     action: str,
                     price: float,
                     size: Decimal,
                     strategy: str,
                     module: str,
                     stop_loss: float = None,
                     take_profit: float = None) -> bool:
        """
        Executa um trade virtual no backtest
        
        Args:
            timestamp: Timestamp do trade
            symbol: Símbolo
            action: 'BUY' ou 'SELL'
            price: Preço de execução
            size: Tamanho da posição (capital)
            strategy: Nome da estratégia
            module: Nome do módulo
            stop_loss: Preço de stop loss
            take_profit: Preço de take profit
            
        Returns:
            bool: True se trade executado
        """
        # Calcular custo de transação
        transaction_cost = float(size) * self.transaction_cost_bps
        
        # CORREÇÃO #1: Deduzir apenas custos ao abrir (capital fica "alocado" na posição)
        self.current_capital -= Decimal(str(transaction_cost))
        
        # Registrar trade
        trade = BacktestTrade(
            timestamp=timestamp,
            symbol=symbol,
            action=action,
            price=price,
            size=size,
            strategy=strategy,
            module=module
        )
        self.trades_history.append(trade)
        
        # Abrir posição
        if action in ['BUY', 'SELL']:
            position = BacktestPosition(
                symbol=symbol,
                action='LONG' if action == 'BUY' else 'SHORT',
                entry_price=price,
                entry_time=timestamp,
                size=size,
                stop_loss=stop_loss or (price * 0.98 if action == 'BUY' else price * 1.02),
                take_profit=take_profit or (price * 1.06 if action == 'BUY' else price * 0.94),
                strategy=strategy,
                module=module
            )
            
            position_key = f"{symbol}_{strategy}"
            self.positions[position_key] = position
            
            # Logging de debug
            logger.debug(f"[Open] {symbol} {action} @ {price:.2f}, Size={float(size):.2f}, "
                        f"Cost={transaction_cost:.2f}, Capital now={float(self.current_capital):.2f}")
        
        return True
    
    def update_positions(self, timestamp: datetime, current_prices: Dict[str, float]):
        """
        Atualiza P&L das posições abertas e fecha se hit SL/TP
        
        Args:
            timestamp: Timestamp atual
            current_prices: Preços atuais {symbol: price}
        """
        positions_to_close = []
        
        for position_key, position in self.positions.items():
            if position.symbol not in current_prices:
                continue
            
            current_price = current_prices[position.symbol]
            
            # Calcular P&L atual
            if position.action == 'LONG':
                pnl = (current_price - position.entry_price) / position.entry_price
            else:  # SHORT
                pnl = (position.entry_price - current_price) / position.entry_price
            
            position.current_pnl = pnl * float(position.size)
            
            # Verificar Stop Loss / Take Profit
            should_close = False
            close_reason = ""
            
            if position.action == 'LONG':
                if current_price <= position.stop_loss:
                    should_close = True
                    close_reason = "STOP_LOSS"
                elif current_price >= position.take_profit:
                    should_close = True
                    close_reason = "TAKE_PROFIT"
            else:  # SHORT
                if current_price >= position.stop_loss:
                    should_close = True
                    close_reason = "STOP_LOSS"
                elif current_price <= position.take_profit:
                    should_close = True
                    close_reason = "TAKE_PROFIT"
            
            if should_close:
                positions_to_close.append((position_key, current_price, close_reason))
        
        # Fechar posições
        for position_key, close_price, reason in positions_to_close:
            self.close_position(timestamp, position_key, close_price, reason)
    
    def close_position(self, timestamp: datetime, position_key: str, 
                      close_price: float, reason: str):
        """
        Fecha uma posição e realiza o P&L
        
        Args:
            timestamp: Timestamp do fechamento
            position_key: Chave da posição
            close_price: Preço de fechamento
            reason: Razão do fechamento
        """
        if position_key not in self.positions:
            return
        
        position = self.positions[position_key]
        
        # Calcular P&L final
        if position.action == 'LONG':
            pnl_pct = (close_price - position.entry_price) / position.entry_price
        else:  # SHORT
            pnl_pct = (position.entry_price - close_price) / position.entry_price
        
        pnl_amount = pnl_pct * float(position.size)
        
        # Custos de transação (abertura + fechamento)
        transaction_cost_open = float(position.size) * self.transaction_cost_bps
        transaction_cost_close = float(position.size) * self.transaction_cost_bps
        total_transaction_costs = transaction_cost_open + transaction_cost_close
        
        # P&L líquido (após ambos os custos)
        net_pnl = pnl_amount - total_transaction_costs
        
        # CORREÇÃO #2 FINAL: Adicionar P&L líquido ao capital
        self.current_capital += Decimal(str(net_pnl))
        
        # Registrar trade de fechamento com P&L
        close_trade = BacktestTrade(
            timestamp=timestamp,
            symbol=position.symbol,
            action='CLOSE',
            price=close_price,
            size=position.size,
            strategy=position.strategy,
            module=position.module,
            pnl=net_pnl  # CORREÇÃO F1-T5-FIX-01: Armazenar P&L real
        )
        self.trades_history.append(close_trade)
        
        # Remover posição
        del self.positions[position_key]
        
        # Logging de debug (CORREÇÃO #3)
        logger.debug(f"[Close] {position.symbol}: Entry={position.entry_price:.2f}, "
                    f"Exit={close_price:.2f}, P&L={net_pnl:.2f}, "
                    f"Capital now={float(self.current_capital):.2f}, Reason={reason}")
    
    def calculate_metrics(self, strategy_name: str = None) -> PerformanceMetrics:
        """
        Calcula métricas de performance
        
        Args:
            strategy_name: Nome da estratégia (None = portfólio total)
        
        Returns:
            PerformanceMetrics
        """
        # Filtrar trades da estratégia
        if strategy_name:
            trades = [t for t in self.trades_history if t.strategy == strategy_name]
        else:
            trades = self.trades_history
        
        if len(trades) == 0:
            return PerformanceMetrics(name=strategy_name or "Portfolio")
        
        # =====================================================
        # CORREÇÃO F1-T5-FIX-01: EQUITY CURVE E WIN/LOSS TRACKING
        # =====================================================
        
        # CORREÇÃO BUG #2: Reconstruir equity curve corretamente
        equity_values = []
        equity_timestamps = []
        current_equity = float(self.initial_capital)
        
        for trade in sorted(trades, key=lambda t: t.timestamp):
            if trade.action == 'CLOSE':
                # Usar P&L REAL armazenado no trade
                current_equity += trade.pnl
            
            equity_values.append(current_equity)
            equity_timestamps.append(trade.timestamp)
        
        # Retorno total
        total_return = (float(self.current_capital) - float(self.initial_capital)) / float(self.initial_capital)
        
        # Número de anos
        years = (self.end_date - self.start_date).days / 365.25
        
        # Retorno anualizado
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Volatilidade anualizada (baseado em equity curve)
        if len(equity_values) > 1:
            # Calcular retornos diários da equity curve
            equity_series = pd.Series(equity_values)
            equity_returns = equity_series.pct_change().dropna()
            daily_vol = equity_returns.std()
            annualized_volatility = daily_vol * np.sqrt(252)  # 252 dias de trading
        else:
            annualized_volatility = 0
        
        # Sharpe Ratio (assumindo risk-free rate = 2%)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility if annualized_volatility > 0 else 0
        
        # CORREÇÃO BUG #3: Maximum Drawdown (corrigido automaticamente pela equity curve)
        peak = float(self.initial_capital)
        max_dd = 0
        for equity in equity_values:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        # CORREÇÃO BUG #1: Win Rate calculado corretamente
        EPSILON = 0.01  # EUR 0.01 (tolerância)
        
        winning_trades = 0
        losing_trades = 0
        breakeven_trades = 0
        total_win_amount = 0.0
        total_loss_amount = 0.0
        
        for trade in trades:
            if trade.action == 'CLOSE' and hasattr(trade, 'pnl'):
                if trade.pnl > EPSILON:
                    winning_trades += 1
                    total_win_amount += trade.pnl
                elif trade.pnl < -EPSILON:
                    losing_trades += 1
                    total_loss_amount += abs(trade.pnl)
                else:
                    breakeven_trades += 1
        
        total_trades_count = len([t for t in trades if t.action == 'CLOSE'])
        
        # Calcular métricas adicionais
        total_decisive_trades = winning_trades + losing_trades
        win_rate = (winning_trades / total_decisive_trades * 100) if total_decisive_trades > 0 else 0.0
        
        avg_win = total_win_amount / winning_trades if winning_trades > 0 else 0.0
        avg_loss = total_loss_amount / losing_trades if losing_trades > 0 else 0.0
        
        profit_factor = total_win_amount / total_loss_amount if total_loss_amount > 0 else 0.0
        
        metrics = PerformanceMetrics(
            name=strategy_name or "Portfolio",
            total_return=total_return * 100,  # Em percentual
            annualized_return=annualized_return * 100,
            annualized_volatility=annualized_volatility * 100,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_dd * 100,
            win_rate=win_rate,  # CORREÇÃO: Win rate real calculado
            total_trades=total_trades_count,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            equity_curve=equity_values,
            timestamps=equity_timestamps  # CORREÇÃO: Timestamps da equity curve
        )
        
        return metrics
    
    def run_backtest(self, strategy_function, strategy_name: str, 
                    symbols: List[str], allocated_capital: Decimal) -> PerformanceMetrics:
        """
        Executa backtest de uma estratégia específica
        
        Args:
            strategy_function: Função que gera sinais
            strategy_name: Nome da estratégia
            symbols: Símbolos para a estratégia
            allocated_capital: Capital alocado
            
        Returns:
            PerformanceMetrics
        """
        logger.info(f"[Backtester] Iniciando backtest: {strategy_name}")
        logger.info(f"  Capital alocado: EUR {float(allocated_capital):,.0f}")
        logger.info(f"  Símbolos: {symbols}")
        
        # Carregar dados
        self.load_market_data(symbols)
        
        # Criar estrutura de tracking para esta estratégia
        strategy_capital = allocated_capital
        strategy_trades = []
        strategy_equity = [float(strategy_capital)]
        strategy_timestamps = [self.start_date]
        
        # Simular dia a dia
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Obter preços do dia
            current_prices = {}
            for symbol in symbols:
                if symbol in self.market_data:
                    try:
                        price_data = self.market_data[symbol]
                        if current_date in price_data.index:
                            current_prices[symbol] = float(price_data.loc[current_date, 'Close'])
                    except:
                        pass
            
            # Gerar sinal da estratégia (placeholder - será implementado por estratégia)
            # signal = strategy_function(current_date, self.market_data)
            
            # Atualizar equity
            # (simplificado - em produção calcular P&L de posições abertas)
            
            # Próximo dia
            current_date += timedelta(days=1)
        
        # Calcular métricas
        metrics = self.calculate_metrics(strategy_name)
        
        logger.info(f"[Backtester] Backtest concluído: {strategy_name}")
        logger.info(f"  Total de trades: {metrics.total_trades}")
        logger.info(f"  Retorno total: {metrics.total_return:.2f}%")
        
        return metrics
    
    def generate_report(self, output_file: str = "RELATORIO_BACKTESTING_FASE1.md"):
        """
        Gera relatório completo em Markdown
        
        Args:
            output_file: Nome do arquivo de saída
        """
        logger.info(f"[Backtester] Gerando relatório: {output_file}")
        
        report_lines = []
        
        # Header
        report_lines.append("# RELATÓRIO DE BACKTESTING - NUMEIA TRADING SYSTEM v3.1")
        report_lines.append(f"**Período:** {self.start_date.date()} a {self.end_date.date()}")
        report_lines.append(f"**Capital Inicial:** EUR {float(self.initial_capital):,.0f}")
        report_lines.append(f"**Capital Final:** EUR {float(self.current_capital):,.0f}")
        report_lines.append("")
        
        # Métricas do portfólio
        portfolio_metrics = self.calculate_metrics()
        report_lines.append("## PERFORMANCE DO PORTFÓLIO")
        report_lines.append(f"- **Retorno Total:** {portfolio_metrics.total_return:.2f}%")
        report_lines.append(f"- **Retorno Anualizado:** {portfolio_metrics.annualized_return:.2f}%")
        report_lines.append(f"- **Sharpe Ratio:** {portfolio_metrics.sharpe_ratio:.2f}")
        report_lines.append(f"- **Max Drawdown:** {portfolio_metrics.max_drawdown:.2f}%")
        report_lines.append("")
        
        # Salvar relatório
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"[Backtester] Relatório salvo: {output_file}")
    
    def get_summary(self) -> Dict:
        """
        Retorna sumário do backtest
        
        Returns:
            Dict com informações principais
        """
        return {
            'period': f"{self.start_date.date()} to {self.end_date.date()}",
            'initial_capital': float(self.initial_capital),
            'final_capital': float(self.current_capital),
            'total_return': ((float(self.current_capital) - float(self.initial_capital)) / float(self.initial_capital)) * 100,
            'total_trades': len(self.trades_history),
            'symbols_tested': len(self.market_data)
        }
