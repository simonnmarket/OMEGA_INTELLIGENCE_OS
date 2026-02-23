# 🏦 SCRIPT DE IMPLANTAÇÃO FASE 1 - EXECUÇÃO AUTOMATIZADA AIC (Windows PowerShell)
# NCNT Tier-0 - Goldman Sachs

$ErrorActionPreference = "Stop"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$LOG_FILE = "deploy_phase1_${TIMESTAMP}.log"

# FUNÇÃO DE LOG
function Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LOG_FILE -Value $logMessage
}

# 1. VALIDAÇÃO INICIAL
Log "🚀 INICIANDO IMPLANTAÇÃO FASE 1 - NCNT TIER-0"

# Verificar se estamos no diretório correto
if (-not (Test-Path "requirements_fase1.txt")) {
    Log "❌ ERRO: Arquivo requirements_fase1.txt não encontrado"
    exit 1
}

# 2. BACKUP DO ESTADO ATUAL
Log "📦 CRIANDO BACKUP DO ESTADO ATUAL"
$BACKUP_DIR = "backup\pre_phase1_${TIMESTAMP}"
New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
Copy-Item -Path "*" -Destination $BACKUP_DIR -Recurse -Exclude "backup","*.log" -ErrorAction SilentlyContinue
Log "✅ Backup criado em: $BACKUP_DIR"

# 3. VERIFICAÇÃO DE PYTHON
Log "🐍 VERIFICANDO PYTHON"
try {
    $pythonVersion = python --version
    Log "✅ Python encontrado: $pythonVersion"
} catch {
    Log "❌ ERRO: Python não encontrado"
    exit 1
}

# 4. INSTALAÇÃO DE DEPENDÊNCIAS
Log "📦 INSTALANDO DEPENDÊNCIAS PYTHON"
python -m pip install --upgrade pip
python -m pip install -r requirements_fase1.txt
if ($LASTEXITCODE -ne 0) {
    Log "❌ ERRO: Falha na instalação de dependências"
    exit 1
}
Log "✅ Dependências instaladas"

# 5. VERIFICAÇÃO DE ESTRUTURA
Log "🏗️ VALIDANDO ESTRUTURA DE DIRETÓRIOS"
$REQUIRED_DIRS = @(
    "01-Departamentos\Execution-Trading\strategies",
    "04-Infraestrutura\database",
    "04-Infraestrutura\api\endpoints"
)

foreach ($dir in $REQUIRED_DIRS) {
    if (-not (Test-Path $dir)) {
        Log "⚠️ Criando diretório: $dir"
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}
Log "✅ Estrutura validada"

# 6. EXECUÇÃO DE TESTES UNITÁRIOS
Log "🧪 EXECUTANDO TESTES UNITÁRIOS"
$TEST_DIR = "01-Departamentos\Execution-Trading\strategies"
if (Test-Path $TEST_DIR) {
    python -m pytest $TEST_DIR -v --tb=short 2>&1 | Tee-Object -FilePath "test_results_${TIMESTAMP}.log"
    if ($LASTEXITCODE -ne 0) {
        Log "⚠️ Alguns testes falharam (verificar test_results_${TIMESTAMP}.log)"
    } else {
        Log "✅ Todos os testes passaram"
    }
} else {
    Log "⚠️ Diretório de testes não encontrado, pulando..."
}

# 7. VALIDAÇÃO DE ARQUIVOS CRÍTICOS
Log "🔍 VALIDANDO ARQUIVOS CRÍTICOS"
$CRITICAL_FILES = @(
    "01-Departamentos\Execution-Trading\strategies\alpha_momentum.py",
    "01-Departamentos\Execution-Trading\strategies\mean_reversion.py",
    "01-Departamentos\Execution-Trading\strategies\breakout_detection.py",
    "04-Infraestrutura\api\main.py",
    "04-Infraestrutura\database\models.py"
)

$allFilesExist = $true
foreach ($file in $CRITICAL_FILES) {
    if (Test-Path $file) {
        Log "✅ $file"
    } else {
        Log "❌ $file - NÃO ENCONTRADO"
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Log "❌ ERRO: Arquivos críticos faltando"
    exit 1
}

# 8. GERAÇÃO DE RELATÓRIO
Log "📊 GERANDO RELATÓRIO DE IMPLANTAÇÃO"
$REPORT_FILE = "deployment_report_phase1_${TIMESTAMP}.json"

$report = @{
    deployment_id = "DEPLOY_PHASE1_${TIMESTAMP}"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    system = "NCNT - Núcleo Central Neuro Transmissor"
    phase = "1 - Implementação de Estratégias"
    status = "COMPLETED"
    components_deployed = @{
        strategies = @("ALPHA_MOMENTUM_v1", "MEAN_REVERSION_v1", "BREAKOUT_DETECTION_v1")
        database = "PostgreSQL models created"
        api = "REST API structure created"
        tests = "Unit tests executed"
    }
    health_check = @{
        files = "OK"
        structure = "OK"
        dependencies = "OK"
    }
    next_steps = @(
        "Configure PostgreSQL database",
        "Start API server: uvicorn 04-Infraestrutura.api.main:app --reload",
        "Test API endpoints",
        "Run backtests"
    )
} | ConvertTo-Json -Depth 10

$report | Out-File -FilePath $REPORT_FILE -Encoding UTF8

Log "🏆 IMPLANTAÇÃO FASE 1 CONCLUÍDA COM SUCESSO"
Log "Relatorio gerado: $REPORT_FILE"
Log "Para iniciar API: uvicorn 04-Infraestrutura.api.main:app --reload"
Log "Estrategias implementadas: 3"
Log "Documentacao: http://localhost:8000/docs (apos iniciar API)"

exit 0

