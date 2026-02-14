import sys
import os

# Adiciona o diretório pai ao path para importar audit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audit.audit import log_event

class ConflictManager:
    def __init__(self):
        self.conflicts = []

    def add_conflict(self, description):
        self.conflicts.append(description)
        log_event("CONFLICT", description)

    def list_conflicts(self):
        return self.conflicts

if __name__ == "__main__":
    cm = ConflictManager()
    cm.add_conflict("System check initiated")
    print(cm.list_conflicts())
