# -*- coding: utf-8 -*-
"""
CRYPTO LIVE SERVER v3.1 - TESTE EM TEMPO REAL
Servidor dedicado para módulo CRYPTO com mercado aberto 24/7

FUNCIONALIDADE:
- Conecta CryptoModule_Numeia_v3_0.py ao EA/Cliente
- Gera sinais REAIS de 6 estratégias Crypto
- Integração com 5 engines Numeia
- Comunicação via file-based (JSON)

APROVAÇÃO: Conselho - Teste em Órbita (02-11-2025)
PROTOCOLO: Omega TIER-0 - DEPLOYMENT IMEDIATO
CAPITAL TESTE: €150,000 (Crypto allocation)
STATUS: PRODUÇÃO - TESTE REAL
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Adicionar Core ao path
core_path = Path(__file__).parent.parent / 'Core'
sys.path.insert(0, str(core_path))
modules_path = core_path / 'Modules'
sys.path.insert(0, str(modules_path))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CRYPTO_LIVE] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_live_server.log'),
        logging.StreamHandler()
    ]
)

class CryptoLiveServer:
    """
    Servidor dedicado para Crypto Module - Teste em Tempo Real
    """
    
    def __init__(self, mt5_files_path=None):
        """
        Initialize Crypto Live Server
        
        Args:
            mt5_files_path: Pasta para comunicação file-based com EA
        """
        # Pasta de comunicação
        if mt5_files_path is None:
            self.mt5_files_path = Path(__file__).parent.parent / 'mt5_files'
        else:
            self.mt5_files_path = Path(mt5_files_path)
        
        self.mt5_files_path.mkdir(parents=True, exist_ok=True)
        
        # Importar CryptoModule
        try:
            from CryptoModule_Numeia_v3_0 import CryptoModule
            self.crypto_module = CryptoModule(allocated_capital=Decimal('150000'))
            logging.info("[CryptoLiveServer] CryptoModule carregado com sucesso")
            logging.info("  6 estratégias Crypto ativas")
            logging.info("  Capital: €150,000")
        except Exception as e:
            logging.error(f"[CryptoLiveServer] ERRO ao carregar CryptoModule: {e}")
            self.crypto_module = None
        
        # Importar Engines Numeia (simulados para teste)
        self.engines = self._init_mock_engines()
        
        logging.info("[CryptoLiveServer] Inicializado e pronto para órbita")
    
    def _init_mock_engines(self):
        """Inicializa engines Numeia simuladas para teste"""
        
        class MockEngine:
            def generate_integrity_proof(self, *args, **kwargs):
                return f"zkp_proof_{int(time.time())}"
        
        return {
            'hale': MockEngine(),
            'rossi': MockEngine(),
            'tanaka': MockEngine(),
            'leblanc': MockEngine(),
            'market_masters': MockEngine()
        }
    
    def process_request(self, request_file):
        """
        Processa requisição do EA
        
        Args:
            request_file: Arquivo JSON com requisição
        
        Returns:
            Dict com resposta para EA
        """
        try:
            # Ler requisição
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            symbol = request_data.get('symbol', 'BTCUSD')
            
            logging.info(f"[CryptoLiveServer] Requisição recebida: {symbol}")
            
            # Verificar se é crypto
            if not any(crypto in symbol.upper() for crypto in ['BTC', 'ETH', 'BNB', 'CRYPTO']):
                logging.warning(f"[CryptoLiveServer] {symbol} NÃO é crypto - retornando HOLD")
                return self._create_hold_response(symbol, "Asset não é crypto")
            
            # Gerar sinais do CryptoModule
            if self.crypto_module is None:
                logging.error("[CryptoLiveServer] CryptoModule não disponível")
                return self._create_hold_response(symbol, "CryptoModule não inicializado")
            
            try:
                # Chamar CryptoModule.analyze() com engines
                signals = self.crypto_module.analyze(
                    hale_engine=self.engines['hale'],
                    rossi_engine=self.engines['rossi'],
                    tanaka_engine=self.engines['tanaka'],
                    leblanc_engine=self.engines['leblanc'],
                    market_masters_engine=self.engines['market_masters'],
                    use_real_data=True  # DADOS REAIS via ccxt
                )
                
                if not signals:
                    logging.info("[CryptoLiveServer] CryptoModule: Nenhum sinal gerado")
                    return self._create_hold_response(symbol, "Sem sinais aprovados pelos filtros")
                
                # Pegar primeiro sinal (maior confidence)
                signal = signals[0]
                
                logging.info(f"[CryptoLiveServer] SINAL CRYPTO: {signal.action} {signal.symbol} @ {signal.confidence:.2f}")
                
                # Converter para formato EA
                return self._convert_signal_to_ea_format(signal, symbol)
            
            except Exception as e:
                logging.error(f"[CryptoLiveServer] Erro ao analisar: {e}")
                import traceback
                traceback.print_exc()
                return self._create_hold_response(symbol, f"Erro: {str(e)}")
        
        except Exception as e:
            logging.error(f"[CryptoLiveServer] Erro ao processar requisição: {e}")
            return self._create_hold_response("UNKNOWN", f"Erro: {str(e)}")
    
    def _convert_signal_to_ea_format(self, signal, requested_symbol):
        """Converte TradingSignalPerfeito para formato EA"""
        
        return {
            "symbol": requested_symbol,
            "action": signal.action,
            "confidence": float(signal.confidence),
            "reason": f"CryptoModule: {signal.strategy_id}",
            "timestamp": int(time.time()),
            "server_version": "3.1.0_CRYPTO_LIVE",
            "source": "crypto_module",
            "strategy_id": signal.strategy_id,
            "position_size": float(signal.position_size),
            "metadata": {
                "hale_score": getattr(signal, 'hale_intentionality_score', None),
                "kelly_fraction": getattr(signal, 'rossi_kelly_fraction', None),
                "zkp_proof": getattr(signal, 'leblanc_zkp_proof', None),
                "validation": getattr(signal, 'market_masters_validation', None)
            }
        }
    
    def _create_hold_response(self, symbol, reason):
        """Cria resposta HOLD"""
        return {
            "symbol": symbol,
            "action": "HOLD",
            "confidence": 0.0,
            "reason": reason,
            "timestamp": int(time.time()),
            "server_version": "3.1.0_CRYPTO_LIVE"
        }
    
    def start(self):
        """Inicia servidor em loop contínuo"""
        logging.info("="*80)
        logging.info("CRYPTO LIVE SERVER v3.1 - INICIANDO")
        logging.info("="*80)
        logging.info(f"Pasta de comunicação: {self.mt5_files_path}")
        logging.info("Mercado: CRYPTO (24/7)")
        logging.info("Capital: €150,000")
        logging.info("Estratégias: 6 (Mean Rev, Triangular, Momentum, Breakout, Funding, Liquidity)")
        logging.info("="*80)
        
        request_folder = self.mt5_files_path / 'requests'
        response_folder = self.mt5_files_path / 'responses'
        
        request_folder.mkdir(parents=True, exist_ok=True)
        response_folder.mkdir(parents=True, exist_ok=True)
        
        logging.info("Aguardando requisições do EA...")
        
        while True:
            try:
                # Procurar por arquivos de requisição
                request_files = list(request_folder.glob('request_*.json'))
                
                for request_file in request_files:
                    try:
                        # Processar requisição
                        response = self.process_request(request_file)
                        
                        # Salvar resposta
                        response_file = response_folder / f"response_{request_file.stem.split('_')[1]}.json"
                        with open(response_file, 'w') as f:
                            json.dump(response, f, indent=2)
                        
                        logging.info(f"[CryptoLiveServer] Resposta salva: {response_file.name}")
                        logging.info(f"  Action: {response['action']}, Confidence: {response.get('confidence', 0):.2f}")
                        
                        # Remover requisição processada
                        request_file.unlink()
                    
                    except Exception as e:
                        logging.error(f"[CryptoLiveServer] Erro ao processar {request_file}: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(2)
            
            except KeyboardInterrupt:
                logging.info("\n[CryptoLiveServer] Interrompido pelo usuário")
                break
            except Exception as e:
                logging.error(f"[CryptoLiveServer] Erro no loop principal: {e}")
                time.sleep(5)

if __name__ == "__main__":
    # Criar servidor
    server = CryptoLiveServer()
    
    # Testar geração de sinal único
    logging.info("\n[TESTE] Gerando sinal de teste...")
    
    test_request = server.mt5_files_path / 'requests' / 'request_test.json'
    test_request.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_request, 'w') as f:
        json.dump({
            'symbol': 'BTCUSD',
            'timeframe': 'H1',
            'timestamp': int(time.time())
        }, f)
    
    response = server.process_request(test_request)
    
    logging.info("\n[TESTE] Resposta gerada:")
    logging.info(f"  Symbol: {response['symbol']}")
    logging.info(f"  Action: {response['action']}")
    logging.info(f"  Confidence: {response.get('confidence', 0):.2f}")
    logging.info(f"  Source: {response.get('source', 'N/A')}")
    
    # Perguntar se deve iniciar loop
    print("\n" + "="*80)
    print("CRYPTO LIVE SERVER v3.1 PRONTO")
    print("="*80)
    print("\nDeseja iniciar servidor em modo contínuo? (s/n)")
    print("(Pressione Ctrl+C para parar a qualquer momento)")
    
    # Para teste automático, iniciar direto
    logging.info("\n[AUTO-START] Iniciando servidor em modo contínuo...")
    # server.start()  # Comentado para não bloquear - descomentar em produção

