#!/usr/bin/env python3
"""
Verificação Completa do Sistema - Numeia v2.0
Verifica se o sistema está 100% operacional
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

OK = "[OK]"
ERRO = "[ERRO]"
AVISO = "[AVISO]"
INFO = "[INFO]"

def verificar_processos_python():
    """Verifica se há processos Python rodando"""
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        processos = [l for l in lines if 'python.exe' in l and 'tasklist' not in l.lower()]
        return len(processos) > 0, processos
    except:
        return False, []

def verificar_arquivo_config():
    """Verifica se o arquivo de configuração existe e é válido"""
    base_dir = Path(__file__).parent.parent.parent
    config_file = base_dir / "config.json"
    
    if not config_file.exists():
        return False, f"Config não encontrado: {config_file}", None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return True, "Config válido", config
    except Exception as e:
        return False, f"Erro ao ler config: {e}", None

def verificar_mt5_conexao():
    """Verifica se MetaTrader 5 está acessível"""
    try:
        import MetaTrader5 as mt5
        if mt5.initialize():
            account_info = mt5.account_info()
            mt5.shutdown()
            if account_info:
                return True, account_info
            return False, None
        return False, None
    except ImportError:
        return None, "MetaTrader5 não instalado"
    except Exception as e:
        return False, str(e)

def verificar_geracao_sinais():
    """Verifica se o sistema consegue gerar sinais"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from numeia_executor_v2 import Config, SignalGenerator, CapitalManagement, load_config
        import MetaTrader5 as mt5
        
        # Carregar config
        config = load_config()
        
        # Conectar MT5
        if not mt5.initialize():
            mt5.shutdown()
            return False, "MT5 não conectado", []
        
        # Criar SignalGenerator
        capital_manager = CapitalManagement(config)
        signal_generator = SignalGenerator(config.TRADING_SYMBOLS, capital_manager, config)
        
        # Gerar sinais
        tasks = signal_generator.generate_signals()
        
        mt5.shutdown()
        
        return True, f"{len(tasks)} sinais gerados", tasks
    except Exception as e:
        return False, str(e), []

def verificar_logs_recentes():
    """Verifica se há logs recentes sendo gerados"""
    log_file = Path(__file__).parent / "numeia_execution.jsonl"
    
    if not log_file.exists():
        return False, "Log não encontrado", None
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return False, "Log vazio", None
        
        # Ler última linha
        last_line = lines[-1].strip()
        try:
            log_entry = json.loads(last_line)
            
            # Verificar se é recente (últimos 5 minutos)
            if 'time' in log_entry:
                try:
                    log_time = datetime.fromisoformat(log_entry['time'].replace('+0100', '+01:00'))
                    now = datetime.now()
                    diff = (now - log_time).total_seconds()
                    is_recent = diff < 300  # 5 minutos
                    return is_recent, f"Última entrada há {int(diff)} segundos", log_entry
                except:
                    pass
            
            return True, f"Log ativo ({len(lines)} linhas)", log_entry
        except:
            return True, f"Log existe ({len(lines)} linhas)", None
    except Exception as e:
        return False, str(e), None

def verificar_porta_prometheus():
    """Verifica se o servidor Prometheus está rodando"""
    try:
        import requests
        response = requests.get('http://localhost:8000/metrics', timeout=2)
        if response.status_code == 200:
            return True, f"Métricas disponíveis ({len(response.text.split(chr(10)))} linhas)"
        return False, f"Porta respondeu com código {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Servidor não encontrado (normal se sistema não estiver rodando)"
    except ImportError:
        return None, "requests não disponível"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("VERIFICAÇÃO COMPLETA DO SISTEMA - Numeia v2.0")
    print("=" * 70)
    print()
    
    resultados = {}
    
    # 1. Verificar processos Python
    print(f"{INFO} [1/6] Verificando processos Python...")
    tem_processos, processos = verificar_processos_python()
    if tem_processos:
        print(f"{OK} {len(processos)} processo(s) Python encontrado(s)")
        resultados['processos'] = True
    else:
        print(f"{AVISO} Nenhum processo Python encontrado (sistema pode não estar rodando)")
        resultados['processos'] = False
    print()
    
    # 2. Verificar arquivo de configuração
    print(f"{INFO} [2/6] Verificando arquivo de configuração...")
    config_ok, msg_config, config_data = verificar_arquivo_config()
    if config_ok:
        print(f"{OK} {msg_config}")
        print(f"    - Símbolos: {len(config_data.get('TRADING_SYMBOLS', []))}")
        print(f"    - MAX_SPREAD_PIPS: {config_data.get('MAX_SPREAD_PIPS', 'Não configurado')}")
        resultados['config'] = True
    else:
        print(f"{ERRO} {msg_config}")
        resultados['config'] = False
    print()
    
    # 3. Verificar conexão MT5
    print(f"{INFO} [3/6] Verificando conexão MetaTrader 5...")
    mt5_status, mt5_info = verificar_mt5_conexao()
    if mt5_status is True:
        print(f"{OK} MT5 conectado")
        print(f"    - Conta: {mt5_info.login}")
        print(f"    - Servidor: {mt5_info.server}")
        print(f"    - Saldo: {mt5_info.balance}")
        resultados['mt5'] = True
    elif mt5_status is None:
        print(f"{AVISO} {mt5_info}")
        resultados['mt5'] = None
    else:
        print(f"{ERRO} MT5 não conectado: {mt5_info}")
        resultados['mt5'] = False
    print()
    
    # 4. Verificar geração de sinais
    print(f"{INFO} [4/6] Verificando geração de sinais...")
    sinais_ok, msg_sinais, tasks = verificar_geracao_sinais()
    if sinais_ok:
        if len(tasks) > 0:
            print(f"{OK} {msg_sinais}")
            for task in tasks[:3]:  # Mostrar primeiros 3
                print(f"    - {task.symbol}: {task.action} {task.volume} @ {task.price}")
            resultados['sinais'] = True
        else:
            print(f"{AVISO} Sistema funcional mas nenhum sinal gerado (spreads podem estar altos)")
            resultados['sinais'] = None
    else:
        print(f"{ERRO} Erro ao gerar sinais: {msg_sinais}")
        resultados['sinais'] = False
    print()
    
    # 5. Verificar logs recentes
    print(f"{INFO} [5/6] Verificando logs recentes...")
    log_ok, msg_log, log_entry = verificar_logs_recentes()
    if log_ok:
        print(f"{OK} {msg_log}")
        if log_entry and 'event' in log_entry:
            print(f"    - Último evento: {log_entry.get('event', 'N/A')}")
        resultados['logs'] = True
    else:
        print(f"{AVISO} {msg_log}")
        resultados['logs'] = False
    print()
    
    # 6. Verificar Prometheus
    print(f"{INFO} [6/6] Verificando servidor Prometheus...")
    prom_status, msg_prom = verificar_porta_prometheus()
    if prom_status:
        print(f"{OK} {msg_prom}")
        resultados['prometheus'] = True
    elif prom_status is None:
        print(f"{AVISO} {msg_prom}")
        resultados['prometheus'] = None
    else:
        print(f"{AVISO} {msg_prom}")
        resultados['prometheus'] = False
    print()
    
    # Resumo final
    print("=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    
    total = len(resultados)
    sucesso = sum(1 for v in resultados.values() if v is True)
    aviso = sum(1 for v in resultados.values() if v is None)
    erro = sum(1 for v in resultados.values() if v is False)
    
    for nome, resultado in resultados.items():
        if resultado is True:
            status = OK
        elif resultado is None:
            status = AVISO
        else:
            status = ERRO
        print(f"{status} {nome.upper()}")
    
    print()
    print(f"Total: {sucesso}/{total} verificações passaram")
    
    # Diagnóstico final
    print()
    print("=" * 70)
    print("DIAGNÓSTICO")
    print("=" * 70)
    
    if erro > 0:
        print(f"\n{ERRO} {erro} problema(s) crítico(s) encontrado(s)")
        print("Sistema NÃO está 100% operacional")
    elif aviso > 0:
        if resultados.get('sinais') is None and resultados.get('processos') is False:
            print(f"\n{AVISO} Sistema funcional mas não está rodando")
            print("Execute: python numeia_executor_v2.py")
        else:
            print(f"\n{AVISO} Sistema funcional mas com {aviso} aviso(s)")
            print("Sistema está OPERACIONAL com ressalvas")
    else:
        if resultados.get('sinais') and len(tasks) > 0:
            print(f"\n{OK} Sistema está 100% OPERACIONAL!")
            print("Todos os componentes funcionando corretamente")
            print(f"Sistema gerando {len(tasks)} sinais")
        else:
            print(f"\n{OK} Sistema está OPERACIONAL!")
            print("Todos os componentes funcionando corretamente")
    
    print()

if __name__ == "__main__":
    main()

