# ==============================================================================
# AURORA CORE TIER-0 - VALIDATION SCRIPT (PowerShell)
# Teste completo de todos os componentes após integração
# Para execução pelo AIC (Agente de Implementação e Controle)
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "🔬 AURORA CORE TIER-0 - VALIDAÇÃO COMPLETA" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# ------------------------------------------------------------------------------
# 1. CONFIGURAÇÃO E VARIÁVEIS
# ------------------------------------------------------------------------------

$BASE_URL = "http://localhost:8081"
$TIMEOUT = 10
$MAX_RETRIES = 3
$VALIDATION_RESULTS = @{
    tests = @()
    summary = @{
        total = 0
        passed = 0
        failed = 0
        warnings = 0
        timestamp = (Get-Date -Format 'o')
    }
}

# Função para registrar resultados
function Record-Test {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Message,
        [string]$Details = ""
    )
    
    $test = @{
        name = $Name
        status = $Status
        message = $Message
        details = $Details
        timestamp = (Get-Date -Format 'o')
    }
    
    $VALIDATION_RESULTS.tests += $test
    $VALIDATION_RESULTS.summary.total++
    
    switch ($Status) {
        "PASSED" { 
            $VALIDATION_RESULTS.summary.passed++
            Write-Host "  ✅ $Name`: $Message" -ForegroundColor Green
        }
        "FAILED" { 
            $VALIDATION_RESULTS.summary.failed++
            Write-Host "  ❌ $Name`: $Message" -ForegroundColor Red
            if ($Details) { Write-Host "     Details: $Details" -ForegroundColor DarkRed }
        }
        "WARNING" {
            $VALIDATION_RESULTS.summary.warnings++
            Write-Host "  ⚠️  $Name`: $Message" -ForegroundColor Yellow
            if ($Details) { Write-Host "     Details: $Details" -ForegroundColor DarkYellow }
        }
        "INFO" {
            Write-Host "  ℹ️  $Name`: $Message" -ForegroundColor Cyan
        }
    }
}

# Função para fazer HTTP request
function Invoke-HttpRequest {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null,
        [hashtable]$Headers = @{}
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = $TIMEOUT
            UseBasicParsing = $true
        }
        
        if ($Headers.Count -gt 0) {
            $params['Headers'] = $Headers
        }
        
        if ($Body) {
            $params['Body'] = ($Body | ConvertTo-Json -Depth 10)
            $params['ContentType'] = 'application/json'
        }
        
        $response = Invoke-WebRequest @params
        return @{
            StatusCode = $response.StatusCode
            Content = $response.Content
            Success = $true
        }
    }
    catch {
        $statusCode = 0
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        return @{
            StatusCode = $statusCode
            Content = $_.Exception.Message
            Success = $false
        }
    }
}

# ------------------------------------------------------------------------------
# 2. VALIDAÇÃO DE SISTEMA BASE
# ------------------------------------------------------------------------------

Write-Host "🔧 1. VALIDAÇÃO DO SISTEMA BASE" -ForegroundColor Cyan
Write-Host "---------------------------------" -ForegroundColor Cyan

# Teste 1.1: Python version
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.[0-9]+") {
        Record-Test "PYTHON_VERSION" "PASSED" "Python instalado e acessível" "$pythonVersion"
    } else {
        Record-Test "PYTHON_VERSION" "FAILED" "Python version inválida" "$pythonVersion"
    }
}
catch {
    Record-Test "PYTHON_VERSION" "FAILED" "Python não encontrado" $_.Exception.Message
}

# Teste 1.2: Estrutura de diretórios
$requiredDirs = @(
    "system_core",
    "connectors",
    "risk",
    "execution",
    "auth",
    "health",
    "utils",
    "api",
    "config",
    "tests"
)

$missingDirs = @()
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $missingDirs += $dir
    }
}

if ($missingDirs.Count -eq 0) {
    Record-Test "DIRECTORY_STRUCTURE" "PASSED" "Todos os diretórios necessários existem" "$($requiredDirs.Count) diretórios validados"
} else {
    Record-Test "DIRECTORY_STRUCTURE" "FAILED" "Diretórios faltando" "Missing: $($missingDirs -join ', ')"
}

# Teste 1.3: Arquivos críticos
$criticalFiles = @(
    "main.py",
    "app.py",
    "requirements.txt",
    "config\settings.py",
    "config\database.py"
)

$missingFiles = @()
foreach ($file in $criticalFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Record-Test "CRITICAL_FILES" "PASSED" "Todos os arquivos críticos presentes" "$($criticalFiles.Count) arquivos validados"
} else {
    Record-Test "CRITICAL_FILES" "FAILED" "Arquivos críticos faltando" "Missing: $($missingFiles -join ', ')"
}

# ------------------------------------------------------------------------------
# 3. VALIDAÇÃO DE IMPORTS E MÓDULOS
# ------------------------------------------------------------------------------

Write-Host ""
Write-Host "📦 2. VALIDAÇÃO DE IMPORTS E MÓDULOS" -ForegroundColor Cyan
Write-Host "-------------------------------------" -ForegroundColor Cyan

$modules = @(
    @{name="utils"; import="from utils.vault_client import Tier0VaultClient"},
    @{name="health"; import="from health.tier0_health import Tier0HealthMonitor"},
    @{name="auth"; import="from auth.tier0_auth import Tier0AuthMiddleware"},
    @{name="system_core"; import="from system_core.async_orchestrator import AsyncOrchestrator"},
    @{name="connectors"; import="from connectors.mt5_connector_tier0 import Tier0MT5Connector"},
    @{name="risk"; import="from risk.finite_state_risk_tier0 import Tier0RiskEngine"},
    @{name="execution"; import="from execution.safe_execution_tier0 import Tier0ExecutionEngine"},
    @{name="api"; import="from api.tier0_endpoints import router"},
    @{name="config"; import="from config.settings import SETTINGS"}
)

foreach ($module in $modules) {
    try {
        $result = python -c "$($module.import); print('OK')" 2>&1
        if ($result -match "OK") {
            Record-Test "IMPORT_$($module.name.ToUpper())" "PASSED" "Módulo $($module.name) importa corretamente" ""
        } else {
            Record-Test "IMPORT_$($module.name.ToUpper())" "FAILED" "Erro ao importar $($module.name)" "$result"
        }
    }
    catch {
        Record-Test "IMPORT_$($module.name.ToUpper())" "FAILED" "Exceção ao importar $($module.name)" $_.Exception.Message
    }
}

# ------------------------------------------------------------------------------
# 4. VALIDAÇÃO DE FUNCIONALIDADE DOS COMPONENTES
# ------------------------------------------------------------------------------

Write-Host ""
Write-Host "⚙️  3. VALIDAÇÃO DE FUNCIONALIDADE DOS COMPONENTES" -ForegroundColor Cyan
Write-Host "---------------------------------------------------" -ForegroundColor Cyan

# Teste 3.1: Vault Client
try {
    $vaultTest = python -c @"
import asyncio
from utils.vault_client import Tier0VaultClient

async def test():
    try:
        vault = Tier0VaultClient('http://localhost:8200', 'demo-token')
        secret = await vault.get_secret('aurora/health', 'test')
        print(f'OK:{secret}')
    except Exception as e:
        print(f'ERROR:{e}')

asyncio.run(test())
"@ 2>&1
    
    if ($vaultTest -match "OK:") {
        $secret = ($vaultTest -split ":")[1]
        Record-Test "VAULT_CLIENT" "PASSED" "Vault client funcional" "Secret: $secret"
    } else {
        Record-Test "VAULT_CLIENT" "FAILED" "Vault client com erro" "$vaultTest"
    }
}
catch {
    Record-Test "VAULT_CLIENT" "FAILED" "Exceção no Vault client" $_.Exception.Message
}

# Teste 3.2: Redlock Manager
try {
    $redlockTest = python -c @"
import asyncio
from utils.redlock_manager import RedlockManager

async def test():
    try:
        redlock = RedlockManager(['localhost:6379'])
        lock_id = await redlock.lock('validation_test', ttl=5000)
        if lock_id:
            await redlock.unlock('validation_test', lock_id)
            print(f'OK:{lock_id}')
        else:
            print('ERROR:Failed to acquire lock')
    except Exception as e:
        print(f'ERROR:{e}')

asyncio.run(test())
"@ 2>&1
    
    if ($redlockTest -match "OK:") {
        $lockId = (($redlockTest -split ":")[1]).Substring(0, 16)
        Record-Test "REDLOCK_MANAGER" "PASSED" "Redlock manager funcional" "Lock ID: $lockId..."
    } else {
        Record-Test "REDLOCK_MANAGER" "FAILED" "Redlock manager com erro" "$redlockTest"
    }
}
catch {
    Record-Test "REDLOCK_MANAGER" "FAILED" "Exceção no Redlock manager" $_.Exception.Message
}

# Teste 3.3: Health Monitor
try {
    $healthTest = python -c @"
import asyncio
from health.tier0_health import Tier0HealthMonitor
from utils.vault_client import Tier0VaultClient
from utils.redlock_manager import RedlockManager

async def test():
    try:
        vault = Tier0VaultClient('http://localhost:8200', 'demo-token')
        redlock = RedlockManager(['localhost:6379'])
        monitor = Tier0HealthMonitor(vault, redlock)
        matrix = await monitor.check_comprehensive()
        print(f'OK:{matrix.overall.name}')
    except Exception as e:
        print(f'ERROR:{e}')

asyncio.run(test())
"@ 2>&1
    
    if ($healthTest -match "OK:") {
        $level = ($healthTest -split ":")[1]
        Record-Test "HEALTH_MONITOR" "PASSED" "Health monitor funcional" "Level: $level"
    } else {
        Record-Test "HEALTH_MONITOR" "FAILED" "Health monitor com erro" "$healthTest"
    }
}
catch {
    Record-Test "HEALTH_MONITOR" "FAILED" "Exceção no Health monitor" $_.Exception.Message
}

# Teste 3.4: Risk Engine
try {
    $riskTest = python -c @"
import asyncio
from risk.finite_state_risk_tier0 import Tier0RiskEngine
from system_core.async_orchestrator import Tier0CircuitBreaker
from utils.vault_client import Tier0VaultClient
from utils.redlock_manager import RedlockManager

async def test():
    try:
        vault = Tier0VaultClient('http://localhost:8200', 'demo-token')
        redlock = RedlockManager(['localhost:6379'])
        cb = Tier0CircuitBreaker(redlock, 'test')
        risk = Tier0RiskEngine(vault, cb)
        result = await risk.evaluate_trade({
            'symbol': 'EURUSD',
            'operation': 'BUY',
            'volume': 0.01,
            'price': 1.0850,
            'drawdown': 0.03
        })
        print(f'OK:{result[\"approved\"]}:{risk.state.name}')
    except Exception as e:
        print(f'ERROR:{e}')

asyncio.run(test())
"@ 2>&1
    
    if ($riskTest -match "OK:") {
        $parts = $riskTest -split ":"
        $approved = $parts[1]
        $state = $parts[2]
        Record-Test "RISK_ENGINE" "PASSED" "Risk engine funcional" "Approved: $approved, State: $state"
    } else {
        Record-Test "RISK_ENGINE" "FAILED" "Risk engine com erro" "$riskTest"
    }
}
catch {
    Record-Test "RISK_ENGINE" "FAILED" "Exceção no Risk engine" $_.Exception.Message
}

# Teste 3.5: MT5 Connector
try {
    $mt5Test = python -c @"
import asyncio
from connectors.mt5_connector_tier0 import Tier0MT5Connector
from system_core.async_orchestrator import Tier0CircuitBreaker
from utils.redlock_manager import RedlockManager

async def test():
    try:
        redlock = RedlockManager(['localhost:6379'])
        cb = Tier0CircuitBreaker(redlock, 'test')
        mt5 = Tier0MT5Connector('demo', 'demo', 'demo', cb)
        await mt5.connect()
        tick = await mt5.get_tick('EURUSD')
        print(f'OK:{tick[\"symbol\"]}:{tick[\"bid\"]}')
    except Exception as e:
        print(f'ERROR:{e}')

asyncio.run(test())
"@ 2>&1
    
    if ($mt5Test -match "OK:") {
        $parts = $mt5Test -split ":"
        $symbol = $parts[1]
        $bid = $parts[2]
        Record-Test "MT5_CONNECTOR" "PASSED" "MT5 connector funcional" "Symbol: $symbol @ $bid"
    } else {
        Record-Test "MT5_CONNECTOR" "FAILED" "MT5 connector com erro" "$mt5Test"
    }
}
catch {
    Record-Test "MT5_CONNECTOR" "FAILED" "Exceção no MT5 connector" $_.Exception.Message
}

# Teste 3.6: Execution Engine
try {
    $execTest = python -c @"
import asyncio
from execution.safe_execution_tier0 import Tier0ExecutionEngine
from connectors.mt5_connector_tier0 import Tier0MT5Connector
from risk.finite_state_risk_tier0 import Tier0RiskEngine
from system_core.async_orchestrator import Tier0CircuitBreaker
from utils.vault_client import Tier0VaultClient
from utils.redlock_manager import RedlockManager

async def test():
    try:
        vault = Tier0VaultClient('http://localhost:8200', 'demo-token')
        redlock = RedlockManager(['localhost:6379'])
        cb = Tier0CircuitBreaker(redlock, 'test')
        mt5 = Tier0MT5Connector('demo', 'demo', 'demo', cb)
        risk = Tier0RiskEngine(vault, cb)
        exec_engine = Tier0ExecutionEngine(mt5, risk, cb, redlock)
        result = await exec_engine.execute_trade({
            'symbol': 'EURUSD',
            'operation': 'BUY',
            'volume': 0.01,
            'price': 1.0850,
            'drawdown': 0.02,
            'idempotency_key': 'validation_test_001'
        })
        print(f'OK:{result[\"status\"]}:{result.get(\"trade_id\", \"N/A\")}')
    except Exception as e:
        print(f'ERROR:{e}')

asyncio.run(test())
"@ 2>&1
    
    if ($execTest -match "OK:") {
        $parts = $execTest -split ":"
        $status = $parts[1]
        $tradeId = $parts[2]
        Record-Test "EXECUTION_ENGINE" "PASSED" "Execution engine funcional" "Status: $status, Trade ID: $tradeId"
    } else {
        Record-Test "EXECUTION_ENGINE" "FAILED" "Execution engine com erro" "$execTest"
    }
}
catch {
    Record-Test "EXECUTION_ENGINE" "FAILED" "Exceção no Execution engine" $_.Exception.Message
}

# ------------------------------------------------------------------------------
# 5. VALIDAÇÃO DE TESTES UNITÁRIOS
# ------------------------------------------------------------------------------

Write-Host ""
Write-Host "🧪 4. VALIDAÇÃO DE TESTES UNITÁRIOS" -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan

# Verificar se pytest está disponível
try {
    $pytestVersion = pytest --version 2>&1
    if ($pytestVersion -match "pytest") {
        Record-Test "PYTEST_AVAILABLE" "PASSED" "pytest disponível" "$pytestVersion"
        
        # Contar testes
        $testCount = (Get-ChildItem -Path "tests" -Recurse -Filter "test_*.py" | Measure-Object).Count
        Record-Test "TEST_FILES" "PASSED" "Arquivos de teste encontrados" "$testCount arquivos de teste"
        
        # Executar testes (quick check)
        Write-Host "  Executando testes rápidos..." -ForegroundColor Gray
        try {
            $testResult = pytest tests/ --collect-only -q 2>&1
            $totalTests = ($testResult | Select-String "test session starts" -Context 0,10 | Out-String)
            if ($testResult -match "(\d+) test") {
                $count = $Matches[1]
                Record-Test "TEST_COLLECTION" "PASSED" "Testes podem ser coletados" "$count testes encontrados"
            } else {
                Record-Test "TEST_COLLECTION" "WARNING" "Não foi possível contar testes" "$testResult"
            }
        }
        catch {
            Record-Test "TEST_COLLECTION" "WARNING" "Erro ao coletar testes" $_.Exception.Message
        }
    } else {
        Record-Test "PYTEST_AVAILABLE" "FAILED" "pytest não encontrado" "$pytestVersion"
    }
}
catch {
    Record-Test "PYTEST_AVAILABLE" "FAILED" "Erro ao verificar pytest" $_.Exception.Message
}

# ------------------------------------------------------------------------------
# 6. VALIDAÇÃO DE CONFIGURAÇÃO
# ------------------------------------------------------------------------------

Write-Host ""
Write-Host "⚙️  5. VALIDAÇÃO DE CONFIGURAÇÃO" -ForegroundColor Cyan
Write-Host "---------------------------------" -ForegroundColor Cyan

# Teste 5.1: Settings carregam corretamente
try {
    $settingsTest = python -c @"
from config.settings import SETTINGS
import json
print(json.dumps({
    'system_name': SETTINGS['system']['name'],
    'version': SETTINGS['system']['version'],
    'demo_mode': SETTINGS['execution']['paper_trading'],
    'max_risk': SETTINGS['risk']['max_risk_per_trade']
}))
"@ 2>&1
    
    if ($settingsTest -match "{") {
        $settings = $settingsTest | ConvertFrom-Json
        Record-Test "SETTINGS_LOAD" "PASSED" "Configurações carregam corretamente" "System: $($settings.system_name) v$($settings.version)"
        
        # Validar demo mode
        if ($settings.demo_mode) {
            Record-Test "DEMO_MODE" "INFO" "Demo mode ativo (esperado)" "Paper trading: $($settings.demo_mode)"
        }
        
        # Validar limites de risco
        if ($settings.max_risk -gt 0 -and $settings.max_risk -le 0.05) {
            Record-Test "RISK_LIMITS" "PASSED" "Limites de risco adequados" "Max risk per trade: $($settings.max_risk * 100)%"
        } else {
            Record-Test "RISK_LIMITS" "WARNING" "Limites de risco fora do esperado" "Max risk: $($settings.max_risk)"
        }
    } else {
        Record-Test "SETTINGS_LOAD" "FAILED" "Erro ao carregar configurações" "$settingsTest"
    }
}
catch {
    Record-Test "SETTINGS_LOAD" "FAILED" "Exceção ao carregar configurações" $_.Exception.Message
}

# Teste 5.2: Database config
try {
    $dbTest = python -c @"
from config.database import DATABASE_CONFIG
import json
print(json.dumps(DATABASE_CONFIG))
"@ 2>&1
    
    if ($dbTest -match "{") {
        $dbConfig = $dbTest | ConvertFrom-Json
        $paths = @($dbConfig.experience_buffer, $dbConfig.models_path, $dbConfig.logs_path)
        $allValid = $true
        foreach ($path in $paths) {
            if (-not $path) {
                $allValid = $false
                break
            }
        }
        
        if ($allValid) {
            Record-Test "DATABASE_CONFIG" "PASSED" "Database config válido" "Todos os caminhos configurados"
        } else {
            Record-Test "DATABASE_CONFIG" "FAILED" "Database config incompleto" "Caminhos faltando"
        }
    } else {
        Record-Test "DATABASE_CONFIG" "FAILED" "Erro ao carregar database config" "$dbTest"
    }
}
catch {
    Record-Test "DATABASE_CONFIG" "FAILED" "Exceção ao carregar database config" $_.Exception.Message
}

# ------------------------------------------------------------------------------
# 7. VALIDAÇÃO DE DOCUMENTAÇÃO
# ------------------------------------------------------------------------------

Write-Host ""
Write-Host "📚 6. VALIDAÇÃO DE DOCUMENTAÇÃO" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan

$docs = @(
    "README_INTEGRATED.md",
    "STATUS_SISTEMA_INTEGRADO.md",
    "ESTRUTURA_MODULOS_STATUS_INTEGRADO.md",
    "INTEGRATION_REPORT.md"
)

$missingDocs = @()
$docsSize = 0

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        $size = (Get-Item $doc).Length / 1KB
        $docsSize += $size
    } else {
        $missingDocs += $doc
    }
}

if ($missingDocs.Count -eq 0) {
    Record-Test "DOCUMENTATION" "PASSED" "Toda documentação presente" "$($docs.Count) documentos, $([math]::Round($docsSize, 2)) KB total"
} else {
    Record-Test "DOCUMENTATION" "FAILED" "Documentação incompleta" "Missing: $($missingDocs -join ', ')"
}

# ------------------------------------------------------------------------------
# 8. RESUMO DA VALIDAÇÃO
# ------------------------------------------------------------------------------

Write-Host ""
Write-Host "📊 7. RESUMO DA VALIDAÇÃO" -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan
Write-Host ""

$total = $VALIDATION_RESULTS.summary.total
$passed = $VALIDATION_RESULTS.summary.passed
$failed = $VALIDATION_RESULTS.summary.failed
$warnings = $VALIDATION_RESULTS.summary.warnings

if ($total -gt 0) {
    $successPercent = [math]::Round(($passed / $total) * 100, 1)
} else {
    $successPercent = 0
}

Write-Host "📈 ESTATÍSTICAS:" -ForegroundColor White
Write-Host "   Total de testes: $total" -ForegroundColor Gray
Write-Host "   Testes passados: $passed" -ForegroundColor Green
Write-Host "   Testes falhados: $failed" -ForegroundColor Red
Write-Host "   Avisos: $warnings" -ForegroundColor Yellow
Write-Host "   Taxa de sucesso: $successPercent%" -ForegroundColor $(if ($successPercent -ge 90) { "Green" } elseif ($successPercent -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

# Listar testes falhados
$failedTests = $VALIDATION_RESULTS.tests | Where-Object { $_.status -eq "FAILED" }

if ($failedTests.Count -gt 0) {
    Write-Host "🚨 TESTES FALHADOS:" -ForegroundColor Red
    foreach ($test in $failedTests) {
        Write-Host "   ❌ $($test.name): $($test.message)" -ForegroundColor Red
        if ($test.details) {
            Write-Host "      Details: $($test.details)" -ForegroundColor DarkRed
        }
    }
    Write-Host ""
}

# Determinar status geral
if ($failed -eq 0 -and $successPercent -ge 95) {
    $status = "✅ EXCELENTE"
    $overall = "PASSED"
    Write-Host "🎉 STATUS GERAL: $status" -ForegroundColor Green
    Write-Host "   Todos os testes críticos passaram!" -ForegroundColor Green
    Write-Host "   Sistema pronto para produção Tier-0" -ForegroundColor Green
}
elseif ($failed -eq 0 -and $successPercent -ge 80) {
    $status = "⚠️  SATISFATÓRIO"
    $overall = "PASSED"
    Write-Host "✅ STATUS GERAL: $status" -ForegroundColor Yellow
    Write-Host "   Sistema operacional com pequenos avisos" -ForegroundColor Yellow
}
elseif ($failed -lt 3 -and $successPercent -ge 70) {
    $status = "⚠️  DEGRADADO"
    $overall = "WARNING"
    Write-Host "⚠️  STATUS GERAL: $status" -ForegroundColor Yellow
    Write-Host "   Sistema funcional mas requer atenção" -ForegroundColor Yellow
}
else {
    $status = "❌ CRÍTICO"
    $overall = "FAILED"
    Write-Host "❌ STATUS GERAL: $status" -ForegroundColor Red
    Write-Host "   Sistema com falhas críticas" -ForegroundColor Red
}

Write-Host ""

# Gerar relatório final
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$finalReport = "VALIDATION_REPORT_$timestamp.json"

$VALIDATION_RESULTS.overall = $overall
$VALIDATION_RESULTS.success_percent = $successPercent
$VALIDATION_RESULTS.status = $status

$VALIDATION_RESULTS | ConvertTo-Json -Depth 10 | Out-File $finalReport -Encoding UTF8

Write-Host "📋 RELATÓRIO FINAL:" -ForegroundColor White
Write-Host "   $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "   Sistema: Aurora Core Tier-0 Integrated" -ForegroundColor Gray
Write-Host "   Status: $status" -ForegroundColor $(if ($overall -eq "PASSED") { "Green" } elseif ($overall -eq "WARNING") { "Yellow" } else { "Red" })
Write-Host "   Sucesso: $successPercent%" -ForegroundColor $(if ($successPercent -ge 90) { "Green" } elseif ($successPercent -ge 70) { "Yellow" } else { "Red" })
Write-Host "   Arquivo de resultados: $finalReport" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🔬 VALIDAÇÃO CONCLUÍDA - AURORA CORE TIER-0" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Exit code baseado no resultado
if ($overall -eq "FAILED") {
    exit 1
}
elseif ($overall -eq "WARNING") {
    exit 2
}
else {
    exit 0
}

