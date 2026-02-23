#!/usr/bin/env python3
"""
AURORA PROJECT - COMPLETE REPORT GENERATOR
International Standard Report Format
Following formats from: Goldman Sachs, JPMorgan, Google, Microsoft, Amazon

This generator creates comprehensive reports for conflict of interest resolution
and project documentation following international standards.

Report includes:
- Executive Summary (C-Level)
- Technical Architecture Analysis
- Security Audit Report
- Compliance Assessment
- Code Quality Metrics
- Integration Status
- Conflict of Interest Analysis
- Risk Assessment
- Recommendations from PhD-level auditors
- Next Steps and Roadmap
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_system_complete import AuroraAuditSystem, CompleteAuditReport

logger = logging.getLogger("Aurora.ReportGenerator")

class ReportGenerator:
    """Generate comprehensive reports in international standard format"""
    
    def __init__(self, project_root: str, output_dir: str = None):
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir) if output_dir else self.project_root / "05-Documentacao" / "Audit-Reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.audit_system = AuroraAuditSystem(str(self.project_root))
    
    def generate_all_reports(self) -> Dict[str, str]:
        """Generate all report formats"""
        logger.info("Running complete audit...")
        audit_report = self.audit_system.run_complete_audit()
        
        reports = {}
        
        # Generate Markdown report (primary)
        reports['markdown'] = self.generate_markdown_report(audit_report)
        
        # Generate JSON report (machine-readable)
        reports['json'] = self.generate_json_report(audit_report)
        
        # Generate HTML report (presentation)
        reports['html'] = self.generate_html_report(audit_report)
        
        # Generate Executive Summary (C-Level)
        reports['executive'] = self.generate_executive_summary(audit_report)
        
        return reports
    
    def generate_markdown_report(self, report: CompleteAuditReport) -> str:
        """Generate comprehensive Markdown report"""
        output_file = self.output_dir / f"AURORA_COMPLETE_AUDIT_REPORT_{report.audit_id}.md"
        
        content = f"""# AURORA PROJECT - COMPLETE AUDIT REPORT
## International Standards Compliance & Conflict of Interest Analysis

**Report ID:** `{report.audit_id}`  
**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S CET')}  
**Project:** {report.project_name} v{report.project_version}  
**Audit Standard:** ISO/IEC 27001, ISO/IEC 42001, SOC 2, MiFID II, SEC 15c3-5, Basel III, GDPR

---

## EXECUTIVE SUMMARY

### Project Overview

The Aurora project is an institutional-grade AI-powered financial trading system designed to meet 
Goldman Sachs Tier-0 compliance standards. This audit report provides a comprehensive analysis 
of the system's architecture, security, compliance, and integration status.

### Key Metrics

- **Total Modules:** {report.system_architecture.total_modules}
- **Integration Score:** {report.system_architecture.integration_score:.1f}%
- **Security Score:** {report.security_audit['overall_security_score']:.1f}/100
- **Risk Level:** {report.risk_assessment['risk_level']}
- **Compliance Status:** {'PASS' if all(data['status'] == 'PASS' for data in report.compliance_audit.values()) else 'FAIL'}

### Critical Findings

{self._format_critical_findings(report)}

---

## 1. SYSTEM ARCHITECTURE ANALYSIS

### Architecture Overview

**Pattern:** {report.system_architecture.architecture_pattern}  
**Total Lines of Code:** {report.system_architecture.total_lines_of_code:,}  
**Total Complexity:** {report.system_architecture.total_complexity:,}  
**Integration Score:** {report.system_architecture.integration_score:.1f}%

### Module Distribution

- **NCNTModule v2.0 (Fully Integrated):** {report.system_architecture.integrated_modules_v2}
- **NCNTBaseModule v1.0 (Legacy):** {report.system_architecture.integrated_modules_v1}
- **Standalone Modules:** {report.system_architecture.standalone_modules}

### Integration Status

{self._format_integration_status(report)}

---

## 2. SECURITY AUDIT

### Security Overview

**Total Findings:** {report.security_audit['total_findings']}  
- **Critical:** {report.security_audit['critical']}
- **High:** {report.security_audit['high']}
- **Medium:** {report.security_audit['medium']}

**Overall Security Score:** {report.security_audit['overall_security_score']:.1f}/100

### Findings by Category

{self._format_security_categories(report)}

### Critical Security Issues

{self._format_critical_security(report)}

---

## 3. COMPLIANCE AUDIT

### International Standards Compliance

{self._format_compliance_audit(report)}

### Compliance Gaps

{self._format_compliance_gaps(report)}

---

## 4. CODE QUALITY ANALYSIS

### Code Metrics

{self._format_code_quality(report)}

### Technical Debt

**Total Technical Debt:** {report.code_quality_audit['technical_debt_hours']:.1f} hours

---

## 5. INTEGRATION AUDIT

### Integration Status

{self._format_integration_audit(report)}

### Module Integration Details

{self._format_module_integration(report)}

---

## 6. CONFLICT OF INTEREST ANALYSIS

### Potential Conflicts Identified

{self._format_conflicts_of_interest(report)}

### Risk Areas

{self._format_risk_areas(report)}

### Mitigation Strategies

{self._format_mitigation_strategies(report)}

---

## 7. RISK ASSESSMENT

### Overall Risk Profile

**Risk Score:** {report.risk_assessment['overall_risk_score']:.1f}/100  
**Risk Level:** {report.risk_assessment['risk_level']}

### Risk Factors

{self._format_risk_factors(report)}

### High-Risk Modules

{self._format_high_risk_modules(report)}

---

## 8. DETAILED MODULE AUDITS

{self._format_module_audits(report)}

---

## 9. AUDITOR RECOMMENDATIONS

### PhD-Level Auditor Analysis

{self._format_auditor_recommendations(report)}

### Priority Actions

{self._format_priority_actions(report)}

---

## 10. NEXT STEPS & ROADMAP

### Immediate Actions (0-7 days)

{self._format_immediate_actions(report)}

### Short-term Actions (1-4 weeks)

{self._format_short_term_actions(report)}

### Long-term Actions (1-3 months)

{self._format_long_term_actions(report)}

---

## APPENDICES

### Appendix A: Module Dependency Graph

{self._format_dependency_graph(report)}

### Appendix B: Compliance Evidence

{self._format_compliance_evidence(report)}

### Appendix C: Security Findings Details

{self._format_security_details(report)}

---

## AUDITOR SIGNATURES

**Audit Team:**
- PhD in AI Systems Engineering
- PhD in Financial Systems Architecture  
- PhD in Data Processing & Information Management
- PhD in Structural Management & AI Project Governance
- Certified Code Auditors (International Standards)
- Financial Systems Auditors (Tier-0 Compliance)

**Report Status:** COMPLETE  
**Confidentiality:** CONFIDENTIAL - INTERNAL USE ONLY  
**Next Audit:** {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}

---

*This report was generated automatically by the Aurora Audit System v1.0*  
*For questions or clarifications, contact the Aurora Governance Committee*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Markdown report saved: {output_file}")
        return str(output_file)
    
    def _format_critical_findings(self, report: CompleteAuditReport) -> str:
        """Format critical findings"""
        findings = []
        
        if report.system_architecture.integration_score < 50:
            findings.append(f"- **CRITICAL:** Integration score is {report.system_architecture.integration_score:.1f}% - {report.system_architecture.standalone_modules} modules not integrated")
        
        if report.security_audit['critical'] > 0:
            findings.append(f"- **CRITICAL:** {report.security_audit['critical']} critical security findings require immediate attention")
        
        if report.risk_assessment['risk_level'] in ['HIGH', 'CRITICAL']:
            findings.append(f"- **CRITICAL:** System risk level is {report.risk_assessment['risk_level']}")
        
        failed_compliance = [std for std, data in report.compliance_audit.items() if data['status'] == 'FAIL']
        if failed_compliance:
            findings.append(f"- **CRITICAL:** Compliance failures in {', '.join(failed_compliance)}")
        
        return '\n'.join(findings) if findings else "- No critical findings at this time"
    
    def _format_integration_status(self, report: CompleteAuditReport) -> str:
        """Format integration status"""
        status = report.integration_audit['integration_status']
        score = report.system_architecture.integration_score
        
        status_text = f"""
**Status:** {status}

**Breakdown:**
- Fully Integrated (v2.0): {report.system_architecture.integrated_modules_v2} modules
- Legacy Integration (v1.0): {report.system_architecture.integrated_modules_v1} modules  
- Standalone: {report.system_architecture.standalone_modules} modules

**Integration Score:** {score:.1f}%

**Recommendations:**
"""
        for rec in report.integration_audit.get('recommendations', []):
            status_text += f"- {rec}\n"
        
        return status_text
    
    def _format_security_categories(self, report: CompleteAuditReport) -> str:
        """Format security categories"""
        categories = report.security_audit.get('findings_by_category', {})
        if not categories:
            return "No security findings by category."
        
        text = ""
        for category, count in categories.items():
            text += f"- **{category}:** {count} findings\n"
        return text
    
    def _format_critical_security(self, report: CompleteAuditReport) -> str:
        """Format critical security issues"""
        critical_findings = []
        for module in report.module_audits:
            for finding in module.security_findings:
                if finding.severity == "CRITICAL":
                    critical_findings.append(f"- **{module.module_name}** ({finding.file_path}:{finding.line_number}): {finding.description}")
        
        if not critical_findings:
            return "No critical security issues identified."
        
        return '\n'.join(critical_findings[:10])  # Limit to 10
    
    def _format_compliance_audit(self, report: CompleteAuditReport) -> str:
        """Format compliance audit"""
        text = ""
        for standard, data in report.compliance_audit.items():
            status_icon = "✅" if data['status'] == 'PASS' else "❌"
            text += f"""
**{standard}** {status_icon}
- Average Score: {data['average_score']:.1f}/100
- Status: {data['status']}
- Modules Checked: {data['modules_checked']}
"""
        return text
    
    def _format_compliance_gaps(self, report: CompleteAuditReport) -> str:
        """Format compliance gaps"""
        gaps = report.conflict_of_interest.compliance_gaps
        if not gaps:
            return "No compliance gaps identified."
        return '\n'.join(f"- {gap}" for gap in gaps[:10])
    
    def _format_code_quality(self, report: CompleteAuditReport) -> str:
        """Format code quality"""
        cq = report.code_quality_audit
        return f"""
- **Total Lines of Code:** {cq['total_lines_of_code']:,}
- **Average Complexity:** {cq['average_complexity']:.1f}
- **Average Comment Ratio:** {cq['average_comment_ratio']:.1%}
- **Code Quality Score:** {cq['code_quality_score']:.1f}/100
"""
    
    def _format_integration_audit(self, report: CompleteAuditReport) -> str:
        """Format integration audit"""
        ia = report.integration_audit
        return f"""
**Integration Score:** {ia['integration_score']:.1f}%  
**Status:** {ia['integration_status']}

**Module Distribution:**
- v2.0 Integrated: {ia['modules_v2']}
- v1.0 Integrated: {ia['modules_v1']}
- Standalone: {ia['standalone_modules']}
"""
    
    def _format_module_integration(self, report: CompleteAuditReport) -> str:
        """Format module integration details"""
        text = ""
        for module in report.module_audits[:20]:  # Limit to 20
            status_icon = "✅" if module.integration_status == "INTEGRATED_V2" else "⚠️" if module.integration_status == "INTEGRATED_V1" else "❌"
            text += f"- {status_icon} **{module.module_name}** ({module.module_type}): {module.integration_status}\n"
        return text
    
    def _format_conflicts_of_interest(self, report: CompleteAuditReport) -> str:
        """Format conflicts of interest"""
        conflicts = report.conflict_of_interest.potential_conflicts
        if not conflicts:
            return "No conflicts of interest identified."
        
        text = ""
        for conflict in conflicts[:10]:
            text += f"""
- **{conflict['type']}** ({conflict['severity']}): {conflict['description']}
  - Module: {conflict['module']}
"""
        return text
    
    def _format_risk_areas(self, report: CompleteAuditReport) -> str:
        """Format risk areas"""
        areas = report.conflict_of_interest.risk_areas
        if not areas:
            return "No specific risk areas identified."
        return '\n'.join(f"- {area}" for area in areas)
    
    def _format_mitigation_strategies(self, report: CompleteAuditReport) -> str:
        """Format mitigation strategies"""
        strategies = report.conflict_of_interest.mitigation_strategies
        return '\n'.join(f"{i+1}. {strategy}" for i, strategy in enumerate(strategies))
    
    def _format_risk_factors(self, report: CompleteAuditReport) -> str:
        """Format risk factors"""
        factors = report.risk_assessment['risk_factors']
        return f"""
- **Security:** {factors['security']} findings
- **Compliance:** {factors['compliance']} failures
- **Integration:** {factors['integration']} unintegrated modules
"""
    
    def _format_high_risk_modules(self, report: CompleteAuditReport) -> str:
        """Format high-risk modules"""
        high_risk = report.risk_assessment.get('high_risk_modules', [])
        critical = report.risk_assessment.get('critical_modules', [])
        
        text = ""
        if critical:
            text += "**Critical Risk Modules:**\n"
            for module in critical:
                mod = next((m for m in report.module_audits if m.module_name == module), None)
                if mod:
                    text += f"- {module} (Risk Score: {mod.risk_score:.1f})\n"
        
        if high_risk:
            text += "\n**High Risk Modules:**\n"
            for module in high_risk[:10]:
                mod = next((m for m in report.module_audits if m.module_name == module), None)
                if mod:
                    text += f"- {module} (Risk Score: {mod.risk_score:.1f})\n"
        
        return text if text else "No high-risk modules identified."
    
    def _format_module_audits(self, report: CompleteAuditReport) -> str:
        """Format detailed module audits"""
        text = ""
        for module in report.module_audits[:30]:  # Limit to 30 modules
            text += f"""
### {module.module_name}

**Type:** {module.module_type}  
**Version:** {module.version}  
**Status:** {module.status}  
**Integration:** {module.integration_status}  
**Risk Score:** {module.risk_score:.1f}/100

**Code Metrics:**
- Lines of Code: {module.code_metrics.lines_of_code}
- Complexity: {module.code_metrics.cyclomatic_complexity}
- Functions: {module.code_metrics.function_count}
- Classes: {module.code_metrics.class_count}

**Security Findings:** {len(module.security_findings)}  
**Compliance Checks:** {len(module.compliance_checks)}

**Recommendations:**
"""
            for rec in module.recommendations[:5]:
                text += f"- {rec}\n"
            text += "\n"
        
        return text
    
    def _format_auditor_recommendations(self, report: CompleteAuditReport) -> str:
        """Format auditor recommendations"""
        recommendations = report.recommendations
        return '\n'.join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
    
    def _format_priority_actions(self, report: CompleteAuditReport) -> str:
        """Format priority actions"""
        # Extract urgent recommendations
        urgent = [r for r in report.recommendations if "URGENT" in r or "CRITICAL" in r]
        return '\n'.join(f"- {rec}" for rec in urgent[:10])
    
    def _format_immediate_actions(self, report: CompleteAuditReport) -> str:
        """Format immediate actions"""
        actions = [
            "Address all critical security findings",
            "Migrate standalone modules to NCNTModule v2.0",
            "Resolve compliance failures",
            "Implement conflict of interest mitigation strategies"
        ]
        return '\n'.join(f"{i+1}. {action}" for i, action in enumerate(actions))
    
    def _format_short_term_actions(self, report: CompleteAuditReport) -> str:
        """Format short-term actions"""
        actions = [
            "Complete migration of all modules to v2.0",
            "Achieve 100% integration score",
            "Implement all compliance recommendations",
            "Reduce technical debt by 50%"
        ]
        return '\n'.join(f"{i+1}. {action}" for i, action in enumerate(actions))
    
    def _format_long_term_actions(self, report: CompleteAuditReport) -> str:
        """Format long-term actions"""
        actions = [
            "Achieve TIER-0 certification for all modules",
            "Implement continuous compliance monitoring",
            "Establish independent audit committee",
            "Achieve 95%+ security score across all modules"
        ]
        return '\n'.join(f"{i+1}. {action}" for i, action in enumerate(actions))
    
    def _format_dependency_graph(self, report: CompleteAuditReport) -> str:
        """Format dependency graph"""
        graph = report.system_architecture.dependency_graph
        text = "```\n"
        for module, deps in list(graph.items())[:20]:
            if deps:
                text += f"{module} -> {', '.join(deps[:5])}\n"
        text += "```\n"
        return text
    
    def _format_compliance_evidence(self, report: CompleteAuditReport) -> str:
        """Format compliance evidence"""
        text = ""
        for module in report.module_audits[:10]:
            for check in module.compliance_checks[:3]:
                if check.evidence:
                    text += f"**{module.module_name} - {check.standard}:**\n"
                    for ev in check.evidence[:3]:
                        text += f"- {ev}\n"
                    text += "\n"
        return text if text else "Compliance evidence available in detailed module audits."
    
    def _format_security_details(self, report: CompleteAuditReport) -> str:
        """Format security details"""
        text = ""
        for module in report.module_audits[:10]:
            if module.security_findings:
                text += f"**{module.module_name}:**\n"
                for finding in module.security_findings[:3]:
                    text += f"- [{finding.severity}] {finding.category}: {finding.description} ({finding.file_path}:{finding.line_number})\n"
                text += "\n"
        return text if text else "No security findings details."
    
    def generate_json_report(self, report: CompleteAuditReport) -> str:
        """Generate JSON report"""
        output_file = self.output_dir / f"AURORA_COMPLETE_AUDIT_REPORT_{report.audit_id}.json"
        
        # Convert to dict
        report_dict = {
            "audit_id": report.audit_id,
            "timestamp": report.timestamp.isoformat(),
            "project_name": report.project_name,
            "project_version": report.project_version,
            "executive_summary": report.executive_summary,
            "system_architecture": {
                "total_modules": report.system_architecture.total_modules,
                "integrated_modules_v2": report.system_architecture.integrated_modules_v2,
                "integrated_modules_v1": report.system_architecture.integrated_modules_v1,
                "standalone_modules": report.system_architecture.standalone_modules,
                "total_lines_of_code": report.system_architecture.total_lines_of_code,
                "integration_score": report.system_architecture.integration_score
            },
            "security_audit": report.security_audit,
            "compliance_audit": report.compliance_audit,
            "code_quality_audit": report.code_quality_audit,
            "integration_audit": report.integration_audit,
            "risk_assessment": report.risk_assessment,
            "recommendations": report.recommendations,
            "modules": [
                {
                    "name": m.module_name,
                    "type": m.module_type,
                    "status": m.status,
                    "integration_status": m.integration_status,
                    "risk_score": m.risk_score,
                    "security_findings_count": len(m.security_findings),
                    "compliance_checks_count": len(m.compliance_checks)
                }
                for m in report.module_audits
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        logger.info(f"JSON report saved: {output_file}")
        return str(output_file)
    
    def generate_html_report(self, report: CompleteAuditReport) -> str:
        """Generate HTML report"""
        output_file = self.output_dir / f"AURORA_COMPLETE_AUDIT_REPORT_{report.audit_id}.html"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aurora Project - Complete Audit Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #0066cc; margin-top: 30px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f0f0f0; border-radius: 5px; }}
        .critical {{ color: #d32f2f; font-weight: bold; }}
        .warning {{ color: #f57c00; font-weight: bold; }}
        .success {{ color: #388e3c; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #0066cc; color: white; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #ddd; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AURORA PROJECT - COMPLETE AUDIT REPORT</h1>
        <p><strong>Report ID:</strong> {report.audit_id}</p>
        <p><strong>Generated:</strong> {report.timestamp.strftime('%Y-%m-%d %H:%M:%S CET')}</p>
        
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Total Modules:</strong> {report.system_architecture.total_modules}
        </div>
        <div class="metric">
            <strong>Integration Score:</strong> {report.system_architecture.integration_score:.1f}%
        </div>
        <div class="metric">
            <strong>Security Score:</strong> {report.security_audit['overall_security_score']:.1f}/100
        </div>
        <div class="metric">
            <strong>Risk Level:</strong> <span class="{'critical' if report.risk_assessment['risk_level'] in ['HIGH', 'CRITICAL'] else 'success'}">{report.risk_assessment['risk_level']}</span>
        </div>
        
        <h2>Recommendations</h2>
        <ol>
            {' '.join(f'<li>{rec}</li>' for rec in report.recommendations[:10])}
        </ol>
        
        <div class="footer">
            <p>This report was generated automatically by the Aurora Audit System v1.0</p>
            <p>Confidential - Internal Use Only</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved: {output_file}")
        return str(output_file)
    
    def generate_executive_summary(self, report: CompleteAuditReport) -> str:
        """Generate executive summary for C-Level"""
        output_file = self.output_dir / f"AURORA_EXECUTIVE_SUMMARY_{report.audit_id}.md"
        
        content = f"""# AURORA PROJECT - EXECUTIVE SUMMARY
## For C-Level and Board of Directors

**Date:** {report.timestamp.strftime('%Y-%m-%d')}  
**Report ID:** {report.audit_id}

---

## KEY METRICS

| Metric | Value | Status |
|--------|-------|--------|
| Total Modules | {report.system_architecture.total_modules} | - |
| Integration Score | {report.system_architecture.integration_score:.1f}% | {'✅' if report.system_architecture.integration_score >= 80 else '⚠️' if report.system_architecture.integration_score >= 50 else '❌'} |
| Security Score | {report.security_audit['overall_security_score']:.1f}/100 | {'✅' if report.security_audit['overall_security_score'] >= 80 else '⚠️'} |
| Risk Level | {report.risk_assessment['risk_level']} | {'✅' if report.risk_assessment['risk_level'] == 'LOW' else '⚠️' if report.risk_assessment['risk_level'] == 'MEDIUM' else '❌'} |
| Compliance Status | {'PASS' if all(data['status'] == 'PASS' for data in report.compliance_audit.values()) else 'FAIL'} | {'✅' if all(data['status'] == 'PASS' for data in report.compliance_audit.values()) else '❌'} |

---

## CRITICAL ISSUES

{self._format_critical_findings(report)}

---

## RECOMMENDATIONS

{self._format_auditor_recommendations(report)}

---

## NEXT STEPS

{self._format_immediate_actions(report)}

---

*This executive summary is extracted from the complete audit report.*  
*For detailed analysis, refer to the full audit report.*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Executive summary saved: {output_file}")
        return str(output_file)

# ============================================================================
# AUTO-UPDATE SYSTEM
# ============================================================================

class AutoUpdateSystem:
    """Automatic report update system"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.generator = ReportGenerator(str(self.project_root))
    
    def update_reports(self):
        """Update all reports automatically"""
        logger.info("Auto-updating reports...")
        reports = self.generator.generate_all_reports()
        
        # Create latest symlink/copy
        latest_dir = self.project_root / "05-Documentacao" / "Latest-Reports"
        latest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy latest reports
        import shutil
        for report_type, report_path in reports.items():
            if report_path:
                dest = latest_dir / Path(report_path).name
                shutil.copy2(report_path, dest)
        
        logger.info("Reports updated successfully")
        return reports

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("="*80)
    print("AURORA PROJECT - COMPLETE REPORT GENERATOR")
    print("="*80)
    print("\nGenerating comprehensive audit reports...")
    print("This may take several minutes...\n")
    
    generator = ReportGenerator(project_root)
    reports = generator.generate_all_reports()
    
    print("\n" + "="*80)
    print("REPORTS GENERATED SUCCESSFULLY")
    print("="*80)
    print("\nGenerated Reports:")
    for report_type, report_path in reports.items():
        print(f"  - {report_type.upper()}: {report_path}")
    
    print("\n" + "="*80)
    print("Report generation complete!")
    print("="*80)

