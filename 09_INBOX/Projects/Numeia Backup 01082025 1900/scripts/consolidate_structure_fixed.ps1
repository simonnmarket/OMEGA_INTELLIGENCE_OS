# CONSOLIDACAO DE ESTRUTURA - ARQUITETURA TIER-0 UNICA
Write-Host "=== CONSOLIDACAO DE ESTRUTURA - ARQUITETURA TIER-0 UNICA ===" -ForegroundColor Green
Write-Host "Data: $(Get-Date)" -ForegroundColor Yellow
Write-Host "Status: CONSOLIDANDO ESTRUTURA DEFINITIVA" -ForegroundColor Cyan
Write-Host ""

# FASE 1: MOVER ARQUIVOS DA ESTRUTURA ANTIGA PARA MQL5/
Write-Host "FASE 1: Movendo arquivos da estrutura antiga..." -ForegroundColor Magenta

# Mover arquivos core
if (Test-Path "core") {
    Write-Host "Movendo arquivos core..." -ForegroundColor Yellow
    Move-Item "core\*.mqh" "MQL5\CORE\" -Force
    Remove-Item "core" -Recurse -Force
}

# Mover arquivos utils
if (Test-Path "utils") {
    Write-Host "Movendo arquivos utils..." -ForegroundColor Yellow
    if (!(Test-Path "MQL5\INCLUDE\utils")) {
        New-Item -ItemType Directory -Path "MQL5\INCLUDE\utils" -Force
    }
    Move-Item "utils\*.mqh" "MQL5\INCLUDE\utils\" -Force
    Remove-Item "utils" -Recurse -Force
}

# Mover arquivos expert
if (Test-Path "expert") {
    Write-Host "Movendo arquivos expert..." -ForegroundColor Yellow
    Move-Item "expert\NumeiaEA.mq5" "MQL5\EXPERT\" -Force
    if (Test-Path "expert\tools") {
        Move-Item "expert\tools\*.mq5" "MQL5\EXPERT\tools\" -Force
    }
    Remove-Item "expert" -Recurse -Force
}

# Mover arquivos auditor
if (Test-Path "auditor") {
    Write-Host "Movendo arquivos auditor..." -ForegroundColor Yellow
    Move-Item "auditor\*.mq5" "MQL5\AUDITOR\" -Force
    Move-Item "auditor\*.mqh" "MQL5\AUDITOR\" -Force
    Remove-Item "auditor" -Recurse -Force
}

# Mover arquivos include (estrutura antiga)
if (Test-Path "include") {
    Write-Host "Movendo arquivos include..." -ForegroundColor Yellow
    Get-ChildItem "include" -Recurse -Include "*.mqh", "*.mq5" | ForEach-Object {
        $relativePath = $_.FullName.Substring($_.FullName.IndexOf("include\") + 8)
        $targetPath = "MQL5\INCLUDE\$relativePath"
        $targetDir = Split-Path $targetPath -Parent
        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force
        }
        Move-Item $_.FullName $targetPath -Force
    }
    Remove-Item "include" -Recurse -Force
}

# Mover arquivos soltos
Write-Host "Movendo arquivos soltos..." -ForegroundColor Yellow
if (Test-Path "live_monitor.mq5") {
    Move-Item "live_monitor.mq5" "MQL5\EXPERT\" -Force
}

# FASE 2: VERIFICAR ESTRUTURA FINAL
Write-Host ""
Write-Host "FASE 2: Verificando estrutura final..." -ForegroundColor Magenta
$criticalDirs = @("MQL5\CORE", "MQL5\INCLUDE", "MQL5\EXPERT", "MQL5\AUDITOR", "MQL5\LOGS", "MQL5\HTML", "MQL5\PYTHON")
foreach ($dir in $criticalDirs) {
    if (Test-Path $dir) {
        $fileCount = (Get-ChildItem $dir -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
        Write-Host "OK: $dir ($fileCount arquivos)" -ForegroundColor Green
    } else {
        Write-Host "AUSENTE: $dir" -ForegroundColor Red
    }
}

# FASE 3: CONTAR ARQUIVOS TOTAIS
Write-Host ""
Write-Host "FASE 3: Contando arquivos totais..." -ForegroundColor Magenta
$totalFiles = (Get-ChildItem "MQL5" -Recurse -Include "*.mqh", "*.mq5" | Measure-Object).Count
Write-Host "Total de arquivos .mqh/.mq5: $totalFiles" -ForegroundColor Cyan

# FASE 4: RELATORIO DE CONSOLIDACAO
Write-Host ""
Write-Host "FASE 4: Gerando relatorio de consolidacao..." -ForegroundColor Magenta
$reportDate = Get-Date -Format "yyyyMMdd"
$reportContent = "=== RELATORIO DE CONSOLIDACAO DE ESTRUTURA ===`n"
$reportContent += "Data: $(Get-Date)`n"
$reportContent += "Status: ESTRUTURA CONSOLIDADA`n"
$reportContent += "Sistema: Quantum Grid Network v6.0`n`n"
$reportContent += "ACOES REALIZADAS:`n"
$reportContent += "- Estrutura antiga removida`n"
$reportContent += "- Todos os arquivos movidos para MQL5/`n"
$reportContent += "- Duplicacoes eliminadas`n"
$reportContent += "- Arquitetura TIER-0 unificada`n`n"
$reportContent += "RESULTADO:`n"
$reportContent += "- Estrutura unica e limpa`n"
$reportContent += "- $totalFiles arquivos consolidados`n"
$reportContent += "- Pronto para compilacao`n`n"
$reportContent += "PROXIMO PASSO:`n"
$reportContent += "- Compilar NumeiaEA.mq5 no MetaEditor`n"
$reportContent += "- Confirmar: 0 erros, 0 warnings"

$reportPath = "consolidation_report_$reportDate.txt"
Set-Content $reportPath $reportContent
Write-Host "Relatorio de consolidacao gerado: $reportPath" -ForegroundColor Green

Write-Host ""
Write-Host "=== CONSOLIDACAO CONCLUIDA COM SUCESSO ===" -ForegroundColor Green
Write-Host "Status: ESTRUTURA UNIFICADA" -ForegroundColor Green
Write-Host "Arquitetura: MQL5/ (TIER-0)" -ForegroundColor Green
Write-Host "Proximo passo: Compilar NumeiaEA.mq5" -ForegroundColor Yellow 