#!/usr/bin/env python3
"""
SISTEMA DE PROTEÇÃO CONTRA ERROS DE LINTING MARKDOWN
Valida e corrige automaticamente erros comuns antes de salvar documentos Markdown
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

class MarkdownLintProtector:
    """Proteção automática contra erros de linting Markdown"""
    
    def __init__(self):
        self.errors_found = defaultdict(list)
        self.corrections_applied = []
        
    def validate_file(self, file_path: Path) -> Dict:
        """Valida um arquivo Markdown e retorna erros encontrados"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        errors = defaultdict(list)
        
        # MD025: Múltiplos H1
        h1_count = sum(1 for line in lines if re.match(r'^#\s+', line))
        if h1_count > 1:
            h1_lines = [(i+1, line.strip()) for i, line in enumerate(lines) 
                       if re.match(r'^#\s+', line)]
            errors['MD025'] = h1_lines[1:]  # Todos exceto o primeiro
        
        # MD012: Múltiplas linhas em branco consecutivas
        blank_count = 0
        for i, line in enumerate(lines, 1):
            if line.strip() == '':
                blank_count += 1
                if blank_count > 1:
                    errors['MD012'].append(i)
            else:
                blank_count = 0
        
        # MD022: Blanks around headings
        for i, line in enumerate(lines):
            if re.match(r'^#{1,6}\s+', line):
                line_num = i + 1
                if i > 0 and lines[i-1].strip() != '':
                    errors['MD022'].append((line_num, 'before'))
                if i < len(lines) - 1 and lines[i+1].strip() != '' and not re.match(r'^#{1,6}\s+', lines[i+1]):
                    errors['MD022'].append((line_num, 'after'))
        
        # MD032: Blanks around lists
        for i, line in enumerate(lines):
            if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                line_num = i + 1
                if i > 0 and lines[i-1].strip() != '' and not re.match(r'^\s*[-*+]\s+', lines[i-1]) and not re.match(r'^\s*\d+\.\s+', lines[i-1]):
                    errors['MD032'].append((line_num, 'before'))
        
        # MD040: Fenced code languages
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```') and line.strip() == '```':
                errors['MD040'].append(i)
        
        # MD031: Blanks around fenced code blocks
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                if i > 0 and lines[i-1].strip() != '':
                    errors['MD031'].append((i+1, 'before'))
        
        return dict(errors)
    
    def auto_fix(self, file_path: Path, create_backup: bool = True) -> Dict:
        """Corrige automaticamente erros comuns"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if create_backup:
            backup_path = file_path.with_suffix('.md.auto_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        
        corrected_lines = lines.copy()
        corrections = defaultdict(int)
        
        # MD025: Converter H1 extras para H2
        h1_positions = [(i, line) for i, line in enumerate(lines) if re.match(r'^#\s+', line)]
        if len(h1_positions) > 1:
            for idx, (line_num, _) in enumerate(h1_positions[1:], 1):
                original_line = corrected_lines[line_num]
                corrected_lines[line_num] = re.sub(r'^#\s+', '## ', original_line)
                corrections['MD025'] += 1
        
        # MD012: Remover linhas em branco consecutivas
        i = 0
        while i < len(corrected_lines) - 1:
            if corrected_lines[i].strip() == '' and corrected_lines[i+1].strip() == '':
                corrected_lines.pop(i+1)
                corrections['MD012'] += 1
            else:
                i += 1
        
        # MD022: Adicionar blanks around headings
        i = 0
        while i < len(corrected_lines):
            line = corrected_lines[i]
            if re.match(r'^#{1,6}\s+', line):
                if i > 0 and corrected_lines[i-1].strip() != '':
                    corrected_lines.insert(i, '\n')
                    corrections['MD022'] += 1
                    i += 1
                if i < len(corrected_lines) - 1:
                    next_line = corrected_lines[i+1]
                    if next_line.strip() != '' and not re.match(r'^#{1,6}\s+', next_line):
                        corrected_lines.insert(i+1, '\n')
                        corrections['MD022'] += 1
                        i += 1
            i += 1
        
        # MD032: Adicionar blanks around lists
        i = 0
        while i < len(corrected_lines):
            line = corrected_lines[i]
            is_list_item = re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line)
            
            if is_list_item:
                if i > 0:
                    prev_line = corrected_lines[i-1]
                    prev_is_list = re.match(r'^\s*[-*+]\s+', prev_line) or re.match(r'^\s*\d+\.\s+', prev_line)
                    if not prev_is_list and prev_line.strip() != '':
                        corrected_lines.insert(i, '\n')
                        corrections['MD032'] += 1
                        i += 1
            i += 1
        
        # MD040: Adicionar linguagem aos blocos de código
        for i, line in enumerate(corrected_lines):
            if line.strip() == '```':
                # Tentar inferir linguagem
                lang = None
                for j in range(max(0, i-5), min(len(corrected_lines), i+20)):
                    context = corrected_lines[j].lower()
                    if 'python' in context or 'def ' in context:
                        lang = 'python'
                        break
                    elif 'javascript' in context or 'function' in context:
                        lang = 'javascript'
                        break
                    elif 'yaml' in context:
                        lang = 'yaml'
                        break
                    elif 'json' in context:
                        lang = 'json'
                        break
                    elif 'pseudocode' in context:
                        lang = 'pseudocode'
                        break
                
                if lang:
                    corrected_lines[i] = f'```{lang}\n'
                    corrections['MD040'] += 1
                else:
                    corrected_lines[i] = '```text\n'
                    corrections['MD040'] += 1
        
        # MD031: Adicionar blanks around fenced code blocks
        i = 0
        while i < len(corrected_lines):
            line = corrected_lines[i]
            if line.strip().startswith('```'):
                if i > 0 and corrected_lines[i-1].strip() != '':
                    corrected_lines.insert(i, '\n')
                    corrections['MD031'] += 1
                    i += 1
            i += 1
        
        # Salvar arquivo corrigido
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(corrected_lines)
        
        return dict(corrections)
    
    def protect_file(self, file_path: Path) -> Tuple[bool, Dict]:
        """Valida e corrige automaticamente se necessário"""
        errors = self.validate_file(file_path)
        
        if errors:
            print(f"⚠️  Erros encontrados em {file_path.name}:")
            total = sum(len(v) for v in errors.values())
            print(f"   Total: {total} erros")
            for code, error_list in errors.items():
                print(f"   {code}: {len(error_list)} erros")
            
            corrections = self.auto_fix(file_path)
            if corrections:
                print(f"✅ Correções aplicadas:")
                for code, count in corrections.items():
                    print(f"   {code}: {count} correções")
                return True, corrections
        else:
            print(f"✅ {file_path.name}: Sem erros de linting")
            return False, {}
        
        return False, {}


def create_pre_commit_hook():
    """Cria um hook de pré-commit para validar Markdown"""
    hook_content = '''#!/bin/sh
# Pre-commit hook para validar Markdown
python PROTECAO_MARKDOWN_LINT.py --pre-commit
'''
    hook_path = Path('.git/hooks/pre-commit')
    if hook_path.parent.exists():
        with open(hook_path, 'w') as f:
            f.write(hook_content)
        hook_path.chmod(0o755)
        print("✅ Hook de pré-commit criado")
    else:
        print("⚠️  Diretório .git não encontrado - hook não criado")


if __name__ == '__main__':
    import sys
    
    protector = MarkdownLintProtector()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--pre-commit':
        # Modo pré-commit: validar apenas arquivos modificados
        import subprocess
        result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'], 
                               capture_output=True, text=True)
        md_files = [Path(f) for f in result.stdout.strip().split('\n') if f.endswith('.md')]
        
        if not md_files:
            print("✅ Nenhum arquivo Markdown modificado")
            sys.exit(0)
        
        has_errors = False
        for md_file in md_files:
            if md_file.exists():
                errors = protector.validate_file(md_file)
                if errors:
                    print(f"❌ Erros em {md_file.name}")
                    has_errors = True
        
        if has_errors:
            print("\\n⚠️  Execute: python PROTECAO_MARKDOWN_LINT.py --fix")
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == '--fix':
        # Modo correção: corrigir todos os arquivos .md
        md_files = list(Path('.').glob('*.md'))
        for md_file in md_files:
            if md_file.name.startswith('AURORA_COMPLETE_TECHNICAL_DOCUMENT'):
                protector.protect_file(md_file)
    else:
        # Modo normal: validar arquivo específico ou todos
        if len(sys.argv) > 1:
            target_file = Path(sys.argv[1])
            if target_file.exists():
                protector.protect_file(target_file)
            else:
                print(f"❌ Arquivo não encontrado: {target_file}")
        else:
            # Validar arquivo principal
            main_file = Path('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md')
            if main_file.exists():
                protector.protect_file(main_file)
            else:
                print("❌ Arquivo AURORA_COMPLETE_TECHNICAL_DOCUMENT.md não encontrado")
