#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Alpha - Scanner Simplificado
Versão: v1.0 | Data: 2025-07-30
Escaneia apenas arquivos do projeto Numeia
"""

import os
import json
import re
from datetime import datetime

def scan_numeia_project():
    """Escaneia apenas arquivos do projeto Numeia"""
    
    # Diretório raiz do projeto
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Extensões MQL5
    mql5_extensions = ['.mq5', '.mqh']
    
    # Arquivos e dependências encontrados
    files_data = []
    dependencies = []
    
    print("🔍 Escaneando projeto Numeia...")
    
    # Percorre apenas o diretório do projeto
    for root, dirs, files in os.walk(root_dir):
        # Ignora diretórios do MetaTrader
        if 'MetaQuotes' in root or 'Terminal' in root:
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in mql5_extensions):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Encontra includes
                    includes = re.findall(r'#include\s+["<]([^">]+)[">]', content)
                    
                    file_info = {
                        'file': relative_path,
                        'size': os.path.getsize(file_path),
                        'includes': includes,
                        'lines': len(content.split('\n'))
                    }
                    
                    files_data.append(file_info)
                    
                    for include in includes:
                        dependencies.append({
                            'from': relative_path,
                            'to': include,
                            'type': 'include'
                        })
                        
                except Exception as e:
                    print(f"⚠️ Erro ao ler {relative_path}: {e}")
    
    # Gera relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'project': 'Numeia',
        'total_files': len(files_data),
        'total_dependencies': len(dependencies),
        'files': files_data,
        'dependencies': dependencies
    }
    
    # Salva dependencies.json
    with open(os.path.join(root_dir, 'dependencies.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Salva relatório de erros
    error_report = {
        'timestamp': datetime.now().isoformat(),
        'project': 'Numeia',
        'status': 'COMPLETED',
        'files_scanned': len(files_data),
        'dependencies_found': len(dependencies),
        'errors': [],
        'summary': {
            'total_files': len(files_data),
            'files_with_includes': len([f for f in files_data if f['includes']]),
            'total_includes': sum(len(f['includes']) for f in files_data)
        }
    }
    
    with open(os.path.join(root_dir, 'error_report.json'), 'w', encoding='utf-8') as f:
        json.dump(error_report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Escaneamento concluído!")
    print(f"📁 Arquivos encontrados: {len(files_data)}")
    print(f"🔗 Dependências encontradas: {len(dependencies)}")
    print(f"📄 dependencies.json gerado")
    print(f"📊 error_report.json gerado")
    
    return report

if __name__ == "__main__":
    scan_numeia_project() 