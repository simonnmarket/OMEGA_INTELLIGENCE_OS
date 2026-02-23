"""
WRAPPER AUTOMATICO — PREMARKETCHECKLIST_MODULE → NCNTModule v2.0
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


class premarketchecklist_moduleWrapper(NCNTModule):
    """Wrapper seguro e compliant para premarketchecklist_module"""
    
    MODULE_VERSION = "2.0.0"
    COMPLIANCE_REQUIRED = True

    def __init__(self):
        super().__init__(
            module_name="premarketchecklist_module_wrapper",
            config={"wrapped_module": "premarketchecklist_module"}
        )
        self.required_modules = []

    def execute(self, *args, **kwargs):
        """Executa o módulo original"""
        self.vitals.status = "HEALTHY"
        try:
            import importlib.util
            module_file = project_root / "03-Operacoes-Diarias/Pre-Market/premarketchecklist_module.py"
            
            if not module_file.exists():
                self.logger.warning(f"Arquivo original nao encontrado: {module_file}")
                return None
            
            spec = importlib.util.spec_from_file_location(
                "premarketchecklist_module", 
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
            self.logger.critical(f"Falha critica em premarketchecklist_module: {e}")
            self.vitals.status = "DEGRADED"
            self.vitals.error_rate += 1.0
            raise
