# RESTAURACAO DE ESTRUTURA ANTERIOR
Write-Host "=== RESTAURACAO DE ESTRUTURA ANTERIOR ===" -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Status: RESTAURANDO ESTRUTURA ORIGINAL" -ForegroundColor Cyan
Write-Host ""

# FASE 1: RESTAURAR PASTAS PRINCIPAIS
Write-Host "FASE 1: Restaurando pastas principais..." -ForegroundColor Magenta

# Restaurar core/
Write-Host "Restaurando core/..." -ForegroundColor Yellow
if (!(Test-Path "core")) {
    New-Item -ItemType Directory -Path "core" -Force
}
Move-Item "MQL5\CORE\*.mqh" "core\" -Force

# Restaurar utils/
Write-Host "Restaurando utils/..." -ForegroundColor Yellow
if (!(Test-Path "utils")) {
    New-Item -ItemType Directory -Path "utils" -Force
}
Move-Item "MQL5\INCLUDE\utils\*.mqh" "utils\" -Force

# Restaurar expert/
Write-Host "Restaurando expert/..." -ForegroundColor Yellow
if (!(Test-Path "expert")) {
    New-Item -ItemType Directory -Path "expert" -Force
}
Move-Item "MQL5\EXPERT\NumeiaEA.mq5" "expert\" -Force
if (!(Test-Path "expert\tools")) {
    New-Item -ItemType Directory -Path "expert\tools" -Force
}
Move-Item "MQL5\EXPERT\tools\*.mq5" "expert\tools\" -Force

# Restaurar auditor/
Write-Host "Restaurando auditor/..." -ForegroundColor Yellow
if (!(Test-Path "auditor")) {
    New-Item -ItemType Directory -Path "auditor" -Force
}
Move-Item "MQL5\AUDITOR\*.mq5" "auditor\" -Force
Move-Item "MQL5\AUDITOR\*.mqh" "auditor\" -Force

# FASE 2: RESTAURAR ESTRUTURA INCLUDE COMPLETA
Write-Host "FASE 2: Restaurando estrutura include completa..." -ForegroundColor Magenta
if (!(Test-Path "include")) {
    New-Item -ItemType Directory -Path "include" -Force
}

# Mover todas as subpastas de MQL5\INCLUDE para include\
Get-ChildItem "MQL5\INCLUDE" -Directory | ForEach-Object {
    $sourcePath = $_.FullName
    $targetPath = "include\$($_.Name)"
    Write-Host "Movendo $($_.Name)..." -ForegroundColor Yellow
    Move-Item $sourcePath $targetPath -Force
}

# FASE 3: RESTAURAR ARQUIVOS SOLTOS
Write-Host "FASE 3: Restaurando arquivos soltos..." -ForegroundColor Magenta
if (Test-Path "MQL5\EXPERT\live_monitor.mq5") {
    Move-Item "MQL5\EXPERT\live_monitor.mq5" "." -Force
}

# FASE 4: VERIFICAR ESTRUTURA RESTAURADA
Write-Host ""
Write-Host "FASE 4: Verificando estrutura restaurada..." -ForegroundColor Magenta
$restoredDirs = @("core", "utils", "expert", "auditor", "include")
foreach ($dir in $restoredDirs) {
    if (Test-Path $dir) {
        $fileCount = (Get-ChildItem $dir -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
        Write-Host "OK: $dir ($fileCount arquivos)" -ForegroundColor Green
    } else {
        Write-Host "AUSENTE: $dir" -ForegroundColor Red
    }
}

# FASE 5: CONTAR ARQUIVOS TOTAIS
Write-Host ""
Write-Host "FASE 5: Contando arquivos totais..." -ForegroundColor Magenta
$totalFiles = (Get-ChildItem -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
Write-Host "Total de arquivos .mqh/.mq5: $totalFiles" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== RESTAURACAO CONCLUIDA ===" -ForegroundColor Green
Write-Host "Status: ESTRUTURA ANTERIOR RESTAURADA" -ForegroundColor Green
Write-Host "Arquitetura: ESTRUTURA ORIGINAL" -ForegroundColor Green