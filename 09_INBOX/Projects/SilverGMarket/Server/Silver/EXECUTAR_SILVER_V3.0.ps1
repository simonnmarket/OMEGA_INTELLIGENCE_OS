# ==============================================================================
# SCRIPT POWERSHELL - EXECUTAR SILVER SYSTEM V3.0 ESCALONADO
# Projeto: SilverGMarket (Independente)
# ==============================================================================

$scriptPath = "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver\silver_system_v3.0_escalonado.py"
Set-Location "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SILVER SYSTEM V3.0 - ESCALONADO COM MULTIPLAS ENTRADAS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Projeto: SilverGMarket (Independente)" -ForegroundColor Yellow
Write-Host "Timeframe: M1 (múltiplas entradas)" -ForegroundColor Yellow
Write-Host "Volume: 0.10 - 50.00 lotes (escalonado)" -ForegroundColor Yellow
Write-Host "Entradas: Ilimitadas por símbolo" -ForegroundColor Yellow
Write-Host "SL/TP: 100/800 pips (tendências 500-1600 pontos)" -ForegroundColor Yellow
Write-Host ""

Write-Host "Verificando horário de trading..." -ForegroundColor Cyan
python verificar_horario_trading_xag.py
Write-Host ""

if (Test-Path $scriptPath) {
    Write-Host "✅ Arquivo encontrado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Iniciando Sistema Silver V3.0 ESCALONADO..." -ForegroundColor Cyan
    Write-Host "   Sistema rodará durante a noite inteira" -ForegroundColor Cyan
    Write-Host ""
    
    python $scriptPath
} else {
    Write-Host "❌ ERRO: Arquivo não encontrado!" -ForegroundColor Red
    Write-Host "Caminho esperado: $scriptPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

