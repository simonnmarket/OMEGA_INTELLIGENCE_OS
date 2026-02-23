import json
import time
import logging
from typing import Dict, List

# Bridge para MT5
from Backend.deepseek_trading_bridge import DeepSeekTradingBridge


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CursorDeepSeekController")


def load_config(path: str = "Backend/config.json") -> Dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Falha ao ler config '{path}': {e}")
        # Defaults mínimos para não travar
        return {
            "mt5_account": 0,
            "mt5_password": "",
            "mt5_server": "",
            "symbols": ["EURUSD"],
            "analysis_interval": 60,
            "risk_per_trade": 1.0,
            "max_positions": 5,
            "default_lot_size": 0.1,
            "entry_confidence": 0.7,
        }


def deepseek_decision_maker(market_data: Dict) -> Dict:
    """
    Stub de decisão DeepSeek.
    - Usa indicadores calculados pela Bridge (market_data)
    - Retorna um dicionário com: signal, confidence, sl, tp, volume, reason
    Troque por sua lógica/LLM/endpoint quando desejar.
    """
    try:
        symbol = market_data.get("symbol")
        price = float(market_data.get("price", 0.0))
        inds = market_data.get("indicators", {})
        rsi = float(inds.get("rsi", 50.0))
        macd = float(inds.get("macd", 0.0))
        macd_signal = float(inds.get("macd_signal", 0.0))
        trend = market_data.get("trend", "NEUTRAL")
        momentum = market_data.get("momentum", "NEUTRAL")
        volume_spike = bool(market_data.get("volume_spike", False))

        # Regras simples (substitua pela IA do DeepSeek)
        bullish = (trend == "BULL") and (momentum == "BULL") and (macd > macd_signal)
        bearish = (trend == "BEAR") and (momentum == "BEAR") and (macd < macd_signal)

        confidence = 0.0
        signal = "HOLD"
        reason = "neutral"

        if bullish and rsi >= 48 and rsi <= 75:
            confidence = 0.75 if not volume_spike else 0.82
            signal = "BUY"
            reason = "bullish + momentum + macd_alignment"
        elif bearish and rsi <= 52 and rsi >= 25:
            confidence = 0.72 if not volume_spike else 0.80
            signal = "SELL"
            reason = "bearish + momentum + macd_alignment"
        else:
            # sinais fracos: ainda podemos emitir BUY/SELL com baixa confiança
            if (macd > macd_signal) and (rsi > 55):
                confidence = 0.6
                signal = "BUY"
                reason = "weak_bullish_bias"
            elif (macd < macd_signal) and (rsi < 45):
                confidence = 0.6
                signal = "SELL"
                reason = "weak_bearish_bias"

        # SL/TP simples (aprox): 0.15% e 0.25% do preço
        if price > 0.0 and signal in ("BUY", "SELL"):
            sl_dist = price * 0.0015
            tp_dist = price * 0.0025
            if signal == "BUY":
                sl = price - sl_dist
                tp = price + tp_dist
            else:
                sl = price + sl_dist
                tp = price - tp_dist
        else:
            sl = 0.0
            tp = 0.0

        return {
            "signal": signal,
            "confidence": round(confidence, 3),
            "sl": round(sl, 5) if sl else None,
            "tp": round(tp, 5) if tp else None,
            "volume": None,  # Bridge usará default do config se None
            "reason": reason,
        }
    except Exception as e:
        logger.error(f"DeepSeek decision error: {e}")
        return {"signal": "HOLD", "confidence": 0.0, "reason": "decision_error"}


def main():
    cfg = load_config()
    account = int(cfg.get("mt5_account", 0))
    password = str(cfg.get("mt5_password", ""))
    server = str(cfg.get("mt5_server", ""))
    symbols: List[str] = list(cfg.get("symbols", ["EURUSD"]))
    interval = int(cfg.get("analysis_interval", 60))

    bridge = DeepSeekTradingBridge(account, password, server)
    bridge.set_decision_callback(deepseek_decision_maker)

    # Inicia loop de trading (bloqueante)
    bridge.run_trading_loop(symbols, interval)


if __name__ == "__main__":
    main()


