#!/usr/bin/env python3
"""Adiciona lista completa de módulos ao documento consolidado"""

import json

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

# Carregar dados
with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Adicionar ao documento
with open('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md', 'a', encoding='utf-8') as f:
    f.write('\n\n## 13. COMPLETE MODULE LIST (259 Modules)\n\n')
    f.write('```\n')
    for module in sorted(data['modules'], key=lambda x: x['path']):
        f.write(f"{module['path']}\n")
    f.write('```\n\n')
    f.write('---\n\n')
    f.write('## 14. MODULE DETAILS BY CATEGORY\n\n')
    
    # Agrupar por categoria
    categories = {}
    for module in data['modules']:
        cat = categorize_module(module['path'])
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(module)
    
    # Escrever por categoria
    for cat in sorted(categories.keys()):
        modules = categories[cat]
        f.write(f'### {cat} ({len(modules)} modules)\n\n')
        
        # Lista resumida (top 30)
        for module in sorted(modules, key=lambda x: x['path'])[:30]:
            path = module['path']
            classes = len(module.get('classes', []))
            functions = len(module.get('functions', []))
            f.write(f'- `{path}` ({classes} classes, {functions} functions)\n')
        
        if len(modules) > 30:
            f.write(f'- ... and {len(modules) - 30} more modules\n')
        
        f.write('\n')

print("✅ Lista de módulos adicionada ao documento consolidado")

