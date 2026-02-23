#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DIRETO DE CONEXÃO - DIAGNOSTICAR PROBLEMA REAL
"""

import socket
import json
import time

def test_server_connection():
    """Testa se o servidor está realmente escutando e aceitando conexões"""
    print("=" * 70)
    print("TESTE DIRETO DE CONEXÃO COM SERVIDOR")
    print("=" * 70)
    
    # Tentar conectar
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        print("\n[1] Tentando conectar em 127.0.0.1:5555...")
        client.connect(('127.0.0.1', 5555))
        print("[OK] Conexão estabelecida!")
        
        # Enviar handshake
        print("\n[2] Enviando handshake...")
        handshake = {
            "message_type": "HANDSHAKE",
            "ea_name": "TestEA",
            "version": "1.02",
            "account": 12345
        }
        message = json.dumps(handshake) + '\n'
        client.sendall(message.encode('utf-8'))
        print("[OK] Handshake enviado!")
        
        # Aguardar resposta
        print("\n[3] Aguardando resposta do servidor...")
        client.settimeout(10)
        try:
            data = client.recv(1024)
            if data:
                response = data.decode('utf-8')
                print(f"[OK] Resposta recebida: {response[:200]}")
                try:
                    response_json = json.loads(response.strip())
                    if response_json.get('message_type') == 'HANDSHAKE_ACK':
                        print("[OK] Handshake ACK recebido corretamente!")
                    else:
                        print(f"[AVISO] Resposta não é HANDSHAKE_ACK: {response_json}")
                except:
                    print(f"[AVISO] Resposta não é JSON válido")
            else:
                print("[ERRO] Nenhuma resposta recebida!")
        except socket.timeout:
            print("[ERRO] Timeout ao aguardar resposta!")
        
        # Aguardar heartbeat
        print("\n[4] Aguardando heartbeat do servidor (30s)...")
        client.settimeout(35)
        try:
            data = client.recv(1024)
            if data:
                response = data.decode('utf-8')
                print(f"[OK] Mensagem recebida: {response[:200]}")
                try:
                    response_json = json.loads(response.strip())
                    if response_json.get('message_type') == 'HEARTBEAT':
                        print("[OK] Heartbeat recebido corretamente!")
                    else:
                        print(f"[AVISO] Mensagem não é HEARTBEAT: {response_json}")
                except:
                    print(f"[AVISO] Mensagem não é JSON válido")
            else:
                print("[ERRO] Nenhum heartbeat recebido!")
        except socket.timeout:
            print("[ERRO] Timeout ao aguardar heartbeat (servidor não está enviando)")
        
        client.close()
        print("\n[OK] Conexão fechada")
        
    except ConnectionRefusedError:
        print("[ERRO] Servidor não está rodando ou porta 5555 não está aberta!")
        print("       Execute: .\\start_main_server.ps1")
    except socket.timeout:
        print("[ERRO] Timeout ao conectar - servidor pode estar muito lento")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
    
    print("\n" + "=" * 70)
    print("TESTE CONCLUÍDO")
    print("=" * 70)

if __name__ == "__main__":
    test_server_connection()

