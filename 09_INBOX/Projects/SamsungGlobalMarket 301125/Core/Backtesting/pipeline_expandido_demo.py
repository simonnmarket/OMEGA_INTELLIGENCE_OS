#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenMyMind Project 007 - Pipeline Expandido Demo

Wrapper simplificado para execução rápida em conta demo.
Executa o pipeline expandido completo com fontes alternativas.

Versão: 1.0 (Demo)
Data: 20 de Novembro de 2025
Status: Pronto para Execução Imediata
"""

import sys
import os
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar e executar pipeline expandido
try:
    from openmymind_pipeline_007_expandido import executar_pipeline_expandido
    
    if __name__ == "__main__":
        print("="*80)
        print("OPENMYMIND PROJECT 007 - PIPELINE EXPANDIDO DEMO")
        print("="*80)
        print()
        print("Executando pipeline expandido completo...")
        print("Fontes: Reddit, Telegram/Discord, Orderbook, On-Chain, Whale Alerts")
        print()
        print("-"*80)
        print()
        
        try:
            resultados = executar_pipeline_expandido()
            
            print()
            print("="*80)
            print("EXECUÇÃO CONCLUÍDA COM SUCESSO")
            print("="*80)
            print()
            print(f"Status: {resultados.get('status', 'desconhecido')}")
            print(f"Reddit: {resultados.get('coleta_reddit', {}).get('registros', 0)} posts coletados")
            print(f"Telegram/Discord: {resultados.get('coleta_telegram_discord', {}).get('registros', 0)} mensagens")
            print(f"Eventos Validados: {resultados.get('validacao_cruzada', {}).get('eventos_validados', 0)}")
            print()
            print("Relatórios disponíveis em: data/")
            print("="*80)
            
            sys.exit(0)
        except KeyboardInterrupt:
            print()
            print("\n[AVISO] Execução interrompida pelo usuário.")
            sys.exit(130)
        except Exception as e:
            print()
            print("="*80)
            print("ERRO NA EXECUÇÃO")
            print("="*80)
            print(f"Erro: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            print("="*80)
            sys.exit(1)
            
except ImportError as e:
    print("="*80)
    print("ERRO DE IMPORTAÇÃO")
    print("="*80)
    print(f"Não foi possível importar o módulo pipeline expandido: {str(e)}")
    print()
    print("Verifique se o arquivo 'openmymind_pipeline_007_expandido.py' existe.")
    print("="*80)
    sys.exit(1)
except Exception as e:
    print("="*80)
    print("ERRO CRÍTICO")
    print("="*80)
    print(f"Erro inesperado: {str(e)}")
    print()
    import traceback
    traceback.print_exc()
    print("="*80)
    sys.exit(1)

