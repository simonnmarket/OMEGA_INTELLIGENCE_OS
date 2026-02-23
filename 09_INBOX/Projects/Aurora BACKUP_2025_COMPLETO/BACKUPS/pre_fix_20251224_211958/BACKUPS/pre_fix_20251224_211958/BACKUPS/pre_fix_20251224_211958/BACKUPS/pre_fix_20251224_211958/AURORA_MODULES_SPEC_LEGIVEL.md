# AURORA v5.1 - Modules Specification (Legível)
**Document ID:** MOD-SPEC-AURORA-5.1-20251221
**Formato:** Markdown Legível
**Origem:** aurora_modules_spec.json
**Data:** 2025-12-21

---

## METADADOS DO SISTEMA

```
Total Módulos: 259
Categorias: 10
Gerado em: 2025-12-21T22:49:19.070741
```

---

## DISTRIBUIÇÃO POR CATEGORIA

- **Core**: 5 módulos
- **Departments**: 40 módulos
- **Documentation**: 1 módulos
- **Governance**: 28 módulos
- **Infrastructure**: 17 módulos
- **Modules**: 10 módulos
- **Monitoring**: 7 módulos
- **Operations**: 12 módulos
- **Processes**: 16 módulos
- **Root**: 123 módulos

---

## CORE (5 módulos)

### Lista de Módulos

```
system_core\__init__.py                                                          | C: 0 F:  0
system_core\message_bus.py                                                       | C: 1 F:  4
system_core\ncnt_orchestrator_complete.py                                        | ERROR
system_core\orchestrator.py                                                      | C: 1 F:  5
system_core\registry.py                                                          | C: 1 F:  7
```

### Especificações Detalhadas (Top 20)


#### system_core\ncnt_orchestrator_complete.py

**ERRO:** invalid non-printable character U+FEFF (ncnt_orchestrator_complete.py, line 1)


---


#### system_core\orchestrator.py

**Tamanho:** 4,061 bytes | **Linhas:** 118

**Classes:**
- `NCNTOrchestrator` (5 métodos)

**Funções:**
- `__init__(self)`
- `register_module(self, module, metadata)`
- `unregister_module(self, module_id)`
- `get_system_status(self)`
- `list_all_modules(self)`

**Imports principais:**
- `asyncio`
- `from typing import ...`
- `from datetime import ...`
- `from message_bus import ...`
- `from registry import ...`
- `from modules.interfaces import ...`


---


#### system_core\message_bus.py

**Tamanho:** 4,025 bytes | **Linhas:** 109

**Classes:**
- `NCNTMessageBus` (4 métodos)

**Funções:**
- `__init__(self)`
- `subscribe(self, module_name, callback)`
- `unsubscribe(self, module_name, callback)`
- `get_stats(self)`

**Imports principais:**
- `asyncio`
- `from typing import ...`
- `from datetime import ...`
- `json`
- `from modules.interfaces import ...`


---


#### system_core\registry.py

**Tamanho:** 3,318 bytes | **Linhas:** 90

**Classes:**
- `NCNTRegistry` (7 métodos)

**Funções:**
- `__init__(self)`
- `register(self, module, metadata)`
- `unregister(self, module_id)`
- `get_module(self, module_id)`
- `get_module_by_name(self, module_name)`
- `list_modules(self, module_type)`
- `get_stats(self)`

**Imports principais:**
- `from typing import ...`
- `from datetime import ...`
- `from modules.interfaces import ...`


---


#### system_core\__init__.py

**Tamanho:** 377 bytes | **Linhas:** 18

**Imports principais:**
- `from orchestrator import ...`
- `from message_bus import ...`
- `from registry import ...`


---

## DEPARTMENTS (40 módulos)

### Lista de Módulos

```
01-Departamentos\AGENTS\CEO_Agent.py                                             | C: 1 F: 11
01-Departamentos\AGENTS\CFO_Agent.py                                             | C: 1 F:  8
01-Departamentos\AGENTS\CKO_Agent.py                                             | C: 1 F:  1
01-Departamentos\AGENTS\CTO_Agent.py                                             | C: 1 F:  1
01-Departamentos\Compliance-Audit\__init__.py                                    | C: 0 F:  0
01-Departamentos\Compliance-Audit\audit_trail.py                                 | C: 0 F:  0
01-Departamentos\Compliance-Audit\compliance_module.py                           | C: 1 F:  5
01-Departamentos\Compliance-Audit\reg_tracker.py                                 | C: 0 F:  0
01-Departamentos\Compliance-Audit\report_generator.py                            | C: 0 F:  0
01-Departamentos\Engineering-Infra\__init__.py                                   | C: 0 F:  0
01-Departamentos\Engineering-Infra\api_gateway.py                                | C: 0 F:  0
01-Departamentos\Engineering-Infra\core_engine.py                                | C: 0 F:  0
01-Departamentos\Engineering-Infra\coreengine_module.py                          | C: 1 F:  2
01-Departamentos\Engineering-Infra\data_layer.py                                 | C: 0 F:  0
01-Departamentos\Execution-Trading\__init__.py                                   | C: 0 F:  0
01-Departamentos\Execution-Trading\order_management.py                           | C: 0 F:  0
01-Departamentos\Execution-Trading\smart_routing.py                              | C: 0 F:  0
01-Departamentos\Execution-Trading\strategies\__init__.py                        | C: 0 F:  0
01-Departamentos\Execution-Trading\strategies\alpha_momentum.py                  | C: 1 F:  5
01-Departamentos\Execution-Trading\strategies\base_strategy.py                   | C: 2 F:  6
01-Departamentos\Execution-Trading\strategies\breakout_detection.py              | C: 1 F:  4
01-Departamentos\Execution-Trading\strategies\mean_reversion.py                  | C: 1 F:  4
01-Departamentos\Execution-Trading\strategy_module.py                            | C: 1 F:  4
01-Departamentos\Execution-Trading\strategy_modules\__init__.py                  | C: 0 F:  0
01-Departamentos\Execution-Trading\strategy_modules\interface.py                 | C: 0 F:  0
01-Departamentos\Execution-Trading\strategy_modules\templates\strategy_template.py | C: 0 F:  0
01-Departamentos\Innovation-Lab\__init__.py                                      | C: 0 F:  0
01-Departamentos\Innovation-Lab\ab_testing.py                                    | C: 0 F:  0
01-Departamentos\Innovation-Lab\innovationlab_module.py                          | C: 1 F:  4
01-Departamentos\Innovation-Lab\prototypes.py                                    | C: 0 F:  0
01-Departamentos\Risk-Controls\__init__.py                                       | C: 0 F:  0
01-Departamentos\Risk-Controls\circuit_breakers.py                               | C: 0 F:  0
01-Departamentos\Risk-Controls\risk_engine.py                                    | C: 0 F:  0
01-Departamentos\Risk-Controls\risk_module.py                                    | C: 1 F: 13
01-Departamentos\Risk-Controls\tier1_validator_v3.py                             | C: 3 F: 14
01-Departamentos\Risk-Controls\tier1_validator_v3_complete.py                    | C: 6 F: 20
01-Departamentos\Treasury-Capital\__init__.py                                    | C: 0 F:  0
01-Departamentos\Treasury-Capital\allocation_engine.py                           | C: 0 F:  0
01-Departamentos\Treasury-Capital\capital_manager.py                             | C: 0 F:  0
01-Departamentos\Treasury-Capital\treasury_module.py                             | C: 2 F:  3
```

### Especificações Detalhadas (Top 20)


#### 01-Departamentos\Risk-Controls\tier1_validator_v3_complete.py

**Tamanho:** 36,248 bytes | **Linhas:** 875

**Classes:**
- `RiskLevel` extends Enum (0 métodos)
- `ValidationResult` extends Enum (0 métodos)
- `TradeSignal` (2 métodos)
- `PortfolioState` (1 métodos)
- `RiskMetrics` (2 métodos)
- `Tier1RiskValidatorV3` (15 métodos)

**Funções:**
- `calculate_fingerprint(self)`
- `validate(self)`
- `get_exposure_pct(self, symbol)`
- `to_dict(self)`
- `calculate_risk_score(self)`
- `__init__(self, config)`
- `validate_trade_signal(self, signal, portfolio)`
- `_calculate_hhi(self, portfolio, signal, trade_value)`
- `_calculate_var_historical(self, returns, confidence)`
- `_calculate_expected_shortfall(self, returns, confidence)`
- `_project_var_impact(self, current_var, position_size_pct, confidence)`
- `_determine_risk_level(self, metrics)`
- `_log_validation(self, validation_id, signal, portfolio, result...)`
- `update_portfolio_metrics(self, portfolio)`
- `_calculate_ulcer_index(self, returns)`
- ... e mais 5 funções

**Imports principais:**
- `numpy`
- `from decimal import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from datetime import ...`
- `hashlib`
- `json`
- `logging`
- `from enum import ...`
- `warnings`
- ... e mais 2 imports


---


#### 01-Departamentos\Risk-Controls\risk_module.py

**Tamanho:** 23,501 bytes | **Linhas:** 572

**Classes:**
- `RiskModule` extends NCNTBaseModule (13 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_risk_limits(self)`
- `_initialize_circuit_breakers(self)`
- `_calculate_absolute_risk(self, position)`
- `_calculate_limit_utilization(self, position)`
- `_check_limit_breaches(self, position)`
- `_update_exposure_tracking(self, risk_metrics)`
- `_calculate_net_exposure(self, portfolio)`
- `_calculate_gross_exposure(self, portfolio)`
- `_calculate_diversification_score(self, portfolio)`
- `_calculate_concentration_metrics(self, portfolio)`
- `_calculate_liquidity_metrics(self, portfolio)`
- `_calculate_portfolio_greeks(self, portfolio)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 8 imports


---


#### 01-Departamentos\Compliance-Audit\compliance_module.py

**Tamanho:** 19,503 bytes | **Linhas:** 502

**Classes:**
- `ComplianceModule` extends NCNTBaseModule (5 métodos)

**Funções:**
- `__init__(self)`
- `_load_regulations(self)`
- `_load_report_templates(self)`
- `_calculate_report_hash(self, report_data)`
- `_calculate_audit_hash(self, data)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 8 imports


---


#### 01-Departamentos\Risk-Controls\tier1_validator_v3.py

**Tamanho:** 19,351 bytes | **Linhas:** 505

**Classes:**
- `RiskSignal` (0 métodos)
- `RiskMetrics` (3 métodos)
- `Tier1RiskValidatorV3` (10 métodos)

**Funções:**
- `test_risk_validator_v3()`
- `__init__(self)`
- `to_dict(self)`
- `calculate_risk_score(self)`
- `__init__(self, config)`
- `validate_trade_signal(self, signal, portfolio)`
- `_calculate_hhi(self, exposures, portfolio_value, signal, trade_value)`
- `_calculate_var_historical(self, returns, confidence)`
- `_calculate_var_parametric(self, returns, confidence)`
- `update_portfolio_metrics(self, portfolio)`
- `get_risk_score(self)`
- `update_daily_pnl(self, pnl)`
- `generate_risk_report(self)`
- `_generate_recommendations(self)`

**Imports principais:**
- `numpy`
- `from decimal import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from datetime import ...`
- `logging`
- `from scipy import ...`


---


#### 01-Departamentos\Innovation-Lab\innovationlab_module.py

**Tamanho:** 17,975 bytes | **Linhas:** 456

**Classes:**
- `InnovationLabModule` extends NCNTBaseModule (4 métodos)

**Funções:**
- `__init__(self)`
- `_calculate_success_rate(self)`
- `_get_top_performing_prototypes(self, limit)`
- `_get_upcoming_milestones(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 10 imports


---


#### 01-Departamentos\Treasury-Capital\treasury_module.py

**Tamanho:** 12,863 bytes | **Linhas:** 304

**Classes:**
- `CapitalAllocation` (1 métodos)
- `TreasuryModule` extends NCNTBaseModule (2 métodos)

**Funções:**
- `to_dict(self)`
- `__init__(self)`
- `_get_target_percentage(self, strategy_id)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 8 imports


---


#### 01-Departamentos\AGENTS\CEO_Agent.py

**Tamanho:** 10,658 bytes | **Linhas:** 265

**Classes:**
- `CEOAgent` (10 métodos)

**Funções:**
- `get_ceo_agent()`
- `__init__(self)`
- `_check_infrastructure(self)`
- `_analyze_module(self, module_path)`
- `_analyze_ncnt_compatibility(self)`
- `_check_monitoring_capability(self)`
- `_analyze_scalability(self)`
- `_check_security_integration(self)`
- `_calculate_scores(self)`
- `_determine_status(self)`
- `_generate_recommendations(self, infrastructure_check, compatibility_analysis)`

**Imports principais:**
- `os`
- `sys`
- `json`
- `from datetime import ...`
- `from typing import ...`
- `logging`


---


#### 01-Departamentos\Execution-Trading\strategy_module.py

**Tamanho:** 8,712 bytes | **Linhas:** 231

**Classes:**
- `StrategyModule` extends NCNTBaseModule (4 métodos)

**Funções:**
- `__init__(self, strategy_name)`
- `_format_signal(self, raw_signal, market_data)`
- `_update_performance_metrics(self, signal)`
- `_log_error(self, error_message)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 9 imports


---


#### 01-Departamentos\Engineering-Infra\coreengine_module.py

**Tamanho:** 6,872 bytes | **Linhas:** 188

**Classes:**
- `CoreEngineModule` extends NCNTBaseModule (2 métodos)

**Funções:**
- `__init__(self)`
- `_find_backup_module(self, module_name)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 8 imports


---


#### 01-Departamentos\Execution-Trading\strategies\alpha_momentum.py

**Tamanho:** 6,597 bytes | **Linhas:** 171

**Classes:**
- `AlphaMomentumStrategy` extends BaseStrategy (4 métodos)

**Funções:**
- `test_alpha_momentum_strategy()`
- `__init__(self)`
- `analyze(self, market_data)`
- `validate_parameters(self)`
- `calculate_risk_metrics(self)`

**Imports principais:**
- `from decimal import ...`
- `from datetime import ...`
- `from typing import ...`
- `pandas`
- `numpy`
- `sys`
- `from pathlib import ...`
- `importlib.util`
- `from base_strategy import ...`
- `from base_strategy import ...`


---


#### 01-Departamentos\Execution-Trading\strategies\breakout_detection.py

**Tamanho:** 6,352 bytes | **Linhas:** 155

**Classes:**
- `BreakoutDetectionStrategy` extends BaseStrategy (4 métodos)

**Funções:**
- `__init__(self)`
- `analyze(self, market_data)`
- `validate_parameters(self)`
- `calculate_risk_metrics(self)`

**Imports principais:**
- `from decimal import ...`
- `from datetime import ...`
- `from typing import ...`
- `pandas`
- `numpy`
- `sys`
- `from pathlib import ...`
- `importlib.util`
- `from base_strategy import ...`
- `from base_strategy import ...`


---


#### 01-Departamentos\Execution-Trading\strategies\mean_reversion.py

**Tamanho:** 6,158 bytes | **Linhas:** 155

**Classes:**
- `MeanReversionStrategy` extends BaseStrategy (4 métodos)

**Funções:**
- `__init__(self)`
- `analyze(self, market_data)`
- `validate_parameters(self)`
- `calculate_risk_metrics(self)`

**Imports principais:**
- `from decimal import ...`
- `from datetime import ...`
- `from typing import ...`
- `pandas`
- `numpy`
- `sys`
- `from pathlib import ...`
- `importlib.util`
- `from base_strategy import ...`
- `from base_strategy import ...`


---


#### 01-Departamentos\AGENTS\CFO_Agent.py

**Tamanho:** 4,084 bytes | **Linhas:** 116

**Classes:**
- `CFOAgent` (8 métodos)

**Funções:**
- `__init__(self)`
- `_check_sharpe_calculation(self)`
- `_check_profit_factor(self)`
- `_check_drawdown_calculation(self)`
- `_check_win_rate(self)`
- `_check_ml_integration(self)`
- `_check_continuous_learning(self)`
- `_check_feedback_loop(self)`

**Imports principais:**
- `os`
- `logging`
- `from datetime import ...`
- `from typing import ...`


---


#### 01-Departamentos\Execution-Trading\strategies\base_strategy.py

**Tamanho:** 2,341 bytes | **Linhas:** 75

**Classes:**
- `TradeSignal` (1 métodos)
- `BaseStrategy` extends ABC (5 métodos)

**Funções:**
- `calculate_checksum(self)`
- `__init__(self, strategy_id, capital_allocation)`
- `analyze(self, market_data)`
- `validate_parameters(self)`
- `calculate_risk_metrics(self)`
- `get_strategy_info(self)`

**Imports principais:**
- `from abc import ...`
- `from dataclasses import ...`
- `from datetime import ...`
- `from typing import ...`
- `hashlib`
- `from decimal import ...`


---


#### 01-Departamentos\AGENTS\CKO_Agent.py

**Tamanho:** 1,481 bytes | **Linhas:** 40

**Classes:**
- `CKOAgent` (1 métodos)

**Funções:**
- `__init__(self)`

**Imports principais:**
- `logging`
- `from datetime import ...`
- `from typing import ...`
- `os`


---


#### 01-Departamentos\AGENTS\CTO_Agent.py

**Tamanho:** 1,195 bytes | **Linhas:** 34

**Classes:**
- `CTOAgent` (1 métodos)

**Funções:**
- `__init__(self)`

**Imports principais:**
- `logging`
- `from datetime import ...`
- `from typing import ...`


---


#### 01-Departamentos\Execution-Trading\strategies\__init__.py

**Tamanho:** 470 bytes | **Linhas:** 18

**Imports principais:**
- `from base_strategy import ...`
- `from alpha_momentum import ...`
- `from mean_reversion import ...`
- `from breakout_detection import ...`


---


#### 01-Departamentos\Risk-Controls\risk_engine.py

**Tamanho:** 49 bytes | **Linhas:** 1


---


#### 01-Departamentos\Execution-Trading\strategy_modules\interface.py

**Tamanho:** 46 bytes | **Linhas:** 1


---


#### 01-Departamentos\Treasury-Capital\capital_manager.py

**Tamanho:** 45 bytes | **Linhas:** 1


---

## DOCUMENTATION (1 módulos)

### Lista de Módulos

```
05-Documentacao\sops_module.py                                                   | C: 1 F:  2
```

### Especificações Detalhadas (Top 20)


#### 05-Documentacao\sops_module.py

**Tamanho:** 9,600 bytes | **Linhas:** 259

**Classes:**
- `SOPsModule` extends NCNTBaseModule (2 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_sops(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 8 imports


---

## GOVERNANCE (28 módulos)

### Lista de Módulos

```
00-Governanca\__init__.py                                                        | C: 0 F:  0
00-Governanca\audit_system_complete.py                                           | C:10 F: 33
00-Governanca\complete_activation_final.py                                       | C: 0 F:  4
00-Governanca\complexity_guard.py                                                | C: 3 F: 17
00-Governanca\fix_report_errors.py                                               | C: 0 F:  2
00-Governanca\generate_complete_report.py                                        | C: 2 F: 31
00-Governanca\generate_complete_technical_report.py                              | C: 1 F: 11
00-Governanca\generate_technical_report.py                                       | C: 0 F:  6
00-Governanca\generate_ultra_complete_report.py                                  | C: 1 F: 39
00-Governanca\genesis_includes.py                                                | C: 4 F: 14
00-Governanca\genesis_includes_v3_complete.py                                    | C: 9 F: 26
00-Governanca\governance_module.py                                               | C: 2 F:  3
00-Governanca\integration_gate_v2.py                                             | C: 2 F: 14
00-Governanca\integration_gate_v3.py                                             | C: 1 F: 18
00-Governanca\prepare_fix_environment.py                                         | C: 0 F:  5
00-Governanca\process_fix_file.py                                                | C: 1 F: 13
00-Governanca\quantum_firewall.py                                                | C: 1 F: 13
00-Governanca\regulatory_context.py                                              | C: 1 F: 11
00-Governanca\restore_executive_report.py                                        | C: 0 F:  1
00-Governanca\run_complete_audit.py                                              | C: 0 F:  1
00-Governanca\script_1_command_injection_test.py                                 | C: 1 F:  5
00-Governanca\script_2_smoke_test_critical_modules.py                            | C: 1 F:  4
00-Governanca\script_3_compliance_quick_validator.py                             | C: 1 F:  5
00-Governanca\script_4_integration_score_calculator.py                           | C: 1 F:  5
00-Governanca\script_5_master_test_runner.py                                     | C: 1 F:  5
00-Governanca\test_module_v2.py                                                  | C: 1 F:  3
00-Governanca\tier1_risk_validator.py                                            | C: 1 F:  6
00-Governanca\validate_upgrade_proposal.py                                       | C: 2 F:  9
```

### Especificações Detalhadas (Top 20)


#### 00-Governanca\generate_ultra_complete_report.py

**Tamanho:** 45,466 bytes | **Linhas:** 1049

**Classes:**
- `UltraCompleteReportGenerator` extends ReportGenerator (39 métodos)

**Funções:**
- `generate_markdown_report(self, report)`
- `_format_critical_findings_complete(self, report)`
- `_format_integration_status_complete(self, report)`
- `_format_all_security_categories(self, report)`
- `_format_all_critical_security(self, report)`
- `_format_all_security_findings(self, report)`
- `_format_complete_compliance_audit(self, report)`
- `_format_all_compliance_gaps(self, report)`
- `_format_all_compliance_evidence(self, report)`
- `_format_complete_code_quality(self, report)`
- `_format_complexity_analysis(self, report)`
- `_format_complexity_distribution(self, report)`
- `_format_complete_integration_audit(self, report)`
- `_format_all_module_integration(self, report)`
- `_format_dependency_analysis(self, report)`
- ... e mais 24 funções

**Imports principais:**
- `os`
- `sys`
- `json`
- `from pathlib import ...`
- `from datetime import ...`
- `logging`
- `from generate_complete_report import ...`


---


#### 00-Governanca\audit_system_complete.py

**Tamanho:** 41,901 bytes | **Linhas:** 1027

**Classes:**
- `CodeMetrics` (0 métodos)
- `SecurityFinding` (0 métodos)
- `ComplianceCheck` (0 métodos)
- `ModuleAudit` (0 métodos)
- `SystemArchitecture` (0 métodos)
- `ConflictOfInterestAnalysis` (0 métodos)
- `CompleteAuditReport` (0 métodos)
- `CodeAnalyzer` (5 métodos)
- `ComplianceAuditor` (6 métodos)
- `AuroraAuditSystem` (22 métodos)

**Funções:**
- `__init__(self)`
- `analyze_file(self, file_path)`
- `_determine_severity(self, category)`
- `_get_recommendation(self, category)`
- `_get_cwe_id(self, category)`
- `audit_module(self, module_audit)`
- `_check_iso27001(self, module)`
- `_check_iso42001(self, module)`
- `_check_mifid_ii(self, module)`
- `_check_sec_15c3_5(self, module)`
- `_check_gdpr(self, module)`
- `__init__(self, project_root)`
- `run_complete_audit(self)`
- `_discover_modules(self)`
- `_audit_module(self, module_path)`
- ... e mais 18 funções

**Imports principais:**
- `os`
- `sys`
- `json`
- `hashlib`
- `ast`
- `inspect`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from pathlib import ...`
- ... e mais 5 imports


---


#### 00-Governanca\integration_gate_v3.py

**Tamanho:** 35,457 bytes | **Linhas:** 876

**Classes:**
- `IntegrationGateV3` (15 métodos)

**Funções:**
- `get_integration_gate_v3()`
- `require_integration_gate_v3(module_class)`
- `__init__(self)`
- `validate_module_integration(self, module_name, certification_level)`
- `_test_genesis_registration(self, module, module_name)`
- `_test_ncnt_module_structure(self, module, module_name)`
- `_test_module_vitals(self, module, module_name)`
- `_test_neural_connections(self, module, module_name)`
- `_test_health_checks(self, module, module_name)`
- `_test_dependencies(self, module, module_name)`
- `_test_neural_signals(self, module, module_name)`
- `_test_performance(self, module, module_name)`
- `_add_failed_check(self, validation_results, check_name, details, weight)`
- `_determine_certification(self, score, target_level)`
- `_generate_recommendations(self, checks)`
- ... e mais 3 funções

**Imports principais:**
- `json`
- `hashlib`
- `os`
- `sys`
- `from datetime import ...`
- `from typing import ...`
- `logging`
- `from genesis_includes_v3_complete import ...`
- `from modules.ncnt_module_template import ...`
- `importlib.util`
- ... e mais 3 imports


---


#### 00-Governanca\generate_complete_report.py

**Tamanho:** 29,431 bytes | **Linhas:** 786

**Classes:**
- `ReportGenerator` (29 métodos)
- `AutoUpdateSystem` (2 métodos)

**Funções:**
- `__init__(self, project_root, output_dir)`
- `generate_all_reports(self)`
- `generate_markdown_report(self, report)`
- `_format_critical_findings(self, report)`
- `_format_integration_status(self, report)`
- `_format_security_categories(self, report)`
- `_format_critical_security(self, report)`
- `_format_compliance_audit(self, report)`
- `_format_compliance_gaps(self, report)`
- `_format_code_quality(self, report)`
- `_format_integration_audit(self, report)`
- `_format_module_integration(self, report)`
- `_format_conflicts_of_interest(self, report)`
- `_format_risk_areas(self, report)`
- `_format_mitigation_strategies(self, report)`
- ... e mais 16 funções

**Imports principais:**
- `os`
- `sys`
- `json`
- `hashlib`
- `from datetime import ...`
- `from pathlib import ...`
- `from typing import ...`
- `logging`
- `from audit_system_complete import ...`
- `shutil`


---


#### 00-Governanca\genesis_includes_v3_complete.py

**Tamanho:** 26,700 bytes | **Linhas:** 657

**Classes:**
- `DependencyIntegrityError` extends Exception (0 métodos)
- `ConfigurationError` extends Exception (0 métodos)
- `CircularDependencyError` extends Exception (0 métodos)
- `ServiceTimeoutError` extends Exception (0 métodos)
- `ServiceStatus` extends Enum (0 métodos)
- `ServiceHealth` (2 métodos)
- `DependencyMetadata` (2 métodos)
- `SystemMetrics` (3 métodos)
- `GenesisIncludes` (15 métodos)

**Funções:**
- `get_genesis()`
- `validate_genesis_integrity()`
- `is_healthy(self)`
- `to_dict(self)`
- `calculate_checksum(self)`
- `validate(self)`
- `to_dict(self)`
- `_calculate_success_rate(self)`
- `_calculate_health_score(self)`
- `__new__(cls)`
- `__init__(self)`
- `_load_system_configuration(self)`
- `_initialize_core_dependencies(self)`
- `_validate_container_integrity(self)`
- `_detect_circular_dependencies(self)`
- ... e mais 11 funções

**Imports principais:**
- `os`
- `sys`
- `json`
- `hashlib`
- `threading`
- `asyncio`
- `from typing import ...`
- `from dataclasses import ...`
- `from datetime import ...`
- `logging`
- ... e mais 4 imports


---


#### 00-Governanca\generate_complete_technical_report.py

**Tamanho:** 19,453 bytes | **Linhas:** 488

**Classes:**
- `TechnicalReportGenerator` (10 métodos)

**Funções:**
- `main()`
- `__init__(self)`
- `calculate_file_checksum(self, filepath)`
- `count_lines(self, filepath)`
- `scan_python_files(self)`
- `test_module_import(self, filepath)`
- `generate_file_report(self, filepath)`
- `generate_statistics(self)`
- `run_full_scan(self)`
- `save_json_report(self)`
- `save_markdown_report(self)`

**Imports principais:**
- `os`
- `sys`
- `json`
- `hashlib`
- `importlib.util`
- `inspect`
- `from pathlib import ...`
- `from datetime import ...`
- `from typing import ...`
- `traceback`


---


#### 00-Governanca\process_fix_file.py

**Tamanho:** 17,241 bytes | **Linhas:** 456

**Classes:**
- `FixFileProcessor` (12 métodos)

**Funções:**
- `main()`
- `__init__(self, project_root)`
- `_load_baseline_report(self)`
- `_calculate_file_checksum(self, filepath)`
- `_backup_file(self, filepath)`
- `_test_module_import(self, filepath)`
- `validate_fix_file(self, fix_file_path)`
- `process_fix_file(self, fix_file_path)`
- `_process_single_python_file(self, filepath)`
- `_process_zip_file(self, zip_path)`
- `_process_json_fixes(self, json_path)`
- `generate_fix_report(self)`
- `save_fix_report(self, report)`

**Imports principais:**
- `os`
- `sys`
- `json`
- `hashlib`
- `importlib.util`
- `shutil`
- `from datetime import ...`
- `from pathlib import ...`
- `from typing import ...`
- `logging`
- ... e mais 1 imports


---


#### 00-Governanca\complexity_guard.py

**Tamanho:** 16,668 bytes | **Linhas:** 419

**Classes:**
- `ComplexityMetrics` (3 métodos)
- `ComplexityGuard` (9 métodos)
- `ClassMethodVisitor` extends ast.NodeVisitor (4 métodos)

**Funções:**
- `__init__(self)`
- `to_dict(self)`
- `calculate_score(self)`
- `__init__(self, base_path)`
- `analyze_module(self, module_path)`
- `_calculate_cyclomatic_complexity(self, tree)`
- `_count_dependencies(self, source_code)`
- `_calculate_nested_depth(self, tree)`
- `audit_all_modules(self)`
- `_check_violations(self, metrics)`
- `_generate_recommendations(self, module_path, metrics)`
- `generate_report(self, output_file)`
- `__init__(self)`
- `visit_ClassDef(self, node)`
- `visit_FunctionDef(self, node)`
- ... e mais 2 funções

**Imports principais:**
- `ast`
- `os`
- `sys`
- `from pathlib import ...`
- `from typing import ...`
- `json`
- `logging`
- `from datetime import ...`


---


#### 00-Governanca\integration_gate_v2.py

**Tamanho:** 16,021 bytes | **Linhas:** 416

**Classes:**
- `IntegrationGateV2` (9 métodos)
- `TestModule` extends NCNTModule (1 métodos)

**Funções:**
- `get_integration_gate()`
- `require_integration_gate(cls)`
- `__init__(self)`
- `certify_module(self, module)`
- `_verify_checksum(self, module, certification)`
- `_verify_compliance(self, module, certification)`
- `_verify_dependencies(self, module, certification)`
- `_verify_neural_connections(self, module, certification)`
- `_verify_structural_integrity(self, module, certification)`
- `is_certified(self, module_name)`
- `get_certification_report(self)`
- `new_init(self)`
- `new_initialize(self)`
- `__init__(self)`

**Imports principais:**
- `json`
- `hashlib`
- `from datetime import ...`
- `from typing import ...`
- `logging`
- `os`
- `sys`
- `from modules.ncnt_module_template import ...`


---


#### 00-Governanca\validate_upgrade_proposal.py

**Tamanho:** 15,483 bytes | **Linhas:** 398

**Classes:**
- `ValidationResult` (0 métodos)
- `UpgradeProposalValidator` (8 métodos)

**Funções:**
- `main()`
- `__init__(self)`
- `_load_baseline(self)`
- `analyze_proposal_structure(self, proposal_code)`
- `validate_operational_preservation(self, proposal_metrics)`
- `validate_performance(self, proposal_metrics)`
- `validate_functionalities(self, proposal_code)`
- `validate_proposal(self, proposal_code, proposal_metrics)`
- `generate_validation_report(self, result)`

**Imports principais:**
- `json`
- `sys`
- `from pathlib import ...`
- `from typing import ...`
- `from datetime import ...`
- `from dataclasses import ...`


---


#### 00-Governanca\generate_technical_report.py

**Tamanho:** 15,004 bytes | **Linhas:** 406

**Funções:**
- `analyze_module_code(module_path)`
- `check_module_operational(module_path)`
- `scan_all_modules()`
- `generate_technical_report(modules)`
- `generate_markdown_report(report)`
- `main()`

**Imports principais:**
- `os`
- `sys`
- `json`
- `importlib.util`
- `from pathlib import ...`
- `from typing import ...`
- `from datetime import ...`
- `ast`


---


#### 00-Governanca\restore_executive_report.py

**Tamanho:** 13,304 bytes | **Linhas:** 399

**Funções:**
- `restore_executive_report()`

**Imports principais:**
- `os`
- `re`
- `from pathlib import ...`


---


#### 00-Governanca\quantum_firewall.py

**Tamanho:** 9,384 bytes | **Linhas:** 247

**Classes:**
- `QuantumFirewall` (12 métodos)

**Funções:**
- `get_firewall(security_level)`
- `__init__(self, security_level)`
- `_generate_secret_key(self)`
- `_get_audit_system(self)`
- `activate(self)`
- `_verify_system_integrity(self)`
- `_analyze_module(self, module_path)`
- `_calculate_file_hash(self, filepath)`
- `validate_request(self, request_data)`
- `_calculate_request_hash(self, request_data)`
- `_block_request(self, reason)`
- `_log_security_event(self, event_type, details, severity)`
- `get_security_status(self)`

**Imports principais:**
- `hashlib`
- `hmac`
- `secrets`
- `json`
- `os`
- `from datetime import ...`
- `from typing import ...`
- `logging`
- `from audit_system_complete import ...`


---


#### 00-Governanca\genesis_includes.py

**Tamanho:** 8,848 bytes | **Linhas:** 254

**Classes:**
- `DependencyConfig` (0 métodos)
- `DependencyError` extends Exception (0 métodos)
- `GenesisIncludes` (10 métodos)
- `MetricsCollector` (3 métodos)

**Funções:**
- `get_genesis()`
- `__new__(cls)`
- `__init__(self)`
- `_load_secrets(self)`
- `_initialize_core_dependencies(self)`
- `register(self, name, dependency, is_interface)`
- `resolve(self, name)`
- `_load_interface(self, interface_name)`
- `_calculate_checksum(self)`
- `validate_integrity(self)`
- `get_all_dependencies(self)`
- `__init__(self)`
- `increment(self, metric)`
- `get_metrics(self)`

**Imports principais:**
- `os`
- `json`
- `hashlib`
- `from typing import ...`
- `from dataclasses import ...`
- `logging`
- `sys`
- `from pathlib import ...`
- `from importlib import ...`


---


#### 00-Governanca\prepare_fix_environment.py

**Tamanho:** 8,523 bytes | **Linhas:** 206

**Funções:**
- `calculate_baseline_checksums(project_root)`
- `prepare_metrics(project_root)`
- `create_directories(project_root)`
- `save_preparation_metrics(metrics, project_root)`
- `main()`

**Imports principais:**
- `os`
- `json`
- `hashlib`
- `from datetime import ...`
- `from pathlib import ...`
- `from typing import ...`


---


#### 00-Governanca\script_3_compliance_quick_validator.py

**Tamanho:** 8,374 bytes | **Linhas:** 210

**Classes:**
- `ComplianceValidator` (5 métodos)

**Funções:**
- `__init__(self)`
- `find_compliance_files(self)`
- `analyze_regulatory_context(self)`
- `check_compliance_implementation(self)`
- `run(self)`

**Imports principais:**
- `os`
- `json`
- `sys`
- `from pathlib import ...`


---


#### 00-Governanca\regulatory_context.py

**Tamanho:** 7,666 bytes | **Linhas:** 207

**Classes:**
- `RegulatoryContext` (11 métodos)

**Funções:**
- `run_compliance_check(self, check_type)`
- `_perform_specific_check(self, check_name)`
- `_check_integrity(self)`
- `_check_latency(self)`
- `_check_audit_log(self)`
- `_check_data_protection(self)`
- `_check_risk_limits(self)`
- `_check_trade_reporting(self)`
- `_check_best_execution(self)`
- `_check_surveillance(self)`
- `_check_business_continuity(self)`

**Imports principais:**
- `hashlib`
- `from dataclasses import ...`
- `from typing import ...`
- `from datetime import ...`
- `logging`


---


#### 00-Governanca\tier1_risk_validator.py

**Tamanho:** 7,645 bytes | **Linhas:** 189

**Classes:**
- `Tier1RiskValidator` (5 métodos)

**Funções:**
- `get_risk_validator()`
- `__init__(self)`
- `validate_strategy_metrics(self, metrics)`
- `_calculate_composite_score(self, validation_details)`
- `_get_grade(self, score)`
- `calculate_position_size(self, portfolio_value, risk_score, volatility)`

**Imports principais:**
- `logging`
- `from datetime import ...`
- `from decimal import ...`
- `from typing import ...`
- `from regulatory_context import ...`


---


#### 00-Governanca\script_5_master_test_runner.py

**Tamanho:** 7,471 bytes | **Linhas:** 220

**Classes:**
- `MasterTestRunner` (5 métodos)

**Funções:**
- `__init__(self)`
- `run_test(self, test_info)`
- `calculate_overall_score(self)`
- `generate_report(self)`
- `run(self)`

**Imports principais:**
- `subprocess`
- `sys`
- `time`
- `from datetime import ...`
- `from pathlib import ...`


---


#### 00-Governanca\script_4_integration_score_calculator.py

**Tamanho:** 7,280 bytes | **Linhas:** 190

**Classes:**
- `IntegrationScoreCalculator` (5 métodos)

**Funções:**
- `__init__(self)`
- `scan_directory(self, directory)`
- `classify_module(self, filepath)`
- `calculate_score(self)`
- `run(self)`

**Imports principais:**
- `os`
- `re`
- `sys`
- `from pathlib import ...`


---

## INFRASTRUCTURE (17 módulos)

### Lista de Módulos

```
04-Infraestrutura\ML_MODELS\MetaLearningAdapter.py                               | C: 1 F:  2
04-Infraestrutura\ML_MODELS\PPOExecutionOptimizer.py                             | C: 1 F:  2
04-Infraestrutura\ML_MODELS\TemporalFusionTransformer.py                         | C: 2 F:  6
04-Infraestrutura\MT5_STOPS_FIX.py                                               | C: 1 F:  7
04-Infraestrutura\api\__init__.py                                                | C: 0 F:  0
04-Infraestrutura\api\database.py                                                | C: 1 F:  4
04-Infraestrutura\api\endpoints\__init__.py                                      | C: 0 F:  2
04-Infraestrutura\api\endpoints\strategies.py                                    | C: 2 F:  2
04-Infraestrutura\api\main.py                                                    | C: 0 F:  0
04-Infraestrutura\database\__init__.py                                           | C: 0 F:  0
04-Infraestrutura\database\connection.py                                         | C: 0 F:  6
04-Infraestrutura\database\models.py                                             | C: 3 F:  0
04-Infraestrutura\moduleregistry.py                                              | C: 1 F:  2
04-Infraestrutura\mt5_executor.py                                                | C: 2 F: 10
04-Infraestrutura\tools\cli\ncnt_cli.py                                          | C: 0 F:  0
04-Infraestrutura\tools\scripts\deploy.py                                        | C: 0 F:  0
04-Infraestrutura\tools\scripts\monitor.py                                       | C: 0 F:  0
```

### Especificações Detalhadas (Top 20)


#### 04-Infraestrutura\mt5_executor.py

**Tamanho:** 27,601 bytes | **Linhas:** 664

**Classes:**
- `OrderType` extends Enum (0 métodos)
- `MT5Executor` (10 métodos)

**Funções:**
- `__init__(self, login, password, server, path...)`
- `connect(self)`
- `disconnect(self)`
- `ensure_connected(self)`
- `get_symbol_info(self, symbol)`
- `convert_signal_to_mt5_order(self, signal, symbol_info, sl_points, tp_points)`
- `execute_order(self, signal)`
- `get_positions(self, symbol)`
- `get_statistics(self)`
- `__del__(self)`

**Imports principais:**
- `sys`
- `logging`
- `from pathlib import ...`
- `from datetime import ...`
- `from typing import ...`
- `from decimal import ...`
- `from enum import ...`
- `time`
- `from MT5_STOPS_FIX import ...`
- `MetaTrader5`
- ... e mais 4 imports


---


#### 04-Infraestrutura\MT5_STOPS_FIX.py

**Tamanho:** 10,540 bytes | **Linhas:** 250

**Classes:**
- `MT5StopsFix` (7 métodos)

**Funções:**
- `__init__(self)`
- `get_symbol_info_correctly(self, symbol)`
- `calculate_stops_based_on_level(self, symbol_info, price, action)`
- `calculate_stops_by_percentage(self, price, action)`
- `validate_stops(self, symbol_info, price, sl, tp...)`
- `execute_order_with_robust_stops(self, symbol, order_type, volume, price...)`
- `_send_order_attempt(self, symbol, order_type, volume, price...)`

**Imports principais:**
- `MetaTrader5`
- `logging`
- `from datetime import ...`
- `from typing import ...`
- `time`


---


#### 04-Infraestrutura\moduleregistry.py

**Tamanho:** 9,438 bytes | **Linhas:** 258

**Classes:**
- `ModuleRegistry` extends NCNTBaseModule (2 métodos)

**Funções:**
- `__init__(self)`
- `_is_valid_version(self, version)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 10 imports


---


#### 04-Infraestrutura\api\endpoints\strategies.py

**Tamanho:** 6,577 bytes | **Linhas:** 203

**Classes:**
- `StrategyExecuteRequest` extends BaseModel (2 métodos)
- `TradeSignalResponse` extends BaseModel (0 métodos)

**Funções:**
- `validate_strategy_id(cls, v)`
- `validate_timestamp(cls, v)`

**Imports principais:**
- `from fastapi import ...`
- `from pydantic import ...`
- `from decimal import ...`
- `from datetime import ...`
- `from typing import ...`
- `hashlib`
- `sys`
- `importlib.util`
- `from pathlib import ...`
- `from database.connection import ...`


---


#### 04-Infraestrutura\ML_MODELS\TemporalFusionTransformer.py

**Tamanho:** 6,338 bytes | **Linhas:** 172

**Classes:**
- `TemporalFusionTransformer` extends nn.Module (3 métodos)
- `TemporalFusionTransformer` (2 métodos)

**Funções:**
- `create_tft_model(input_features, device)`
- `__init__(self, input_size, hidden_size, num_heads, num_encoder_layers...)`
- `forward(self, historical_data, future_data, static_data)`
- `predict_trading_signal(self, market_data, confidence_threshold)`
- `__init__(self)`
- `predict_trading_signal(self)`

**Imports principais:**
- `from typing import ...`
- `numpy`
- `torch`
- `torch.nn`
- `torch.nn.functional`


---


#### 04-Infraestrutura\api\database.py

**Tamanho:** 4,045 bytes | **Linhas:** 132

**Classes:**
- `TimestampMixin` (0 métodos)

**Funções:**
- `get_db()`
- `db_session()`
- `init_database()`
- `get_database_status()`

**Imports principais:**
- `logging`
- `from contextlib import ...`
- `from datetime import ...`
- `from typing import ...`
- `from sqlalchemy import ...`
- `from sqlalchemy.orm import ...`
- `from sqlalchemy.exc import ...`
- `from sqlalchemy.pool import ...`


---


#### 04-Infraestrutura\database\models.py

**Tamanho:** 3,036 bytes | **Linhas:** 70

**Classes:**
- `StrategyExecution` extends Base (0 métodos)
- `Trade` extends Base (0 métodos)
- `PerformanceMetrics` extends Base (0 métodos)

**Imports principais:**
- `from sqlalchemy import ...`
- `from sqlalchemy.ext.declarative import ...`
- `from sqlalchemy.sql import ...`
- `from datetime import ...`
- `from decimal import ...`


---


#### 04-Infraestrutura\database\connection.py

**Tamanho:** 2,876 bytes | **Linhas:** 107

**Funções:**
- `load_config()`
- `get_database_url()`
- `get_engine()`
- `get_session()`
- `check_db_connection()`
- `close_connection()`

**Imports principais:**
- `json`
- `os`
- `from pathlib import ...`
- `from sqlalchemy import ...`
- `from sqlalchemy.orm import ...`
- `from typing import ...`
- `logging`


---


#### 04-Infraestrutura\ML_MODELS\PPOExecutionOptimizer.py

**Tamanho:** 1,396 bytes | **Linhas:** 41

**Classes:**
- `PPOExecutionOptimizer` (2 métodos)

**Funções:**
- `__init__(self)`
- `optimize_execution(self, market_data)`

**Imports principais:**
- `logging`
- `from typing import ...`
- `torch`


---


#### 04-Infraestrutura\ML_MODELS\MetaLearningAdapter.py

**Tamanho:** 1,294 bytes | **Linhas:** 39

**Classes:**
- `MetaLearningAdapter` (2 métodos)

**Funções:**
- `__init__(self)`
- `adapt_to_new_market(self, market_data)`

**Imports principais:**
- `logging`
- `from typing import ...`
- `torch`


---


#### 04-Infraestrutura\api\main.py

**Tamanho:** 1,015 bytes | **Linhas:** 48

**Imports principais:**
- `from fastapi import ...`
- `from fastapi.middleware.cors import ...`
- `from endpoints import ...`


---


#### 04-Infraestrutura\api\__init__.py

**Tamanho:** 577 bytes | **Linhas:** 21

**Imports principais:**
- `from database import ...`
- `from main import ...`
- `from endpoints import ...`


---


#### 04-Infraestrutura\api\endpoints\__init__.py

**Tamanho:** 473 bytes | **Linhas:** 22

**Funções:**
- `get_all_routers()`
- `register_all_routers(app)`

**Imports principais:**
- `from None import ...`
- `from None import ...`
- `from None import ...`


---


#### 04-Infraestrutura\database\__init__.py

**Tamanho:** 399 bytes | **Linhas:** 18

**Imports principais:**
- `from connection import ...`
- `from models import ...`


---


#### 04-Infraestrutura\tools\scripts\monitor.py

**Tamanho:** 25 bytes | **Linhas:** 1


---


#### 04-Infraestrutura\tools\scripts\deploy.py

**Tamanho:** 18 bytes | **Linhas:** 1


---


#### 04-Infraestrutura\tools\cli\ncnt_cli.py

**Tamanho:** 15 bytes | **Linhas:** 1


---

## MODULES (12 módulos)

### Lista de Módulos

```
fix_all_8_modules.py                                                             | C: 1 F:  8
modules\__init__.py                                                              | C: 0 F:  0
modules\connectors\__init__.py                                                   | C: 0 F:  0
modules\connectors\data_connector.py                                             | C: 0 F:  0
modules\connectors\execution_connector.py                                        | C: 0 F:  0
modules\connectors\risk_connector.py                                             | C: 0 F:  0
modules\connectors\strategy_connector.py                                         | C: 0 F:  0
modules\interfaces.py                                                            | C: 3 F:  9
modules\ncnt_base.py                                                             | C: 5 F:  7
modules\ncnt_module_template.py                                                  | C: 6 F: 50
modules\ncnt_module_template_v2.py                                               | C: 9 F: 51
validate_239_modules.py                                                          | C: 1 F:  7
```

### Especificações Detalhadas (Top 20)


#### modules\ncnt_module_template_v2.py

**Tamanho:** 45,596 bytes | **Linhas:** 1133

**Classes:**
- `RegulatoryContext` (11 métodos)
- `NeuralConnection` (3 métodos)
- `ModuleVitals` (4 métodos)
- `NCNTModule` extends NCNTBaseModule (16 métodos)
- `RiskControlsModule` extends NCNTModule (14 métodos)
- `TestModuleV2` extends NCNTModule (1 métodos)
- `NCNTBaseModule` (1 métodos)
- `ModuleType` (0 métodos)
- `NCNTTransmission` (0 métodos)

**Funções:**
- `run_compliance_check(self, check_type)`
- `_perform_specific_check(self, check_name)`
- `_check_integrity(self)`
- `_check_latency(self)`
- `_check_audit_log(self)`
- `_check_data_protection(self)`
- `_check_risk_limits(self)`
- `_check_trade_reporting(self)`
- `_check_best_execution(self)`
- `_check_surveillance(self)`
- `_check_business_continuity(self)`
- `calculate_checksum(self)`
- `update_activity(self)`
- `is_active(self, timeout_seconds)`
- `is_alive(self)`
- ... e mais 36 funções

**Imports principais:**
- `hashlib`
- `json`
- `inspect`
- `sys`
- `os`
- `from dataclasses import ...`
- `from typing import ...`
- `from datetime import ...`
- `logging`
- `from ncnt_base import ...`
- ... e mais 6 imports


---


#### modules\ncnt_module_template.py

**Tamanho:** 45,472 bytes | **Linhas:** 1126

**Classes:**
- `RegulatoryContext` (11 métodos)
- `NeuralConnection` (3 métodos)
- `ModuleVitals` (4 métodos)
- `NCNTModule` extends NCNTBaseModule (16 métodos)
- `RiskControlsModule` extends NCNTModule (14 métodos)
- `TestModuleV2` extends NCNTModule (1 métodos)

**Funções:**
- `run_compliance_check(self, check_type)`
- `_perform_specific_check(self, check_name)`
- `_check_integrity(self)`
- `_check_latency(self)`
- `_check_audit_log(self)`
- `_check_data_protection(self)`
- `_check_risk_limits(self)`
- `_check_trade_reporting(self)`
- `_check_best_execution(self)`
- `_check_surveillance(self)`
- `_check_business_continuity(self)`
- `calculate_checksum(self)`
- `update_activity(self)`
- `is_active(self, timeout_seconds)`
- `is_alive(self)`
- ... e mais 35 funções

**Imports principais:**
- `hashlib`
- `json`
- `inspect`
- `sys`
- `os`
- `from dataclasses import ...`
- `from typing import ...`
- `from datetime import ...`
- `logging`
- `from ncnt_base import ...`
- ... e mais 8 imports


---


#### fix_all_8_modules.py

**Tamanho:** 16,505 bytes | **Linhas:** 495

**Classes:**
- `AuroraModuleFixer` (7 métodos)

**Funções:**
- `main()`
- `__init__(self, project_root)`
- `create_backup(self)`
- `fix_database_module(self)`
- `fix_api_init_files(self)`
- `fix_string_modules(self)`
- `generate_report(self)`
- `run_complete_fix(self)`

**Imports principais:**
- `os`
- `sys`
- `logging`
- `subprocess`
- `from pathlib import ...`
- `from datetime import ...`
- `shutil`
- `json`
- `re`


---


#### validate_239_modules.py

**Tamanho:** 11,256 bytes | **Linhas:** 293

**Classes:**
- `AuroraModuleValidator` (6 métodos)

**Funções:**
- `main()`
- `__init__(self, project_root)`
- `find_all_python_modules(self)`
- `validate_module(self, module_path)`
- `validate_all_modules(self, max_workers)`
- `generate_validation_report(self)`
- `save_results(self)`

**Imports principais:**
- `os`
- `sys`
- `json`
- `logging`
- `subprocess`
- `from pathlib import ...`
- `from datetime import ...`
- `from concurrent.futures import ...`
- `from typing import ...`


---


#### modules\ncnt_base.py

**Tamanho:** 7,966 bytes | **Linhas:** 220

**Classes:**
- `ModuleType` extends Enum (0 métodos)
- `AssetClass` extends Enum (0 métodos)
- `TransmissionPriority` extends Enum (0 métodos)
- `NCNTTransmission` (4 métodos)
- `NCNTBaseModule` extends ABC (3 métodos)

**Funções:**
- `validate(self)`
- `_calculate_checksum(self)`
- `to_dict(self)`
- `from_dict(cls, data)`
- `__init__(self, module_name, module_type)`
- `_generate_module_id(self)`
- `update_metric(self, metric_name, value)`

**Imports principais:**
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- `uuid`
- `from pathlib import ...`
- `logging`
- ... e mais 5 imports


---


#### modules\interfaces.py

**Tamanho:** 6,867 bytes | **Linhas:** 185

**Classes:**
- `NCNTTransmission` (5 métodos)
- `NCNTModuleInterface` extends ABC (2 métodos)
- `NCNTStandardConnector` extends NCNTModuleInterface (2 métodos)

**Funções:**
- `__init__(self, transmission_id, source_module, target_module, module_type...)`
- `_calculate_checksum(self)`
- `validate(self)`
- `to_dict(self)`
- `from_dict(cls, data)`
- `__init__(self, module_name, module_type)`
- `get_status(self)`
- `__init__(self, module_name, module_type)`
- `_create_error_response(self, error_message, original_transmission)`

**Imports principais:**
- `from datetime import ...`
- `from typing import ...`
- `json`
- `hashlib`
- `uuid`
- `from abc import ...`


---


#### modules\__init__.py

**Tamanho:** 312 bytes | **Linhas:** 17

**Imports principais:**
- `from interfaces import ...`


---


#### modules\connectors\strategy_connector.py

**Tamanho:** 28 bytes | **Linhas:** 1


---


#### modules\connectors\execution_connector.py

**Tamanho:** 26 bytes | **Linhas:** 1


---


#### modules\connectors\__init__.py

**Tamanho:** 25 bytes | **Linhas:** 1


---


#### modules\connectors\data_connector.py

**Tamanho:** 21 bytes | **Linhas:** 1


---


#### modules\connectors\risk_connector.py

**Tamanho:** 21 bytes | **Linhas:** 1


---

## MONITORING (7 módulos)

### Lista de Módulos

```
06-Monitoramento\Feedback-Loop\action_items.py                                   | C: 0 F:  0
06-Monitoramento\Feedback-Loop\post_mortem.py                                    | C: 0 F:  0
06-Monitoramento\Feedback-Loop\rca_templates.py                                  | C: 0 F:  0
06-Monitoramento\feedbackloop_module.py                                          | C: 2 F:  5
06-Monitoramento\generate_validation_report.py                                   | C: 0 F:  0
06-Monitoramento\neural_connection_monitor_v2.py                                 | C: 3 F: 16
06-Monitoramento\run_validation_scan.py                                          | C: 0 F:  0
```

### Especificações Detalhadas (Top 20)


#### 06-Monitoramento\neural_connection_monitor_v2.py

**Tamanho:** 25,828 bytes | **Linhas:** 616

**Classes:**
- `ConnectionHealth` (1 métodos)
- `ModuleHealthReport` (2 métodos)
- `NeuralConnectionMonitor` (12 métodos)

**Funções:**
- `calculate_score(self)`
- `to_dict(self)`
- `get_health_status(self)`
- `__init__(self, scan_interval_seconds)`
- `start_monitoring(self)`
- `stop_monitoring(self)`
- `scan_all_modules(self)`
- `_test_connection(self, module, connection)`
- `_calculate_module_checksum(self, module)`
- `analyze_health(self, scan_results)`
- `generate_alerts(self, health_reports)`
- `save_health_history(self, health_reports)`
- `get_health_summary(self)`
- `_generate_system_recommendations(self, health_reports)`
- `generate_report(self, filepath)`
- ... e mais 1 funções

**Imports principais:**
- `time`
- `json`
- `from typing import ...`
- `from datetime import ...`
- `logging`
- `threading`
- `hashlib`
- `sys`
- `os`
- `from dataclasses import ...`
- ... e mais 3 imports


---


#### 06-Monitoramento\feedbackloop_module.py

**Tamanho:** 18,934 bytes | **Linhas:** 483

**Classes:**
- `FeedbackLoopModule` extends NCNTBaseModule (4 métodos)
- `NCNTOrchestrator` (1 métodos)

**Funções:**
- `__init__(self)`
- `_get_category_keywords(self, category)`
- `_calculate_priority_score(self, feedback)`
- `_suggest_assignee(self, feedback)`
- `__init__(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 9 imports


---


#### 06-Monitoramento\run_validation_scan.py

**Tamanho:** 1,113 bytes | **Linhas:** 34

**Imports principais:**
- `sys`
- `os`
- `from pathlib import ...`
- `from neural_connection_monitor_v2 import ...`
- `time`


---


#### 06-Monitoramento\generate_validation_report.py

**Tamanho:** 822 bytes | **Linhas:** 26

**Imports principais:**
- `sys`
- `os`
- `from pathlib import ...`
- `from neural_connection_monitor_v2 import ...`


---


#### 06-Monitoramento\Feedback-Loop\rca_templates.py

**Tamanho:** 34 bytes | **Linhas:** 1


---


#### 06-Monitoramento\Feedback-Loop\action_items.py

**Tamanho:** 32 bytes | **Linhas:** 1


---


#### 06-Monitoramento\Feedback-Loop\post_mortem.py

**Tamanho:** 22 bytes | **Linhas:** 1


---

## OPERATIONS (12 módulos)

### Lista de Módulos

```
03-Operacoes-Diarias\Execution-Window\__init__.py                                | C: 0 F:  0
03-Operacoes-Diarias\Execution-Window\executionwindow_module.py                  | C: 1 F:  5
03-Operacoes-Diarias\Execution-Window\throttling.py                              | C: 0 F:  0
03-Operacoes-Diarias\Post-Trade\__init__.py                                      | C: 0 F:  0
03-Operacoes-Diarias\Post-Trade\delta_reports.py                                 | C: 0 F:  0
03-Operacoes-Diarias\Post-Trade\posttradereconciliation_module.py                | C: 1 F:  3
03-Operacoes-Diarias\Post-Trade\reconciliation.py                                | C: 0 F:  0
03-Operacoes-Diarias\Pre-Market\__init__.py                                      | C: 0 F:  0
03-Operacoes-Diarias\Pre-Market\premarketchecklist_module.py                     | C: 1 F:  2
03-Operacoes-Diarias\Real-Time-Dashboard\__init__.py                             | C: 0 F:  0
03-Operacoes-Diarias\Real-Time-Dashboard\dashboard.py                            | C: 0 F:  0
03-Operacoes-Diarias\Real-Time-Dashboard\realtimedashboard_module.py             | C: 1 F: 14
```

### Especificações Detalhadas (Top 20)


#### 03-Operacoes-Diarias\Post-Trade\posttradereconciliation_module.py

**Tamanho:** 32,738 bytes | **Linhas:** 815

**Classes:**
- `PostTradeReconciliationModule` extends NCNTBaseModule (3 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_reconciliation_rules(self)`
- `_group_discrepancies_by_field(self, discrepancies)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 8 imports


---


#### 03-Operacoes-Diarias\Real-Time-Dashboard\realtimedashboard_module.py

**Tamanho:** 28,687 bytes | **Linhas:** 734

**Classes:**
- `RealTimeDashboardModule` extends NCNTBaseModule (14 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_dashboard_config(self)`
- `_format_widget_data(self, widget_type, data, config)`
- `_format_gauge_data(self, data, config)`
- `_format_line_chart_data(self, data, config)`
- `_format_table_data(self, data, config)`
- `_format_bar_chart_data(self, data, config)`
- `_format_status_grid_data(self, data, config)`
- `_initialize_kpi_history(self)`
- `_calculate_trend(self, metric, current_value)`
- `_get_metric_history(self, metric, points)`
- `_get_bar_color(self, metric, value)`
- `_get_status_icon(self, status)`
- `_get_status_color(self, status)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 14 imports


---


#### 03-Operacoes-Diarias\Execution-Window\executionwindow_module.py

**Tamanho:** 22,376 bytes | **Linhas:** 581

**Classes:**
- `ExecutionWindowModule` extends NCNTBaseModule (5 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_market_schedules(self)`
- `_initialize_throttling_rules(self)`
- `_get_next_trading_day(self, asset_class)`
- `_get_next_status_change(self, asset_class, current_status)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 14 imports


---


#### 03-Operacoes-Diarias\Pre-Market\premarketchecklist_module.py

**Tamanho:** 16,721 bytes | **Linhas:** 425

**Classes:**
- `PreMarketChecklistModule` extends NCNTBaseModule (2 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_checklist(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 9 imports


---


#### 03-Operacoes-Diarias\Post-Trade\__init__.py

**Tamanho:** 32 bytes | **Linhas:** 1


---


#### 03-Operacoes-Diarias\Post-Trade\delta_reports.py

**Tamanho:** 30 bytes | **Linhas:** 1


---


#### 03-Operacoes-Diarias\Post-Trade\reconciliation.py

**Tamanho:** 29 bytes | **Linhas:** 1


---


#### 03-Operacoes-Diarias\Pre-Market\__init__.py

**Tamanho:** 27 bytes | **Linhas:** 1


---


#### 03-Operacoes-Diarias\Real-Time-Dashboard\__init__.py

**Tamanho:** 26 bytes | **Linhas:** 1


---


#### 03-Operacoes-Diarias\Execution-Window\throttling.py

**Tamanho:** 24 bytes | **Linhas:** 1


---


#### 03-Operacoes-Diarias\Execution-Window\__init__.py

**Tamanho:** 23 bytes | **Linhas:** 1


---


#### 03-Operacoes-Diarias\Real-Time-Dashboard\dashboard.py

**Tamanho:** 21 bytes | **Linhas:** 1


---

## PROCESSES (16 módulos)

### Lista de Módulos

```
02-Processos-Chave\CI-CD\__init__.py                                             | C: 0 F:  0
02-Processos-Chave\CI-CD\cicdpipeline_module.py                                  | C: 1 F:  2
02-Processos-Chave\CI-CD\stages\build.py                                         | C: 0 F:  0
02-Processos-Chave\CI-CD\stages\deploy.py                                        | C: 0 F:  0
02-Processos-Chave\CI-CD\stages\test.py                                          | C: 0 F:  0
02-Processos-Chave\Incident-Response\__init__.py                                 | C: 0 F:  0
02-Processos-Chave\Incident-Response\incidentresponse_module.py                  | C: 1 F:  7
02-Processos-Chave\Onboarding\__init__.py                                        | C: 0 F:  0
02-Processos-Chave\Onboarding\counterparty_onboarding.py                         | C: 0 F:  0
02-Processos-Chave\Onboarding\data_onboarding.py                                 | C: 0 F:  0
02-Processos-Chave\Onboarding\onboarding_module.py                               | C: 1 F:  4
02-Processos-Chave\Onboarding\strategy_onboarding.py                             | C: 0 F:  0
02-Processos-Chave\QA-Backtesting\__init__.py                                    | C: 0 F:  0
02-Processos-Chave\QA-Backtesting\backtest_engine.py                             | C: 0 F:  0
02-Processos-Chave\QA-Backtesting\qabacktesting_module.py                        | C: 1 F:  7
02-Processos-Chave\backtesting\backtest_runner_v3.py                             | C: 6 F: 26
```

### Especificações Detalhadas (Top 20)


#### 02-Processos-Chave\backtesting\backtest_runner_v3.py

**Tamanho:** 47,098 bytes | **Linhas:** 1166

**Classes:**
- `BacktestResult` extends Enum (0 métodos)
- `StrategyPerformance` extends Enum (0 métodos)
- `ConfidenceInterval` (2 métodos)
- `TradeRecord` (1 métodos)
- `BacktestMetrics` (4 métodos)
- `BacktestRunnerV3` (18 métodos)

**Funções:**
- `sample_strategy(data)`
- `sharpe_ratio(sharpe, n_returns, confidence)`
- `annual_return(returns, confidence)`
- `calculate_pnl(self)`
- `to_dict(self)`
- `calculate_composite_score(self)`
- `_get_performance_category(self)`
- `_get_validation_status(self)`
- `__init__(self, initial_capital, commission_pct, slippage_bps, risk_free_rate...)`
- `run_backtest(self, strategy, symbol, start_date, end_date...)`
- `_load_historical_data(self, symbol, start_date, end_date, timeframe)`
- `_execute_strategy(self, strategy, data)`
- `_execute_trades(self, signals, data, include_costs)`
- `_calculate_position_size(self, capital, confidence, max_position_pct)`
- `_calculate_returns(self, equity_curve)`
- ... e mais 11 funções

**Imports principais:**
- `numpy`
- `pandas`
- `from decimal import ...`
- `from typing import ...`
- `from datetime import ...`
- `json`
- `hashlib`
- `logging`
- `asyncio`
- `from dataclasses import ...`
- ... e mais 8 imports


---


#### 02-Processos-Chave\CI-CD\cicdpipeline_module.py

**Tamanho:** 25,889 bytes | **Linhas:** 630

**Classes:**
- `CICDPipelineModule` extends NCNTBaseModule (2 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_stages(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 13 imports


---


#### 02-Processos-Chave\Onboarding\onboarding_module.py

**Tamanho:** 24,132 bytes | **Linhas:** 567

**Classes:**
- `OnboardingModule` extends NCNTBaseModule (4 métodos)

**Funções:**
- `__init__(self)`
- `_create_data_onboarding_pipeline(self)`
- `_create_strategy_onboarding_pipeline(self)`
- `_create_counterparty_onboarding_pipeline(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 12 imports


---


#### 02-Processos-Chave\QA-Backtesting\qabacktesting_module.py

**Tamanho:** 23,107 bytes | **Linhas:** 539

**Classes:**
- `QABacktestingModule` extends NCNTBaseModule (7 métodos)

**Funções:**
- `__init__(self)`
- `_assess_sharpe_ratio(self, sharpe_ratio)`
- `_assess_drawdown(self, max_drawdown)`
- `_assess_win_rate(self, win_rate)`
- `_assess_profit_factor(self, profit_factor)`
- `_calculate_consistency(self, backtest_results)`
- `_assess_data_quality(self, data_summary)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 15 imports


---


#### 02-Processos-Chave\Incident-Response\incidentresponse_module.py

**Tamanho:** 21,761 bytes | **Linhas:** 555

**Classes:**
- `IncidentResponseModule` extends NCNTBaseModule (7 métodos)

**Funções:**
- `__init__(self)`
- `_initialize_playbooks(self)`
- `_initialize_escalation_paths(self)`
- `_initialize_communication_templates(self)`
- `_assemble_sev1_response_team(self)`
- `_assemble_sev2_response_team(self)`
- `_assemble_general_response_team(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_base import ...`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- ... e mais 8 imports


---


#### 02-Processos-Chave\CI-CD\__init__.py

**Tamanho:** 34 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\Incident-Response\__init__.py

**Tamanho:** 33 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\QA-Backtesting\__init__.py

**Tamanho:** 33 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\Onboarding\counterparty_onboarding.py

**Tamanho:** 28 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\Onboarding\strategy_onboarding.py

**Tamanho:** 28 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\QA-Backtesting\backtest_engine.py

**Tamanho:** 22 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\Onboarding\data_onboarding.py

**Tamanho:** 21 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\Onboarding\__init__.py

**Tamanho:** 17 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\CI-CD\stages\deploy.py

**Tamanho:** 14 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\CI-CD\stages\build.py

**Tamanho:** 13 bytes | **Linhas:** 1


---


#### 02-Processos-Chave\CI-CD\stages\test.py

**Tamanho:** 12 bytes | **Linhas:** 1


---

## ROOT (121 módulos)

### Lista de Módulos

```
AURORA_ETAPA_A_EXECUCAO_AUTOMATICA_AIC.py                                        | C: 1 F: 20
AURORA_FINAL_COMPLETO_100.py                                                     | C: 4 F:  8
AURORA_FINAL_EXECUCAO_AIC_V5.1.py                                                | C: 4 F:  8
AURORA_TEST_MODE_NO_STOPS.py                                                     | C: 4 F: 12
AURORA_V5_CORRECAO_DEFINITIVA_100_PERCENT.py                                     | C: 1 F:  8
AURORA_V5_MAPEAMENTO_COMPLETO_274_MODULOS.py                                     | C: 0 F:  3
AURORA_V5_VALIDACAO_DEFINITIVA_100_PERCENT.py                                    | C: 1 F:  5
AURORA_V5_VERIFICACAO_FINAL_252_MODULOS.py                                       | C: 1 F:  8
CONVERTER_JSON_PARA_MD.py                                                        | C: 0 F:  3
DIAGNOSTICO_SINAIS.py                                                            | C: 0 F:  2
EXECUTAR_FASE_BETA_FORCADA.py                                                    | C: 0 F:  0
GENERATE_COMPLETE_TECHNICAL_SPEC.py                                              | C: 1 F:  8
HANTEC_STOPS_DISCOVERY.py                                                        | C: 0 F:  3
MT5_EXECUTOR_PROFISSIONAL.py                                                     | C: 1 F:  8
SOLUCAO_DEFINITIVA_MT5.py                                                        | C: 0 F:  3
aurora_etapa_a.py                                                                | C: 5 F: 15
aurora_etapa_b.py                                                                | C: 0 F:  0
aurora_etapa_c.py                                                                | C: 0 F:  0
aurora_etapa_d.py                                                                | C: 0 F:  0
aurora_etapa_e.py                                                                | C: 0 F:  0
aurora_strategies_integration.py                                                 | C: 1 F:  5
complete_integration.py                                                          | C: 0 F:  2
create_structure.py                                                              | C: 0 F:  1
executive_presentation.py                                                        | C: 1 F: 16
fase2_ativar_nucleo_tier0.py                                                     | C: 0 F:  0
fase3_migracao_massa.py                                                          | C: 0 F:  6
fase4_validacao_final.py                                                         | C: 0 F:  0
integrate_ncnt.py                                                                | C: 0 F:  3
main.py                                                                          | C: 0 F:  0
main_ncnt.py                                                                     | C: 0 F:  0
ncnt_scan.py                                                                     | C: 2 F:  1
ncnt_system_complete.py                                                          | C:25 F: 93
ncnt_wrapper_generator.py                                                        | C: 0 F:  4
test_mt5_integration.py                                                          | C: 0 F:  5
tests\test_strategies.py                                                         | C: 4 F: 13
verificar_json.py                                                                | C: 0 F:  0
visual_presentation.py                                                           | C: 1 F: 10
visual_presentation_simple.py                                                    | C: 1 F:  9
wrappers_v2\__init___wrapper.py                                                  | C: 1 F:  2
wrappers_v2\ab_testing_wrapper.py                                                | C: 1 F:  2
wrappers_v2\allocation_engine_wrapper.py                                         | C: 1 F:  2
wrappers_v2\alpha_momentum_wrapper.py                                            | C: 1 F:  2
wrappers_v2\api_gateway_wrapper.py                                               | C: 1 F:  2
wrappers_v2\audit_system_complete_wrapper.py                                     | C: 1 F:  2
wrappers_v2\audit_trail_wrapper.py                                               | C: 1 F:  2
wrappers_v2\aurora_etapa_a_wrapper.py                                            | C: 1 F:  4
wrappers_v2\backtest_engine_wrapper.py                                           | C: 1 F:  2
wrappers_v2\backtest_runner_v3_wrapper.py                                        | C: 1 F:  2
wrappers_v2\base_strategy_wrapper.py                                             | C: 1 F:  2
wrappers_v2\breakout_detection_wrapper.py                                        | C: 1 F:  2
wrappers_v2\build_wrapper.py                                                     | C: 1 F:  2
wrappers_v2\capital_manager_wrapper.py                                           | C: 1 F:  2
wrappers_v2\cicdpipeline_module_wrapper.py                                       | C: 1 F:  2
wrappers_v2\circuit_breakers_wrapper.py                                          | C: 1 F:  2
wrappers_v2\complete_integration_wrapper.py                                      | C: 1 F:  2
wrappers_v2\complexity_guard_wrapper.py                                          | C: 1 F:  2
wrappers_v2\compliance_module_wrapper.py                                         | C: 1 F:  2
wrappers_v2\connection_wrapper.py                                                | C: 1 F:  2
wrappers_v2\core_engine_wrapper.py                                               | C: 1 F:  2
wrappers_v2\coreengine_module_wrapper.py                                         | C: 1 F:  2
wrappers_v2\counterparty_onboarding_wrapper.py                                   | C: 1 F:  2
wrappers_v2\create_structure_wrapper.py                                          | C: 1 F:  2
wrappers_v2\dashboard_wrapper.py                                                 | C: 1 F:  2
wrappers_v2\data_layer_wrapper.py                                                | C: 1 F:  2
wrappers_v2\data_onboarding_wrapper.py                                           | C: 1 F:  2
wrappers_v2\delta_reports_wrapper.py                                             | C: 1 F:  2
wrappers_v2\deploy_wrapper.py                                                    | C: 1 F:  2
wrappers_v2\executionwindow_module_wrapper.py                                    | C: 1 F:  2
wrappers_v2\executive_presentation_wrapper.py                                    | C: 1 F:  2
wrappers_v2\feedbackloop_module_wrapper.py                                       | C: 1 F:  2
wrappers_v2\fix_report_errors_wrapper.py                                         | C: 1 F:  2
wrappers_v2\generate_complete_report_wrapper.py                                  | C: 1 F:  2
wrappers_v2\generate_ultra_complete_report_wrapper.py                            | C: 1 F:  2
wrappers_v2\genesis_includes_v3_complete_wrapper.py                              | C: 1 F:  2
wrappers_v2\genesis_includes_wrapper.py                                          | C: 1 F:  2
wrappers_v2\governance_module_wrapper.py                                         | C: 1 F:  2
wrappers_v2\incidentresponse_module_wrapper.py                                   | C: 1 F:  2
wrappers_v2\innovationlab_module_wrapper.py                                      | C: 1 F:  2
wrappers_v2\integrate_ncnt_wrapper.py                                            | C: 1 F:  2
wrappers_v2\integration_gate_v2_wrapper.py                                       | C: 1 F:  2
wrappers_v2\integration_gate_v3_wrapper.py                                       | C: 1 F:  2
wrappers_v2\interface_wrapper.py                                                 | C: 1 F:  2
wrappers_v2\main_ncnt_wrapper.py                                                 | C: 1 F:  2
wrappers_v2\main_wrapper.py                                                      | C: 1 F:  2
wrappers_v2\mean_reversion_wrapper.py                                            | C: 1 F:  2
wrappers_v2\models_wrapper.py                                                    | C: 1 F:  2
wrappers_v2\moduleregistry_wrapper.py                                            | C: 1 F:  2
wrappers_v2\ncnt_base_wrapper.py                                                 | C: 1 F:  2
wrappers_v2\ncnt_cli_wrapper.py                                                  | C: 1 F:  2
wrappers_v2\ncnt_orchestrator_complete_wrapper.py                                | C: 1 F:  2
wrappers_v2\ncnt_scan_wrapper.py                                                 | C: 1 F:  2
wrappers_v2\ncnt_system_complete_wrapper.py                                      | C: 1 F:  2
wrappers_v2\onboarding_module_wrapper.py                                         | C: 1 F:  2
wrappers_v2\order_management_wrapper.py                                          | C: 1 F:  2
wrappers_v2\posttradereconciliation_module_wrapper.py                            | C: 1 F:  2
wrappers_v2\premarketchecklist_module_wrapper.py                                 | C: 1 F:  2
wrappers_v2\prototypes_wrapper.py                                                | C: 1 F:  2
wrappers_v2\qabacktesting_module_wrapper.py                                      | C: 1 F:  2
wrappers_v2\realtimedashboard_module_wrapper.py                                  | C: 1 F:  2
wrappers_v2\reconciliation_wrapper.py                                            | C: 1 F:  2
wrappers_v2\reg_tracker_wrapper.py                                               | C: 1 F:  2
wrappers_v2\regulatory_context_wrapper.py                                        | C: 1 F:  2
wrappers_v2\report_generator_wrapper.py                                          | C: 1 F:  2
wrappers_v2\restore_executive_report_wrapper.py                                  | C: 1 F:  2
wrappers_v2\risk_engine_wrapper.py                                               | C: 1 F:  2
wrappers_v2\risk_module_wrapper.py                                               | C: 1 F:  2
wrappers_v2\run_complete_audit_wrapper.py                                        | C: 1 F:  2
wrappers_v2\smart_routing_wrapper.py                                             | C: 1 F:  2
wrappers_v2\sops_module_wrapper.py                                               | C: 1 F:  2
wrappers_v2\strategies_wrapper.py                                                | C: 1 F:  2
wrappers_v2\strategy_module_wrapper.py                                           | C: 1 F:  2
wrappers_v2\strategy_onboarding_wrapper.py                                       | C: 1 F:  2
wrappers_v2\strategy_template_wrapper.py                                         | C: 1 F:  2
wrappers_v2\test_module_v2_wrapper.py                                            | C: 1 F:  2
wrappers_v2\test_wrapper.py                                                      | C: 1 F:  2
wrappers_v2\throttling_wrapper.py                                                | C: 1 F:  2
wrappers_v2\tier1_validator_v3_complete_wrapper.py                               | C: 1 F:  2
wrappers_v2\tier1_validator_v3_wrapper.py                                        | C: 1 F:  2
wrappers_v2\treasury_module_wrapper.py                                           | C: 1 F:  2
wrappers_v2\visual_presentation_simple_wrapper.py                                | C: 1 F:  2
wrappers_v2\visual_presentation_wrapper.py                                       | C: 1 F:  2
```

### Especificações Detalhadas (Top 20)


#### ncnt_system_complete.py

**Tamanho:** 322,491 bytes | **Linhas:** 7855

**Classes:**
- `ModuleType` extends Enum (0 métodos)
- `AssetClass` extends Enum (0 métodos)
- `TransmissionPriority` extends Enum (0 métodos)
- `NCNTTransmission` (4 métodos)
- `NCNTBaseModule` extends ABC (3 métodos)
- `GovernanceModule` extends NCNTBaseModule (2 métodos)
- `CapitalAllocation` (1 métodos)
- `TreasuryModule` extends NCNTBaseModule (2 métodos)
- `CoreEngineModule` extends NCNTBaseModule (2 métodos)
- `StrategyModule` extends NCNTBaseModule (4 métodos)
- `RiskModule` extends NCNTBaseModule (13 métodos)
- `ComplianceModule` extends NCNTBaseModule (5 métodos)
- `InnovationLabModule` extends NCNTBaseModule (4 métodos)
- `CICDPipelineModule` extends NCNTBaseModule (2 métodos)
- `QABacktestingModule` extends NCNTBaseModule (7 métodos)
- `OnboardingModule` extends NCNTBaseModule (4 métodos)
- `IncidentResponseModule` extends NCNTBaseModule (7 métodos)
- `PreMarketChecklistModule` extends NCNTBaseModule (2 métodos)
- `ExecutionWindowModule` extends NCNTBaseModule (5 métodos)
- `RealTimeDashboardModule` extends NCNTBaseModule (14 métodos)
- `PostTradeReconciliationModule` extends NCNTBaseModule (3 métodos)
- `ModuleRegistry` extends NCNTBaseModule (2 métodos)
- `SOPsModule` extends NCNTBaseModule (2 métodos)
- `FeedbackLoopModule` extends NCNTBaseModule (4 métodos)
- `NCNTOrchestrator` (1 métodos)

**Funções:**
- `validate(self)`
- `_calculate_checksum(self)`
- `to_dict(self)`
- `from_dict(cls, data)`
- `__init__(self, module_name, module_type)`
- `_generate_module_id(self)`
- `update_metric(self, metric_name, value)`
- `__init__(self)`
- `_create_default_charter(self)`
- `to_dict(self)`
- `__init__(self)`
- `_get_target_percentage(self, strategy_id)`
- `__init__(self)`
- `_find_backup_module(self, module_name)`
- `__init__(self, strategy_name)`
- ... e mais 78 funções

**Imports principais:**
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from enum import ...`
- `json`
- `yaml`
- `hashlib`
- `uuid`
- `from pathlib import ...`
- `logging`
- ... e mais 40 imports


---


#### AURORA_FINAL_EXECUCAO_AIC_V5.1.py

**Tamanho:** 42,650 bytes | **Linhas:** 1678

**Classes:**
- `ScientificHypothesisTester` (2 métodos)
- `AuroraInfrastructureValidator` (1 métodos)
- `AuroraAdvancedEvolution` (2 métodos)
- `AuroraAICExecutor` (2 métodos)

**Funções:**
- `__init__(self)`
- `_apply_ma_crossover_strategy(self, data, symbol)`
- `__init__(self)`
- `__init__(self)`
- `generate_evolution_roadmap(self, phase_alpha_passed, phase_beta_passed)`
- `__init__(self)`
- `generate_final_report(self, results)`
- `convert_to_native(obj)`

**Imports principais:**
- `asyncio`
- `json`
- `sys`
- `logging`
- `from datetime import ...`
- `from pathlib import ...`
- `from typing import ...`
- `pandas`
- `numpy`
- `yfinance`
- ... e mais 8 imports


---


#### AURORA_ETAPA_A_EXECUCAO_AUTOMATICA_AIC.py

**Tamanho:** 40,774 bytes | **Linhas:** 970

**Classes:**
- `AuroraEtapaAExecutor` (19 métodos)

**Funções:**
- `main()`
- `__init__(self)`
- `executar_com_seguranca(self, comando, descricao, timeout)`
- `verificar_ambiente(self)`
- `validar_modulos_criticos(self)`
- `executar_teste_sistema(self)`
- `coletar_dados_mercado(self)`
- `calcular_metricas_consolidadas(self, dados_mercado)`
- `analisar_pontos_criticos_ceo(self)`
- `analisar_ia_agents(self)`
- `analisar_comunicacao_modulos(self)`
- `analisar_pipeline_estrategias(self)`
- `analisar_prevencao_conflitos(self)`
- `analisar_gestao_profit(self)`
- `calcular_decisao_final(self)`
- ... e mais 5 funções

**Imports principais:**
- `os`
- `sys`
- `json`
- `logging`
- `subprocess`
- `importlib.util`
- `from pathlib import ...`
- `from datetime import ...`
- `from typing import ...`
- `time`
- ... e mais 1 imports


---


#### AURORA_FINAL_COMPLETO_100.py

**Tamanho:** 40,314 bytes | **Linhas:** 941

**Classes:**
- `AuroraStrategySystem` (1 métodos)
- `MT5Executor` (1 métodos)
- `AuroraTradingSystem` (2 métodos)
- `SimpleTradeSignal` (1 métodos)

**Funções:**
- `safe_convert_to_list(data)`
- `robust_market_data_fetch(symbol, period, interval)`
- `__init__(self)`
- `__init__(self, simulation_mode, use_real)`
- `__init__(self, use_real_mt5)`
- `stop(self)`
- `safe_float_list(data_col)`
- `__init__(self, signal_dict)`

**Imports principais:**
- `asyncio`
- `json`
- `sys`
- `logging`
- `traceback`
- `from datetime import ...`
- `from typing import ...`
- `from pathlib import ...`
- `pandas`
- `numpy`
- ... e mais 7 imports


---


#### AURORA_TEST_MODE_NO_STOPS.py

**Tamanho:** 40,124 bytes | **Linhas:** 939

**Classes:**
- `MT5NoStopsExecutor` (5 métodos)
- `AuroraStrategies` (1 métodos)
- `AuroraMonitor` (4 métodos)
- `AuroraTestSystem` (2 métodos)

**Funções:**
- `__init__(self, simulation_mode)`
- `initialize_mt5_basic(self)`
- `execute_order_no_stops(self, symbol, order_type, volume)`
- `close_all_test_orders(self)`
- `shutdown(self)`
- `__init__(self)`
- `__init__(self)`
- `log_cycle(self, cycle_data)`
- `get_summary(self)`
- `print_real_time_status(self)`
- `__init__(self, simulation_mode)`
- `stop(self)`

**Imports principais:**
- `asyncio`
- `json`
- `sys`
- `logging`
- `traceback`
- `from datetime import ...`
- `from typing import ...`
- `pandas`
- `numpy`
- `yfinance`
- ... e mais 8 imports


---


#### aurora_etapa_a.py

**Tamanho:** 31,135 bytes | **Linhas:** 802

**Classes:**
- `Config` (0 métodos)
- `TestResult` (0 métodos)
- `PointAnalysis` (0 métodos)
- `AnalysisReport` (0 métodos)
- `AuroraEtapaAAnalyzer` (9 métodos)

**Funções:**
- `get_market_data(symbol, days)`
- `calculate_sharpe(returns, risk_free_rate)`
- `calculate_profit_factor(trades)`
- `calculate_max_drawdown(equity_curve)`
- `apply_transaction_costs(price, cost_pct, slippage_pct)`
- `main()`
- `__init__(self)`
- `test_ia_agents_architecture(self)`
- `test_ia_module_communication(self)`
- `test_strategy_pipeline(self)`
- `test_conflict_prevention(self)`
- `test_profit_learning(self)`
- `run_complete_analysis(self)`
- `_analyze_point(self, point_name, tests)`
- `save_report(self, report, format)`

**Imports principais:**
- `pandas`
- `numpy`
- `yfinance`
- `json`
- `logging`
- `asyncio`
- `from datetime import ...`
- `from typing import ...`
- `from dataclasses import ...`
- `from pathlib import ...`
- ... e mais 13 imports


---


#### ncnt_scan.py

**Tamanho:** 21,545 bytes | **Linhas:** 524

**Classes:**
- `ModuleType` (0 métodos)
- `AICNCNTScanner` (1 métodos)

**Funções:**
- `__init__(self)`

**Imports principais:**
- `json`
- `hashlib`
- `inspect`
- `asyncio`
- `os`
- `sys`
- `from pathlib import ...`
- `from datetime import ...`
- `from typing import ...`


---


#### executive_presentation.py

**Tamanho:** 18,762 bytes | **Linhas:** 511

**Classes:**
- `AuroraExecutivePresentation` (15 métodos)

**Funções:**
- `main()`
- `__init__(self)`
- `generate_presentation(self)`
- `_header(self)`
- `_executive_summary(self)`
- `_system_architecture(self)`
- `_core_components(self)`
- `_risk_management(self)`
- `_governance_compliance(self)`
- `_technology_stack(self)`
- `_performance_metrics(self)`
- `_implementation_status(self)`
- `_strategic_roadmap(self)`
- `_conclusion(self)`
- `save_to_file(self, filename)`
- ... e mais 1 funções

**Imports principais:**
- `os`
- `sys`
- `from datetime import ...`
- `from pathlib import ...`
- `json`


---


#### AURORA_V5_VERIFICACAO_FINAL_252_MODULOS.py

**Tamanho:** 15,382 bytes | **Linhas:** 398

**Classes:**
- `VerificadorFinal` (7 métodos)

**Funções:**
- `main()`
- `__init__(self)`
- `encontrar_modulos_validos(self)`
- `verificar_modulo_estrito(self, modulo_path)`
- `contar_linhas(self, arquivo_path)`
- `verificar_modulos_criticos(self)`
- `executar_verificacao_completa(self)`
- `gerar_relatorio_final(self)`

**Imports principais:**
- `os`
- `sys`
- `json`
- `from pathlib import ...`
- `from datetime import ...`
- `subprocess`
- `importlib.util`


---


#### aurora_strategies_integration.py

**Tamanho:** 14,859 bytes | **Linhas:** 318

**Classes:**
- `AuroraStrategiesManager` (4 métodos)

**Funções:**
- `__init__(self, mt5_enabled, mt5_login, mt5_password, mt5_server)`
- `initialize_strategies(self)`
- `convert_yfinance_to_market_data(self, data, symbol)`
- `get_strategies_status(self)`
- `safe_to_list(series_or_df, max_items)`

**Imports principais:**
- `sys`
- `logging`
- `from pathlib import ...`
- `from datetime import ...`
- `from typing import ...`
- `from decimal import ...`
- `pandas`
- `numpy`
- `yfinance`
- `asyncio`
- ... e mais 4 imports


---


#### AURORA_V5_CORRECAO_DEFINITIVA_100_PERCENT.py

**Tamanho:** 13,649 bytes | **Linhas:** 389

**Classes:**
- `CorretorDefinitivo` (7 métodos)

**Funções:**
- `main()`
- `__init__(self)`
- `criar_backup_total(self)`
- `encontrar_modulos_com_problema(self)`
- `corrigir_modulo(self, info_modulo)`
- `criar_modulos_faltantes(self)`
- `executar_correcao_completa(self)`
- `validar_100_porcento(self)`

**Imports principais:**
- `os`
- `sys`
- `re`
- `from pathlib import ...`
- `from datetime import ...`
- `shutil`
- `subprocess`


---


#### HANTEC_STOPS_DISCOVERY.py

**Tamanho:** 12,049 bytes | **Linhas:** 306

**Funções:**
- `discover_minimal_stops(symbol, test_volume)`
- `test_all_cryptos()`
- `generate_recommendation(results)`

**Imports principais:**
- `MetaTrader5`
- `logging`
- `from datetime import ...`
- `time`
- `traceback`


---


#### MT5_EXECUTOR_PROFISSIONAL.py

**Tamanho:** 11,023 bytes | **Linhas:** 298

**Classes:**
- `MT5ExecutorProfissional` (7 métodos)

**Funções:**
- `main()`
- `__init__(self)`
- `initialize(self)`
- `_discover_symbols(self)`
- `get_symbol_mt5(self, symbol)`
- `is_market_open(self, symbol)`
- `execute_order(self, symbol, order_type, volume)`
- `shutdown(self)`

**Imports principais:**
- `MetaTrader5`
- `logging`
- `from datetime import ...`
- `from typing import ...`


---


#### ncnt_wrapper_generator.py

**Tamanho:** 10,238 bytes | **Linhas:** 262

**Funções:**
- `extract_main_function(module_path)`
- `find_module_file(module_name)`
- `generate_wrapper(module_name, module_path, output_dir)`
- `main()`

**Imports principais:**
- `os`
- `re`
- `from pathlib import ...`


---


#### GENERATE_COMPLETE_TECHNICAL_SPEC.py

**Tamanho:** 10,231 bytes | **Linhas:** 296

**Classes:**
- `ModuleAnalyzer` (5 métodos)

**Funções:**
- `generate_complete_spec()`
- `generate_spec_document(categorized, all_specs, total)`
- `generate_module_detail(spec)`
- `__init__(self, root_path)`
- `find_all_modules(self)`
- `analyze_module(self, module_path)`
- `_get_name(self, node)`
- `categorize_module(self, path)`

**Imports principais:**
- `ast`
- `os`
- `from pathlib import ...`
- `from typing import ...`
- `from datetime import ...`
- `json`


---


#### create_structure.py

**Tamanho:** 9,359 bytes | **Linhas:** 227

**Funções:**
- `create_structure(base_path, structure, prefix)`

**Imports principais:**
- `os`
- `from pathlib import ...`
- `sys`
- `io`


---


#### fase3_migracao_massa.py

**Tamanho:** 9,189 bytes | **Linhas:** 279

**Funções:**
- `find_module_file(module_name)`
- `create_wrapper(module_name, module_path, output_dir)`
- `migrate_critical_modules()`
- `migrate_legacy_modules()`
- `migrate_standalone_modules()`
- `main()`

**Imports principais:**
- `sys`
- `os`
- `re`
- `shutil`
- `from pathlib import ...`
- `from typing import ...`
- `importlib.util`


---


#### visual_presentation.py

**Tamanho:** 9,110 bytes | **Linhas:** 273

**Classes:**
- `Colors` (0 métodos)

**Funções:**
- `clear_screen()`
- `print_header(text)`
- `print_section(text)`
- `print_success(text)`
- `print_info(text)`
- `print_warning(text)`
- `print_error(text)`
- `animate_text(text, delay)`
- `check_api()`
- `main()`

**Imports principais:**
- `time`
- `sys`
- `from pathlib import ...`
- `from datetime import ...`
- `os`
- `requests`


---


#### wrappers_v2\aurora_etapa_a_wrapper.py

**Tamanho:** 8,971 bytes | **Linhas:** 244

**Classes:**
- `AuroraEtapaAAnalyzerWrapper` extends NCNTModule (4 métodos)

**Funções:**
- `__init__(self, config)`
- `_establish_neural_connections(self)`
- `execute_analysis(self)`
- `_perform_module_specific_compliance_checks(self)`

**Imports principais:**
- `sys`
- `from pathlib import ...`
- `from modules.ncnt_module_template_v2 import ...`
- `from datetime import ...`
- `from typing import ...`
- `logging`
- `sys`
- `from pathlib import ...`
- `from importlib import ...`
- `from aurora_etapa_a import ...`
- ... e mais 2 imports


---


#### AURORA_V5_MAPEAMENTO_COMPLETO_274_MODULOS.py

**Tamanho:** 8,859 bytes | **Linhas:** 254

**Funções:**
- `mapear_modulos_completos(project_root)`
- `gerar_relatorio_detalhado(resultados)`
- `main()`

**Imports principais:**
- `os`
- `sys`
- `json`
- `from pathlib import ...`
- `from datetime import ...`
- `subprocess`
- `importlib.util`


---
