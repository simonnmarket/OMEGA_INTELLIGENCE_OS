#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE QUANTITATIVO DO SERVIDOR
Projeto Prometheus v3.0.0 | Samsung Global Market
Protocolo: Omega TIER-0

Objetivo: Validar que servidor Python está 100% funcional
Critérios de Sucesso:
  - Conexões: 100% (50/50)
  - ACKs: 100% (50/50)
  - Heartbeats: ≥95% (48/50)
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
NUM_TESTS = 50
TIMEOUT_ACK = 2.0  # segundos
TIMEOUT_HEARTBEAT = 15.0  # segundos

# Estatísticas
stats = {
    'connections_success': 0,
    'connections_fail': 0,
    'ack_received': 0,
    'ack_timeout': 0,
    'heartbeat_received': 0,
    'heartbeat_timeout': 0,
    'latencies': []
}

def test_connection(test_num):
    """Testa uma conexão completa com o servidor"""
    try:
        # 1. Conectar ao servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT_ACK)
        
        start_time = time.time()
        sock.connect((SERVER_HOST, SERVER_PORT))
        connect_time = time.time() - start_time
        
        stats['connections_success'] += 1
        print(f"[{test_num:02d}] [OK] Conectado em {connect_time*1000:.1f}ms")
        
        # 2. Enviar HANDSHAKE
        handshake = {
            "message_type": "HANDSHAKE",
            "ea_name": "TestClient",
            "version": "1.04",
            "account": 123456
        }
        message = json.dumps(handshake, ensure_ascii=False) + '\n'
        sock.sendall(message.encode('utf-8'))
        print(f"[{test_num:02d}]   → HANDSHAKE enviado")
        
        # 3. Aguardar ACK
        buffer = b''
        ack_start = time.time()
        
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    print(f"[{test_num:02d}]   [ERRO] Servidor desconectou antes de ACK")
                    stats['ack_timeout'] += 1
                    sock.close()
                    return False
                    
                buffer += chunk
                
                # Procurar mensagem completa
                if b'\n' in buffer:
                    message_bytes, buffer = buffer.split(b'\n', 1)
                    message_str = message_bytes.decode('utf-8')
                    message_dict = json.loads(message_str)
                    
                    if message_dict.get('message_type') == 'HANDSHAKE_ACK':
                        ack_latency = time.time() - ack_start
                        stats['ack_received'] += 1
                        stats['latencies'].append(ack_latency)
                        print(f"[{test_num:02d}]   [OK] ACK recebido em {ack_latency*1000:.1f}ms")
                        break
                        
            except socket.timeout:
                print(f"[{test_num:02d}]   [TIMEOUT] Aguardando ACK ({TIMEOUT_ACK}s)")
                stats['ack_timeout'] += 1
                sock.close()
                return False
        
        # 4. Aguardar HEARTBEAT
        sock.settimeout(TIMEOUT_HEARTBEAT)
        heartbeat_start = time.time()
        
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    print(f"[{test_num:02d}]   [ERRO] Servidor desconectou antes de HEARTBEAT")
                    stats['heartbeat_timeout'] += 1
                    sock.close()
                    return False
                    
                buffer += chunk
                
                # Procurar mensagem completa
                while b'\n' in buffer:
                    message_bytes, buffer = buffer.split(b'\n', 1)
                    message_str = message_bytes.decode('utf-8')
                    message_dict = json.loads(message_str)
                    
                    if message_dict.get('message_type') == 'HEARTBEAT':
                        heartbeat_latency = time.time() - heartbeat_start
                        stats['heartbeat_received'] += 1
                        print(f"[{test_num:02d}]   [OK] HEARTBEAT recebido em {heartbeat_latency*1000:.0f}ms")
                        sock.close()
                        return True
                        
            except socket.timeout:
                print(f"[{test_num:02d}]   [TIMEOUT] Aguardando HEARTBEAT ({TIMEOUT_HEARTBEAT}s)")
                stats['heartbeat_timeout'] += 1
                sock.close()
                return False
        
    except ConnectionRefusedError:
        print(f"[{test_num:02d}] [ERRO] Conexao recusada (servidor nao esta rodando?)")
        stats['connections_fail'] += 1
        return False
        
    except Exception as e:
        print(f"[{test_num:02d}] [ERRO] Erro: {e}")
        stats['connections_fail'] += 1
        return False

def main():
    print("=" * 80)
    print("TESTE QUANTITATIVO DO SERVIDOR")
    print("Projeto Prometheus v3.0.0 | Samsung Global Market")
    print("=" * 80)
    print(f"\nConfiguração:")
    print(f"  Servidor: {SERVER_HOST}:{SERVER_PORT}")
    print(f"  Número de testes: {NUM_TESTS}")
    print(f"  Timeout ACK: {TIMEOUT_ACK}s")
    print(f"  Timeout HEARTBEAT: {TIMEOUT_HEARTBEAT}s")
    print(f"\nIniciando testes...\n")
    
    start_time = time.time()
    
    for i in range(1, NUM_TESTS + 1):
        test_connection(i)
        time.sleep(0.1)  # Pequeno delay entre testes
    
    total_time = time.time() - start_time
    
    # Relatório
    print("\n" + "=" * 80)
    print("RELATÓRIO DE VALIDAÇÃO")
    print("=" * 80)
    print(f"\nData: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tempo total: {total_time:.1f}s")
    
    print(f"\n1. CONEXÕES:")
    print(f"   Sucesso: {stats['connections_success']}/{NUM_TESTS} ({stats['connections_success']/NUM_TESTS*100:.1f}%)")
    print(f"   Falha:   {stats['connections_fail']}/{NUM_TESTS} ({stats['connections_fail']/NUM_TESTS*100:.1f}%)")
    
    print(f"\n2. HANDSHAKE ACK:")
    print(f"   Recebido: {stats['ack_received']}/{NUM_TESTS} ({stats['ack_received']/NUM_TESTS*100:.1f}%)")
    print(f"   Timeout:  {stats['ack_timeout']}/{NUM_TESTS} ({stats['ack_timeout']/NUM_TESTS*100:.1f}%)")
    
    if stats['latencies']:
        avg_latency = sum(stats['latencies']) / len(stats['latencies'])
        min_latency = min(stats['latencies'])
        max_latency = max(stats['latencies'])
        print(f"   Latência média: {avg_latency*1000:.1f}ms")
        print(f"   Latência mín:   {min_latency*1000:.1f}ms")
        print(f"   Latência máx:   {max_latency*1000:.1f}ms")
    
    print(f"\n3. HEARTBEATS:")
    print(f"   Recebido: {stats['heartbeat_received']}/{NUM_TESTS} ({stats['heartbeat_received']/NUM_TESTS*100:.1f}%)")
    print(f"   Timeout:  {stats['heartbeat_timeout']}/{NUM_TESTS} ({stats['heartbeat_timeout']/NUM_TESTS*100:.1f}%)")
    
    # Critérios de sucesso
    print(f"\n4. CRITÉRIOS DE SUCESSO:")
    
    connections_ok = stats['connections_success'] == NUM_TESTS
    ack_ok = stats['ack_received'] == NUM_TESTS
    heartbeat_ok = stats['heartbeat_received'] >= int(NUM_TESTS * 0.95)
    
    print(f"   Conexões 100%:     {'✓ PASSOU' if connections_ok else '✗ FALHOU'}")
    print(f"   ACKs 100%:         {'✓ PASSOU' if ack_ok else '✗ FALHOU'}")
    print(f"   Heartbeats ≥95%:   {'✓ PASSOU' if heartbeat_ok else '✗ FALHOU'}")
    
    all_ok = connections_ok and ack_ok and heartbeat_ok
    
    print(f"\n5. RESULTADO FINAL:")
    if all_ok:
        print(f"   ✓✓✓ SERVIDOR 100% FUNCIONAL ✓✓✓")
        print(f"\n   O servidor está pronto para uso em produção.")
        return 0
    else:
        print(f"   ✗✗✗ SERVIDOR COM PROBLEMAS ✗✗✗")
        print(f"\n   Ações necessárias:")
        if not connections_ok:
            print(f"     - Verificar se servidor está rodando")
            print(f"     - Verificar firewall/antivírus")
        if not ack_ok:
            print(f"     - Verificar lógica de handshake no servidor")
            print(f"     - Verificar logs do servidor")
        if not heartbeat_ok:
            print(f"     - Verificar thread de heartbeat no servidor")
            print(f"     - Verificar intervalo de heartbeat (deve ser <15s)")
        return 1
    
    print("=" * 80)

if __name__ == '__main__':
    sys.exit(main())
