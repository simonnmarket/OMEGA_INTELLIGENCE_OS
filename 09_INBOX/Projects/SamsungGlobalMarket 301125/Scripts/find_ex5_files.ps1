# SCRIPT DE IDENTIFICAÇÃO DE ARQUIVOS .EX5
# Projeto Prometheus v3.0.0 | Samsung Global Market
# Protocolo: Omega TIER-0
#
# Objetivo: Identificar qual arquivo .ex5 o MT5 está usando

Write-Host "=" * 80
Write-Host "IDENTIFICAÇÃO DE ARQUIVOS .EX5"
Write-Host "Projeto Prometheus v3.0.0 | Samsung Global Market"
Write-Host "=" * 80
Write-Host ""

# Caminho base do MT5
$MT5Path = "$env:APPDATA\MetaQuotes"

Write-Host "Procurando arquivos SamsungGlobalMarket_EA.ex5..."
Write-Host "Caminho base: $MT5Path"
Write-Host ""

# Encontrar todos os arquivos .ex5
$files = Get-ChildItem -Path $MT5Path -Recurse -Filter "SamsungGlobalMarket_EA.ex5" -ErrorAction SilentlyContinue

if ($files.Count -eq 0) {
    Write-Host "✗ NENHUM ARQUIVO .EX5 ENCONTRADO!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ações necessárias:"
    Write-Host "  1. Abrir MetaEditor"
    Write-Host "  2. Abrir arquivo .mq5"
    Write-Host "  3. Compilar (F7)"
    Write-Host ""
    exit 1
}

Write-Host "Encontrados $($files.Count) arquivo(s):" -ForegroundColor Green
Write-Host ""

# Listar todos os arquivos
$fileList = @()
foreach ($file in $files) {
    $info = @{
        Path = $file.FullName
        Size = $file.Length
        LastWriteTime = $file.LastWriteTime
        Age = (Get-Date) - $file.LastWriteTime
    }
    $fileList += New-Object PSObject -Property $info
}

# Ordenar por data (mais recente primeiro)
$fileList = $fileList | Sort-Object -Property LastWriteTime -Descending

# Exibir tabela
$i = 1
foreach ($file in $fileList) {
    $ageMinutes = [math]::Round($file.Age.TotalMinutes, 1)
    $ageHours = [math]::Round($file.Age.TotalHours, 1)
    $ageDays = [math]::Round($file.Age.TotalDays, 1)
    
    if ($i -eq 1) {
        Write-Host "[$i] MAIS RECENTE:" -ForegroundColor Cyan
    } else {
        Write-Host "[$i] Arquivo antigo:" -ForegroundColor Yellow
    }
    
    Write-Host "    Caminho: $($file.Path)"
    Write-Host "    Tamanho: $($file.Size) bytes"
    Write-Host "    Data:    $($file.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    
    if ($ageMinutes -lt 60) {
        Write-Host "    Idade:   $ageMinutes minutos" -ForegroundColor Green
    } elseif ($ageHours -lt 24) {
        Write-Host "    Idade:   $ageHours horas" -ForegroundColor Yellow
    } else {
        Write-Host "    Idade:   $ageDays dias" -ForegroundColor Red
    }
    
    Write-Host ""
    $i++
}

# Análise
Write-Host "=" * 80
Write-Host "ANÁLISE"
Write-Host "=" * 80
Write-Host ""

$mostRecent = $fileList[0]
$expectedPath = "$MT5Path\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.ex5"

Write-Host "Arquivo mais recente:"
Write-Host "  $($mostRecent.Path)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Caminho esperado:"
Write-Host "  $expectedPath"
Write-Host ""

if ($mostRecent.Path -eq $expectedPath) {
    Write-Host "✓ Arquivo mais recente está no caminho esperado" -ForegroundColor Green
} else {
    Write-Host "✗ Arquivo mais recente NÃO está no caminho esperado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ações necessárias:"
    Write-Host "  1. Deletar TODOS os arquivos .ex5 listados acima"
    Write-Host "  2. Recompilar EA no MetaEditor"
    Write-Host "  3. Verificar que arquivo foi gerado no caminho esperado"
}

Write-Host ""

# Verificar arquivo .mq5
$mq5Path = "$MT5Path\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5"

if (Test-Path $mq5Path) {
    $mq5File = Get-Item $mq5Path
    $mq5Age = (Get-Date) - $mq5File.LastWriteTime
    
    Write-Host "Arquivo fonte (.mq5):"
    Write-Host "  Caminho: $mq5Path"
    Write-Host "  Data:    $($mq5File.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host "  Idade:   $([math]::Round($mq5Age.TotalMinutes, 1)) minutos"
    Write-Host ""
    
    # Comparar datas
    $timeDiff = $mostRecent.LastWriteTime - $mq5File.LastWriteTime
    
    if ($timeDiff.TotalSeconds -gt 0) {
        Write-Host "✓ Arquivo .ex5 é mais recente que .mq5 (compilado após última edição)" -ForegroundColor Green
    } else {
        Write-Host "✗ Arquivo .mq5 é mais recente que .ex5 (código não foi recompilado!)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Ações necessárias:"
        Write-Host "  1. Abrir MetaEditor"
        Write-Host "  2. Abrir $mq5Path"
        Write-Host "  3. Compilar (F7)"
    }
} else {
    Write-Host "✗ Arquivo fonte .mq5 NÃO ENCONTRADO em:" -ForegroundColor Red
    Write-Host "  $mq5Path"
}

Write-Host ""
Write-Host ("=" * 80)

# Comando para deletar todos os arquivos
Write-Host ""
Write-Host "Para deletar TODOS os arquivos .ex5 encontrados, execute:"
Write-Host ""
Write-Host "Get-ChildItem -Path '$MT5Path' -Recurse -Filter 'SamsungGlobalMarket_EA.ex5' -ErrorAction SilentlyContinue | Remove-Item -Force" -ForegroundColor Yellow
Write-Host ""
