"""
MT5 Connector - AURORA v6.0 MVP
Gerencia conexão e operações com MetaTrader 5
"""

import MetaTrader5 as mt5
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger("MT5_CONNECTOR")


class MT5Connector:
    """
    Conector para MetaTrader 5
    Responsável por:
    - Inicializar/finalizar conexão
    - Executar ordens (BUY/SELL)
    - Consultar posições e saldo
    - Obter dados de mercado
    """
    
    def __init__(self, account: int = None, server: str = None, password: str = None):
        self.account = account
        self.server = server
        self.password = password
        self.connected = False
        self.last_error = None
        
    def connect(self) -> bool:
        """Inicializa conexão com MT5"""
        try:
            if not mt5.initialize():
                self.last_error = mt5.last_error()
                logger.error(f"MT5 initialize failed: {self.last_error}")
                return False
            
            # Login se credenciais fornecidas
            if self.account and self.password:
                if not mt5.login(self.account, password=self.password, server=self.server):
                    self.last_error = mt5.last_error()
                    logger.error(f"MT5 login failed: {self.last_error}")
                    return False
            
            self.connected = True
            account_info = mt5.account_info()
            logger.info(f"MT5 connected: {account_info.login} @ {account_info.server}")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Finaliza conexão com MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 disconnected")
    
    def get_account_info(self) -> Optional[Dict]:
        """Retorna informações da conta"""
        if not self.connected:
            return None
        
        info = mt5.account_info()
        if info:
            return {
                "login": info.login,
                "server": info.server,
                "balance": info.balance,
                "equity": info.equity,
                "margin": info.margin,
                "free_margin": info.margin_free,
                "currency": info.currency,
                "leverage": info.leverage
            }
        return None
    
    def execute_order(
        self,
        symbol: str,
        action: str,  # "BUY" or "SELL"
        volume: float,
        sl: float = None,
        tp: float = None,
        comment: str = "AURORA_v6"
    ) -> Dict:
        """
        Executa ordem no MT5
        
        Returns:
            dict: {success: bool, order_id: int, error: str}
        """
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        
        # Obter info do símbolo
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return {"success": False, "error": f"Symbol {symbol} not found"}
        
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)
        
        # Preparar request
        tick = mt5.symbol_info_tick(symbol)
        price = tick.ask if action == "BUY" else tick.bid
        
        order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        if sl:
            request["sl"] = sl
        if tp:
            request["tp"] = tp
        
        # Enviar ordem
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {
                "success": False,
                "error": f"Order failed: {result.retcode} - {result.comment}",
                "retcode": result.retcode
            }
        
        logger.info(f"Order executed: {action} {volume} {symbol} @ {price}")
        
        return {
            "success": True,
            "order_id": result.order,
            "price": price,
            "volume": volume,
            "symbol": symbol,
            "action": action
        }
    
    def close_position(self, ticket: int) -> Dict:
        """Fecha posição pelo ticket"""
        if not self.connected:
            return {"success": False, "error": "Not connected"}
        
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return {"success": False, "error": f"Position {ticket} not found"}
        
        pos = position[0]
        symbol = pos.symbol
        volume = pos.volume
        
        # Ordem inversa para fechar
        action = "SELL" if pos.type == mt5.POSITION_TYPE_BUY else "BUY"
        
        return self.execute_order(symbol, action, volume, comment=f"Close_{ticket}")
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """Retorna posições abertas"""
        if not self.connected:
            return []
        
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()
        
        if positions is None:
            return []
        
        return [
            {
                "ticket": p.ticket,
                "symbol": p.symbol,
                "type": "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL",
                "volume": p.volume,
                "price_open": p.price_open,
                "price_current": p.price_current,
                "profit": p.profit,
                "sl": p.sl,
                "tp": p.tp
            }
            for p in positions
        ]
    
    def get_market_data(self, symbol: str, timeframe: int = mt5.TIMEFRAME_M5, count: int = 100):
        """Obtém dados OHLCV do mercado"""
        if not self.connected:
            return None
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        return rates
    
    def get_tick(self, symbol: str) -> Optional[Dict]:
        """Obtém tick atual"""
        if not self.connected:
            return None
        
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            return {
                "bid": tick.bid,
                "ask": tick.ask,
                "last": tick.last,
                "volume": tick.volume,
                "time": datetime.fromtimestamp(tick.time)
            }
        return None


# Singleton para uso global
_connector_instance = None

def get_connector() -> MT5Connector:
    """Retorna instância singleton do connector"""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = MT5Connector()
    return _connector_instance

