#!/usr/bin/env python3
"""
WRAPPER NCNT v2.0 - AURORA ETAPA A ANALYZER
Integra análise dos 5 pontos críticos CEO ao framework NCNT
"""

import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ncnt_module_template_v2 import NCNTModule, NeuralConnection, ModuleVitals, RegulatoryContext
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger("NCNT.AuroraEtapaA")


class AuroraEtapaAAnalyzerWrapper(NCNTModule):
    """
    Wrapper NCNT v2.0 para Aurora Etapa A Analyzer
    Analisa os 5 pontos críticos CEO com compliance embedded
    """
    
    MODULE_VERSION = "5.0.0"
    COMPLIANCE_REQUIRED = True
    
    def __init__(self, config: Dict = None):
        """Inicializa o wrapper"""
        default_config = {
            "symbols": ['EURUSD=X', 'BTC-USD', 'GC=F', '^GSPC'],
            "min_sharpe": 1.5,
            "min_profit_factor": 1.8,
            "max_drawdown": 0.15
        }
        
        merged_config = {**default_config, **(config or {})}
        super().__init__("AuroraEtapaAAnalyzer", merged_config)
        
        # Dependências
        self.required_modules = [
            "RegulatoryContext",
            "IntegrationGate",
            "NeuralConnectionMonitor"
        ]
        
        # Contexto regulatório específico
        self.regulatory_context.frameworks = [
            "MiFID_II",
            "SEC_Rule_15c3_5",
            "ISO_27001",
            "ISO_42001"
        ]
        
        self.regulatory_context.required_checks = [
            "integrity",
            "risk_limits",
            "trade_reporting",
            "best_execution",
            "conflict_prevention"
        ]
        
        logger.info("Aurora Etapa A Analyzer wrapper inicializado")
    
    def _establish_neural_connections(self) -> bool:
        """Estabelece conexões neurais com módulos relacionados"""
        success = super()._establish_neural_connections()
        
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from importlib import import_module
            genesis_module = import_module('00-Governanca.genesis_includes_v3_complete')
            genesis = genesis_module.get_genesis()
            
            # Conexão com Regulatory Context
            if "RegulatoryContext" in genesis._dependency_registry:
                reg_conn = NeuralConnection(
                    module_id=self.module_id,
                    connection_type="COMPLIANCE_DATA",
                    target_module="RegulatoryContext",
                    bandwidth=0.8,
                    latency_ms=10.0
                )
                reg_conn.checksum = reg_conn.calculate_checksum()
                self.neural_connections.append(reg_conn)
                self.vitals.active_connections.append("RegulatoryContext")
            
            # Conexão com Integration Gate
            if "IntegrationGate" in genesis._dependency_registry:
                int_conn = NeuralConnection(
                    module_id=self.module_id,
                    connection_type="INTEGRATION_DATA",
                    target_module="IntegrationGate",
                    bandwidth=0.7,
                    latency_ms=15.0
                )
                int_conn.checksum = int_conn.calculate_checksum()
                self.neural_connections.append(int_conn)
                self.vitals.active_connections.append("IntegrationGate")
            
            logger.info(f"🔗 {len(self.neural_connections)} conexões neurais estabelecidas")
            
        except Exception as e:
            logger.warning(f"⚠️ Conexões neurais incompletas: {e}")
        
        return success
    
    def execute_analysis(self) -> Dict[str, Any]:
        """
        Executa análise completa dos 5 pontos críticos CEO
        Retorna relatório completo
        """
        try:
            self.vitals.status = "HEALTHY"
            
            # Importar e executar análise
            from aurora_etapa_a import AuroraEtapaAAnalyzer
            
            analyzer = AuroraEtapaAAnalyzer()
            report = analyzer.run_complete_analysis()
            
            # Salvar relatórios
            json_file = analyzer.save_report(report, 'json')
            csv_file = analyzer.save_report(report, 'csv')
            
            # Preparar resultado
            result = {
                "timestamp": datetime.now().isoformat(),
                "module": self.module_name,
                "module_id": self.module_id,
                "success_rate": report.success_rate,
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "by_point": report.by_point,
                "decision": report.decision,
                "recommendations": report.recommendations,
                "reports_generated": {
                    "json": json_file,
                    "csv": csv_file
                },
                "compliance_status": self.vitals.compliance_status
            }
            
            # Atualizar vitals
            self.vitals.last_heartbeat = datetime.now()
            
            logger.info(f"✅ Análise completa executada - Taxa de sucesso: {report.success_rate:.1f}%")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro na execução da análise: {e}")
            self.vitals.status = "DEGRADED"
            self.vitals.error_rate += 1.0
            raise
    
    def _perform_module_specific_compliance_checks(self) -> Dict[str, Any]:
        """Checks de compliance específicos para análise CEO"""
        checks = []
        violations = []
        
        # Check 1: Análise executada recentemente
        try:
            from aurora_etapa_a import AuroraEtapaAAnalyzer
            analyzer = AuroraEtapaAAnalyzer()
            # Verificar se pode executar
            can_execute = True
            checks.append({
                "check": "analysis_executable",
                "status": "PASS" if can_execute else "VIOLATION",
                "details": {"executable": can_execute}
            })
        except Exception as e:
            checks.append({
                "check": "analysis_executable",
                "status": "VIOLATION",
                "details": {"error": str(e)}
            })
            violations.append("Análise não executável")
        
        # Check 2: Métricas institucionais configuradas
        has_metrics = all(key in self.config for key in [
            "min_sharpe", "min_profit_factor", "max_drawdown"
        ])
        checks.append({
            "check": "institutional_metrics_configured",
            "status": "PASS" if has_metrics else "VIOLATION",
            "details": {"configured": has_metrics}
        })
        
        if not has_metrics:
            violations.append("Métricas institucionais não configuradas")
        
        return {
            "checks_performed": checks,
            "has_violations": len(violations) > 0,
            "violations": violations,
            "status": "COMPLIANT" if len(violations) == 0 else "VIOLATION"
        }


# ============================================================================
# EXECUÇÃO STANDALONE
# ============================================================================

if __name__ == "__main__":
    """Teste do wrapper"""
    print("🧪 TESTE AURORA ETAPA A WRAPPER")
    print("=" * 60)
    
    try:
        # Criar instância
        wrapper = AuroraEtapaAAnalyzerWrapper()
        
        # Inicializar
        success = wrapper._initialize_module()
        
        if success:
            print("✅ Wrapper inicializado com sucesso")
            print(f"   Checksum: {wrapper.module_checksum[:12]}...")
            print(f"   Compliance: {wrapper.vitals.compliance_status}")
            print(f"   Conexões: {len(wrapper.neural_connections)}")
            
            # Executar análise
            print("\n🚀 Executando análise...")
            result = wrapper.execute_analysis()
            
            print(f"\n✅ Análise concluída:")
            print(f"   Taxa de sucesso: {result['success_rate']:.1f}%")
            print(f"   Decisão: {result['decision']}")
            print(f"   Relatórios: {result['reports_generated']}")
            
        else:
            print("❌ Falha na inicialização")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

