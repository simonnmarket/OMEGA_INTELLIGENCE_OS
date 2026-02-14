import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audit.audit import log_event
from conflict_management.conflict_manager import ConflictManager

class IntegrationLayer:
    def __init__(self):
        self.conflict_manager = ConflictManager()
        log_event("SYSTEM", "Integration Layer initialized")

    def process_module(self, module_name):
        log_event("PROCESS", f"Processing module: {module_name}")
        # Simulação de verificação de integridade
        if "error" in module_name.lower():
            self.conflict_manager.add_conflict(f"Module {module_name} has an error")
        return True

if __name__ == "__main__":
    il = IntegrationLayer()
    il.process_module("Test Module")
