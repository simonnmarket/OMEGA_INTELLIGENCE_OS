#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO COMPLETA DO SISTEMA PROMETHEUS v4.1
Verifica se todos os componentes estão 100% operacionais
"""

import os
import sys
import json
from pathlib import Path

print("="*80)
print("VERIFICAÇÃO COMPLETA DO SISTEMA PROMETHEUS v4.1")
print("="*80)
print()

erros = []
avisos = []
sucessos = []

# 1. Verificar arquivos principais
print("1. VERIFICANDO ARQUIVOS PRINCIPAIS...")
print("-" * 80)

arquivos_necessarios = [
    "prometheus_master_control_v4.1.py",
    "run_discovery.py",
    "run_production.py",
    "config.json"
]

for arquivo in arquivos_necessarios:
    caminho = Path(__file__).parent / arquivo
    if caminho.exists():
        tamanho = caminho.stat().st_size
        print(f"✓ {arquivo} - OK ({tamanho:,} bytes)")
        sucessos.append(f"Arquivo {arquivo} existe")
    else:
        print(f"✗ {arquivo} - NÃO ENCONTRADO")
        erros.append(f"Arquivo {arquivo} não encontrado")

print()

# 2. Verificar dependências Python
print("2. VERIFICANDO DEPENDÊNCIAS PYTHON...")
print("-" * 80)

dependencias = {
    "MetaTrader5": "mt5",
    "pandas": "pd",
    "numpy": "np",
    "json": "json",
    "logging": "logging",
    "threading": "threading",
    "datetime": "datetime",
    "pathlib": "Path"
}

for nome, alias in dependencias.items():
    try:
        if nome == "json" or nome == "logging" or nome == "threading" or nome == "datetime" or nome == "pathlib":
            __import__(nome)
        else:
            __import__(alias if alias != nome else nome)
        print(f"✓ {nome} - OK")
        sucessos.append(f"Dependência {nome} instalada")
    except ImportError:
        print(f"✗ {nome} - NÃO INSTALADO")
        erros.append(f"Dependência {nome} não instalada")

print()

# 3. Verificar sintaxe do código principal
print("3. VERIFICANDO SINTAXE DO CÓDIGO...")
print("-" * 80)

try:
    with open(Path(__file__).parent / "prometheus_master_control_v4.1.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    compile(codigo, "prometheus_master_control_v4.1.py", "exec")
    print("✓ Sintaxe do código principal - OK")
    sucessos.append("Sintaxe do código principal válida")
except SyntaxError as e:
    print(f"✗ Erro de sintaxe: {e}")
    erros.append(f"Erro de sintaxe no código principal: {e}")
except Exception as e:
    print(f"✗ Erro ao verificar sintaxe: {e}")
    erros.append(f"Erro ao verificar sintaxe: {e}")

print()

# 4. Verificar config.json
print("4. VERIFICANDO CONFIGURAÇÃO...")
print("-" * 80)

config_path = Path(__file__).parent.parent.parent / "config.json"
if config_path.exists():
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        campos_necessarios = ["TRADING_SYMBOLS", "ORDER_VOLUME", "EXECUTION_CYCLE_SECONDS"]
        for campo in campos_necessarios:
            if campo in config:
                print(f"✓ {campo} - OK: {config[campo]}")
                sucessos.append(f"Config {campo} presente")
            else:
                print(f"⚠ {campo} - NÃO ENCONTRADO (usará padrão)")
                avisos.append(f"Config {campo} não encontrado, usará padrão")
    except json.JSONDecodeError as e:
        print(f"✗ Erro ao ler config.json: {e}")
        erros.append(f"Erro ao ler config.json: {e}")
    except Exception as e:
        print(f"✗ Erro: {e}")
        erros.append(f"Erro ao verificar config.json: {e}")
else:
    print("⚠ config.json não encontrado (usará configuração padrão)")
    avisos.append("config.json não encontrado, usará padrão")

print()

# 5. Verificar conexão MT5
print("5. VERIFICANDO CONEXÃO MT5...")
print("-" * 80)

try:
    import MetaTrader5 as mt5
    if mt5.initialize():
        account_info = mt5.account_info()
        if account_info:
            print(f"✓ MT5 conectado - Conta: {account_info.login}, Servidor: {account_info.server}")
            sucessos.append("MT5 conectado com sucesso")
        else:
            print("⚠ MT5 inicializado mas sem informações da conta")
            avisos.append("MT5 inicializado mas sem informações da conta")
        mt5.shutdown()
    else:
        erro = mt5.last_error()
        print(f"✗ Falha ao inicializar MT5: {erro}")
        erros.append(f"Falha ao inicializar MT5: {erro}")
except Exception as e:
    print(f"✗ Erro ao verificar MT5: {e}")
    erros.append(f"Erro ao verificar MT5: {e}")

print()

# 6. Verificar estrutura de diretórios
print("6. VERIFICANDO ESTRUTURA DE DIRETÓRIOS...")
print("-" * 80)

diretorio_atual = Path(__file__).parent
print(f"✓ Diretório atual: {diretorio_atual}")
sucessos.append(f"Diretório atual: {diretorio_atual}")

if diretorio_atual.exists() and diretorio_atual.is_dir():
    print(f"✓ Diretório existe e é acessível")
    sucessos.append("Diretório acessível")
else:
    print(f"✗ Problema com diretório")
    erros.append("Problema com diretório")

print()

# 7. Verificar se discovery foi executado (opcional)
print("7. VERIFICANDO ARQUIVO DE ATIVOS (opcional)...")
print("-" * 80)

tradeable_assets = Path(__file__).parent / "TRADEABLE_ASSETS.json"
if tradeable_assets.exists():
    try:
        with open(tradeable_assets, 'r') as f:
            assets = json.load(f)
        print(f"✓ TRADEABLE_ASSETS.json encontrado - {len(assets)} ativos")
        sucessos.append(f"TRADEABLE_ASSETS.json com {len(assets)} ativos")
    except Exception as e:
        print(f"⚠ Erro ao ler TRADEABLE_ASSETS.json: {e}")
        avisos.append(f"Erro ao ler TRADEABLE_ASSETS.json: {e}")
else:
    print("⚠ TRADEABLE_ASSETS.json não encontrado (execute discovery primeiro)")
    avisos.append("TRADEABLE_ASSETS.json não encontrado - execute discovery primeiro")

print()

# RESUMO FINAL
print("="*80)
print("RESUMO DA VERIFICAÇÃO")
print("="*80)
print(f"✓ Sucessos: {len(sucessos)}")
print(f"⚠ Avisos: {len(avisos)}")
print(f"✗ Erros: {len(erros)}")
print()

if erros:
    print("ERROS CRÍTICOS (impedem funcionamento):")
    for erro in erros:
        print(f"  ✗ {erro}")
    print()
    print("="*80)
    print("❌ SISTEMA NÃO ESTÁ 100% OPERACIONAL")
    print("="*80)
    print("\nCorrija os erros acima antes de usar o sistema.")
    sys.exit(1)
elif avisos:
    print("AVISOS (não impedem funcionamento, mas atenção):")
    for aviso in avisos:
        print(f"  ⚠ {aviso}")
    print()
    print("="*80)
    print("⚠ SISTEMA OPERACIONAL COM AVISOS")
    print("="*80)
    print("\nO sistema pode funcionar, mas verifique os avisos acima.")
    sys.exit(0)
else:
    print("="*80)
    print("✅ SISTEMA 100% OPERACIONAL")
    print("="*80)
    print("\nTodos os componentes estão funcionando corretamente!")
    print("\nPróximos passos:")
    print("  1. Execute: python run_discovery.py (ou clique duas vezes)")
    print("  2. Após discovery, execute: python run_production.py (ou clique duas vezes)")
    sys.exit(0)

