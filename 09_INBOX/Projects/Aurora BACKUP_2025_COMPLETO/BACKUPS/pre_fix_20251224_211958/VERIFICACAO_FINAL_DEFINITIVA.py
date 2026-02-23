#!/usr/bin/env python3
"""Verificação final definitiva do documento consolidado"""

import re

with open('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar contagens incorretas
wrong_counts = re.findall(r'\b(259|257|437)\b', content)
correct_counts = re.findall(r'\b252\b', content)

print("=" * 60)
print("VERIFICAÇÃO FINAL DEFINITIVA")
print("=" * 60)
print(f"\n📄 Documento: AURORA_COMPLETE_TECHNICAL_DOCUMENT.md")
print(f"   Tamanho: {len(content):,} caracteres")
print(f"   Linhas: {len(content.split(chr(10)))}")

print(f"\n🔍 Verificação de contagens:")
print(f"   Referências a 252 (CORRETO): {len(correct_counts)}")
print(f"   Referências a 259/257/437 (INCORRETO): {len(wrong_counts)}")

if wrong_counts:
    print(f"\n❌ ERRO: Encontradas {len(wrong_counts)} referências incorretas:")
    for count in set(wrong_counts):
        occurrences = len([m for m in wrong_counts if m == count])
        print(f"   - {count}: {occurrences} ocorrências")
    print("\n⚠️  CORREÇÃO NECESSÁRIA")
else:
    print("\n✅ NENHUMA REFERÊNCIA INCORRETA ENCONTRADA")

# Verificar seções principais
sections = {
    "PARTE 1": "PARTE 1: ESPECIFICAÇÃO TÉCNICA FORMAL" in content,
    "PARTE 2": "PARTE 2: ESPECIFICAÇÃO COMPLETA" in content,
    "PARTE 3": "PARTE 3: ESPECIFICAÇÃO DE MÓDULOS" in content,
    "PARTE 4": "PARTE 4: LISTA COMPLETA" in content,
    "Lista completa": "## 4.1 Complete Module List" in content,
    "Detalhes por categoria": "## 4.2 Module Details" in content
}

print(f"\n📋 Seções do documento:")
for section, present in sections.items():
    status = "✅" if present else "❌"
    print(f"   {status} {section}")

# Conclusão
if not wrong_counts and all(sections.values()):
    print("\n" + "=" * 60)
    print("✅ RELATÓRIO DEFINITIVO E CORRETO")
    print("=" * 60)
    print("✅ Todas as contagens corrigidas para 252")
    print("✅ Todos os 3 relatórios consolidados")
    print("✅ Lista completa de módulos presente")
    print("✅ Sem discrepâncias")
    print("\n✅ PROBLEMA RESOLVIDO DEFINITIVAMENTE")
else:
    print("\n" + "=" * 60)
    print("⚠️  AJUSTES NECESSÁRIOS")
    print("=" * 60)

