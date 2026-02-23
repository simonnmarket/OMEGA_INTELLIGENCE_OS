#!/usr/bin/env python3
"""Corrigir MD025: Múltiplos H1 - manter apenas o primeiro, converter outros para H2"""

import re
from pathlib import Path

print("=" * 70)
print("CORREÇÃO MD025: Múltiplos H1 no documento")
print("=" * 70)

doc_path = Path('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md')

with open(doc_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"\n📄 Total de linhas: {len(lines)}")

# Encontrar todos os H1
h1_positions = []
for i, line in enumerate(lines):
    if re.match(r'^#\s+', line):
        h1_positions.append((i, line.strip()))

print(f"\n🔍 H1 encontrados: {len(h1_positions)}")
for idx, (line_num, text) in enumerate(h1_positions[:10]):
    print(f"   {idx+1}. Linha {line_num+1}: {text[:70]}")

if len(h1_positions) <= 1:
    print("\n✅ Apenas 1 H1 encontrado - MD025 OK!")
    exit(0)

print(f"\n⚠️  {len(h1_positions)} H1 encontrados - MD025 violado!")
print("   Mantendo o primeiro H1, convertendo os demais para H2...")

# Criar backup
backup_path = doc_path.with_suffix('.md.backup_md025')
with open(backup_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print(f"✅ Backup criado: {backup_path}")

# Corrigir: manter primeiro H1, converter outros para H2
corrected_lines = lines.copy()
converted_count = 0

for idx, (line_num, original_text) in enumerate(h1_positions):
    if idx == 0:
        # Primeiro H1 - manter como está
        print(f"   ✅ Mantendo H1 na linha {line_num+1}: {original_text[:50]}")
    else:
        # Outros H1 - converter para H2
        original_line = corrected_lines[line_num]
        # Substituir # por ##
        new_line = re.sub(r'^#\s+', '## ', original_line)
        corrected_lines[line_num] = new_line
        converted_count += 1
        print(f"   🔄 Convertendo H1→H2 na linha {line_num+1}: {original_text[:50]}")

# Salvar arquivo corrigido
with open(doc_path, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(corrected_lines)

print(f"\n✅ {converted_count} H1 convertidos para H2")
print(f"✅ Arquivo corrigido: {doc_path}")

# Verificação final
print("\n🔍 VERIFICAÇÃO FINAL:")
final_h1 = []
for i, line in enumerate(corrected_lines):
    if re.match(r'^#\s+', line):
        final_h1.append((i+1, line.strip()))

if len(final_h1) == 1:
    print(f"   ✅ Apenas 1 H1 restante - MD025 CORRIGIDO!")
    print(f"   H1 na linha {final_h1[0][0]}: {final_h1[0][1][:70]}")
else:
    print(f"   ⚠️  Ainda há {len(final_h1)} H1 - verificar manualmente")

print("\n" + "=" * 70)
print("✅ PROCESSO CONCLUÍDO")

