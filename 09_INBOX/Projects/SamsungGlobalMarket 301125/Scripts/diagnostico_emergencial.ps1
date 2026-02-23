# DIAGNOSTICO EMERGENCIAL - RESOLUCAO IMEDIATA

$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

Write-Host "===========================================================================" -ForegroundColor Red
Write-Host "DIAGNOSTICO EMERGENCIAL - PROBLEMA DETECTADO" -ForegroundColor Red
Write-Host "==========================================================================="
Write-Host ""

# 1. Verificar servidor
Write-Host "[1] VERIFICANDO SERVIDOR..." -ForegroundColor Yellow
$procs = Get-Process python -ErrorAction SilentlyContinue
if ($procs) {
    Write-Host "  Processo Python encontrado: PID $($procs.Id)" -ForegroundColor Green
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId = $($procs.Id)").CommandLine
    Write-Host "  Comando: $cmd" -ForegroundColor Gray
} else {
    Write-Host "  ERRO: Servidor nao esta rodando!" -ForegroundColor Red
}
Write-Host ""

# 2. Verificar arquivos
Write-Host "[2] VERIFICANDO ARQUIVOS..." -ForegroundColor Yellow
if (Test-Path $mt5Path) {
    $reqs = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
    $resps = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
    
    Write-Host "  Requests: $($reqs.Count)" -ForegroundColor Cyan
    Write-Host "  Responses: $($resps.Count)" -ForegroundColor Cyan
    
    if ($reqs) {
        Write-Host "  AVISO: Requests antigos encontrados!" -ForegroundColor Yellow
        foreach ($r in $reqs) {
            $age = ((Get-Date) - $r.LastWriteTime).TotalSeconds
            Write-Host "    $($r.Name) - $([math]::Round($age, 1))s atras" -ForegroundColor $(if ($age -gt 60) { "Red" } else { "Yellow" })
        }
    }
    
    if ($resps -and $resps.Count -gt 10) {
        Write-Host "  ERRO: Muitos responses acumulados ($($resps.Count))!" -ForegroundColor Red
        Write-Host "  Acao: Limpar responses antigos" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ERRO: Diretorio nao existe!" -ForegroundColor Red
}
Write-Host ""

# 3. Acao recomendada
Write-Host "[3] ACAO RECOMENDADA:" -ForegroundColor Yellow
Write-Host "  1. Parar servidor atual (se estiver errado)" -ForegroundColor Cyan
Write-Host "  2. Limpar responses antigos (>5 minutos)" -ForegroundColor Cyan
Write-Host "  3. Iniciar servidor file-based correto" -ForegroundColor Cyan
Write-Host ""

Write-Host "Deseja executar limpeza automatica? (S/N): " -NoNewline -ForegroundColor Yellow
$resposta = Read-Host

if ($resposta -eq "S" -or $resposta -eq "s") {
    Write-Host ""
    Write-Host "Limpando responses antigos (>5 minutos)..." -ForegroundColor Yellow
    
    if (Test-Path $mt5Path) {
        $resps = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
        $limpeza = 0
        foreach ($resp in $resps) {
            $age = ((Get-Date) - $resp.LastWriteTime).TotalMinutes
            if ($age -gt 5) {
                Remove-Item $resp.FullName -Force
                $limpeza++
            }
        }
        Write-Host "  $limpeza arquivo(s) removido(s)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Cyan

