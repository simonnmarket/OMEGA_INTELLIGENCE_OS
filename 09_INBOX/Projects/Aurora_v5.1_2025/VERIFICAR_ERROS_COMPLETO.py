#!/usr/bin/env python3
"""Verificação completa de erros no documento técnico"""

import re
from pathlib import Path
from collections import Counter

print("=" * 70)
print("VERIFICAÇÃO COMPLETA DE ERROS - AURORA_COMPLETE_TECHNICAL_DOCUMENT.md")
print("=" * 70)

doc_path = Path('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md')

with open(doc_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

print(f"\n📄 Total de linhas: {len(lines)}")
print(f"📄 Total de caracteres: {len(content)}")

# 1. Verificar "emotion" em todas as variações possíveis
emotion_patterns = [
    r'\bemotion\b',
    r'\bemotions\b',
    r'\bEmotion\b',
    r'\bEmotions\b',
    r'\bEMOTION\b',
    r'\bEMOTIONS\b',
    r'emotion',
    r'emotions',
]

emotion_errors = []
for pattern in emotion_patterns:
    matches = list(re.finditer(pattern, content, re.IGNORECASE))
    if matches:
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            emotion_errors.append((line_num, match.group(), match.start()))

print(f"\n1️⃣  VERIFICAÇÃO 'EMOTION':")
if emotion_errors:
    print(f"   ❌ Encontrado: {len(emotion_errors)} ocorrências")
    for line_num, word, pos in emotion_errors[:20]:
        print(f"      Linha {line_num}, posição {pos}: '{word}'")
else:
    print(f"   ✅ Nenhuma referência a 'emotion' encontrada")

# 2. Verificar problemas de formatação Markdown
md_errors = []
md_patterns = [
    (r'```[^`\n]*$', 'Bloco de código não fechado'),
    (r'^\*\*[^*]+\*\*[^*]', 'Formatação Markdown suspeita'),
    (r'\[.*\]\([^)]*$', 'Link não fechado'),
    (r'^#{1,6}\s+$', 'Cabeçalho vazio'),
]

for pattern, desc in md_patterns:
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    if matches:
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            md_errors.append((line_num, desc, match.group()[:50]))

print(f"\n2️⃣  VERIFICAÇÃO MARKDOWN:")
if md_errors:
    print(f"   ⚠️  Encontrado: {len(md_errors)} problemas")
    for line_num, desc, sample in md_errors[:20]:
        print(f"      Linha {line_num}: {desc} - '{sample}'")
else:
    print(f"   ✅ Nenhum problema de formatação Markdown")

# 3. Verificar caracteres problemáticos
char_errors = []
for i, line in enumerate(lines, 1):
    # Caracteres de controle (exceto \n, \r, \t)
    if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', line):
        char_errors.append((i, 'Caractere de controle', repr(line[:50])))
    # Tabs (devem ser espaços em Markdown)
    if '\t' in line:
        char_errors.append((i, 'Tab encontrado', 'deve ser espaços'))

print(f"\n3️⃣  VERIFICAÇÃO CARACTERES:")
if char_errors:
    print(f"   ⚠️  Encontrado: {len(char_errors)} problemas")
    for line_num, desc, info in char_errors[:20]:
        print(f"      Linha {line_num}: {desc}")
else:
    print(f"   ✅ Nenhum caractere problemático")

# 4. Verificar linhas muito longas
long_lines = [(i+1, len(line)) for i, line in enumerate(lines) if len(line) > 1000]

print(f"\n4️⃣  VERIFICAÇÃO LINHAS LONGAS:")
if long_lines:
    print(f"   ⚠️  Encontrado: {len(long_lines)} linhas > 1000 caracteres")
    for line_num, length in long_lines[:10]:
        print(f"      Linha {line_num}: {length} caracteres")
else:
    print(f"   ✅ Nenhuma linha muito longa")

# 5. Verificar encoding
encoding_errors = []
try:
    content.encode('utf-8')
except UnicodeEncodeError as e:
    encoding_errors.append(('Erro de encoding', str(e)))

print(f"\n5️⃣  VERIFICAÇÃO ENCODING:")
if encoding_errors:
    print(f"   ❌ Problemas de encoding encontrados")
    for desc, info in encoding_errors:
        print(f"      {desc}: {info}")
else:
    print(f"   ✅ Encoding UTF-8 válido")

# 6. Verificar palavras suspeitas que podem ser "emotion" mal formatado
suspicious = []
suspicious_patterns = [
    r'\bem[oi]t[io]n\w*\b',
    r'\bem[oi]t[io]ns\b',
    r'\be\s*m\s*o\s*t\s*i\s*o\s*n\s*s?\b',
]

for pattern in suspicious_patterns:
    matches = list(re.finditer(pattern, content, re.IGNORECASE))
    if matches:
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            suspicious.append((line_num, match.group(), match.start()))

print(f"\n6️⃣  VERIFICAÇÃO PADRÕES SUSPEITOS:")
if suspicious:
    print(f"   ⚠️  Encontrado: {len(suspicious)} padrões suspeitos")
    for line_num, word, pos in suspicious[:20]:
        print(f"      Linha {line_num}, posição {pos}: '{word}'")
else:
    print(f"   ✅ Nenhum padrão suspeito encontrado")

# RESUMO TOTAL
total_errors = len(emotion_errors) + len(md_errors) + len(char_errors) + len(long_lines) + len(encoding_errors) + len(suspicious)

print(f"\n" + "=" * 70)
print(f"📊 RESUMO TOTAL:")
print(f"   Total de problemas encontrados: {total_errors}")
print(f"   - Referências a 'emotion': {len(emotion_errors)}")
print(f"   - Erros de formatação MD: {len(md_errors)}")
print(f"   - Caracteres problemáticos: {len(char_errors)}")
print(f"   - Linhas muito longas: {len(long_lines)}")
print(f"   - Problemas de encoding: {len(encoding_errors)}")
print(f"   - Padrões suspeitos: {len(suspicious)}")

if total_errors == 0:
    print(f"\n✅ Nenhum problema encontrado!")
else:
    print(f"\n⚠️  {total_errors} problemas encontrados que podem precisar de correção")

print("\n" + "=" * 70)

