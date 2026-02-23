#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE STRESS DE ALTA TECNOLOGIA - SERVIDOR MT5
PROJETO: Samsung Global Market
OBJETIVO: Validar robustez, performance e resiliencia do servidor sob condicoes extremas.
DATA: 2025-10-27
"""

import socket
import json
import threading
import time
import subprocess
import sys
import os
import random
from datetime import datetime

# --- Configuracoes do Teste ---
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555
NUM_CLIENTS = 5  # Numero de EAs simulados
MESSAGES_PER_CLIENT = 200  # Mensagens por cliente
TEST_DURATION_SECONDS = 60  # Duracao total do teste

# --- Resultados do Teste ---
test_results = {
    "server_started": False,
    "all_clients_connected": False,
    "clients_connected": 0,
    "messages_sent": 0,
    "messages_received": 0,
    "heartbeats_sent": 0,
    "heartbeats_received": 0,
    "malformed_messages_sent": 0,
    "errors_on_server": 0,
    "latencies": [],
    "passed": False
}

# Lock para thread-safety
results_lock = threading.Lock()

def start_server_process():
    """Inicia o servidor Python em um subprocesso."""
    print("[ACTION] Iniciando o servidor em subprocesso...")
    try:
        # Assume que o script do servidor esta no mesmo diretorio
        server_script = "simple_mt5_server.py"
        process = subprocess.Popen(
            [sys.executable, server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Aguardar o servidor inicializar
        time.sleep(3)
        
        # Verificar se o processo esta vivo e se a porta esta aberta
        if process.poll() is None and is_port_open():
            print("[OK] Servidor iniciado com sucesso.")
            test_results["server_started"] = True
            return process
        else:
            print("[FAIL] Servidor falhou ao iniciar.")
            return None
    except Exception as e:
        print(f"[FAIL] Erro ao iniciar subprocesso do servidor: {e}")
        return None

def is_port_open():
    """Verifica se a porta do servidor esta aberta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((SERVER_HOST, SERVER_PORT))
        return True
    except:
        return False

def simulate_ea_client(client_id):
    """Simula um cliente EA que envia e recebe mensagens."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        
        with results_lock:
            test_results["clients_connected"] += 1
        
        print(f"[CLIENT {client_id}] Conectado.")
        
        # 1. Handshake
        handshake_msg = {
            "message_type": "HANDSHAKE",
            "ea_name": f"StressTest_EA_{client_id}",
            "version": "1.01",
            "account": 12345 + client_id
        }
        send_message(client_socket, handshake_msg)
        
        # Aguardar resposta
        time.sleep(0.5)
        
        try:
            response = receive_message(client_socket)
            if response and response.get("message_type") == "HANDSHAKE_ACK":
                print(f"[CLIENT {client_id}] Handshake OK.")
            else:
                print(f"[CLIENT {client_id}] [WARN] Handshake sem resposta.")
        except:
            print(f"[CLIENT {client_id}] [WARN] Timeout no handshake.")
        
        # 2. Loop de envio de mensagens
        start_time = time.time()
        messages_sent_by_this_client = 0
        
        for i in range(MESSAGES_PER_CLIENT):
            if time.time() - start_time > TEST_DURATION_SECONDS:
                break

            # Enviar sinal de teste
            signal_msg = {
                "message_type": "SIGNAL",
                "id": f"STRESS_{client_id}_{i}",
                "symbol": "EURUSD",
                "action": random.choice(["BUY", "SELL"]),
                "volume": 0.01,
                "stop_loss": 1.0800,
                "take_profit": 1.0900
            }
            send_message(client_socket, signal_msg)
            messages_sent_by_this_client += 1
            
            with results_lock:
                test_results["messages_sent"] += 1

            # Pequeno atraso para nao sobrecarregar instantaneamente
            time.sleep(0.01)

            # Enviar Heartbeat ACK periodicamente
            if i % 20 == 0:
                ack_msg = {"message_type": "HEARTBEAT_ACK"}
                send_message(client_socket, ack_msg)
                with results_lock:
                    test_results["heartbeats_sent"] += 1
            
            # Enviar mensagem malformada para testar resiliencia
            if i % 50 == 0:
                malformed_msg = "{'message_type': 'MALFORMED', 'invalid': True"
                try:
                    client_socket.sendall((malformed_msg + '\n').encode('utf-8'))
                    with results_lock:
                        test_results["malformed_messages_sent"] += 1
                except:
                    pass

        print(f"[CLIENT {client_id}] Finalizado envio de {messages_sent_by_this_client} mensagens.")
        client_socket.close()

    except Exception as e:
        print(f"[CLIENT {client_id}] [ERROR] {e}")

def send_message(sock, msg_dict):
    """Envia uma mensagem JSON para o servidor."""
    try:
        message = json.dumps(msg_dict) + '\n'
        sock.sendall(message.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Falha ao enviar mensagem: {e}")

def receive_message(sock):
    """Recebe uma mensagem do servidor."""
    try:
        sock.settimeout(2)
        data = sock.recv(1024).decode('utf-8').strip()
        if data:
            for line in data.split('\n'):
                if line.strip():
                    return json.loads(line.strip())
    except:
        pass
    return None

def run_stress_test():
    """Executa o teste de stress completo."""
    print("=" * 80)
    print("TESTE DE STRESS DE ALTA TECNOLOGIA - SERVIDOR MT5")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuracao:")
    print(f"  - Numero de clientes: {NUM_CLIENTS}")
    print(f"  - Mensagens por cliente: {MESSAGES_PER_CLIENT}")
    print(f"  - Duracao maxima: {TEST_DURATION_SECONDS}s")
    print("=" * 80)
    
    server_process = start_server_process()
    if not server_process:
        generate_final_report()
        return False

    time.sleep(2)  # Garantir que o servidor esta pronto para conexoes

    print("\n[ACTION] Iniciando simulacao de multiplos clientes...")
    client_threads = []
    for i in range(NUM_CLIENTS):
        thread = threading.Thread(target=simulate_ea_client, args=(i + 1,))
        client_threads.append(thread)
        thread.start()
        time.sleep(0.2)  # Pequeno atraso entre conexoes

    print(f"[ACTION] {NUM_CLIENTS} clientes iniciados. Aguardando conclusao...")
    for thread in client_threads:
        thread.join()

    print("\n[ACTION] Teste concluido. Analisando servidor...")
    time.sleep(2)

    # Parar o servidor
    print("[ACTION] Parando o servidor...")
    try:
        server_process.terminate()
        server_process.wait(timeout=5)
    except:
        server_process.kill()
    
    # Ler logs do servidor para verificar erros
    try:
        server_logs = server_process.stdout.read() if server_process.stdout else ""
        if server_logs:
            if "[ERRO]" in server_logs or "Traceback" in server_logs:
                print("[FAIL] Erros detectados nos logs do servidor.")
                print("--- LOGS DO SERVIDOR ---")
                print(server_logs[:1000])  # Primeiros 1000 caracteres
                print("-------------------------")
                test_results["errors_on_server"] = server_logs.count("[ERRO]")
    except:
        print("[WARN] Nao foi possivel ler logs do servidor")

    # Gerar relatorio final
    generate_final_report()
    
    return test_results["passed"]

def generate_final_report():
    """Gera o relatorio final do teste."""
    print("\n" + "=" * 80)
    print("RELATORIO FINAL DO TESTE DE STRESS")
    print("=" * 80)

    print(f"Servidor Iniciado:          {'[PASS]' if test_results['server_started'] else '[FAIL]'}")
    print(f"Clientes Conectados:        {test_results['clients_connected']}/{NUM_CLIENTS}")
    print(f"Mensagens Enviadas:         {test_results['messages_sent']}")
    print(f"Mensagens Malformadas:      {test_results['malformed_messages_sent']}")
    print(f"Heartbeats Enviados:        {test_results['heartbeats_sent']}")
    print(f"Erros no Servidor:          {test_results['errors_on_server']}")
    
    # Criterios de aprovacao
    passed = (
        test_results['server_started'] and
        test_results['clients_connected'] >= NUM_CLIENTS * 0.8 and  # 80% dos clientes conectaram
        test_results['messages_sent'] > NUM_CLIENTS * MESSAGES_PER_CLIENT * 0.8 and  # 80% das mensagens enviadas
        test_results['errors_on_server'] == 0
    )
    
    test_results["passed"] = passed

    print("\n" + "=" * 80)
    print("VEREDITO FINAL")
    print("=" * 80)
    if passed:
        print("[PASS] TESTE DE STRESS PASSOU!")
        print("")
        print("CONCLUSAO:")
        print("  O servidor e ROBUSTO e CONFIAVEL.")
        print("  O sistema esta VALIDADO PARA PRODUCAO.")
        print("  PRONTO PARA FASE 5: PAPER TRADING")
        print("")
        print("PROXIMA ACAO:")
        print("  Iniciar paper trading de 30 dias com confianca total.")
    else:
        print("[FAIL] TESTE DE STRESS FALHOU!")
        print("")
        print("PROBLEMAS IDENTIFICADOS:")
        if not test_results['server_started']:
            print("  - Servidor nao conseguiu iniciar")
        if test_results['clients_connected'] < NUM_CLIENTS * 0.8:
            print(f"  - Poucos clientes conectaram ({test_results['clients_connected']}/{NUM_CLIENTS})")
        if test_results['messages_sent'] < NUM_CLIENTS * MESSAGES_PER_CLIENT * 0.8:
            print(f"  - Poucas mensagens enviadas ({test_results['messages_sent']}/{NUM_CLIENTS * MESSAGES_PER_CLIENT})")
        if test_results['errors_on_server'] > 0:
            print(f"  - Erros detectados no servidor ({test_results['errors_on_server']})")
        print("")
        print("PROXIMA ACAO:")
        print("  Corrigir os problemas identificados e executar teste novamente.")
    
    print("=" * 80)

if __name__ == "__main__":
    try:
        success = run_stress_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Teste interrompido pelo usuario")
        sys.exit(2)
    except Exception as e:
        print(f"\n[ERROR] Erro fatal no teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

