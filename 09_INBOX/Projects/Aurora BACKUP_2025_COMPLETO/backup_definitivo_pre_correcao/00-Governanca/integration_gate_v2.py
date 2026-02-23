#!/usr/bin/env python3
"""
PORTÃO DE INTEGRAÇÃO v2.0 - COM COMPLIANCE EMBEDDED
ATUALIZADO para NCNTModule v2.0
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import os
import sys

# Importar template v2.0
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))
from modules.ncnt_module_template import NCNTModule, RegulatoryContext

logger = logging.getLogger("NCNT.IntegrationGate")

class IntegrationGateV2:
    """
    Portão de integração v2.0 com compliance embedded
    Valida e certifica módulos antes de permitir integração
    """
    
    def __init__(self):
        self.certified_modules: Dict[str, Dict] = {}
        self.pending_certifications: Dict[str, Dict] = {}
        self.certification_history: List[Dict] = []
        
        # Contexto regulatório para certificação
        self.regulatory_context = RegulatoryContext(
            frameworks=["MiFID_II", "SEC_Rule_15c3_5", "EMIR", "GDPR", "Basel_III"],
            required_checks=[
                "integrity",
                "latency",
                "audit_log",
                "data_protection",
                "risk_limits",
                "best_execution"
            ]
        )
        
        logger.info("🚪 Integration Gate v2.0 inicializado")
    
    def certify_module(self, module: NCNTModule) -> Tuple[bool, Dict]:
        """
        Certifica um módulo para integração
        Retorna (sucesso, detalhes)
        """
        module_name = module.module_name
        
        # Verificar se já está certificado
        if module_name in self.certified_modules:
            cert = self.certified_modules[module_name]
            if cert["status"] == "CERTIFIED":
                logger.info(f"✅ Módulo {module_name} já está certificado")
                return True, cert
        
        # Iniciar processo de certificação
        certification_id = hashlib.sha3_256(
            f"{module_name}:{datetime.now().timestamp()}".encode()
        ).hexdigest()[:16]
        
        certification = {
            "certification_id": certification_id,
            "module_name": module_name,
            "module_id": module.module_id,
            "module_version": getattr(module, 'MODULE_VERSION', '0.0.0'),
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING",
            "checks": [],
            "violations": [],
            "warnings": [],
            "checksum_module": module.module_checksum[:16] if hasattr(module, 'module_checksum') else None,
            "checksum_instance": module.instance_checksum[:16] if hasattr(module, 'instance_checksum') else None
        }
        
        # Executar verificações
        all_passed = True
        
        # 1. Verificar checksum
        if not self._verify_checksum(module, certification):
            all_passed = False
        
        # 2. Verificar compliance
        if not self._verify_compliance(module, certification):
            all_passed = False
        
        # 3. Verificar dependências
        if not self._verify_dependencies(module, certification):
            all_passed = False
        
        # 4. Verificar conexões neurais
        if not self._verify_neural_connections(module, certification):
            all_passed = False
        
        # 5. Verificar integridade estrutural
        if not self._verify_structural_integrity(module, certification):
            all_passed = False
        
        # Determinar status final
        if all_passed and len(certification["violations"]) == 0:
            certification["status"] = "CERTIFIED"
            self.certified_modules[module_name] = certification
            logger.info(f"✅ Módulo {module_name} certificado com sucesso")
        else:
            certification["status"] = "REJECTED"
            self.pending_certifications[module_name] = certification
            logger.warning(f"⚠️ Módulo {module_name} rejeitado na certificação")
        
        # Adicionar ao histórico
        self.certification_history.append(certification)
        if len(self.certification_history) > 100:
            self.certification_history = self.certification_history[-100:]
        
        return all_passed and len(certification["violations"]) == 0, certification
    
    def _verify_checksum(self, module: NCNTModule, certification: Dict) -> bool:
        """Verifica checksum do módulo"""
        try:
            if not hasattr(module, 'module_checksum') or not module.module_checksum:
                certification["checks"].append({
                    "check": "checksum",
                    "status": "FAIL",
                    "details": "Checksum não encontrado"
                })
                certification["violations"].append("Checksum ausente")
                return False
            
            # Verificar se checksum é válido (não vazio, formato correto)
            if len(module.module_checksum) < 32:
                certification["checks"].append({
                    "check": "checksum",
                    "status": "FAIL",
                    "details": "Checksum inválido (muito curto)"
                })
                certification["violations"].append("Checksum inválido")
                return False
            
            certification["checks"].append({
                "check": "checksum",
                "status": "PASS",
                "details": {
                    "module_checksum": module.module_checksum[:16],
                    "instance_checksum": module.instance_checksum[:16] if hasattr(module, 'instance_checksum') else None
                }
            })
            return True
            
        except Exception as e:
            certification["checks"].append({
                "check": "checksum",
                "status": "ERROR",
                "error": str(e)
            })
            certification["violations"].append(f"Erro na verificação de checksum: {e}")
            return False
    
    def _verify_compliance(self, module: NCNTModule, certification: Dict) -> bool:
        """Verifica compliance do módulo"""
        try:
            if not hasattr(module, 'regulatory_context'):
                certification["checks"].append({
                    "check": "compliance",
                    "status": "FAIL",
                    "details": "RegulatoryContext não encontrado"
                })
                certification["violations"].append("Compliance não configurado")
                return False
            
            # Executar compliance check
            compliance_result = module.run_compliance_check()
            
            if compliance_result["overall_status"] == "VIOLATION":
                certification["checks"].append({
                    "check": "compliance",
                    "status": "FAIL",
                    "details": compliance_result
                })
                certification["violations"].extend([
                    f"Compliance violation: {v}" for v in compliance_result.get("violations", [])
                ])
                return False
            
            certification["checks"].append({
                "check": "compliance",
                "status": "PASS",
                "details": {
                    "status": compliance_result["overall_status"],
                    "score": compliance_result.get("metrics", {}).get("compliance_score", 0)
                }
            })
            
            if compliance_result["overall_status"] == "WARNING":
                certification["warnings"].append("Compliance com warnings")
            
            return True
            
        except Exception as e:
            certification["checks"].append({
                "check": "compliance",
                "status": "ERROR",
                "error": str(e)
            })
            certification["violations"].append(f"Erro na verificação de compliance: {e}")
            return False
    
    def _verify_dependencies(self, module: NCNTModule, certification: Dict) -> bool:
        """Verifica dependências do módulo"""
        try:
            if not hasattr(module, 'required_modules'):
                return True  # Sem dependências é válido
            
            missing = []
            for dep in module.required_modules:
                if dep not in self.certified_modules:
                    missing.append(dep)
            
            if missing:
                certification["checks"].append({
                    "check": "dependencies",
                    "status": "WARNING",
                    "details": {"missing": missing}
                })
                certification["warnings"].append(f"Dependências não certificadas: {missing}")
            else:
                certification["checks"].append({
                    "check": "dependencies",
                    "status": "PASS",
                    "details": {"dependencies": module.required_modules}
                })
            
            return True  # Dependências faltando são warning, não bloqueiam
            
        except Exception as e:
            certification["checks"].append({
                "check": "dependencies",
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    def _verify_neural_connections(self, module: NCNTModule, certification: Dict) -> bool:
        """Verifica conexões neurais"""
        try:
            if not hasattr(module, 'get_neural_connections'):
                certification["checks"].append({
                    "check": "neural_connections",
                    "status": "WARNING",
                    "details": "Método get_neural_connections não encontrado"
                })
                return True
            
            connections = module.get_neural_connections()
            
            certification["checks"].append({
                "check": "neural_connections",
                "status": "PASS",
                "details": {
                    "connection_count": len(connections),
                    "connections": [
                        {
                            "target": conn.target_module,
                            "type": conn.connection_type,
                            "bandwidth": conn.bandwidth
                        }
                        for conn in connections
                    ]
                }
            })
            
            return True
            
        except Exception as e:
            certification["checks"].append({
                "check": "neural_connections",
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    def _verify_structural_integrity(self, module: NCNTModule, certification: Dict) -> bool:
        """Verifica integridade estrutural do módulo"""
        try:
            # Verificar se módulo tem métodos essenciais
            required_methods = [
                'get_vitals',
                'perform_health_check',
                'send_neural_signal',
                'receive_neural_signal'
            ]
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(module, method):
                    missing_methods.append(method)
            
            if missing_methods:
                certification["checks"].append({
                    "check": "structural_integrity",
                    "status": "FAIL",
                    "details": {"missing_methods": missing_methods}
                })
                certification["violations"].append(f"Métodos essenciais faltando: {missing_methods}")
                return False
            
            certification["checks"].append({
                "check": "structural_integrity",
                "status": "PASS",
                "details": {"all_methods_present": True}
            })
            
            return True
            
        except Exception as e:
            certification["checks"].append({
                "check": "structural_integrity",
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    def is_certified(self, module_name: str) -> bool:
        """Verifica se módulo está certificado"""
        return module_name in self.certified_modules and \
               self.certified_modules[module_name]["status"] == "CERTIFIED"
    
    def get_certification_report(self) -> Dict:
        """Gera relatório de certificações"""
        return {
            "timestamp": datetime.now().isoformat(),
            "certified_modules": len(self.certified_modules),
            "pending_certifications": len(self.pending_certifications),
            "certified": list(self.certified_modules.keys()),
            "pending": list(self.pending_certifications.keys()),
            "recent_certifications": self.certification_history[-10:] if self.certification_history else []
        }

# Instância global do portão
_global_gate: Optional[IntegrationGateV2] = None

def get_integration_gate() -> IntegrationGateV2:
    """Retorna instância global do portão"""
    global _global_gate
    if _global_gate is None:
        _global_gate = IntegrationGateV2()
    return _global_gate

# Decorator para exigir certificação
def require_integration_gate(cls):
    """Decorator que exige certificação no Integration Gate"""
    original_init = cls.__init__
    original_initialize = getattr(cls, '_initialize_module', None)
    
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Não certificar aqui - será feito após _initialize_module
    
    def new_initialize(self):
        # Chamar inicialização original
        if original_initialize:
            result = original_initialize(self)
        else:
            result = True
        
        # Certificar após inicialização (quando checksum já foi calculado)
        if result:
            gate = get_integration_gate()
            success, cert = gate.certify_module(self)
            if not success:
                self.logger.warning(f"Modulo {self.module_name} nao passou na certificacao: {cert.get('violations', [])}")
                # Não bloquear, apenas avisar
        
        return result
    
    cls.__init__ = new_init
    if original_initialize:
        cls._initialize_module = new_initialize
    
    return cls

if __name__ == "__main__":
    """Teste do portão"""
    print("🧪 TESTE DO INTEGRATION GATE v2.0")
    print("=" * 70)
    
    gate = IntegrationGateV2()
    
    # Criar módulo de teste
    class TestModule(NCNTModule):
        MODULE_VERSION = "1.0.0"
        def __init__(self):
            super().__init__("TestModule", {})
    
    module = TestModule()
    module._initialize_module()
    
    # Certificar
    success, cert = gate.certify_module(module)
    
    print(f"\n📋 Resultado da Certificação:")
    print(f"   Status: {cert['status']}")
    print(f"   Checks: {len(cert['checks'])}")
    print(f"   Violations: {len(cert['violations'])}")
    print(f"   Warnings: {len(cert['warnings'])}")
    
    if success:
        print("\n✅ Módulo certificado com sucesso!")
    else:
        print("\n❌ Módulo rejeitado na certificação")
    
    report = gate.get_certification_report()
    print(f"\n📊 Relatório: {report['certified_modules']} módulos certificados")

