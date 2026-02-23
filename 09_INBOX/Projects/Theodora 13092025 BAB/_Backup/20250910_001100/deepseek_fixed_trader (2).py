import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_fixed.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DeepSeek-Fixed")


class FixedTrader:
    def __init__(self, account, password, server):
        self.account = account
        self.password = password
        self.server = server
        self.connected = False

    def connect_mt5(self):
        """Conectar ao MT5 com verificação robusta"""
        try:
            logger.info("Inicializando MT5...")

            # Fechar qualquer sessão anterior
            try:
                if mt5.initialize():
                    mt5.shutdown()
                    time.sleep(0.5)
            except Exception:
                pass

            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"Falha ao inicializar: {error}")
                return False

            logger.info("Tentando login...")
            authorized = mt5.login(self.account, self.password, self.server)
            if not authorized:
                error = mt5.last_error()
                logger.error(f"Login falhou: {error}")
                mt5.shutdown()
                return False

            acc_info = mt5.account_info()
            if acc_info is None:
                logger.error("Não foi possível obter informações da conta")
                mt5.shutdown()
                return False

            logger.info(f"CONECTADO! Conta: {acc_info.login}")
            logger.info(f"Saldo: ${acc_info.balance}")
            logger.info(f"Corretora: {acc_info.company}")

            self.connected = True
            return True

        except Exception as e:
            logger.error(f"Erro fatal na conexão: {e}")
            return False

    def _ensure_symbol(self, symbol: str) -> bool:
        info = mt5.symbol_info(symbol)
        if info is None:
            logger.error(f"Símbolo inválido/indisponível: {symbol}")
            return False
        if not info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Não foi possível selecionar {symbol}")
                return False
        return True

    def get_data(self, symbol, timeframe=mt5.TIMEFRAME_M1, bars=240):
        """Buscar dados com verificação robusta"""
        try:
            if not self._ensure_symbol(symbol):
                return None

            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            if rates is None or len(rates) == 0:
                logger.warning(f"Sem dados para {symbol}. last_error={mt5.last_error()}")
                return None

            df = pd.DataFrame(rates)
            if df.empty:
                logger.warning(f"DataFrame vazio para {symbol}")
                return None

            df['time'] = pd.to_datetime(df['time'], unit='s')

            # Indicadores
            df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
            df['rsi'] = self.calculate_rsi(df['close'], 14)

            logger.debug(f"{symbol}: {len(df)} candles, Último close: {float(df['close'].iloc[-1]):.5f}")
            return df

        except Exception as e:
            logger.error(f"Erro em get_data para {symbol}: {e}")
            return None

    def calculate_rsi(self, prices, period):
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0.0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
        loss = loss.replace(0, 1e-10)
        rs = gain / loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi.fillna(method='bfill').fillna(50.0)

    def analyze_market(self, symbol):
        """Análise de mercado simplificada e robusta"""
        df = self.get_data(symbol)
        if df is None or len(df) < 20:
            return None

        last = df.iloc[-1]

        trend_up = last['ema_fast'] > last['ema_slow']
        rsi_low = last['rsi'] < 40
        rsi_high = last['rsi'] > 60

        logger.debug(f"{symbol} - Preço: {float(last['close']):.5f}, RSI: {float(last['rsi']):.1f}, EMA: {'UP' if trend_up else 'DOWN'}")

        if trend_up and rsi_low:
            return {
                'signal': 'BUY',
                'confidence': 0.75,
                'reason': f"Trend UP + RSI {float(last['rsi']):.1f}"
            }
        elif not trend_up and rsi_high:
            return {
                'signal': 'SELL',
                'confidence': 0.70,
                'reason': f"Trend DOWN + RSI {float(last['rsi']):.1f}"
            }

        return None

    def _compute_sl_tp(self, symbol: str, side: str, price: float) -> tuple[float, float]:
        info = mt5.symbol_info(symbol)
        point = info.point if info and info.point > 0 else 0.00001
        min_stop_points = int(info.trade_stops_level or 0)
        sl_points = max(50, min_stop_points)
        tp_points = max(75, min_stop_points + 25)

        if side == 'BUY':
            sl = price - sl_points * point
            tp = price + tp_points * point
        else:
            sl = price + sl_points * point
            tp = price - tp_points * point
        return sl, tp

    def execute_trade(self, symbol, decision):
        """EXECUÇÃO CORRIGIDA - com tratamento robusto de erros"""
        if not self.connected:
            logger.error("Não conectado ao MT5")
            return False

        try:
            if not self._ensure_symbol(symbol):
                return False

            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Não foi possível obter tick para {symbol}")
                return False

            if decision['signal'] == 'BUY':
                price = tick.ask
                order_type = mt5.ORDER_TYPE_BUY
            else:
                price = tick.bid
                order_type = mt5.ORDER_TYPE_SELL

            lot_size = 0.01  # muito pequeno para teste
            sl, tp = self._compute_sl_tp(symbol, decision['signal'], float(price))

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": float(price),
                "sl": float(sl),
                "tp": float(tp),
                "deviation": 20,
                "magic": 20240907,
                "comment": f"DEEPSEEK-{decision['signal']}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            logger.debug(f"Enviando ordem: {symbol} {decision['signal']} {lot_size}L | price={price} sl={sl} tp={tp}")

            result = mt5.order_send(request)
            if result is None:
                logger.error(f"order_send() retornou None | last_error={mt5.last_error()}")
                return False

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(
                    f"ORDEM EXECUTADA! {decision['signal']} {symbol} {lot_size}L | price={price:.5f} sl={sl:.5f} tp={tp:.5f} | order={getattr(result,'order',0)} deal={getattr(result,'deal',0)}"
                )
                return True

            # Fallback para modo de preenchimento
            if result.retcode in (mt5.TRADE_RETCODE_INVALID_FILL, mt5.TRADE_RETCODE_REQUOTE):
                request["type_filling"] = mt5.ORDER_FILLING_RETURN
                result2 = mt5.order_send(request)
                if result2 is None:
                    logger.error(f"Fallback RETURN retornou None | last_error={mt5.last_error()}")
                    return False
                if result2.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"ORDEM EXECUTADA (fallback RETURN)! {decision['signal']} {symbol} {lot_size}L")
                    return True
                logger.warning(f"Ordem recusada (fallback). retcode={result2.retcode} comment={getattr(result2,'comment','')}")
                return False

            logger.warning(f"Ordem recusada: {result.retcode} - {getattr(result,'comment','')}")
            return False

        except Exception as e:
            logger.error(f"Erro na execução: {e}")
            return False

    def run_trading_loop(self, symbols, interval=30, timeframe=mt5.TIMEFRAME_M1):
        """Loop principal corrigido"""
        if not self.connect_mt5():
            logger.error("Não foi possível conectar ao MT5")
            return

        logger.info("INICIANDO SISTEMA CORRIGIDO!")
        logger.info(f"Símbolos: {symbols}")

        while True:
            try:
                for symbol in symbols:
                    decision = self.analyze_market(symbol)
                    if decision:
                        logger.info(f"SINAL ENCONTRADO: {decision['signal']} {symbol} | {decision['reason']}")
                        self.execute_trade(symbol, decision)
                    time.sleep(1)

                logger.info(f"Ciclo completo. Próximo em {interval}s...")
                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("Interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(10)


# CONFIGURAÇÃO - EDITAR AQUI!
YOUR_ACCOUNT = 12345678       # ← SUA CONTA
YOUR_PASSWORD = "sua_senha"   # ← SUA SENHA
YOUR_SERVER = "seu_servidor"  # ← SEU SERVIDOR

# SÍMBOLOS para teste
SYMBOLS = ["EURUSD", "XAUUSD", "GBPUSD"]

if __name__ == "__main__":
    print("=" * 60)
    print("           DEEPSEEK TRADER - VERSÃO CORRIGIDA")
    print("           CORREÇÃO: order_send() retornando None")
    print("=" * 60)

    trader = FixedTrader(YOUR_ACCOUNT, YOUR_PASSWORD, YOUR_SERVER)
    trader.run_trading_loop(SYMBOLS, interval=30)


