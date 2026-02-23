# -*- coding: utf-8 -*-
"""
Capital Manager - Gestão Adaptativa de Risco em Portfólio
Calcula tamanho de posição baseado em risco e capital disponível
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None

logger = logging.getLogger(__name__)


@dataclass
class PositionRisk:
    """Informações de risco de uma posição."""
    symbol: str
    volume: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_per_trade_pct: float
    risk_amount: float
    position_value: float
    margin_required: float
    timestamp: datetime = field(default_factory=datetime.now)


class CapitalManager:
    """
    Gerencia capital e risco adaptativo do portfólio.
    Calcula tamanho de posição baseado em risco disponível.
    """
    
    def __init__(
        self,
        max_risk_per_trade: float = 0.02,  # 2% por trade
        max_portfolio_risk: float = 0.10,  # 10% total do portfólio
        min_position_size: float = 0.01,
        max_position_size: float = 1.0
    ):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.min_position_size = min_position_size
        self.max_position_size = max_position_size
        
        self.portfolio_value: float = 0.0
        self.available_margin: float = 0.0
        self.open_positions: Dict[str, PositionRisk] = {}
        self.daily_pnl: float = 0.0
        self.total_exposure: float = 0.0
        
        self._mt5_initialized = False
        self._initialize_mt5()
        
        logger.info(
            f"CapitalManager inicializado: "
            f"Risco/trade: {max_risk_per_trade*100}%, "
            f"Risco/portfólio: {max_portfolio_risk*100}%"
        )
    
    def _initialize_mt5(self) -> bool:
        """Inicializa conexão MT5 se necessário."""
        if not MT5_AVAILABLE:
            logger.warning("MetaTrader5 não disponível. Usando modo simulação.")
            return False
        
        if self._mt5_initialized:
            return True
        
        if not mt5.initialize():
            error_code, error_details = mt5.last_error()
            logger.warning(f"Falha ao inicializar MT5: {error_code}: {error_details}")
            return False
        
        self._mt5_initialized = True
        self._update_portfolio_info()
        logger.info("Conexão MT5 estabelecida para CapitalManager.")
        return True
    
    def _update_portfolio_info(self):
        """Atualiza informações do portfólio do MT5."""
        if not self._mt5_initialized or not MT5_AVAILABLE:
            # Modo simulação
            self.portfolio_value = 100000.0  # Valor padrão demo
            self.available_margin = 50000.0
            return
        
        try:
            account_info = mt5.account_info()
            if account_info:
                self.portfolio_value = account_info.balance
                self.available_margin = account_info.margin_free
                
                # Atualizar exposição total
                positions = mt5.positions_get()
                if positions:
                    self.total_exposure = sum(
                        pos.volume * pos.price_open 
                        for pos in positions
                    )
                else:
                    self.total_exposure = 0.0
        except Exception as e:
            logger.error(f"Erro ao atualizar informações do portfólio: {e}")
    
    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        risk_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calcula tamanho de posição baseado em risco.
        
        Args:
            symbol: Símbolo do ativo
            entry_price: Preço de entrada
            stop_loss: Preço de stop loss
            risk_amount: Quantia em risco (opcional, calcula se None)
        
        Returns:
            Dict com volume, risco e informações da posição
        """
        self._update_portfolio_info()
        
        # Calcular risco por unidade
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit <= 0:
            logger.warning(f"Risco por unidade inválido para {symbol}: {risk_per_unit}")
            return {
                'volume': 0.0,
                'risk_amount': 0.0,
                'risk_percent': 0.0,
                'valid': False,
                'reason': 'Invalid stop loss'
            }
        
        # Calcular risco em dólares
        if risk_amount is None:
            risk_amount = self.portfolio_value * self.max_risk_per_trade
        
        # Calcular volume baseado no risco
        volume = risk_amount / risk_per_unit
        
        # Obter informações do símbolo para normalizar volume
        symbol_info = None
        if self._mt5_initialized and MT5_AVAILABLE:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                # Normalizar volume para lotes mínimos
                min_volume = symbol_info.volume_min
                max_volume = symbol_info.volume_max
                volume_step = symbol_info.volume_step
                
                volume = max(min_volume, min(volume, max_volume))
                # Arredondar para step
                volume = round(volume / volume_step) * volume_step
        
        # Garantir limites
        volume = max(self.min_position_size, min(volume, self.max_position_size))
        
        # Recalcular risco real
        actual_risk_amount = volume * risk_per_unit
        actual_risk_percent = (actual_risk_amount / self.portfolio_value) * 100
        
        # Verificar limite de risco do portfólio
        portfolio_risk_percent = (self.total_exposure / self.portfolio_value) * 100
        if portfolio_risk_percent + actual_risk_percent > self.max_portfolio_risk * 100:
            logger.warning(
                f"Risco do portfólio excedido: {portfolio_risk_percent:.2f}% + "
                f"{actual_risk_percent:.2f}% > {self.max_portfolio_risk*100}%"
            )
            volume = 0.0
            actual_risk_amount = 0.0
        
        # Calcular take profit (assumindo 2:1 reward:risk)
        take_profit = entry_price + (2 * (entry_price - stop_loss))
        
        result = {
            'volume': volume,
            'risk_amount': actual_risk_amount,
            'risk_percent': actual_risk_percent,
            'take_profit': take_profit,
            'valid': volume > 0,
            'portfolio_risk_before': portfolio_risk_percent,
            'portfolio_risk_after': portfolio_risk_percent + actual_risk_percent
        }
        
        logger.info(
            f"Tamanho de posição calculado para {symbol}: "
            f"Volume: {volume}, Risco: ${actual_risk_amount:.2f} ({actual_risk_percent:.2f}%)"
        )
        
        return result
    
    def can_open_position(self, symbol: str, required_margin: float) -> bool:
        """
        Verifica se pode abrir nova posição.
        
        Args:
            symbol: Símbolo do ativo
            required_margin: Margem necessária para a posição
        
        Returns:
            True se pode abrir posição
        """
        self._update_portfolio_info()
        
        if required_margin > self.available_margin:
            logger.warning(
                f"Margem insuficiente para {symbol}: "
                f"Requerido: ${required_margin:.2f}, Disponível: ${self.available_margin:.2f}"
            )
            return False
        
        # Verificar limite de posições abertas por símbolo
        if symbol in self.open_positions:
            logger.warning(f"Já existe posição aberta para {symbol}")
            return False
        
        return True
    
    def register_position(self, position: PositionRisk):
        """Registra nova posição aberta."""
        self.open_positions[position.symbol] = position
        self.total_exposure += position.position_value
        logger.info(f"Posição registrada: {position.symbol} - Volume: {position.volume}")
    
    def close_position(self, symbol: str, pnl: float):
        """Remove posição fechada e atualiza P&L."""
        if symbol in self.open_positions:
            position = self.open_positions.pop(symbol)
            self.total_exposure -= position.position_value
            self.daily_pnl += pnl
            logger.info(f"Posição fechada: {symbol} - P&L: ${pnl:.2f}")
        else:
            logger.warning(f"Tentativa de fechar posição inexistente: {symbol}")
    
    def get_portfolio_status(self) -> Dict[str, Any]:
        """Retorna status completo do portfólio."""
        self._update_portfolio_info()
        
        return {
            'portfolio_value': self.portfolio_value,
            'available_margin': self.available_margin,
            'total_exposure': self.total_exposure,
            'exposure_percent': (self.total_exposure / self.portfolio_value * 100) if self.portfolio_value > 0 else 0,
            'daily_pnl': self.daily_pnl,
            'open_positions_count': len(self.open_positions),
            'open_positions': list(self.open_positions.keys())
        }

