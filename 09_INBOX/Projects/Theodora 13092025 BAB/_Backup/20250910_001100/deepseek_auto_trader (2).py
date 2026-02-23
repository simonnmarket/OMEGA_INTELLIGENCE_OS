# deepseek_auto_trader.py
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_log.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DeepSeekAutoTrader")


class DeepSeekAutoTrader:
    def __init__(self, account_number: int, password: str, server: str):
        self.account_number = account_number
        self.password = password
        self.server = server
        self.connected = False
        self.running = False
        self.trade_count = 0
        self.max_trades_per_day = 10
        
    def connect_mt5(self) -> bool:
        """Conectar ao MetaTrader 5"""
        try:
            if not mt5.initialize():
                logger.error("❌ Falha ao inicializar MT5")
                return False
                
            if not mt5.login(self.account_number, self.password, self.server):
                logger.error("❌ Falha no login MT5")
                return False
                
            logger.info(f"✅ Conectado ao MT5 - Conta: {self.account_number}")
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão MT5: {e}")
            return False

    def get_realtime_data(self, symbol: str, timeframe: int = mt5.TIMEFRAME_M5, bars: int = 50) -> pd.DataFrame:
        """Obter dados em tempo real do MT5"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            if rates is None or len(rates) == 0:
                return pd.DataFrame()
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Calcular indicadores técnicos
            df = self.calculate_indicators(df)
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular todos os indicadores técnicos"""
        # Médias móveis
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volume
        df['volume_sma'] = df['tick_volume'].rolling(20).mean()
        
        return df

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def analyze_market(self, symbol: str, df: pd.DataFrame) -> Dict:
        """Análise completa do mercado usando IA local"""
        if df.empty or len(df) < 20:
            return {"signal": "HOLD", "confidence": 0.0, "reason": "Dados insuficientes"}
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 1. ANÁLISE DE TENDÊNCIA
        trend_bullish = last['ema_12'] > last['ema_26'] > last['sma_50']
        trend_bearish = last['ema_12'] < last['ema_26'] < last['sma_50']
        
        # 2. ANÁLISE DE MOMENTUM
        rsi_oversold = last['rsi'] < 30
        rsi_overbought = last['rsi'] > 70
        rsi_bullish = last['rsi'] > 50 and last['rsi'] > prev['rsi']
        rsi_bearish = last['rsi'] < 50 and last['rsi'] < prev['rsi']
        
        # 3. ANÁLISE MACD
        macd_bullish = last['macd'] > last['macd_signal'] and last['macd_hist'] > 0
        macd_bearish = last['macd'] < last['macd_signal'] and last['macd_hist'] < 0
        
        # 4. ANÁLISE BOLLINGER
        bb_oversold = last['close'] < last['bb_lower'] * 1.02
        bb_overbought = last['close'] > last['bb_upper'] * 0.98
        bb_squeeze = (last['bb_upper'] - last['bb_lower']) / last['bb_middle'] < 0.01
        
        # 5. ANÁLISE DE VOLUME
        volume_spike = last['tick_volume'] > last['volume_sma'] * 2.0
        
        # LÓGICA DE DECISÃO AVANÇADA
        confidence = 0.0
        signal = "HOLD"
        reason = "Aguardando confirmação"
        
        # SINAL DE COMPRA FORTE
        if (trend_bullish and rsi_oversold and macd_bullish and 
            bb_oversold and volume_spike):
            confidence = 0.92
            signal = "BUY"
            reason = "Tendência alta + RSI oversold + MACD positivo + BB oversold + Volume alto"
        
        # SINAL DE VENDA FORTE
        elif (trend_bearish and rsi_overbought and macd_bearish and 
              bb_overbought and volume_spike):
            confidence = 0.88
            signal = "SELL"
            reason = "Tendência baixa + RSI overbought + MACD negativo + BB overbought + Volume alto"
        
        # SINAIS MODERADOS
        elif trend_bullish and rsi_bullish and macd_bullish:
            confidence = 0.75
            signal = "BUY"
            reason = "Tendência alta + Momentum positivo + MACD favorável"
            
        elif trend_bearish and rsi_bearish and macd_bearish:
            confidence = 0.72
            signal = "SELL"
            reason = "Tendência baixa + Momentum negativo + MACD favorável"
        
        # CALCULAR STOP LOSS E TAKE PROFIT
        atr = (df['high'].iloc[-20:].max() - df['low'].iloc[-20:].min()) * 0.1
        current_price = last['close']
        
        if signal == "BUY":
            sl = current_price - (atr * 1.5)
            tp = current_price + (atr * 2.5)
        elif signal == "SELL":
            sl = current_price + (atr * 1.5)
            tp = current_price - (atr * 2.5)
        else:
            sl = tp = 0.0
        
        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": round(confidence, 2),
            "reason": reason,
            "price": round(current_price, 5),
            "sl": round(sl, 5),
            "tp": round(tp, 5),
            "time": datetime.now().strftime("%H:%M:%S"),
            "rsi": round(last['rsi'], 2),
            "trend": "BULL" if trend_bullish else "BEAR" if trend_bearish else "NEUTRAL"
        }

    def execute_trade(self, analysis: Dict, lot_size: float = 0.1) -> bool:
        """Executar ordem baseada na análise"""
        if not self.connected:
            logger.error("❌ Não conectado ao MT5")
            return False
            
        if self.trade_count >= self.max_trades_per_day:
            logger.warning("⚠️ Limite diário de trades atingido")
            return False
            
        symbol = analysis['symbol']
        signal = analysis['signal']
        
        try:
            # Selecionar símbolo
            if not mt5.symbol_select(symbol, True):
                logger.error(f"❌ Símbolo {symbol} não disponível")
                return False
            
            # Obter preço atual
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"❌ Erro ao obter tick para {symbol}")
                return False
                
            price = tick.ask if signal == "BUY" else tick.bid
            point = mt5.symbol_info(symbol).point
            deviation = 20
            
            # Preparar ordem
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_BUY if signal == "BUY" else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": analysis['sl'],
                "tp": analysis['tp'],
                "deviation": deviation,
                "magic": 2024,
                "comment": f"DeepSeekAuto_{signal}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            # Enviar ordem
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.trade_count += 1
                logger.info(f"✅ ORDEM EXECUTADA: {signal} {symbol} {lot_size}L")
                logger.info(f"   📊 Preço: {price} | SL: {analysis['sl']} | TP: {analysis['tp']}")
                logger.info(f"   🎯 Confidence: {analysis['confidence']} | RSI: {analysis['rsi']}")
                return True
            else:
                logger.error(f"❌ Erro na ordem: {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar trade: {e}")
            return False

    def monitor_market(self, symbols: List[str], interval: int = 60):
        """Monitorar mercado em tempo real"""
        logger.info(f"🎯 Iniciando monitoramento para: {', '.join(symbols)}")
        logger.info(f"⏰ Intervalo de análise: {interval} segundos")
        
        while self.running:
            try:
                for symbol in symbols:
                    # Obter dados em tempo real
                    df = self.get_realtime_data(symbol)
                    if df.empty:
                        continue
                    
                    # Analisar mercado
                    analysis = self.analyze_market(symbol, df)
                    
                    # Log da análise
                    log_msg = (f"{symbol}: {analysis['signal']} "
                              f"(Conf: {analysis['confidence']}) | "
                              f"RSI: {analysis['rsi']} | "
                              f"Preço: {analysis['price']}")
                    logger.info(log_msg)
                    
                    # Executar trade se confiança alta
                    if analysis['confidence'] >= 0.7 and analysis['signal'] != 'HOLD':
                        if self.execute_trade(analysis):
                            logger.info(f"💡 Motivo: {analysis['reason']}")
                    
                    time.sleep(1)  # Pequena pausa entre símbolos
                
                # Aguardar próximo ciclo
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(30)

    def start_trading(self, symbols: List[str], analysis_interval: int = 60):
        """Iniciar sistema de trading"""
        if not self.connect_mt5():
            return False
            
        self.running = True
        self.trade_count = 0
        
        # Iniciar thread de monitoramento
        monitor_thread = threading.Thread(
            target=self.monitor_market,
            args=(symbols, analysis_interval),
            daemon=True
        )
        monitor_thread.start()
        
        logger.info("🚀 Sistema DeepSeek AutoTrader INICIADO!")
        logger.info("📊 Monitorando mercado em tempo real...")
        logger.info("⏸️  Pressione Ctrl+C para parar")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_trading()
            
        return True

    def stop_trading(self):
        """Parar sistema de trading"""
        self.running = False
        logger.info("🛑 Sistema de trading parado")
        mt5.shutdown()


# CONFIGURAÇÃO PRINCIPAL
if __name__ == "__main__":
    # ================= CONFIGURAÇÃO =================
    # ↪ SUAS CREDENCIAIS MT5 (EDITAR AQUI!)
    MT5_ACCOUNT = 12345678            # Seu número da conta
    MT5_PASSWORD = "sua_senha"        # Sua senha do MT5
    MT5_SERVER = "seu_servidor"       # Nome do servidor
    
    # ↪ SÍMBOLOS PARA NEGOCIAR
    SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
    
    # ↪ CONFIGURAÇÕES DE TRADING
    ANALYSIS_INTERVAL = 60            # Segundos entre análises (60 = 1 min)
    LOT_SIZE = 0.1                    # Tamanho do lote padrão
    
    # ================= EXECUÇÃO =================
    trader = DeepSeekAutoTrader(MT5_ACCOUNT, MT5_PASSWORD, MT5_SERVER)
    
    try:
        trader.start_trading(SYMBOLS, ANALYSIS_INTERVAL)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
    finally:
        trader.stop_trading()


