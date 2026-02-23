# -*- coding: utf-8 -*-
"""
FUTURES CALENDAR SPREADS ORCHESTRATOR - SAMSUNG GLOBAL MARKET
STATUS: PRODUÇÃO TIER-0
DATA: 2025-01-27
FUNÇÃO: Sistema especializado para trading de calendar spreads em futuros
CHECKSUM: SHA3-256: FUTURES_HASH_PLACEHOLDER
"""

import asyncio
import numpy as np
import pandas as pd
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
from scipy import stats
from sklearn.linear_model import LinearRegression
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==================== ESTRUTURAS DE DADOS ====================

@dataclass
class FuturesContract:
    """Representa um contrato futuro individual"""
    symbol: str                 # Ex: "CLH4" (Crude Oil March 2024)
    underlying: str             # Ex: "CL" (Crude Oil)
    expiry_month: str          # Ex: "H" (March)
    expiry_year: int           # Ex: 2024
    price: float               # Preço atual do contrato
    volume: float              # Volume de negociação
    open_interest: int         # Contratos em aberto
    timestamp: datetime
    
    def days_to_expiry(self) -> int:
        """Calcula dias até vencimento"""
        # Simplificado: assumir 3º sexta-feira do mês
        expiry_date = self._calculate_expiry_date()
        return (expiry_date - datetime.now()).days
    
    def _calculate_expiry_date(self) -> datetime:
        """Calcula data de vencimento baseado no código do mês"""
        month_codes = {
            'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6,
            'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12
        }
        month = month_codes.get(self.expiry_month, 1)
        # 3ª sexta-feira do mês (simplificado)
        return datetime(self.expiry_year, month, 15)

@dataclass
class CalendarSpread:
    """Representa um calendar spread (F1 - F2)"""
    front_contract: FuturesContract    # Contrato próximo (F1)
    back_contract: FuturesContract     # Contrato distante (F2)
    spread_value: float                # F1 - F2
    spread_percentage: float           # (F1 - F2) / F2
    timestamp: datetime
    
    def __post_init__(self):
        """Calcula valores do spread"""
        self.spread_value = self.front_contract.price - self.back_contract.price
        self.spread_percentage = self.spread_value / self.back_contract.price

# ==================== ANALISADORES ESPECIALIZADOS ====================

class RollYieldAnalyzer:
    """Analisa o rendimento de rolagem de contratos futuros"""
    
    def __init__(self):
        logging.info("📊 RollYieldAnalyzer inicializado")
    
    def calculate_roll_yield(self, F1: float, F2: float, days_to_expiry: int) -> Dict:
        """
        Calcula o roll yield (rendimento de rolagem).
        
        Roll Yield = (F1 - F2) / F2 × (365 / days_to_expiry)
        
        Positivo: Backwardation (F1 > F2) - bullish
        Negativo: Contango (F1 < F2) - bearish
        """
        if F2 == 0 or days_to_expiry == 0:
            return {'roll_yield': 0.0, 'regime': 'NEUTRAL', 'annualized': 0.0}
        
        spread_pct = (F1 - F2) / F2
        annualized_yield = spread_pct * (365 / days_to_expiry)
        
        # Classificação de regime
        if annualized_yield > 0.05:  # >5% anualizado
            regime = "STRONG_BACKWARDATION"
            signal = "BULLISH"
        elif annualized_yield > 0:
            regime = "BACKWARDATION"
            signal = "NEUTRAL_BULLISH"
        elif annualized_yield < -0.05:
            regime = "STRONG_CONTANGO"
            signal = "BEARISH"
        else:
            regime = "CONTANGO"
            signal = "NEUTRAL_BEARISH"
        
        return {
            'roll_yield': spread_pct,
            'annualized_yield': annualized_yield,
            'regime': regime,
            'signal': signal,
            'days_to_expiry': days_to_expiry
        }

class CointegrationAnalyzer:
    """Analisa cointegração entre contratos futuros"""
    
    def __init__(self):
        logging.info("🔗 CointegrationAnalyzer inicializado")
    
    def test_cointegration(
        self,
        prices_F1: np.ndarray,
        prices_F2: np.ndarray,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Testa cointegração entre dois contratos usando Engle-Granger.
        
        Args:
            prices_F1: Série de preços do contrato front
            prices_F2: Série de preços do contrato back
            confidence_level: Nível de confiança (95% = 0.95)
            
        Returns:
            Dict com resultados do teste
        """
        if len(prices_F1) != len(prices_F2) or len(prices_F1) < 30:
            return {'cointegrated': False, 'reason': 'Dados insuficientes'}
        
        # Passo 1: Regressão linear F1 = α + β×F2 + ε
        X = prices_F2.reshape(-1, 1)
        y = prices_F1
        
        model = LinearRegression()
        model.fit(X, y)
        
        alpha = model.intercept_
        beta = model.coef_[0]
        
        # Passo 2: Calcular resíduos
        residuals = y - model.predict(X)
        
        # Passo 3: Teste de estacionaridade dos resíduos (ADF simplificado)
        # Usamos autocorrelação como proxy
        autocorr = np.corrcoef(residuals[:-1], residuals[1:])[0, 1]
        
        # Passo 4: Verificar mean reversion
        mean_residual = np.mean(residuals)
        std_residual = np.std(residuals)
        half_life = self._calculate_half_life(residuals)
        
        # Decisão de cointegração
        is_cointegrated = (
            abs(autocorr) < 0.9 and  # Resíduos não muito autocorrelacionados
            std_residual < np.mean([np.std(prices_F1), np.std(prices_F2)]) * 0.3 and
            half_life < len(residuals) * 0.5
        )
        
        return {
            'cointegrated': is_cointegrated,
            'alpha': alpha,
            'beta': beta,
            'hedge_ratio': beta,
            'residuals_mean': mean_residual,
            'residuals_std': std_residual,
            'autocorrelation': autocorr,
            'half_life': half_life,
            'confidence': confidence_level if is_cointegrated else 0.0
        }
    
    def _calculate_half_life(self, residuals: np.ndarray) -> float:
        """Calcula meia-vida de mean reversion"""
        if len(residuals) < 2:
            return float('inf')
        
        # Regressão: Δy = α + β×y_{t-1}
        y_lag = residuals[:-1]
        y_diff = np.diff(residuals)
        
        if len(y_lag) == 0 or np.std(y_lag) == 0:
            return float('inf')
        
        try:
            model = LinearRegression()
            model.fit(y_lag.reshape(-1, 1), y_diff)
            beta = model.coef_[0]
            
            if beta >= 0:
                return float('inf')
            
            half_life = -np.log(2) / np.log(1 + beta)
            return max(0, half_life)
        except:
            return float('inf')

class MarketRegimeDetector:
    """Detecta regime de mercado (bull, bear, ranging)"""
    
    def __init__(self):
        logging.info("🎯 MarketRegimeDetector inicializado")
    
    def detect_regime(
        self,
        prices: np.ndarray,
        fast_window: int = 20,
        slow_window: int = 50
    ) -> Dict:
        """
        Detecta regime de mercado usando médias móveis.
        
        Returns:
            Dict com regime detectado e força da tendência
        """
        if len(prices) < slow_window:
            return {'regime': 'UNKNOWN', 'strength': 0.0, 'confidence': 0.0}
        
        # Médias móveis
        ma_fast = np.mean(prices[-fast_window:])
        ma_slow = np.mean(prices[-slow_window:])
        
        # Tendência
        trend_strength = (ma_fast - ma_slow) / ma_slow
        
        # Volatilidade
        volatility = np.std(prices[-fast_window:]) / np.mean(prices[-fast_window:])
        
        # Classificação
        if trend_strength > 0.05:
            regime = "STRONG_BULL"
            confidence = min(abs(trend_strength) / 0.10, 1.0)
        elif trend_strength > 0.02:
            regime = "BULL"
            confidence = min(abs(trend_strength) / 0.05, 1.0)
        elif trend_strength < -0.05:
            regime = "STRONG_BEAR"
            confidence = min(abs(trend_strength) / 0.10, 1.0)
        elif trend_strength < -0.02:
            regime = "BEAR"
            confidence = min(abs(trend_strength) / 0.05, 1.0)
        else:
            regime = "RANGING"
            confidence = 1.0 - min(abs(trend_strength) / 0.02, 1.0)
        
        # Volatilidade do regime
        if volatility > 0.03:
            vol_regime = "HIGH_VOLATILITY"
        elif volatility > 0.015:
            vol_regime = "NORMAL_VOLATILITY"
        else:
            vol_regime = "LOW_VOLATILITY"
        
        return {
            'regime': regime,
            'trend_strength': trend_strength,
            'confidence': confidence,
            'volatility': volatility,
            'volatility_regime': vol_regime,
            'ma_fast': ma_fast,
            'ma_slow': ma_slow
        }

class CarryTradeAnalyzer:
    """Analisa oportunidades de carry trade em futuros"""
    
    def __init__(self):
        logging.info("💰 CarryTradeAnalyzer inicializado")
    
    def calculate_carry(
        self,
        F1: float,
        F2: float,
        days_between: int,
        risk_free_rate: float = 0.02
    ) -> Dict:
        """
        Calcula o carry de manter um spread de futuros.
        
        Carry = (F2 - F1) / F1 × (365 / days_between) - risk_free_rate
        
        Positivo: Contango com carry atrativo
        Negativo: Backwardation ou carry negativo
        """
        if F1 == 0 or days_between == 0:
            return {'carry': 0.0, 'attractive': False}
        
        # Carry anualizado
        carry = ((F2 - F1) / F1) * (365 / days_between)
        
        # Carry ajustado pelo risco
        risk_adjusted_carry = carry - risk_free_rate
        
        # Decisão
        is_attractive = risk_adjusted_carry > 0.03  # >3% anualizado
        
        return {
            'carry': carry,
            'risk_adjusted_carry': risk_adjusted_carry,
            'annualized_carry': carry,
            'is_attractive': is_attractive,
            'spread_pct': (F2 - F1) / F1,
            'days_between': days_between
        }

class VolatilityAnalyzer:
    """Analisa volatilidade histórica e implícita"""
    
    def __init__(self):
        logging.info("📉 VolatilityAnalyzer inicializado")
    
    def calculate_historical_volatility(
        self,
        prices: np.ndarray,
        window: int = 30
    ) -> Dict:
        """
        Calcula volatilidade histórica (realizada).
        
        Vol = std(returns) × √252
        """
        if len(prices) < window:
            return {'volatility': 0.0, 'regime': 'UNKNOWN'}
        
        # Retornos logarítmicos
        returns = np.log(prices[1:] / prices[:-1])
        
        # Volatilidade rolling
        vol_rolling = pd.Series(returns).rolling(window).std() * np.sqrt(252)
        
        # Volatilidade atual
        current_vol = vol_rolling.iloc[-1] if len(vol_rolling) > 0 else 0.0
        
        # Média histórica
        avg_vol = np.mean(vol_rolling.dropna())
        
        # Classificação
        vol_percentile = stats.percentileofscore(vol_rolling.dropna(), current_vol)
        
        if vol_percentile > 80:
            vol_regime = "EXTREME_HIGH"
        elif vol_percentile > 60:
            vol_regime = "HIGH"
        elif vol_percentile > 40:
            vol_regime = "NORMAL"
        elif vol_percentile > 20:
            vol_regime = "LOW"
        else:
            vol_regime = "EXTREME_LOW"
        
        return {
            'current_volatility': current_vol,
            'average_volatility': avg_vol,
            'volatility_percentile': vol_percentile,
            'volatility_regime': vol_regime,
            'vol_ratio': current_vol / avg_vol if avg_vol > 0 else 1.0
        }
    
    def predict_future_volatility(
        self,
        prices: np.ndarray,
        horizon_days: int = 30
    ) -> float:
        """
        Prediz volatilidade futura usando modelo GARCH simplificado.
        
        Para simplificação, usa EWMA (Exponentially Weighted Moving Average)
        """
        if len(prices) < 60:
            return 0.0
        
        # Retornos
        returns = np.log(prices[1:] / prices[:-1])
        
        # EWMA com lambda = 0.94 (padrão RiskMetrics)
        lambda_ewma = 0.94
        
        # Variância EWMA
        variance_ewma = 0
        for i in range(len(returns) - 1, max(0, len(returns) - 100), -1):
            weight = lambda_ewma ** (len(returns) - 1 - i)
            variance_ewma += weight * returns[i] ** 2
        
        # Normalizar
        variance_ewma /= sum([lambda_ewma ** i for i in range(min(100, len(returns)))])
        
        # Volatilidade predita (anualizada)
        predicted_vol = np.sqrt(variance_ewma) * np.sqrt(252)
        
        return predicted_vol

class CorrelationAnalyzer:
    """Analisa correlação entre contratos e identificação de oportunidades"""
    
    def __init__(self):
        logging.info("🔗 CorrelationAnalyzer inicializado")
    
    def calculate_spread_correlation(
        self,
        prices_F1: np.ndarray,
        prices_F2: np.ndarray,
        window: int = 60
    ) -> Dict:
        """
        Calcula correlação rolling entre contratos.
        
        Args:
            prices_F1: Preços do contrato front
            prices_F2: Preços do contrato back
            window: Janela para cálculo rolling
        """
        if len(prices_F1) != len(prices_F2) or len(prices_F1) < window:
            return {'correlation': 1.0, 'stability': 'UNKNOWN'}
        
        # Correlação total
        total_correlation = np.corrcoef(prices_F1, prices_F2)[0, 1]
        
        # Correlação rolling
        corr_rolling = []
        for i in range(window, len(prices_F1)):
            corr = np.corrcoef(
                prices_F1[i-window:i],
                prices_F2[i-window:i]
            )[0, 1]
            corr_rolling.append(corr)
        
        # Estabilidade da correlação
        corr_std = np.std(corr_rolling)
        
        if corr_std < 0.05:
            stability = "VERY_STABLE"
        elif corr_std < 0.10:
            stability = "STABLE"
        elif corr_std < 0.20:
            stability = "MODERATE"
        else:
            stability = "UNSTABLE"
        
        # Correlação recente
        recent_correlation = corr_rolling[-1] if corr_rolling else total_correlation
        
        return {
            'total_correlation': total_correlation,
            'recent_correlation': recent_correlation,
            'correlation_std': corr_std,
            'stability': stability,
            'correlation_trend': 'INCREASING' if len(corr_rolling) > 1 and corr_rolling[-1] > corr_rolling[-10] else 'STABLE'
        }

# ==================== ORQUESTRADOR PRINCIPAL ====================

class FuturesCalendarSpreadOrchestrator:
    """
    Orquestrador completo para trading de calendar spreads em futuros.
    
    Integra todas as análises para gerar sinais de trading robustos.
    """
    
    def __init__(self):
        """Inicializa o orquestrador com todos os analisadores"""
        logging.info("\n" + "="*100)
        logging.info("🚀 FUTURES CALENDAR SPREAD ORCHESTRATOR - INICIALIZANDO")
        logging.info("="*100 + "\n")
        
        self.roll_yield_analyzer = RollYieldAnalyzer()
        self.cointegration_analyzer = CointegrationAnalyzer()
        self.regime_detector = MarketRegimeDetector()
        self.carry_analyzer = CarryTradeAnalyzer()
        self.volatility_analyzer = VolatilityAnalyzer()
        self.correlation_analyzer = CorrelationAnalyzer()
        
        self.active_spreads = {}
        self.analysis_history = []
        
        logging.info("✅ Todos os analisadores inicializados com sucesso\n")
    
    def create_calendar_spread(
        self,
        underlying: str,
        front_month: str,
        back_month: str,
        front_price: float,
        back_price: float,
        year: int = 2024
    ) -> CalendarSpread:
        """
        Cria um calendar spread.
        
        Args:
            underlying: Código do ativo (ex: "CL" para Crude Oil)
            front_month: Código do mês próximo (ex: "H" para March)
            back_month: Código do mês distante (ex: "M" para June)
            front_price: Preço do contrato front
            back_price: Preço do contrato back
            year: Ano de vencimento
        """
        front_contract = FuturesContract(
            symbol=f"{underlying}{front_month}{str(year)[-1]}",
            underlying=underlying,
            expiry_month=front_month,
            expiry_year=year,
            price=front_price,
            volume=100000,
            open_interest=50000,
            timestamp=datetime.now()
        )
        
        back_contract = FuturesContract(
            symbol=f"{underlying}{back_month}{str(year)[-1]}",
            underlying=underlying,
            expiry_month=back_month,
            expiry_year=year,
            price=back_price,
            volume=80000,
            open_interest=40000,
            timestamp=datetime.now()
        )
        
        spread = CalendarSpread(
            front_contract=front_contract,
            back_contract=back_contract,
            spread_value=0.0,  # Será calculado no __post_init__
            spread_percentage=0.0,
            timestamp=datetime.now()
        )
        
        spread_name = f"{front_contract.symbol}/{back_contract.symbol}"
        self.active_spreads[spread_name] = spread
        
        logging.info(f"📊 Calendar Spread Criado: {spread_name}")
        logging.info(f"   F1: ${front_price:.2f} | F2: ${back_price:.2f}")
        logging.info(f"   Spread: ${spread.spread_value:.2f} ({spread.spread_percentage*100:.2f}%)\n")
        
        return spread
    
    def analyze_spread_opportunity(
        self,
        spread: CalendarSpread,
        historical_prices_F1: np.ndarray,
        historical_prices_F2: np.ndarray
    ) -> Dict:
        """
        Executa análise completa do spread para identificar oportunidades.
        
        Returns:
            Dict com todas as análises e sinal de trading
        """
        logging.info(f"\n🔬 ANÁLISE COMPLETA: {spread.front_contract.symbol}/{spread.back_contract.symbol}")
        logging.info("="*100 + "\n")
        
        F1 = spread.front_contract.price
        F2 = spread.back_contract.price
        days_to_expiry = spread.front_contract.days_to_expiry()
        
        # 1. ROLL YIELD
        roll_yield = self.roll_yield_analyzer.calculate_roll_yield(F1, F2, days_to_expiry)
        logging.info(f"📊 Roll Yield Analysis:")
        logging.info(f"   - Spread: {roll_yield['roll_yield']*100:.2f}%")
        logging.info(f"   - Annualized: {roll_yield['annualized_yield']*100:.2f}%")
        logging.info(f"   - Regime: {roll_yield['regime']}")
        logging.info(f"   - Signal: {roll_yield['signal']}\n")
        
        # 2. COINTEGRAÇÃO
        cointegration = self.cointegration_analyzer.test_cointegration(
            historical_prices_F1,
            historical_prices_F2
        )
        logging.info(f"🔗 Cointegration Analysis:")
        logging.info(f"   - Cointegrated: {cointegration['cointegrated']}")
        logging.info(f"   - Hedge Ratio: {cointegration['hedge_ratio']:.4f}")
        logging.info(f"   - Half-Life: {cointegration['half_life']:.1f} days")
        logging.info(f"   - Residuals Std: {cointegration['residuals_std']:.4f}\n")
        
        # 3. REGIME DE MERCADO
        regime = self.regime_detector.detect_regime(historical_prices_F1)
        logging.info(f"🎯 Market Regime:")
        logging.info(f"   - Regime: {regime['regime']}")
        logging.info(f"   - Trend Strength: {regime['trend_strength']*100:.2f}%")
        logging.info(f"   - Confidence: {regime['confidence']*100:.1f}%")
        logging.info(f"   - Volatility: {regime['volatility_regime']}\n")
        
        # 4. CARRY TRADE
        days_between = abs(spread.front_contract.days_to_expiry() - spread.back_contract.days_to_expiry())
        if days_between == 0:
            days_between = 90  # Assumir 3 meses
        
        carry = self.carry_analyzer.calculate_carry(F1, F2, days_between)
        logging.info(f"💰 Carry Trade Analysis:")
        logging.info(f"   - Carry: {carry['carry']*100:.2f}%")
        logging.info(f"   - Risk-Adjusted: {carry['risk_adjusted_carry']*100:.2f}%")
        logging.info(f"   - Attractive: {carry['is_attractive']}\n")
        
        # 5. VOLATILIDADE
        volatility = self.volatility_analyzer.calculate_historical_volatility(historical_prices_F1)
        predicted_vol = self.volatility_analyzer.predict_future_volatility(historical_prices_F1)
        
        logging.info(f"📉 Volatility Analysis:")
        logging.info(f"   - Current Vol: {volatility['current_volatility']*100:.2f}%")
        logging.info(f"   - Average Vol: {volatility['average_volatility']*100:.2f}%")
        logging.info(f"   - Predicted Vol: {predicted_vol*100:.2f}%")
        logging.info(f"   - Regime: {volatility['volatility_regime']}\n")
        
        # 6. CORRELAÇÃO
        correlation = self.correlation_analyzer.calculate_spread_correlation(
            historical_prices_F1,
            historical_prices_F2
        )
        logging.info(f"🔗 Correlation Analysis:")
        logging.info(f"   - Total Correlation: {correlation['total_correlation']:.4f}")
        logging.info(f"   - Recent Correlation: {correlation['recent_correlation']:.4f}")
        logging.info(f"   - Stability: {correlation['stability']}\n")
        
        # 7. GERAÇÃO DE SINAL DE TRADING
        signal = self._generate_trading_signal(
            spread,
            roll_yield,
            cointegration,
            regime,
            carry,
            volatility,
            correlation
        )
        
        # Salvar análise
        analysis_result = {
            'spread_name': f"{spread.front_contract.symbol}/{spread.back_contract.symbol}",
            'timestamp': datetime.now(),
            'roll_yield': roll_yield,
            'cointegration': cointegration,
            'regime': regime,
            'carry': carry,
            'volatility': volatility,
            'correlation': correlation,
            'signal': signal
        }
        
        self.analysis_history.append(analysis_result)
        
        return analysis_result
    
    def _generate_trading_signal(
        self,
        spread: CalendarSpread,
        roll_yield: Dict,
        cointegration: Dict,
        regime: Dict,
        carry: Dict,
        volatility: Dict,
        correlation: Dict
    ) -> Dict:
        """
        Gera sinal de trading baseado em todas as análises.
        
        Lógica de Decisão:
        1. Cointegração confirmada → Pair trade viável
        2. Roll yield atrativo → Direcional
        3. Regime favorável → Aumenta confiança
        4. Carry positivo → Long spread
        5. Volatilidade baixa → Momento ideal
        """
        logging.info("="*100)
        logging.info("🎯 GERAÇÃO DE SINAL DE TRADING")
        logging.info("="*100 + "\n")
        
        # Score de confiança (0-100)
        confidence_score = 0
        reasons = []
        
        # Critério 1: Cointegração
        if cointegration['cointegrated']:
            confidence_score += 30
            reasons.append("Cointegração confirmada")
        
        # Critério 2: Roll Yield atrativo
        if abs(roll_yield['annualized_yield']) > 0.05:
            confidence_score += 25
            reasons.append(f"Roll yield {roll_yield['annualized_yield']*100:.1f}%")
        
        # Critério 3: Carry positivo
        if carry['is_attractive']:
            confidence_score += 20
            reasons.append(f"Carry atrativo {carry['risk_adjusted_carry']*100:.1f}%")
        
        # Critério 4: Correlação estável
        if correlation['stability'] in ['VERY_STABLE', 'STABLE']:
            confidence_score += 15
            reasons.append(f"Correlação estável ({correlation['total_correlation']:.2f})")
        
        # Critério 5: Volatilidade favorável
        if volatility['volatility_regime'] in ['NORMAL', 'LOW']:
            confidence_score += 10
            reasons.append("Volatilidade favorável")
        
        # Determinar ação
        if confidence_score >= 60:
            if spread.spread_value > 0:
                action = "SELL_SPREAD"  # F1 caro vs F2
                direction = "BEAR_SPREAD"
            else:
                action = "BUY_SPREAD"   # F1 barato vs F2
                direction = "BULL_SPREAD"
            
            recommendation = "EXECUTE"
        elif confidence_score >= 40:
            action = "MONITOR"
            direction = "NEUTRAL"
            recommendation = "WATCH_LIST"
        else:
            action = "PASS"
            direction = "NO_TRADE"
            recommendation = "SKIP"
        
        signal = {
            'action': action,
            'direction': direction,
            'recommendation': recommendation,
            'confidence_score': confidence_score,
            'confidence_pct': confidence_score / 100,
            'reasons': reasons,
            'spread_value': spread.spread_value,
            'spread_percentage': spread.spread_percentage,
            'expected_profit': self._estimate_profit(spread, roll_yield, carry),
            'risk_score': 1.0 - (confidence_score / 100),
            'timestamp': datetime.now()
        }
        
        # Log do sinal
        logging.info(f"📋 SINAL GERADO:")
        logging.info(f"   - Ação: {signal['action']}")
        logging.info(f"   - Direção: {signal['direction']}")
        logging.info(f"   - Recomendação: {signal['recommendation']}")
        logging.info(f"   - Confiança: {signal['confidence_pct']*100:.1f}%")
        logging.info(f"   - Razões: {', '.join(reasons)}")
        logging.info(f"   - Lucro Esperado: ${signal['expected_profit']:,.2f}\n")
        
        logging.info("="*100 + "\n")
        
        return signal
    
    def _estimate_profit(
        self,
        spread: CalendarSpread,
        roll_yield: Dict,
        carry: Dict
    ) -> float:
        """Estima lucro esperado do trade"""
        # Assumir convergência do spread para zero
        expected_convergence = abs(spread.spread_value) * 0.7  # 70% de convergência
        
        # Carry adicional
        carry_profit = carry['risk_adjusted_carry'] * spread.front_contract.price * 0.5
        
        # Lucro total estimado
        total_profit = expected_convergence + carry_profit
        
        return total_profit
    
    def generate_report(self):
        """Gera relatório consolidado de todas as análises"""
        if not self.analysis_history:
            logging.warning("⚠️ Nenhuma análise foi executada ainda")
            return
        
        logging.info("\n" + "="*100)
        logging.info("📊 RELATÓRIO CONSOLIDADO DE CALENDAR SPREADS")
        logging.info("="*100 + "\n")
        
        # Contar sinais por tipo
        signals_count = {}
        for analysis in self.analysis_history:
            action = analysis['signal']['action']
            signals_count[action] = signals_count.get(action, 0) + 1
        
        logging.info("RESUMO DE SINAIS:")
        for action, count in signals_count.items():
            logging.info(f"   - {action}: {count}")
        
        # Sinais executáveis
        executable = [a for a in self.analysis_history if a['signal']['recommendation'] == 'EXECUTE']
        
        logging.info(f"\n✅ OPORTUNIDADES EXECUTÁVEIS: {len(executable)}")
        
        for idx, analysis in enumerate(executable, 1):
            signal = analysis['signal']
            logging.info(f"\n{idx}. {analysis['spread_name']}")
            logging.info(f"   - Ação: {signal['action']}")
            logging.info(f"   - Confiança: {signal['confidence_pct']*100:.1f}%")
            logging.info(f"   - Lucro Esperado: ${signal['expected_profit']:,.2f}")
        
        logging.info("\n" + "="*100 + "\n")

# ==================== FUNÇÃO DE DEMONSTRAÇÃO ====================

async def demonstration():
    """Demonstração completa do orquestrador"""
    
    orchestrator = FuturesCalendarSpreadOrchestrator()
    
    # Exemplo 1: Crude Oil Calendar Spread (CLH4/CLM4)
    logging.info("📋 EXEMPLO 1: CRUDE OIL CALENDAR SPREAD")
    logging.info("-"*100 + "\n")
    
    # Gerar dados históricos simulados
    days = 100
    F1_prices = 75 + np.cumsum(np.random.randn(days) * 0.5)
    F2_prices = 76 + np.cumsum(np.random.randn(days) * 0.45)
    
    # Criar spread
    spread_cl = orchestrator.create_calendar_spread(
        underlying="CL",
        front_month="H",  # March
        back_month="M",   # June
        front_price=F1_prices[-1],
        back_price=F2_prices[-1],
        year=2024
    )
    
    # Analisar
    analysis_cl = orchestrator.analyze_spread_opportunity(
        spread_cl,
        F1_prices,
        F2_prices
    )
    
    # Exemplo 2: E-mini S&P 500 Calendar Spread (ESH4/ESM4)
    logging.info("\n📋 EXEMPLO 2: E-MINI S&P 500 CALENDAR SPREAD")
    logging.info("-"*100 + "\n")
    
    ES_F1_prices = 4500 + np.cumsum(np.random.randn(days) * 15)
    ES_F2_prices = 4510 + np.cumsum(np.random.randn(days) * 14)
    
    spread_es = orchestrator.create_calendar_spread(
        underlying="ES",
        front_month="H",
        back_month="M",
        front_price=ES_F1_prices[-1],
        back_price=ES_F2_prices[-1],
        year=2024
    )
    
    analysis_es = orchestrator.analyze_spread_opportunity(
        spread_es,
        ES_F1_prices,
        ES_F2_prices
    )
    
    # Exemplo 3: Gold Calendar Spread (GCZ4/GCG5)
    logging.info("\n📋 EXEMPLO 3: GOLD CALENDAR SPREAD")
    logging.info("-"*100 + "\n")
    
    GC_F1_prices = 1950 + np.cumsum(np.random.randn(days) * 8)
    GC_F2_prices = 1955 + np.cumsum(np.random.randn(days) * 7.5)
    
    spread_gc = orchestrator.create_calendar_spread(
        underlying="GC",
        front_month="Z",  # December
        back_month="G",   # February (next year)
        front_price=GC_F1_prices[-1],
        back_price=GC_F2_prices[-1],
        year=2024
    )
    
    analysis_gc = orchestrator.analyze_spread_opportunity(
        spread_gc,
        GC_F1_prices,
        GC_F2_prices
    )
    
    # Gerar relatório final
    orchestrator.generate_report()
    
    logging.info("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!\n")

if __name__ == "__main__":
    asyncio.run(demonstration())

