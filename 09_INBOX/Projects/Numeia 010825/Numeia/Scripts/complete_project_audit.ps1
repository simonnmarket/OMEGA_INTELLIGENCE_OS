# AUDITORIA COMPLETA DO PROJETO - PROTOCOLO TIER-0
Write-Host "=== AUDITORIA COMPLETA DO PROJETO NUMEIA ===" -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Protocolo: TIER-0 COMPLETE SCAN" -ForegroundColor Cyan
Write-Host ""

# FASE 1: SCAN COMPLETO DE ARQUIVOS
Write-Host "FASE 1: Scan completo de arquivos..." -ForegroundColor Magenta
$allFiles = Get-ChildItem -Recurse -Include "*.mqh", "*.mq5"
$totalFiles = $allFiles.Count
Write-Host "Total de arquivos encontrados: $totalFiles" -ForegroundColor Cyan

# FASE 2: ANÁLISE POR DIRETÓRIO
Write-Host ""
Write-Host "FASE 2: Análise por diretório..." -ForegroundColor Magenta
$directoryAnalysis = $allFiles | Group-Object Directory | Sort-Object Name

foreach ($dir in $directoryAnalysis) {
    $dirName = Split-Path $dir.Name -Leaf
    Write-Host "  $dirName`: $($dir.Count) arquivos" -ForegroundColor White
}

# FASE 3: VERIFICAÇÃO DE DEPENDÊNCIAS
Write-Host ""
Write-Host "FASE 3: Verificação de dependências..." -ForegroundColor Magenta
$includePattern = '#include\s+<([^>]+)>'
$dependencies = @{}

foreach ($file in $allFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $matches = [regex]::Matches($content, $includePattern)
            foreach ($match in $matches) {
                $includePath = $match.Groups[1].Value
                if (!$dependencies.ContainsKey($includePath)) {
                    $dependencies[$includePath] = @()
                }
                $dependencies[$includePath] += $file.Name
            }
        }
    } catch {
        Write-Host "Erro ao ler: $($file.Name)" -ForegroundColor Red
    }
}

# FASE 4: VERIFICAÇÃO DE ARQUIVOS FALTANTES
Write-Host ""
Write-Host "FASE 4: Verificação de arquivos faltantes..." -ForegroundColor Magenta
$missingFiles = @()
$existingFiles = $allFiles | ForEach-Object { $_.Name }

foreach ($dependency in $dependencies.Keys) {
    $dependencyFile = $dependency -replace '/', '\'
    $found = $false
    
    foreach ($file in $allFiles) {
        if ($file.FullName -like "*\$dependencyFile*") {
            $found = $true
            break
        }
    }
    
    if (!$found) {
        $missingFiles += $dependency
    }
}

# FASE 5: RELATÓRIO COMPLETO
Write-Host ""
Write-Host "FASE 5: Gerando relatório completo..." -ForegroundColor Magenta

$systemStatus = if ($missingFiles.Count -eq 0) { "OPERACIONAL" } else { "COM PROBLEMAS" }
$readyToCompile = if ($missingFiles.Count -eq 0) { "SIM" } else { "NÃO" }

$reportContent = @"
=== AUDITORIA COMPLETA DO PROJETO NUMEIA ===
Data: $(Get-Date)
Protocolo: TIER-0 COMPLETE SCAN
Status: VERIFICAÇÃO SISTEMÁTICA

=== RESUMO EXECUTIVO ===
- Total de arquivos: $totalFiles
- Diretórios analisados: $($directoryAnalysis.Count)
- Dependências encontradas: $($dependencies.Count)
- Arquivos faltantes: $($missingFiles.Count)

=== ANÁLISE POR DIRETÓRIO ===
"@

foreach ($dir in $directoryAnalysis) {
    $dirName = Split-Path $dir.Name -Leaf
    $reportContent += "`n$dirName`: $($dir.Count) arquivos"
}

$reportContent += @"

=== DEPENDÊNCIAS ENCONTRADAS ===
"@

foreach ($dep in $dependencies.Keys | Sort-Object) {
    $reportContent += "`n$dep`n  Usado por: $($dependencies[$dep] -join ', ')"
}

if ($missingFiles.Count -gt 0) {
    $reportContent += @"

=== ARQUIVOS FALTANTES ===
"@
    foreach ($missing in $missingFiles) {
        $reportContent += "`n❌ $missing"
    }
} else {
    $reportContent += @"

=== ARQUIVOS FALTANTES ===
✅ NENHUM ARQUIVO FALTANTE DETECTADO
"@
}

$reportContent += @"

=== STATUS FINAL ===
- Sistema: $systemStatus
- Pronto para compilação: $readyToCompile
- Próximo passo: Compilar NumeiaEA.mq5
"@

# Salvar relatório
$reportPath = "complete_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Set-Content $reportPath $reportContent

Write-Host ""
Write-Host "=== AUDITORIA CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Relatório salvo: $reportPath" -ForegroundColor Green
Write-Host "Arquivos faltantes: $($missingFiles.Count)" -ForegroundColor $(if ($missingFiles.Count -eq 0) { 'Green' } else { 'Red' })
Write-Host "Status: $systemStatus" -ForegroundColor $(if ($missingFiles.Count -eq 0) { 'Green' } else { 'Red' })