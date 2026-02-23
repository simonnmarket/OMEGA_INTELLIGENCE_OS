# CORREÇÃO GLOBAL DE INCLUDES - ASPAS DUPLAS
Write-Host "=== CORREÇÃO GLOBAL DE INCLUDES ===" -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Status: SUBSTITUINDO TODOS OS INCLUDES" -ForegroundColor Cyan
Write-Host ""

# FASE 1: ENCONTRAR TODOS OS ARQUIVOS MQH E MQ5
Write-Host "FASE 1: Encontrando todos os arquivos..." -ForegroundColor Magenta

$mqhFiles = Get-ChildItem -Recurse -Include "*.mqh", "*.mq5"
Write-Host "Arquivos encontrados: $($mqhFiles.Count)" -ForegroundColor Cyan

# FASE 2: CORRIGIR INCLUDES EM CADA ARQUIVO
Write-Host ""
Write-Host "FASE 2: Corrigindo includes..." -ForegroundColor Magenta

$totalCorrections = 0

foreach ($file in $mqhFiles) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    $fileCorrections = 0
    
    # Substituir includes com <>
    $content = $content -replace '#include\s*<([^>]+)>', '#include "$1"'
    
    # Contar correções
    $corrections = ([regex]::Matches($originalContent, '#include\s*<[^>]+>')).Count
    $totalCorrections += $corrections
    
    if ($corrections -gt 0) {
        Write-Host "Corrigindo: $($file.Name) - $corrections includes" -ForegroundColor Yellow
        Set-Content $file.FullName $content -NoNewline
        $fileCorrections += $corrections
    }
}

# FASE 3: RELATÓRIO FINAL
Write-Host ""
Write-Host "FASE 3: Gerando relatório..." -ForegroundColor Magenta

$reportContent = @"
=== CORREÇÃO GLOBAL DE INCLUDES - RELATÓRIO ===
Data: $(Get-Date)
Status: TODOS OS INCLUDES CORRIGIDOS

=== ESTATÍSTICAS ===
Total de arquivos processados: $($mqhFiles.Count)
Total de correções aplicadas: $totalCorrections

=== PADRÃO APLICADO ===
ANTES: #include <arquivo.mqh>
DEPOIS: #include "arquivo.mqh"

=== PRÓXIMO PASSO ===
1. Copiar arquivos para MetaTrader
2. Compilar NumeiaEA.mq5
3. Verificar: 0 erros de include
"@

$reportPath = "includes_quotes_correction_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Set-Content $reportPath $reportContent

Write-Host ""
Write-Host "=== CORREÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Total de correções: $totalCorrections" -ForegroundColor Green
Write-Host "Relatório salvo: $reportPath" -ForegroundColor Green
Write-Host "Próximo passo: Copiar para MetaTrader e compilar" -ForegroundColor Yellow