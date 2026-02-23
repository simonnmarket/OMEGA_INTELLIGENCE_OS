# -*- coding: utf-8 -*-
"""
CRYPTO SERVIDOR FINAL - VERSÃO SIMPLIFICADA QUE FUNCIONA
Data: 02-11-2025 17:29 CET

FOCO: FUNCIONAR 100% AGORA
- Análise técnica RSI + ATR
- Sinais BUY/SELL com confidence > 0.50
- SL/TP dinâmicos
- CAPAZ DE PEGAR MOVIMENTOS DE 34K+ PONTOS!
"""

import os
import json
import time
import logging
import ccxt
import numpy as np
from pathlib import Path
from datetime import datetime

# Logging
log_file = Path(__file__).parent / 'CRYPTO_SIMPLES.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pasta MT5
MT5_PATH = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
REQUEST_FILE = MT5_PATH / 'AIRequest.BTCUSD.json'
RESPONSE_FILE = MT5_PATH / 'AIResponse.BTCUSD.json'

# Conectar Binance
try:
    exchange = ccxt.binance()
    logger.info("✅ Binance conectado")
except:
    exchange = None
    logger.error("❌ Binance falhou")

# Estatísticas
total_requests = 0
total_buy = 0
total_sell = 0
total_hold = 0
last_mtime = 0

logger.info("="*80)
logger.info("🚀 CRYPTO SIMPLES FUNCIONAL - ATIVO")
logger.info("="*80)

def analyze(symbol='BTC/USDT'):
    """Análise técnica SIMPLES e FUNCIONAL"""
    global exchange
    
    try:
        # Buscar dados 5min (para capturar movimentos rápidos)
        ohlcv = exchange.fetch_ohlcv(symbol, '5m', limit=100)
        
        closes = [x[4] for x in ohlcv]
        highs = [x[2] for x in ohlcv]
        lows = [x[3] for x in ohlcv]
        
        # RSI(14)
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        rsi = 100
        if avg_loss > 0:
            rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        # ATR(14)
        trs = []
        for i in range(-14, 0):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]) if i > -14 else 0,
                abs(lows[i] - closes[i-1]) if i > -14 else 0
            )
            trs.append(tr)
        atr = sum(trs) / len(trs)
        
        current_price = closes[-1]
        
        logger.info(f"  RSI: {rsi:.1f} | Preço: {current_price:.2f} | ATR: {atr:.2f}")
        
        # SINAIS AGRESSIVOS (para pegar movimentos de 34k pontos!)
        if rsi < 40:  # Oversold moderado
            action = 'BUY'
            confidence = 0.60 + ((40 - rsi) / 100)
            sl = current_price - (2 * atr)
            tp = current_price + (8 * atr)  # Target agressivo!
            reason = f"RSI {rsi:.1f} (oversold)"
        elif rsi > 60:  # Overbought moderado
            action = 'SELL'
            confidence = 0.60 + ((rsi - 60) / 100)
            sl = current_price + (2 * atr)
            tp = current_price - (8 * atr)
            reason = f"RSI {rsi:.1f} (overbought)"
        else:
            return {'action': 'HOLD', 'confidence': 0.0, 'reason': f'RSI neutro ({rsi:.1f})'}
        
        logger.info(f"  🎯 SINAL: {action} @ {confidence:.2%} | SL: {sl:.2f} | TP: {tp:.2f}")
        
        return {
            'action': action,
            'confidence': min(confidence, 0.95),
            'stop_loss': sl,
            'take_profit': tp,
            'reason': reason
        }
    
    except Exception as e:
        logger.error(f"ERRO: {e}")
        return {'action': 'HOLD', 'confidence': 0.0, 'reason': str(e)}

# LOOP PRINCIPAL
try:
    logger.info("⏳ Aguardando requests...\n")
    
    while True:
        if REQUEST_FILE.exists():
            current_mtime = REQUEST_FILE.stat().st_mtime
            
            if current_mtime > last_mtime:
                try:
                    # Ler request
                    with open(REQUEST_FILE, 'r') as f:
                        request = json.load(f)
                    
                    total_requests += 1
                    
                    logger.info("")
                    logger.info("="*80)
                    logger.info(f"REQUEST #{total_requests}: {request.get('symbol')}")
                    logger.info("="*80)
                    
                    # ANALISAR
                    signal = analyze('BTC/USDT')
                    
                    action = signal['action']
                    
                    if action == 'BUY':
                        total_buy += 1
                    elif action == 'SELL':
                        total_sell += 1
                    else:
                        total_hold += 1
                    
                    # Criar response
                    response = {
                        "symbol": request.get('symbol'),
                        "action": action,
                        "confidence": float(signal.get('confidence', 0.0)),
                        "stop_loss": float(signal.get('stop_loss', 0)),
                        "take_profit": float(signal.get('take_profit', 0)),
                        "reason": signal.get('reason', ''),
                        "timestamp": int(datetime.now().timestamp()),
                        "server_version": "SIMPLES_FUNCIONAL"
                    }
                    
                    # Salvar
                    with open(RESPONSE_FILE, 'w') as f:
                        json.dump(response, f, indent=2)
                    
                    logger.info(f"✅ RESPONSE: {action} @ {response['confidence']:.2%}")
                    logger.info(f"📊 BUY={total_buy} | SELL={total_sell} | HOLD={total_hold}")
                    logger.info("="*80 + "\n")
                    
                    last_mtime = current_mtime
                
                except Exception as e:
                    logger.error(f"ERRO: {e}")
        
        time.sleep(1)

except KeyboardInterrupt:
    logger.info(f"\nPARADO | Total: {total_requests} | BUY: {total_buy} | SELL: {total_sell} | HOLD: {total_hold}")

