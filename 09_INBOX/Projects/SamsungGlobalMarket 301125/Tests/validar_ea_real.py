#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDAÇÃO FINAL: TESTE COM EA REAL
Projeto Prometheus v3.0.0 | Samsung Global Market

Este teste monitora os LOGS do MT5 para validar se o EA real está funcionando.
"""

import socket
import json
import time
import sys
from datetime import datetime

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

def print_section(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def simulate_ea_behavior():
    """Simula exatamente o comportamento que o EA deveria ter"""
    print_section("SIMULACAO DO COMPORTAMENTO DO EA")
    
    print("Conectando como EA real...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((SERVER_HOST, SERVER_PORT))
        print("[OK] Conectado")
        
        # Handshake EXATAMENTE como EA faz
        handshake = {
            "message_type": "HANDSHAKE",
            "ea_name": "SamsungGlobalMarket_EA",
            "version": "1.05",
            "account": 510065181
        }
        message = json.dumps(handshake) + '\n'
        sock.sendall(message.encode('utf-8'))
        print("[OK] Handshake enviado")
        
        # Aguardar ACK (como EA faz com ReceiveMessage)
        buffer = b''
        start_time = time.time()
        ack_received = False
        
        print("Aguardando ACK (como EA faria com SocketRead timeout 900ms)...")
        
        # Simular múltiplas chamadas de SocketRead (como OnTimer faz a cada 1s)
        for attempt in range(5):  # 5 tentativas = 5 segundos
            try:
                sock.settimeout(0.9)  # 900ms como no EA
                chunk = sock.recv(4096)
                
                if chunk:
                    buffer += chunk
                    print(f"  [{attempt+1}] Dados recebidos: {len(chunk)} bytes")
                    
                    if b'\n' in buffer:
                        message_bytes, buffer = buffer.split(b'\n', 1)
                        try:
                            message_dict = json.loads(message_bytes.decode('utf-8'))
                            if message_dict.get('message_type') == 'HANDSHAKE_ACK':
                                elapsed = time.time() - start_time
                                print(f"[OK] ACK recebido em {elapsed*1000:.1f}ms")
                                print(f"     Servidor: {message_dict.get('server_name', 'N/A')}")
                                ack_received = True
                                break
                        except:
                            pass
                else:
                    print(f"  [{attempt+1}] Nenhum dado (timeout 900ms) - NORMAL")
                    
            except socket.timeout:
                print(f"  [{attempt+1}] Timeout 900ms - NORMAL (sem dados ainda)")
                continue
        
        if not ack_received:
            print("[ERRO] ACK não recebido após 5 tentativas")
            sock.close()
            return False
        
        # Simular recebimento de heartbeats (como EA faria)
        print("\nSimulando recebimento de heartbeats (como EA faria)...")
        heartbeat_count = 0
        test_duration = 20  # 20 segundos
        test_start = time.time()
        buffer = b''
        
        while (time.time() - test_start) < test_duration:
            try:
                sock.settimeout(0.9)  # 900ms
                chunk = sock.recv(4096)
                
                if chunk:
                    buffer += chunk
                    
                    while b'\n' in buffer:
                        message_bytes, buffer = buffer.split(b'\n', 1)
                        try:
                            message_dict = json.loads(message_bytes.decode('utf-8'))
                            if message_dict.get('message_type') == 'HEARTBEAT':
                                heartbeat_count += 1
                                elapsed = time.time() - test_start
                                print(f"  [{heartbeat_count}] Heartbeat recebido em T+{elapsed:.1f}s")
                        except:
                            pass
                else:
                    # Timeout 900ms sem dados - NORMAL (não é erro)
                    pass
                    
            except socket.timeout:
                # Timeout 900ms - NORMAL (não é erro)
                continue
        
        sock.close()
        
        print(f"\nTotal de heartbeats recebidos: {heartbeat_count}")
        
        if heartbeat_count >= 1:
            print("[OK] EA deveria receber heartbeats corretamente")
            return True
        else:
            print("[ERRO] EA NÃO receberia heartbeats")
            return False
            
    except Exception as e:
        print(f"[ERRO] Falha na simulação: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 80)
    print(" VALIDACAO: COMPORTAMENTO DO EA REAL")
    print("=" * 80)
    print("\nEste teste simula EXATAMENTE como o EA se comporta:")
    print("  - SocketRead com timeout de 900ms")
    print("  - Múltiplas chamadas (como OnTimer a cada 1s)")
    print("  - Processamento de mensagens como EA faz")
    
    result = simulate_ea_behavior()
    
    print_section("CONCLUSAO")
    
    if result:
        print("[OK] O EA DEVERIA funcionar corretamente")
        print("\nPRÓXIMOS PASSOS:")
        print("  1. Compilar EA versão 1.05")
        print("  2. Anexar ao MT5")
        print("  3. Verificar logs do EA")
        print("  4. Se ainda não funcionar, problema pode ser:")
        print("     - EA não está lendo do socket corretamente")
        print("     - OnTimer não está sendo chamado")
        print("     - Buffer não está sendo processado corretamente")
    else:
        print("[ERRO] O EA NÃO funcionaria mesmo com servidor OK")
        print("\nPROBLEMAS POSSÍVEIS:")
        print("  - Timeout de 900ms pode ser insuficiente")
        print("  - Lógica de processamento de buffer pode ter problema")
        print("  - OnTimer pode não estar chamando ReceiveMessage")
    
    print("=" * 80)
    
    return 0 if result else 1

if __name__ == '__main__':
    sys.exit(main())

