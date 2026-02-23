# -*- coding: utf-8 -*-
"""
MT5_Connector v2.0 - Servidor Robusto com Heartbeat Ativo
PROJETO: Samsung Global Market
DATA: 2025-10-27
STATUS: CORRIGIDO - HEARTBEAT ATIVO IMPLEMENTADO
"""

import socket
import json
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Callable, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MT5_Connector:
    def __init__(self, host='127.0.0.1', port=5555, heartbeat_interval=30):
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval
        self.server_socket = None
        self.client_socket = None
        self.is_running = False
        self.is_connected = False

        # Callbacks
        self.on_execution_report: Optional[Callable] = None
        self.on_connection_change: Optional[Callable] = None
        
        # Thread para heartbeat
        self.heartbeat_thread = None

    def start_server(self):
        """Inicia o servidor e as threads de comunicação."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.is_running = True
            logging.info(f"✅ Servidor MT5 iniciado em {self.host}:{self.port}")

            # Thread para aceitar conexões
            threading.Thread(target=self._accept_connections, daemon=True).start()
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar servidor: {e}")
            self.stop_server()

    def _accept_connections(self):
        """Aguarda e aceita conexões de EAs."""
        while self.is_running:
            try:
                self.server_socket.settimeout(1.0)  # Timeout para permitir verificação de is_running
                self.client_socket, addr = self.server_socket.accept()
                self.is_connected = True
                logging.info(f"🤝 EA conectado de {addr}")
                if self.on_connection_change:
                    self.on_connection_change(True, addr)

                # Inicia thread de heartbeat
                self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
                self.heartbeat_thread.start()

                # Inicia thread para ouvir o cliente
                threading.Thread(target=self._listen_to_client, args=(self.client_socket, addr), daemon=True).start()

            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    logging.error(f"❌ Erro ao aceitar conexão: {e}")
                break

    def _listen_to_client(self, sock, addr):
        """Escuta mensagens do cliente conectado."""
        buffer = ""
        while self.is_connected and self.is_running:
            try:
                sock.settimeout(1.0)
                data = sock.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        self._handle_message(line.strip(), addr)

            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"❌ Erro ao receber dados de {addr}: {e}")
                break
        
        self._disconnect_client()

    def _handle_message(self, message: str, addr):
        """Processa mensagens recebidas do EA."""
        try:
            data = json.loads(message)
            msg_type = data.get("message_type")

            if msg_type == "HANDSHAKE":
                self._handle_handshake(data, addr)
            elif msg_type == "HEARTBEAT_ACK":
                logging.debug("💓 Heartbeat ACK recebido.")
            elif msg_type == "EXECUTION_REPORT":
                self._handle_execution_report(data)
            elif msg_type == "SHUTDOWN":
                logging.info("🛑 EA solicitou shutdown.")
                self._disconnect_client()
            else:
                logging.warning(f"⚠️ Tipo de mensagem desconhecido: {msg_type}")
        except json.JSONDecodeError:
            logging.error(f"❌ Falha ao decodificar JSON: {message}")
        except Exception as e:
            logging.error(f"❌ Erro ao processar mensagem: {e}")

    def _handle_handshake(self, handshake: Dict, addr):
        """Processa o handshake inicial do EA."""
        logging.info(f"🤝 Handshake recebido de: {handshake.get('ea_name')} v{handshake.get('version')}")
        response = {
            'message_type': 'HANDSHAKE_ACK',
            'server_name': 'Samsung Global Market',
            'version': '3.1',
            'status': 'READY'
        }
        self._send_message(response)

    def _handle_execution_report(self, report: Dict):
        """Processa o relatório de execução do EA."""
        logging.info(f"📊 Relatório de execução recebido: {report.get('status')} - Ordem {report.get('order_ticket')}")
        if self.on_execution_report:
            self.on_execution_report(report)

    def _heartbeat_loop(self):
        """Envia mensagens de heartbeat para o EA em intervalos regulares."""
        logging.info(f"💓 Iniciando heartbeat loop (intervalo: {self.heartbeat_interval}s)")
        while self.is_connected and self.is_running:
            try:
                heartbeat_msg = {
                    "message_type": "HEARTBEAT", 
                    "timestamp": int(time.time() * 1000),
                    "server_status": "ACTIVE"
                }
                self._send_message(heartbeat_msg)
                logging.debug("💓 Heartbeat enviado")
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logging.error(f"❌ Erro no heartbeat loop: {e}")
                break

    def _send_message(self, message_dict: Dict):
        """Envia uma mensagem JSON para o EA conectado."""
        if self.is_connected and self.client_socket:
            try:
                message = json.dumps(message_dict) + "\n"
                self.client_socket.sendall(message.encode('utf-8'))
            except Exception as e:
                logging.error(f"❌ Erro ao enviar mensagem: {e}")
                self._disconnect_client()

    def send_signal(self, signal_dict: Dict):
        """Envia um sinal de trading para o EA."""
        logging.info(f"📤 Enviando sinal: {signal_dict.get('id')} ({signal_dict.get('action')} {signal_dict.get('symbol')})")
        self._send_message(signal_dict)
        return self.is_connected

    def _disconnect_client(self):
        """Desconecta o cliente atual e limpa o estado."""
        if self.is_connected:
            self.is_connected = False
            if self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None
            logging.info("⚠️ EA desconectado.")
            if self.on_connection_change:
                self.on_connection_change(False, None)

    def stop_server(self):
        """Para o servidor e todas as threads."""
        logging.info("🛑 Parando servidor...")
        self.is_running = False
        self._disconnect_client()
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        logging.info("✅ Servidor parado.")

# Função auxiliar para criar sinais
def create_signal_message(signal_id, symbol, action, volume, stop_loss, take_profit, comment="", magic_number=12345):
    return {
        "message_type": "SIGNAL",
        "id": signal_id,
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "action": action,
        "volume": volume,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "magic_number": magic_number,
        "comment": comment
    }