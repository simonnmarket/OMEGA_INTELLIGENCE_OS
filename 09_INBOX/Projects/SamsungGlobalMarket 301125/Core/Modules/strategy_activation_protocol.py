# -*- coding: utf-8 -*-
"""
STRATEGY ACTIVATION PROTOCOL (PAE) - SAMSUNG GLOBAL MARKET
STATUS: PRODUÇÃO TIER-0
DATA: 2025-01-27
FUNÇÃO: Protocolo de ativação estratégica com frameworks Bayesianos
FRAMEWORKS: Thomas Bayes, William Hamilton, Carl Friedrich Gauss, Ludwig Boltzmann
CHECKSUM: SHA3-256: PAE_HASH_PLACEHOLDER
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==================== FRAMEWORK DE THOMAS BAYES ====================

class BayesianThresholdManager:
    """
    Gerenciador de thresholds dinâmicos baseado em Teorema de Bayes.
    
    CONCEITO: A probabilidade de um trade ser bom não é fixa. 
    Ela é atualizada continuamente com cada nova evidência (trade executado).
    
    P(Sucesso | Evidência) ∝ P(Evidência | Sucesso) × P(Sucesso)
    """
    
    def __init__(self, strategy_name: str, initial_threshold: float = 0.65):
        """
        Inicializa com threshold razoável (65% ao invés de 95%+).
        
        Args:
            strategy_name: Nome da estratégia
            initial_threshold: Threshold inicial (default: 0.65)
        """
        self.strategy_name = strategy_name
        self.threshold = initial_threshold
        self.prior_success_rate = 0.55  # Prior neutro ligeiramente otimista
        self.observations = 0
        self.successful_trades = 0
        self.failed_trades = 0
        
        logging.info(f"🎯 BayesianThresholdManager criado para {strategy_name}")
        logging.info(f"   - Threshold inicial: {self.threshold*100:.1f}%")
        logging.info(f"   - Prior: {self.prior_success_rate*100:.1f}%\n")
    
    def update_belief(self, trade_was_profitable: bool):
        """
        Atualiza crença bayesiana baseada no resultado do trade.
        
        Args:
            trade_was_profitable: True se o trade foi lucrativo
        """
        self.observations += 1
        
        if trade_was_profitable:
            self.successful_trades += 1
        else:
            self.failed_trades += 1
        
        # Taxa de aprendizado adaptativa (diminui com mais observações)
        learning_rate = 1 / (1 + np.sqrt(self.observations))
        
        # Atualização Bayesiana
        if trade_was_profitable:
            # Aumenta confiança
            self.prior_success_rate += learning_rate * (1 - self.prior_success_rate)
        else:
            # Diminui confiança
            self.prior_success_rate -= learning_rate * self.prior_success_rate
        
        # Ajusta threshold inversamente proporcional à taxa de sucesso
        # Mais sucesso → threshold menor → mais trades
        # Menos sucesso → threshold maior → menos trades (proteção)
        self.threshold = 0.5 + (1 - self.prior_success_rate) * 0.45
        
        # Limitar entre 0.3 e 0.9
        self.threshold = max(0.3, min(0.9, self.threshold))
        
        logging.info(f"📊 Belief atualizada para {self.strategy_name}:")
        logging.info(f"   - Observações: {self.observations}")
        logging.info(f"   - Win Rate: {self.prior_success_rate*100:.1f}%")
        logging.info(f"   - Novo Threshold: {self.threshold*100:.1f}%\n")
    
    def should_activate(self, raw_signal_strength: float) -> bool:
        """
        Decide se a estratégia deve gerar um sinal.
        
        Args:
            raw_signal_strength: Força do sinal bruto (0.0 - 1.0)
            
        Returns:
            True se deve ativar
        """
        should_act = raw_signal_strength > self.threshold
        
        if should_act:
            logging.info(f"✅ {self.strategy_name} ATIVADA")
            logging.info(f"   - Signal strength: {raw_signal_strength*100:.1f}%")
            logging.info(f"   - Threshold: {self.threshold*100:.1f}%\n")
        
        return should_act
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do gerenciador"""
        return {
            'strategy': self.strategy_name,
            'observations': self.observations,
            'successful_trades': self.successful_trades,
            'failed_trades': self.failed_trades,
            'win_rate': self.successful_trades / self.observations if self.observations > 0 else 0,
            'current_threshold': self.threshold,
            'prior_success_rate': self.prior_success_rate
        }

# ==================== FRAMEWORK DE HAMILTON & GAUSS ====================

class UniversalRiskManager:
    """
    Gerenciador universal de risco com stop-loss duplo.
    
    CONCEITO HAMILTONIANO: Otimização da trajetória de lucro.
    CONCEITO GAUSSIANO: Proteção contra outliers (eventos extremos).
    """
    
    def __init__(
        self,
        fixed_stop_pct: float = 0.15,
        trailing_stop_pct: float = 0.10,
        take_profit_pct: float = 0.25
    ):
        """
        Inicializa gerenciador de risco.
        
        Args:
            fixed_stop_pct: Stop-loss fixo (default: 15%)
            trailing_stop_pct: Trailing stop (default: 10%)
            take_profit_pct: Take profit (default: 25%)
        """
        self.fixed_stop_pct = fixed_stop_pct
        self.trailing_stop_pct = trailing_stop_pct
        self.take_profit_pct = take_profit_pct
        self.peak_price = None
        
        logging.info("🛡️ UniversalRiskManager inicializado")
        logging.info(f"   - Fixed Stop: {fixed_stop_pct*100:.1f}%")
        logging.info(f"   - Trailing Stop: {trailing_stop_pct*100:.1f}%")
        logging.info(f"   - Take Profit: {take_profit_pct*100:.1f}%\n")
    
    def check_exit_signal(
        self,
        entry_price: float,
        current_price: float,
        position_type: str = 'LONG'
    ) -> Dict:
        """
        Verifica se deve fechar a posição.
        
        Returns:
            Dict com decisão e razão
        """
        # Atualizar pico de preço
        if position_type == 'LONG':
            if self.peak_price is None or current_price > self.peak_price:
                self.peak_price = current_price
            
            # Calcular P&L
            pnl_pct = (current_price - entry_price) / entry_price
            drawdown_from_peak = (current_price - self.peak_price) / self.peak_price
            
            # STOP-LOSS FIXO DE GAUSS (proteção contra outliers)
            if pnl_pct < -self.fixed_stop_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'FIXED_STOP_LOSS',
                    'type': 'PROTECTION',
                    'pnl': pnl_pct,
                    'urgency': 'IMMEDIATE'
                }
            
            # TRAILING STOP DE HAMILTON (otimização de trajetória)
            if self.peak_price and drawdown_from_peak < -self.trailing_stop_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'TRAILING_STOP',
                    'type': 'OPTIMIZATION',
                    'pnl': pnl_pct,
                    'peak_pnl': (self.peak_price - entry_price) / entry_price,
                    'urgency': 'HIGH'
                }
            
            # TAKE PROFIT
            if pnl_pct > self.take_profit_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'TAKE_PROFIT',
                    'type': 'PROFIT_REALIZATION',
                    'pnl': pnl_pct,
                    'urgency': 'NORMAL'
                }
        
        elif position_type == 'SHORT':
            if self.peak_price is None or current_price < self.peak_price:
                self.peak_price = current_price
            
            pnl_pct = (entry_price - current_price) / entry_price
            drawdown_from_peak = (self.peak_price - current_price) / self.peak_price
            
            # Lógica invertida para SHORT
            if pnl_pct < -self.fixed_stop_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'FIXED_STOP_LOSS',
                    'type': 'PROTECTION',
                    'pnl': pnl_pct,
                    'urgency': 'IMMEDIATE'
                }
            
            if self.peak_price and drawdown_from_peak > self.trailing_stop_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'TRAILING_STOP',
                    'type': 'OPTIMIZATION',
                    'pnl': pnl_pct,
                    'urgency': 'HIGH'
                }
            
            if pnl_pct > self.take_profit_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'TAKE_PROFIT',
                    'type': 'PROFIT_REALIZATION',
                    'pnl': pnl_pct,
                    'urgency': 'NORMAL'
                }
        
        return {
            'action': 'HOLD',
            'reason': 'WITHIN_PARAMETERS',
            'pnl': pnl_pct if 'pnl_pct' in locals() else 0,
            'urgency': 'NONE'
        }
    
    def reset(self):
        """Reseta o gerenciador para nova posição"""
        self.peak_price = None

# ==================== FRAMEWORK DE LUDWIG BOLTZMANN ====================

class MarketRegimeFilter:
    """
    Detector de regime de mercado baseado em conceitos termodinâmicos.
    
    CONCEITO DE BOLTZMANN: Mercados têm "entropia".
    - Alta entropia: Tendências fortes, caóticas (perigoso para mean reversion)
    - Baixa entropia: Ranging, previsível (ideal para mean reversion)
    """
    
    def __init__(self):
        logging.info("🌡️ MarketRegimeFilter inicializado (Framework Boltzmann)\n")
    
    def detect_regime(
        self,
        prices: np.ndarray,
        lookback: int = 50
    ) -> Dict:
        """
        Classifica regime de mercado baseado em momentum e volatilidade.
        
        Returns:
            Dict com regime detectado e métricas
        """
        if len(prices) < lookback:
            return {
                'regime': 'INSUFFICIENT_DATA',
                'entropy': 0.0,
                'safe_for_mean_reversion': False,
                'safe_for_trend_following': False
            }
        
        recent_prices = prices[-lookback:]
        
        # Médias móveis
        ma_short = np.mean(recent_prices[-20:])
        ma_long = np.mean(recent_prices)
        
        # "Temperatura" do mercado (momentum)
        momentum = (ma_short - ma_long) / ma_long
        
        # "Entropia" do mercado (volatilidade normalizada)
        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(returns)
        avg_volatility = 0.015  # Baseline
        entropy = volatility / avg_volatility
        
        # Classificação termodinâmica
        if abs(momentum) > 0.05 and entropy > 1.5:
            regime = "HIGH_ENTROPY_TRENDING"
            safe_mean_rev = False
            safe_trend = True
            description = "Tendência forte com alta volatilidade"
        
        elif abs(momentum) < 0.02 and entropy < 0.8:
            regime = "LOW_ENTROPY_RANGING"
            safe_mean_rev = True
            safe_trend = False
            description = "Mercado lateral com baixa volatilidade"
        
        elif abs(momentum) > 0.03:
            regime = "MODERATE_TRENDING"
            safe_mean_rev = False
            safe_trend = True
            description = "Tendência moderada"
        
        elif entropy > 1.2:
            regime = "HIGH_ENTROPY_RANGING"
            safe_mean_rev = False  # Muito volátil
            safe_trend = False
            description = "Mercado lateral porém volátil"
        
        else:
            regime = "TRANSITIONING"
            safe_mean_rev = True
            safe_trend = False
            description = "Mercado em transição"
        
        return {
            'regime': regime,
            'description': description,
            'momentum': momentum,
            'entropy': entropy,
            'volatility': volatility,
            'safe_for_mean_reversion': safe_mean_rev,
            'safe_for_trend_following': safe_trend,
            'confidence': min(abs(momentum) * 10 + entropy * 0.5, 1.0)
        }
    
    def is_safe_for_strategy(
        self,
        regime_info: Dict,
        strategy_type: str
    ) -> bool:
        """
        Verifica se o regime é seguro para um tipo de estratégia.
        
        Args:
            regime_info: Resultado de detect_regime()
            strategy_type: 'mean_reversion', 'trend_following', 'arbitrage'
        """
        if strategy_type == 'mean_reversion':
            return regime_info['safe_for_mean_reversion']
        
        elif strategy_type == 'trend_following':
            return regime_info['safe_for_trend_following']
        
        elif strategy_type == 'arbitrage':
            # Arbitragem funciona melhor em baixa volatilidade
            return regime_info['entropy'] < 1.0
        
        elif strategy_type == 'carry_trade':
            # Carry trade prefere mercados estáveis
            return regime_info['regime'] in ['LOW_ENTROPY_RANGING', 'TRANSITIONING']
        
        else:
            # Estratégias sem classificação: permitir sempre
            return True

# ==================== FRAMEWORK INTEGRADO DE DECISÃO ====================

class EnhancedStrategyDecisionEngine:
    """
    Motor de decisão aprimorado que integra todos os frameworks.
    
    Combina:
    - Bayes: Thresholds adaptativos
    - Gauss: Proteção contra outliers (stop-loss fixo)
    - Hamilton: Otimização de trajetória (trailing stop)
    - Boltzmann: Classificação de entropia de mercado
    """
    
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.bayesian_manager = BayesianThresholdManager(strategy_name)
        self.risk_manager = UniversalRiskManager()
        self.regime_filter = MarketRegimeFilter()
        
        logging.info(f"🧠 EnhancedStrategyDecisionEngine criado: {strategy_name}\n")
    
    def evaluate_entry(
        self,
        raw_signal_strength: float,
        market_prices: np.ndarray,
        strategy_type: str = 'mean_reversion'
    ) -> Dict:
        """
        Avalia se deve entrar em um trade.
        
        Returns:
            Dict com decisão e justificativa
        """
        # 1. Detectar regime de mercado (Boltzmann)
        regime = self.regime_filter.detect_regime(market_prices)
        
        # 2. Verificar se regime é seguro para a estratégia
        regime_safe = self.regime_filter.is_safe_for_strategy(regime, strategy_type)
        
        # 3. Verificar threshold Bayesiano
        threshold_passed = self.bayesian_manager.should_activate(raw_signal_strength)
        
        # 4. Decisão final
        should_enter = threshold_passed and regime_safe
        
        decision = {
            'should_enter': should_enter,
            'raw_signal_strength': raw_signal_strength,
            'bayesian_threshold': self.bayesian_manager.threshold,
            'threshold_passed': threshold_passed,
            'market_regime': regime['regime'],
            'regime_safe': regime_safe,
            'regime_description': regime['description'],
            'confidence': raw_signal_strength if should_enter else 0.0
        }
        
        # Log da decisão
        if should_enter:
            logging.info(f"✅ ENTRADA APROVADA: {self.strategy_name}")
            logging.info(f"   - Regime: {regime['regime']}")
            logging.info(f"   - Signal: {raw_signal_strength*100:.1f}% > {self.bayesian_manager.threshold*100:.1f}%")
        else:
            if not threshold_passed:
                logging.info(f"❌ Entrada bloqueada: Signal {raw_signal_strength*100:.1f}% < Threshold {self.bayesian_manager.threshold*100:.1f}%")
            if not regime_safe:
                logging.info(f"⚠️ Entrada bloqueada: Regime {regime['regime']} não seguro para {strategy_type}")
        
        return decision
    
    def evaluate_exit(
        self,
        entry_price: float,
        current_price: float,
        position_type: str = 'LONG'
    ) -> Dict:
        """
        Avalia se deve sair de um trade (Gauss + Hamilton).
        
        Returns:
            Dict com decisão de saída
        """
        return self.risk_manager.check_exit_signal(
            entry_price,
            current_price,
            position_type
        )
    
    def update_performance(self, trade_was_profitable: bool):
        """Atualiza performance para aprendizado Bayesiano"""
        self.bayesian_manager.update_belief(trade_was_profitable)

# ==================== UTILIDADES ====================

class ActivationProtocolHelper:
    """Classe auxiliar com métodos utilitários"""
    
    @staticmethod
    def calculate_signal_strength(
        confidence: float,
        market_conditions: Dict
    ) -> float:
        """
        Calcula força do sinal baseado em múltiplos fatores.
        
        Args:
            confidence: Confiança base da estratégia (0-1)
            market_conditions: Dict com condições de mercado
            
        Returns:
            Signal strength normalizada (0-1)
        """
        # Base: confiança da estratégia
        strength = confidence
        
        # Ajustes baseados em condições
        if 'volatility' in market_conditions:
            vol = market_conditions['volatility']
            # Penalizar volatilidade extrema
            if vol > 0.04:
                strength *= 0.8
            elif vol < 0.01:
                strength *= 1.1
        
        if 'volume' in market_conditions:
            volume_ratio = market_conditions.get('volume_ratio', 1.0)
            # Recompensar volume alto (liquidez)
            if volume_ratio > 1.5:
                strength *= 1.1
            elif volume_ratio < 0.5:
                strength *= 0.85
        
        # Limitar entre 0 e 1
        return max(0.0, min(1.0, strength))
    
    @staticmethod
    def should_strategy_activate_in_state(
        intentional_state: str,
        strategy_name: str
    ) -> bool:
        """
        Corrige a lógica de estados intencionais.
        
        REGRA GERAL: Permitir ação em estados ativos, bloquear apenas em PRESERVE_CAPITAL.
        """
        # Estados que BLOQUEIAM todas as estratégias
        blocking_states = ["PRESERVE_CAPITAL", "EMERGENCY_EXIT", "SYSTEM_HALT"]
        
        if intentional_state in blocking_states:
            return False
        
        # Mapeamento específico por tipo de estratégia
        strategy_permissions = {
            # Mean Reversion: Ativo em SCAN e RANGING
            'MEAN_REVERSION': ['SCAN_OPPORTUNITIES', 'ACCUMULATE', 'NEUTRAL'],
            
            # Trend Following: Ativo em ACCUMULATE e BULL
            'TREND_FOLLOWING': ['ACCUMULATE', 'STRONG_BULL_TREND', 'SCAN_OPPORTUNITIES'],
            
            # Arbitrage: Sempre ativo (exceto em bloqueio)
            'ARBITRAGE': ['SCAN_OPPORTUNITIES', 'ACCUMULATE', 'NEUTRAL', 'STRONG_BULL_TREND'],
            
            # Sector Rotation: Ativo em SCAN e ACCUMULATE
            'SECTOR_ROTATION': ['SCAN_OPPORTUNITIES', 'ACCUMULATE', 'NEUTRAL'],
            
            # Volatility: Ativo sempre
            'VOLATILITY': ['SCAN_OPPORTUNITIES', 'ACCUMULATE', 'NEUTRAL', 'STRONG_BULL_TREND'],
            
            # Default: Ativo em estados não bloqueantes
            'DEFAULT': ['SCAN_OPPORTUNITIES', 'ACCUMULATE', 'NEUTRAL', 'STRONG_BULL_TREND']
        }
        
        # Determinar tipo de estratégia pelo nome
        if 'MEAN' in strategy_name.upper() or 'REVERSION' in strategy_name.upper():
            allowed_states = strategy_permissions['MEAN_REVERSION']
        elif 'ARBITRAGE' in strategy_name.upper():
            allowed_states = strategy_permissions['ARBITRAGE']
        elif 'ROTATION' in strategy_name.upper():
            allowed_states = strategy_permissions['SECTOR_ROTATION']
        elif 'VOLATILITY' in strategy_name.upper():
            allowed_states = strategy_permissions['VOLATILITY']
        else:
            allowed_states = strategy_permissions['DEFAULT']
        
        return intentional_state in allowed_states

# ==================== TESTE STANDALONE ====================

def test_activation_protocol():
    """Testa o protocolo de ativação"""
    print("\n" + "="*100)
    print("[PAE] TESTE DO PROTOCOLO DE ATIVACAO ESTRATEGICA")
    print("="*100 + "\n")
    
    # Teste 1: Bayesian Threshold Manager
    print("[TESTE 1] Bayesian Threshold Manager\n")
    btm = BayesianThresholdManager("TestStrategy", initial_threshold=0.65)
    
    # Simular trades
    print("Simulando 5 trades...")
    btm.update_belief(True)   # Trade 1: Sucesso
    btm.update_belief(True)   # Trade 2: Sucesso
    btm.update_belief(False)  # Trade 3: Falha
    btm.update_belief(True)   # Trade 4: Sucesso
    btm.update_belief(False)  # Trade 5: Falha
    
    stats = btm.get_statistics()
    print(f"\nEstatísticas finais:")
    print(f"   Win Rate: {stats['win_rate']*100:.1f}%")
    print(f"   Threshold atual: {stats['current_threshold']*100:.1f}%\n")
    
    # Teste 2: Universal Risk Manager
    print("\n[TESTE 2] Universal Risk Manager\n")
    urm = UniversalRiskManager()
    
    entry = 100.0
    scenarios = [
        ('Preço subiu 10%', 110.0),
        ('Preço caiu 18%', 82.0),
        ('Preço subiu 30%', 130.0),
        ('Preço subiu 20%, depois caiu 12%', 105.6)
    ]
    
    for desc, price in scenarios:
        result = urm.check_exit_signal(entry, price)
        print(f"{desc} -> {result['action']} ({result['reason']})")
    
    urm.reset()
    
    # Teste 3: Market Regime Filter
    print("\n[TESTE 3] Market Regime Filter\n")
    mrf = MarketRegimeFilter()
    
    # Gerar diferentes cenários de mercado
    ranging_market = 100 + np.random.randn(100) * 1  # Baixa volatilidade
    trending_market = 100 + np.cumsum(np.ones(100) * 0.5)  # Tendência forte
    
    regime_ranging = mrf.detect_regime(ranging_market)
    regime_trending = mrf.detect_regime(trending_market)
    
    print(f"Mercado Ranging: {regime_ranging['regime']}")
    print(f"   - Safe for Mean Reversion: {regime_ranging['safe_for_mean_reversion']}")
    print(f"   - Entropia: {regime_ranging['entropy']:.2f}\n")
    
    print(f"Mercado Trending: {regime_trending['regime']}")
    print(f"   - Safe for Mean Reversion: {regime_trending['safe_for_mean_reversion']}")
    print(f"   - Entropia: {regime_trending['entropy']:.2f}\n")
    
    # Teste 4: Enhanced Decision Engine
    print("\n[TESTE 4] Enhanced Strategy Decision Engine\n")
    engine = EnhancedStrategyDecisionEngine("TestStrategy")
    
    decision = engine.evaluate_entry(
        raw_signal_strength=0.75,
        market_prices=ranging_market,
        strategy_type='mean_reversion'
    )
    
    print(f"Decisão de entrada: {decision['should_enter']}")
    print(f"   - Regime: {decision['market_regime']}")
    print(f"   - Regime seguro: {decision['regime_safe']}")
    print(f"   - Threshold passou: {decision['threshold_passed']}\n")
    
    print("="*100)
    print("[OK] TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
    print("="*100 + "\n")

if __name__ == "__main__":
    test_activation_protocol()

