#!/usr/bin/env python3
"""Adiciona lista completa de módulos ao documento final"""

import json
from pathlib import Path

# Scripts utilitários (não são módulos do sistema)
utility_scripts = {
    'ADICIONAR_LISTA_MODULOS.py',
    'ADICIONAR_LISTA_COMPLETA_FINAL.py',
    'CONVERTER_JSON_PARA_MD.py',
    'GENERATE_COMPLETE_TECHNICAL_SPEC.py',
    'VERIFICAR_COMPLETUDE_RELATORIO.py',
    'VERIFICAR_E_CORRIGIR_RELATORIO.py',
    'verificar_json.py',
    'DIAGNOSTICO_SINAIS.py',
    'HANTEC_STOPS_DISCOVERY.py',
    'SOLUCAO_DEFINITIVA_MT5.py',
    'MT5_EXECUTOR_PROFISSIONAL.py'
}

# Carregar JSON
with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtrar apenas módulos do sistema
system_modules = [m for m in data['modules'] if m['path'] not in utility_scripts]

def categorize_module(path: str) -> str:
    """Categoriza módulo por caminho."""
    if "system_core" in path:
        return "Core"
    elif "00-Governanca" in path:
        return "Governance"
    elif "01-Departamentos" in path:
        return "Departments"
    elif "04-Infraestrutura" in path:
        return "Infrastructure"
    elif "06-Monitoramento" in path:
        return "Monitoring"
    elif "03-Operacoes" in path:
        return "Operations"
    elif "02-Processos" in path:
        return "Processes"
    elif "modules" in path and "wrappers" not in path:
        return "Modules"
    else:
        return "Root"

# Agrupar por categoria
categories = {}
for module in system_modules:
    cat = categorize_module(module['path'])
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(module)

# Adicionar ao documento
with open('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md', 'a', encoding='utf-8') as f:
    f.write('\n\n## 13. COMPLETE MODULE LIST (252 System Modules)\n\n')
    f.write('```\n')
    for module in sorted(system_modules, key=lambda x: x['path']):
        f.write(f"{module['path']}\n")
    f.write('```\n\n')
    f.write('---\n\n')
    f.write('## 14. MODULE DETAILS BY CATEGORY\n\n')
    
    # Escrever por categoria
    for cat in sorted(categories.keys()):
        modules = categories[cat]
        f.write(f'### {cat} ({len(modules)} modules)\n\n')
        
        # Lista completa
        for module in sorted(modules, key=lambda x: x['path']):
            path = module['path']
            if 'error' not in module:
                classes = len(module.get('classes', []))
                functions = len(module.get('functions', []))
                f.write(f'- `{path}` ({classes} classes, {functions} functions)\n')
            else:
                f.write(f'- `{path}` (ERROR)\n')
        
        f.write('\n')

print(f"✅ Lista completa adicionada: {len(system_modules)} módulos do sistema")

