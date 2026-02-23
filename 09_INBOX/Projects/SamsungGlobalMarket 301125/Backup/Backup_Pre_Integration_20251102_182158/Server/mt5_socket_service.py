#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVIÇO DE SOCKET MT5 - COMUNICAÇÃO COM EA
PROJETO: Prometheus v3.0.0
PROTOCOLO: Omega TIER-0
ARQUITETURA: Big Tech - Serviço Desacoplado

Gerencia comunicação TCP/IP com Expert Advisors do MetaTrader 5.
Implementa protocolo de handshake, heartbeat e transmissão de sinais.
"""

import socket
import json
import threading
import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger("SocketService")

# ============================================================================
# SERVIÇO DE SOCKET MT5
# ============================================================================
class MT5SocketService:
    """
    Serviço de comunicação TCP/IP para MetaTrader 5.
    Gerencia conexões de múltiplos EAs simultaneamente.
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 5555):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.clients: List[socket.socket] = []
        self.client_info: Dict[socket.socket, Dict] = {}
        self.trading_engine = None  # Referência ao motor de trading
        self.heartbeat_interval = 10  # Segundos (reduzido para aumentar chance de EA v1.02 capturar)
        self._lock = threading.Lock()
        
    def set_trading_engine(self, engine):
        """Recebe a referência do motor de trading."""
        self.trading_engine = engine
        logger.debug("Referência ao TradingEngine configurada")
    
    def start(self):
        """Inicia o serviço de socket."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Timeout para permitir verificação de is_running
            self.is_running = True
            
            logger.info(f"[OK] Servico de Socket iniciado em {self.host}:{self.port}")
            logger.info(f"[INFO] Aguardando conexoes de EAs...")
            
            # Thread para enviar heartbeats periodicamente
            heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                name="HeartbeatSender",
                daemon=True
            )
            heartbeat_thread.start()
            
            # Loop principal: aceitar conexões
            while self.is_running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    
                    logger.info(f"[CONEXAO] NOVA CONEXAO ACEITA de {addr}")
                    
                    with self._lock:
                        self.clients.append(client_socket)
                        self.client_info[client_socket] = {
                            'address': addr,
                            'connected_at': datetime.now(),
                            'last_heartbeat': datetime.now()
                        }
                    
                    logger.info(f"[CLIENTE] EA conectado de {addr} (Total de clientes: {len(self.clients)})")
                    
                    # Thread dedicada para cada cliente
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr),
                        name=f"ClientHandler-{addr[0]}:{addr[1]}",
                        daemon=True
                    )
                    client_thread.start()
                    logger.info(f"[INFO] Thread de handler iniciada para {addr}")
                    
                except socket.timeout:
                    continue  # Timeout normal, verificar is_running
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Erro ao aceitar conexão: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Erro crítico ao iniciar servidor de socket: {e}")
            self.is_running = False
            raise
    
    def _handle_client(self, client_socket: socket.socket, addr):
        """Trata a comunicação com um cliente (EA) específico."""
        buffer = ""
        logger.info(f"[HANDLER] Handler iniciado para {addr} - aguardando mensagens...")
        
        try:
            while self.is_running:
                client_socket.settimeout(1.0)
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    
                    if not data:
                        logger.info(f"[DESCONEXAO] Cliente {addr} desconectou (dados vazios)")
                        break  # Cliente desconectou
                    
                    logger.info(f"[DADOS] Dados recebidos de {addr}: {len(data)} bytes - {data[:100]}")
                    buffer += data
                    
                    # Processar mensagens completas (separadas por \n)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                message = json.loads(line.strip())
                                self._process_message(message, client_socket)
                            except json.JSONDecodeError:
                                logger.warning(f"Mensagem JSON inválida de {addr}: {line[:50]}")
                                continue
                                
                except socket.timeout:
                    continue  # Timeout normal, continuar loop
                except Exception as e:
                    logger.error(f"Erro ao receber dados de {addr}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Erro ao comunicar com {addr}: {e}")
        finally:
            # Limpar cliente
            with self._lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
                if client_socket in self.client_info:
                    del self.client_info[client_socket]
            
            try:
                client_socket.close()
            except:
                pass
            
            logger.info(f"[DESCONEXAO] EA de {addr} desconectado")
    
    def _process_message(self, message: Dict[str, Any], client_socket: socket.socket):
        """Processa mensagens recebidas do EA."""
        msg_type = message.get("message_type")
        
        # Atualizar último heartbeat
        with self._lock:
            if client_socket in self.client_info:
                self.client_info[client_socket]['last_heartbeat'] = datetime.now()
        
        if msg_type == "HANDSHAKE":
            self._handle_handshake(message, client_socket)
            
        elif msg_type == "HANDSHAKE_CONFIRMED":
            self._handle_handshake_confirmed(message, client_socket)
            
        elif msg_type == "HEARTBEAT_ACK":
            logger.debug("Heartbeat ACK recebido")
            
        elif msg_type == "EXECUTION_REPORT":
            self._handle_execution_report(message)
            
        else:
            logger.warning(f"Tipo de mensagem desconhecido: {msg_type}")
    
    def _handle_handshake(self, message: Dict, client_socket: socket.socket):
        """
        Processa mensagem de handshake do EA.
        ETAPA 1/3 do PCA: Recebe HANDSHAKE e envia HANDSHAKE_ACK.
        """
        ea_name = message.get('ea_name', 'Unknown')
        version = message.get('version', 'Unknown')
        account = message.get('account', 'Unknown')
        
        logger.info(f"[PCA] ETAPA 1/3: HANDSHAKE recebido de {ea_name} v{version} | Conta: {account}")
        
        # Atualizar info do cliente
        with self._lock:
            if client_socket in self.client_info:
                self.client_info[client_socket]['ea_name'] = ea_name
                self.client_info[client_socket]['version'] = version
                self.client_info[client_socket]['account'] = account
                self.client_info[client_socket]['pca_state'] = 'ACK_SENT'  # Aguardando HANDSHAKE_CONFIRMED
        
        # ETAPA 2: Enviar HANDSHAKE_ACK
        response = {
            "message_type": "HANDSHAKE_ACK",
            "server_name": "Samsung Global Market Server",
            "version": "3.0.0",
            "status": "READY",
            "timestamp": int(time.time() * 1000)
        }
        
        self._send_to_client(client_socket, response)
        logger.info(f"[PCA] ETAPA 2/3: HANDSHAKE_ACK enviado para {ea_name}")
        logger.info(f"[PCA] Aguardando HANDSHAKE_CONFIRMED de {ea_name}...")
    
    def _handle_handshake_confirmed(self, message: Dict, client_socket: socket.socket):
        """
        Processa mensagem HANDSHAKE_CONFIRMED do EA.
        ETAPA 3/3 do PCA: Recebe HANDSHAKE_CONFIRMED e envia OK final.
        """
        ea_name = message.get('ea_name', 'Unknown')
        
        logger.info(f"[PCA] ETAPA 3/3: HANDSHAKE_CONFIRMED recebido de {ea_name}")
        
        # Atualizar estado do PCA no cliente
        with self._lock:
            if client_socket in self.client_info:
                self.client_info[client_socket]['pca_state'] = 'CONFIRMED'
        
        # Enviar OK final para confirmar conexão
        response = {
            "message_type": "OK",
            "status": "CONNECTION_ESTABLISHED",
            "timestamp": int(time.time() * 1000)
        }
        
        self._send_to_client(client_socket, response)
        logger.info(f"[PCA] OK enviado para {ea_name} - CONEXAO ESTABELECIDA")
    
    def _handle_execution_report(self, message: Dict):
        """Processa relatório de execução do EA."""
        status = message.get('status', 'UNKNOWN')
        order_ticket = message.get('order_ticket', 0)
        signal_id = message.get('original_signal_id', 'N/A')
        
        logger.info(f"[RELATORIO] Signal {signal_id}: {status} (Order #{order_ticket})")
        
        # Notificar TradingEngine sobre execução (se necessário)
        if self.trading_engine and hasattr(self.trading_engine, 'on_execution_report'):
            self.trading_engine.on_execution_report(message)
    
    def _heartbeat_loop(self):
        """Loop para enviar heartbeats periódicos para todos os clientes."""
        time.sleep(2)  # Aguardar conexões iniciais
        
        while self.is_running:
            try:
                with self._lock:
                    clients_to_send = list(self.clients)  # Copiar lista para evitar modificação durante iteração
                    client_count = len(clients_to_send)
                
                if clients_to_send:
                    heartbeat = {
                        "message_type": "HEARTBEAT",
                        "timestamp": int(time.time() * 1000),
                        "server_status": "ACTIVE"
                    }
                    
                    successful_sends = 0
                    for client in clients_to_send:
                        try:
                            # Verificar se cliente ainda está na lista (pode ter desconectado)
                            with self._lock:
                                if client not in self.clients:
                                    continue  # Cliente foi removido, pular
                            
                            self._send_to_client(client, heartbeat)
                            successful_sends += 1
                        except Exception as e:
                            logger.warning(f"[HEARTBEAT] Erro ao enviar para cliente: {e}")
                            # Cliente será removido no próximo ciclo pela thread handler
                    
                    if successful_sends > 0:
                        logger.info(f"[HEARTBEAT] Enviado para {successful_sends}/{client_count} cliente(s)")
                    elif client_count > 0:
                        logger.warning(f"[HEARTBEAT] Nenhum heartbeat enviado (todos desconectados?)")
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de heartbeat: {e}")
                time.sleep(self.heartbeat_interval)
    
    def _send_to_client(self, client_socket: socket.socket, message_dict: Dict):
        """Envia mensagem para um cliente específico."""
        try:
            message = json.dumps(message_dict, ensure_ascii=False) + '\n'
            client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            logger.warning(f"Erro ao enviar mensagem para cliente: {e}")
            raise
    
    def send_signal_to_clients(self, signal: Dict[str, Any]):
        """
        Envia sinal de trading para todos os EAs conectados.
        Chamado pelo TradingEngine quando um novo sinal é gerado.
        """
        if not self.is_running:
            return
        
        with self._lock:
            clients_to_send = list(self.clients)
        
        if not clients_to_send:
            logger.debug("Nenhum EA conectado. Sinal não enviado.")
            return
        
        # Formatar sinal para protocolo MT5
        mt5_signal = {
            "message_type": "SIGNAL",
            "id": signal.get('id', f"sgm_{int(time.time())}"),
            "symbol": signal.get('asset', signal.get('symbol', 'UNKNOWN')),
            "action": signal.get('action', 'UNKNOWN'),
            "volume": signal.get('volume', 0.01),
            "stop_loss": signal.get('stop_loss'),
            "take_profit": signal.get('take_profit'),
            "confidence": signal.get('confidence', 0.5),
            "timestamp": signal.get('timestamp', int(time.time() * 1000))
        }
        
        # Enviar para todos os clientes
        successful_sends = 0
        for client in clients_to_send:
            try:
                self._send_to_client(client, mt5_signal)
                successful_sends += 1
            except Exception:
                # Cliente será removido no próximo ciclo
                pass
        
        logger.info(f"[SINAL] Sinal enviado para {successful_sends}/{len(clients_to_send)} EA(s): {mt5_signal['id']}")
    
    def stop(self):
        """Para o serviço de socket."""
        logger.info("Parando serviço de socket...")
        self.is_running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Fechar todas as conexões de clientes
        with self._lock:
            for client in list(self.clients):
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
            self.client_info.clear()
        
        logger.info("[OK] Servico de Socket parado")

