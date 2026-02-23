# -*- coding: utf-8 -*-
"""
SERVIDOR MT5 SIMPLES - SAMSUNG GLOBAL MARKET
Inicia servidor e aguarda EA, enviando sinais de teste
"""

import sys
import time
from MT5_Connector import MT5_Connector, create_signal_message

def main():
    print("\n" + "="*80)
    print("[MT5 SERVER] SAMSUNG GLOBAL MARKET - SERVIDOR ATIVO")
    print("="*80 + "\n")
    
    # Criar e iniciar conector
    connector = MT5_Connector(host='127.0.0.1', port=5555)
    
    # Callback para conexão
    def on_connection(connected, address):
        if connected:
            print(f"\n[OK] EA conectado de {address}")
            print("[INFO] Conexao estavel. Aguardando 5 segundos...")
            print("[INFO] Entao enviarei 3 sinais de teste.\n")
        else:
            print(f"\n[AVISO] EA desconectado\n")
    
    # Callback para relatórios
    def on_report(report):
        print(f"\n[RELATORIO] {report.get('status')} - Order {report.get('order_ticket')}")
    
    connector.on_connection_change = on_connection
    connector.on_execution_report = on_report
    
    # Iniciar servidor
    connector.start_server()
    
    print("[INFO] Servidor iniciado em 127.0.0.1:5555")
    print("[INFO] Aguardando conexao do EA...")
    print("[INFO] Por favor, anexe o EA no MT5 se ainda nao fez.\n")
    
    try:
        # Aguardar EA conectar
        timeout = 60
        start = time.time()
        
        while not connector.is_connected and (time.time() - start) < timeout:
            time.sleep(1)
        
        if not connector.is_connected:
            print("\n[TIMEOUT] EA nao conectou em 60 segundos.")
            print("[INFO] Verifique se o EA esta anexado ao grafico no MT5.\n")
            return
        
        # EA conectado - aguardar estabilização
        print("\n[OK] EA conectado! Aguardando estabilizacao (5s)...\n")
        time.sleep(5)
        
        # Enviar sinais de teste
        print("[TESTE] Enviando 3 sinais de teste...\n")
        
        signals = [
            create_signal_message("TEST_001", "EURUSD", "BUY", 0.01, 1.0800, 1.1000),
            create_signal_message("TEST_002", "GBPUSD", "SELL", 0.01, 1.2700, 1.2500),
            create_signal_message("TEST_003", "XAUUSD", "BUY", 0.01, 1900.0, 2000.0)
        ]
        
        for idx, signal in enumerate(signals, 1):
            if connector.is_connected:
                print(f"[{idx}/3] Enviando sinal: {signal['action']} {signal['symbol']}")
                connector.send_signal(signal)
                time.sleep(2)
            else:
                print(f"\n[ERRO] EA desconectou antes do sinal {idx}")
                break
        
        # Aguardar relatórios
        print("\n[INFO] Aguardando relatorios (10 segundos)...\n")
        time.sleep(10)
        
        # Verificar relatórios
        reports = connector.get_pending_reports()
        print(f"\n[RESULTADO] {len(reports)} relatorios recebidos\n")
        
        for report in reports:
            print(f"   - {report.get('original_signal_id')}: {report.get('status')}")
        
        # Estatísticas
        print("\n[ESTATISTICAS]")
        stats = connector.get_statistics()
        print(f"   Sinais enviados: {stats['signals_sent']}")
        print(f"   Relatorios recebidos: {stats['reports_received']}")
        print(f"   Uptime: {stats['uptime_seconds']:.0f}s")
        
        # Manter servidor ativo
        print("\n[INFO] Servidor ativo. Pressione Ctrl+C para parar.\n")
        
        while connector.is_connected:
            time.sleep(5)
            if connector.is_connected:
                print(f"[STATUS] Conexao estavel. Uptime: {(time.time()-start):.0f}s")
    
    except KeyboardInterrupt:
        print("\n\n[INFO] Servidor sendo parado pelo usuario...\n")
    
    finally:
        connector.stop_server()
        print("[OK] Servidor parado.\n")

if __name__ == "__main__":
    main()

