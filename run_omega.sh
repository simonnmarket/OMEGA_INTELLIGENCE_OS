#!/bin/bash
# Run all modules and initialize system

echo "Starting OMEGA_INTELLIGENCE_OS..."

# Executar scripts shell do Core
bash 01_CORE/engine/engine_run.sh
bash 01_CORE/controllers/controllers_run.sh
bash 01_CORE/models/models_define.sh
bash 01_CORE/interfaces/interfaces_run.sh
bash 01_CORE/validators/validators_run.sh
bash 01_CORE/agents/agents_run.sh

# Executar inicialização Python
# Usando python se disponível, ou python3
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

$PYTHON_CMD 01_CORE/audit/audit.py
$PYTHON_CMD 01_CORE/conflict_management/conflict_manager.py
$PYTHON_CMD 01_CORE/integration_layer/integration.py
$PYTHON_CMD 01_CORE/ai_interface/interface.py
$PYTHON_CMD 01_CORE/engine/assessment.py
$PYTHON_CMD 02_MODULES/RiskManager/rules.py
$PYTHON_CMD 01_CORE/controllers/library_controller.py

echo "OMEGA_INTELLIGENCE_OS initialized successfully."
