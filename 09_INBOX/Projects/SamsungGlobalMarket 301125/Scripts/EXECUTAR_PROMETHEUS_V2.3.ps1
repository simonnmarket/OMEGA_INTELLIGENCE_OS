# ==============================================================================
# SCRIPT PARA EXECUTAR PROMETHEUS V2.3
# ==============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PROMETHEUS V2.3 - INICIANDO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navegar para o diretório do projeto
$projectPath = "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia"
Set-Location $projectPath

Write-Host "📁 Diretório: $projectPath" -ForegroundColor Green
Write-Host ""

# Verificar se o arquivo existe
if (Test-Path "prometheus_v2.3_gerenciamento_escalonado.py") {
    Write-Host "✅ Arquivo encontrado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Iniciando sistema..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "IMPORTANTE: Certifique-se de que o MetaTrader 5 está aberto e conectado!" -ForegroundColor Red
    Write-Host ""
    
    # Executar o sistema
    python prometheus_v2.3_gerenciamento_escalonado.py
} else {
    Write-Host "❌ ERRO: Arquivo não encontrado!" -ForegroundColor Red
    Write-Host "   Verifique se está no diretório correto." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

