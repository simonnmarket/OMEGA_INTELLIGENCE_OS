#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Template YAML - Processa template de plano de ação em formato YAML
e executa atualizações no sistema de governança de forma segura e controlada.
"""

import sys
import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Adicionar path do módulo de governança
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


class ProcessadorTemplateYAML:
    """
    Processa template YAML de plano de ação e executa atualizações no sistema de governança.
    """
    
    def __init__(self, template_file: str):
        """
        Inicializa processador com arquivo YAML.
        
        Args:
            template_file: Caminho do arquivo template YAML
        """
        self.template_file = template_file
        self.orchestrator = FinancialProjectOrchestrator("project_manifest.json")
        self.fonte = FonteVerdadeAurora()
        self.dados_template = {}
        self.relatorio_execucao = {
            "modulos_processados": 0,
            "acoes_executadas": 0,
            "compliance_tags_adicionadas": 0,
            "erros": [],
            "avisos": []
        }
        
    def validar_pre_execucao(self) -> bool:
        """Valida sistema antes de processar template."""
        print("\n" + "=" * 80)
        print("VALIDACAO PRE-EXECUCAO")
        print("=" * 80)
        
        if not protocolo_obrigatorio_antes_de_qualquer_acao():
            print("\nERRO: Validacao pre-execucao falhou. Abortando.")
            return False
        
        print("\n✅ Validacao pre-execucao passou com sucesso")
        return True
    
    def carregar_template(self) -> Dict:
        """Carrega e valida template YAML."""
        if not os.path.exists(self.template_file):
            raise FileNotFoundError(f"Template nao encontrado: {self.template_file}")
        
        print(f"\nCarregando template: {self.template_file}")
        
        with open(self.template_file, 'r', encoding='utf-8') as f:
            self.dados_template = yaml.safe_load(f)
        
        if not self.dados_template:
            raise ValueError("Template vazio ou invalido")
        
        print("✅ Template carregado com sucesso")
        return self.dados_template
    
    def validar_template(self) -> Tuple[bool, List[str]]:
        """Valida estrutura e conteúdo do template."""
        print("\nValidando estrutura do template...")
        erros = []
        
        # Validar campos obrigatórios
        campos_obrigatorios = [
            "metadata",
            "objetivo",
            "modulos_afetados"
        ]
        
        for campo in campos_obrigatorios:
            if campo not in self.dados_template:
                erros.append(f"Campo obrigatorio ausente: {campo}")
        
        # Validar módulos
        modulos = self.dados_template.get("modulos_afetados", {}).get("lista", [])
        if not modulos:
            erros.append("Nenhum modulo afetado especificado")
        
        for mod in modulos:
            if "id" not in mod:
                erros.append("Modulo sem ID especificado")
            elif not mod["id"].startswith("MOD-"):
                erros.append(f"ID de modulo invalido: {mod.get('id')}")
        
        if erros:
            print(f"❌ {len(erros)} erros encontrados:")
            for erro in erros:
                print(f"   - {erro}")
            return False, erros
        
        print("✅ Template validado com sucesso")
        return True, []
    
    def validar_transicoes_fsm(self) -> Tuple[bool, List[str]]:
        """Valida transições FSM para todos os módulos."""
        print("\nValidando transicoes FSM...")
        erros = []
        
        modulos = self.dados_template.get("modulos_afetados", {}).get("lista", [])
        
        for mod in modulos:
            mod_id = mod.get("id")
            status_atual = mod.get("status_atual", "")
            acao = mod.get("acao_planejada", "")
            
            if not mod_id:
                continue
            
            # Verificar se módulo existe
            if mod_id not in self.orchestrator.state["modules"]:
                erros.append(f"Modulo {mod_id} nao encontrado no sistema")
                continue
            
            # Determinar status desejado baseado na ação
            # Se módulo está em BACKLOG e tem ação, deve ir para ACTIVE
            module = self.orchestrator.state["modules"][mod_id]
            current_status = module.get("status", "BACKLOG")
            
            # Status desejado geralmente é ACTIVE para início de trabalho
            requested_status = "ACTIVE"
            
            # Validar transição
            if not self.orchestrator._can_transition(current_status, requested_status):
                erros.append(
                    f"Transicao nao autorizada para {mod_id}: "
                    f"{current_status} → {requested_status}"
                )
        
        todas_validas = len(erros) == 0
        
        if todas_validas:
            print("✅ Todas as transicoes sao validas")
        else:
            print(f"❌ {len(erros)} transicoes invalidas encontradas")
            for erro in erros:
                print(f"   - {erro}")
        
        return todas_validas, erros
    
    def executar_registro_intencao(self, dry_run: bool = False) -> int:
        """Executa registro de intenção para todos os módulos."""
        print("\n" + "=" * 80)
        print("EXECUTANDO REGISTRO DE INTENCAO")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 DRY RUN: Nenhuma alteracao sera feita")
        
        registros = self.dados_template.get("registro_intencao", [])
        executados = 0
        
        for registro in registros:
            mod_id = registro.get("modulo_id")
            action_desc = registro.get("action_desc", "")
            status_type = registro.get("status_type", "active")
            actor = registro.get("actor", "Template_Processor")
            regulatory_context = registro.get("regulatory_context", [])
            
            if not mod_id or not action_desc:
                continue
            
            print(f"\nRegistrando intencao para {mod_id}...")
            print(f"   Acao: {action_desc[:60]}...")
            
            if dry_run:
                print("   [DRY RUN] Registro seria executado")
                executados += 1
                continue
            
            try:
                resultado = self.orchestrator.log_event(
                    mod_id=mod_id,
                    action_desc=action_desc,
                    status_type=status_type,
                    actor=actor,
                    regulatory_context=regulatory_context if regulatory_context else None
                )
                
                # Atualizar template com resultado
                registro["executado"] = True
                registro["data"] = datetime.now().strftime("%Y-%m-%d")
                registro["timestamp"] = datetime.now().isoformat()
                registro["resultado"] = "SUCESSO"
                
                executados += 1
                self.relatorio_execucao["acoes_executadas"] += 1
                print(f"   ✅ Registro executado com sucesso")
                
            except Exception as e:
                erro = f"Erro ao registrar intencao para {mod_id}: {e}"
                registro["resultado"] = "ERRO"
                registro["observacoes"] = str(e)
                self.relatorio_execucao["erros"].append(erro)
                print(f"   ❌ {erro}")
        
        return executados
    
    def executar_registro_conclusao(self, dry_run: bool = False) -> int:
        """Executa registro de conclusão para todos os módulos."""
        print("\n" + "=" * 80)
        print("EXECUTANDO REGISTRO DE CONCLUSAO")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 DRY RUN: Nenhuma alteracao sera feita")
        
        conclusoes = self.dados_template.get("registro_conclusao", [])
        executados = 0
        
        for conclusao in conclusoes:
            mod_id = conclusao.get("modulo_id")
            action_desc = conclusao.get("action_desc", "")
            status_type = conclusao.get("status_type", "completed")
            actor = conclusao.get("actor", "Template_Processor")
            metadata = conclusao.get("metadata", {})
            regulatory_context = conclusao.get("regulatory_context", [])
            
            if not mod_id or not action_desc:
                continue
            
            print(f"\nRegistrando conclusao para {mod_id}...")
            print(f"   Acao: {action_desc[:60]}...")
            
            if dry_run:
                print("   [DRY RUN] Registro seria executado")
                executados += 1
                continue
            
            try:
                resultado = self.orchestrator.log_event(
                    mod_id=mod_id,
                    action_desc=action_desc,
                    status_type=status_type,
                    actor=actor,
                    metadata=metadata if metadata else None,
                    regulatory_context=regulatory_context if regulatory_context else None
                )
                
                # Atualizar template com resultado
                conclusao["executado"] = True
                conclusao["data"] = datetime.now().strftime("%Y-%m-%d")
                conclusao["timestamp"] = datetime.now().isoformat()
                conclusao["resultado"] = "SUCESSO"
                
                executados += 1
                self.relatorio_execucao["acoes_executadas"] += 1
                print(f"   ✅ Registro executado com sucesso")
                
            except Exception as e:
                erro = f"Erro ao registrar conclusao para {mod_id}: {e}"
                conclusao["resultado"] = "ERRO"
                conclusao["observacoes"] = str(e)
                self.relatorio_execucao["erros"].append(erro)
                print(f"   ❌ {erro}")
        
        return executados
    
    def executar_compliance_tags(self, dry_run: bool = False) -> int:
        """Adiciona tags de compliance conforme especificado."""
        print("\n" + "=" * 80)
        print("ADICIONANDO TAGS DE COMPLIANCE")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 DRY RUN: Nenhuma alteracao sera feita")
        
        compliance = self.dados_template.get("compliance", [])
        adicionadas = 0
        
        for item in compliance:
            mod_id = item.get("modulo_id")
            tags = item.get("tags", [])
            
            if not mod_id or not tags:
                continue
            
            print(f"\nAdicionando tags de compliance para {mod_id}...")
            
            for tag in tags:
                framework = tag.get("framework", "")
                version = tag.get("version", "")
                
                if not framework:
                    continue
                
                print(f"   Tag: {framework} {version}")
                
                if dry_run:
                    print("   [DRY RUN] Tag seria adicionada")
                    continue
                
                try:
                    resultado = self.orchestrator.add_compliance_tag(
                        mod_id, framework, version
                    )
                    adicionadas += 1
                    self.relatorio_execucao["compliance_tags_adicionadas"] += 1
                    print(f"   ✅ Tag adicionada")
                    
                except Exception as e:
                    erro = f"Erro ao adicionar tag {framework} para {mod_id}: {e}"
                    self.relatorio_execucao["erros"].append(erro)
                    print(f"   ❌ {erro}")
            
            if not dry_run:
                item["adicionadas"] = True
                item["data"] = datetime.now().strftime("%Y-%m-%d")
        
        return adicionadas
    
    def salvar_template_atualizado(self, output_file: str = None):
        """Salva template atualizado com resultados da execução."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = Path(self.template_file).stem
            output_file = f"{base_name}_EXECUTADO_{timestamp}.yaml"
        
        print(f"\nSalvando template atualizado: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.dados_template, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False, indent=2)
        
        print(f"✅ Template salvo")
        return output_file
    
    def gerar_relatorio(self) -> str:
        """Gera relatório final da execução."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_file = f"RELATORIO_EXECUCAO_YAML_{timestamp}.json"
        
        relatorio_completo = {
            "template_file": self.template_file,
            "data_execucao": datetime.now().isoformat(),
            "relatorio_execucao": self.relatorio_execucao,
            "status_sistema": self.orchestrator.generate_report(detailed=False),
            "modulos_afetados": len(self.dados_template.get("modulos_afetados", {}).get("lista", []))
        }
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio_completo, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Relatorio salvo em: {relatorio_file}")
        return relatorio_file


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Processar template YAML de plano de ação')
    parser.add_argument('template_file', help='Arquivo template YAML')
    parser.add_argument('--dry-run', action='store_true', help='Apenas simular sem executar')
    parser.add_argument('--fase', choices=['intencao', 'conclusao', 'compliance', 'tudo'], 
                       default='tudo', help='Fase a executar')
    
    args = parser.parse_args()
    
    try:
        processador = ProcessadorTemplateYAML(args.template_file)
        
        # Validar pré-execução
        if not processador.validar_pre_execucao():
            print("\n❌ Validação pré-execução falhou. Abortando.")
            sys.exit(1)
        
        # Carregar template
        dados = processador.carregar_template()
        
        # Validar template
        valido, erros = processador.validar_template()
        if not valido:
            print("\n❌ Template inválido. Corrija os erros antes de prosseguir.")
            sys.exit(1)
        
        # Validar transições
        transicoes_validas, erros_trans = processador.validar_transicoes_fsm()
        if not transicoes_validas:
            print("\n❌ Transições inválidas encontradas. Corrija o template antes de prosseguir.")
            sys.exit(1)
        
        # Executar ações conforme fase especificada
        if args.fase in ['intencao', 'tudo']:
            processador.executar_registro_intencao(dry_run=args.dry_run)
        
        if args.fase in ['conclusao', 'tudo']:
            processador.executar_registro_conclusao(dry_run=args.dry_run)
        
        if args.fase in ['compliance', 'tudo']:
            processador.executar_compliance_tags(dry_run=args.dry_run)
        
        # Salvar template atualizado
        if not args.dry_run:
            processador.salvar_template_atualizado()
        
        # Gerar relatório
        relatorio_file = processador.gerar_relatorio()
        
        # Resumo final
        print("\n" + "=" * 80)
        if args.dry_run:
            print("DRY RUN CONCLUÍDO - Nenhuma alteração foi feita")
        else:
            print("EXECUÇÃO CONCLUÍDA")
        print("=" * 80)
        print(f"   Módulos processados: {processador.relatorio_execucao['modulos_processados']}")
        print(f"   Ações executadas: {processador.relatorio_execucao['acoes_executadas']}")
        print(f"   Tags de compliance: {processador.relatorio_execucao['compliance_tags_adicionadas']}")
        print(f"   Erros: {len(processador.relatorio_execucao['erros'])}")
        
        if processador.relatorio_execucao['erros']:
            print("\n⚠️  Erros encontrados:")
            for erro in processador.relatorio_execucao['erros']:
                print(f"   - {erro}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

