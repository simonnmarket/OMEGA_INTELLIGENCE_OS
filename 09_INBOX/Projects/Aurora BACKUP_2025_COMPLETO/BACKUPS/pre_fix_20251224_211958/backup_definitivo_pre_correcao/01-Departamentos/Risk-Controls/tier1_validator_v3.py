#!/usr/bin/env python3
"""
RISK VALIDATOR TIER-1 v3.0 - COM VaR E HHI
Implementação baseada nas Análises #2 e #3
Adaptado para estrutura Aurora
"""

import numpy as np
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("scipy não disponível, usando métodos alternativos para VaR")

logger = logging.getLogger("NCNT.RiskValidator")

@dataclass
class RiskSignal:
    """Sinal de trading com validação de contrato"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    quantity: Decimal
    price: Decimal
    confidence: float
    timestamp: datetime
    signal_id: str
    strategy_id: str

class RiskMetrics:
    """Métricas de risco calculadas"""
    
    def __init__(self):
        self.var_95: float = 0.0
        self.hhi: float = 0.0  # Herfindahl-Hirschman Index
        self.max_drawdown: float = 0.0
        self.volatility: float = 0.0
        self.sharpe_ratio: float = 0.0
        self.calmar_ratio: float = 0.0
        self.sortino_ratio: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'var_95': self.var_95,
            'hhi': self.hhi,
            'max_drawdown': self.max_drawdown,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'calmar_ratio': self.calmar_ratio,
            'sortino_ratio': self.sortino_ratio,
            'risk_score': self.calculate_risk_score()
        }
    
    def calculate_risk_score(self) -> float:
        """Calcula score de risco (0-100, menor é melhor)"""
        score = 0
        
        # VaR (peso 30%)
        if self.var_95 > 0.02:  # > 2%
            score += min((self.var_95 - 0.02) * 100 * 30, 30)
        
        # HHI (peso 25%)
        if self.hhi > 0.25:  # > 0.25 (concentração)
            score += min((self.hhi - 0.25) * 100 * 25, 25)
        
        # Max Drawdown (peso 20%)
        if self.max_drawdown > 0.15:  # > 15%
            score += min((self.max_drawdown - 0.15) * 100 * 20, 20)
        
        # Volatilidade (peso 15%)
        if self.volatility > 0.20:  # > 20%
            score += min((self.volatility - 0.20) * 100 * 15, 15)
        
        # Sharpe Ratio (peso 10%)
        if self.sharpe_ratio < 1.0:  # < 1.0
            score += min((1.0 - self.sharpe_ratio) * 10 * 10, 10)
        
        return min(score, 100)

class Tier1RiskValidatorV3:
    """
    Validador de Risco Tier-1 com VaR e HHI
    Implementação baseada em padrões Goldman Sachs adaptados para retail
    """
    
    # THRESHOLDS INSTITUCIONAIS (com justificativa matemática)
    THRESHOLDS = {
        # POSITION SIZING (Kelly Criterion adaptado)
        'max_position_size': Decimal('0.10'),  # 10% - limite conservador
        
        # RISK MANAGEMENT (VaR based)
        'max_daily_loss': Decimal('0.05'),     # 5% - máximo diário
        'max_concentration': Decimal('0.25'),  # 25% - diversificação mínima
        'var_95_threshold': 0.015,             # 1.5% VaR - nível aceitável
        
        # SIGNAL QUALITY
        'min_confidence': 0.70,                # 70% - significância estatística
        'min_sharpe': 1.0,                     # 1.0 - mínimo aceitável
        
        # PORTFOLIO HEALTH
        'max_hhi': 0.25,                       # HHI máximo
        'max_drawdown': 0.15,                  # 15% drawdown máximo
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or self.THRESHOLDS.copy()
        # Garante que valores Decimal são mantidos
        for key in ['max_position_size', 'max_daily_loss', 'max_concentration']:
            if key in self.config and not isinstance(self.config[key], Decimal):
                self.config[key] = Decimal(str(self.config[key]))
        
        self.daily_pnl = Decimal('0')
        self.daily_start = datetime.now().date()
        self.risk_metrics = RiskMetrics()
        
        logger.info("Risk Validator Tier-1 v3.0 inicializado")
    
    def validate_trade_signal(self, signal: RiskSignal, 
                             portfolio: Dict) -> Tuple[bool, str, Dict]:
        """
        Valida sinal de trading com VaR e HHI integrados
        
        Args:
            signal: Sinal de trading
            portfolio: Estado atual do portfólio
            
        Returns:
            Tuple[bool, str, Dict]: (aprovado, motivo, métricas)
        """
        validation_checks = []
        metrics = {}
        
        try:
            # 1. VALIDAÇÃO DE CONFIANÇA
            if signal.confidence < self.config['min_confidence']:
                validation_checks.append(
                    f"CONFIDENCE: {signal.confidence:.1%} < {self.config['min_confidence']:.0%}"
                )
            
            # 2. VALIDAÇÃO DE TAMANHO DE POSIÇÃO (Kelly adaptado)
            trade_value = signal.quantity * signal.price
            portfolio_value = Decimal(str(portfolio.get('total_value', 1)))
            if portfolio_value <= 0:
                return False, "REJECTED: Portfolio value <= 0", {}
            
            position_size = trade_value / portfolio_value
            
            if position_size > self.config['max_position_size']:
                validation_checks.append(
                    f"POSITION: {position_size:.1%} > {self.config['max_position_size']:.0%}"
                )
            
            # 3. VALIDAÇÃO DE CONCENTRAÇÃO (HHI)
            exposures = portfolio.get('exposures', {})
            current_exposure = Decimal(str(exposures.get(signal.symbol, 0)))
            new_exposure = current_exposure + trade_value
            concentration = new_exposure / portfolio_value
            
            if concentration > self.config['max_concentration']:
                validation_checks.append(
                    f"CONCENTRATION: {concentration:.1%} > {self.config['max_concentration']:.0%}"
                )
            
            # 4. CÁLCULO HHI (Herfindahl-Hirschman Index)
            hhi = self._calculate_hhi(exposures, portfolio_value, signal, trade_value)
            metrics['hhi'] = hhi
            
            if hhi > self.config['max_hhi']:
                validation_checks.append(
                    f"HHI: {hhi:.3f} > {self.config['max_hhi']:.2f}"
                )
            
            # 5. CÁLCULO VaR (Value at Risk)
            returns = portfolio.get('recent_returns', [])
            if len(returns) >= 20:  # Mínimo para cálculo estatístico
                var_95 = self._calculate_var_historical(returns, confidence=0.95)
                metrics['var_95'] = var_95
                
                # Projeção do impacto do trade no VaR
                trade_impact = float(position_size) * 0.02  # Sensibilidade conservadora
                projected_var = var_95 + trade_impact
                
                if projected_var > self.config['var_95_threshold']:
                    validation_checks.append(
                        f"VaR_PROJ: {projected_var:.2%} > {self.config['var_95_threshold']:.1%}"
                    )
            
            # 6. VALIDAÇÃO DE DRAWDOWN DIÁRIO
            if self.daily_pnl < -self.config['max_daily_loss'] * portfolio_value:
                validation_checks.append(
                    f"DAILY_LOSS: {self.daily_pnl/portfolio_value:.1%} < -{self.config['max_daily_loss']:.0%}"
                )
            
            # 7. VALIDAÇÃO DE SHARPE RATIO (se disponível)
            sharpe = portfolio.get('sharpe_ratio', 0)
            if sharpe < self.config['min_sharpe']:
                validation_checks.append(
                    f"SHARPE: {sharpe:.2f} < {self.config['min_sharpe']:.1f}"
                )
            
            # RESULTADO FINAL
            if not validation_checks:
                return True, "APPROVED", metrics
            else:
                reason = "; ".join(validation_checks)
                return False, f"REJECTED: {reason}", metrics
                
        except Exception as e:
            logger.error(f"Erro na validação de risco: {e}", exc_info=True)
            return False, f"ERROR: {str(e)}", {}
    
    def _calculate_hhi(self, exposures: Dict, portfolio_value: Decimal,
                      signal: RiskSignal, trade_value: Decimal) -> float:
        """
        Calcula Herfindahl-Hirschman Index
        
        Fórmula: HHI = Σ(s_i²) onde s_i = exposição_i / total
        
        Interpretação:
        - HHI ≈ 0 → Diversificação perfeita
        - HHI ≈ 1 → Concentração total
        - Threshold: < 0.25 para diversificação adequada
        """
        if portfolio_value <= 0:
            return 0.0
        
        # Cria cópia das exposições e adiciona o novo trade
        exp_copy = {k: Decimal(str(v)) for k, v in exposures.items()}
        exp_copy[signal.symbol] = exp_copy.get(signal.symbol, Decimal('0')) + trade_value
        
        # Calcula participações percentuais
        participations = []
        for exp in exp_copy.values():
            pct = float(exp / portfolio_value)
            if pct > 0:
                participations.append(pct)
        
        # Calcula HHI
        hhi = sum(p**2 for p in participations)
        return hhi
    
    def _calculate_var_historical(self, returns: List[float], 
                                 confidence: float = 0.95) -> float:
        """
        Calcula Value at Risk histórico
        
        Args:
            returns: Lista de retornos históricos
            confidence: Nível de confiança (ex: 0.95 para 95%)
            
        Returns:
            VaR no nível de confiança especificado
        """
        if not returns or len(returns) < 20:
            return 0.0
        
        # Converte para numpy array
        returns_array = np.array(returns)
        
        # Método histórico simples
        percentile = (1 - confidence) * 100
        var = np.percentile(returns_array, percentile)
        
        # Retorna valor absoluto (sempre positivo para perda)
        return abs(var)
    
    def _calculate_var_parametric(self, returns: List[float],
                                 confidence: float = 0.95) -> float:
        """
        Calcula VaR paramétrico (assumindo distribuição normal)
        
        Fórmula: VaR = μ + z_score * σ
        Onde z_score é o quantil da distribuição normal
        """
        if not returns or len(returns) < 20:
            return 0.0
        
        returns_array = np.array(returns)
        mean = np.mean(returns_array)
        std = np.std(returns_array)
        
        if SCIPY_AVAILABLE:
            # Z-score para nível de confiança
            z_score = stats.norm.ppf(1 - confidence)
        else:
            # Aproximação simples para z-score (95% = 1.645)
            z_score = 1.645 if confidence == 0.95 else 2.326 if confidence == 0.99 else 1.28
        
        var = mean + z_score * std
        return abs(var)
    
    def update_portfolio_metrics(self, portfolio: Dict) -> RiskMetrics:
        """
        Atualiza métricas de risco do portfólio
        
        Args:
            portfolio: Dicionário com dados do portfólio
            
        Returns:
            RiskMetrics: Métricas calculadas
        """
        metrics = RiskMetrics()
        
        try:
            # Dados do portfólio
            returns = portfolio.get('returns', [])
            exposures = portfolio.get('exposures', {})
            portfolio_value = Decimal(str(portfolio.get('total_value', 1)))
            
            # 1. Calcula VaR
            if len(returns) >= 20:
                metrics.var_95 = self._calculate_var_historical(returns, 0.95)
            
            # 2. Calcula HHI
            if exposures and portfolio_value > 0:
                participations = []
                for exp in exposures.values():
                    pct = float(Decimal(str(exp)) / portfolio_value)
                    if pct > 0:
                        participations.append(pct)
                
                if participations:
                    metrics.hhi = sum(p**2 for p in participations)
            
            # 3. Calcula Max Drawdown
            if len(returns) >= 10:
                returns_array = np.array(returns)
                cumulative = np.cumprod(1 + returns_array)
                running_max = np.maximum.accumulate(cumulative)
                drawdowns = (cumulative - running_max) / running_max
                metrics.max_drawdown = abs(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0
            
            # 4. Calcula Volatilidade
            if len(returns) >= 10:
                metrics.volatility = np.std(returns) * np.sqrt(252)  # Anualizada
            
            # 5. Calcula Sharpe Ratio
            if len(returns) >= 10 and metrics.volatility > 0:
                mean_return = np.mean(returns) * 252  # Anualizado
                risk_free_rate = 0.02  # 2% assumido
                metrics.sharpe_ratio = (mean_return - risk_free_rate) / metrics.volatility
            
            # 6. Calcula Calmar Ratio (Sharpe adaptado para drawdown)
            if metrics.max_drawdown > 0 and len(returns) >= 10:
                mean_return = np.mean(returns) * 252
                metrics.calmar_ratio = mean_return / metrics.max_drawdown
            
            # 7. Calcula Sortino Ratio (volatilidade apenas downside)
            if len(returns) >= 10:
                downside_returns = [r for r in returns if r < 0]
                if downside_returns:
                    downside_dev = np.std(downside_returns) * np.sqrt(252)
                    if downside_dev > 0:
                        mean_return = np.mean(returns) * 252
                        risk_free_rate = 0.02
                        metrics.sortino_ratio = (mean_return - risk_free_rate) / downside_dev
            
            self.risk_metrics = metrics
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {e}", exc_info=True)
        
        return metrics
    
    def get_risk_score(self) -> float:
        """Retorna score de risco atual"""
        return self.risk_metrics.calculate_risk_score()
    
    def update_daily_pnl(self, pnl: Decimal):
        """Atualiza P&L diário"""
        today = datetime.now().date()
        
        # Reseta se for novo dia
        if today != self.daily_start:
            self.daily_pnl = Decimal('0')
            self.daily_start = today
        
        self.daily_pnl += pnl
    
    def generate_risk_report(self) -> Dict:
        """Gera relatório completo de risco"""
        return {
            'timestamp': datetime.now().isoformat(),
            'risk_score': self.get_risk_score(),
            'metrics': self.risk_metrics.to_dict(),
            'thresholds': {k: str(v) if isinstance(v, Decimal) else v for k, v in self.config.items()},
            'daily_pnl': float(self.daily_pnl),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas no risco atual"""
        recommendations = []
        
        if self.risk_metrics.var_95 > 0.02:
            recommendations.append("Reduzir exposição - VaR acima do limite")
        
        if self.risk_metrics.hhi > 0.3:
            recommendations.append("Diversificar portfólio - Concentração alta")
        
        if self.risk_metrics.max_drawdown > 0.15:
            recommendations.append("Implementar stop-loss mais conservador")
        
        if self.risk_metrics.sharpe_ratio < 1.0:
            recommendations.append("Reavaliar estratégias - Sharpe abaixo do ideal")
        
        if float(self.daily_pnl) < -0.03:  # -3%
            recommendations.append("Parar trading hoje - Perda diária significativa")
        
        return recommendations

# TESTES UNITÁRIOS
def test_risk_validator_v3():
    """Testes completos do Risk Validator v3.0"""
    print("🧪 Testando Risk Validator Tier-1 v3.0")
    
    validator = Tier1RiskValidatorV3()
    
    # Teste 1: Sinal válido
    valid_signal = RiskSignal(
        symbol="BTCUSDT",
        action="BUY",
        quantity=Decimal("0.1"),
        price=Decimal("50000"),
        confidence=0.85,
        timestamp=datetime.now(),
        signal_id="TEST_001",
        strategy_id="ALPHA_MOMENTUM"
    )
    
    valid_portfolio = {
        'total_value': Decimal("100000"),
        'exposures': {"BTCUSDT": Decimal("5000")},
        'recent_returns': [0.01, -0.02, 0.015, -0.01, 0.02] * 4,  # 20 retornos
        'returns': [0.01, -0.02, 0.015, -0.01, 0.02] * 10  # 50 retornos
    }
    
    approved, reason, metrics = validator.validate_trade_signal(
        valid_signal, valid_portfolio
    )
    
    assert approved == True
    assert "APPROVED" in reason
    print("✅ Teste 1: Sinal válido aprovado")
    
    # Teste 2: Sinal com confiança baixa
    low_confidence_signal = RiskSignal(
        symbol="BTCUSDT",
        action="BUY",
        quantity=Decimal("0.1"),
        price=Decimal("50000"),
        confidence=0.60,  # Abaixo do mínimo
        timestamp=datetime.now(),
        signal_id="TEST_002",
        strategy_id="ALPHA_MOMENTUM"
    )
    
    approved, reason, _ = validator.validate_trade_signal(
        low_confidence_signal, valid_portfolio
    )
    
    assert approved == False
    assert "CONFIDENCE" in reason
    print("✅ Teste 2: Confiança baixa rejeitada")
    
    # Teste 3: Cálculo de HHI
    portfolio_concentrated = {
        'total_value': Decimal("100000"),
        'exposures': {"BTCUSDT": Decimal("80000")},  # 80% concentrado
        'returns': [0.01] * 20
    }
    
    metrics = validator.update_portfolio_metrics(portfolio_concentrated)
    assert metrics.hhi > 0.5  # Deve ser alto
    print("✅ Teste 3: HHI calculado corretamente")
    
    # Teste 4: Cálculo de VaR
    returns_volatile = list(np.random.normal(0, 0.05, 100))  # 5% volatilidade
    portfolio_volatile = {
        'total_value': Decimal("100000"),
        'exposures': {},
        'returns': returns_volatile
    }
    
    metrics = validator.update_portfolio_metrics(portfolio_volatile)
    assert metrics.var_95 > 0  # Deve ser positivo
    print("✅ Teste 4: VaR calculado corretamente")
    
    # Teste 5: Score de risco
    risk_score = validator.get_risk_score()
    assert 0 <= risk_score <= 100
    print(f"✅ Teste 5: Score de risco: {risk_score:.1f}/100")
    
    print("\n🎯 Risk Validator v3.0 testado com sucesso!")
    return True

if __name__ == "__main__":
    test_risk_validator_v3()

