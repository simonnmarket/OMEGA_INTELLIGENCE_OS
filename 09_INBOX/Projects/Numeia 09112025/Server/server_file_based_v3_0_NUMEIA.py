"""
Samsung Global Market - Servidor de Análise ML v3.0 COM NUMEIA
Comunicação baseada em arquivos (File-Based IPC)
INTEGRAÇÃO COMPLETA: NumeiaTradingSystem v3.0

PROTOCOLO: Omega TIER-0 - Recuperação Crítica
DATA: 2025-10-30
STATUS: PRODUÇÃO - NumeiaTradingSystem ATIVO
"""

import os
import json
import glob
import time
import logging
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from typing import Dict, List

# Adicionar diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Core"))

# ============================================================================
# IMPORTS DO NUMEIA TRADING SYSTEM
# ============================================================================
try:
    from NumeiaTradingSystem_v3_0_FINAL import (
        HaleIntentionalityEngine,
        RossiDynamicKellyEngine,
        TanakaKalmanEngine,
        LeblancZKPEngine,
        MarketMastersPerfectionEngine,
        PetrovEntanglementEngine,
        OilStrategyProvenV3,
        GoldenStrategyFuturesV3,
        TradingSignalPerfeito
    )
    NUMEIA_LOADED = True
    logger_init_msg = "[OK] NumeiaTradingSystem v3.0 importado com sucesso"
except ImportError as e:
    NUMEIA_LOADED = False
    logger_init_msg = f"[ERRO] Falha ao importar NumeiaTradingSystem: {e}"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Log de inicialização
logger.info("=" * 70)
logger.info("SAMSUNG GLOBAL MARKET - SERVIDOR V3.0 COM NUMEIA")
logger.info("=" * 70)
logger.info(logger_init_msg)
logger.info("=" * 70)


class SamsungNumeiaServer:
    """
    Servidor de análise ML v3.0 que integra o NumeiaTradingSystem.
    Comunica com EA via arquivos JSON (file-based IPC).
    """
    
    def __init__(self, mt5_files_path=None):
        """
        Inicializar servidor com NumeiaTradingSystem.
        
        Args:
            mt5_files_path: Caminho para diretório de arquivos do MT5.
        """
        if mt5_files_path is None:
            mt5_files_path = os.path.join(
                os.getenv('APPDATA'),
                'MetaQuotes', 'Terminal', 'Common', 'Files'
            )
        
        self.mt5_files_path = mt5_files_path
        self.running = False
        self.numeia_loaded = NUMEIA_LOADED
        
        # ================================================================
        # INICIALIZAR ENGINES DO NUMEIA
        # ================================================================
        if self.numeia_loaded:
            try:
                logger.info("[INIT] Inicializando engines do Numeia...")
                
                self.hale_engine = HaleIntentionalityEngine()
                logger.info("  [OK] HaleIntentionalityEngine inicializado")
                logger.info(f"       Estado inicial: {self.hale_engine.intentional_state}")
                
                self.petrov_engine = PetrovEntanglementEngine()
                logger.info("  [OK] PetrovEntanglementEngine inicializado")
                
                self.rossi_engine = RossiDynamicKellyEngine()
                logger.info("  [OK] RossiDynamicKellyEngine inicializado")
                
                self.tanaka_engine = TanakaKalmanEngine()
                logger.info("  [OK] TanakaKalmanEngine inicializado")
                
                self.leblanc_engine = LeblancZKPEngine()
                logger.info("  [OK] LeblancZKPEngine inicializado")
                
                self.market_masters = MarketMastersPerfectionEngine()
                logger.info("  [OK] MarketMastersPerfectionEngine inicializado")
                
                # ========================================================
                # INICIALIZAR ESTRATÉGIAS
                # ========================================================
                logger.info("[INIT] Inicializando estratégias...")
                
                self.strategies = [
                    OilStrategyProvenV3(
                        self.hale_engine, self.rossi_engine, self.tanaka_engine,
                        self.leblanc_engine, self.market_masters
                    ),
                    GoldenStrategyFuturesV3(
                        self.hale_engine, self.rossi_engine, self.tanaka_engine,
                        self.leblanc_engine, self.market_masters
                    )
                ]
                
                for strategy in self.strategies:
                    logger.info(f"  [OK] Estratégia: {strategy.strategy_id}")
                
                logger.info("=" * 70)
                logger.info("[SUCCESS] NumeiaTradingSystem v3.0 ATIVO E OPERACIONAL")
                logger.info(f"[SUCCESS] Engines: 6 | Estratégias: {len(self.strategies)}")
                logger.info("=" * 70)
                
            except Exception as e:
                logger.error(f"[ERRO] Falha ao inicializar Numeia: {e}")
                self.numeia_loaded = False
                raise
        else:
            logger.error("[ERRO CRÍTICO] NumeiaTradingSystem não carregado!")
            logger.error("[ERRO CRÍTICO] Sistema NÃO PODE OPERAR sem Numeia!")
            raise ImportError("NumeiaTradingSystem v3.0 é obrigatório para v3.0 server")
        
        logger.info(f"[INFO] Diretório MT5: {self.mt5_files_path}")
    
    def _convert_ea_to_numeia(self, request_data: Dict) -> Dict:
        """
        Converter dados do EA para formato NumeiaTradingSystem.
        
        Args:
            request_data: Dados recebidos do EA (bid, ask, spread, symbol, etc.)
        
        Returns:
            market_data: Dados no formato esperado pelo Numeia
        """
        symbol = request_data.get('symbol', 'UNKNOWN')
        bid = float(request_data.get('bid', 0.0))
        ask = float(request_data.get('ask', 0.0))
        spread = float(request_data.get('spread', 0.0))
        timestamp = request_data.get('time', int(time.time()))
        
        # Construir estrutura de dados para Numeia
        # NOTA: Numeia espera dados mais ricos (macro, etc.)
        # Por enquanto, usar estrutura mínima
        market_data = {
            'symbol': symbol,
            'prices': [bid],  # Simplificado: apenas último preço
            'bid': bid,
            'ask': ask,
            'spread': spread,
            'timestamp': timestamp,
            'macro': {
                'geo_risk': 0.3,  # Valor padrão (TODO: integrar dados reais)
                'dxy': 100.0,     # Valor padrão (TODO: integrar dados reais)
                'inflation': 0.02  # Valor padrão (TODO: integrar dados reais)
            }
        }
        
        return market_data
    
    def _convert_numeia_to_ea(self, signals: List) -> Dict:
        """
        Converter sinais do Numeia para formato EA.
        
        Args:
            signals: Lista de TradingSignalPerfeito do Numeia
        
        Returns:
            response: Resposta no formato esperado pelo EA
        """
        if not signals or len(signals) == 0:
            # Sem sinais → HOLD
            return {
                "action": "HOLD",
                "confidence": 0.90,  # Alta confiança em HOLD (filtros Numeia)
                "reason": "Nenhum sinal gerado - filtros Numeia ativos",
                "timestamp": int(time.time()),
                "server_version": "3.0.0_NUMEIA",
                "source": "numeia",
                "strategy_id": None,
                "risk_score": 0.0,
                "leblanc_zkp_proof": None
            }
        
        # Usar primeiro sinal (pode haver múltiplos)
        signal = signals[0]
        
        # Converter TradingSignalPerfeito para formato EA
        response = {
            "symbol": signal.asset,
            "action": signal.action,  # BUY, SELL, HOLD
            "confidence": float(signal.confidence),
            "risk_score": float(signal.risk_score),
            "reason": f"Sinal Numeia: {signal.strategy_id}",
            "timestamp": signal.timestamp,
            "server_version": "3.0.0_NUMEIA",
            "source": "numeia",
            "strategy_id": signal.strategy_id,
            "leblanc_zkp_proof": signal.leblanc_zkp_proof,
            "metadata": signal.metadata
        }
        
        # Log do sinal gerado
        logger.info("=" * 70)
        logger.info(f"[SINAL NUMEIA] {signal.action} {signal.asset}")
        logger.info(f"  Estratégia: {signal.strategy_id}")
        logger.info(f"  Confidence: {float(signal.confidence):.2%}")
        logger.info(f"  Risk Score: {float(signal.risk_score):.2f}")
        logger.info(f"  ZKP Proof: {signal.leblanc_zkp_proof[:16]}...")
        logger.info("=" * 70)
        
        return response
    
    async def analyze_market(self, request_data: Dict) -> Dict:
        """
        Analisar dados de mercado usando NumeiaTradingSystem.
        
        Args:
            request_data: Dicionário com dados do request (symbol, bid, ask, etc.)
        
        Returns:
            Dicionário com resposta (action, confidence, reason, etc.)
        """
        symbol = request_data.get('symbol', 'UNKNOWN')
        bid = request_data.get('bid', 0.0)
        ask = request_data.get('ask', 0.0)
        spread = request_data.get('spread', 0.0)
        
        logger.info(f"[ANALYZE] {symbol}: bid={bid:.5f}, ask={ask:.5f}, spread={spread:.1f}")
        
        if not self.numeia_loaded:
            logger.error("[ERRO] NumeiaTradingSystem não carregado - retornando HOLD")
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "ERRO: Numeia não carregado",
                "timestamp": int(time.time()),
                "server_version": "3.0.0_NUMEIA_ERROR"
            }
        
        # ================================================================
        # CONVERTER DADOS EA → NUMEIA
        # ================================================================
        market_data = self._convert_ea_to_numeia(request_data)
        
        # ================================================================
        # EXECUTAR ANÁLISE DO NUMEIA
        # ================================================================
        all_signals = []
        
        for strategy in self.strategies:
            try:
                # Executar estratégia (async)
                signals = await strategy.analyze(market_data)
                
                if signals:
                    all_signals.extend(signals)
                    logger.info(f"  [SIGNAL] {strategy.strategy_id}: {len(signals)} sinal(is)")
                
            except Exception as e:
                logger.error(f"  [ERRO] Estratégia {strategy.strategy_id}: {e}")
                continue
        
        # ================================================================
        # APLICAR FILTROS HALEINTENTIONALITY
        # ================================================================
        # TODO: Implementar filtro completo do HaleEngine
        # Por enquanto, apenas verificar estado
        if self.hale_engine.intentional_state == "LIQUIDATE_EXPOSURE":
            logger.warning("[FILTRO] HaleEngine em modo LIQUIDATE - bloqueando sinais")
            all_signals = []  # Bloquear todos os sinais
        
        # ================================================================
        # CONVERTER SINAIS NUMEIA → EA
        # ================================================================
        response = self._convert_numeia_to_ea(all_signals)
        
        logger.info(f"[RESULT] {symbol}: {response['action']} (conf={response['confidence']:.2f})")
        
        return response
    
    def process_request(self, request_file: str):
        """
        Processar arquivo de request.
        
        Args:
            request_file: Caminho completo do arquivo AIRequest.*.json
        """
        try:
            # 1. Ler request
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            symbol = request_data.get('symbol', 'UNKNOWN')
            logger.info(f"[REQUEST] Processando {symbol} de {os.path.basename(request_file)}")
            
            # 2. Analisar usando Numeia (ASYNC)
            # Criar event loop se necessário
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            response_data = loop.run_until_complete(self.analyze_market(request_data))
            
            # 3. Escrever response
            response_file = request_file.replace("AIRequest", "AIResponse")
            with open(response_file, 'w') as f:
                # JSON compacto para facilitar parsing no EA
                json.dump(response_data, f, separators=(',', ':'))
            
            logger.info(f"[RESPONSE] {symbol} escrito em {os.path.basename(response_file)}")
            
            # 4. Deletar request (limpar)
            os.remove(request_file)
            logger.debug(f"[CLEANUP] {os.path.basename(request_file)} deletado")
            
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] JSON inválido em {request_file}: {e}")
            # Deletar arquivo corrompido
            os.remove(request_file)
        except Exception as e:
            logger.error(f"[ERROR] Falha ao processar {request_file}: {e}")
    
    def run(self):
        """
        Loop principal do servidor.
        """
        self.running = True
        logger.info("=" * 70)
        logger.info("[START] Servidor v3.0 Numeia iniciado. Aguardando requests...")
        logger.info("=" * 70)
        
        try:
            while self.running:
                # Buscar arquivos de request
                pattern = os.path.join(self.mt5_files_path, "AIRequest.*.json")
                request_files = glob.glob(pattern)
                
                if request_files:
                    logger.info(f"[SCAN] {len(request_files)} request(s) encontrado(s)")
                    
                    # Processar cada request
                    for request_file in request_files:
                        self.process_request(request_file)
                
                # Aguardar 1 segundo antes de próximo scan
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("[STOP] Servidor interrompido pelo usuário (Ctrl+C)")
        except Exception as e:
            logger.error(f"[ERROR] Erro fatal no servidor: {e}")
        finally:
            self.running = False
            logger.info("[STOP] Servidor finalizado")
    
    def stop(self):
        """
        Parar servidor.
        """
        logger.info("[STOP] Parando servidor...")
        self.running = False


def main():
    """
    Função principal.
    """
    import sys
    
    print("=" * 70)
    print("Samsung Global Market - Servidor v3.0 COM NUMEIA")
    print("Comunicação baseada em arquivos (File-Based IPC)")
    print("NumeiaTradingSystem v3.0 INTEGRADO")
    print("=" * 70)
    print()
    
    # Aceitar caminho como argumento de linha de comando
    if len(sys.argv) > 1:
        mt5_files_path = sys.argv[1]
        print(f"Caminho recebido como argumento: {mt5_files_path}")
    else:
        mt5_files_path = None  # Usar padrão
    
    # Criar servidor
    try:
        server = SamsungNumeiaServer(mt5_files_path=mt5_files_path)
    except Exception as e:
        logger.error(f"[ERRO CRÍTICO] Falha ao criar servidor: {e}")
        logger.error("[ERRO CRÍTICO] Sistema não pode iniciar sem NumeiaTradingSystem")
        return 1
    
    # Verificar se diretório existe
    if not os.path.exists(server.mt5_files_path):
        logger.error(f"ERRO: Diretório não encontrado: {server.mt5_files_path}")
        logger.error("Por favor, verifique o caminho e tente novamente.")
        return 1
    
    logger.info(f"Diretório de arquivos: {server.mt5_files_path}")
    logger.info("Pressione Ctrl+C para parar o servidor")
    print()
    
    # Iniciar servidor
    server.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

