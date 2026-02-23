# 🏦 SCRIPT DE VALIDAÇÃO PÓS-IMPLANTAÇÃO FASE 1
# NCNT Tier-0 - Goldman Sachs

$ErrorActionPreference = "Continue"
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  VALIDAÇÃO FASE 1 - NCNT TIER-0" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Verificar estrutura de arquivos
Write-Host "1. Verificando estrutura de arquivos..." -ForegroundColor Yellow
$CRITICAL_FILES = @(
    "01-Departamentos\Execution-Trading\strategies\alpha_momentum.py",
    "01-Departamentos\Execution-Trading\strategies\mean_reversion.py",
    "01-Departamentos\Execution-Trading\strategies\breakout_detection.py",
    "01-Departamentos\Execution-Trading\strategies\base_strategy.py",
    "04-Infraestrutura\api\main.py",
    "04-Infraestrutura\api\endpoints\strategies.py",
    "04-Infraestrutura\database\models.py",
    "04-Infraestrutura\database\connection.py",
    "requirements_fase1.txt"
)

$allFilesExist = $true
foreach ($file in $CRITICAL_FILES) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - NÃO ENCONTRADO" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if ($allFilesExist) {
    Write-Host "`n✅ Todos os arquivos críticos encontrados`n" -ForegroundColor Green
} else {
    Write-Host "`n❌ Alguns arquivos críticos estão faltando`n" -ForegroundColor Red
}

# 2. Verificar imports Python
Write-Host "2. Verificando imports Python..." -ForegroundColor Yellow
try {
    python -c "import sys; sys.path.insert(0, '.'); from strategies import AlphaMomentumStrategy, MeanReversionStrategy, BreakoutDetectionStrategy; print('✅ Imports OK')"
    Write-Host "  ✅ Imports funcionando corretamente" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️ Erro nos imports (pode ser normal se dependências não instaladas)" -ForegroundColor Yellow
}

# 3. Verificar dependências
Write-Host "`n3. Verificando dependências..." -ForegroundColor Yellow
$REQUIRED_PACKAGES = @("fastapi", "pandas", "numpy", "sqlalchemy")
foreach ($package in $REQUIRED_PACKAGES) {
    try {
        python -c "import $package" 2>&1 | Out-Null
        Write-Host "  ✅ $package instalado" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $package não instalado" -ForegroundColor Red
    }
}

# 4. Verificar estrutura de diretórios
Write-Host "`n4. Verificando estrutura de diretórios..." -ForegroundColor Yellow
$REQUIRED_DIRS = @(
    "01-Departamentos\Execution-Trading\strategies",
    "04-Infraestrutura\database",
    "04-Infraestrutura\api\endpoints",
    "tests"
)

foreach ($dir in $REQUIRED_DIRS) {
    if (Test-Path $dir) {
        Write-Host "  ✅ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dir - NÃO ENCONTRADO" -ForegroundColor Red
    }
}

# 5. Resumo
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DA VALIDAÇÃO" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Instalar dependências: pip install -r requirements_fase1.txt" -ForegroundColor White
Write-Host "  2. Executar testes: pytest tests/test_strategies.py -v" -ForegroundColor White
Write-Host "  3. Iniciar API: uvicorn 04-Infraestrutura.api.main:app --reload" -ForegroundColor White
Write-Host "  4. Acessar documentação: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

