# ============================================================================
# SCRIPT DE VERIFICAÇÃO RÁPIDA DE KPIs
# PROJETO: Prometheus v3.0.0
# ============================================================================

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "VERIFICACAO RAPIDA DE KPIs" -ForegroundColor Yellow
Write-Host "==========================================================================="
Write-Host ""

cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket

# Ativar ambiente virtual
& .\venv\Scripts\Activate.ps1

# Executar analytics engine
python analytics_engine.py

Write-Host ""
Write-Host "==========================================================================="

