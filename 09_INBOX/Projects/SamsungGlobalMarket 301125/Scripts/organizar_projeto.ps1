# SCRIPT DE ORGANIZAÇÃO COMPLETA DO PROJETO
# Projeto Prometheus v3.0.0 | Samsung Global Market
# Organiza todos os arquivos da raiz em pastas por função

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "ORGANIZACAO COMPLETA DO PROJETO" -ForegroundColor Yellow
Write-Host "Projeto Prometheus v3.0.0 | Samsung Global Market" -ForegroundColor White
Write-Host "==========================================================================="
Write-Host ""

$projectRoot = $PSScriptRoot + "\.."
Set-Location $projectRoot

# Criar estrutura de pastas
Write-Host "[1/6] Criando estrutura de pastas..." -ForegroundColor Cyan

$pastas = @(
    "Documentation",
    "Tests",
    "Analysis",
    "Core",
    "Output",
    "Backups"
)

foreach ($pasta in $pastas) {
    if (-not (Test-Path $pasta)) {
        New-Item -ItemType Directory -Path $pasta -Force | Out-Null
        Write-Host "  [OK] Pasta criada: $pasta" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] Pasta ja existe: $pasta" -ForegroundColor Yellow
    }
}

Write-Host ""

# Mover arquivos Python de teste
Write-Host "[2/6] Organizando arquivos Python de teste..." -ForegroundColor Cyan

$testFiles = @(
    "test_direct_connection.py",
    "test_server_connection.py",
    "test_heartbeat_fix.py",
    "test_ea_server_connection.py",
    "test_server_quantitative.py",
    "test_watchdog.py",
    "run_mt5_integration_test.py",
    "stress_test_engine.py",
    "stress_test_final.py",
    "stress_test_mt5_server.py"
)

$testFilesMoved = 0
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Move-Item $file "Tests\" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Movido: $file -> Tests\" -ForegroundColor Green
        $testFilesMoved++
    }
}
Write-Host "  [INFO] $testFilesMoved arquivo(s) de teste movidos" -ForegroundColor Cyan

Write-Host ""

# Mover arquivos Python principais/core
Write-Host "[3/6] Organizando arquivos Python principais..." -ForegroundColor Cyan

$coreFiles = @{
    "analytics_engine.py" = "Core"
    "backtesting_engine.py" = "Core"
    "continuous_monitor.py" = "Core"
    "data_fetcher.py" = "Core"
    "futures_calendar_spreads.py" = "Core"
    "strategy_activation_protocol.py" = "Core"
    "NumeiaTradingSystem_v3_0_FINAL.py" = "Core"
    "NumeiaTradingSystem_v3_0_FINAL_backup.py" = "Backups"
    "run_backtests.py" = "Core"
    "run_parallel_backtests.py" = "Core"
    "server_watchdog.py" = "Core"
    "simple_mt5_server.py" = "Core"
    "start_mt5_server.py" = "Core"
    "start_mt5_server_continuous.py" = "Core"
    "MT5_Connector.py" = "Core"
    "debug_connection.py" = "Tests"
    "debug_server.py" = "Tests"
}

$coreFilesMoved = 0
foreach ($file in $coreFiles.Keys) {
    if (Test-Path $file) {
        $destino = $coreFiles[$file]
        Move-Item $file "$destino\" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Movido: $file -> $destino\" -ForegroundColor Green
        $coreFilesMoved++
    }
}
Write-Host "  [INFO] $coreFilesMoved arquivo(s) principais movidos" -ForegroundColor Cyan

Write-Host ""

# Mover documentos/relatórios
Write-Host "[4/6] Organizando documentos e relatórios..." -ForegroundColor Cyan

$docFiles = @(
    "*.md",
    "*.txt"
)

$docsMoved = 0
Get-ChildItem -Filter *.md | Where-Object { $_.Directory.Name -eq (Split-Path $projectRoot -Leaf) } | ForEach-Object {
    Move-Item $_.FullName "Documentation\" -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Movido: $($_.Name) -> Documentation\" -ForegroundColor Green
    $docsMoved++
}

Get-ChildItem -Filter *.txt | Where-Object { $_.Directory.Name -eq (Split-Path $projectRoot -Leaf) } | ForEach-Object {
    # Arquivos de output vão para Output/
    if ($_.Name -like "*result*" -or $_.Name -like "*analysis*" -or $_.Name -like "*portfolio*" -or $_.Name -like "*backtest*") {
        Move-Item $_.FullName "Output\" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Movido: $($_.Name) -> Output\" -ForegroundColor Green
    } else {
        Move-Item $_.FullName "Documentation\" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Movido: $($_.Name) -> Documentation\" -ForegroundColor Green
    }
    $docsMoved++
}

Write-Host "  [INFO] $docsMoved arquivo(s) de documentacao movidos" -ForegroundColor Cyan

Write-Host ""

# Organizar arquivos de output
Write-Host "[5/6] Organizando arquivos de output..." -ForegroundColor Cyan

$outputFiles = @(
    "backtest_results_*.txt",
    "portfolio_analysis_*.txt"
)

$outputMoved = 0
Get-ChildItem -Filter "backtest_results_*.txt" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "Output\" -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Movido: $($_.Name) -> Output\" -ForegroundColor Green
    $outputMoved++
}

Get-ChildItem -Filter "portfolio_analysis_*.txt" -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName "Output\" -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Movido: $($_.Name) -> Output\" -ForegroundColor Green
    $outputMoved++
}

Write-Host "  [INFO] $outputMoved arquivo(s) de output movidos" -ForegroundColor Cyan

Write-Host ""

# Verificar estrutura final
Write-Host "[6/6] Verificando estrutura final..." -ForegroundColor Cyan

$arquivosRaiz = Get-ChildItem -File | Where-Object { 
    $_.Name -ne "README.md" -and 
    $_.Name -notlike ".*" -and
    $_.Extension -in @(".py", ".md", ".txt", ".mq5", ".mqh")
}

if ($arquivosRaiz.Count -gt 0) {
    Write-Host "  [AVISO] Ainda existem $($arquivosRaiz.Count) arquivo(s) na raiz:" -ForegroundColor Yellow
    $arquivosRaiz | ForEach-Object {
        Write-Host "    - $($_.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [OK] Raiz limpa! Todos os arquivos organizados" -ForegroundColor Green
}

Write-Host ""

# Resumo final
Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "ESTRUTURA FINAL" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""

$estrutura = @{
    "Experts" = "Expert Advisor (EA MQL5)"
    "Server" = "Servidor Python (microserviços)"
    "Scripts" = "Scripts PowerShell (automação)"
    "Core" = "Módulos Python principais"
    "Tests" = "Arquivos de teste e validação"
    "Documentation" = "Documentação e relatórios"
    "Output" = "Resultados de backtests e análises"
    "Backups" = "Backups de arquivos importantes"
}

foreach ($pasta in $estrutura.Keys) {
    if (Test-Path $pasta) {
        $arquivos = (Get-ChildItem $pasta -File -Recurse -ErrorAction SilentlyContinue).Count
        Write-Host "$pasta/" -ForegroundColor Cyan
        Write-Host "  Funcao: $($estrutura[$pasta])" -ForegroundColor White
        Write-Host "  Arquivos: $arquivos" -ForegroundColor Gray
        Write-Host ""
    }
}

Write-Host "===========================================================================" -ForegroundColor Green
Write-Host "ORGANIZACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

