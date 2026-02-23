#!/usr/bin/env python3
"""
TESTE DE INTEGRAÇÃO MT5 - AURORA v5.1
======================================
Script para testar a conexão e envio de ordens ao MetaTrader 5

Uso:
    python test_mt5_integration.py
    python test_mt5_integration.py --login 123456 --password senha --server broker
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("MT5_TEST")

# Importar executor MT5
try:
    sys.path.insert(0, str(Path(__file__).parent / "04-Infraestrutura"))
    from mt5_executor import MT5Executor
    MT5_AVAILABLE = True
except ImportError as e:
    MT5_AVAILABLE = False
    logger.error(f"❌ Não foi possível importar MT5Executor: {str(e)}")
    logger.error("   Certifique-se de que o arquivo 04-Infraestrutura/mt5_executor.py existe")
    sys.exit(1)


def test_connection(login=None, password=None, server=None):
    """Testa conexão com MT5"""
    logger.info("=" * 60)
    logger.info("🔌 TESTE DE CONEXÃO MT5")
    logger.info("=" * 60)
    
    executor = MT5Executor(login=login, password=password, server=server)
    
    if executor.connected:
        logger.info("✅ CONEXÃO ESTABELECIDA COM SUCESSO")
        return executor
    else:
        logger.error("❌ FALHA NA CONEXÃO")
        logger.error("   Verifique:")
        logger.error("   1. MetaTrader 5 está instalado e rodando")
        logger.error("   2. Credenciais corretas (se fornecidas)")
        logger.error("   3. Terminal MT5 está aberto")
        return None


def test_symbol_info(executor: MT5Executor, symbol: str = "EURUSD"):
    """Testa obtenção de informações de símbolo"""
    logger.info("=" * 60)
    logger.info(f"📊 TESTE DE INFORMAÇÕES DO SÍMBOLO: {symbol}")
    logger.info("=" * 60)
    
    symbol_info = executor.get_symbol_info(symbol)
    
    if symbol_info:
        logger.info("✅ INFORMAÇÕES OBTIDAS COM SUCESSO")
        logger.info(f"   Nome: {symbol_info.get('name')}")
        logger.info(f"   Descrição: {symbol_info.get('description')}")
        logger.info(f"   Bid: {symbol_info.get('bid')}")
        logger.info(f"   Ask: {symbol_info.get('ask')}")
        logger.info(f"   Spread: {symbol_info.get('spread')}")
        logger.info(f"   Volume Min: {symbol_info.get('volume_min')}")
        logger.info(f"   Volume Max: {symbol_info.get('volume_max')}")
        return symbol_info
    else:
        logger.error(f"❌ FALHA AO OBTER INFORMAÇÕES DE {symbol}")
        logger.error("   Verifique se o símbolo está disponível no seu broker")
        return None


def test_positions(executor: MT5Executor):
    """Testa obtenção de posições abertas"""
    logger.info("=" * 60)
    logger.info("📈 TESTE DE POSIÇÕES ABERTAS")
    logger.info("=" * 60)
    
    positions = executor.get_positions()
    
    if positions is not None:
        logger.info(f"✅ {len(positions)} posição(ões) aberta(s)")
        for pos in positions:
            logger.info(f"   Ticket: {pos['ticket']} | {pos['symbol']} | {pos['type']} | Volume: {pos['volume']} | Profit: {pos['profit']:.2f}")
        return positions
    else:
        logger.warning("⚠️  Nenhuma posição aberta ou erro ao obter posições")
        return []


def test_statistics(executor: MT5Executor):
    """Testa obtenção de estatísticas"""
    logger.info("=" * 60)
    logger.info("📊 TESTE DE ESTATÍSTICAS")
    logger.info("=" * 60)
    
    stats = executor.get_statistics()
    
    logger.info("✅ ESTATÍSTICAS OBTIDAS:")
    logger.info(f"   Conectado: {stats['connected']}")
    logger.info(f"   Ordens Enviadas: {stats['orders_sent']}")
    logger.info(f"   Ordens Falhadas: {stats['orders_failed']}")
    logger.info(f"   Taxa de Sucesso: {stats['success_rate']:.2f}%")
    logger.info(f"   Posições Abertas: {stats['positions_open']}")
    logger.info(f"   Lucro Total: {stats['total_profit']:.2f}")
    if stats.get('account_balance'):
        logger.info(f"   Saldo: {stats['account_balance']:.2f}")
        logger.info(f"   Equity: {stats['account_equity']:.2f}")
    
    return stats


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Teste de integração MT5 - Aurora v5.1")
    parser.add_argument("--login", type=int, help="Número da conta MT5")
    parser.add_argument("--password", type=str, help="Senha da conta MT5")
    parser.add_argument("--server", type=str, help="Servidor broker")
    parser.add_argument("--symbol", type=str, default="EURUSD", help="Símbolo para teste (padrão: EURUSD)")
    parser.add_argument("--skip-connection", action="store_true", help="Pular teste de conexão")
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("🚀 AURORA v5.1 - TESTE DE INTEGRAÇÃO MT5")
    logger.info("=" * 60)
    logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    if not MT5_AVAILABLE:
        logger.error("❌ MetaTrader5 não disponível")
        logger.error("   Execute: pip install MetaTrader5")
        return 1
    
    # Teste 1: Conexão
    if not args.skip_connection:
        executor = test_connection(args.login, args.password, args.server)
        if not executor:
            return 1
    else:
        logger.info("⏭️  Pulando teste de conexão")
        executor = MT5Executor(login=args.login, password=args.password, server=args.server)
        if not executor.connected:
            logger.error("❌ Não foi possível conectar ao MT5")
            return 1
    
    logger.info("")
    
    # Teste 2: Informações do símbolo
    symbol_info = test_symbol_info(executor, args.symbol)
    if not symbol_info:
        logger.warning("⚠️  Continuando apesar do erro...")
    
    logger.info("")
    
    # Teste 3: Posições abertas
    positions = test_positions(executor)
    
    logger.info("")
    
    # Teste 4: Estatísticas
    stats = test_statistics(executor)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ TESTE DE INTEGRAÇÃO CONCLUÍDO")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📝 PRÓXIMOS PASSOS:")
    logger.info("   1. Se todos os testes passaram, a integração está funcionando")
    logger.info("   2. Execute o sistema Aurora para começar a receber ordens")
    logger.info("   3. Monitore as posições no terminal MT5")
    logger.info("")
    
    # Desconectar
    executor.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

