#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Atualizações de Agentes Externos - AURORA v5.1
Processa templates YAML enviados por agentes externos/conselheiros
com validações rigorosas e blindagem total
"""

import sys
import os
import yaml
import json
import hashlib
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


class ProcessadorAgenteExterno:
    """
    Processa atualizações de agentes externos com validações rigorosas.
    """
    
    def __init__(self):
        """Inicializa processador com orquestrador e fonte de verdade."""
        self.orchestrator = FinancialProjectOrchestrator("project_manifest.json")
        self.fonte = FonteVerdadeAurora()
        self.relatorio = {
            "processados": 0,
            "aceitos": 0,
            "rejeitados": 0,
            "erros": [],
            "avisos": []
        }
    
    def validar_pre_processamento(self) -> bool:
        """Valida sistema antes de processar."""
        print("\n" + "=" * 80)
        print("VALIDACAO PRE-PROCESSAMENTO")
        print("=" * 80)
        
        if not protocolo_obrigatorio_antes_de_qualquer_acao():
            print("\nERRO: Validacao pre-processamento falhou. Abortando.")
            return False
        
        print("\n✅ Validacao pre-processamento passou")
        return True
    
    def carregar_template(self, template_file: str) -> Dict:
        """Carrega e valida template YAML."""
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"Template nao encontrado: {template_file}")
        
        print(f"\nCarregando template: {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            dados = yaml.safe_load(f)
        
        if not dados:
            raise ValueError("Template vazio ou invalido")
        
        # Validar estrutura
        campos_obrigatorios = ["metadata", "modulos_afetados"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise ValueError(f"Campo obrigatorio ausente: {campo}")
        
        print("✅ Template carregado e validado")
        return dados
    
    def validar_modulos(self, modulos: List[Dict]) -> Tuple[bool, List[str]]:
        """Valida que módulos mencionados existem no sistema."""
        erros = []
        
        for mod in modulos:
            mod_id = mod.get("id")
            if not mod_id:
                continue
            
            if mod_id not in self.orchestrator.state["modules"]:
                erros.append(f"Modulo {mod_id} nao encontrado no sistema")
        
        todas_validas = len(erros) == 0
        
        if todas_validas:
            print("✅ Todos os modulos sao validos")
        else:
            print(f"❌ {len(erros)} modulos invalidos encontrados")
            for erro in erros:
                print(f"   - {erro}")
        
        return todas_validas, erros
    
    def processar_sugestoes(self, dados: Dict, dry_run: bool = False) -> Dict:
        """Processa sugestões do agente externo."""
        print("\n" + "=" * 80)
        print("PROCESSANDO SUGESTOES")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 DRY RUN: Nenhuma alteracao sera feita")
        
        sugestoes = dados.get("sugestoes", [])
        processadas = 0
        
        for sugestao in sugestoes:
            tipo = sugestao.get("tipo", "")
            mod_id = sugestao.get("modulo_id", "")
            
            if not mod_id or mod_id not in self.orchestrator.state["modules"]:
                self.relatorio["erros"].append(f"Sugestao invalida: modulo {mod_id} nao encontrado")
                continue
            
            print(f"\nProcessando sugestao: {tipo} para {mod_id}")
            
            if tipo == "PRIORIDADE":
                prioridade = sugestao.get("valor_sugerido", "")
                if not dry_run:
                    try:
                        resultado = self.orchestrator.update_priorities(mod_id, prioridade)
                        processadas += 1
                        print(f"   ✅ {resultado}")
                    except Exception as e:
                        self.relatorio["erros"].append(f"Erro ao atualizar prioridade: {e}")
            
            elif tipo == "BLINDAGEM":
                blindagem_tipo = sugestao.get("blindagem_tipo", "")
                valor = sugestao.get("valor_sugerido", False)
                if not dry_run:
                    try:
                        resultado = self.orchestrator.update_blindagem(mod_id, blindagem_tipo, valor)
                        processadas += 1
                        print(f"   ✅ {resultado}")
                    except Exception as e:
                        self.relatorio["erros"].append(f"Erro ao atualizar blindagem: {e}")
            
            elif tipo == "PROGRESSO":
                progresso = sugestao.get("valor_sugerido", 0)
                if not dry_run:
                    try:
                        resultado = self.orchestrator.update_progress(mod_id, progresso)
                        processadas += 1
                        print(f"   ✅ {resultado}")
                    except Exception as e:
                        self.relatorio["erros"].append(f"Erro ao atualizar progresso: {e}")
        
        return {"processadas": processadas}
    
    def processar_atualizacoes_status(self, dados: Dict, dry_run: bool = False) -> Dict:
        """Processa atualizações de status com validação FSM."""
        print("\n" + "=" * 80)
        print("PROCESSANDO ATUALIZACOES DE STATUS")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 DRY RUN: Nenhuma alteracao sera feita")
        
        atualizacoes = dados.get("atualizacoes_status", [])
        processadas = 0
        
        for atualizacao in atualizacoes:
            mod_id = atualizacao.get("modulo_id", "")
            status_atual = atualizacao.get("status_atual", "")
            status_sugerido = atualizacao.get("status_sugerido", "")
            justificativa = atualizacao.get("justificativa", "")
            
            if not mod_id or mod_id not in self.orchestrator.state["modules"]:
                self.relatorio["erros"].append(f"Atualizacao invalida: modulo {mod_id} nao encontrado")
                continue
            
            # Validar transição FSM
            module = self.orchestrator.state["modules"][mod_id]
            current_status = module.get("status", "BACKLOG")
            
            if current_status != status_atual:
                self.relatorio["avisos"].append(
                    f"AVISO: Status atual de {mod_id} e {current_status}, nao {status_atual}"
                )
            
            # Mapear status sugerido para status_type
            status_mapping = {
                "ACTIVE": "active",
                "COMPLETED": "completed",
                "INACTIVE": "inactive",
                "BACKLOG": "backlog"
            }
            status_type = status_mapping.get(status_sugerido, "confirmed")
            
            print(f"\nProcessando atualizacao de status: {mod_id}")
            print(f"   {status_atual} → {status_sugerido}")
            
            if not dry_run:
                try:
                    # Preparar metadata
                    metadata = {}
                    if atualizacao.get("testes_aplicados"):
                        metadata["test_coverage"] = atualizacao.get("cobertura_testes", 0)
                        metadata["tests_applied"] = True
                    
                    resultado = self.orchestrator.log_event(
                        mod_id=mod_id,
                        action_desc=f"Atualizacao de status: {justificativa}",
                        status_type=status_type,
                        actor=dados.get("metadata", {}).get("sender_name", "Agente_Externo"),
                        metadata=metadata if metadata else None
                    )
                    processadas += 1
                    print(f"   ✅ Status atualizado")
                except Exception as e:
                    self.relatorio["erros"].append(f"Erro ao atualizar status: {e}")
                    print(f"   ❌ Erro: {e}")
        
        return {"processadas": processadas}
    
    def processar_compliance(self, dados: Dict, dry_run: bool = False) -> Dict:
        """Processa sugestões de compliance."""
        print("\n" + "=" * 80)
        print("PROCESSANDO TAGS DE COMPLIANCE")
        print("=" * 80)
        
        if dry_run:
            print("\n🔍 DRY RUN: Nenhuma alteracao sera feita")
        
        compliance = dados.get("compliance_sugestoes", [])
        processadas = 0
        
        for tag in compliance:
            mod_id = tag.get("modulo_id", "")
            framework = tag.get("framework", "")
            version = tag.get("version", "")
            
            if not mod_id or mod_id not in self.orchestrator.state["modules"]:
                self.relatorio["erros"].append(f"Tag invalida: modulo {mod_id} nao encontrado")
                continue
            
            print(f"\nAdicionando tag de compliance: {mod_id}")
            print(f"   Framework: {framework} {version}")
            
            if not dry_run:
                try:
                    resultado = self.orchestrator.add_compliance_tag(mod_id, framework, version)
                    processadas += 1
                    print(f"   ✅ {resultado}")
                except Exception as e:
                    self.relatorio["erros"].append(f"Erro ao adicionar tag: {e}")
        
        return {"processadas": processadas}
    
    def calcular_hash_template(self, template_file: str) -> str:
        """Calcula hash SHA3-256 do template para assinatura digital."""
        with open(template_file, 'rb') as f:
            content = f.read()
        return hashlib.sha3_256(content).hexdigest()
    
    def gerar_relatorio(self, dados: Dict, template_file: str) -> str:
        """Gera relatório de processamento."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_file = f"RELATORIO_AGENTE_EXTERNO_{timestamp}.json"
        
        hash_template = self.calcular_hash_template(template_file)
        
        relatorio_completo = {
            "template_file": template_file,
            "hash_template": hash_template,
            "data_processamento": datetime.now().isoformat(),
            "sender": dados.get("metadata", {}).get("sender_name", "Unknown"),
            "relatorio": self.relatorio,
            "status_sistema": self.orchestrator.generate_report(detailed=False)
        }
        
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio_completo, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Relatorio salvo em: {relatorio_file}")
        return relatorio_file


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Processar template de agente externo')
    parser.add_argument('template_file', help='Arquivo template YAML do agente externo')
    parser.add_argument('--dry-run', action='store_true', help='Apenas simular sem executar')
    
    args = parser.parse_args()
    
    try:
        processador = ProcessadorAgenteExterno()
        
        # Validar pré-processamento
        if not processador.validar_pre_processamento():
            print("\n❌ Validação pré-processamento falhou. Abortando.")
            sys.exit(1)
        
        # Carregar template
        dados = processador.carregar_template(args.template_file)
        
        # Validar módulos
        modulos = dados.get("modulos_afetados", [])
        todas_validas, erros = processador.validar_modulos(modulos)
        
        if not todas_validas:
            print("\n❌ Módulos inválidos encontrados. Corrija o template antes de prosseguir.")
            sys.exit(1)
        
        # Processar sugestões
        processador.processar_sugestoes(dados, dry_run=args.dry_run)
        
        # Processar atualizações de status
        processador.processar_atualizacoes_status(dados, dry_run=args.dry_run)
        
        # Processar compliance
        processador.processar_compliance(dados, dry_run=args.dry_run)
        
        # Gerar relatório
        relatorio_file = processador.gerar_relatorio(dados, args.template_file)
        
        # Resumo final
        print("\n" + "=" * 80)
        if args.dry_run:
            print("DRY RUN CONCLUÍDO - Nenhuma alteração foi feita")
        else:
            print("PROCESSAMENTO CONCLUÍDO")
        print("=" * 80)
        print(f"   Sugestões processadas: {processador.relatorio.get('processados', 0)}")
        print(f"   Aceitas: {processador.relatorio.get('aceitos', 0)}")
        print(f"   Rejeitadas: {processador.relatorio.get('rejeitados', 0)}")
        print(f"   Erros: {len(processador.relatorio.get('erros', []))}")
        print(f"   Avisos: {len(processador.relatorio.get('avisos', []))}")
        
        if processador.relatorio.get('erros'):
            print("\n⚠️  Erros encontrados:")
            for erro in processador.relatorio['erros']:
                print(f"   - {erro}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

