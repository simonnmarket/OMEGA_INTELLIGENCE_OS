#!/usr/bin/env python3
"""Verifica e corrige o relatório completo"""

import json
from pathlib import Path

# 1. Definir scripts utilitários (não são módulos do sistema)
utility_scripts = {
    'ADICIONAR_LISTA_MODULOS.py',
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

# 2. Contar módulos reais do sistema
root = Path('.')
exclude = {'__pycache__', '.git', 'legacy_backup', 'backup', 'backups_', 'TEMP_FIX_EXTRACT'}
real_modules = []
for py_file in root.rglob('*.py'):
    if any(excl in str(py_file) for excl in exclude):
        continue
    if py_file.stat().st_size > 0:
        rel_path = str(py_file.relative_to(root))
        if rel_path not in utility_scripts:
            real_modules.append(rel_path)

real_modules_set = set(real_modules)

# 3. Carregar JSON
with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

json_modules_set = set(m['path'] for m in json_data['modules'])

# 4. Filtrar apenas módulos do sistema no JSON
json_system_modules = json_modules_set - utility_scripts

# 5. Verificar
print("=" * 60)
print("VERIFICAÇÃO FINAL DO RELATÓRIO")
print("=" * 60)
print(f"\nMódulos reais do sistema: {len(real_modules_set)}")
print(f"Módulos no JSON (sistema): {len(json_system_modules)}")
print(f"Scripts utilitários: {len(utility_scripts)}")

missing = real_modules_set - json_system_modules
extra = json_system_modules - real_modules_set

if missing:
    print(f"\n⚠️  Módulos faltando no JSON ({len(missing)}):")
    for m in sorted(missing):
        print(f"   - {m}")
else:
    print("\n✅ Todos os módulos do sistema estão no JSON")

if extra:
    print(f"\n⚠️  Módulos extras no JSON ({len(extra)}):")
    for m in sorted(extra):
        print(f"   - {m}")
else:
    print("\n✅ Nenhum módulo extra no JSON")

# 6. Verificar documento
with open('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md', 'r', encoding='utf-8') as f:
    doc_content = f.read()

has_list = "## 13. COMPLETE MODULE LIST" in doc_content or "COMPLETE MODULE LIST" in doc_content
has_details = "## 14. MODULE DETAILS" in doc_content

print(f"\n📄 Documento:")
print(f"   Lista completa presente: {has_list}")
print(f"   Detalhes por categoria: {has_details}")

# 7. Conclusão
if len(real_modules_set) == len(json_system_modules) and not missing and not extra:
    print("\n" + "=" * 60)
    print("✅ RELATÓRIO COMPLETO E CORRETO")
    print("=" * 60)
    print(f"Total módulos do sistema Aurora: {len(real_modules_set)}")
    print(f"Total módulos documentados: {len(json_system_modules)}")
    print("✅ Sem discrepâncias")
    print("✅ Todos os módulos listados")
else:
    print("\n" + "=" * 60)
    print("⚠️  AJUSTES NECESSÁRIOS")
    print("=" * 60)
    if missing:
        print(f"Adicionar {len(missing)} módulos ao JSON")
    if extra:
        print(f"Remover {len(extra)} módulos do JSON (ou documentar como scripts)")

