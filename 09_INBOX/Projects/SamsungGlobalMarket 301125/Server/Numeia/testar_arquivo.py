#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido para verificar se o arquivo principal pode ser importado
"""

import sys
import os

print("="*80)
print("TESTE DE COMPATIBILIDADE DO ARQUIVO")
print("="*80)
print()

# Verificar Python
print(f"Python: {sys.version}")
print(f"Executável: {sys.executable}")
print()

# Tentar importar o arquivo principal
print("Tentando importar prometheus_master_control_v4.1...")
try:
    # Adicionar diretório ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Tentar compilar o arquivo
    with open("prometheus_master_control_v4.1.py", 'r', encoding='utf-8') as f:
        code = f.read()
    
    compile(code, "prometheus_master_control_v4.1.py", "exec")
    print("✓ Arquivo compilado com sucesso!")
    print("✓ Sem erros de sintaxe!")
    
except SyntaxError as e:
    print(f"✗ ERRO DE SINTAXE: {e}")
    print(f"  Linha: {e.lineno}")
    print(f"  Texto: {e.text}")
except UnicodeDecodeError as e:
    print(f"✗ ERRO DE ENCODING: {e}")
except Exception as e:
    print(f"✗ ERRO: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print("Pressione ENTER para sair...")
input()

