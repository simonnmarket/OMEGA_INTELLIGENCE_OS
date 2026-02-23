# ============================================================================
# SCRIPT PARA VERIFICAR EVENTOS DE CONEXÃO
# ============================================================================

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO EVENTOS DE CONEXAO DO EA" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""

$logFile = "logs\main_server.log"

if (-not (Test-Path $logFile)) {
    Write-Host "[ERRO] Arquivo de log nao encontrado: $logFile" -ForegroundColor Red
    Write-Host "       Servidor pode nao estar rodando" -ForegroundColor Yellow
    exit 1
}

Write-Host "Ultimas 50 linhas do log:" -ForegroundColor Green
Write-Host ""

$logs = Get-Content $logFile -Tail 50

# Procurar eventos relevantes
$connectionEvents = $logs | Select-String -Pattern "NOVA CONEXAO|EA conectado|Handler iniciado|Dados recebidos|HANDSHAKE|HEARTBEAT|conectado de" -CaseSensitive:$false

if ($connectionEvents) {
    Write-Host "[EVENTOS DE CONEXAO ENCONTRADOS]:" -ForegroundColor Green
    Write-Host ""
    $connectionEvents | ForEach-Object {
        $line = $_
        if ($line -match "NOVA CONEXAO") {
            Write-Host "  [OK] $line" -ForegroundColor Green
        } elseif ($line -match "Handler iniciado") {
            Write-Host "  [OK] $line" -ForegroundColor Green
        } elseif ($line -match "Dados recebidos") {
            Write-Host "  [OK] $line" -ForegroundColor Cyan
        } elseif ($line -match "HANDSHAKE") {
            Write-Host "  [OK] $line" -ForegroundColor Cyan
        } elseif ($line -match "HEARTBEAT.*Enviado") {
            Write-Host "  [OK] $line" -ForegroundColor Green
        } else {
            Write-Host "  [INFO] $line" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "[AVISO] Nenhum evento de conexao encontrado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ultimas linhas do log:" -ForegroundColor Gray
    $logs | Select-Object -Last 10
}

Write-Host ""
Write-Host "==========================================================================="
Write-Host "DIAGNOSTICO:" -ForegroundColor Yellow
Write-Host "==========================================================================="

if ($connectionEvents -match "NOVA CONEXAO") {
    Write-Host "[OK] Servidor esta registrando conexoes do EA" -ForegroundColor Green
} else {
    Write-Host "[PROBLEMA] Servidor NAO esta registrando conexoes" -ForegroundColor Red
    Write-Host "           EA pode nao estar se conectando OU servidor nao esta escutando" -ForegroundColor Yellow
}

if ($connectionEvents -match "Dados recebidos") {
    Write-Host "[OK] EA esta enviando dados para o servidor" -ForegroundColor Green
} else {
    Write-Host "[PROBLEMA] EA NAO esta enviando dados (handshake)" -ForegroundColor Red
}

if ($connectionEvents -match "HANDSHAKE") {
    Write-Host "[OK] Handshake foi processado corretamente" -ForegroundColor Green
} else {
    Write-Host "[PROBLEMA] Handshake NAO foi processado" -ForegroundColor Red
}

if ($connectionEvents -match "HEARTBEAT.*Enviado") {
    Write-Host "[OK] Heartbeats estao sendo enviados" -ForegroundColor Green
} else {
    Write-Host "[PROBLEMA] Heartbeats NAO estao sendo enviados" -ForegroundColor Red
}

Write-Host ""

