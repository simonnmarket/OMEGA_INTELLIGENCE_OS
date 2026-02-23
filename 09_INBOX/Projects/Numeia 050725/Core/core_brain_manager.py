# numeia/core/core_brain_manager.py

from .module_registry import ModuleRegistry
from .execution_orchestrator import ExecutionOrchestrator

class CoreBrainManager:
    def __init__(self):
        self.registry = ModuleRegistry()
        self.orchestrator = ExecutionOrchestrator(self.registry)

    def initialize(self):
        print("[CoreBrainManager] Inicializando módulos registrados...")
        self.registry.initialize_all()

    def execute_cycle(self):
        print("[CoreBrainManager] Iniciando ciclo de execução...")
        execution_flow = self.orchestrator.define_execution_flow()
        for module in execution_flow:
            print(f"[CoreBrainManager] Executando módulo: {module.name}")
            module.execute()

    def health_check(self):
        print("[CoreBrainManager] Verificando integridade dos módulos...")
        return self.registry.check_all_modules()

    def audit_check(self):
        print("[CoreBrainManager] Enviando status à auditoria...")
        return self.registry.generate_audit_report()
