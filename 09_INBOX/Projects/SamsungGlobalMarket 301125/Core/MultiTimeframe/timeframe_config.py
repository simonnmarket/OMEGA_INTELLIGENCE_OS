"""
Configurações e estruturas de dados para análise Multi-Timeframe

Referências Científicas:
- Elder (1993): Triple Screen System configuration
- Murphy (1999): Confluence weighting methodology
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class TimeframeConfig:
    """
    Configuração de um timeframe específico
    
    Attributes:
        name: Nome descritivo (ex: 'monthly', 'weekly', 'daily')
        period: Período no formato pandas/ccxt (ex: '1M', '1W', '1D', '4H', '1H', '15T')
        function: Função do timeframe ('trend', 'swing', 'setup', 'timing', 'confirmation', 'execution')
        weight: Peso na confluência 0.0-1.0 (maior = mais importante)
    
    Baseado em Elder (1993) Triple Screen methodology
    """
    name: str
    period: str
    function: str  # 'trend', 'swing', 'setup', 'timing', 'confirmation', 'execution'
    weight: float  # 0.0-1.0
    
    def __post_init__(self):
        """Validação de parâmetros"""
        valid_functions = ['trend', 'swing', 'setup', 'timing', 'confirmation', 'execution']
        if self.function not in valid_functions:
            raise ValueError(f"function deve ser um de: {valid_functions}")
        
        if not (0.0 <= self.weight <= 1.0):
            raise ValueError(f"weight deve estar entre 0.0 e 1.0, recebido: {self.weight}")


@dataclass
class MultiTimeframeSignal:
    """
    Sinal de trading com análise multi-timeframe completa
    
    Attributes:
        action: 'BUY', 'SELL', ou 'HOLD'
        confidence: Score de confiança 0.0-1.0
        timeframes_aligned: Número de timeframes alinhados com tendência primária
        confluence_score: Score de confluência (Murphy 1999)
        entry_price: Preço de entrada sugerido
        stop_loss: Preço de stop loss otimizado (TF baixo)
        take_profit: Preço de take profit otimizado (TF alto)
        risk_reward: Razão risk/reward
        timeframe_analysis: Detalhes da análise por timeframe
        metadata: Informações adicionais
    
    Baseado em:
    - Elder (1993): Entry/Exit optimization
    - Murphy (1999): Confluence scoring
    """
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0.0-1.0
    timeframes_aligned: int
    confluence_score: float  # 0.0-1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    timeframe_analysis: Dict  # Análise detalhada por TF
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        """Validação de parâmetros"""
        if self.action not in ['BUY', 'SELL', 'HOLD']:
            raise ValueError(f"action deve ser BUY, SELL, ou HOLD, recebido: {self.action}")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence deve estar entre 0.0 e 1.0, recebido: {self.confidence}")
        
        if not (0.0 <= self.confluence_score <= 1.0):
            raise ValueError(f"confluence_score deve estar entre 0.0 e 1.0, recebido: {self.confluence_score}")
    
    def to_dict(self) -> Dict:
        """Converte para dicionário (compatível com TradingSignalPerfeito)"""
        return {
            'action': self.action,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'risk_reward': self.risk_reward,
            'timeframes_aligned': self.timeframes_aligned,
            'confluence_score': self.confluence_score,
            'mtf_enabled': True,
            'metadata': self.metadata or {}
        }

