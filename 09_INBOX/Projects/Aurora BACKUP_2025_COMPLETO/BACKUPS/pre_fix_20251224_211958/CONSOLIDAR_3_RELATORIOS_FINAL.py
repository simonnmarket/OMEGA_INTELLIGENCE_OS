#!/usr/bin/env python3
"""
CONSOLIDAÇÃO DEFINITIVA DOS 3 RELATÓRIOS
Corrige todas as contagens para 252 e consolida em um único documento
"""

import json
from pathlib import Path
from datetime import datetime

# Scripts utilitários (não são módulos do sistema)
utility_scripts = {
    'ADICIONAR_LISTA_MODULOS.py',
    'ADICIONAR_LISTA_COMPLETA_FINAL.py',
    'CONSOLIDAR_3_RELATORIOS_FINAL.py',
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

# 1. Verificar contagem real
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

CORRECT_COUNT = len(real_modules)
print(f"✅ Contagem verificada: {CORRECT_COUNT} módulos do sistema")

# 2. Carregar JSON e filtrar
with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

system_modules = [m for m in json_data['modules'] if m['path'] not in utility_scripts]

# 3. Categorizar módulos
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
    else:
        return "Root"

categories = {}
for module in system_modules:
    cat = categorize_module(module['path'])
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(module)

# 4. Ler os 3 relatórios
print("📖 Lendo relatórios...")

# Relatório 1: AURORA_TECHNICAL_SPECIFICATION.md
with open('AURORA_TECHNICAL_SPECIFICATION.md', 'r', encoding='utf-8') as f:
    spec1 = f.read()

# Relatório 2: AURORA_COMPLETE_TECHNICAL_SPECIFICATION.md
with open('AURORA_COMPLETE_TECHNICAL_SPECIFICATION.md', 'r', encoding='utf-8') as f:
    spec2 = f.read()

# Relatório 3: AURORA_MODULES_SPEC_LEGIVEL.md
with open('AURORA_MODULES_SPEC_LEGIVEL.md', 'r', encoding='utf-8') as f:
    spec3 = f.read()

# 5. Corrigir todas as contagens nos relatórios
print("🔧 Corrigindo contagens...")
spec1 = spec1.replace('259', str(CORRECT_COUNT)).replace('257', str(CORRECT_COUNT)).replace('437', str(CORRECT_COUNT))
spec2 = spec2.replace('259', str(CORRECT_COUNT)).replace('257', str(CORRECT_COUNT)).replace('437', str(CORRECT_COUNT))
spec3 = spec3.replace('259', str(CORRECT_COUNT)).replace('257', str(CORRECT_COUNT)).replace('437', str(CORRECT_COUNT))

# 6. Criar documento consolidado
print("📝 Criando documento consolidado...")

consolidated = f"""# AURORA v5.1 - Complete Technical Document (Consolidated)
**Document ID:** TS-AURORA-5.1-CONSOLIDATED-{datetime.now().strftime('%Y%m%d')}  
**Classification:** Technical Specification  
**Format:** IEEE/IETF Standard  
**Version:** 5.1.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** Production  
**Total Modules:** {CORRECT_COUNT} (System Modules - Verified)

---

## ⚠️ NOTA IMPORTANTE

Este documento consolida os 3 relatórios técnicos do sistema AURORA:
1. AURORA_TECHNICAL_SPECIFICATION.md (Especificação Técnica Formal)
2. AURORA_COMPLETE_TECHNICAL_SPECIFICATION.md (Especificação Completa)
3. AURORA_MODULES_SPEC_LEGIVEL.md (Especificação de Módulos Legível)

**Contagem verificada:** {CORRECT_COUNT} módulos do sistema (scripts utilitários excluídos)

---

# PARTE 1: ESPECIFICAÇÃO TÉCNICA FORMAL

"""

# Adicionar Parte 1 (do primeiro relatório, mas sem duplicar metadados)
spec1_clean = spec1.split('## 1. DOCUMENT METADATA')[1]  # Pular metadados duplicados
consolidated += spec1_clean

consolidated += f"""

---

# PARTE 2: ESPECIFICAÇÃO COMPLETA DE MÓDULOS

"""

# Adicionar Parte 2 (do segundo relatório, mas sem duplicar metadados)
spec2_clean = spec2.split('## 1. EXECUTIVE SUMMARY')[1]  # Pular metadados duplicados
consolidated += spec2_clean

consolidated += f"""

---

# PARTE 3: ESPECIFICAÇÃO DE MÓDULOS (LEGÍVEL)

"""

# Adicionar Parte 3 (do terceiro relatório, mas sem duplicar metadados)
spec3_clean = spec3.split('## METADADOS DO SISTEMA')[1]  # Pular metadados duplicados
consolidated += spec3_clean

# 7. Adicionar lista completa de módulos
consolidated += f"""

---

# PARTE 4: LISTA COMPLETA DE MÓDULOS ({CORRECT_COUNT} System Modules)

## 4.1 Complete Module List

```
"""

for module in sorted(system_modules, key=lambda x: x['path']):
    consolidated += f"{module['path']}\n"

consolidated += """```

---

## 4.2 Module Details by Category

"""

for cat in sorted(categories.keys()):
    modules = categories[cat]
    consolidated += f"### {cat} ({len(modules)} modules)\n\n"
    
    for module in sorted(modules, key=lambda x: x['path']):
        path = module['path']
        if 'error' not in module:
            classes = len(module.get('classes', []))
            functions = len(module.get('functions', []))
            consolidated += f"- `{path}` ({classes} classes, {functions} functions)\n"
        else:
            consolidated += f"- `{path}` (ERROR)\n"
    
    consolidated += "\n"

# 8. Adicionar verificação final
consolidated += f"""

---

# VERIFICAÇÃO FINAL

## Contagem Verificada

- **Módulos reais do sistema:** {CORRECT_COUNT}
- **Módulos documentados:** {len(system_modules)}
- **Status:** {'✅ CORRETO' if CORRECT_COUNT == len(system_modules) else '❌ ERRO'}

## Distribuição por Categoria

"""

for cat in sorted(categories.keys()):
    consolidated += f"- **{cat}**: {len(categories[cat])} módulos\n"

consolidated += f"""

---

**END OF CONSOLIDATED TECHNICAL DOCUMENT**

*Documento gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Total de módulos do sistema: {CORRECT_COUNT}*
"""

# 9. Salvar
output_file = 'AURORA_COMPLETE_TECHNICAL_DOCUMENT_CONSOLIDATED.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(consolidated)

print(f"\n✅ Documento consolidado criado: {output_file}")
print(f"   Tamanho: {len(consolidated):,} caracteres")
print(f"   Módulos documentados: {CORRECT_COUNT}")
print(f"   Status: {'✅ CORRETO' if CORRECT_COUNT == len(system_modules) else '❌ ERRO'}")

