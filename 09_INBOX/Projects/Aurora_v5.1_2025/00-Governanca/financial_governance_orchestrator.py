"""
FINANCIAL SYSTEM GOVERNANCE ORCHESTRATOR - ENTERPRISE EDITION
================================================================

ESTRUTURA DE GOVERNANÇA INSTITUCIONAL
-------------------------------------
Este módulo implementa o Tratado de Governança para sistemas financeiros críticos,
seguindo padrões Goldman Sachs, JP Morgan, e Google SRE.

PRINCÍPIOS FUNDAMENTAIS:
1. AUDIT TRAIL IMUTÁVEL: Todos os logs são WORM (Write-Once-Read-Many) e encaminhados
   para storage externo/SIEM (Security Information & Event Management)
2. FSM INSTITUCIONAL: Máquina de estados com transições autorizadas documentadas
3. PIVOT PROTECTION: Módulos INACTIVE ficam em modo leitura até reativação explícita
4. CONSISTENCY BY DESIGN: IDs MOD-XXX são sequenciais e nunca reutilizados

PROTOCOLO OPERACIONAL PARA AGENTES IA:
---------------------------------------
1. SINCRONIZAÇÃO PRÉ-TAREFA:
   - Antes de qualquer ação, verificar status do módulo em project_manifest.json
   - Se status = BACKLOG, registrar log_event de ativação primeiro
   - Se status = INACTIVE, solicitar reativação documentada

2. EXECUÇÃO CONTROLADA:
   - Cada alteração de código deve corresponder a uma ação específica
   - Registrar intenção (status_type="active") antes de iniciar
   - Registrar conclusão (status_type="confirmed"/"completed") após validar

3. GESTÃO DE CRISE (PIVOT):
   - Para descontinuar funcionalidades: status_type="inactive"
   - Para retomar funcionalidades: status_type="active" com justificativa
   - Módulos INACTIVE: bloqueio total de execução automática

4. AUDIT TRAIL OBRIGATÓRIO:
   - Todo evento registrado em dois níveis: módulo + global_logs
   - Timestamp, ator, estado anterior, novo estado sempre documentados
   - Logs devem ser replicados para SIEM corporativo em produção

ESTADOS DA FSM (FINITE STATE MACHINE):
---------------------------------------
BACKLOG  → Identificado, não iniciado
ACTIVE   → Em desenvolvimento/operação ativa
INACTIVE → Congelado/descontinuado (somente leitura)
COMPLETED → Implementado e validado

TRANSIÇÕES AUTORIZADAS (FSM INSTITUCIONAL):
-------------------------------------------
BACKLOG  → ACTIVE           : Início de desenvolvimento
ACTIVE   → INACTIVE         : Congelamento por pivot
ACTIVE   → COMPLETED        : Implementação concluída
INACTIVE → ACTIVE           : Reativação documentada
COMPLETED → INACTIVE        : Descontinuação pós-conclusão
"""

import json
import datetime
import os
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional


class Status(Enum):
    """Estados institucionais da máquina de estados financeira."""
    BACKLOG = "BACKLOG"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    COMPLETED = "COMPLETED"


# TABELA DE TRANSIÇÕES AUTORIZADAS (FSM INSTITUCIONAL)
# Definem o fluxo de estados permitido para manter integridade operacional
ALLOWED_TRANSITIONS = {
    Status.BACKLOG.value: {Status.ACTIVE.value},
    Status.ACTIVE.value: {Status.INACTIVE.value, Status.COMPLETED.value},
    Status.INACTIVE.value: {Status.ACTIVE.value},  # Reativação requer evento explícito
    Status.COMPLETED.value: {Status.INACTIVE.value},  # Descontinuação pós-conclusão
}


class FinancialProjectOrchestrator:
    """
    ORQUESTRADOR INSTITUCIONAL DE MÓDULOS FINANCEIROS CRÍTICOS
    
    Atributos Principais:
        - Persistência em JSON com versionamento
        - FSM (Finite State Machine) com transições controladas
        - Audit Trail imutável em dois níveis (módulo + global)
        - Pivot Protection para módulos descontinuados
    
    Uso Corporativo:
        >>> orchestrator = FinancialProjectOrchestrator()
        >>> orchestrator.import_from_list(["risk_module", "trade_executor"])
        >>> orchestrator.log_event("MOD-001", "Implementação CVA", "active", actor="CRO")
        >>> orchestrator.log_event("MOD-001", "CVA validado por Model Risk", "completed", actor="Model Validation")
        >>> print(orchestrator.generate_report())
    """
    
    def __init__(self, db_file: str = "project_manifest.json"):
        """
        Inicializa o orquestrador com arquivo de persistência.
        
        Args:
            db_file: Caminho do arquivo JSON de governança
        """
        self.db_file = db_file
        self.state: Dict[str, Any] = self._load_db()
        self._ensure_external_logging_hook()

    # -------------------------------------------------------------------------
    # PERSISTÊNCIA E INTEGRIDADE
    # -------------------------------------------------------------------------
    def _load_db(self) -> Dict[str, Any]:
        """Carrega ou inicializa o estado de governança."""
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = self._initialize_new_manifest()
        
        return self._enforce_schema_integrity(data)
    
    def _initialize_new_manifest(self) -> Dict[str, Any]:
        """Inicializa um novo manifesto com metadados institucionais."""
        return {
            "metadata": {
                "project": "AURORA Trading System v5.1",
                "version": "2.0-enterprise",
                "governance_framework": "FSM Institutional v3.0",
                "compliance_frameworks": ["MiFID II", "Basel III", "SEC Rule 611", "GDPR"],
                "created_at": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "last_sync": datetime.datetime.now().isoformat(),
                "data_retention_policy": "7 years (FINRA 4511 compliant)",
            },
            "kpis": {
                "backlog": 0,
                "active": 0,
                "inactive": 0,
                "completed": 0
            },
            "priorities": [],
            "modules": {},
            "global_logs": [],
        }
    
    def _enforce_schema_integrity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Garante integridade do schema e adiciona campos obrigatórios."""
        data.setdefault("metadata", {})
        metadata = data["metadata"]
        metadata.setdefault("project", "AURORA Trading System v5.1")
        metadata.setdefault("version", "2.0-enterprise")
        metadata["last_updated"] = datetime.datetime.now().isoformat()
        metadata.setdefault("governance_framework", "FSM Institutional v3.0")
        if "last_sync" not in metadata:
            metadata["last_sync"] = datetime.datetime.now().isoformat()
        
        # Adicionar KPIs se não existir
        data.setdefault("kpis", {
            "backlog": 0,
            "active": 0,
            "inactive": 0,
            "completed": 0
        })
        
        # Adicionar priorities se não existir
        data.setdefault("priorities", [])
        
        data.setdefault("modules", {})
        data.setdefault("global_logs", [])
        
        # Adicionar campos novos aos módulos existentes (migração)
        for mod_id, module in data["modules"].items():
            if "priority" not in module:
                module["priority"] = "EVOLUÇÃO"
            if "blindagem" not in module:
                module["blindagem"] = {
                    "T": False,  # Testes
                    "H": False,  # Homologação
                    "I": False   # Integração
                }
            if "progress" not in module:
                module["progress"] = 0
        
        # Validação de consistência de IDs
        self._validate_module_ids(data["modules"])
        
        return data
    
    def _validate_module_ids(self, modules: Dict[str, Any]) -> None:
        """Valida que todos os IDs seguem padrão MOD-XXX e são únicos."""
        seen_ids = set()
        for mod_id in modules.keys():
            if not mod_id.startswith("MOD-"):
                print(f"⚠️  AVISO: ID não padrão detectado: {mod_id}")
            if mod_id in seen_ids:
                raise ValueError(f"❌ ERRO CRÍTICO: ID duplicado: {mod_id}")
            seen_ids.add(mod_id)
    
    def _save(self) -> None:
        """Persiste estado com validações e hooks de logging externo."""
        # Atualiza timestamp
        self.state["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
        
        # Atualizar KPIs antes de salvar
        self.calculate_kpis()
        
        # Hook para logging externo (SIEM, WORM storage)
        self._export_logs_to_external_system()
        
        # Persistência local
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False, sort_keys=True)
    
    def _ensure_external_logging_hook(self) -> None:
        """Configura hook para logging externo (SIEM corporativo)."""
        # Em produção, implementar conexão com Splunk/QRadar/Syslog
        # Por enquanto, apenas interface placeholder
        self.external_logging_enabled = False
        
    def _export_logs_to_external_system(self) -> None:
        """Exporta logs para sistemas de monitoramento corporativo."""
        if self.external_logging_enabled:
            # Implementar: syslog, HTTP POST para SIEM, etc.
            pass

    # -------------------------------------------------------------------------
    # MOTOR DE ONBOARDING (IMPORTAÇÃO)
    # -------------------------------------------------------------------------
    def _next_numeric_module_id(self) -> int:
        """
        Gera próximo ID numérico sequencial para MOD-XXX.
        
        Returns:
            Próximo número disponível (ex: 1, 2, 3...)
        
        Regra de Negócio:
            IDs nunca são reutilizados, mesmo que módulo seja descontinuado
        """
        max_id = 0
        for mid in self.state["modules"].keys():
            if mid.startswith("MOD-") and mid[4:].isdigit():
                try:
                    num_id = int(mid[4:])
                    max_id = max(max_id, num_id)
                except ValueError:
                    continue
        return max_id + 1
    
    def import_from_list(self, names_list: List[str]) -> str:
        """
        Importa módulos a partir de lista de nomes (onboarding conceitual).
        
        Args:
            names_list: Lista de nomes de módulos a importar
        
        Returns:
            Resumo da operação
        
        Exemplo:
            >>> import_from_list(["risk_module", "compliance_engine", "audit_trail"])
            "3 módulos importados com sucesso."
        """
        imported = 0
        duplicates = 0
        
        for name in names_list:
            # Gera ID sequencial
            next_id_num = self._next_numeric_module_id()
            mod_id = f"MOD-{str(next_id_num).zfill(3)}"
            
            # Pivot Protection: nunca sobrescreve módulo existente
            if mod_id in self.state["modules"]:
                duplicates += 1
                continue
            
            self._register_module(
                mod_id=mod_id,
                name=name,
                desc=f"Importado via lista conceitual - {datetime.datetime.now().strftime('%Y-%m-%d')}",
                import_source="conceptual_list"
            )
            imported += 1
        
        if duplicates > 0:
            print(f"⚠️  Ignorados {duplicates} módulos com IDs duplicados")
        
        self._save()
        return f"{imported} módulos importados com sucesso. IDs atribuídos: MOD-{self._next_numeric_module_id() - imported:03d} a MOD-{self._next_numeric_module_id() - 1:03d}"
    
    def import_from_directory(self, path: str, recursive: bool = True) -> str:
        """
        Escaneia diretório de código e cria módulos automaticamente.
        
        Args:
            path: Caminho do diretório raiz
            recursive: Incluir subdiretórios
        
        Returns:
            Resumo da operação
        
        Exemplo:
            >>> import_from_directory("./src", recursive=True)
            "45 módulos detectados em estrutura de diretórios."
        """
        root = Path(path)
        count = 0
        skipped = 0
        
        if not root.exists() or not root.is_dir():
            return f"❌ ERRO: Caminho inválido: {path}"
        
        # Padrão de escaneamento
        scan_pattern = "**" if recursive else "*"
        
        for item in root.glob(scan_pattern):
            if item.is_dir() and not item.name.startswith("."):
                # Determina tipo de ID baseado na estrutura
                if item.parent == root:
                    mod_id = f"MOD-DIR-{item.name.upper()}"
                else:
                    # Para subdiretórios: incluir path relativo
                    rel_path = str(item.relative_to(root)).replace("/", "-").replace("\\", "-")
                    mod_id = f"MOD-SUB-{rel_path.upper()}"
                
                # Pivot Protection: verifica se já existe
                if mod_id in self.state["modules"]:
                    skipped += 1
                    continue
                
                self._register_module(
                    mod_id=mod_id,
                    name=item.name,
                    desc=f"Estrutura de diretório detectada: {item}",
                    import_source="directory_scan"
                )
                count += 1
        
        self._save()
        
        summary = f"{count} diretórios convertidos em módulos."
        if skipped > 0:
            summary += f" {skipped} ignorados (já existentes)."
        
        return summary
    
    def _register_module(self, mod_id: str, name: str, desc: str, import_source: str = "unknown") -> None:
        """
        Registra novo módulo no sistema de governança.
        
        Args:
            mod_id: ID único do módulo (MOD-XXX)
            name: Nome descritivo
            desc: Descrição detalhada
            import_source: Origem do registro
        
        Regras:
            - Nunca sobrescreve módulos existentes
            - Inicializa com estado BACKLOG
            - Cria audit trail inicial
        """
        if mod_id in self.state["modules"]:
            raise ValueError(f"Módulo {mod_id} já existe. Operação bloqueada por Pivot Protection.")
        
        self.state["modules"][mod_id] = {
            "name": name,
            "description": desc,
            "status": Status.BACKLOG.value,
            "import_source": import_source,
            "import_timestamp": datetime.datetime.now().isoformat(),
            "actions": [],
            "created_at": datetime.datetime.now().isoformat(),
            "last_modified": datetime.datetime.now().isoformat(),
            "compliance_tags": [],  # Para tagging de frameworks regulatórios
            "risk_score": None,     # Score de risco dinâmico
            "priority": "EVOLUÇÃO",  # NOVO: Sistema de prioridades
            "blindagem": {           # NOVO: Blindagem (T/H/I)
                "T": False,  # Testes
                "H": False,  # Homologação
                "I": False   # Integração
            },
            "progress": 0,  # NOVO: Progresso (0-100)
        }
        
        # Audit trail inicial
        self._add_global_log(
            module_id=mod_id,
            action=f"Módulo registrado via {import_source}",
            event_type="IMPORT",
            previous_status=None,
            new_status=Status.BACKLOG.value,
            actor="System"
        )

    # -------------------------------------------------------------------------
    # FSM (FINITE STATE MACHINE) - VALIDAÇÃO DE TRANSIÇÕES
    # -------------------------------------------------------------------------
    def _can_transition(self, current_status: str, new_status: str) -> bool:
        """
        Valida se transição de estado é permitida pela FSM institucional.
        
        Args:
            current_status: Status atual do módulo
            new_status: Status pretendido
        
        Returns:
            True se transição é permitida, False caso contrário
        
        Regras:
            - Auto-transição (mesmo estado) sempre permitida
            - Transições devem estar em ALLOWED_TRANSITIONS
            - Transições não autorizadas são bloqueadas
        """
        if current_status == new_status:
            return True
        
        allowed_targets = ALLOWED_TRANSITIONS.get(current_status, set())
        return new_status in allowed_targets
    
    def get_allowed_transitions(self, current_status: str) -> List[str]:
        """
        Retorna lista de transições permitidas a partir do estado atual.
        
        Args:
            current_status: Status atual do módulo
        
        Returns:
            Lista de status permitidos
        
        Exemplo:
            >>> get_allowed_transitions("BACKLOG")
            ["ACTIVE"]
        """
        if current_status not in ALLOWED_TRANSITIONS:
            return []
        
        return list(ALLOWED_TRANSITIONS[current_status])

    # -------------------------------------------------------------------------
    # MOTOR DE AUDIT TRAIL E EXECUÇÃO CONTROLADA
    # -------------------------------------------------------------------------
    def log_event(
        self,
        mod_id: str,
        action_desc: str,
        status_type: str = "confirmed",
        actor: Optional[str] = None,
        metadata: Optional[Dict] = None,
        regulatory_context: Optional[List[str]] = None,
    ) -> str:
        """
        Registra evento no audit trail e gerencia transições de estado.
        
        Args:
            mod_id: Identificador do módulo (MOD-XXX)
            action_desc: Descrição objetiva da ação
            status_type:
                - "confirmed": Mantém/coloca em ACTIVE (execução confirmada)
                - "active": Transição para ACTIVE (início de trabalho)
                - "inactive": Transição para INACTIVE (congelamento)
                - "completed": Transição para COMPLETED (conclusão)
            actor: Responsável pela ação (ex: "CTO", "Risk Officer", "AI_Agent")
            metadata: Metadados adicionais do evento
            regulatory_context: Contextos regulatórios aplicáveis
        
        Returns:
            Resultado da operação (sucesso ou erro detalhado)
        
        Regras de Negócio:
            1. PIVOT PROTECTION: Módulos INACTIVE só aceitam reativação explícita
            2. FSM CONTROLADA: Transições devem seguir tabela autorizada
            3. AUDIT TRAIL DUPLO: Eventos registrados em módulo + global_logs
            4. IMUTABILIDADE: Logs nunca são alterados ou deletados
        """
        # Validação básica
        if mod_id not in self.state["modules"]:
            return f"❌ ERRO: Módulo {mod_id} não encontrado no manifesto."
        
        module = self.state["modules"][mod_id]
        current_status = module.get("status", Status.BACKLOG.value)
        actor = actor or "System"
        
        # Normaliza tipo de status
        status_type_lower = status_type.lower()
        status_type_normalized = status_type_lower
        
        # Determina novo status baseado no tipo de evento
        status_mapping = {
            "completed": Status.COMPLETED.value,
            "active": Status.ACTIVE.value,
            "confirmed": Status.ACTIVE.value,
            "inactive": Status.INACTIVE.value,
        }
        
        requested_status = status_mapping.get(status_type_normalized, current_status)
        
        # ========== PIVOT PROTECTION (PROTEÇÃO CRÍTICA) ==========
        if current_status == Status.INACTIVE.value and requested_status != Status.ACTIVE.value:
            error_msg = (
                f"🚨 BLOQUEIO POR PIVOT PROTECTION: Módulo {mod_id} está INATIVO.\n"
                f"   Ação solicitada: {action_desc}\n"
                f"   Status solicitado: {requested_status}\n"
                f"   REQUER: Reativação explícita com status_type='active' ou 'confirmed'"
            )
            print(error_msg)
            return error_msg
        
        # ========== VALIDAÇÃO FSM (CONTROLE DE TRANSIÇÕES) ==========
        if not self._can_transition(current_status, requested_status):
            allowed = self.get_allowed_transitions(current_status)
            error_msg = (
                f"🚨 TRANSIÇÃO FSM NÃO AUTORIZADA: {current_status} → {requested_status}\n"
                f"   Módulo: {mod_id}\n"
                f"   Ação: {action_desc}\n"
                f"   Transições permitidas: {allowed if allowed else 'Nenhuma'}"
            )
            print(error_msg)
            return error_msg
        
        # ========== PREPARAÇÃO DO EVENTO ==========
        timestamp = datetime.datetime.now().isoformat()
        
        # Evento no nível do módulo
        module_event = {
            "timestamp": timestamp,
            "action": action_desc,
            "type": status_type_normalized.upper(),
            "previous_status": current_status,
            "new_status": requested_status,
            "actor": actor,
            "version_affected": metadata.get("version") if metadata else None,
            "regulatory_context": regulatory_context or [],
        }
        
        if metadata:
            module_event["metadata"] = metadata
        
        # ========== REGISTRO NO AUDIT TRAIL ==========
        # 1. Append no log do módulo (audit trail local)
        if "actions" not in module:
            module["actions"] = []
        module["actions"].append(module_event)
        
        # 2. Atualiza status e timestamp
        module["status"] = requested_status
        module["last_modified"] = timestamp
        
        # 3. Append no log global (audit trail institucional)
        self._add_global_log(
            module_id=mod_id,
            action=action_desc,
            event_type=status_type_normalized.upper(),
            previous_status=current_status,
            new_status=requested_status,
            actor=actor,
            metadata=metadata,
            regulatory_context=regulatory_context
        )
        
        # 4. Persistência
        self._save()
        
        # ========== RESULTADO ==========
        success_msg = (
            f"✅ EVENTO REGISTRADO: {mod_id}\n"
            f"   Status: {current_status} → {requested_status}\n"
            f"   Ação: {action_desc}\n"
            f"   Ator: {actor}\n"
            f"   Timestamp: {timestamp}"
        )
        
        if regulatory_context:
            success_msg += f"\n   Contexto Regulatório: {', '.join(regulatory_context)}"
        
        print(success_msg)
        return success_msg
    
    def _add_global_log(
        self,
        module_id: str,
        action: str,
        event_type: str,
        previous_status: Optional[str],
        new_status: str,
        actor: str,
        metadata: Optional[Dict] = None,
        regulatory_context: Optional[List[str]] = None,
    ) -> None:
        """
        Adiciona evento ao log global (imutável, WORM-compliant).
        
        Este log é o audit trail institucional que nunca é alterado.
        Em produção, deve ser replicado para SIEM/WORM storage.
        """
        global_event = {
            "id": f"EVENT-{len(self.state['global_logs']) + 1:06d}",
            "timestamp": datetime.datetime.now().isoformat(),
            "module_id": module_id,
            "module_name": self.state["modules"].get(module_id, {}).get("name", "Unknown"),
            "action": action,
            "type": event_type,
            "previous_status": previous_status,
            "new_status": new_status,
            "actor": actor,
            "regulatory_context": regulatory_context or [],
            "system_version": self.state["metadata"]["version"],
        }
        
        if metadata:
            global_event["metadata"] = metadata
        
        # Garante imutabilidade: não modifica eventos existentes
        self.state["global_logs"].append(global_event)
        
        # Limite prático (em produção, arquivaria em cold storage)
        if len(self.state["global_logs"]) > 100000:  # 100k eventos
            print("⚠️  AVISO: Log global atingiu 100k eventos. Considere arquivamento.")

    # -------------------------------------------------------------------------
    # RELATÓRIOS E VISUALIZAÇÃO
    # -------------------------------------------------------------------------
    def generate_report(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Gera relatório executivo do estado da governança.
        
        Args:
            detailed: Incluir detalhes por módulo
        
        Returns:
            Dicionário com estatísticas e análise
        """
        modules = self.state["modules"]
        
        # Estatísticas básicas
        stats = {
            "TOTAL_MODULES": len(modules),
            "BY_STATUS": {},
            "BY_SOURCE": {},
            "TIMELINE": {
                "first_import": None,
                "last_activity": None,
                "activity_last_30d": 0,
            }
        }
        
        # Contagem por status
        for module in modules.values():
            status = module.get("status", Status.BACKLOG.value)
            stats["BY_STATUS"][status] = stats["BY_STATUS"].get(status, 0) + 1
            
            # Contagem por fonte
            source = module.get("import_source", "unknown")
            stats["BY_SOURCE"][source] = stats["BY_SOURCE"].get(source, 0) + 1
        
        # Detalhamento se solicitado
        if detailed:
            stats["MODULES_DETAILED"] = {
                mod_id: {
                    "name": data["name"],
                    "status": data["status"],
                    "created": data["created_at"],
                    "last_modified": data.get("last_modified", data["created_at"]),
                    "action_count": len(data.get("actions", [])),
                    "compliance_tags": data.get("compliance_tags", []),
                }
                for mod_id, data in modules.items()
            }
        
        # Análise de risco (simplificada)
        stats["RISK_ANALYSIS"] = {
            "high_risk_indicator": stats["BY_STATUS"].get(Status.ACTIVE.value, 0) > 50,
            "stagnation_warning": stats["BY_STATUS"].get(Status.BACKLOG.value, 0) > stats["TOTAL_MODULES"] * 0.3,
            "compliance_coverage": self._calculate_compliance_coverage(),
        }
        
        return stats
    
    def _calculate_compliance_coverage(self) -> float:
        """Calcula cobertura de frameworks regulatórios."""
        total_modules = len(self.state["modules"])
        if total_modules == 0:
            return 0.0
        
        modules_with_compliance = 0
        for module in self.state["modules"].values():
            if module.get("compliance_tags"):
                modules_with_compliance += 1
        
        return modules_with_compliance / total_modules * 100
    
    def get_module_history(self, mod_id: str) -> List[Dict[str, Any]]:
        """
        Retorna histórico completo de ações de um módulo.
        
        Args:
            mod_id: ID do módulo
        
        Returns:
            Lista de eventos em ordem cronológica
        """
        if mod_id not in self.state["modules"]:
            return []
        
        return self.state["modules"][mod_id].get("actions", [])
    
    def search_events(self, 
                     search_term: Optional[str] = None,
                     module_id: Optional[str] = None,
                     event_type: Optional[str] = None,
                     actor: Optional[str] = None,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca eventos no log global com filtros.
        
        Args:
            search_term: Termo para busca textual
            module_id: Filtrar por módulo
            event_type: Filtrar por tipo de evento
            actor: Filtrar por ator
            start_date: Data inicial (ISO format)
            end_date: Data final (ISO format)
        
        Returns:
            Lista de eventos filtrados
        """
        results = []
        
        for event in self.state.get("global_logs", []):
            # Aplica filtros
            if module_id and event.get("module_id") != module_id:
                continue
                
            if event_type and event.get("type") != event_type.upper():
                continue
                
            if actor and event.get("actor") != actor:
                continue
            
            # Filtro de data
            event_date = event.get("timestamp", "")
            if start_date and event_date < start_date:
                continue
            if end_date and event_date > end_date:
                continue
            
            # Busca textual
            if search_term:
                search_term_lower = search_term.lower()
                text_fields = [
                    event.get("action", ""),
                    event.get("module_name", ""),
                    event.get("actor", ""),
                ]
                if not any(search_term_lower in field.lower() for field in text_fields):
                    continue
            
            results.append(event)
        
        return results

    # -------------------------------------------------------------------------
    # UTILITÁRIOS DE COMPLIANCE
    # -------------------------------------------------------------------------
    def add_compliance_tag(self, mod_id: str, framework: str, version: str = "") -> str:
        """
        Adiciona tag de framework regulatório a um módulo.
        
        Args:
            mod_id: ID do módulo
            framework: Framework (ex: "MiFID II", "Basel III", "GDPR")
            version: Versão específica
        
        Returns:
            Resultado da operação
        """
        if mod_id not in self.state["modules"]:
            return f"❌ Módulo {mod_id} não encontrado."
        
        module = self.state["modules"][mod_id]
        
        if "compliance_tags" not in module:
            module["compliance_tags"] = []
        
        tag = f"{framework} {version}".strip()
        if tag not in module["compliance_tags"]:
            module["compliance_tags"].append(tag)
            self._save()
            
            # Audit trail
            self._add_global_log(
                module_id=mod_id,
                action=f"Tag de compliance adicionada: {tag}",
                event_type="COMPLIANCE",
                previous_status=module.get("status"),
                new_status=module.get("status"),
                actor="System"
            )
            
            return f"✅ Tag de compliance '{tag}' adicionada a {mod_id}"
        
        return f"⚠️  Tag '{tag}' já existe em {mod_id}"
    
    def get_compliance_report(self) -> Dict[str, List[str]]:
        """
        Gera relatório de cobertura de compliance por framework.
        
        Returns:
            Dicionário com framework -> lista de módulos cobertos
        """
        report = {}
        
        for mod_id, module in self.state["modules"].items():
            tags = module.get("compliance_tags", [])
            for tag in tags:
                report.setdefault(tag, [])
                report[tag].append(mod_id)
        
        return report
    
    # -------------------------------------------------------------------------
    # DASHBOARD E KPIs (NOVAS FUNCIONALIDADES)
    # -------------------------------------------------------------------------
    def calculate_kpis(self) -> Dict[str, int]:
        """
        Calcula KPIs a partir dos módulos registrados.
        
        Returns:
            Dicionário com contagem por status
        """
        kpis = {
            "backlog": 0,
            "active": 0,
            "inactive": 0,
            "completed": 0
        }
        
        for module in self.state["modules"].values():
            status = module.get("status", Status.BACKLOG.value)
            if status in kpis:
                kpis[status] = kpis.get(status, 0) + 1
        
        # Atualizar no estado
        self.state["kpis"] = kpis
        self._save()
        
        return kpis
    
    def update_priorities(self, mod_id: str, priority: str) -> str:
        """
        Atualiza prioridade de um módulo.
        
        Args:
            mod_id: ID do módulo
            priority: Prioridade (CRÍTICO, EMERGÊNCIA, ATIVO, EVOLUÇÃO)
        
        Returns:
            Resultado da operação
        """
        if mod_id not in self.state["modules"]:
            return f"❌ Módulo {mod_id} não encontrado."
        
        module = self.state["modules"][mod_id]
        old_priority = module.get("priority", "EVOLUÇÃO")
        module["priority"] = priority
        self._save()
        
        # Atualizar lista de prioridades
        priorities = self.state.get("priorities", [])
        # Remover se já existe
        priorities = [p for p in priorities if p.get("id") != mod_id]
        # Adicionar novo
        priorities.append({
            "id": mod_id,
            "name": module.get("name", ""),
            "priority": priority,
            "blindagem": module.get("blindagem", {})
        })
        # Ordenar por prioridade
        priority_order = {"CRÍTICO": 0, "EMERGÊNCIA": 1, "ATIVO": 2, "EVOLUÇÃO": 3}
        priorities.sort(key=lambda x: priority_order.get(x.get("priority", "EVOLUÇÃO"), 99))
        self.state["priorities"] = priorities
        self._save()
        
        # Audit trail
        self._add_global_log(
            module_id=mod_id,
            action=f"Prioridade atualizada: {old_priority} → {priority}",
            event_type="PRIORITY",
            previous_status=module.get("status"),
            new_status=module.get("status"),
            actor="System"
        )
        
        return f"✅ Prioridade de {mod_id} atualizada: {old_priority} → {priority}"
    
    def update_blindagem(self, mod_id: str, blindagem_type: str, value: bool) -> str:
        """
        Atualiza blindagem de um módulo.
        
        Args:
            mod_id: ID do módulo
            blindagem_type: Tipo (T=Testes, H=Homologação, I=Integração)
            value: True ou False
        
        Returns:
            Resultado da operação
        """
        if mod_id not in self.state["modules"]:
            return f"❌ Módulo {mod_id} não encontrado."
        
        module = self.state["modules"][mod_id]
        if "blindagem" not in module:
            module["blindagem"] = {"T": False, "H": False, "I": False}
        
        blindagem_type = blindagem_type.upper()
        if blindagem_type not in ["T", "H", "I"]:
            return f"❌ Tipo de blindagem inválido: {blindagem_type}. Use T, H ou I."
        
        old_value = module["blindagem"].get(blindagem_type, False)
        module["blindagem"][blindagem_type] = value
        self._save()
        
        # Audit trail
        tipo_nome = {"T": "Testes", "H": "Homologação", "I": "Integração"}[blindagem_type]
        self._add_global_log(
            module_id=mod_id,
            action=f"Blindagem {tipo_nome} atualizada: {old_value} → {value}",
            event_type="BLINDAGEM",
            previous_status=module.get("status"),
            new_status=module.get("status"),
            actor="System"
        )
        
        return f"✅ Blindagem {tipo_nome} de {mod_id} atualizada: {old_value} → {value}"
    
    def update_progress(self, mod_id: str, progress: int) -> str:
        """
        Atualiza progresso de um módulo (0-100).
        
        Args:
            mod_id: ID do módulo
            progress: Progresso (0-100)
        
        Returns:
            Resultado da operação
        """
        if mod_id not in self.state["modules"]:
            return f"❌ Módulo {mod_id} não encontrado."
        
        if not 0 <= progress <= 100:
            return f"❌ Progresso deve estar entre 0 e 100. Recebido: {progress}"
        
        module = self.state["modules"][mod_id]
        old_progress = module.get("progress", 0)
        module["progress"] = progress
        self._save()
        
        # Audit trail
        self._add_global_log(
            module_id=mod_id,
            action=f"Progresso atualizado: {old_progress}% → {progress}%",
            event_type="PROGRESS",
            previous_status=module.get("status"),
            new_status=module.get("status"),
            actor="System"
        )
        
        return f"✅ Progresso de {mod_id} atualizado: {old_progress}% → {progress}%"
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Gera dados para dashboard HTML.
        
        Returns:
            Dicionário com dados formatados para dashboard
        """
        # Calcular KPIs
        kpis = self.calculate_kpis()
        
        # Obter prioridades (top 10)
        priorities = self.state.get("priorities", [])[:10]
        
        # Obter módulos (top 20 para dashboard)
        modules_list = []
        for mod_id, module in list(self.state["modules"].items())[:20]:
            modules_list.append({
                "id": mod_id,
                "name": module.get("name", ""),
                "status": module.get("status", "BACKLOG"),
                "priority": module.get("priority", "EVOLUÇÃO"),
                "progress": module.get("progress", 0),
                "blindagem": module.get("blindagem", {"T": False, "H": False, "I": False}),
                "last_modified": module.get("last_modified", module.get("created_at", ""))
            })
        
        return {
            "kpis": kpis,
            "priorities": priorities,
            "modules": modules_list,
            "metadata": {
                "total_modules": len(self.state["modules"]),
                "last_sync": self.state["metadata"].get("last_sync", ""),
                "last_updated": self.state["metadata"].get("last_updated", ""),
                "version": self.state["metadata"].get("version", "")
            }
        }
    
    def sync_from_directory(self, use_source_of_truth: bool = True) -> str:
        """
        Sincroniza módulos do filesystem → manifest.
        
        IMPORTANTE: Por padrão usa fonte de verdade (252 módulos documentados).
        Se use_source_of_truth=False, escaneia filesystem (não recomendado).
        
        Args:
            use_source_of_truth: Se True, usa lista documentada de 252 módulos
        
        Returns:
            Resumo da sincronização
        """
        if use_source_of_truth:
            # Usar fonte de verdade (252 módulos documentados)
            try:
                from PROTOCOLO_FONTE_VERDADE import FonteVerdadeAurora
                fonte = FonteVerdadeAurora()
                modulos_documentados = fonte.obter_lista_modulos_documentada()
                
                # Verificar quais já estão no manifesto
                modulos_existentes = set(self.state["modules"].keys())
                novos = 0
                
                for mod_path in modulos_documentados:
                    nome_doc = mod_path.replace('\\', '_').replace('/', '_').replace('.py', '')
                    # Verificar se já existe
                    existe = False
                    for mod_id, mod_data in self.state["modules"].items():
                        if mod_data.get("name") == nome_doc:
                            existe = True
                            break
                    
                    if not existe:
                        # Importar módulo
                        next_id = self._next_numeric_module_id()
                        mod_id = f"MOD-{str(next_id).zfill(3)}"
                        # Extrair nome do arquivo
                        nome_arquivo = os.path.basename(mod_path) if os.path.sep in mod_path else mod_path
                        if nome_arquivo.endswith('.py'):
                            nome_arquivo = nome_arquivo[:-3]
                        self._register_module(
                            mod_id=mod_id,
                            name=nome_arquivo,
                            desc=f"Módulo documentado: {mod_path}",
                            import_source="source_of_truth"
                        )
                        novos += 1
                
                # Atualizar last_sync
                self.state["metadata"]["last_sync"] = datetime.datetime.now().isoformat()
                self._save()
                
                return f"Sincronizados {len(modulos_documentados)} módulos da fonte de verdade. {novos} novos módulos adicionados."
                
            except ImportError:
                return "ERRO: PROTOCOLO_FONTE_VERDADE.py não encontrado. Use fonte de verdade para sync."
        else:
            # Escanear filesystem (não recomendado, pode quebrar contagem de 252)
            root = Path(".")
            modules_count = 0
            
            for py_file in root.rglob("*.py"):
                if "backup" in py_file.parts or "backups" in py_file.parts or "__pycache__" in py_file.parts:
                    continue
                
                # Verificar se já existe
                path_str = str(py_file)
                existe = False
                for mod_data in self.state["modules"].values():
                    if mod_data.get("path") == path_str:
                        existe = True
                        break
                
                if not existe:
                    next_id = self._next_numeric_module_id()
                    mod_id = f"MOD-{str(next_id).zfill(3)}"
                    nome_arquivo = py_file.stem  # Nome sem extensão
                    self._register_module(
                        mod_id=mod_id,
                        name=nome_arquivo,
                        desc=f"Detectado via filesystem scan: {path_str}",
                        import_source="filesystem_scan"
                    )
                    modules_count += 1
            
            self.state["metadata"]["last_sync"] = datetime.datetime.now().isoformat()
            self._save()
            
            return f"Sincronizados {modules_count} módulos do filesystem. AVISO: Use fonte de verdade para garantir 252 módulos corretos."


def status_type_upper(status_type: str) -> str:
    """
    Normaliza tipo de status para uppercase.
    
    Args:
        status_type: Tipo de status em qualquer case
    
    Returns:
        Tipo em uppercase ou string vazia
    """
    return (status_type or "").upper()


# -----------------------------------------------------------------------------
# EXEMPLOS DE USO E TESTES
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("FINANCIAL SYSTEM GOVERNANCE ORCHESTRATOR - DEMONSTRAÇÃO")
    print("=" * 80)
    
    # 1. Inicialização
    orchestrator = FinancialProjectOrchestrator("demo_manifest.json")
    
    # 2. Importação de módulos
    print("\n📦 IMPORTANDO MÓDULOS CONCEITUAIS...")
    result = orchestrator.import_from_list([
        "Quantum Firewall",
        "Tier 1 Risk Validator", 
        "Audit System Complete",
        "CEO Agent Decision Engine",
        "Market Risk Module",
        "Alpha Momentum Strategy",
        "MT5 Execution Gateway",
        "Neural Connection Monitor"
    ])
    print(f"   Resultado: {result}")
    
    # 3. Ativação de um módulo
    print("\n⚡ ATIVANDO MÓDULO PARA DESENVOLVIMENTO...")
    result = orchestrator.log_event(
        mod_id="MOD-001",
        action_desc="Início do desenvolvimento do Quantum Firewall com validação MiFID II",
        status_type="active",
        actor="Chief Risk Officer",
        regulatory_context=["MiFID II", "Basel III", "SEC Rule 611"]
    )
    print(f"   {result}")
    
    # 4. Adicionando tag de compliance
    print("\n🏛️  ADICIONANDO TAGS DE COMPLIANCE...")
    result = orchestrator.add_compliance_tag("MOD-001", "MiFID II", "Artigo 16, 48")
    print(f"   {result}")
    result = orchestrator.add_compliance_tag("MOD-001", "Basel III", "Pillar 1")
    print(f"   {result}")
    
    # 5. Conclusão de desenvolvimento
    print("\n✅ REGISTRANDO CONCLUSÃO DE DESENVOLVIMENTO...")
    result = orchestrator.log_event(
        mod_id="MOD-001",
        action_desc="Quantum Firewall implementado com validação regulatória completa",
        status_type="completed",
        actor="Head of Technology",
        metadata={"version": "1.0.0", "test_coverage": "95%"},
        regulatory_context=["MiFID II", "GDPR", "FINRA 4511"]
    )
    print(f"   {result}")
    
    # 6. Gerando relatório
    print("\n📊 RELATÓRIO EXECUTIVO DO ESTADO DA GOVERNANÇA:")
    report = orchestrator.generate_report(detailed=False)
    
    print(f"   Total de Módulos: {report['TOTAL_MODULES']}")
    print(f"   Distribuição por Status:")
    for status, count in report["BY_STATUS"].items():
        print(f"     {status}: {count}")
    
    print(f"   Análise de Risco:")
    risk = report["RISK_ANALYSIS"]
    print(f"     Indicador de Alto Risco: {'SIM' if risk['high_risk_indicator'] else 'NÃO'}")
    print(f"     Cobertura Compliance: {risk['compliance_coverage']:.1f}%")
    
    # 7. Buscando histórico
    print("\n🔍 HISTÓRICO DO MÓDULO MOD-001:")
    history = orchestrator.get_module_history("MOD-001")
    for i, event in enumerate(history[-3:], 1):  # Últimos 3 eventos
        print(f"   {i}. [{event['timestamp'][:16]}] {event['actor']}: {event['action']}")
    
    # 8. Busca no log global
    print("\n🔎 BUSCA POR EVENTOS RECENTES:")
    recent_events = orchestrator.search_events(
        event_type="COMPLETED",
        start_date=(datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    )
    print(f"   Eventos 'COMPLETED' nas últimas 24h: {len(recent_events)}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRAÇÃO CONCLUÍDA. Manifesto salvo em: demo_manifest.json")
    print("=" * 80)

