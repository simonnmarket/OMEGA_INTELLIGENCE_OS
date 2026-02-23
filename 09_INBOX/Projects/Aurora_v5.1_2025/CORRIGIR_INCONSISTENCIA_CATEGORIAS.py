#!/usr/bin/env python3
"""Corrige inconsistência na contagem de categorias"""

import json
from pathlib import Path

# Scripts utilitários
utility_scripts = {
    'ADICIONAR_LISTA_MODULOS.py',
    'ADICIONAR_LISTA_COMPLETA_FINAL.py',
    'CONSOLIDAR_3_RELATORIOS_FINAL.py',
    'CORRIGIR_INCONSISTENCIA_CATEGORIAS.py',
    'CONVERTER_JSON_PARA_MD.py',
    'GENERATE_COMPLETE_TECHNICAL_SPEC.py',
    'VERIFICAR_COMPLETUDE_RELATORIO.py',
    'VERIFICAR_E_CORRIGIR_RELATORIO.py',
    'VERIFICACAO_FINAL_DEFINITIVA.py',
    'verificar_json.py',
    'DIAGNOSTICO_SINAIS.py',
    'HANTEC_STOPS_DISCOVERY.py',
    'SOLUCAO_DEFINITIVA_MT5.py',
    'MT5_EXECUTOR_PROFISSIONAL.py'
}

# Contar módulos reais
root = Path('.')
exclude = {'__pycache__', '.git', 'legacy_backup', 'backup', 'backups_', 'TEMP_FIX_EXTRACT'}

def categorize_module(path: str) -> str:
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
    elif "05-Documentacao" in path:
        return "Documentation"
    else:
        return "Root"

real_modules = []
for py_file in root.rglob('*.py'):
    if any(excl in str(py_file) for excl in exclude):
        continue
    if py_file.stat().st_size > 0:
        rel_path = str(py_file.relative_to(root))
        if rel_path not in utility_scripts:
            real_modules.append(rel_path)

# Categorizar
categories = {}
for module in real_modules:
    cat = categorize_module(module)
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(module)

print("=" * 60)
print("CONTAGEM REAL POR CATEGORIA")
print("=" * 60)
for cat in sorted(categories.keys()):
    print(f"{cat:20}: {len(categories[cat]):3} módulos")

total = sum(len(v) for v in categories.values())
print(f"\n{'TOTAL':20}: {total:3} módulos")

# Verificar JSON
with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

json_modules = [m for m in json_data['modules'] if m['path'] not in utility_scripts]
json_categories = {}
for module in json_modules:
    cat = categorize_module(module['path'])
    if cat not in json_categories:
        json_categories[cat] = []
    json_categories[cat].append(module)

print("\n" + "=" * 60)
print("CONTAGEM NO JSON POR CATEGORIA")
print("=" * 60)
for cat in sorted(json_categories.keys()):
    print(f"{cat:20}: {len(json_categories[cat]):3} módulos")

json_total = sum(len(v) for v in json_categories.values())
print(f"\n{'TOTAL':20}: {json_total:3} módulos")

# Comparar
print("\n" + "=" * 60)
print("COMPARAÇÃO")
print("=" * 60)
all_cats = set(categories.keys()) | set(json_categories.keys())
for cat in sorted(all_cats):
    real_count = len(categories.get(cat, []))
    json_count = len(json_categories.get(cat, []))
    if real_count != json_count:
        print(f"⚠️  {cat:20}: Real={real_count:3} JSON={json_count:3} (DIFERENÇA)")
    else:
        print(f"✅ {cat:20}: {real_count:3} módulos")

print(f"\n✅ Total Real: {total}")
print(f"✅ Total JSON: {json_total}")
print(f"✅ Status: {'CORRETO' if total == json_total else 'ERRO'}")

# Valores corretos para correção
print("\n" + "=" * 60)
print("VALORES CORRETOS PARA CORREÇÃO")
print("=" * 60)
for cat in sorted(categories.keys()):
    print(f"- **{cat}**: {len(categories[cat])} módulos")

