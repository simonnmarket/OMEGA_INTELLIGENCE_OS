# Monitoramento em tempo real do sistema
param(
    [int]$IntervalSeconds = 2
)

$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

Clear-Host
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "MONITORAMENTO EM TEMPO REAL - SAMSUNG GLOBAL MARKET" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host "Intervalo: $IntervalSeconds segundos | Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] ==========================================================" -ForegroundColor Cyan
    
    # Servidor
    $proc = Get-Process python -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "  [SERVIDOR] RODANDO (PID: $($proc.Id))" -ForegroundColor Green
    } else {
        Write-Host "  [SERVIDOR] PARADO!" -ForegroundColor Red
    }
    
    # Arquivos
    if (Test-Path $mt5Path) {
        $reqs = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
        $resps = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
        
        Write-Host "  [REQUESTS] $($reqs.Count)" -ForegroundColor Cyan
        if ($reqs) {
            foreach ($r in $reqs) {
                $age = [math]::Round(((Get-Date) - $r.LastWriteTime).TotalSeconds, 1)
                $status = if ($age -lt 10) { "OK" } elseif ($age -lt 30) { "MEDIO" } else { "ANTIGO!" }
                $color = if ($age -lt 10) { "Green" } elseif ($age -lt 30) { "Yellow" } else { "Red" }
                Write-Host "    $status - $($r.Name) ($age s)" -ForegroundColor $color
            }
        }
        
        Write-Host "  [RESPONSES] $($resps.Count)" -ForegroundColor Cyan
        if ($resps) {
            foreach ($r in $resps) {
                $age = [math]::Round(((Get-Date) - $r.LastWriteTime).TotalSeconds, 1)
                Write-Host "    $($r.Name) ($age s)" -ForegroundColor Green
                
                # Tentar ler conteudo
                try {
                    $content = Get-Content $r.FullName -Raw | ConvertFrom-Json
                    Write-Host "      Action: $($content.action) | Confidence: $($content.confidence)" -ForegroundColor Gray
                } catch {
                    Write-Host "      (JSON nao pode ser lido)" -ForegroundColor Yellow
                }
            }
        }
    }
    
    Write-Host ""
    Start-Sleep -Seconds $IntervalSeconds
}

