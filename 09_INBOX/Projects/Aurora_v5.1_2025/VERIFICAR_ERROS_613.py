#!/usr/bin/env python3
"""Verificar e corrigir 613 erros relacionados a 'emotions' no relatório"""

import re
from pathlib import Path

print("=" * 70)
print("VERIFICAÇÃO DE ERROS - AURORA_COMPLETE_TECHNICAL_DOCUMENT.md")
print("=" * 70)

doc_path = Path('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md')

# Ler o documento
with open(doc_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

print(f"\n📄 Total de linhas no documento: {len(lines)}")

# Procurar por padrões problemáticos
errors_found = []

# 1. Procurar por "emotion" (case insensitive)
emotion_pattern = re.compile(r'emotion', re.IGNORECASE)
emotion_matches = []
for i, line in enumerate(lines, 1):
    if emotion_pattern.search(line):
        emotion_matches.append((i, line))
        errors_found.append(('emotion', i, line))

print(f"\n🔍 Verificando padrões problemáticos:")

if emotion_matches:
    print(f"   ❌ Encontrado 'emotion' em {len(emotion_matches)} linhas:")
    for num, line in emotion_matches[:20]:
        print(f"      Linha {num}: {line[:100]}")
else:
    print(f"   ✅ Nenhuma referência a 'emotion' encontrada")

# 2. Procurar por caracteres problemáticos que podem causar erros
problematic_chars = []
char_patterns = [
    (r'[^\x00-\x7F]', 'Caracteres não-ASCII'),
    (r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', 'Caracteres de controle'),
    (r'\t', 'Tabs'),
]

for pattern_name, pattern in char_patterns:
    matches = []
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line):
            matches.append((i, line))
    if matches:
        print(f"\n   ⚠️  {pattern_name}: {len(matches)} linhas")
        problematic_chars.extend(matches[:10])

# 3. Procurar por problemas de formatação Markdown
md_errors = []
md_patterns = [
    (r'```[^`\n]*$', 'Bloco de código não fechado'),
    (r'^\*\*[^*]+\*\*[^*]', 'Formatação Markdown suspeita'),
    (r'\[.*\]\([^)]*$', 'Link Markdown não fechado'),
]

for pattern, desc in md_patterns:
    matches = []
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line):
            matches.append((i, line))
    if matches:
        print(f"\n   ⚠️  {desc}: {len(matches)} linhas")
        md_errors.extend(matches[:10])

# 4. Procurar por linhas muito longas (podem causar problemas)
long_lines = [(i, line) for i, line in enumerate(lines, 1) if len(line) > 500]
if long_lines:
    print(f"\n   ⚠️  Linhas muito longas (>500 chars): {len(long_lines)}")

# 5. Verificar encoding e caracteres especiais problemáticos
encoding_issues = []
for i, line in enumerate(lines, 1):
    try:
        line.encode('utf-8')
    except UnicodeEncodeError:
        encoding_issues.append((i, line))
    # Procurar por caracteres que podem causar problemas em alguns parsers
    if re.search(r'[^\x20-\x7E\n\r\t]', line) and not re.search(r'[àáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ]', line):
        # Verificar se não é apenas acentuação portuguesa
        if any(ord(c) > 127 for c in line):
            encoding_issues.append((i, line))

if encoding_issues:
    print(f"\n   ⚠️  Possíveis problemas de encoding: {len(encoding_issues)} linhas")

# 6. Contar total de problemas encontrados
total_issues = len(emotion_matches) + len(problematic_chars) + len(md_errors) + len(long_lines) + len(encoding_issues)

print(f"\n" + "=" * 70)
print(f"📊 RESUMO:")
print(f"   Total de problemas encontrados: {total_issues}")
print(f"   - Referências a 'emotion': {len(emotion_matches)}")
print(f"   - Caracteres problemáticos: {len(problematic_chars)}")
print(f"   - Erros de formatação MD: {len(md_errors)}")
print(f"   - Linhas muito longas: {len(long_lines)}")
print(f"   - Problemas de encoding: {len(encoding_issues)}")

if total_issues == 0:
    print(f"\n✅ Nenhum problema encontrado!")
else:
    print(f"\n⚠️  Problemas encontrados que precisam ser corrigidos")

# Se encontrou "emotion", vamos corrigir
if emotion_matches:
    print(f"\n🔧 CORRIGINDO referências a 'emotion'...")
    corrected_content = content
    corrections = 0
    
    # Remover ou corrigir referências a emotion
    for num, line in emotion_matches:
        # Verificar contexto para entender o que fazer
        if 'emotion' in line.lower():
            # Se for um erro óbvio, remover
            if re.search(r'\bemotion\b', line, re.IGNORECASE):
                # Substituir por string vazia ou comentário
                corrected_content = corrected_content.replace(line, '', 1)
                corrections += 1
    
    if corrections > 0:
        # Fazer backup
        backup_path = doc_path.with_suffix('.md.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Backup criado: {backup_path}")
        
        # Salvar correção
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        print(f"   ✅ {corrections} correções aplicadas")
    else:
        print(f"   ℹ️  Nenhuma correção automática possível")

print("\n" + "=" * 70)

