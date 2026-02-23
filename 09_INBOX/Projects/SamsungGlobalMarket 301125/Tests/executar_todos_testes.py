#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT MASTER - EXECUTA TODOS OS TESTES AUTOMATICAMENTE
Projeto Prometheus v3.0.0 | Samsung Global Market
Protocolo: Omega TIER-0

Este script executa todos os testes de validação quantitativa
sem depender do PowerShell Extension.
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Adicionar raiz do projeto ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print()

def check_server_running(host='127.0.0.1', port=5555):
    """Verifica se servidor está rodando"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print_header("PROTOCOLO DE VALIDACAO QUANTITATIVA - EXECUCAO AUTOMATICA")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projeto: Prometheus v3.0.0 | Samsung Global Market")
    
    # Verificar se servidor está rodando
    print("\n[ETAPA 0] Verificando se servidor Python esta rodando...")
    if check_server_running():
        print("  [OK] Servidor esta rodando na porta 5555")
    else:
        print("  [ERRO] Servidor NAO esta rodando na porta 5555")
        print("\n  Acoes necessarias:")
        print("  1. Abra uma janela PowerShell SEPARADA")
        print("  2. Execute: cd C:\\Users\\Lenovo\\.cursor\\SamsungGlobalMarket")
        print("  3. Execute: .\\Scripts\\start_main_server.ps1")
        print("  4. Aguarde mensagem: '[SUCESSO] TODOS OS SERVICOS INICIADOS'")
        print("  5. Execute este script novamente")
        return 1
    
    # ETAPA 1: Teste Quantitativo do Servidor
    print("\n[ETAPA 1] Executando teste quantitativo do servidor (50 testes)...")
    print("-" * 80)
    try:
        test1_path = os.path.join(project_root, "Tests", "test_server_quantitative.py")
        result = subprocess.run(
            [sys.executable, test1_path],
            cwd=project_root,
            capture_output=False,
            text=True
        )
        if result.returncode != 0:
            print(f"\n  [AVISO] Teste retornou codigo: {result.returncode}")
        else:
            print("\n  [OK] Teste quantitativo concluido")
    except Exception as e:
        print(f"  [ERRO] Falha ao executar teste: {e}")
        return 1
    
    input("\nPressione ENTER para continuar para ETAPA 2...")
    
    # ETAPA 2: Identificar arquivos .ex5 (via PowerShell, mas com tratamento de erro)
    print("\n[ETAPA 2] Identificando arquivos .ex5 do EA...")
    print("-" * 80)
    try:
        ps_script = os.path.join(project_root, "Scripts", "find_ex5_files.ps1")
        if os.path.exists(ps_script):
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        else:
            print("  [AVISO] Script PowerShell nao encontrado")
    except subprocess.TimeoutExpired:
        print("  [AVISO] Script PowerShell timeout (continuando...)")
    except Exception as e:
        print(f"  [AVISO] Erro ao executar script PowerShell: {e}")
        print("  (Isso nao e critico - continuando...)")
    
    input("\nPressione ENTER para continuar para ETAPA 3...")
    
    # ETAPA 3: Teste End-to-End
    print("\n[ETAPA 3] Executando teste end-to-end (simulacao completa de EA)...")
    print("  Duração: 100 segundos")
    print("  Esperado: >=9 heartbeats")
    print("-" * 80)
    try:
        test3_path = os.path.join(project_root, "Tests", "test_ea_server_connection.py")
        result = subprocess.run(
            [sys.executable, test3_path],
            cwd=project_root,
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            print("\n  [OK] Teste end-to-end PASSOU!")
        else:
            print(f"\n  [AVISO] Teste end-to-end retornou codigo: {result.returncode}")
    except Exception as e:
        print(f"  [ERRO] Falha ao executar teste: {e}")
        return 1
    
    # RESUMO FINAL
    print_header("RESUMO DO PROTOCOLO DE VALIDACAO")
    print("Todos os testes foram executados.")
    print("\nProximos passos:")
    print("  1. Revisar resultados de cada etapa acima")
    print("  2. Se todos os testes passaram, anexar EA ao MT5")
    print("  3. Validar que EA mostra versao 1.04 nos logs")
    print("  4. Verificar que EA recebe HANDSHAKE_ACK e heartbeats")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[AVISO] Teste interrompido pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

