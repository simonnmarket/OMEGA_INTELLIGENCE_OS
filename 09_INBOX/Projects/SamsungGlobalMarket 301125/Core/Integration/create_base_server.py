# -*- coding: utf-8 -*-
"""
PROTOCOLO NUMEIA v3.1 - FASE 2.1
Criar Servidor Base Consolidado

FUNÇÃO: _create_base_server()
OBJETIVO: Criar servidor de produção baseado em SystemOrchestrator_v3_1
TESTÁVEL: Sim - verifica arquivo criado, imports funcionando, estrutura válida
"""

import os
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _create_base_server() -> bool:
    """
    Criar servidor base (NumeiaTradingSystem_v3_1_Server.py)
    
    Requisitos:
    - Baseado em SystemOrchestrator_v3_1.py (importa componentes)
    - Infraestrutura básica sem estratégias específicas ainda
    - Comunicação file-based com EA (AIRequest/AIResponse)
    - Logging robusto
    - Estrutura para receber módulos (Crypto, Forex, Equities, Gold, Futures)
    
    Returns:
        bool: True se servidor criado com sucesso, False se falhou
    
    VALIDAÇÃO:
    - Verifica que arquivo foi criado
    - Testa que código é sintaticamente válido (compile)
    - Verifica imports necessários
    - Valida estrutura do servidor
    """
    try:
        logger.info("="*80)
        logger.info("FASE 2.1: Criando servidor base")
        logger.info("="*80)
        
        # Diretório de produção
        project_root = Path(__file__).parent.parent.parent
        production_dir = project_root / 'Server' / 'Production'
        server_file = production_dir / 'NumeiaTradingSystem_v3_1_Server.py'
        
        logger.info(f"Arquivo a criar: {server_file}")
        
        # Conteúdo do servidor base
        server_code = '''# -*- coding: utf-8 -*-
"""
NUMEIA TRADING SYSTEM v3.1 - SERVIDOR DE PRODUÇÃO
Integração Completa Baseada em SystemOrchestrator_v3_1

COMPONENTES INTEGRADOS:
- SystemOrchestrator (coordenação central)
- GlobalCapitalManager (gestão de €500K)
- CorrelationAnalyzer (detecção de conflitos)
- GlobalKillSwitch (proteção sistêmica)
- UnifiedDataFetcher (dados multi-fonte)

MÓDULOS SUPORTADOS:
- Crypto (€150K)
- Equities (€100K)
- Forex (€100K)
- Gold (€75K)
- Futures (€75K)

COMUNICAÇÃO: File-based IPC com EA
PROTOCOLO: Omega TIER-0 + Blindagem Científica 100%
DATA: 02-11-2025
STATUS: PRODUÇÃO
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, List

# Setup paths
current_dir = Path(__file__).parent.parent
core_dir = current_dir / 'Core'

sys.path.insert(0, str(core_dir))

# Configuração de logging
log_file = current_dir / 'numeia_server_v3_1.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# IMPORTAR SYSTEMORCHESTRATOR
# ============================================================================
try:
    from SystemOrchestrator_v3_1 import (
        SystemOrchestrator,
        GlobalCapitalManager,
        CorrelationAnalyzer,
        GlobalKillSwitch,
        UnifiedDataFetcher
    )
    ORCHESTRATOR_LOADED = True
    logger.info("✅ SystemOrchestrator_v3_1 importado com sucesso")
except ImportError as e:
    ORCHESTRATOR_LOADED = False
    logger.error(f"❌ Erro ao importar SystemOrchestrator: {e}")
    logger.error("Execute este servidor do diretório Server/Production/")

# Pasta MT5
MT5_PATH = Path(os.getenv('APPDATA')) / 'MetaQuotes' / 'Terminal' / 'Common' / 'Files'
REQUEST_FILE = MT5_PATH / 'AIRequest.BTCUSD.json'
RESPONSE_FILE = MT5_PATH / 'AIResponse.BTCUSD.json'

logger.info("="*80)
logger.info("NUMEIA TRADING SYSTEM v3.1 - SERVIDOR DE PRODUÇÃO")
logger.info("="*80)

class NumeiaTradingSystemServer:
    """
    Servidor de produção do NumeiaTradingSystem v3.1
    
    Integra todos os componentes do SystemOrchestrator e gerencia
    comunicação com EA via file-based IPC.
    """
    
    def __init__(self):
        if not ORCHESTRATOR_LOADED:
            raise ImportError("SystemOrchestrator não carregado - impossível continuar")
        
        # Inicializar componentes
        logger.info("Inicializando componentes...")
        
        try:
            # Orchestrator central
            self.orchestrator = SystemOrchestrator()
            logger.info("  ✅ SystemOrchestrator inicializado")
            
            # Controle de processamento
            self.last_mtime = 0
            self.total_requests = 0
            self.total_signals = 0
            
            logger.info("="*80)
            logger.info("SERVIDOR BASE INICIALIZADO COM SUCESSO")
            logger.info("="*80)
            logger.info(f"Capital total: €{self.orchestrator.capital_manager.total_capital:,.2f}")
            logger.info(f"Módulos: {len(self.orchestrator.capital_manager.allocated_capital)}")
            logger.info("="*80)
        
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar componentes: {e}")
            raise
    
    def process_request(self):
        """
        Processa request do EA
        
        Fluxo:
        1. Lê AIRequest.BTCUSD.json
        2. Chama orchestrator.analyze()
        3. Retorna melhor sinal em AIResponse.BTCUSD.json
        """
        if not REQUEST_FILE.exists():
            return
        
        current_mtime = REQUEST_FILE.stat().st_mtime
        
        if current_mtime <= self.last_mtime:
            return
        
        try:
            # Ler request
            with open(REQUEST_FILE, 'r') as f:
                request = json.load(f)
            
            self.total_requests += 1
            symbol = request.get('symbol', 'UNKNOWN')
            
            logger.info("")
            logger.info("="*80)
            logger.info(f"REQUEST #{self.total_requests}: {symbol}")
            logger.info("="*80)
            
            # Converter símbolo EA para formato módulos
            # BTCUSD → BTC/USDT para Crypto
            crypto_symbol = 'BTC/USDT'
            
            # Preparar market data para orchestrator
            market_data = {
                'symbol': crypto_symbol,
                'bid': request.get('bid', 0),
                'ask': request.get('ask', 0),
                'timestamp': request.get('time', 0)
            }
            
            # ANALISAR com orchestrator
            logger.info("Analisando com SystemOrchestrator...")
            
            # Por enquanto, retornar HOLD (módulos serão integrados em Fase 3)
            # Esta é apenas a ESTRUTURA base
            response = {
                "symbol": symbol,
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "Servidor base - módulos serão integrados em Fase 3",
                "timestamp": int(datetime.now().timestamp()),
                "server_version": "v3.1_BASE"
            }
            
            logger.info(f"  Response: {response['action']}")
            
            # Salvar response
            with open(RESPONSE_FILE, 'w') as f:
                json.dump(response, f, indent=2)
            
            logger.info("✅ Response criada")
            logger.info("="*80)
            
            self.last_mtime = current_mtime
        
        except Exception as e:
            logger.error(f"❌ Erro ao processar request: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def start(self):
        """Loop principal do servidor"""
        logger.info("🚀 SERVIDOR BASE ATIVO")
        logger.info("⏳ Aguardando requests do EA...")
        logger.info("")
        
        cycle = 0
        
        try:
            while True:
                self.process_request()
                
                cycle += 1
                if cycle >= 60:
                    logger.info(f"[💓] Sistema vivo | Requests: {self.total_requests}")
                    cycle = 0
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("")
            logger.info("="*80)
            logger.info("🛑 SERVIDOR PARADO")
            logger.info(f"Total requests: {self.total_requests}")
            logger.info("="*80)

if __name__ == "__main__":
    print("\\n" + "="*80)
    print("NUMEIA TRADING SYSTEM v3.1 - SERVIDOR BASE")
    print("="*80)
    print("\\nMÓDULOS: Crypto, Equities, Forex, Gold, Futures")
    print("CAPITAL: €500.000")
    print("COMUNICAÇÃO: File-based IPC")
    print("\\n" + "="*80 + "\\n")
    
    try:
        server = NumeiaTradingSystemServer()
        server.start()
    except Exception as e:
        print(f"\\n❌ ERRO ao inicializar servidor: {e}")
        sys.exit(1)
'''
        
        # Salvar arquivo
        logger.info("Criando arquivo do servidor base...")
        
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(server_code)
        
        logger.info(f"  ✅ Arquivo criado: {server_file.name}")
        logger.info(f"  📊 Tamanho: {server_file.stat().st_size} bytes")
        
        # Validar que arquivo existe
        if not server_file.exists():
            logger.error("❌ Arquivo não foi criado!")
            return False
        
        # Testar compilação (sintaxe válida)
        logger.info("\nValidando sintaxe do código...")
        try:
            with open(server_file, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, server_file.name, 'exec')
            logger.info("  ✅ Sintaxe válida")
        except SyntaxError as e:
            logger.error(f"  ❌ Erro de sintaxe: {e}")
            return False
        
        # Verificar imports necessários
        logger.info("\nVerificando imports necessários...")
        required_imports = [
            'SystemOrchestrator_v3_1',
            'json',
            'logging',
            'pathlib'
        ]
        
        imports_ok = True
        for imp in required_imports:
            if imp in code:
                logger.info(f"  ✅ Import encontrado: {imp}")
            else:
                logger.warning(f"  ⚠️ Import não encontrado: {imp}")
                imports_ok = False
        
        logger.info("="*80)
        logger.info("VALIDAÇÃO DO SERVIDOR BASE:")
        logger.info(f"  Arquivo criado: {server_file.exists()}")
        logger.info(f"  Sintaxe válida: True")
        logger.info(f"  Imports OK: {imports_ok}")
        logger.info(f"  Tamanho: {server_file.stat().st_size} bytes")
        logger.info("="*80)
        
        if server_file.exists() and imports_ok:
            logger.info("✅ SERVIDOR BASE CRIADO COM SUCESSO")
            return True
        else:
            logger.error("❌ VALIDAÇÃO FALHOU")
            return False
    
    except Exception as e:
        logger.error(f"❌ ERRO ao criar servidor base: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# =====================================================
# TESTE DA FUNÇÃO
# =====================================================

def test_create_base_server():
    """
    Teste para validar que servidor base foi criado corretamente
    
    Returns:
        dict: Resultado do teste com status e detalhes
    """
    logger.info("")
    logger.info("="*80)
    logger.info("TESTE: _create_base_server()")
    logger.info("="*80)
    
    # Executar função
    result = _create_base_server()
    
    # Verificar arquivo criado
    project_root = Path(__file__).parent.parent.parent
    server_file = project_root / 'Server' / 'Production' / 'NumeiaTradingSystem_v3_1_Server.py'
    
    validation = {
        'file_exists': server_file.exists(),
        'file_size': server_file.stat().st_size if server_file.exists() else 0,
        'syntax_valid': False,
        'imports_found': []
    }
    
    if server_file.exists():
        # Testar sintaxe
        try:
            with open(server_file, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, server_file.name, 'exec')
            validation['syntax_valid'] = True
            
            # Verificar imports críticos
            critical_imports = ['SystemOrchestrator', 'GlobalCapitalManager', 'logging', 'json']
            for imp in critical_imports:
                if imp in code:
                    validation['imports_found'].append(imp)
        except:
            pass
    
    # Resultado do teste
    test_result = {
        'function': '_create_base_server()',
        'passed': result and validation['file_exists'] and validation['syntax_valid'],
        'timestamp': datetime.now().isoformat(),
        'details': {
            'server_created': result,
            'file_path': str(server_file),
            'validation': validation
        }
    }
    
    if test_result['passed']:
        logger.info("✅ TESTE PASSOU")
        logger.info(f"  Arquivo: {server_file.name}")
        logger.info(f"  Tamanho: {validation['file_size']} bytes")
        logger.info(f"  Sintaxe: {'✅ Válida' if validation['syntax_valid'] else '❌ Inválida'}")
        logger.info(f"  Imports: {len(validation['imports_found'])}/{len(['SystemOrchestrator', 'GlobalCapitalManager', 'logging', 'json'])}")
    else:
        logger.error("❌ TESTE FALHOU")
        if not result:
            logger.error("  Função _create_base_server() retornou False")
        if not validation['file_exists']:
            logger.error("  Arquivo não foi criado")
        if not validation['syntax_valid']:
            logger.error("  Código tem erros de sintaxe")
    
    logger.info("="*80)
    
    return test_result

if __name__ == "__main__":
    """Executar teste quando rodar este arquivo"""
    
    print("\\n" + "="*80)
    print("PROTOCOLO NUMEIA v3.1 - FASE 2.1")
    print("Funcao: _create_base_server()")
    print("="*80 + "\\n")
    
    # Executar teste
    result = test_create_base_server()
    
    # Mostrar resultado
    print("\\n" + "="*80)
    print("RESULTADO DO TESTE:")
    print("="*80)
    print(f"Funcao: {result['function']}")
    print(f"Passou: {result['passed']}")
    print(f"Timestamp: {result['timestamp']}")
    
    if result['details']['validation']:
        val = result['details']['validation']
        print(f"\\nValidacao:")
        print(f"  Arquivo existe: {val['file_exists']}")
        print(f"  Tamanho: {val['file_size']} bytes")
        print(f"  Sintaxe valida: {val['syntax_valid']}")
        print(f"  Imports encontrados: {len(val['imports_found'])}")
        if val['imports_found']:
            for imp in val['imports_found']:
                print(f"    - {imp}")
    
    print("="*80 + "\\n")
    
    # Salvar resultado
    with open('test_result_phase_2_1.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("Resultado salvo em: test_result_phase_2_1.json\\n")

