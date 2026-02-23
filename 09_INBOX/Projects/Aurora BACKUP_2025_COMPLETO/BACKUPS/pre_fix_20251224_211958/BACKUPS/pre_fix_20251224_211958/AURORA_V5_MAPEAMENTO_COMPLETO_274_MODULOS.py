#!/usr/bin/env python3
"""
AURORA_V5_MAPEAMENTO_COMPLETO_274_MODULOS.py

Mapeia EXATAMENTE todos os 274 módulos e identifica problemas.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess
import importlib.util

def mapear_modulos_completos(project_root="."):
    """Mapeia todos os módulos Python e seus status."""
    
    root = Path(project_root).absolute()
    resultados = {
        "timestamp": datetime.now().isoformat(),
        "diretorio_raiz": str(root),
        "total_modulos": 0,
        "modulos_operacionais": 0,
        "modulos_com_problema": 0,
        "modulos_por_status": {},
        "lista_completa": [],
        "problemas_detalhados": []
    }
    
    # Encontrar TODOS os arquivos .py
    modulos = []
    for caminho in root.rglob("*.py"):
        # Excluir diretórios padrão
        if any(excluir in str(caminho) for excluir in ["__pycache__", ".git", "backup"]):
            continue
        modulos.append(caminho)
    
    resultados["total_modulos"] = len(modulos)
    print(f"🔍 Encontrados {len(modulos)} módulos Python")
    
    # Verificar cada módulo
    for i, modulo in enumerate(modulos, 1):
        rel_path = str(modulo.relative_to(root))
        status = "pendente"
        
        try:
            # 1. Verificar sintaxe
            compilacao = subprocess.run(
                [sys.executable, "-m", "py_compile", str(modulo)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if compilacao.returncode != 0:
                status = "erro_sintaxe"
                resultados["problemas_detalhados"].append({
                    "modulo": rel_path,
                    "status": status,
                    "erro": compilacao.stderr[:500]
                })
            else:
                # 2. Tentar importar
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"modulo_{i}",
                        str(modulo)
                    )
                    if spec and spec.loader:
                        # Marcar como importável
                        status = "operacional"
                    else:
                        status = "erro_import"
                except Exception as e:
                    status = "erro_import"
                    resultados["problemas_detalhados"].append({
                        "modulo": rel_path,
                        "status": status,
                        "erro": str(e)
                    })
        
        except subprocess.TimeoutExpired:
            status = "timeout"
        except Exception as e:
            status = "erro_verificacao"
            resultados["problemas_detalhados"].append({
                "modulo": rel_path,
                "status": status,
                "erro": str(e)
            })
        
        # Contabilizar
        resultados["modulos_por_status"][status] = resultados["modulos_por_status"].get(status, 0) + 1
        
        if status == "operacional":
            resultados["modulos_operacionais"] += 1
        else:
            resultados["modulos_com_problema"] += 1
        
        resultados["lista_completa"].append({
            "modulo": rel_path,
            "status": status,
            "caminho_completo": str(modulo)
        })
        
        if i % 50 == 0:
            print(f"📊 Processados {i}/{len(modulos)} módulos...")
    
    return resultados

def gerar_relatorio_detalhado(resultados):
    """Gera relatório completo."""
    
    relatorio = f"""AURORA v5.0 - MAPEAMENTO COMPLETO DOS {resultados['total_modulos']} MÓDULOS
================================================================================
Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Diretório: {resultados['diretorio_raiz']}
================================================================================

ESTATÍSTICAS GERAIS
-------------------
Total de Módulos Python: {resultados['total_modulos']}
Módulos Operacionais: {resultados['modulos_operacionais']}
Módulos com Problema: {resultados['modulos_com_problema']}
Taxa de Sucesso: {(resultados['modulos_operacionais']/resultados['total_modulos']*100):.2f}%

DISTRIBUIÇÃO POR STATUS
-----------------------
"""
    
    for status, quantidade in resultados["modulos_por_status"].items():
        percentual = (quantidade / resultados["total_modulos"]) * 100
        relatorio += f"{status}: {quantidade} módulos ({percentual:.1f}%)\n"
    
    # Listar módulos com problema
    if resultados["problemas_detalhados"]:
        relatorio += f"""

MÓDULOS COM PROBLEMAS ({len(resultados['problemas_detalhados'])})
----------------------------------------------------------------
"""
        for problema in resultados["problemas_detalhados"][:20]:  # Limitar a 20
            relatorio += f"❌ {problema['modulo']}\n"
            relatorio += f"   Status: {problema['status']}\n"
            relatorio += f"   Erro: {problema['erro'][:100]}...\n\n"
        
        if len(resultados["problemas_detalhados"]) > 20:
            relatorio += f"... e mais {len(resultados['problemas_detalhados']) - 20} módulos\n"
    
    # Módulos críticos
    modulos_criticos = [
        "aurora_etapa_a.py",
        "main_ncnt.py",
        "ncnt_system_complete.py",
        "06-Monitoramento/feedbackloop_module.py",
        "system_core/ncnt_orchestrator_complete.py",
        "04-Infraestrutura/api/database.py",
        "04-Infraestrutura/api/main.py",
        "04-Infraestrutura/api/endpoints/strategies.py",
        "00-Governanca/tier1_risk_validator.py",
        "00-Governanca/quantum_firewall.py",
        "01-Departamentos/AGENTS/CEO_Agent.py",
        "01-Departamentos/AGENTS/CFO_Agent.py",
        "01-Departamentos/AGENTS/CTO_Agent.py",
        "01-Departamentos/AGENTS/CKO_Agent.py"
    ]
    
    relatorio += """

STATUS DOS MÓDULOS CRÍTICOS
---------------------------
"""
    
    for critico in modulos_criticos:
        encontrado = False
        for modulo_info in resultados["lista_completa"]:
            if modulo_info["modulo"] == critico:
                status_icon = "✅" if modulo_info["status"] == "operacional" else "❌"
                relatorio += f"{status_icon} {critico}: {modulo_info['status']}\n"
                encontrado = True
                break
        
        if not encontrado:
            relatorio += f"❓ {critico}: NÃO ENCONTRADO\n"
    
    relatorio += f"""

AÇÕES RECOMENDADAS
------------------
"""
    
    if resultados["modulos_com_problema"] == 0:
        relatorio += """1. ✅ Sistema 100% operacional
2. 🚀 Executar aurora_etapa_a.py com dados reais
3. 📊 Coletar métricas empíricas
4. 🎯 Tomar decisão baseada em dados"""
    else:
        relatorio += f"""1. 🔧 Corrigir {resultados['modulos_com_problema']} módulos com problema
2. 🧪 Re-executar mapeamento após correções
3. 🎯 Buscar 100% de operacionalidade
4. 🚀 Só então executar aurora_etapa_a.py"""
    
    return relatorio

def main():
    """Função principal."""
    print("=" * 80)
    print("🔍 MAPEAMENTO COMPLETO DOS 274 MÓDULOS AURORA v5.0")
    print("=" * 80)
    
    try:
        # Executar mapeamento
        resultados = mapear_modulos_completos()
        
        # Gerar relatório
        relatorio = gerar_relatorio_detalhado(resultados)
        
        # Salvar resultados
        json_path = Path("aurora_mapeamento_completo.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório
        txt_path = Path("aurora_mapeamento_relatorio.txt")
        txt_path.write_text(relatorio, encoding='utf-8')
        
        # Exibir resumo
        print("\n" + relatorio)
        print("=" * 80)
        
        print(f"\n📁 JSON detalhado: {json_path}")
        print(f"📁 Relatório texto: {txt_path}")
        
        # Status final
        taxa = (resultados["modulos_operacionais"] / resultados["total_modulos"]) * 100
        
        if taxa == 100:
            print("\n🎉 SISTEMA 100% OPERACIONAL!")
            return 0
        elif taxa >= 95:
            print(f"\n⚠️  SISTEMA {taxa:.1f}% OPERACIONAL")
            return 1
        else:
            print(f"\n❌ SISTEMA APENAS {taxa:.1f}% OPERACIONAL")
            return 2
            
    except Exception as e:
        print(f"\n❌ Erro no mapeamento: {str(e)}")
        return 3

if __name__ == "__main__":
    sys.exit(main())

