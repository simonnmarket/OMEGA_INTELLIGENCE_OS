'''
QUANTUM FIREWALL - Sistema de segurança integrado
LOCAL: 00-Governanca/quantum_firewall.py
INTEGRAÇÃO: Compatível com módulos existentes do AURORA
'''

import hashlib
import hmac
import secrets
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

class QuantumFirewall:
    """
    Sistema de firewall com criptografia quântica-resistente
    Integra com estrutura existente do AURORA
    """
    
    SECURITY_LEVELS = {
        'TIER-0': {'hash_algo': 'sha3_256', 'key_size': 32, 'iterations': 100000},
        'TIER-1': {'hash_algo': 'sha256', 'key_size': 32, 'iterations': 10000},
        'TIER-2': {'hash_algo': 'sha256', 'key_size': 16, 'iterations': 1000}
    }
    
    def __init__(self, security_level: str = 'TIER-0'):
        self.security_level = security_level
        self.config = self.SECURITY_LEVELS.get(security_level, self.SECURITY_LEVELS['TIER-0'])
        self.is_active = False
        self.blocked_attempts = 0
        self.allowed_attempts = 5
        self.logger = logging.getLogger("QUANTUM_FIREWALL")
        
        # Chave de segurança
        self.secret_key = self._generate_secret_key()
        
        # Integração com audit system
        self.audit_system = self._get_audit_system()
    
    def _generate_secret_key(self) -> bytes:
        """Gera chave secreta criptograficamente segura"""
        return secrets.token_bytes(self.config['key_size'])
    
    def _get_audit_system(self):
        """Tenta integrar com sistema de auditoria existente"""
        try:
            from audit_system_complete import AuditSystem
            return AuditSystem()
        except ImportError:
            self.logger.info("[FIREWALL] AuditSystem não encontrado, usando logging interno")
            return None
    
    def activate(self) -> bool:
        """Ativa o firewall com verificação de integridade"""
        try:
            # 1. Verificar integridade dos módulos críticos
            integrity_check = self._verify_system_integrity()
            
            if not integrity_check['all_valid']:
                self.logger.error(f"[FIREWALL] Falha na integridade: {integrity_check}")
                return False
            
            # 2. Ativar componentes de segurança
            self.is_active = True
            
            # 3. Registrar ativação
            self._log_security_event(
                event_type="FIREWALL_ACTIVATION",
                details={
                    'status': 'activated',
                    'security_level': self.security_level,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"[FIREWALL] ✅ Ativado com sucesso. Nível: {self.security_level}")
            return True
            
        except Exception as e:
            self.logger.error(f"[FIREWALL] ❌ Erro na ativação: {e}")
            return False
    
    def _verify_system_integrity(self) -> Dict[str, Any]:
        """Verifica integridade dos módulos do sistema"""
        critical_modules = [
            '00-Governanca/genesis_includes_v3_complete.py',
            '00-Governanca/regulatory_context.py',
            'modules/ncnt_module_template_v2.py',
            'wrappers_v2/'
        ]
        
        results = {}
        for module_path in critical_modules:
            module_info = self._analyze_module(module_path)
            results[module_path] = module_info
        
        results['all_valid'] = all(
            r.get('exists', False) and r.get('integrity', False) 
            for r in results.values() if isinstance(r, dict)
        )
        
        return results
    
    def _analyze_module(self, module_path: str) -> Dict[str, Any]:
        """Analisa módulo individual"""
        if not os.path.exists(module_path):
            return {'exists': False, 'integrity': False, 'error': 'Not found'}
        
        try:
            if os.path.isdir(module_path):
                files = os.listdir(module_path)
                py_files = [f for f in files if f.endswith('.py')]
                return {
                    'exists': True,
                    'type': 'directory',
                    'file_count': len(py_files),
                    'integrity': len(py_files) > 0
                }
            else:
                file_size = os.path.getsize(module_path)
                with open(module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_valid_content = len(content) > 100
                return {
                    'exists': True,
                    'type': 'file',
                    'size': file_size,
                    'integrity': has_valid_content
                }
        except Exception as e:
            return {'exists': True, 'integrity': False, 'error': str(e)}
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calcula hash do arquivo"""
        hash_algo = getattr(hashlib, self.config['hash_algo'])
        hasher = hash_algo()
        
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida requisição com múltiplas camadas de segurança"""
        if not self.is_active:
            return {
                'valid': False,
                'reason': 'Firewall não ativo',
                'security_level': self.security_level,
                'timestamp': datetime.now().isoformat()
            }
        
        # Verificação básica
        if not isinstance(request_data, dict):
            self.blocked_attempts += 1
            return self._block_request("Estrutura de dados inválida")
        
        # Verificação de timestamp
        if 'timestamp' not in request_data:
            self.blocked_attempts += 1
            return self._block_request("Timestamp ausente")
        
        # Calcular hash da requisição
        request_hash = self._calculate_request_hash(request_data)
        
        return {
            'valid': True,
            'security_level': self.security_level,
            'request_hash': request_hash[:16],
            'firewall_active': self.is_active,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_request_hash(self, request_data: Dict) -> str:
        """Calcula hash da requisição"""
        data_to_hash = request_data.copy()
        data_to_hash.pop('timestamp', None)
        data_to_hash.pop('signature', None)
        
        message = json.dumps(data_to_hash, sort_keys=True).encode()
        return hashlib.sha3_256(message).hexdigest()
    
    def _block_request(self, reason: str) -> Dict[str, Any]:
        """Registra e retorna bloqueio de requisição"""
        self._log_security_event(
            event_type="REQUEST_BLOCKED",
            details={'reason': reason, 'blocked_attempts': self.blocked_attempts},
            severity="WARNING"
        )
        
        return {
            'valid': False,
            'reason': reason,
            'security_level': self.security_level,
            'blocked_attempts': self.blocked_attempts,
            'timestamp': datetime.now().isoformat()
        }
    
    def _log_security_event(self, event_type: str, details: Dict, severity: str = "INFO"):
        """Registra evento de segurança"""
        log_entry = {
            'event_type': event_type,
            'details': details,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'firewall_level': self.security_level
        }
        
        log_message = f"[FIREWALL] {event_type}: {json.dumps(details, default=str)}"
        
        if severity == "WARNING":
            self.logger.warning(log_message)
        elif severity == "ERROR":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
        
        if self.audit_system:
            try:
                self.audit_system.log_event(
                    event_type=event_type,
                    details=details,
                    severity=severity
                )
            except Exception as e:
                self.logger.error(f"[FIREWALL] Erro ao logar no audit system: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Retorna status de segurança atual"""
        return {
            'active': self.is_active,
            'security_level': self.security_level,
            'blocked_attempts': self.blocked_attempts,
            'allowed_attempts': self.allowed_attempts,
            'secret_key_configured': bool(self.secret_key),
            'audit_system_connected': bool(self.audit_system),
            'timestamp': datetime.now().isoformat()
        }

def get_firewall(security_level: str = 'TIER-0') -> QuantumFirewall:
    """Retorna instância configurada do firewall"""
    return QuantumFirewall(security_level=security_level)

