"""
EURUSD Agent - AURORA v6.0 MVP
Agente especializado em Euro (EUR/USD)
"""

import numpy as np
from typing import Dict
from datetime import datetime
import logging

from .agent_base import AgentBase

logger = logging.getLogger("AGENT_EURUSD")


class EURUSDAgent(AgentBase):
    """
    Agente Especializado em EURUSD (Euro)
    
    Características:
    - Modelo otimizado para par mais líquido
    - Sensível a diferenciais de taxa ECB/Fed
    - Mean Reversion dominante
    - Aprende padrões de news events
    
    Genoma Específico:
    - liquidity_preference: Preferência por alta liquidez
    - mean_reversion_strength: Força da reversão à média
    - news_sensitivity: Sensibilidade a eventos
    """
    
    def __init__(self, data_path: str = "data/agents/"):
        super().__init__(
            symbol="EURUSD",
            data_path=data_path,
            min_sharpe=-0.3,  # Menos tolerante (par mais previsível)
            evolution_interval=150  # Evolui mais devagar
        )
        
        # Genoma específico do Euro
        self.genome.update({
            "liquidity_preference": 1.2,
            "mean_reversion_strength": 0.7,
            "news_sensitivity": 0.5,
            "session_bias": {
                "asia": 0.6,
                "london": 1.3,
                "newyork": 1.1
            },
            "bollinger_periods": 20,
            "bollinger_std": 2.0
        })
        
        # Estado interno
        self.price_history = []
        self.mean_price = 0.0
        self.std_price = 0.0
        
        logger.info(f"EURUSDAgent initialized with euro-specific genome")
    
    def _get_current_session(self) -> str:
        """Identifica sessão atual"""
        hour = datetime.utcnow().hour
        
        if 0 <= hour < 8:
            return "asia"
        elif 8 <= hour < 16:
            return "london"
        else:
            return "newyork"
    
    def _update_statistics(self, price: float):
        """Atualiza estatísticas de preço"""
        self.price_history.append(price)
        
        # Manter últimos N preços
        periods = self.genome["bollinger_periods"]
        if len(self.price_history) > periods * 2:
            self.price_history = self.price_history[-periods * 2:]
        
        if len(self.price_history) >= periods:
            recent = self.price_history[-periods:]
            self.mean_price = np.mean(recent)
            self.std_price = np.std(recent)
    
    def _calculate_features(self, state: Dict) -> np.ndarray:
        """Extrai features do estado"""
        features = []
        
        bid = state.get("bid", 0)
        ask = state.get("ask", 0)
        mid = (bid + ask) / 2 if bid > 0 else 0
        
        # Atualizar estatísticas
        if mid > 0:
            self._update_statistics(mid)
        
        # Spread normalizado
        spread = (ask - bid) / mid if mid > 0 else 0
        features.append(spread * 10000)  # Em pips
        
        # Z-score (distância da média em desvios padrão)
        if self.std_price > 0:
            z_score = (mid - self.mean_price) / self.std_price
        else:
            z_score = 0
        features.append(z_score)
        
        # Bollinger position (-1 a 1)
        if self.std_price > 0:
            upper = self.mean_price + self.genome["bollinger_std"] * self.std_price
            lower = self.mean_price - self.genome["bollinger_std"] * self.std_price
            bb_pos = (mid - lower) / (upper - lower) if upper != lower else 0.5
            features.append((bb_pos - 0.5) * 2)  # Normalizado -1 a 1
        else:
            features.append(0)
        
        # Se tiver dados OHLCV
        if "ohlcv" in state and len(state["ohlcv"]) >= 5:
            ohlcv = state["ohlcv"]
            closes = [bar[4] for bar in ohlcv[-5:]]
            
            # Momentum curto
            momentum = (closes[-1] - closes[0]) / closes[0] if closes[0] > 0 else 0
            features.append(momentum * 10000)  # Em pips
            
            # Direção das últimas barras
            up_bars = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
            features.append((up_bars / len(closes)) - 0.5)
        else:
            features.extend([0, 0])
        
        # Padding
        while len(features) < 10:
            features.append(0)
        
        return np.array(features[:10])
    
    def generate_signal(self, state: Dict) -> Dict:
        """
        Gera sinal de trading para EURUSD
        
        Estratégia: Mean Reversion com confirmação de momentum
        """
        if not self.active:
            return {"action": "HOLD", "confidence": 0.0, "reason": "Agent inactive"}
        
        features = self._calculate_features(state)
        session = self._get_current_session()
        session_mult = self.genome["session_bias"].get(session, 1.0)
        
        # Modelo
        weights = self.model.get("weights", np.zeros(10))
        bias = self.model.get("bias", 0)
        
        raw_score = np.dot(features, weights) + bias
        
        # Mean reversion component
        z_score = features[1] if len(features) > 1 else 0
        mr_signal = -z_score * self.genome["mean_reversion_strength"]
        
        # Combinar
        combined = (raw_score + mr_signal) * session_mult
        
        # Exploração
        if np.random.random() < self.genome["exploration_rate"]:
            combined += np.random.randn() * 0.3
        
        # Decisão
        confidence = abs(np.tanh(combined))
        
        if combined > self.genome["confidence_threshold"]:
            action = "BUY"
        elif combined < -self.genome["confidence_threshold"]:
            action = "SELL"
        else:
            action = "HOLD"
        
        return {
            "action": action,
            "confidence": float(confidence),
            "symbol": self.symbol,
            "session": session,
            "z_score": float(z_score),
            "mean_reversion_signal": float(mr_signal),
            "timestamp": datetime.now().isoformat()
        }
    
    def learn_online(self, state: Dict, action: str, reward: float, next_state: Dict):
        """Aprendizado online após cada trade"""
        features = self._calculate_features(state)
        lr = self.genome["learning_rate"]
        
        # Target baseado em reward
        if action == "BUY":
            target = 1.0 if reward > 0 else -1.0
        elif action == "SELL":
            target = -1.0 if reward > 0 else 1.0
        else:
            target = 0.0
        
        # Update
        weights = self.model.get("weights", np.zeros(10))
        error = target - np.dot(features, weights)
        weights += lr * error * features
        
        self.model["weights"] = weights
        self.model["last_update"] = datetime.now().isoformat()
        
        # Registrar
        self.record_trade(
            action=action,
            price=state.get("bid", 0),
            volume=0.01,
            pnl=reward,
            confidence=abs(np.tanh(np.dot(features, weights))),
            state_features=features
        )
        
        # Ajustar mean_reversion_strength baseado em performance
        if reward > 0 and abs(features[1]) > 1.5:  # Z-score extremo com lucro
            self.genome["mean_reversion_strength"] = min(
                1.0,
                self.genome["mean_reversion_strength"] * 1.01
            )
        
        logger.debug(f"EURUSD online learning: action={action}, reward={reward:.4f}")

