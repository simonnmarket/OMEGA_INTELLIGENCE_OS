#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVIDOR MT5 SIMPLES E ROBUSTO
PROJETO: Samsung Global Market
SOLUCAO DEFINITIVA - SEM MAIS ITERACOES
"""

import socket
import json
import threading
import time

def handle_client(client_socket, addr):
    """Trata comunicação com EA - VERSÃO SIMPLIFICADA"""
    print(f"[OK] EA conectado: {addr}")
    
    # Thread para RECEBER mensagens do EA
    def receive_messages():
        buffer = ""
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = json.loads(line.strip())
                            msg_type = msg.get('message_type')
                            
                            if msg_type == 'HANDSHAKE':
                                print(f"[HANDSHAKE] EA: {msg.get('ea_name')} v{msg.get('version')}")
                                # Enviar ACK
                                ack = {
                                    'message_type': 'HANDSHAKE_ACK',
                                    'server_name': 'Samsung Global Market',
                                    'version': '3.1',
                                    'status': 'READY'
                                }
                                client_socket.sendall((json.dumps(ack) + '\n').encode('utf-8'))
                                print("[OK] Handshake ACK enviado")
                                
                            elif msg_type == 'HEARTBEAT_ACK':
                                print("[HEARTBEAT] ACK recebido do EA")
                                
                            elif msg_type == 'EXECUTION_REPORT':
                                print(f"[RELATORIO] Status: {msg.get('status')}, Ordem: {msg.get('order_ticket')}")
                                
                        except json.JSONDecodeError:
                            pass
                            
            except Exception as e:
                print(f"[ERRO] Receber: {e}")
                break
    
    # Thread para ENVIAR heartbeats
    def send_heartbeats():
        time.sleep(2)  # Aguardar handshake
        while True:
            try:
                hb = {
                    'message_type': 'HEARTBEAT',
                    'timestamp': int(time.time() * 1000),
                    'server_status': 'ACTIVE'
                }
                client_socket.sendall((json.dumps(hb) + '\n').encode('utf-8'))
                print("[HEARTBEAT] Enviado para EA")
                time.sleep(30)  # A cada 30 segundos
            except Exception as e:
                print(f"[ERRO] Heartbeat: {e}")
                break
    
    # Iniciar threads
    recv_thread = threading.Thread(target=receive_messages, daemon=True)
    hb_thread = threading.Thread(target=send_heartbeats, daemon=True)
    
    recv_thread.start()
    hb_thread.start()
    
    # Aguardar threads
    recv_thread.join()
    print(f"[INFO] EA desconectado: {addr}")
    client_socket.close()

def start_server():
    """Inicia servidor TCP"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 5555))
    server.listen(1)
    
    print("=" * 60)
    print("SERVIDOR MT5 INICIADO")
    print("=" * 60)
    print("Host: 127.0.0.1")
    print("Port: 5555")
    print("=" * 60)
    print("Aguardando conexao do EA...")
    print("")
    
    while True:
        try:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[INFO] Servidor parado")
            break
        except Exception as e:
            print(f"[ERRO] {e}")

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[OK] Servidor finalizado")

