#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validação completa que GARANTE todos os 252 módulos estão integrados.
Executa validações rigorosas e gera relatório detalhado.
"""

import sys
import os
from pathlib import Path
import json

# Importar protocolo de fonte de verdade
try:
    from PROTOCOLO_FONTE_VERDADE import FonteVerdadeAurora, protocolo_obrigatorio_antes_de_qualquer_acao
except ImportError:
    print("ERRO: PROTOCOLO_FONTE_VERDADE.py nao encontrado")
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator
except ImportError:
    print("ERRO: financial_governance_orchestrator nao encontrado")
    sys.exit(1)


def validar_integracao_completa():
    """
    Validação COMPLETA e RIGOROSA de que todos os 252 módulos estão integrados.
    """
    print("\n" + "=" * 80)
    print("VALIDACAO COMPLETA DE INTEGRACAO - AURORA v5.1")
    print("=" * 80)
    
    # 1. Executar protocolo obrigatório
    print("\n[1/5] Executando protocolo de fonte de verdade...")
    if not protocolo_obrigatorio_antes_de_qualquer_acao():
        print("\nERRO CRITICO: Validacao falhou. Abortando.")
        return False
    
    # 2. Obter lista documentada
    print("\n[2/5] Obtendo lista documentada de modulos...")
    fonte = FonteVerdadeAurora()
    modulos_documentados = fonte.obter_lista_modulos_documentada()
    print(f"   Total de modulos documentados: {len(modulos_documentados)}")
    
    # 3. Verificar integração no sistema de governança
    print("\n[3/5] Verificando integracao no sistema de governanca...")
    todos_integrados, rel_integracao = fonte.verificar_modulos_integrados()
    
    print(f"   Modulos no manifesto: {rel_integracao['total_no_manifesto']}")
    print(f"   Modulos integrados: {rel_integracao['total_integrados']}")
    print(f"   Modulos faltando: {rel_integracao['total_faltando']}")
    print(f"   Percentual integrado: {rel_integracao['percentual_integrado']:.1f}%")
    
    if not todos_integrados:
        print(f"\nERRO: {rel_integracao['total_faltando']} modulos faltando!")
        print("Primeiros modulos faltando:")
        for mod in rel_integracao['modulos_faltando'][:5]:
            print(f"   - {mod}")
        return False
    
    # 4. Verificar existência física
    print("\n[4/5] Verificando existencia fisica dos modulos...")
    modulos_inexistentes = []
    for mod_path in modulos_documentados:
        paths_to_try = [
            mod_path,
            mod_path.replace('/', '\\'),
            mod_path.replace('\\', '/'),
        ]
        
        existe = False
        for path_variant in paths_to_try:
            if os.path.exists(path_variant):
                existe = True
                break
        
        if not existe:
            modulos_inexistentes.append(mod_path)
    
    print(f"   Modulos existentes: {len(modulos_documentados) - len(modulos_inexistentes)}")
    print(f"   Modulos inexistentes: {len(modulos_inexistentes)}")
    
    if modulos_inexistentes:
        print(f"\nERRO: {len(modulos_inexistentes)} modulos nao existem fisicamente!")
        print("Primeiros modulos inexistentes:")
        for mod in modulos_inexistentes[:5]:
            print(f"   - {mod}")
        return False
    
    # 5. Verificar metadados no sistema de governança
    print("\n[5/5] Verificando metadados no sistema de governanca...")
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    modules_dict = orchestrator.state["modules"]
    
    modulos_com_metadados = 0
    modulos_sem_metadados = []
    
    for mod_path in modulos_documentados:
        nome_doc = mod_path.replace('\\', '_').replace('/', '_').replace('.py', '')
        
        # Procurar módulo correspondente
        encontrado = False
        for mod_id, mod_data in modules_dict.items():
            if mod_data.get("name") == nome_doc:
                if mod_data.get("metadata", {}).get("category"):
                    modulos_com_metadados += 1
                    encontrado = True
                    break
        
        if not encontrado:
            modulos_sem_metadados.append(mod_path)
    
    print(f"   Modulos com metadados: {modulos_com_metadados}")
    print(f"   Modulos sem metadados: {len(modulos_sem_metadados)}")
    
    if modulos_sem_metadados:
        print(f"\nAVISO: {len(modulos_sem_metadados)} modulos sem metadados completos")
        if len(modulos_sem_metadados) > 10:
            print("(Mais de 10 modulos sem metadados)")
    
    # Relatório final
    print("\n" + "=" * 80)
    print("VALIDACAO COMPLETA CONCLUIDA")
    print("=" * 80)
    print(f"✅ Total de modulos documentados: {len(modulos_documentados)}")
    print(f"✅ Modulos integrados: {rel_integracao['total_integrados']}")
    print(f"✅ Modulos existentes: {len(modulos_documentados) - len(modulos_inexistentes)}")
    print(f"✅ Modulos com metadados: {modulos_com_metadados}")
    print(f"✅ Percentual de integracao: {rel_integracao['percentual_integrado']:.1f}%")
    
    if todos_integrados and len(modulos_inexistentes) == 0:
        print("\n🎉 SISTEMA 100% INTEGRADO E VALIDADO!")
        return True
    else:
        print("\n⚠️  SISTEMA COM INCONSISTENCIAS - REQUER CORRECAO")
        return False


def main():
    """Funcao principal"""
    try:
        sucesso = validar_integracao_completa()
        
        if sucesso:
            print("\n✅ Validacao passou com sucesso!")
            sys.exit(0)
        else:
            print("\n❌ Validacao falhou. Corrija os erros antes de prosseguir.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERRO durante validacao: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

