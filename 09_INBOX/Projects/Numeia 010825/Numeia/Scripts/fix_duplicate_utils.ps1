# CORREÇÃO DE DUPLICAÇÃO UTILS - PROTOCOLO TIER-0
Write-Host "=== CORREÇÃO DE DUPLICAÇÃO UTILS ===" -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Status: REMOVENDO PASTA VAZIA" -ForegroundColor Cyan
Write-Host ""

# FASE 1: VERIFICAR SITUAÇÃO
Write-Host "FASE 1: Verificando situação atual..." -ForegroundColor Magenta

$rootUtils = "utils"
$includeUtils = "include/utils"

Write-Host "Verificando: $rootUtils" -ForegroundColor Cyan
if (Test-Path $rootUtils) {
    $rootFiles = Get-ChildItem $rootUtils -Include "*.mqh", "*.mq5" | Measure-Object
    Write-Host "✅ $rootUtils: $($rootFiles.Count) arquivos" -ForegroundColor Green
} else {
    Write-Host "❌ $rootUtils: não encontrada" -ForegroundColor Red
}

Write-Host "Verificando: $includeUtils" -ForegroundColor Cyan
if (Test-Path $includeUtils) {
    $includeFiles = Get-ChildItem $includeUtils -Include "*.mqh", "*.mq5" | Measure-Object
    Write-Host "⚠️ $includeUtils: $($includeFiles.Count) arquivos" -ForegroundColor Yellow
    
    if ($includeFiles.Count -eq 0) {
        Write-Host "  -> PASTA VAZIA - SERÁ REMOVIDA" -ForegroundColor Red
    }
} else {
    Write-Host "❌ $includeUtils: não encontrada" -ForegroundColor Red
}

# FASE 2: REMOVER PASTA VAZIA
Write-Host ""
Write-Host "FASE 2: Removendo pasta vazia..." -ForegroundColor Magenta

if (Test-Path $includeUtils) {
    $files = Get-ChildItem $includeUtils -Recurse
    if ($files.Count -eq 0) {
        Write-Host "Removendo pasta vazia: $includeUtils" -ForegroundColor Yellow
        Remove-Item $includeUtils -Recurse -Force
        Write-Host "✅ Pasta removida: $includeUtils" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Pasta não está vazia, verificando conteúdo..." -ForegroundColor Yellow
        foreach ($file in $files) {
            Write-Host "  Encontrado: $($file.Name)" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "✅ Pasta já não existe: $includeUtils" -ForegroundColor Green
}

# FASE 3: VERIFICAR OUTRAS DUPLICAÇÕES
Write-Host ""
Write-Host "FASE 3: Verificando outras duplicações..." -ForegroundColor Magenta

$possibleDuplicates = @(
    "core",
    "auditor", 
    "expert"
)

foreach ($dir in $possibleDuplicates) {
    $rootDir = $dir
    $includeDir = "include/$dir"
    
    if (Test-Path $rootDir) {
        $rootCount = (Get-ChildItem $rootDir -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
        Write-Host "$rootDir (raiz): $rootCount arquivos" -ForegroundColor Cyan
    }
    
    if (Test-Path $includeDir) {
        $includeCount = (Get-ChildItem $includeDir -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
        Write-Host "$includeDir: $includeCount arquivos" -ForegroundColor Cyan
        
        if ($includeCount -eq 0) {
            Write-Host "⚠️ $includeDir está vazia!" -ForegroundColor Yellow
        }
    }
}

# FASE 4: RELATÓRIO FINAL
Write-Host ""
Write-Host "FASE 4: Gerando relatório..." -ForegroundColor Magenta

$reportContent = @"
=== CORREÇÃO DE DUPLICAÇÃO UTILS - RELATÓRIO ===
Data: $(Get-Date)
Status: DUPLICAÇÃO CORRIGIDA

=== SITUAÇÃO ANTERIOR ===
- utils/ (raiz): 4 arquivos importantes
- include/utils/: pasta vazia (REMOVIDA)

=== SITUAÇÃO ATUAL ===
- utils/ (raiz): mantida com todos os arquivos
- include/utils/: removida (não existe mais)

=== ARQUIVOS EM utils/ (raiz) ===
"@

if (Test-Path $rootUtils) {
    $files = Get-ChildItem $rootUtils -Include "*.mqh", "*.mq5"
    foreach ($file in $files) {
        $reportContent += "`n✅ $($file.Name)"
    }
}

$reportContent += @"

=== PRÓXIMO PASSO ===
1. Corrigir includes para usar utils/ (raiz)
2. Compilar logger_institutional.mqh
3. Verificar: 0 erros de include
"@

$reportPath = "duplicate_utils_fix_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Set-Content $reportPath $reportContent

Write-Host ""
Write-Host "=== CORREÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Relatório salvo: $reportPath" -ForegroundColor Green
Write-Host "Pasta vazia removida: $includeUtils" -ForegroundColor Green