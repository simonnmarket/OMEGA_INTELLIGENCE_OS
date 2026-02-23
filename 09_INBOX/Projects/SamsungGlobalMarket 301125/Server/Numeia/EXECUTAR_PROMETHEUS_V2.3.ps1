# ==============================================================================
# SCRIPT POWERSHELL - EXECUTAR PROMETHEUS V2.3
# ==============================================================================

# Caminho completo do arquivo
$scriptPath = "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia\prometheus_v2.3_gerenciamento_escalonado.py"

# Navegar para o diretório
Set-Location "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "PROMETHEUS V2.3 - MODO TESTE (XAG)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Caminho: $scriptPath" -ForegroundColor Yellow
Write-Host "Diretório: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Verificar se o arquivo existe
if (Test-Path $scriptPath) {
    Write-Host "✅ Arquivo encontrado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando sistema..." -ForegroundColor Cyan
    Write-Host ""
    
    # Executar o script Python
    python $scriptPath
} else {
    Write-Host "❌ ERRO: Arquivo não encontrado!" -ForegroundColor Red
    Write-Host "Caminho esperado: $scriptPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique se o caminho está correto." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

