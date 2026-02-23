"""
Samsung Global Market - Servidor de Análise ML v3.1 COM NUMEIA (CORRIGIDO)
COMUNICAÇÃO FILE-BASED IPC - FORMATO EA COMPATÍVEL
INTEGRAÇÃO SEGURA: NumeiaTradingSystem v3.0

PROTOCOLO: Omega TIER-0 - Correção Crítica
DATA: 2025-10-30
STATUS: PRODUÇÃO - CORRIGIDO E TESTADO
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
from typing import Dict, List, Any

# Adicionar diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Core"))

# ============================================================================
# IMPORTS DO NUMEIA TRADING SYSTEM - VERSAO CORRIGIDA
# ============================================================================
try:
    from NumeiaTradingSystem_v3_0_FINAL import (
        HaleIntentionalityEngine,
        RossiDynamicKellyEngine,
        TanakaKalmanEngine, 
        LeblancZKPEngine,
        MarketMastersPerfectionEngine,
        OilStrategyProvenV3,
        GoldenStrategyFuturesV3,
        # ✅ CORREÇÃO: Importar a classe principal também
        NumeiaTradingSystem
    )
    NUMEIA_LOADED = True
    logger_init_msg = "[OK] NumeiaTradingSystem v3.0 importado com sucesso"
except ImportError as e:
    NUMEIA_LOADED = False
    logger_init_msg = f"[ERRO] Falha ao importar NumeiaTradingSystem: {e}"
    # ❌ SE FALHAR, SISTEMA NÃO PODE OPERAR
    raise

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Log de inicialização
logger.info("=" * 70)
logger.info("SAMSUNG GLOBAL MARKET - SERVIDOR V3.1 CORRIGIDO")
logger.info("=" * 70)
logger.info(logger_init_msg)
logger.info("=" * 70)


class SamsungNumeiaServerV31:
    """
    Servidor v3.1 CORRIGIDO - Integração segura com NumeiaTradingSystem.
    Formato 100% compatível com EA existente.
    """
    
    def __init__(self, mt5_files_path=None):
        """
        Inicializar servidor v3.1 corrigido.
        """
        if mt5_files_path is None:
            mt5_files_path = os.path.join(
                os.getenv('APPDATA'),
                'MetaQuotes', 'Terminal', 'Common', 'Files'
            )
        
        self.mt5_files_path = mt5_files_path
        self.running = False
        
        # ✅ VALIDAÇÃO CRÍTICA: Numeia deve estar carregado
        if not NUMEIA_LOADED:
            logger.error("[ERRO CRÍTICO] NumeiaTradingSystem não carregado!")
            raise ImportError("NumeiaTradingSystem é obrigatório")
        
        # ================================================================
        # INICIALIZAR NUMEIA TRADING SYSTEM - FORMA CORRETA
        # ================================================================
        try:
            logger.info("[INIT] Inicializando NumeiaTradingSystem...")
            
            # ✅ CORREÇÃO: Usar o sistema principal do Numeia
            # Passar capital_base padrão
            self.numeia_system = NumeiaTradingSystem(capital_base=Decimal('10000.0'))
            logger.info("[OK] NumeiaTradingSystem inicializado")
            
            # ✅ CORREÇÃO: Acessar estratégias através do sistema
            self.strategies = self.numeia_system.strategies_v3
            logger.info(f"[OK] {len(self.strategies)} estratégias carregadas")
            
            # Log das estratégias ativas
            for name, strategy in self.strategies.items():
                logger.info(f"  [STRATEGY] {name}: {strategy.strategy_id}")
            
            logger.info("=" * 70)
            logger.info("[SUCCESS] Servidor v3.1 CORRIGIDO - Pronto para operar")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"[ERRO CRÍTICO] Falha na inicialização: {e}")
            raise
    
    def _convert_ea_to_numeia(self, request_data: Dict) -> Dict:
        """
        ✅ CORREÇÃO: Converter dados EA → Numeia de forma segura.
        """
        symbol = request_data.get('symbol', 'UNKNOWN')
        
        # ✅ CORREÇÃO: Criar estrutura mínima mas compatível
        market_data = {
            'symbol': symbol,
            'prices': [float(request_data.get('bid', 0.0))],
            'bid': float(request_data.get('bid', 0.0)),
            'ask': float(request_data.get('ask', 0.0)),
            'spread': float(request_data.get('spread', 0.0)),
            'timestamp': request_data.get('time', int(time.time())),
            'macro': {
                'geo_risk': 0.3,   # Default - será melhorado depois
                'dxy': 100.0,      # Default  
                'inflation': 0.02  # Default
            }
        }
        
        return market_data
    
    def _filter_signals_by_asset(self, signals: List, requested_symbol: str) -> List:
        """
        ✅ CRÍTICO v3.2: Filtrar sinais apenas para o asset solicitado.
        
        Args:
            signals: Lista de sinais do Numeia
            requested_symbol: Símbolo solicitado pelo EA (ex: GBPUSD)
        
        Returns:
            Lista filtrada de sinais compatíveis com o símbolo
        """
        if not signals:
            return []
        
        filtered = []
        
        # Mapeamento de símbolos compatíveis
        SYMBOL_MAPPING = {
            'GBPUSD': ['GBPUSD', 'GBP/USD', 'GBP_USD'],
            'EURUSD': ['EURUSD', 'EUR/USD', 'EUR_USD'],
            'USDJPY': ['USDJPY', 'USD/JPY', 'USD_JPY'],
            # Adicionar mais conforme necessário
        }
        
        # Obter lista de assets compatíveis
        compatible_assets = SYMBOL_MAPPING.get(requested_symbol, [requested_symbol])
        
        for signal in signals:
            signal_asset = getattr(signal, 'asset', '')
            
            # Verificar se asset do sinal é compatível
            if signal_asset in compatible_assets:
                filtered.append(signal)
                logger.info(f"  [MATCH] Sinal {signal_asset} compatível com {requested_symbol}")
            else:
                logger.warning(f"  [SKIP] Sinal {signal_asset} NÃO compatível com {requested_symbol} - ignorado")
        
        return filtered
    
    def _convert_numeia_to_ea(self, signals: List, requested_symbol: str = None) -> Dict:
        """
        ✅ CORREÇÃO CRÍTICA: Converter Numeia → EA de forma ROBUSTA.
        """
        if not signals:
            # ✅ SEM SINAIS: HOLD com alta confiança (filtros ativos)
            return {
                "action": "HOLD",
                "confidence": 0.90,
                "reason": "Nenhum sinal - filtros Numeia ativos",
                "timestamp": int(time.time()),
                "server_version": "3.1.0_NUMEIA_CORRIGIDO"
            }
        
        # ✅ CORREÇÃO: Usar primeiro sinal de forma segura
        signal = signals[0]
        
        # ✅ CORREÇÃO: Acessar atributos de forma segura
        try:
            action = getattr(signal, 'action', 'HOLD')
            confidence = float(getattr(signal, 'confidence', Decimal('0.5')))
            asset = getattr(signal, 'asset', 'UNKNOWN')
            strategy_id = getattr(signal, 'strategy_id', 'UNKNOWN')
            
            # ✅ CORREÇÃO: Risk score com fallback
            risk_score = float(getattr(signal, 'risk_score', Decimal('0.3')))
            
            # ✅ CORREÇÃO: ZKP proof opcional
            zkp_proof = getattr(signal, 'leblanc_zkp_proof', None)
            
        except (AttributeError, ValueError) as e:
            logger.error(f"[ERRO] Falha ao acessar atributos do sinal: {e}")
            return {
                "action": "HOLD", 
                "confidence": 0.0,
                "reason": f"Erro no sinal: {e}",
                "timestamp": int(time.time()),
                "server_version": "3.1.0_ERROR"
            }
        
        # ✅ FORMATO 100% COMPATÍVEL COM EA
        # ✅ CRÍTICO v3.2: Usar símbolo solicitado, não asset do sinal
        response = {
            "action": action,
            "confidence": confidence,
            "risk_score": risk_score,
            "reason": f"Sinal Numeia: {strategy_id}",
            "timestamp": int(time.time()),
            "server_version": "3.2.0_ASSET_FILTER",
            "source": "numeia",
            "strategy_id": strategy_id,
            "symbol": requested_symbol if requested_symbol else asset  # ✅ Usar símbolo correto
        }
        
        # ✅ Adicionar ZKP proof apenas se existir
        if zkp_proof:
            response["leblanc_zkp_proof"] = zkp_proof
        
        # Log do sinal
        logger.info("=" * 50)
        logger.info(f"[SINAL] {action} {asset} (conf: {confidence:.1%})")
        logger.info(f"[SINAL] Estratégia: {strategy_id}")
        logger.info("=" * 50)
        
        return response
    
    async def analyze_market(self, request_data: Dict) -> Dict:
        """
        ✅ CORREÇÃO: Análise de mercado robusta com tratamento de erro.
        ✅ CRÍTICO v3.2: Filtro de asset para prevenir mismatch
        """
        symbol = request_data.get('symbol', 'UNKNOWN')
        
        logger.info(f"[ANALYZE] Analisando {symbol} com Numeia...")
        
        try:
            # 1. Converter dados
            market_data = self._convert_ea_to_numeia(request_data)
            
            # 2. Executar estratégias do Numeia
            all_signals = []
            
            for name, strategy in self.strategies.items():
                try:
                    # ✅ CORREÇÃO: Executar estratégia de forma assíncrona
                    signals = await strategy.analyze(market_data)
                    
                    if signals and len(signals) > 0:
                        all_signals.extend(signals)
                        logger.info(f"  [SIGNAL] {name}: {len(signals)} sinal(is)")
                        
                except Exception as e:
                    logger.warning(f"  [AVISO] Estratégia {name} falhou: {e}")
                    continue
            
            # ✅ CRÍTICO v3.2: FILTRAR SINAIS POR ASSET
            filtered_signals = self._filter_signals_by_asset(all_signals, symbol)
            
            if len(all_signals) != len(filtered_signals):
                logger.warning(f"[FILTRO] {len(all_signals) - len(filtered_signals)} sinal(is) filtrado(s) - asset incompatível")
            
            # 3. Converter sinais para formato EA
            response = self._convert_numeia_to_ea(filtered_signals, symbol)
            
            logger.info(f"[RESULT] {symbol}: {response['action']} (conf: {response['confidence']:.1%})")
            
            return response
            
        except Exception as e:
            logger.error(f"[ERRO] Falha na análise: {e}")
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": f"Erro na análise: {e}",
                "timestamp": int(time.time()),
                "server_version": "3.1.0_ERROR"
            }
    
    def process_request(self, request_file: str):
        """
        ✅ CORREÇÃO: Processamento de request com tratamento robusto.
        """
        try:
            # Ler request
            with open(request_file, 'r') as f:
                request_data = json.load(f)
            
            symbol = request_data.get('symbol', 'UNKNOWN')
            logger.info(f"[REQUEST] Processando {symbol}")
            
            # Executar análise (async)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            response_data = loop.run_until_complete(
                self.analyze_market(request_data)
            )
            
            # Escrever response
            response_file = request_file.replace("AIRequest", "AIResponse")
            with open(response_file, 'w') as f:
                json.dump(response_data, f, separators=(',', ':'))
            
            logger.info(f"[RESPONSE] {symbol} -> {response_data['action']}")
            
            # Limpar request
            os.remove(request_file)
            
        except Exception as e:
            logger.error(f"[ERROR] Falha no processamento: {e}")
            # Não deletar request em caso de erro - permite retry
    
    def run(self):
        """
        Loop principal corrigido.
        """
        self.running = True
        logger.info("=" * 70)
        logger.info("[START] Servidor v3.1 CORRIGIDO iniciado")
        logger.info("=" * 70)
        
        try:
            while self.running:
                # Buscar requests
                pattern = os.path.join(self.mt5_files_path, "AIRequest.*.json")
                request_files = glob.glob(pattern)
                
                if request_files:
                    for request_file in request_files:
                        self.process_request(request_file)
                
                time.sleep(1)  # 1 segundo entre scans
                
        except KeyboardInterrupt:
            logger.info("[STOP] Interrompido pelo usuário")
        except Exception as e:
            logger.error(f"[ERROR] Erro fatal: {e}")
        finally:
            self.running = False
            logger.info("[STOP] Servidor finalizado")


def main():
    """
    Função principal corrigida.
    """
    print("=" * 70)
    print("Samsung Global Market - Servidor v3.1 CORRIGIDO")
    print("NumeiaTradingSystem v3.0 - INTEGRAÇÃO SEGURA")
    print("=" * 70)
    print()
    
    # Aceitar caminho como argumento
    if len(sys.argv) > 1:
        mt5_files_path = sys.argv[1]
    else:
        mt5_files_path = None
    
    try:
        # ✅ CORREÇÃO: Passar caminho para servidor
        server = SamsungNumeiaServerV31(mt5_files_path=mt5_files_path)
        
        # Verificar se diretório existe
        if not os.path.exists(server.mt5_files_path):
            logger.error(f"ERRO: Diretório não encontrado: {server.mt5_files_path}")
            return 1
        
        logger.info(f"Diretório MT5: {server.mt5_files_path}")
        logger.info("Pressione Ctrl+C para parar")
        print()
        
        # Iniciar servidor
        server.run()
        return 0
        
    except Exception as e:
        logger.error(f"[ERRO] Sistema não pode iniciar: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

