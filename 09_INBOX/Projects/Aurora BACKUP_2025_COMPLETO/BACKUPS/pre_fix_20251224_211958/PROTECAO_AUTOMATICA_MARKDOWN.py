#!/usr/bin/env python3
"""
PROTEÇÃO AUTOMÁTICA - Valida Markdown antes de salvar
Pode ser usado como hook de pré-commit ou validação automática
"""

import sys
from pathlib import Path
from PROTECAO_MARKDOWN_LINT import MarkdownLintProtector

def protect_before_save(file_path: str) -> bool:
    """
    Protege arquivo Markdown antes de salvar
    Retorna True se arquivo está OK ou foi corrigido
    """
    protector = MarkdownLintProtector(file_path)
    
    # Validar
    is_valid = protector.validate()
    
    if is_valid:
        return True
    
    # Tentar corrigir automaticamente
    print(f"⚠️  Erros encontrados em {file_path}")
    print(protector.report())
    print("\n🔧 Aplicando correções automáticas...")
    
    if protector.auto_fix():
        # Revalidar após correção
        protector = MarkdownLintProtector(file_path)
        is_valid = protector.validate()
        
        if is_valid:
            print("✅ Arquivo corrigido e validado automaticamente!")
            return True
        else:
            print("⚠️  Ainda há erros após correção automática")
            print(protector.report())
            return False
    
    return False


def validate_all_markdown_files(directory: str = '.') -> bool:
    """Valida todos os arquivos .md no diretório"""
    dir_path = Path(directory)
    md_files = list(dir_path.glob('**/*.md'))
    
    print(f"🔍 Encontrados {len(md_files)} arquivos Markdown")
    
    all_valid = True
    for md_file in md_files:
        # Ignorar backups
        if 'backup' in md_file.name.lower():
            continue
        
        protector = MarkdownLintProtector(md_file)
        is_valid = protector.validate()
        
        if not is_valid:
            print(f"\n❌ {md_file}")
            print(protector.report())
            all_valid = False
    
    if all_valid:
        print("\n✅ Todos os arquivos Markdown estão válidos!")
    
    return all_valid


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        auto_fix = '--fix' in sys.argv or '--auto' in sys.argv
        
        if auto_fix:
            success = protect_before_save(file_path)
            sys.exit(0 if success else 1)
        else:
            protector = MarkdownLintProtector(file_path)
            is_valid = protector.validate()
            if not is_valid:
                print(protector.report())
            sys.exit(0 if is_valid else 1)
    else:
        # Validar todos os arquivos
        success = validate_all_markdown_files()
        sys.exit(0 if success else 1)

