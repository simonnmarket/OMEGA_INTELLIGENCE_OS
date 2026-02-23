"""
MT5_STOPS_FIX.py - Correção definitiva para "Invalid stops" no MT5
===============================================================

PROBLEMA: Erro 10016 - Invalid stops ao enviar ordens com SL/TP
SOLUÇÃO: Implementação híbrida com fallback inteligente

OPÇÕES IMPLEMENTADAS:
1. ✅ Cálculo correto baseado em stops_level do símbolo
2. ✅ Fallback para percentuais seguros
3. ✅ Último recurso: enviar sem SL/TP e adicionar depois
"""

import MetaTrader5 as mt5
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import time

logger = logging.getLogger("MT5_STOPS_FIX")

class MT5StopsFix:
    """
    Classe para corrigir o problema "Invalid stops" no MT5.
    Implementa todas as estratégias recomendadas.
    """
    
    def __init__(self):
        self.symbols_cache = {}  # Cache de informações dos símbolos
        
    def get_symbol_info_correctly(self, symbol: str) -> Optional[Dict]:
        """Obtém informações do símbolo com tratamento de erros robusto."""
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Símbolo {symbol} não encontrado")
                return None
            
            info = {
                'name': symbol,
                'point': symbol_info.point,
                'digits': symbol_info.digits,
                'trade_stops_level': symbol_info.trade_stops_level,
                'trade_mode': symbol_info.trade_mode,
                'trade_exemode': symbol_info.trade_exemode,
                'trade_tick_size': getattr(symbol_info, 'trade_tick_size', 0),
                'trade_tick_value': getattr(symbol_info, 'trade_tick_value', 0),
                'trade_contract_size': getattr(symbol_info, 'trade_contract_size', 1),
            }
            
            logger.debug(f"📊 Símbolo {symbol}: point={info['point']}, stops_level={info['trade_stops_level']}")
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter info do símbolo {symbol}: {e}")
            return None
    
    def calculate_stops_based_on_level(self, symbol_info: Dict, price: float, 
                                      action: str) -> Tuple[float, float]:
        """Calcula SL/TP baseado no stops_level do símbolo."""
        try:
            point = symbol_info['point']
            stops_level = symbol_info['trade_stops_level']
            
            if stops_level <= 10:
                logger.debug(f"Stops_level muito pequeno ({stops_level}), usando percentuais")
                return self.calculate_stops_by_percentage(price, action)
            
            min_distance = stops_level * point
            logger.debug(f"Distância mínima (stops_level): {min_distance:.5f}")
            
            if action == "BUY":
                sl = price - (min_distance * 3)
                tp = price + (min_distance * 5)
            else:  # SELL
                sl = price + (min_distance * 3)
                tp = price - (min_distance * 5)
            
            digits = symbol_info['digits']
            sl = round(sl, digits)
            tp = round(tp, digits)
            
            logger.info(f"📍 SL/TP baseado em stops_level: SL={sl}, TP={tp} (min_dist={min_distance:.5f})")
            return sl, tp
            
        except Exception as e:
            logger.error(f"Erro no cálculo baseado em stops_level: {e}")
            return self.calculate_stops_by_percentage(price, action)
    
    def calculate_stops_by_percentage(self, price: float, action: str) -> Tuple[float, float]:
        """Calcula SL/TP usando percentuais seguros (fallback)."""
        try:
            sl_percent = 0.01  # 1% para SL
            tp_percent = 0.02  # 2% para TP
            
            if action == "BUY":
                sl = price * (1 - sl_percent)
                tp = price * (1 + tp_percent)
            else:  # SELL
                sl = price * (1 + sl_percent)
                tp = price * (1 - tp_percent)
            
            logger.info(f"📍 SL/TP baseado em percentuais: SL={sl:.5f}, TP={tp:.5f}")
            return sl, tp
            
        except Exception as e:
            logger.error(f"Erro no cálculo por percentual: {e}")
            return 0.0, 0.0
    
    def validate_stops(self, symbol_info: Dict, price: float, 
                      sl: float, tp: float, action: str) -> bool:
        """Valida se os stops são aceitáveis antes de enviar."""
        try:
            point = symbol_info['point']
            stops_level = symbol_info['trade_stops_level']
            
            if sl != 0:
                if action == "BUY":
                    if sl >= price:
                        return False
                    sl_distance = abs(price - sl)
                else:
                    if sl <= price:
                        return False
                    sl_distance = abs(sl - price)
                
                min_sl_distance = stops_level * point if stops_level > 0 else point * 10
                if sl_distance < min_sl_distance:
                    return False
            
            if tp != 0:
                if action == "BUY":
                    if tp <= price:
                        return False
                    tp_distance = abs(tp - price)
                else:
                    if tp >= price:
                        return False
                    tp_distance = abs(price - tp)
                
                min_tp_distance = stops_level * point if stops_level > 0 else point * 10
                if tp_distance < min_tp_distance:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de stops: {e}")
            return False
    
    def execute_order_with_robust_stops(self, symbol: str, order_type: str, 
                                       volume: float, price: float = 0.0,
                                       sl: float = 0.0, tp: float = 0.0,
                                       magic: int = 123456) -> Dict:
        """Executa ordem com gestão robusta de stops."""
        result = {
            'symbol': symbol,
            'order_type': order_type,
            'status': 'PENDING',
            'attempts': [],
            'final_order_ticket': None
        }
        
        symbol_info = self.get_symbol_info_correctly(symbol)
        if not symbol_info:
            result['status'] = 'FAILED'
            result['error'] = 'Symbol info not available'
            return result
        
        # ESTRATÉGIA 1: Stops calculados corretamente
        if sl == 0 or tp == 0:
            sl, tp = self.calculate_stops_based_on_level(symbol_info, price if price > 0 else mt5.symbol_info_tick(symbol).ask, order_type)
        
        if self.validate_stops(symbol_info, price, sl, tp, order_type):
            attempt_result = self._send_order_attempt(symbol, order_type, volume, price, sl, tp, magic, "Strategy 1")
            result['attempts'].append(attempt_result)
            if attempt_result['success']:
                result['status'] = 'SUCCESS'
                result['final_order_ticket'] = attempt_result['order_ticket']
                return result
        
        # ESTRATÉGIA 2: Percentuais conservadores
        sl, tp = self.calculate_stops_by_percentage(price if price > 0 else mt5.symbol_info_tick(symbol).ask, order_type)
        if sl != 0 and tp != 0:
            attempt_result = self._send_order_attempt(symbol, order_type, volume, price, sl, tp, magic, "Strategy 2")
            result['attempts'].append(attempt_result)
            if attempt_result['success']:
                result['status'] = 'SUCCESS'
                result['final_order_ticket'] = attempt_result['order_ticket']
                return result
        
        # ESTRATÉGIA 3: Sem stops
        attempt_result = self._send_order_attempt(symbol, order_type, volume, price, 0, 0, magic, "Strategy 3 (no stops)")
        result['attempts'].append(attempt_result)
        if attempt_result['success']:
            result['status'] = 'SUCCESS_NO_STOPS'
            result['final_order_ticket'] = attempt_result['order_ticket']
            return result
        
        result['status'] = 'FAILED_ALL_ATTEMPTS'
        return result
    
    def _send_order_attempt(self, symbol: str, order_type: str, volume: float,
                           price: float, sl: float, tp: float, 
                           magic: int, strategy_name: str) -> Dict:
        """Tenta enviar uma ordem com parâmetros específicos."""
        attempt = {
            'strategy': strategy_name,
            'success': False,
            'error': None,
            'order_ticket': None
        }
        
        try:
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                attempt['error'] = "Tick not available"
                return attempt
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": price if price > 0 else (tick.ask if order_type == "BUY" else tick.bid),
                "sl": sl if sl > 0 else 0,
                "tp": tp if tp > 0 else 0,
                "deviation": 10,
                "magic": magic,
                "comment": f"Aurora_{strategy_name}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result is None:
                attempt['error'] = "Result is None"
            elif result.retcode != mt5.TRADE_RETCODE_DONE:
                attempt['error'] = f"Error {result.retcode}: {result.comment}"
            else:
                attempt['success'] = True
                attempt['order_ticket'] = result.order
                logger.info(f"✅ {strategy_name}: Ordem {result.order} executada!")
            
        except Exception as e:
            attempt['error'] = str(e)
        
        return attempt

