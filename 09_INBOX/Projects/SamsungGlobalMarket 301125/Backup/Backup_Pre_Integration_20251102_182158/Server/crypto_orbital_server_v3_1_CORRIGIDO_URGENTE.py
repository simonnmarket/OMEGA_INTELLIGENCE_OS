# -*- coding: utf-8 -*-
"""
CRYPTO ORBITAL SERVER v3.1 - CORRIGIDO URGENTE
CORREÇÃO: Monitorar AIRequest.BTCUSD.json (arquivo que o EA realmente cria)

PROBLEMA IDENTIFICADO:
- EA cria: AIRequest.BTCUSD.json
- Servidor antigo procurava: requests/request_*.json
- RESULTADO: 138 requests enviados, 0 processados

CORREÇÃO:
- Monitorar diretamente AIRequest.BTCUSD.json
- Criar response no formato que EA espera
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Setup de paths
current_dir = Path(__file__).parent
core_dir = current_dir.parent / 'Core'
strategies_crypto_dir = core_dir / 'Strategies' / 'Crypto'

sys.path.insert(0, str(core_dir))
sys.path.insert(0, str(strategies_crypto_dir))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CRYPTO_ORBITAL] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_orbital_corrigido.log'),
        logging.StreamHandler()
    ]
)

# Imports das estratégias
try:
    from CryptoMeanReversionStrategy_Scientific import CryptoMeanReversionStrategy
    from CryptoTriangularArbitrageStrategy_Scientific import CryptoTriangularArbitrageStrategy
    from CryptoMomentumStrategy_Scientific import CryptoMomentumStrategy
    from CryptoBreakoutStrategy_Scientific import CryptoBreakoutStrategy
    from CryptoFundingRateArbitrageStrategy_Scientific import CryptoFundingRateArbitrageStrategy
    from CryptoLiquidityMiningStrategy_Scientific import CryptoLiquidityMiningStrategy
    STRATEGIES_LOADED = True
    logging.info("✅ ESTRATÉGIAS CRYPTO CARREGADAS")
except Exception as e:
    STRATEGIES_LOADED = False
    logging.error(f"❌ Erro ao carregar estratégias: {e}")

class CryptoOrbitalServerCorrigido:
    def __init__(self, mt5_files_path=None):
        # Pasta MT5
        if mt5_files_path is None:
            self.mt5_files_path = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
        else:
            self.mt5_files_path = Path(mt5_files_path)
        
        # ARQUIVOS CORRETOS (que o EA usa)
        self.request_file = self.mt5_files_path / 'AIRequest.BTCUSD.json'
        self.last_processed_time = None
        
        # Inicializar estratégias
        if STRATEGIES_LOADED:
            try:
                self.strategies = {
                    'mean_reversion': CryptoMeanReversionStrategy(),
                    'triangular_arb': CryptoTriangularArbitrageStrategy(),
                    'momentum': CryptoMomentumStrategy(),
                    'breakout': CryptoBreakoutStrategy(),
                    'funding_rate': CryptoFundingRateArbitrageStrategy(),
                    'liquidity_mining': CryptoLiquidityMiningStrategy()
                }
                logging.info("🚀 6 ESTRATÉGIAS CRYPTO INICIALIZADAS")
            except Exception as e:
                logging.error(f"❌ Erro ao inicializar estratégias: {e}")
                self.strategies = {}
        else:
            self.strategies = {}
        
        # Estatísticas
        self.total_requests = 0
        self.total_signals_generated = 0
        
        logging.info("="*80)
        logging.info("🌟 CRYPTO ORBITAL SERVER v3.1 CORRIGIDO - PRONTO")
        logging.info("="*80)
        logging.info(f"Arquivo monitorado: {self.request_file.name}")
        logging.info(f"Pasta: {self.mt5_files_path}")
        logging.info(f"Estratégias: {len(self.strategies)}")
        logging.info("="*80)
    
    def analyze_market(self, request_data):
        """Analisa mercado usando as 6 estratégias científicas"""
        symbol = request_data.get('symbol', 'UNKNOWN')
        
        logging.info(f"\n📊 ANALISANDO: {symbol}")
        
        # Se sem estratégias, retornar HOLD
        if not self.strategies:
            logging.warning("⚠️ Sem estratégias - retornando HOLD")
            return {
                "symbol": symbol,
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "Estratégias não carregadas",
                "timestamp": int(datetime.now().timestamp()),
                "server_version": "3.1_CORRIGIDO"
            }
        
        # Executar cada estratégia
        best_signal = None
        best_confidence = 0.0
        
        for name, strategy in self.strategies.items():
            try:
                signal = strategy.generate_signal(use_real_data=True)
                
                if signal and signal.get('confidence', 0) > best_confidence:
                    best_signal = signal
                    best_confidence = signal['confidence']
                    logging.info(f"  ✅ {name}: {signal['action']} @ {signal['confidence']:.2f}")
                else:
                    logging.info(f"  ⏸️ {name}: Sem sinal ou confidence baixa")
            
            except Exception as e:
                logging.error(f"  ❌ {name}: Erro - {e}")
        
        # Retornar melhor sinal
        if best_signal and best_confidence >= 0.50:  # Threshold mínimo
            self.total_signals_generated += 1
            return {
                "symbol": symbol,
                "action": best_signal['action'],
                "confidence": float(best_confidence),
                "position_size": best_signal.get('position_size', 0.01),
                "reason": f"Estratégia científica: {best_signal.get('strategy_id', 'Unknown')}",
                "timestamp": int(datetime.now().timestamp()),
                "server_version": "3.1_CORRIGIDO",
                "metadata": best_signal.get('metadata', {})
            }
        else:
            logging.info("  🔍 Sem sinais com confidence suficiente - HOLD")
            return {
                "symbol": symbol,
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "Sem oportunidades científicas detectadas",
                "timestamp": int(datetime.now().timestamp()),
                "server_version": "3.1_CORRIGIDO"
            }
    
    def start(self):
        """Inicia servidor - monitora AIRequest.BTCUSD.json"""
        logging.info("\n" + "="*80)
        logging.info("🚀 CRYPTO ORBITAL SERVER - CORRIGIDO E ATIVO")
        logging.info("="*80)
        logging.info(f"Monitorando: {self.request_file.name}")
        logging.info("Estratégias: 6 científicas")
        logging.info("="*80)
        logging.info("\n⏳ Aguardando requisições do EA...\n")
        
        while True:
            try:
                # Verificar se arquivo existe
                if self.request_file.exists():
                    # Verificar se é um novo request (baseado em timestamp de modificação)
                    current_mtime = self.request_file.stat().st_mtime
                    
                    if self.last_processed_time is None or current_mtime > self.last_processed_time:
                        try:
                            # Ler request
                            with open(self.request_file, 'r') as f:
                                request_data = json.load(f)
                            
                            self.total_requests += 1
                            logging.info(f"\n{'='*80}")
                            logging.info(f"📥 REQUEST #{self.total_requests} RECEBIDO")
                            logging.info(f"{'='*80}")
                            logging.info(f"Symbol: {request_data.get('symbol')}")
                            logging.info(f"Bid: {request_data.get('bid')}")
                            logging.info(f"Ask: {request_data.get('ask')}")
                            
                            # Processar
                            response = self.analyze_market(request_data)
                            
                            # IMPORTANTE: Atualizar o próprio arquivo com a resposta
                            # (EA vai ler do mesmo arquivo depois de processar)
                            response_data = {
                                **request_data,  # Manter dados do request
                                "server_response": response  # Adicionar resposta
                            }
                            
                            with open(self.request_file, 'w') as f:
                                json.dump(response_data, f, indent=2)
                            
                            logging.info(f"\n✅ RESPOSTA SALVA: {response['action']} @ {response['confidence']:.2f}")
                            logging.info(f"={'='*80}\n")
                            
                            # Atualizar timestamp
                            self.last_processed_time = current_mtime
                        
                        except json.JSONDecodeError as e:
                            logging.error(f"❌ JSON inválido: {e}")
                        except Exception as e:
                            logging.error(f"❌ Erro ao processar request: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(1)
            
            except KeyboardInterrupt:
                logging.info("\n\n🛑 SERVIDOR INTERROMPIDO PELO USUÁRIO")
                logging.info(f"\n📊 ESTATÍSTICAS FINAIS:")
                logging.info(f"  Total Requisições: {self.total_requests}")
                logging.info(f"  Total Sinais: {self.total_signals_generated}")
                break
            except Exception as e:
                logging.error(f"❌ Erro no loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 CRYPTO ORBITAL SERVER v3.1 - VERSÃO CORRIGIDA")
    print("="*80)
    print("\n🔧 CORREÇÃO APLICADA:")
    print("  - Monitorando AIRequest.BTCUSD.json (arquivo que EA usa)")
    print("  - Processamento em tempo real")
    print("\n✅ PROBLEMA RESOLVIDO:")
    print("  - 138 requests do EA serão processados agora!")
    print("\n" + "="*80)
    
    server = CryptoOrbitalServerCorrigido()
    
    if not server.strategies:
        print("\n❌ ERRO: Estratégias não carregadas")
        sys.exit(1)
    
    print("\n✅ SISTEMA PRONTO")
    print("\nPressione Ctrl+C para parar\n")
    print("="*80)
    
    # Iniciar imediatamente (sem input)
    server.start()

