#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG CONNECTION - Samsung Global Market
Verifica comunicação entre Python e MT5
"""

import socket
import json
import time
import threading

class ConnectionDebugger:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        
    def start_debug_server(self):
        """Inicia servidor de debug com logs detalhados"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.is_running = True
        
        print("=" * 60)
        print("DEBUG SERVER INICIADO")
        print("=" * 60)
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print("=" * 60)
        print("Aguardando conexão do EA...")
        
        # Thread para aceitar conexões
        threading.Thread(target=self._accept_connections, daemon=True).start()
        
    def _accept_connections(self):
        """Aceita conexões do EA"""
        while self.is_running:
            try:
                self.client_socket, addr = self.server_socket.accept()
                print(f"\n[OK] EA CONECTADO: {addr}")
                print("=" * 60)
                
                # Thread para ouvir o cliente
                threading.Thread(target=self._listen_to_client, args=(self.client_socket,), daemon=True).start()
                
            except Exception as e:
                if self.is_running:
                    print(f"❌ Erro ao aceitar conexão: {e}")
                break
                
    def _listen_to_client(self, sock):
        """Escuta mensagens do EA"""
        while self.is_running:
            try:
                data = sock.recv(1024)
                if data:
                    message = data.decode('utf-8').strip()
                    print(f"\n[MENSAGEM] RECEBIDA DO EA:")
                    print(f"Raw: {repr(message)}")
                    
                    try:
                        parsed = json.loads(message)
                        print(f"JSON: {json.dumps(parsed, indent=2)}")
                        
                        # Processar handshake
                        if parsed.get('message_type') == 'HANDSHAKE':
                            self._handle_handshake(parsed)
                        elif parsed.get('message_type') == 'HEARTBEAT':
                            self._handle_heartbeat(parsed)
                        else:
                            print(f"[AVISO] Tipo desconhecido: {parsed.get('message_type')}")
                            
                    except json.JSONDecodeError:
                        print(f"[ERRO] JSON invalido: {message}")
                        
                else:
                    print("[INFO] EA desconectado")
                    break
                    
            except Exception as e:
                print(f"[ERRO] Erro ao receber dados: {e}")
                break
                
        print("[INFO] Conexao com EA perdida")
        self.client_socket = None
        
    def _handle_handshake(self, handshake):
        """Processa handshake do EA"""
        print("\n[HANDSHAKE] PROCESSANDO:")
        print(f"EA Name: {handshake.get('ea_name', 'N/A')}")
        print(f"Version: {handshake.get('version', 'N/A')}")
        print(f"Account: {handshake.get('account', 'N/A')}")
        
        # Enviar HANDSHAKE_ACK
        response = {
            "message_type": "HANDSHAKE_ACK",
            "server_name": "Samsung Global Market Debug",
            "version": "3.1",
            "status": "READY"
        }
        
        self._send_message(response)
        
    def _handle_heartbeat(self, heartbeat):
        """Processa heartbeat do EA"""
        print(f"\n[HEARTBEAT] RECEBIDO: {heartbeat.get('timestamp', 'N/A')}")
        
        # Enviar HEARTBEAT_ACK
        response = {
            "message_type": "HEARTBEAT_ACK",
            "timestamp": int(time.time() * 1000),
            "status": "OK"
        }
        
        self._send_message(response)
        
    def _send_message(self, message_dict):
        """Envia mensagem para o EA"""
        if self.client_socket:
            try:
                message = json.dumps(message_dict) + "\n"
                self.client_socket.sendall(message.encode('utf-8'))
                print(f"\n[MENSAGEM] ENVIADA:")
                print(f"Raw: {repr(message)}")
                print(f"JSON: {json.dumps(message_dict, indent=2)}")
                
            except Exception as e:
                print(f"[ERRO] Erro ao enviar mensagem: {e}")
                self.client_socket = None
                
    def stop_debug_server(self):
        """Para o servidor de debug"""
        self.is_running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("\n[INFO] Debug server parado")

if __name__ == "__main__":
    debugger = ConnectionDebugger()
    
    try:
        debugger.start_debug_server()
        
        print("\n[INSTRUCOES]:")
        print("1. Anexe o EA ao grafico no MT5")
        print("2. Observe os logs aqui")
        print("3. Pressione Ctrl+C para parar")
        
        # Manter servidor ativo
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[INFO] Parando debug server...")
        debugger.stop_debug_server()
