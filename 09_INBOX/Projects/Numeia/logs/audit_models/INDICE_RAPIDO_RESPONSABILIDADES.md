# ÍNDICE RÁPIDO DE RESPONSABILIDADES - PROJETO NUMEIA

## 🚨 **CONSULTA RÁPIDA - QUANDO ALGO NÃO FUNCIONAR**

### 📋 **POR FUNÇÃO:**

#### **🔍 Auditoria e Validação:**
- **Validação de nomenclatura:** `include/audit/audit_nomenclature_validator.mqh`
- **Verificação de conformidade:** `include/audit/compliancechecker.mqh`
- **Motor de auditoria:** `include/audit/audit_engine.mq5`
- **Auditoria do núcleo:** `include/audit/core_audit_engine.mq5`
- **Auditoria de includes:** `include/audit/include_audit_engine.mq5`

#### **🛡️ Painéis de Integridade:**
- **Painel de integridade:** `include/audit/AuditIntegrityPanel.mq5`
- **Painel do núcleo:** `include/audit/CoreIntegrityPanel.mq5`

#### **🧠 Sistema Neural:**
- **Rede neural quântica:** `include/neural/quantum_neural_net.mqh`
- **Filtro neural:** `include/neural/quantum_neural_filter.mqh`
- **Processador de sinais:** `include/intelligence/neural_signal_processor.mqh`

#### **🔍 Detecção de Anomalias:**
- **Detector de anomalias AI:** `include/intelligence/anomaly_detector_ai.mqh`
- **Auditor inteligente:** `include/audit/audit_ml_system/intelligent_auditor.mqh`
- **Análise de padrões:** `include/audit/audit_ml_system/error_pattern_analyzer.mqh`

#### **📊 Análise de Mercado:**
- **Matriz de correlação:** `include/analysis/correlation_matrix.mqh`
- **Detector de regime:** `include/analysis/market_regime_detector.mqh`
- **Validador multi-timeframe:** `include/analysis/multi_timeframe_validator.mqh`
- **Detector HFT:** `include/analysis/quantum_hft_detector.mqh`
- **Darkpool quântico:** `include/analysis/quantum_darkpool.mqh`
- **Order book quântico:** `include/analysis/quantum_order_book.mqh`

#### **⚛️ Sistema Quântico:**
- **Simulador de entrelaçamento:** `include/quantum/quantum_entanglement_simulator.mqh`
- **Otimizador quântico:** `include/quantum/quantum_optimizer.mqh`
- **Sistema de portas:** `include/quantum/quantum_gate_system.mqh`
- **Filtro de ruído:** `include/quantum/quantum_noise_filter.mqh`
- **Simulador de annealing:** `include/quantum/quantum_annealing_simulator.mqh`

#### **🛡️ Segurança:**
- **Firewall quântico:** `include/security/quantumfirewall.mqh`
- **Blockchain quântico:** `include/security/QuantumBlockchain.mqh`

#### **📈 Execução de Trades:**
- **Executor de trades:** `include/executionlogic/trade_executor.mqh`
- **Gerenciador de modo seguro:** `include/executionlogic/safe_mode_manager.mqh`

#### **🧠 Inteligência:**
- **Aprendizado quântico:** `include/intelligence/quantum_learning.mqh`
- **Motor de viés Thaler:** `include/intelligence/thaler_bias_engine.mqh`

#### **📊 Dados e Integração:**
- **Feed de dados:** `include/integration/quantum_data_feed.mqh`
- **Dados de mercado:** `include/data/quantum_market_data.mqh`

---

### 📋 **POR PROBLEMA:**

#### **❌ Duplicidades detectadas:**
- **Responsável:** `include/audit/audit_nomenclature_validator.mqh`
- **Logs:** `logs/RELATORIO_FALHA_CRITICA_DUPLICACAO_2025-07-21.log`

#### **❌ Auditoria insuficiente:**
- **Responsável:** `include/audit/audit_engine.mq5`
- **Logs:** `logs/RELATORIO_FALHA_AUDITORIA_INSUFICIENTE_2025-07-21.log`

#### **❌ Dependências quebradas:**
- **Responsável:** `include/audit/include_audit_engine.mq5`
- **Logs:** `logs/integration_validation/`

#### **❌ Problemas de blindagem:**
- **Responsável:** `include/utils/logger_institutional.mqh`
- **Logs:** `logs/blindagem/`

#### **❌ Falhas neurais:**
- **Responsável:** `include/neural/quantum_neural_net.mqh`
- **Logs:** `logs/audit_ml_system/`

#### **❌ Problemas de segurança:**
- **Responsável:** `include/security/quantumfirewall.mqh`
- **Logs:** `logs/security_operations/`

---

### 📋 **POR MÓDULO:**

#### **📊 ANALYSIS (6 arquivos):**
- `correlation_matrix.mqh` → Matriz de correlação
- `market_regime_detector.mqh` → Detector de regime
- `multi_timeframe_validator.mqh` → Validador multi-timeframe
- `quantum_hft_detector.mqh` → Detector HFT
- `quantum_darkpool.mqh` → Darkpool
- `quantum_order_book.mqh` → Order book

#### **⚛️ QUANTUM (5 arquivos):**
- `quantum_entanglement_simulator.mqh` → Entrelaçamento
- `quantum_optimizer.mqh` → Otimizador
- `quantum_gate_system.mqh` → Portas
- `quantum_noise_filter.mqh` → Filtro de ruído
- `quantum_annealing_simulator.mqh` → Annealing

#### **🧠 INTELLIGENCE (4 arquivos):**
- `quantum_learning.mqh` → Aprendizado
- `anomaly_detector_ai.mqh` → Detector de anomalias
- `neural_signal_processor.mqh` → Processador de sinais
- `thaler_bias_engine.mqh` → Motor de viés

#### **🔗 INTEGRATION (2 arquivos):**
- `quantum_data_feed.mqh` → Feed de dados
- `quantum_market_data.mqh` → Dados de mercado

#### **📦 MODULES (3 arquivos):**
- `quantum_neuralnet.mqh` → Rede neural
- `quantum_processor.mqh` → Processador
- `quantum_var_calculator.mqh` → Calculadora VaR

#### **⚙️ EXECUTIONLOGIC (2 arquivos):**
- `trade_executor.mqh` → Executor de trades
- `safe_mode_manager.mqh` → Gerenciador de modo seguro

#### **🛡️ SECURITY (2 arquivos):**
- `quantumfirewall.mqh` → Firewall
- `QuantumBlockchain.mqh` → Blockchain

#### **📊 RISK (1 arquivo):**
- `risk_profile.mqh` → Perfil de risco

---

### 📋 **LOGS IMPORTANTES:**

#### **🚨 Logs de Falhas:**
- `logs/RELATORIO_FALHA_CRITICA_DUPLICACAO_2025-07-21.log`
- `logs/RELATORIO_FALHA_AUDITORIA_INSUFICIENTE_2025-07-21.log`
- `logs/RELATORIO_CORRECOES_CRITICAS_QA_2025-07-21.log`

#### **📊 Relatórios de Auditoria:**
- `logs/AUDITORIA_INSTITUCIONAL_COMPLETA_2025-07-21.log`
- `logs/RELATORIO_CONFORMIDADE_INSTITUCIONAL_2025-07-21.log`
- `logs/AUDITORIA_COMPLETA_PROJETO_NUMEIA_2025-07-21.log`

#### **🔍 Validação de Integração:**
- `logs/integration_validation/`
- `logs/includes_audit/`
- `logs/consolidated_reports/`

#### **🛡️ Operações de Segurança:**
- `logs/security_operations/`
- `logs/blindagem/`
- `logs/critical_corrections/`

---

### 📋 **PROCEDIMENTO DE EMERGÊNCIA:**

1. **Identificar o problema**
2. **Consultar este índice**
3. **Localizar o arquivo responsável**
4. **Verificar logs específicos**
5. **Aplicar correção seguindo protocolo TIER-0**
6. **Validar integridade**
7. **Atualizar histórico**

---

*Índice atualizado em: 2025-07-21*
*Versão: 1.0*
*Protocolo: TIER-0* 