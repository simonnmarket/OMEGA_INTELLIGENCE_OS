# ==============================================
# SILVER QUANTUM REAL V6.0 – SÓ O QUE FUNCIONA (2025)
# Apenas XAGUSD, XAGAUD, XAGEUR, XAGGBP
# Apenas COMPRAS – Trend Following Robusto com ATR-Risk
# ==============================================

import MetaTrader5 as mt5
import pandas as pd
import talib
from datetime import datetime
import time

# ----------------------------------------------
# CONFIGURAÇÕES GERAIS
# ----------------------------------------------
SYMBOLS = ["XAGUSD", "XAGAUD", "XAGEUR", "XAGGBP"]

# Risco
RISK_PER_TRADE = 0.01       # 1% do equity por trade
MAX_TOTAL_RISK = 0.20       # 20% do equity arriscado somando todas as posições

# SL e gerenciamento (AGORA EM PONTOS - MAIS SEGURO E FÁCIL DE CONTROLAR)
SL_POINTS = 300             # Stop Loss em PONTOS (não pips) - mais seguro e preciso
USE_ATR_SL = False          # Se True, usa ATR * SL_ATR_MULT. Se False, usa SL_POINTS
SL_ATR_MULT = 2.3           # (Apenas se USE_ATR_SL = True)
BE_ATR_MULT = 1.0           # BE quando lucro >= 1 ATR
TRAIL_START_ATR_MULT = 1.5  # começa trailing após 1.5 ATR de lucro
TRAIL_STEP_ATR_MULT = 1.0   # trailing a 1 ATR de distância

# Limites operacionais
MAX_POS_PER_SYMBOL = 25
MAX_LOT_PER_SYMBOL = 5.0
MIN_SECONDS_BETWEEN_ENTRIES = 300

MAGIC_NUMBER = 20251129

# ----------------------------------------------
# CLASSE PRINCIPAL
# ----------------------------------------------
class SilverQuantumReal:
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

        print("Silver Quantum REAL V6.0 – ATIVO")
        return True

    def df(self, symbol, timeframe, bars=200):
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

    # ---------------------------
    # Filtro de tendência forte
    # ---------------------------
    def tendencia_forte(self, symbol):
        # Exige SMA20 > SMA50 em D1, H4, H1 + inclinação positiva da SMA50
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
    # Cálculo de ATR (H4)
    # ---------------------------
    def get_atr_h4(self, symbol, period=14):
        df_h4 = self.df(symbol, mt5.TIMEFRAME_H4, max(60, period + 10))
        if df_h4 is None or len(df_h4) < period + 1:
            return None

        atr = talib.ATR(df_h4["high"], df_h4["low"], df_h4["close"], timeperiod=period)
        if pd.isna(atr.iloc[-1]):
            return None
        return float(atr.iloc[-1])

    # ---------------------------
    # Sizing baseado em PONTOS (mais seguro e fácil de controlar)
    # ---------------------------
    def calcular_lote(self, symbol, sl_points):
        """
        Calcula o lote baseado em risco % do equity e SL em PONTOS.
        Mais seguro e fácil de controlar do que usar ATR.
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
    # Risco total atual
    # ---------------------------
    def risco_total_corrente(self):
        """
        Estima o risco total se todos os SLs forem atingidos:
        soma(|preço_entrada - SL| * volume * tick_value / tick_size).
        """
        total_risk = 0.0
        for symbol in SYMBOLS:
            positions = mt5.positions_get(symbol=symbol)
            if not positions:
                continue

            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                continue

            tick_value = symbol_info.trade_tick_value
            tick_size = symbol_info.trade_tick_size

            for p in positions:
                if p.sl <= 0:
                    # Se não houver SL, considera o risco infinito -> bloqueia novas entradas
                    return float("inf")
                price_diff = abs(p.price_open - p.sl)
                ticks = price_diff / tick_size
                loss_money = ticks * tick_value * p.volume
                total_risk += loss_money

        return total_risk

    # ---------------------------
    # Abrir posição
    # ---------------------------
    def abrir(self, symbol):
        # Filtro de tendência
        if not self.tendencia_forte(symbol):
            return

        # Intervalo mínimo entre entradas
        if time.time() - self.ultima_entrada[symbol] < MIN_SECONDS_BETWEEN_ENTRIES:
            return

        # Limites de posições
        pos = mt5.positions_get(symbol=symbol)
        qtd = len(pos) if pos else 0
        if qtd >= MAX_POS_PER_SYMBOL:
            return

        # Calcula SL em PONTOS (mais seguro e fácil de controlar)
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return

        tick_size = symbol_info.trade_tick_size

        # Usa SL em PONTOS ao invés de ATR (mais seguro)
        if USE_ATR_SL:
            # Modo ATR (antigo)
            atr = self.get_atr_h4(symbol, 14)
            if atr is None:
                return
            sl_distance_price = atr * SL_ATR_MULT
            sl_points_used = sl_distance_price / tick_size
        else:
            # Modo PONTOS (novo - mais seguro e fácil de controlar)
            sl_points_used = SL_POINTS
            sl_distance_price = SL_POINTS * tick_size

        # Calcula lote por risco usando SL em pontos
        lote = self.calcular_lote(symbol, sl_points_used)
        if lote <= 0:
            return

        # Verifica limite de lote total por símbolo
        current_volume = sum(p.volume for p in (pos or []))
        if current_volume + lote > MAX_LOT_PER_SYMBOL:
            return

        # Calcula preço do SL
        sl_price = tick.bid - sl_distance_price

        # Checagem de risco agregado
        equity = self.get_equity()
        if equity is None or equity <= 0:
            return

        # Risco extra deste trade (aprox.)
        symbol_info = mt5.symbol_info(symbol)
        tick_value = symbol_info.trade_tick_value
        tick_size = symbol_info.trade_tick_size
        price_diff = abs(tick.ask - sl_price)
        ticks = price_diff / tick_size
        this_trade_risk = ticks * tick_value * lote

        total_risk_now = self.risco_total_corrente()
        if total_risk_now == float("inf"):
            return

        if (total_risk_now + this_trade_risk) > (equity * MAX_TOTAL_RISK):
            # Não abre se risco total passaria do limite
            return

        # Monta request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lote),
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": sl_price,
            "tp": 0.0,
            "deviation": 30,
            "magic": MAGIC_NUMBER,
            "comment": "SilverQuantumV6",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None:
            print(f"{symbol} | ERRO: order_send retornou None")
            return

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            self.ultima_entrada[symbol] = time.time()
            print(f"{symbol} | BUY {lote} @ {tick.ask:.3f} | SL={sl_price:.3f} ({sl_points_used:.0f} pontos)")
        else:
            print(f"{symbol} | FALHA order_send: retcode={result.retcode}, comment={result.comment}")

    # ---------------------------
    # Gerenciamento: BE + Trailing + Reversão
    # ---------------------------
    def gerenciar(self):
        for symbol in SYMBOLS:
            positions = mt5.positions_get(symbol=symbol)
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
            tick_value = symbol_info.trade_tick_value
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
                    # trailing "atrás" do preço atual
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
                        "comment": "SL-Update",
                    }
                    res_mod = mt5.order_send(modify_request)
                    if res_mod is not None and res_mod.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"{symbol} | SL atualizado para {new_sl:.3f} (ticket {p.ticket})")
                    else:
                        print(f"{symbol} | Falha ao atualizar SL (ticket {p.ticket})")

            # Reversão de tendência → fecha tudo no símbolo
            if not self.tendencia_forte(symbol):
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
                        "comment": "Reversao-FechaTudo",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    res_close = mt5.order_send(close_request)
                    if res_close is not None and res_close.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"{symbol} | FECHOU posição {p.ticket} por reversão")
                    else:
                        print(f"{symbol} | Falha ao fechar posição {p.ticket} por reversão")

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
                time.sleep(60)
            except Exception as e:
                print(f"Erro no loop principal: {e}")
                time.sleep(30)

# ----------------------------------------------
# EXECUÇÃO
# ----------------------------------------------
if __name__ == "__main__":
    bot = SilverQuantumReal()
    bot.run()

