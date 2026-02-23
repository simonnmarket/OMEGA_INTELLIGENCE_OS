#!/usr/bin/env python3
"""
AURORA CORE TIER-0 - VALIDATION SCRIPT
Teste completo de todos os componentes após integração
"""

import asyncio
import sys
import json
from datetime import datetime

print("=" * 80)
print("🔬 AURORA CORE TIER-0 - VALIDAÇÃO COMPLETA")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}")
print()

results = {
    "tests": [],
    "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0}
}

def record_test(name, status, message, details=""):
    """Record test result"""
    test = {
        "name": name,
        "status": status,
        "message": message,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    results["tests"].append(test)
    results["summary"]["total"] += 1
    
    if status == "PASSED":
        results["summary"]["passed"] += 1
        print(f"  ✅ {name}: {message}")
    elif status == "FAILED":
        results["summary"]["failed"] += 1
        print(f"  ❌ {name}: {message}")
        if details:
            print(f"     Details: {details}")
    elif status == "WARNING":
        results["summary"]["warnings"] += 1
        print(f"  ⚠️  {name}: {message}")
    else:  # INFO
        print(f"  ℹ️  {name}: {message}")

# ==============================================================================
# 1. VALIDAÇÃO DE IMPORTS
# ==============================================================================

print("📦 1. VALIDAÇÃO DE IMPORTS")
print("-" * 40)

modules = [
    ("utils.vault_client", "Tier0VaultClient"),
    ("utils.redlock_manager", "RedlockManager"),
    ("health.tier0_health", "Tier0HealthMonitor"),
    ("auth.tier0_auth", "Tier0AuthMiddleware"),
    ("system_core.async_orchestrator", "AsyncOrchestrator"),
    ("connectors.mt5_connector_tier0", "Tier0MT5Connector"),
    ("risk.finite_state_risk_tier0", "Tier0RiskEngine"),
    ("execution.safe_execution_tier0", "Tier0ExecutionEngine"),
    ("api.tier0_endpoints", "router"),
    ("config.settings", "SETTINGS"),
    ("config.database", "DATABASE_CONFIG"),
]

for module_name, class_name in modules:
    try:
        module = __import__(module_name, fromlist=[class_name])
        getattr(module, class_name)
        record_test(f"IMPORT_{module_name.upper().replace('.', '_')}", "PASSED", f"Módulo {module_name} importa corretamente")
    except Exception as e:
        record_test(f"IMPORT_{module_name.upper().replace('.', '_')}", "FAILED", f"Erro ao importar {module_name}", str(e))

# ==============================================================================
# 2. VALIDAÇÃO DE FUNCIONALIDADE DOS COMPONENTES
# ==============================================================================

print()
print("⚙️  2. VALIDAÇÃO DE FUNCIONALIDADE DOS COMPONENTES")
print("-" * 50)

async def test_components():
    """Test all components"""
    
    # Import all required modules
    from utils.vault_client import Tier0VaultClient
    from utils.redlock_manager import RedlockManager
    from health.tier0_health import Tier0HealthMonitor
    from risk.finite_state_risk_tier0 import Tier0RiskEngine
    from system_core.async_orchestrator import Tier0CircuitBreaker
    from connectors.mt5_connector_tier0 import Tier0MT5Connector
    from execution.safe_execution_tier0 import Tier0ExecutionEngine
    
    # Initialize base components
    vault = Tier0VaultClient('http://localhost:8200', 'demo-token')
    redlock = RedlockManager(['localhost:6379'])
    
    # Test 1: Vault Client
    try:
        secret = await vault.get_secret('aurora/health', 'test')
        record_test("VAULT_CLIENT", "PASSED", "Vault client funcional", f"Secret: {secret}")
    except Exception as e:
        record_test("VAULT_CLIENT", "FAILED", "Vault client com erro", str(e))
    
    # Test 2: Redlock Manager
    try:
        lock_id = await redlock.lock('validation_test', ttl=5000)
        if lock_id:
            await redlock.unlock('validation_test', lock_id)
            record_test("REDLOCK_MANAGER", "PASSED", "Redlock manager funcional", f"Lock ID: {lock_id[:16]}...")
        else:
            record_test("REDLOCK_MANAGER", "FAILED", "Failed to acquire lock")
    except Exception as e:
        record_test("REDLOCK_MANAGER", "FAILED", "Redlock manager com erro", str(e))
    
    # Test 3: Health Monitor
    try:
        monitor = Tier0HealthMonitor(vault, redlock)
        matrix = await monitor.check_comprehensive()
        record_test("HEALTH_MONITOR", "PASSED", "Health monitor funcional", 
                   f"Level: {matrix.overall.name}, Components: {len(matrix.components)}")
    except Exception as e:
        record_test("HEALTH_MONITOR", "FAILED", "Health monitor com erro", str(e))
    
    # Test 4: Circuit Breaker
    try:
        cb = Tier0CircuitBreaker(redlock, 'test')
        can_exec = await cb.can_execute()
        state_info = await cb.get_state()
        record_test("CIRCUIT_BREAKER", "PASSED", "Circuit breaker funcional",
                   f"Can execute: {can_exec}, State: {state_info.get('state', 'UNKNOWN')}")
    except Exception as e:
        record_test("CIRCUIT_BREAKER", "FAILED", "Circuit breaker com erro", str(e))
    
    # Test 5: Risk Engine
    try:
        risk = Tier0RiskEngine(vault, cb)
        result = await risk.evaluate_trade({
            'symbol': 'EURUSD',
            'operation': 'BUY',
            'volume': 0.01,
            'price': 1.0850,
            'drawdown': 0.03
        })
        approved = result.get('approved', False)
        record_test("RISK_ENGINE", "PASSED", "Risk engine funcional",
                   f"Approved: {approved}, State: {risk.state.name}")
    except Exception as e:
        record_test("RISK_ENGINE", "FAILED", "Risk engine com erro", str(e))
    
    # Test 6: MT5 Connector
    try:
        mt5 = Tier0MT5Connector('demo', 'demo', 'demo', cb)
        await mt5.connect()
        tick = await mt5.get_tick('EURUSD')
        record_test("MT5_CONNECTOR", "PASSED", "MT5 connector funcional",
                   f"Symbol: {tick.get('symbol')}, Bid: {tick.get('bid')}")
    except Exception as e:
        record_test("MT5_CONNECTOR", "FAILED", "MT5 connector com erro", str(e))
    
    # Test 7: Execution Engine
    try:
        exec_engine = Tier0ExecutionEngine(mt5, risk, cb, redlock)
        result = await exec_engine.execute_trade({
            'symbol': 'EURUSD',
            'operation': 'BUY',
            'volume': 0.01,
            'price': 1.0850,
            'drawdown': 0.02,
            'idempotency_key': 'validation_test_001'
        })
        status = result.get('status', 'UNKNOWN')
        trade_id = result.get('trade_id', 'N/A')
        record_test("EXECUTION_ENGINE", "PASSED", "Execution engine funcional",
                   f"Status: {status}, Trade ID: {trade_id}")
    except Exception as e:
        record_test("EXECUTION_ENGINE", "FAILED", "Execution engine com erro", str(e))

# Run async tests
asyncio.run(test_components())

# ==============================================================================
# 3. VALIDAÇÃO DE CONFIGURAÇÃO
# ==============================================================================

print()
print("⚙️  3. VALIDAÇÃO DE CONFIGURAÇÃO")
print("-" * 35)

try:
    from config.settings import SETTINGS
    system_name = SETTINGS.get('system', {}).get('name', 'UNKNOWN')
    version = SETTINGS.get('system', {}).get('version', 'UNKNOWN')
    paper_trading = SETTINGS.get('execution', {}).get('paper_trading', False)
    record_test("SETTINGS_LOAD", "PASSED", "Configurações carregam corretamente",
               f"System: {system_name} v{version}, Paper trading: {paper_trading}")
    
    # Check risk limits
    max_risk = SETTINGS.get('risk', {}).get('max_risk_per_trade', 0)
    if 0 < max_risk <= 0.05:
        record_test("RISK_LIMITS", "PASSED", "Limites de risco adequados",
                   f"Max risk per trade: {max_risk * 100}%")
    else:
        record_test("RISK_LIMITS", "WARNING", "Limites de risco fora do esperado",
                   f"Max risk: {max_risk}")
except Exception as e:
    record_test("SETTINGS_LOAD", "FAILED", "Erro ao carregar configurações", str(e))

try:
    from config.database import DATABASE_CONFIG
    exp_buffer = DATABASE_CONFIG.get('experience_buffer', '')
    models_path = DATABASE_CONFIG.get('models_path', '')
    if exp_buffer and models_path:
        record_test("DATABASE_CONFIG", "PASSED", "Database config válido",
                   "Todos os caminhos configurados")
    else:
        record_test("DATABASE_CONFIG", "FAILED", "Database config incompleto")
except Exception as e:
    record_test("DATABASE_CONFIG", "FAILED", "Erro ao carregar database config", str(e))

# ==============================================================================
# 4. VALIDAÇÃO DE ARQUITETURA
# ==============================================================================

print()
print("🏗️  4. VALIDAÇÃO DE ARQUITETURA")
print("-" * 35)

import os

# Check critical directories
critical_dirs = [
    "system_core", "connectors", "risk", "execution",
    "auth", "health", "utils", "api", "config",
    "strategies", "learning", "ml_models", "tests"
]

missing_dirs = [d for d in critical_dirs if not os.path.isdir(d)]

if not missing_dirs:
    record_test("DIRECTORY_STRUCTURE", "PASSED", "Estrutura de diretórios completa",
               f"{len(critical_dirs)} diretórios validados")
else:
    record_test("DIRECTORY_STRUCTURE", "FAILED", "Diretórios faltando",
               f"Missing: {', '.join(missing_dirs)}")

# Check critical files
critical_files = [
    "main.py", "app.py", "requirements.txt",
    "config/settings.py", "config/database.py"
]

missing_files = [f for f in critical_files if not os.path.isfile(f)]

if not missing_files:
    record_test("CRITICAL_FILES", "PASSED", "Todos os arquivos críticos presentes",
               f"{len(critical_files)} arquivos validados")
else:
    record_test("CRITICAL_FILES", "FAILED", "Arquivos críticos faltando",
               f"Missing: {', '.join(missing_files)}")

# Check documentation
docs = [
    "README_INTEGRATED.md",
    "STATUS_SISTEMA_INTEGRADO.md",
    "ESTRUTURA_MODULOS_STATUS_INTEGRADO.md",
    "INTEGRATION_REPORT.md"
]

missing_docs = [d for d in docs if not os.path.isfile(d)]

if not missing_docs:
    total_size = sum(os.path.getsize(d) for d in docs) / 1024
    record_test("DOCUMENTATION", "PASSED", "Documentação completa",
               f"{len(docs)} documentos, {total_size:.2f} KB total")
else:
    record_test("DOCUMENTATION", "FAILED", "Documentação incompleta",
               f"Missing: {', '.join(missing_docs)}")

# ==============================================================================
# 5. RESUMO FINAL
# ==============================================================================

print()
print("=" * 80)
print("📊 RESUMO DA VALIDAÇÃO")
print("=" * 80)
print()

total = results["summary"]["total"]
passed = results["summary"]["passed"]
failed = results["summary"]["failed"]
warnings = results["summary"]["warnings"]

success_percent = (passed / total * 100) if total > 0 else 0

print(f"📈 ESTATÍSTICAS:")
print(f"   Total de testes: {total}")
print(f"   Testes passados: {passed}")
print(f"   Testes falhados: {failed}")
print(f"   Avisos: {warnings}")
print(f"   Taxa de sucesso: {success_percent:.1f}%")
print()

# List failed tests
failed_tests = [t for t in results["tests"] if t["status"] == "FAILED"]

if failed_tests:
    print("🚨 TESTES FALHADOS:")
    for test in failed_tests:
        print(f"   ❌ {test['name']}: {test['message']}")
        if test['details']:
            print(f"      Details: {test['details']}")
    print()

# Determine overall status
if failed == 0 and success_percent >= 95:
    status = "✅ EXCELENTE"
    overall = "PASSED"
    print(f"🎉 STATUS GERAL: {status}")
    print("   Todos os testes críticos passaram!")
    print("   Sistema pronto para produção Tier-0")
    exit_code = 0
elif failed == 0 and success_percent >= 80:
    status = "⚠️  SATISFATÓRIO"
    overall = "PASSED"
    print(f"✅ STATUS GERAL: {status}")
    print("   Sistema operacional com pequenos avisos")
    exit_code = 0
elif failed < 3 and success_percent >= 70:
    status = "⚠️  DEGRADADO"
    overall = "WARNING"
    print(f"⚠️  STATUS GERAL: {status}")
    print("   Sistema funcional mas requer atenção")
    exit_code = 2
else:
    status = "❌ CRÍTICO"
    overall = "FAILED"
    print(f"❌ STATUS GERAL: {status}")
    print("   Sistema com falhas críticas")
    exit_code = 1

print()

# Save report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_file = f"VALIDATION_REPORT_{timestamp}.json"

results["overall"] = overall
results["success_percent"] = success_percent
results["status"] = status
results["validation_timestamp"] = datetime.now().isoformat()

with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"📋 RELATÓRIO FINAL:")
print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   Sistema: Aurora Core Tier-0 Integrated")
print(f"   Status: {status}")
print(f"   Sucesso: {success_percent:.1f}%")
print(f"   Arquivo de resultados: {report_file}")
print()

print("=" * 80)
print("🔬 VALIDAÇÃO CONCLUÍDA - AURORA CORE TIER-0")
print("=" * 80)
print()

sys.exit(exit_code)

