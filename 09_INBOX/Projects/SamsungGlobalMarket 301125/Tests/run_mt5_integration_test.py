# -*- coding: utf-8 -*-
"""
TESTE DE INTEGRAÇÃO MT5 - SAMSUNG GLOBAL MARKET
STATUS: PRODUÇÃO TIER-0
DATA: 2025-01-27
FUNÇÃO: Validar comunicação Python ↔ MetaTrader 5
"""

import time
import logging
from MT5_Connector import MT5_Connector, create_signal_message
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def on_execution_report_received(report):
    """Callback quando relatório de execução é recebido"""
    print("\n" + "="*100)
    print("[CALLBACK] RELATÓRIO DE EXECUÇÃO RECEBIDO")
    print("="*100)
    print(f"Signal ID: {report.get('original_signal_id')}")
    print(f"Status: {report.get('status')}")
    print(f"Order: {report.get('order_ticket')}")
    print(f"Symbol: {report.get('symbol')}")
    print(f"Price: {report.get('price')}")
    print("="*100 + "\n")

def on_connection_change(connected, address):
    """Callback quando status de conexão muda"""
    if connected:
        print(f"\n✅ [EVENTO] EA conectado de {address}\n")
    else:
        print(f"\n⚠️ [EVENTO] EA desconectado\n")

def run_integration_test():
    """Executa teste completo de integração"""
    
    print("\n" + "="*100)
    print("🧪 TESTE DE INTEGRAÇÃO SAMSUNG GLOBAL MARKET ↔ METATRADER 5")
    print("="*100 + "\n")
    
    # Criar conector
    connector = MT5_Connector(host='127.0.0.1', port=5555)
    
    # Registrar callbacks
    connector.on_execution_report = on_execution_report_received
    connector.on_connection_change = on_connection_change
    
    # Iniciar servidor
    print("[PASSO 1] Iniciando servidor de socket...\n")
    connector.start_server()
    
    print("[PASSO 2] Aguardando conexão do EA...")
    print("[INFO] Por favor, inicie o EA 'SamsungGlobalMarket_EA' no MetaTrader 5")
    print("[INFO] Aguardando até 60 segundos...\n")
    
    # Aguardar conexão
    timeout = 60
    start_time = time.time()
    
    while not connector.is_connected and (time.time() - start_time) < timeout:
        time.sleep(1)
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0 and elapsed > 0:
            print(f"[INFO] Aguardando... ({elapsed}s/{timeout}s)")
    
    if not connector.is_connected:
        print("\n❌ [FALHA] EA não conectou em 60 segundos")
        print("[INFO] Certifique-se de que:")
        print("   1. MetaTrader 5 está aberto")
        print("   2. EA 'SamsungGlobalMarket_EA' está compilado")
        print("   3. EA está anexado a um gráfico")
        print("   4. Trading automático está habilitado\n")
        connector.stop_server()
        return False
    
    print("\n[PASSO 3] Enviando sinais de teste...\n")
    
    # TESTE 1: Sinal de compra EUR/USD
    print("[TESTE 1] Enviando sinal BUY EURUSD...")
    signal1 = create_signal_message(
        signal_id="TEST_BUY_EURUSD_001",
        symbol="EURUSD",
        action="BUY",
        volume=0.01,  # Micro lote
        stop_loss=1.0800,
        take_profit=1.1000,
        comment="Test Buy from Python",
        magic_number=12345
    )
    
    success1 = connector.send_signal(signal1)
    print(f"   Resultado: {'✅ Enviado' if success1 else '❌ Falhou'}\n")
    
    time.sleep(2)
    
    # TESTE 2: Sinal de venda GBP/USD
    print("[TESTE 2] Enviando sinal SELL GBPUSD...")
    signal2 = create_signal_message(
        signal_id="TEST_SELL_GBPUSD_002",
        symbol="GBPUSD",
        action="SELL",
        volume=0.01,
        stop_loss=1.2700,
        take_profit=1.2500,
        comment="Test Sell from Python"
    )
    
    success2 = connector.send_signal(signal2)
    print(f"   Resultado: {'✅ Enviado' if success2 else '❌ Falhou'}\n")
    
    time.sleep(2)
    
    # TESTE 3: Sinal de compra XAUUSD (Ouro)
    print("[TESTE 3] Enviando sinal BUY XAUUSD (Gold)...")
    signal3 = create_signal_message(
        signal_id="TEST_BUY_XAUUSD_003",
        symbol="XAUUSD",
        action="BUY",
        volume=0.01,
        stop_loss=1900.00,
        take_profit=2000.00,
        comment="Test Gold from Python"
    )
    
    success3 = connector.send_signal(signal3)
    print(f"   Resultado: {'✅ Enviado' if success3 else '❌ Falhou'}\n")
    
    # Aguardar relatórios
    print("[PASSO 4] Aguardando relatórios de execução (10 segundos)...\n")
    time.sleep(10)
    
    # Verificar relatórios recebidos
    reports = connector.get_pending_reports()
    
    print(f"\n[PASSO 5] Processando relatórios ({len(reports)} recebidos)...\n")
    
    for idx, report in enumerate(reports, 1):
        print(f"Relatório {idx}:")
        print(f"   Signal ID: {report.get('original_signal_id')}")
        print(f"   Status: {report.get('status')}")
        print(f"   Order: {report.get('order_ticket')}")
        print(f"   Error: {report.get('error_description', 'None')}\n")
    
    # Estatísticas finais
    print("\n[PASSO 6] Estatísticas da conexão:\n")
    stats = connector.get_statistics()
    
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Resultado final
    print("\n" + "="*100)
    print("📊 RESULTADO DO TESTE DE INTEGRAÇÃO")
    print("="*100)
    
    if len(reports) >= 2:  # Pelo menos 2 de 3 sinais respondidos
        print("✅ TESTE BEM-SUCEDIDO!")
        print("   - Comunicação Python ↔ MT5 funcional")
        print("   - Sinais enviados corretamente")
        print("   - Relatórios recebidos")
        result = True
    else:
        print("⚠️ TESTE PARCIAL")
        print("   - Comunicação estabelecida")
        print("   - Poucos relatórios recebidos (verificar EA)")
        result = False
    
    print("="*100 + "\n")
    
    # Parar servidor
    print("[FINALIZANDO] Parando servidor...\n")
    connector.stop_server()
    
    return result

if __name__ == "__main__":
    try:
        success = run_integration_test()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Teste interrompido pelo usuário\n")
        exit(2)
    except Exception as e:
        print(f"\n❌ [ERRO] {type(e).__name__}: {str(e)}\n")
        exit(3)

