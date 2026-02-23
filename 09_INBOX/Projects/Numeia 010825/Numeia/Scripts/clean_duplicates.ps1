# ELIMINACAO COMPLETA DE DUPLICACOES
Write-Host "=== ELIMINACAO COMPLETA DE DUPLICACOES ===" -ForegroundColor Red
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Status: REMOVENDO ESTRUTURA MQL5 DUPLICADA" -ForegroundColor Cyan
Write-Host ""

# FASE 1: VERIFICAR ESTRUTURA ATUAL
Write-Host "FASE 1: Verificando estrutura atual..." -ForegroundColor Magenta
Write-Host "Pastas encontradas:" -ForegroundColor Yellow
Get-ChildItem -Directory | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor White }

# FASE 2: ELIMINAR ESTRUTURA MQL5 DUPLICADA
Write-Host ""
Write-Host "FASE 2: Eliminando estrutura MQL5 duplicada..." -ForegroundColor Magenta

# Remover MQL5 completamente
if (Test-Path "MQL5") {
    Write-Host "Removendo pasta MQL5 completamente..." -ForegroundColor Red
    Remove-Item "MQL5" -Recurse -Force
    Write-Host "MQL5 removida com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Pasta MQL5 não encontrada." -ForegroundColor Yellow
}

# FASE 3: VERIFICAR ESTRUTURA FINAL
Write-Host ""
Write-Host "FASE 3: Verificando estrutura final..." -ForegroundColor Magenta
Write-Host "Pastas restantes:" -ForegroundColor Yellow
Get-ChildItem -Directory | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor White }

# FASE 4: CONTAR ARQUIVOS
Write-Host ""
Write-Host "FASE 4: Contando arquivos..." -ForegroundColor Magenta
$totalFiles = (Get-ChildItem -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
Write-Host "Total de arquivos .mqh/.mq5: $totalFiles" -ForegroundColor Cyan

# FASE 5: VERIFICAR PASTAS CRITICAS
Write-Host ""
Write-Host "FASE 5: Verificando pastas críticas..." -ForegroundColor Magenta
$criticalDirs = @("core", "utils", "expert", "auditor", "include")
foreach ($dir in $criticalDirs) {
    if (Test-Path $dir) {
        $fileCount = (Get-ChildItem $dir -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
        Write-Host "OK: $dir ($fileCount arquivos)" -ForegroundColor Green
    } else {
        Write-Host "AUSENTE: $dir" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== ELIMINACAO CONCLUIDA ===" -ForegroundColor Green
Write-Host "Status: DUPLICACOES REMOVIDAS" -ForegroundColor Green
Write-Host "Estrutura: APENAS ESTRUTURA ORIGINAL" -ForegroundColor Green