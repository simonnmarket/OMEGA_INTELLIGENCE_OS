# ==============================================
# INSTALAÇÃO DE DEPENDÊNCIAS - SILVER QUANTUM V6.0
# ==============================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INSTALANDO DEPENDENCIAS - SILVER QUANTUM V6.0" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Python nao encontrado!" -ForegroundColor Red
    exit 1
}

# Instalar MetaTrader5
Write-Host ""
Write-Host "Instalando MetaTrader5..." -ForegroundColor Yellow
pip install MetaTrader5

# Instalar pandas
Write-Host ""
Write-Host "Instalando pandas..." -ForegroundColor Yellow
pip install pandas

# Instalar TA-Lib (pode precisar de binários)
Write-Host ""
Write-Host "Instalando TA-Lib..." -ForegroundColor Yellow
Write-Host "NOTA: TA-Lib pode precisar de binarios do Windows" -ForegroundColor Yellow
Write-Host "Se falhar, baixe de: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib" -ForegroundColor Yellow
pip install TA-Lib

# Verificar instalação
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO INSTALACAO..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

python -c "import MetaTrader5 as mt5; print('MetaTrader5: OK')"
python -c "import pandas as pd; print('pandas: OK')"
python -c "import talib; print('TA-Lib: OK')"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

