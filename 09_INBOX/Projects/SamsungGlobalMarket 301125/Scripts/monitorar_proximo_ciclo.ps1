# Monitorar próximo ciclo do EA e reportar resultado completo
param(
    [int]$TimeoutMinutes = 10
)

$ErrorActionPreference = "Continue"
$projectPath = Split-Path -Parent $PSScriptRoot
$mt5Path = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "MONITORAMENTO DO PROXIMO CICLO - RELATORIO COMPLETO" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""
Write-Host "Iniciado em: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "Timeout: $TimeoutMinutes minutos" -ForegroundColor Gray
Write-Host ""

# Limpar responses antigos para ter certeza que estamos vendo novos
Write-Host "[PREPARACAO] Limpando responses antigos..." -ForegroundColor Yellow
Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host "  Responses antigos removidos" -ForegroundColor Green
Write-Host ""

Write-Host "[AGUARDANDO] Esperando EA enviar novos requests..." -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$cycleDetected = $false
$requestsSeen = @{}

while (((Get-Date) - $startTime).TotalMinutes -lt $TimeoutMinutes) {
    Start-Sleep -Seconds 2
    
    # Procurar por novos requests
    $newRequests = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue | 
                   Where-Object { ((Get-Date) - $_.LastWriteTime).TotalSeconds -lt 10 }
    
    foreach ($req in $newRequests) {
        if (-not $requestsSeen.ContainsKey($req.Name)) {
            $requestsSeen[$req.Name] = $true
            $cycleDetected = $true
            
            try {
                $reqContent = Get-Content $req.FullName -Raw | ConvertFrom-Json
                $symbol = $reqContent.symbol
                
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] REQUEST DETECTADO: $symbol" -ForegroundColor Green
                Write-Host "  Arquivo: $($req.Name)" -ForegroundColor Gray
                Write-Host "  Bid: $($reqContent.bid)" -ForegroundColor Gray
                Write-Host "  Ask: $($reqContent.ask)" -ForegroundColor Gray
                Write-Host "  Spread: $($reqContent.spread) pips" -ForegroundColor Gray
                
                # Aguardar response
                Write-Host "  Aguardando response..." -ForegroundColor Yellow
                $responseFile = $req.FullName -replace "AIRequest", "AIResponse"
                
                $waited = 0
                $maxWait = 10
                while ($waited -lt $maxWait -and -not (Test-Path $responseFile)) {
                    Start-Sleep -Seconds 1
                    $waited++
                }
                
                if (Test-Path $responseFile) {
                    Start-Sleep -Milliseconds 500  # Garantir que arquivo foi escrito completamente
                    $respContent = Get-Content $responseFile -Raw | ConvertFrom-Json
                    
                    Write-Host "  RESPONSE RECEBIDO:" -ForegroundColor Green
                    Write-Host "    Action: $($respContent.action)" -ForegroundColor $(
                        if ($respContent.action -eq "BUY") { "Green" }
                        elseif ($respContent.action -eq "SELL") { "Magenta" }
                        else { "Yellow" }
                    )
                    Write-Host "    Confidence: $($respContent.confidence)" -ForegroundColor White
                    Write-Host "    Reason: $($respContent.reason)" -ForegroundColor Gray
                    Write-Host ""
                    
                    # Avaliar resultado
                    if ($respContent.action -eq "BUY" -or $respContent.action -eq "SELL") {
                        Write-Host "  ✅ SINAL DE TRADE GERADO!" -ForegroundColor Green
                        
                        if ($respContent.confidence -ge 0.50) {
                            Write-Host "  ✅ CONFIDENCE >= 0.50 - EA DEVE EXECUTAR" -ForegroundColor Green
                            Write-Host ""
                            Write-Host "  Aguardando 5s para verificar se trade foi aberto..." -ForegroundColor Yellow
                            Start-Sleep -Seconds 5
                            Write-Host "  VERIFIQUE NO MT5: Aba 'Negociacoes' ou 'Historico'" -ForegroundColor Cyan
                        } else {
                            Write-Host "  ⚠️ CONFIDENCE < 0.50 - EA NAO VAI EXECUTAR" -ForegroundColor Yellow
                        }
                    } else {
                        Write-Host "  ⚠️ HOLD - Nenhum trade executado" -ForegroundColor Yellow
                    }
                    
                } else {
                    Write-Host "  ❌ ERRO: Response NAO foi criado em ${maxWait}s!" -ForegroundColor Red
                    Write-Host "  Problema: Servidor nao processou o request" -ForegroundColor Red
                }
                
                Write-Host ""
                
            } catch {
                Write-Host "  Erro ao processar request: $_" -ForegroundColor Red
            }
        }
    }
    
    if ($cycleDetected) {
        # Esperar mais um pouco para pegar todos os símbolos do ciclo
        Start-Sleep -Seconds 5
        break
    }
    
    # Mostrar progresso
    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalSeconds, 0)
    if ($elapsed % 10 -eq 0) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Aguardando... (${elapsed}s)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "RELATORIO FINAL" -ForegroundColor Green
Write-Host "==========================================================================="
Write-Host ""

if ($cycleDetected) {
    Write-Host "✅ Ciclo detectado e analisado" -ForegroundColor Green
    Write-Host ""
    
    # Resumo final
    Write-Host "[RESUMO]:" -ForegroundColor Yellow
    Write-Host "  Requests processados: $($requestsSeen.Count)" -ForegroundColor White
    
    $allResponses = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
    $buyCount = 0
    $sellCount = 0
    $holdCount = 0
    
    foreach ($resp in $allResponses) {
        try {
            $content = Get-Content $resp.FullName -Raw | ConvertFrom-Json
            if ($content.action -eq "BUY") { $buyCount++ }
            elseif ($content.action -eq "SELL") { $sellCount++ }
            elseif ($content.action -eq "HOLD") { $holdCount++ }
        } catch {}
    }
    
    Write-Host "  BUY: $buyCount" -ForegroundColor $(if ($buyCount -gt 0) { "Green" } else { "Gray" })
    Write-Host "  SELL: $sellCount" -ForegroundColor $(if ($sellCount -gt 0) { "Magenta" } else { "Gray" })
    Write-Host "  HOLD: $holdCount" -ForegroundColor $(if ($holdCount -gt 0) { "Yellow" } else { "Gray" })
    Write-Host ""
    
    if ($buyCount -gt 0 -or $sellCount -gt 0) {
        Write-Host "✅ SISTEMA FUNCIONANDO - Sinais BUY/SELL sendo gerados" -ForegroundColor Green
        Write-Host ""
        Write-Host "Verifique no MetaTrader 5:" -ForegroundColor Cyan
        Write-Host "  1. Aba 'Negociacoes' - Posicoes abertas" -ForegroundColor White
        Write-Host "  2. Aba 'Historico' - Ordens executadas" -ForegroundColor White
        Write-Host "  3. Aba 'Especialistas' - Logs do EA" -ForegroundColor White
    } else {
        Write-Host "❌ PROBLEMA: Apenas HOLD sendo gerado" -ForegroundColor Red
        Write-Host ""
        Write-Host "Causas possiveis:" -ForegroundColor Yellow
        Write-Host "  1. Servidor ainda usando codigo antigo (cache)" -ForegroundColor White
        Write-Host "  2. Logica do servidor incorreta" -ForegroundColor White
        Write-Host "  3. Spread muito alto para logica atual" -ForegroundColor White
    }
    
} else {
    Write-Host "❌ TIMEOUT: Nenhum ciclo detectado em $TimeoutMinutes minutos" -ForegroundColor Red
    Write-Host ""
    Write-Host "Causas possiveis:" -ForegroundColor Yellow
    Write-Host "  1. EA nao esta anexado ao grafico" -ForegroundColor White
    Write-Host "  2. EA esta pausado" -ForegroundColor White
    Write-Host "  3. MetaTrader 5 fechado" -ForegroundColor White
    Write-Host "  4. Intervalo do EA muito longo (>10 min)" -ForegroundColor White
}

Write-Host ""
Write-Host "Finalizado em: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

