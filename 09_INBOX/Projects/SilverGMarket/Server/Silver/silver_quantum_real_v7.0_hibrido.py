# ==============================================
# SILVER QUANTUM REAL V7.0 – HÍBRIDO (Trend + Mean Reversion)
# Apenas XAGUSD, XAGAUD, XAGEUR, XAGGBP
# Apenas COMPRAS – Integração V6.0 + V8.0
# ==============================================

import MetaTrader5 as mt5
import pandas as pd
import talib
from datetime import datetime
import time
import numpy as np

# ----------------------------------------------
# CONFIGURAÇÕES GERAIS
# ----------------------------------------------
SYMBOLS = ["XAGUSD", "XAGAUD", "XAGEUR", "XAGGBP"]

# Risco (Mais conservador - do V8.0)
RISK_PER_TRADE = 0.01       # 1% do equity por trade
MAX_TOTAL_RISK = 0.15       # 15% do equity (reduzido de 20% para mais conservadorismo)

# SL e gerenciamento (Mantido do V6.0 - SL em pontos)
SL_POINTS = 300             # Stop Loss em PONTOS (mais seguro e fácil de controlar)
USE_ATR_SL = False          # Se True, usa ATR * SL_ATR_MULT. Se False, usa SL_POINTS
SL_ATR_MULT = 2.3           # (Apenas se USE_ATR_SL = True)
BE_ATR_MULT = 1.0           # BE quando lucro >= 1 ATR
TRAIL_START_ATR_MULT = 1.5  # começa trailing após 1.5 ATR de lucro
TRAIL_STEP_ATR_MULT = 1.0   # trailing a 1 ATR de distância

# Estratégia (Híbrida - pode alternar)
STRATEGY_MODE = "TREND"     # "TREND" ou "MEAN_REVERSION" ou "HYBRID"
# TREND: Usa MA20/MA50 crossover (V6.0)
# MEAN_REVERSION: Usa Bollinger Bands (V8.0)
# HYBRID: Usa ambos (mais restritivo)

# Parâmetros Mean Reversion (do V8.0)
BB_PERIOD = 20
BB_DEVIATIONS = 2.0
MAX_M15_RANGE = 0.30        # % do ATR H4: Filtro de regime (evita BB Walk)

# Limites operacionais (Meio termo entre V6.0 e V8.0)
MAX_POS_PER_SYMBOL = 8      # Reduzido de 25 para 8 (mais conservador)
MAX_LOT_PER_SYMBOL = 5.0
MIN_SECONDS_BETWEEN_ENTRIES = 300

MAGIC_NUMBER = 20251201     # Novo Magic Number para V7.0

# ----------------------------------------------
# CLASSE PRINCIPAL
# ----------------------------------------------
class SilverQuantumV7:
    def __init__(self):
        self.ultima_entrada = {s: 0 for s in SYMBOLS}

    # ---------------------------
    # Conexão e utilidades
    # ---------------------------
    def conectar(self):
        if not mt5.initialize():
            print("MT5 falhou ao inicializar")
            return False

        for s in SYMBOLS:
            if not mt5.symbol_select(s, True):
                print(f"Falha ao selecionar símbolo: {s}")

        print("=" * 60)
        print("Silver Quantum REAL V7.0 HÍBRIDO – ATIVO")
        print(f"Estratégia: {STRATEGY_MODE}")
        print(f"SL: {SL_POINTS} pontos")
        print(f"Max Posições: {MAX_POS_PER_SYMBOL} por símbolo")
        print(f"Risco Total: {MAX_TOTAL_RISK * 100}%")
        print("=" * 60)
        return True

    def df(self, symbol, timeframe, bars=250):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        if rates is None or len(rates) == 0:
            return None
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    def get_equity(self):
        acc_info = mt5.account_info()
        if acc_info is None:
            return None
        return acc_info.equity

    def get_atr_h4(self, symbol, period=14):
        df_h4 = self.df(symbol, mt5.TIMEFRAME_H4, max(60, period + 10))
        if df_h4 is None or len(df_h4) < period + 1:
            return None
        atr = talib.ATR(df_h4["high"], df_h4["low"], df_h4["close"], timeperiod=period)
        if pd.isna(atr.iloc[-1]):
            return None
        return float(atr.iloc[-1])

    # ---------------------------
    # Filtro Macro H4 - SMA200 (do V8.0)
    # ---------------------------
    def macro_tendencia_alta(self, symbol):
        """
        Filtro macro: Preço acima da SMA200 H4 e SMA200 subindo.
        Do V8.0 - mais conservador e robusto.
        """
        df_h4 = self.df(symbol, mt5.TIMEFRAME_H4, 250)
        if df_h4 is None or len(df_h4) < 200:
            return False

        close = df_h4["close"]
        sma200 = talib.SMA(close, 200)

        if pd.isna(sma200.iloc[-1]) or pd.isna(sma200.iloc[-6]):
            return False

        # Preço atual acima da SMA200 E inclinação da SMA200 positiva
        if close.iloc[-1] > sma200.iloc[-1] and sma200.iloc[-1] > sma200.iloc[-6]:
            return True
        return False

    # ---------------------------
    # Filtro de Tendência Forte Multi-Timeframe (do V6.0)
    # ---------------------------
    def tendencia_forte(self, symbol):
        """
        Filtro de tendência: MA20 > MA50 em D1, H4, H1 + inclinação positiva.
        Do V6.0 - confirmação em múltiplos timeframes.
        """
        for tf in [mt5.TIMEFRAME_D1, mt5.TIMEFRAME_H4, mt5.TIMEFRAME_H1]:
            d = self.df(symbol, tf, 120)
            if d is None or len(d) < 60:
                return False

            close = d["close"]
            ma20 = talib.SMA(close, 20)
            ma50 = talib.SMA(close, 50)

            if pd.isna(ma20.iloc[-1]) or pd.isna(ma50.iloc[-1]):
                return False

            if ma20.iloc[-1] <= ma50.iloc[-1]:
                return False

            # Inclinação da SMA50 (últimas 10 barras)
            if len(ma50.dropna()) < 60:
                return False
            ma50_now = ma50.iloc[-1]
            ma50_past = ma50.iloc[-11]   # ~10 barras atrás
            if ma50_now <= ma50_past:
                return False

            # Preço deve estar acima das duas MAs
            last_close = close.iloc[-1]
            if last_close <= ma20.iloc[-1] or last_close <= ma50.iloc[-1]:
                return False

        return True

    # ---------------------------
    # Sinal Mean Reversion - Bollinger Bands (do V8.0)
    # ---------------------------
    def sinal_reversao_valido(self, symbol, h4_atr):
        """
        Sinal de Mean Reversion: Preço toca banda inferior BB + filtro de regime.
        Do V8.0 - evita BB Walk (alta volatilidade).
        """
        df_m15 = self.df(symbol, mt5.TIMEFRAME_M15, 60)
        if df_m15 is None or len(df_m15) < BB_PERIOD + 1:
            return False, None, None

        close = df_m15["close"]
        open_price = df_m15["open"].iloc[-1]

        # 1. Bandas de Bollinger
        upper, middle, lower = talib.BBANDS(
            close, timeperiod=BB_PERIOD, nbdevup=BB_DEVIATIONS, 
            nbdevdn=BB_DEVIATIONS, matype=0
        )
        lower_band = lower.iloc[-1]
        middle_band = middle.iloc[-1]
        last_close = close.iloc[-1]

        # Condição de Compra: Tocou/Cruzou a Banda Inferior
        is_oversold = last_close <= lower_band

        # 2. Filtro de Regime (Evita BB Walk - alta volatilidade)
        max_range_h4_based = h4_atr * MAX_M15_RANGE
        current_range_from_open = abs(last_close - open_price)

        if is_oversold and current_range_from_open < max_range_h4_based:
            # É sobre-venda E o movimento atual não é explosivo
            return True, lower_band, middle_band

        return False, None, None

    # ---------------------------
    # Sizing baseado em PONTOS (do V6.0)
    # ---------------------------
    def calcular_lote(self, symbol, sl_points):
        """
        Calcula o lote baseado em risco % do equity e SL em PONTOS.
        Do V6.0 - mais seguro e fácil de controlar.
        """
        equity = self.get_equity()
        if equity is None or equity <= 0:
            return 0.0

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 0.0

        tick_value = symbol_info.trade_tick_value
        tick_size = symbol_info.trade_tick_size
        lot_step = symbol_info.volume_step
        min_lot = symbol_info.volume_min
        max_lot = min(symbol_info.volume_max, MAX_LOT_PER_SYMBOL)

        if tick_value <= 0 or tick_size <= 0:
            return 0.0

        # Distância do SL em preço = SL_POINTS * tick_size
        sl_distance = sl_points * tick_size

        # Risco monetário por trade
        risk_money = equity * RISK_PER_TRADE

        # Valor monetário por ponto de preço para 1 lote
        ticks_per_price = sl_distance / tick_size
        loss_per_lot = ticks_per_price * tick_value

        if loss_per_lot <= 0:
            return 0.0

        lots = risk_money / loss_per_lot

        # Respeitar limites do símbolo
        lots = max(min_lot, min(lots, max_lot))

        # Ajustar para múltiplo de volume_step
        steps = round(lots / lot_step)
        lots = steps * lot_step

        return round(lots, 2)

    # ---------------------------
    # Risco total atual (do V6.0)
    # ---------------------------
    def risco_total_corrente(self):
        """
        Estima o risco total se todos os SLs forem atingidos.
        Do V6.0 - cálculo robusto de risco agregado.
        """
        total_risk = 0.0
        for symbol in SYMBOLS:
            positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
            if not positions:
                continue

            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                continue

            tick_value = symbol_info.trade_tick_value
            tick_size = symbol_info.trade_tick_size

            for p in positions:
                if p.sl <= 0:
                    return float("inf")
                price_diff = abs(p.price_open - p.sl)
                ticks = price_diff / tick_size
                loss_money = ticks * tick_value * p.volume
                total_risk += loss_money

        return total_risk

    # ---------------------------
    # Abrir posição (HÍBRIDO)
    # ---------------------------
    def abrir(self, symbol):
        # 1. Filtro Macro H4 - SMA200 (do V8.0 - obrigatório)
        if not self.macro_tendencia_alta(symbol):
            return

        # 2. ATR H4 (necessário para filtros)
        atr_h4 = self.get_atr_h4(symbol, 14)
        if atr_h4 is None:
            return

        # 3. Sinal de entrada baseado na estratégia escolhida
        sinal_valido = False
        tp_price = 0.0

        if STRATEGY_MODE == "TREND":
            # Estratégia Trend Following (V6.0)
            sinal_valido = self.tendencia_forte(symbol)
            # TP será gerenciado por trailing stop

        elif STRATEGY_MODE == "MEAN_REVERSION":
            # Estratégia Mean Reversion (V8.0)
            is_valid, lower_band, middle_band = self.sinal_reversao_valido(symbol, atr_h4)
            sinal_valido = is_valid
            tp_price = middle_band if is_valid else 0.0

        elif STRATEGY_MODE == "HYBRID":
            # Híbrido: Ambos devem confirmar (mais restritivo)
            trend_ok = self.tendencia_forte(symbol)
            mr_ok, lower_band, middle_band = self.sinal_reversao_valido(symbol, atr_h4)
            sinal_valido = trend_ok and mr_ok
            tp_price = middle_band if sinal_valido else 0.0

        if not sinal_valido:
            return

        # 4. Intervalo mínimo entre entradas
        if time.time() - self.ultima_entrada[symbol] < MIN_SECONDS_BETWEEN_ENTRIES:
            return

        # 5. Limites de posições
        pos = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
        qtd = len(pos) if pos else 0
        if qtd >= MAX_POS_PER_SYMBOL:
            return

        # 6. Calcula SL em PONTOS (do V6.0)
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return

        tick_size = symbol_info.trade_tick_size

        # Usa SL em PONTOS (mais seguro)
        if USE_ATR_SL:
            sl_distance_price = atr_h4 * SL_ATR_MULT
            sl_points_used = sl_distance_price / tick_size
        else:
            sl_points_used = SL_POINTS
            sl_distance_price = SL_POINTS * tick_size

        # 7. Calcula lote por risco
        lote = self.calcular_lote(symbol, sl_points_used)
        if lote <= 0:
            return

        # 8. Verifica limite de lote total por símbolo
        current_volume = sum(p.volume for p in (pos or []))
        if current_volume + lote > MAX_LOT_PER_SYMBOL:
            return

        # 9. Calcula preço do SL
        sl_price = tick.bid - sl_distance_price

        # 10. Checagem de risco agregado
        equity = self.get_equity()
        if equity is None or equity <= 0:
            return

        tick_value = symbol_info.trade_tick_value
        price_diff = abs(tick.ask - sl_price)
        ticks = price_diff / tick_size
        this_trade_risk = ticks * tick_value * lote

        total_risk_now = self.risco_total_corrente()
        if total_risk_now == float("inf"):
            return

        if (total_risk_now + this_trade_risk) > (equity * MAX_TOTAL_RISK):
            return

        # 11. Monta request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lote),
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": round(sl_price, 5),
            "tp": round(tp_price, 5) if tp_price > 0 else 0.0,
            "deviation": 30,
            "magic": MAGIC_NUMBER,
            "comment": f"SilverV7_{STRATEGY_MODE[:4]}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None:
            error_code = mt5.last_error()
            print(f"{symbol} | ERRO: order_send retornou None - Código: {error_code[0]}, Descrição: {error_code[1]}")
            return

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.ultima_entrada[symbol] = time.time()
            tp_info = f" | TP={tp_price:.3f}" if tp_price > 0 else " | TP=Trailing"
            print(f"{symbol} | BUY {lote} @ {tick.ask:.3f} | SL={sl_price:.3f} ({sl_points_used:.0f} pts){tp_info} | {STRATEGY_MODE}")
        else:
            print(f"{symbol} | FALHA order_send: retcode={result.retcode}, comment={result.comment}")

    # ---------------------------
    # Gerenciamento: BE + Trailing + Reversão (do V6.0)
    # ---------------------------
    def gerenciar(self):
        """
        Gerenciamento avançado: Break-Even + Trailing Stop + Fechamento por reversão.
        Do V6.0 - proteção progressiva de lucros.
        """
        for symbol in SYMBOLS:
            positions = mt5.positions_get(symbol=symbol, magic=MAGIC_NUMBER)
            if not positions:
                continue

            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                continue

            atr = self.get_atr_h4(symbol, 14)
            if atr is None:
                continue

            be_distance = atr * BE_ATR_MULT
            trail_start = atr * TRAIL_START_ATR_MULT
            trail_step = atr * TRAIL_STEP_ATR_MULT

            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                continue

            tick_size = symbol_info.trade_tick_size

            for p in positions:
                if p.type != mt5.POSITION_TYPE_BUY:
                    continue

                # Lucro em preço
                price_profit = tick.bid - p.price_open

                new_sl = p.sl

                # Break-even: move SL para pouco acima do preço de entrada
                if price_profit >= be_distance:
                    be_price = p.price_open + (tick_size * 2.0)
                    if p.sl < be_price:
                        new_sl = be_price

                # Trailing: se lucro já passou do trail_start
                if price_profit >= trail_start:
                    trail_price = tick.bid - trail_step
                    if trail_price > new_sl:
                        new_sl = trail_price

                # Aplica modificação de SL, se necessário
                if new_sl > 0 and abs(new_sl - p.sl) >= tick_size:
                    modify_request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": symbol,
                        "position": p.ticket,
                        "sl": new_sl,
                        "tp": p.tp,
                        "magic": MAGIC_NUMBER,
                    }
                    res_mod = mt5.order_send(modify_request)
                    if res_mod is not None and res_mod.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"{symbol} | SL atualizado para {new_sl:.3f} (ticket {p.ticket})")
                    # else: Falha silenciosa (pode ser requote)

            # Reversão de tendência macro → fecha tudo no símbolo
            if not self.macro_tendencia_alta(symbol):
                for p in positions:
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "position": p.ticket,
                        "volume": p.volume,
                        "type": mt5.ORDER_TYPE_SELL if p.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "price": tick.bid if p.type == mt5.POSITION_TYPE_BUY else tick.ask,
                        "deviation": 30,
                        "magic": MAGIC_NUMBER,
                        "comment": "Reversao-Macro",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    res_close = mt5.order_send(close_request)
                    if res_close is not None and res_close.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"{symbol} | FECHOU posição {p.ticket} por reversão macro")
                    # else: Falha silenciosa

    # ---------------------------
    # Loop principal
    # ---------------------------
    def run(self):
        if not self.conectar():
            return

        while True:
            try:
                for s in SYMBOLS:
                    self.abrir(s)
                self.gerenciar()
                time.sleep(60)  # Checa a cada minuto
            except Exception as e:
                print(f"Erro no loop principal: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(30)

# ----------------------------------------------
# EXECUÇÃO
# ----------------------------------------------
if __name__ == "__main__":
    bot = SilverQuantumV7()
    bot.run()

