# ==============================================================================
# SCRIPT POWERSHELL - EXECUTAR SILVER SYSTEM
# Projeto: SilverGMarket (Independente)
# ==============================================================================

# Caminho completo do arquivo
$scriptPath = "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver\silver_system_v2.3.py"

# Navegar para o diretório
Set-Location "C:\Users\Lenovo\.cursor\SilverGMarket\Server\Silver"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SILVER SYSTEM V2.3 - PROJETO SILVERGMARKET" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Projeto: SilverGMarket (Independente)" -ForegroundColor Yellow
Write-Host "Símbolos: XAGUSD, XAGAUD, XAGEUR, XAGGBP" -ForegroundColor Yellow
Write-Host "Magic Number: 99992 (isolado)" -ForegroundColor Yellow
Write-Host "Caminho: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# Verificar horário
Write-Host "Verificando horário de trading..." -ForegroundColor Cyan
python verificar_horario_trading_xag.py
Write-Host ""

# Verificar se o arquivo existe
if (Test-Path $scriptPath) {
    Write-Host "✅ Arquivo encontrado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando Sistema Silver..." -ForegroundColor Cyan
    Write-Host ""
    
    # Executar o script Python
    python $scriptPath
} else {
    Write-Host "❌ ERRO: Arquivo não encontrado!" -ForegroundColor Red
    Write-Host "Caminho esperado: $scriptPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

