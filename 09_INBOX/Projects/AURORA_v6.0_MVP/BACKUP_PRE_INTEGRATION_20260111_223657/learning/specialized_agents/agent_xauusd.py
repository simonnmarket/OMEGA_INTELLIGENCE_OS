"""
XAUUSD Agent - AURORA v6.0 MVP
Agente especializado em Gold (XAU/USD)
"""

import numpy as np
from typing import Dict
from datetime import datetime
import logging

from .agent_base import AgentBase

logger = logging.getLogger("AGENT_XAUUSD")


class XAUUSDAgent(AgentBase):
    """
    Agente Especializado em XAUUSD (Gold)
    
    Características:
    - Modelo otimizado para volatilidade do ouro
    - Sensível a USD strength e risk-off flows
    - Momentum + Mean Reversion híbrido
    - Aprende padrões de sessões (Asia/London/NY)
    
    Genoma Específico:
    - gold_volatility_factor: Ajuste para alta volatilidade
    - usd_correlation_weight: Peso da correlação com DXY
    - session_bias: Preferência por sessão de trading
    """
    
    def __init__(self, data_path: str = "data/agents/"):
        super().__init__(
            symbol="XAUUSD",
            data_path=data_path,
            min_sharpe=-0.5,  # Mais tolerante inicialmente
            evolution_interval=100
        )
        
        # Genoma específico do Gold
        self.genome.update({
            "gold_volatility_factor": 1.5,
            "usd_correlation_weight": 0.3,
            "session_bias": {
                "asia": 0.8,
                "london": 1.2,
                "newyork": 1.0
            },
            "atr_multiplier": 2.0,
            "trend_confirmation_bars": 3
        })
        
        # Estado interno
        self.last_signals = []
        self.session_performance = {"asia": 0, "london": 0, "newyork": 0}
        
        logger.info(f"XAUUSDAgent initialized with gold-specific genome")
    
    def _get_current_session(self) -> str:
        """Identifica sessão atual baseado em hora UTC"""
        hour = datetime.utcnow().hour
        
        if 0 <= hour < 8:
            return "asia"
        elif 8 <= hour < 16:
            return "london"
        else:
            return "newyork"
    
    def _calculate_features(self, state: Dict) -> np.ndarray:
        """Extrai features do estado para o modelo"""
        features = []
        
        # Price features
        bid = state.get("bid", 0)
        ask = state.get("ask", 0)
        spread = ask - bid
        
        features.append(spread / bid if bid > 0 else 0)  # Spread normalizado
        
        # Se tiver dados históricos
        if "ohlcv" in state:
            ohlcv = state["ohlcv"]
            if len(ohlcv) >= 10:
                closes = [bar[4] for bar in ohlcv[-10:]]
                
                # Momentum (retorno 5 barras)
                momentum = (closes[-1] - closes[-5]) / closes[-5] if closes[-5] > 0 else 0
                features.append(momentum)
                
                # Volatilidade (std dos retornos)
                returns = np.diff(closes) / closes[:-1]
                volatility = np.std(returns) if len(returns) > 0 else 0
                features.append(volatility * self.genome["gold_volatility_factor"])
                
                # RSI simplificado
                gains = [r for r in returns if r > 0]
                losses = [-r for r in returns if r < 0]
                avg_gain = np.mean(gains) if gains else 0
                avg_loss = np.mean(losses) if losses else 0.0001
                rsi = 100 - (100 / (1 + avg_gain / avg_loss))
                features.append((rsi - 50) / 50)  # Normalizado -1 a 1
        
        # Padding se necessário
        while len(features) < 10:
            features.append(0)
        
        return np.array(features[:10])
    
    def generate_signal(self, state: Dict) -> Dict:
        """
        Gera sinal de trading para XAUUSD
        
        Args:
            state: {
                "bid": float,
                "ask": float,
                "ohlcv": List[Tuple] (opcional),
                "indicators": Dict (opcional)
            }
            
        Returns:
            {"action": "BUY|SELL|HOLD", "confidence": 0.0-1.0, "metadata": Dict}
        """
        if not self.active:
            return {"action": "HOLD", "confidence": 0.0, "reason": "Agent inactive"}
        
        # Extrair features
        features = self._calculate_features(state)
        
        # Sessão atual
        session = self._get_current_session()
        session_multiplier = self.genome["session_bias"].get(session, 1.0)
        
        # Modelo simples: combinação linear + exploração
        weights = self.model.get("weights", np.zeros(10))
        bias = self.model.get("bias", 0)
        
        # Score bruto
        raw_score = np.dot(features, weights) + bias
        
        # Aplicar fatores
        adjusted_score = raw_score * session_multiplier * self.genome["gold_volatility_factor"]
        
        # Exploração (epsilon-greedy)
        if np.random.random() < self.genome["exploration_rate"]:
            adjusted_score += np.random.randn() * 0.5
        
        # Converter para ação
        confidence = abs(np.tanh(adjusted_score))
        
        if adjusted_score > self.genome["confidence_threshold"]:
            action = "BUY"
        elif adjusted_score < -self.genome["confidence_threshold"]:
            action = "SELL"
        else:
            action = "HOLD"
        
        # Guardar para análise
        signal = {
            "action": action,
            "confidence": float(confidence),
            "symbol": self.symbol,
            "session": session,
            "raw_score": float(raw_score),
            "features": features.tolist(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.last_signals.append(signal)
        if len(self.last_signals) > 100:
            self.last_signals.pop(0)
        
        return signal
    
    def learn_online(self, state: Dict, action: str, reward: float, next_state: Dict):
        """
        Aprendizado online após cada trade
        
        Atualiza pesos do modelo baseado no reward
        """
        features = self._calculate_features(state)
        
        # Learning rate adaptativo
        lr = self.genome["learning_rate"]
        
        # Gradient simples: ajustar pesos na direção do reward
        if action == "BUY":
            target = 1.0 if reward > 0 else -1.0
        elif action == "SELL":
            target = -1.0 if reward > 0 else 1.0
        else:
            target = 0.0
        
        # Update weights
        weights = self.model.get("weights", np.zeros(10))
        error = target - np.dot(features, weights)
        
        # Gradient descent step
        weights += lr * error * features
        
        # Atualizar modelo
        self.model["weights"] = weights
        self.model["last_update"] = datetime.now().isoformat()
        
        # Registrar trade
        self.record_trade(
            action=action,
            price=state.get("bid", 0),
            volume=0.01,
            pnl=reward,
            confidence=abs(np.tanh(np.dot(features, weights))),
            state_features=features
        )
        
        # Atualizar performance por sessão
        session = self._get_current_session()
        self.session_performance[session] += reward
        
        logger.debug(f"XAUUSD online learning: action={action}, reward={reward:.4f}")
    
    def get_session_stats(self) -> Dict:
        """Retorna estatísticas por sessão"""
        return {
            "session_performance": self.session_performance,
            "current_session": self._get_current_session(),
            "session_bias": self.genome["session_bias"]
        }

