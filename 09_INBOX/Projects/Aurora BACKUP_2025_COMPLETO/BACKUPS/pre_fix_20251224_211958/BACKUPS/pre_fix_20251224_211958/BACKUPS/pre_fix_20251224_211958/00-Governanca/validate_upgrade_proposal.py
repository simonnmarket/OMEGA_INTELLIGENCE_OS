#!/usr/bin/env python3
"""
VALIDADOR DE PROPOSTA DE UPGRADE - PROTOCOLO P&NR
Valida se proposta de upgrade atende critérios de Preservação e Não-Regressão
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ValidationResult:
    """Resultado da validação"""
    approved: bool
    regressions: List[Dict]
    improvements: List[Dict]
    risks: List[Dict]
    kpi_comparison: Dict
    recommendation: str
    requires_ceo_escalation: bool


class UpgradeProposalValidator:
    """Validador de propostas de upgrade conforme Protocolo P&NR"""
    
    def __init__(self):
        self.baseline_path = Path(__file__).parent / 'baseline_metrics.json'
        self.baseline = self._load_baseline()
        self.regressions = []
        self.improvements = []
        self.risks = []
    
    def _load_baseline(self) -> Dict:
        """Carrega métricas baseline"""
        try:
            with open(self.baseline_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Erro ao carregar baseline: {e}")
            return {}
    
    def analyze_proposal_structure(self, proposal_code: str) -> Dict:
        """Analisa estrutura da proposta"""
        analysis = {
            "components": [],
            "new_components": [],
            "modified_components": [],
            "removed_components": [],
            "structure_changes": []
        }
        
        # Análise básica de estrutura
        if "CORE/" in proposal_code or "core/" in proposal_code.lower():
            analysis["components"].append("CORE")
        
        if "AGENTS/" in proposal_code or "agents/" in proposal_code.lower():
            analysis["new_components"].append("AGENTS")
        
        if "ML_MODELS/" in proposal_code or "ml_models/" in proposal_code.lower():
            analysis["new_components"].append("ML_MODELS")
        
        if "STRATEGIES/" in proposal_code or "strategies/" in proposal_code.lower():
            analysis["components"].append("STRATEGIES")
        
        return analysis
    
    def validate_operational_preservation(self, proposal_metrics: Dict) -> Tuple[bool, List]:
        """Valida preservação operacional"""
        issues = []
        baseline_ops = self.baseline.get("operational_metrics", {})
        
        # Validar módulos operacionais
        baseline_operational = baseline_ops.get("operational_modules", 132)
        proposal_operational = proposal_metrics.get("operational_modules", 0)
        
        if proposal_operational < baseline_operational:
            issues.append({
                "metric": "operational_modules",
                "baseline": baseline_operational,
                "proposal": proposal_operational,
                "regression": baseline_operational - proposal_operational,
                "severity": "CRITICAL"
            })
        
        # Validar integration score
        baseline_score = baseline_ops.get("integration_score", 65.91)
        proposal_score = proposal_metrics.get("integration_score", 0)
        
        if proposal_score < baseline_score:
            issues.append({
                "metric": "integration_score",
                "baseline": baseline_score,
                "proposal": proposal_score,
                "regression": baseline_score - proposal_score,
                "severity": "HIGH"
            })
        
        # Validar taxa operacional
        baseline_rate = baseline_ops.get("operational_rate", 100.0)
        proposal_rate = proposal_metrics.get("operational_rate", 0)
        
        if proposal_rate < baseline_rate:
            issues.append({
                "metric": "operational_rate",
                "baseline": baseline_rate,
                "proposal": proposal_rate,
                "regression": baseline_rate - proposal_rate,
                "severity": "CRITICAL"
            })
        
        return len(issues) == 0, issues
    
    def validate_performance(self, proposal_metrics: Dict) -> Tuple[bool, List]:
        """Valida performance (KPIs)"""
        issues = []
        baseline_perf = self.baseline.get("performance_metrics", {})
        baseline_kpis = self.baseline.get("kpi_thresholds", {})
        
        # Validar Risk Score
        baseline_risk = baseline_perf.get("risk_score", 15)
        proposal_risk = proposal_metrics.get("risk_score", 100)
        
        if proposal_risk > baseline_risk:
            issues.append({
                "metric": "risk_score",
                "baseline": baseline_risk,
                "proposal": proposal_risk,
                "regression": proposal_risk - baseline_risk,
                "severity": "HIGH"
            })
        
        # Validar Compliance Status
        baseline_compliance = baseline_perf.get("compliance_status", "PASS")
        proposal_compliance = proposal_metrics.get("compliance_status", "FAIL")
        
        if proposal_compliance != "PASS" and baseline_compliance == "PASS":
            issues.append({
                "metric": "compliance_status",
                "baseline": baseline_compliance,
                "proposal": proposal_compliance,
                "regression": "Compliance degraded",
                "severity": "CRITICAL"
            })
        
        # Validar Vulnerabilities
        baseline_vuln = baseline_perf.get("vulnerabilities_critical", 0)
        proposal_vuln = proposal_metrics.get("vulnerabilities_critical", 0)
        
        if proposal_vuln > baseline_vuln:
            issues.append({
                "metric": "vulnerabilities_critical",
                "baseline": baseline_vuln,
                "proposal": proposal_vuln,
                "regression": proposal_vuln - baseline_vuln,
                "severity": "CRITICAL"
            })
        
        return len(issues) == 0, issues
    
    def validate_functionalities(self, proposal_code: str) -> Tuple[bool, List]:
        """Valida preservação de funcionalidades críticas"""
        issues = []
        critical_funcs = self.baseline.get("critical_functionalities", {})
        
        # Verificar cada funcionalidade crítica
        for func_name, func_info in critical_funcs.items():
            if func_info.get("required", False):
                # Verificar se funcionalidade está presente na proposta
                func_keywords = {
                    "ncnt_module_v2": ["NCNTModule", "ncnt_module_template_v2"],
                    "neural_connections": ["NeuralConnection", "neural_connection"],
                    "regulatory_context": ["RegulatoryContext", "regulatory_context"],
                    "audit_system": ["AuditSystem", "audit_system"],
                    "integration_gate": ["IntegrationGate", "integration_gate"],
                    "neural_monitor": ["NeuralConnectionMonitor", "neural_connection_monitor"],
                    "etapa_a_analyzer": ["AuroraEtapaAAnalyzer", "aurora_etapa_a"]
                }
                
                keywords = func_keywords.get(func_name, [func_name])
                found = any(keyword.lower() in proposal_code.lower() for keyword in keywords)
                
                if not found:
                    issues.append({
                        "functionality": func_name,
                        "status": "MISSING",
                        "severity": "CRITICAL",
                        "required": True
                    })
        
        return len(issues) == 0, issues
    
    def validate_proposal(self, proposal_code: str, proposal_metrics: Dict = None) -> ValidationResult:
        """Valida proposta completa"""
        print("=" * 80)
        print("[VALIDATION] VALIDANDO PROPOSTA DE UPGRADE - PROTOCOLO P&NR")
        print("=" * 80)
        
        if proposal_metrics is None:
            proposal_metrics = {}
        
        # 1. Análise de estrutura
        print("\n[1/4] Analisando estrutura da proposta...")
        structure_analysis = self.analyze_proposal_structure(proposal_code)
        print(f"    Componentes identificados: {len(structure_analysis['components'])}")
        print(f"    Novos componentes: {len(structure_analysis['new_components'])}")
        
        # 2. Validação operacional
        print("\n[2/4] Validando preservação operacional...")
        ops_valid, ops_issues = self.validate_operational_preservation(proposal_metrics)
        if ops_issues:
            self.regressions.extend(ops_issues)
            print(f"    [FAIL] {len(ops_issues)} regressões operacionais identificadas")
        else:
            print(f"    [PASS] Preservação operacional validada")
        
        # 3. Validação de performance
        print("\n[3/4] Validando performance (KPIs)...")
        perf_valid, perf_issues = self.validate_performance(proposal_metrics)
        if perf_issues:
            self.regressions.extend(perf_issues)
            print(f"    [FAIL] {len(perf_issues)} regressões de performance identificadas")
        else:
            print(f"    [PASS] Performance validada")
        
        # 4. Validação de funcionalidades
        print("\n[4/4] Validando funcionalidades críticas...")
        func_valid, func_issues = self.validate_functionalities(proposal_code)
        if func_issues:
            self.regressions.extend(func_issues)
            print(f"    [FAIL] {len(func_issues)} funcionalidades críticas ausentes")
        else:
            print(f"    [PASS] Funcionalidades críticas preservadas")
        
        # Determinar aprovação
        approved = len(self.regressions) == 0
        requires_ceo_escalation = len([r for r in self.regressions if r.get("severity") == "CRITICAL"]) > 0
        
        # Recomendação
        if approved:
            recommendation = "APROVADO - Proposta atende todos os critérios P&NR"
        elif requires_ceo_escalation:
            recommendation = "REJEITADO - REGRESSÕES CRÍTICAS - ESCALAR CEO IMEDIATAMENTE"
        else:
            recommendation = "REJEITADO - Regressões identificadas - Requer correções"
        
        # Comparação de KPIs
        kpi_comparison = {
            "operational_modules": {
                "baseline": self.baseline.get("operational_metrics", {}).get("operational_modules", 132),
                "proposal": proposal_metrics.get("operational_modules", 0),
                "status": "PASS" if proposal_metrics.get("operational_modules", 0) >= 132 else "FAIL"
            },
            "integration_score": {
                "baseline": self.baseline.get("operational_metrics", {}).get("integration_score", 65.91),
                "proposal": proposal_metrics.get("integration_score", 0),
                "status": "PASS" if proposal_metrics.get("integration_score", 0) >= 65.91 else "FAIL"
            },
            "risk_score": {
                "baseline": self.baseline.get("performance_metrics", {}).get("risk_score", 15),
                "proposal": proposal_metrics.get("risk_score", 100),
                "status": "PASS" if proposal_metrics.get("risk_score", 100) <= 15 else "FAIL"
            }
        }
        
        result = ValidationResult(
            approved=approved,
            regressions=self.regressions,
            improvements=self.improvements,
            risks=self.risks,
            kpi_comparison=kpi_comparison,
            recommendation=recommendation,
            requires_ceo_escalation=requires_ceo_escalation
        )
        
        return result
    
    def generate_validation_report(self, result: ValidationResult) -> str:
        """Gera relatório de validação"""
        report = f"""
# RELATÓRIO DE VALIDAÇÃO DE UPGRADE - PROTOCOLO P&NR

**Data:** {datetime.now().isoformat()}
**Status:** {'✅ APROVADO' if result.approved else '❌ REJEITADO'}

---

## RESULTADO DA VALIDAÇÃO

**Aprovação:** {'✅ APROVADO' if result.approved else '❌ REJEITADO'}
**Recomendação:** {result.recommendation}
**Escalação CEO:** {'🚨 REQUERIDA' if result.requires_ceo_escalation else '✅ Não requerida'}

---

## REGRESSÕES IDENTIFICADAS

Total: {len(result.regressions)}

"""
        
        for i, reg in enumerate(result.regressions, 1):
            report += f"""
### Regressão {i}

- **Métrica/Funcionalidade:** {reg.get('metric', reg.get('functionality', 'Unknown'))}
- **Baseline:** {reg.get('baseline', 'N/A')}
- **Proposta:** {reg.get('proposal', reg.get('status', 'N/A'))}
- **Regressão:** {reg.get('regression', 'N/A')}
- **Severidade:** {reg.get('severity', 'UNKNOWN')}
"""
        
        report += f"""
---

## COMPARAÇÃO DE KPIs

"""
        
        for kpi, data in result.kpi_comparison.items():
            status_icon = "✅" if data["status"] == "PASS" else "❌"
            report += f"""
- **{kpi}:**
  - Baseline: {data['baseline']}
  - Proposta: {data['proposal']}
  - Status: {status_icon} {data['status']}
"""
        
        report += f"""
---

## DECISÃO FINAL

**{'✅ APROVAR' if result.approved else '❌ REJEITAR'}**

"""
        
        if result.requires_ceo_escalation:
            report += """
## 🚨 ESCALAÇÃO CEO OBRIGATÓRIA

**REGRESSÕES CRÍTICAS IDENTIFICADAS**

Processo de atualização **INTERROMPIDO** até aprovação do CEO.
"""
        
        return report


def main():
    """Função principal"""
    validator = UpgradeProposalValidator()
    
    print("=" * 80)
    print("VALIDADOR DE PROPOSTA DE UPGRADE - PROTOCOLO P&NR")
    print("=" * 80)
    print("\nAguardando proposta de upgrade...")
    print("Use: validate_upgrade_proposal.py <proposal_code_file>")
    
    if len(sys.argv) > 1:
        proposal_file = Path(sys.argv[1])
        if proposal_file.exists():
            with open(proposal_file, 'r', encoding='utf-8') as f:
                proposal_code = f.read()
            
            result = validator.validate_proposal(proposal_code)
            report = validator.generate_validation_report(result)
            
            # Salvar relatório
            report_file = Path(__file__).parent.parent / f"UPGRADE_VALIDATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print("\n" + "=" * 80)
            print("RESULTADO DA VALIDAÇÃO:")
            print("=" * 80)
            print(f"\nAprovação: {'✅ APROVADO' if result.approved else '❌ REJEITADO'}")
            print(f"Recomendação: {result.recommendation}")
            print(f"Regressões: {len(result.regressions)}")
            print(f"\nRelatório salvo em: {report_file}")
            
            if result.requires_ceo_escalation:
                print("\n🚨 ESCALAÇÃO CEO OBRIGATÓRIA - PROCESSO INTERROMPIDO")
            
            return 0 if result.approved else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

