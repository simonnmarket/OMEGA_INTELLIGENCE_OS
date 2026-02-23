# -*- coding: utf-8 -*-
"""
CRYPTO SERVER SIMPLES E FUNCIONAL
Solução minimalista - FUNCIONA GARANTIDO

EA cria: request.json
Servidor lê: request.json
Servidor cria: response.json
EA lê: response.json
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Logging simples
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pasta MT5
MT5_PATH = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
REQUEST_FILE = MT5_PATH / 'AIRequest.BTCUSD.json'  # ARQUIVO QUE O EA USA
RESPONSE_FILE = MT5_PATH / 'response.json'

logger.info("="*80)
logger.info("CRYPTO SERVER SIMPLES - INICIANDO")
logger.info(f"Request: {REQUEST_FILE}")
logger.info(f"Response: {RESPONSE_FILE}")
logger.info("="*80)

# Estatísticas
total_requests = 0
last_mtime = 0

try:
    while True:
        # Verificar se há request NOVO (por timestamp)
        if REQUEST_FILE.exists():
            current_mtime = REQUEST_FILE.stat().st_mtime
            
            if current_mtime > last_mtime:
                try:
                    # Ler request
                    with open(REQUEST_FILE, 'r') as f:
                        request = json.load(f)
                    
                    total_requests += 1
                    symbol = request.get('symbol', 'UNKNOWN')
                    
                    logger.info(f"REQUEST #{total_requests}: {symbol}")
                    
                    # Criar response (HOLD por enquanto para testar)
                    response = {
                        "symbol": symbol,
                        "action": "HOLD",
                        "confidence": 0.5,
                        "reason": "Sistema em validação",
                        "timestamp": int(datetime.now().timestamp())
                    }
                    
                    # Salvar response
                    with open(RESPONSE_FILE, 'w') as f:
                        json.dump(response, f, indent=2)
                    
                    logger.info(f"RESPONSE: {response['action']}")
                    
                    # Atualizar timestamp processado
                    last_mtime = current_mtime
                    
                except Exception as e:
                    logger.error(f"ERRO: {e}")
        
        # Aguardar 1 segundo
        time.sleep(1)

except KeyboardInterrupt:
    logger.info(f"\nSERVIDOR PARADO. Total: {total_requests} requests")

