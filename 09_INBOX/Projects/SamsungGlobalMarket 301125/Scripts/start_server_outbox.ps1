$ErrorActionPreference = 'Stop'

Write-Host "[Outbox] Terminando processos python antigos..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "[Outbox] Ativando venv..." -ForegroundColor Yellow
Set-Location "C:\Users\Lenovo\.cursor\SamsungGlobalMarket"

$venvActivate = ".\venv\Scripts\Activate.ps1"
if (-Not (Test-Path $venvActivate)) {
    Throw "Virtualenv não encontrado em $venvActivate"
}
. $venvActivate

Write-Host "[Outbox] Instalando/Atualizando dependências críticas..." -ForegroundColor Yellow
pip install --upgrade MetaTrader5 yfinance scikit-learn tabulate | Out-Null

Write-Host "[Outbox] Limpando TacticalSignals antigo..." -ForegroundColor Yellow
$signalsPath = Join-Path $env:APPDATA 'MetaQuotes\Terminal\Common\Files\TacticalSignals.json'
if (Test-Path $signalsPath) {
    Remove-Item $signalsPath -Force
}

Write-Host "[Outbox] Iniciando servidor tático v6.0..." -ForegroundColor Green
Set-Location "C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server"

python .\Numeia_v6_0_Tactical_Server.py

