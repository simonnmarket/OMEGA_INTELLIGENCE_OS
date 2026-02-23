#==============================================================================
# MONITORAMENTO PROATIVO NOITE - VERIFICAÇÃO A CADA 5 MINUTOS
# Sistema de Vigilância Ativa - Prometheus v3.0.0
#==============================================================================

$ErrorActionPreference = "Continue"
$Host.UI.RawUI.WindowTitle = "🛡️ Monitor Proativo - Vigilância Noite GBPUSD"

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "🛡️  MONITORAMENTO PROATIVO - OPERAÇÃO NOTURNA GBPUSD" -ForegroundColor Yellow
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "Frequência: Verificação a cada 5 minutos" -ForegroundColor White
Write-Host "Alertas: Ausência de ordens por 5-10 minutos = FALHA DETECTADA" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

$mt5Path = "$env:APPDATA\MetaQuotes\Terminal\Common\Files"
$lastCheckTime = Get-Date
$iteration = 0

# Contador de verificação sem ordens
$cyclesWithoutOrders = 0
$maxCyclesWithoutOrders = 2  # 2 ciclos = 10 minutos (5min x 2)

while ($true) {
    $iteration++
    $currentTime = Get-Date
    $timestamp = $currentTime.ToString("HH:mm:ss")
    
    Write-Host "[$timestamp] ======================================== Verificação #$iteration" -ForegroundColor Cyan
    
    # ============================================================
    # 1. VERIFICAR SERVIDOR PYTHON
    # ============================================================
    Write-Host "  [1/4] Verificando servidor Python..." -ForegroundColor Gray
    $pythonProcesses = Get-Process | Where-Object {$_.ProcessName -like "*python*"} -ErrorAction SilentlyContinue
    
    if ($pythonProcesses) {
        Write-Host "    ✅ Servidor Python rodando (PID: $($pythonProcesses[0].Id))" -ForegroundColor Green
        
        # Verificar qual servidor está rodando
        $serverType = "UNKNOWN"
        foreach ($proc in $pythonProcesses) {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -match "server_file_based") {
                $serverType = "FILE_BASED"
                break
            } elseif ($cmdLine -match "main_server") {
                $serverType = "SOCKET"
                break
            }
        }
        
        if ($serverType -eq "FILE_BASED") {
            Write-Host "    ✅ Servidor correto: server_file_based_v2.0.0.py" -ForegroundColor Green
        } elseif ($serverType -eq "SOCKET") {
            Write-Host "    ⚠️  Servidor alternativo: main_server.py" -ForegroundColor Yellow
        } else {
            Write-Host "    ⚠️  Tipo de servidor não identificado" -ForegroundColor Yellow
        }
    } else {
        Write-Host "    🔴 ERRO: Servidor Python NÃO está rodando!" -ForegroundColor Red
        Write-Host "    🔴 AÇÃO NECESSÁRIA: Reiniciar servidor!" -ForegroundColor Red
    }
    
    # ============================================================
    # 2. VERIFICAR REQUESTS/RESPONSES (Comunicação EA <-> Server)
    # ============================================================
    Write-Host "  [2/4] Verificando comunicação EA <-> Servidor..." -ForegroundColor Gray
    
    if (Test-Path $mt5Path) {
        # Contar requests
        $requests = Get-ChildItem -Path $mt5Path -Filter "AIRequest.*.json" -ErrorAction SilentlyContinue
        $responses = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue
        
        Write-Host "    📊 Requests: $($requests.Count) | Responses: $($responses.Count)" -ForegroundColor Cyan
        
        # Verificar idade dos requests
        $oldRequests = 0
        foreach ($req in $requests) {
            $age = (Get-Date) - $req.LastWriteTime
            if ($age.TotalSeconds -gt 30) {
                $oldRequests++
                Write-Host "    ⚠️  Request antigo: $($req.Name) ($([math]::Round($age.TotalSeconds))s atrás)" -ForegroundColor Yellow
            }
        }
        
        if ($oldRequests -gt 0) {
            Write-Host "    🔴 ALERTA: $oldRequests request(s) antigo(s) - Servidor pode não estar processando!" -ForegroundColor Red
        }
        
        # Verificar se responses foram criados recentemente
        $recentResponses = 0
        foreach ($resp in $responses) {
            $age = (Get-Date) - $resp.LastWriteTime
            if ($age.TotalSeconds -lt 3600) {  # Última hora
                $recentResponses++
            }
        }
        
        Write-Host "    📊 Responses nos últimos 60min: $recentResponses" -ForegroundColor Cyan
    } else {
        Write-Host "    🔴 ERRO: Diretório MT5 não existe: $mt5Path" -ForegroundColor Red
    }
    
    # ============================================================
    # 3. VERIFICAR APLICAÇÕES/ORDENS EXECUTADAS
    # ============================================================
    Write-Host "  [3/4] Verificando execução de trades..." -ForegroundColor Gray
    
    # Verificar se há responses com action=BUY ou SELL (não HOLD)
    $tradeSignals = 0
    if (Test-Path $mt5Path) {
        foreach ($resp in $responses) {
            try {
                $content = Get-Content $resp.FullName -Raw -ErrorAction SilentlyContinue
                if ($content -match '"action":"(BUY|SELL)"') {
                    $tradeSignals++
                }
            } catch {
                # Ignorar erro de leitura
            }
        }
    }
    
    Write-Host "    📊 Sinais de trade (BUY/SELL) encontrados: $tradeSignals" -ForegroundColor Cyan
    
    # ============================================================
    # 4. DIAGNÓSTICO: Ordem não executada por 5-10 minutos?
    # ============================================================
    Write-Host "  [4/4] Diagnóstico de saúde do sistema..." -ForegroundColor Gray
    
    $lastResponse = Get-ChildItem -Path $mt5Path -Filter "AIResponse.*.json" -ErrorAction SilentlyContinue | 
                    Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($lastResponse) {
        $responseAge = (Get-Date) - $lastResponse.LastWriteTime
        Write-Host "    📊 Última response: $([math]::Round($responseAge.TotalSeconds))s atrás" -ForegroundColor Cyan
        
        # Verificar se última response tinha sinal de trade
        try {
            $lastContent = Get-Content $lastResponse.FullName -Raw -ErrorAction SilentlyContinue
            if ($lastContent -match '"action":"(BUY|SELL)"') {
                Write-Host "    ✅ Última response tinha sinal de trade" -ForegroundColor Green
                $cyclesWithoutOrders = 0  # Reset contador
            } elseif ($lastContent -match '"action":"HOLD"') {
                $cyclesWithoutOrders++
                Write-Host "    ⚠️  Response com HOLD (esperado durante espera de oportunidade)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "    ⚠️  Erro ao ler último response" -ForegroundColor Yellow
        }
    } else {
        Write-Host "    ⚠️  Nenhum response encontrado ainda" -ForegroundColor Yellow
        $cyclesWithoutOrders++
    }
    
    # ============================================================
    # ALERTA CRÍTICO: Sistema pode estar com falha
    # ============================================================
    if ($cyclesWithoutOrders -ge $maxCyclesWithoutOrders) {
        Write-Host ""
        Write-Host "===============================================================================" -ForegroundColor Red
        Write-Host "🔴 ALERTA CRÍTICO: Sistema pode estar com FALHA!" -ForegroundColor Red
        Write-Host "===============================================================================" -ForegroundColor Red
        Write-Host "Motivo: Sem sinais de trade (BUY/SELL) por $($cyclesWithoutOrders * 5) minutos" -ForegroundColor Yellow
        Write-Host "Action: Verificar manualmente o EA e logs do servidor" -ForegroundColor Yellow
        Write-Host "===============================================================================" -ForegroundColor Red
        Write-Host ""
    } elseif ($cyclesWithoutOrders -eq 0) {
        Write-Host "    ✅ Sistema operacional: sinais recebidos recentemente" -ForegroundColor Green
    }
    
    # ============================================================
    # RES bundle
    # ============================================================
    Write-Host ""
    Write-Host "  [RESUMO] Estado do sistema:" -ForegroundColor Cyan
    Write-Host "    • Servidor: $(if($pythonProcesses){'✅ RODANDO'}else{'🔴 PARADO'})" -ForegroundColor $(if($pythonProcesses){'Green'}else{'Red'})
    Write-Host "    • Comunicação: $(if($oldRequests -eq 0){'✅ OK'}else{'⚠️ REVISAR'})" -ForegroundColor $(if($oldRequests -eq 0){'Green'}else{'Yellow'})
    Write-Host "    • Execução: $(if($tradeSignals -gt 0 -or $cyclesWithoutOrders -lt 2){'✅ OK'}else{'⚠️ INSPECTAR'})" -ForegroundColor $(if($tradeSignals -gt 0 -or $cyclesWithoutOrders -lt 2){'Green'}else{'Yellow'})
    Write-Host ""
    
    $lastCheckTime = $currentTime
    
    # Aguardar 5 minutos até próxima verificação
    Write-Host "[$timestamp] Aguardando 5 minutos até próxima verificação..." -ForegroundColor Gray
    Write-Host ""
    
    Start-Sleep -Seconds 300  # 5 minutos
}

