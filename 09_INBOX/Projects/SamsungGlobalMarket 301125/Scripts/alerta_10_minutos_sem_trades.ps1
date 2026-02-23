# Alerta se não houver trades em 10 minutos
param(
    [int]$TimeoutMinutes = 10,
    [string]$LogFile = "logs\trades_monitor.log"
)

$ErrorActionPreference = "Continue"
$projectPath = Split-Path -Parent $PSScriptRoot
$logFileFull = Join-Path $projectPath $LogFile

# Criar diretório de logs
$logDir = Split-Path $logFileFull
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-MonitorLog { param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $logFileFull -Value $logEntry
    Write-Host $logEntry
}

# Arquivo para rastrear última trade
$lastTradeFile = Join-Path $projectPath "logs\last_trade_time.txt"
$startTime = Get-Date

Write-MonitorLog "========================================"
Write-MonitorLog "MONITOR: Alertar se sem trades em $TimeoutMinutes minutos"
Write-MonitorLog "Iniciado em: $startTime"
Write-MonitorLog "========================================"
Write-Host ""
Write-Host "Monitoramento ativo. Alertando se nenhuma trade em $TimeoutMinutes minutos..." -ForegroundColor Yellow
Write-Host ""

# Verificar se há registro de última trade
$lastTradeTime = $null
if (Test-Path $lastTradeFile) {
    try {
        $lastTradeTimeStr = Get-Content $lastTradeFile -Raw
        $lastTradeTime = [DateTime]::Parse($lastTradeTimeStr)
        Write-MonitorLog "Ultima trade registrada: $lastTradeTime"
    } catch {
        Write-MonitorLog "Nao foi possivel ler ultima trade - assumindo nenhuma trade ainda"
    }
}

# Monitorar diretório MT5 para responses que indicam trades
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

Write-Host "Monitorando responses para detectar sinais de trading..." -ForegroundColor Cyan
Write-Host ""

$checkInterval = 30  # Verificar a cada 30 segundos
$elapsedMinutes = 0

while ($true) {
    Start-Sleep -Seconds $checkInterval
    $elapsedMinutes = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
    
    # Verificar responses recentes que possam indicar trades
    if (Test-Path $mt5Path) {
        $recentResps = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue | 
                       Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -lt 60 }
        
        $tradesFound = 0
        $buySignals = 0
        $sellSignals = 0
        
        foreach ($resp in $recentResps) {
            try {
                $content = Get-Content $resp.FullName -Raw | ConvertFrom-Json
                $action = $content.action
                
                if ($action -eq "BUY" -or $action -eq "SELL") {
                    $tradesFound++
                    if ($action -eq "BUY") { $buySignals++ }
                    if ($action -eq "SELL") { $sellSignals++ }
                    
                    # Atualizar última trade
                    (Get-Date).ToString("yyyy-MM-dd HH:mm:ss") | Out-File $lastTradeFile -Encoding UTF8
                    $lastTradeTime = Get-Date
                    
                    Write-MonitorLog "SINAL DETECTADO: $($content.symbol) - $action (conf: $($content.confidence))"
                }
            } catch {
                # Ignorar erros de parsing
            }
        }
        
        if ($tradesFound -gt 0) {
            Write-Host "[$elapsedMinutes min] Sinais encontrados: $tradesFound (BUY: $buySignals, SELL: $sellSignals)" -ForegroundColor Green
            Write-MonitorLog "Status: $tradesFound sinal(is) de trading encontrado(s)"
            $elapsedMinutes = 0  # Reset contador
        } else {
            Write-Host "[$elapsedMinutes min] Nenhum sinal BUY/SELL (apenas HOLD ou nenhum response)" -ForegroundColor Gray
            
            # Verificar timeout
            if ($elapsedMinutes -ge $TimeoutMinutes) {
                Write-Host ""
                Write-Host "===========================================================================" -ForegroundColor Red
                Write-Host "ALERTA CRITICO: $TimeoutMinutes MINUTOS SEM NENHUMA TRADE!" -ForegroundColor Red
                Write-Host "===========================================================================" -ForegroundColor Red
                Write-Host ""
                
                Write-MonitorLog "ALERTA CRITICO: $TimeoutMinutes minutos sem trades - Possivel problema no sistema"
                
                # Diagnóstico
                Write-Host "DIAGNOSTICO:" -ForegroundColor Yellow
                
                # Verificar servidor
                $proc = Get-Process python -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "  Servidor: RODANDO (PID: $($proc.Id))" -ForegroundColor Green
                } else {
                    Write-Host "  Servidor: PARADO!" -ForegroundColor Red
                }
                
                # Verificar requests
                $reqs = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
                Write-Host "  Requests: $($reqs.Count)" -ForegroundColor $(if ($reqs.Count -gt 0) { "Yellow" } else { "Gray" })
                
                # Verificar responses
                $allResps = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
                Write-Host "  Responses: $($allResps.Count)" -ForegroundColor $(if ($allResps.Count -gt 0) { "Cyan" } else { "Gray" })
                
                # Analisar responses recentes
                if ($allResps) {
                    $holdCount = 0
                    $buyCount = 0
                    $sellCount = 0
                    
                    foreach ($r in $allResps) {
                        try {
                            $c = Get-Content $r.FullName -Raw | ConvertFrom-Json
                            if ($c.action -eq "HOLD") { $holdCount++ }
                            elseif ($c.action -eq "BUY") { $buyCount++ }
                            elseif ($c.action -eq "SELL") { $sellCount++ }
                        } catch {}
                    }
                    
                    Write-Host "  Actions: BUY=$buyCount, SELL=$sellCount, HOLD=$holdCount" -ForegroundColor Cyan
                    
                    if ($buyCount -eq 0 -and $sellCount -eq 0 -and $holdCount -gt 0) {
                        Write-Host ""
                        Write-Host "  PROBLEMA IDENTIFICADO: Apenas HOLD sendo gerado!" -ForegroundColor Red
                        Write-Host "  Acao: Verificar logica do servidor - deve encontrar oportunidades" -ForegroundColor Yellow
                    }
                }
                
                Write-Host ""
                Write-Host "Execute diagnostico completo:" -ForegroundColor Yellow
                Write-Host "  .\Scripts\verificar_estado_completo.ps1" -ForegroundColor Cyan
                Write-Host ""
                
                # Tocar som de alerta
                [System.Media.SystemSounds]::Exclamation.Play()
                
                # Reset contador após alerta (não repetir continuamente)
                $startTime = Get-Date
                $elapsedMinutes = 0
            }
        }
    }
}

