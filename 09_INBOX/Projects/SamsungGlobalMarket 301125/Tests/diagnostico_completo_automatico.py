#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO COMPLETO AUTOMÁTICO DO SISTEMA
Projeto Prometheus v3.0.0 | Samsung Global Market

Este script executa TODOS os diagnósticos automaticamente e gera relatório completo.
SEM NECESSIDADE DE INTERVENÇÃO MANUAL.
"""

import socket
import json
import time
import sys
import os
import subprocess
from datetime import datetime

# Configurações
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# Cores para output (removidas para compatibilidade)
class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    CYAN = ''
    RESET = ''

def print_section(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def test_server_running():
    """Testa se servidor está rodando"""
    print_section("TESTE 1: SERVIDOR PYTHON ESTÁ RODANDO?")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((SERVER_HOST, SERVER_PORT))
        sock.close()
        
        if result == 0:
            print("[OK] Servidor está rodando na porta 5555")
            return True
        else:
            print("[ERRO] Servidor NÃO está rodando na porta 5555")
            print("\nSOLUÇÃO:")
            print("  Execute: .\\Scripts\\start_main_server.ps1")
            return False
    except Exception as e:
        print(f"[ERRO] Falha ao verificar servidor: {e}")
        return False

def test_connection_and_handshake():
    """Testa conexão e handshake completo"""
    print_section("TESTE 2: CONEXÃO E HANDSHAKE")
    
    try:
        # Conectar
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        start_time = time.time()
        sock.connect((SERVER_HOST, SERVER_PORT))
        connect_time = time.time() - start_time
        
        print(f"[OK] Conectado em {connect_time*1000:.1f}ms")
        
        # Enviar handshake
        handshake = {
            "message_type": "HANDSHAKE",
            "ea_name": "SamsungGlobalMarket_EA",
            "version": "1.05",
            "account": 510065181
        }
        message = json.dumps(handshake) + '\n'
        sock.sendall(message.encode('utf-8'))
        print("[OK] Handshake enviado")
        
        # Aguardar ACK
        buffer = b''
        start_time = time.time()
        ack_received = False
        
        while (time.time() - start_time) < 3.0:
            try:
                sock.settimeout(1)
                chunk = sock.recv(4096)
                if not chunk:
                    break
                    
                buffer += chunk
                
                if b'\n' in buffer:
                    message_bytes, buffer = buffer.split(b'\n', 1)
                    try:
                        message_dict = json.loads(message_bytes.decode('utf-8'))
                        if message_dict.get('message_type') == 'HANDSHAKE_ACK':
                            ack_time = time.time() - start_time
                            print(f"[OK] HANDSHAKE_ACK recebido em {ack_time*1000:.1f}ms")
                            print(f"     Servidor: {message_dict.get('server_name', 'N/A')}")
                            print(f"     Versão: {message_dict.get('version', 'N/A')}")
                            ack_received = True
                            break
                    except:
                        pass
            except socket.timeout:
                continue
        
        sock.close()
        
        if ack_received:
            return True
        else:
            print("[ERRO] HANDSHAKE_ACK não recebido em 3 segundos")
            return False
            
    except ConnectionRefusedError:
        print("[ERRO] Conexão recusada - servidor não está rodando")
        return False
    except Exception as e:
        print(f"[ERRO] Falha no teste: {e}")
        return False

def test_heartbeats(duration=30):
    """Testa recebimento de heartbeats"""
    print_section(f"TESTE 3: HEARTBEATS (duração: {duration}s)")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((SERVER_HOST, SERVER_PORT))
        
        # Handshake rápido
        handshake = {
            "message_type": "HANDSHAKE",
            "ea_name": "TestClient",
            "version": "1.05",
            "account": 123456
        }
        sock.sendall((json.dumps(handshake) + '\n').encode('utf-8'))
        
        # Aguardar ACK
        buffer = b''
        start = time.time()
        while (time.time() - start) < 3:
            try:
                chunk = sock.recv(4096)
                if chunk:
                    buffer += chunk
                    if b'HANDSHAKE_ACK' in buffer:
                        break
            except:
                pass
        
        # Agora testar heartbeats
        heartbeat_count = 0
        heartbeat_times = []
        test_start = time.time()
        buffer = b''
        
        print(f"Aguardando heartbeats por {duration} segundos...")
        
        while (time.time() - test_start) < duration:
            try:
                sock.settimeout(12)
                chunk = sock.recv(4096)
                if not chunk:
                    break
                    
                buffer += chunk
                
                while b'\n' in buffer:
                    message_bytes, buffer = buffer.split(b'\n', 1)
                    try:
                        message_dict = json.loads(message_bytes.decode('utf-8'))
                        if message_dict.get('message_type') == 'HEARTBEAT':
                            heartbeat_count += 1
                            elapsed = time.time() - test_start
                            heartbeat_times.append(elapsed)
                            print(f"  [{heartbeat_count}] Heartbeat recebido em T+{elapsed:.1f}s")
                    except:
                        pass
                        
            except socket.timeout:
                elapsed = time.time() - test_start
                if elapsed >= duration:
                    break
                continue
        
        sock.close()
        
        print(f"\nTotal de heartbeats recebidos: {heartbeat_count}")
        
        # Esperamos pelo menos 2 heartbeats em 30s (heartbeat a cada 10s)
        expected_min = max(1, int(duration / 10) - 1)
        
        if heartbeat_count >= expected_min:
            print(f"[OK] Heartbeats suficientes (esperado: >= {expected_min})")
            if heartbeat_count >= 2:
                intervals = [heartbeat_times[i] - heartbeat_times[i-1] 
                            for i in range(1, len(heartbeat_times))]
                avg_interval = sum(intervals) / len(intervals)
                print(f"     Intervalo médio: {avg_interval:.1f}s")
            return True
        else:
            print(f"[ERRO] Heartbeats insuficientes (recebidos: {heartbeat_count}, esperado: >= {expected_min})")
            return False
            
    except Exception as e:
        print(f"[ERRO] Falha no teste de heartbeats: {e}")
        return False

def check_mt5_files():
    """Verifica arquivos do MT5"""
    print_section("TESTE 4: ARQUIVOS DO MT5")
    
    mt5_path = os.path.expandvars(r"%APPDATA%\MetaQuotes\Terminal")
    results = {
        'mq5_exists': False,
        'ex5_exists': False,
        'mq5_path': '',
        'ex5_files': []
    }
    
    # Buscar arquivo .mq5
    if os.path.exists(mt5_path):
        for root, dirs, files in os.walk(mt5_path):
            if 'SamsungGlobalMarket_EA.mq5' in files:
                results['mq5_exists'] = True
                results['mq5_path'] = os.path.join(root, 'SamsungGlobalMarket_EA.mq5')
                break
    
    # Buscar arquivos .ex5
    if os.path.exists(mt5_path):
        for root, dirs, files in os.walk(mt5_path):
            if 'SamsungGlobalMarket_EA.ex5' in files:
                results['ex5_exists'] = True
                ex5_path = os.path.join(root, 'SamsungGlobalMarket_EA.ex5')
                results['ex5_files'].append(ex5_path)
    
    # Reportar resultados
    if results['mq5_exists']:
        print(f"[OK] Arquivo .mq5 encontrado:")
        print(f"     {results['mq5_path']}")
    else:
        print("[AVISO] Arquivo .mq5 NÃO encontrado no MT5")
        print("        Isso pode explicar problemas de compilação")
    
    if results['ex5_exists']:
        print(f"[OK] {len(results['ex5_files'])} arquivo(s) .ex5 encontrado(s):")
        for ex5 in results['ex5_files']:
            mtime = os.path.getmtime(ex5)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"     {ex5}")
            print(f"        Última modificação: {mtime_str}")
    else:
        print("[AVISO] Nenhum arquivo .ex5 encontrado")
        print("        EA pode não ter sido compilado ainda")
    
    return results

def generate_report(results):
    """Gera relatório final"""
    print_section("RELATÓRIO FINAL DE DIAGNÓSTICO")
    
    print(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nRESULTADOS:")
    print(f"  1. Servidor rodando:        {'[OK]' if results['server'] else '[ERRO]'}")
    print(f"  2. Conexão e Handshake:     {'[OK]' if results['handshake'] else '[ERRO]'}")
    print(f"  3. Heartbeats:              {'[OK]' if results['heartbeats'] else '[ERRO]'}")
    print(f"  4. Arquivos MT5 (.mq5):     {'[OK]' if results['files']['mq5_exists'] else '[AVISO]'}")
    print(f"  5. Arquivos MT5 (.ex5):     {'[OK]' if results['files']['ex5_exists'] else '[AVISO]'}")
    
    all_ok = results['server'] and results['handshake'] and results['heartbeats']
    
    print("\n" + "=" * 80)
    
    if all_ok:
        print("CONCLUSÃO: SERVIDOR ESTÁ 100% FUNCIONAL")
        print("\nO problema provavelmente está no EA ou na forma como ele se conecta.")
        print("\nPRÓXIMOS PASSOS:")
        print("  1. Certifique-se que EA versão 1.05 está compilado")
        print("  2. Anexe EA ao MT5")
        print("  3. Verifique logs do EA para erros")
        print("  4. Verifique se EA mostra versão 1.05 no log de inicialização")
    else:
        print("CONCLUSÃO: PROBLEMAS DETECTADOS NO SERVIDOR")
        print("\nAÇÕES NECESSÁRIAS:")
        if not results['server']:
            print("  - Iniciar servidor Python: .\\Scripts\\start_main_server.ps1")
        if not results['handshake']:
            print("  - Verificar logs do servidor para erros de handshake")
        if not results['heartbeats']:
            print("  - Verificar thread de heartbeat no servidor")
    
    print("=" * 80)
    
    return all_ok

def main():
    print("=" * 80)
    print(" DIAGNÓSTICO COMPLETO AUTOMÁTICO DO SISTEMA")
    print(" Projeto Prometheus v3.0.0 | Samsung Global Market")
    print("=" * 80)
    print(f"\nIniciando diagnóstico em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'server': False,
        'handshake': False,
        'heartbeats': False,
        'files': {}
    }
    
    # Executar testes
    results['server'] = test_server_running()
    
    if results['server']:
        results['handshake'] = test_connection_and_handshake()
        
        if results['handshake']:
            results['heartbeats'] = test_heartbeats(30)  # 30 segundos de teste
    
    results['files'] = check_mt5_files()
    
    # Gerar relatório
    all_ok = generate_report(results)
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[AVISO] Diagnóstico interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

