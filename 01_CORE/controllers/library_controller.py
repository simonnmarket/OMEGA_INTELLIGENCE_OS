import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audit.audit import log_event

METADATA_FILE = "02_MODULES/Include/metadata_schema.json"

class LibraryController:
    def __init__(self):
        try:
            with open(METADATA_FILE, "r") as f:
                self.metadata = json.load(f)
        except Exception as e:
            # Fallback handling or empty init
            self.metadata = []
        log_event("LIBRARY", "Library Controller initialized")

    def filter_modules(self, **criteria):
        results = self.metadata
        # Se metadata for um objeto (schema) em vez de lista, precisamos adaptar. 
        # O código do usuário assume uma lista de objetos.
        if isinstance(results, dict): 
            # Se for apenas o schema, não há dados para filtrar.
            # Vamos assumir que em produção haveria uma lista real.
            # Para não quebrar, retornamos vazio se não for lista.
            results = [] 
            
        for key, value in criteria.items():
            results = [m for m in results if m.get(key) == value]
        log_event("LIBRARY", f"Filtered modules with criteria: {criteria}")
        return results

if __name__ == "__main__":
    lc = LibraryController()
    lc.filter_modules(status="ready")
