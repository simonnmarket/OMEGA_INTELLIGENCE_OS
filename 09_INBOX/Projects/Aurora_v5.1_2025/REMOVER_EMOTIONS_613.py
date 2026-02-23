#!/usr/bin/env python3
"""Remover todas as referências a 'emotion'/'emotions' do documento técnico"""

import re
from pathlib import Path

print("=" * 70)
print("REMOÇÃO DE REFERÊNCIAS A 'EMOTION'/'EMOTIONS'")
print("=" * 70)

doc_path = Path('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md')

# Ler o documento
with open(doc_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

print(f"\n📄 Total de linhas: {len(lines)}")

# Padrões para encontrar "emotion" em qualquer variação
patterns = [
    (r'\bemotion\b', 'emotion'),
    (r'\bemotions\b', 'emotions'),
    (r'\bEmotion\b', 'Emotion'),
    (r'\bEmotions\b', 'Emotions'),
    (r'\bEMOTION\b', 'EMOTION'),
    (r'\bEMOTIONS\b', 'EMOTIONS'),
    (r'\bEmo[Tt]ion\b', 'Emotion (case variant)'),
    (r'\bEmo[Tt]ions\b', 'Emotions (case variant)'),
]

# Encontrar todas as ocorrências
all_matches = []
for pattern, desc in patterns:
    matches = list(re.finditer(pattern, content, re.IGNORECASE))
    if matches:
        print(f"\n🔍 Padrão '{desc}': {len(matches)} ocorrências")
        for match in matches[:10]:  # Mostrar primeiras 10
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].replace('\n', ' ')
            print(f"   Posição {match.start()}: ...{context}...")
        all_matches.extend(matches)

# Também procurar em palavras compostas ou com hífen
compound_patterns = [
    r'emotion[-_]',
    r'[-_]emotion',
    r'emotion\w+',
    r'\w+emotion',
]

for pattern in compound_patterns:
    matches = list(re.finditer(pattern, content, re.IGNORECASE))
    if matches:
        print(f"\n🔍 Padrão composto '{pattern}': {len(matches)} ocorrências")
        for match in matches[:5]:
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].replace('\n', ' ')
            print(f"   Posição {match.start()}: ...{context}...")
        all_matches.extend(matches)

# Remover duplicatas (mesma posição)
unique_matches = []
seen_positions = set()
for match in all_matches:
    if match.start() not in seen_positions:
        unique_matches.append(match)
        seen_positions.add(match.start())

print(f"\n📊 RESUMO:")
print(f"   Total de ocorrências únicas encontradas: {len(unique_matches)}")

if len(unique_matches) == 0:
    print("\n✅ Nenhuma referência a 'emotion'/'emotions' encontrada!")
    print("   O documento já está limpo.")
else:
    print(f"\n🔧 REMOVENDO {len(unique_matches)} ocorrências...")
    
    # Ordenar por posição (do final para o início para não alterar índices)
    unique_matches.sort(key=lambda m: m.start(), reverse=True)
    
    # Criar backup
    backup_path = doc_path.with_suffix('.md.backup_emotion_removal')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   ✅ Backup criado: {backup_path}")
    
    # Remover ocorrências (do final para o início)
    corrected_content = content
    removed_count = 0
    
    for match in unique_matches:
        # Verificar contexto para decidir como remover
        start = match.start()
        end = match.end()
        
        # Se for uma palavra isolada, remover apenas a palavra
        if re.match(r'\b\w+\b', match.group()):
            # Verificar se há espaço antes e depois
            before_char = content[start-1] if start > 0 else ' '
            after_char = content[end] if end < len(content) else ' '
            
            # Se houver espaços, remover a palavra e um espaço adjacente
            if before_char == ' ' and after_char == ' ':
                # Remover palavra e um espaço
                corrected_content = corrected_content[:start-1] + corrected_content[end:]
            elif before_char == ' ':
                # Remover espaço antes e palavra
                corrected_content = corrected_content[:start-1] + corrected_content[end:]
            elif after_char == ' ':
                # Remover palavra e espaço depois
                corrected_content = corrected_content[:start] + corrected_content[end+1:]
            else:
                # Apenas remover a palavra
                corrected_content = corrected_content[:start] + corrected_content[end:]
        else:
            # Remover como está
            corrected_content = corrected_content[:start] + corrected_content[end:]
        
        removed_count += 1
    
    # Salvar arquivo corrigido
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    print(f"   ✅ {removed_count} ocorrências removidas")
    print(f"   ✅ Arquivo salvo: {doc_path}")
    
    # Verificação final
    print(f"\n🔍 VERIFICAÇÃO FINAL:")
    final_check = re.findall(r'\bemotion\w*\b', corrected_content, re.IGNORECASE)
    if final_check:
        print(f"   ⚠️  Ainda restam {len(final_check)} ocorrências")
        print(f"   Exemplos: {set(final_check[:10])}")
    else:
        print(f"   ✅ Nenhuma referência a 'emotion' restante!")

print("\n" + "=" * 70)
print("✅ PROCESSO CONCLUÍDO")

