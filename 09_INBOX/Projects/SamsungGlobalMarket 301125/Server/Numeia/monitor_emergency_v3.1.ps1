# Monitoramento de Sobrevivência - Protocolo Prometheus v3.1
# FASE II: Monitoramento de KPIs Financeiros

while ($true) {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "MONITORAMENTO DE SOBREVIVÊNCIA v3.1" -ForegroundColor Cyan
    Write-Host "Protocolo Prometheus Emergency" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $logFile = ".\numeia_execution.jsonl"
    
    if (-not (Test-Path $logFile)) {
        Write-Host "Arquivo de log não encontrado. Aguardando..." -ForegroundColor Yellow
        Start-Sleep 60
        continue
    }
    
    # Lê todos os logs e filtra ORDER_CLOSED
    $allLogs = Get-Content $logFile | ForEach-Object {
        try {
            $_ | ConvertFrom-Json
        } catch {
            $null
        }
    }
    
    $closedOrders = $allLogs | Where-Object { $_.message.event -eq "ORDER_CLOSED" }
    
    $totalTrades = $closedOrders.Count
    $profitTrades = ($closedOrders | Where-Object { $_.message.profit -gt 0 }).Count
    $lossTrades = ($closedOrders | Where-Object { $_.message.profit -lt 0 }).Count
    
    $totalProfit = ($closedOrders | ForEach-Object { $_.message.profit } | Measure-Object -Sum).Sum
    $totalLoss = ($closedOrders | ForEach-Object { if ($_.message.profit -lt 0) { [Math]::Abs($_.message.profit) } else { 0 } } | Measure-Object -Sum).Sum
    
    $winRate = if ($totalTrades -gt 0) { 
        [Math]::Round(($profitTrades / $totalTrades) * 100, 2) 
    } else { 
        0 
    }
    
    $profitFactor = if ($totalLoss -gt 0) {
        [Math]::Round($totalProfit / $totalLoss, 2)
    } else {
        if ($totalProfit -gt 0) { "∞" } else { 0 }
    }
    
    # Calcula drawdown máximo (simplificado)
    $runningPnL = 0
    $maxDrawdown = 0
    $peak = 0
    foreach ($order in $closedOrders | Sort-Object { $_.time }) {
        $runningPnL += $order.message.profit
        if ($runningPnL > $peak) {
            $peak = $runningPnL
        }
        $drawdown = $peak - $runningPnL
        if ($drawdown > $maxDrawdown) {
            $maxDrawdown = $drawdown
        }
    }
    
    Write-Host "KPIs FINANCEIROS:" -ForegroundColor Green
    Write-Host "-----------------" -ForegroundColor Green
    Write-Host "Total de Trades: $totalTrades" -ForegroundColor White
    Write-Host "Trades Lucrativos: $profitTrades" -ForegroundColor Green
    Write-Host "Trades com Perda: $lossTrades" -ForegroundColor Red
    Write-Host ""
    Write-Host "Win Rate: $winRate%" -ForegroundColor $(if ($winRate -ge 55) { "Green" } else { "Yellow" })
    Write-Host "Profit Factor: $profitFactor" -ForegroundColor $(if ($profitFactor -gt 1.3) { "Green" } else { "Yellow" })
    Write-Host "P&L Total: $([Math]::Round($totalProfit, 2))" -ForegroundColor $(if ($totalProfit -gt 0) { "Green" } else { "Red" })
    Write-Host "Maximum Drawdown: $([Math]::Round($maxDrawdown, 2))" -ForegroundColor $(if ($maxDrawdown -lt 3) { "Green" } else { "Red" })
    Write-Host ""
    Write-Host "CRITÉRIOS DE SUCESSO:" -ForegroundColor Cyan
    Write-Host "---------------------" -ForegroundColor Cyan
    Write-Host "Profit Factor > 1.3: $(if ($profitFactor -gt 1.3 -or $profitFactor -eq "∞") { "✅" } else { "❌" })" -ForegroundColor $(if ($profitFactor -gt 1.3 -or $profitFactor -eq "∞") { "Green" } else { "Red" })
    Write-Host "Win Rate > 55%: $(if ($winRate -ge 55) { "✅" } else { "❌" })" -ForegroundColor $(if ($winRate -ge 55) { "Green" } else { "Red" })
    Write-Host "Total Trades >= 20: $(if ($totalTrades -ge 20) { "✅" } else { "❌" })" -ForegroundColor $(if ($totalTrades -ge 20) { "Green" } else { "Yellow" })
    Write-Host "Max Drawdown < 3%: $(if ($maxDrawdown -lt 3) { "✅" } else { "❌" })" -ForegroundColor $(if ($maxDrawdown -lt 3) { "Green" } else { "Red" })
    Write-Host ""
    Write-Host "Status: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "Próxima atualização em 60 segundos..." -ForegroundColor Gray
    Write-Host ""
    
    Start-Sleep 60
}

