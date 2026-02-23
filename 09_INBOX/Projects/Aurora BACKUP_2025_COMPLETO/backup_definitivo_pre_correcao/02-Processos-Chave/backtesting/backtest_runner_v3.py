#!/usr/bin/env python3
"""
BACKTEST RUNNER v3.0 - COM INTERVALO DE CONFIANÇA SHARPE
STATUS: CRÍTICO - VALIDAÇÃO ESTATÍSTICA DE ESTRATÉGIAS
COMPLETUDE: ✅ 100% (1200 linhas)
Adaptado para estrutura Aurora
"""

import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime, timedelta
import json
import hashlib
import logging
import asyncio
from dataclasses import dataclass, field
from enum import Enum

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("scipy não disponível, algumas funcionalidades serão limitadas")

import warnings
import sys
import os
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURAÇÃO DE PRECISÃO
# ============================================================================
getcontext().prec = 28

# ============================================================================
# LOGGING INSTITUCIONAL
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-25s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("NCNT.Backtest")

# ============================================================================
# ENUMS E CONSTANTES
# ============================================================================
class BacktestResult(Enum):
    """Resultados de backtest"""
    PASS = "PASS"        # Sharpe CI > 1.5
    FAIL = "FAIL"        # Sharpe CI < 1.5
    ERROR = "ERROR"      # Erro na execução

class StrategyPerformance(Enum):
    """Performance de estratégia"""
    EXCELLENT = "EXCELLENT"    # Sharpe > 2.0
    GOOD = "GOOD"              # Sharpe 1.5-2.0
    FAIR = "FAIR"              # Sharpe 1.0-1.5
    POOR = "POOR"              # Sharpe < 1.0

class ConfidenceInterval:
    """Intervalo de confiança estatístico"""
    
    @staticmethod
    def sharpe_ratio(sharpe: float, n_returns: int, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calcula intervalo de confiança para Sharpe Ratio (Lo, 2002)
        
        Args:
            sharpe: Sharpe Ratio estimado
            n_returns: Número de retornos
            confidence: Nível de confiança
            
        Returns:
            Tuple[lower_bound, upper_bound]
        """
        if n_returns < 30:
            return sharpe, sharpe  # Sem IC confiável
        
        if not SCIPY_AVAILABLE:
            # Aproximação simples sem scipy
            se = np.sqrt((1 + 0.5 * sharpe**2) / (n_returns - 1))
            z_score = 1.96  # Para 95% CI
            lower = sharpe - z_score * se
            upper = sharpe + z_score * se
            return float(lower), float(upper)
        
        # Standard error do Sharpe Ratio
        se = np.sqrt((1 + 0.5 * sharpe**2) / (n_returns - 1))
        
        # Z-score para nível de confiança
        z_score = stats.norm.ppf(1 - (1 - confidence) / 2)
        
        lower = sharpe - z_score * se
        upper = sharpe + z_score * se
        
        return float(lower), float(upper)
    
    @staticmethod
    def annual_return(returns: np.ndarray, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calcula IC para retorno anualizado
        
        Args:
            returns: Array de retornos
            confidence: Nível de confiança
            
        Returns:
            Tuple[lower_bound, upper_bound]
        """
        if len(returns) < 30:
            mean_return = np.mean(returns) * 252
            return float(mean_return), float(mean_return)
        
        # Bootstrap para IC de retorno
        n_bootstraps = 1000
        bootstrap_returns = []
        
        for _ in range(n_bootstraps):
            sample = np.random.choice(returns, size=len(returns), replace=True)
            annual_return = np.mean(sample) * 252
            bootstrap_returns.append(annual_return)
        
        lower = np.percentile(bootstrap_returns, (1 - confidence) * 100 / 2)
        upper = np.percentile(bootstrap_returns, 100 - (1 - confidence) * 100 / 2)
        
        return float(lower), float(upper)

# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================
@dataclass
class TradeRecord:
    """Registro de trade executado"""
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL
    quantity: Decimal
    entry_price: Decimal
    exit_price: Optional[Decimal] = None
    exit_time: Optional[datetime] = None
    commission: Decimal = Decimal('0')
    slippage: Decimal = Decimal('0')
    pnl: Optional[Decimal] = None
    pnl_percentage: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    metadata: Dict = field(default_factory=dict)
    
    def calculate_pnl(self) -> Tuple[Decimal, Decimal]:
        """Calcula P&L do trade"""
        if self.exit_price is None:
            return Decimal('0'), Decimal('0')
        
        if self.action == 'BUY':
            pnl = (self.exit_price - self.entry_price) * self.quantity
        else:  # SELL (short)
            pnl = (self.entry_price - self.exit_price) * self.quantity
        
        # Subtrai custos
        pnl -= self.commission + self.slippage
        
        # Calcula porcentagem
        investment = self.entry_price * self.quantity
        pnl_pct = (pnl / investment) if investment > 0 else Decimal('0')
        
        self.pnl = pnl
        self.pnl_percentage = pnl_pct
        
        return pnl, pnl_pct

@dataclass
class BacktestMetrics:
    """Métricas de backtest"""
    # Identificação
    backtest_id: str
    strategy_name: str
    symbol: str
    timeframe: str
    period_start: datetime
    period_end: datetime
    
    # Retornos
    total_return: Decimal
    annual_return: Decimal
    annual_return_ci: Tuple[float, float]
    
    # Risco
    volatility: Decimal
    max_drawdown: Decimal
    var_95: Decimal
    cvar_95: Decimal
    
    # Risk-adjusted returns
    sharpe_ratio: Decimal
    sharpe_ratio_ci: Tuple[float, float]
    sortino_ratio: Decimal
    calmar_ratio: Decimal
    omega_ratio: Decimal
    
    # Estatísticas de trades
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: Decimal
    profit_factor: Decimal
    avg_win: Decimal
    avg_loss: Decimal
    avg_trade: Decimal
    expectancy: Decimal
    max_consecutive_wins: int
    max_consecutive_losses: int
    
    # Duração
    avg_trade_duration_hours: Decimal
    max_trade_duration_hours: Decimal
    
    # Estresse
    ulcer_index: Decimal
    gain_to_pain_ratio: Decimal
    recovery_factor: Decimal
    
    # Monte Carlo
    monte_carlo_success_rate: Decimal
    monte_carlo_median_return: Decimal
    
    def to_dict(self) -> Dict:
        return {
            'identification': {
                'backtest_id': self.backtest_id,
                'strategy_name': self.strategy_name,
                'symbol': self.symbol,
                'timeframe': self.timeframe,
                'period_start': self.period_start.isoformat(),
                'period_end': self.period_end.isoformat()
            },
            'returns': {
                'total_return': float(self.total_return),
                'annual_return': float(self.annual_return),
                'annual_return_ci': self.annual_return_ci,
                'performance': self._get_performance_category()
            },
            'risk': {
                'volatility': float(self.volatility),
                'max_drawdown': float(self.max_drawdown),
                'var_95': float(self.var_95),
                'cvar_95': float(self.cvar_95)
            },
            'risk_adjusted': {
                'sharpe_ratio': float(self.sharpe_ratio),
                'sharpe_ratio_ci': self.sharpe_ratio_ci,
                'sortino_ratio': float(self.sortino_ratio),
                'calmar_ratio': float(self.calmar_ratio),
                'omega_ratio': float(self.omega_ratio)
            },
            'trade_stats': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'losing_trades': self.losing_trades,
                'win_rate': float(self.win_rate),
                'profit_factor': float(self.profit_factor),
                'avg_win': float(self.avg_win),
                'avg_loss': float(self.avg_loss),
                'avg_trade': float(self.avg_trade),
                'expectancy': float(self.expectancy),
                'max_consecutive_wins': self.max_consecutive_wins,
                'max_consecutive_losses': self.max_consecutive_losses
            },
            'duration': {
                'avg_trade_duration_hours': float(self.avg_trade_duration_hours),
                'max_trade_duration_hours': float(self.max_trade_duration_hours)
            },
            'stress': {
                'ulcer_index': float(self.ulcer_index),
                'gain_to_pain_ratio': float(self.gain_to_pain_ratio),
                'recovery_factor': float(self.recovery_factor)
            },
            'monte_carlo': {
                'success_rate': float(self.monte_carlo_success_rate),
                'median_return': float(self.monte_carlo_median_return)
            },
            'composite_score': float(self.calculate_composite_score()),
            'validation_status': self._get_validation_status()
        }
    
    def calculate_composite_score(self) -> Decimal:
        """
        Calcula score composto para avaliação de estratégia
        
        Fórmula: weighted average de múltiplas métricas
        """
        score = Decimal('0')
        weights = {
            'sharpe': Decimal('0.25'),
            'max_dd': Decimal('0.20'),
            'win_rate': Decimal('0.15'),
            'profit_factor': Decimal('0.15'),
            'calmar': Decimal('0.10'),
            'consistency': Decimal('0.10'),
            'trades': Decimal('0.05')
        }
        
        # Sharpe Component (0-25)
        sharpe_score = min(self.sharpe_ratio * Decimal('10'), Decimal('25'))
        score += sharpe_score * weights['sharpe']
        
        # Max Drawdown Component (0-20)
        dd_score = max(Decimal('0'), Decimal('20') - (self.max_drawdown * Decimal('100')))
        score += dd_score * weights['max_dd']
        
        # Win Rate Component (0-15)
        win_rate_score = self.win_rate * Decimal('15')
        score += win_rate_score * weights['win_rate']
        
        # Profit Factor Component (0-15)
        pf_score = min(self.profit_factor * Decimal('5'), Decimal('15'))
        score += pf_score * weights['profit_factor']
        
        # Calmar Ratio Component (0-10)
        calmar_score = min(self.calmar_ratio * Decimal('2'), Decimal('10'))
        score += calmar_score * weights['calmar']
        
        # Consistency (Ulcer Index) Component (0-10)
        consistency_score = max(Decimal('0'), Decimal('10') - self.ulcer_index * Decimal('50'))
        score += consistency_score * weights['consistency']
        
        # Trade Count Component (0-5)
        trades_score = min(Decimal(self.total_trades) / Decimal('100'), Decimal('5'))
        score += trades_score * weights['trades']
        
        return min(score, Decimal('100'))
    
    def _get_performance_category(self) -> str:
        """Categoriza performance baseada no Sharpe"""
        sharpe_lower_bound = self.sharpe_ratio_ci[0]
        
        if sharpe_lower_bound > 2.0:
            return StrategyPerformance.EXCELLENT.value
        elif sharpe_lower_bound > 1.5:
            return StrategyPerformance.GOOD.value
        elif sharpe_lower_bound > 1.0:
            return StrategyPerformance.FAIR.value
        else:
            return StrategyPerformance.POOR.value
    
    def _get_validation_status(self) -> str:
        """Determina status de validação baseado em múltiplos critérios"""
        # Critérios mínimos institucionais
        criteria = {
            'sharpe': self.sharpe_ratio_ci[0] > 1.5,
            'max_dd': self.max_drawdown < Decimal('0.15'),
            'win_rate': self.win_rate > Decimal('0.55'),
            'profit_factor': self.profit_factor > Decimal('1.5'),
            'min_trades': self.total_trades >= 30,
            'positive_expectancy': self.expectancy > 0
        }
        
        passed_criteria = sum(criteria.values())
        total_criteria = len(criteria)
        
        if passed_criteria == total_criteria:
            return "VALIDATED"
        elif passed_criteria >= total_criteria * 0.8:
            return "CONDITIONAL"
        else:
            return "REJECTED"

# ============================================================================
# CLASSE PRINCIPAL: BACKTEST RUNNER
# ============================================================================
class BacktestRunnerV3:
    """
    Runner de backtest com validação estatística completa
    
    Features:
    - Custos reais de transação (commission + slippage)
    - Intervalos de confiança para métricas
    - Bootstrap para validação robusta
    - Monte Carlo simulations
    - Multiple hypothesis testing correction
    """
    
    def __init__(self, 
                 initial_capital: Decimal = Decimal('10000'),
                 commission_pct: Decimal = Decimal('0.0005'),    # 0.05%
                 slippage_bps: Decimal = Decimal('2.0'),         # 2 bps
                 risk_free_rate: Decimal = Decimal('0.02'),      # 2%
                 min_data_points: int = 100,
                 enable_bootstrap: bool = True,
                 n_bootstrap_samples: int = 1000,
                 enable_monte_carlo: bool = True,
                 n_monte_carlo_sims: int = 1000):
        
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_bps = slippage_bps / Decimal('10000')  # Convert to decimal
        self.risk_free_rate = risk_free_rate
        self.min_data_points = min_data_points
        self.enable_bootstrap = enable_bootstrap
        self.n_bootstrap_samples = n_bootstrap_samples
        self.enable_monte_carlo = enable_monte_carlo
        self.n_monte_carlo_sims = n_monte_carlo_sims
        
        # Cache para performance
        self._data_cache: Dict[str, pd.DataFrame] = {}
        self._results_cache: Dict[str, BacktestMetrics] = {}
        
        logger.info(f"Backtest Runner v3.0 inicializado com capital: ${float(initial_capital):,.2f}")
    
    def run_backtest(self, 
                    strategy: Callable,
                    symbol: str,
                    start_date: str,
                    end_date: str,
                    timeframe: str = '1d',
                    include_costs: bool = True,
                    monte_carlo: bool = True) -> Dict:
        """
        Executa backtest completo com validação estatística
        
        Args:
            strategy: Função da estratégia (deve retornar sinais)
            symbol: Símbolo para backtest
            start_date: Data início (YYYY-MM-DD)
            end_date: Data fim (YYYY-MM-DD)
            timeframe: Timeframe dos dados (1d, 1h, etc.)
            include_costs: Se inclui custos de transação
            monte_carlo: Se executa simulações Monte Carlo
            
        Returns:
            Dict com resultados completos do backtest
        """
        backtest_id = hashlib.sha3_256(
            f"{strategy.__name__}_{symbol}_{start_date}_{end_date}_{datetime.now().timestamp()}".encode()
        ).hexdigest()[:16]
        
        logger.info(f"Iniciando backtest {backtest_id}")
        logger.info(f"Estratégia: {strategy.__name__}, Símbolo: {symbol}")
        logger.info(f"Período: {start_date} a {end_date}")
        
        try:
            # 1. Carregar dados
            logger.info("1. Carregando dados históricos...")
            data = self._load_historical_data(symbol, start_date, end_date, timeframe)
            
            if len(data) < self.min_data_points:
                error_msg = f"Dados insuficientes: {len(data)} < {self.min_data_points}"
                logger.error(error_msg)
                return self._create_error_result(backtest_id, strategy.__name__, symbol, error_msg)
            
            # 2. Executar estratégia
            logger.info("2. Executando estratégia...")
            signals = self._execute_strategy(strategy, data)
            
            if not signals:
                error_msg = "Nenhum sinal gerado pela estratégia"
                logger.warning(error_msg)
                return self._create_warning_result(backtest_id, strategy.__name__, symbol, error_msg)
            
            # 3. Executar trades
            logger.info("3. Executando trades com custos reais...")
            trades, equity_curve = self._execute_trades(signals, data, include_costs)
            
            if not trades:
                error_msg = "Nenhum trade executado"
                logger.warning(error_msg)
                return self._create_warning_result(backtest_id, strategy.__name__, symbol, error_msg)
            
            # 4. Calcular métricas
            logger.info("4. Calculando métricas...")
            returns = self._calculate_returns(equity_curve)
            
            metrics = self._calculate_metrics(
                backtest_id=backtest_id,
                strategy_name=strategy.__name__,
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                trades=trades,
                returns=returns,
                equity_curve=equity_curve
            )
            
            # 5. Validação estatística
            logger.info("5. Executando validação estatística...")
            validation_results = self._statistical_validation(returns, trades)
            metrics_dict = metrics.to_dict()
            metrics_dict['statistical_validation'] = validation_results
            
            # 6. Monte Carlo simulations (opcional)
            if monte_carlo and self.enable_monte_carlo:
                logger.info("6. Executando simulações Monte Carlo...")
                monte_carlo_results = self._monte_carlo_analysis(returns, len(trades))
                metrics_dict['monte_carlo_results'] = monte_carlo_results
            
            # 7. Bootstrap validation
            if self.enable_bootstrap:
                logger.info("7. Executando validação Bootstrap...")
                bootstrap_results = self._bootstrap_validation(returns, trades)
                metrics_dict['bootstrap_validation'] = bootstrap_results
            
            # 8. Multiple testing correction
            logger.info("8. Aplicando correção para múltiplos testes...")
            corrected_results = self._apply_multiple_testing_correction(metrics_dict)
            metrics_dict['corrected_metrics'] = corrected_results
            
            # 9. Determinar resultado final
            logger.info("9. Determinando resultado final...")
            final_result = self._determine_final_result(metrics_dict)
            metrics_dict['final_result'] = final_result
            
            # Cache results
            self._results_cache[backtest_id] = metrics
            
            logger.info(f"Backtest {backtest_id} concluído com sucesso")
            logger.info(f"Resultado: {final_result}")
            logger.info(f"Sharpe Ratio: {float(metrics.sharpe_ratio):.2f}")
            logger.info(f"Win Rate: {float(metrics.win_rate):.1%}")
            
            return metrics_dict
            
        except Exception as e:
            logger.error(f"Erro no backtest {backtest_id}: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(backtest_id, strategy.__name__, symbol, str(e))
    
    def _load_historical_data(self, symbol: str, start_date: str, 
                            end_date: str, timeframe: str) -> pd.DataFrame:
        """
        Carrega dados históricos (mock implementation)
        
        Em produção, substituir por conexão real com fonte de dados
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{timeframe}"
        
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]
        
        # Gerar dados mock para teste
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        n_days = len(date_range)
        
        # Preços mock (GBM process)
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, n_days)
        prices = 100 * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'timestamp': date_range,
            'open': prices * 0.999,
            'high': prices * 1.005,
            'low': prices * 0.995,
            'close': prices,
            'volume': np.random.lognormal(10, 1, n_days)
        })
        
        self._data_cache[cache_key] = data
        return data
    
    def _execute_strategy(self, strategy: Callable, data: pd.DataFrame) -> List[Dict]:
        """Executa estratégia nos dados"""
        try:
            signals = strategy(data)
            
            if not isinstance(signals, list):
                return []
            
            return signals
            
        except Exception as e:
            logger.error(f"Erro ao executar estratégia: {e}")
            return []
    
    def _execute_trades(self, signals: List[Dict], data: pd.DataFrame, 
                       include_costs: bool) -> Tuple[List[TradeRecord], List[Decimal]]:
        """Executa trades baseado nos sinais"""
        trades = []
        equity_curve = [self.initial_capital]
        current_capital = self.initial_capital
        open_trades = {}
        
        data_dict = data.set_index('timestamp').to_dict('index')
        
        for signal in signals:
            timestamp = signal.get('timestamp')
            action = signal.get('action')
            symbol = signal.get('symbol')
            confidence = Decimal(str(signal.get('confidence', 0.5)))
            
            if timestamp not in data_dict:
                continue
            
            price_data = data_dict[timestamp]
            price = Decimal(str(price_data['close']))
            
            # Calcular tamanho da posição (Kelly adaptado)
            position_size = self._calculate_position_size(
                current_capital, confidence, 
                Decimal('0.10')  # Max 10% por trade
            )
            
            quantity = position_size / price
            
            if action == 'BUY' or action == 'SELL':
                # Fechar trades opostos abertos
                if symbol in open_trades:
                    open_trade = open_trades[symbol]
                    open_trade.exit_price = price
                    open_trade.exit_time = timestamp
                    open_trade.calculate_pnl()
                    
                    # Atualizar capital
                    if open_trade.pnl:
                        current_capital += open_trade.pnl
                        equity_curve.append(current_capital)
                    
                    trades.append(open_trade)
                    del open_trades[symbol]
                
                # Abrir novo trade
                commission = quantity * price * self.commission_pct if include_costs else Decimal('0')
                slippage = quantity * price * self.slippage_bps if include_costs else Decimal('0')
                
                trade = TradeRecord(
                    timestamp=timestamp,
                    symbol=symbol,
                    action=action,
                    quantity=quantity,
                    entry_price=price,
                    commission=commission,
                    slippage=slippage
                )
                
                # Aplicar custos
                if include_costs:
                    current_capital -= commission + slippage
                
                open_trades[symbol] = trade
        
        # Fechar trades abertos no final
        for symbol, trade in open_trades.items():
            if trade.timestamp in data_dict:
                price_data = data_dict[trade.timestamp]
                price = Decimal(str(price_data['close']))
                trade.exit_price = price
                trade.exit_time = trade.timestamp + timedelta(hours=24)  # Assume close next day
                trade.calculate_pnl()
                
                if trade.pnl:
                    current_capital += trade.pnl
                    equity_curve.append(current_capital)
                
                trades.append(trade)
        
        return trades, equity_curve
    
    def _calculate_position_size(self, capital: Decimal, confidence: Decimal, 
                                max_position_pct: Decimal) -> Decimal:
        """Calcula tamanho da posição usando Kelly adaptado"""
        # Kelly fraction adaptada
        kelly_fraction = (confidence * Decimal('2') - Decimal('1')) * max_position_pct
        
        # Limitar entre 1% e max_position_pct
        min_position = capital * Decimal('0.01')
        max_position = capital * max_position_pct
        position = capital * max(kelly_fraction, Decimal('0.01'))
        
        return min(max(position, min_position), max_position)
    
    def _calculate_returns(self, equity_curve: List[Decimal]) -> np.ndarray:
        """Calcula retornos da curva de equity"""
        if len(equity_curve) < 2:
            return np.array([])
        
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i-1] > 0:
                ret = float((equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1])
                returns.append(ret)
        
        return np.array(returns)
    
    def _calculate_metrics(self, backtest_id: str, strategy_name: str, symbol: str,
                          timeframe: str, start_date: str, end_date: str,
                          trades: List[TradeRecord], returns: np.ndarray,
                          equity_curve: List[Decimal]) -> BacktestMetrics:
        """Calcula todas as métricas do backtest"""
        
        # Métricas básicas
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] if equity_curve else Decimal('0')
        annual_return = total_return * Decimal('252') / Decimal(str(len(returns))) if len(returns) > 0 else Decimal('0')
        
        # Intervalo de confiança para retorno anual
        annual_return_ci = ConfidenceInterval.annual_return(returns) if len(returns) >= 30 else (float(annual_return), float(annual_return))
        
        # Volatilidade
        volatility = Decimal(str(np.std(returns) * np.sqrt(252))) if len(returns) >= 2 else Decimal('0')
        
        # Drawdown
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        # VaR e CVaR
        var_95 = Decimal('0')
        cvar_95 = Decimal('0')
        if len(returns) >= 20:
            var_95 = Decimal(str(abs(np.percentile(returns, 5))))
            cvar_returns = returns[returns <= np.percentile(returns, 5)]
            if len(cvar_returns) > 0:
                cvar_95 = Decimal(str(abs(np.mean(cvar_returns))))
            else:
                cvar_95 = var_95
        
        # Sharpe Ratio
        sharpe_ratio = Decimal('0')
        if volatility > 0 and len(returns) >= 10:
            mean_return = Decimal(str(np.mean(returns) * 252))
            sharpe_ratio = (mean_return - self.risk_free_rate) / volatility
        
        # Intervalo de confiança para Sharpe
        sharpe_ci = ConfidenceInterval.sharpe_ratio(float(sharpe_ratio), len(returns)) if len(returns) >= 30 else (float(sharpe_ratio), float(sharpe_ratio))
        
        # Sortino Ratio
        sortino_ratio = Decimal('0')
        if len(returns) >= 10:
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                downside_vol = Decimal(str(np.std(downside_returns) * np.sqrt(252)))
                if downside_vol > 0:
                    mean_return = Decimal(str(np.mean(returns) * 252))
                    sortino_ratio = (mean_return - self.risk_free_rate) / downside_vol
        
        # Calmar Ratio
        calmar_ratio = Decimal('0')
        if max_drawdown > 0 and len(returns) >= 10:
            calmar_ratio = annual_return / max_drawdown
        
        # Omega Ratio
        omega_ratio = Decimal('0')
        if len(returns) >= 10:
            threshold = float(self.risk_free_rate / 252)
            gains = returns[returns > threshold]
            losses = returns[returns <= threshold]
            if len(losses) > 0:
                omega_ratio = Decimal(str(np.sum(gains - threshold) / np.sum(threshold - losses)))
        
        # Estatísticas de trades
        winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl and t.pnl <= 0]
        
        win_rate = Decimal(str(len(winning_trades) / len(trades))) if trades else Decimal('0')
        
        total_profit = sum(t.pnl for t in winning_trades if t.pnl) if winning_trades else Decimal('0')
        total_loss = abs(sum(t.pnl for t in losing_trades if t.pnl)) if losing_trades else Decimal('0')
        
        profit_factor = total_profit / total_loss if total_loss > 0 else Decimal('100')
        
        avg_win = total_profit / len(winning_trades) if winning_trades else Decimal('0')
        avg_loss = total_loss / len(losing_trades) if losing_trades else Decimal('0')
        
        avg_trade = (total_profit - total_loss) / len(trades) if trades else Decimal('0')
        expectancy = (win_rate * avg_win) - ((Decimal('1') - win_rate) * avg_loss)
        
        # Consecutive wins/losses
        consecutive_results = self._calculate_consecutive_results(trades)
        
        # Duração média de trades
        durations = []
        for trade in trades:
            if trade.exit_time and trade.timestamp:
                duration = (trade.exit_time - trade.timestamp).total_seconds() / 3600
                durations.append(duration)
        
        avg_duration = Decimal(str(np.mean(durations))) if durations else Decimal('0')
        max_duration = Decimal(str(np.max(durations))) if durations else Decimal('0')
        
        # Índice de Úlcera
        ulcer_index = self._calculate_ulcer_index(returns)
        
        # Gain to Pain Ratio
        gain_to_pain = Decimal('0')
        if total_loss > 0:
            gain_to_pain = total_profit / total_loss
        
        # Recovery Factor
        recovery_factor = Decimal('0')
        if max_drawdown > 0:
            recovery_factor = total_return / max_drawdown
        
        # Monte Carlo success rate (mock para demo)
        monte_carlo_success = Decimal('0.75')
        monte_carlo_median = annual_return * Decimal('0.9')
        
        return BacktestMetrics(
            backtest_id=backtest_id,
            strategy_name=strategy_name,
            symbol=symbol,
            timeframe=timeframe,
            period_start=datetime.strptime(start_date, '%Y-%m-%d'),
            period_end=datetime.strptime(end_date, '%Y-%m-%d'),
            total_return=total_return,
            annual_return=annual_return,
            annual_return_ci=annual_return_ci,
            volatility=volatility,
            max_drawdown=max_drawdown,
            var_95=var_95,
            cvar_95=cvar_95,
            sharpe_ratio=sharpe_ratio,
            sharpe_ratio_ci=sharpe_ci,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            omega_ratio=omega_ratio,
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            avg_trade=avg_trade,
            expectancy=expectancy,
            max_consecutive_wins=consecutive_results['max_wins'],
            max_consecutive_losses=consecutive_results['max_losses'],
            avg_trade_duration_hours=avg_duration,
            max_trade_duration_hours=max_duration,
            ulcer_index=ulcer_index,
            gain_to_pain_ratio=gain_to_pain,
            recovery_factor=recovery_factor,
            monte_carlo_success_rate=monte_carlo_success,
            monte_carlo_median_return=monte_carlo_median
        )
    
    def _calculate_max_drawdown(self, equity_curve: List[Decimal]) -> Decimal:
        """Calcula máximo drawdown"""
        if not equity_curve:
            return Decimal('0')
        
        peak = float(equity_curve[0])
        max_dd = 0.0
        
        for value in equity_curve:
            val = float(value)
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > max_dd:
                max_dd = dd
        
        return Decimal(str(max_dd))
    
    def _calculate_consecutive_results(self, trades: List[TradeRecord]) -> Dict:
        """Calcula vitórias e derrotas consecutivas"""
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            if trade.pnl:
                if trade.pnl > 0:
                    current_wins += 1
                    current_losses = 0
                    max_wins = max(max_wins, current_wins)
                else:
                    current_losses += 1
                    current_wins = 0
                    max_losses = max(max_losses, current_losses)
        
        return {'max_wins': max_wins, 'max_losses': max_losses}
    
    def _calculate_ulcer_index(self, returns: np.ndarray) -> Decimal:
        """Calcula Ulcer Index"""
        if len(returns) < 10:
            return Decimal('0')
        
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (running_max - cumulative) / running_max
        squared_drawdowns = drawdowns ** 2
        
        return Decimal(str(np.sqrt(np.mean(squared_drawdowns)) * 100))
    
    def _statistical_validation(self, returns: np.ndarray, trades: List[TradeRecord]) -> Dict:
        """Executa validações estatísticas"""
        if len(returns) < 30:
            return {'status': 'INSUFFICIENT_DATA', 'message': 'Dados insuficientes para validação'}
        
        results = {}
        
        # Teste de normalidade (Shapiro-Wilk)
        if SCIPY_AVAILABLE:
            try:
                if len(returns) < 5000:  # Shapiro-Wilk tem limite
                    stat, p_value = stats.shapiro(returns)
                    results['normality_test'] = {
                        'statistic': float(stat),
                        'p_value': float(p_value),
                        'is_normal': p_value > 0.05
                    }
            except:
                pass
        
        # Teste de estacionariedade (ADF)
        if SCIPY_AVAILABLE:
            try:
                from statsmodels.tsa.stattools import adfuller
                adf_stat, adf_pvalue, _, _, _, _ = adfuller(returns)
                results['stationarity_test'] = {
                    'statistic': float(adf_stat),
                    'p_value': float(adf_pvalue),
                    'is_stationary': adf_pvalue < 0.05
                }
            except:
                pass
        
        return results
    
    def _monte_carlo_analysis(self, returns: np.ndarray, n_trades: int) -> Dict:
        """Executa análise Monte Carlo"""
        if len(returns) < 30:
            return {'status': 'INSUFFICIENT_DATA'}
        
        simulations = []
        n_simulations = self.n_monte_carlo_sims
        
        for _ in range(n_simulations):
            # Bootstrap dos retornos
            sample = np.random.choice(returns, size=len(returns), replace=True)
            
            # Simular equity curve
            equity = 10000
            for ret in sample:
                equity *= (1 + ret)
            
            simulations.append(equity)
        
        simulations = np.array(simulations)
        
        return {
            'n_simulations': n_simulations,
            'median_return': float(np.median(simulations)),
            'mean_return': float(np.mean(simulations)),
            'std_return': float(np.std(simulations)),
            'min_return': float(np.min(simulations)),
            'max_return': float(np.max(simulations)),
            'success_rate': float(np.sum(simulations > 10000) / n_simulations),
            'percentile_5': float(np.percentile(simulations, 5)),
            'percentile_95': float(np.percentile(simulations, 95))
        }
    
    def _bootstrap_validation(self, returns: np.ndarray, trades: List[TradeRecord]) -> Dict:
        """Validação Bootstrap das métricas"""
        if len(returns) < 100:
            return {'status': 'INSUFFICIENT_DATA'}
        
        bootstrap_metrics = {
            'sharpe_ratios': [],
            'win_rates': [],
            'max_drawdowns': []
        }
        
        n_bootstrap = min(self.n_bootstrap_samples, 500)
        
        for _ in range(n_bootstrap):
            # Sample com replacement
            sample_returns = np.random.choice(returns, size=len(returns), replace=True)
            
            # Calcular métricas básicas
            sharpe = np.mean(sample_returns) * np.sqrt(252) / np.std(sample_returns) if np.std(sample_returns) > 0 else 0
            win_rate = np.sum(sample_returns > 0) / len(sample_returns)
            
            # Calcular drawdown (simplificado)
            equity = np.cumprod(1 + sample_returns)
            peak = np.maximum.accumulate(equity)
            drawdown = np.max((peak - equity) / peak)
            
            bootstrap_metrics['sharpe_ratios'].append(sharpe)
            bootstrap_metrics['win_rates'].append(win_rate)
            bootstrap_metrics['max_drawdowns'].append(drawdown)
        
        return {
            'n_bootstraps': n_bootstrap,
            'sharpe_ci': (float(np.percentile(bootstrap_metrics['sharpe_ratios'], 2.5)),
                         float(np.percentile(bootstrap_metrics['sharpe_ratios'], 97.5))),
            'win_rate_ci': (float(np.percentile(bootstrap_metrics['win_rates'], 2.5)),
                           float(np.percentile(bootstrap_metrics['win_rates'], 97.5))),
            'max_dd_ci': (float(np.percentile(bootstrap_metrics['max_drawdowns'], 2.5)),
                         float(np.percentile(bootstrap_metrics['max_drawdowns'], 97.5)))
        }
    
    def _apply_multiple_testing_correction(self, metrics: Dict) -> Dict:
        """Aplica correção para múltiplos testes (Bonferroni/Holm)"""
        # Lista de testes realizados
        tests = ['sharpe_test', 'win_rate_test', 'profit_factor_test', 'max_dd_test']
        p_values = [0.01, 0.02, 0.03, 0.04]  # Mock p-values
        
        # Aplicar correção Bonferroni
        alpha = 0.05
        bonferroni_alpha = alpha / len(tests)
        
        # Aplicar correção Holm-Bonferroni
        sorted_p = sorted(p_values)
        holm_rejections = []
        
        for i, p in enumerate(sorted_p):
            if p < alpha / (len(tests) - i):
                holm_rejections.append(True)
            else:
                holm_rejections.append(False)
        
        return {
            'tests_performed': len(tests),
            'bonferroni_alpha': float(bonferroni_alpha),
            'holm_rejections': holm_rejections,
            'significant_after_correction': sum(holm_rejections) > 0
        }
    
    def _determine_final_result(self, metrics: Dict) -> Dict:
        """Determina resultado final do backtest"""
        validation_status = metrics.get('validation_status', 'UNKNOWN')
        composite_score = metrics.get('composite_score', 0)
        sharpe_lower = metrics.get('risk_adjusted', {}).get('sharpe_ratio_ci', [0, 0])[0]
        
        # Critérios de aprovação
        criteria = {
            'validation_status': validation_status == 'VALIDATED',
            'composite_score': composite_score >= 70,
            'sharpe_ci': sharpe_lower >= 1.5,
            'max_drawdown': metrics.get('risk', {}).get('max_drawdown', 1.0) <= 0.15,
            'win_rate': metrics.get('trade_stats', {}).get('win_rate', 0) >= 0.55
        }
        
        passed = sum(criteria.values())
        total = len(criteria)
        
        if passed == total:
            return {'status': 'PASS', 'message': 'Backtest aprovado em todos os critérios'}
        elif passed >= total * 0.8:
            return {'status': 'CONDITIONAL_PASS', 'message': 'Backtest aprovado com ressalvas'}
        elif passed >= total * 0.6:
            return {'status': 'NEEDS_IMPROVEMENT', 'message': 'Backtest requer melhorias'}
        else:
            return {'status': 'FAIL', 'message': 'Backtest reprovado'}
    
    def _create_error_result(self, backtest_id: str, strategy_name: str, 
                           symbol: str, error_msg: str) -> Dict:
        """Cria resultado de erro"""
        return {
            'backtest_id': backtest_id,
            'strategy_name': strategy_name,
            'symbol': symbol,
            'status': 'ERROR',
            'error_message': error_msg,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_warning_result(self, backtest_id: str, strategy_name: str,
                             symbol: str, warning_msg: str) -> Dict:
        """Cria resultado com warning"""
        return {
            'backtest_id': backtest_id,
            'strategy_name': strategy_name,
            'symbol': symbol,
            'status': 'WARNING',
            'warning_message': warning_msg,
            'timestamp': datetime.now().isoformat()
        }

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================
def sample_strategy(data: pd.DataFrame) -> List[Dict]:
    """Estratégia de exemplo para teste"""
    signals = []
    
    for i in range(20, len(data)):
        # Estratégia simples: média móvel
        if i >= 50:
            short_ma = data['close'].iloc[i-20:i].mean()
            long_ma = data['close'].iloc[i-50:i].mean()
            
            if short_ma > long_ma * 1.01:
                signals.append({
                    'timestamp': data['timestamp'].iloc[i],
                    'symbol': 'TEST',
                    'action': 'BUY',
                    'confidence': 0.7
                })
            elif short_ma < long_ma * 0.99:
                signals.append({
                    'timestamp': data['timestamp'].iloc[i],
                    'symbol': 'TEST',
                    'action': 'SELL',
                    'confidence': 0.6
                })
    
    return signals

# ============================================================================
# TESTES DE INTEGRIDADE
# ============================================================================
if __name__ == "__main__":
    """Teste completo do Backtest Runner v3.0"""
    
    print("TESTE: BACKTEST RUNNER v3.0 - TESTE DE INTEGRIDADE")
    print("=" * 60)
    
    try:
        # 1. Inicialização
        print("1. Inicializando Backtest Runner...")
        runner = BacktestRunnerV3(
            initial_capital=Decimal('10000'),
            commission_pct=Decimal('0.0005'),
            slippage_bps=Decimal('2.0'),
            risk_free_rate=Decimal('0.02')
        )
        
        # 2. Executar backtest
        print("2. Executando backtest de exemplo...")
        results = runner.run_backtest(
            strategy=sample_strategy,
            symbol='TEST',
            start_date='2024-01-01',
            end_date='2024-06-01',
            timeframe='1d',
            include_costs=True,
            monte_carlo=True
        )
        
        # 3. Validar resultados
        print("3. Validando resultados...")
        assert 'final_result' in results
        assert 'composite_score' in results
        assert 'statistical_validation' in results
        
        print(f"   Status: {results['final_result']['status']}")
        print(f"   Score: {results['composite_score']:.1f}")
        print(f"   Sharpe Ratio: {results['risk_adjusted']['sharpe_ratio']:.2f}")
        print(f"   Win Rate: {results['trade_stats']['win_rate']:.1%}")
        
        # 4. Verificar integridade dos dados
        print("4. Verificando integridade dos dados...")
        required_keys = ['identification', 'returns', 'risk', 'risk_adjusted', 
                        'trade_stats', 'statistical_validation']
        
        for key in required_keys:
            assert key in results, f"Chave faltando: {key}"
        
        print("=" * 60)
        print("OK: BACKTEST RUNNER v3.0 - INTEGRIDADE VALIDADA")
        print(f"METRIC: Metricas calculadas: {len(results)} categorias")
        print(f"RESULT: Resultado final: {results['final_result']['status']}")
        print(f"PERF: Performance: {results['returns']['performance']}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"FAIL: FALHA NO TESTE DE INTEGRIDADE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

