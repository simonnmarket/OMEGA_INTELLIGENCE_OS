#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para completar metadados dos módulos que ainda não têm categoria.
Garante que TODOS os módulos tenham metadados completos.
"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator
except ImportError:
    print("ERRO: financial_governance_orchestrator nao encontrado")
    sys.exit(1)

try:
    from PROTOCOLO_FONTE_VERDADE import FonteVerdadeAurora
except ImportError:
    print("ERRO: PROTOCOLO_FONTE_VERDADE.py nao encontrado")
    sys.exit(1)


def categorizar_modulo_por_nome(nome_modulo):
    """Categoriza módulo baseado no nome."""
    nome_lower = nome_modulo.lower()
    
    if 'governanc' in nome_lower or '00-' in nome_lower:
        return "Governance"
    elif 'departament' in nome_lower or '01-' in nome_lower or 'agent' in nome_lower:
        return "Departments"
    elif 'process' in nome_lower or '02-' in nome_lower:
        return "Processes"
    elif 'operac' in nome_lower or '03-' in nome_lower:
        return "Operations"
    elif 'infraestrutur' in nome_lower or 'infrastructure' in nome_lower or '04-' in nome_lower:
        return "Infrastructure"
    elif 'documentac' in nome_lower or 'documentation' in nome_lower or '05-' in nome_lower:
        return "Documentation"
    elif 'monitor' in nome_lower or '06-' in nome_lower:
        return "Monitoring"
    elif 'system_core' in nome_lower or 'ncnt' in nome_lower:
        return "Core"
    elif 'modules' in nome_lower and 'wrapper' not in nome_lower:
        return "Modules"
    else:
        return "Root"


def completar_metadados_faltantes():
    """Completa metadados dos módulos que ainda não têm categoria."""
    print("\n" + "=" * 80)
    print("COMPLETANDO METADADOS FALTANTES - AURORA v5.1")
    print("=" * 80)
    
    # Validar primeiro
    fonte = FonteVerdadeAurora()
    if not fonte.verificar_fontes():
        print("ERRO: Fontes de verdade nao encontradas")
        return False
    
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    modules_dict = orchestrator.state["modules"]
    
    print(f"\nTotal de modulos no manifesto: {len(modules_dict)}")
    
    # Identificar módulos sem metadados completos
    modulos_sem_metadados = []
    for mod_id, mod_data in modules_dict.items():
        metadata = mod_data.get("metadata", {})
        if not metadata.get("category"):
            modulos_sem_metadados.append((mod_id, mod_data))
    
    print(f"Modulos sem metadados completos: {len(modulos_sem_metadados)}")
    
    if not modulos_sem_metadados:
        print("\n✅ Todos os modulos ja tem metadados completos!")
        return True
    
    # Completar metadados
    print(f"\nCompletando metadados de {len(modulos_sem_metadados)} modulos...")
    completados = 0
    
    for mod_id, mod_data in modulos_sem_metadados:
        nome = mod_data.get("name", "")
        
        # Tentar encontrar no documento primeiro
        categoria = None
        path_documentado = None
        
        try:
            modulos_doc = fonte.obter_lista_modulos_documentada()
            for mod_path in modulos_doc:
                nome_doc = mod_path.replace('\\', '_').replace('/', '_').replace('.py', '')
                if nome_doc == nome or nome in nome_doc or nome_doc in nome:
                    categoria = fonte.categorizar_module(mod_path)
                    path_documentado = mod_path
                    break
        except:
            pass
        
        # Se não encontrou no documento, categorizar por nome
        if not categoria:
            categoria = categorizar_modulo_por_nome(nome)
        
        # Adicionar metadados
        if "metadata" not in mod_data:
            mod_data["metadata"] = {}
        
        mod_data["metadata"]["category"] = categoria
        if path_documentado:
            mod_data["metadata"]["documented_path"] = path_documentado
        
        completados += 1
    
    # Salvar
    orchestrator._save()
    
    print(f"✅ {completados} modulos com metadados completados")
    
    # Validar novamente
    print("\nValidando novamente...")
    modulos_sem_metadados_apos = []
    for mod_id, mod_data in orchestrator.state["modules"].items():
        metadata = mod_data.get("metadata", {})
        if not metadata.get("category"):
            modulos_sem_metadados_apos.append(mod_id)
    
    if modulos_sem_metadados_apos:
        print(f"⚠️  Ainda ha {len(modulos_sem_metadados_apos)} modulos sem metadados")
    else:
        print("✅ Todos os modulos agora tem metadados completos!")
    
    return len(modulos_sem_metadados_apos) == 0


def main():
    """Funcao principal"""
    try:
        sucesso = completar_metadados_faltantes()
        
        if sucesso:
            print("\n✅ Metadados completados com sucesso!")
            sys.exit(0)
        else:
            print("\n⚠️  Alguns metadados ainda faltam, mas progresso foi feito.")
            sys.exit(0)  # Não é erro crítico
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

