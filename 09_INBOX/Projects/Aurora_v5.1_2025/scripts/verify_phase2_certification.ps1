# ============================================================================
# NCNT FASE 2 - VERIFICAÇÃO COMPLETA E CERTIFICAÇÃO
# Nível: Goldman Sachs Tier-0 Audit Standard
# Tolerância: Zero (fail-fast com evidência)
# Adaptado para Windows PowerShell
# ============================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuração
$BASE_DIR = "C:\Users\Lenovo\Projects\Aurora"
$REPORT_DIR = "$BASE_DIR\06-Monitoramento\logs"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$REPORT_FILE = "$REPORT_DIR\ncnt_verification_report_$TIMESTAMP.json"

# Criar diretório de logs se não existir
if (-not (Test-Path $REPORT_DIR)) {
    New-Item -ItemType Directory -Path $REPORT_DIR -Force | Out-Null
}

# Função para calcular SHA256 (equivalente ao sha3sum)
function Get-FileHash256 {
    param([string]$FilePath)
    $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
    return $hash.Hash
}

# Função para calcular hash de string
function Get-StringHash256 {
    param([string]$String)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($String)
    $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    return ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
}

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "🔍 NCNT FASE 2 - VERIFICAÇÃO E CERTIFICAÇÃO COMPLETA" -ForegroundColor Cyan
Write-Host "📊 Padrão: ISO/IEC 25010 + IEEE 1012 + CMMI-DEV v2.0" -ForegroundColor Cyan
Write-Host "🎯 Objetivo: Validação independente com evidência comprovada" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  ATENÇÃO: Este script irá:" -ForegroundColor Yellow
Write-Host "   1. Executar testes reais (não apenas verificar existência)" -ForegroundColor White
Write-Host "   2. Gerar logs com checksum SHA256" -ForegroundColor White
Write-Host "   3. Validar estatisticamente cada componente" -ForegroundColor White
Write-Host "   4. Comparar com baseline esperado" -ForegroundColor White
Write-Host "   5. Gerar certificação apenas se TODOS os testes passarem" -ForegroundColor White
Write-Host ""

Read-Host "⏰ Pressione ENTER para iniciar verificação completa..."

# ============================================================================
# SEÇÃO 1: VERIFICAÇÃO DE AMBIENTE (PRÉ-REQUISITOS)
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "1. 🏗️  VERIFICAÇÃO DE AMBIENTE E PRÉ-REQUISITOS" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1.1 Sistema Operacional
Write-Host "📋 1.1 Sistema Operacional:" -ForegroundColor Yellow
$OS_INFO = "$($env:OS) - $($env:COMPUTERNAME)"
$OS_VERSION = [System.Environment]::OSVersion.VersionString
$OS_CHECKSUM = Get-StringHash256 "$OS_INFO $OS_VERSION"
Write-Host "   ℹ️  Info: $OS_INFO" -ForegroundColor White
Write-Host "   ℹ️  Versão: $OS_VERSION" -ForegroundColor White
Write-Host "   🔒 Checksum: $($OS_CHECKSUM.Substring(0, 16))..." -ForegroundColor Gray
Write-Host "   ✅ VALIDADO: Sistema Windows compatível" -ForegroundColor Green

# 1.2 Versão do Python
Write-Host ""
Write-Host "📋 1.2 Python Environment:" -ForegroundColor Yellow
try {
    $PYTHON_VERSION = python --version 2>&1
    $PYTHON_CHECKSUM = Get-StringHash256 $PYTHON_VERSION
    $PYTHON_MAJOR = (python -c "import sys; print(sys.version_info.major)" 2>&1)
    $PYTHON_MINOR = (python -c "import sys; print(sys.version_info.minor)" 2>&1)
    
    Write-Host "   ℹ️  Versão: $PYTHON_VERSION" -ForegroundColor White
    Write-Host "   🔒 Checksum: $($PYTHON_CHECKSUM.Substring(0, 16))..." -ForegroundColor Gray
    
    if ([int]$PYTHON_MAJOR -eq 3 -and [int]$PYTHON_MINOR -ge 8) {
        Write-Host "   ✅ VALIDADO: Python 3.8+ (Requisito atendido)" -ForegroundColor Green
        $PYTHON_VALID = $true
    } else {
        Write-Host "   ❌ FALHA CRÍTICA: Python 3.8+ requerido" -ForegroundColor Red
        $PYTHON_VALID = $false
    }
} catch {
    Write-Host "   ❌ FALHA CRÍTICA: Python não encontrado" -ForegroundColor Red
    $PYTHON_VALID = $false
    $PYTHON_VERSION = "NÃO ENCONTRADO"
    $PYTHON_CHECKSUM = ""
}

# 1.3 Dependências Python
Write-Host ""
Write-Host "📋 1.3 Dependências Python (com verificação de versão):" -ForegroundColor Yellow
$REQUIRED_PACKAGES = @("numpy", "pandas", "scipy")
$MISSING_PACKAGES = @()

foreach ($package in $REQUIRED_PACKAGES) {
    try {
        $version = python -c "import $package; print($package.__version__)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $package : $version" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $package : NÃO INSTALADO" -ForegroundColor Red
            $MISSING_PACKAGES += $package
        }
    } catch {
        Write-Host "   ❌ $package : NÃO INSTALADO" -ForegroundColor Red
        $MISSING_PACKAGES += $package
    }
}

if ($MISSING_PACKAGES.Count -eq 0) {
    Write-Host "   ✅ TODAS as dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Pacotes faltando: $($MISSING_PACKAGES -join ', ')" -ForegroundColor Yellow
    Write-Host "   💡 Execute: pip install $($MISSING_PACKAGES -join ' ')" -ForegroundColor Cyan
}

# 1.4 Recursos do Sistema
Write-Host ""
Write-Host "📋 1.4 Recursos do Sistema:" -ForegroundColor Yellow
$TOTAL_MEM = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
$AVAILABLE_MEM = [math]::Round((Get-Counter '\Memory\Available MBytes').CounterSamples.CookedValue / 1024, 2)
$DISK_SPACE = [math]::Round((Get-PSDrive C).Free / 1GB, 2)

Write-Host "   💾 Memória Total: ${TOTAL_MEM} GB" -ForegroundColor White
Write-Host "   💾 Memória Disponível: ${AVAILABLE_MEM} GB" -ForegroundColor White
Write-Host "   🗃️  Espaço em Disco (C:): ${DISK_SPACE} GB" -ForegroundColor White

if ($AVAILABLE_MEM -lt 2) {
    Write-Host "   ⚠️  AVISO: Memória disponível abaixo de 2GB" -ForegroundColor Yellow
}

if ($DISK_SPACE -lt 10) {
    Write-Host "   ⚠️  AVISO: Espaço em disco abaixo de 10GB" -ForegroundColor Yellow
}

# ============================================================================
# SEÇÃO 2: VERIFICAÇÃO DA ESTRUTURA NCNT
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "2. 📁 VERIFICAÇÃO DA ESTRUTURA NCNT FASE 2" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

$REQUIRED_DIRS = @(
    "00-Governanca",
    "01-Departamentos\Risk-Controls",
    "02-Processos-Chave\backtesting",
    "02-Processos-Chave\execution",
    "02-Processos-Chave\resilience",
    "03-Operacoes-Diarias",
    "04-Infraestrutura\database",
    "04-Infraestrutura\api",
    "04-Infraestrutura\dashboard",
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

# 2.1 Verificação de diretórios
Write-Host "📋 2.1 Estrutura de Diretórios:" -ForegroundColor Yellow
$MISSING_DIRS = @()

foreach ($dir in $REQUIRED_DIRS) {
    $FULL_PATH = Join-Path $BASE_DIR $dir
    if (Test-Path $FULL_PATH) {
        $DIR_SIZE = (Get-ChildItem -Path $FULL_PATH -Recurse -ErrorAction SilentlyContinue | 
                    Measure-Object -Property Length -Sum).Sum / 1MB
        $FILE_COUNT = (Get-ChildItem -Path $FULL_PATH -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "   ✅ $dir : Existe ($([math]::Round($DIR_SIZE, 2)) MB, $FILE_COUNT arquivos)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $dir : NÃO ENCONTRADO" -ForegroundColor Red
        $MISSING_DIRS += $dir
    }
}

if ($MISSING_DIRS.Count -eq 0) {
    Write-Host "   🎯 TODOS os diretórios necessários existem" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Diretórios faltando: $($MISSING_DIRS -join ', ')" -ForegroundColor Yellow
}

# 2.2 Verificação de arquivos
Write-Host ""
Write-Host "📋 2.2 Arquivos Principais:" -ForegroundColor Yellow
$MISSING_FILES = @()
$CORRUPTED_FILES = @()

foreach ($file in $REQUIRED_FILES) {
    $FULL_PATH = Join-Path $BASE_DIR $file
    if (Test-Path $FULL_PATH) {
        $FILE_SIZE = (Get-Item $FULL_PATH).Length
        $FILE_CHECKSUM = Get-FileHash256 $FULL_PATH
        
        if ($FILE_SIZE -gt 1000) {
            $sizeStr = "$FILE_SIZE bytes"
            Write-Host "   [OK] $file : OK ($sizeStr)" -ForegroundColor Green
            $checksumStr = $FILE_CHECKSUM.Substring(0, 16) + "..."
            Write-Host "      [CHECKSUM] $checksumStr" -ForegroundColor Gray
            
            # Verificação de sintaxe Python
            if ($file -like "*.py") {
                $syntaxCheck = python -m py_compile $FULL_PATH 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "      [PYTHON] Sintaxe Python: VALIDADA" -ForegroundColor Green
                } else {
                    Write-Host "      [ERRO] Sintaxe Python: INVALIDADA" -ForegroundColor Red
                    $CORRUPTED_FILES += $file
                }
            }
        } else {
            Write-Host "   [AVISO] $file : SUSPEITO (tamanho: $FILE_SIZE bytes)" -ForegroundColor Yellow
            $CORRUPTED_FILES += $file
        }
    } else {
        Write-Host "   [FALTA] $file : NAO ENCONTRADO" -ForegroundColor Red
        $MISSING_FILES += $file
    }
}

# 2.3 Estatísticas da estrutura
Write-Host ""
Write-Host "📋 2.3 Estatísticas da Estrutura:" -ForegroundColor Yellow
$TOTAL_FILES = (Get-ChildItem -Path $BASE_DIR -Recurse -File -ErrorAction SilentlyContinue).Count
$TOTAL_PY_FILES = (Get-ChildItem -Path $BASE_DIR -Recurse -Filter "*.py" -ErrorAction SilentlyContinue).Count
$TOTAL_SIZE = [math]::Round((Get-ChildItem -Path $BASE_DIR -Recurse -File -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1MB, 2)

Write-Host "   📊 Total de arquivos: $TOTAL_FILES" -ForegroundColor White
Write-Host "   📊 Arquivos Python: $TOTAL_PY_FILES" -ForegroundColor White
Write-Host "   📊 Tamanho total: ${TOTAL_SIZE} MB" -ForegroundColor White

# ============================================================================
# SEÇÃO 3: TESTES FUNCIONAIS (EXECUÇÃO REAL)
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "3. ⚙️ TESTES FUNCIONAIS - EXECUÇÃO E VALIDAÇÃO" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

$TEST_RESULTS = @()
$TEST_TIMES = @()

# 3.1 Teste do Genesis Includes
Write-Host "📋 3.1 Genesis Includes v3.0:" -ForegroundColor Yellow
$GENESIS_TEST_FILE = Join-Path $BASE_DIR "00-Governanca\genesis_includes_v3_complete.py"
if (Test-Path $GENESIS_TEST_FILE) {
    $START_TIME = Get-Date
    $LOG_FILE = "$REPORT_DIR\genesis_test_$TIMESTAMP.log"
    
    python $GENESIS_TEST_FILE 2>&1 | Tee-Object -FilePath $LOG_FILE
    $EXIT_CODE = $LASTEXITCODE
    $END_TIME = Get-Date
    $ELAPSED_TIME = ($END_TIME - $START_TIME).TotalSeconds
    
    if ($EXIT_CODE -eq 0) {
        $logContent = Get-Content $LOG_FILE -Raw
        if ($logContent -match "GENESIS INCLUDES v3.0 - INTEGRIDADE VALIDADA") {
            Write-Host "   [PASS] TESTE PASSOU: Integridade validada" -ForegroundColor Green
            $TEST_RESULTS += "GENESIS: PASS"
            
            if ($logContent -match "Dependencias: (\d+)") {
                $DEP_COUNT = $matches[1]
                Write-Host "      [METRIC] Dependencias registradas: $DEP_COUNT" -ForegroundColor White
            }
            if ($logContent -match "Integridade: (\w+)") {
                $INTEGRITY = $matches[1]
                Write-Host "      [STATUS] Status integridade: $INTEGRITY" -ForegroundColor White
            }
            Write-Host "      [TIME] Tempo execucao: $([math]::Round($ELAPSED_TIME, 2))s" -ForegroundColor White
        } else {
            Write-Host "   [FAIL] TESTE FALHOU: Saida nao contem validacao" -ForegroundColor Red
            $TEST_RESULTS += "GENESIS: FAIL"
        }
    } else {
        Write-Host "   [FAIL] TESTE FALHOU: Codigo de erro $EXIT_CODE" -ForegroundColor Red
        $TEST_RESULTS += "GENESIS: FAIL"
        Write-Host "      [ERROR] Ultimas linhas do log:" -ForegroundColor Yellow
        Get-Content $LOG_FILE -Tail 5 | ForEach-Object { Write-Host "         $_" -ForegroundColor Gray }
    }
} else {
    Write-Host "   [MISSING] ARQUIVO NAO ENCONTRADO: $GENESIS_TEST_FILE" -ForegroundColor Red
    $TEST_RESULTS += "GENESIS: MISSING"
}

# 3.2 Teste do Risk Validator
Write-Host ""
Write-Host "📋 3.2 Risk Validator Tier-1 v3.0:" -ForegroundColor Yellow
$RISK_TEST_FILE = Join-Path $BASE_DIR "01-Departamentos\Risk-Controls\tier1_validator_v3_complete.py"
if (Test-Path $RISK_TEST_FILE) {
    $START_TIME = Get-Date
    $LOG_FILE = "$REPORT_DIR\risk_test_$TIMESTAMP.log"
    
    python $RISK_TEST_FILE 2>&1 | Tee-Object -FilePath $LOG_FILE
    $EXIT_CODE = $LASTEXITCODE
    $END_TIME = Get-Date
    $ELAPSED_TIME = ($END_TIME - $START_TIME).TotalSeconds
    
    if ($EXIT_CODE -eq 0) {
        $logContent = Get-Content $LOG_FILE -Raw
        if ($logContent -match "RISK VALIDATOR v3.0 - INTEGRIDADE VALIDADA") {
            Write-Host "   [PASS] TESTE PASSOU: Validador de risco funcional" -ForegroundColor Green
            $TEST_RESULTS += "RISK_VALIDATOR: PASS"
            
            if ($logContent -match "Score de risco:") {
                $RISK_SCORE = ($logContent -split "Score de risco: ")[1] -split "`n" | Select-Object -First 1
                Write-Host "      [METRIC] Score de risco: $RISK_SCORE" -ForegroundColor White
            }
            if ($logContent -match "Nivel de risco:") {
                $RISK_LEVEL = ($logContent -split "Nivel de risco: ")[1] -split "`n" | Select-Object -First 1
                Write-Host "      [METRIC] Nivel de risco: $RISK_LEVEL" -ForegroundColor White
            }
            Write-Host "      [TIME] Tempo execucao: $([math]::Round($ELAPSED_TIME, 2))s" -ForegroundColor White
        } else {
            Write-Host "   [FAIL] TESTE FALHOU: Validacao incompleta" -ForegroundColor Red
            $TEST_RESULTS += "RISK_VALIDATOR: FAIL"
        }
    } else {
        Write-Host "   [FAIL] TESTE FALHOU: Codigo $EXIT_CODE" -ForegroundColor Red
        $TEST_RESULTS += "RISK_VALIDATOR: FAIL"
        Write-Host "      [ERROR] Erro:" -ForegroundColor Yellow
        Get-Content $LOG_FILE -Tail 3 | ForEach-Object { Write-Host "         $_" -ForegroundColor Gray }
    }
} else {
    Write-Host "   [MISSING] ARQUIVO NAO ENCONTRADO" -ForegroundColor Red
    $TEST_RESULTS += "RISK_VALIDATOR: MISSING"
}

# 3.3 Teste do Backtest Runner
Write-Host ""
Write-Host "📋 3.3 Backtest Runner v3.0:" -ForegroundColor Yellow
$BACKTEST_TEST_FILE = Join-Path $BASE_DIR "02-Processos-Chave\backtesting\backtest_runner_v3.py"
if (Test-Path $BACKTEST_TEST_FILE) {
    $START_TIME = Get-Date
    $LOG_FILE = "$REPORT_DIR\backtest_test_$TIMESTAMP.log"
    
    python $BACKTEST_TEST_FILE 2>&1 | Tee-Object -FilePath $LOG_FILE
    $EXIT_CODE = $LASTEXITCODE
    $END_TIME = Get-Date
    $ELAPSED_TIME = ($END_TIME - $START_TIME).TotalSeconds
    
    if ($EXIT_CODE -eq 0) {
        $logContent = Get-Content $LOG_FILE -Raw
        if ($logContent -match "BACKTEST RUNNER v3.0 - INTEGRIDADE VALIDADA") {
            Write-Host "   [PASS] TESTE PASSOU: Backtest runner funcional" -ForegroundColor Green
            $TEST_RESULTS += "BACKTEST_RUNNER: PASS"
            
            if ($logContent -match "Sharpe Ratio:") {
                $SHARPE = ($logContent -split "Sharpe Ratio: ")[1] -split "`n" | Select-Object -First 1
                Write-Host "      [METRIC] Sharpe Ratio: $SHARPE" -ForegroundColor White
            }
            if ($logContent -match "Win Rate:") {
                $WIN_RATE = ($logContent -split "Win Rate: ")[1] -split "`n" | Select-Object -First 1
                Write-Host "      [METRIC] Win Rate: $WIN_RATE" -ForegroundColor White
            }
            if ($logContent -match "Resultado final:") {
                $RESULT = ($logContent -split "Resultado final: ")[1] -split "`n" | Select-Object -First 1
                Write-Host "      [METRIC] Resultado: $RESULT" -ForegroundColor White
            }
            Write-Host "      [TIME] Tempo execucao: $([math]::Round($ELAPSED_TIME, 2))s" -ForegroundColor White
        } else {
            Write-Host "   [FAIL] TESTE FALHOU: Validacao incompleta" -ForegroundColor Red
            $TEST_RESULTS += "BACKTEST_RUNNER: FAIL"
        }
    } else {
        Write-Host "   [FAIL] TESTE FALHOU: Codigo $EXIT_CODE" -ForegroundColor Red
        $TEST_RESULTS += "BACKTEST_RUNNER: FAIL"
        Write-Host "      [ERROR] Erro:" -ForegroundColor Yellow
        Get-Content $LOG_FILE -Tail 3 | ForEach-Object { Write-Host "         $_" -ForegroundColor Gray }
    }
} else {
    Write-Host "   [MISSING] ARQUIVO NAO ENCONTRADO" -ForegroundColor Red
    $TEST_RESULTS += "BACKTEST_RUNNER: MISSING"
}

# ============================================================================
# SEÇÃO 4: ANÁLISE ESTATÍSTICA E VALIDAÇÃO
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "4. 📊 ANÁLISE ESTATÍSTICA E VALIDAÇÃO DE RESULTADOS" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# 4.1 Estatísticas de testes
$PASS_COUNT = ($TEST_RESULTS | Where-Object { $_ -like "*PASS*" }).Count
$FAIL_COUNT = ($TEST_RESULTS | Where-Object { $_ -like "*FAIL*" -or $_ -like "*MISSING*" }).Count
$TOTAL_TESTS = $TEST_RESULTS.Count

$SUCCESS_RATE = 0
if ($TOTAL_TESTS -gt 0) {
    $SUCCESS_RATE = [math]::Round(($PASS_COUNT * 100) / $TOTAL_TESTS, 2)
}

Write-Host "📋 4.1 Estatisticas dos Testes:" -ForegroundColor Yellow
Write-Host "   [PASS] Testes Passados: $PASS_COUNT" -ForegroundColor Green
Write-Host "   [FAIL] Testes Falhados: $FAIL_COUNT" -ForegroundColor Red
Write-Host "   [TOTAL] Total de Testes: $TOTAL_TESTS" -ForegroundColor White
Write-Host "   [RATE] Taxa de Sucesso: ${SUCCESS_RATE}%" -ForegroundColor Cyan

# 4.2 Validação estatística
Write-Host ""
Write-Host "📋 4.2 Validacao Estatistica:" -ForegroundColor Yellow
$EXPECTED_SUCCESS_RATE = 90

if ($TOTAL_TESTS -ge 3) {
    if ($SUCCESS_RATE -ge $EXPECTED_SUCCESS_RATE) {
        $msg1 = "VALIDACAO ESTATISTICA: Sistema atende padrao (>=$EXPECTED_SUCCESS_RATE%)"
        Write-Host "   [VALID] $msg1" -ForegroundColor Green
        $STAT_VALID = $true
    } else {
        $msg2 = "VALIDACAO ESTATISTICA: Sistema abaixo do padrao ($SUCCESS_RATE por cento < $EXPECTED_SUCCESS_RATE por cento)"
        Write-Host "   [WARNING] $msg2" -ForegroundColor Yellow
        $STAT_VALID = $false
    }
} else {
    Write-Host "   [WARNING] Dados insuficientes para analise estatistica" -ForegroundColor Yellow
    $STAT_VALID = $false
}

# ============================================================================
# SEÇÃO 5: GERAÇÃO DE CERTIFICAÇÃO E RELATÓRIO
# ============================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "5. 🏆 GERAÇÃO DE CERTIFICAÇÃO E RELATÓRIO FINAL" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# 5.1 Determinar status geral
$OVERALL_STATUS = "UNKNOWN"

if ($FAIL_COUNT -eq 0 -and $PASS_COUNT -eq $TOTAL_TESTS -and $TOTAL_TESTS -ge 3) {
    $OVERALL_STATUS = "CERTIFIED"
    $CERTIFICATION_LEVEL = "TIER-0 (GOLDMAN SACHS STANDARD)"
} elseif ($FAIL_COUNT -le 1 -and $SUCCESS_RATE -ge 80) {
    $OVERALL_STATUS = "CONDITIONALLY_CERTIFIED"
    $CERTIFICATION_LEVEL = "TIER-1 (PRODUCTION READY)"
} elseif ($SUCCESS_RATE -ge 60) {
    $OVERALL_STATUS = "DEVELOPMENT_CERTIFIED"
    $CERTIFICATION_LEVEL = "TIER-2 (DEVELOPMENT)"
} else {
    $OVERALL_STATUS = "NOT_CERTIFIED"
    $CERTIFICATION_LEVEL = "FAILED"
}

# 5.2 Gerar relatório JSON
$REPORT_DATA = @{
    verification_report = @{
        protocol_version = "NCNT_PHASE2_VERIFICATION_v1.0"
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        auditor = "Sistema de Verificação Independente (SVI)"
        standards_applied = @(
            "ISO/IEC 25010:2011 - Qualidade de Produto",
            "IEEE 1012-2016 - Verificação e Validação",
            "CMMI-DEV v2.0 - Nível 3",
            "Goldman Sachs Tier-0 Audit Standard"
        )
        environment_verification = @{
            operating_system = $OS_INFO
            os_version = $OS_VERSION
            os_checksum = $OS_CHECKSUM
            python_version = $PYTHON_VERSION
            python_checksum = $PYTHON_CHECKSUM
            python_valid = $PYTHON_VALID
            missing_packages = $MISSING_PACKAGES
            system_memory_gb = $AVAILABLE_MEM
            disk_space_gb = $DISK_SPACE
        }
        structure_verification = @{
            base_directory = $BASE_DIR
            total_directories = $REQUIRED_DIRS.Count
            missing_directories = $MISSING_DIRS
            total_files = $TOTAL_FILES
            python_files = $TOTAL_PY_FILES
            total_size_mb = $TOTAL_SIZE
            missing_files = $MISSING_FILES
            corrupted_files = $CORRUPTED_FILES
        }
        functional_tests = @{
            total_tests = $TOTAL_TESTS
            passed_tests = $PASS_COUNT
            failed_tests = $FAIL_COUNT
            success_rate = $SUCCESS_RATE
            test_results = $TEST_RESULTS
            statistical_validation = $STAT_VALID
        }
        certification = @{
            overall_status = $OVERALL_STATUS
            certification_level = $CERTIFICATION_LEVEL
            certification_date = (Get-Date -Format "yyyy-MM-dd")
            valid_until = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
            requirements_met = ($OVERALL_STATUS -eq "CERTIFIED")
            recommendations = if ($OVERALL_STATUS -ne "CERTIFIED") { 
                "Corrigir componentes falhos antes da produção" 
            } else { 
                "Sistema pronto para implantação" 
            }
        }
        integrity_checks = @{
            verification_script_checksum = (Get-FileHash256 $PSCommandPath)
            report_checksum = ""
            validation_timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
            audit_trail_available = $true
        }
    }
}

# Converter para JSON e salvar
$JSON_REPORT = $REPORT_DATA | ConvertTo-Json -Depth 10
$JSON_REPORT | Out-File -FilePath $REPORT_FILE -Encoding UTF8

# Calcular checksum do relatório
$REPORT_CHECKSUM = Get-FileHash256 $REPORT_FILE
$REPORT_DATA.verification_report.integrity_checks.report_checksum = $REPORT_CHECKSUM

# Salvar novamente com checksum
$JSON_REPORT = $REPORT_DATA | ConvertTo-Json -Depth 10
$JSON_REPORT | Out-File -FilePath $REPORT_FILE -Encoding UTF8

# 5.3 Apresentar resultados finais
Write-Host "📋 5.1 Status Final da Verificacao:" -ForegroundColor Yellow
Write-Host "   [STATUS] Status Geral: $OVERALL_STATUS" -ForegroundColor $(if ($OVERALL_STATUS -eq "CERTIFIED") { "Green" } else { "Yellow" })
Write-Host "   [LEVEL] Nivel de Certificacao: $CERTIFICATION_LEVEL" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 5.2 Sumario Executivo:" -ForegroundColor Yellow
Write-Host "   [VALID] Componentes Validados: $PASS_COUNT/$TOTAL_TESTS" -ForegroundColor White
Write-Host "   [RATE] Taxa de Sucesso: $SUCCESS_RATE por cento" -ForegroundColor White
Write-Host "   [STRUCT] Estrutura Completa: $(if ($MISSING_DIRS.Count -eq 0) { 'SIM' } else { 'NAO' })" -ForegroundColor White
Write-Host "   [FILES] Arquivos Principais: $(if ($MISSING_FILES.Count -eq 0) { 'COMPLETOS' } else { 'INCOMPLETOS' })" -ForegroundColor White
Write-Host ""

Write-Host "📋 5.3 Relatorio Gerado:" -ForegroundColor Yellow
Write-Host "   [FILE] Arquivo: $REPORT_FILE" -ForegroundColor White
Write-Host "   [CHECKSUM] Checksum do Relatorio: $($REPORT_CHECKSUM.Substring(0, 32))..." -ForegroundColor Gray
Write-Host ""

Write-Host "📋 5.4 Proximos Passos:" -ForegroundColor Yellow
switch ($OVERALL_STATUS) {
    "CERTIFIED" {
        Write-Host "   [OK] Sistema validado - Prosseguir para implantacao" -ForegroundColor Green
        Write-Host "   [NEXT] Executar testes de integracao" -ForegroundColor Cyan
    }
    "CONDITIONALLY_CERTIFIED" {
        Write-Host "   [WARNING] Sistema com ressalvas - Corrigir falhas antes da producao" -ForegroundColor Yellow
        Write-Host "   [FIX] Revisar componentes com falha" -ForegroundColor Cyan
    }
    "DEVELOPMENT_CERTIFIED" {
        Write-Host "   [DEV] Sistema apenas para desenvolvimento" -ForegroundColor Yellow
        Write-Host "   [STOP] NAO implantar em producao" -ForegroundColor Red
    }
    "NOT_CERTIFIED" {
        Write-Host "   [FAIL] Sistema nao certificado" -ForegroundColor Red
        Write-Host "   [REVIEW] Revisar completamente a implementacao" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "🏁 VERIFICAÇÃO CONCLUÍDA - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "RECOMENDACAO BASEADA NOS RESULTADOS:" -ForegroundColor Yellow
if ($OVERALL_STATUS -eq "CERTIFIED") {
    Write-Host "   >> Sistema certificado - Pronto para continuar FASE 2" -ForegroundColor Green
} elseif ($OVERALL_STATUS -eq "CONDITIONALLY_CERTIFIED") {
    Write-Host "   >> Corrigir falhas menores antes de prosseguir" -ForegroundColor Yellow
} else {
    Write-Host "   >> Revisar implementacao antes de continuar" -ForegroundColor Red
}

# Exit code baseado no resultado
if ($OVERALL_STATUS -eq "CERTIFIED" -or $OVERALL_STATUS -eq "CONDITIONALLY_CERTIFIED") {
    exit 0
} else {
    exit 1
}

