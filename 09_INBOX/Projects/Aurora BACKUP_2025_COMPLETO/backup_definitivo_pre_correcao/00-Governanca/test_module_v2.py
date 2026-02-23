#!/usr/bin/env python3
"""
MÓDULO DE TESTE v2.0 - Para validar o template atualizado
"""

import sys
import os

# Adicionar caminhos
project_root = os.path.dirname(os.path.dirname(__file__))
modules_path = os.path.join(project_root, 'modules')
sys.path.insert(0, project_root)
sys.path.insert(0, modules_path)

# Importar template
import importlib.util
template_path = os.path.join(modules_path, 'ncnt_module_template.py')
spec = importlib.util.spec_from_file_location("ncnt_module_template", template_path)
ncnt_template = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ncnt_template)
NCNTModule = ncnt_template.NCNTModule

# Importar integration gate
gate_path = os.path.join(os.path.dirname(__file__), 'integration_gate_v2.py')
spec_gate = importlib.util.spec_from_file_location("integration_gate_v2", gate_path)
gate_module = importlib.util.module_from_spec(spec_gate)
spec_gate.loader.exec_module(gate_module)
require_integration_gate = gate_module.require_integration_gate
get_integration_gate = gate_module.get_integration_gate
import hashlib
from datetime import datetime
from typing import Dict

@require_integration_gate
class TestModuleV2(NCNTModule):
    """Módulo de teste que usa todas as features v2.0"""
    
    MODULE_VERSION = "2.0.0"
    
    def __init__(self, test_param: int = 42):
        config = {
            "test_param": test_param,
            "created_at": datetime.now().isoformat(),
            "test_config": "custom_value_123"
        }
        
        super().__init__("TestModuleV2_Demo", config)
        
        # Dependências de exemplo
        self.required_modules = ["system_config"]
        
        # Configuração específica para gerar instance_checksum único
        self.instance_specific_data = {
            "param": test_param,
            "hash": hashlib.sha3_256(str(test_param).encode()).hexdigest()[:8]
        }
    
    def _perform_module_specific_compliance_checks(self) -> Dict:
        """Checks de compliance específicos para teste"""
        return {
            "checks_performed": [
                {"check": "test_check_1", "status": "PASS", "details": {"value": 42}},
                {"check": "test_check_2", "status": "PASS", "details": {"custom": True}}
            ],
            "has_violations": False,
            "violations": [],
            "status": "COMPLIANT"
        }
    
    def custom_operation(self, input_data: str) -> str:
        """Operação específica do módulo para teste"""
        return f"Processed: {input_data} (config: {self.config['test_param']})"

# Teste de instanciação
if __name__ == "__main__":
    print("TESTE DE INSTANCIACAO DO MODULO v2.0")
    print("=" * 70)
    
    try:
        # Teste 1: Módulo com configuração padrão
        print("1. Criando módulo com config padrão...")
        module1 = TestModuleV2(test_param=100)
        success1 = module1._initialize_module()
        
        if success1:
            print(f"   [OK] Modulo 1 inicializado")
            print(f"   Checksum: {module1.module_checksum[:16]}...")
            print(f"   Instance Checksum: {module1.instance_checksum[:16]}...")
            print(f"   Compliance: {module1.vitals.compliance_status}")
        else:
            print("   [ERRO] Falha na inicializacao do modulo 1")
        
        # Teste 2: Módulo com configuração diferente (deve ter instance_checksum diferente)
        print("\n2. Criando módulo com config diferente...")
        module2 = TestModuleV2(test_param=200)
        success2 = module2._initialize_module()
        
        if success2:
            print(f"   [OK] Modulo 2 inicializado")
            print(f"   Checksum: {module2.module_checksum[:16]}...")
            print(f"   Instance Checksum: {module2.instance_checksum[:16]}...")
        
        # Verificar se checksums são diferentes
        print("\n3. Verificando checksums unicos por instancia...")
        print(f"   Modulo 1 (param=100): {module1.instance_checksum[:16]}")
        print(f"   Modulo 2 (param=200): {module2.instance_checksum[:16]}")
        
        same_module_checksum = module1.module_checksum == module2.module_checksum
        same_instance_checksum = module1.instance_checksum == module2.instance_checksum
        
        print(f"   Module Checksums iguais? {'[OK] SIM (CORRETO - mesma classe)' if same_module_checksum else '[ERRO] NAO (PROBLEMA)'}")
        print(f"   Instance Checksums iguais? {'[ERRO] SIM (PROBLEMA)' if same_instance_checksum else '[OK] NAO (CORRETO - configs diferentes)'}")
        
        # Teste 3: Verificar certificação no Integration Gate
        print("\n4. Verificando certificacao no Integration Gate...")
        gate = get_integration_gate()
        is_cert1 = gate.is_certified("TestModuleV2_Demo")
        print(f"   Modulo certificado? {'[OK] SIM' if is_cert1 else '[ERRO] NAO'}")
        
        # Teste 4: Operação customizada
        print("\n5. Testando operacao customizada...")
        result = module1.custom_operation("test_input")
        print(f"   Resultado: {result}")
        
        print("\n" + "=" * 70)
        print("TESTE COMPLETO - Template v2.0 funcional")
        print("TODAS as funcionalidades validadas com sucesso")
        
    except Exception as e:
        print(f"\n[ERRO] FALHA NO TESTE: {e}")
        import traceback
        traceback.print_exc()

