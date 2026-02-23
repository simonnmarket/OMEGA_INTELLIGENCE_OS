#!/usr/bin/env python3
"""
Script de Verificação de Status - Numeia v2.0
Verifica se o sistema está funcionando corretamente
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

OK = "[OK]"
ERRO = "[ERRO]"
AVISO = "[AVISO]"
INFO = "[INFO]"

def verificar_processos_python():
    """Verifica se há processos Python rodando"""
    print(f"{INFO} Verificando processos Python...")
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        processos = [l for l in lines if 'python.exe' in l]
        if processos:
            print(f"{OK} Processos Python encontrados: {len(processos)}")
            for proc in processos:
                print(f"  - {proc.strip()}")
            return True
        else:
            print(f"{AVISO} Nenhum processo Python encontrado")
            return False
    except Exception as e:
        print(f"{ERRO} Erro ao verificar processos: {e}")
        return False

def verificar_arquivos_log():
    """Verifica se há arquivos de log sendo gerados"""
    print(f"\n{INFO} Verificando arquivos de log...")
    log_dir = Path(__file__).parent
    log_file = log_dir / "numeia_execution.jsonl"
    
    if log_file.exists():
        # Ler última linha do log
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    try:
                        log_entry = json.loads(last_line)
                        print(f"{OK} Log encontrado: {log_file}")
                        print(f"  - Última entrada: {log_entry.get('time', 'N/A')}")
                        print(f"  - Evento: {log_entry.get('event', 'N/A')}")
                        print(f"  - Total de linhas: {len(lines)}")
                        
                        # Verificar se há entradas recentes (últimos 5 minutos)
                        if 'time' in log_entry:
                            try:
                                log_time = datetime.fromisoformat(log_entry['time'].replace('+0100', '+01:00'))
                                now = datetime.now()
                                diff = (now - log_time).total_seconds()
                                if diff < 300:  # 5 minutos
                                    print(f"{OK} Log ativo (última entrada há {int(diff)} segundos)")
                                    return True
                                else:
                                    print(f"{AVISO} Log inativo (última entrada há {int(diff/60)} minutos)")
                                    return False
                            except:
                                pass
                        return True
                    except json.JSONDecodeError:
                        print(f"{AVISO} Log existe mas formato inválido na última linha")
                        return False
                else:
                    print(f"{AVISO} Log existe mas está vazio")
                    return False
        except Exception as e:
            print(f"{ERRO} Erro ao ler log: {e}")
            return False
    else:
        print(f"{AVISO} Arquivo de log não encontrado: {log_file}")
        return False

def verificar_arquivo_config():
    """Verifica se o arquivo de configuração existe e é válido"""
    print(f"\n{INFO} Verificando arquivo de configuração...")
    base_dir = Path(__file__).parent.parent.parent
    config_file = base_dir / "config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"{OK} Config encontrado: {config_file}")
            print(f"  - EMERGENCY_MODE_ENABLED: {config.get('EMERGENCY_MODE_ENABLED')}")
            print(f"  - EXECUTION_CYCLE_SECONDS: {config.get('EXECUTION_CYCLE_SECONDS')}")
            print(f"  - Símbolos: {len(config.get('TRADING_SYMBOLS', []))}")
            return True
        except Exception as e:
            print(f"{ERRO} Erro ao ler config: {e}")
            return False
    else:
        print(f"{ERRO} Config não encontrado: {config_file}")
        return False

def verificar_mt5_conexao():
    """Verifica se MetaTrader 5 está acessível"""
    print(f"\n{INFO} Verificando conexão MetaTrader 5...")
    try:
        import MetaTrader5 as mt5
        if mt5.initialize():
            account_info = mt5.account_info()
            if account_info:
                print(f"{OK} MetaTrader 5 conectado")
                print(f"  - Conta: {account_info.login}")
                print(f"  - Servidor: {account_info.server}")
                print(f"  - Saldo: {account_info.balance}")
                mt5.shutdown()
                return True
            else:
                print(f"{AVISO} MetaTrader 5 inicializado mas sem informações da conta")
                mt5.shutdown()
                return False
        else:
            print(f"{ERRO} Falha ao inicializar MetaTrader 5")
            print(f"  - Erro: {mt5.last_error()}")
            return False
    except ImportError:
        print(f"{ERRO} MetaTrader5 não instalado: pip install MetaTrader5")
        return False
    except Exception as e:
        print(f"{ERRO} Erro ao conectar MT5: {e}")
        return False

def verificar_porta_prometheus():
    """Verifica se o servidor Prometheus está rodando"""
    print(f"\n{INFO} Verificando servidor Prometheus...")
    try:
        import requests
        response = requests.get('http://localhost:8000/metrics', timeout=2)
        if response.status_code == 200:
            print(f"{OK} Servidor Prometheus ativo na porta 8000")
            lines = response.text.split('\n')
            print(f"  - Métricas disponíveis: {len(lines)} linhas")
            return True
        else:
            print(f"{AVISO} Porta 8000 respondeu mas com código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{AVISO} Servidor Prometheus não encontrado na porta 8000")
        print(f"  - Isso é normal se o sistema ainda não iniciou")
        return False
    except ImportError:
        print(f"{AVISO} Biblioteca 'requests' não disponível para verificação")
        return None
    except Exception as e:
        print(f"{AVISO} Erro ao verificar Prometheus: {e}")
        return False

def main():
    print("=" * 70)
    print("VERIFICAÇÃO DE STATUS - Numeia v2.0")
    print("=" * 70)
    print()
    
    resultados = {
        "processos": verificar_processos_python(),
        "log": verificar_arquivos_log(),
        "config": verificar_arquivo_config(),
        "mt5": verificar_mt5_conexao(),
        "prometheus": verificar_porta_prometheus()
    }
    
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    
    total = len(resultados)
    sucesso = sum(1 for v in resultados.values() if v is True)
    
    for nome, resultado in resultados.items():
        status = OK if resultado else (AVISO if resultado is None else ERRO)
        print(f"{status} {nome.upper()}")
    
    print(f"\nResultado: {sucesso}/{total} verificações passaram")
    
    # Diagnóstico
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO")
    print("=" * 70)
    
    if not resultados["processos"]:
        print(f"\n{AVISO} Nenhum processo Python encontrado")
        print("  - O sistema pode não estar rodando")
        print("  - Execute: python numeia_executor_v2.py")
    elif not resultados["log"]:
        print(f"\n{AVISO} Nenhum log ativo encontrado")
        print("  - O sistema pode ter iniciado mas não está gerando logs")
        print("  - Verifique erros no console")
    elif resultados["log"]:
        print(f"\n{OK} Sistema parece estar funcionando!")
        print("  - Logs ativos detectados")
        print("  - Verifique o arquivo numeia_execution.jsonl para detalhes")
    
    if not resultados["mt5"]:
        print(f"\n{ERRO} MetaTrader 5 não conectado")
        print("  - Abra o MetaTrader 5 e conecte à sua conta")
        print("  - Verifique se a API está habilitada")
    
    if resultados["prometheus"]:
        print(f"\n{OK} Servidor de métricas ativo")
        print("  - Acesse: http://localhost:8000/metrics")
    
    print()

if __name__ == "__main__":
    main()

