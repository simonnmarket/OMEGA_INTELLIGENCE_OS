# ============================================================================
# NCNT FASE 2 - VERIFICAÇÃO COMPLETA E CERTIFICAÇÃO (VERSÃO SIMPLIFICADA)
# ============================================================================

$ErrorActionPreference = "Continue"
$BASE_DIR = "C:\Users\Lenovo\Projects\Aurora"
$REPORT_DIR = "$BASE_DIR\06-Monitoramento\logs"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$REPORT_FILE = "$REPORT_DIR\ncnt_verification_report_$TIMESTAMP.json"

if (-not (Test-Path $REPORT_DIR)) {
    New-Item -ItemType Directory -Path $REPORT_DIR -Force | Out-Null
}

function Get-FileHash256 {
    param([string]$FilePath)
    $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
    return $hash.Hash
}

function Get-StringHash256 {
    param([string]$String)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($String)
    $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    return ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "NCNT FASE 2 - VERIFICACAO E CERTIFICACAO COMPLETA" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# SEÇÃO 1: AMBIENTE
Write-Host "1. VERIFICACAO DE AMBIENTE" -ForegroundColor Yellow
Write-Host ""

$OS_INFO = "$($env:OS) - $($env:COMPUTERNAME)"
$OS_VERSION = [System.Environment]::OSVersion.VersionString
$OS_CHECKSUM = Get-StringHash256 "$OS_INFO $OS_VERSION"
Write-Host "   Sistema: $OS_INFO" -ForegroundColor White
Write-Host "   Versao: $OS_VERSION" -ForegroundColor White
Write-Host "   Checksum: $($OS_CHECKSUM.Substring(0, 16))..." -ForegroundColor Gray

try {
    $PYTHON_VERSION = python --version 2>&1
    $PYTHON_CHECKSUM = Get-StringHash256 $PYTHON_VERSION
    $PYTHON_MAJOR = (python -c "import sys; print(sys.version_info.major)" 2>&1)
    $PYTHON_MINOR = (python -c "import sys; print(sys.version_info.minor)" 2>&1)
    Write-Host "   Python: $PYTHON_VERSION" -ForegroundColor White
    Write-Host "   Checksum: $($PYTHON_CHECKSUM.Substring(0, 16))..." -ForegroundColor Gray
    if ([int]$PYTHON_MAJOR -eq 3 -and [int]$PYTHON_MINOR -ge 8) {
        Write-Host "   [OK] Python 3.8+ validado" -ForegroundColor Green
        $PYTHON_VALID = $true
    } else {
        Write-Host "   [FAIL] Python 3.8+ requerido" -ForegroundColor Red
        $PYTHON_VALID = $false
    }
} catch {
    Write-Host "   [FAIL] Python nao encontrado" -ForegroundColor Red
    $PYTHON_VALID = $false
    $PYTHON_VERSION = "NAO ENCONTRADO"
    $PYTHON_CHECKSUM = ""
}

$MISSING_PACKAGES = @()
foreach ($pkg in @("numpy", "pandas", "scipy")) {
    try {
        $v = python -c "import $pkg; print($pkg.__version__)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   [OK] $pkg : $v" -ForegroundColor Green
        } else {
            $MISSING_PACKAGES += $pkg
        }
    } catch {
        $MISSING_PACKAGES += $pkg
    }
}

# SEÇÃO 2: ESTRUTURA
Write-Host ""
Write-Host "2. VERIFICACAO DA ESTRUTURA" -ForegroundColor Yellow
Write-Host ""

$REQUIRED_DIRS = @(
    "00-Governanca",
    "01-Departamentos\Risk-Controls",
    "02-Processos-Chave\backtesting",
    "03-Operacoes-Diarias",
    "04-Infraestrutura",
    "05-Documentacao",
    "06-Monitoramento",
    "scripts"
)

$REQUIRED_FILES = @(
    "00-Governanca\genesis_includes_v3_complete.py",
    "00-Governanca\complexity_guard.py",
    "01-Departamentos\Risk-Controls\tier1_validator_v3_complete.py",
    "02-Processos-Chave\backtesting\backtest_runner_v3.py"
)

$MISSING_DIRS = @()
foreach ($dir in $REQUIRED_DIRS) {
    $path = Join-Path $BASE_DIR $dir
    if (Test-Path $path) {
        $count = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "   [OK] $dir ($count arquivos)" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] $dir" -ForegroundColor Red
        $MISSING_DIRS += $dir
    }
}

$MISSING_FILES = @()
foreach ($file in $REQUIRED_FILES) {
    $path = Join-Path $BASE_DIR $file
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        $hash = Get-FileHash256 $path
        Write-Host "   [OK] $file ($size bytes)" -ForegroundColor Green
        Write-Host "        Checksum: $($hash.Substring(0, 16))..." -ForegroundColor Gray
    } else {
        Write-Host "   [FAIL] $file" -ForegroundColor Red
        $MISSING_FILES += $file
    }
}

# SEÇÃO 3: TESTES FUNCIONAIS
Write-Host ""
Write-Host "3. TESTES FUNCIONAIS" -ForegroundColor Yellow
Write-Host ""

$TEST_RESULTS = @()

# Teste 1: Genesis Includes
Write-Host "   3.1 Genesis Includes v3.0:" -ForegroundColor Cyan
$genesisFile = Join-Path $BASE_DIR "00-Governanca\genesis_includes_v3_complete.py"
if (Test-Path $genesisFile) {
    $start = Get-Date
    $logFile = "$REPORT_DIR\genesis_test_$TIMESTAMP.log"
    python $genesisFile 2>&1 | Tee-Object -FilePath $logFile | Out-Null
    $exitCode = $LASTEXITCODE
    $elapsed = ((Get-Date) - $start).TotalSeconds
    
    $logContent = Get-Content $logFile -Raw
    if ($exitCode -eq 0 -and $logContent -match "GENESIS INCLUDES v3.0 - INTEGRIDADE VALIDADA") {
        Write-Host "      [PASS] Teste passou" -ForegroundColor Green
        Write-Host "      Tempo: $([math]::Round($elapsed, 2))s" -ForegroundColor White
        $TEST_RESULTS += "GENESIS: PASS"
    } else {
        Write-Host "      [FAIL] Teste falhou" -ForegroundColor Red
        $TEST_RESULTS += "GENESIS: FAIL"
    }
} else {
    Write-Host "      [MISSING] Arquivo nao encontrado" -ForegroundColor Red
    $TEST_RESULTS += "GENESIS: MISSING"
}

# Teste 2: Risk Validator
Write-Host ""
Write-Host "   3.2 Risk Validator v3.0:" -ForegroundColor Cyan
$riskFile = Join-Path $BASE_DIR "01-Departamentos\Risk-Controls\tier1_validator_v3_complete.py"
if (Test-Path $riskFile) {
    $start = Get-Date
    $logFile = "$REPORT_DIR\risk_test_$TIMESTAMP.log"
    python $riskFile 2>&1 | Tee-Object -FilePath $logFile | Out-Null
    $exitCode = $LASTEXITCODE
    $elapsed = ((Get-Date) - $start).TotalSeconds
    
    $logContent = Get-Content $logFile -Raw
    if ($exitCode -eq 0 -and $logContent -match "RISK VALIDATOR v3.0 - INTEGRIDADE VALIDADA") {
        Write-Host "      [PASS] Teste passou" -ForegroundColor Green
        Write-Host "      Tempo: $([math]::Round($elapsed, 2))s" -ForegroundColor White
        $TEST_RESULTS += "RISK_VALIDATOR: PASS"
    } else {
        Write-Host "      [FAIL] Teste falhou" -ForegroundColor Red
        $TEST_RESULTS += "RISK_VALIDATOR: FAIL"
    }
} else {
    Write-Host "      [MISSING] Arquivo nao encontrado" -ForegroundColor Red
    $TEST_RESULTS += "RISK_VALIDATOR: MISSING"
}

# Teste 3: Backtest Runner
Write-Host ""
Write-Host "   3.3 Backtest Runner v3.0:" -ForegroundColor Cyan
$backtestFile = Join-Path $BASE_DIR "02-Processos-Chave\backtesting\backtest_runner_v3.py"
if (Test-Path $backtestFile) {
    $start = Get-Date
    $logFile = "$REPORT_DIR\backtest_test_$TIMESTAMP.log"
    python $backtestFile 2>&1 | Tee-Object -FilePath $logFile | Out-Null
    $exitCode = $LASTEXITCODE
    $elapsed = ((Get-Date) - $start).TotalSeconds
    
    $logContent = Get-Content $logFile -Raw
    if ($exitCode -eq 0 -and $logContent -match "BACKTEST RUNNER v3.0 - INTEGRIDADE VALIDADA") {
        Write-Host "      [PASS] Teste passou" -ForegroundColor Green
        Write-Host "      Tempo: $([math]::Round($elapsed, 2))s" -ForegroundColor White
        $TEST_RESULTS += "BACKTEST_RUNNER: PASS"
    } else {
        Write-Host "      [FAIL] Teste falhou" -ForegroundColor Red
        $TEST_RESULTS += "BACKTEST_RUNNER: FAIL"
    }
} else {
    Write-Host "      [MISSING] Arquivo nao encontrado" -ForegroundColor Red
    $TEST_RESULTS += "BACKTEST_RUNNER: MISSING"
}

# SEÇÃO 4: ANÁLISE
Write-Host ""
Write-Host "4. ANALISE ESTATISTICA" -ForegroundColor Yellow
Write-Host ""

$PASS_COUNT = ($TEST_RESULTS | Where-Object { $_ -like "*PASS*" }).Count
$FAIL_COUNT = ($TEST_RESULTS | Where-Object { $_ -like "*FAIL*" -or $_ -like "*MISSING*" }).Count
$TOTAL_TESTS = $TEST_RESULTS.Count
$SUCCESS_RATE = if ($TOTAL_TESTS -gt 0) { [math]::Round(($PASS_COUNT * 100) / $TOTAL_TESTS, 2) } else { 0 }

Write-Host "   Testes Passados: $PASS_COUNT" -ForegroundColor Green
Write-Host "   Testes Falhados: $FAIL_COUNT" -ForegroundColor Red
Write-Host "   Total: $TOTAL_TESTS" -ForegroundColor White
Write-Host "   Taxa de Sucesso: $SUCCESS_RATE por cento" -ForegroundColor Cyan

# SEÇÃO 5: CERTIFICAÇÃO
Write-Host ""
Write-Host "5. CERTIFICACAO" -ForegroundColor Yellow
Write-Host ""

if ($FAIL_COUNT -eq 0 -and $PASS_COUNT -eq $TOTAL_TESTS -and $TOTAL_TESTS -ge 3) {
    $OVERALL_STATUS = "CERTIFIED"
    $CERT_LEVEL = "TIER-0 (GOLDMAN SACHS STANDARD)"
} elseif ($FAIL_COUNT -le 1 -and $SUCCESS_RATE -ge 80) {
    $OVERALL_STATUS = "CONDITIONALLY_CERTIFIED"
    $CERT_LEVEL = "TIER-1 (PRODUCTION READY)"
} elseif ($SUCCESS_RATE -ge 60) {
    $OVERALL_STATUS = "DEVELOPMENT_CERTIFIED"
    $CERT_LEVEL = "TIER-2 (DEVELOPMENT)"
} else {
    $OVERALL_STATUS = "NOT_CERTIFIED"
    $CERT_LEVEL = "FAILED"
}

Write-Host "   Status: $OVERALL_STATUS" -ForegroundColor $(if ($OVERALL_STATUS -eq "CERTIFIED") { "Green" } else { "Yellow" })
Write-Host "   Nivel: $CERT_LEVEL" -ForegroundColor Cyan

# Gerar relatório JSON
$report = @{
    verification_report = @{
        protocol_version = "NCNT_PHASE2_VERIFICATION_v1.0"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        auditor = "Sistema de Verificacao Independente (SVI)"
        environment = @{
            os = $OS_INFO
            python = $PYTHON_VERSION
            python_valid = $PYTHON_VALID
            missing_packages = $MISSING_PACKAGES
        }
        structure = @{
            missing_dirs = $MISSING_DIRS
            missing_files = $MISSING_FILES
        }
        tests = @{
            total = $TOTAL_TESTS
            passed = $PASS_COUNT
            failed = $FAIL_COUNT
            success_rate = $SUCCESS_RATE
            results = $TEST_RESULTS
        }
        certification = @{
            status = $OVERALL_STATUS
            level = $CERT_LEVEL
            date = (Get-Date -Format "yyyy-MM-dd")
        }
    }
}

$report | ConvertTo-Json -Depth 10 | Out-File -FilePath $REPORT_FILE -Encoding UTF8
$REPORT_CHECKSUM = Get-FileHash256 $REPORT_FILE

Write-Host ""
Write-Host "Relatorio gerado: $REPORT_FILE" -ForegroundColor Green
Write-Host "Checksum: $($REPORT_CHECKSUM.Substring(0, 32))..." -ForegroundColor Gray
Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "VERIFICACAO CONCLUIDA" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

if ($OVERALL_STATUS -eq "CERTIFIED" -or $OVERALL_STATUS -eq "CONDITIONALLY_CERTIFIED") {
    exit 0
} else {
    exit 1
}

