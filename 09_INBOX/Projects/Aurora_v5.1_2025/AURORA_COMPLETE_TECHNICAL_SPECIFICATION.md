# AURORA v5.1 - Complete Technical Specification
**Document ID:** TS-AURORA-5.1-COMPLETE-20251221  
**Classification:** Technical Specification  
**Format:** IEEE/IETF Standard  
**Version:** 5.1.0  
**Date:** 2025-12-21  
**Status:** Production  
**Total Modules:** 259

---

## 1. EXECUTIVE SUMMARY

```
SYSTEM: AURORA v5.1
TOTAL_MODULES: 259
ARCHITECTURE: NCNT (Neural Central Transmission Core)
PATTERN: Hierarchical Modular Bank-Like
LANGUAGE: Python 3.8+
COMPLIANCE: Tier-0 Institutional
```

### Module Distribution

- **Core**: 5 modules
- **Departments**: 40 modules
- **Documentation**: 1 modules
- **Governance**: 28 modules
- **Infrastructure**: 17 modules
- **Modules**: 10 modules
- **Monitoring**: 7 modules
- **Operations**: 12 modules
- **Processes**: 16 modules
- **Root**: 123 modules


---

## 2. MODULE SPECIFICATIONS

### 2.1 Module Index by Category


#### Core (5 modules)

```
system_core\__init__.py                                                          | C: 0 F:  0
system_core\message_bus.py                                                       | C: 1 F:  4
system_core\ncnt_orchestrator_complete.py                                        | ERROR
system_core\orchestrator.py                                                      | C: 1 F:  5
system_core\registry.py                                                          | C: 1 F:  7
```

#### Departments (40 modules)

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

#### Documentation (1 modules)

```
05-Documentacao\sops_module.py                                                   | C: 1 F:  2
```

#### Governance (28 modules)

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

#### Infrastructure (17 modules)

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

#### Modules (10 modules)

```
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
```

#### Monitoring (7 modules)

```
06-Monitoramento\Feedback-Loop\action_items.py                                   | C: 0 F:  0
06-Monitoramento\Feedback-Loop\post_mortem.py                                    | C: 0 F:  0
06-Monitoramento\Feedback-Loop\rca_templates.py                                  | C: 0 F:  0
06-Monitoramento\feedbackloop_module.py                                          | C: 2 F:  5
06-Monitoramento\generate_validation_report.py                                   | C: 0 F:  0
06-Monitoramento\neural_connection_monitor_v2.py                                 | C: 3 F: 16
06-Monitoramento\run_validation_scan.py                                          | C: 0 F:  0
```

#### Operations (12 modules)

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

#### Processes (16 modules)

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

#### Root (123 modules)

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
fix_all_8_modules.py                                                             | C: 1 F:  8
integrate_ncnt.py                                                                | C: 0 F:  3
main.py                                                                          | C: 0 F:  0
main_ncnt.py                                                                     | C: 0 F:  0
ncnt_scan.py                                                                     | C: 2 F:  1
ncnt_system_complete.py                                                          | C:25 F: 93
ncnt_wrapper_generator.py                                                        | C: 0 F:  4
test_mt5_integration.py                                                          | C: 0 F:  5
tests\test_strategies.py                                                         | C: 4 F: 13
validate_239_modules.py                                                          | C: 1 F:  7
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

---

## 3. DETAILED MODULE SPECIFICATIONS


---

## 4. COMPLETE MODULE LIST

```
00-Governanca\__init__.py
00-Governanca\audit_system_complete.py
00-Governanca\complete_activation_final.py
00-Governanca\complexity_guard.py
00-Governanca\fix_report_errors.py
00-Governanca\generate_complete_report.py
00-Governanca\generate_complete_technical_report.py
00-Governanca\generate_technical_report.py
00-Governanca\generate_ultra_complete_report.py
00-Governanca\genesis_includes.py
00-Governanca\genesis_includes_v3_complete.py
00-Governanca\governance_module.py
00-Governanca\integration_gate_v2.py
00-Governanca\integration_gate_v3.py
00-Governanca\prepare_fix_environment.py
00-Governanca\process_fix_file.py
00-Governanca\quantum_firewall.py
00-Governanca\regulatory_context.py
00-Governanca\restore_executive_report.py
00-Governanca\run_complete_audit.py
00-Governanca\script_1_command_injection_test.py
00-Governanca\script_2_smoke_test_critical_modules.py
00-Governanca\script_3_compliance_quick_validator.py
00-Governanca\script_4_integration_score_calculator.py
00-Governanca\script_5_master_test_runner.py
00-Governanca\test_module_v2.py
00-Governanca\tier1_risk_validator.py
00-Governanca\validate_upgrade_proposal.py
01-Departamentos\AGENTS\CEO_Agent.py
01-Departamentos\AGENTS\CFO_Agent.py
01-Departamentos\AGENTS\CKO_Agent.py
01-Departamentos\AGENTS\CTO_Agent.py
01-Departamentos\Compliance-Audit\__init__.py
01-Departamentos\Compliance-Audit\audit_trail.py
01-Departamentos\Compliance-Audit\compliance_module.py
01-Departamentos\Compliance-Audit\reg_tracker.py
01-Departamentos\Compliance-Audit\report_generator.py
01-Departamentos\Engineering-Infra\__init__.py
01-Departamentos\Engineering-Infra\api_gateway.py
01-Departamentos\Engineering-Infra\core_engine.py
01-Departamentos\Engineering-Infra\coreengine_module.py
01-Departamentos\Engineering-Infra\data_layer.py
01-Departamentos\Execution-Trading\__init__.py
01-Departamentos\Execution-Trading\order_management.py
01-Departamentos\Execution-Trading\smart_routing.py
01-Departamentos\Execution-Trading\strategies\__init__.py
01-Departamentos\Execution-Trading\strategies\alpha_momentum.py
01-Departamentos\Execution-Trading\strategies\base_strategy.py
01-Departamentos\Execution-Trading\strategies\breakout_detection.py
01-Departamentos\Execution-Trading\strategies\mean_reversion.py
01-Departamentos\Execution-Trading\strategy_module.py
01-Departamentos\Execution-Trading\strategy_modules\__init__.py
01-Departamentos\Execution-Trading\strategy_modules\interface.py
01-Departamentos\Execution-Trading\strategy_modules\templates\strategy_template.py
01-Departamentos\Innovation-Lab\__init__.py
01-Departamentos\Innovation-Lab\ab_testing.py
01-Departamentos\Innovation-Lab\innovationlab_module.py
01-Departamentos\Innovation-Lab\prototypes.py
01-Departamentos\Risk-Controls\__init__.py
01-Departamentos\Risk-Controls\circuit_breakers.py
01-Departamentos\Risk-Controls\risk_engine.py
01-Departamentos\Risk-Controls\risk_module.py
01-Departamentos\Risk-Controls\tier1_validator_v3.py
01-Departamentos\Risk-Controls\tier1_validator_v3_complete.py
01-Departamentos\Treasury-Capital\__init__.py
01-Departamentos\Treasury-Capital\allocation_engine.py
01-Departamentos\Treasury-Capital\capital_manager.py
01-Departamentos\Treasury-Capital\treasury_module.py
02-Processos-Chave\CI-CD\__init__.py
02-Processos-Chave\CI-CD\cicdpipeline_module.py
02-Processos-Chave\CI-CD\stages\build.py
02-Processos-Chave\CI-CD\stages\deploy.py
02-Processos-Chave\CI-CD\stages\test.py
02-Processos-Chave\Incident-Response\__init__.py
02-Processos-Chave\Incident-Response\incidentresponse_module.py
02-Processos-Chave\Onboarding\__init__.py
02-Processos-Chave\Onboarding\counterparty_onboarding.py
02-Processos-Chave\Onboarding\data_onboarding.py
02-Processos-Chave\Onboarding\onboarding_module.py
02-Processos-Chave\Onboarding\strategy_onboarding.py
02-Processos-Chave\QA-Backtesting\__init__.py
02-Processos-Chave\QA-Backtesting\backtest_engine.py
02-Processos-Chave\QA-Backtesting\qabacktesting_module.py
02-Processos-Chave\backtesting\backtest_runner_v3.py
03-Operacoes-Diarias\Execution-Window\__init__.py
03-Operacoes-Diarias\Execution-Window\executionwindow_module.py
03-Operacoes-Diarias\Execution-Window\throttling.py
03-Operacoes-Diarias\Post-Trade\__init__.py
03-Operacoes-Diarias\Post-Trade\delta_reports.py
03-Operacoes-Diarias\Post-Trade\posttradereconciliation_module.py
03-Operacoes-Diarias\Post-Trade\reconciliation.py
03-Operacoes-Diarias\Pre-Market\__init__.py
03-Operacoes-Diarias\Pre-Market\premarketchecklist_module.py
03-Operacoes-Diarias\Real-Time-Dashboard\__init__.py
03-Operacoes-Diarias\Real-Time-Dashboard\dashboard.py
03-Operacoes-Diarias\Real-Time-Dashboard\realtimedashboard_module.py
04-Infraestrutura\ML_MODELS\MetaLearningAdapter.py
04-Infraestrutura\ML_MODELS\PPOExecutionOptimizer.py
04-Infraestrutura\ML_MODELS\TemporalFusionTransformer.py
04-Infraestrutura\MT5_STOPS_FIX.py
04-Infraestrutura\api\__init__.py
04-Infraestrutura\api\database.py
04-Infraestrutura\api\endpoints\__init__.py
04-Infraestrutura\api\endpoints\strategies.py
04-Infraestrutura\api\main.py
04-Infraestrutura\database\__init__.py
04-Infraestrutura\database\connection.py
04-Infraestrutura\database\models.py
04-Infraestrutura\moduleregistry.py
04-Infraestrutura\mt5_executor.py
04-Infraestrutura\tools\cli\ncnt_cli.py
04-Infraestrutura\tools\scripts\deploy.py
04-Infraestrutura\tools\scripts\monitor.py
05-Documentacao\sops_module.py
06-Monitoramento\Feedback-Loop\action_items.py
06-Monitoramento\Feedback-Loop\post_mortem.py
06-Monitoramento\Feedback-Loop\rca_templates.py
06-Monitoramento\feedbackloop_module.py
06-Monitoramento\generate_validation_report.py
06-Monitoramento\neural_connection_monitor_v2.py
06-Monitoramento\run_validation_scan.py
AURORA_ETAPA_A_EXECUCAO_AUTOMATICA_AIC.py
AURORA_FINAL_COMPLETO_100.py
AURORA_FINAL_EXECUCAO_AIC_V5.1.py
AURORA_TEST_MODE_NO_STOPS.py
AURORA_V5_CORRECAO_DEFINITIVA_100_PERCENT.py
AURORA_V5_MAPEAMENTO_COMPLETO_274_MODULOS.py
AURORA_V5_VALIDACAO_DEFINITIVA_100_PERCENT.py
AURORA_V5_VERIFICACAO_FINAL_252_MODULOS.py
CONVERTER_JSON_PARA_MD.py
DIAGNOSTICO_SINAIS.py
EXECUTAR_FASE_BETA_FORCADA.py
GENERATE_COMPLETE_TECHNICAL_SPEC.py
HANTEC_STOPS_DISCOVERY.py
MT5_EXECUTOR_PROFISSIONAL.py
SOLUCAO_DEFINITIVA_MT5.py
aurora_etapa_a.py
aurora_etapa_b.py
aurora_etapa_c.py
aurora_etapa_d.py
aurora_etapa_e.py
aurora_strategies_integration.py
complete_integration.py
create_structure.py
executive_presentation.py
fase2_ativar_nucleo_tier0.py
fase3_migracao_massa.py
fase4_validacao_final.py
fix_all_8_modules.py
integrate_ncnt.py
main.py
main_ncnt.py
modules\__init__.py
modules\connectors\__init__.py
modules\connectors\data_connector.py
modules\connectors\execution_connector.py
modules\connectors\risk_connector.py
modules\connectors\strategy_connector.py
modules\interfaces.py
modules\ncnt_base.py
modules\ncnt_module_template.py
modules\ncnt_module_template_v2.py
ncnt_scan.py
ncnt_system_complete.py
ncnt_wrapper_generator.py
system_core\__init__.py
system_core\message_bus.py
system_core\ncnt_orchestrator_complete.py
system_core\orchestrator.py
system_core\registry.py
test_mt5_integration.py
tests\test_strategies.py
validate_239_modules.py
verificar_json.py
visual_presentation.py
visual_presentation_simple.py
wrappers_v2\__init___wrapper.py
wrappers_v2\ab_testing_wrapper.py
wrappers_v2\allocation_engine_wrapper.py
wrappers_v2\alpha_momentum_wrapper.py
wrappers_v2\api_gateway_wrapper.py
wrappers_v2\audit_system_complete_wrapper.py
wrappers_v2\audit_trail_wrapper.py
wrappers_v2\aurora_etapa_a_wrapper.py
wrappers_v2\backtest_engine_wrapper.py
wrappers_v2\backtest_runner_v3_wrapper.py
wrappers_v2\base_strategy_wrapper.py
wrappers_v2\breakout_detection_wrapper.py
wrappers_v2\build_wrapper.py
wrappers_v2\capital_manager_wrapper.py
wrappers_v2\cicdpipeline_module_wrapper.py
wrappers_v2\circuit_breakers_wrapper.py
wrappers_v2\complete_integration_wrapper.py
wrappers_v2\complexity_guard_wrapper.py
wrappers_v2\compliance_module_wrapper.py
wrappers_v2\connection_wrapper.py
wrappers_v2\core_engine_wrapper.py
wrappers_v2\coreengine_module_wrapper.py
wrappers_v2\counterparty_onboarding_wrapper.py
wrappers_v2\create_structure_wrapper.py
wrappers_v2\dashboard_wrapper.py
wrappers_v2\data_layer_wrapper.py
wrappers_v2\data_onboarding_wrapper.py
wrappers_v2\delta_reports_wrapper.py
wrappers_v2\deploy_wrapper.py
wrappers_v2\executionwindow_module_wrapper.py
wrappers_v2\executive_presentation_wrapper.py
wrappers_v2\feedbackloop_module_wrapper.py
wrappers_v2\fix_report_errors_wrapper.py
wrappers_v2\generate_complete_report_wrapper.py
wrappers_v2\generate_ultra_complete_report_wrapper.py
wrappers_v2\genesis_includes_v3_complete_wrapper.py
wrappers_v2\genesis_includes_wrapper.py
wrappers_v2\governance_module_wrapper.py
wrappers_v2\incidentresponse_module_wrapper.py
wrappers_v2\innovationlab_module_wrapper.py
wrappers_v2\integrate_ncnt_wrapper.py
wrappers_v2\integration_gate_v2_wrapper.py
wrappers_v2\integration_gate_v3_wrapper.py
wrappers_v2\interface_wrapper.py
wrappers_v2\main_ncnt_wrapper.py
wrappers_v2\main_wrapper.py
wrappers_v2\mean_reversion_wrapper.py
wrappers_v2\models_wrapper.py
wrappers_v2\moduleregistry_wrapper.py
wrappers_v2\ncnt_base_wrapper.py
wrappers_v2\ncnt_cli_wrapper.py
wrappers_v2\ncnt_orchestrator_complete_wrapper.py
wrappers_v2\ncnt_scan_wrapper.py
wrappers_v2\ncnt_system_complete_wrapper.py
wrappers_v2\onboarding_module_wrapper.py
wrappers_v2\order_management_wrapper.py
wrappers_v2\posttradereconciliation_module_wrapper.py
wrappers_v2\premarketchecklist_module_wrapper.py
wrappers_v2\prototypes_wrapper.py
wrappers_v2\qabacktesting_module_wrapper.py
wrappers_v2\realtimedashboard_module_wrapper.py
wrappers_v2\reconciliation_wrapper.py
wrappers_v2\reg_tracker_wrapper.py
wrappers_v2\regulatory_context_wrapper.py
wrappers_v2\report_generator_wrapper.py
wrappers_v2\restore_executive_report_wrapper.py
wrappers_v2\risk_engine_wrapper.py
wrappers_v2\risk_module_wrapper.py
wrappers_v2\run_complete_audit_wrapper.py
wrappers_v2\smart_routing_wrapper.py
wrappers_v2\sops_module_wrapper.py
wrappers_v2\strategies_wrapper.py
wrappers_v2\strategy_module_wrapper.py
wrappers_v2\strategy_onboarding_wrapper.py
wrappers_v2\strategy_template_wrapper.py
wrappers_v2\test_module_v2_wrapper.py
wrappers_v2\test_wrapper.py
wrappers_v2\throttling_wrapper.py
wrappers_v2\tier1_validator_v3_complete_wrapper.py
wrappers_v2\tier1_validator_v3_wrapper.py
wrappers_v2\treasury_module_wrapper.py
wrappers_v2\visual_presentation_simple_wrapper.py
wrappers_v2\visual_presentation_wrapper.py
```
