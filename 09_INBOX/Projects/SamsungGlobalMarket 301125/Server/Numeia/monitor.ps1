# PROMETHEUS v4.1 - LIVE MONITOR
# Dashboard simples e atualizável

while ($true) {
    Clear-Host
    Write-Host "=== PROMETHEUS v4.1 - LIVE MONITOR ===" -ForegroundColor Green
    Write-Host ""
    
    # Verificar se o sistema está vivo (Heartbeat)
    try {
        $hb = Get-Item prometheus_heartbeat.tmp -ErrorAction Stop
        $age = (Get-Date) - $hb.LastWriteTime
        $ageSeconds = [math]::Round($age.TotalSeconds, 0)
        if ($ageSeconds -lt 120) {
            Write-Host "❤️  HEARTBEAT: Ativo (último ping há $ageSeconds s)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  HEARTBEAT: Desatualizado (último ping há $ageSeconds s)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "💔 HEARTBEAT: INATIVO - SISTEMA PAROU!" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Verificar os últimos logs
    Write-Host "📊 ÚLTIMOS LOGS:" -ForegroundColor Yellow
    try {
        $logs = Get-Content prometheus_master_log.jsonl -Tail 5 -ErrorAction SilentlyContinue
        if ($logs) {
            $logs | ForEach-Object { 
                $line = $_
                if ($line -match "ORDER_EXECUTED") {
                    Write-Host "   ✅ $line" -ForegroundColor Green
                } elseif ($line -match "ORDER_CLOSED") {
                    Write-Host "   💰 $line" -ForegroundColor Cyan
                } elseif ($line -match "PRODUCTION_CYCLE") {
                    Write-Host "   🔄 $line" -ForegroundColor Blue
                } elseif ($line -match "ERROR|CRITICAL") {
                    Write-Host "   ❌ $line" -ForegroundColor Red
                } else {
                    Write-Host "   $line"
                }
            }
        } else {
            Write-Host "   Nenhum log encontrado."
        }
    } catch {
        Write-Host "   Nenhum log encontrado."
    }
    
    Write-Host ""
    Write-Host "Pressione Ctrl+C para sair" -ForegroundColor Gray
    
    Start-Sleep 10
}

