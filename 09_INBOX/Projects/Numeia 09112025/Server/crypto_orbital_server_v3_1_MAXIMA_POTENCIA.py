# -*- coding: utf-8 -*-
"""
CRYPTO ORBITAL SERVER v3.1 - OTIMIZADO (Pós-Limpeza F1-T3)
TESTE EM CONTA DEMO COM SISTEMA CIENTÍFICO OTIMIZADO

CONFIGURAÇÃO:
- 4 ESTRATÉGIAS CIENTÍFICAS CRYPTO VIÁVEIS (100% peer-reviewed)
- Estratégias ativas: Mean Reversion, Triangular Arb, Momentum, Breakout
- Estratégias removidas: Funding Rate, Liquidity Mining (inviáveis)
- Capital: €120,000 (alocação otimizada Crypto)
- Mercado: CRYPTO 24/7 (aberto agora)

APROVAÇÃO: Conselho - Sistema Otimizado (02-11-2025)
PROTOCOLO: Omega TIER-0 - SISTEMA LIMPO E EFICIENTE
STATUS: OPERACIONAL - 100% VIÁVEL
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# ============================================================================
# SETUP DE PATHS PARA IMPORTAR MÓDULOS CIENTÍFICOS
# ============================================================================

current_dir = Path(__file__).parent
core_dir = current_dir.parent / 'Core'
strategies_crypto_dir = core_dir / 'Strategies' / 'Crypto'

# Adicionar ao path
sys.path.insert(0, str(core_dir))
sys.path.insert(0, str(strategies_crypto_dir))

# Configuração de logging DETALHADO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CRYPTO_ORBITAL] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_orbital_server.log'),
        logging.StreamHandler()
    ]
)

# ============================================================================
# IMPORTS DAS ESTRATÉGIAS CIENTÍFICAS CRYPTO
# ============================================================================

try:
    from CryptoMeanReversionStrategy_Scientific import CryptoMeanReversionStrategy
    from CryptoTriangularArbitrageStrategy_Scientific import CryptoTriangularArbitrageStrategy
    from CryptoMomentumStrategy_Scientific import CryptoMomentumStrategy
    from CryptoBreakoutStrategy_Scientific import CryptoBreakoutStrategy
    # REMOVIDO: FundingRateArbitrage e LiquidityMining (inviáveis - Diretiva F1-T3)
    
    STRATEGIES_LOADED = True
    logging.info("="*80)
    logging.info("✅ 4 ESTRATÉGIAS CIENTÍFICAS CRYPTO CARREGADAS (pós-limpeza)")
    logging.info("="*80)
    
except Exception as e:
    STRATEGIES_LOADED = False
    logging.error(f"❌ ERRO ao carregar estratégias: {e}")
    logging.error("Verifique se está na pasta correta")

class CryptoOrbitalServer:
    """
    Servidor Crypto Orbital - Máxima Potência
    
    FILOSOFIA:
    - ZERO limitações artificiais
    - Todas as 6 estratégias ativas simultaneamente
    - Deixar o motor rugir - ver o que acontece
    - Dados REAIS via ccxt (Binance)
    """
    
    def __init__(self, mt5_files_path=None):
        """Initialize Crypto Orbital Server"""
        
        # Pasta de comunicação com EA
        if mt5_files_path is None:
            self.mt5_files_path = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
        else:
            self.mt5_files_path = Path(mt5_files_path)
        
        self.mt5_files_path.mkdir(parents=True, exist_ok=True)
        
        # ============================================================================
        # INICIALIZAR 6 ESTRATÉGIAS CIENTÍFICAS - FORÇA MÁXIMA
        # ============================================================================
        
        if STRATEGIES_LOADED:
            try:
                self.strategies = {
                    'mean_reversion': CryptoMeanReversionStrategy(),
                    'triangular_arb': CryptoTriangularArbitrageStrategy(),
                    'momentum': CryptoMomentumStrategy(),
                    'breakout': CryptoBreakoutStrategy()
                    # REMOVIDO: funding_rate e liquidity_mining (Diretiva F1-T3)
                }
                
                logging.info("🚀 4 ESTRATÉGIAS CRYPTO INICIALIZADAS (pós-otimização):")
                for name, strategy in self.strategies.items():
                    logging.info(f"  ✅ {name}: {strategy.__class__.__name__}")
                
            except Exception as e:
                logging.error(f"❌ Erro ao inicializar estratégias: {e}")
                self.strategies = {}
        else:
            self.strategies = {}
            logging.warning("⚠️ Estratégias não carregadas - modo fallback")
        
        # Estatísticas
        self.total_requests = 0
        self.total_signals_generated = 0
        self.total_buy_signals = 0
        self.total_sell_signals = 0
        
        logging.info("="*80)
        logging.info("🌟 CRYPTO ORBITAL SERVER v3.1 - SISTEMA OTIMIZADO")
        logging.info("="*80)
        logging.info(f"Capital: €120,000 (pós-otimização)")
        logging.info(f"Estratégias: {len(self.strategies)} (100% viáveis)")
        logging.info(f"Status: OPERACIONAL - Sistema limpo")
        logging.info(f"Pasta comunicação: {self.mt5_files_path}")
        logging.info("="*80)
    
    def analyze_market(self, request_data):
        """
        Analisa mercado com 4 estratégias científicas Crypto (pós-otimização)
        
        Args:
            request_data: Dados do EA (symbol, timeframe, etc)
        
        Returns:
            Dict com sinal para EA
        """
        symbol = request_data.get('symbol', 'BTCUSD')
        
        self.total_requests += 1
        
        logging.info(f"\n{'='*80}")
        logging.info(f"📊 ANÁLISE #{self.total_requests}: {symbol}")
        logging.info(f"{'='*80}")
        
        # Verificar se é crypto
        crypto_symbols = ['BTC', 'ETH', 'BNB', 'CRYPTO']
        is_crypto = any(c in symbol.upper() for c in crypto_symbols)
        
        if not is_crypto:
            logging.warning(f"⚠️ {symbol} não é CRYPTO - retornando HOLD")
            return self._create_response(symbol, "HOLD", 0.0, "Asset não é crypto")
        
        # ============================================================================
        # EXECUTAR TODAS AS 4 ESTRATÉGIAS VIÁVEIS - SISTEMA OTIMIZADO
        # ============================================================================
        
        all_signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                logging.info(f"\n🔍 Executando: {strategy_name}...")
                
                # Gerar sinal (use_real_data=True para ccxt)
                signal = strategy.generate_signal(use_real_data=True)
                
                if signal:
                    logging.info(f"  ✅ SINAL: {signal['action']} {signal['asset']} @ {signal['confidence']:.2f}")
                    all_signals.append({
                        'strategy': strategy_name,
                        'signal': signal
                    })
                else:
                    logging.info(f"  💤 Sem sinal")
            
            except Exception as e:
                logging.error(f"  ❌ Erro em {strategy_name}: {e}")
        
        # ============================================================================
        # SELECIONAR MELHOR SINAL (MAIOR CONFIDENCE) - SEM FILTROS ARTIFICIAIS
        # ============================================================================
        
        if not all_signals:
            logging.info("\n💤 RESULTADO: Nenhuma estratégia gerou sinal")
            return self._create_response(symbol, "HOLD", 0.0, "Nenhuma estratégia ativa")
        
        # Ordenar por confidence
        all_signals.sort(key=lambda x: x['signal']['confidence'], reverse=True)
        
        # Melhor sinal
        best = all_signals[0]
        best_signal = best['signal']
        best_strategy = best['strategy']
        
        logging.info(f"\n🏆 MELHOR SINAL:")
        logging.info(f"  Estratégia: {best_strategy}")
        logging.info(f"  Action: {best_signal['action']}")
        logging.info(f"  Asset: {best_signal['asset']}")
        logging.info(f"  Confidence: {best_signal['confidence']:.2f}")
        
        # Estatísticas
        self.total_signals_generated += 1
        if best_signal['action'] == 'BUY':
            self.total_buy_signals += 1
        elif best_signal['action'] == 'SELL':
            self.total_sell_signals += 1
        
        # Retornar para EA
        return self._create_response(
            symbol=symbol,
            action=best_signal['action'],
            confidence=best_signal['confidence'],
            reason=f"Estratégia: {best_strategy}",
            strategy_id=best_strategy,
            metadata=best_signal.get('metadata', {})
        )
    
    def _create_response(self, symbol, action, confidence, reason, strategy_id=None, metadata=None):
        """Cria resposta formatada para EA"""
        return {
            "symbol": symbol,
            "action": action,
            "confidence": float(confidence),
            "reason": reason,
            "timestamp": int(time.time()),
            "server_version": "3.1.0_CRYPTO_ORBITAL_MAX_POWER",
            "source": "crypto_scientific",
            "strategy_id": strategy_id or "none",
            "metadata": metadata or {},
            "statistics": {
                "total_requests": self.total_requests,
                "total_signals": self.total_signals_generated,
                "buy_signals": self.total_buy_signals,
                "sell_signals": self.total_sell_signals
            }
        }
    
    def start(self):
        """Inicia servidor em loop contínuo"""
        logging.info("\n" + "="*80)
        logging.info("🚀 CRYPTO ORBITAL SERVER - ENTRANDO EM ÓRBITA")
        logging.info("="*80)
        logging.info("Modo: FORÇA MÁXIMA (zero limitações)")
        logging.info("Estratégias: 6 científicas ativas")
        logging.info("Dados: REAIS via ccxt (Binance)")
        logging.info("Capital: €150,000")
        logging.info("Conta: DEMO (teste seguro)")
        logging.info("="*80)
        logging.info("\n⏳ Aguardando requisições do EA...\n")
        
        request_folder = self.mt5_files_path / 'requests'
        response_folder = self.mt5_files_path / 'responses'
        
        request_folder.mkdir(parents=True, exist_ok=True)
        response_folder.mkdir(parents=True, exist_ok=True)
        
        while True:
            try:
                # Procurar requisições
                request_files = list(request_folder.glob('request_*.json'))
                
                for request_file in request_files:
                    try:
                        # Ler requisição
                        with open(request_file, 'r') as f:
                            request_data = json.load(f)
                        
                        # Processar
                        response = self.analyze_market(request_data)
                        
                        # Salvar resposta
                        response_file = response_folder / f"response_{request_file.stem.split('_')[1]}.json"
                        with open(response_file, 'w') as f:
                            json.dump(response, f, indent=2)
                        
                        logging.info(f"\n✅ RESPOSTA ENVIADA: {response_file.name}")
                        logging.info(f"   {response['action']} @ {response['confidence']:.2f}")
                        
                        # Remover requisição
                        request_file.unlink()
                    
                    except Exception as e:
                        logging.error(f"❌ Erro ao processar {request_file}: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(1)
            
            except KeyboardInterrupt:
                logging.info("\n\n🛑 SERVIDOR INTERROMPIDO PELO USUÁRIO")
                logging.info(f"\n📊 ESTATÍSTICAS FINAIS:")
                logging.info(f"  Total Requisições: {self.total_requests}")
                logging.info(f"  Total Sinais: {self.total_signals_generated}")
                logging.info(f"  BUY: {self.total_buy_signals}")
                logging.info(f"  SELL: {self.total_sell_signals}")
                break
            except Exception as e:
                logging.error(f"❌ Erro no loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 CRYPTO ORBITAL SERVER v3.1 - SISTEMA OTIMIZADO")
    print("="*80)
    print("\nMODO: OPERACIONAL (pós-limpeza F1-T3)")
    print("ESTRATÉGIAS: 4 científicas viáveis (peer-reviewed)")
    print("CAPITAL: €120,000")
    print("DADOS: REAIS via ccxt")
    print("\n⚠️  AVISO: Este é um TESTE em conta DEMO")
    print("⚠️  Sistema otimizado - apenas estratégias viáveis")
    print("\n" + "="*80)
    
    # Criar e iniciar servidor
    server = CryptoOrbitalServer()
    
    if not server.strategies:
        print("\n❌ ERRO: Estratégias não carregadas")
        print("Verifique se está executando da pasta Server/")
        print("\nComando correto:")
        print("cd C:\\Users\\Lenovo\\.cursor\\SamsungGlobalMarket\\Server")
        print("python crypto_orbital_server_v3_1_MAXIMA_POTENCIA.py")
        sys.exit(1)
    
    print("\n✅ SISTEMA PRONTO PARA LANÇAMENTO")
    print("\nPressione Ctrl+C para parar a qualquer momento")
    print("\n" + "="*80)
    
    input("\nPressione ENTER para iniciar lançamento orbital... ")
    
    # LANÇAMENTO!
    server.start()

