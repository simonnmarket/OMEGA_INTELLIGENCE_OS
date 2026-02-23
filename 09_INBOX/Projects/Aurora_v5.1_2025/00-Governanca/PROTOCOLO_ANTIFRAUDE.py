#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 PROTOCOLO ANTIFRAUDE - AURORA v5.1
=====================================

PROTOCOLO CRÍTICO QUE IMPEDE RELATÓRIOS FALSOS E FRAUDES NO SISTEMA

REGRAS ABSOLUTAS:
1. NENHUM relatório pode ser gerado sem execução real validada
2. NENHUM checklist pode ser atualizado sem evidências verificáveis
3. NENHUM status "CONCLUÍDO" sem confirmação do usuário
4. TODAS as execuções devem gerar logs e evidências
5. TODAS as atualizações são auditadas automaticamente

Data de Criação: 2025-12-26
Motivo: Prevenir fraudes como ARCH-001
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class StatusExecucao(Enum):
    """Status de execução validado"""
    NAO_EXECUTADO = "NAO_EXECUTADO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    EXECUTADO_COM_SUCESSO = "EXECUTADO_COM_SUCESSO"
    EXECUTADO_COM_ERRO = "EXECUTADO_COM_ERRO"
    VALIDADO_PELO_USUARIO = "VALIDADO_PELO_USUARIO"


class TipoEvidencia(Enum):
    """Tipos de evidências aceitas"""
    LOG_EXECUCAO = "LOG_EXECUCAO"
    ARQUIVO_GERADO = "ARQUIVO_GERADO"
    HASH_VERIFICACAO = "HASH_VERIFICACAO"
    SAIDA_CONSOLE = "SAIDA_CONSOLE"
    TESTE_AUTOMATIZADO = "TESTE_AUTOMATIZADO"
    CONFIRMACAO_USUARIO = "CONFIRMACAO_USUARIO"


class ProtocoloAntifraude:
    """
    Sistema de proteção contra relatórios falsos e fraudes.
    
    Este protocolo é OBRIGATÓRIO antes de:
    - Gerar qualquer relatório de conclusão
    - Atualizar checklist com status "CONCLUÍDO"
    - Marcar tarefa como completa
    """
    
    def __init__(self, projeto_root: str = "."):
        self.projeto_root = Path(projeto_root).resolve()
        self.audit_dir = self.projeto_root / "00-Governanca" / "auditoria_antifraude"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivo de auditoria principal
        self.audit_file = self.audit_dir / "auditoria_completa.json"
        self.registro_execucoes = self._carregar_registro()
        
        # Lista de tarefas bloqueadas (fraudes detectadas)
        self.tarefas_bloqueadas = self._carregar_tarefas_bloqueadas()
    
    def _carregar_registro(self) -> Dict:
        """Carrega registro de execuções"""
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "versao": "1.0.0",
            "data_criacao": datetime.now().isoformat(),
            "execucoes": {},
            "fraudes_detectadas": [],
            "bloqueios_ativos": []
        }
    
    def _salvar_registro(self):
        """Salva registro de execuções"""
        with open(self.audit_file, 'w', encoding='utf-8') as f:
            json.dump(self.registro_execucoes, f, indent=2, ensure_ascii=False)
    
    def _carregar_tarefas_bloqueadas(self) -> List[str]:
        """Carrega lista de tarefas bloqueadas"""
        bloqueios_file = self.audit_dir / "tarefas_bloqueadas.json"
        if bloqueios_file.exists():
            try:
                with open(bloqueios_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("tarefas", [])
            except:
                pass
        return []
    
    def _salvar_tarefas_bloqueadas(self):
        """Salva lista de tarefas bloqueadas"""
        bloqueios_file = self.audit_dir / "tarefas_bloqueadas.json"
        with open(bloqueios_file, 'w', encoding='utf-8') as f:
            json.dump({"tarefas": self.tarefas_bloqueadas}, f, indent=2, ensure_ascii=False)
    
    def registrar_inicio_execucao(self, tarefa_id: str, script_path: str, 
                                   descricao: str = "") -> str:
        """
        Registra início de execução de uma tarefa.
        
        Returns:
            ID único da execução
        """
        execucao_id = f"{tarefa_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        registro = {
            "execucao_id": execucao_id,
            "tarefa_id": tarefa_id,
            "script_path": str(script_path),
            "descricao": descricao,
            "status": StatusExecucao.EM_ANDAMENTO.value,
            "timestamp_inicio": datetime.now().isoformat(),
            "timestamp_fim": None,
            "evidencias": [],
            "hash_script": self._calcular_hash_arquivo(script_path),
            "saida_console": None,
            "codigo_saida": None,
            "validado_pelo_usuario": False,
            "relatorio_gerado": False
        }
        
        if "execucoes" not in self.registro_execucoes:
            self.registro_execucoes["execucoes"] = {}
        
        self.registro_execucoes["execucoes"][execucao_id] = registro
        self._salvar_registro()
        
        return execucao_id
    
    def registrar_fim_execucao(self, execucao_id: str, codigo_saida: int,
                                saida_console: str = "", evidencias: List[Dict] = None):
        """
        Registra fim de execução com evidências.
        
        Args:
            execucao_id: ID da execução
            codigo_saida: Código de saída do script (0 = sucesso)
            saida_console: Saída do console
            evidencias: Lista de evidências geradas
        """
        if execucao_id not in self.registro_execucoes["execucoes"]:
            raise ValueError(f"Execução {execucao_id} não encontrada")
        
        registro = self.registro_execucoes["execucoes"][execucao_id]
        registro["timestamp_fim"] = datetime.now().isoformat()
        registro["codigo_saida"] = codigo_saida
        registro["saida_console"] = saida_console[:10000]  # Limitar tamanho
        registro["evidencias"] = evidencias or []
        
        if codigo_saida == 0:
            registro["status"] = StatusExecucao.EXECUTADO_COM_SUCESSO.value
        else:
            registro["status"] = StatusExecucao.EXECUTADO_COM_ERRO.value
        
        self._salvar_registro()
    
    def adicionar_evidencia(self, execucao_id: str, tipo: TipoEvidencia,
                            caminho: str, descricao: str = "", hash_arquivo: str = None):
        """Adiciona evidência a uma execução"""
        if execucao_id not in self.registro_execucoes["execucoes"]:
            raise ValueError(f"Execução {execucao_id} não encontrada")
        
        evidencia = {
            "tipo": tipo.value,
            "caminho": str(caminho),
            "descricao": descricao,
            "hash": hash_arquivo or self._calcular_hash_arquivo(caminho),
            "timestamp": datetime.now().isoformat()
        }
        
        self.registro_execucoes["execucoes"][execucao_id]["evidencias"].append(evidencia)
        self._salvar_registro()
    
    def validar_execucao_antes_relatorio(self, tarefa_id: str) -> Tuple[bool, str, Dict]:
        """
        VALIDAÇÃO CRÍTICA: Verifica se execução real ocorreu antes de permitir relatório.
        
        Returns:
            (permitido, mensagem, detalhes)
        """
        # Buscar última execução da tarefa
        execucoes_tarefa = [
            (eid, exec_data)
            for eid, exec_data in self.registro_execucoes["execucoes"].items()
            if exec_data["tarefa_id"] == tarefa_id
        ]
        
        if not execucoes_tarefa:
            return False, f"❌ NENHUMA EXECUÇÃO REGISTRADA para {tarefa_id}", {}
        
        # Pegar última execução
        ultima_exec = sorted(execucoes_tarefa, key=lambda x: x[1]["timestamp_inicio"], reverse=True)[0]
        execucao_id, exec_data = ultima_exec
        
        # Verificar se está bloqueada
        if tarefa_id in self.tarefas_bloqueadas:
            return False, f"🚨 TAREFA {tarefa_id} ESTÁ BLOQUEADA (fraude detectada anteriormente)", {}
        
        # Verificar status
        if exec_data["status"] == StatusExecucao.NAO_EXECUTADO.value:
            return False, f"❌ Execução {execucao_id} não foi executada", exec_data
        
        if exec_data["status"] == StatusExecucao.EM_ANDAMENTO.value:
            return False, f"⏳ Execução {execucao_id} ainda está em andamento", exec_data
        
        if exec_data["status"] == StatusExecucao.EXECUTADO_COM_ERRO.value:
            return False, f"❌ Execução {execucao_id} falhou (código: {exec_data.get('codigo_saida')})", exec_data
        
        # Verificar evidências
        evidencias = exec_data.get("evidencias", [])
        if not evidencias:
            return False, f"⚠️ Execução {execucao_id} não possui evidências válidas", exec_data
        
        # Verificar se arquivos de evidência existem
        evidencias_validas = 0
        for evid in evidencias:
            if os.path.exists(evid["caminho"]):
                evidencias_validas += 1
        
        if evidencias_validas == 0:
            return False, f"❌ Nenhuma evidência física encontrada para {execucao_id}", exec_data
        
        # Verificar se já foi validado pelo usuário (para status CONCLUÍDO)
        if not exec_data.get("validado_pelo_usuario", False):
            return True, f"⚠️ Execução {execucao_id} precisa de confirmação do usuário antes de marcar como CONCLUÍDO", exec_data
        
        return True, f"✅ Execução {execucao_id} validada", exec_data
    
    def bloquear_tarefa(self, tarefa_id: str, motivo: str):
        """Bloqueia uma tarefa (fraude detectada)"""
        if tarefa_id not in self.tarefas_bloqueadas:
            self.tarefas_bloqueadas.append(tarefa_id)
            self._salvar_tarefas_bloqueadas()
        
        # Registrar fraude
        fraude = {
            "tarefa_id": tarefa_id,
            "motivo": motivo,
            "timestamp": datetime.now().isoformat(),
            "status": "BLOQUEADA"
        }
        
        if "fraudes_detectadas" not in self.registro_execucoes:
            self.registro_execucoes["fraudes_detectadas"] = []
        
        self.registro_execucoes["fraudes_detectadas"].append(fraude)
        self._salvar_registro()
    
    def validar_antes_atualizar_checklist(self, item_id: str, novo_status: str,
                                          evidencia_fornecida: str = "") -> Tuple[bool, str]:
        """
        VALIDAÇÃO OBRIGATÓRIA antes de atualizar checklist.
        
        BLOQUEIA atualização se:
        - Status for "CONCLUÍDO" sem execução validada
        - Tarefa estiver bloqueada
        - Não houver evidências
        """
        # Verificar se está bloqueada
        if item_id in self.tarefas_bloqueadas:
            return False, f"🚨 BLOQUEADO: {item_id} está bloqueada por fraude anterior"
        
        # Se status for CONCLUÍDO, validar execução
        if novo_status.upper() in ["CONCLUÍDO", "CONCLUIDO", "COMPLETO", "SUCESSO"]:
            permitido, mensagem, detalhes = self.validar_execucao_antes_relatorio(item_id)
            
            if not permitido:
                return False, f"🚨 BLOQUEADO: {mensagem}"
            
            # Verificar se foi validado pelo usuário
            if not detalhes.get("validado_pelo_usuario", False):
                return False, f"⚠️ REQUER CONFIRMAÇÃO: {item_id} precisa de confirmação do usuário antes de marcar como CONCLUÍDO"
        
        return True, "✅ Validação aprovada"
    
    def marcar_validado_pelo_usuario(self, execucao_id: str):
        """Marca execução como validada pelo usuário"""
        if execucao_id not in self.registro_execucoes["execucoes"]:
            raise ValueError(f"Execução {execucao_id} não encontrada")
        
        self.registro_execucoes["execucoes"][execucao_id]["validado_pelo_usuario"] = True
        self.registro_execucoes["execucoes"][execucao_id]["status"] = StatusExecucao.VALIDADO_PELO_USUARIO.value
        self._salvar_registro()
    
    def _calcular_hash_arquivo(self, caminho: str) -> Optional[str]:
        """Calcula hash SHA256 de arquivo"""
        try:
            if os.path.exists(caminho):
                with open(caminho, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()[:16]
        except:
            pass
        return None
    
    def gerar_relatorio_auditoria(self) -> str:
        """Gera relatório completo de auditoria"""
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("🚨 RELATÓRIO DE AUDITORIA ANTIFRAUDE")
        relatorio.append("=" * 80)
        relatorio.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        relatorio.append("")
        
        # Estatísticas
        total_execucoes = len(self.registro_execucoes.get("execucoes", {}))
        total_fraudes = len(self.registro_execucoes.get("fraudes_detectadas", []))
        total_bloqueios = len(self.tarefas_bloqueadas)
        
        relatorio.append("📊 ESTATÍSTICAS:")
        relatorio.append(f"  • Total de execuções registradas: {total_execucoes}")
        relatorio.append(f"  • Fraudes detectadas: {total_fraudes}")
        relatorio.append(f"  • Tarefas bloqueadas: {total_bloqueios}")
        relatorio.append("")
        
        # Tarefas bloqueadas
        if self.tarefas_bloqueadas:
            relatorio.append("🚨 TAREFAS BLOQUEADAS:")
            for tarefa in self.tarefas_bloqueadas:
                relatorio.append(f"  • {tarefa}")
            relatorio.append("")
        
        # Fraudes detectadas
        if self.registro_execucoes.get("fraudes_detectadas"):
            relatorio.append("❌ FRAUDES DETECTADAS:")
            for fraude in self.registro_execucoes["fraudes_detectadas"][-10:]:  # Últimas 10
                relatorio.append(f"  • {fraude['tarefa_id']}: {fraude['motivo']} ({fraude['timestamp']})")
            relatorio.append("")
        
        # Últimas execuções
        relatorio.append("📋 ÚLTIMAS 10 EXECUÇÕES:")
        execucoes = sorted(
            self.registro_execucoes.get("execucoes", {}).items(),
            key=lambda x: x[1]["timestamp_inicio"],
            reverse=True
        )[:10]
        
        for exec_id, exec_data in execucoes:
            status_emoji = {
                "NAO_EXECUTADO": "❌",
                "EM_ANDAMENTO": "⏳",
                "EXECUTADO_COM_SUCESSO": "✅",
                "EXECUTADO_COM_ERRO": "❌",
                "VALIDADO_PELO_USUARIO": "✅"
            }.get(exec_data["status"], "❓")
            
            relatorio.append(f"  {status_emoji} {exec_data['tarefa_id']} ({exec_data['status']})")
            relatorio.append(f"     Evidências: {len(exec_data.get('evidencias', []))}")
            relatorio.append(f"     Validado: {'Sim' if exec_data.get('validado_pelo_usuario') else 'Não'}")
        
        relatorio.append("")
        relatorio.append("=" * 80)
        
        return "\n".join(relatorio)


# ============================================================================
# FUNÇÕES DE VALIDAÇÃO OBRIGATÓRIAS
# ============================================================================

def validar_antes_gerar_relatorio(tarefa_id: str, projeto_root: str = ".") -> Tuple[bool, str]:
    """
    FUNÇÃO OBRIGATÓRIA: Valida antes de gerar qualquer relatório.
    
    USO:
        if not validar_antes_gerar_relatorio("ARCH-001"):
            print("BLOQUEADO: Execução não validada")
            return
    """
    protocolo = ProtocoloAntifraude(projeto_root)
    permitido, mensagem, _ = protocolo.validar_execucao_antes_relatorio(tarefa_id)
    return permitido, mensagem


def validar_antes_atualizar_checklist(item_id: str, novo_status: str,
                                     evidencia: str = "", projeto_root: str = ".") -> Tuple[bool, str]:
    """
    FUNÇÃO OBRIGATÓRIA: Valida antes de atualizar checklist.
    
    USO:
        if not validar_antes_atualizar_checklist("ARCH-001", "CONCLUÍDO", "evidencia"):
            print("BLOQUEADO: Não pode atualizar")
            return
    """
    protocolo = ProtocoloAntifraude(projeto_root)
    return protocolo.validar_antes_atualizar_checklist(item_id, novo_status, evidencia)


def executar_com_auditoria(tarefa_id: str, script_path: str, descricao: str = "",
                           projeto_root: str = ".") -> Tuple[bool, str, Dict]:
    """
    Executa script com auditoria completa.
    
    Returns:
        (sucesso, execucao_id, dados_execucao)
    """
    protocolo = ProtocoloAntifraude(projeto_root)
    
    # Registrar início
    execucao_id = protocolo.registrar_inicio_execucao(tarefa_id, script_path, descricao)
    
    try:
        # Executar script
        resultado = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hora máximo
        )
        
        # Coletar evidências
        evidencias = []
        
        # Evidência: saída do console
        if resultado.stdout:
            log_file = protocolo.audit_dir / f"{execucao_id}_console.log"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(resultado.stdout)
            evidencias.append({
                "tipo": TipoEvidencia.SAIDA_CONSOLE.value,
                "caminho": str(log_file),
                "descricao": "Saída do console"
            })
        
        # Registrar fim
        protocolo.registrar_fim_execucao(
            execucao_id,
            resultado.returncode,
            resultado.stdout,
            evidencias
        )
        
        return resultado.returncode == 0, execucao_id, protocolo.registro_execucoes["execucoes"][execucao_id]
    
    except subprocess.TimeoutExpired:
        protocolo.registrar_fim_execucao(execucao_id, -1, "TIMEOUT", [])
        return False, execucao_id, {}
    except Exception as e:
        protocolo.registrar_fim_execucao(execucao_id, -1, str(e), [])
        return False, execucao_id, {}


if __name__ == "__main__":
    # Teste do protocolo
    print("=" * 80)
    print("🚨 TESTE DO PROTOCOLO ANTIFRAUDE")
    print("=" * 80)
    
    protocolo = ProtocoloAntifraude()
    
    # Gerar relatório
    relatorio = protocolo.gerar_relatorio_auditoria()
    print(relatorio)
    
    # Salvar relatório
    relatorio_file = protocolo.audit_dir / "relatorio_auditoria.txt"
    with open(relatorio_file, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print(f"\n✅ Relatório salvo em: {relatorio_file}")

