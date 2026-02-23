#!/usr/bin/env python3
"""
Script para identificar e corrigir erros no relatório executivo
"""

import re
import os
from pathlib import Path

def check_markdown_errors(file_path):
    """Verifica erros de formatação Markdown"""
    errors = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Verificar problemas comuns
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # 1. Tabelas: linhas que começam com | devem terminar com |
        if stripped.startswith('|') and not stripped.endswith('|') and '|' in stripped:
            if not stripped.endswith('|') and len(stripped.split('|')) > 2:
                errors.append(f"Linha {i}: Tabela não termina com |")
        
        # 2. Blocos de código não fechados
        if '```' in line:
            count = line.count('```')
            if count % 2 != 0:
                errors.append(f"Linha {i}: Bloco de código possivelmente não fechado")
        
        # 3. Links quebrados
        if re.search(r'\[.*\]\([^)]*$', line):
            errors.append(f"Linha {i}: Link possivelmente quebrado")
        
        # 4. Headers mal formatados
        if re.match(r'^#{1,6}\s+$', stripped):
            errors.append(f"Linha {i}: Header vazio")
        
        # 5. Espaços em excesso
        if stripped.endswith('  ') and not stripped.endswith('  \n'):
            errors.append(f"Linha {i}: Espaços em excesso no final")
    
    # Verificar estrutura de tabelas
    in_table = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('|') and '|' in stripped[1:]:
            if not in_table:
                in_table = True
            # Verificar se todas as colunas estão presentes
            cols = stripped.split('|')
            cols = [c.strip() for c in cols if c.strip()]
            if in_table and i > 1:
                prev_line = lines[i-2].strip() if i > 1 else ''
                if prev_line.startswith('|'):
                    prev_cols = prev_line.split('|')
                    prev_cols = [c.strip() for c in prev_cols if c.strip()]
                    if len(cols) != len(prev_cols) and '---' not in prev_line:
                        errors.append(f"Linha {i}: Número de colunas inconsistente na tabela")
        elif in_table and stripped == '':
            in_table = False
    
    return errors

def fix_markdown_errors(file_path):
    """Corrige erros comuns de formatação Markdown"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    changes = []
    
    for i, line in enumerate(lines):
        original = line
        fixed = line
        
        # Corrigir tabelas que não terminam com |
        if fixed.strip().startswith('|') and '|' in fixed.strip()[1:]:
            if not fixed.strip().endswith('|') and len(fixed.strip().split('|')) > 2:
                # Adicionar | no final se necessário
                if not fixed.rstrip().endswith('|'):
                    fixed = fixed.rstrip() + ' |'
                    changes.append(f"Linha {i+1}: Adicionado | no final da tabela")
        
        # Remover espaços em excesso no final (exceto para quebras de linha Markdown)
        if fixed.rstrip() != fixed and not fixed.endswith('  '):
            fixed = fixed.rstrip()
            if original != fixed:
                changes.append(f"Linha {i+1}: Removidos espaços em excesso")
        
        fixed_lines.append(fixed)
    
    # Verificar e corrigir blocos de código
    code_block_open = False
    for i, line in enumerate(fixed_lines):
        if '```' in line:
            count = line.count('```')
            if count % 2 != 0:
                code_block_open = not code_block_open
            if code_block_open and i == len(fixed_lines) - 1:
                # Adicionar fechamento se necessário
                fixed_lines.append('```')
                changes.append(f"Linha {i+2}: Adicionado fechamento de bloco de código")
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Salvar arquivo corrigido
    if changes:
        backup_path = str(file_path) + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return changes, backup_path
    
    return [], None

if __name__ == "__main__":
    report_path = Path(__file__).parent.parent / "RELATORIO_EXECUTIVO_CONFLITOS_INTERESSE.md"
    
    if not report_path.exists():
        print(f"Arquivo não encontrado: {report_path}")
        exit(1)
    
    print("="*80)
    print("VERIFICANDO ERROS NO RELATÓRIO EXECUTIVO")
    print("="*80)
    print()
    
    # Verificar erros
    errors = check_markdown_errors(report_path)
    
    print(f"Total de erros encontrados: {len(errors)}")
    if errors:
        print("\nErros encontrados:")
        for error in errors[:40]:  # Mostrar primeiros 40
            print(f"  - {error}")
        if len(errors) > 40:
            print(f"  ... e mais {len(errors) - 40} erros")
    else:
        print("Nenhum erro encontrado na verificação automática.")
    
    print()
    print("="*80)
    print("CORRIGINDO ERROS")
    print("="*80)
    print()
    
    # Corrigir erros
    changes, backup = fix_markdown_errors(report_path)
    
    if changes:
        print(f"Total de correções aplicadas: {len(changes)}")
        print("\nCorreções aplicadas:")
        for change in changes[:20]:  # Mostrar primeiras 20
            print(f"  - {change}")
        if len(changes) > 20:
            print(f"  ... e mais {len(changes) - 20} correções")
        print(f"\nBackup salvo em: {backup}")
    else:
        print("Nenhuma correção necessária.")
    
    print()
    print("="*80)
    print("VERIFICAÇÃO FINAL")
    print("="*80)
    print()
    
    # Verificar novamente
    final_errors = check_markdown_errors(report_path)
    print(f"Erros restantes após correção: {len(final_errors)}")
    
    if final_errors:
        print("\nErros que requerem atenção manual:")
        for error in final_errors[:20]:
            print(f"  - {error}")
    else:
        print("✅ Nenhum erro restante!")

