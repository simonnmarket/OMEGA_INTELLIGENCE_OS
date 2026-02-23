#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO TÉCNICO DO SISTEMA PROMETHEUS v3.6
Gera relatório completo de integridade e prontidão operacional
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# --- CONFIGURAÇÕES ---
PROJECT_PATH = os.getcwd()
CONFIG_FILE = str(Path(PROJECT_PATH).parent.parent / "config.json")
LOG_FILE = "numeia_execution.jsonl"
HEARTBEAT_FILE = "executor_heartbeat.tmp"
REQUIRED_FILES = [
    "executor_emergency_v3.1.py",
    "backtest_intelligence_validation_v3.6.py",
    "executor_serial_v2.py"
]
BACKTEST_RESULTS_FILE = "backtest_validation_results_v3.6.csv"
COMPARISON_FILE = "validation_comparison_v3.6.csv"

def check_file_existence_and_content(filepath, is_json=False):
    """Verifica se o arquivo existe e, se for JSON, se é válido."""
    if not os.path.exists(filepath):
        return {"status": "MISSING", "content": None, "path": filepath}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            if is_json:
                content = json.load(f)
                return {"status": "OK", "content": content, "path": filepath, "size": os.path.getsize(filepath)}
            else:
                size = os.path.getsize(filepath)
                return {"status": "OK", "content": f"File exists, size: {size} bytes", "path": filepath, "size": size}
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "content": f"Invalid JSON: {str(e)}", "path": filepath}
    except Exception as e:
        return {"status": "ERROR", "content": str(e), "path": filepath}

def check_python_dependencies():
    """Lista as dependências e suas versões."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Filtrar dependências importantes
            important_deps = {}
            for line in result.stdout.split('\n'):
                if any(dep in line.lower() for dep in ['metatrader5', 'pandas', 'numpy', 'pydantic']):
                    parts = line.split()
                    if len(parts) >= 2:
                        important_deps[parts[0]] = parts[1]
            return {"status": "OK", "content": important_deps, "full_output": result.stdout}
        else:
            return {"status": "ERROR", "content": result.stderr}
    except subprocess.TimeoutExpired:
        return {"status": "ERROR", "content": "Timeout ao verificar dependências"}
    except Exception as e:
        return {"status": "ERROR", "content": str(e)}

def check_mt5_connection():
    """Verifica a conexão e status do MT5."""
    if not MT5_AVAILABLE:
        return {"status": "UNAVAILABLE", "content": "MetaTrader5 não instalado"}
    
    try:
        if not mt5.initialize():
            error = mt5.last_error()
            return {"status": "FAILED", "content": f"MT5 Initialize failed: {error}"}
        
        account_info = mt5.account_info()
        if account_info is None:
            mt5.shutdown()
            return {"status": "FAILED", "content": "Could not get account info."}
            
        terminal_info = mt5.terminal_info()
        
        # Verificar alguns símbolos
        test_symbols = ["XAUUSD", "EURUSD", "BTCUSD"]
        symbol_status = {}
        for symbol in test_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                tick = mt5.symbol_info_tick(symbol)
                symbol_status[symbol] = {
                    "available": True,
                    "tick_available": tick is not None,
                    "last_tick_time": tick.time if tick else None
                }
            else:
                symbol_status[symbol] = {"available": False}
        
        mt5.shutdown()
        
        return {
            "status": "OK",
            "content": {
                "account_login": account_info.login,
                "account_server": account_info.server,
                "account_balance": account_info.balance,
                "terminal_connected": terminal_info.connected if terminal_info else False,
                "trade_allowed": terminal_info.trade_allowed if terminal_info else False,
                "symbols_status": symbol_status
            }
        }
    except Exception as e:
        return {"status": "ERROR", "content": str(e)}

def check_backtest_results():
    """Verifica se há resultados do backtest e qual foi a decisão."""
    results = {
        "validation_results": check_file_existence_and_content(BACKTEST_RESULTS_FILE),
        "comparison_results": check_file_existence_and_content(COMPARISON_FILE)
    }
    
    decision = None
    if results["validation_results"]["status"] == "OK" and PANDAS_AVAILABLE:
        try:
            df = pd.read_csv(BACKTEST_RESULTS_FILE)
            if 'decision' in df.columns:
                decisions = df['decision'].unique()
                decision = list(decisions)
            elif 'filter_used' in df.columns:
                # Tentar inferir decisão da estrutura
                baseline = df[df['filter_used'] == False]
                with_filter = df[df['filter_used'] == True]
                if not baseline.empty and not with_filter.empty:
                    decision = "PENDING_ANALYSIS"
        except Exception as e:
            decision = f"Error reading CSV: {str(e)}"
    
    results["decision"] = decision
    return results

def main():
    report = {
        "report_timestamp": datetime.now().isoformat(),
        "project_path": PROJECT_PATH,
        "checks": {}
    }
    
    # 1. Integridade do Código-Fonte
    print("Verificando integridade do código-fonte...")
    report["checks"]["code_integrity"] = {}
    for file in REQUIRED_FILES:
        filepath = os.path.join(PROJECT_PATH, file)
        report["checks"]["code_integrity"][file] = check_file_existence_and_content(filepath)
    
    report["checks"]["dependencies"] = check_python_dependencies()
    report["checks"]["pandas_available"] = PANDAS_AVAILABLE
    report["checks"]["mt5_available"] = MT5_AVAILABLE
    
    # 2. Estado da Configuração
    print("Verificando configuração...")
    report["checks"]["configuration"] = check_file_existence_and_content(CONFIG_FILE, is_json=True)
    
    # 3. Conectividade e Pipeline de Dados
    print("Verificando conectividade MT5...")
    report["checks"]["mt5_connection"] = check_mt5_connection()
    
    log_path = os.path.join(PROJECT_PATH, LOG_FILE)
    report["checks"]["logging_system"] = check_file_existence_and_content(log_path)
    
    heartbeat_path = os.path.join(PROJECT_PATH, HEARTBEAT_FILE)
    report["checks"]["heartbeat_system"] = check_file_existence_and_content(heartbeat_path)
    
    # 4. Status da Validação Estratégica
    print("Verificando status da validação...")
    backtest_path = os.path.join(PROJECT_PATH, BACKTEST_RESULTS_FILE)
    report["checks"]["backtest_status"] = check_backtest_results()
    
    # 5. Prontidão para Execução (Resumo)
    print("Calculando prontidão para execução...")
    report["execution_readiness"] = "READY"
    blockers = []
    
    # Verificar bloqueadores críticos
    if not MT5_AVAILABLE:
        report["execution_readiness"] = "NOT_READY"
        blockers.append("MetaTrader5 não instalado")
    
    if report["checks"]["mt5_connection"]["status"] not in ["OK"]:
        report["execution_readiness"] = "NOT_READY"
        blockers.append(f"MT5 Connection: {report['checks']['mt5_connection']['status']}")
    
    if report["checks"]["configuration"]["status"] != "OK":
        report["execution_readiness"] = "NOT_READY"
        blockers.append(f"Config: {report['checks']['configuration']['status']}")
    
    # Verificar arquivos críticos
    critical_files = ["executor_emergency_v3.1.py", "backtest_intelligence_validation_v3.6.py"]
    for file in critical_files:
        if report["checks"]["code_integrity"].get(file, {}).get("status") != "OK":
            report["execution_readiness"] = "NOT_READY"
            blockers.append(f"Arquivo crítico ausente: {file}")
    
    report["blockers"] = blockers
    
    # Salvar o relatório
    output_file = os.path.join(PROJECT_PATH, "prometheus_system_status.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print(f"Relatório de diagnóstico gerado: {output_file}")
    print(f"Status de Prontidão: {report['execution_readiness']}")
    if blockers:
        print(f"Bloqueadores identificados: {len(blockers)}")
        for blocker in blockers:
            print(f"  - {blocker}")
    print("=" * 80)
    
    return report

if __name__ == "__main__":
    main()

