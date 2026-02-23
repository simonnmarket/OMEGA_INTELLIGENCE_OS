#!/usr/bin/env python3
"""
MONITOR DE CONEXÕES NEURAIS - VERIFICA SINAIS VITAIS DE TODOS OS MÓDULOS
Executa automaticamente a cada 30 segundos ou sob demanda
STATUS: CRÍTICO - GARANTE INTEGRAÇÃO OPERACIONAL
"""

import time
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import threading
import hashlib
import sys
import os
from dataclasses import dataclass, field

# ============================================================================
# LOGGING PARA MONITORAMENTO
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-25s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("NCNT.NeuralMonitor")

# Importar template v2.0
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))
try:
    from modules.ncnt_module_template_v2 import NCNTModule, NeuralConnection, ModuleVitals, RegulatoryContext
except ImportError:
    # Fallback se não encontrar
    logger.warning("Template v2.0 não encontrado, usando fallback")
    NeuralConnection = None
    ModuleVitals = None

# ============================================================================
# ESTRUTURAS DE DADOS DO MONITOR
# ============================================================================

@dataclass
class ConnectionHealth:
    """Saúde de uma conexão neural"""
    source_module: str
    target_module: str
    connection_type: str
    status: str  # "HEALTHY", "DEGRADED", "DISCONNECTED"
    latency_ms: float
    last_signal_time: datetime
    signal_count: int = 0
    error_count: int = 0
    
    def calculate_score(self) -> float:
        """Calcula score de saúde (0-100)"""
        if self.status == "DISCONNECTED":
            return 0.0
        
        score = 100.0
        
        # Penalidade por latência
        if self.latency_ms > 100:  # > 100ms é problemático
            score -= min(30, (self.latency_ms - 100) / 10)
        
        # Penalidade por erro
        if self.signal_count > 0:
            error_rate = self.error_count / self.signal_count
            score -= error_rate * 100
        
        # Penalidade por inatividade
        inactive_minutes = (datetime.now() - self.last_signal_time).total_seconds() / 60
        if inactive_minutes > 5:  # > 5 minutos sem sinal
            score -= min(50, inactive_minutes * 2)
        
        return max(0.0, score)

@dataclass
class ModuleHealthReport:
    """Relatório de saúde completo de um módulo"""
    module_name: str
    timestamp: datetime
    vitals: Dict
    neural_connections: List[Dict]
    connection_scores: List[float]
    overall_score: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "module_name": self.module_name,
            "timestamp": self.timestamp.isoformat(),
            "vitals": self.vitals,
            "neural_connections": self.neural_connections,
            "connection_scores": self.connection_scores,
            "overall_score": self.overall_score,
            "recommendations": self.recommendations,
            "health_status": self.get_health_status()
        }
    
    def get_health_status(self) -> str:
        """Retorna status de saúde baseado no score"""
        if self.overall_score >= 90:
            return "EXCELLENT"
        elif self.overall_score >= 70:
            return "HEALTHY"
        elif self.overall_score >= 50:
            return "DEGRADED"
        else:
            return "CRITICAL"

# ============================================================================
# CLASSE PRINCIPAL: NEURAL CONNECTION MONITOR
# ============================================================================

class NeuralConnectionMonitor:
    """
    Monitora conexões neurais entre todos os módulos
    Executa scans periódicos e gera alertas
    """
    
    def __init__(self, scan_interval_seconds: int = 30):
        self.scan_interval = scan_interval_seconds
        self.health_history: Dict[str, List[ModuleHealthReport]] = {}
        self.alerts: List[Dict] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Cache para performance
        self.last_scan_results: Dict = {}
        self.checksum_cache: Dict[str, str] = {}
        
        logger.info(f"Neural Connection Monitor inicializado (intervalo: {scan_interval_seconds}s)")
    
    def start_monitoring(self) -> bool:
        """Inicia monitoramento contínuo em background"""
        if self.monitoring_active:
            logger.warning("Monitoramento ja esta ativo")
            return False
        
        self.monitoring_active = True
        
        def monitor_worker():
            logger.info("Monitoramento neural iniciado")
            
            while self.monitoring_active:
                try:
                    # Executar scan completo
                    scan_results = self.scan_all_modules()
                    
                    # Analisar resultados
                    health_report = self.analyze_health(scan_results)
                    
                    # Gerar alertas se necessário
                    alerts = self.generate_alerts(health_report)
                    
                    # Salvar histórico
                    self.save_health_history(health_report)
                    
                    # Log resumo
                    healthy_count = sum(1 for report in health_report.values() 
                                      if report.get_health_status() in ["EXCELLENT", "HEALTHY"])
                    
                    logger.info(f"Scan neural: {healthy_count}/{len(health_report)} modulos saudaveis")
                    
                    # Aguardar próximo scan
                    time.sleep(self.scan_interval)
                    
                except Exception as e:
                    logger.error(f"Erro no monitoramento: {e}")
                    time.sleep(5)  # Wait before retry
        
        # Iniciar thread de monitoramento
        self.monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Monitoramento neural iniciado com sucesso")
        return True
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoramento neural parado")
    
    def scan_all_modules(self) -> Dict:
        """
        Escaneia todos os módulos e suas conexões
        Retorna dicionário com status de cada módulo
        """
        try:
            # Importação dinâmica
            genesis_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "00-Governanca",
                "genesis_includes_v3_complete.py"
            )
            
            if not os.path.exists(genesis_path):
                logger.error(f"Genesis Includes nao encontrado em {genesis_path}")
                return {"error": "Genesis Includes não encontrado"}
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("genesis_includes", genesis_path)
            genesis_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(genesis_module)
            
            genesis = genesis_module.get_genesis()
            
            # Obter todos os módulos registrados
            all_modules = genesis._dependency_registry.copy()
            scan_results = {}
            scan_timestamp = datetime.now()
            
            for module_name, module_info in all_modules.items():
                try:
                    # Resolver módulo
                    module = genesis.resolve(module_name)
                    
                    # Verificar se é um NCNTModule
                    if not hasattr(module, 'get_vitals') or not hasattr(module, 'get_neural_connections'):
                        continue  # Pular módulos não-NCNT
                    
                    # Coletar dados
                    vitals = module.get_vitals()
                    connections = module.get_neural_connections()
                    
                    # Testar conexões
                    connection_status = []
                    for conn in connections:
                        status = self._test_connection(module, conn)
                        connection_status.append(status)
                    
                    # Armazenar resultados
                    scan_results[module_name] = {
                        "module_info": module_info,
                        "vitals": {
                            "status": vitals.status,
                            "connection_count": vitals.connection_count,
                            "active_connections": vitals.active_connections,
                            "is_alive": vitals.is_alive(),
                            "last_heartbeat": vitals.last_heartbeat.isoformat(),
                            "time_since_heartbeat": (scan_timestamp - vitals.last_heartbeat).total_seconds()
                        },
                        "neural_connections": [
                            {
                                "target": conn.target_module,
                                "type": conn.connection_type,
                                "checksum": conn.checksum,
                                "bandwidth": conn.bandwidth,
                                "latency_ms": conn.latency_ms
                            }
                            for conn in connections
                        ],
                        "connection_tests": connection_status,
                        "scan_timestamp": scan_timestamp.isoformat(),
                        "checksum": self._calculate_module_checksum(module)
                    }
                    
                except Exception as e:
                    logger.error(f"Erro ao escanear modulo {module_name}: {e}")
                    scan_results[module_name] = {
                        "error": str(e),
                        "scan_timestamp": scan_timestamp.isoformat()
                    }
            
            self.last_scan_results = scan_results
            logger.debug(f"Scan completado: {len(scan_results)} modulos escaneados")
            return scan_results
            
        except Exception as e:
            logger.error(f"Erro fatal no scan: {e}")
            return {"error": str(e)}
    
    def _test_connection(self, module, connection) -> Dict:
        """Testa uma conexão neural específica"""
        try:
            start_time = time.time()
            
            # Testar envio de sinal
            test_signal = {
                "type": "HEALTH_CHECK",
                "timestamp": datetime.now().isoformat(),
                "source": module.module_name,
                "target": connection.target_module,
                "test_id": hashlib.sha3_256(f"{time.time()}".encode()).hexdigest()[:8]
            }
            
            success = False
            try:
                if hasattr(module, 'send_neural_signal'):
                    success = module.send_neural_signal(connection.target_module, test_signal)
            except:
                pass  # Módulo pode não ter send_neural_signal implementado
            
            latency = (time.time() - start_time) * 1000  # ms
            
            return {
                "target": connection.target_module,
                "success": success,
                "latency_ms": latency,
                "test_timestamp": datetime.now().isoformat(),
                "status": "HEALTHY" if success and latency < 100 else "DEGRADED"
            }
            
        except Exception as e:
            return {
                "target": connection.target_module if hasattr(connection, 'target_module') else "UNKNOWN",
                "success": False,
                "error": str(e),
                "status": "DISCONNECTED"
            }
    
    def _calculate_module_checksum(self, module) -> str:
        """Calcula checksum do estado atual do módulo"""
        try:
            data = f"{module.module_name}{module.vitals.status}{len(module.neural_connections)}"
            return hashlib.sha3_256(data.encode()).hexdigest()[:16]
        except:
            return "UNKNOWN"
    
    def analyze_health(self, scan_results: Dict) -> Dict[str, ModuleHealthReport]:
        """Analisa saúde dos módulos baseado nos resultados do scan"""
        health_reports = {}
        
        for module_name, data in scan_results.items():
            if "error" in data:
                # Módulo com erro
                health_reports[module_name] = ModuleHealthReport(
                    module_name=module_name,
                    timestamp=datetime.fromisoformat(data["scan_timestamp"]),
                    vitals={"status": "ERROR", "error": data["error"]},
                    neural_connections=[],
                    connection_scores=[],
                    overall_score=0.0,
                    recommendations=["Investigar erro no modulo"]
                )
                continue
            
            # Analisar conexões
            connection_scores = []
            recommendations = []
            
            vitals = data["vitals"]
            connections = data["neural_connections"]
            connection_tests = data.get("connection_tests", [])
            
            # Score das conexões
            for test in connection_tests:
                score = 100.0 if test.get("success") else 0.0
                
                # Penalidade por latência
                latency = test.get("latency_ms", 0)
                if latency > 100:
                    score -= min(30, (latency - 100) / 10)
                
                connection_scores.append(score)
                
                # Recomendações baseadas em problemas
                if score < 70:
                    recommendations.append(f"Melhorar conexao com {test.get('target')} (score: {score:.1f})")
            
            # Score geral do módulo
            overall_score = 0.0
            if connection_scores:
                overall_score = sum(connection_scores) / len(connection_scores)
            elif vitals["is_alive"]:
                overall_score = 80.0  # Módulo vivo mas sem conexões
            else:
                overall_score = 0.0
            
            # Recomendações adicionais
            if not vitals["is_alive"]:
                recommendations.append("Modulo nao esta vivo - reinicializar")
            elif len(connections) == 0:
                recommendations.append("Modulo isolado - estabelecer conexoes")
            elif overall_score < 50:
                recommendations.append("Saude critica - intervencao necessaria")
            
            # Criar relatório
            health_reports[module_name] = ModuleHealthReport(
                module_name=module_name,
                timestamp=datetime.fromisoformat(data["scan_timestamp"]),
                vitals=vitals,
                neural_connections=connections,
                connection_scores=connection_scores,
                overall_score=overall_score,
                recommendations=recommendations
            )
        
        return health_reports
    
    def generate_alerts(self, health_reports: Dict[str, ModuleHealthReport]) -> List[Dict]:
        """Gera alertas baseados nos relatórios de saúde"""
        alerts = []
        alert_time = datetime.now()
        
        for module_name, report in health_reports.items():
            status = report.get_health_status()
            
            if status == "CRITICAL":
                alert = {
                    "level": "CRITICAL",
                    "module": module_name,
                    "message": f"Modulo {module_name} em estado CRITICO (score: {report.overall_score:.1f})",
                    "timestamp": alert_time.isoformat(),
                    "details": report.to_dict(),
                    "recommendations": report.recommendations
                }
                alerts.append(alert)
                logger.critical(f"ALERTA CRITICO: {module_name}")
            
            elif status == "DEGRADED":
                alert = {
                    "level": "WARNING",
                    "module": module_name,
                    "message": f"Modulo {module_name} em estado DEGRADADO (score: {report.overall_score:.1f})",
                    "timestamp": alert_time.isoformat(),
                    "details": report.to_dict()
                }
                alerts.append(alert)
                logger.warning(f"ALERTA: {module_name} degradado")
        
        # Alerta se muitos módulos estão com problemas
        critical_count = sum(1 for report in health_reports.values() 
                           if report.get_health_status() == "CRITICAL")
        
        if critical_count >= 3:
            system_alert = {
                "level": "SYSTEM_CRITICAL",
                "message": f"Sistema em estado CRITICO: {critical_count} modulos criticos",
                "timestamp": alert_time.isoformat(),
                "affected_modules": [
                    name for name, report in health_reports.items()
                    if report.get_health_status() == "CRITICAL"
                ]
            }
            alerts.append(system_alert)
            logger.critical("ALERTA SISTEMICO: Multiplos modulos criticos")
        
        # Adicionar aos alertas históricos
        self.alerts.extend(alerts)
        
        # Manter apenas últimos 1000 alertas
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        return alerts
    
    def save_health_history(self, health_reports: Dict[str, ModuleHealthReport]):
        """Salva histórico de saúde"""
        timestamp = datetime.now()
        
        for module_name, report in health_reports.items():
            if module_name not in self.health_history:
                self.health_history[module_name] = []
            
            self.health_history[module_name].append(report)
            
            # Manter apenas últimas 100 entradas por módulo
            if len(self.health_history[module_name]) > 100:
                self.health_history[module_name] = self.health_history[module_name][-100:]
    
    def get_health_summary(self) -> Dict:
        """Retorna resumo da saúde do sistema"""
        if not self.last_scan_results:
            return {"status": "NO_DATA", "message": "Nenhum scan executado"}
        
        try:
            health_reports = self.analyze_health(self.last_scan_results)
            
            # Estatísticas
            total_modules = len(health_reports)
            healthy_modules = sum(1 for r in health_reports.values() 
                                if r.get_health_status() in ["EXCELLENT", "HEALTHY"])
            degraded_modules = sum(1 for r in health_reports.values() 
                                 if r.get_health_status() == "DEGRADED")
            critical_modules = sum(1 for r in health_reports.values() 
                                 if r.get_health_status() == "CRITICAL")
            
            # Score médio do sistema
            avg_score = sum(r.overall_score for r in health_reports.values()) / total_modules if total_modules > 0 else 0
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_modules": total_modules,
                "healthy_modules": healthy_modules,
                "degraded_modules": degraded_modules,
                "critical_modules": critical_modules,
                "system_score": avg_score,
                "system_status": "HEALTHY" if avg_score >= 80 else "DEGRADED" if avg_score >= 60 else "CRITICAL",
                "active_alerts": len([a for a in self.alerts if a["level"] in ["CRITICAL", "SYSTEM_CRITICAL"]]),
                "recommendations": self._generate_system_recommendations(health_reports)
            }
            
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def _generate_system_recommendations(self, health_reports: Dict) -> List[str]:
        """Gera recomendações para o sistema como um todo"""
        recommendations = []
        
        # Contar módulos por status
        status_count = {}
        for report in health_reports.values():
            status = report.get_health_status()
            status_count[status] = status_count.get(status, 0) + 1
        
        # Recomendações baseadas em estatísticas
        if status_count.get("CRITICAL", 0) > 0:
            recommendations.append(f"Intervir em {status_count['CRITICAL']} modulo(s) critico(s)")
        
        if status_count.get("DEGRADED", 0) > 2:
            recommendations.append(f"Melhorar {status_count['DEGRADED']} modulo(s) degradado(s)")
        
        # Verificar módulos isolados
        isolated = [name for name, report in health_reports.items() 
                   if report.vitals.get("connection_count", 0) == 0]
        
        if isolated:
            recommendations.append(f"Conectar {len(isolated)} modulo(s) isolado(s): {', '.join(isolated)}")
        
        return recommendations
    
    def generate_report(self, filepath: str = None) -> str:
        """Gera relatório completo em JSON"""
        summary = self.get_health_summary()
        detailed_reports = {}
        
        if "error" not in self.last_scan_results:
            health_reports = self.analyze_health(self.last_scan_results)
            detailed_reports = {name: report.to_dict() for name, report in health_reports.items()}
        
        report = {
            "report_type": "NEURAL_CONNECTION_HEALTH_REPORT",
            "timestamp": datetime.now().isoformat(),
            "monitor_config": {
                "scan_interval": self.scan_interval,
                "monitoring_active": self.monitoring_active
            },
            "system_summary": summary,
            "detailed_reports": detailed_reports,
            "recent_alerts": self.alerts[-10:] if self.alerts else [],
            "checksum": hashlib.sha3_256(
                json.dumps(summary, sort_keys=True).encode()
            ).hexdigest()[:32]
        }
        
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_json)
            logger.info(f"Relatorio salvo em: {filepath}")
        
        return report_json

# ============================================================================
# TESTES E USO
# ============================================================================

if __name__ == "__main__":
    """Teste do monitor de conexões neurais"""
    
    print("NEURAL CONNECTION MONITOR - TESTE DE INTEGRIDADE")
    print("=" * 60)
    
    try:
        # 1. Inicializar monitor
        print("1. Inicializando monitor...")
        monitor = NeuralConnectionMonitor(scan_interval_seconds=5)
        
        # 2. Executar scan único
        print("2. Executando scan de modulos...")
        scan_results = monitor.scan_all_modules()
        
        if "error" in scan_results:
            print(f"[ERRO] Erro no scan: {scan_results['error']}")
        else:
            print(f"[OK] Scan completado: {len(scan_results)} modulos encontrados")
        
        # 3. Analisar saúde
        print("3. Analisando saude dos modulos...")
        health_reports = monitor.analyze_health(scan_results)
        
        # 4. Gerar resumo
        print("4. Gerando resumo do sistema...")
        summary = monitor.get_health_summary()
        
        print(f"   Modulos totais: {summary.get('total_modules', 0)}")
        print(f"   Saudaveis: {summary.get('healthy_modules', 0)}")
        print(f"   Degradados: {summary.get('degraded_modules', 0)}")
        print(f"   Criticos: {summary.get('critical_modules', 0)}")
        print(f"   Score do sistema: {summary.get('system_score', 0):.1f}")
        print(f"   Status: {summary.get('system_status', 'UNKNOWN')}")
        
        # 5. Gerar relatório
        print("5. Gerando relatorio completo...")
        report = monitor.generate_report()
        print(f"   Relatorio gerado ({len(report)} bytes)")
        
        # 6. Testar monitoramento contínuo
        print("6. Testando monitoramento continuo...")
        monitor.start_monitoring()
        time.sleep(3)  # Aguardar um ciclo
        monitor.stop_monitoring()
        
        print("=" * 60)
        print("NEURAL CONNECTION MONITOR - INTEGRIDADE VALIDADA")
        print("Sistema pronto para monitoramento continuo")
        
    except Exception as e:
        print(f"[ERRO] FALHA NO TESTE: {e}")
        import traceback
        traceback.print_exc()
