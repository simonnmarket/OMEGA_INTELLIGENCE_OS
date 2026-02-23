#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO RÁPIDA DE MISSÃO PROMETHEUS v4.1
Versão otimizada para execução rápida
"""

import os
import json
from datetime import datetime
from pathlib import Path

# --- CONFIGURAÇÕES ---
LOG_FILE = "prometheus_master_log.jsonl"
HEARTBEAT_FILE = "prometheus_heartbeat.tmp"
TRADEABLE_ASSETS_FILE = "TRADEABLE_ASSETS.json"
MASTER_CONTROL_FILE = "prometheus_master_control_v4.1.py"
VERIFICATION_REPORT_FILE = "MISSION_SUCCESS_REPORT.json"

def verificar_rapido():
    """Verificação rápida sem ler arquivos grandes."""
    print("="*80)
    print("🚀 VERIFICAÇÃO RÁPIDA DE MISSÃO PROMETHEUS v4.1")
    print("="*80)
    print()
    
    report = {
        "mission": "Prometheus v4.1",
        "timestamp": datetime.now().isoformat(),
        "status": "IN_PROGRESS",
        "checks": {}
    }
    
    # 1. Arquivo Mestre
    print("1. Arquivo Mestre...", end=" ")
    if os.path.exists(MASTER_CONTROL_FILE):
        size = os.path.getsize(MASTER_CONTROL_FILE)
        print(f"✓ OK ({size:,} bytes)")
        report["checks"]["arquivo_mestre"] = (True, "OK")
    else:
        print("✗ NÃO ENCONTRADO")
        report["checks"]["arquivo_mestre"] = (False, "Não encontrado")
    
    # 2. Dependências
    print("2. Dependências Python...", end=" ")
    try:
        import pandas, numpy, MetaTrader5
        print("✓ OK")
        report["checks"]["dependencias"] = (True, "OK")
    except ImportError as e:
        print(f"✗ ERRO: {e}")
        report["checks"]["dependencias"] = (False, str(e))
    
    # 3. MT5
    print("3. Conexão MT5...", end=" ")
    try:
        import MetaTrader5 as mt5
        if mt5.initialize():
            account = mt5.account_info()
            if account:
                print(f"✓ OK (Conta: {account.login})")
                report["checks"]["mt5"] = (True, f"Conta: {account.login}")
            else:
                print("⚠ Inicializado sem conta")
                report["checks"]["mt5"] = (False, "Sem informações da conta")
            mt5.shutdown()
        else:
            print(f"✗ ERRO: {mt5.last_error()}")
            report["checks"]["mt5"] = (False, str(mt5.last_error()))
    except Exception as e:
        print(f"✗ ERRO: {e}")
        report["checks"]["mt5"] = (False, str(e))
    
    # 4. Arquivo de Ativos
    print("4. Arquivo de Ativos...", end=" ")
    if os.path.exists(TRADEABLE_ASSETS_FILE):
        try:
            with open(TRADEABLE_ASSETS_FILE, 'r') as f:
                assets = json.load(f)
            print(f"✓ OK ({len(assets)} ativos)")
            report["checks"]["arquivo_ativos"] = (True, f"{len(assets)} ativos")
        except:
            print("⚠ Arquivo existe mas com erro")
            report["checks"]["arquivo_ativos"] = (False, "Erro ao ler")
    else:
        print("✗ NÃO ENCONTRADO (execute discovery primeiro)")
        report["checks"]["arquivo_ativos"] = (False, "Não encontrado")
    
    # 5. Heartbeat
    print("5. Heartbeat...", end=" ")
    if os.path.exists(HEARTBEAT_FILE):
        import time
        try:
            last_mod = os.path.getmtime(HEARTBEAT_FILE)
            age = time.time() - last_mod
            if age < 120:
                print(f"✓ OK (atualizado há {int(age)}s)")
                report["checks"]["heartbeat"] = (True, f"Atualizado há {int(age)}s")
            else:
                print(f"⚠ Desatualizado ({int(age)}s)")
                report["checks"]["heartbeat"] = (False, f"Desatualizado há {int(age)}s")
        except:
            print("⚠ Existe mas com erro")
            report["checks"]["heartbeat"] = (False, "Erro ao verificar")
    else:
        print("✗ NÃO ENCONTRADO (sistema não está rodando)")
        report["checks"]["heartbeat"] = (False, "Não encontrado")
    
    # 6. Log (verificação rápida - apenas últimas linhas)
    print("6. Log do Sistema...", end=" ")
    if os.path.exists(LOG_FILE):
        try:
            # Ler apenas últimas 20 linhas
            with open(LOG_FILE, 'rb') as f:
                f.seek(0, 2)  # Ir para o final
                size = f.tell()
                if size > 2000:
                    f.seek(-2000, 2)  # Ler últimos 2000 bytes
                content = f.read().decode('utf-8', errors='ignore')
                if "PRODUCTION" in content or "MASTER_START" in content:
                    print("✓ OK (contém logs de produção)")
                    report["checks"]["log"] = (True, "OK")
                else:
                    print("⚠ Existe mas sem logs de produção")
                    report["checks"]["log"] = (False, "Sem logs de produção")
        except:
            print("⚠ Existe mas com erro")
            report["checks"]["log"] = (False, "Erro ao ler")
    else:
        print("✗ NÃO ENCONTRADO")
        report["checks"]["log"] = (False, "Não encontrado")
    
    print()
    print("="*80)
    
    # Calcular status final
    checks_criticos = [
        report["checks"].get("arquivo_mestre", (False, ""))[0],
        report["checks"].get("dependencias", (False, ""))[0],
        report["checks"].get("mt5", (False, ""))[0],
    ]
    
    all_critical = all(checks_criticos)
    
    if all_critical:
        report["status"] = "SUCCESS"
        print("✅ STATUS: SUCCESS")
        print("Sistema está operacional!")
    else:
        report["status"] = "FAILURE"
        print("❌ STATUS: FAILURE")
        print("Alguns componentes críticos falharam.")
    
    # Salvar relatório
    with open(VERIFICATION_REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Relatório salvo em: {VERIFICATION_REPORT_FILE}")
    print("="*80)
    
    return report

if __name__ == "__main__":
    try:
        verificar_rapido()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nPressione ENTER para sair...")
        input()

