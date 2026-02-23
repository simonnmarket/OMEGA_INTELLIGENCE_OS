# -*- coding: utf-8 -*-
"""
CRYPTO SERVER FINAL v3.2 - SOLUÇÃO DEFINITIVA
Data: 02-11-2025

PROBLEMA RESOLVIDO:
- EA cria: AIRequest.BTCUSD.json (atualiza continuamente)
- Servidor monitora e processa sem loop infinito
- Usa hash do conteúdo para evitar reprocessamento

STATUS: TESTADO E FUNCIONAL
"""

import os
import sys
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Setup paths
current_dir = Path(__file__).parent
core_dir = current_dir.parent / 'Core'
sys.path.insert(0, str(core_dir))

# Logging
log_file = current_dir / 'crypto_server_final.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoServerFinal:
    def __init__(self):
        # Pasta MT5
        self.mt5_files_path = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
        self.request_file = self.mt5_files_path / 'AIRequest.BTCUSD.json'
        
        # Controle de processamento (usa hash do conteúdo)
        self.last_processed_hash = None
        
        # Estatísticas
        self.total_requests = 0
        self.total_buy = 0
        self.total_sell = 0
        self.total_hold = 0
        
        logger.info("="*80)
        logger.info("CRYPTO SERVER FINAL v3.2 - INICIALIZADO")
        logger.info("="*80)
        logger.info(f"Arquivo monitorado: {self.request_file.name}")
        logger.info(f"Pasta: {self.mt5_files_path}")
        logger.info("="*80)
    
    def _get_file_hash(self, file_path):
        """Calcula hash do conteúdo do arquivo"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def analyze_market(self, request_data):
        """
        Análise de mercado simplificada
        PLACEHOLDER: Retorna HOLD por enquanto
        TODO: Integrar estratégias científicas depois de validar comunicação
        """
        symbol = request_data.get('symbol', 'UNKNOWN')
        bid = request_data.get('bid', 0)
        ask = request_data.get('ask', 0)
        
        logger.info(f"Analisando: {symbol} | Bid: {bid} | Ask: {ask}")
        
        # Por enquanto, sempre retorna HOLD (para testar comunicação)
        action = "HOLD"
        confidence = 0.0
        reason = "Sistema em validação - aguardando confirmação de comunicação"
        
        self.total_hold += 1
        
        return {
            "symbol": symbol,
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "timestamp": int(datetime.now().timestamp()),
            "server_version": "3.2_FINAL"
        }
    
    def process_request(self):
        """Processa um request se for novo"""
        if not self.request_file.exists():
            return False
        
        # Calcular hash do arquivo atual
        current_hash = self._get_file_hash(self.request_file)
        
        if current_hash is None:
            return False
        
        # Se já processamos este exato conteúdo, pular
        if current_hash == self.last_processed_hash:
            return False
        
        # Novo request detectado!
        try:
            # Ler request
            with open(self.request_file, 'r') as f:
                request_data = json.load(f)
            
            # Incrementar contador
            self.total_requests += 1
            
            logger.info("")
            logger.info("="*80)
            logger.info(f"REQUEST #{self.total_requests} RECEBIDO")
            logger.info("="*80)
            
            # Processar
            response = self.analyze_market(request_data)
            
            # Criar arquivo de resposta SEPARADO (para EA ler)
            response_file = self.mt5_files_path / 'AIResponse.BTCUSD.json'
            with open(response_file, 'w') as f:
                json.dump(response, f, indent=2)
            
            logger.info(f"RESPOSTA: {response['action']} | Confidence: {response['confidence']:.2f}")
            logger.info(f"Arquivo resposta criado: {response_file.name}")
            logger.info("="*80)
            logger.info("")
            
            # Atualizar hash processado
            self.last_processed_hash = current_hash
            
            return True
        
        except Exception as e:
            logger.error(f"ERRO ao processar request: {e}")
            return False
    
    def start(self):
        """Loop principal do servidor"""
        logger.info("")
        logger.info("="*80)
        logger.info("SERVIDOR ATIVO - AGUARDANDO REQUESTS")
        logger.info("="*80)
        logger.info("")
        
        cycle_count = 0
        
        try:
            while True:
                # Tentar processar
                processed = self.process_request()
                
                if processed:
                    logger.info(f"Estatísticas: Total={self.total_requests} | BUY={self.total_buy} | SELL={self.total_sell} | HOLD={self.total_hold}")
                
                # A cada 60 ciclos (1 minuto), mostrar heartbeat
                cycle_count += 1
                if cycle_count >= 60:
                    logger.info(f"[HEARTBEAT] Servidor ativo | Requests processados: {self.total_requests}")
                    cycle_count = 0
                
                # Aguardar 1 segundo
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("")
            logger.info("="*80)
            logger.info("SERVIDOR PARADO PELO USUÁRIO")
            logger.info("="*80)
            logger.info(f"Total de requests processados: {self.total_requests}")
            logger.info(f"BUY: {self.total_buy} | SELL: {self.total_sell} | HOLD: {self.total_hold}")
            logger.info("="*80)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CRYPTO SERVER FINAL v3.2")
    print("="*80)
    print("\nSOLUÇÃO DEFINITIVA:")
    print("- Monitoramento via hash de conteúdo (sem loop)")
    print("- Resposta em arquivo separado")
    print("- Logs detalhados")
    print("\n" + "="*80 + "\n")
    
    server = CryptoServerFinal()
    server.start()

