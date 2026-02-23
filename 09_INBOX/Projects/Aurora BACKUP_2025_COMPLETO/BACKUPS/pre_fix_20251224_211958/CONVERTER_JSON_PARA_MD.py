#!/usr/bin/env python3
"""
Converte aurora_modules_spec.json para formato Markdown legível
"""

import json
from pathlib import Path

def categorize_module(path: str) -> str:
    """Categoriza módulo por caminho."""
    if path.startswith("00-Governanca") or "00-Governanca" in path:
        return "Governance"
    elif path.startswith("01-Departamentos") or "01-Departamentos" in path:
        return "Departments"
    elif path.startswith("02-Processos-Chave") or "02-Processos-Chave" in path:
        return "Processes"
    elif path.startswith("03-Operacoes-Diarias") or "03-Operacoes-Diarias" in path:
        return "Operations"
    elif path.startswith("04-Infraestrutura") or "04-Infraestrutura" in path:
        return "Infrastructure"
    elif path.startswith("05-Documentacao") or "05-Documentacao" in path:
        return "Documentation"
    elif path.startswith("06-Monitoramento") or "06-Monitoramento" in path:
        return "Monitoring"
    elif path.startswith("system_core") or "system_core" in path:
        return "Core"
    elif path.startswith("modules") or "modules" in path:
        return "Modules"
    else:
        return "Root"

def format_module_spec(spec: dict) -> str:
    """Formata especificação de um módulo."""
    path = spec['path']
    doc = f"\n#### {path}\n\n"
    
    if "error" in spec:
        doc += f"**ERRO:** {spec['error']}\n\n"
        return doc
    
    doc += f"**Tamanho:** {spec['size_bytes']:,} bytes | **Linhas:** {spec['lines']}\n\n"
    
    if spec.get("classes"):
        doc += "**Classes:**\n"
        for cls in spec["classes"]:
            doc += f"- `{cls['name']}`"
            if cls.get("bases"):
                bases = ", ".join(cls["bases"])
                doc += f" extends {bases}"
            doc += f" ({len(cls['methods'])} métodos)\n"
        doc += "\n"
    
    if spec.get("functions"):
        doc += "**Funções:**\n"
        for func in spec["functions"][:15]:  # Limitar a 15
            async_marker = "async " if func.get("is_async") else ""
            params = ", ".join(func["params"][:5])
            if len(func["params"]) > 5:
                params += "..."
            doc += f"- `{async_marker}{func['name']}({params})`\n"
        if len(spec["functions"]) > 15:
            doc += f"- ... e mais {len(spec['functions']) - 15} funções\n"
        doc += "\n"
    
    if spec.get("imports"):
        doc += "**Imports principais:**\n"
        for imp in spec["imports"][:10]:  # Limitar a 10
            doc += f"- `{imp}`\n"
        if len(spec["imports"]) > 10:
            doc += f"- ... e mais {len(spec['imports']) - 10} imports\n"
        doc += "\n"
    
    return doc

def main():
    """Função principal."""
    print("Convertendo JSON para Markdown legível...")
    
    # Carregar JSON
    with open('aurora_modules_spec.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Criar documento
    output = []
    output.append("# AURORA v5.1 - Modules Specification (Legível)")
    output.append("**Document ID:** MOD-SPEC-AURORA-5.1-20251221")
    output.append("**Formato:** Markdown Legível")
    output.append("**Origem:** aurora_modules_spec.json")
    output.append("**Data:** 2025-12-21")
    output.append("")
    output.append("---")
    output.append("")
    output.append("## METADADOS DO SISTEMA")
    output.append("")
    output.append("```")
    output.append(f"Total Módulos: {data['metadata']['total_modules']}")
    output.append(f"Categorias: {data['metadata']['categories']}")
    output.append(f"Gerado em: {data['metadata']['generated']}")
    output.append("```")
    output.append("")
    output.append("---")
    output.append("")
    output.append("## DISTRIBUIÇÃO POR CATEGORIA")
    output.append("")
    
    for cat, count in sorted(data['categorized'].items()):
        output.append(f"- **{cat}**: {count} módulos")
    
    output.append("")
    output.append("---")
    output.append("")
    
    # Agrupar por categoria
    categorized_modules = {}
    for spec in data['modules']:
        cat = categorize_module(spec['path'])
        if cat not in categorized_modules:
            categorized_modules[cat] = []
        categorized_modules[cat].append(spec)
    
    # Gerar seções por categoria
    for category in sorted(categorized_modules.keys()):
        modules = categorized_modules[category]
        output.append(f"## {category.upper()} ({len(modules)} módulos)")
        output.append("")
        
        # Lista resumida
        output.append("### Lista de Módulos")
        output.append("")
        output.append("```")
        for spec in sorted(modules, key=lambda x: x['path']):
            path = spec['path']
            if "error" not in spec:
                classes = len(spec.get("classes", []))
                functions = len(spec.get("functions", []))
                output.append(f"{path:80s} | C:{classes:2d} F:{functions:3d}")
            else:
                output.append(f"{path:80s} | ERROR")
        output.append("```")
        output.append("")
        
        # Detalhes dos módulos principais (top 20 por categoria)
        important = sorted(modules, key=lambda x: x.get('size_bytes', 0), reverse=True)[:20]
        if important:
            output.append("### Especificações Detalhadas (Top 20)")
            output.append("")
            for spec in important:
                output.append(format_module_spec(spec))
                output.append("---")
                output.append("")
    
    # Salvar
    output_file = "AURORA_MODULES_SPEC_LEGIVEL.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    
    print(f"✅ Arquivo gerado: {output_file}")
    print(f"   Total de módulos processados: {len(data['modules'])}")
    print(f"   Categorias: {len(categorized_modules)}")

if __name__ == "__main__":
    main()

