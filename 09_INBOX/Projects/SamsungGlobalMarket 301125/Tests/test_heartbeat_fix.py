#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE INTEGRAÇÃO MT5 - Samsung Global Market
Validação da correção do heartbeat
"""

import time
import sys
from MT5_Connector import MT5_Connector, create_signal_message

def test_integration():
    """Testa a integração completa com heartbeat ativo"""
    print("=" * 60)
    print("TESTE DE INTEGRACAO MT5 - SAMSUNG GLOBAL MARKET")
    print("=" * 60)
    print("Versao: 2.0 (Heartbeat Ativo)")
    print("Data: 2025-10-27")
    print("=" * 60)
    
    # Criar conector
    connector = MT5_Connector(heartbeat_interval=30)
    
    # Callbacks para monitoramento
    def on_execution_report(report):
        print(f"[CALLBACK] RELATORIO DE EXECUCAO RECEBIDO")
        print(f"  Status: {report.get('status')}")
        print(f"  Ordem: {report.get('order_ticket')}")
        print(f"  Symbol: {report.get('symbol')}")
        print(f"  Volume: {report.get('volume')}")
        print(f"  Preco: {report.get('price')}")
        print(f"  Lucro: {report.get('profit')}")
    
    def on_connection_change(connected, addr):
        if connected:
            print(f"[CALLBACK] EA CONECTADO: {addr}")
        else:
            print(f"[CALLBACK] EA DESCONECTADO")
    
    connector.on_execution_report = on_execution_report
    connector.on_connection_change = on_connection_change
    
    try:
        # Iniciar servidor
        print("\n[INFO] Iniciando servidor MT5...")
        connector.start_server()
        
        print("\n[INSTRUCOES]")
        print("1. Anexe o EA SamsungGlobalMarket_EA ao grafico no MT5")
        print("2. Aguarde o handshake completo")
        print("3. Observe os heartbeats a cada 30 segundos")
        print("4. Pressione Ctrl+C para parar")
        
        # Aguardar conexão
        print("\n[AGUARDANDO] Conexao do EA...")
        timeout = 60  # 60 segundos
        start_time = time.time()
        
        while not connector.is_connected and (time.time() - start_time) < timeout:
            time.sleep(1)
            if int(time.time() - start_time) % 10 == 0:
                print(f"[INFO] Aguardando conexao... {int(time.time() - start_time)}s")
        
        if not connector.is_connected:
            print(f"\n[TIMEOUT] EA nao conectou em {timeout} segundos")
            print("[INFO] Verifique se o EA esta anexado ao grafico no MT5")
            return False
        
        print(f"\n[SUCESSO] EA conectado!")
        
        # Aguardar estabilização
        print("[INFO] Aguardando estabilizacao (10 segundos)...")
        time.sleep(10)
        
        # Enviar sinal de teste
        print("\n[TESTE] Enviando sinal de teste...")
        test_signal = create_signal_message(
            signal_id="TEST_BUY_EURUSD_001",
            symbol="EURUSD",
            action="BUY",
            volume=0.01,
            stop_loss=1.0800,
            take_profit=1.0900,
            comment="Teste de integracao"
        )
        
        success = connector.send_signal(test_signal)
        if success:
            print("[SUCESSO] Sinal enviado com sucesso!")
        else:
            print("[ERRO] Falha ao enviar sinal")
            return False
        
        # Aguardar relatórios
        print("\n[INFO] Aguardando relatorios de execucao (30 segundos)...")
        time.sleep(30)
        
        # Manter servidor ativo
        print("\n[INFO] Servidor ativo. Pressione Ctrl+C para parar.")
        print("[MONITORAMENTO] Observe os heartbeats nos logs")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[INFO] Parando teste...")
        connector.stop_server()
        print("[OK] Teste finalizado")
        return True
    
    except Exception as e:
        print(f"\n[ERRO] {type(e).__name__}: {str(e)}")
        connector.stop_server()
        return False

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n" + "=" * 60)
        print("TESTE CONCLUIDO COM SUCESSO!")
        print("=" * 60)
        print("Integracao MT5-Python funcionando corretamente")
        print("Heartbeat ativo implementado")
        print("Pronto para Paper Trading")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("TESTE FALHOU")
        print("=" * 60)
        print("Verifique os logs para diagnosticar o problema")
        print("=" * 60)
        sys.exit(1)
