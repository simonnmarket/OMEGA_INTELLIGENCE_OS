# Dashboard visual em tempo real
$ErrorActionPreference = "Continue"

$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
$projectPath = Split-Path -Parent $PSScriptRoot

function Get-StatusColor { param($status)
    switch($status) {
        "OK" { return "Green" }
        "WARN" { return "Yellow" }
        "ERROR" { return "Red" }
        default { return "Gray" }
    }
}

function Show-Dashboard {
    Clear-Host
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host "DASHBOARD EM TEMPO REAL - SAMSUNG GLOBAL MARKET" -ForegroundColor Green
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host "Ultima atualizacao: $timestamp" -ForegroundColor Gray
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 1. STATUS DO SERVIDOR
    Write-Host "[1] SERVIDOR PYTHON" -ForegroundColor Yellow
    $proc = Get-Process python -ErrorAction SilentlyContinue
    if ($proc) {
        $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)" | Select-Object -ExpandProperty CommandLine)
        if ($cmd -like "*server_file_based*") {
            Write-Host "  Status: " -NoNewline
            Write-Host "RODANDO (CORRETO)" -ForegroundColor Green
            Write-Host "  PID: $($proc.Id)" -ForegroundColor Gray
            $serverStatus = "OK"
        } elseif ($cmd -like "*main_server*") {
            Write-Host "  Status: " -NoNewline
            Write-Host "RODANDO (INCORRETO - main_server)" -ForegroundColor Red
            Write-Host "  PID: $($proc.Id)" -ForegroundColor Gray
            $serverStatus = "ERROR"
        } else {
            Write-Host "  Status: " -NoNewline
            Write-Host "RODANDO (DESCONHECIDO)" -ForegroundColor Yellow
            Write-Host "  PID: $($proc.Id)" -ForegroundColor Gray
            $serverStatus = "WARN"
        }
    } else {
        Write-Host "  Status: " -NoNewline
        Write-Host "PARADO!" -ForegroundColor Red
        $serverStatus = "ERROR"
    }
    Write-Host ""
    
    # 2. ARQUIVOS MT5
    Write-Host "[2] ARQUIVOS MT5" -ForegroundColor Yellow
    if (Test-Path $mt5Path) {
        $reqs = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
        $resps = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
        
        Write-Host "  Requests: " -NoNewline
        if ($reqs) {
            $oldReqs = ($reqs | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -gt 30 })
            if ($oldReqs) {
                Write-Host "$($reqs.Count) ($($oldReqs.Count) ANTIGOS >30s)" -ForegroundColor Red
                $filesStatus = "ERROR"
            } else {
                Write-Host "$($reqs.Count) (OK)" -ForegroundColor Green
                $filesStatus = "OK"
            }
            
            foreach ($r in $reqs | Select-Object -First 3) {
                $age = [math]::Round(((Get-Date) - $r.LastWriteTime).TotalSeconds, 1)
                $color = if ($age -gt 30) { "Red" } elseif ($age -gt 10) { "Yellow" } else { "Green" }
                Write-Host "    $($r.Name) - ${age}s" -ForegroundColor $color
            }
        } else {
            Write-Host "0 (OK)" -ForegroundColor Green
            $filesStatus = "OK"
        }
        
        Write-Host "  Responses: " -NoNewline
        if ($resps) {
            $recentResps = ($resps | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -lt 10 })
            $color = if ($resps.Count -gt 20) { "Red" } elseif ($resps.Count -gt 5) { "Yellow" } else { "Green" }
            Write-Host "$($resps.Count) (Recentes: $recentResps)" -ForegroundColor $color
            
            # Mostrar responses recentes
            $recentRespsList = $resps | Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -lt 10 } | Select-Object -First 3
            foreach ($r in $recentRespsList) {
                $age = [math]::Round(((Get-Date) - $r.LastWriteTime).TotalSeconds, 1)
                try {
                    $content = Get-Content $r.FullName -Raw | ConvertFrom-Json
                    Write-Host "    $($r.Name) - ${age}s - Action: $($content.action) Conf: $($content.confidence)" -ForegroundColor Cyan
                } catch {
                    Write-Host "    $($r.Name) - ${age}s - (JSON invalido)" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "0" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ERRO: Diretorio nao existe!" -ForegroundColor Red
        $filesStatus = "ERROR"
    }
    Write-Host ""
    
    # 3. STATUS GERAL
    Write-Host "[3] STATUS GERAL DO SISTEMA" -ForegroundColor Yellow
    
    if ($serverStatus -eq "OK" -and $filesStatus -eq "OK") {
        Write-Host "  " -NoNewline
        Write-Host "OPERACIONAL" -ForegroundColor Green -BackgroundColor Black
        Write-Host "  Todos os componentes funcionando corretamente" -ForegroundColor Gray
    } elseif ($serverStatus -eq "ERROR") {
        Write-Host "  " -NoNewline
        Write-Host "BLOQUEADO - SERVIDOR PARADO" -ForegroundColor Red -BackgroundColor Black
        Write-Host "  Aco: Iniciar servidor imediatamente" -ForegroundColor Yellow
    } elseif ($filesStatus -eq "ERROR") {
        Write-Host "  " -NoNewline
        Write-Host "ALERTA - REQUESTS ANTIGOS" -ForegroundColor Yellow -BackgroundColor Black
        Write-Host "  Servidor pode nao estar processando requests" -ForegroundColor Yellow
    } else {
        Write-Host "  " -NoNewline
        Write-Host "AVISO" -ForegroundColor Yellow -BackgroundColor Black
    }
    Write-Host ""
    
    # 4. LOGS RECENTES (se existirem)
    $logFile = Join-Path $projectPath "logs\monitor_realtime.log"
    if (Test-Path $logFile) {
        Write-Host "[4] ULTIMOS EVENTOS" -ForegroundColor Yellow
        $lastLogs = Get-Content $logFile -Tail 5 -ErrorAction SilentlyContinue
        foreach ($log in $lastLogs) {
            if ($log -like "*ERROR*") {
                Write-Host "  $log" -ForegroundColor Red
            } elseif ($log -like "*WARN*") {
                Write-Host "  $log" -ForegroundColor Yellow
            } elseif ($log -like "*SUCCESS*") {
                Write-Host "  $log" -ForegroundColor Green
            } else {
                Write-Host "  $log" -ForegroundColor Gray
            }
        }
        Write-Host ""
    }
    
    Write-Host "===========================================================================" -ForegroundColor Cyan
    Write-Host "Atualizacao automatica a cada 2 segundos | Ctrl+C para parar" -ForegroundColor Gray
    Write-Host "===========================================================================" -ForegroundColor Cyan
}

# Loop principal
while ($true) {
    Show-Dashboard
    Start-Sleep -Seconds 2
}

