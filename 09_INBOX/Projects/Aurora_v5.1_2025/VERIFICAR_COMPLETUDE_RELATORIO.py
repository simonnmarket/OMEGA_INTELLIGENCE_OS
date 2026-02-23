#!/usr/bin/env python3
"""Verifica completude do relatório técnico"""

import json
from pathlib import Path

# 1. Contagem real do sistema
root = Path('.')
exclude = {'__pycache__', '.git', 'legacy_backup', 'backup', 'backups_', 'TEMP_FIX_EXTRACT'}
real_modules = set()
for py_file in root.rglob('*.py'):
    if any(excl in str(py_file) for excl in exclude):
        continue
    if py_file.stat().st_size > 0:
        rel_path = str(py_file.relative_to(root))
        real_modules.add(rel_path)

# 2. Contagem no JSON
with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

json_modules = set(m['path'] for m in json_data['modules'])

# 3. Verificar discrepâncias
missing_in_json = real_modules - json_modules
missing_in_real = json_modules - real_modules

# 4. Filtrar scripts utilitários (não são módulos do sistema)
utility_scripts = {
    'ADICIONAR_LISTA_MODULOS.py',
    'CONVERTER_JSON_PARA_MD.py',
    'GENERATE_COMPLETE_TECHNICAL_SPEC.py',
    'VERIFICAR_COMPLETUDE_RELATORIO.py',
    'verificar_json.py',
    'DIAGNOSTICO_SINAIS.py'
}

real_system_modules = real_modules - utility_scripts

print("=" * 60)
print("VERIFICAÇÃO DE COMPLETUDE DO RELATÓRIO")
print("=" * 60)
print(f"\n1. Módulos reais do sistema: {len(real_system_modules)}")
print(f"2. Módulos no JSON: {len(json_modules)}")
print(f"3. Scripts utilitários (excluídos): {len(utility_scripts & real_modules)}")

if missing_in_json - utility_scripts:
    print(f"\n⚠️  MÓDULOS FALTANDO NO JSON:")
    for m in sorted(missing_in_json - utility_scripts):
        print(f"   - {m}")
else:
    print("\n✅ Nenhum módulo do sistema faltando no JSON")

if missing_in_real:
    print(f"\n⚠️  MÓDULOS NO JSON QUE NÃO EXISTEM:")
    for m in sorted(missing_in_real):
        print(f"   - {m}")
else:
    print("\n✅ Todos os módulos do JSON existem")

# 5. Verificar se documento tem lista completa
with open('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md', 'r', encoding='utf-8') as f:
    doc_content = f.read()

doc_modules_count = doc_content.count('\n00-') + doc_content.count('\n01-') + doc_content.count('\n02-') + doc_content.count('\n03-') + doc_content.count('\n04-') + doc_content.count('\n05-') + doc_content.count('\n06-') + doc_content.count('\nsystem_core') + doc_content.count('\nmodules\\') + doc_content.count('\nAURORA_') + doc_content.count('\naurora_') + doc_content.count('\nmain') + doc_content.count('\nncnt_')

print(f"\n6. Módulos listados no documento: ~{doc_modules_count} referências")

# 6. Conclusão
if len(real_system_modules) == len(json_modules) and not missing_in_real:
    print("\n" + "=" * 60)
    print("✅ RELATÓRIO COMPLETO E CONSISTENTE")
    print("=" * 60)
    print(f"Total módulos do sistema: {len(real_system_modules)}")
    print(f"Total módulos documentados: {len(json_modules)}")
    print("✅ Sem discrepâncias")
else:
    print("\n" + "=" * 60)
    print("⚠️  DISCREPÂNCIAS ENCONTRADAS")
    print("=" * 60)
    print(f"Diferença: {abs(len(real_system_modules) - len(json_modules))} módulos")

