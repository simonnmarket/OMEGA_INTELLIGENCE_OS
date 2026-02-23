# -*- coding: utf-8 -*-
"""
🚀 CRYPTO ORBITAL LAUNCH v3.1 - FORÇA MÁXIMA
Sistema completo, atualizado e integrado - MODO ÓRBITA

APROVAÇÃO: Conselho - Teste em Órbita (02-11-2025)
PROTOCOLO: Omega TIER-0 - LAUNCH IMMEDIATO
STATUS: PRODUÇÃO - NAVE GRANDIOSA EM ÓRBITA
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# ═════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE PATHS - CRÍTICO PARA IMPORTS
# ═════════════════════════════════════════════════════════════════════════

core_path = Path(__file__).parent.parent / 'Core'
modules_path = core_path / 'Modules'
strategies_path = core_path / 'Strategies'
crypto_strategies_path = strategies_path / 'Crypto'

# Adicionar todos os paths ao sys.path
sys.path.insert(0, str(core_path))
sys.path.insert(0, str(modules_path))
sys.path.insert(0, str(strategies_path))
sys.path.insert(0, str(crypto_strategies_path))

# ═════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE LOGGING
# ═════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [🚀 ORBITAL] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_orbital_launch.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════════════════
# IMPORTS DO SISTEMA COMPLETO
# ═════════════════════════════════════════════════════════════════════════

try:
    # CryptoModule científico
    from CryptoModule_Numeia_v3_0 import CryptoModule
    
    # ForexModule científico
    from ForexModule_Numeia_v3_0 import ForexModule
    
    # GoldModule científico
    from GoldModule_Numeia_v3_0 import GoldModule
    
    # FuturesModule científico
    from FuturesModule_Numeia_v3_0 import FuturesModule
    
    logger.info("[OK] Todos os módulos científicos importados")
    
    MODULES_LOADED = True
except ImportError as e:
    logger.error(f"[ERRO] Falha ao importar módulos: {e}")
    MODULES_LOADED = False
    import traceback
    traceback.print_exc()

try:
    # Engines Numeia antigas (para compatibilidade)
    from NumeiaTradingSystem_v3_0_FINAL import (
        HaleIntentionalityEngine,
        RossiDynamicKellyEngine,
        TanakaKalmanEngine,
        LeblancZKPEngine,
        MarketMastersPerfectionEngine
    )
    
    ENGINES_LOADED = True
    logger.info("[OK] Engines Numeia importados")
except ImportError as e:
    logger.warning(f"[AVISO] Engines Numeia antigas não disponíveis: {e}")
    ENGINES_LOADED = False

# ═════════════════════════════════════════════════════════════════════════
# SERVIDOR ORBITAL - SISTEMA COMPLETO
# ═════════════════════════════════════════════════════════════════════════

class CryptoOrbitalLaunch:
    """
    🚀 SERVIDOR ORBITAL - SISTEMA COMPLETO EM FORÇA MÁXIMA
    
    Integra:
    - 6 estratégias Crypto científicas
    - 3 estratégias Forex científicas
    - 1 estratégia Gold científica
    - 2 estratégias Futures científicas
    
    Total: 12 estratégias científicas peer-reviewed
    """
    
    def __init__(self, mt5_files_path=None):
        """
        Initialize Orbital Launch Server
        
        Args:
            mt5_files_path: Pasta para comunicação file-based com EA
        """
        # Pasta de comunicação
        if mt5_files_path is None:
            self.mt5_files_path = Path(__file__).parent.parent / 'mt5_files'
        else:
            self.mt5_files_path = Path(mt5_files_path)
        
        self.mt5_files_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("="*80)
        logger.info("🚀 CRYPTO ORBITAL LAUNCH v3.1 - NAVE GRANDIOSA")
        logger.info("="*80)
        
        # Inicializar módulos científicos
        if MODULES_LOADED:
            try:
                # CryptoModule - Capital €150k
                self.crypto_module = CryptoModule(allocated_capital=Decimal('150000'))
                logger.info("✅ CryptoModule: €150,000 | 6 estratégias")
                
                # ForexModule - Capital €100k
                self.forex_module = ForexModule(allocated_capital=Decimal('100000'))
                logger.info("✅ ForexModule: €100,000 | 3 estratégias")
                
                # GoldModule - Capital €75k
                self.gold_module = GoldModule(allocated_capital=Decimal('75000'))
                logger.info("✅ GoldModule: €75,000 | 1 estratégia")
                
                # FuturesModule - Capital €75k
                self.futures_module = FuturesModule(allocated_capital=Decimal('75000'))
                logger.info("✅ FuturesModule: €75,000 | 2 estratégias")
                
                logger.info("="*80)
                logger.info("TOTAL: 12 ESTRATÉGIAS CIENTÍFICAS ATIVAS")
                logger.info("="*80)
                
            except Exception as e:
                logger.error(f"[ERRO] Falha ao inicializar módulos: {e}")
                import traceback
                traceback.print_exc()
                self.crypto_module = None
                self.forex_module = None
                self.gold_module = None
                self.futures_module = None
        else:
            self.crypto_module = None
            self.forex_module = None
            self.gold_module = None
            self.futures_module = None
        
        logger.info("="*80)
        logger.info("🚀 SISTEMA PRONTO PARA ÓRBITA - AGUARDANDO COMANDOS")
        logger.info("="*80)
    
    def identify_asset(self, symbol: str) -> str:
        """
        Identificar tipo de ativo pelo símbolo
        
        Args:
            symbol: Símbolo do ativo (ex: BTCUSD, GBPUSD, XAUUSD)
            
        Returns:
            Tipo de ativo: 'crypto', 'forex', 'gold', 'futures' ou 'unknown'
        """
        symbol_upper = symbol.upper()
        
        # Crypto
        crypto_keywords = ['BTC', 'ETH', 'BNB', 'USDT', 'CRYPTO']
        if any(k in symbol_upper for k in crypto_keywords):
            return 'crypto'
        
        # Gold
        if 'XAU' in symbol_upper or 'GOLD' in symbol_upper:
            return 'gold'
        
        # Forex
        forex_keywords = ['EUR', 'GBP', 'USD', 'JPY', 'AUD', 'CHF', 'NZD', 'CAD']
        if any(k in symbol_upper for k in forex_keywords) and 'XAU' not in symbol_upper:
            return 'forex'
        
        # Futures
        futures_keywords = ['ES', 'NQ', 'YM', 'RTY', 'FUTURES']
        if any(k in symbol_upper for k in futures_keywords):
            return 'futures'
        
        return 'unknown'
    
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
            
            logger.info(f"[REQUEST] {symbol} recebido")
            
            # Identificar tipo de ativo
            asset_type = self.identify_asset(symbol)
            logger.info(f"[ASSET] {symbol} → {asset_type}")
            
            # Roteamento inteligente para módulo correto
            signals = []
            
            if asset_type == 'crypto' and self.crypto_module:
                logger.info("[ROUTE] → CryptoModule científico")
                try:
                    signals = self.crypto_module.analyze()
                    logger.info(f"[CRYPTO] {len(signals)} sinais científicos gerados")
                except Exception as e:
                    logger.error(f"[CRYPTO ERROR] {e}")
                    import traceback
                    traceback.print_exc()
            
            elif asset_type == 'forex' and self.forex_module:
                logger.info("[ROUTE] → ForexModule científico")
                try:
                    signals = self.forex_module.analyze()
                    logger.info(f"[FOREX] {len(signals)} sinais científicos gerados")
                except Exception as e:
                    logger.error(f"[FOREX ERROR] {e}")
                    import traceback
                    traceback.print_exc()
            
            elif asset_type == 'gold' and self.gold_module:
                logger.info("[ROUTE] → GoldModule científico")
                try:
                    signals = self.gold_module.analyze()
                    logger.info(f"[GOLD] {len(signals)} sinais científicos gerados")
                except Exception as e:
                    logger.error(f"[GOLD ERROR] {e}")
                    import traceback
                    traceback.print_exc()
            
            elif asset_type == 'futures' and self.futures_module:
                logger.info("[ROUTE] → FuturesModule científico")
                try:
                    signals = self.futures_module.analyze()
                    logger.info(f"[FUTURES] {len(signals)} sinais científicos gerados")
                except Exception as e:
                    logger.error(f"[FUTURES ERROR] {e}")
                    import traceback
                    traceback.print_exc()
            
            else:
                logger.warning(f"[UNKNOWN] {symbol} não mapeado para módulo")
                return self._create_hold_response(symbol, f"Asset type '{asset_type}' não suportado")
            
            # Processar sinais
            if not signals:
                logger.info(f"[NO SIGNALS] Nenhum sinal gerado para {symbol}")
                return self._create_hold_response(symbol, "Sem sinais aprovados pelos filtros")
            
            # Pegar melhor sinal (maior confidence)
            best_signal = max(signals, key=lambda s: s.confidence)
            
            logger.info("="*80)
            logger.info(f"🚀 SINAL CIENTÍFICO GERADO:")
            logger.info(f"   Asset: {symbol} ({asset_type})")
            logger.info(f"   Action: {best_signal.action}")
            logger.info(f"   Confidence: {best_signal.confidence:.4f}")
            logger.info(f"   Strategy: {best_signal.strategy_id}")
            logger.info(f"   Position Size: {best_signal.position_size}")
            logger.info("="*80)
            
            # Converter para formato EA
            return self._convert_signal_to_ea_format(best_signal, symbol)
        
        except Exception as e:
            logger.error(f"[ERROR] Erro ao processar requisição: {e}")
            import traceback
            traceback.print_exc()
            return self._create_hold_response("UNKNOWN", f"Erro: {str(e)}")
    
    def _convert_signal_to_ea_format(self, signal, requested_symbol):
        """Converte TradingSignalPerfeito para formato EA"""
        
        return {
            "symbol": requested_symbol,
            "action": signal.action,
            "confidence": float(signal.confidence),
            "reason": f"Scientific Module: {signal.strategy_id}",
            "timestamp": int(time.time()),
            "server_version": "3.1.0_ORBITAL_LAUNCH",
            "source": "scientific_module",
            "strategy_id": signal.strategy_id,
            "position_size": float(signal.position_size),
            "metadata": {
                "hale_score": getattr(signal, 'hale_intentionality_score', None),
                "kelly_fraction": getattr(signal, 'rossi_kelly_fraction', None),
                "zkp_proof": getattr(signal, 'leblanc_zkp_proof', None),
                "validation": getattr(signal, 'market_masters_validation', None),
                "scientific": True
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
            "server_version": "3.1.0_ORBITAL_LAUNCH"
        }
    
    def start(self):
        """Inicia servidor em loop contínuo"""
        request_folder = self.mt5_files_path / 'requests'
        response_folder = self.mt5_files_path / 'responses'
        
        request_folder.mkdir(parents=True, exist_ok=True)
        response_folder.mkdir(parents=True, exist_ok=True)
        
        logger.info("")
        logger.info("╔════════════════════════════════════════════════════════════════════════╗")
        logger.info("║  🚀 NAVE EM ÓRBITA - AGUARDANDO COMANDOS DO EA                       ║")
        logger.info("╚════════════════════════════════════════════════════════════════════════╝")
        logger.info("")
        
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
                        
                        logger.info(f"[RESPONSE] {response_file.name} → {response['action']} @ {response.get('confidence', 0):.4f}")
                        
                        # Remover requisição processada
                        request_file.unlink()
                    
                    except Exception as e:
                        logger.error(f"[ERROR] Erro ao processar {request_file}: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(2)
            
            except KeyboardInterrupt:
                logger.info("")
                logger.info("╔════════════════════════════════════════════════════════════════════════╗")
                logger.info("║  ⚠️  NAVE RETORNA À BASE - COMANDO MANUAL DE INTERRUPÇÃO             ║")
                logger.info("╚════════════════════════════════════════════════════════════════════════╝")
                logger.info("")
                break
            except Exception as e:
                logger.error(f"[ERROR] Erro no loop principal: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)

if __name__ == "__main__":
    # Criar servidor orbital
    server = CryptoOrbitalLaunch()
    
    # Iniciar loop contínuo
    server.start()

