"""
WRAPPER AUTOMATICO — GENESIS_INCLUDES_V3_COMPLETE → NCNTModule v2.0
Gerado em: 2025-12-16
Baseado no NCNT MODULE TEMPLATE v2.0 (Tier-0 Goldman Sachs)
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "modules"))

from modules.ncnt_module_template_v2 import NCNTModule


class genesis_includes_v3_completeWrapper(NCNTModule):
    """Wrapper seguro e compliant para genesis_includes_v3_complete"""
    
    MODULE_VERSION = "2.0.0"
    COMPLIANCE_REQUIRED = True

    def __init__(self):
        super().__init__(
            module_name="genesis_includes_v3_complete_wrapper",
            config={"wrapped_module": "genesis_includes_v3_complete"}
        )
        self.required_modules = []

    def execute(self, *args, **kwargs):
        """Executa o módulo original"""
        self.vitals.status = "HEALTHY"
        try:
            import importlib.util
            module_file = project_root / "00-Governanca/genesis_includes_v3_complete.py"
            
            if not module_file.exists():
                self.logger.warning(f"Arquivo original nao encontrado: {module_file}")
                return None
            
            spec = importlib.util.spec_from_file_location(
                "genesis_includes_v3_complete", 
                str(module_file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Tentar executar função principal
            if hasattr(module, "main"):
                return getattr(module, "main")(*args, **kwargs)
            elif hasattr(module, "run"):
                return getattr(module, "run")(*args, **kwargs)
            else:
                return module
            
        except Exception as e:
            self.logger.critical(f"Falha critica em genesis_includes_v3_complete: {e}")
            self.vitals.status = "DEGRADED"
            self.vitals.error_rate += 1.0
            raise
