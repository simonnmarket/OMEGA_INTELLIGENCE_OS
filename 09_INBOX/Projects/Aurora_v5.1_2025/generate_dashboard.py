#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Dashboard HTML - AURORA v5.1
Gera dashboard HTML atualizado com dados do sistema de governança
"""

import sys
import os
import json
import webbrowser
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator
except ImportError:
    print("ERRO: financial_governance_orchestrator nao encontrado")
    sys.exit(1)


def generate_dashboard_html(output_file: str = "dashboard.html", auto_open: bool = True):
    """
    Gera dashboard HTML completo com dados do sistema de governança.
    
    Args:
        output_file: Arquivo HTML de saída
        auto_open: Se True, abre no navegador automaticamente
    """
    print("\n" + "=" * 80)
    print("GERANDO DASHBOARD HTML - AURORA v5.1")
    print("=" * 80)
    
    # Carregar orquestrador
    orchestrator = FinancialProjectOrchestrator("project_manifest.json")
    
    # Gerar dados
    print("\nColetando dados do sistema...")
    data = orchestrator.generate_dashboard_data()
    
    # Calcular estatísticas adicionais
    total_modules = data["metadata"]["total_modules"]
    kpis = data["kpis"]
    
    # Gerar HTML
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURORA v5.1 - Dashboard de Governança</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .kpis {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .kpi-card.backlog {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .kpi-card.active {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        
        .kpi-card.inactive {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        
        .kpi-card.completed {{
            background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        }}
        
        .kpi-card h3 {{
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
            opacity: 0.9;
        }}
        
        .kpi-card .value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .kpi-card .percentage {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .priorities {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        
        .priority-item {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        
        .priority-item.critico {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        
        .priority-item.emergencia {{
            border-left-color: #fd7e14;
            background: #fff8f0;
        }}
        
        .priority-item.ativo {{
            border-left-color: #28a745;
            background: #f0fff4;
        }}
        
        .modules-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .modules-table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .modules-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        .modules-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-backlog {{
            background: #ffeaa7;
            color: #d63031;
        }}
        
        .status-active {{
            background: #74b9ff;
            color: #0984e3;
        }}
        
        .status-inactive {{
            background: #fd79a8;
            color: #e84393;
        }}
        
        .status-completed {{
            background: #55efc4;
            color: #00b894;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }}
        
        .blindagem {{
            display: flex;
            gap: 5px;
        }}
        
        .blindagem-item {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
        }}
        
        .blindagem-item.true {{
            background: #28a745;
        }}
        
        .blindagem-item.false {{
            background: #dc3545;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
            font-size: 0.9em;
        }}
        
        .refresh-info {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.5;
            }}
        }}
        
        .auto-refresh {{
            animation: pulse 2s infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ AURORA v5.1 - Dashboard de Governança</h1>
            <div class="subtitle">Sistema de Governança Institucional - Monitoramento em Tempo Real</div>
        </div>
        
        <div class="kpis">
            <div class="kpi-card backlog">
                <h3>Backlog</h3>
                <div class="value">{kpis.get('backlog', 0)}</div>
                <div class="percentage">{round(kpis.get('backlog', 0) / total_modules * 100, 1) if total_modules > 0 else 0}%</div>
            </div>
            <div class="kpi-card active">
                <h3>Active</h3>
                <div class="value">{kpis.get('active', 0)}</div>
                <div class="percentage">{round(kpis.get('active', 0) / total_modules * 100, 1) if total_modules > 0 else 0}%</div>
            </div>
            <div class="kpi-card inactive">
                <h3>Inactive</h3>
                <div class="value">{kpis.get('inactive', 0)}</div>
                <div class="percentage">{round(kpis.get('inactive', 0) / total_modules * 100, 1) if total_modules > 0 else 0}%</div>
            </div>
            <div class="kpi-card completed">
                <h3>Completed</h3>
                <div class="value">{kpis.get('completed', 0)}</div>
                <div class="percentage">{round(kpis.get('completed', 0) / total_modules * 100, 1) if total_modules > 0 else 0}%</div>
            </div>
        </div>
        
        <div class="priorities">
            <h2 class="section-title">🎯 Prioridades Críticas</h2>
            {generate_priorities_html(data.get('priorities', []))}
        </div>
        
        <div class="modules">
            <h2 class="section-title">📦 Módulos do Sistema (Top 20)</h2>
            {generate_modules_table_html(data.get('modules', []))}
        </div>
        
        <div class="footer">
            <p><strong>Total de Módulos:</strong> {total_modules} | <strong>Última Atualização:</strong> {data['metadata'].get('last_updated', 'N/A')[:19]}</p>
            <p><strong>Versão:</strong> {data['metadata'].get('version', 'N/A')} | <strong>Última Sincronização:</strong> {data['metadata'].get('last_sync', 'N/A')[:19]}</p>
        </div>
        
        <div class="refresh-info">
            <p>🔄 Dashboard atualizado automaticamente a cada 30 segundos</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh a cada 30 segundos
        setInterval(function() {{
            location.reload();
        }}, 30000);
        
        // Dados para JavaScript (se necessário)
        const dashboardData = {json.dumps(data, ensure_ascii=False, indent=2)};
    </script>
</body>
</html>"""
    
    # Salvar arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Dashboard gerado: {output_file}")
    print(f"   Total de módulos: {total_modules}")
    print(f"   KPIs: Backlog={kpis.get('backlog', 0)}, Active={kpis.get('active', 0)}, Inactive={kpis.get('inactive', 0)}, Completed={kpis.get('completed', 0)}")
    
    # Abrir no navegador
    if auto_open:
        file_path = os.path.abspath(output_file)
        file_url = f"file:///{file_path.replace(os.sep, '/')}"
        webbrowser.open(file_url)
        print(f"   🌐 Dashboard aberto no navegador")
    
    return output_file


def generate_priorities_html(priorities: list) -> str:
    """Gera HTML para lista de prioridades."""
    if not priorities:
        return "<p style='color: #666; padding: 20px;'>Nenhuma prioridade crítica definida.</p>"
    
    html = ""
    for priority in priorities:
        priority_class = priority.get("priority", "EVOLUÇÃO").lower()
        if "crítico" in priority_class or "critico" in priority_class:
            priority_class = "critico"
        elif "emergência" in priority_class or "emergencia" in priority_class:
            priority_class = "emergencia"
        elif "ativo" in priority_class:
            priority_class = "ativo"
        else:
            priority_class = ""
        
        blindagem = priority.get("blindagem", {})
        blindagem_html = f"""
            <div class="blindagem">
                <span class="blindagem-item {'true' if blindagem.get('T') else 'false'}" title="Testes"></span>
                <span class="blindagem-item {'true' if blindagem.get('H') else 'false'}" title="Homologação"></span>
                <span class="blindagem-item {'true' if blindagem.get('I') else 'false'}" title="Integração"></span>
            </div>
        """
        
        html += f"""
            <div class="priority-item {priority_class}">
                <strong>{priority.get('id', 'N/A')}</strong> - {priority.get('name', 'N/A')}
                <br>
                <span style="color: #666; font-size: 0.9em;">Prioridade: {priority.get('priority', 'EVOLUÇÃO')}</span>
                {blindagem_html}
            </div>
        """
    
    return html


def generate_modules_table_html(modules: list) -> str:
    """Gera HTML para tabela de módulos."""
    if not modules:
        return "<p style='color: #666; padding: 20px;'>Nenhum módulo encontrado.</p>"
    
    html = """
    <table class="modules-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Status</th>
                <th>Prioridade</th>
                <th>Progresso</th>
                <th>Blindagem</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for module in modules:
        mod_id = module.get("id", "N/A")
        name = module.get("name", "N/A")
        status = module.get("status", "BACKLOG")
        priority = module.get("priority", "EVOLUÇÃO")
        progress = module.get("progress", 0)
        blindagem = module.get("blindagem", {})
        
        status_class = status.lower()
        status_badge = f'<span class="status-badge status-{status_class}">{status}</span>'
        
        progress_html = f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <span style="font-size: 0.85em; color: #666;">{progress}%</span>
        """
        
        blindagem_html = f"""
            <div class="blindagem">
                <span class="blindagem-item {'true' if blindagem.get('T') else 'false'}" title="Testes"></span>
                <span class="blindagem-item {'true' if blindagem.get('H') else 'false'}" title="Homologação"></span>
                <span class="blindagem-item {'true' if blindagem.get('I') else 'false'}" title="Integração"></span>
            </div>
        """
        
        html += f"""
            <tr>
                <td><strong>{mod_id}</strong></td>
                <td>{name[:50]}{'...' if len(name) > 50 else ''}</td>
                <td>{status_badge}</td>
                <td>{priority}</td>
                <td>{progress_html}</td>
                <td>{blindagem_html}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    
    return html


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerar dashboard HTML')
    parser.add_argument('--output', '-o', default='dashboard.html', help='Arquivo de saída')
    parser.add_argument('--no-open', action='store_true', help='Não abrir no navegador')
    
    args = parser.parse_args()
    
    try:
        output_file = generate_dashboard_html(
            output_file=args.output,
            auto_open=not args.no_open
        )
        print(f"\n✅ Dashboard gerado com sucesso: {output_file}")
        
    except Exception as e:
        print(f"\n❌ ERRO ao gerar dashboard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

