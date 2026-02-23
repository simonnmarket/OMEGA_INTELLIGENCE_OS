# -*- coding: utf-8 -*-
"""
Script de Verificação de Dependências - Numeia V2.0
Verifica se todas as dependências necessárias estão instaladas
"""

import sys

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas."""
    dependencias = {
        'MetaTrader5': 'MetaTrader5',
        'pydantic': 'pydantic',
        'prometheus_client': 'prometheus_client',
        'requests': 'requests',
        'numpy': 'numpy',
        'pandas': 'pandas'
    }
    
    faltando = []
    instaladas = []
    
    print("="*80)
    print("VERIFICAÇÃO DE DEPENDÊNCIAS - NUMEIA V2.0")
    print("="*80)
    print()
    
    for nome, modulo in dependencias.items():
        try:
            __import__(modulo)
            print(f"✅ {nome}: INSTALADO")
            instaladas.append(nome)
        except ImportError:
            print(f"❌ {nome}: NÃO INSTALADO")
            faltando.append(nome)
    
    print()
    print("="*80)
    print(f"Total: {len(instaladas)} instaladas, {len(faltando)} faltando")
    print("="*80)
    
    if faltando:
        print()
        print("📦 INSTALAR DEPENDÊNCIAS FALTANTES:")
        print()
        print("pip install " + " ".join(faltando))
        print()
        return False
    
    print()
    print("✅ TODAS AS DEPENDÊNCIAS ESTÃO INSTALADAS!")
    print()
    return True

if __name__ == "__main__":
    sucesso = verificar_dependencias()
    sys.exit(0 if sucesso else 1)

