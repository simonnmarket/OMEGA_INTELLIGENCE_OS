#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar template de plano de ação e atualizar sistema de governança.
Este script lê o template preenchido e executa as ações de forma segura e controlada.
"""

import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-Governanca'))

try:
    from financial_governance_orchestrator import FinancialProjectOrchestrator
except ImportError:
    print("ERRO: financial_governance_orchestrator nao encontrado")
    sys.exit(1)

try:
    from PROTOCOLO_FONTE_VERDADE import FonteVerdadeAurora, protocolo_obrigatorio_antes_de_qualquer_acao
except ImportError:
    print("ERRO: PROTOCOLO_FONTE_VERDADE.py nao encontrado")
    sys.exit(1)


class ProcessadorTemplatePlanoAcao:
    """
    Processa template de plano de ação e executa atualizações no sistema de governança.
    """
    
    def __init__(self, template_file: str):
        """
        Inicializa processador com arquivo de template.
        
        Args:
            template_file: Caminho do arquivo template preenchido
        """
        self.template_file = template_file
        self.orchestrator = FinancialProjectOrchestrator("project_manifest.json")
        self.fonte = FonteVerdadeAurora()
        self.modulos_afetados = []
        self.acoes_registradas = []
        self.erros = []
        
    def validar_pre_execucao(self) -> bool:
        """
        Valida sistema antes de processar template.
        
        Returns:
            True se validação passou, False caso contrário
        """
        print("\n" + "=" * 80)
        print("VALIDACAO PRE-EXECUCAO")
        print("=" * 80)
        
        # Executar protocolo obrigatório
        if not protocolo_obrigatorio_antes_de_qualquer_acao():
            print("\nERRO: Validacao pre-execucao falhou. Abortando.")
            return False
        
        print("\n✅ Validacao pre-execucao passou com sucesso")
        return True
    
    def ler_template(self) -> Dict:
        """
        Lê e parseia o template preenchido.
        
        Returns:
            Dicionário com dados extraídos do template
        """
        if not os.path.exists(self.template_file):
            raise FileNotFoundError(f"Template nao encontrado: {self.template_file}")
        
        print(f"\nLendo template: {self.template_file}")
        
        with open(self.template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair informações do template
        dados = {
            "objetivo": self._extrair_secao(content, "OBJETIVO DO PLANO"),
            "modulos_afetados": self._extrair_modulos_afetados(content),
            "acoes_planejadas": self._extrair_acoes_planejadas(content),
            "checklist": self._extrair_checklist(content),
            "compliance": self._extrair_compliance(content),
        }
        
        return dados
    
    def _extrair_secao(self, content: str, titulo: str) -> str:
        """Extrai conteúdo de uma seção do template."""
        pattern = f"## {titulo}.*?```(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extrair_modulos_afetados(self, content: str) -> List[Dict]:
        """Extrai lista de módulos afetados do template."""
        modulos = []
        
        # Procurar tabela de módulos
        pattern = r"\| MOD-(\d+)\s*\| ([^\|]+)\s*\| ([^\|]+)\s*\| ([^\|]+)\s*\| ([^\|]+)\s*\|"
        matches = re.findall(pattern, content)
        
        for match in matches:
            mod_id = f"MOD-{match[0]}"
            modulos.append({
                "id": mod_id,
                "nome": match[1].strip(),
                "status_atual": match[2].strip(),
                "acao_planejada": match[3].strip(),
                "prioridade": match[4].strip()
            })
        
        # Se não encontrou tabela, procurar lista
        if not modulos:
            pattern = r"- MOD-(\d+):\s*(.+)"
            matches = re.findall(pattern, content)
            for match in matches:
                mod_id = f"MOD-{match[0]}"
                modulos.append({
                    "id": mod_id,
                    "acao_planejada": match[1].strip()
                })
        
        return modulos
    
    def _extrair_acoes_planejadas(self, content: str) -> List[Dict]:
        """Extrai ações planejadas do template."""
        acoes = []
        
        # Procurar código Python de log_event
        pattern = r'orchestrator\.log_event\(\s*mod_id="(MOD-\d+)"[^)]+action_desc="([^"]+)"[^)]+status_type="(\w+)"'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            acoes.append({
                "mod_id": match[0],
                "action_desc": match[1],
                "status_type": match[2]
            })
        
        return acoes
    
    def _extrair_checklist(self, content: str) -> Dict:
        """Extrai status do checklist do template."""
        checklist = {
            "validacao_previa": [],
            "execucao": [],
            "testes": [],
            "validacao_final": []
        }
        
        # Procurar checkboxes marcados
        pattern = r"- \[([ x])\] (.+)"
        matches = re.findall(pattern, content)
        
        for checked, item in matches:
            if checked == 'x':
                # Categorizar item
                if "validacao" in item.lower() or "protocolo" in item.lower():
                    checklist["validacao_previa"].append(item)
                elif "teste" in item.lower():
                    checklist["testes"].append(item)
                elif "registro" in item.lower() or "execucao" in item.lower():
                    checklist["execucao"].append(item)
                elif "validacao final" in item.lower() or "pos-execucao" in item.lower():
                    checklist["validacao_final"].append(item)
        
        return checklist
    
    def _extrair_compliance(self, content: str) -> List[Dict]:
        """Extrai tags de compliance do template."""
        compliance = []
        
        pattern = r'orchestrator\.add_compliance_tag\("(MOD-\d+)",\s*"([^"]+)",\s*"([^"]*)"\)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            compliance.append({
                "mod_id": match[0],
                "framework": match[1],
                "version": match[2]
            })
        
        return compliance
    
    def validar_transicoes(self, modulos: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Valida transições FSM para todos os módulos.
        
        Returns:
            (todas_validas, lista_erros)
        """
        print("\nValidando transicoes FSM...")
        erros = []
        
        for mod in modulos:
            mod_id = mod.get("id")
            status_atual = mod.get("status_atual", "")
            status_type = mod.get("status_type", "active")
            
            if not mod_id:
                continue
            
            # Verificar se módulo existe
            if mod_id not in self.orchestrator.state["modules"]:
                erros.append(f"Módulo {mod_id} não encontrado no sistema")
                continue
            
            # Validar transição
            module = self.orchestrator.state["modules"][mod_id]
            current_status = module.get("status", "BACKLOG")
            
            status_mapping = {
                "completed": "COMPLETED",
                "active": "ACTIVE",
                "confirmed": "ACTIVE",
                "inactive": "INACTIVE",
            }
            requested_status = status_mapping.get(status_type.lower(), current_status)
            
            if not self.orchestrator._can_transition(current_status, requested_status):
                erros.append(
                    f"Transição não autorizada para {mod_id}: "
                    f"{current_status} → {requested_status}"
                )
        
        todas_validas = len(erros) == 0
        
        if todas_validas:
            print("✅ Todas as transições são válidas")
        else:
            print(f"❌ {len(erros)} transições inválidas encontradas")
            for erro in erros:
                print(f"   - {erro}")
        
        return todas_validas, erros
    
    def executar_acoes(self, dados: Dict, dry_run: bool = False) -> Dict:
        """
        Executa ações do template no sistema de governança.
        
        Args:
            dados: Dados extraídos do template
            dry_run: Se True, apenas simula sem executar
        
        Returns:
            Relatório de execução
        """
        print("\n" + "=" * 80)
        print("EXECUTANDO ACOES DO TEMPLATE")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 DRY RUN: Nenhuma alteração será feita")
        
        relatorio = {
            "modulos_processados": 0,
            "acoes_executadas": 0,
            "compliance_tags_adicionadas": 0,
            "erros": []
        }
        
        # Processar módulos afetados
        modulos = dados.get("modulos_afetados", [])
        
        for mod in modulos:
            mod_id = mod.get("id")
            if not mod_id:
                continue
            
            print(f"\nProcessando {mod_id}...")
            
            # Registrar ação se especificada
            acao = mod.get("acao_planejada", "")
            if acao and not dry_run:
                try:
                    resultado = self.orchestrator.log_event(
                        mod_id=mod_id,
                        action_desc=acao,
                        status_type="active",
                        actor="Template_Processor"
                    )
                    relatorio["acoes_executadas"] += 1
                    print(f"   ✅ Ação registrada: {acao[:50]}")
                except Exception as e:
                    erro = f"Erro ao registrar ação para {mod_id}: {e}"
                    relatorio["erros"].append(erro)
                    print(f"   ❌ {erro}")
            
            relatorio["modulos_processados"] += 1
        
        # Adicionar tags de compliance
        compliance = dados.get("compliance", [])
        for tag in compliance:
            mod_id = tag.get("mod_id")
            framework = tag.get("framework")
            version = tag.get("version", "")
            
            if not dry_run:
                try:
                    resultado = self.orchestrator.add_compliance_tag(
                        mod_id, framework, version
                    )
                    relatorio["compliance_tags_adicionadas"] += 1
                    print(f"   ✅ Tag de compliance adicionada: {framework}")
                except Exception as e:
                    erro = f"Erro ao adicionar tag para {mod_id}: {e}"
                    relatorio["erros"].append(erro)
                    print(f"   ❌ {erro}")
        
        return relatorio
    
    def gerar_relatorio(self, dados: Dict, relatorio_execucao: Dict) -> str:
        """
        Gera relatório final da execução.
        
        Returns:
            Caminho do arquivo de relatório gerado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_file = f"RELATORIO_EXECUCAO_TEMPLATE_{timestamp}.json"
        
        relatorio_completo = {
            "template_file": self.template_file,
            "data_execucao": datetime.now().isoformat(),
            "dados_template": dados,
            "relatorio_execucao": relatorio_execucao,
            "status_sistema": self.orchestrator.generate_report(detailed=False)
        }
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio_completo, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Relatório salvo em: {relatorio_file}")
        return relatorio_file


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Processar template de plano de ação')
    parser.add_argument('template_file', help='Arquivo template preenchido')
    parser.add_argument('--dry-run', action='store_true', help='Apenas simular sem executar')
    
    args = parser.parse_args()
    
    try:
        processador = ProcessadorTemplatePlanoAcao(args.template_file)
        
        # Validar pré-execução
        if not processador.validar_pre_execucao():
            print("\n❌ Validação pré-execução falhou. Abortando.")
            sys.exit(1)
        
        # Ler template
        print("\nLendo template...")
        dados = processador.ler_template()
        
        print(f"\n📊 Dados extraídos:")
        print(f"   Módulos afetados: {len(dados.get('modulos_afetados', []))}")
        print(f"   Ações planejadas: {len(dados.get('acoes_planejadas', []))}")
        print(f"   Tags de compliance: {len(dados.get('compliance', []))}")
        
        # Validar transições
        modulos = dados.get("modulos_afetados", [])
        todas_validas, erros = processador.validar_transicoes(modulos)
        
        if not todas_validas:
            print("\n❌ Transições inválidas encontradas. Corrija o template antes de prosseguir.")
            sys.exit(1)
        
        # Executar ações
        relatorio = processador.executar_acoes(dados, dry_run=args.dry_run)
        
        # Gerar relatório
        relatorio_file = processador.gerar_relatorio(dados, relatorio)
        
        print("\n" + "=" * 80)
        if args.dry_run:
            print("DRY RUN CONCLUÍDO - Nenhuma alteração foi feita")
        else:
            print("EXECUÇÃO CONCLUÍDA")
        print("=" * 80)
        print(f"   Módulos processados: {relatorio['modulos_processados']}")
        print(f"   Ações executadas: {relatorio['acoes_executadas']}")
        print(f"   Tags de compliance: {relatorio['compliance_tags_adicionadas']}")
        print(f"   Erros: {len(relatorio['erros'])}")
        
        if relatorio['erros']:
            print("\n⚠️  Erros encontrados:")
            for erro in relatorio['erros']:
                print(f"   - {erro}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

