#!/usr/bin/env python3
"""
VALIDAÇÃO AUTOMÁTICA ANTES DE SALVAR DOCUMENTOS MARKDOWN
Este script deve ser executado antes de salvar qualquer documento Markdown
"""

import sys
from pathlib import Path

# Adicionar o diretório atual ao path para importar o protector
sys.path.insert(0, str(Path(__file__).parent))

from PROTECAO_MARKDOWN_LINT import MarkdownLintProtector

def main():
    """Valida e corrige automaticamente documentos Markdown"""
    print("=" * 70)
    print("VALIDAÇÃO E PROTEÇÃO MARKDOWN - AURORA")
    print("=" * 70)
    
    protector = MarkdownLintProtector()
    
    # Arquivo principal
    main_file = Path('AURORA_COMPLETE_TECHNICAL_DOCUMENT.md')
    
    if not main_file.exists():
        print(f"❌ Arquivo não encontrado: {main_file}")
        return 1
    
    print(f"\n📄 Validando: {main_file.name}")
    
    # Validar
    errors = protector.validate_file(main_file)
    
    if errors:
        total_errors = sum(len(v) for v in errors.values())
        print(f"\n⚠️  {total_errors} erros encontrados:")
        for code, error_list in sorted(errors.items()):
            print(f"   {code}: {len(error_list)} erros")
        
        # Perguntar se deve corrigir automaticamente
        print("\n🔧 Aplicar correções automáticas? (s/N): ", end='')
        response = input().strip().lower()
        
        if response == 's':
            corrections = protector.auto_fix(main_file, create_backup=True)
            print(f"\n✅ Correções aplicadas:")
            for code, count in corrections.items():
                print(f"   {code}: {count} correções")
            
            # Verificar novamente
            final_errors = protector.validate_file(main_file)
            if final_errors:
                remaining = sum(len(v) for v in final_errors.values())
                print(f"\n⚠️  {remaining} erros ainda restam (podem precisar de correção manual)")
            else:
                print(f"\n✅ Todos os erros corrigidos!")
        else:
            print("\n⚠️  Correções não aplicadas. Execute novamente com --fix para corrigir automaticamente.")
            return 1
    else:
        print("\n✅ Nenhum erro encontrado - documento está em conformidade!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

