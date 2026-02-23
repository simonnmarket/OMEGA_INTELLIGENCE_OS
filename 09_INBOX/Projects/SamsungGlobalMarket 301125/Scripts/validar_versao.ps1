# Script de Validação - Versão 1.02
# Samsung Global Market

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "VALIDACAO FINAL - EA VERSAO 1.02" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar arquivo .mq5
Write-Host "[1] Verificando arquivo fonte (.mq5)..." -ForegroundColor Yellow
$mq5Path = "C:\Users\Lenovo\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\SamsungGlobalMarket_EA.mq5"

if (Test-Path $mq5Path) {
    $content = Get-Content $mq5Path -Raw
    
    # Verificar #property version
    if ($content -match '#property version\s+"1\.02"') {
        Write-Host "    [OK] #property version 1.02" -ForegroundColor Green
    } else {
        Write-Host "    [ERRO] #property version NAO e 1.02!" -ForegroundColor Red
    }
    
    # Verificar Print da versão
    if ($content -match 'Print\("Versao: 1\.02"\)') {
        Write-Host "    [OK] Print versao 1.02" -ForegroundColor Green
    } else {
        Write-Host "    [ERRO] Print versao NAO e 1.02!" -ForegroundColor Red
    }
    
    # Verificar versão no handshake
    if ($content -match '"version":"1\.02"') {
        Write-Host "    [OK] Handshake versao 1.02" -ForegroundColor Green
    } else {
        Write-Host "    [ERRO] Handshake versao NAO e 1.02!" -ForegroundColor Red
    }
} else {
    Write-Host "    [ERRO] Arquivo .mq5 nao encontrado!" -ForegroundColor Red
}

Write-Host ""

# Verificar servidor Python
Write-Host "[2] Verificando servidor Python..." -ForegroundColor Yellow
$connection = Get-NetTCPConnection -LocalPort 5555 -ErrorAction SilentlyContinue
if ($connection) {
    Write-Host "    [OK] Servidor ativo na porta 5555" -ForegroundColor Green
} else {
    Write-Host "    [AVISO] Servidor NAO esta rodando!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "RESULTADO DA VALIDACAO" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se todos os itens acima estao [OK], compile (F7) e anexe o EA." -ForegroundColor White
Write-Host ""
Write-Host "DEVE APARECER NOS LOGS DO MT5:" -ForegroundColor Yellow
Write-Host "  Versao: 1.02  <- OBRIGATORIO!" -ForegroundColor Green
Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan

