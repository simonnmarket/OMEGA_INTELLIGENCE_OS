#!/usr/bin/env python3
"""
Script de validação do sistema AURORA CORE TIER-0
Verifica compliance, segurança e funcionalidade
"""

import os
import sys
import importlib
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def check_imports():
    """Verificar todos os imports"""
    print("📦 Verificando imports...")
    
    modules = [
        "utils.vault_client",
        "utils.redlock_manager",
        "health.tier0_health",
        "auth.tier0_auth",
        "core.async_orchestrator",
        "connectors.mt5_connector_tier0",
        "risk.finite_state_risk_tier0",
        "execution.safe_execution_tier0",
        "api.tier0_endpoints",
        "app"
    ]
    
    errors = []
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            errors.append(module)
    
    return len(errors) == 0


def check_pydantic_models():
    """Verificar modelos Pydantic"""
    print("\n📋 Verificando modelos Pydantic...")
    
    try:
        from risk.finite_state_risk_tier0 import TradeData, RiskMetrics
        
        # Test TradeData
        trade = TradeData(
            symbol="EURUSD",
            operation="BUY",
            volume=0.01,
            price=1.0850,
            drawdown=0.05
        )
        print(f"  ✅ TradeData: {trade.symbol} {trade.operation}")
        
        # Test RiskMetrics
        metrics = RiskMetrics()
        print(f"  ✅ RiskMetrics: drawdown={metrics.current_drawdown}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


async def check_vault_client():
    """Verificar Vault client"""
    print("\n🔐 Verificando Vault client...")
    
    try:
        from utils.vault_client import Tier0VaultClient
        
        client = Tier0VaultClient(
            vault_addr="http://localhost:8200",
            vault_token="demo-token"
        )
        
        # Test get_secret
        secret = await client.get_secret("aurora/health", "test")
        print(f"  ✅ Vault client: secret retrieved")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


async def check_redlock():
    """Verificar Redlock manager"""
    print("\n🔒 Verificando Redlock...")
    
    try:
        from utils.redlock_manager import RedlockManager
        
        redlock = RedlockManager(["localhost:6379"])
        
        # Test lock
        lock_id = await redlock.lock("test_resource", ttl=5000)
        if lock_id:
            print(f"  ✅ Lock acquired: {lock_id[:8]}...")
            await redlock.unlock("test_resource", lock_id)
            print(f"  ✅ Lock released")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


async def check_health_monitor():
    """Verificar Health monitor"""
    print("\n🏥 Verificando Health monitor...")
    
    try:
        from utils.vault_client import Tier0VaultClient
        from utils.redlock_manager import RedlockManager
        from health.tier0_health import Tier0HealthMonitor, HealthLevel
        
        vault = Tier0VaultClient("http://localhost:8200", "demo")
        redlock = RedlockManager(["localhost:6379"])
        
        monitor = Tier0HealthMonitor(vault, redlock)
        matrix = await monitor.check_comprehensive()
        
        print(f"  ✅ Overall health: {matrix.overall.name}")
        for name, comp in matrix.components.items():
            print(f"     - {name}: {comp.level.name}")
        
        return matrix.overall.value >= HealthLevel.STABLE.value
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


async def check_circuit_breakers():
    """Verificar Circuit breakers"""
    print("\n⚡ Verificando Circuit breakers...")
    
    try:
        from utils.redlock_manager import RedlockManager
        from core.async_orchestrator import Tier0CircuitBreaker, CircuitState
        
        redlock = RedlockManager(["localhost:6379"])
        cb = Tier0CircuitBreaker(redlock, "test_component")
        
        # Test initial state
        can_execute = await cb.can_execute()
        state = await cb.get_state()
        
        print(f"  ✅ Circuit breaker state: {state['state'].value}")
        print(f"  ✅ Can execute: {can_execute}")
        
        return state['state'] == CircuitState.CLOSED
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def check_security():
    """Verificar configurações de segurança"""
    print("\n🔒 Verificando segurança...")
    
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    issues = []
    
    # Check for hardcoded passwords
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for hardcoded secrets (simplified check)
                    if 'password = "' in content.lower() and 'demo' not in content.lower():
                        issues.append(f"{file}: possible hardcoded password")
    
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
        return False
    else:
        print("  ✅ No hardcoded secrets found")
        return True


async def main():
    """Main validation routine"""
    print("=" * 60)
    print("🚀 AURORA CORE TIER-0 - SYSTEM VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Run checks
    results.append(("Imports", check_imports()))
    results.append(("Pydantic Models", check_pydantic_models()))
    results.append(("Vault Client", await check_vault_client()))
    results.append(("Redlock", await check_redlock()))
    results.append(("Health Monitor", await check_health_monitor()))
    results.append(("Circuit Breakers", await check_circuit_breakers()))
    results.append(("Security", check_security()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n  Total: {passed}/{len(results)} passed")
    
    if failed == 0:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} VALIDATION(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

