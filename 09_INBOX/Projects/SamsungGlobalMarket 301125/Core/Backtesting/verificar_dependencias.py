#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Verificação de Dependências e Pendências - OpenMyMind Project 007
"""

import sys
from pathlib import Path

def verificar_dependencia(nome, modulo, opcional=False):
    """Verifica se uma dependência está instalada"""
    try:
        __import__(modulo)
        print(f"✓ {nome} - INSTALADO")
        return True
    except ImportError:
        status = "OPCIONAL" if opcional else "REQUERIDO"
        print(f"✗ {nome} - NÃO INSTALADO ({status})")
        return False

def verificar_snscrape():
    """Verifica snscrape especificamente"""
    try:
        import snscrape.modules.twitter as sntwitter
        print("✓ snscrape - INSTALADO")
        return True
    except ImportError:
        print("✗ snscrape - NÃO INSTALADO (REQUERIDO para coleta de tweets)")
        return False

def verificar_arquivos():
    """Verifica se os arquivos principais existem"""
    arquivos_necessarios = [
        "Core/Backtesting/openmymind_pipeline_007.py",
        "Core/Backtesting/test_openmymind_completo.py",
        "Core/Backtesting/gerar_relatorio_final.py"
    ]
    
    print("\n" + "="*80)
    print("VERIFICAÇÃO DE ARQUIVOS")
    print("="*80)
    
    todos_existem = True
    for arquivo in arquivos_necessarios:
        caminho = Path(arquivo)
        if caminho.exists():
            print(f"✓ {arquivo} - EXISTE")
        else:
            print(f"✗ {arquivo} - NÃO ENCONTRADO")
            todos_existem = False
    
    return todos_existem

def verificar_pendencias():
    """Verifica pendências conhecidas no código"""
    print("\n" + "="*80)
    print("VERIFICAÇÃO DE PENDÊNCIAS CONHECIDAS")
    print("="*80)
    
    pendencias = []
    
    # Verificar problema de dimensões no sistema neural
    arquivo_principal = Path("Core/Backtesting/openmymind_pipeline_007.py")
    if arquivo_principal.exists():
        conteudo = arquivo_principal.read_text(encoding='utf-8')
        
        if "Problema de dimensões de tensor" in conteudo or "4-D query tensor" in conteudo:
            pendencias.append({
                "tipo": "AVISO",
                "descricao": "Problema de dimensões de tensor no sistema neural (atenção multi-head)",
                "impacto": "Sistema neural executa mas com avisos",
                "prioridade": "MÉDIA"
            })
    
    # Verificar variáveis de ambiente
    import os
    env_vars = {
        "ETHERSCAN_API_KEY": "Coleta de dados on-chain",
        "WHALEALERT_API_KEY": "Coleta de whale alerts"
    }
    
    env_faltando = []
    for var, desc in env_vars.items():
        if not os.getenv(var):
            env_faltando.append(f"{var} - {desc}")
    
    if env_faltando:
        pendencias.append({
            "tipo": "CONFIGURAÇÃO",
            "descricao": "Variáveis de ambiente não configuradas",
            "detalhes": env_faltando,
            "impacto": "Coletas específicas não funcionarão",
            "prioridade": "BAIXA (opcional)"
        })
    
    # Exibir pendências
    if pendencias:
        for i, pend in enumerate(pendencias, 1):
            print(f"\n[{i}] {pend['tipo']}: {pend['descricao']}")
            print(f"    Impacto: {pend['impacto']}")
            print(f"    Prioridade: {pend['prioridade']}")
            if 'detalhes' in pend:
                print("    Detalhes:")
                for det in pend['detalhes']:
                    print(f"      - {det}")
    else:
        print("✓ Nenhuma pendência crítica encontrada")
    
    return pendencias

def main():
    """Função principal de verificação"""
    print("="*80)
    print("VERIFICAÇÃO DE DEPENDÊNCIAS E STATUS - OPENMYMIND PROJECT 007")
    print("="*80)
    
    print("\nDEPENDÊNCIAS PRINCIPAIS:")
    print("-"*80)
    
    dependencias_ok = True
    
    # Dependências obrigatórias
    dependencias_ok &= verificar_dependencia("torch", "torch")
    dependencias_ok &= verificar_dependencia("pandas", "pandas")
    dependencias_ok &= verificar_dependencia("numpy", "numpy")
    dependencias_ok &= verificar_dependencia("ccxt", "ccxt")
    dependencias_ok &= verificar_dependencia("requests", "requests")
    dependencias_ok &= verificar_dependencia("sqlalchemy", "sqlalchemy")
    dependencias_ok &= verificar_dependencia("yfinance", "yfinance")
    
    # Dependências opcionais
    print("\nDEPENDÊNCIAS OPCIONAIS:")
    print("-"*80)
    snscrape_ok = verificar_snscrape()
    vectorbt_ok = verificar_dependencia("vectorbt", "vectorbt", opcional=True)
    
    # Verificar arquivos
    arquivos_ok = verificar_arquivos()
    
    # Verificar pendências
    pendencias = verificar_pendencias()
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO FINAL")
    print("="*80)
    
    status_geral = "PRONTO" if dependencias_ok and arquivos_ok else "PENDÊNCIAS"
    
    print(f"Status Geral: {status_geral}")
    print(f"Dependências Principais: {'✓ OK' if dependencias_ok else '✗ FALTANDO'}")
    print(f"snscrape: {'✓ OK' if snscrape_ok else '✗ FALTANDO (coleta de tweets não funcionará)'}")
    print(f"vectorbt: {'✓ OK' if vectorbt_ok else '⚠ OPCIONAL (backtest usará fallback pandas)'}")
    print(f"Arquivos: {'✓ OK' if arquivos_ok else '✗ FALTANDO'}")
    print(f"Pendências Encontradas: {len(pendencias)}")
    
    if not dependencias_ok:
        print("\n⚠ AÇÃO NECESSÁRIA:")
        print("   Execute: pip install torch pandas numpy ccxt requests sqlalchemy yfinance")
    
    if not snscrape_ok:
        print("\n⚠ AÇÃO NECESSÁRIA:")
        print("   Execute: pip install snscrape")
        print("   Nota: snscrape pode requerer instalação adicional de dependências do sistema")
    
    if pendencias:
        print("\n⚠ PENDÊNCIAS IDENTIFICADAS:")
        for pend in pendencias:
            if pend['prioridade'] != "BAIXA (opcional)":
                print(f"   - {pend['descricao']}")
    
    print("\n" + "="*80)
    
    return 0 if (dependencias_ok and arquivos_ok) else 1

if __name__ == "__main__":
    sys.exit(main())

