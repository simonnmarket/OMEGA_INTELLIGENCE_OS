#!/usr/bin/env python3
"""
TESTE END-TO-END - SIMULAÇÃO COMPLETA DE EA
Projeto Prometheus v3.0.0 | Samsung Global Market
Protocolo: Omega TIER-0

Objetivo: Simular EA completo e validar comunicação bidirecional
Critérios de Sucesso:
  - Conexão estabelecida
  - ACK recebido (timeout 2s)
  - ≥9 heartbeats recebidos em 100s
"""

import socket
import json
import time
import sys
import io
from datetime import datetime

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurações
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555
TIMEOUT_ACK = 2.0  # segundos
TIMEOUT_HEARTBEAT = 12.0  # segundos (heartbeat a cada 10s)
TEST_DURATION = 100  # segundos
MIN_HEARTBEATS = 9  # mínimo esperado em 100s

def main():
    print("=" * 80)
    print("TESTE END-TO-END - SIMULAÇÃO COMPLETA DE EA")
    print("Projeto Prometheus v3.0.0 | Samsung Global Market")
    print("=" * 80)
    print(f"\nConfiguração:")
    print(f"  Servidor: {SERVER_HOST}:{SERVER_PORT}")
    print(f"  Timeout ACK: {TIMEOUT_ACK}s")
    print(f"  Timeout HEARTBEAT: {TIMEOUT_HEARTBEAT}s")
    print(f"  Duração do teste: {TEST_DURATION}s")
    print(f"  Heartbeats mínimos esperados: {MIN_HEARTBEATS}")
    print(f"\nIniciando teste...\n")
    
    try:
        # 1. CONECTAR AO SERVIDOR
        print("[1/4] Conectando ao servidor...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT_ACK)
        
        start_time = time.time()
        sock.connect((SERVER_HOST, SERVER_PORT))
        connect_time = time.time() - start_time
        
        print(f"      [OK] Conectado em {connect_time*1000:.1f}ms")
        
        # 2. ENVIAR HANDSHAKE
        print(f"\n[2/4] Enviando HANDSHAKE...")
        handshake = {
            "message_type": "HANDSHAKE",
            "ea_name": "SamsungGlobalMarket_EA",
            "version": "1.04",
            "account": 510065181
        }
        message = json.dumps(handshake, ensure_ascii=False) + '\n'
        sock.sendall(message.encode('utf-8'))
        print(f"      [OK] HANDSHAKE enviado")
        
        # 3. AGUARDAR ACK
        print(f"\n[3/4] Aguardando HANDSHAKE_ACK...")
        buffer = b''
        ack_start = time.time()
        ack_received = False
        
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    print(f"      [ERRO] Servidor desconectou antes de ACK")
                    sock.close()
                    return 1
                    
                buffer += chunk
                
                # Processar todas as mensagens completas
                while b'\n' in buffer:
                    message_bytes, buffer = buffer.split(b'\n', 1)
                    message_str = message_bytes.decode('utf-8')
                    message_dict = json.loads(message_str)
                    
                    msg_type = message_dict.get('message_type')
                    
                    if msg_type == 'HANDSHAKE_ACK':
                        ack_latency = time.time() - ack_start
                        print(f"      [OK] ACK recebido em {ack_latency*1000:.1f}ms")
                        print(f"        Servidor: {message_dict.get('server_name', 'N/A')}")
                        print(f"        Versão: {message_dict.get('version', 'N/A')}")
                        ack_received = True
                        break
                        
                if ack_received:
                    break
                    
            except socket.timeout:
                print(f"      [TIMEOUT] Aguardando ACK ({TIMEOUT_ACK}s)")
                sock.close()
                return 1
        
        # 4. AGUARDAR HEARTBEATS
        print(f"\n[4/4] Aguardando HEARTBEATS por {TEST_DURATION}s...")
        print(f"      (Esperado: ≥{MIN_HEARTBEATS} heartbeats)")
        print()
        
        sock.settimeout(TIMEOUT_HEARTBEAT)
        test_start = time.time()
        heartbeat_count = 0
        heartbeat_times = []
        
        while (time.time() - test_start) < TEST_DURATION:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    print(f"\n      [ERRO] Servidor desconectou apos {time.time() - test_start:.1f}s")
                    break
                    
                buffer += chunk
                
                # Processar todas as mensagens completas
                while b'\n' in buffer:
                    message_bytes, buffer = buffer.split(b'\n', 1)
                    message_str = message_bytes.decode('utf-8')
                    message_dict = json.loads(message_str)
                    
                    msg_type = message_dict.get('message_type')
                    
                    if msg_type == 'HEARTBEAT':
                        heartbeat_count += 1
                        elapsed = time.time() - test_start
                        heartbeat_times.append(elapsed)
                        
                        timestamp = message_dict.get('timestamp', 0)
                        server_status = message_dict.get('server_status', 'N/A')
                        
                        print(f"      [{heartbeat_count:02d}] Heartbeat recebido em T+{elapsed:.1f}s | Status: {server_status}")
                        
                        # Enviar ACK
                        ack = {
                            "message_type": "HEARTBEAT_ACK",
                            "timestamp": int(time.time() * 1000)
                        }
                        ack_msg = json.dumps(ack, ensure_ascii=False) + '\n'
                        sock.sendall(ack_msg.encode('utf-8'))
                        
            except socket.timeout:
                elapsed = time.time() - test_start
                print(f"\n      [AVISO] Timeout aguardando heartbeat em T+{elapsed:.1f}s")
                if elapsed >= TEST_DURATION:
                    break
                # Continuar aguardando
        
        sock.close()
        
        # RELATÓRIO FINAL
        print("\n" + "=" * 80)
        print("RELATÓRIO DE VALIDAÇÃO END-TO-END")
        print("=" * 80)
        print(f"\nData: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duração do teste: {time.time() - start_time:.1f}s")
        
        print(f"\n1. CONEXÃO:")
        print(f"   Status: [OK] SUCESSO")
        print(f"   Latência: {connect_time*1000:.1f}ms")
        
        print(f"\n2. HANDSHAKE:")
        print(f"   ACK recebido: [OK] SIM")
        print(f"   Latência: {ack_latency*1000:.1f}ms")
        
        print(f"\n3. HEARTBEATS:")
        print(f"   Recebidos: {heartbeat_count}")
        print(f"   Esperado: ≥{MIN_HEARTBEATS}")
        print(f"   Taxa: {heartbeat_count / (TEST_DURATION / 10):.1%} (esperado ~100%)")
        
        if heartbeat_count >= 2:
            intervals = [heartbeat_times[i] - heartbeat_times[i-1] for i in range(1, len(heartbeat_times))]
            avg_interval = sum(intervals) / len(intervals)
            min_interval = min(intervals)
            max_interval = max(intervals)
            
            print(f"\n   Intervalo médio: {avg_interval:.1f}s (esperado ~10s)")
            print(f"   Intervalo mín:   {min_interval:.1f}s")
            print(f"   Intervalo máx:   {max_interval:.1f}s")
        
        # CRITÉRIOS DE SUCESSO
        print(f"\n4. CRITÉRIOS DE SUCESSO:")
        
        connection_ok = True
        ack_ok = ack_received
        heartbeat_ok = heartbeat_count >= MIN_HEARTBEATS
        
        print(f"   Conexao estabelecida:  {'[OK] PASSOU' if connection_ok else '[ERRO] FALHOU'}")
        print(f"   ACK recebido:          {'[OK] PASSOU' if ack_ok else '[ERRO] FALHOU'}")
        print(f"   Heartbeats >={MIN_HEARTBEATS}:         {'[OK] PASSOU' if heartbeat_ok else '[ERRO] FALHOU'}")
        
        all_ok = connection_ok and ack_ok and heartbeat_ok
        
        print(f"\n5. RESULTADO FINAL:")
        if all_ok:
            print(f"   [OK] COMUNICACAO END-TO-END 100% FUNCIONAL")
            print(f"\n   O sistema está pronto para uso com EA real.")
            return 0
        else:
            print(f"   [ERRO] COMUNICACAO COM PROBLEMAS")
            print(f"\n   Ações necessárias:")
            if not ack_ok:
                print(f"     - Verificar lógica de handshake no servidor")
            if not heartbeat_ok:
                print(f"     - Verificar thread de heartbeat no servidor")
                print(f"     - Verificar intervalo de heartbeat (esperado ~10s)")
                print(f"     - Verificar logs do servidor para erros")
            return 1
        
    except ConnectionRefusedError:
        print(f"\n[ERRO] Conexao recusada")
        print(f"  Servidor não está rodando em {SERVER_HOST}:{SERVER_PORT}")
        print(f"\n  Ações necessárias:")
        print(f"    1. Iniciar servidor: .\\start_main_server.ps1")
        print(f"    2. Verificar que porta {SERVER_PORT} não está em uso")
        return 1
        
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        print("=" * 80)

if __name__ == '__main__':
    sys.exit(main())
