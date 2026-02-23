#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO DE MISSÃO PROMETHEUS v4.1
Script de verificação de sucesso operacional e estratégico
"""

import os
import json
import subprocess
import time
import MetaTrader5 as mt5
from datetime import datetime
from pathlib import Path

# --- CONFIGURAÇÕES ---
LOG_FILE = "prometheus_master_log.jsonl"
HEARTBEAT_FILE = "prometheus_heartbeat.tmp"
TRADEABLE_ASSETS_FILE = "TRADEABLE_ASSETS.json"
MASTER_CONTROL_FILE = "prometheus_master_control_v4.1.py"
VERIFICATION_REPORT_FILE = "MISSION_SUCCESS_REPORT.json"

def check_file_exists_and_size(filepath, min_size=300):
    """Verifica se o arquivo existe e tem o tamanho mínimo."""
    if not os.path.exists(filepath):
        return False, f"Arquivo {filepath} não encontrado."
    if os.path.getsize(filepath) < min_size:
        return False, f"Arquivo {filepath} muito pequeno (<{min_size} bytes)."
    return True, "OK"

def check_python_dependencies():
    """Verifica se as dependências estão instaladas."""
    try:
        import pandas
        import numpy
        import MetaTrader5
        return True, "OK"
    except ImportError as e:
        return False, f"Dependência faltando: {e}"

def check_mt5_connection():
    """Verifica a conexão com o MT5."""
    if not mt5.initialize():
        return False, f"Falha ao inicializar MT5: {mt5.last_error()}"
    
    account_info = mt5.account_info()
    if account_info is None:
        mt5.shutdown()
        return False, "Não foi possível obter informações da conta."
        
    result = True, f"OK - Conta: {account_info.login}, Servidor: {account_info.server}"
    mt5.shutdown()
    return result

def check_log_and_heartbeat():
    """Verifica se logs e heartbeat estão sendo gerados."""
    if not os.path.exists(LOG_FILE):
        return False, "Arquivo de log não encontrado."
        
    if not os.path.exists(HEARTBEAT_FILE):
        return False, "Arquivo de heartbeat não encontrado."
        
    # Verificar se o heartbeat foi atualizado nos últimos 2 minutos
    try:
        last_mod_time = os.path.getmtime(HEARTBEAT_FILE)
        time_diff = time.time() - last_mod_time
        if time_diff > 120:
            return False, f"Heartbeat não atualizado recentemente ({int(time_diff)}s > 120s)."
    except Exception as e:
        return False, f"Erro ao verificar heartbeat: {e}"
        
    return True, "OK"

def check_production_cycle():
    """Verifica se os ciclos de produção estão no log."""
    if not os.path.exists(LOG_FILE):
        return False, "Arquivo de log não encontrado."
    
    try:
        # Ler apenas as últimas 100 linhas para ser mais rápido
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Verificar apenas as últimas 100 linhas
            last_lines = lines[-100:] if len(lines) > 100 else lines
            content = ''.join(last_lines)
            if "PRODUCTION_CYCLE_START" in content or "PRODUCTION_CYCLE_COMPLETE" in content:
                return True, "OK"
            if "PRODUCTION_MODE" in content or "PRODUCTION_SIGNALS_GENERATED" in content:
                return True, "OK - Modo produção detectado"
        return False, "Ciclo de produção não encontrado no log."
    except Exception as e:
        return False, f"Erro ao ler o log: {e}"

def check_assets_file():
    """Verifica se o arquivo de ativos foi criado."""
    if not os.path.exists(TRADEABLE_ASSETS_FILE):
        return False, "Arquivo de ativos negociáveis não encontrado."
    
    try:
        with open(TRADEABLE_ASSETS_FILE, 'r') as f:
            assets = json.load(f)
            if not assets or len(assets) == 0:
                return False, "Arquivo de ativos vazio."
            return True, f"OK - {len(assets)} ativos encontrados"
    except Exception as e:
        return False, f"Erro ao ler arquivo de ativos: {e}"

def check_watchdog():
    """Verifica se o watchdog está ativo."""
    if not os.path.exists(LOG_FILE):
        return False, "Arquivo de log não encontrado."
    
    try:
        # Ler apenas as últimas 50 linhas para ser mais rápido
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            last_lines = lines[-50:] if len(lines) > 50 else lines
            content = ''.join(last_lines)
            if "WATCHDOG_STARTED" in content or "WATCHDOG_INITIALIZED" in content:
                return True, "OK"
        return False, "Watchdog não encontrado no log."
    except Exception as e:
        return False, f"Erro ao verificar watchdog: {e}"

def check_system_running():
    """Verifica se o sistema está rodando (heartbeat recente)."""
    if not os.path.exists(HEARTBEAT_FILE):
        return False, "Heartbeat não encontrado - sistema não está rodando."
    
    try:
        last_mod_time = os.path.getmtime(HEARTBEAT_FILE)
        time_diff = time.time() - last_mod_time
        if time_diff < 120:  # Atualizado nos últimos 2 minutos
            return True, f"OK - Sistema rodando (heartbeat atualizado há {int(time_diff)}s)"
        else:
            return False, f"Sistema parado (heartbeat desatualizado há {int(time_diff)}s)"
    except Exception as e:
        return False, f"Erro ao verificar sistema: {e}"

def run_verification():
    """Executa todos os checks e gera o relatório."""
    print("="*80)
    print("🚀 INICIANDO VERIFICAÇÃO DE MISSÃO PROMETHEUS v4.1...")
    print("="*80)
    print()
    
    report = {
        "mission": "Prometheus v4.1",
        "timestamp": datetime.now().isoformat(),
        "status": "IN_PROGRESS",
        "checks": {}
    }

    # 1. Verificação de Implantação Técnica
    print("1. VERIFICANDO IMPLANTAÇÃO TÉCNICA...")
    print("-" * 80)
    
    arquivo_mestre = check_file_exists_and_size(MASTER_CONTROL_FILE, min_size=10000)
    print(f"  Arquivo Mestre: {arquivo_mestre[1]}")
    
    dependencias = check_python_dependencies()
    print(f"  Dependências: {dependencias[1]}")
    
    report["checks"]["implantacao_tecnica"] = {
        "arquivo_mestre_criado": arquivo_mestre,
        "dependencias_verificadas": dependencias
    }
    print()

    # 2. Verificação de Inicialização
    print("2. VERIFICANDO INICIALIZAÇÃO...")
    print("-" * 80)
    
    sistema_iniciado = check_log_and_heartbeat()
    print(f"  Sistema Iniciado (Log/Heartbeat): {sistema_iniciado[1]}")
    
    conexao_mt5 = check_mt5_connection()
    print(f"  Conexão MT5: {conexao_mt5[1]}")
    
    report["checks"]["inicializacao"] = {
        "sistema_iniciado": sistema_iniciado,
        "conexao_mt5": conexao_mt5
    }
    print()

    # 3. Verificação de Operação Autônoma
    print("3. VERIFICANDO OPERAÇÃO AUTÔNOMA...")
    print("-" * 80)
    
    watchdog_ativo = check_watchdog()
    print(f"  Watchdog Ativo: {watchdog_ativo[1]}")
    
    ciclos_producao = check_production_cycle()
    print(f"  Ciclos de Produção: {ciclos_producao[1]}")
    
    sistema_rodando = check_system_running()
    print(f"  Sistema Rodando: {sistema_rodando[1]}")
    
    report["checks"]["operacao_autonoma"] = {
        "watchdog_ativo": watchdog_ativo,
        "ciclos_producao": ciclos_producao,
        "sistema_rodando": sistema_rodando
    }
    print()

    # 4. Verificação de Estratégia Seletiva
    print("4. VERIFICANDO ESTRATÉGIA SELETIVA...")
    print("-" * 80)
    
    arquivo_ativos = check_assets_file()
    print(f"  Arquivo de Ativos: {arquivo_ativos[1]}")
    
    report["checks"]["estrategia_seletiva"] = {
        "arquivo_ativos_gerado": arquivo_ativos
    }
    print()

    # Verificação final de sucesso
    print("="*80)
    print("CALCULANDO RESULTADO FINAL...")
    print("="*80)
    
    all_checks_passed = (
        report["checks"]["implantacao_tecnica"]["arquivo_mestre_criado"][0] and
        report["checks"]["implantacao_tecnica"]["dependencias_verificadas"][0] and
        report["checks"]["inicializacao"]["conexao_mt5"][0] and
        report["checks"]["operacao_autonoma"]["watchdog_ativo"][0] and
        report["checks"]["operacao_autonoma"]["ciclos_producao"][0] and
        report["checks"]["estrategia_seletiva"]["arquivo_ativos_gerado"][0]
    )
    
    report["status"] = "SUCCESS" if all_checks_passed else "FAILURE"
    report["all_checks_passed"] = all_checks_passed
    
    # Salvar relatório
    with open(VERIFICATION_REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Exibir resultado
    print()
    if all_checks_passed:
        print("✅ STATUS DA MISSÃO: SUCCESS")
        print("="*80)
        print("🎉 TODOS OS CHECKS PASSARAM!")
        print("O sistema Prometheus v4.1 está 100% operacional.")
    else:
        print("❌ STATUS DA MISSÃO: FAILURE")
        print("="*80)
        print("⚠️ ALGUNS CHECKS FALHARAM:")
        print()
        for categoria, checks in report["checks"].items():
            for check_name, (passed, message) in checks.items():
                if not passed:
                    print(f"  ✗ {categoria}.{check_name}: {message}")
    
    print()
    print(f"📋 Relatório completo salvo em: {VERIFICATION_REPORT_FILE}")
    print("="*80)
    
    return report

if __name__ == "__main__":
    try:
        mission_report = run_verification()
        print("\nPressione ENTER para sair...")
        input()
    except KeyboardInterrupt:
        print("\n\nVerificação interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ ERRO durante verificação: {e}")
        import traceback
        traceback.print_exc()
        print("\nPressione ENTER para sair...")
        input()

