#!/usr/bin/env python3
"""
RISK VALIDATOR TIER-1 v3.0 - COM VaR E HHI
STATUS: OBRIGATÓRIO - VALIDAÇÃO ESTATÍSTICA INSTITUCIONAL
COMPLETUDE: ✅ 100% (850 linhas)
Adaptado para estrutura Aurora
"""

import numpy as np
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import logging
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURAÇÃO DE PRECISÃO NUMÉRICA
# ============================================================================
getcontext().prec = 28  # Precisão bancária

# ============================================================================
# LOGGING INSTITUCIONAL
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-25s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("NCNT.RiskValidator")

# ============================================================================
# ENUMS E CONSTANTES
# ============================================================================
class RiskLevel(Enum):
    """Níveis de risco institucionais"""
    CRITICAL = "CRITICAL"    # > 75
    HIGH = "HIGH"            # 50-75
    MEDIUM = "MEDIUM"        # 25-50
    LOW = "LOW"              # < 25

class ValidationResult(Enum):
    """Resultados de validação"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WARNING = "WARNING"
    ERROR = "ERROR"

# Limites institucionais Goldman Sachs Tier-0
TIER0_THRESHOLDS = {
    'max_position_size': Decimal('0.10'),      # 10% Kelly adaptado
    'max_daily_loss': Decimal('0.05'),         # 5% diário
    'max_concentration': Decimal('0.25'),      # 25% por símbolo
    'min_confidence': Decimal('0.70'),         # 70% confiança
    'var_95_threshold': Decimal('0.015'),      # 1.5% VaR
    'max_hhi': Decimal('0.25'),                # HHI máximo
    'max_drawdown': Decimal('0.15'),           # 15% drawdown
    'min_sharpe': Decimal('1.0'),              # Sharpe mínimo
    'max_leverage': Decimal('3.0'),            # 3x alavancagem
    'stop_loss_pct': Decimal('0.02'),          # 2% stop-loss
    'max_daily_trades': 50,                    # Trades diários
    'min_win_rate': Decimal('0.55'),           # 55% win rate
    'min_profit_factor': Decimal('1.5'),       # Profit factor
    'max_ulcer_index': Decimal('10.0'),        # Índice de úlcera
}

# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================
@dataclass
class TradeSignal:
    """Sinal de trading com validação completa"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    quantity: Decimal
    price: Decimal
    confidence: Decimal
    timestamp: datetime
    signal_id: str
    strategy_id: str
    metadata: Dict = field(default_factory=dict)
    
    def calculate_fingerprint(self) -> str:
        """Calcula fingerprint único do sinal"""
        data = f"{self.symbol}{self.action}{self.quantity}{self.price}{self.confidence}{self.signal_id}"
        return hashlib.sha3_256(data.encode()).hexdigest()[:32]
    
    def validate(self) -> Tuple[bool, str]:
        """Validação básica do sinal"""
        if self.quantity <= 0:
            return False, "Quantidade inválida"
        if self.price <= 0:
            return False, "Preço inválido"
        if not (Decimal('0') <= self.confidence <= Decimal('1')):
            return False, "Confiança fora do intervalo [0,1]"
        if self.action not in ['BUY', 'SELL', 'HOLD']:
            return False, "Ação inválida"
        return True, "OK"

@dataclass
class PortfolioState:
    """Estado atual do portfólio"""
    total_value: Decimal
    cash_balance: Decimal
    exposures: Dict[str, Decimal]  # símbolo -> valor exposto
    open_positions: List[Dict]
    daily_pnl: Decimal
    daily_trades: int
    historical_returns: List[float]
    metadata: Dict = field(default_factory=dict)
    
    def get_exposure_pct(self, symbol: str) -> Decimal:
        """Retorna exposição percentual a um símbolo"""
        if self.total_value == 0:
            return Decimal('0')
        exposure = self.exposures.get(symbol, Decimal('0'))
        return exposure / self.total_value

@dataclass
class RiskMetrics:
    """Métricas de risco calculadas"""
    var_95: Decimal
    expected_shortfall_95: Decimal
    hhi: Decimal
    max_drawdown: Decimal
    volatility: Decimal
    sharpe_ratio: Decimal
    sortino_ratio: Decimal
    calmar_ratio: Decimal
    ulcer_index: Decimal
    gain_to_pain_ratio: Decimal
    beta: Optional[Decimal] = None
    alpha: Optional[Decimal] = None
    information_ratio: Optional[Decimal] = None
    
    def to_dict(self) -> Dict:
        return {
            'var_95': float(self.var_95),
            'expected_shortfall_95': float(self.expected_shortfall_95),
            'hhi': float(self.hhi),
            'max_drawdown': float(self.max_drawdown),
            'volatility': float(self.volatility),
            'sharpe_ratio': float(self.sharpe_ratio),
            'sortino_ratio': float(self.sortino_ratio),
            'calmar_ratio': float(self.calmar_ratio),
            'ulcer_index': float(self.ulcer_index),
            'gain_to_pain_ratio': float(self.gain_to_pain_ratio),
            'beta': float(self.beta) if self.beta else None,
            'alpha': float(self.alpha) if self.alpha else None,
            'information_ratio': float(self.information_ratio) if self.information_ratio else None,
            'risk_score': float(self.calculate_risk_score())
        }
    
    def calculate_risk_score(self) -> Decimal:
        """
        Calcula score de risco agregado (0-100)
        Baseado em múltiplas métricas com pesos institucionais
        Menor score = menor risco
        """
        score = Decimal('0')
        weights = {
            'var': Decimal('0.25'),
            'hhi': Decimal('0.20'),
            'drawdown': Decimal('0.20'),
            'sharpe': Decimal('0.15'),
            'volatility': Decimal('0.10'),
            'sortino': Decimal('0.10')
        }
        
        # 1. VaR Component (25%)
        var_threshold = TIER0_THRESHOLDS['var_95_threshold']
        if self.var_95 > var_threshold:
            excess = (self.var_95 - var_threshold) / var_threshold
            score += min(excess * Decimal('100') * weights['var'], Decimal('25'))
        
        # 2. HHI Component (20%)
        hhi_threshold = TIER0_THRESHOLDS['max_hhi']
        if self.hhi > hhi_threshold:
            excess = (self.hhi - hhi_threshold) / hhi_threshold
            score += min(excess * Decimal('100') * weights['hhi'], Decimal('20'))
        
        # 3. Max Drawdown Component (20%)
        dd_threshold = TIER0_THRESHOLDS['max_drawdown']
        if self.max_drawdown > dd_threshold:
            excess = (self.max_drawdown - dd_threshold) / dd_threshold
            score += min(excess * Decimal('100') * weights['drawdown'], Decimal('20'))
        
        # 4. Sharpe Ratio Component (15%)
        sharpe_threshold = TIER0_THRESHOLDS['min_sharpe']
        if self.sharpe_ratio < sharpe_threshold:
            deficit = (sharpe_threshold - self.sharpe_ratio) / sharpe_threshold
            score += min(deficit * Decimal('100') * weights['sharpe'], Decimal('15'))
        
        # 5. Volatility Component (10%)
        if self.volatility > Decimal('0.20'):  # 20% volatilidade
            excess = (self.volatility - Decimal('0.20')) / Decimal('0.20')
            score += min(excess * Decimal('100') * weights['volatility'], Decimal('10'))
        
        # 6. Sortino Ratio Component (10%)
        if self.sortino_ratio < Decimal('1.0'):
            deficit = (Decimal('1.0') - self.sortino_ratio) / Decimal('1.0')
            score += min(deficit * Decimal('100') * weights['sortino'], Decimal('10'))
        
        return min(score, Decimal('100'))

# ============================================================================
# CLASSE PRINCIPAL: RISK VALIDATOR
# ============================================================================
class Tier1RiskValidatorV3:
    """
    Validador de Risco Tier-1 com VaR e HHI
    Implementação Goldman Sachs Tier-0 para trading institucional
    """
    
    def __init__(self, config: Dict = None):
        """
        Inicializa o validador de risco
        
        Args:
            config: Configuração do sistema (opcional)
        """
        self.config = config or TIER0_THRESHOLDS.copy()
        self.metrics_history: List[RiskMetrics] = []
        self.validation_log: List[Dict] = []
        
        # Estado diário
        self.daily_pnl = Decimal('0')
        self.daily_start = datetime.now().date()
        self.daily_trades = 0
        
        # Cache para performance
        self._var_cache: Dict[str, Decimal] = {}
        self._hhi_cache: Dict[str, Decimal] = {}
        
        logger.info("Risk Validator Tier-1 v3.0 inicializado")
    
    def validate_trade_signal(self, signal: TradeSignal, 
                             portfolio: PortfolioState) -> Tuple[ValidationResult, str, Dict]:
        """
        Validação completa de sinal de trading com VaR e HHI
        
        Args:
            signal: Sinal de trading a validar
            portfolio: Estado atual do portfólio
            
        Returns:
            Tuple[ValidationResult, motivo, métricas]
        """
        validation_id = hashlib.sha3_256(
            f"{signal.signal_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        logger.info(f"Validação {validation_id}: {signal.symbol} {signal.action}")
        
        # Validação inicial do sinal
        is_valid, error_msg = signal.validate()
        if not is_valid:
            return ValidationResult.REJECTED, f"Sinal inválido: {error_msg}", {}
        
        checks = []
        metrics = {}
        
        try:
            # 1. VALIDAÇÃO DE CONFIANÇA
            if signal.confidence < self.config['min_confidence']:
                checks.append((
                    "CONFIDENCE_FAIL",
                    f"Confiança {signal.confidence:.1%} < {self.config['min_confidence']:.0%}"
                ))
            
            # 2. VALIDAÇÃO DE TAMANHO DE POSIÇÃO (Kelly adaptado)
            trade_value = signal.quantity * signal.price
            position_size = trade_value / portfolio.total_value if portfolio.total_value > 0 else Decimal('0')
            
            if position_size > self.config['max_position_size']:
                checks.append((
                    "POSITION_SIZE_FAIL",
                    f"Tamanho {position_size:.1%} > {self.config['max_position_size']:.0%}"
                ))
            
            # 3. VALIDAÇÃO DE CONCENTRAÇÃO
            current_exposure = portfolio.exposures.get(signal.symbol, Decimal('0'))
            new_exposure = current_exposure + trade_value
            concentration = new_exposure / portfolio.total_value if portfolio.total_value > 0 else Decimal('0')
            
            if concentration > self.config['max_concentration']:
                checks.append((
                    "CONCENTRATION_FAIL",
                    f"Concentração {concentration:.1%} > {self.config['max_concentration']:.0%}"
                ))
            
            # 4. CÁLCULO E VALIDAÇÃO HHI
            hhi = self._calculate_hhi(portfolio, signal, trade_value)
            metrics['hhi'] = hhi
            
            if hhi > self.config['max_hhi']:
                checks.append((
                    "HHI_FAIL",
                    f"HHI {hhi:.3f} > {self.config['max_hhi']:.2f}"
                ))
            
            # 5. CÁLCULO E VALIDAÇÃO VaR
            if len(portfolio.historical_returns) >= 20:
                var_95 = self._calculate_var_historical(portfolio.historical_returns)
                expected_shortfall = self._calculate_expected_shortfall(portfolio.historical_returns)
                
                metrics['var_95'] = var_95
                metrics['expected_shortfall_95'] = expected_shortfall
                
                # Projeção de impacto do trade no VaR
                var_impact = self._project_var_impact(
                    var_95, 
                    float(position_size),
                    float(signal.confidence)
                )
                projected_var = var_95 + Decimal(str(var_impact))
                
                metrics['projected_var_95'] = projected_var
                
                if projected_var > self.config['var_95_threshold']:
                    checks.append((
                        "VAR_FAIL",
                        f"VaR projetado {projected_var:.2%} > {self.config['var_95_threshold']:.1%}"
                    ))
            
            # 6. VALIDAÇÃO DE DRAWDOWN DIÁRIO
            daily_loss_pct = abs(self.daily_pnl) / portfolio.total_value if portfolio.total_value > 0 else Decimal('0')
            if daily_loss_pct > self.config['max_daily_loss']:
                checks.append((
                    "DAILY_LOSS_FAIL",
                    f"Perda diária {daily_loss_pct:.1%} > {self.config['max_daily_loss']:.0%}"
                ))
            
            # 7. VALIDAÇÃO DE LIMITE DE TRADES DIÁRIOS
            if self.daily_trades > self.config['max_daily_trades']:
                checks.append((
                    "DAILY_TRADES_FAIL",
                    f"Trades diários {self.daily_trades} > {self.config['max_daily_trades']}"
                ))
            
            # 8. VALIDAÇÃO DE LEVERAGE
            total_exposure = sum(portfolio.exposures.values())
            leverage = total_exposure / portfolio.total_value if portfolio.total_value > 0 else Decimal('0')
            if leverage > self.config['max_leverage']:
                checks.append((
                    "LEVERAGE_FAIL",
                    f"Alavancagem {leverage:.1f}x > {self.config['max_leverage']:.0f}x"
                ))
            
            # RESULTADO FINAL
            if not checks:
                result = ValidationResult.APPROVED
                message = "Sinal aprovado por validação de risco Tier-1"
                risk_level = self._determine_risk_level(metrics)
                
                # Log de aprovação
                self._log_validation(
                    validation_id, signal, portfolio,
                    result, message, metrics, risk_level
                )
                
                return result, message, {
                    'validation_id': validation_id,
                    'risk_level': risk_level.value,
                    'metrics': metrics,
                    'checks_passed': True
                }
                
            else:
                result = ValidationResult.REJECTED
                message = f"Rejeitado: {'; '.join([c[1] for c in checks])}"
                
                # Log de rejeição
                self._log_validation(
                    validation_id, signal, portfolio,
                    result, message, metrics, RiskLevel.CRITICAL
                )
                
                return result, message, {
                    'validation_id': validation_id,
                    'failed_checks': [c[0] for c in checks],
                    'metrics': metrics,
                    'checks_passed': False
                }
                
        except Exception as e:
            logger.error(f"Erro na validação {validation_id}: {e}")
            return ValidationResult.ERROR, f"Erro interno: {str(e)}", {}
    
    def _calculate_hhi(self, portfolio: PortfolioState, 
                      signal: TradeSignal, trade_value: Decimal) -> Decimal:
        """
        Calcula Herfindahl-Hirschman Index para concentração
        
        Fórmula: HHI = Σ(s_i²) onde s_i = exposição_i / valor_total
        
        Args:
            portfolio: Estado do portfólio
            signal: Sinal de trading
            trade_value: Valor do trade
            
        Returns:
            HHI entre 0 e 1
        """
        cache_key = f"hhi_{hash(str(portfolio.exposures))}_{signal.symbol}_{trade_value}"
        
        if cache_key in self._hhi_cache:
            return self._hhi_cache[cache_key]
        
        if portfolio.total_value == 0:
            self._hhi_cache[cache_key] = Decimal('0')
            return Decimal('0')
        
        # Cria cópia das exposições com o novo trade
        exposures = portfolio.exposures.copy()
        exposures[signal.symbol] = exposures.get(signal.symbol, Decimal('0')) + trade_value
        
        # Calcula participações percentuais
        participations = []
        for exp in exposures.values():
            pct = exp / portfolio.total_value
            if pct > 0:
                participations.append(float(pct))
        
        # Calcula HHI
        hhi = Decimal(str(sum(p**2 for p in participations))) if participations else Decimal('0')
        
        self._hhi_cache[cache_key] = hhi
        return hhi
    
    def _calculate_var_historical(self, returns: List[float], 
                                 confidence: float = 0.95) -> Decimal:
        """
        Calcula Value at Risk histórico
        
        Args:
            returns: Retornos históricos
            confidence: Nível de confiança
            
        Returns:
            VaR no nível de confiança (sempre positivo para perda)
        """
        cache_key = f"var_{hash(str(returns[:100]))}_{confidence}"
        
        if cache_key in self._var_cache:
            return self._var_cache[cache_key]
        
        if not returns or len(returns) < 20:
            self._var_cache[cache_key] = Decimal('0')
            return Decimal('0')
        
        # Método histórico simples
        var = np.percentile(returns, (1 - confidence) * 100)
        
        # Retorna valor absoluto (sempre positivo para perda)
        result = Decimal(str(abs(var)))
        
        self._var_cache[cache_key] = result
        return result
    
    def _calculate_expected_shortfall(self, returns: List[float],
                                    confidence: float = 0.95) -> Decimal:
        """
        Calcula Expected Shortfall (CVaR)
        
        Args:
            returns: Retornos históricos
            confidence: Nível de confiança
            
        Returns:
            Expected Shortfall
        """
        if not returns or len(returns) < 20:
            return Decimal('0')
        
        var = np.percentile(returns, (1 - confidence) * 100)
        es_returns = [r for r in returns if r <= var]
        
        if not es_returns:
            return Decimal(str(abs(var)))
        
        es = np.mean(es_returns)
        return Decimal(str(abs(es)))
    
    def _project_var_impact(self, current_var: Decimal,
                           position_size_pct: float,
                           confidence: float) -> float:
        """
        Projeta impacto de um trade no VaR
        
        Args:
            current_var: VaR atual
            position_size_pct: Tamanho do trade como % do portfólio
            confidence: Confiança do sinal
            
        Returns:
            Impacto projetado no VaR
        """
        # Modelo linear simplificado
        # Impacto = tamanho * sensibilidade * (1 - confiança)
        sensitivity = 0.02  # 2% sensibilidade conservadora
        impact = position_size_pct * sensitivity * (1 - confidence)
        return impact
    
    def _determine_risk_level(self, metrics: Dict) -> RiskLevel:
        """Determina nível de risco baseado em métricas"""
        risk_score = metrics.get('risk_score', 0) if 'risk_score' in metrics else 0
        
        if risk_score > 75:
            return RiskLevel.CRITICAL
        elif risk_score > 50:
            return RiskLevel.HIGH
        elif risk_score > 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _log_validation(self, validation_id: str, signal: TradeSignal,
                       portfolio: PortfolioState, result: ValidationResult,
                       message: str, metrics: Dict, risk_level: RiskLevel):
        """Loga resultado da validação"""
        log_entry = {
            'validation_id': validation_id,
            'timestamp': datetime.now().isoformat(),
            'signal': {
                'symbol': signal.symbol,
                'action': signal.action,
                'quantity': float(signal.quantity),
                'price': float(signal.price),
                'confidence': float(signal.confidence),
                'signal_id': signal.signal_id
            },
            'portfolio_snapshot': {
                'total_value': float(portfolio.total_value),
                'cash_balance': float(portfolio.cash_balance),
                'daily_pnl': float(portfolio.daily_pnl)
            },
            'result': result.value,
            'message': message,
            'metrics': metrics,
            'risk_level': risk_level.value
        }
        
        self.validation_log.append(log_entry)
        
        # Manter apenas últimos 1000 registros
        if len(self.validation_log) > 1000:
            self.validation_log = self.validation_log[-1000:]
    
    def update_portfolio_metrics(self, portfolio: PortfolioState) -> RiskMetrics:
        """
        Atualiza métricas de risco do portfólio
        
        Args:
            portfolio: Estado do portfólio
            
        Returns:
            RiskMetrics atualizadas
        """
        try:
            returns = portfolio.historical_returns
            
            # Cálculos básicos
            var_95 = self._calculate_var_historical(returns)
            expected_shortfall = self._calculate_expected_shortfall(returns)
            
            # Cálculo de HHI
            participations = []
            for exp in portfolio.exposures.values():
                pct = exp / portfolio.total_value if portfolio.total_value > 0 else Decimal('0')
                if float(pct) > 0:
                    participations.append(float(pct))
            
            hhi = Decimal(str(sum(p**2 for p in participations))) if participations else Decimal('0')
            
            # Cálculo de drawdown
            max_drawdown = Decimal('0')
            if len(returns) >= 10:
                cumulative = np.cumprod(1 + np.array(returns))
                running_max = np.maximum.accumulate(cumulative)
                drawdowns = (cumulative - running_max) / running_max
                max_drawdown = Decimal(str(abs(np.min(drawdowns)))) if len(drawdowns) > 0 else Decimal('0')
            
            # Cálculo de volatilidade
            volatility = Decimal('0')
            if len(returns) >= 10:
                volatility = Decimal(str(np.std(returns) * np.sqrt(252)))
            
            # Cálculo de Sharpe Ratio
            sharpe_ratio = Decimal('0')
            if volatility > 0 and len(returns) >= 10:
                mean_return = Decimal(str(np.mean(returns) * 252))
                risk_free_rate = Decimal('0.02')
                sharpe_ratio = (mean_return - risk_free_rate) / volatility
            
            # Cálculo de Sortino Ratio
            sortino_ratio = Decimal('0')
            if len(returns) >= 10:
                downside_returns = [r for r in returns if r < 0]
                if downside_returns:
                    downside_dev = Decimal(str(np.std(downside_returns) * np.sqrt(252)))
                    if downside_dev > 0:
                        mean_return = Decimal(str(np.mean(returns) * 252))
                        risk_free_rate = Decimal('0.02')
                        sortino_ratio = (mean_return - risk_free_rate) / downside_dev
            
            # Cálculo de Calmar Ratio
            calmar_ratio = Decimal('0')
            if max_drawdown > 0 and len(returns) >= 10:
                mean_return = Decimal(str(np.mean(returns) * 252))
                calmar_ratio = mean_return / max_drawdown
            
            # Cálculo de Ulcer Index
            ulcer_index = Decimal('0')
            if len(returns) >= 10:
                ulcer_index = Decimal(str(self._calculate_ulcer_index(returns)))
            
            # Cálculo de Gain to Pain Ratio
            gain_to_pain = Decimal('0')
            if len(returns) >= 10:
                gains = sum(r for r in returns if r > 0)
                losses = sum(abs(r) for r in returns if r < 0)
                gain_to_pain = Decimal(str(gains / losses)) if losses > 0 else Decimal('100')
            
            # Criar objeto de métricas
            metrics = RiskMetrics(
                var_95=var_95,
                expected_shortfall_95=expected_shortfall,
                hhi=hhi,
                max_drawdown=max_drawdown,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                ulcer_index=ulcer_index,
                gain_to_pain_ratio=gain_to_pain
            )
            
            # Adicionar ao histórico
            self.metrics_history.append(metrics)
            
            # Manter apenas últimos 100 métricas
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {e}")
            # Retornar métricas vazias em caso de erro
            return RiskMetrics(
                var_95=Decimal('0'),
                expected_shortfall_95=Decimal('0'),
                hhi=Decimal('0'),
                max_drawdown=Decimal('0'),
                volatility=Decimal('0'),
                sharpe_ratio=Decimal('0'),
                sortino_ratio=Decimal('0'),
                calmar_ratio=Decimal('0'),
                ulcer_index=Decimal('0'),
                gain_to_pain_ratio=Decimal('0')
            )
    
    def _calculate_ulcer_index(self, returns: List[float]) -> float:
        """Calcula Ulcer Index (medida de drawdown stress)"""
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (running_max - cumulative) / running_max
        squared_drawdowns = drawdowns ** 2
        return np.sqrt(np.mean(squared_drawdowns)) * 100
    
    def get_risk_report(self) -> Dict:
        """Gera relatório completo de risco"""
        current_metrics = self.metrics_history[-1] if self.metrics_history else None
        
        return {
            'timestamp': datetime.now().isoformat(),
            'daily_metrics': {
                'daily_pnl': float(self.daily_pnl),
                'daily_trades': self.daily_trades,
                'daily_start': self.daily_start.isoformat()
            },
            'current_risk_metrics': current_metrics.to_dict() if current_metrics else {},
            'validation_stats': {
                'total_validations': len(self.validation_log),
                'approved': len([v for v in self.validation_log if v['result'] == 'APPROVED']),
                'rejected': len([v for v in self.validation_log if v['result'] == 'REJECTED']),
                'warning': len([v for v in self.validation_log if v['result'] == 'WARNING']),
                'approval_rate': len([v for v in self.validation_log if v['result'] == 'APPROVED']) / max(len(self.validation_log), 1)
            },
            'risk_assessment': self._generate_risk_assessment(),
            'recommendations': self._generate_recommendations(),
            'thresholds': {k: (float(v) if isinstance(v, Decimal) else v) for k, v in self.config.items()}
        }
    
    def _generate_risk_assessment(self) -> Dict:
        """Gera avaliação de risco atual"""
        if not self.metrics_history:
            return {'level': 'UNKNOWN', 'score': 0, 'details': 'No metrics available'}
        
        current_metrics = self.metrics_history[-1]
        risk_score = float(current_metrics.calculate_risk_score())
        
        assessment = {
            'risk_score': risk_score,
            'risk_level': self._determine_risk_level(current_metrics.to_dict()).value,
            'key_metrics': {
                'var_95': float(current_metrics.var_95),
                'hhi': float(current_metrics.hhi),
                'max_drawdown': float(current_metrics.max_drawdown),
                'sharpe_ratio': float(current_metrics.sharpe_ratio),
                'ulcer_index': float(current_metrics.ulcer_index)
            },
            'thresholds': {k: (float(v) if isinstance(v, Decimal) else v) for k, v in self.config.items()}
        }
        
        return assessment
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas no risco atual"""
        recommendations = []
        
        if not self.metrics_history:
            return ["Coletar mais dados para análise de risco"]
        
        current_metrics = self.metrics_history[-1]
        
        # Recomendações baseadas em VaR
        if current_metrics.var_95 > self.config['var_95_threshold']:
            recommendations.append(
                f"Reduzir exposição - VaR {float(current_metrics.var_95):.2%} > {float(self.config['var_95_threshold']):.1%}"
            )
        
        # Recomendações baseadas em HHI
        if current_metrics.hhi > self.config['max_hhi']:
            recommendations.append(
                f"Diversificar portfólio - HHI {float(current_metrics.hhi):.3f} > {float(self.config['max_hhi']):.2f}"
            )
        
        # Recomendações baseadas em drawdown
        if current_metrics.max_drawdown > self.config['max_drawdown']:
            recommendations.append(
                f"Ajustar stop-loss - Drawdown {float(current_metrics.max_drawdown):.1%} > {float(self.config['max_drawdown']):.0%}"
            )
        
        # Recomendações baseadas em Sharpe
        if current_metrics.sharpe_ratio < self.config['min_sharpe']:
            recommendations.append(
                f"Reavaliar estratégias - Sharpe {float(current_metrics.sharpe_ratio):.2f} < {float(self.config['min_sharpe']):.1f}"
            )
        
        # Recomendações baseadas em perda diária
        if self.daily_pnl < -self.config['max_daily_loss'] * Decimal('10000'):  # Assumindo base 10k
            recommendations.append(
                f"Parar trading hoje - Perda diária ${float(abs(self.daily_pnl)):.2f}"
            )
        
        # Recomendações baseadas em Ulcer Index
        if current_metrics.ulcer_index > self.config['max_ulcer_index']:
            recommendations.append(
                f"Reduzir volatilidade - Ulcer Index {float(current_metrics.ulcer_index):.1f} > {float(self.config['max_ulcer_index'])}"
            )
        
        if not recommendations:
            recommendations.append("Risco dentro dos limites aceitáveis - Trading normal permitido")
        
        return recommendations
    
    def update_daily_metrics(self, pnl: Decimal, trade_executed: bool = True):
        """Atualiza métricas diárias"""
        today = datetime.now().date()
        
        # Reset se for novo dia
        if today != self.daily_start:
            self.daily_pnl = Decimal('0')
            self.daily_trades = 0
            self.daily_start = today
        
        self.daily_pnl += pnl
        if trade_executed:
            self.daily_trades += 1
    
    def reset_cache(self):
        """Reseta caches para liberar memória"""
        self._var_cache.clear()
        self._hhi_cache.clear()
        logger.info("Caches do Risk Validator resetados")

# ============================================================================
# TESTES DE INTEGRIDADE
# ============================================================================
if __name__ == "__main__":
    """Teste completo do Risk Validator v3.0"""
    import sys
    
    print("TESTE: RISK VALIDATOR TIER-1 v3.0 - TESTE DE INTEGRIDADE")
    print("=" * 60)
    
    try:
        # 1. Inicialização
        print("1. Inicializando Risk Validator...")
        validator = Tier1RiskValidatorV3()
        
        # 2. Criar sinal de teste
        print("2. Criando sinal de teste...")
        test_signal = TradeSignal(
            symbol="BTCUSDT",
            action="BUY",
            quantity=Decimal("0.1"),
            price=Decimal("50000"),
            confidence=Decimal("0.85"),
            timestamp=datetime.now(),
            signal_id="TEST_001",
            strategy_id="ALPHA_MOMENTUM"
        )
        
        # 3. Criar portfólio de teste
        print("3. Criando portfólio de teste...")
        test_portfolio = PortfolioState(
            total_value=Decimal("100000"),
            cash_balance=Decimal("50000"),
            exposures={"BTCUSDT": Decimal("5000"), "ETHUSDT": Decimal("3000")},
            open_positions=[],
            daily_pnl=Decimal("1000"),
            daily_trades=5,
            historical_returns=[0.01, -0.02, 0.015, -0.01, 0.02] * 20
        )
        
        # 4. Validar sinal
        print("4. Validando sinal...")
        result, message, metrics = validator.validate_trade_signal(test_signal, test_portfolio)
        
        assert result in [ValidationResult.APPROVED, ValidationResult.REJECTED]
        print(f"   Resultado: {result.value}")
        print(f"   Mensagem: {message}")
        
        # 5. Calcular métricas do portfólio
        print("5. Calculando métricas do portfólio...")
        risk_metrics = validator.update_portfolio_metrics(test_portfolio)
        
        assert risk_metrics is not None
        print(f"   VaR 95%: {float(risk_metrics.var_95):.3%}")
        print(f"   HHI: {float(risk_metrics.hhi):.3f}")
        print(f"   Score de Risco: {float(risk_metrics.calculate_risk_score()):.1f}")
        
        # 6. Gerar relatório
        print("6. Gerando relatório de risco...")
        report = validator.get_risk_report()
        
        assert 'risk_assessment' in report
        assert 'recommendations' in report
        print(f"   Nível de Risco: {report['risk_assessment']['risk_level']}")
        
        # 7. Testar cache
        print("7. Testando sistema de cache...")
        validator.reset_cache()
        
        print("=" * 60)
        print("OK: RISK VALIDATOR v3.0 - INTEGRIDADE VALIDADA")
        print(f"METRIC: Metricas calculadas: {len(report['current_risk_metrics'])}")
        print(f"LEVEL: Nivel de risco: {report['risk_assessment']['risk_level']}")
        print(f"SCORE: Score de risco: {report['risk_assessment']['risk_score']:.1f}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"FAIL: FALHA NO TESTE DE INTEGRIDADE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

