# CORREÇÃO DE INCLUDES - PROTOCOLO TIER-0
Write-Host "=== CORREÇÃO DE INCLUDES ===" -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Status: CORRIGINDO CAMINHOS DE INCLUDE" -ForegroundColor Cyan
Write-Host ""

# FASE 1: CORREÇÕES NECESSÁRIAS
Write-Host "FASE 1: Identificando correções necessárias..." -ForegroundColor Magenta

$corrections = @{
    # Arquivo -> Linha -> Correção
    "utils/logger_institutional.mqh" = @{
        "14" = '#include <timestamp_formatter.mqh>'
        "15" = '#include <risk_profile.mqh>'
        "16" = '#include <market_regime_detector.mqh>'
        "17" = '#include <anomaly_detector_ai.mqh>'
        "18" = '#include <log_panel.mqh>'
    }
}

# FASE 2: APLICAR CORREÇÕES
Write-Host ""
Write-Host "FASE 2: Aplicando correções..." -ForegroundColor Magenta

foreach ($file in $corrections.Keys) {
    if (Test-Path $file) {
        Write-Host "Corrigindo: $file" -ForegroundColor Yellow
        
        $content = Get-Content $file -Raw
        $lines = $content -split "`n"
        
        foreach ($lineNum in $corrections[$file].Keys) {
            $lineIndex = [int]$lineNum - 1
            if ($lineIndex -lt $lines.Length) {
                $oldLine = $lines[$lineIndex]
                $newLine = $corrections[$file][$lineNum]
                $lines[$lineIndex] = $newLine
                Write-Host "  Linha $lineNum: $oldLine -> $newLine" -ForegroundColor Cyan
            }
        }
        
        $newContent = $lines -join "`n"
        Set-Content $file $newContent -NoNewline
        Write-Host "✅ Corrigido: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Arquivo não encontrado: $file" -ForegroundColor Red
    }
}

# FASE 3: VERIFICAR OUTROS ARQUIVOS COM PROBLEMAS SIMILARES
Write-Host ""
Write-Host "FASE 3: Verificando outros arquivos..." -ForegroundColor Magenta

$mqhFiles = Get-ChildItem -Recurse -Include "*.mqh", "*.mq5" | Where-Object { $_.Name -ne "logger_institutional.mqh" }

$problemPatterns = @(
    '#include <utils/',
    '#include <risk/',
    '#include <analysis/',
    '#include <intelligence/',
    '#include <visuals/'
)

foreach ($file in $mqhFiles) {
    $content = Get-Content $file.FullName -Raw
    $hasProblems = $false
    
    foreach ($pattern in $problemPatterns) {
        if ($content -match [regex]::Escape($pattern)) {
            if (!$hasProblems) {
                Write-Host "⚠️ Possíveis problemas em: $($file.Name)" -ForegroundColor Yellow
                $hasProblems = $true
            }
            Write-Host "  Encontrado: $pattern" -ForegroundColor Red
        }
    }
}

# FASE 4: RELATÓRIO FINAL
Write-Host ""
Write-Host "FASE 4: Gerando relatório..." -ForegroundColor Magenta

$reportContent = @"
=== CORREÇÃO DE INCLUDES - RELATÓRIO ===
Data: $(Get-Date)
Status: INCLUDES CORRIGIDOS

=== CORREÇÕES APLICADAS ===
"@

foreach ($file in $corrections.Keys) {
    if (Test-Path $file) {
        $reportContent += "`n✅ $file"
        foreach ($lineNum in $corrections[$file].Keys) {
            $reportContent += "`n  Linha $lineNum`: $($corrections[$file][$lineNum])"
        }
    } else {
        $reportContent += "`n❌ $file (não encontrado)"
    }
}

$reportContent += @"

=== PRÓXIMO PASSO ===
1. Compilar logger_institutional.mqh
2. Verificar: 0 erros de include
3. Compilar NumeiaEA.mq5
4. Verificar: 0 erros, 0 warnings
"@

$reportPath = "include_correction_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Set-Content $reportPath $reportContent

Write-Host ""
Write-Host "=== CORREÇÃO CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Relatório salvo: $reportPath" -ForegroundColor Green
Write-Host "Próximo passo: Compilar no MetaEditor" -ForegroundColor Yellow