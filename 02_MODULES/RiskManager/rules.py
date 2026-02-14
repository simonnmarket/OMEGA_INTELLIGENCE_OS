import sys
import os

# Ajuste de path para alcançar 01_CORE a partir de 02_MODULES/RiskManager
# O script está em ../02_MODULES/RiskManager/rules.py. O Core está em ../01_CORE
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../01_CORE')))
from conflict_management.conflict_manager import ConflictManager
from audit.audit import log_event

class RiskValidator:
    def __init__(self):
        self.conflict_manager = ConflictManager()
        log_event("RISK", "Risk Validator initialized")

    def validate(self, project_data):
        if any(v < 0 for v in project_data.get("values", [])):
            self.conflict_manager.add_conflict("Negative value detected")
            return False
        return True

if __name__ == "__main__":
    rv = RiskValidator()
    rv.validate({"values": [10, -5, 20]})
