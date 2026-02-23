#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE CONEXAO COM SERVIDOR
OBJETIVO: Verificar se o servidor esta respondendo
"""

import socket
import json
import time

def test_server():
    """Testa conexão com servidor"""
    print("=" * 60)
    print("TESTE DE CONEXAO COM SERVIDOR")
    print("=" * 60)
    print("")
    
    try:
        # Conectar ao servidor
        print("[1] Conectando ao servidor 127.0.0.1:5555...")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(('127.0.0.1', 5555))
        print("[OK] Conexao estabelecida!")
        print("")
        
        # Enviar HANDSHAKE
        print("[2] Enviando HANDSHAKE...")
        handshake = {
            'message_type': 'HANDSHAKE',
            'ea_name': 'TestClient',
            'version': '1.0',
            'account': 99999
        }
        client.sendall((json.dumps(handshake) + '\n').encode('utf-8'))
        print("[OK] HANDSHAKE enviado!")
        print("")
        
        # Aguardar resposta
        print("[3] Aguardando resposta do servidor...")
        client.settimeout(10)
        data = client.recv(1024).decode('utf-8')
        
        if data:
            print("[OK] Resposta recebida:")
            print(data)
            response = json.loads(data.strip())
            print(f"    Tipo: {response.get('message_type')}")
            print(f"    Status: {response.get('status')}")
            print("")
            
            # Aguardar heartbeat
            print("[4] Aguardando heartbeat (30 segundos)...")
            for i in range(35):
                client.settimeout(1)
                try:
                    hb_data = client.recv(1024).decode('utf-8')
                    if hb_data:
                        hb = json.loads(hb_data.strip())
                        if hb.get('message_type') == 'HEARTBEAT':
                            print(f"[OK] Heartbeat recebido! Count: {hb.get('count')}")
                            print("")
                            print("=" * 60)
                            print("RESULTADO: SERVIDOR FUNCIONANDO CORRETAMENTE!")
                            print("=" * 60)
                            client.close()
                            return True
                except socket.timeout:
                    print(f"... aguardando ({i+1}s)")
                    time.sleep(1)
            
            print("")
            print("=" * 60)
            print("RESULTADO: SERVIDOR NAO ENVIOU HEARTBEAT!")
            print("=" * 60)
            client.close()
            return False
        else:
            print("[ERRO] Nenhuma resposta do servidor!")
            client.close()
            return False
            
    except socket.timeout:
        print("[ERRO] Timeout ao conectar/receber dados!")
        return False
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    result = test_server()
    print("")
    if result:
        print("CONCLUSAO: Servidor esta FUNCIONANDO!")
    else:
        print("CONCLUSAO: Servidor NAO esta funcionando corretamente!")
        print("O servidor precisa ser corrigido ou reiniciado.")

