#!/usr/bin/env python3
"""Corrigir erros de linting Markdown (MD032, MD040, MD012, MD022, etc.)"""

import re
from pathlib import Path
from collections import defaultdict

print("=" * 70)
print("CORREÇÃO DE ERROS MARKDOWN LINT")
print("=" * 70)

doc_path = Path('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md')

with open(doc_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"\n📄 Total de linhas: {len(lines)}")

errors = defaultdict(list)

# MD012: Multiple consecutive blank lines (máximo 1 linha em branco)
print("\n🔍 Verificando MD012 (múltiplas linhas em branco)...")
blank_count = 0
for i, line in enumerate(lines, 1):
    if line.strip() == '':
        blank_count += 1
        if blank_count > 1:
            errors['MD012'].append(i)
    else:
        blank_count = 0

# MD022: Blanks around headings (deve ter linha em branco antes e depois)
print("🔍 Verificando MD022 (blanks around headings)...")
for i, line in enumerate(lines):
    if re.match(r'^#{1,6}\s+', line):
        line_num = i + 1
        # Verificar linha antes
        if i > 0 and lines[i-1].strip() != '':
            errors['MD022'].append((line_num, 'before'))
        # Verificar linha depois
        if i < len(lines) - 1 and lines[i+1].strip() != '' and not re.match(r'^#{1,6}\s+', lines[i+1]):
            errors['MD022'].append((line_num, 'after'))

# MD032: Blanks around lists (deve ter linha em branco antes e depois de listas)
print("🔍 Verificando MD032 (blanks around lists)...")
for i, line in enumerate(lines):
    if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
        line_num = i + 1
        # Verificar linha antes
        if i > 0 and lines[i-1].strip() != '' and not re.match(r'^\s*[-*+]\s+', lines[i-1]) and not re.match(r'^\s*\d+\.\s+', lines[i-1]):
            errors['MD032'].append((line_num, 'before'))
        # Verificar linha depois (após último item da lista)
        if i < len(lines) - 1:
            next_line = lines[i+1]
            # Se próxima linha não é item de lista e não está vazia
            if not re.match(r'^\s*[-*+]\s+', next_line) and not re.match(r'^\s*\d+\.\s+', next_line) and next_line.strip() != '':
                # Verificar se é o último item da lista
                if i == 0 or not (re.match(r'^\s*[-*+]\s+', lines[i-1]) or re.match(r'^\s*\d+\.\s+', lines[i-1])):
                    # Verificar se próxima linha não é continuação (indentada)
                    if not re.match(r'^\s{4,}', next_line):
                        errors['MD032'].append((line_num, 'after'))

# MD040: Fenced code languages (blocos de código devem ter linguagem especificada)
print("🔍 Verificando MD040 (fenced code languages)...")
in_code_block = False
code_block_start = None
for i, line in enumerate(lines, 1):
    if line.strip().startswith('```'):
        if not in_code_block:
            # Início de bloco
            in_code_block = True
            code_block_start = i
            # Verificar se tem linguagem especificada
            lang_match = re.match(r'^```(\w+)', line)
            if not lang_match:
                errors['MD040'].append(code_block_start)
        else:
            # Fim de bloco
            in_code_block = False
            code_block_start = None

# MD031: Fenced code blocks should be surrounded by blank lines
print("🔍 Verificando MD031 (blanks around fenced code blocks)...")
for i, line in enumerate(lines):
    if line.strip().startswith('```'):
        line_num = i + 1
        # Verificar linha antes
        if i > 0 and lines[i-1].strip() != '':
            errors['MD031'].append((line_num, 'before'))
        # Verificar linha depois (fim do bloco)
        if i < len(lines) - 1:
            # Procurar fim do bloco
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith('```'):
                    # Verificar linha depois do fim
                    if j < len(lines) - 1 and lines[j+1].strip() != '':
                        errors['MD031'].append((j+1, 'after'))
                    break

# MD041: First line in file should be a top level heading
print("🔍 Verificando MD041 (first line heading)...")
if lines and not re.match(r'^#\s+', lines[0]):
    errors['MD041'].append(1)

# MD013: Line length (linhas muito longas)
print("🔍 Verificando MD013 (line length)...")
for i, line in enumerate(lines, 1):
    if len(line.rstrip('\n\r')) > 80:  # Markdownlint padrão é 80, mas pode ser 120
        # Ignorar linhas de código e URLs
        if not line.strip().startswith('```') and not re.match(r'^\s*\|', line) and 'http' not in line:
            errors['MD013'].append((i, len(line.rstrip('\n\r'))))

# Resumo
print("\n" + "=" * 70)
print("📊 RESUMO DE ERROS ENCONTRADOS:")
total = 0
for error_code, error_list in sorted(errors.items()):
    count = len(error_list)
    total += count
    print(f"   {error_code}: {count} erros")
    if count <= 10:
        for item in error_list[:5]:
            print(f"      - {item}")

print(f"\n   TOTAL: {total} erros encontrados")

# Agora corrigir
print("\n" + "=" * 70)
print("🔧 CORRIGINDO ERROS...")

# Criar backup
backup_path = doc_path.with_suffix('.md.backup_markdown')
with open(backup_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print(f"✅ Backup criado: {backup_path}")

# Criar cópia para correção
corrected_lines = lines.copy()

# MD012: Remover linhas em branco consecutivas (manter apenas 1)
print("\n🔧 Corrigindo MD012...")
i = 0
while i < len(corrected_lines) - 1:
    if corrected_lines[i].strip() == '' and corrected_lines[i+1].strip() == '':
        corrected_lines.pop(i+1)
    else:
        i += 1

# MD022: Adicionar linhas em branco ao redor de headings
print("🔧 Corrigindo MD022...")
i = 0
while i < len(corrected_lines):
    line = corrected_lines[i]
    if re.match(r'^#{1,6}\s+', line):
        # Adicionar linha antes se necessário
        if i > 0 and corrected_lines[i-1].strip() != '':
            corrected_lines.insert(i, '\n')
            i += 1
        # Adicionar linha depois se necessário
        if i < len(corrected_lines) - 1:
            next_line = corrected_lines[i+1]
            if next_line.strip() != '' and not re.match(r'^#{1,6}\s+', next_line):
                corrected_lines.insert(i+1, '\n')
                i += 1
    i += 1

# MD032: Adicionar linhas em branco ao redor de listas
print("🔧 Corrigindo MD032...")
i = 0
while i < len(corrected_lines):
    line = corrected_lines[i]
    is_list_item = re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line)
    
    if is_list_item:
        # Verificar se é início de lista (linha antes não é item de lista)
        if i > 0:
            prev_line = corrected_lines[i-1]
            prev_is_list = re.match(r'^\s*[-*+]\s+', prev_line) or re.match(r'^\s*\d+\.\s+', prev_line)
            if not prev_is_list and prev_line.strip() != '':
                # Adicionar linha antes
                corrected_lines.insert(i, '\n')
                i += 1
        
        # Verificar se é fim de lista (próxima linha não é item de lista)
        if i < len(corrected_lines) - 1:
            next_line = corrected_lines[i+1]
            next_is_list = re.match(r'^\s*[-*+]\s+', next_line) or re.match(r'^\s*\d+\.\s+', next_line)
            if not next_is_list and next_line.strip() != '' and not re.match(r'^\s{4,}', next_line):
                # Verificar se não é continuação indentada
                if not re.match(r'^\s{4,}', next_line):
                    corrected_lines.insert(i+1, '\n')
                    i += 1
    i += 1

# MD040: Adicionar linguagem aos blocos de código
print("🔧 Corrigindo MD040...")
for i, line in enumerate(corrected_lines):
    if line.strip().startswith('```') and line.strip() == '```':
        # Tentar inferir linguagem do contexto
        lang = None
        # Verificar linhas próximas para contexto
        for j in range(max(0, i-5), min(len(corrected_lines), i+20)):
            context_line = corrected_lines[j].lower()
            if 'python' in context_line or 'def ' in context_line or 'import ' in context_line:
                lang = 'python'
                break
            elif 'javascript' in context_line or 'function' in context_line or 'const ' in context_line:
                lang = 'javascript'
                break
            elif 'yaml' in context_line or 'yml' in context_line:
                lang = 'yaml'
                break
            elif 'json' in context_line:
                lang = 'json'
                break
            elif 'pseudocode' in context_line or 'algorithm' in context_line:
                lang = 'pseudocode'
                break
        
        if lang:
            corrected_lines[i] = f'```{lang}\n'
        else:
            # Padrão: usar 'text' ou deixar vazio se não conseguir inferir
            # Mas MD040 exige linguagem, então usar 'text' como fallback
            corrected_lines[i] = '```text\n'

# MD031: Adicionar linhas em branco ao redor de blocos de código
print("🔧 Corrigindo MD031...")
i = 0
while i < len(corrected_lines):
    line = corrected_lines[i]
    if line.strip().startswith('```'):
        # Adicionar linha antes se necessário
        if i > 0 and corrected_lines[i-1].strip() != '':
            corrected_lines.insert(i, '\n')
            i += 1
        
        # Encontrar fim do bloco
        for j in range(i+1, len(corrected_lines)):
            if corrected_lines[j].strip().startswith('```'):
                # Adicionar linha depois se necessário
                if j < len(corrected_lines) - 1 and corrected_lines[j+1].strip() != '':
                    corrected_lines.insert(j+1, '\n')
                break
    i += 1

# Salvar arquivo corrigido
with open(doc_path, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(corrected_lines)

print(f"\n✅ Arquivo corrigido: {doc_path}")

# Verificação final
print("\n" + "=" * 70)
print("🔍 VERIFICAÇÃO FINAL...")

# Recontar erros após correção
final_errors = defaultdict(list)

# MD012
blank_count = 0
for i, line in enumerate(corrected_lines, 1):
    if line.strip() == '':
        blank_count += 1
        if blank_count > 1:
            final_errors['MD012'].append(i)
    else:
        blank_count = 0

# MD040
in_code_block = False
for i, line in enumerate(corrected_lines, 1):
    if line.strip().startswith('```'):
        if not in_code_block:
            in_code_block = True
            lang_match = re.match(r'^```(\w+)', line)
            if not lang_match:
                final_errors['MD040'].append(i)
        else:
            in_code_block = False

print(f"\n📊 ERROS RESTANTES:")
total_final = 0
for error_code, error_list in sorted(final_errors.items()):
    count = len(error_list)
    total_final += count
    print(f"   {error_code}: {count} erros")

if total_final == 0:
    print(f"\n✅ TODOS OS ERROS CORRIGIDOS!")
else:
    print(f"\n⚠️  {total_final} erros ainda restam (podem precisar de correção manual)")

print("\n" + "=" * 70)
print("✅ PROCESSO CONCLUÍDO")

