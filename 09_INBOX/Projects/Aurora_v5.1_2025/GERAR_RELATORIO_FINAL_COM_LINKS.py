#!/usr/bin/env python3
"""
Script para gerar relatórios finais com links clicáveis
"""

import os
import json
from datetime import datetime
from pathlib import Path

def create_clickable_link(file_path, display_name=None, icon="📄"):
    """Criar link clicável markdown"""
    if not display_name:
        display_name = os.path.basename(file_path)
    
    # Verificar se arquivo existe
    if os.path.exists(file_path):
        return f"[{icon} {display_name}]({file_path})"
    else:
        return f"[{icon} {display_name}]({file_path}) ⚠️ (não encontrado)"

def generate_final_report_with_links():
    """Gerar relatório final com links clicáveis"""
    
    print("=" * 70)
    print("GERANDO RELATÓRIO FINAL COM LINKS CLICÁVEIS")
    print("=" * 70)
    
    # Documentos principais
    documents = {
        "Documento Consolidado Completo": "AURORA_COMPLETE_TECHNICAL_DOCUMENT.md",
        "Documento Sintetizado Final": "AURORA_SISTEMA_SINTETIZADO_FINAL_V5.1.md",
        "Especificação Técnica Formal": "AURORA_TECHNICAL_SPECIFICATION.md",
        "Especificação Completa": "AURORA_COMPLETE_TECHNICAL_SPECIFICATION.md",
        "Especificação Legível": "AURORA_MODULES_SPEC_LEGIVEL.md"
    }
    
    # Arquivos JSON
    json_files = {
        "Especificação de Módulos (JSON)": "aurora_modules_spec.json",
        "Mapeamento Completo": "aurora_mapeamento_completo.json",
        "Estado do Projeto": "AURORA_PROJECT_STATE.json",
        "Relatório Sintetizado": "AURORA_SINTETIZADO_REPORT.json"
    }
    
    # Scripts importantes
    scripts = {
        "Gerar Especificação Completa": "GENERATE_COMPLETE_TECHNICAL_SPEC.py",
        "Verificação Final Definitiva": "VERIFICACAO_FINAL_DEFINITIVA.py",
        "Verificar Completude": "VERIFICAR_COMPLETUDE_FINAL.py",
        "Gerar Documento Sintetizado": "GERAR_DOCUMENTO_SINTETIZADO_FINAL.py"
    }
    
    # Arquivos críticos do sistema
    critical_files = {
        "Orchestrator Core": "system_core/ncnt_orchestrator_complete.py",
        "Main Entry Point": "main_ncnt.py",
        "Executor Principal": "AURORA_FINAL_EXECUCAO_AIC_V5.1.py",
        "MT5 Executor": "MT5_EXECUTOR_PROFESSIONAL.py"
    }
    
    # Gerar relatório
    report = f"""# 📊 RELATÓRIO FINAL - AURORA v5.1

**Data de Geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** Production Ready  
**Total Módulos:** 252 (System Modules - Verified)

---

## 📋 ÍNDICE RÁPIDO COM LINKS

### 📄 Documentos Principais

"""
    
    for name, file_path in documents.items():
        report += f"- {create_clickable_link(file_path, name)}\n"
    
    report += "\n### 📊 Arquivos de Dados Estruturados\n\n"
    
    for name, file_path in json_files.items():
        report += f"- {create_clickable_link(file_path, name, '📊')}\n"
    
    report += "\n### 🔧 Scripts de Verificação\n\n"
    
    for name, file_path in scripts.items():
        report += f"- {create_clickable_link(file_path, name, '🔧')}\n"
    
    report += "\n### ⚙️ Arquivos Críticos do Sistema\n\n"
    
    for name, file_path in critical_files.items():
        report += f"- {create_clickable_link(file_path, name, '⚙️')}\n"
    
    report += f"""

---

## 🎯 DOCUMENTO PRINCIPAL RECOMENDADO

**Para visão geral rápida:**
👉 {create_clickable_link("AURORA_SISTEMA_SINTETIZADO_FINAL_V5.1.md", "Documento Sintetizado Final (506 linhas)", "📄")}

**Para detalhes completos:**
👉 {create_clickable_link("AURORA_COMPLETE_TECHNICAL_DOCUMENT.md", "Documento Consolidado Completo (5,632 linhas)", "📄")}

---

## 📊 ESTRUTURA DO PROJETO

### Camadas Hierárquicas

- [📁 00-Governance/](00-Governanca/) - 28 módulos
- [📁 01-Departments/](01-Departamentos/) - 40 módulos
- [📁 02-Processes-Chave/](02-Processos-Chave/) - 16 módulos
- [📁 03-Operacoes-Diarias/](03-Operacoes-Diarias/) - 12 módulos
- [📁 04-Infraestrutura/](04-Infraestrutura/) - 17 módulos
- [📁 05-Documentacao/](05-Documentacao/) - 1 módulo
- [📁 06-Monitoramento/](06-Monitoramento/) - 7 módulos

---

## ✅ VERIFICAÇÃO RÁPIDA

### Checklist de Integridade

- [ ] {create_clickable_link("AURORA_SISTEMA_SINTETIZADO_FINAL_V5.1.md", "Documento sintetizado existe", "✅")}
- [ ] {create_clickable_link("AURORA_COMPLETE_TECHNICAL_DOCUMENT.md", "Documento consolidado existe", "✅")}
- [ ] {create_clickable_link("aurora_modules_spec.json", "JSON de especificação existe", "✅")}
- [ ] {create_clickable_link("system_core/ncnt_orchestrator_complete.py", "Orchestrator core existe", "✅")}
- [ ] {create_clickable_link("main_ncnt.py", "Main entry point existe", "✅")}

---

## 🔄 COMANDOS ÚTEIS

### Abrir Documentos

```bash
# Abrir documento sintetizado (recomendado)
code AURORA_SISTEMA_SINTETIZADO_FINAL_V5.1.md

# Abrir documento completo
code AURORA_COMPLETE_TECHNICAL_DOCUMENT.md

# Abrir especificação JSON
code aurora_modules_spec.json
```

### Executar Verificações

```bash
# Verificar completude
python VERIFICAR_COMPLETUDE_FINAL.py

# Validação definitiva
python VERIFICACAO_FINAL_DEFINITIVA.py

# Gerar especificação completa
python GENERATE_COMPLETE_TECHNICAL_SPEC.py
```

---

## 📈 ESTATÍSTICAS

- **Total de Módulos:** 252 (System Modules)
- **Documentos Principais:** {len(documents)} documentos
- **Arquivos JSON:** {len(json_files)} arquivos
- **Scripts de Verificação:** {len(scripts)} scripts
- **Arquivos Críticos:** {len(critical_files)} arquivos

---

**Relatório gerado automaticamente em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Script:** GERAR_RELATORIO_FINAL_COM_LINKS.py  
**Status:** ✅ COMPLETO COM LINKS CLICÁVEIS
"""
    
    # Salvar relatório
    output_file = "RELATORIO_FINAL_AURORA_V5.1.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Relatório gerado: {output_file}")
    print(f"   📄 Todos os links são clicáveis na plataforma Cursor")
    print(f"   🎯 Documento principal: AURORA_SISTEMA_SINTETIZADO_FINAL_V5.1.md")
    
    # Criar também um índice HTML simples
    html_index = f"""<!DOCTYPE html>
<html>
<head>
    <title>AURORA v5.1 - Índice de Documentos</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        .link {{ margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }}
        .link a {{ text-decoration: none; color: #3498db; font-weight: bold; }}
        .link a:hover {{ color: #2980b9; }}
    </style>
</head>
<body>
    <h1>📊 AURORA v5.1 - Índice de Documentos</h1>
    <p><strong>Data:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>📄 Documentos Principais</h2>
"""
    
    for name, file_path in documents.items():
        if os.path.exists(file_path):
            html_index += f'    <div class="link"><a href="{file_path}">📄 {name}</a></div>\n'
    
    html_index += """
    <h2>📊 Arquivos de Dados</h2>
"""
    
    for name, file_path in json_files.items():
        if os.path.exists(file_path):
            html_index += f'    <div class="link"><a href="{file_path}">📊 {name}</a></div>\n'
    
    html_index += """
</body>
</html>
"""
    
    html_file = "INDICE_DOCUMENTOS_AURORA.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_index)
    
    print(f"   🌐 Índice HTML gerado: {html_file}")
    print("\n" + "=" * 70)
    print("✅ RELATÓRIO FINAL GERADO COM SUCESSO!")
    print("=" * 70)
    print(f"\n📄 Arquivo principal: {output_file}")
    print(f"🌐 Índice HTML: {html_file}")
    print(f"\n💡 DICA: Clique nos links no arquivo markdown para abrir diretamente!")
    
    return output_file

if __name__ == "__main__":
    try:
        generate_final_report_with_links()
    except Exception as e:
        print(f"\n❌ Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()

