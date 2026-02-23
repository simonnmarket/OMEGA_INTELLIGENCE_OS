import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import logging
import json
import os
from datetime import datetime, timedelta

# Configuração de logging AGRESSIVA - para ver TUDO
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_debug.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DeepSeek-Aggressive")


class AggressiveTrader:
    def __init__(self, account: int, password: str, server: str):
        self.account = account
        self.password = password
        self.server = server
        self.connected = False

    def connect_mt5(self) -> bool:
        """Conectar ao MT5 com VERBOSE"""
        try:
            logger.info("Inicializando MT5...")
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"Falha ao inicializar: {error}")
                return False

            logger.info("Tentando login...")
            if not mt5.login(self.account, self.password, self.server):
                error = mt5.last_error()
                logger.error(f"Login falhou: {error}")
                mt5.shutdown()
                return False

            acc_info = mt5.account_info()
            if acc_info is None:
                logger.error(f"account_info() retornou None. last_error={mt5.last_error()}")
                return False

            logger.info(f"CONECTADO! Conta: {acc_info.login}")
            logger.info(f"Saldo: ${acc_info.balance}")
            logger.info(f"Corretora: {acc_info.company}")

            self.connected = True
            return True

        except Exception as e:
            logger.error(f"Erro fatal: {e}")
            return False

    def _ensure_symbol(self, symbol: str) -> bool:
        info = mt5.symbol_info(symbol)
        if info is None:
            logger.warning(f"Símbolo inválido ou indisponível: {symbol}")
            return False
        if not info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.warning(f"Não foi possível selecionar símbolo: {symbol}")
                return False
        return True

    def get_data(self, symbol: str, timeframe=mt5.TIMEFRAME_M1, bars: int = 300) -> pd.DataFrame | None:
        """Buscar dados com logging detalhado"""
        try:
            if not self._ensure_symbol(symbol):
                return None

            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            if rates is None:
                logger.warning(f"Sem dados para {symbol}. last_error={mt5.last_error()}")
                return None

            df = pd.DataFrame(rates)
            if df.empty:
                logger.warning(f"DataFrame vazio para {symbol}")
                return None

            df['time'] = pd.to_datetime(df['time'], unit='s')

            # Indicadores simples
            df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
            df['rsi'] = self.calculate_rsi(df['close'], 14)

            logger.debug(f"Dados {symbol}: {len(df)} candles")
            return df

        except Exception as e:
            logger.error(f"Erro em get_data({symbol}): {e}")
            return None

    def calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calcular RSI simplificado (com salvaguardas contra divisão por zero)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0.0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
        loss = loss.replace(0, 1e-10)
        rs = gain / loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi.bfill().fillna(50.0)

    def analyze_market_AGGRESSIVE(self, symbol: str) -> dict | None:
        """ANÁLISE AGRESSIVA - para ABRIR ORDENS"""
        df = self.get_data(symbol)
        if df is None or len(df) < 20:
            return None

        last = df.iloc[-1]

        trend_up = last['ema_fast'] > last['ema_slow']
        trend_down = last['ema_fast'] < last['ema_slow']
        rsi_low = last['rsi'] < 40
        rsi_high = last['rsi'] > 60

        volume_avg = df['tick_volume'].rolling(20).mean().iloc[-1]
        volume_high = last['tick_volume'] > volume_avg * 1.2 if pd.notna(volume_avg) else False

        logger.debug(
            f"{symbol} - RSI: {float(last['rsi']):.1f}, Trend: {'UP' if trend_up else 'DOWN'}, Volume: {'HIGH' if volume_high else 'LOW'}"
        )

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.warning(f"symbol_info_tick retornou None para {symbol}")
            return None

        # Entradas agressivas por pullback
        if trend_up and rsi_low:
            return {
                'signal': 'BUY',
                'confidence': 0.75,
                'price': tick.ask,
                'reason': f"Trend UP + RSI {float(last['rsi']):.1f}"
            }
        elif trend_down and rsi_high:
            return {
                'signal': 'SELL',
                'confidence': 0.70,
                'price': tick.bid,
                'reason': f"Trend DOWN + RSI {float(last['rsi']):.1f}"
            }

        # Entradas agressivas por rompimento (momentum)
        if trend_up and float(last['rsi']) > 65.0:
            return {
                'signal': 'BUY',
                'confidence': 0.60,
                'price': tick.ask,
                'reason': f"Momentum breakout (RSI {float(last['rsi']):.1f} > 65)"
            }
        if trend_down and float(last['rsi']) < 35.0:
            return {
                'signal': 'SELL',
                'confidence': 0.60,
                'price': tick.bid,
                'reason': f"Momentum breakdown (RSI {float(last['rsi']):.1f} < 35)"
            }

        # Microestrutura: OFI + VWAP desvio (priorizar causas: fluxo/volume)
        micro = self.analyze_microstructure(symbol)
        if micro is not None:
            return micro

        return None

    def analyze_microstructure(self, symbol: str, seconds_window: int = 90) -> dict | None:
        """Análise de microestrutura via OFI (Order Flow Imbalance) e VWAP intraday"""
        try:
            since = datetime.now() - timedelta(seconds=seconds_window)
            ticks = mt5.copy_ticks_from(symbol, since, 5000, mt5.COPY_TICKS_INFO | mt5.COPY_TICKS_TRADE)
            if ticks is None or len(ticks) < 20:
                return None

            import numpy as np
            tdf = pd.DataFrame(ticks)
            # midprice aproximação
            if 'bid' in tdf.columns and 'ask' in tdf.columns:
                tdf['mid'] = (tdf['bid'].fillna(method='ffill') + tdf['ask'].fillna(method='ffill')) / 2.0
            else:
                tdf['mid'] = tdf['last'].fillna(method='ffill')

            tdf['dmid'] = tdf['mid'].diff().fillna(0.0)
            tdf['sign'] = np.sign(tdf['dmid'])
            tdf['vol'] = tdf.get('volume', tdf.get('last', pd.Series(index=tdf.index, data=0.0))).fillna(0.0)
            vol_sum = float(tdf['vol'].sum()) or 1.0
            ofi = float((tdf['sign'] * tdf['vol']).sum()) / vol_sum

            # VWAP intraday pela janela
            price_for_vwap = tdf['mid'].fillna(method='ffill')
            cum_v = tdf['vol'].cumsum().replace(0, np.nan)
            vwap = float((price_for_vwap * tdf['vol']).cumsum().iloc[-1] / cum_v.iloc[-1]) if cum_v.iloc[-1] == cum_v.iloc[-1] else float(price_for_vwap.iloc[-1])
            last_mid = float(price_for_vwap.iloc[-1])
            vwap_dev_bp = 10000.0 * (last_mid - vwap) / vwap

            info = mt5.symbol_info(symbol)
            tick = mt5.symbol_info_tick(symbol)
            if info is None or tick is None:
                return None

            mid = (tick.ask + tick.bid) / 2.0
            spread_bp = 10000.0 * (tick.ask - tick.bid) / mid if mid else 0.0

            logger.debug(f"{symbol} Microstructure - OFI={ofi:.2f}, VWAP_dev(bp)={vwap_dev_bp:.1f}, spread_bp={spread_bp:.1f}")

            # Regras objetivas
            if ofi > 0.05 and vwap_dev_bp > -15 and spread_bp < 100:
                return {
                    'signal': 'BUY',
                    'confidence': min(0.85, 0.55 + ofi),
                    'price': tick.ask,
                    'reason': f"OFI {ofi:.2f} BUY + VWAP dev {vwap_dev_bp:.1f}bp"
                }
            if ofi < -0.05 and vwap_dev_bp < 15 and spread_bp < 100:
                return {
                    'signal': 'SELL',
                    'confidence': min(0.85, 0.55 + abs(ofi)),
                    'price': tick.bid,
                    'reason': f"OFI {ofi:.2f} SELL + VWAP dev {vwap_dev_bp:.1f}bp"
                }
            return None
        except Exception as e:
            logger.error(f"Erro em analyze_microstructure({symbol}): {e}")
            return None

    def _compute_sl_tp(self, symbol: str, side: str, price: float) -> tuple[float, float]:
        info = mt5.symbol_info(symbol)
        point = info.point
        min_stop_points = max(int(info.trade_stops_level or 0), 50)
        base_sl_points = max(100, min_stop_points)
        base_tp_points = max(150, min_stop_points + 50)

        if side == 'BUY':
            sl = price - base_sl_points * point
            tp = price + base_tp_points * point
        else:
            sl = price + base_sl_points * point
            tp = price - base_tp_points * point
        return sl, tp

    def execute_trade_AGGRESSIVE(self, symbol: str, decision: dict) -> bool:
        """EXECUÇÃO AGRESSIVA - lote fixo para TESTE (com salvaguardas)"""
        if not self.connected:
            logger.error("MT5 não conectado")
            return False

        try:
            if not self._ensure_symbol(symbol):
                return False

            info = mt5.symbol_info(symbol)
            if info is None:
                logger.error(f"symbol_info({symbol}) retornou None")
                return False

            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"symbol_info_tick({symbol}) retornou None")
                return False

            side = decision['signal']
            price = float(decision.get('price') or (tick.ask if side == 'BUY' else tick.bid))

            lot_size = 0.10
            sl, tp = self._compute_sl_tp(symbol, side, price)

            order_type = mt5.ORDER_TYPE_BUY if side == 'BUY' else mt5.ORDER_TYPE_SELL

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 150,
                "magic": 999888,
                "comment": "DEEPSEEK-AGGRESSIVE",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            result = mt5.order_send(request)
            if result is None:
                logger.error(f"order_send retornou None. last_error={mt5.last_error()} | request={request}")
                return False

            logger.debug(f"order_send retcode={result.retcode}, comment={getattr(result, 'comment', '')}")

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"ORDEM ABERTA! {side} {symbol} {lot_size}L | preço={price} sl={sl} tp={tp}")
                return True

            # Fallback: tentar RETURN se FOK falhar por modo de preenchimento
            if result.retcode in (mt5.TRADE_RETCODE_INVALID_FILL, mt5.TRADE_RETCODE_MARKET_CLOSED, mt5.TRADE_RETCODE_REQUOTE):
                request["type_filling"] = mt5.ORDER_FILLING_RETURN
                result2 = mt5.order_send(request)
                if result2 is None:
                    logger.error(f"Fallback RETURN também retornou None. last_error={mt5.last_error()}")
                    return False
                if result2.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"ORDEM ABERTA (fallback RETURN)! {side} {symbol} {lot_size}L")
                    return True
                logger.warning(f"Ordem não executada (fallback). retcode={result2.retcode}, comment={getattr(result2, 'comment', '')}")
                return False

            # Se INVALID_STOPS → enviar sem SL/TP e ajustar depois
            if result.retcode == mt5.TRADE_RETCODE_INVALID_STOPS:
                request_no_stops = dict(request)
                request_no_stops.pop("sl", None)
                request_no_stops.pop("tp", None)
                result3 = mt5.order_send(request_no_stops)
                if result3 is not None and result3.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"ORDEM ABERTA (sem SL/TP por INVALID_STOPS). Ajustando stops...")
                    # Tentar ajustar SL/TP via modificação de posição
                    time.sleep(0.3)
                    if mt5.positions_total() > 0:
                        for i in range(mt5.positions_total()):
                            if mt5.position_select(symbol):
                                entry = mt5.position_get_double(mt5.POSITION_PRICE_OPEN)
                                side_now = mt5.position_get_integer(mt5.POSITION_TYPE)
                                if side_now == mt5.POSITION_TYPE_BUY:
                                    sl_adj, tp_adj = self._compute_sl_tp(symbol, 'BUY', entry)
                                else:
                                    sl_adj, tp_adj = self._compute_sl_tp(symbol, 'SELL', entry)
                                mt5.order_modify(result3.order, entry, sl_adj, tp_adj, 0)
                    return True

            logger.warning(f"Ordem não executada. retcode={result.retcode}, comment={getattr(result, 'comment', '')}")
            return False

        except Exception as e:
            logger.error(f"Erro na ordem: {e}")
            return False

    def run_aggressive_scan(self, symbols: list[str], interval: int = 30) -> None:
        """SCAN AGRESSIVO - focado em ABRIR ORDENS"""
        if not self.connect_mt5():
            return

        logger.info("INICIANDO SCAN AGRESSIVO!")
        logger.info(f"Símbolos: {symbols}")
        logger.info(f"Intervalo: {interval}s")

        max_trades = 3  # Máximo de trades por ciclo

        while True:
            try:
                trade_count = 0
                for symbol in symbols:
                    if trade_count >= max_trades:
                        break

                    decision = self.analyze_market_AGGRESSIVE(symbol)
                    if decision:
                        logger.info(f"SINAL: {decision['signal']} {symbol} ({decision['reason']})")
                        if self.execute_trade_AGGRESSIVE(symbol, decision):
                            trade_count += 1
                            time.sleep(2)

                    time.sleep(0.5)

                logger.info(f"Scan completo. Trades: {trade_count}. Próximo em {interval}s...")
                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("Interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop: {e}")
                time.sleep(10)


def _load_config_defaults():
    config_path = os.path.join("Backend", "config.json")
    defaults = {
        "mt5_account": 12345678,
        "mt5_password": "sua_senha",
        "mt5_server": "seu_servidor",
        "symbols": ["EURUSD", "XAUUSD", "GBPUSD", "USDJPY"],
        "analysis_interval": 30
    }
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in defaults:
                if k in data and data[k]:
                    defaults[k] = data[k]
    except Exception as e:
        logger.warning(f"Falha ao ler {config_path}: {e}. Usando defaults embutidos.")
    return defaults

if __name__ == "__main__":
    print("=" * 60)
    print("           DEEPSEEK TRADER AGRESSIVO - V1.0")
    print("           FOCO: ABRIR ORDENS AGORA!")
    print("=" * 60)
    cfg = _load_config_defaults()
    trader = AggressiveTrader(cfg["mt5_account"], cfg["mt5_password"], cfg["mt5_server"])
    trader.run_aggressive_scan(cfg["symbols"], interval=int(cfg.get("analysis_interval", 30)))


