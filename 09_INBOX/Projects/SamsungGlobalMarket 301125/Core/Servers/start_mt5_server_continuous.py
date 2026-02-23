# -*- coding: utf-8 -*-
"""
SERVIDOR MT5 CONTÍNUO - SEM TIMEOUT
Permanece ativo até Ctrl+C
"""

import sys
import time
from MT5_Connector import MT5_Connector, create_signal_message

def main():
    print("\n" + "="*80)
    print("[MT5 SERVER] SAMSUNG GLOBAL MARKET - SERVIDOR CONTINUO")
    print("="*80)
    print("[INFO] Servidor permanecera ativo ate Ctrl+C")
    print("[INFO] Nenhum timeout, nenhum sinal automatico")
    print("[INFO] Apenas escuta e processa comandos do EA\n")
    
    # Criar e iniciar conector
    connector = MT5_Connector(host='127.0.0.1', port=5555)
    
    # Callback para conexão
    def on_connection(connected, address):
        if connected:
            print(f"\n[OK] EA CONECTADO: {address}")
            print("[INFO] Conexao estavel. Sistema pronto.\n")
        else:
            print(f"\n[INFO] EA desconectou. Aguardando nova conexao...\n")
    
    # Callback para relatórios
    def on_report(report):
        status = report.get('status', 'UNKNOWN')
        signal_id = report.get('original_signal_id', 'N/A')
        ticket = report.get('order_ticket', 0)
        print(f"\n[RELATORIO] Signal {signal_id}: {status} (Order #{ticket})")
    
    connector.on_connection_change = on_connection
    connector.on_execution_report = on_report
    
    # Iniciar servidor
    connector.start_server()
    
    print("[OK] Servidor iniciado em 127.0.0.1:5555")
    print("[INFO] Aguardando conexao do EA...")
    print("[INFO] Pressione Ctrl+C para parar o servidor.\n")
    
    try:
        # Loop infinito - aguarda até Ctrl+C
        while True:
            time.sleep(5)
            
            # Mostrar status a cada 60s
            if int(time.time()) % 60 == 0:
                stats = connector.get_statistics()
                uptime = stats['uptime_seconds']
                
                if connector.is_connected:
                    print(f"[STATUS] EA conectado | Uptime: {uptime:.0f}s | Sinais: {stats['signals_sent']} | Relatorios: {stats['reports_received']}")
                else:
                    print(f"[STATUS] Aguardando EA... | Uptime servidor: {uptime:.0f}s")
                
                time.sleep(1)  # Evitar múltiplas impressões no mesmo segundo
    
    except KeyboardInterrupt:
        print("\n\n[INFO] Ctrl+C detectado. Parando servidor...\n")
    
    finally:
        connector.stop_server()
        print("[OK] Servidor parado.\n")

if __name__ == "__main__":
    main()

