# deepseek_trading_bridge.py
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import logging
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deepseek_trading.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DeepSeek-Bridge")


class DeepSeekTradingBridge:
    def __init__(self, account_number: int, password: str, server: str):
        self.account_number = account_number
        self.password = password
        self.server = server
        self.connected = False
        self.running = False
        self.decision_callback = None
        
    def connect_mt5(self) -> bool:
        """Conectar ao MetaTrader 5"""
        try:
            if not mt5.initialize():
                logger.error("Falha ao inicializar MT5")
                return False
                
            if not mt5.login(self.account_number, self.password, self.server):
                err = mt5.last_error()
                logger.error(f"Falha no login MT5 | account={self.account_number} server='{self.server}' last_error={err}")
                return False
                
            logger.info(f"Conectado ao MT5 - Conta: {self.account_number}")
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão MT5: {e}")
            return False

    def set_decision_callback(self, callback):
        """Definir callback para decisões do DeepSeek"""
        self.decision_callback = callback

    def get_market_data(self, symbol: str, timeframe: int = mt5.TIMEFRAME_M5, bars: int = 50) -> pd.DataFrame:
        """Obter dados de mercado em tempo real"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            if rates is None or len(rates) == 0:
                return pd.DataFrame()
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Calcular indicadores básicos
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            df['rsi'] = self.calculate_rsi(df['close'], 14)
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['volume_avg'] = df['tick_volume'].rolling(20).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados: {e}")
            return pd.DataFrame()

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def execute_trade(self, symbol: str, signal: str, volume: float, 
                     sl: float = None, tp: float = None) -> bool:
        """Executar ordem de trading"""
        try:
            if not self.connected:
                logger.error("Não conectado ao MT5")
                return False
                
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Símbolo {symbol} não encontrado")
                return False
                
            if not symbol_info.visible:
                mt5.symbol_select(symbol, True)
                time.sleep(1)
            
            point = mt5.symbol_info(symbol).point
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Tick ausente para {symbol}")
                return False
            price = tick.ask if signal == "BUY" else tick.bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl if sl else price - (300 * point) if signal == "BUY" else price + (300 * point),
                "tp": tp if tp else price + (500 * point) if signal == "BUY" else price - (500 * point),
                "deviation": 20,
                "magic": 234000,
                "comment": f"DeepSeek-{signal}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Falha na ordem: {result.comment}")
                return False
            else:
                logger.info(f"Ordem executada: {signal} {symbol} {volume}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao executar trade: {e}")
            return False

    def prepare_market_analysis(self, symbol: str) -> Dict:
        """Preparar análise de mercado para o DeepSeek"""
        df = self.get_market_data(symbol)
        if df.empty:
            return None
            
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        
        analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "price": last['close'],
            "indicators": {
                "ema_12": last['ema_12'],
                "ema_26": last['ema_26'],
                "rsi": last['rsi'],
                "macd": last['macd'],
                "macd_signal": last['macd_signal'],
                "volume": last['tick_volume'],
                "volume_avg": last['volume_avg']
            },
            "trend": "BULL" if last['ema_12'] > last['ema_26'] else "BEAR",
            "momentum": "BULL" if last['macd'] > last['macd_signal'] else "BEAR",
            "volume_spike": last['tick_volume'] > last['volume_avg'] * 1.5
        }
        
        return analysis

    def request_deepseek_decision(self, symbol: str) -> Optional[Dict]:
        """Solicitar decisão do DeepSeek através do Cursor"""
        if not self.decision_callback:
            logger.error("Callback de decisão não configurado")
            return None
            
        # Preparar dados para análise
        market_data = self.prepare_market_analysis(symbol)
        if not market_data:
            return None
            
        # Solicitar decisão via callback
        try:
            decision = self.decision_callback(market_data)
            return decision
        except Exception as e:
            logger.error(f"Erro ao obter decisão: {e}")
            return None

    def run_trading_loop(self, symbols: List[str], interval: int = 60):
        """Loop principal de trading com integração DeepSeek"""
        logger.info("Iniciando Sistema de Ponte DeepSeek + MT5")
        
        if not self.connect_mt5():
            return
        
        self.running = True
        
        while self.running:
            try:
                for symbol in symbols:
                    if not self.running:
                        break
                        
                    logger.info(f"📊 Analisando {symbol}...")
                    
                    # Solicitar decisão do DeepSeek
                    decision = self.request_deepseek_decision(symbol)
                    
                    if decision and decision.get('signal') in ['BUY', 'SELL']:
                        confidence = decision.get('confidence', 0)
                        if confidence > 0.7:
                            # Executar trade baseado na decisão
                            success = self.execute_trade(
                                symbol=symbol,
                                signal=decision['signal'],
                                volume=decision.get('volume', 0.1),
                                sl=decision.get('sl'),
                                tp=decision.get('tp')
                            )
                            
                            if success:
                                logger.info(f"🎯 Trade executado baseado na decisão do DeepSeek")
                    
                    time.sleep(1)  # Pequena pausa entre símbolos
                
                logger.info(f"Proxima analise em {interval} segundos...")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Interrompido pelo usuario")
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop: {e}")
                time.sleep(30)

    def stop_trading(self):
        """Parar sistema de trading"""
        self.running = False
        logger.info("Sistema de trading parado")
        mt5.shutdown()


# Função de callback padrão (será substituída pelo Cursor)
def default_decision_callback(market_data: Dict) -> Dict:
    """Callback padrão para decisões do DeepSeek"""
    # Esta função será substituída pela inteligência do DeepSeek via Cursor
    return {
        "signal": "HOLD",
        "confidence": 0.0,
        "reason": "Callback não configurado"
    }


